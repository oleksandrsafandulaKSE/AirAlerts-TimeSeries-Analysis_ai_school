// The "what kind of alert" wording (plans/M13.md §1). Self-contained (no imports): scripts/build_site.py inlines this
// file into the page, so the tested words are the shipped words.
export function kindWords(x) {
  if (x && x.status === "error") return "alert kinds unavailable right now";
  if (!x || x.status !== "ok") return "not enough data on alert kinds";
  if (x.M === 0) return "no alerts here in 7 days";
  if (!Number.isInteger(x.M) || !Number.isInteger(x.N)) return "not enough data on alert kinds";
  if (x.N === 0) return "alert kinds not known yet";
  const s = x.share;
  if (!Number.isFinite(s)) return "not enough data on alert kinds";
  const head = s > 0.5 ? "likely red (missiles)" : s < 0.5 ? "likely yellow (drones)" : "red or yellow equally likely";
  return `${head} · red in ${x.R} of the last ${x.N} alerts${x.U ? ` (${x.U} of the last ${x.M} not yet classified)` : ""}`;
}
