# Claude response, round 2 — plans/M7.md

## Changes made
- A2 — AGREE: every label-based rate (unit 14 d/30 d, national 14 d, offset prior) is sum(y)/count(y) over eligible rows (unmasked, label known, s ≤ t − H), the binary label of grid.build_grid; national pooled over units.
- Q1 — recorded explicitly, no escalation needed: the human approved in chat (i) "recent rates over 14 and 30 days as inputs", (ii) "make the model learn on top of the recent rate", (iii) the weekly refit. §0 now names these as the ONLY M7 components that may read earlier test labels (always s ≤ t − H, like the recent-rate baseline), recorded in proposed D-030. Blocks B and C use onset events up to t (raw data, as the existing M2 onset-count features already do), not labels.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): folds and acceptance rule; causal expanding prior; V5 on V3; H = 1 only.

## Escalations
(none)
