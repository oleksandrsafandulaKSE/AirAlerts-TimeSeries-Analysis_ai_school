# Proposed DECISIONS.md entry — M6c-1 (the human edits and commits)

## D-040 — M6c-1 first new-regime typed models (Claude+Codex consensus + reviews, 2026-10-18)
- Context: D-033…D-035 (proposed) allow typed targets and training on API data. M6c-1 trains any / yellow / red onset
  models (H = 1 headline, H = 3) on alerts.in.ua history only (event-time reconstruction), split train 09-13 → 10-04,
  validation 10-04 → 10-11, test 10-11 → 10-17 19:00 UTC (scored once). EXPLORATORY: one test week.
- Approved by the human in chat (2026-10-18): D-017 exception — `newregime/` + `scripts/run_newregime.py` (src/ and
  run_all.py stay frozen); committing M6c-1 on its branch (no PR, no merge).
- PROVISIONAL (consensus, to ratify): (1) blend window = out-of-sample rows only (s ≥ fit cut-off), n = distinct
  onset events, pooled, n0 = 50, 28 d; (2) red-share extra baseline on common ANY support; (3) coverage holes →
  national missing-data intervals with the official gap treatment; (4) reporting = `metric_table` groups, ≥ 10/10
  within-oblast AUC; (5) validation-week blend = retrospective diagnostic only; (6) test-once reservation keyed by
  the test week, refusing any overlapping week; (7) `air_raid` only.
- Evidence (test week, Brier skill vs rolling recent rate, all oblasts): ANY model +0.085 (H1) / +0.118 (H3); YELLOW
  +0.045 / +0.054; RED −0.063 / −0.069 (blend −0.017 / −0.013). Frozen official model on ANY: +0.029 / +0.130.
- Known limits: w at test start comes from the validation week where the model was early-stopped/calibrated
  (w ≈ 0.93 any/yellow), so n0 = 50 barely shrinks it; recent rate's within-oblast AUC is < 0.5 on validation, which
  flatters skill; 2 weeks of effective training rows.
