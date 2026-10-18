// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";
import { scoreSnapshots, scoreSeries, checkBlob, historyPayload, dayOfKey, KEEP, LATE_AFTER, LOOKBACK } from "./check.mjs";
import * as live from "./live.mjs";
import { registryAt, contextAt, compactSnapshot, buildHistory, blendItems, BLEND_WINDOW } from "./models.mjs";
import { validMonthly } from "./typed.mjs";

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
export const snapshotKeyV2 = (t) => `snapv2/${new Date(Math.floor(t / HOUR) * HOUR).toISOString().slice(0, 13)}`;

// typedModel: null (no typed model yet: baseline only, w = 0) or a list of model versions (plans/M6-site.md §5)
// m12: null, or the loaded M12 registry (models.mjs loadRegistry). Inactive: archived predictions only (plans/M12.md §B).
export async function runUpdate({ fetchFn, store, token, now, model, regions, seed, timeoutMs = FETCH_TIMEOUT, typedModel = null,
                                  m12 = null }) {
  const status = { ok: false, at: now, active_alerts: null, excluded: null, rejected: [], history_unit: null,
                   history_ok: null, history_failing: [], error: null, level_unknown: 0, typed_error: null };
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
    status.level_unknown += res.levelUnknown;
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
    status.level_unknown += res.levelUnknown;
    status.history_ok = true;
    state.historyFail[unit] = 0;
  } catch (e) {
    status.history_ok = false;
    status.history_error = e.message;                 // coverage of this unit does not advance; streak shown on the page
    state.historyFail[unit] = (state.historyFail[unit] || 0) + 1;
  }
  status.history_failing = Object.entries(state.historyFail).filter(([, n]) => n >= 2).map(([u, n]) => ({ unit: u, consecutive: n }));
  const forecast = forecastAll(state, now, model, regions, typedModel);
  status.typed_error = forecast.typed.error || null;          // the "any" forecast is still written (typed is in training)
  // M12: an error on the new path never blocks the M8 forecast; it is shown in the status (no silent fallback)
  let m12out = null;
  if (m12) {
    status.m12 = { active: m12.active, error: null };
    try {
      m12out = registryAt(state, now, regions, m12, contextAt(state, now, regions, live));
      if (m12.active) {
        const snaps = await readSnapshots(store, snapshotKeyV2(now - BLEND_WINDOW - 25 * HOUR), "snapv2/");
        const rejectionLog = (await store.get("rejection_log", { type: "json" })) || [];
        blendItems(m12out, m12, now, buildHistory(state, m12, snaps, now, rejectionLog).history);
        forecast.m12 = { active: true, tau: now, items: m12out.items };    // the switch (plans/M12.md §E)
      }
      const bad = Object.entries(m12out.items).filter(([, it]) => it.error).map(([k, it]) => `${k}: ${it.error}`);
      if (bad.length) status.m12.error = bad.join("; ").slice(0, 300);             // per-item errors, others still served
    } catch (e) { status.m12.error = String(e.message).slice(0, 200); m12out = null; }
  }
  status.ok = true;
  await store.setJSON("state", state);
  await store.setJSON("latest", forecast);
  if (m12out) {                                                   // first successful write in the UTC hour wins (as M11)
    try {                                                         // a storage error here never blocks the M8 writes below
      const k2 = snapshotKeyV2(now);
      if ((await store.get(k2, { type: "json" })) === null) await store.setJSON(k2, compactSnapshot(m12out, now, now));
    } catch (e) { status.m12.error = `snapv2 write: ${String(e.message).slice(0, 180)}`; }
  }
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
  if (m12) {
    try {
      await updateCheckV2(store, state, now, regions, m12);
      // retention: inactive -> 35 days (nothing is ever scored from them). ACTIVE -> kept (no silent rolling window:
      // the cumulative per-series archive is session-2 work, plans/M12.md §D; growth ~10 KB per hour).
      if (!m12.active) {
        const cut2 = snapshotKeyV2(now - KEEP);
        const { blobs: b2 } = await store.list({ prefix: "snapv2/" });
        for (const b of b2) if (b.key <= cut2) await store.delete(b.key);
      }
    } catch (e) { status.m12.error = `check_v2 / retention: ${String(e.message).slice(0, 180)}`; }
    await store.setJSON("status", status);
  }
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

// M12 per-series check (plans/M12.md §D): inactive -> {status: "inactive"} and nothing is computed
export async function updateCheckV2(store, state, now, regions, m12) {
  const hour = Math.floor(now / HOUR) * HOUR;
  const prev = await store.get("check_v2", { type: "json" });
  if (prev && prev.computed_hour === hour) return prev;
  let blob;
  try {
    if (!m12.active) blob = { status: "inactive", computed_hour: hour, series: [] };
    else {
      const snaps = await readSnapshots(store, "", "snapv2/");
      const rejectionLog = (await store.get("rejection_log", { type: "json" })) || [];
      blob = { status: "active", computed_hour: hour, exploratory: true,
               series: m12.items.map(m => scoreSeries(state, snaps, now, regions, { key: m.key, version: m.version, type: m.type,
                 H: m.Hms, active: true, activatedAt: m12.activated_at, rejectionLog })) };
    }
  } catch (e) { blob = { status: "error", computed_hour: hour, error: String(e.message).slice(0, 200) }; }
  await store.setJSON("check_v2", blob);
  return blob;
}

export async function readSnapshots(store, fromKey = "", prefix = "snap/") {
  const { blobs } = await store.list({ prefix });
  const keys = blobs.map(b => b.key).filter(k => k >= fromKey).sort();
  const values = await Promise.all(keys.map(k => store.get(k, { type: "json" })));
  return keys.map((key, i) => ({ key, value: values[i] })).filter(x => x.value !== null);
}

// typed_monthly: the monthly chart data (netlify/live/data/typed_monthly.json, plans/M6-site.md §5). A bad file never
// breaks the main GET: it is replaced by null and the error is returned next to it (the page says so).
export async function readPayload(store, monthly = { schema: 1, months: [] }) {
  let typed_monthly = monthly, typed_monthly_error = null;
  try { validMonthly(monthly); } catch (e) { typed_monthly = null; typed_monthly_error = e.message.slice(0, 200); }
  const [status, forecast] = await Promise.all([store.get("status", { type: "json" }), store.get("latest", { type: "json" })]);
  return { status, forecast, typed_monthly, typed_monthly_error };
}

// GET /api/history (§A3): assembled from the stored state and the last 7 days of snapshots
export async function readHistory(store, now, regions) {
  const [state, epoch] = await Promise.all([store.get("state", { type: "json" }), store.get("check_epoch", { type: "json" })]);
  if (!state) return null;
  const snapshots = await readSnapshots(store, snapshotKey(now - 7 * 24 * HOUR));
  return historyPayload(state, snapshots, now, regions, { epoch });
}
