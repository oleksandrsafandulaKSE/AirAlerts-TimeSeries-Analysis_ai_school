# Claude response, round 3 — plans/M3b-H3.md

## Changes made
- NEW acceptance-test issue — AGREE. Verified: `run_m3` exports `test_availability_no_labels` (D-024), which reads masks of test rows, so a raw alert at C+1h legitimately changes it. §4 now has two separate checks at H = 3: (1) label poisoning with masks/features held fixed — flip every y with t + H > C → base-rate tables, 50% check, p_unit, validation predictions and metrics identical; (2) a raw 40-min alert at C+1h → the same label diagnostics, fitted quantities, validation predictions and metrics identical; test-availability counts and source metadata may change and are not compared. Exact blanked/filtered rows still asserted.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): `official_h3` / `reports/official_h3/`; new-regime section stays H = 1.

## Escalations
(none)
