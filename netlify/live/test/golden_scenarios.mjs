// Fixed scenarios for the "any is unchanged" golden test (plans/M6-site.md §6). `lib` = {emptyState, applyActive,
// applyHistory, forecastAll} from either the pre-M6 code (to write golden_any.json) or the current code (to compare).
// Only the M8 output fields are kept.
const MIN = 60e3, H = 60 * MIN, D = 24 * H;
const T0 = Date.parse("2026-10-01T00:00:00Z");
const iso = t => new Date(t).toISOString();
const M8_FIELDS = ["p", "state", "physical_alert", "recent_rate", "recent_hours", "caution", "confirmed_until",
                   "alerts_last_24h", "minutes_since_last_start"];

// deterministic pseudo-random generator (mulberry32)
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

function A(id, oblast, start, end, level, type = "air_raid", upd = null) {
  return { id, location_oblast: oblast, location_type: "raion", started_at: iso(start), finished_at: end === null ? null : iso(end),
           updated_at: iso(upd ?? (end ?? start)), alert_type: type, alert_level: level };
}

// history per unit over [T0 - 20 d, T0): yellow and red alerts (some red inside yellow), some artillery
function history(regions, r) {
  const name = Object.fromEntries(Object.entries(regions.api_oblast_name).map(([n, u]) => [u, n]));
  const by = {};
  let id = 1;
  regions.units.forEach((u, i) => {
    const list = [];
    for (let t = T0 - 20 * D + i * 7 * MIN; t < T0 - 2 * H; t += (3 + 20 * r()) * H) {
      const dur = (20 + 150 * r()) * MIN, lvl = r() < 0.25 ? "red" : "yellow";
      list.push(A(`g${id++}`, name[u], t, t + dur, lvl, r() < 0.05 ? "artillery_shelling" : "air_raid"));
      if (lvl === "yellow" && r() < 0.2) list.push(A(`g${id++}`, name[u], t + 10 * MIN, t + 40 * MIN, "red"));
    }
    by[u] = list;
  });
  return { by, name };
}

function pick(f) {
  const units = {};
  for (const [u, x] of Object.entries(f.units)) units[u] = Object.fromEntries(M8_FIELDS.map(k => [k, x[k]]));
  return { tau: f.tau, horizon_minutes: f.horizon_minutes, units };
}

export function runScenarios(lib, regions, model) {
  const out = {};
  const { by, name } = history(regions, rng(42));
  const confirm = (s, t) => regions.units.forEach(u => lib.applyHistory(s, u, by[u].filter(a => Date.parse(a.started_at) < t), t, regions));
  const polls = (s, from, to, active = () => []) => { for (let t = from; t <= to; t += MIN) lib.applyActive(s, active(t), t, regions); };

  // 1. normal: all units confirmed at T0, polls every minute for 90 min with live alerts appearing and vanishing
  {
    const s = lib.emptyState(T0 - 40 * D);
    confirm(s, T0);
    const live = t => [t >= T0 + 20 * MIN && t < T0 + 50 * MIN ? A("n1", name.kyiv_city, T0 + 19 * MIN, null, "yellow") : null,
                       t >= T0 + 30 * MIN ? A("n2", name.kharkivska, T0 + 29 * MIN, null, "red") : null].filter(Boolean);
    polls(s, T0, T0 + 90 * MIN, live);
    out.normal = [T0 + 10 * MIN, T0 + 35 * MIN, T0 + 90 * MIN].map(t => pick(lib.forecastAll(s, t, model, regions)));
  }
  // 2. migration-like: records first stored by ACTIVE polls, then reconciled by history calls in rotation
  {
    const s = lib.emptyState(T0 - 40 * D);
    confirm(s, T0);
    polls(s, T0, T0 + 30 * MIN, t => t < T0 + 15 * MIN ? [A("m1", name.odeska, T0 + 2 * MIN, null, "yellow")] : []);
    lib.applyHistory(s, "odeska", [...by.odeska, A("m1", name.odeska, T0 + 2 * MIN, T0 + 14 * MIN, "yellow", "air_raid", T0 + 14 * MIN)], T0 + 30 * MIN, regions);
    polls(s, T0 + 31 * MIN, T0 + 40 * MIN);
    out.migration = [T0 + 20 * MIN, T0 + 40 * MIN].map(t => pick(lib.forecastAll(s, t, model, regions)));
  }
  // 3. rejected ACTIVE and history records
  {
    const s = lib.emptyState(T0 - 40 * D);
    confirm(s, T0);
    polls(s, T0, T0 + 20 * MIN);
    lib.applyActive(s, [{ ...A("r1", name.kyiv_city, T0 + 20 * MIN, null, "yellow"), started_at: "bad" }], T0 + 21 * MIN, regions);
    lib.applyHistory(s, "lvivska", [...by.lvivska, { ...A("r2", name.lvivska, T0 - 3 * H, null, "red"), finished_at: iso(T0 - 4 * H) }], T0 + 22 * MIN, regions);
    out.rejected = [T0 + 22 * MIN].map(t => pick(lib.forecastAll(s, t, model, regions)));
  }
  // 4. a 10-minute poll hole, then the history backfill confirms it unit by unit
  {
    const s = lib.emptyState(T0 - 40 * D);
    confirm(s, T0);
    polls(s, T0, T0 + 10 * MIN);
    polls(s, T0 + 21 * MIN, T0 + 30 * MIN);
    const before = pick(lib.forecastAll(s, T0 + 30 * MIN, model, regions));
    regions.units.slice(0, 12).forEach((u, i) => lib.applyHistory(s, u, by[u], T0 + (31 + i) * MIN, regions));
    out.hole = [before, pick(lib.forecastAll(s, T0 + 43 * MIN, model, regions))];
  }
  return out;
}
