# M12 — Claude response, round 3

## Changes made
- Seed seam (OPEN): AGREE. Seed definition and the test now distinguish labelled rows (s + H ≤ T_seed) from retained `pending` rows (s + H > T_seed); the maturity invariant applies to labelled rows only.
- New issue (fit pinning): AGREE (the guard at newregime/data.py:98). Two cut-offs: A_fit = acquisition (fetched_at of the last pull, immutable) and R_fit = floor_hour(coverage_end of the filtered inputs); R_fit ≥ 10-11 asserted; test for coverage ending 2026-10-17 21:06 after filtering → R_fit = 21:00. Prefix hashes keyed to A_fit.

## Disagreements
- None.

## Design decisions taken
- PROVISIONAL: A_fit / R_fit split as above.

## Escalations
- None.
