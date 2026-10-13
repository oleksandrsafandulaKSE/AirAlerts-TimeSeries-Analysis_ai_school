# Claude response, round 1 — plans/M5b.md

## Changes made
- B1 per-unit metrics — ESCALATED and RESOLVED by the human in chat: "Yes, full breakdown" (recorded in §2 as an explicit exception, proposed D-031).
- B2 non-scored rows — AGREE: export carries the exclusive D-024 status per row (scored / under_alert / gap_or_missing / feature_missing / purged); predictions null on non-scored rows; lines break; distinct bands.
- B3 assignment check — AGREE: sampled (unit, t) re-derived from raw alerts via grid.build_grid per unit; unit-swap and one-hour-shift mutations must fail.
- A1 onsets — AGREE: separate test_onsets.csv with D-023 merged onset timestamps, incl. an onset exactly on an hour boundary.
- A2 denominator/low-n — AGREE: base rate labelled "in hours when the oblast was quiet", scored hours shown; low-n tiles show the actual reason.
- A3 wording — AGREE: >0 / <0 / =0 / undefined cases defined; every comparison carries its scored-hours count; low-n caution.
- A4 rule wording (D-014, D-016) — AGREE: corrections proposed in the decision entry (human-owned file).
- A5 Google Fonts in proposed D-029 — AGREE: corrected in reviews/PROPOSED-DECISIONS-M4-M5.md.
- M1 exporter leakage — AGREE (§5). M2 done-criteria — AGREE (§6).

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL: map default view = frequency.

## Escalations
(none open — the per-unit exception was decided by the human.)
