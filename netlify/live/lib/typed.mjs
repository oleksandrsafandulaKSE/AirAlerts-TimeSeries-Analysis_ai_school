// M6 typed forecasts on the live site (plans/M6-site.md §3, §5): per alert level (yellow = drones, red = missiles), the
// rolling recent-rate baseline at tau, blended with a typed model once one exists (w = 0 until then). Pure functions.
import { unitIntervals, offsetAt, covered } from "./features.mjs";
import { coverageAt, holes, levelAt, ALERT_TYPES } from "./live.mjs";
// typed targets count the same alert types as M8's approved "any" target (one list; plan §3). Live binding: only read
// inside functions, so the live.mjs <-> typed.mjs import cycle is safe.
export { ALERT_TYPES as TYPED_ALERT_TYPES } from "./live.mjs";

const HOUR = 3600e3, DAY = 24 * HOUR, CAP = DAY;
export const LEVELS = ["yellow", "red"];
export const HORIZON_MINUTES = 60;
export const N0 = 50;                                // M6-definition PROVISIONAL: w = n/(n + n0) * clip(w*, 0, 1)
export const CAUTION_MIN_HOURS = 48;                 // same as live.mjs (M8)

// w = n/(n + n0) * clip(w*, 0, 1)   (plans/M6-definition.md, "Blend shown on the site")
export function blendWeight({ n, n0 = N0, wStar }) {
  if (!(Number.isFinite(n) && n >= 0)) throw new Error(`blend weight: bad n ${n}`);
  if (!(Number.isFinite(n0) && n0 > 0)) throw new Error(`blend weight: bad n0 ${n0}`);
  if (!Number.isFinite(wStar)) throw new Error(`blend weight: bad w* ${wStar}`);
  return (n / (n + n0)) * Math.min(1, Math.max(0, wStar));
}

// p = w * p_model + (1 - w) * p_baseline; w = 0 returns the baseline exactly
export function blend(pModel, pBase, w) {
  if (!(w >= 0 && w <= 1)) throw new Error(`blend: weight ${w} outside [0, 1]`);
  return w === 0 ? pBase : w * pModel + (1 - w) * pBase;
}

function checkModel(m, tau) {
  if (!Array.isArray(m.alert_types) || JSON.stringify([...m.alert_types].sort()) !== JSON.stringify([...ALERT_TYPES].sort()))
    throw new Error(`typed model ${m.version}: alert_types ${m.alert_types} != ${ALERT_TYPES}`);
  if (m.horizon_minutes !== HORIZON_MINUTES) throw new Error(`typed model ${m.version}: horizon ${m.horizon_minutes} != ${HORIZON_MINUTES}`);
  if (!Number.isFinite(m.trained_through) || !Number.isFinite(m.available_at) || m.trained_through + HOUR > m.available_at)
    throw new Error(`typed model ${m.version}: trained_through + 1 h must be <= available_at`);
  if (m.trained_through + HOUR > tau) throw new Error(`typed model ${m.version}: labels reach past tau`);
}

// causal version selection (plan §5): the latest version available at tau; later versions are never used at tau
export function selectModel(versions, tau) {
  if (versions === null || versions === undefined) return null;
  if (!Array.isArray(versions)) throw new Error("typedModel must be a list of versions");
  let best = null;
  for (const m of versions) {
    if (!Number.isFinite(m.available_at)) throw new Error(`typed model ${m.version}: available_at missing`);
    if (m.available_at <= tau && (best === null || m.available_at > best.available_at)) best = m;
  }
  if (best) checkModel(best, tau);
  return best;
}

// Typed alerts of one level as known at tau, plus the unresolved-level holes per unit (plan §3)
function typedKnown(state, tau) {
  const byLevel = Object.fromEntries(LEVELS.map(l => [l, []]));
  const unresolved = {};
  for (const r of Object.values(state.records)) {
    if (r.firstSeen > tau || r.start > tau || !ALERT_TYPES.includes(r.alert_type)) continue;
    const end = r.end !== null && r.endKnown !== null && r.endKnown <= tau && r.end <= tau ? r.end : null;
    const level = levelAt(r, tau);
    if (level === null) {
      const e = end === null ? r.start + CAP : Math.min(end, r.start + CAP);
      (unresolved[r.unit] ||= []).push([r.start, e]);
    } else byLevel[level].push({ unit: r.unit, start: r.start, end });
  }
  return { byLevel, unresolved };
}

function intersect(a, b) {
  const out = [];
  for (const [a0, a1] of a) for (const [b0, b1] of b) { const lo = Math.max(a0, b0), hi = Math.min(a1, b1); if (hi > lo) out.push([lo, hi]); }
  return out;
}

// days of typed history held complete for all units (plan §4): intersection of typed coverage, minus unresolved zones
export function historyDays(state, tau, regions, unresolved) {
  let acc = [[state.historyStart, tau]];
  for (const u of regions.units) {
    // coverage = complement of its holes within [historyStart, tau), minus this unit's unresolved-level zones
    const notCovered = [...holes(coverageAt(state, u, tau, "levelCoverage"), state.historyStart, tau), ...(unresolved[u] || [])];
    acc = intersect(acc, holes(notCovered, state.historyStart, tau));
  }
  const len = acc.reduce((s, [a, b]) => s + (b - a), 0);
  return { days: Math.floor(len / DAY), since: acc.length ? Math.min(...acc.map(([a]) => a)) : null };
}

