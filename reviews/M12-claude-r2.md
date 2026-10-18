# M12 — Claude response, round 2

## Changes made
- B4 (OPEN): AGREE (verified collect/api_collector.py:580-583: latest version per id, no fetched_at cut). New `horizons.load_pinned(T_fit)` filters datastore / pull log / holes by fetched_at ≤ T_fit BEFORE the same reconstruction.
- A2 (OPEN): AGREE. Identity = (unit, snapshot hour); labels, maturity and blend use the actual issue time τ_s; test for a 10:05 snapshot.
- A3 (OPEN): AGREE. Rule, coverage and national comparator all anchored at the same τ.
- M2 (OPEN): AGREE. Keyed per-row comparison vs an independent `pipeline.score_range` recomputation (y, status, p_model, p_baseline, w, p_blend), swap fixture.
- Q2 (OPEN): AGREE. §0 rewritten: switch is in M12 session 2, deploy by the human.
- Provisional scope: AGREE. Reservation restored to H = 6/12/24 only; H = 1/3 on a second week left to the human.
- New issue (seam): AGREE. Seed holds s ≤ T_seed with `pending` labels resolved later by the live label function; while inactive, the new path stores p_model / p_baseline only and resolves no reserved-week label.

## Disagreements
- None.

## Design decisions taken
- PROVISIONAL: inactive path stores predictions only (no w, no blended p).

## Escalations
- None.
