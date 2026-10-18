// GET: the live forecast checks (plans/M11.md §A2, plans/M13.md §2): {m8: the current model's 1 h series,
// v2: the M12 per-series check (status "inactive" until the switch)}. Exploratory API data, not part of the study.
import { getStore } from "@netlify/blobs";
import { STORE_NAME } from "../live/lib/runner.mjs";

export default async () => {
  const store = getStore({ name: STORE_NAME, consistency: "strong" });
  const [m8, v2] = await Promise.all([store.get("check", { type: "json" }), store.get("check_v2", { type: "json" })]);
  return new Response(JSON.stringify({ m8, v2 }), {
    status: m8 ? 200 : 503,
    headers: { "content-type": "application/json", "cache-control": "public, max-age=300" } });
};

export const config = { path: "/api/check" };
