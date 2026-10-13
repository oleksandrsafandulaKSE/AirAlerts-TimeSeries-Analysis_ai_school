import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { runUpdate, readPayload, snapshotKey, API } from "../lib/runner.mjs";
import { stale } from "../lib/live.mjs";

const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const model = JSON.parse(readFileSync(new URL("../model/model_live.json", import.meta.url)));
const seed = JSON.parse(readFileSync(new URL("../data/seed_state.json", import.meta.url)));
const TOKEN = "test-token-DO-NOT-LEAK-3141592653";
const NOW = Date.parse("2026-10-12T16:46:00Z");          // one minute after the dump's coverage end

function memStore() {
  const m = new Map();
  return { m, async get(k) { return m.has(k) ? JSON.parse(m.get(k)) : null; },
           async setJSON(k, v) { m.set(k, JSON.stringify(v)); }, async delete(k) { m.delete(k); },
           async list({ prefix = "" } = {}) { return { blobs: [...m.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })), directories: [] }; } };
}
function mockFetch(routes) {
  const calls = [];
  const fn = async (url, opts) => {
    calls.push({ url, auth: opts.headers.Authorization });
    const r = routes(url);
    return { ok: r.status === 200, status: r.status, json: async () => r.body };
  };
  return { fn, calls };
}
const ok = (alerts) => ({ status: 200, body: { alerts } });

test("one run: 1 ACTIVE + 1 history call, bearer token sent, forecast for all 24 units, state persisted", async () => {
  const store = memStore();
  const f = mockFetch(url => ok([]));
  const st = await runUpdate({ fetchFn: f.fn, store, token: TOKEN, now: NOW, model, regions, seed });
  assert.equal(st.ok, true);
  assert.equal(f.calls.length, 2);
  assert.equal(f.calls[0].url, `${API}/alerts/active.json`);
  assert.match(f.calls[1].url, /\/regions\/\d+\/alerts\/month_ago\.json$/);
  assert.ok(f.calls.every(c => c.auth === `Bearer ${TOKEN}`));
  const p = await readPayload(store);
  assert.equal(Object.keys(p.forecast.units).length, 24);
  assert.equal(p.forecast.tau, NOW);
  assert.equal(stale(p, NOW + 60e3), false);
  for (const u of Object.values(p.forecast.units)) {
    assert.ok(["forecast", "alert_running", "data_gap"].includes(u.state));
    if (u.state === "forecast") assert.ok(u.p > 0 && u.p < 1);
  }
  assert.ok(store.m.has(snapshotKey(NOW)));
  // rotation advances: the second run asks for a different unit
  const f2 = mockFetch(url => ok([]));
  await runUpdate({ fetchFn: f2.fn, store, token: TOKEN, now: NOW + 60e3, model, regions, seed });
  assert.notEqual(f2.calls[1].url, f.calls[1].url);
});

test("the token never appears in the stored payload, status or errors", async () => {
  const store = memStore();
  const f = mockFetch(url => url.includes("month_ago") ? { status: 429, body: null } : ok([]));
  await runUpdate({ fetchFn: f.fn, store, token: TOKEN, now: NOW, model, regions, seed });
  for (const v of store.m.values()) assert.ok(!v.includes(TOKEN));
  const bad = memStore();
  const st = await runUpdate({ fetchFn: mockFetch(() => ({ status: 401, body: null })).fn, store: bad, token: TOKEN,
                               now: NOW, model, regions, seed });
  assert.equal(st.ok, false);
  assert.ok(!JSON.stringify(st).includes(TOKEN));
});

test("failed ACTIVE poll: status says so, no new forecast, page goes stale", async () => {
  const store = memStore();
  await runUpdate({ fetchFn: mockFetch(() => ok([])).fn, store, token: TOKEN, now: NOW, model, regions, seed });
  const st = await runUpdate({ fetchFn: mockFetch(() => ({ status: 503, body: null })).fn, store, token: TOKEN,
                               now: NOW + 60e3, model, regions, seed });
  assert.equal(st.ok, false);
  assert.match(st.error, /active: HTTP 503/);
  const p = await readPayload(store);
  assert.equal(p.forecast.tau, NOW);                      // previous forecast kept, not refreshed
  assert.equal(stale(p, NOW + 2 * 60e3), true);           // failed status greys the map
});

test("failed history call: forecast still made, history_ok false; malformed body raises into the status", async () => {
  const store = memStore();
  const st = await runUpdate({ fetchFn: mockFetch(url => url.includes("month_ago") ? { status: 500, body: null } : ok([])).fn,
                               store, token: TOKEN, now: NOW, model, regions, seed });
  assert.equal(st.ok, true);
  assert.equal(st.history_ok, false);
  const st2 = await runUpdate({ fetchFn: mockFetch(() => ({ status: 200, body: { nope: 1 } })).fn, store: memStore(),
                                token: TOKEN, now: NOW, model, regions, seed });
  assert.equal(st2.ok, false);
  assert.match(st2.error, /no 'alerts' array/);
});

