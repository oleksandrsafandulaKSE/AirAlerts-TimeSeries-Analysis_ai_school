# Claude response, round 4 — plans/M8.md

## Changes made
- M2 — AGREE: holes now carry an EXTENDED zone [h0, h1 + 24 h) handled exactly like config.uncertainty_zones: onset-count windows touching it → unknown; time-since → unknown if τ ≥ h0 and the last event is before h1 + 24 h (features.py D-023 rule); label hours in [h0 − H, h1 + 24 h) excluded from k, n, q (the hours grid.gap_mask_for masks), in addition to requiring confirmed label windows.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged).

## Escalations
(none)
