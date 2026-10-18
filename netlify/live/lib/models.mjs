// M12 model registry on the live site (plans/M12.md §B, §D): "any" H = 1/3/6/12/24 and yellow/red H = 1/3, trained on
// alerts.in.ua history only (M6c-1 recipe). Air-raid alerts ONLY on this path (D-045, approved 2026-10-18); the M8 path
// in live.mjs is untouched. Pure functions: no network, no storage, no token.
// INACTIVE until activation.json says so: then only p_model and p_baseline are produced (no blend weight, no blended p,
// no label of the reserved test week) — plans/M12.md §B.
import { unitIntervals, featuresAt, covered } from "./features.mjs";
import { rawScore } from "./lgb.mjs";
import { coverageAt, levelAt } from "./live.mjs";        // import cycle is safe: only used inside functions

export const MAIN_ALERT_TYPES = ["air_raid"];
const HOUR = 3600e3, DAY = 24 * HOUR, CAP = DAY;
export const N0 = 50, BLEND_WINDOW = 28 * DAY, SETTLE = 3 * HOUR, LOOKBACK = DAY, LATE_AFTER = 15 * 60e3;
const OTHER = { yellow: "red", red: "yellow" };

function upperIdx(arr, x) { let lo = 0, hi = arr.length; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] <= x) lo = m + 1; else hi = m; } return lo; }
const countIn = (arr, lo, hi) => upperIdx(arr, hi) - upperIdx(arr, lo);            // (lo, hi]
const onsetsIn = (arr, lo, hi) => arr.slice(upperIdx(arr, lo), upperIdx(arr, hi));   // (lo, hi]

// merged [a, b) intervals; touching blocks merge (a continuous confirmed span) — as check.mjs
export function mergeIntervals(list) {
  const iv = list.map(([a, b]) => [a, b]).filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
  const out = [];
  for (const [a, b] of iv) {
    if (out.length && a <= out[out.length - 1][1]) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b);
    else out.push([a, b]);
  }
  return out;
}

export function sigmoid(z) { return 1 / (1 + Math.exp(-z)); }

// src/model.py apply_calibration: "none" or Platt on logit(clip(p))
export function calibrate(p, cal) {
  if (cal.decision === "none") return p;
  if (cal.decision !== "platt") throw new Error(`unknown calibration ${cal.decision}`);
  const c = Math.min(Math.max(p, cal.clip), 1 - cal.clip);
  return sigmoid(cal.slope * Math.log(c / (1 - c)) + cal.intercept);
}

// src/grid.py gap_mask_for: the label window (s, s + H] touches a raw hole [g0, g1), or s is in the 24 h after it
export function gapMasked(s, H, gaps) {
  return gaps.some(([g0, g1]) => (s < g1 && s + H >= g0) || (s >= g1 && s < g1 + DAY));
}

// D-025 rolling recent rate (src/baselines.py recent_rate) at tau for label horizon H: eligible hour rows s with
// tau - 14 d <= s <= tau - H, s >= gridStart, not under a capped alert of the type at s, label window not gap-masked;
// y(s) = an onset in (s, s + H]; shrunk toward the unit's TRAIN rate: (k + alpha p_unit) / (n + alpha).
export function recentRate(v, tau, H, pUnit, alpha, windowMs, gridStart, gaps) {
  const lo = Math.max(Math.ceil((tau - windowMs) / HOUR) * HOUR, gridStart);
  const hi = Math.floor((tau - H) / HOUR) * HOUR;
  let k = 0, n = 0;
  for (let s = lo; s <= hi; s += HOUR) {
    if (covered(s, v.ms, v.me) || gapMasked(s, H, gaps)) continue;
    n += 1;
    if (countIn(v.onsets, s, s + H) > 0) k += 1;
  }
  return { k, n, rate: (k + alpha * pUnit) / (n + alpha) };
}

// Air-raid alerts known at tau, by type ("any" = every air-raid alert; yellow/red = its level as known at tau) and the
// unresolved-level zones (typed only), as typed.mjs does for M6-site.
export function knownByType(state, tau) {
  const out = { any: [], yellow: [], red: [] }, unresolved = {};
  for (const r of Object.values(state.records)) {
    if (r.firstSeen > tau || r.start > tau || !MAIN_ALERT_TYPES.includes(r.alert_type)) continue;
    const end = r.end !== null && r.endKnown !== null && r.endKnown <= tau && r.end <= tau ? r.end : null;
    const a = { unit: r.unit, start: r.start, end, id: r.id };
    out.any.push(a);
    const level = levelAt(r, tau);
    if (level === "yellow" || level === "red") out[level].push(a);
    else { const e = end === null ? r.start + CAP : Math.min(end, r.start + CAP); (unresolved[r.unit] ||= []).push([r.start, e]); }
  }
  return { byType: out, unresolved };
}

