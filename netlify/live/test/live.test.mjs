import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { unitIntervals, offsetAt } from "../lib/features.mjs";
import { emptyState, applyActive, applyHistory, knownAt, coverageAt, holesAt, forecastAll, mapUnit, DataError, stale,
         nextRotationUnit, POLL_GAP_MAX } from "../lib/live.mjs";

const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const model = JSON.parse(readFileSync(new URL("../model/model_live.json", import.meta.url)));
const H = 3600e3, D = 24 * H;
const T0 = Date.parse("2026-10-01T00:00:00Z");
const iso = t => new Date(t).toISOString();
const A = (id, oblast, start, end = null, upd = null, type = "air_raid") =>
  ({ id, location_oblast: oblast, location_type: "raion", started_at: iso(start), finished_at: end === null ? null : iso(end),
     updated_at: iso(upd ?? (end ?? start)), alert_type: type, alert_level: "yellow" });
const KYIV = "м. Київ", KYIVSKA = "Київська область";
const NAME = Object.fromEntries(Object.entries(regions.api_oblast_name).map(([n, u]) => [u, n]));
// every unit confirmed up to T with one closed alert 3 days earlier (time-since inputs are then defined everywhere)
const confirmAll = (s, T) => regions.units.forEach((u, i) => applyHistory(s, u, [A(`past-${u}`, NAME[u], T - 3 * D - i * 60e3, T - 3 * D + 20 * 60e3)], T, regions));

test("unit mapping: exact names, Kyiv City vs Kyivska, exclusions, unknown raises", () => {
  assert.equal(mapUnit(KYIV, regions), "kyiv_city");
  assert.equal(mapUnit(KYIVSKA, regions), "kyivska");
  assert.equal(mapUnit("Луганська область", regions), null);
  assert.equal(mapUnit("Автономна Республіка Крим", regions), null);
  assert.throws(() => mapUnit("Київ", regions), DataError);
});

test("schema: a bad record of a known unit is rejected and marked; an unknown oblast name fails the batch", () => {
  const s = emptyState(T0 - 40 * D);
  const bad = [{ ...A(1, KYIV, T0), started_at: "2026-10-01T00:00:00" }, A(2, KYIV, T0, null, null, "teleport"),
               A(3, KYIVSKA, T0, T0 - H), { ...A(4, KYIVSKA, T0), id: undefined }, { ...A(5, KYIVSKA, T0), started_at: null },
               { ...A(6, KYIVSKA, T0), updated_at: undefined }];
  const r = applyActive(s, [...bad, A(7, "Одеська область", T0 - 60e3)], T0, regions);
  assert.equal(r.rejected.length, 6);
  assert.deepEqual(Object.keys(s.records), ["7"]);                            // only the valid record is stored
  assert.deepEqual([...new Set(s.rejections.map(x => x[1]))].sort(), ["kyiv_city", "kyivska"]);
  assert.equal(applyActive(emptyState(T0), [A(8, KYIV, T0, null, null, "chemical")], T0, regions).rejected.length, 0);  // documented type
  assert.throws(() => applyActive(s, [A(9, "Невідома область", T0)], T0, regions), DataError);
  assert.throws(() => applyActive(s, [null], T0, regions), DataError);        // cannot be attributed to a unit
  assert.throws(() => applyActive(s, { nope: 1 }, T0, regions), DataError);
});

