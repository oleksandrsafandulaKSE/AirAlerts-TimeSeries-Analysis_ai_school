// M12 (plans/M12.md): the live model registry — parity with the Python pipeline per (type, H) on the real API
// reconstruction, independent truncation tests per H with a negative control, the air-raid filter (D-045), the inactive
// rule, the blend weight and the live labelling of pending rows.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { loadRegistry, registryAt, weightAt, labelRow, gapMasked, recentRate, calibrate, blendItems, knownByType, compactSnapshot,
         MAIN_ALERT_TYPES, SETTLE } from "../lib/models.mjs";
import { unitIntervals } from "../lib/features.mjs";

const HOUR = 3600e3, DAY = 24 * HOUR;
const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const dir = new URL("../model/m12/", import.meta.url);
const J = f => JSON.parse(readFileSync(new URL(f, dir)));
const registry = J("registry.json");
const models = Object.fromEntries(registry.models.map(m => [m.key, J(`model_${m.key}.json`)]));
const seed = J("blend_seed.json");
const parity = J("parity_sample.json");
const rec = JSON.parse(readFileSync(new URL("./m12_parity_records.json", import.meta.url)));

// state: every record known from its start, its end known at its end (event-time reconstruction, as the Python
// frames), coverage confirmed from historyStart on (the dump has no hole)
function stateFrom(records, historyStart) {
  const s = { records: {}, coverage: {}, levelCoverage: {}, polls: [], rotation: 0, historyStart, rejections: [], historyFail: {} };
  for (const r of records) s.records[r.id] = { id: r.id, unit: r.unit, level: "raion", alert_type: r.alert_type, start: r.start,
    end: r.end, updated: r.start, firstSeen: r.start, endKnown: r.end, endSource: r.end === null ? null : "history", absent: [],
    levels: [[r.start, r.level]] };
  for (const u of regions.units) s.levelCoverage[u] = s.coverage[u] = [[historyStart, 8.64e15, historyStart]];
  return s;
}
// label gaps = [EPOCH, historyStart) for every unit, as src/config.mask_gaps (and live.mjs forecastAll's beforeHistory)
const ctxAt = (hs, extra = {}) => ({ zones: [[-8.64e15, hs + DAY]],
  labelGaps: Object.fromEntries(regions.units.map(u => [u, [[-8.64e15, hs]]])), rej: { active: new Set(), history: new Set() }, debug: true, ...extra });
const reg = loadRegistry({ registry, models, seed, activation: { active: false } });
const ACT = { active: true, activated_at: registry.earliest_activation, test_metrics_sha256: "0".repeat(64) };
const state = stateFrom(rec.records, rec.historyStart);
const close = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

test("registry: 9 models, air-raid only, inactive as shipped", () => {
  assert.deepEqual(registry.models.map(m => m.key).sort(),
                   ["any_h1", "any_h12", "any_h24", "any_h3", "any_h6", "red_h1", "red_h3", "yellow_h1", "yellow_h3"]);
  assert.deepEqual(MAIN_ALERT_TYPES, ["air_raid"]);
  assert.equal(J("activation.json").active, false);
  assert.throws(() => blendItems({ items: {} }, reg, 0, {}), /not allowed while the registry is inactive/);
});

test("parity with Python per (type, H): features, raw, calibrated model, D-025 baseline (1e-9)", () => {
  const byTau = {};
  for (const [key, p] of Object.entries(parity)) for (const r of p.rows) (byTau[r.tau] ||= []).push([key, r]);
  let n = 0;
  for (const [tau, list] of Object.entries(byTau)) {
    const out = registryAt(state, Number(tau), regions, reg, ctxAt(rec.historyStart));
    for (const [key, r] of list) {
      const u = out.items[key].units[r.unit];
      const m = reg.items.find(x => x.key === key);
      assert.equal(u.state, "forecast", `${key} ${r.unit} ${new Date(Number(tau)).toISOString()}: state ${u.state}`);
      r.x.forEach((v, i) => close(u.x[i], v === null ? NaN : v, 1e-9, `${key} ${r.unit} ${tau} ${m.features[i]}`));
      close(u.p_model, r.p_model, 1e-9, `${key} ${r.unit} ${tau} p_model`);
      close(u.p_baseline, r.p_baseline, 1e-12, `${key} ${r.unit} ${tau} p_baseline`);
      n += 1;
    }
  }
  assert.ok(n >= 9 * 150, `only ${n} parity rows`);
});