export function loadRegistry({ registry, models, seed = null, activation }) {
  if (!registry || registry.schema !== 1 || !Array.isArray(registry.models)) throw new Error("m12 registry: bad schema");
  if (!activation || typeof activation.active !== "boolean") throw new Error("m12 activation: need {active: boolean}");
  const items = registry.models.map(m => {
    if (JSON.stringify(m.alert_types) !== JSON.stringify(MAIN_ALERT_TYPES)) throw new Error(`m12 ${m.key}: alert_types ${m.alert_types}`);
    const dump = models[m.key];
    if (!dump || !Array.isArray(dump.tree_info)) throw new Error(`m12 ${m.key}: model dump missing`);
    if (JSON.stringify(dump.feature_names) !== JSON.stringify(m.features)) throw new Error(`m12 ${m.key}: feature order differs`);
    return { ...m, Hms: m.H * HOUR, dump, seed: seed && seed.items ? seed.items[m.key] || null : null };
  });
  if (activation.active) {
    // the switch is allowed only after the reserved week is scored and its last labels have settled (plans/M12.md §B)
    const earliest = registry.earliest_activation;
    if (!Number.isFinite(earliest)) throw new Error("m12 registry: earliest_activation missing");
    if (!Number.isFinite(activation.activated_at) || activation.activated_at < earliest)
      throw new Error(`m12 activation: activated_at must be ms since epoch and >= ${new Date(earliest).toISOString()}`);
    if (typeof activation.test_metrics_sha256 !== "string" || !/^[0-9a-f]{64}$/.test(activation.test_metrics_sha256))
      throw new Error("m12 activation: test_metrics_sha256 of reports/m12/metrics.csv required");
  }
  return { active: activation.active, activated_at: activation.active ? activation.activated_at : null, items };
}

/**
 * Every registry item at tau. ctx: {zones (extended event zones), labelGaps {unit: raw holes}, rej {active:Set, history:Set}}.
 * Returns {active, items: {key: {version, type, H, units: {u: {state, p_model, p_baseline, recent_n, caution}}}}}.
 * Blending (w, p) is added by blendItems() only when the registry is active.
 */
export function registryAt(state, tau, regions, reg, ctx) {
  const { byType, unresolved } = knownByType(state, tau);
  const ivs = { any: unitIntervals(byType.any), yellow: unitIntervals(byType.yellow), red: unitIntervals(byType.red) };
  const inZone = ctx.zones.some(([a, b]) => tau >= a && tau < b);
  const feats = { any: featuresAt(ivs.any, tau, regions, ctx.zones), yellow: featuresAt(ivs.yellow, tau, regions, ctx.zones),
                  red: featuresAt(ivs.red, tau, regions, ctx.zones) };
  const empty = { ms: [], me: [], onsets: [] };
  const items = {};
  for (const m of reg.items) {
    try { items[m.key] = itemAt(m, regions, ivs, feats, unresolved, inZone, tau, ctx, empty); }
    catch (e) {                                      // one bad (type, H) never blocks the others (plans/M12.md §B)
      const gap = Object.fromEntries(regions.units.map(u => [u, { state: "data_gap", p_model: null, p_baseline: null, recent_n: null,
                                                                  caution: ["model_error"] }]));
      items[m.key] = { version: m.version, type: m.type, H: m.H, units: gap, error: String(e.message).slice(0, 200) };
    }
  }
  return { active: reg.active, items };
}