test("a rejected ACTIVE record blanks only its own unit; a rejected history record only flags caution", () => {
  const s = emptyState(T0 - 40 * D);
  confirmAll(s, T0);
  const tau = T0 + 30 * 60e3;
  for (let t = T0; t < tau; t += 60e3) applyActive(s, [], t, regions);
  applyActive(s, [{ ...A(1, KYIV, tau - 60e3), started_at: "bad" }], tau, regions);
  const res = applyHistory(s, "lvivska", [A(2, "Львівська область", T0 - 5 * H, T0 - 4 * H), { ...A(3, "Львівська область", T0 - 3 * H), finished_at: iso(T0 - 4 * H) }], tau, regions);
  assert.equal(res.rejected.length, 1);
  assert.ok(s.records["2"]);                                                   // the valid history record is kept
  const f = forecastAll(s, tau, model, regions);
  assert.equal(f.units.kyiv_city.state, "data_gap");
  assert.ok(f.units.kyiv_city.caution.includes("rejected_active_record"));
  assert.equal(f.units.lvivska.state, "forecast");
  assert.ok(f.units.lvivska.caution.includes("rejected_history_record"));
  assert.equal(f.units.kyivska.state, "forecast");                             // neighbours are not blanked
  assert.equal(forecastAll(s, tau + D, model, regions).units.kyiv_city.caution.includes("rejected_active_record"), false);
  const nRej = s.rejections.length;
  assert.throws(() => applyHistory(s, "lvivska", [A(4, KYIV, T0), { ...A(5, "Львівська область", T0), id: null }], tau, regions), DataError);
  assert.equal(s.records["4"], undefined);                                     // wrong unit: nothing written,
  assert.equal(s.rejections.length, nRej);                                     // not even rejection marks
  s.records["odesa-1"] = { ...s.records["2"], id: "odesa-1", unit: "odeska" };   // an id stored for another unit
  assert.throws(() => applyHistory(s, "lvivska", [A(6, "Львівська область", T0 - 2 * H, T0 - H), A("odesa-1", "Львівська область", T0)], tau, regions), /changed unit/);
  assert.equal(s.records["6"], undefined);                                     // the valid record before it is not written
  assert.equal(s.rejections.length, nRej);
});

test("active poll: new ids, vanished ids keep an unknown end, duplicates keep the latest parsed updated_at", () => {
  const s = emptyState(T0 - 40 * D);
  applyActive(s, [A(1, KYIV, T0 - 10 * 60e3), A(9, "Луганська область", T0 - 400 * D)], T0, regions);
  assert.equal(s.records["1"].firstSeen, T0);
  assert.equal(s.records["9"], undefined);                                    // excluded unit never stored
  applyActive(s, [], T0 + 60e3, regions);                                     // vanished
  assert.equal(s.records["1"].end, null);
  assert.deepEqual(s.records["1"].absent, [[T0 + 60e3, null]]);
  applyActive(s, [A(1, KYIV, T0 - 10 * 60e3)], T0 + 2 * 60e3, regions);      // reappears
  assert.deepEqual(s.records["1"].absent, [[T0 + 60e3, T0 + 2 * 60e3]]);
  applyActive(s, [], T0 + 3 * 60e3, regions);
  const k = knownAt(s, T0 + 2 * H).find(a => a.unit === "kyiv_city");
  assert.equal(k.end, null);                                                   // still open (24 h cap applies)
  applyActive(s, [A(1, KYIV, T0 - 10 * 60e3, null, T0 + 120e3)], T0 + 2 * 60e3, regions);
  applyActive(s, [A(1, KYIV, T0 - 10 * 60e3, null, T0 + 100e3)], T0 + 3 * 60e3, regions);   // older update ignored
  assert.equal(s.records["1"].updated, T0 + 120e3);
});

test("history reconciliation: exact end known only from the call time; versions respected", () => {
  const s = emptyState(T0 - 40 * D);
  applyActive(s, [A(1, KYIV, T0 - 10 * 60e3)], T0, regions);
  applyActive(s, [], T0 + 60e3, regions);
  const call = T0 + 20 * 60e3;
  applyHistory(s, "kyiv_city", [A(1, KYIV, T0 - 10 * 60e3, T0 + 30e3, T0 + 30e3),
                                A(2, KYIV, T0 + 2 * 60e3, T0 + 3 * 60e3)], call, regions);   // a short alert missed by polls
  assert.equal(s.records["1"].end, T0 + 30e3);
  // at a time before the reconciliation the end and the short alert are unknown (no leakage of later knowledge)
  const before = knownAt(s, call - 1);
  assert.equal(before.find(a => a.start === T0 - 10 * 60e3).end, null);
  assert.equal(before.filter(a => a.start === T0 + 2 * 60e3).length, 0);
  const after = knownAt(s, call);
  assert.equal(after.find(a => a.start === T0 - 10 * 60e3).end, T0 + 30e3);
  assert.equal(after.filter(a => a.start === T0 + 2 * 60e3).length, 1);
  assert.throws(() => applyHistory(s, "kyivska", [A(3, KYIV, T0)], call, regions), DataError);   // wrong unit
});

