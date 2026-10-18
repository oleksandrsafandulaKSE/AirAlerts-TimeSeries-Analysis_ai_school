// M13 §3 (plans/M13.md): the live "what kind of alert" rule — (a) reconstruction parity with newregime/redshare.py,
// (b) independent knowledge-at-tau tests, (c) truncation + a leaky rule caught, window endpoints, DST, standing cap,
// simultaneous red + yellow, escalations, unresolved levels, Kyiv City vs Kyivska, and the rendered words.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { kindAt, kindWords, WINDOW } from "../lib/kind.mjs";

const HOUR = 3600e3, DAY = 24 * HOUR;
const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const rec = JSON.parse(readFileSync(new URL("./m12_parity_records.json", import.meta.url)));

// (a) assumption of the reconstruction fixture: records and their levels are known from their starts
function stateFrom(records, historyStart, levelsKnownAtStart = true) {
  const s = { records: {}, coverage: {}, levelCoverage: {}, polls: [], rotation: 0, historyStart, rejections: [], historyFail: {} };
  for (const r of records) s.records[r.id] = { id: r.id, unit: r.unit, level: "raion", alert_type: r.alert_type ?? "air_raid", start: r.start,
    end: r.end, updated: r.start, firstSeen: r.firstSeen ?? r.start, endKnown: r.endKnown !== undefined ? r.endKnown : r.end, endSource: "history",
    absent: [], levels: r.levels ?? (levelsKnownAtStart && r.level ? [[r.start, r.level]] : []) };
  for (const u of regions.units) s.levelCoverage[u] = s.coverage[u] = [[historyStart, 8.64e15, historyStart]];
  return s;
}
const state = stateFrom(rec.records, rec.historyStart);

test("(a) parity with newregime/redshare.py on every scored onset (reconstruction fixture)", () => {
  const csv = readFileSync(new URL("../../../reports/m12/redshare_rows.csv", import.meta.url), "utf8").trim().split("\n");
  const head = csv[0].split(","), col = n => head.indexOf(n);
  let n = 0;
  const cache = new Map();
  for (const line of csv.slice(1)) {
    const f = line.split(",");
    const tau = Date.parse(f[col("tau")].replace(" ", "T"));
    if (!cache.has(tau)) cache.set(tau, kindAt(state, tau, regions));
    const k = cache.get(tau), x = k.units[f[col("unit")]];
    assert.equal(x.status, "ok");
    assert.equal(x.R, Number(f[col("R")]), `${f[col("unit")]} ${f[col("tau")]} R`);
    assert.equal(x.N, Number(f[col("N")]), `${f[col("unit")]} ${f[col("tau")]} N`);
    assert.equal(x.U, 0);
    assert.ok(Math.abs(x.share - Number(f[col("rule")])) < 1e-12);
    assert.ok(Math.abs(k.national.share - Number(f[col("national")])) < 1e-12, `national at ${f[col("tau")]}`);
    n++;
  }
  assert.ok(n > 3000, `only ${n} rows`);
});

const T0 = Date.parse("2026-10-10T12:00:00Z"), HS = T0 - 20 * DAY;
const A = (id, unit, start, end, level, extra = {}) => ({ id, unit, start, end, level, ...extra });