function itemAt(m, regions, ivs, feats, unresolved, inZone, tau, ctx, empty) {
    const units = {};
    for (const u of regions.units) {
      const v = ivs[m.type][u] || empty;
      const f = { ...feats[m.type][u] };
      if (m.type !== "any") { const o = ivs[OTHER[m.type]][u] || empty; f.other_level_active_at_t = inZone ? NaN : (covered(tau, o.ms, o.me) ? 1 : 0); }
      const gaps = [...(ctx.labelGaps[u] || []), ...(m.type === "any" ? [] : (unresolved[u] || []))];
      const pu = m.p_unit[u];
      const base = Number.isFinite(pu) ? recentRate(v, tau, m.Hms, pu, m.alpha, m.recent_window_hours * HOUR, m.grid_start, gaps)
                                       : { k: null, n: null, rate: null };     // no train rows of this unit: explicit gap
      const x = m.features.map(n => f[n]);
      let st = "forecast", pModel = null;
      if (covered(tau, v.ms, v.me)) st = "alert_running";
      else if (inZone || x.some(Number.isNaN) || ctx.rej.active.has(u) || !(Number.isFinite(base.rate) && base.rate >= 0 && base.rate <= 1) ||
               (m.type !== "any" && (unresolved[u] || []).some(([a, e]) => tau >= a && tau < e))) st = "data_gap";
      else {
        pModel = calibrate(sigmoid(rawScore(m.dump, x)), m.calibration);
        if (!(pModel > 0 && pModel < 1)) throw new Error(`m12 ${m.key}: p ${pModel} outside (0, 1)`);
      }
      const caution = [];
      if (!Number.isFinite(pu)) caution.push("no_train_rate");
      if (ctx.rej.history.has(u)) caution.push("rejected_history_record");
      if (ctx.rej.active.has(u)) caution.push("rejected_active_record");
      units[u] = { state: st, p_model: pModel, p_baseline: st === "forecast" ? base.rate : null, recent_n: base.n, caution };
      if (ctx.debug) Object.assign(units[u], { x, active: covered(tau, v.ms, v.me), baseline_any_state: base });
    }
  return { version: m.version, type: m.type, H: m.H, units };
}

// ------------------------------------------------------------------ blend (plans/M12.md §B; newregime/blend.py)
// rows: [{unit, s, y, p_model, p_baseline, events: ["unit|onset"]}] LABELLED rows only. Operational cut-off = the
// validation end: rows with s < cutoff never enter. Window [max(tau - 28 d, cutoff), tau - H].
export function weightAt(rows, tau, H, cutoff, n0 = N0, window = BLEND_WINDOW) {
  if (tau < cutoff) return { w: 0, w_star: null, n: 0, rows_used: 0 };
  const lo = Math.max(tau - window, cutoff), hi = tau - H;
  let num = 0, den = 0, used = 0;
  const ev = new Set();
  for (const r of rows) {
    if (r.s < lo || r.s > hi || (r.y !== 0 && r.y !== 1)) continue;
    used += 1;
    num += (r.p_baseline - r.y) * (r.p_baseline - r.p_model);
    den += (r.p_model - r.p_baseline) ** 2;
    if (r.y === 1) for (const e of r.events) ev.add(e);
  }
  const wStar = used ? (den === 0 ? 0 : num / den) : 0;
  const n = ev.size;
  return { w: (n / (n + n0)) * Math.min(1, Math.max(0, wStar)), w_star: used ? wStar : null, n, rows_used: used };
}

/**
 * Label one archived/pending row (unit, s, H) from the alerts known at `now` (labels may use later knowledge; the
 * stored p never changes). null when not yet labelable: now < s + H + SETTLE, confirmed coverage not continuous over
 * [s - 24 h, s + H], or the unit was under a capped alert of the type at s (reconciled). `forbid` = [a, b): a label
 * window touching it is never resolved (the reserved test week while inactive).
 */
export function labelRow(state, row, type, Hms, now, forbid = null, cache = null) {
  if (now < row.s + Hms + SETTLE) return null;
  if (forbid && row.s < forbid[1] && row.s + Hms > forbid[0]) return null;
  const covKey = type === "any" ? "coverage" : "levelCoverage";            // typed labels need confirmed levels
  const cov = cache && cache.cov ? cache.cov[covKey][row.unit] : mergeIntervals(coverageAt(state, row.unit, now, covKey));
  if (!cov.some(([a, b]) => a <= row.s - LOOKBACK && b >= row.s + Hms)) return null;
  const kb = cache ? null : knownByType(state, now);
  if (type !== "any") {                          // an alert of still-unknown level in the window: label unknown, not 0
    const un = (cache ? cache.unresolved : kb.unresolved)[row.unit] || [];
    if (un.some(([a]) => a > row.s && a <= row.s + Hms)) return null;
  }
  const ivs = cache ? cache[type] : unitIntervals(kb.byType[type]);       // cache: same `now`
  const v = ivs[row.unit] || { ms: [], me: [], onsets: [] };
  if (covered(row.s, v.ms, v.me)) return null;
  const ev = onsetsIn(v.onsets, row.s, row.s + Hms);
  return { ...row, y: ev.length ? 1 : 0, events: ev.map(o => `${row.unit}|${o}`) };
}

