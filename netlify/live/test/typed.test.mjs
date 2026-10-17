// M6-site (plans/M6-site.md §6): typed (yellow / red) forecasts on the live site — levels, typed coverage, per-type
// eligibility and states, truncation with negative controls, the model plug-in contract, the "any" golden, the page.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { offsetAt } from "../lib/features.mjs";
import { emptyState, applyActive, applyHistory, forecastAll, levelAt, ALERT_TYPES } from "../lib/live.mjs";
import * as live from "../lib/live.mjs";
import { typedAt, blend, blendWeight, selectModel, validMonthly, historyDays, TYPED_ALERT_TYPES, N0 } from "../lib/typed.mjs";
import { readPayload, runUpdate } from "../lib/runner.mjs";
import { runScenarios } from "./golden_scenarios.mjs";

const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const model = JSON.parse(readFileSync(new URL("../model/model_live.json", import.meta.url)));
const MIN = 60e3, H = 60 * MIN, D = 24 * H;
const T0 = Date.parse("2026-10-01T00:00:00Z");
const HS = T0 - 3 * D;                                   // history start (hour-aligned)
const iso = t => new Date(t).toISOString();
const NAME = Object.fromEntries(Object.entries(regions.api_oblast_name).map(([n, u]) => [u, n]));
const A = (id, unit, start, end, level, type = "air_raid", upd = null) =>
  ({ id, location_oblast: NAME[unit], location_type: "raion", started_at: iso(start), finished_at: end === null ? null : iso(end),
     updated_at: iso(upd ?? (end ?? start)), alert_type: type, alert_level: level });
const typed = (s, tau, zones = [], m = null) => typedAt(s, tau, regions, zones, m);

// every unit confirmed at T with its own list of alerts; kyivska: yellow [T0-10h, T0-8h) with red [T0-9.5h, T0-9h) inside
function base(extra = {}) {
  const s = emptyState(HS);
  for (const u of regions.units) {
    const list = { kyivska: [A("y1", "kyivska", T0 - 10 * H, T0 - 8 * H, "yellow"), A("r1", "kyivska", T0 - 9.5 * H, T0 - 9 * H, "red")] }[u] || [];
    applyHistory(s, u, [...list, ...(extra[u] || [])], T0, regions);
  }
  return s;
}

test("levels: kept from ACTIVE and history as timestamped versions; unknown level stored as null and counted", () => {
  const s = emptyState(HS);
  const r1 = applyActive(s, [A("a", "odeska", T0 - 5 * MIN, null, "yellow"), A("b", "odeska", T0 - 4 * MIN, null, "orange"),
                             { ...A("c", "odeska", T0 - 3 * MIN, null, null), alert_level: undefined }], T0, regions);
  assert.equal(r1.rejected.length, 0);                                        // never a rejection
  assert.equal(r1.levelUnknown, 2);
  assert.deepEqual(s.records.a.levels, [[T0, "yellow"]]);
  assert.deepEqual(s.records.b.levels, []);
  assert.equal(s.records.a.alert_level, undefined);                           // only the versions are stored
  // history at T0 + 10 min: backfills b, changes a's level (newer updated_at), leaves c unknown
  const r2 = applyHistory(s, "odeska", [A("a", "odeska", T0 - 5 * MIN, null, "red", "air_raid", T0 + 5 * MIN),
                                        A("b", "odeska", T0 - 4 * MIN, null, "yellow", "air_raid", T0 - 4 * MIN),
                                        { ...A("c", "odeska", T0 - 3 * MIN, null, null), alert_level: "purple" }], T0 + 10 * MIN, regions);
  assert.equal(r2.levelUnknown, 1);
  assert.deepEqual(s.records.a.levels, [[T0, "yellow"], [T0 + 10 * MIN, "red"]]);
  assert.deepEqual(s.records.b.levels, [[T0 + 10 * MIN, "yellow"]]);
  assert.equal(levelAt(s.records.a, T0 + 9 * MIN), "yellow");
  assert.equal(levelAt(s.records.a, T0 + 10 * MIN), "red");
  assert.equal(levelAt(s.records.b, T0 + 9 * MIN), null);
  assert.equal(levelAt(s.records.c, T0 + 60 * MIN), null);
  // the same id twice in one batch, or a flapping level with the same updated_at, adds no version
  for (let i = 0; i < 5; i++) applyActive(s, [A("a", "odeska", T0 - 5 * MIN, null, "yellow", "air_raid", T0 + 5 * MIN),
                                              A("a", "odeska", T0 - 5 * MIN, null, "red", "air_raid", T0 + 5 * MIN)], T0 + (11 + i) * MIN, regions);
  assert.deepEqual(s.records.a.levels, [[T0, "yellow"], [T0 + 10 * MIN, "red"]]);
  // an older history version never overwrites a newer level
  applyHistory(s, "odeska", [A("a", "odeska", T0 - 5 * MIN, null, "yellow", "air_raid", T0 - 5 * MIN)], T0 + 20 * MIN, regions);
  assert.equal(levelAt(s.records.a, T0 + 30 * MIN), "red");
});