test("parity: under an alert of the model's type at tau -> no forecast", () => {
  for (const [key, p] of Object.entries(parity)) {
    assert.ok(p.under_alert.length > 0, key);
    for (const r of p.under_alert) {
      const u = registryAt(state, r.tau, regions, reg, ctxAt(rec.historyStart)).items[key].units[r.unit];
      assert.equal(u.state, "alert_running", `${key} ${r.unit} ${r.tau}`);
      assert.equal(u.p_model, null);
    }
  }
});

test("parity: operational blend weight from the seed equals Python's blend.weights (cut-off = validation end)", () => {
  for (const [key, p] of Object.entries(parity)) {
    const m = reg.items.find(x => x.key === key);
    for (const w of p.weights) {
      const got = weightAt(m.seed.labelled, w.tau, m.Hms, m.blend_cutoff);
      close(got.w, w.w, 1e-12, `${key} w at ${w.tau}`);
      assert.equal(got.n, w.n, `${key} n at ${w.tau}`);
    }
  }
});

test("seed: no labelled row past T_seed; pending rows carry no label; nothing before the validation end", () => {
  for (const m of reg.items) {
    const H = m.Hms, T = m.seed.T_seed;
    assert.ok(m.seed.labelled.every(r => r.s + H <= T && r.s >= m.blend_cutoff && (r.y === 0 || r.y === 1)), m.key);
    assert.ok(m.seed.pending.every(r => r.s + H > T && r.s <= T && !("y" in r)), m.key);
    assert.ok(m.seed.labelled.filter(r => r.y === 1).every(r => r.events.length > 0), m.key);
  }
});

// ---------------------------------------------------------------- truncation (independent of the Python side)
function truncated(st, tau) {
  const s = structuredClone(st);
  for (const [id, r] of Object.entries(s.records)) {
    if (r.start > tau) delete s.records[id];
    else if (r.end !== null && r.end > tau) { r.end = null; r.endKnown = null; }
  }
  return s;
}
// pinned moments: on the hour, off the hour, right after an onset, inside an alert, 24 h after a start
const TAUS = (() => {
  const any = unitIntervals(knownByType(state, Date.parse("2026-10-17T00:00:00Z")).byType.any).kharkivska;
  const o = any.onsets.find(t => t > Date.parse("2026-10-01T00:00:00Z"));
  return [Date.parse("2026-10-05T12:00:00Z"), Date.parse("2026-10-09T07:23:00Z"), o + 60e3, o + 30 * 60e3, o + DAY,
          Date.parse("2026-10-17T23:00:00Z")];
})();

test("truncation per (type, H): feature vectors, mask state and p identical with data after tau removed", () => {
  for (const tau of TAUS) {
    const a = registryAt(state, tau, regions, reg, ctxAt(rec.historyStart));
    const b = registryAt(truncated(state, tau), tau, regions, reg, ctxAt(rec.historyStart));
    for (const key of Object.keys(a.items)) for (const u of regions.units) {
      const x = a.items[key].units[u], y = b.items[key].units[u];
      assert.deepEqual(x.x.map(v => (Number.isNaN(v) ? "NaN" : v)), y.x.map(v => (Number.isNaN(v) ? "NaN" : v)), `${key} ${u} ${tau}`);
      assert.equal(x.state, y.state, `${key} ${u} ${tau}`);
      assert.equal(x.active, y.active);
      assert.equal(x.p_model, y.p_model);
      assert.equal(x.p_baseline, y.p_baseline);
    }
  }
});

