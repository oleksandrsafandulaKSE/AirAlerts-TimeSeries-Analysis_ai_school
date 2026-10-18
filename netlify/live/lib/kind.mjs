// "If an alert starts, will it be red or yellow?" — the 7-day red-share rule on the live site (plans/M13.md §3; D-044;
// same definition as newregime/redshare.py). Air-raid alerts only (D-045). Pure function, knowledge at tau only:
// an alert counts from firstSeen, its end only once known, its level as known at tau (levels are versions).
//   "any" onset = the start of a merged air-raid interval (D-020 24 h cap); an escalation inside a running interval is
//   not an onset. Colour of an onset: red if a red alert starts at that instant, else unknown if an alert starting then
//   has no level yet, else yellow. Rule at tau over the unit's onsets with start in (tau - 7 d, tau]:
//   M = observed onsets, N = classified (R red + yellow), U = unclassified; share = R / N (null when N = 0).
//   Coverage = confirmed LEVEL history OR the ACTIVE-poll record for the tail since the last history call (the same
//   rule as the M8 event inputs, live.mjs holesAt; history is refreshed one oblast per run, ACTIVE every run and
//   carries levels). A unit not covered over [tau - 7 d, tau] that way -> status "not_enough_data".
//   National share = pooled R / N over the units with full coverage (null with no national data when N = 0).
import { unitIntervals } from "./features.mjs";
import { coverageAt, levelAt, POLL_GAP_MAX } from "./live.mjs";   // import cycle is safe: only used inside functions

export const KIND_ALERT_TYPES = ["air_raid"];
export const WINDOW = 7 * 24 * 3600e3;

function merged(list) {
  const iv = list.filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
  const out = [];
  for (const [a, b] of iv) { if (out.length && a <= out[out.length - 1][1]) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b); else out.push([a, b]); }
  return out;
}

export function kindAt(state, tau, regions) {
  const known = [], startLevels = {};
  for (const r of Object.values(state.records)) {
    if (r.firstSeen > tau || r.start > tau || !KIND_ALERT_TYPES.includes(r.alert_type)) continue;
    const end = r.end !== null && r.endKnown !== null && r.endKnown <= tau && r.end <= tau ? r.end : null;
    known.push({ unit: r.unit, start: r.start, end });
    const key = `${r.unit}|${r.start}`;
    (startLevels[key] ||= []).push(levelAt(r, tau));
  }
  const ivs = unitIntervals(known);
  const colour = (u, o) => {
    const lv = startLevels[`${u}|${o}`] || [];
    return lv.includes("red") ? "red" : lv.some(l => l !== "yellow") ? "unknown" : "yellow";
  };
  const units = {};
  let natR = 0, natN = 0;
  const polls = (state.polls || []).filter(([a]) => a <= tau).map(([a, b]) => [a, Math.min(b + POLL_GAP_MAX, tau)]);
  for (const u of regions.units) {
    const cov = merged([...coverageAt(state, u, tau, "levelCoverage"), ...polls]);
    if (!cov.some(([a, b]) => a <= tau - WINDOW && b >= tau)) { units[u] = { status: "not_enough_data", M: null, N: null, R: null, U: null, share: null }; continue; }
    const on = ((ivs[u] || {}).onsets || []).filter(o => o > tau - WINDOW && o <= tau);
    let R = 0, Y = 0, U = 0;
    for (const o of on) { const c = colour(u, o); if (c === "red") R++; else if (c === "yellow") Y++; else U++; }
    const N = R + Y;
    units[u] = { status: "ok", M: on.length, N, R, U, share: N ? R / N : null };
    natR += R; natN += N;
  }
  return { tau, window_days: 7, alert_types: KIND_ALERT_TYPES, units, national: { R: natR, N: natN, share: natN ? natR / natN : null } };
}

export { kindWords } from "./kind_words.mjs";