test("typed coverage comes only from history calls of the new code; an old store has none (data gap, 0 days)", () => {
  const s = base();
  assert.equal(s.levelCoverage.kyivska.length, 1);
  const old = structuredClone(s);
  delete old.levelCoverage;
  for (const r of Object.values(old.records)) delete r.levels;
  const f = typed(old, T0);
  assert.ok(regions.units.every(u => f.units[u].yellow.state === "data_gap" && f.units[u].red.state === "data_gap"));
  assert.equal(f.meta.history_days, 0);
  assert.equal(f.meta.history_since, null);
  // one new history call for kyivska: only kyivska gets typed coverage
  applyHistory(old, "kyivska", [A("y1", "kyivska", T0 - 10 * H, T0 - 8 * H, "yellow"), A("r1", "kyivska", T0 - 9.5 * H, T0 - 9 * H, "red")], T0 + MIN, regions);
  const g = typed(old, T0 + MIN);
  assert.equal(g.units.kyivska.yellow.state, "forecast");
  assert.equal(g.units.lvivska.yellow.state, "data_gap");
});

test("per-type eligibility, hand-computed: red onset inside yellow counts for red; a yellow hour is not masked for red", () => {
  const f = typed(base(), T0);
  // eligible hours: s in [HS + 24 h, T0 - 1 h] = 48 hours (history-start zone [HS - 1 h, HS + 24 h) excluded)
  // yellow: s = T0-10h and T0-9h are under yellow -> n = 46; the onset T0-10h lies in (T0-11h, T0-10h] -> k = 1
  // red: [T0-9.5h, T0-9h) covers no hour start -> n = 48; the onset T0-9.5h lies in (T0-10h, T0-9h] -> k = 1
  const y = f.units.kyivska.yellow, r = f.units.kyivska.red;
  assert.deepEqual([y.recent_k, y.recent_n, r.recent_k, r.recent_n], [1, 46, 1, 48]);
  assert.equal(y.p_baseline, (1 + 10 * (1 / 46)) / (46 + 10));
  assert.equal(r.p_baseline, (1 + 10 * (1 / 48)) / (48 + 10));
  assert.equal(y.p, y.p_baseline);                                          // w = 0: the baseline exactly
  assert.deepEqual([y.state, y.w, y.p_model], ["forecast", 0, null]);
  assert.deepEqual(f.units.kyivska.yellow.caution, ["few_hours"]);          // 46 < 48 forecastable hours
  assert.deepEqual(f.units.lvivska.red.caution, []);                        // exactly 48
  assert.deepEqual([f.units.lvivska.red.recent_k, f.units.lvivska.red.recent_n], [0, 48]);
  // the same through offsetAt directly on the yellow-only intervals (the typed path adds nothing else)
  assert.equal(f.meta.mode, "baseline_only");
  assert.deepEqual(f.meta.alert_types, ["air_raid"]);                       // human decision 2026-10-18
  assert.deepEqual(TYPED_ALERT_TYPES, ["air_raid"]);
  assert.ok(ALERT_TYPES.length > 1);                                        // the "any" map keeps all types
  assert.equal(f.meta.history_days, 3);
  assert.equal(f.meta.history_since, HS);
});

