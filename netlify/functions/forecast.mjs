// GET: the latest forecast and the status of the last run, in one payload (plans/M8.md §2).
import { getStore } from "@netlify/blobs";
import { readPayload, STORE_NAME } from "../live/lib/runner.mjs";

export default async () => {
  const payload = await readPayload(getStore({ name: STORE_NAME, consistency: "strong" }));
  return new Response(JSON.stringify(payload), {
    headers: { "content-type": "application/json", "cache-control": "public, max-age=30" } });
};

export const config = { path: "/api/forecast" };