test("guards: missing token raises AFTER writing a failed status; missing seed raises", async () => {
  const st0 = memStore();
  await assert.rejects(runUpdate({ fetchFn: mockFetch(() => ok([])).fn, store: st0, token: undefined, now: NOW,
                                   model, regions, seed }), /ALERTS_IN_UA_TOKEN/);
  const p0 = await readPayload(st0);
  assert.equal(p0.status.ok, false);
  assert.match(p0.status.error, /ALERTS_IN_UA_TOKEN is not set/);
  assert.equal(stale(p0, NOW), true);
  await assert.rejects(runUpdate({ fetchFn: mockFetch(() => ok([])).fn, store: memStore(), token: TOKEN, now: NOW,
                                   model, regions, seed: undefined }), /no valid seed/);
});

test("snapshots: one key per UTC hour; every snapshot 7 days old or older is deleted, also after a long pause", async () => {
  const store = memStore();
  const old = NOW - 7 * 24 * 3600e3;
  store.m.set(snapshotKey(old), "{}");
  store.m.set(snapshotKey(old - 5 * 3600e3), "{}");                       // missed by an exact-key delete
  store.m.set(snapshotKey(old + 3600e3), "{}");                           // younger than 7 days: kept
  await runUpdate({ fetchFn: mockFetch(() => ok([])).fn, store, token: TOKEN, now: NOW, model, regions, seed });
  assert.equal(store.m.has(snapshotKey(old)), false);
  assert.equal(store.m.has(snapshotKey(old - 5 * 3600e3)), false);
  assert.equal(store.m.has(snapshotKey(old + 3600e3)), true);
  assert.equal(snapshotKey(Date.parse("2026-10-12T16:59:59Z")), "snap/2026-10-12T16");
});

test("no token or env value is hard-coded in the function sources", () => {
  const dirs = [new URL("../../functions/", import.meta.url), new URL("../lib/", import.meta.url)];
  for (const d of dirs) for (const f of readdirSync(d).filter(x => x.endsWith(".mjs"))) {
    const src = readFileSync(new URL(f, d), "utf8");
    assert.ok(!/Bearer [A-Za-z0-9]{8,}/.test(src), f);
    assert.ok(!/console\.(log|error|warn)\([^)]*token/i.test(src), f);
  }
});

test("one malformed ACTIVE record: the run succeeds, only that unit is a data gap, the rejection is in the status", async () => {
  const store = memStore();
  const good = { id: "g1", location_oblast: "Одеська область", location_type: "raion", started_at: "2026-10-12T16:40:00.000Z",
                 finished_at: null, updated_at: "2026-10-12T16:40:00.000Z", alert_type: "air_raid" };
  const bad = { ...good, id: "b1", location_oblast: "м. Київ", alert_type: "teleport" };
  const f = mockFetch(url => url.includes("active") ? ok([good, bad, { ...good, id: "b2", location_oblast: "Київська область", started_at: "2026-10-12 16:40" }]) : ok([]));
  let st;
  for (let i = 0; i < 26; i++) st = await runUpdate({ fetchFn: f.fn, store, token: TOKEN, now: NOW + i * 60e3, model, regions, seed });
  assert.equal(st.ok, true);
  assert.deepEqual(st.rejected.map(r => r.unit).sort(), ["kyiv_city", "kyivska"]);
  const p = await readPayload(store);
  assert.equal(p.forecast.units.kyiv_city.state, "data_gap");
  assert.equal(p.forecast.units.kyivska.state, "data_gap");
  assert.ok(Object.values(p.forecast.units).some(u => u.state === "forecast"));
  const unknown = mockFetch(url => url.includes("active") ? ok([{ ...good, location_oblast: "Невідома область" }]) : ok([]));
  const st2 = await runUpdate({ fetchFn: unknown.fn, store, token: TOKEN, now: NOW + 27 * 60e3, model, regions, seed });
  assert.equal(st2.ok, false);                                       // an unattributable record is a schema change: loud
  assert.match(st2.error, /unknown oblast name/);
});

test("a unit whose history keeps failing is listed in the status; a success resets the streak", async () => {
  const store = memStore();
  let failLviv = true;
  const f = mockFetch(url => url.includes(`/regions/${regions.api_uid.lvivska}/`) && failLviv ? { status: 500, body: null } : ok([]));
  let st;
  for (let i = 0; i < 24 * 2 + 1; i++) st = await runUpdate({ fetchFn: f.fn, store, token: TOKEN, now: NOW + i * 60e3, model, regions, seed });
  assert.deepEqual(st.history_failing, [{ unit: "lvivska", consecutive: 2 }]);
  failLviv = false;
  for (let i = 49; i < 24 * 3 + 1; i++) st = await runUpdate({ fetchFn: f.fn, store, token: TOKEN, now: NOW + i * 60e3, model, regions, seed });
  assert.deepEqual(st.history_failing, []);
});

test("a hanging API call is aborted by the timeout and reported, not left pending", async () => {
  const store = memStore();
  const hang = async (url, opts) => new Promise((_, rej) => opts.signal.addEventListener("abort", () => rej(opts.signal.reason)));
  const st = await runUpdate({ fetchFn: hang, store, token: TOKEN, now: NOW, model, regions, seed, timeoutMs: 50 });
  assert.equal(st.ok, false);
  assert.match(st.error, /^active: /);
});

test("the scheduled function reads the state with strong consistency and is scheduled every minute", () => {
  const src = readFileSync(new URL("../../functions/update-forecast.mjs", import.meta.url), "utf8");
  assert.match(src, /consistency: "strong"/);
  assert.match(src, /schedule: "\* \* \* \* \*"/);
});
