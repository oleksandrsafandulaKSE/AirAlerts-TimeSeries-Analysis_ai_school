// M11 §A4: live forecast check, snapshot archive, history payload and the recent-pattern grid.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { emptyState, applyHistory, applyActive, forecastAll, knownAt, REJECT_KEEP } from "../lib/live.mjs";
import { unitIntervals, offsetAt } from "../lib/features.mjs";
import { scoreSnapshots, historyPayload, snapshotFlags, binOf, hourOfKey as hourOf, freezeDue, checkBlob, REASONS, SETTLE, KEEP, LOOKBACK } from "../lib/check.mjs";
import { recentPattern, kyivLocalToUtc } from "../lib/pattern.mjs";
import { runUpdate, snapshotKey, readSnapshots, readHistory, updateCheck } from "../lib/runner.mjs";

const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const model = JSON.parse(readFileSync(new URL("../model/model_live.json", import.meta.url)));
const MIN = 60e3, H = 3600e3, D = 24 * H;
const iso = t => new Date(t).toISOString();
const NAME = Object.fromEntries(Object.entries(regions.api_oblast_name).map(([n, u]) => [u, n]));
const A = (id, unit, start, end, type = "air_raid") =>
  ({ id: String(id), location_oblast: NAME[unit], location_type: "raion", started_at: iso(start),
     finished_at: end === null ? null : iso(end), updated_at: iso(end ?? start), alert_type: type });
const TAU = Date.parse("2026-10-01T10:00:00Z");
const NOW = TAU + 5 * H;                                       // settled: >= tau + 1 h + 3 h

// every unit's history confirmed at `call` (coverage [call - 30 d, call)), with the given alerts
function world(alerts = {}, call = NOW) {
  const s = emptyState(call - 40 * D);
  for (const u of regions.units) applyHistory(s, u, alerts[u] || [], call, regions);
  return s;
}
const allUnits = (x) => Object.fromEntries(regions.units.map(u => [u, typeof x === "function" ? x(u) : { ...x }]));
function snap(tau, units = {}, extra = {}) {
  const base = allUnits({ p: 0.1, state: "forecast", recent_rate: 0.2, caution: [] });
  for (const [u, v] of Object.entries(units)) base[u] = { ...base[u], ...v };
  return { key: snapshotKey(tau), value: { tau, written_at: tau, units: base, ...extra } };
}
const only = (unit, v = {}) => allUnits(u => u === unit ? { p: 0.1, state: "forecast", recent_rate: 0.2, caution: [], ...v }
                                                        : { p: null, state: "alert_running", recent_rate: 0.2, caution: [] });
const score = (s, snaps, now = NOW, opts = {}) => scoreSnapshots(s, snaps, now, regions, { epoch: 0, ...opts });
const rowOf = (r, unit) => r.rows.filter(x => x.unit === unit);
const near = (a, b, tol = 1e-12) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);

test("labels: an onset exactly at tau is NOT counted, one exactly at tau + 1 h IS", () => {
  // zero-duration alert at tau (an onset that does not put the unit under alert at tau); a later one at tau + 1 h
  const s = world({ odeska: [A(1, "odeska", TAU, TAU)], lvivska: [A(2, "lvivska", TAU + H, TAU + H + 20 * MIN)] });
  const r = score(s, [snap(TAU)]);
  assert.equal(rowOf(r, "odeska")[0].y, 0);
  assert.equal(rowOf(r, "lvivska")[0].y, 1);
  assert.equal(r.overall.positives, 1);
});

test("a unit under alert at tau (snapshot alert_running) is not scored even if an onset follows", () => {
  const s = world({ odeska: [A(1, "odeska", TAU + 10 * MIN, TAU + 30 * MIN)] });
  const r = score(s, [snap(TAU, { odeska: { state: "alert_running", p: null } })]);
  assert.equal(rowOf(r, "odeska").length, 0);
  assert.equal(r.excluded.not_forecast, 1);
});

