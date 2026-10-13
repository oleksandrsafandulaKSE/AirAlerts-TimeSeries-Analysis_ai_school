# Claude response, round 2 — plans/M3b-H3.md

## Changes made
- NEW BLOCKER (pre-C labels at H = 3) — AGREE. Verified: `grid.base_rate_table` filters `t < before` (src/grid.py) and `evaluate.isolate_test_labels` blanks `t >= test_start`; at H = 3 rows C−2h and C−1h keep labels whose window (t, t+3h] reaches past C. Plan §2 now requires `t + H ≤ C` for every label read before M4: (a) base-rate table/check filter `t + H ≤ C`; (b) `isolate_test_labels(frame, C, H)` blanks y where `t + H > C`. At H = 1 the row sets are identical (hourly grid), so H = 1 outputs must stay byte-identical (already a done-criterion).
- §4: new test — a synthetic onset at C + 1h leaves every M1/M3 output unchanged at H = 3; exact blanked rows (t ≥ C − 2h) and base-rate rows asserted.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): `official_h3` / `reports/official_h3/`; new-regime section stays H = 1.

## Escalations
(none — this tightens the implementation of existing rules D-021/D-022; no rule changes.)