test("states: red running -> red level_active while yellow is forecast; artillery is not counted for yellow/red", () => {
  const s = base({ odeska: [A("r2", "odeska", T0 - 30 * MIN, null, "red")],
                   sumska: [A("art", "sumska", T0 - 20 * MIN, null, "red", "artillery_shelling")] });
  const f = typed(s, T0);
  assert.equal(f.units.odeska.red.state, "level_active");
  assert.equal(f.units.odeska.red.p, null);
  assert.ok(f.units.odeska.red.p_baseline > 0);                            // the two-week rate is still reported
  assert.equal(f.units.odeska.yellow.state, "forecast");
  assert.equal(f.units.sumska.red.state, "forecast");                      // air-raid only (human, 2026-10-18) ...
  assert.equal(forecastAll(s, T0, model, regions).units.sumska.state, "alert_running");   // ... the "any" map counts it
  // the "any" view of the same unit: an alert is running, so no "any" forecast, but the typed yellow forecast exists
  const any = forecastAll(s, T0, model, regions);
  assert.equal(any.units.odeska.state, "alert_running");
  assert.equal(any.units.odeska.typed.yellow.state, "forecast");
});

test("unresolved level: a bounded typed hole for both levels, data gap only while it may be running", () => {
  const s = base({ kyivska: [{ ...A("u1", "kyivska", T0 - 5 * H, T0 - 4 * H, null), alert_level: undefined }],
                   odeska: [{ ...A("u2", "odeska", T0 - 30 * MIN, null, null), alert_level: undefined }] });
  const f = typed(s, T0);
  // hole [T0-5h, T0-4h): label hours with s + 1h >= T0-5h are excluded -> s in [T0-6h, T0-1h], 6 hours fewer
  assert.deepEqual([f.units.kyivska.yellow.recent_n, f.units.kyivska.red.recent_n], [40, 42]);
  assert.equal(f.units.kyivska.yellow.state, "forecast");                   // it ended before tau
  assert.equal(f.units.odeska.yellow.state, "data_gap");                   // open with unknown level: may be running
  assert.equal(f.units.odeska.red.state, "data_gap");
  // the day count leaves out the unresolved zones: [T0-5h, T0-4h) and [T0-30min, T0)
  const hd = historyDays(s, T0, regions, { kyivska: [[T0 - 5 * H, T0 - 4 * H]], odeska: [[T0 - 30 * MIN, T0 + 23.5 * H]] });
  assert.equal(hd.days, 2);                                                 // 3 days - 1.5 h -> 2 full days
  assert.equal(f.meta.history_days, 2);
  // the level arrives with the next history call: from then on the hole is gone
  applyHistory(s, "odeska", [A("u2", "odeska", T0 - 30 * MIN, null, "yellow", "air_raid", T0 + 5 * MIN)], T0 + 10 * MIN, regions);
  applyActive(s, [], T0 + 10 * MIN, regions);
  const g = typed(s, T0 + 10 * MIN);
  assert.equal(g.units.odeska.yellow.state, "level_active");
  assert.equal(g.units.odeska.red.state, "forecast");
  assert.equal(typed(s, T0 + 9 * MIN).units.odeska.red.state, "data_gap");  // replay before the level was known
});

