// GET: last 7 days of hourly snapshots and last 14 days of per-oblast alert intervals and coverage (plans/M11.md §A3).
// Exploratory API data; derived intervals only (no raw API records, no token).
import { getStore } from "@netlify/blobs";
import { readHistory, STORE_NAME } from "../live/lib/runner.mjs";
import regions from "../live/data/regions.json" with { type: "json" };

export default async () => {
  const payload = await readHistory(getStore({ name: STORE_NAME, consistency: "strong" }), Date.now(), regions);
  return new Response(JSON.stringify(payload), {
    status: payload ? 200 : 503,
    headers: { "content-type": "application/json", "cache-control": "public, max-age=300" } });
};

export const config = { path: "/api/history" };