test("(b) live knowledge at tau: delayed discovery, a level known later, coverage confirmed later, unknown end", () => {
  // first seen after tau -> not counted at tau
  let s = stateFrom([A("1", "lvivska", T0 - 2 * HOUR, T0 - HOUR, "red", { firstSeen: T0 + HOUR })], HS);
  assert.equal(kindAt(s, T0, regions).units.lvivska.M, 0);
  // level known only after tau -> the onset is observed but unclassified at tau, red afterwards
  s = stateFrom([A("1", "lvivska", T0 - 2 * HOUR, T0 - HOUR, null, { levels: [[T0 + HOUR, "red"]] })], HS);
  assert.deepEqual((({ M, N, U }) => ({ M, N, U }))(kindAt(s, T0, regions).units.lvivska), { M: 1, N: 0, U: 1 });
  assert.equal(kindAt(s, T0 + 2 * HOUR, regions).units.lvivska.R, 1);
  // level coverage confirmed after tau -> not enough data at tau
  s = stateFrom([], HS); s.levelCoverage.lvivska = [[HS, 8.64e15, T0 + HOUR]];
  assert.equal(kindAt(s, T0, regions).units.lvivska.status, "not_enough_data");
  // unknown end (end known only after tau): still running at tau with the 24 h cap -> a start 2 h later is not an onset
  s = stateFrom([A("1", "lvivska", T0 - 5 * HOUR, T0 + 3 * HOUR, "yellow", { endKnown: T0 + 3 * HOUR }),
                 A("2", "lvivska", T0 - 3 * HOUR, T0 - 2 * HOUR, "red")], HS);
  assert.deepEqual((({ M, R }) => ({ M, R }))(kindAt(s, T0, regions).units.lvivska), { M: 1, R: 0 });
});

test("(b) standing alert > 24 h: after the cap, a later start is a new onset", () => {
  const s = stateFrom([A("1", "kharkivska", T0 - 3 * DAY, null, "yellow"), A("2", "kharkivska", T0 - DAY - HOUR, T0 - DAY, "red")], HS);
  const x = kindAt(s, T0, regions).units.kharkivska;
  assert.equal(x.M, 2); assert.equal(x.R, 1);
});

test("(c) truncation invariance at pinned tau, and a leaky rule (window ending at tau + 1 h) is caught", () => {
  const truncate = (st, tau) => { const c = structuredClone(st);
    for (const [id, r] of Object.entries(c.records)) { if (r.start > tau) delete c.records[id]; else if (r.end !== null && r.end > tau) { r.end = null; r.endKnown = null; } }
    return c; };
  const taus = [Date.parse("2026-10-05T12:00:00Z"), Date.parse("2026-10-09T07:23:00Z"), Date.parse("2026-10-15T00:00:00Z")];
  for (const tau of taus) assert.deepEqual(kindAt(truncate(state, tau), tau, regions), kindAt(state, tau, regions));
  const leaky = (st, tau) => kindAt(st, tau + HOUR, regions);                     // reads the hour after tau
  assert.ok(taus.some(tau => JSON.stringify(leaky(state, tau).units) !== JSON.stringify(leaky(truncate(state, tau), tau).units)));
});

test("(c) window endpoints: an onset exactly at tau - 7 d is out, exactly at tau is in; simultaneous red + yellow -> red", () => {
  const s = stateFrom([A("1", "odeska", T0 - WINDOW, T0 - WINDOW + HOUR, "red"), A("2", "odeska", T0, T0 + HOUR, "yellow"),
                       A("3", "volynska", T0 - HOUR, T0 - 30 * 60e3, "yellow"), A("4", "volynska", T0 - HOUR, T0 - 20 * 60e3, "red")], HS);
  const k = kindAt(s, T0, regions);
  assert.deepEqual((({ M, R, N }) => ({ M, R, N }))(k.units.odeska), { M: 1, R: 0, N: 1 });
  assert.deepEqual((({ M, R }) => ({ M, R }))(k.units.volynska), { M: 1, R: 1 });
});

