// Local preview of the live page (not deployed): serves site/ and /api/forecast, running the SAME runUpdate every minute
// against the real alerts.in.ua API with an in-memory store. Token from the environment only, never printed.
//   node --env-file=.env netlify/live/dev_server.mjs   -> http://localhost:8888
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { runUpdate, readPayload } from "./lib/runner.mjs";

const root = new URL("../../", import.meta.url);
const model = JSON.parse(readFileSync(new URL("netlify/live/model/model_live.json", root)));
const regions = JSON.parse(readFileSync(new URL("netlify/live/data/regions.json", root)));
const seed = JSON.parse(readFileSync(new URL("netlify/live/data/seed_state.json", root)));
const monthly = JSON.parse(readFileSync(new URL("netlify/live/data/typed_monthly.json", root)));
const m = new Map();
const store = { async get(k) { return m.has(k) ? JSON.parse(m.get(k)) : null; },
                async setJSON(k, v) { m.set(k, JSON.stringify(v)); }, async delete(k) { m.delete(k); },
                async list({ prefix = "" } = {}) { return { blobs: [...m.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })), directories: [] }; } };

async function tick() {
  const st = await runUpdate({ fetchFn: fetch, store, token: process.env.ALERTS_IN_UA_TOKEN, now: Date.now(), model, regions, seed });
  const f = (await readPayload(store)).forecast;
  const c = {}; if (f) for (const u of Object.values(f.units)) c[u.state] = (c[u.state] || 0) + 1;
  console.log(new Date().toISOString(), `ok=${st.ok} active=${st.active_alerts} history=${st.history_unit}:${st.history_ok}`,
              st.error ? `error=${st.error}` : "", JSON.stringify(c));
}

createServer(async (req, res) => {
  if (req.url.startsWith("/api/forecast")) {
    res.writeHead(200, { "content-type": "application/json", "cache-control": "no-store" });
    return res.end(JSON.stringify(await readPayload(store, monthly)));
  }
  if (req.url === "/" || req.url.startsWith("/index.html")) {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    return res.end(readFileSync(new URL("site/index.html", root)));
  }
  res.writeHead(404); res.end("not found");
}).listen(8888, () => console.log("dev server on http://localhost:8888"));

await tick();
setInterval(() => tick().catch(e => console.log("tick failed:", e.message)), 60e3);
