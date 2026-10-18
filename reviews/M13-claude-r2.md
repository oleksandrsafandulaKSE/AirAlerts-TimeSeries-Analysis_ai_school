# M13 — Claude response, round 2

## Changes made
- B2 (OPEN): AGREE. §6 now matches §1: one rule, mixed labelled segments; the "until 7 days" sentence removed.
- New: failure isolation: AGREE (runner.mjs aggregates item errors into status.m12.error). Fatal (whole registry, no forecast.m12) vs item failure (items[k].error) separated; `m12_state.item_errors`; an item failure disables only that horizon / the yellow-red line; test with a failed red_h1.
- New: false absence: AGREE. Counts observed M, classified N, unclassified U; "no alerts" only when M = 0; "alert kinds not known yet" when N = 0 < M.

## Disagreements
- None.

## Design decisions taken
- PROVISIONAL: wording for unclassified onsets.

## Escalations
- None.