test("truncation negative control: a feature that reads the final end time is caught", () => {
  // witness: 1 h into the first kharkivska air-raid alert after 1 Oct that lasted > 2 h (its end is after tau)
  const w = Object.values(state.records).filter(r => r.unit === "kharkivska" && r.alert_type === "air_raid" && r.end !== null &&
                                               r.start > Date.parse("2026-10-01T00:00:00Z") && r.end - r.start > 2 * HOUR)
                                       .sort((a, b) => a.start - b.start)[0];
  const tau = w.start + HOUR;
  const leaky = st => {                                    // "minutes until this alert ends" (an end not known at tau)
    const r = st.records[w.id];
    return r && r.end !== null ? (r.end - tau) / 60e3 : null;
  };
  assert.ok(leaky(state) > 0);
  assert.equal(leaky(truncated(state, tau)), null);
  // the real inputs at the same tau are unchanged by the truncation (the leak is only in the leaky feature)
  const a = registryAt(state, tau, regions, reg, ctxAt(rec.historyStart)).items.any_h1.units.kharkivska;
  const b = registryAt(truncated(state, tau), tau, regions, reg, ctxAt(rec.historyStart)).items.any_h1.units.kharkivska;
  assert.deepEqual(a.x, b.x);
});

test("mutations: a later finished_at, an alert of exactly 24 h (cap), and Kyiv City vs Kyivska", () => {
  const tau = Date.parse("2026-10-10T12:00:00Z");
  const base = registryAt(state, tau, regions, reg, ctxAt(rec.historyStart)).items;
  // a future end moved further: nothing at tau changes
  const s1 = structuredClone(state);
  const r = Object.values(s1.records).find(r => r.start <= tau && r.end !== null && r.end > tau + HOUR);
  r.end += 5 * HOUR; r.endKnown = r.end;
  const m1 = registryAt(s1, tau, regions, reg, ctxAt(rec.historyStart)).items;
  for (const k of Object.keys(base)) assert.deepEqual(m1[k].units, base[k].units, k);
  // an open alert started exactly 24 h before tau no longer counts as running at tau (D-020 cap), 1 ms earlier it does
  const s2 = structuredClone(state);
  s2.records.cap = { id: "cap", unit: "zakarpatska", level: "raion", alert_type: "air_raid", start: tau - DAY, end: null,
                     updated: tau - DAY, firstSeen: tau - DAY, endKnown: null, endSource: null, absent: [], levels: [[tau - DAY, "yellow"]] };
  assert.notEqual(registryAt(s2, tau, regions, reg, ctxAt(rec.historyStart)).items.any_h1.units.zakarpatska.state, "alert_running");
  assert.equal(registryAt(s2, tau - 1, regions, reg, ctxAt(rec.historyStart)).items.any_h1.units.zakarpatska.state, "alert_running");
  // an alert added in Kyiv City only: Kyivska's state, features and baseline do not change
  const s3 = structuredClone(state);
  s3.records.kc = { id: "kc", unit: "kyiv_city", level: "oblast", alert_type: "air_raid", start: tau - 2 * HOUR, end: tau - HOUR,
                    updated: tau - HOUR, firstSeen: tau - 2 * HOUR, endKnown: tau - HOUR, endSource: "history", absent: [], levels: [[tau - 2 * HOUR, "yellow"]] };
  const m3 = registryAt(s3, tau, regions, reg, ctxAt(rec.historyStart)).items.any_h1.units;
  assert.notDeepEqual(m3.kyiv_city.x, base.any_h1.units.kyiv_city.x);
  const k = base.any_h1.units.kyivska, k3 = m3.kyivska;
  assert.equal(k3.p_baseline, k.p_baseline);
  assert.equal(k3.x[0], k.x[0]); assert.equal(k3.x[1], k.x[1]);
});

test("D-045: an artillery alert changes nothing on the M12 path", () => {
  const tau = Date.parse("2026-10-10T12:00:00Z");
  const s = structuredClone(state);
  s.records.art = { id: "art", unit: "dnipropetrovska", level: "hromada", alert_type: "artillery_shelling", start: tau - 30 * 60e3,
                    end: null, updated: tau - 30 * 60e3, firstSeen: tau - 30 * 60e3, endKnown: null, endSource: null, absent: [],
                    levels: [[tau - 30 * 60e3, "red"]] };
  const a = registryAt(state, tau, regions, reg, ctxAt(rec.historyStart)).items, b = registryAt(s, tau, regions, reg, ctxAt(rec.historyStart)).items;
  for (const k of Object.keys(a)) assert.deepEqual(b[k].units, a[k].units, k);
});