test("rejected records: ACTIVE -> typed data gap for that unit only; history -> caution", () => {
  const s = base();
  for (let t = T0; t <= T0 + 10 * MIN; t += MIN) applyActive(s, [], t, regions);
  applyActive(s, [{ ...A("bad", "kyiv_city", T0 + 5 * MIN, null, "red"), started_at: "bad" }], T0 + 11 * MIN, regions);
  applyHistory(s, "lvivska", [{ ...A("bad2", "lvivska", T0 - 3 * H, null, "red"), finished_at: iso(T0 - 4 * H) }], T0 + 11 * MIN, regions);
  const f = forecastAll(s, T0 + 11 * MIN, model, regions);
  assert.equal(f.units.kyiv_city.state, "data_gap");
  assert.deepEqual([f.units.kyiv_city.typed.yellow.state, f.units.kyiv_city.typed.red.state], ["data_gap", "data_gap"]);
  assert.ok(f.units.kyiv_city.typed.red.caution.includes("rejected_active_record"));
  assert.equal(f.units.kyivska.typed.yellow.state, "forecast");                   // neighbours are not blanked
  assert.equal(f.units.lvivska.typed.yellow.state, "forecast");
  assert.ok(f.units.lvivska.typed.yellow.caution.includes("rejected_history_record"));
});

test("a typed failure never takes down the 'any' forecast, and it is reported, not hidden", async () => {
  const s = base();
  for (let t = T0; t <= T0 + 10 * MIN; t += MIN) applyActive(s, [], t, regions);
  const bad = [stub({ predict: () => 1.5 })];
  const ok = forecastAll(s, T0 + 10 * MIN, model, regions), f = forecastAll(s, T0 + 10 * MIN, model, regions, bad);
  const any = x => JSON.stringify(Object.fromEntries(Object.entries(x.units).map(([u, v]) => { const { typed: _, ...rest } = v; return [u, rest]; })));
  assert.equal(any(f), any(ok));
  assert.equal(f.typed.mode, "error");
  assert.match(f.typed.error, /outside/);
  assert.ok(regions.units.every(u => f.units[u].typed.red.state === "data_gap" && f.units[u].typed.red.caution.includes("typed_error")));
  // through the scheduled run: the forecast is written and status carries the typed error
  const m = new Map();
  const store = { async get(k) { return m.has(k) ? JSON.parse(m.get(k)) : null; }, async setJSON(k, v) { m.set(k, JSON.stringify(v)); },
                  async delete(k) { m.delete(k); }, async list({ prefix = "" } = {}) { return { blobs: [...m.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })) }; } };
  await store.setJSON("state", s);
  const fetchFn = async () => ({ ok: true, status: 200, json: async () => ({ alerts: [] }) });
  const st = await runUpdate({ fetchFn, store, token: "t", now: T0 + 11 * MIN, model, regions, seed: null, typedModel: bad });
  assert.equal(st.ok, true);
  assert.match(st.typed_error, /outside/);
  assert.equal((await store.get("latest")).tau, T0 + 11 * MIN);
  const st2 = await runUpdate({ fetchFn, store, token: "t", now: T0 + 12 * MIN, model, regions, seed: null });
  assert.equal(st2.typed_error, null);
});

test("event holes (the M8 zones) make the typed state a data gap", () => {
  const s = base();
  const f = forecastAll(s, T0 + 20 * MIN, model, regions);                   // no ACTIVE poll since T0: a hole
  assert.ok(regions.units.every(u => f.units[u].typed.yellow.state === "data_gap"));
  assert.ok(regions.units.every(u => f.units[u].state === "data_gap"));
});

// ---- truncation (leakage): production typedAt(full) == typedAt(truncated) at witnesses where the future would matter
function truncate(s, tau) {
  const t = structuredClone(s);
  for (const [id, r] of Object.entries(t.records)) {
    if (r.firstSeen > tau) { delete t.records[id]; continue; }
    if (r.endKnown !== null && r.endKnown > tau) { r.end = null; r.endKnown = null; r.endSource = null; }
    r.levels = (r.levels || []).filter(([k]) => k <= tau);
  }
  for (const key of ["coverage", "levelCoverage"]) for (const u of Object.keys(t[key] || {})) t[key][u] = t[key][u].filter(([, , c]) => c <= tau);
  return t;
}
const pick = f => JSON.stringify(f.units);

