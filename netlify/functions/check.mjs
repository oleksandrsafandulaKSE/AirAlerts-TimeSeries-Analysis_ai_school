// GET: the live forecast check (plans/M11.md §A2), recomputed at most once per UTC hour by update-forecast.
// Exploratory API data, not part of the study.
import { getStore } from "@netlify/blobs";
import { STORE_NAME } from "../live/lib/runner.mjs";

export default async () => {
  const check = await getStore({ name: STORE_NAME, consistency: "strong" }).get("check", { type: "json" });
  return new Response(JSON.stringify(check), {
    status: check ? 200 : 503,
    headers: { "content-type": "application/json", "cache-control": "public, max-age=300" } });
};

export const config = { path: "/api/check" };