// ---------------------------------------------------------------- pieces
test("gap mask = src/grid.py gap_mask_for (label window touches the hole, or 24 h after it)", () => {
  const g = [[10 * HOUR, 12 * HOUR]];
  assert.equal(gapMasked(9 * HOUR, HOUR, g), true);          // (9, 10] touches [10, 12): s + H >= g0
  assert.equal(gapMasked(8 * HOUR, HOUR, g), false);
  assert.equal(gapMasked(35 * HOUR, HOUR, g), true);         // 12 + 24 = 36 h
  assert.equal(gapMasked(36 * HOUR, HOUR, g), false);
  assert.equal(gapMasked(4 * HOUR, 6 * HOUR, g), true);      // H = 6: (4, 10]
});

test("recent rate: rows s <= tau - H only (a label not yet known at tau never counts)", () => {
  const v = { ms: [], me: [], onsets: [100 * HOUR + 30 * 60e3] };
  const r1 = recentRate(v, 100 * HOUR + HOUR, HOUR, 0.1, 10, 14 * DAY, 0, []);        // s = 100 h is the last row: (100, 101]
  const r0 = recentRate(v, 100 * HOUR + HOUR - 1, HOUR, 0.1, 10, 14 * DAY, 0, []);    // 1 ms earlier: s = 99 h is the last
  assert.equal(r1.k, 1); assert.equal(r0.k, 0);
  const r6 = recentRate(v, 100 * HOUR + 6 * HOUR, 6 * HOUR, 0.1, 10, 14 * DAY, 0, []);  // H = 6: rows up to s = 100 h
  assert.ok(r6.k >= 1);
});

test("calibration: none returns p; Platt matches src/model.py", () => {
  assert.equal(calibrate(0.3, { decision: "none" }), 0.3);
  const c = { decision: "platt", clip: 1e-6, slope: 0.9, intercept: 0.2 };
  close(calibrate(0.3, c), 1 / (1 + Math.exp(-(0.9 * Math.log(0.3 / 0.7) + 0.2))), 1e-15, "platt");
});

test("blend weight: window [max(tau - 28 d, cutoff), tau - H], distinct onsets, n0 = 50", () => {
  const cutoff = 1000 * HOUR;
  const rows = [{ unit: "a", s: cutoff - HOUR, y: 1, p_model: 0.9, p_baseline: 0.2, events: ["a|1"] },            // before cut-off
                { unit: "a", s: cutoff, y: 1, p_model: 0.8, p_baseline: 0.3, events: ["a|2", "a|3"] },
                { unit: "b", s: cutoff + HOUR, y: 0, p_model: 0.1, p_baseline: 0.4, events: [] },
                { unit: "b", s: cutoff + 5 * HOUR, y: 1, p_model: 0.7, p_baseline: 0.5, events: ["b|9"] }];        // s > tau - H
  const w = weightAt(rows, cutoff + 5 * HOUR, HOUR, cutoff);
  const num = (0.3 - 1) * (0.3 - 0.8) + (0.4 - 0) * (0.4 - 0.1), den = 0.5 ** 2 + 0.3 ** 2;
  assert.equal(w.rows_used, 2); assert.equal(w.n, 2);
  close(w.w, (2 / 52) * Math.min(1, num / den), 1e-15, "w");
  assert.equal(weightAt(rows, cutoff - 1, HOUR, cutoff).w, 0);
});