test("truncation: ends, levels and coverage known only after tau are invisible at tau (witnesses + oracle controls)", () => {
  const T1 = T0 + 2 * H, tau = T0 + 90 * MIN;
  const s = base({ odeska: [A("w1", "odeska", T0 - 4 * H, null, "yellow")],                                       // (a) end later
                   kharkivska: [{ ...A("w2", "kharkivska", T0 - 3 * H, T0 - 2.5 * H, null), alert_level: undefined }] }); // (b)
  for (let t = T0; t <= T1; t += MIN) applyActive(s, [], t, regions);
  applyHistory(s, "odeska", [A("w1", "odeska", T0 - 4 * H, T0 - 3 * H, "yellow", "air_raid", T0 - 3 * H)], T1, regions);
  applyHistory(s, "kharkivska", [A("w2", "kharkivska", T0 - 3 * H, T0 - 2.5 * H, "red", "air_raid", T0 - 2.5 * H)], T1, regions);
  applyHistory(s, "lvivska", [], T1, regions);                                                                   // (c)
  applyHistory(s, "zhytomyrska", [A("w3", "zhytomyrska", T0 + 60 * MIN, null, "yellow")], T1, regions);  // (d) first seen later
  const full = typed(s, tau), cut = typed(truncate(s, tau), tau);
  assert.equal(pick(full), pick(cut));
  assert.equal(JSON.stringify(full.meta), JSON.stringify(cut.meta));
  // oracle states: the same facts made known at tau -> each witness changes, so the equality above is not vacuous
  const oa = structuredClone(s); oa.records.w1.endKnown = tau;
  assert.equal(full.units.odeska.yellow.state, "level_active");
  assert.equal(typed(oa, tau).units.odeska.yellow.state, "forecast");
  const ob = structuredClone(s); ob.records.w2.levels = [[tau, "red"]];
  assert.notEqual(typed(ob, tau).units.kharkivska.red.recent_n, full.units.kharkivska.red.recent_n);
  const oc = structuredClone(s); oc.levelCoverage.lvivska = oc.levelCoverage.lvivska.map(([a, b, c]) => [a, b, Math.min(c, tau)]);
  assert.notEqual(typed(oc, tau).units.lvivska.yellow.recent_n, full.units.lvivska.yellow.recent_n);
  const od = structuredClone(s); od.records.w3.firstSeen = tau; od.records.w3.levels = [[tau, "yellow"]];
  assert.equal(full.units.zhytomyrska.yellow.state, "forecast");
  assert.equal(typed(od, tau).units.zhytomyrska.yellow.state, "level_active");
  // and the immature window: counting label hours s in (tau - 1 h, tau] (a leaky variant) differs at an hour-aligned tau
  // where typed coverage reaches tau (lvivska's history call at T1), so the extra hour is not hidden by a coverage hole
  const tauH = T1, cut2 = truncate(s, tauH);
  const real = typed(cut2, tauH).units.lvivska.yellow;
  const known = Object.values(cut2.records).filter(r => r.unit === "lvivska" && levelAt(r, tauH) === "yellow");
  const leaky = offsetAt({}, tauH + H, regions, HS, { lvivska: [[-8.64e15, HS]] }).lvivska;            // window one hour on
  assert.equal(known.length, 0);
  assert.equal(real.recent_n + 1, leaky.n);
});

// ---- model plug-in contract (plan §5)
const stub = (o = {}) => ({ version: "v1", trained_through: T0 - 2 * D, available_at: T0 - D, alert_types: ["air_raid"],
  horizon_minutes: 60, predict: () => 0.2, weight: () => ({ n: 50, n0: N0, wStar: 0.8 }), ...o });

