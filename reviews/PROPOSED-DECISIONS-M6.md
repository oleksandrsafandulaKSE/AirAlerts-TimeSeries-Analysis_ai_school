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
