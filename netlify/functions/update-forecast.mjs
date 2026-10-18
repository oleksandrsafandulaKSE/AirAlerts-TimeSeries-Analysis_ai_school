// Scheduled every 5 minutes (plans/M8.md §2; human decision 2026-10-18: every 5 min to stay inside the free plan's credits). Token only from the Netlify environment; never logged.
import { getStore } from "@netlify/blobs";
import { runUpdate, STORE_NAME } from "../live/lib/runner.mjs";
import model from "../live/model/model_live.json" with { type: "json" };
import regions from "../live/data/regions.json" with { type: "json" };
import seed from "../live/data/seed_state.json" with { type: "json" };
import { m12 } from "../live/lib/m12_bundle.mjs";

export default async () => {
  const status = await runUpdate({ fetchFn: fetch, store: getStore({ name: STORE_NAME, consistency: "strong" }), token: process.env.ALERTS_IN_UA_TOKEN,
                                   now: Date.now(), model, regions, seed, m12 });
  console.log(`update: ok=${status.ok} active=${status.active_alerts} history=${status.history_unit}:${status.history_ok} m12=${status.m12 ? (status.m12.error ? 'error' : (status.m12.active ? 'active' : 'inactive')) : 'off'}`);
};

export const config = { schedule: "*/5 * * * *" };
