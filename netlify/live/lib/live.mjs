// Live state and forecasts (plans/M8.md §2). Pure functions: no network, no storage, no token.
import { unitIntervals, featuresAt, offsetAt, covered } from "./features.mjs";
import { predictOffset } from "./lgb.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR, CAP = DAY;
export const HISTORY_WINDOW = 30 * DAY;
export const POLL_GAP_MAX = 5 * MIN;          // polls further apart leave a hole (plans/M8.md §2: a failed ACTIVE poll > 5 min)
export const STALE_AFTER = 5 * MIN;
export const COMPACT_AFTER = 8 * DAY;      // coverage blocks confirmed this long before the latest call are merged; this
                                            // only delays visibility for replays at old tau. The M11 check reads coverage
                                            // as known NOW (union unchanged by merging), so 35-day retention is unaffected
// caution: two-week rate from few hours, or above the 99.9th percentile of the training offsets (0.647; max 0.811,
// 742,114 fit rows, official data) -> the model extrapolates there
export const CAUTION_MIN_HOURS = 48, CAUTION_RATE = 0.65;
// human decision: ALL alert types of the API (the documented set; unknown types are rejected record by record)
export const ALERT_TYPES = ["air_raid", "artillery_shelling", "urban_fights", "chemical", "nuclear"];
export const REJECT_KEEP = DAY;               // rejected-record marks are kept this long (unit shows data gap / caution)

export class DataError extends Error {}

export function emptyState(historyStart) {
  return { records: {}, coverage: {}, polls: [], rotation: 0, historyStart, rejections: [], historyFail: {} };
}

function parseTime(s, field, required = false) {
  if (s === null || s === undefined) { if (required) throw new DataError(`${field} missing`); return null; }
  if (typeof s !== "string" || !s.endsWith("Z")) throw new DataError(`${field}: timestamp without 'Z' (UTC): ${s}`);
  const t = Date.parse(s);
  if (Number.isNaN(t)) throw new DataError(`${field}: unparseable timestamp ${s}`);
  return t;
}

export function mapUnit(name, regions) {
  if (regions.excluded_api_names.includes(name)) return null;               // Luhanska, Crimea, Sevastopol (D-008)
  const u = regions.api_oblast_name[name];
  if (!u) throw new DataError(`unknown oblast name from the API: ${name}`);
  return u;
}

function mergeIntervals(list) {
  const iv = list.slice().sort((a, b) => a[0] - b[0]);
  const out = [];
  for (const [a, b] of iv) {
    if (out.length && a <= out[out.length - 1][1]) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b);
    else out.push([a, b]);
  }
  return out;
}

// One API record -> normalised fields (raises DataError on schema problems; err.unit = the unit if it is known)
function normalise(a, regions) {
  if (a === null || typeof a !== "object") throw new DataError("record is not an object");
  const unit = mapUnit(a.location_oblast, regions);            // unknown name raises WITHOUT a unit (national problem)
  if (unit === null) return null;
  try {
    if (a.id === null || a.id === undefined || a.id === "") throw new DataError("id missing");
    if (!ALERT_TYPES.includes(a.alert_type)) throw new DataError(`unexpected alert_type ${a.alert_type}`);
    const start = parseTime(a.started_at, "started_at", true);
    const end = parseTime(a.finished_at, "finished_at");
    if (end !== null && end < start) throw new DataError(`alert ${a.id}: finished_at < started_at`);
    return { id: String(a.id), unit, level: a.location_type, alert_type: a.alert_type, start, end,
             updated: parseTime(a.updated_at, "updated_at", true) };
  } catch (e) { e.unit = unit; throw e; }
}

// Validate a batch record by record. A bad record of a KNOWN unit is rejected and marked (that unit shows "data gap"
// while marked); an unknown oblast name cannot be attributed, so it fails the whole batch (a schema change needs a human).
function validated(state, alerts, t, regions, where) {
  if (!Array.isArray(alerts)) throw new DataError(`${where}: alerts is not an array`);
  const ok = [], rejected = [];
  for (const raw of alerts) {
    try { const a = normalise(raw, regions); ok.push(a); }
    catch (e) {
      if (!(e instanceof DataError) || !e.unit) throw e;
      rejected.push({ unit: e.unit, reason: e.message.slice(0, 120) });
    }
  }
  return { ok, rejected };
}

// marks are written only once the whole batch has been accepted
function markRejected(state, rejected, t, where) {
  for (const r of rejected) state.rejections.push([t, r.unit, where]);
  state.rejections = state.rejections.filter(([r]) => r > t - REJECT_KEEP);
}