test("unsettled (now < tau + 4 h) and unconfirmed coverage are not scored; tau + 4 h exactly is settled", () => {
  const s = world({}, TAU + 2 * H);
  assert.equal(score(s, [snap(TAU)], TAU + H + SETTLE - 1).excluded.unsettled, 24);
  assert.equal(score(s, [snap(TAU)], TAU + H + SETTLE).rows.length, 24);
  const early = world({}, TAU + 30 * MIN);                      // history confirmed only to tau + 30 min
  const r = score(early, [snap(TAU)], NOW);
  assert.equal(r.rows.length, 0);
  assert.equal(r.excluded.coverage_hole, 24);
});

test("a coverage hole inside [tau - 24 h, tau + 1 h] -> not scored, although coverage is confirmed until later", () => {
  const s = world({}, NOW);
  s.coverage.odeska = [[TAU - 40 * D, TAU - 5 * H, TAU - 5 * H], [TAU - 3 * H, NOW, NOW]];
  s.coverage.lvivska = [[TAU - 40 * D, TAU - 24 * H - 1, TAU - 24 * H - 1], [TAU - 24 * H, NOW, NOW]];   // hole before the window
  s.coverage.kyivska = [[TAU - 40 * D, TAU - 24 * H + 1, NOW], [TAU - 24 * H + 1, NOW, NOW]];           // touching blocks
  const r = score(s, [snap(TAU)]);
  assert.equal(rowOf(r, "odeska").length, 0);
  assert.equal(rowOf(r, "lvivska").length, 1);
  assert.equal(rowOf(r, "kyivska").length, 1);
  assert.equal(r.excluded.coverage_hole, 1);
});

test("pooled BSS (not the mean of per-day skills); model = recent rate -> exactly 0; bins sum to rows", () => {
  const t1 = TAU, t2 = TAU + D;
  const s = world({ odeska: [A(1, "odeska", t1 + 20 * MIN, t1 + 40 * MIN)] }, t2 + 5 * H);
  const r = score(s, [snap(t1, only("odeska", { p: 0.5, recent_rate: 0.1 })), snap(t2, only("odeska", { p: 0.1, recent_rate: 0.5 }))], t2 + 5 * H);
  assert.deepEqual(r.rows.map(x => x.y), [1, 0]);
  const pooled = 1 - (0.25 + 0.01) / (0.81 + 0.25), meanDaily = ((1 - 0.25 / 0.81) + (1 - 0.01 / 0.25)) / 2;
  near(r.overall.bss, pooled);
  assert.ok(Math.abs(pooled - meanDaily) > 0.05);
  assert.equal(r.days.length, 2);
  near(r.days[1].cumulative_bss, pooled);
  near(r.days[0].bss, 1 - 0.25 / 0.81);
  const same = score(world({ odeska: [A(1, "odeska", TAU + 20 * MIN, TAU + 40 * MIN)] }),
                     [snap(TAU, allUnits(u => ({ p: 0.03 + regions.units.indexOf(u) / 100, recent_rate: 0.03 + regions.units.indexOf(u) / 100, state: "forecast", caution: [] })))]);
  assert.equal(same.overall.bss, 0);
  assert.equal(same.reliability.reduce((a, b) => a + b.rows, 0), same.overall.rows);
  assert.equal(same.overall.rows, 24);
});

test("BSS null with a reason: no rows, zero reference loss; p = 1.0 lands in the last bin", () => {
  const none = score(world(), []);
  assert.equal(none.overall.bss, null);
  assert.equal(none.overall.bss_reason, "no rows");
  const z = score(world(), [snap(TAU, allUnits({ p: 1.0, recent_rate: 0, state: "forecast", caution: [] }))]);
  assert.equal(z.overall.rows, 24);
  assert.equal(z.overall.bss, null);
  assert.equal(z.overall.bss_reason, "zero reference loss");
  assert.equal(z.reliability[9].rows, 24);
  assert.equal(binOf(1.0), 9); assert.equal(binOf(0.0999999), 0); assert.equal(binOf(0.1), 1); assert.equal(binOf(0.9), 9);
  assert.ok(z.overall.low_n);
});

