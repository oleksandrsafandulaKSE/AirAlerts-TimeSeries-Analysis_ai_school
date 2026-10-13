# Claude response, round 3 — plans/M5.md

## Changes made
- B3 — AGREE: hand-written README text may contain no result number in any format: every number token outside the generated blocks must match an explicit allow-list (dates/times/years, D-numbers, milestone ids, version pins, rule constants enumerated in §8); mutations inserting "0 units used", "1 positive", "7 positives", "9 rows" must fail the test. `positives` and `within_unit_units_used` therefore appear only in generated, source-verified tables.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): static self-contained site + required local Streamlit; inline SVG/vanilla JS; private preview (supplementary); Netlify deployment OUTSTANDING until a verified URL.

## Escalations
(none)