// zones: the M8 extended event zones (hole + 24 h) used by forecastAll
// rej: units with a rejected record as known at tau (from live.mjs forecastAll): ACTIVE -> typed data gap (an alert of
// unknown level may be running), history -> caution (a past typed label may be missing), as for "any".
export function typedAt(state, tau, regions, zones, typedVersions = null, rej = { active: new Set(), history: new Set() }) {
  const typedModel = selectModel(typedVersions, tau);
  const inZone = zones.some(([a, b]) => tau >= a && tau < b);
  const { byLevel, unresolved } = typedKnown(state, tau);
  const gaps = {}, hasCoverage = {};
  for (const u of regions.units) {
    const cov = coverageAt(state, u, tau, "levelCoverage");
    hasCoverage[u] = cov.length > 0;
    gaps[u] = [[-8.64e15, state.historyStart], ...holes(cov, state.historyStart, tau), ...(unresolved[u] || [])];
  }
  const units = Object.fromEntries(regions.units.map(u => [u, {}]));
  const weights = {};
  for (const level of LEVELS) {
    const ivs = unitIntervals(byLevel[level]);
    const off = offsetAt(ivs, tau, regions, state.historyStart, gaps);
    let w = 0, wInfo = null;
    if (typedModel) {
      const wi = typedModel.weight(level, tau, { state, regions, zones });
      w = blendWeight(wi);
      wInfo = { w, n: wi.n, n0: wi.n0 ?? N0, w_star: wi.wStar };
    }
    weights[level] = wInfo;
    for (const u of regions.units) {
      const v = ivs[u] || { ms: [], me: [] }, o = off[u];
      let st = "forecast";
      if (covered(tau, v.ms, v.me)) st = "level_active";
      else if (inZone || !hasCoverage[u] || rej.active.has(u) || (unresolved[u] || []).some(([a, e]) => tau >= a && tau < e) || o.rate === null) st = "data_gap";
      let p = null, pModel = null;
      if (st === "forecast") {
        if (typedModel) {
          pModel = typedModel.predict(level, u, tau, { state, regions, zones });
          if (!(pModel > 0 && pModel < 1)) throw new Error(`typed model p ${pModel} outside (0, 1)`);
        }
        p = typedModel ? blend(pModel, o.rate, w) : o.rate;
      }
      // p_baseline = the two-week rate (shown even when that level is active); p = the forecast, only in state "forecast".
      // The baseline can be exactly 0 (a unit that has never had that level: q = 0), as in improve/live_ref.py; only a
      // MODEL's p is required to lie in (0, 1).
      const caution = [];
      if (st === "forecast" && o.n < CAUTION_MIN_HOURS) caution.push("few_hours");
      if (rej.history.has(u)) caution.push("rejected_history_record");
      if (rej.active.has(u)) caution.push("rejected_active_record");
      units[u][level] = { state: st, p, p_baseline: o.rate, p_model: pModel, w, recent_k: o.k, recent_n: o.n, caution };
    }
  }
  const hd = historyDays(state, tau, regions, unresolved);
  const meta = { label: "in training", mode: typedModel ? "blend" : "baseline_only",
                 model: typedModel ? { version: typedModel.version, trained_through: typedModel.trained_through,
                                       available_at: typedModel.available_at } : null,
                 weights, alert_types: ALERT_TYPES, levels: LEVELS, horizon_minutes: HORIZON_MINUTES,
                 history_days: hd.days, history_since: hd.since };
  return { units, meta };
}

// The typed section failed (bad model version, model output outside (0, 1), ...): every unit shows a typed data gap
// and the error is carried in the payload (and status.typed_error); the "any" forecast is unaffected.
export function typedFailure(regions, err) {
  const gap = { state: "data_gap", p: null, p_baseline: null, p_model: null, w: 0, recent_k: null, recent_n: null, caution: ["typed_error"] };
  const units = Object.fromEntries(regions.units.map(u => [u, { yellow: { ...gap, caution: [...gap.caution] }, red: { ...gap, caution: [...gap.caution] } }]));
  return { units, meta: { label: "in training", mode: "error", error: String(err && err.message || err).slice(0, 200), model: null,
                          weights: { yellow: null, red: null }, alert_types: ALERT_TYPES, levels: LEVELS,
                          horizon_minutes: HORIZON_MINUTES, history_days: null, history_since: null } };
}

// Monthly chart contract (plan §5): written by M6c-1 / M6b, served as payload.typed_monthly; a bad file throws.
const MONTH_KEYS = ["month", "type", "brier_skill_vs_baseline", "w_mean", "n_rows", "n_onsets"];
export function validMonthly(m) {
  if (!m || m.schema !== 1 || !Array.isArray(m.months)) throw new Error("typed_monthly: need {schema: 1, months: [...]}");
  const seen = new Set();
  for (const r of m.months) {
    if (!r || typeof r !== "object" || Object.keys(r).sort().join() !== [...MONTH_KEYS].sort().join())
      throw new Error(`typed_monthly: a row must have exactly ${MONTH_KEYS.join(", ")}`);
    if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(r.month)) throw new Error(`typed_monthly: bad month ${r.month}`);
    if (!["any", "yellow", "red"].includes(r.type)) throw new Error(`typed_monthly: bad type ${r.type}`);
    if (!(Number.isFinite(r.brier_skill_vs_baseline) && r.brier_skill_vs_baseline <= 1)) throw new Error("typed_monthly: bad Brier skill");
    if (!(Number.isFinite(r.w_mean) && r.w_mean >= 0 && r.w_mean <= 1)) throw new Error("typed_monthly: w_mean outside [0, 1]");
    if (!(Number.isInteger(r.n_rows) && r.n_rows > 0 && Number.isInteger(r.n_onsets) && r.n_onsets >= 0 && r.n_onsets <= r.n_rows))
      throw new Error("typed_monthly: bad counts");
    const k = `${r.month}/${r.type}`;
    if (seen.has(k)) throw new Error(`typed_monthly: duplicate ${k}`);
    seen.add(k);
  }
  return m;
}
