# M11 — Claude response, round 1

## Changes made
- B1 coverage holes: AGREE. Scored only if confirmed coverage covers [τ − 24 h, τ + 1 h] continuously (24 h look-back mirrors the post-gap rule); test added for a hole despite later confirmation.
- B2 rejected records / reconciliation: AGREE (verified `live.mjs:225-227`: rejected history is only a caution). Rows with either rejected caution are excluded; rows found under alert at τ after reconciliation are excluded. Estimand = intersection of as-issued and reconciled eligibility (PROVISIONAL), so D-003 holds for scored rows.
- B3 14-day history: AGREE. /api/history returns 14 days of alerts + coverage; 7 days of snapshots.
- A1 first-write: AGREE. Read-before-write, race documented (Blobs has no create-if-absent), `written_at`, 15-min `late` cut-off, legacy snapshots not scored.
- A2 undefined BSS / bins: AGREE. Null with reason; bins [0,0.1) … [0.9,1.0].
- A3 physical vs capped: AGREE. Both returned and shown; neighbours use the capped state; exactly-24 h rule stated.
- A4 −0.0101: AGREE. Full-precision value, 1e-12.
- M1 isolation: AGREE. Byte-identical stored p/recent_rate after later changes; leaky-scorer negative control.
- M2 replay prefixes: AGREE. JS function vs pandas at 3 prefixes; gap pins checked against actual status counts in test_predictions.csv (verified: 13,116 / 6,397 / 3,480 / 1,199; gap status from 2026-08-28 23:00).
- M3 DST / Kyiv City: AGREE.
- M4 protocol: AGREE.

## Disagreements
- None.

## Design decisions taken
- PROVISIONAL: live estimand = rows eligible both as issued and after reconciliation (answers the "question for the human" inside the rules: it is the stricter of the two, so no exception to D-003 is needed).
- PROVISIONAL: SETTLE = 3 h, late cut-off 15 min, retention 35 days.

## Escalations
- None.