test("(c) escalation inside a running yellow is not an onset; DST day; Kyiv City vs Kyivska", () => {
  const dst = Date.parse("2026-10-25T00:30:00Z");                                // the night clocks go back in Kyiv
  const s = stateFrom([A("1", "kyiv_city", T0 - 3 * HOUR, T0 - HOUR, "yellow"), A("2", "kyiv_city", T0 - 2 * HOUR, T0 - 90 * 60e3, "red"),
                       A("3", "kyivska", dst - HOUR, dst - 30 * 60e3, "red")], HS);
  const k = kindAt(s, T0, regions);
  assert.deepEqual((({ M, R, N }) => ({ M, R, N }))(k.units.kyiv_city), { M: 1, R: 0, N: 1 });
  assert.equal(k.units.kyivska.M, 0);
  const k2 = kindAt(s, dst + HOUR, regions);
  assert.equal(k2.units.kyivska.R, 1); assert.equal(k2.units.kyiv_city.M, 0);      // Kyiv City's 10 Oct alert is out of the window
  assert.deepEqual(k2.national, { R: 1, N: 1, share: 1 });
  // national pools units with coverage only; an uncovered unit is left out (and an empty pool gives null)
  s.levelCoverage.kyivska = [[HS, 8.64e15, dst + 2 * HOUR]];
  assert.deepEqual(kindAt(s, dst + HOUR, regions).national, { R: 0, N: 0, share: null });
});

test("rendered words: no alerts (M = 0) vs kinds not known yet (M = 3, U = 3, N = 0) vs a share", () => {
  assert.equal(kindWords({ status: "ok", M: 0, N: 0, R: 0, U: 0, share: null }), "no alerts here in 7 days");
  assert.equal(kindWords({ status: "ok", M: 3, N: 0, R: 0, U: 3, share: null }), "alert kinds not known yet");
  assert.equal(kindWords({ status: "not_enough_data" }), "not enough data on alert kinds");
  assert.equal(kindWords({ status: "ok", M: 5, N: 4, R: 3, U: 1, share: 0.75 }), "likely red (missiles) · red in 3 of the last 4 alerts (1 of the last 5 not yet classified)");
  assert.equal(kindWords({ status: "ok", M: 4, N: 4, R: 1, U: 0, share: 0.25 }), "likely yellow (drones) · red in 1 of the last 4 alerts");
  assert.equal(kindWords({ status: "ok", M: 2, N: 2, R: 1, U: 0, share: 0.5 }), "red or yellow equally likely · red in 1 of the last 2 alerts");
});

test("rotated coverage (production): history confirmed 1 h before tau + ACTIVE polls for the tail -> ok; a poll gap -> not enough data", () => {
  const s = stateFrom([A("1", "lvivska", T0 - 3 * HOUR, T0 - 2 * HOUR, "red")], HS);
  for (const u of regions.units) s.levelCoverage[u] = s.coverage[u] = [[HS, T0 - HOUR, T0 - HOUR]];   // last history call 1 h ago
  s.polls = [[T0 - 2 * HOUR, T0 - 60e3]];                                                            // ACTIVE every minute since
  const k = kindAt(s, T0, regions);
  assert.ok(regions.units.every(u => k.units[u].status === "ok"), "all units covered by history + polls");
  assert.equal(k.units.lvivska.R, 1);
  s.polls = [[T0 - 2 * HOUR, T0 - 40 * 60e3]];                                                       // polls stopped 40 min ago
  assert.equal(kindAt(s, T0, regions).units.lvivska.status, "not_enough_data");
});

test("an end that happened before tau but was only learned after tau: still running at tau (no new onset)", () => {
  // alert 1 ended at T0 - 4 h, but that end was learned at T0 + 1 h; alert 2 starts at T0 - 3 h
  const s = stateFrom([A("1", "lvivska", T0 - 5 * HOUR, T0 - 4 * HOUR, "yellow", { endKnown: T0 + HOUR }),
                       A("2", "lvivska", T0 - 3 * HOUR, T0 - 2 * HOUR, "red")], HS);
  assert.deepEqual((({ M, R }) => ({ M, R }))(kindAt(s, T0, regions).units.lvivska), { M: 1, R: 0 });   // ignoring endKnown -> M = 2
  assert.equal(kindAt(s, T0 + 2 * HOUR, regions).units.lvivska.M, 2);                                 // once the end is known
});