test("a rejected_history_record caution at issue -> not scored", () => {
  const r = score(world(), [snap(TAU, { odeska: { caution: ["rejected_history_record"] }, lvivska: { caution: ["few_hours"] } })]);
  assert.equal(rowOf(r, "odeska").length, 0);
  assert.equal(rowOf(r, "lvivska").length, 1);
  assert.equal(r.excluded.rejected_at_issue, 1);
});

test("rejections logged after issue exclude (log survives the 24 h expiry); tau - 24 h - 1 ms does not", () => {
  const s = world();
  s.rejections = [];                                            // the live 24 h marks have expired
  const log = [[TAU + 2 * H, "odeska", "history"], [TAU - 24 * H - 1, "lvivska", "history"], [TAU - 24 * H, "kyivska", "active"]];
  const r = score(s, [snap(TAU)], NOW, { rejectionLog: log });
  assert.equal(rowOf(r, "odeska").length, 0);
  assert.equal(rowOf(r, "lvivska").length, 1);
  assert.equal(rowOf(r, "kyivska").length, 0);
  assert.equal(r.excluded.rejected_after_issue, 2);
});

test("rejection_log: written by the runner, kept 35 days, survives the 24 h expiry of state.rejections", async () => {
  const store = memStore();
  const T0 = Date.parse("2026-10-01T00:00:00Z");
  await store.setJSON("state", world({}, T0));
  const bad = { ...A("b1", "odeska", T0 - 10 * MIN, null), alert_type: "teleport" };
  await runUpdate({ fetchFn: fetchOf(url => url.includes("active") ? [bad] : []), store, token: "t", now: T0, model, regions });
  assert.deepEqual(await store.get("rejection_log"), [[T0, "odeska", "active"]]);
  const later = T0 + REJECT_KEEP + 2 * H;
  await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: later, model, regions });
  assert.equal((await store.get("state")).rejections.length, 0);          // live marks expired
  assert.deepEqual(await store.get("rejection_log"), [[T0, "odeska", "active"]]);
  const bad2 = { ...bad, id: "b2", location_oblast: NAME.lvivska };
  // kept 35 d + 24 h: the oldest kept snapshot (tau = now - 35 d) still sees rejections back to tau - 24 h
  await runUpdate({ fetchFn: fetchOf(url => url.includes("active") ? [bad2] : []), store, token: "t", now: T0 + KEEP + LOOKBACK - H, model, regions });
  assert.equal((await store.get("rejection_log")).length, 2);
  const bad3 = { ...bad, id: "b3", location_oblast: NAME.kyivska };
  await runUpdate({ fetchFn: fetchOf(url => url.includes("active") ? [bad3] : []), store, token: "t", now: T0 + KEEP + LOOKBACK + H, model, regions });
  assert.deepEqual((await store.get("rejection_log")).map(x => x[1]), ["lvivska", "kyivska"]);   // only the oldest entry is gone
});

test("late boundary: tau = hour + 14:59.999 is scored, hour + 15:00.000 is late; legacy snapshots are not scored", () => {
  const s = world();
  const ok = snap(TAU); ok.value.tau = TAU + 15 * MIN - 1;
  const late = snap(TAU + H); late.value.tau = TAU + H + 15 * MIN;
  const legacy = snap(TAU + 2 * H); delete legacy.value.written_at;
  const r = score(s, [ok, late, legacy], NOW + 3 * H);
  assert.equal(snapshotFlags(ok.key, ok.value, 0).late, false);
  assert.equal(snapshotFlags(late.key, late.value, 0).late, true);
  assert.equal(r.rows.length, 24);
  assert.equal(r.excluded.late, 24);
  assert.equal(r.excluded.legacy, 24);
  const before = score(s, [snap(TAU)], NOW, { epoch: TAU + 1 });           // key hour before the check epoch -> legacy
  assert.equal(before.excluded.legacy, 24);
  assert.equal(score(s, [snap(TAU)], NOW, { epoch: null }).excluded.legacy, 24);
});