// Blend every registry item: only when ACTIVE. history: {key: [labelled rows]} (seed + labelled live/pending rows).
export function blendItems(out, reg, tau, history) {
  if (!reg.active) throw new Error("m12: blending is not allowed while the registry is inactive");
  for (const m of reg.items) {
    const it = out.items[m.key];
    const wi = weightAt(history[m.key] || [], tau, m.Hms, m.blend_cutoff);
    it.weight = wi;
    for (const x of Object.values(it.units)) {
      x.w = wi.w;
      x.p = x.state === "forecast" ? wi.w * x.p_model + (1 - wi.w) * x.p_baseline : null;
    }
  }
  return out;
}

// ------------------------------------------------------------------ live wiring (runner.mjs)
// The same inputs forecastAll (live.mjs) derives at tau: extended event zones, per-unit label gaps (before-history +
// coverage holes) and the rejected-record marks as known at tau. forecastAll itself is not changed (M8 golden).
export function contextAt(state, tau, regions, live) {
  const h = live.holesAt(state, tau, regions);
  const zones = [...h.beforeHistory, ...h.event].map(([a, b]) => [a, b + DAY]);
  const labelGaps = Object.fromEntries(regions.units.map(u => [u, [...h.beforeHistory, ...h.label[u]]]));
  const rej = { active: new Set(), history: new Set() };
  for (const [t, u, where] of state.rejections || []) if (t <= tau && tau - t < live.REJECT_KEEP) rej[where].add(u);
  return { zones, labelGaps, rej };
}

// Compact archived snapshot (snapv2/<UTC hour>): per item and unit [state, p_model, p_baseline, rejected?(0/1), w, p].
// While INACTIVE, w and p are null (no blend is computed).
export function compactSnapshot(out, tau, now) {
  const items = {};
  for (const [key, it] of Object.entries(out.items)) {
    const units = {};
    for (const [u, x] of Object.entries(it.units))
      units[u] = [x.state, x.p_model, x.p_baseline, x.caution.some(c => c.startsWith("rejected_")) ? 1 : 0,
                  out.active ? x.w : null, out.active ? x.p : null];
    items[key] = { version: it.version, type: it.type, H: it.H, units };
  }
  return { schema: 2, tau, written_at: now, active: out.active, items };
}

/**
 * Blend history for every item at `now` (ACTIVE only): the seed's labelled rows, its pending rows and the archived live
 * rows (issue time tau_s > T_seed, row time = tau_s) labelled by labelRow. Seed and live never overlap: a live row
 * with tau_s <= T_seed is ignored (counted). Rows older than now - 28 d - H are evicted.
 */
export function buildHistory(state, reg, snapsV2, now, rejectionLog = []) {
  if (!reg.active) throw new Error("m12: no blend history while the registry is inactive");
  const out = {}, ignored = {};
  const k = knownByType(state, now);
  const kb = k.byType;
  const units = Object.keys(state.coverage || {});
  const cov = { coverage: {}, levelCoverage: {} };
  for (const key of ["coverage", "levelCoverage"]) for (const u of units) cov[key][u] = mergeIntervals(coverageAt(state, u, now, key));
  const cache = { any: unitIntervals(kb.any), yellow: unitIntervals(kb.yellow), red: unitIntervals(kb.red), unresolved: k.unresolved, cov };
  const rej = [...(rejectionLog || []), ...(state.rejections || [])];
  const rejected = (u, s) => rej.some(([t, x]) => x === u && t >= s - LOOKBACK && t <= now);
  for (const m of reg.items) {
    const T = m.seed.T_seed, keep = now - BLEND_WINDOW - m.Hms;
    const rows = m.seed.labelled.filter(r => r.s >= keep);
    ignored[m.key] = 0;
    const cand = m.seed.pending.map(r => ({ unit: r.unit, s: r.s, p_model: r.p_model, p_baseline: r.p_baseline }));
    for (const { key: sk, value: sn } of snapsV2) {
      const it = sn && sn.items && sn.items[m.key];
      if (!it || it.version !== m.version) continue;                      // a new version starts its own history
      if (sn.tau <= T) { ignored[m.key] += 1; continue; }
      const hour = Date.parse(sk.slice(7) + ":00:00.000Z");               // "snapv2/2026-10-26T10"
      if (!(sn.tau >= hour) || sn.tau - hour >= LATE_AFTER) continue;      // late snapshot: as the scorer
      for (const [u, x] of Object.entries(it.units))
        if (x[0] === "forecast" && x[3] === 0) cand.push({ unit: u, s: sn.tau, p_model: x[1], p_baseline: x[2] });
    }
    for (const r of cand) {
      if (r.s < keep || rejected(r.unit, r.s)) continue;
      const l = labelRow(state, r, m.type, m.Hms, now, null, cache);
      if (l) rows.push(l);
    }
    out[m.key] = rows;
  }
  return { history: out, ignored };
}
