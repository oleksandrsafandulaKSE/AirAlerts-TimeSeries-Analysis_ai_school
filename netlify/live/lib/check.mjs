// Live forecast check and history (plans/M11.md §A2-§A3). Pure functions: no network, no storage, no token.
// EXPLORATORY: API data, its own section, never mixed with the study's official metrics (D-007, D-015).
import { unitIntervals, covered } from "./features.mjs";
import { knownAt, coverageAt } from "./live.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR;
export const SETTLE = 3 * HOUR;               // a snapshot is scored only from tau + 1 h + SETTLE on
export const LATE_AFTER = 15 * MIN;           // tau >= hour start + 15 min -> late, not scored
export const LOOKBACK = DAY;                  // confirmed coverage must span [tau - 24 h, tau + 1 h]
export const KEEP = 35 * DAY;                 // snapshot and rejection_log retention
export const LOW_N_ROWS = 200, LOW_N_POS = 20;
// exclusion reasons, in the order they are tested (each row is counted under the first one that applies)
export const REASONS = ["legacy", "late", "unsettled", "not_forecast", "rejected_at_issue", "coverage_hole",
                        "rejected_after_issue", "reconciled_under_alert"];

export const hourOfKey = key => Date.parse(key.slice(5) + ":00:00.000Z");      // "snap/2026-10-12T16" -> ms

// late / legacy from the key, the stored tau and written_at, and the check_epoch (first run of the M11 runner):
// legacy = written before the first M11 run (no written_at, or written_at < epoch), so the first M11 hour is kept
export function snapshotFlags(key, snap, epoch) {
  const h = hourOfKey(key);
  const legacy = epoch === null || epoch === undefined || !snap || typeof snap.written_at !== "number" || snap.written_at < epoch;
  const late = !snap || !(snap.tau >= h) || snap.tau - h >= LATE_AFTER;
  return { hour: h, late, legacy };
}

// merged [a, b) intervals; touching blocks merge (a continuous confirmed span)
export function mergeIntervals(list) {
  const iv = list.map(([a, b]) => [a, b]).filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
  const out = [];
  for (const [a, b] of iv) {
    if (out.length && a <= out[out.length - 1][1]) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b);
    else out.push([a, b]);
  }
  return out;
}
const spans = (merged, a, b) => merged.some(([x, y]) => x <= a && y >= b);

function upperIdx(arr, x) { let lo = 0, hi = arr.length; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] <= x) lo = m + 1; else hi = m; } return lo; }
const countIn = (arr, lo, hi) => upperIdx(arr, hi) - upperIdx(arr, lo);              // (lo, hi]

function acc() { return { rows: 0, positives: 0, sum_bp: 0, sum_br: 0 }; }
function add(a, p, rr, y) { a.rows += 1; a.positives += y; a.sum_bp += (p - y) ** 2; a.sum_br += (rr - y) ** 2; }
// pooled BSS = 1 - sum B_p / sum B_rr (never an average of per-day skills); null with a reason when undefined
export function summarise(a) {
  const out = { rows: a.rows, positives: a.positives, base_rate: null, brier_p: null, brier_recent_rate: null,
                bss: null, bss_reason: null, low_n: a.rows < LOW_N_ROWS || a.positives < LOW_N_POS };
  if (a.rows === 0) { out.bss_reason = "no rows"; return out; }
  out.base_rate = a.positives / a.rows;
  out.brier_p = a.sum_bp / a.rows;
  out.brier_recent_rate = a.sum_br / a.rows;
  if (a.sum_br === 0) out.bss_reason = "zero reference loss";
  else out.bss = 1 - a.sum_bp / a.sum_br;
  return out;
}
export const binOf = p => Math.min(9, Math.floor(p * 10));       // [0, 0.1), ..., [0.9, 1.0]; p = 1 -> last bin

// Rejections known to the scorer: the persistent log (35 d + 24 h) and the live 24 h marks (same entries, union is safe)
function rejectionTimes(state, rejectionLog, unit) {
  const out = [];
  for (const [t, u] of [...(rejectionLog || []), ...((state && state.rejections) || [])]) if (u === unit) out.push(t);
  return out;
}