test("blend weight and blend, by hand", () => {
  assert.equal(blendWeight({ n: 50, n0: 50, wStar: 0.8 }), 0.4);
  assert.equal(blendWeight({ n: 0, wStar: 0.8 }), 0);
  assert.equal(blendWeight({ n: 150, n0: 50, wStar: 3 }), 0.75);             // clip to 1
  assert.equal(blendWeight({ n: 150, n0: 50, wStar: -2 }), 0);               // clip to 0
  assert.throws(() => blendWeight({ n: -1, wStar: 0.5 }));
  assert.throws(() => blendWeight({ n: 1, n0: 0, wStar: 0.5 }));
  assert.equal(blend(0.9, 0.123456789, 0), 0.123456789);                     // w = 0 returns the baseline exactly
  assert.equal(blend(0.5, 0.1, 0.5), 0.3);
  assert.throws(() => blend(0.5, 0.1, 1.5));
});

test("model plug-in: blend mode, causal version selection, and every rejection", () => {
  const s = base();
  const f = typed(s, T0, [], [stub()]);
  const y = f.units.lvivska.yellow;
  assert.equal(f.meta.mode, "blend");
  assert.equal(f.meta.weights.yellow.w, 0.4);
  assert.equal(y.p_model, 0.2);
  assert.ok(Math.abs(y.p - (0.4 * 0.2 + 0.6 * y.p_baseline)) < 1e-15);
  // a version available only after tau is never used at tau; it is used once available
  const late = stub({ version: "v2", trained_through: T0 - H, available_at: T0 + H, predict: () => 0.9 });
  assert.equal(selectModel([stub(), late], T0).version, "v1");
  assert.equal(selectModel([stub(), late], T0 + H).version, "v2");
  assert.equal(typed(s, T0, [], [late]).meta.mode, "baseline_only");
  assert.equal(typed(s, T0, [], [late]).units.lvivska.yellow.p, typed(s, T0).units.lvivska.yellow.p);
  assert.throws(() => typed(s, T0, [], [stub({ alert_types: [...ALERT_TYPES] })]), /alert_types/);   // all types != air_raid
  assert.throws(() => typed(s, T0, [], [stub({ horizon_minutes: 180 })]), /horizon/);
  assert.throws(() => typed(s, T0, [], [stub({ trained_through: T0 - D })]), /available_at/);     // malformed
  assert.throws(() => typed(s, T0, [], [stub({ predict: () => 1 })]), /outside/);
  assert.throws(() => typed(s, T0, [], [stub({ available_at: undefined })]), /available_at/);
  assert.throws(() => typed(s, T0, [], stub()), /list/);
});

// ---- "any" is unchanged: the pre-M6 code wrote golden_any.json on the same scenarios
test("the M8 'any' forecast is byte-identical to the pre-M6 code (golden)", () => {
  const golden = JSON.parse(readFileSync(new URL("./golden_any.json", import.meta.url))).scenarios;
  const now = runScenarios(live, regions, model);
  assert.deepEqual(Object.keys(now), ["normal", "migration", "rejected", "hole"]);
  assert.equal(JSON.stringify(now), JSON.stringify(golden));
});