// ACTIVE poll at pollTime: new ids appear (first seen now); open records of covered units that vanished keep an
// UNKNOWN end (D-027: open, 24 h cap) until history reconciliation supplies the true end.
export function applyActive(state, alerts, pollTime, regions) {
  const seen = new Set();
  let added = 0, skipped = 0;
  const { ok, rejected } = validated(state, alerts, pollTime, regions, "active");
  markRejected(state, rejected, pollTime, "active");
  for (const a of ok) {
    if (a === null) { skipped++; continue; }
    seen.add(a.id);
    const r = state.records[a.id];
    if (!r) {
      state.records[a.id] = { ...a, end: null, firstSeen: pollTime, endKnown: null, endSource: null, absent: [] };
      added++;
    } else {
      if (a.updated > r.updated) r.updated = a.updated;
      const last = r.absent[r.absent.length - 1];
      if (last && last[1] === null) last[1] = pollTime;                     // reappeared in ACTIVE
    }
  }
  for (const r of Object.values(state.records)) {
    const last = r.absent[r.absent.length - 1];
    if (r.end === null && !(last && last[1] === null) && r.firstSeen <= pollTime && !seen.has(r.id) && r.start <= pollTime) {
      r.absent.push([pollTime, null]);                                       // end unknown until reconciled
    }
  }
  const last = state.polls[state.polls.length - 1];
  if (last && pollTime - last[1] <= POLL_GAP_MAX) last[1] = pollTime; else state.polls.push([pollTime, pollTime]);
  return { added, skipped, rejected };
}

// month_ago history for one unit at callTime: exact starts/ends (latest parsed updated_at wins); confirms coverage
// [callTime - 30 d, callTime) for that unit.
export function applyHistory(state, unit, alerts, callTime, regions) {
  const { ok, rejected } = validated(state, alerts, callTime, regions, "history");
  for (const a of ok) {                                         // check pass: nothing is written if any check fails
    if (a === null) continue;
    if (a.unit !== unit) throw new DataError(`history for ${unit} returned an alert of ${a.unit}`);
    const r = state.records[a.id];
    if (r && r.unit !== a.unit) throw new DataError(`alert ${a.id} changed unit`);
  }
  markRejected(state, rejected, callTime, "history");
  for (const a of ok) {                                         // nothing is written before the whole batch is checked
    if (a === null) continue;
    const r = state.records[a.id];
    if (!r) {
      state.records[a.id] = { ...a, firstSeen: callTime, endKnown: a.end === null ? null : callTime,
                              endSource: a.end === null ? null : "history", absent: [] };
    } else if (a.updated >= r.updated) {
      r.updated = a.updated;
      if (a.end !== null && r.end === null) { r.end = a.end; r.endKnown = callTime; r.endSource = "history"; }
    }
  }
  // each block [a, b, confirmedAt]: known only from confirmedAt on (truncation-exact); old blocks are compacted, which
  // only ever DELAYS their visibility for replays far in the past (conservative, never leaky)
  const blocks = [...(state.coverage[unit] || []), [callTime - HISTORY_WINDOW, callTime, callTime]];
  const old = blocks.filter(([, , c]) => c < callTime - COMPACT_AFTER), recent = blocks.filter(([, , c]) => c >= callTime - COMPACT_AFTER);
  const merged = [];
  for (const [a, b, c] of old.sort((x, y) => x[0] - y[0])) {
    const m = merged[merged.length - 1];
    if (m && a <= m[1]) { m[1] = Math.max(m[1], b); m[2] = Math.max(m[2], c); } else merged.push([a, b, c]);
  }
  state.coverage[unit] = [...merged, ...recent];
  return { rejected };
}

// coverage of a unit as known at tau: blocks confirmed at or before tau
export function coverageAt(state, unit, tau) {
  return (state.coverage[unit] || []).filter(([, , c]) => c <= tau).map(([a, b]) => [a, Math.min(b, tau)]);
}

// Alerts as known at tau: first seen <= tau; the end only if it was known at tau.
export function knownAt(state, tau) {
  const out = [];
  for (const r of Object.values(state.records)) {
    if (r.firstSeen > tau || r.start > tau) continue;
    const end = r.end !== null && r.endKnown !== null && r.endKnown <= tau && r.end <= tau ? r.end : null;
    out.push({ unit: r.unit, start: r.start, end });
  }
  return out;
}

