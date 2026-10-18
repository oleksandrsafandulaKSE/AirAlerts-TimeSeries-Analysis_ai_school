// Local preview of the live page (not deployed): serves site/ and /api/forecast, /api/history, /api/check.
//   node --env-file=.env netlify/live/dev_server.mjs   -> live: the SAME runUpdate every minute against alerts.in.ua
//                                                         (in-memory store; token from the environment, never printed)
//   node netlify/live/dev_server.mjs                    -> offline (no token): the saved dump (seed_state.json) is
//      replayed through the same runUpdate every 5 minutes over its last SIM_DAYS days (default 3), with a fake API
//      that only returns what was known at each moment; the page then shows that frozen moment (marked out of date).
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { runUpdate, readPayload, readHistory } from "./lib/runner.mjs";
import { emptyState, applyHistory } from "./lib/live.mjs";

const root = new URL("../../", import.meta.url);
const model = JSON.parse(readFileSync(new URL("netlify/live/model/model_live.json", root)));
const regions = JSON.parse(readFileSync(new URL("netlify/live/data/regions.json", root)));
const seed = JSON.parse(readFileSync(new URL("netlify/live/data/seed_state.json", root)));
const monthly = JSON.parse(readFileSync(new URL("netlify/live/data/typed_monthly.json", root)));
const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR;
const m = new Map();
// values are kept as objects (the replay makes ~900 runs); every response is serialised, so nothing leaks by reference
const store = { async get(k) { return m.has(k) ? structuredClone(m.get(k)) : null; },
                async setJSON(k, v) { m.set(k, structuredClone(v)); }, async delete(k) { m.delete(k); },
                async list({ prefix = "" } = {}) { return { blobs: [...m.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })), directories: [] }; } };
const TOKEN = process.env.ALERTS_IN_UA_TOKEN;
let clock = () => Date.now();

async function tick() {
  const st = await runUpdate({ fetchFn: fetch, store, token: TOKEN, now: Date.now(), model, regions, seed });
  const f = (await readPayload(store)).forecast;
  const c = {}; if (f) for (const u of Object.values(f.units)) c[u.state] = (c[u.state] || 0) + 1;
  console.log(new Date().toISOString(), `ok=${st.ok} active=${st.active_alerts} history=${st.history_unit}:${st.history_ok}`,
              st.error ? `error=${st.error}` : "", JSON.stringify(c));
}

// Offline replay: a fake alerts.in.ua that answers with the dump's records as they stood at time t
async function replayDump(days) {
  const NAME = Object.fromEntries(Object.entries(regions.api_oblast_name).map(([n, u]) => [u, n]));
  const iso = t => new Date(t).toISOString();
  const recs = Object.values(seed.records);
  const end = Math.max(...Object.values(seed.coverage).flat().map(([, b]) => b));
  const api = (r, t) => { const closed = r.end !== null && r.end <= t;
    return { id: r.id, location_oblast: NAME[r.unit], location_type: r.level, alert_type: r.alert_type, started_at: iso(r.start),
             finished_at: closed ? iso(r.end) : null, updated_at: iso(closed ? r.end : r.start) }; };
  const active = t => recs.filter(r => r.start <= t && (r.end === null || r.end > t)).map(r => api(r, t));
  const history = (u, t) => recs.filter(r => r.unit === u && r.end !== null && r.end <= t && r.end > t - 30 * DAY).map(r => api(r, t));
  const S = Math.floor((end - days * DAY) / HOUR) * HOUR;
  const s0 = emptyState(seed.historyStart);
  for (const u of regions.units) applyHistory(s0, u, history(u, S), S, regions);
  await store.setJSON("state", s0);
  const uidUnit = Object.fromEntries(Object.entries(regions.api_uid).map(([u, id]) => [String(id), u]));
  let t = S, n = 0;
  const fetchFn = async (url) => {
    const mm = url.match(/\/regions\/(\d+)\//);
    return { ok: true, status: 200, json: async () => ({ alerts: mm ? history(uidUnit[mm[1]], t) : active(t) }) };
  };
  const t0 = Date.now();
  for (; t <= end; t += 5 * MIN, n++) {
    const st = await runUpdate({ fetchFn, store, token: "offline-replay", now: t, model, regions });
    if (!st.ok) throw new Error(`replay run at ${iso(t)} failed: ${st.error}`);
    if (n % 144 === 0) console.log(`replay ${iso(t)} (${n} runs, ${((Date.now() - t0) / 1e3).toFixed(0)} s)`);
  }
  const check = await store.get("check");
  console.log(`offline replay done: ${n} runs from ${iso(S)} to ${iso(t - 5 * MIN)}; check: ${check.ok ? `${check.overall.rows} rows, ${check.days_scored} days` : check.error}`);
  return t - 5 * MIN;
}

const json = (res, v, code = 200) => { res.writeHead(v === null ? 503 : code, { "content-type": "application/json", "cache-control": "no-store" }); res.end(JSON.stringify(v)); };
createServer(async (req, res) => {
  if (req.url.startsWith("/api/forecast")) return json(res, await readPayload(store, monthly));
  if (req.url.startsWith("/api/history")) return json(res, await readHistory(store, clock(), regions));
  if (req.url.startsWith("/api/check")) return json(res, await store.get("check"));
  if (req.url === "/" || req.url.startsWith("/index.html")) {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    return res.end(readFileSync(new URL("site/index.html", root)));
  }
  res.writeHead(404); res.end("not found");
}).on("error", e => { console.error(`dev server: ${e.message}`); process.exit(1); })
  .listen(8888, () => console.log("dev server on http://localhost:8888"));
await new Promise(r => setTimeout(r, 200));                           // a taken port fails here, before the replay

if (TOKEN) {
  await tick();
  setInterval(() => tick().catch(e => console.log("tick failed:", e.message)), 60e3);
} else {
  console.log("no ALERTS_IN_UA_TOKEN: offline replay of the saved dump (no network)");
  const end = await replayDump(Number(process.env.SIM_DAYS || 3));
  clock = () => end;
}