test("reconciliation: an alert that started before tau and ran at tau -> not scored, although the snapshot said forecast", () => {
  const s = world({ odeska: [A(1, "odeska", TAU - 30 * MIN, TAU + 10 * MIN)],
                    lvivska: [A(2, "lvivska", TAU - 30 * H, TAU + 2 * H)] });          // standing (> 24 h): not under alert
  const r = score(s, [snap(TAU)]);
  assert.equal(rowOf(r, "odeska").length, 0);
  assert.equal(r.excluded.reconciled_under_alert, 1);
  assert.equal(rowOf(r, "lvivska").length, 1);
  assert.deepEqual(REASONS.filter(k => r.excluded[k]), ["reconciled_under_alert"]);
});

test("isolation: archived p / recent_rate are used byte-identically after later data changes; a leaky scorer is caught", async () => {
  const store = memStore();
  const T0 = Date.parse("2026-10-01T09:00:00Z");
  const s0 = world({ odeska: [A(1, "odeska", T0 - 30 * H, T0 - 29 * H)] }, T0);
  await store.setJSON("state", s0);
  for (let t = T0; t <= T0 + 2 * H; t += 5 * MIN)
    await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: t, model, regions });
  const snaps = await readSnapshots(store);
  const archived = JSON.stringify(snaps.map(x => x.value));
  const tau = snaps[1].value.tau;                              // 10:00
  assert.equal(snaps[1].value.units.odeska.state, "forecast");
  // later knowledge: an end changes, reconciled records appear, new onsets (one unknown at issue, one in the label window)
  const st = await store.get("state");
  const later = tau + 6 * H;
  applyHistory(st, "odeska", [A(1, "odeska", T0 - 30 * H, T0 - 28 * H), A(7, "odeska", tau - 40 * MIN, tau - 35 * MIN),
                              A(8, "odeska", tau + 20 * MIN, tau + 30 * MIN)], later, regions);
  for (const u of regions.units) if (u !== "odeska") applyHistory(st, u, [], later, regions);
  const r = score(st, snaps, later, { epoch: hourOf(snaps[0].key) });
  assert.equal(JSON.stringify(snaps.map(x => x.value)), archived);
  const row = r.rows.find(x => x.unit === "odeska" && x.tau === tau);
  assert.equal(row.p, snaps[1].value.units.odeska.p);
  assert.equal(row.recent_rate, snaps[1].value.units.odeska.recent_rate);
  assert.equal(row.y, 1);
  // identity check: every scored row's p / recent_rate equals the archived snapshot's, byte for byte
  const byKey = new Map(JSON.parse(archived).map(v => [v.tau, v]));
  const usesArchive = rows => rows.every(x => byKey.get(x.tau).units[x.unit].p === x.p && byKey.get(x.tau).units[x.unit].recent_rate === x.recent_rate);
  assert.ok(r.rows.length > 0 && usesArchive(r.rows));
  // negative control: a deliberately leaky scorer recomputes recent_rate from FINAL data with labels up to s = tau
  // (> tau - 1 h); the identity check must catch it
  const leakyScore = (state, snapshots, now) => {
    const ivs = unitIntervals(knownAt(state, now));
    const res = score(state, snapshots, now, { epoch: snapshots[0] && hourOf(snapshots[0].key) });
    for (const x of res.rows) x.recent_rate = offsetAt(ivs, x.tau + H, regions, state.historyStart)[x.unit].rate;
    return res;
  };
  const leaky = leakyScore(st, snaps, later);
  assert.equal(leaky.rows.length, r.rows.length);
  assert.equal(usesArchive(leaky.rows), false);
});

const pastAlerts = T0 => Object.fromEntries(regions.units.map(u => [u, [A(`p-${u}`, u, T0 - 3 * D, T0 - 3 * D + 20 * MIN)]]));