// Holes = complement of coverage within [historyStart, tau); returned as raw [h0, h1)
function holes(intervals, from, to) {
  const out = [];
  let cur = from;
  for (const [a, b] of mergeIntervals(intervals.map(([a, b]) => [Math.max(a, from), Math.min(b, to)]).filter(([a, b]) => b > a))) {
    if (a > cur) out.push([cur, a]);
    cur = Math.max(cur, b);
  }
  if (cur < to) out.push([cur, to]);
  return out;
}

export function holesAt(state, tau, regions) {
  const label = {}, event = [];
  const polls = state.polls.map(([a, b]) => [a, b + POLL_GAP_MAX]);
  for (const u of regions.units) {
    const conf = coverageAt(state, u, tau);
    label[u] = holes(conf, state.historyStart, tau);
    // EVENT inputs: confirmed history OR the ACTIVE-poll record for the unconfirmed tail (human-approved exception)
    for (const h of holes([...conf, ...polls], state.historyStart, tau)) event.push(h);
  }
  return { label, event, beforeHistory: [[-8.64e15, state.historyStart]] };
}

export function forecastAll(state, tau, model, regions) {
  const known = knownAt(state, tau);
  const ivs = unitIntervals(known);
  const h = holesAt(state, tau, regions);
  const zones = [...h.beforeHistory, ...h.event].map(([a, b]) => [a, b + DAY]);           // extended zones
  const feats = featuresAt(ivs, tau, regions, zones);
  const gapsByUnit = Object.fromEntries(regions.units.map(u => [u, [...h.beforeHistory, ...h.label[u]]]));
  const off = offsetAt(ivs, tau, regions, state.historyStart, gapsByUnit);
  // physical alert = shown as an outline on the map, NOT a model input: an alert listed in the latest ACTIVE poll at or
  // before tau (vanished ids are over even before history reconciles their exact end), or an end known to be after tau
  const physical = {};
  for (const r of Object.values(state.records)) {
    if (r.firstSeen > tau || r.start > tau) continue;
    const endKnown = r.end !== null && r.endKnown !== null && r.endKnown <= tau;
    const on = endKnown ? r.end > tau : !r.absent.some(([a, b]) => a <= tau && (b === null || b > tau));
    if (on) physical[r.unit] = true;
  }
  // rejected records as known at tau (within REJECT_KEEP): from ACTIVE -> the unit's state is unknown (data gap);
  // from history -> caution (a past record may be missing from its labels). Only that unit is marked (limitation).
  const rej = { active: new Set(), history: new Set() };
  for (const [t, u, where] of state.rejections || []) if (t <= tau && tau - t < REJECT_KEEP) rej[where].add(u);
  const confirmedUntil = u => { const c = coverageAt(state, u, tau); return c.length ? Math.max(...c.map(([, b]) => b)) : null; };
  const units = {};
  for (const u of regions.units) {
    const f = feats[u], o = off[u];
    const x = model.feature_names.map(n => f[n]);
    let p = null, state_ = "forecast";
    const v = ivs[u] || { ms: [], me: [] };
    if (covered(tau, v.ms, v.me)) state_ = "alert_running";                    // D-020 capped mask: no forecast
    else if (x.some(Number.isNaN) || o.rate === null || rej.active.has(u)) state_ = "data_gap";
    else p = predictOffset(model, x, o.rate);
    const caution = [];
    if (o.rate !== null && o.n < CAUTION_MIN_HOURS) caution.push("few_hours");
    if (o.rate !== null && o.rate > CAUTION_RATE) caution.push("beyond_training");
    if (rej.history.has(u)) caution.push("rejected_history_record");
    if (rej.active.has(u)) caution.push("rejected_active_record");
    units[u] = { p, state: state_, physical_alert: !!physical[u], recent_rate: o.rate, recent_hours: o.n, caution,
                 confirmed_until: confirmedUntil(u),
                 alerts_last_24h: Number.isNaN(f.onsets_last_24h) ? null : f.onsets_last_24h,
                 minutes_since_last_start: Number.isNaN(f.minutes_since_last_start) ? null : f.minutes_since_last_start };
  }
  return { tau, horizon_minutes: 60, units, model: { features: model.feature_names } };
}

export function nextRotationUnit(state, regions) {
  const u = regions.units[state.rotation % regions.units.length];
  state.rotation = (state.rotation + 1) % regions.units.length;
  return u;
}

export function stale(payload, now) {
  if (!payload || !payload.status || !payload.forecast) return true;
  if (payload.status.ok === false) return true;
  return now - payload.forecast.tau > STALE_AFTER;
}