test("labelRow: settle, coverage over [s - 24 h, s + H], onset at s not counted, at s + H counted, forbidden week", () => {
  const s0 = Date.parse("2026-10-12T00:00:00Z");
  const st = stateFrom([{ id: "1", unit: "lvivska", alert_type: "air_raid", level: "yellow", start: s0 + HOUR, end: s0 + 2 * HOUR },
                        { id: "2", unit: "volynska", alert_type: "air_raid", level: "yellow", start: s0, end: s0 + HOUR }],
                       rec.historyStart);
  const H = HOUR;
  assert.equal(labelRow(st, { unit: "lvivska", s: s0 }, "any", H, s0 + H + SETTLE - 1), null);
  const l = labelRow(st, { unit: "lvivska", s: s0 }, "any", H, s0 + H + SETTLE);
  assert.equal(l.y, 1); assert.deepEqual(l.events, [`lvivska|${s0 + HOUR}`]);            // onset exactly at s + H
  assert.equal(labelRow(st, { unit: "volynska", s: s0 }, "any", H, s0 + 10 * H), null);   // under alert at s (reconciled)
  assert.equal(labelRow(st, { unit: "lvivska", s: s0 + HOUR }, "any", H, s0 + 10 * H), null); // onset exactly at s: under alert
  const st2 = structuredClone(st);
  st2.coverage.lvivska = [[rec.historyStart, s0 - 2 * HOUR, rec.historyStart], [s0 - HOUR, 8.64e15, s0]];   // hole in [s - 24 h, s]
  assert.equal(labelRow(st2, { unit: "lvivska", s: s0 }, "any", H, s0 + 10 * H), null);
  assert.equal(labelRow(st, { unit: "lvivska", s: s0 }, "any", H, s0 + 10 * H, [s0 + 30 * 60e3, s0 + 7 * DAY]), null);
});

// ---------------------------------------------------------------- runner integration
import { runUpdate, snapshotKeyV2 } from "../lib/runner.mjs";
import { scoreSeries } from "../lib/check.mjs";
import { buildHistory } from "../lib/models.mjs";
const m8model = JSON.parse(readFileSync(new URL("../model/model_live.json", import.meta.url)));
function memStore() {
  const m = new Map();
  return { m, async get(k) { return m.has(k) ? JSON.parse(m.get(k)) : null; },
           async setJSON(k, v) { m.set(k, JSON.stringify(v)); }, async delete(k) { m.delete(k); },
           async list({ prefix = "" } = {}) { return { blobs: [...m.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })), directories: [] }; } };
}
const fetchNone = async () => ({ ok: true, status: 200, json: async () => ({ alerts: [] }) });
// a small live-like state: the parity state's records up to T, coverage confirmed at T
function liveState(T) {
  const s = truncated(state, T);
  for (const r of Object.values(s.records)) { if (r.end !== null) r.endKnown = Math.max(r.end, r.firstSeen); }
  for (const u of regions.units) s.levelCoverage[u] = s.coverage[u] = [[rec.historyStart, T, T]];
  s.polls = [[T - HOUR, T]];
  return s;
}

test("runner, INACTIVE: /latest is byte-identical to a run without M12; snapv2 holds predictions only; check_v2 inactive", async () => {
  const T = Date.parse("2026-10-17T10:02:00Z");
  const a = memStore(), b = memStore();
  await a.setJSON("state", liveState(T)); await b.setJSON("state", liveState(T));
  await runUpdate({ fetchFn: fetchNone, store: a, token: "t", now: T, model: m8model, regions });
  const st = await runUpdate({ fetchFn: fetchNone, store: b, token: "t", now: T, model: m8model, regions, m12: reg });
  assert.equal(st.m12.error, null);
  assert.equal(a.m.get("latest"), b.m.get("latest"));
  const snap = await b.get(snapshotKeyV2(T));
  assert.equal(snap.active, false);
  for (const it of Object.values(snap.items)) for (const x of Object.values(it.units)) { assert.equal(x[4], null); assert.equal(x[5], null); }
  assert.ok(Object.values(snap.items.any_h6.units).some(x => x[0] === "forecast" && x[1] > 0 && x[2] >= 0));
  assert.deepEqual((await b.get("check_v2")).status, "inactive");
  // first write in the hour wins
  await runUpdate({ fetchFn: fetchNone, store: b, token: "t", now: T + 20 * 60e3, model: m8model, regions, m12: reg });
  assert.equal((await b.get(snapshotKeyV2(T))).tau, T);
});