test("first write in the hour wins and is scored; a run at hour + 16 min writes a late snapshot that is not scored; check hourly", async () => {
  const store = memStore();
  const T0 = Date.parse("2026-10-01T09:00:00Z");
  await store.setJSON("state", world(pastAlerts(T0), T0));
  await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: T0, model, regions });
  const first = store.m.get(snapshotKey(T0));
  for (const t of [T0 + 5 * MIN, T0 + 10 * MIN])
    await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: t, model, regions });
  assert.equal(store.m.get(snapshotKey(T0)), first);                                  // later runs in the hour do not overwrite
  assert.equal(JSON.parse(first).written_at, T0);
  assert.equal(JSON.parse(first).late, false);
  assert.equal(await store.get("check_epoch"), T0);
  await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: T0 + H + 16 * MIN, model, regions });   // 09:10 -> 10:16: a missed-runs hour
  const late = await store.get(snapshotKey(T0 + H));
  assert.equal(late.late, true);
  const st = await store.get("state");
  for (const u of regions.units) applyHistory(st, u, [], T0 + 8 * H, regions);           // later history confirms the window
  const snaps = await readSnapshots(store);
  const r = score(st, snaps, T0 + 9 * H, { epoch: await store.get("check_epoch") });
  assert.equal(r.excluded.late, 24);
  assert.equal(r.rows.length, 24);                                                       // the first write is scored ...
  const firstSnap = JSON.parse(first);
  assert.ok(r.rows.every(x => x.tau === T0 && x.p === firstSnap.units[x.unit].p && x.recent_rate === firstSnap.units[x.unit].recent_rate));
  // ... a snapshot written before the check epoch is legacy, never scored; one written by the first M11 run of a
  // mid-hour deploy (written_at >= epoch) is scored
  assert.equal(score(st, snaps, T0 + 9 * H, { epoch: T0 + 2 * MIN }).excluded.legacy, 24);
  const mid = snaps.map(x => x.key === snapshotKey(T0) ? { key: x.key, value: { ...x.value, written_at: T0 + 7 * MIN } } : x);
  assert.equal(score(st, mid, T0 + 9 * H, { epoch: T0 + 7 * MIN }).rows.length, 24);
  const c = await store.get("check");
  assert.equal(c.computed_hour, T0 + H);                       // recomputed once in the hour, not on every run
  const again = await updateCheck(store, st, T0 + H + 50 * MIN, regions, T0);
  assert.equal(again.computed_at, c.computed_at);
  assert.ok(!("rows" in c));
});

test("Kyiv City and Kyivska with different alerts stay separate through history, check and group totals", () => {
  const s = world({ kyiv_city: [A(1, "kyiv_city", TAU + 10 * MIN, TAU + 20 * MIN)], kyivska: [A(2, "kyivska", TAU - 3 * H, TAU - 2 * H)] });
  const r = score(s, [snap(TAU, { kyiv_city: { p: 0.4 }, kyivska: { p: 0.05 } })]);
  assert.equal(rowOf(r, "kyiv_city")[0].y, 1);
  assert.equal(rowOf(r, "kyivska")[0].y, 0);
  assert.equal(r.groups.kyiv_city.rows, 1);
  assert.equal(r.groups.kyiv_city.positives, 1);
  assert.equal(r.groups.rear.positives, 0);
  near(r.units.kyiv_city.brier_p, 0.36);
  near(r.units.kyivska.brier_p, 0.0025);
  const h = historyPayload(s, [snap(TAU)], NOW, regions, { epoch: 0 });
  assert.deepEqual(h.units.kyiv_city.onsets, [TAU + 10 * MIN]);
  assert.deepEqual(h.units.kyivska.onsets, [TAU - 3 * H]);
});

