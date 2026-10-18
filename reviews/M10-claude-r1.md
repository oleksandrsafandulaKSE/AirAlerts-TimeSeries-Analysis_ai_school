# M10 — Claude response, round 1

## Changes made
- B1 (A3 prior): PARTLY. Each variant now builds its own grid, labels, baseline and offset; the prior is the existing causal EXPANDING q(t) (`improve/features_plus.py:4,71`), so no full-train prior is used. Added variant-isolation label-mutation tests.
- B2 (§D AUC threshold): AGREE. Within-unit AUC uses ≥ 10 positives and ≥ 10 negatives per slice (D-025), exclusions listed, NaN with reason.
- A1 denominators: AGREE. Exact definitions added; groups pool numerators and denominators.
- A2 shifted onsets: AGREE. Split into disappeared / shifted / new-in-L1; duration median defined on the hromada rows starting at a disappeared onset.
- A3 zones: AGREE. Applied zone = `config.uncertainty_zones` [2026-08-29, 2026-09-04); predicate = `_zone_nan`; detected edges are a check only; recovery times stated.
- M1–M4 tests: AGREE. Exact weight vector via `get_weight()`, hand-calculated BSS, cut-off keys, onset at t / t+H, exposure edge pins, carry-in / unknown end / >24h, DST transitions, Kyiv City vs Kyivska.
- M5 done-when: AGREE. PR-AUC and PR-AUC/base rate, validation reliability plot, leakage evidence, run_meta ranges/counts, proposed decision entry.

## Disagreements
- B1: "reusing M7's frozen full-train prior" — not true for the code: `label_rates` computes q(t) as an expanding rate from labels with s ≤ t − H. The plan now says so explicitly; no other change.

## Design decisions taken
- PROVISIONAL: A2 matching is exact-instant (±0 s), since L1 onsets are a subset of L0 rows' starts.
- PROVISIONAL: group rates pool, never average.

## Escalations
- None. §E stays gated by a human-written approval file (question 3); the target is not changed.