test("runner, ACTIVE: /latest carries the blended M12 forecast; the M8 output is still there", async () => {
  const T = Date.parse("2026-10-17T10:02:00Z");
  const act = loadRegistry({ registry, models, seed, activation: ACT });
  const s = memStore();
  await s.setJSON("state", liveState(T));
  const st = await runUpdate({ fetchFn: fetchNone, store: s, token: "t", now: T, model: m8model, regions, m12: act });
  assert.equal(st.m12.error, null);
  const lat = await s.get("latest");
  assert.ok(lat.units.kyiv_city);                                   // M8 section unchanged in shape
  const it = lat.m12.items.any_h3;
  const f = Object.values(it.units).find(x => x.state === "forecast");
  assert.ok(f.w >= 0 && f.w <= 1 && Math.abs(f.p - (f.w * f.p_model + (1 - f.w) * f.p_baseline)) < 1e-15);
  assert.throws(() => loadRegistry({ registry, models, seed, activation: { active: true } }), /activated_at/);
  assert.throws(() => loadRegistry({ registry, models, seed, activation: { ...ACT, activated_at: registry.earliest_activation - 1 } }), /activated_at/);
  assert.throws(() => loadRegistry({ registry, models, seed, activation: { ...ACT, activated_at: Math.floor(registry.earliest_activation / 1000) } }), /activated_at/);
  assert.throws(() => loadRegistry({ registry, models, seed, activation: { active: true, activated_at: registry.earliest_activation } }), /test_metrics_sha256/);
  assert.equal(new Date(registry.earliest_activation).toISOString(), "2026-10-26T03:00:00.000Z");
});

test("scoreSeries: inactive computes nothing; active scores (tau, tau + H] after tau + H + SETTLE, per version", () => {
  const tau = Date.parse("2026-10-10T12:00:00Z");
  const T = tau + 30 * HOUR;
  const s = liveState(T);
  const out = registryAt(s, tau, regions, reg, ctxAt(rec.historyStart));
  for (const it of Object.values(out.items)) for (const x of Object.values(it.units)) { x.w = 0.5; x.p = x.p_model === null ? null : 0.5 * x.p_model + 0.5 * x.p_baseline; }
  const sn = { key: snapshotKeyV2(tau), value: { ...compactSnap(out, tau), active: true } };
  const m = reg.items.find(x => x.key === "any_h24");
  assert.deepEqual(scoreSeries(s, [sn], T, regions, { key: m.key, version: m.version, type: "any", H: m.Hms, active: false }),
                   { key: m.key, version: m.version, status: "inactive" });
  const early = scoreSeries(s, [sn], tau + m.Hms + SETTLE - 1, regions, { key: m.key, version: m.version, type: "any", H: m.Hms, active: true, activatedAt: tau });
  assert.equal(early.overall.rows, 0); assert.ok(early.excluded.unsettled > 0);
  const ok = scoreSeries(s, [sn], T, regions, { key: m.key, version: m.version, type: "any", H: m.Hms, active: true, activatedAt: tau });
  assert.ok(ok.overall.rows > 0);
  const before = scoreSeries(s, [sn], T, regions, { key: m.key, version: m.version, type: "any", H: m.Hms, active: true, activatedAt: tau + 1 });
  assert.equal(before.overall.rows, 0); assert.equal(before.excluded.before_activation, 1);
  const other = scoreSeries(s, [sn], T, regions, { key: m.key, version: "other", type: "any", H: m.Hms, active: true, activatedAt: tau });
  assert.equal(other.overall.rows, 0); assert.equal(other.excluded.other_version, 1);
  // exact: rows = units forecast at issue and not under an alert at tau (reconciled); label = an onset in (tau, tau + H]
  const v = unitIntervals(knownByType(s, T).byType.any), e = { ms: [], me: [], onsets: [] };
  const kept = regions.units.filter(u => out.items.any_h24.units[u].state === "forecast" &&
    !((v[u] || e).ms.some((a, i) => a <= tau && tau < (v[u] || e).me[i])));
  const pos = kept.filter(u => (v[u] || e).onsets.some(o => o > tau && o <= tau + m.Hms)).length;
  assert.equal(ok.overall.rows, kept.length);
  assert.equal(ok.overall.positives, pos);
});
function compactSnap(out, tau) {
  const items = {};
  for (const [k, it] of Object.entries(out.items)) items[k] = { version: it.version, type: it.type, H: it.H,
    units: Object.fromEntries(Object.entries(it.units).map(([u, x]) => [u, [x.state, x.p_model, x.p_baseline, 0, x.w, x.p]])) };
  return { schema: 2, tau, written_at: tau, items };
}