test("history payload: physical union, open alerts flagged, D-020 capped intervals (exactly 24 h capped at start + 24 h)", () => {
  const s = world({ odeska: [A(1, "odeska", TAU - 50 * H, TAU - 26 * H), A(2, "odeska", TAU - 3 * H, TAU - 2 * H),
                             A(3, "odeska", TAU - 150 * MIN, TAU - 90 * MIN)] });
  applyActive(s, [A(4, "odeska", NOW - 30 * H, null)], NOW, regions);                       // open, standing
  const h = historyPayload(s, [snap(TAU), snap(TAU - 8 * D)], NOW, regions, { epoch: 0 });
  const o = h.units.odeska;
  assert.deepEqual(o.physical, [[TAU - 50 * H, TAU - 26 * H], [TAU - 3 * H, TAU - 90 * MIN]]);
  assert.deepEqual(o.open, [[NOW - 30 * H, NOW, "active"]]);
  // 24 h alert capped at exactly start + 24 h; the open standing alert counts 24 h and merges with the overlapping two
  assert.deepEqual(o.capped, [[TAU - 50 * H, TAU - 26 * H], [NOW - 30 * H, NOW - 6 * H]]);
  assert.equal(h.snapshots.length, 1);                                                      // only the last 7 days
  assert.deepEqual(h.snapshots[0].units.odeska, [0.1, "forecast", 0.2]);
  assert.ok(o.coverage.length === 1 && o.coverage[0][1] === NOW);
  assert.ok(!JSON.stringify(h).includes("location_oblast"));                                // derived only, no raw records
});

test("pattern: 25-hour day 2025-10-26 (repeated 03:00): the 03-06 block holds 4 real hours and both 03:30s", () => {
  const now = Date.parse("2025-10-27T12:00:00Z");
  const on = [Date.parse("2025-10-26T00:30:00Z"), Date.parse("2025-10-26T01:30:00Z")];   // 03:30 EEST and 03:30 EET
  const days = recentPattern(on, [[now - 10 * D, now]], now, 2);
  const d = days[0];
  assert.equal(d.date, "2025-10-26");
  assert.equal(d.blocks[1].hours, 4);
  assert.equal(d.blocks[1].count, 2);
  assert.equal(d.blocks.reduce((a, b) => a + b.hours, 0), 25);
  assert.equal(d.partial, false);
});

test("pattern: 23-hour day 2026-03-29 (skipped 03:00): the 03-06 block holds 2 real hours", () => {
  const now = Date.parse("2026-03-30T12:00:00Z");
  const days = recentPattern([Date.parse("2026-03-29T01:00:00Z")], [[now - 10 * D, now]], now, 2);
  const b = days[0].blocks[1];
  assert.equal(days[0].date, "2026-03-29");
  assert.equal(b.hours, 2);
  assert.equal(b.start, Date.parse("2026-03-29T01:00:00Z"));
  assert.equal(b.count, 1);
  assert.equal(days[0].blocks.reduce((a, x) => a + x.hours, 0), 23);
  assert.equal(kyivLocalToUtc(2026, 3, 29, 3), kyivLocalToUtc(2026, 3, 29, 4));
});

test("pattern: partial first day, a 30-min coverage hole -> no data (not 0), a covered quiet block -> 0, future blocks", () => {
  const now = Date.parse("2026-10-12T09:30:00Z");                     // 12:30 Kyiv (EEST)
  const start = Date.parse("2026-10-11T07:00:00Z");                   // 10:00 Kyiv on day 1
  const hole = [Date.parse("2026-10-11T16:00:00Z"), Date.parse("2026-10-11T16:30:00Z")];   // 19:00-19:30 Kyiv
  const days = recentPattern([Date.parse("2026-10-11T08:00:00Z")], [[start, hole[0]], [hole[1], now]], now, 2);
  const [d1, d2] = days;
  assert.deepEqual(d1.blocks.map(b => b.status), ["no_data", "no_data", "no_data", "no_data", "ok", "ok", "no_data", "ok"]);
  assert.equal(d1.blocks[3].count, null);                              // 09-12 Kyiv: partly before the history starts
  assert.equal(d1.blocks[4].count, 0);                                 // 12-15 covered, no onsets -> 0
  assert.equal(d1.blocks[6].count, null);                              // 18-21 contains the 30-min hole
  assert.ok(d1.partial);
  assert.deepEqual(d2.blocks.map(b => b.status), ["ok", "ok", "ok", "ok", "in_progress", "future", "future", "future"]);
  assert.equal(d2.blocks[4].count, null);
  assert.ok(d2.partial);
});