// Raw per-day totals (sums, never ratios): what a frozen day keeps after its snapshots expire (cumulative check)
function dayTotals(regions) {
  return { overall: acc(), groups: Object.fromEntries([...new Set(Object.values(regions.groups))].map(g => [g, acc()])),
           units: Object.fromEntries(regions.units.map(u => [u, acc()])),
           bins: Array.from({ length: 10 }, () => ({ rows: 0, sum_p: 0, positives: 0 })),
           excluded: Object.fromEntries(REASONS.map(r => [r, 0])), snapshots: 0 };
}
function merge(into, a) {
  const m = (x, y) => { x.rows += y.rows; x.positives += y.positives; x.sum_bp += y.sum_bp; x.sum_br += y.sum_br; };
  m(into.overall, a.overall);
  for (const [g, v] of Object.entries(a.groups)) m(into.groups[g] ||= acc(), v);
  for (const [u, v] of Object.entries(a.units)) m(into.units[u] ||= acc(), v);
  a.bins.forEach((b, i) => { into.bins[i].rows += b.rows; into.bins[i].sum_p += b.sum_p; into.bins[i].positives += b.positives; });
  for (const [k, n] of Object.entries(a.excluded)) into.excluded[k] = (into.excluded[k] || 0) + n;
  into.snapshots += a.snapshots;
}
export const dayOfKey = key => key.slice(5, 15);                    // "snap/2026-10-12T16" -> "2026-10-12" (UTC)
// a day is frozen once now >= day start + KEEP - 1 day: all its snapshots still exist (deletion starts at day + KEEP)
// and it settled long ago; the runner deletes a snapshot only after its day is frozen
export const freezeDue = (day, now) => Date.parse(day + "T00:00:00Z") + KEEP - DAY <= now;

/**
 * Score archived hourly snapshots against the alerts as known at `now` (estimand: plans/M11.md §A2, PROVISIONAL).
 * snapshots: [{key, value}] as stored ("snap/<UTC hour>"). opts: {epoch, rejectionLog, archive}.
 * archive: {day: raw totals} of FROZEN days (cumulative since launch, human 2026-10-18); a frozen day is never
 * re-scored from its snapshots, so nothing is counted twice. `due` lists the days to freeze now.
 * p and recent_rate are read ONLY from the stored snapshot; labels and reconciliation may use later knowledge.
 */
export function scoreSnapshots(state, snapshots, now, regions, { epoch = null, rejectionLog = [], archive = {} } = {}) {
  const ivs = unitIntervals(knownAt(state, now));
  const empty = { ms: [], me: [], onsets: [] };
  const cov = Object.fromEntries(regions.units.map(u => [u, mergeIntervals(coverageAt(state, u, now))]));
  const rej = Object.fromEntries(regions.units.map(u => [u, rejectionTimes(state, rejectionLog, u)]));
  const live = {};
  const rows = [];
  for (const { key, value: snap } of [...snapshots].sort((a, b) => (a.key < b.key ? -1 : 1))) {
    const day = dayOfKey(key);
    if (archive[day]) continue;                                    // frozen: counted from the archive only
    const T = live[day] ||= dayTotals(regions);
    T.snapshots += 1;
    const fl = snapshotFlags(key, snap, epoch);
    const tau = snap && snap.tau;
    for (const u of regions.units) {
      const x = snap && snap.units ? snap.units[u] : undefined;
      let why = null;
      if (fl.legacy) why = "legacy";
      else if (fl.late) why = "late";
      else if (now < tau + HOUR + SETTLE) why = "unsettled";
      else if (!x || x.state !== "forecast" || typeof x.p !== "number" || typeof x.recent_rate !== "number") why = "not_forecast";
      else if ((x.caution || []).some(c => c === "rejected_history_record" || c === "rejected_active_record")) why = "rejected_at_issue";
      else if (!spans(cov[u], tau - LOOKBACK, tau + HOUR)) why = "coverage_hole";
      else if (rej[u].some(t => t >= tau - LOOKBACK && t <= now)) why = "rejected_after_issue";
      else { const v = ivs[u] || empty; if (covered(tau, v.ms, v.me)) why = "reconciled_under_alert"; }
      if (why) { T.excluded[why] += 1; continue; }
      const v = ivs[u] || empty;
      const y = countIn(v.onsets, tau, tau + HOUR) > 0 ? 1 : 0;          // onset in (tau, tau + 1 h]
      const p = x.p, rr = x.recent_rate;
      add(T.overall, p, rr, y); add(T.groups[regions.groups[u]], p, rr, y); add(T.units[u], p, rr, y);
      const b = T.bins[binOf(p)]; b.rows += 1; b.sum_p += p; b.positives += y;
      rows.push({ unit: u, tau, p, recent_rate: rr, y });
    }
  }
  const all = { ...archive, ...live };
  const total = dayTotals(regions), cum = acc();
  const dayOut = Object.keys(all).sort().map(d => {
    const a = all[d];
    merge(total, a);
    const o = a.overall;
    cum.rows += o.rows; cum.positives += o.positives; cum.sum_bp += o.sum_bp; cum.sum_br += o.sum_br;
    const c = summarise(cum);
    return { day: d, frozen: !!archive[d], ...summarise(o), cumulative_bss: c.bss, cumulative_rows: c.rows };
  });
  const due = Object.keys(live).filter(d => freezeDue(d, now)).sort();
  return {
    computed_at: now, computed_hour: Math.floor(now / HOUR) * HOUR, exploratory: true,
    rules: { settle_hours: SETTLE / HOUR, late_after_min: LATE_AFTER / MIN, lookback_hours: LOOKBACK / HOUR,
             low_n: { rows: LOW_N_ROWS, positives: LOW_N_POS }, epoch, keep_days: KEEP / DAY },
    snapshots: total.snapshots, days_scored: dayOut.filter(d => d.rows > 0).length,
    first_day: dayOut.length ? dayOut[0].day : null, frozen_days: Object.keys(archive).length,
    overall: summarise(total.overall),
    groups: Object.fromEntries(Object.entries(total.groups).map(([g, a]) => [g, summarise(a)])),
    days: dayOut,
    units: Object.fromEntries(Object.entries(total.units).map(([u, a]) => [u, summarise(a)])),
    reliability: total.bins.map((b, i) => ({ lo: i / 10, hi: (i + 1) / 10, rows: b.rows, mean_p: b.rows ? b.sum_p / b.rows : null,
                                             observed: b.rows ? b.positives / b.rows : null })),
    excluded: total.excluded, rows, live_totals: live, due,
  };
}