test("buildHistory: seed + pending + live rows (issue time); live rows at or before T_seed ignored; other versions skipped", () => {
  const act = loadRegistry({ registry, models, seed, activation: ACT });
  const m = act.items.find(x => x.key === "any_h1");
  const T = m.seed.T_seed;
  const now = T + 2 * DAY;
  const s = liveState(now);
  const mk = (tau, version) => ({ key: snapshotKeyV2(tau), value: { schema: 2, tau, written_at: tau, active: true,
    items: { any_h1: { version, units: { lvivska: ["forecast", 0.2, 0.1, 0, 0.5, 0.15] } } } } });
  const snaps = [mk(T - HOUR, m.version), mk(T + 5 * 60e3 + HOUR, m.version), mk(T + 3 * HOUR, "older-version")];
  const { history, ignored } = buildHistory(s, act, snaps, now);
  assert.equal(ignored.any_h1, 1);
  const live = history.any_h1.filter(r => r.s === T + 5 * 60e3 + HOUR);
  assert.equal(live.length, 1);                                    // row time = the actual issue time (xx:05)
  assert.ok(history.any_h1.some(r => m.seed.pending.some(p => p.s === r.s && p.unit === r.unit)));   // pending labelled
  assert.ok(!history.any_h1.some(r => r.s === T + 3 * HOUR));
  assert.throws(() => buildHistory(s, reg, snaps, now), /inactive/);
});


// ---------------------------------------------------------------- review fixes
test("a unit without a train rate (p_unit) is an explicit data gap, never a NaN baseline", () => {
  const m = reg.items.find(x => x.key === "yellow_h1");
  const missing = regions.units.filter(u => !Number.isFinite(m.p_unit[u]));
  assert.ok(missing.length >= 1);
  const tau = Date.parse("2026-10-15T12:00:00Z");
  const s = structuredClone(state);
  for (const u of missing) s.records[`y-${u}`] = { id: `y-${u}`, unit: u, level: "raion", alert_type: "air_raid", start: tau - 5 * HOUR,
    end: tau - 4 * HOUR, updated: tau - 4 * HOUR, firstSeen: tau - 5 * HOUR, endKnown: tau - 4 * HOUR, endSource: "history", absent: [],
    levels: [[tau - 5 * HOUR, "yellow"]] };
  const out = registryAt(s, tau, regions, reg, ctxAt(rec.historyStart));
  for (const u of missing) {
    const x = out.items.yellow_h1.units[u];
    assert.equal(x.state, "data_gap"); assert.equal(x.p_baseline, null); assert.ok(x.caution.includes("no_train_rate"));
  }
});

test("one bad (type, H) never blocks the others", () => {
  const bad = { ...registry, models: registry.models.map(m => (m.key === "red_h3" ? { ...m, calibration: { decision: "bogus" } } : m)) };
  const r = loadRegistry({ registry: bad, models, seed, activation: { active: false } });
  const out = registryAt(state, Date.parse("2026-10-15T12:00:00Z"), regions, r, ctxAt(rec.historyStart));
  assert.match(out.items.red_h3.error, /unknown calibration/);
  assert.ok(Object.values(out.items.red_h3.units).every(x => x.state === "data_gap"));
  assert.ok(Object.values(out.items.any_h6.units).some(x => x.state === "forecast"));
});