test("pattern source is self-contained (inlined into the page by build_site.py)", () => {
  const src = readFileSync(new URL("../lib/pattern.mjs", import.meta.url), "utf8");
  assert.ok(!/^\s*import /m.test(src));
});

test("the API functions serve history and check; neither payload contains the token", async () => {
  const store = memStore();
  const T0 = Date.parse("2026-10-01T09:00:00Z");
  // one closed alert per unit 3 days earlier, so the time-since inputs are defined and the units are forecast
  await store.setJSON("state", world(Object.fromEntries(regions.units.map(u => [u, [A(`p-${u}`, u, T0 - 3 * D, T0 - 3 * D + 20 * MIN)]])), T0));
  const TOKEN = "test-token-DO-NOT-LEAK-27182818";
  for (let t = T0; t <= T0 + 5 * H; t += 20 * MIN) await runUpdate({ fetchFn: fetchOf(() => []), store, token: TOKEN, now: t, model, regions });
  const h = await readHistory(store, T0 + 5 * H, regions);
  assert.equal(h.snapshots.length, 6);
  assert.ok(h.exploratory);
  const c = await store.get("check");
  assert.equal(c.ok, true);
  assert.ok(c.overall.rows > 0);                                      // the 09:00 and 10:00 snapshots are settled at 14:00
  assert.equal(c.excluded.unsettled, 4 * 24);
  for (const v of store.m.values()) assert.ok(!v.includes(TOKEN));
  assert.ok(!JSON.stringify(h).includes(TOKEN));
  for (const f of ["history.mjs", "check.mjs"]) {
    const src = readFileSync(new URL(`../../functions/${f}`, import.meta.url), "utf8");
    assert.match(src, /consistency: "strong"/);
    assert.ok(!/ALERTS_IN_UA_TOKEN/.test(src));
  }
});

function memStore() {
  const m = new Map();
  return { m, async get(k) { return m.has(k) ? JSON.parse(m.get(k)) : null; },
           async setJSON(k, v) { m.set(k, JSON.stringify(v)); }, async delete(k) { m.delete(k); },
           async list({ prefix = "" } = {}) { return { blobs: [...m.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })), directories: [] }; } };
}
function fetchOf(fn) { return async (url) => ({ ok: true, status: 200, json: async () => ({ alerts: fn(url) }) }); }

test("a failing check computation is stored, put in the run status and logged; the forecast is still written", async () => {
  const store = memStore();
  const T0 = Date.parse("2026-10-01T09:00:00Z");
  await store.setJSON("state", world(pastAlerts(T0), T0));
  await store.setJSON("rejection_log", { corrupt: true });              // a corrupt blob makes scoring throw
  const errs = []; const orig = console.error; console.error = m => errs.push(m);
  let st;
  try { st = await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: T0 + 2 * MIN, model, regions }); }
  finally { console.error = orig; }
  assert.equal(st.ok, true);
  const c = await store.get("check");
  assert.equal(c.ok, false);
  assert.ok(st.check_error && st.check_error === c.error);
  assert.equal((await store.get("status")).check_error, c.error);
  assert.equal(errs.length, 1);
  assert.equal((await store.get("latest")).tau, T0 + 2 * MIN);
});

