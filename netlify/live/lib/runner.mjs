// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";
import { scoreSnapshots, checkBlob, historyPayload, dayOfKey, KEEP, LATE_AFTER, LOOKBACK } from "./check.mjs";

export const API = "https://api.alerts.in.ua/v1";
const HOUR = 3600e3, FETCH_TIMEOUT = 8000;
export const STORE_NAME = "airalert-live";

async function getJSON(fetchFn, url, token, timeoutMs) {
  const r = await fetchFn(url, { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(timeoutMs) });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${url.replace(API, "")}`);       // message never contains the token
  const body = await r.json();
  if (!body || !Array.isArray(body.alerts)) throw new Error(`no 'alerts' array in ${url.replace(API, "")}`);
  return body;
}

export const snapshotKey = (t) => `snap/${new Date(Math.floor(t / HOUR) * HOUR).toISOString().slice(0, 13)}`;

export async function runUpdate({ fetchFn, store, token, now, model, regions, seed, timeoutMs = FETCH_TIMEOUT }) {
  const status = { ok: false, at: now, active_alerts: null, excluded: null, rejected: [], history_unit: null,
                   history_ok: null, history_failing: [], error: null };
  if (!token) {                                        // visible on the page, then the run fails
    status.error = "configuration: ALERTS_IN_UA_TOKEN is not set";
    await store.setJSON("status", status);
    throw new Error("ALERTS_IN_UA_TOKEN is not set");
  }
  let state = await store.get("state", { type: "json" });
  if (!state) {
    if (!seed || !seed.records || !seed.coverage || !seed.rejections || !seed.historyFail) throw new Error("empty store and no valid seed state");
    state = structuredClone(seed);                    // first run: start from the saved dump (plans/M8.md §2)
  }
  try {
    const active = await getJSON(fetchFn, `${API}/alerts/active.json`, token, timeoutMs);
    const res = applyActive(state, active.alerts, now, regions);
    status.active_alerts = active.alerts.length;
    status.excluded = res.skipped;
    status.rejected = res.rejected.map(r => ({ ...r, from: "active" }));
  } catch (e) {
    status.error = `active: ${e.message}`;
    await store.setJSON("status", status);
    return status;                                     // no forecast from a failed poll; the page greys at once
  }
  const unit = nextRotationUnit(state, regions);
  status.history_unit = unit;
  try {
    const h = await getJSON(fetchFn, `${API}/regions/${regions.api_uid[unit]}/alerts/month_ago.json`, token, timeoutMs);
    const res = applyHistory(state, unit, h.alerts, now, regions);
    status.rejected.push(...res.rejected.map(r => ({ ...r, from: "history" })));
    status.history_ok = true;
    state.historyFail[unit] = 0;
  } catch (e) {
    status.history_ok = false;
    status.history_error = e.message;                 // coverage of this unit does not advance; streak shown on the page
    state.historyFail[unit] = (state.historyFail[unit] || 0) + 1;
  }
  status.history_failing = Object.entries(state.historyFail).filter(([, n]) => n >= 2).map(([u, n]) => ({ unit: u, consecutive: n }));
  const forecast = forecastAll(state, now, model, regions);
  status.ok = true;
  await store.setJSON("state", state);
  await store.setJSON("latest", forecast);
  // M11 §A1: the FIRST successful write in a UTC hour wins (Blobs has no create-if-absent: a rare race between two
  // overlapping runs can overwrite; the scorer uses the stored snapshot's own tau, so a race changes which forecast is
  // archived, never how it is scored). Snapshots from before the first M11 run are legacy (check_epoch).
  let epoch = await store.get("check_epoch", { type: "json" });
  if (epoch === null || epoch === undefined) { epoch = now; await store.setJSON("check_epoch", epoch); }
  const key = snapshotKey(now);
  if ((await store.get(key, { type: "json" })) === null) {
    await store.setJSON(key, { ...forecast, written_at: now, late: now - Math.floor(now / HOUR) * HOUR >= LATE_AFTER });
  }
  // persistent rejection log (state.rejections expire after 24 h; the check needs them for 35 days)
  if (status.rejected.length) {
    const log = (await store.get("rejection_log", { type: "json" })) || [];
    for (const r of status.rejected) log.push([now, r.unit, r.from]);
    // kept KEEP + LOOKBACK: the oldest kept snapshot (tau = now - KEEP) needs rejections back to tau - 24 h
    await store.setJSON("rejection_log", log.filter(([t]) => t > now - KEEP - LOOKBACK));
  }
  await store.setJSON("status", status);
  const check = await updateCheck(store, state, now, regions, epoch);
  if (check.ok === false && check.computed_at === now) {          // surfaced in the status and the log, not only in the blob
    status.check_error = check.error;
    console.error(`check failed: ${check.error}`);
    await store.setJSON("status", status);
  }
  // retention AFTER the check: a snapshot older than KEEP is deleted only once its day is frozen in check_archive
  // (cumulative check since launch); if freezing keeps failing, old snapshots stay (visible error, nothing lost)
  const cutoff = snapshotKey(now - KEEP);
  const frozen = ((await store.get("check_archive", { type: "json" })) || { days: {} }).days;
  const { blobs } = await store.list({ prefix: "snap/" });
  for (const b of blobs) if (b.key <= cutoff && frozen[dayOfKey(b.key)]) await store.delete(b.key);   // ISO keys sort by time
  return status;
}

// Recompute the live check at most once per UTC hour (§A2). A scoring error is stored in the blob (shown on the page),
// never hidden; the forecast of this run is already written.
export async function updateCheck(store, state, now, regions, epoch) {
  const hour = Math.floor(now / HOUR) * HOUR;
  const prev = await store.get("check", { type: "json" });
  if (prev && prev.computed_hour === hour) return prev;
  let blob;
  try {
    const snapshots = await readSnapshots(store);
    const rejectionLog = (await store.get("rejection_log", { type: "json" })) || [];
    const archive = await store.get("check_archive", { type: "json" });
    if (!archive && prev && prev.frozen_days > 0) throw new Error("check_archive is missing although days were frozen before");
    const days = archive ? archive.days : {};
    const res = scoreSnapshots(state, snapshots, now, regions, { epoch, rejectionLog, archive: days });
    if (res.due.length) {                                          // freeze before any of the day's snapshots can expire
      for (const d of res.due) days[d] = res.live_totals[d];
      await store.setJSON("check_archive", { days, updated_at: now });
      blob = checkBlob(scoreSnapshots(state, snapshots, now, regions, { epoch, rejectionLog, archive: days }));
    } else blob = checkBlob(res);
  } catch (e) {
    blob = { ok: false, computed_at: now, computed_hour: hour, error: String(e.message).slice(0, 200) };
  }
  await store.setJSON("check", blob);
  return blob;
}

export async function readSnapshots(store, fromKey = "") {
  const { blobs } = await store.list({ prefix: "snap/" });
  const keys = blobs.map(b => b.key).filter(k => k >= fromKey).sort();
  const values = await Promise.all(keys.map(k => store.get(k, { type: "json" })));
  return keys.map((key, i) => ({ key, value: values[i] })).filter(x => x.value !== null);
}

export async function readPayload(store) {
  const [status, forecast] = await Promise.all([store.get("status", { type: "json" }), store.get("latest", { type: "json" })]);
  return { status, forecast };
}

// GET /api/history (§A3): assembled from the stored state and the last 7 days of snapshots
export async function readHistory(store, now, regions) {
  const [state, epoch] = await Promise.all([store.get("state", { type: "json" }), store.get("check_epoch", { type: "json" })]);
  if (!state) return null;
  const snapshots = await readSnapshots(store, snapshotKey(now - 7 * 24 * HOUR));
  return historyPayload(state, snapshots, now, regions, { epoch });
}
