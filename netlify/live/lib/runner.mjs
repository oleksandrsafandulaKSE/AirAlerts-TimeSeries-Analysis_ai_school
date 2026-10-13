// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";

export const API = "https://api.alerts.in.ua/v1";
const HOUR = 3600e3, SNAPSHOT_DAYS = 7, FETCH_TIMEOUT = 8000;
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
  await store.setJSON(snapshotKey(now), forecast);    // one snapshot per UTC hour (last write in the hour wins)
  const cutoff = snapshotKey(now - SNAPSHOT_DAYS * 24 * HOUR);
  const { blobs } = await store.list({ prefix: "snap/" });
  for (const b of blobs) if (b.key <= cutoff) await store.delete(b.key);   // ISO hour keys sort chronologically
  await store.setJSON("status", status);
  return status;
}

export async function readPayload(store) {
  const [status, forecast] = await Promise.all([store.get("status", { type: "json" }), store.get("latest", { type: "json" })]);
  return { status, forecast };
}