// ---- cumulative since launch (human, 2026-10-18): frozen per-day totals in check_archive ----
test("cumulative: a frozen day adds to the live days, pooled; its remaining snapshots are not counted twice", () => {
  const t1 = TAU, t2 = TAU + D;
  const s = world({ odeska: [A(1, "odeska", t1 + 20 * MIN, t1 + 40 * MIN)] }, t2 + 5 * H);
  const snaps = [snap(t1, only("odeska", { p: 0.5, recent_rate: 0.1 })), snap(t2, only("odeska", { p: 0.1, recent_rate: 0.5 }))];
  const full = score(s, snaps, t2 + 5 * H);
  const day1 = new Date(t1).toISOString().slice(0, 10);
  const frozen = { [day1]: full.live_totals[day1] };
  const c = score(s, snaps, t2 + 5 * H, { archive: frozen });              // day 1 snapshots still present
  near(c.overall.bss, full.overall.bss);
  assert.equal(c.overall.rows, 2);
  assert.equal(c.rows.length, 1);                                            // only the live day was scored again
  assert.deepEqual(c.days.map(d => [d.day, d.frozen]), [[day1, true], [new Date(t2).toISOString().slice(0, 10), false]]);
  const gone = score(s, [snaps[1]], t2 + 5 * H, { archive: frozen });       // day 1 snapshots deleted
  near(gone.overall.bss, full.overall.bss);
  assert.equal(gone.units.odeska.rows, 2);
  assert.equal(gone.reliability.reduce((a, b) => a + b.rows, 0), 2);
  assert.equal(gone.frozen_days, 1);
  assert.equal(gone.first_day, day1);
  const blob = checkBlob(gone);
  assert.ok(!("live_totals" in blob) && !("due" in blob) && !("rows" in blob));
});

test("freeze boundary: a day is due at day start + 35 d - 24 h, before any of its snapshots can expire", () => {
  const d0 = Date.parse("2026-10-01T00:00:00Z");
  assert.equal(freezeDue("2026-10-01", d0 + KEEP - D - 1), false);
  assert.equal(freezeDue("2026-10-01", d0 + KEEP - D), true);
  assert.ok(d0 + KEEP - D < d0 + KEEP);                                      // first deletion of that day: key <= now - 35 d
});

test("runner: a day is frozen in check_archive, its snapshots are deleted only afterwards, and it stays in the check", async () => {
  const store = memStore();
  const D0 = Date.parse("2026-10-01T00:00:00Z"), T0 = D0 + 9 * H;
  await store.setJSON("state", world(pastAlerts(T0), T0));
  await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: T0, model, regions });
  const st = await store.get("state");
  for (const u of regions.units) applyHistory(st, u, [], T0 + 2 * H, regions);     // confirms [tau - 24 h, tau + 1 h]
  await store.setJSON("state", st);
  const run = t => runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: t, model, regions });
  await run(D0 + KEEP - D - H);                                                 // not due yet
  assert.equal(await store.get("check_archive"), null);
  assert.ok(store.m.has(snapshotKey(T0)));
  await run(D0 + KEEP - D + H);                                                 // due: frozen, snapshot still there
  const arch = await store.get("check_archive");
  assert.equal(arch.days["2026-10-01"].overall.rows, 24);
  assert.ok(store.m.has(snapshotKey(T0)));
  await run(D0 + KEEP + 10 * H);                                                // past retention: deleted after freezing
  assert.equal(store.m.has(snapshotKey(T0)), false);
  const c = await store.get("check");
  const day = c.days.find(d => d.day === "2026-10-01");
  assert.ok(day.frozen && day.rows === 24);
  assert.ok(c.overall.rows >= 24 && c.frozen_days >= 1);
});

test("runner: if freezing fails, old snapshots are kept; a lost archive is an error, not a silent restart", async () => {
  const store = memStore();
  const D0 = Date.parse("2026-10-01T00:00:00Z"), T0 = D0 + 9 * H;
  await store.setJSON("state", world(pastAlerts(T0), T0));
  await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: T0, model, regions });
  await store.setJSON("rejection_log", { corrupt: true });                     // scoring throws -> nothing frozen
  const orig = console.error; console.error = () => {};
  try {
    const st = await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: D0 + KEEP + 10 * H, model, regions });
    assert.ok(st.check_error);
    assert.ok(store.m.has(snapshotKey(T0)));                                   // kept: its day is not frozen
    await store.setJSON("rejection_log", []);
    await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: D0 + KEEP + 11 * H, model, regions });
    assert.ok((await store.get("check_archive")).days["2026-10-01"]);
    store.m.delete("check_archive");                                           // lost blob
    const st2 = await runUpdate({ fetchFn: fetchOf(() => []), store, token: "t", now: D0 + KEEP + 12 * H, model, regions });
    assert.match(st2.check_error, /check_archive is missing/);
  } finally { console.error = orig; }
});