test("coverage: disjoint intervals and holes; poll gaps make event holes", () => {
  const s = emptyState(T0 - 100 * D);
  applyHistory(s, "kyiv_city", [], T0 - 60 * D, regions);                    // confirms [T0-90d, T0-60d)
  applyHistory(s, "kyiv_city", [], T0, regions);                             // confirms [T0-30d, T0): disjoint
  const h = holesAt(s, T0, regions);
  assert.deepEqual(h.label.kyiv_city, [[T0 - 100 * D, T0 - 90 * D], [T0 - 60 * D, T0 - 30 * D]]);
  applyActive(s, [], T0 + 60e3, regions);
  applyActive(s, [], T0 + 60e3 + POLL_GAP_MAX + 1, regions);                 // gap > 2 min between polls
  assert.equal(s.polls.length, 2);
});

test("forecast: data gap while warming up, a probability once covered, D-020 mask vs physical alert", () => {
  const s = emptyState(T0 - 40 * D);
  for (const u of regions.units) applyHistory(s, u, [], T0, regions);         // all confirmed up to T0
  const tau = T0 + 30 * 60e3;
  for (let t = T0; t <= tau; t += 60e3) applyActive(s, [A(5, KYIV, T0 - 26 * H)], t, regions);   // > 24 h standing alert
  applyActive(s, [A(5, KYIV, T0 - 26 * H), A(6, KYIVSKA, tau - 5 * 60e3)], tau, regions);
  const f = forecastAll(s, tau, model, regions);
  assert.equal(f.units.kyiv_city.physical_alert, true);
  assert.equal(f.units.kyiv_city.state, "forecast");                         // standing > 24 h: still forecast (D-020)
  assert.ok(f.units.kyiv_city.p > 0 && f.units.kyiv_city.p < 1);
  assert.equal(f.units.kyivska.state, "alert_running");                      // fresh alert: masked, no probability
  assert.equal(f.units.kyivska.p, null);
  const early = emptyState(T0 - 40 * D);
  applyActive(early, [], tau, regions);
  assert.equal(forecastAll(early, tau, model, regions).units.kyiv_city.state, "data_gap");   // nothing confirmed yet
});

test("vanished alert: outline off at once, mask keeps the unknown end until history reconciles it", () => {
  const s = emptyState(T0 - 40 * D);
  for (const u of regions.units) applyHistory(s, u, [], T0, regions);
  const t1 = T0 + 10 * 60e3, t2 = T0 + 20 * 60e3;
  for (let t = T0; t <= t1; t += 60e3) applyActive(s, [A(11, KYIV, T0 + 60e3)], t, regions);
  for (let t = t1 + 60e3; t <= t2; t += 60e3) applyActive(s, [], t, regions);           // gone from ACTIVE at t1 + 1 min
  let f = forecastAll(s, t2, model, regions);
  assert.equal(f.units.kyiv_city.physical_alert, false);
  assert.equal(f.units.kyiv_city.state, "alert_running");                     // end not confirmed: never guessed
  assert.equal(forecastAll(s, t1, model, regions).units.kyiv_city.physical_alert, true);
  applyHistory(s, "kyiv_city", [A(11, KYIV, T0 + 60e3, t1 + 30e3)], t2 + 60e3, regions);
  applyActive(s, [], t2 + 60e3, regions);
  f = forecastAll(s, t2 + 60e3, model, regions);
  assert.equal(f.units.kyiv_city.state, "forecast");
  assert.equal(f.units.kyiv_city.confirmed_until, t2 + 60e3);
  assert.equal(forecastAll(s, t2, model, regions).units.kyiv_city.state, "alert_running");   // as known at t2
});

test("truncation: the forecast at tau does not change when later polls/reconciliations arrive", () => {
  const s = emptyState(T0 - 40 * D);
  for (const u of regions.units) applyHistory(s, u, [], T0, regions);
  for (let t = T0; t <= T0 + 30 * 60e3; t += 60e3) applyActive(s, [], t, regions);
  const tau = T0 + 30 * 60e3;
  const f1 = forecastAll(s, tau, model, regions);
  for (let t = tau + 60e3; t <= tau + 40 * 60e3; t += 60e3) applyActive(s, [A(7, KYIV, tau + 30e3)], t, regions);
  applyHistory(s, "kyiv_city", [A(7, KYIV, tau + 30e3, tau + 10 * 60e3), A(8, KYIV, tau - 60e3, tau + 5 * 60e3)], tau + 41 * 60e3, regions);
  const f2 = forecastAll(s, tau, model, regions);
  assert.deepEqual(f2, f1);
  // negative control: using the reconciled end/alert regardless of when it became known changes the result
  const leaky = JSON.parse(JSON.stringify(s));
  for (const r of Object.values(leaky.records)) { r.firstSeen = 0; r.endKnown = 0; }
  assert.notDeepEqual(forecastAll(leaky, tau, model, regions).units.kyiv_city, f1.units.kyiv_city);
});

