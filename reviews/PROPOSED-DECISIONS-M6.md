# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow counts, and vice versa).
  H = 1 headline, H = 3 also reported. `threats[]` is not used.
- Amends CLAUDE.md Target (adds the typed targets).

## D-034 — Training on API data allowed, API only (me, 2026-10-17)
- Amends CLAUDE.md "No training or tuning on API data". New-regime models (any / yellow / red) train only on API
  data, never mixed with official data. "Any" uses the official recipe retrained from scratch; the frozen official
  model stays as a comparison line.

## D-035 — Train now, monthly, fully automatic (me, 2026-10-17)
- Amends D-016 (≥ 3 months before yellow-regime training) and CLAUDE.md "a yellow-regime model is trained only with
  the human's explicit approval". The first training uses the history available now (results EXPLORATORY). Monthly
  retrains go live automatically if `pytest` (incl. leakage) passes; otherwise last month's model is kept.
- Safety net: the blend p = w·model + (1 − w)·baseline, with w from the last 28 days of known labels (shown on the
  site).

## D-036 — Live site shows typed forecasts on hover (me, 2026-10-17)
- Yellow/red only on oblast hover, labelled "in training", with collection status and the monthly chart.

## D-037 — Collector shares the M8 token (me, 2026-10-17)
- Same `ALERTS_IN_UA_TOKEN`, collector at 1 history request / 2 min (M8: 1/min; limit 2/min). Bursts are
  possible, and 429s are retried and logged. A second token only if 429s appear.

## D-038 — M6 commits open alert versions (me, 2026-10-17)
- Confirms D-027 for the datastore: open versions (empty `finished_at`) are committed. Supersedes D-016's wording
  "CSV of closed alerts".

## D-039 — Collection resumes automatically after a coverage hole (me, 2026-10-17)
- Exception to CLAUDE.md Architecture #6 ("detected gaps … nothing is committed"), for the collector only. A detected
  hole is recorded per unit in `reports/collect/coverage_holes.csv`, the new data is committed, and the run then ends
  red (exit code 3, so GitHub e-mails the owner). Coverage = the pulls' windows minus the recorded holes. Every
  other data check still fails the run with nothing committed.

## D-040 — Typed forecasts on the live site (M6-site; me, 2026-10-18: "yes")
- The live site shows yellow/red only in the oblast tooltip and card, labelled "in training". It uses the per-level
  two-week baseline until a typed model exists (blend weight 0). Levels are kept with the time they became known
  (versions; when the API changes a level in place, the latest version is kept — me, 2026-10-18). A yellow/red error
  never blocks the main forecast; it is shown on the page and in the run status.
- Design decisions P2–P8 of reviews/M6-site-consensus.md approved (me, 2026-10-18).
- Yellow/red count AIR-RAID alerts only (me, 2026-10-18), matching the M6c-1 models; the "any" target and map keep all
  API alert types (M8, D-032 proposed). Evidence: in the API data, red artillery alerts (Dnipropetrovska) keep the
  oblast "under red" and hide air-raid onsets (all types: 1,086 red / 4,498 yellow onsets vs air-raid only 1,119 /
  4,509). Amends D-033's typed targets: type = alert_level among air-raid alerts.
