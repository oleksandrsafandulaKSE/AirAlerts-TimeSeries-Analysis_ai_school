# Claude response, round 3 — plans/M8.md

## Changes made
- B3 — AGREE: confirmed intervals may be disjoint; every successful history call confirms [c − 30 d, c) and is merged; only truly uncovered stretches remain holes (an unrecoverable stretch after a > 30-day outage stays a hole; fresh coverage after it is recorded).
- M2 — AGREE: label hours count only if the whole label window lies in one confirmed interval (windows crossing a hole excluded, as gap_mask_for does); 24 h post-hole state uncertainty for the unit and for national/neighbour inputs of every involved unit, unless backfilled.
- NEW (poll-only completeness) — ESCALATED and decided by the human: labels use history-confirmed hours ONLY (poll-only hours never supply labels); EVENT inputs may use the ACTIVE-poll record for the unconfirmed tail (≤ ~25 min) — an explicit human-approved live-mode exception (proposed D-032), stated on the page (§9).

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged).

## Escalations
(none open — the poll-tail exception was decided by the human.)