test("a history call made after tau never fills a hole as seen at tau (coverage carries its confirmation time)", () => {
  const s = emptyState(T0 - 40 * D);
  for (const u of regions.units) applyHistory(s, u, u === "kyiv_city" ? [A(21, KYIV, T0 - 5 * H, T0 - 4.5 * H)] : [], T0, regions);
  const tau = T0 + 3 * H;                                                     // labels s in [T0 - 1h, tau - 1h] sit in the hole
  for (let t = T0; t <= tau; t += 60e3) applyActive(s, [], t, regions);
  const before = forecastAll(s, tau, model, regions);
  applyHistory(s, "kyiv_city", [], tau + 10 * 60e3, regions);
  assert.deepEqual(coverageAt(s, "kyiv_city", tau), [[T0 - 30 * D, T0]]);
  assert.deepEqual(forecastAll(s, tau, model, regions), before);
  assert.notEqual(forecastAll(s, tau + 10 * 60e3, model, regions).units.kyiv_city.recent_rate, before.units.kyiv_city.recent_rate);
  // compaction only merges blocks confirmed > COMPACT_AFTER (8 days) before the newest call
  for (let k = 1; k <= 12; k++) applyHistory(s, "kyiv_city", [], tau + k * D, regions);
  assert.ok(s.coverage.kyiv_city.length < 14 && s.coverage.kyiv_city.length >= 9);
  assert.ok(s.coverage.kyiv_city.every(([a, b, c]) => b <= c));
});

test("poll gaps (runs every 5 min): up to 7 min between polls is covered, a longer gap (a missed run) is a national data gap", () => {
  const mk = gap => {
    const s = emptyState(T0 - 40 * D);
    confirmAll(s, T0);
    let t = T0;
    for (; t < T0 + 30 * 60e3; t += 5 * 60e3) applyActive(s, [], t, regions);
    t += gap - 5 * 60e3;
    for (const end = t + 20 * 60e3; t <= end; t += 5 * 60e3) applyActive(s, [], t, regions);
    return forecastAll(s, t - 5 * 60e3, model, regions);
  };
  const states = f => new Set(Object.values(f.units).map(x => x.state));
  assert.deepEqual(states(mk(5 * 60e3 + 20e3)), new Set(["forecast"]));       // one run + scheduler jitter
  assert.deepEqual(states(mk(7 * 60e3)), new Set(["forecast"]));
  assert.deepEqual(states(mk(7 * 60e3 + 1000)), new Set(["data_gap"]));
  assert.deepEqual(states(mk(10 * 60e3)), new Set(["data_gap"]));               // a missed run is a hole
});

test("per-unit label holes: a global list equals the same holes per unit; a hole in one unit changes only that unit", () => {
  const known = [{ unit: "kyiv_city", start: T0 - 50 * H, end: T0 - 49.5 * H }, { unit: "lvivska", start: T0 - 30 * H, end: T0 - 29 * H }];
  const ivs = unitIntervals(known), hs = T0 - 20 * D, tau = T0;
  const hole = [[T0 - 40 * H, T0 - 38 * H]];
  const glob = offsetAt(ivs, tau, regions, hs, hole);
  const per = offsetAt(ivs, tau, regions, hs, Object.fromEntries(regions.units.map(u => [u, hole])));
  assert.deepEqual(per, glob);
  const none = offsetAt(ivs, tau, regions, hs, {});
  const one = offsetAt(ivs, tau, regions, hs, { kyiv_city: hole });
  assert.notDeepEqual(one.kyiv_city, none.kyiv_city);
  for (const u of regions.units) if (u !== "kyiv_city") assert.deepEqual([one[u].k, one[u].n], [none[u].k, none[u].n]);
});

