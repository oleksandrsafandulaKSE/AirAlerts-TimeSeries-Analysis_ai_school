// Live model inputs at an arbitrary moment tau (ms since epoch, UTC) — mirrors src/features.py and
// improve/live_ref.py (plans/M8.md §2). Alerts: [{unit, start, end}] with ms times, end = null when unknown.
const HOUR = 3600e3, DAY = 24 * HOUR, CAP = 24 * HOUR, ALPHA = 10;

// D-020 counting interval + D-023 merge (touching merges), onsets = merged starts + uncovered zero-duration starts
export function unitIntervals(alerts) {
  const by = {};
  for (const a of alerts) (by[a.unit] ||= []).push(a);
  const out = {};
  for (const [u, list] of Object.entries(by)) {
    const iv = list.map(a => { const capped = a.start + CAP; const e = a.end === null || a.end === undefined ? capped : Math.min(a.end, capped); return [a.start, e]; })
                   .sort((p, q) => p[0] - q[0] || p[1] - q[1]);
    const ms = [], me = [];
    for (const [s, e] of iv) {
      if (e <= s) continue;
      if (ms.length && s <= me[me.length - 1]) { if (e > me[me.length - 1]) me[me.length - 1] = e; }
      else { ms.push(s); me.push(e); }
    }
    const zero = iv.filter(([s, e]) => e <= s).map(([s]) => s).filter(s => !covered(s, ms, me));
    const onsets = [...new Set([...ms, ...zero])].sort((a, b) => a - b);
    out[u] = { ms, me, onsets };
  }
  return out;
}

function upperIdx(arr, x) { let lo = 0, hi = arr.length; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] <= x) lo = m + 1; else hi = m; } return lo; }
export function covered(x, ms, me) { const i = upperIdx(ms, x) - 1; return i >= 0 && x < me[i]; }
function lastLE(arr, x) { const i = upperIdx(arr, x) - 1; return i >= 0 ? arr[i] : null; }
function countIn(arr, lo, hi) { return upperIdx(arr, hi) - upperIdx(arr, lo); }       // (lo, hi]

const kyivFmt = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Kyiv", hour: "numeric", hourCycle: "h23", weekday: "short" });
const WD = { Mon: 0, Tue: 1, Wed: 2, Thu: 3, Fri: 4, Sat: 5, Sun: 6 };
export function kyivHourWeekday(tau) {
  const parts = Object.fromEntries(kyivFmt.formatToParts(new Date(tau)).map(p => [p.type, p.value]));
  return [Number(parts.hour), WD[parts.weekday]];
}

// zones: [[u0, u1)] EXTENDED uncertainty zones (hole + 24 h), as config.uncertainty_zones
export function featuresAt(ivs, tau, regions, zones = []) {
  const inZone = zones.some(([a, b]) => tau >= a && tau < b);
  const [hour, weekday] = kyivHourWeekday(tau);
  const empty = { ms: [], me: [], onsets: [] };
  const active = {};
  for (const u of regions.units) { const v = ivs[u] || empty; active[u] = covered(tau, v.ms, v.me) ? 1 : 0; }
  const national = regions.units.reduce((s, u) => s + active[u], 0);
  const out = {};
  regions.units.forEach((u, code) => {
    const v = ivs[u] || empty;
    let sinceStart = lastLE(v.onsets, tau), sinceEnd = lastLE(v.me, tau);
    let fStart = sinceStart === null ? NaN : (tau - sinceStart) / 60e3;
    let fEnd = sinceEnd === null ? NaN : (tau - sinceEnd) / 60e3;
    for (const [a, b] of zones) {
      if (tau >= a && !(sinceStart !== null && sinceStart >= b)) fStart = NaN;
      if (tau >= a && !(sinceEnd !== null && sinceEnd >= b)) fEnd = NaN;
    }
    const win = w => zones.some(([a, b]) => tau >= a && tau - w < b) ? NaN : countIn(v.onsets, tau - w, tau);
    let nb = 0; for (const n of regions.neighbours[u] || []) nb += active[n];
    out[u] = {
      active_at_t: inZone ? NaN : active[u],
      minutes_since_last_start: fStart, minutes_since_last_end: fEnd,
      onsets_last_24h: win(DAY), onsets_last_7d: win(7 * DAY),
      neighbors_active_at_t: inZone ? NaN : nb, national_active_count_at_t: inZone ? NaN : national,
      hour_kyiv: hour, weekday_kyiv: weekday, unit_code: code,
    };
  });
  return out;
}

// Hourly label grid from historyStart (ceil to hour) to floor(tau - 1h): y(s) = onset in (s, s + 1h];
// eligible = not active at s, not in a label gap zone [h0 - 1h, h1 + 24h) (gaps = raw holes [h0, h1)).
export function offsetAt(ivs, tau, regions, historyStart, gaps = []) {
  const start = Math.ceil(historyStart / HOUR) * HOUR, last = Math.floor((tau - HOUR) / HOUR) * HOUR;
  const lo = Math.ceil((tau - 14 * DAY) / HOUR) * HOUR;
  const empty = { ms: [], me: [], onsets: [] };
  const per = {}; let natK = 0, natN = 0;
  for (const u of regions.units) {
    const v = ivs[u] || empty;
    const ug = Array.isArray(gaps) ? gaps : (gaps[u] || []);       // raw holes [h0, h1): global list or per unit
    let kE = 0, nE = 0, kW = 0, nW = 0;
    for (let s = start; s <= last; s += HOUR) {
      if (covered(s, v.ms, v.me)) continue;
      if (ug.some(([a, b]) => s < b + DAY && s + HOUR >= a)) continue;
      const y = countIn(v.onsets, s, s + HOUR) > 0 ? 1 : 0;
      kE += y; nE += 1;
      if (s >= lo) { kW += y; nW += 1; }
    }
    natK += kE; natN += nE;
    per[u] = { kE, nE, kW, nW };
  }
  const qNat = natN ? natK / natN : null;
  const out = {};
  for (const u of regions.units) {
    const p = per[u];
    const q = p.nE ? p.kE / p.nE : qNat;
    out[u] = { k: p.kW, n: p.nW, q, rate: q === null ? null : (p.kW + ALPHA * q) / (p.nW + ALPHA) };
  }
  return out;
}
