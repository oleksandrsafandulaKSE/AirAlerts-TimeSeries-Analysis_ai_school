# Claude response, round 3 — plans/M7.md

## Changes made
- A2 — AGREE: the obsolete merged-onset national-rate definition is removed; onsets are named only for blocks B and C.
- Oracle — AGREE: zero residual returns clip(r(t), 1e-4, 1 − 1e-4), with endpoint cases r = 0 → 1e-4 and r = 1 → 1 − 1e-4 tested.
- NEW (rate definitions) — AGREE: k = sum(y), n = count(y) over eligible mature rows; unit rates (14 d, 30 d, offset r(t)) shrunk (k + 10·q)/(n + 10) with the causal prior; the expanding prior q and the national 14-d rate are pooled, unshrunk k/n.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged).

## Escalations
(none)