// ---- monthly chart contract
test("monthly chart contract: the committed file is valid and empty; bad rows throw; served in the payload", async () => {
  const m = JSON.parse(readFileSync(new URL("../data/typed_monthly.json", import.meta.url)));
  assert.deepEqual(validMonthly(m), { schema: 1, months: [] });
  const row = { month: "2026-11", type: "red", brier_skill_vs_baseline: 0.02, w_mean: 0.3, n_rows: 700, n_onsets: 30 };
  validMonthly({ schema: 1, months: [row, { ...row, type: "yellow" }] });
  for (const bad of [{ ...row, month: "2026-13" }, { ...row, type: "green" }, { ...row, w_mean: 1.2 }, { ...row, n_onsets: 701 },
                     { ...row, extra: 1 }, { ...row, brier_skill_vs_baseline: NaN }])
    assert.throws(() => validMonthly({ schema: 1, months: [bad] }));
  assert.throws(() => validMonthly({ schema: 1, months: [row, row] }), /duplicate/);
  assert.throws(() => validMonthly({ schema: 2, months: [] }));
  const store = { async get() { return null; } };
  const good = await readPayload(store, m);
  assert.deepEqual([good.typed_monthly, good.typed_monthly_error], [m, null]);
  const badP = await readPayload(store, { schema: 1, months: [{ ...row, type: "x" }] });   // the main GET still answers
  assert.equal(badP.typed_monthly, null);
  assert.match(badP.typed_monthly_error, /bad type/);
});

// ---- the page: the marked block of pure functions from the template
const tpl = readFileSync(new URL("../../../site_src/template.html", import.meta.url), "utf8");
const block = tpl.slice(tpl.indexOf("/* typed-block:start"), tpl.indexOf("/* typed-block:end */"));
const { typedTipHtml, typedCardHtml } = new Function(block + "; return { typedTipHtml, typedCardHtml };")();

test("page: tooltip and card text for baseline-only, level-active, data-gap and blend payloads", () => {
  const meta = { label: "in training", mode: "baseline_only", model: null, weights: { yellow: null, red: null },
                 history_days: 35, history_since: Date.parse("2026-09-12T17:00:43Z") };
  const x = { yellow: { state: "forecast", p: 0.123, caution: [] }, red: { state: "level_active", p: null, caution: [] } };
  const tip = typedTipHtml(x, meta);
  assert.match(tip, /Yellow \(drones\): 12%/);
  assert.match(tip, /Red \(missiles\): red alert running/);
  assert.match(tip, /in training, baseline only/);
  const card = typedCardHtml(x, meta, { schema: 1, months: [] });
  for (const s of ["in training", "baseline only: two-week rate per type; model in training (blend weight 0)",
                   "Collecting data: 35 days of yellow/red history in total since 12 Sept 2026", "available after the first monthly retrain",
                   "air-raid alerts only (the main map counts all alert types)"]) assert.ok(card.includes(s), s);
  const gap = typedCardHtml({ yellow: { state: "data_gap", p: null, caution: [] }, red: { state: "forecast", p: 0.004, caution: ["few_hours"] } }, meta, null);
  assert.match(gap, /data gap/);
  assert.match(gap, /&lt;1% \*/);
  assert.match(gap, /fewer than 48 forecastable hours/);
  const bl = typedCardHtml(x, { ...meta, mode: "blend", model: { version: "<v1>" }, weights: { yellow: { w: 0.4 }, red: { w: 0.1 } } },
                           { schema: 1, months: [{ month: "2026-11" }, { month: "2026-11" }, { month: "2026-12" }] });
  assert.match(bl, /blend of model &lt;v1&gt; .*yellow w = 0\.40, red w = 0\.10/);             // escaped
  assert.match(bl, /2 months available/);
  const err = { ...meta, mode: "error", error: "<boom>" };
  assert.match(typedCardHtml(x, err, null), /unavailable right now \(error: &lt;boom&gt;\)/);
  assert.match(typedTipHtml(x, err), /Yellow\/red forecast unavailable/);
  assert.match(typedCardHtml(x, meta, null, "bad file"), /unavailable \(data file error\)/);
  assert.match(card, /starts in the next 60 minutes/);
  const partial = typedCardHtml({ yellow: { state: "forecast" }, red: null }, { mode: "blend", weights: { yellow: {} } }, { months: [null] });
  assert.ok(!/NaN|undefined|Invalid Date/.test(partial), partial);                // partial fields degrade to "n/a"
  assert.equal(typedTipHtml(undefined, meta), "");                         // a payload without typed fields shows nothing
  assert.equal(typedCardHtml(x, undefined, null), "");
});
