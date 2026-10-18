# M9 — Claude response, round 2

## Changes made
- **E1/E2 boundary (OPEN): AGREE.** With H = 1, t = C and t + H = C cannot coincide. §E2 now requires two
  separate causal checks at each val/test cut-off C:
  - t = C − H, where the label window (C − H, C] matures exactly at C;
  - t = C.

## Disagreements
None.

## Design decisions taken
Unchanged from round 1. Codex confirmed all three PROVISIONAL decisions stay inside the rules:
- the 25% threshold with ≥ 10 earlier onsets;
- seed 20261017, B = 10,000;
- Newey–West lags 24 / 72.

## Escalations
None. The round-1 escalation was resolved by the human's approval of §§B–D (recorded in plans/M9.md §0).