// The check blob as served: the per-row list stays out (it is only used by tests and for recomputation)
export function checkBlob(result) { const { rows, live_totals, due, ...rest } = result; return { ok: true, ...rest }; }

/**
 * /api/history payload (§A3): last 7 days of hourly snapshots, last 14 days of per-unit physical alerts (union of the
 * raw intervals as known now; open ones flagged), capped "under alert" intervals (D-020, merged), onsets and the
 * confirmed coverage. Derived intervals only: no raw API records, no token.
 */
export function historyPayload(state, snapshots, now, regions, { epoch = null } = {}) {
  const from7 = now - 7 * DAY, from14 = now - 14 * DAY;
  const clip = (list, lo) => list.filter(([a, b]) => b > lo && a < now).map(([a, b]) => [Math.max(a, lo), Math.min(b, now)]);
  const snaps = [];
  for (const { key, value: s } of [...snapshots].sort((a, b) => (a.key < b.key ? -1 : 1))) {
    const fl = snapshotFlags(key, s, epoch);
    if (fl.hour < Math.floor(from7 / HOUR) * HOUR) continue;
    const units = {};
    for (const u of regions.units) { const x = s.units && s.units[u]; units[u] = x ? [x.p, x.state, x.recent_rate] : null; }
    snaps.push({ hour: fl.hour, tau: s.tau, late: fl.late, legacy: fl.legacy, units });
  }
  const ivs = unitIntervals(knownAt(state, now));
  const out = {};
  for (const u of regions.units) {
    const phys = [], open = [];
    for (const r of Object.values(state.records)) {
      if (r.unit !== u || r.start > now) continue;
      const endKnown = r.end !== null && r.endKnown !== null && r.endKnown <= now;
      if (endKnown) { if (r.end > from14) phys.push([r.start, r.end]); continue; }
      // end not known yet: open while listed in ACTIVE; a vanished id is over from its first absence (shown dashed)
      const gone = r.absent.find(([, b]) => b === null);
      open.push([r.start, gone ? gone[0] : now, gone ? "vanished" : "active"]);
    }
    const v = ivs[u] || { ms: [], me: [], onsets: [] };
    out[u] = {
      physical: clip(mergeIntervals(phys), from14),
      open: open.filter(([, b]) => b > from14).map(([a, b, k]) => [Math.max(a, from14), b, k]),
      capped: clip(v.ms.map((a, i) => [a, v.me[i]]), from14),
      onsets: v.onsets.filter(t => t > from14 && t <= now),
      coverage: clip(mergeIntervals(coverageAt(state, u, now)), from14),
    };
  }
  return { now, exploratory: true, from_7d: from7, from_14d: from14, snapshots: snaps, units: out };
}