test("a storage error on the M12 path never blocks the M8 snapshot, status and check", async () => {
  const T = Date.parse("2026-10-17T10:02:00Z");
  const s = memStore();
  await s.setJSON("state", liveState(T));
  const orig = s.setJSON.bind(s);
  s.setJSON = async (k, v) => { if (k.startsWith("snapv2/") || k === "check_v2") throw new Error("disk full"); return orig(k, v); };
  const st = await runUpdate({ fetchFn: fetchNone, store: s, token: "t", now: T, model: m8model, regions, m12: reg });
  assert.equal(st.ok, true);
  assert.match(st.m12.error, /disk full/);
  assert.ok(await s.get("snap/2026-10-17T10"));
  assert.ok(await s.get("check"));
  assert.match((await s.get("status")).m12.error, /disk full/);
});

test("typed labels: an alert of still-unknown level in the window -> no label (not 0); needs level coverage", () => {
  const s0 = Date.parse("2026-10-12T00:00:00Z");
  const st = stateFrom([{ id: "1", unit: "lvivska", alert_type: "air_raid", level: "yellow", start: s0 - 3 * HOUR, end: s0 - 2 * HOUR }],
                       rec.historyStart);
  st.records.u = { id: "u", unit: "lvivska", level: "raion", alert_type: "air_raid", start: s0 + 30 * 60e3, end: s0 + HOUR,
                   updated: s0, firstSeen: s0 + 30 * 60e3, endKnown: s0 + HOUR, endSource: "history", absent: [], levels: [] };
  assert.equal(labelRow(st, { unit: "lvivska", s: s0 }, "red", HOUR, s0 + 10 * HOUR), null);
  assert.equal(labelRow(st, { unit: "lvivska", s: s0 }, "any", HOUR, s0 + 10 * HOUR).y, 1);
  const st2 = structuredClone(st); delete st2.records.u; st2.levelCoverage.lvivska = [];
  assert.equal(labelRow(st2, { unit: "lvivska", s: s0 }, "yellow", HOUR, s0 + 10 * HOUR), null);
});

test("negative control inside registryAt, per (type, H): future onsets pulled before tau are caught by the truncation comparison", () => {
  // the leak: alerts that start in (tau, tau + H] are moved to tau - 1 min (a feature that reads future events)
  const leaky = (st, tau, H) => { const s = structuredClone(st);
    for (const r of Object.values(s.records)) if (r.start > tau && r.start <= tau + H) { r.start = tau - 60e3; r.firstSeen = r.start; r.levels = [[r.start, r.levels[0][1]]]; }
    return s; };
  // tau: an hour start with both a yellow and a red air-raid start in the next hour, before T_seed
  const starts = Object.values(state.records).filter(r => r.start > Date.parse("2026-10-01T00:00:00Z") && r.start < Date.parse("2026-10-17T00:00:00Z"));
  const tau = starts.map(r => Math.floor(r.start / HOUR) * HOUR).sort((a, b) => a - b).find(t =>
    starts.some(r => r.levels[0][1] === "red" && r.start > t && r.start <= t + HOUR) &&
    starts.some(r => r.levels[0][1] === "yellow" && r.start > t && r.start <= t + HOUR));
  assert.ok(tau);
  for (const m of reg.items) {
    const a = registryAt(leaky(state, tau, m.Hms), tau, regions, reg, ctxAt(rec.historyStart)).items[m.key];
    const b = registryAt(leaky(truncated(state, tau), tau, m.Hms), tau, regions, reg, ctxAt(rec.historyStart)).items[m.key];
    const differ = regions.units.some(u => JSON.stringify(a.units[u].x) !== JSON.stringify(b.units[u].x) || a.units[u].state !== b.units[u].state);
    assert.ok(differ, `${m.key}: the leak was not caught`);
    // and the real (non-leaky) inputs are identical
    const c = registryAt(state, tau, regions, reg, ctxAt(rec.historyStart)).items[m.key];
    const d = registryAt(truncated(state, tau), tau, regions, reg, ctxAt(rec.historyStart)).items[m.key];
    assert.ok(regions.units.every(u => JSON.stringify(c.units[u].x) === JSON.stringify(d.units[u].x)), m.key);
  }
});
