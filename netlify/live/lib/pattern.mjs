// Recent pattern (plans/M11.md §B2b): onsets per Kyiv calendar day x 3-hour Kyiv clock block. DESCRIPTIVE only.
// Self-contained (no imports): scripts/build_site.py inlines this file into the page, so the tested code is the shipped code.
const PATTERN_HOUR = 3600e3;
const PATTERN_FMT = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Kyiv", year: "numeric", month: "2-digit", day: "2-digit",
                                                       hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
function kyivParts(t) {
  const p = Object.fromEntries(PATTERN_FMT.formatToParts(new Date(t)).map(x => [x.type, x.value]));
  return { y: +p.year, m: +p.month, d: +p.day, h: +p.hour, min: +p.minute };
}
// First UTC instant at which the Kyiv clock reads >= y-m-d h:00. Repeated hour (autumn) -> the first instance;
// skipped hour (spring) -> the moment the clock jumps past it.
export function kyivLocalToUtc(y, m, d, h) {
  const wall = Date.UTC(y, m - 1, d, h);
  const ok = [3, 2].map(off => wall - off * PATTERN_HOUR).filter(t => { const p = kyivParts(t); return p.y === y && p.m === m && p.d === d && p.h === h && p.min === 0; });
  if (ok.length) return Math.min(...ok);
  return wall - 2 * PATTERN_HOUR;                // inside the spring gap: 03:00 EET does not exist, the clock reads 04:00 EEST
}
function nextDay(y, m, d) { const t = new Date(Date.UTC(y, m - 1, d + 1)); return [t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate()]; }
function prevDays(y, m, d, k) { const t = new Date(Date.UTC(y, m - 1, d - k)); return [t.getUTCFullYear(), t.getUTCMonth() + 1, t.getUTCDate()]; }

/**
 * onsets: sorted or unsorted ms timestamps (capped merged onsets, D-020/D-023); coverage: [[a, b)] confirmed intervals;
 * now: ms. Returns nDays Kyiv calendar days (oldest first), 8 blocks each: {start, end, hours, count, status} with
 * status "ok" (fully covered: count is the number of onsets in [start, end)), "no_data" (any part not covered:
 * count null, never 0), "in_progress" (contains now) or "future" (starts at or after now). A day with any non-"ok"
 * block is partial.
 */
export function recentPattern(onsets, coverage, now, nDays = 14) {
  const cov = coverage.map(([a, b]) => [a, b]).filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
  const merged = [];
  for (const [a, b] of cov) { if (merged.length && a <= merged[merged.length - 1][1]) merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b); else merged.push([a, b]); }
  const full = (a, b) => merged.some(([x, y]) => x <= a && y >= b);
  const today = kyivParts(now);
  const days = [];
  for (let k = nDays - 1; k >= 0; k--) {
    const [y, m, d] = prevDays(today.y, today.m, today.d, k);
    const blocks = [];
    for (let b = 0; b < 8; b++) {
      const start = kyivLocalToUtc(y, m, d, 3 * b), end = b === 7 ? kyivLocalToUtc(...nextDay(y, m, d), 0) : kyivLocalToUtc(y, m, d, 3 * b + 3);
      const hours = (end - start) / PATTERN_HOUR;
      let status = "ok", count = null;
      if (start >= now) status = "future";
      else if (end > now) status = "in_progress";
      else if (!full(start, end)) status = "no_data";
      else count = onsets.filter(t => t >= start && t < end).length;
      blocks.push({ start, end, hours, count, status });
    }
    const date = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    days.push({ date, blocks, partial: blocks.some(x => x.status !== "ok") });
  }
  return days;
}