test("negative controls: an end used before it was known, and immature label hours, are caught by truncation", () => {
  const s = emptyState(T0 - 40 * D);
  confirmAll(s, T0);
  const tau = T0 + 3 * H + 20 * 60e3;
  for (let t = T0; t <= tau + 2 * H; t += 60e3) applyActive(s, t < T0 + 3 * H + 30 * 60e3 && t >= T0 + 2 * H ? [A(31, KYIV, T0 + 2 * H)] : [], t, regions);
  applyHistory(s, "kyiv_city", [A(31, KYIV, T0 + 2 * H, T0 + 2 * H + 10 * 60e3)], tau + 2 * H, regions);   // end known only later
  const real = forecastAll(s, tau, model, regions).units.kyiv_city;
  assert.equal(real.state, "alert_running");                                  // as known at tau: still open
  const leakyEnd = JSON.parse(JSON.stringify(s));
  for (const r of Object.values(leakyEnd.records)) if (r.endKnown !== null) r.endKnown = r.start;
  assert.notDeepEqual(forecastAll(leakyEnd, tau, model, regions).units.kyiv_city, real);
  // immature labels: an offset window ending at floor(tau) instead of floor(tau - 1 h) sees the onset at T0 + 2 h + ...
  const ivsAll = unitIntervals(knownAt(s, tau + 2 * H)), ivsTau = unitIntervals(knownAt(s, tau));
  const leaky = (iv, t) => offsetAt(iv, t + H, regions, s.historyStart, {}).kyiv_city;     // includes s in (t - 1h, t]
  const realOff = (iv, t) => offsetAt(iv, t, regions, s.historyStart, {}).kyiv_city;
  assert.deepEqual(realOff(ivsAll, tau), realOff(ivsTau, tau));               // the real offset is truncation-invariant
  const tau2 = T0 + 2 * H - 30 * 60e3;                                          // witness: onset at T0 + 2 h is in (s, s + 1 h] for s = T0 + 1 h
  assert.notDeepEqual(leaky(unitIntervals(knownAt(s, tau + 2 * H)), tau2), leaky(unitIntervals(knownAt(s, tau2)), tau2));
});

test("replay: forecasts recorded live over 9 days equal their recomputation from the final state (snapshots auditable)", () => {
  const s = emptyState(T0 - 30 * D);
  confirmAll(s, T0);
  const EVERY = 5 * 60e3, recorded = [];
  const alerts = [];                                                           // a few alerts per day in two units
  for (let d = 0; d < 9; d++) for (const [o, h] of [[KYIV, 3], [KYIVSKA, 9], [KYIV, 15]]) {
    const st = T0 + d * D + h * H + 7 * 60e3; alerts.push({ id: `r${d}-${h}`, o, st, en: st + 40 * 60e3 }); }
  let rot = 0;
  for (let t = T0 + EVERY; t <= T0 + 9 * D; t += EVERY) {
    applyActive(s, alerts.filter(a => a.st <= t && a.en > t).map(a => A(a.id, a.o, a.st)), t, regions);
    const u = regions.units[rot++ % 24];
    const name = Object.keys(regions.api_oblast_name).find(n => regions.api_oblast_name[n] === u);
    applyHistory(s, u, alerts.filter(a => a.o === name && a.en <= t).map(a => A(a.id, a.o, a.st, a.en)), t, regions);
    if (t % (6 * H) === 0) recorded.push([t, forecastAll(s, t, model, regions)]);
  }
  const last = recorded[recorded.length - 1][0];
  const kept = recorded.filter(([t]) => t >= last - 7 * D);
  assert.ok(kept.length >= 28);
  for (const [t, f] of kept) assert.deepEqual(forecastAll(s, t, model, regions), f, new Date(t).toISOString());
  assert.ok(kept.some(([, f]) => f.units.kyiv_city.state === "forecast"));
});

test("stale payloads and rotation", () => {
  const now = T0;
  assert.equal(stale({ status: { ok: true }, forecast: { tau: now - 60e3 } }, now), false);
  assert.equal(stale({ status: { ok: false }, forecast: { tau: now - 60e3 } }, now), true);
  assert.equal(stale({ status: { ok: true }, forecast: { tau: now - 11 * 60e3 } }, now), false);   // within two runs
  assert.equal(stale({ status: { ok: true }, forecast: { tau: now - 12 * 60e3 - 1 } }, now), true);
  const s = emptyState(0);
  const seen = new Set(); for (let i = 0; i < 24; i++) seen.add(nextRotationUnit(s, regions));
  assert.equal(seen.size, 24);
});
