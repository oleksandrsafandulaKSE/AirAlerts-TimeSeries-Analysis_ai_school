# M6c-1 — Claude's response to Codex round 1

## Changes made
- B1 "n = number of positives" — AGREE. The definition says onsets. §6 now: n = distinct type-T onset events
  (unit, o) with o ∈ (s, s+H] for some positive window row s ∈ W(t); an H = 3 onset counts once. Window W(t) named and
  defined (eligible, s ∈ [t − 28 d, t − H], s ≥ fit cut-off).
- B2 red-share support — AGREE. rr_any(t) comes from `src.baselines.recent_rate`, which reads only past ANY labels,
  so it exists on every RED scoring row (incl. ANY-masked rows); share counts k_red and k_any over the SAME rows
  (ANY-eligible ⊂ RED-eligible), π_u likewise on train. The approximation on yellow-active rows is stated.
- B3 validation w(t) not causal — AGREE. §6 now separates (a) TEST-WEEK blend = causal, reported; (b) VALIDATION
  blend = "retrospective diagnostic", separate block. New test 14: the fit stage on the datastore reconstructed at
  the test start gives byte-identical models/calibrators/baseline tables, so test outcomes cannot reach the fitted
  components behind w(t); test 13 keeps the label-perturbation check for the rolling parts.
- A1 marker — AGREE. Reservation at a fixed path keyed by split (`reports/newregime_test_access/…`), exclusive
  create BEFORE any test label is read, one reservation for all 6 models, status started → done; any existing file
  blocks fit and test; never auto-cleared.
- A2 fingerprint — AGREE. Pre-registration hashes `pull_log.csv`, `coverage_holes.csv`, the datastore, and code incl.
  `collect/api_collector.py`.
- M1 witnesses — AGREE (test 10): open alert / 24 h cap edges, onset exactly at t and at t + H, purge boundary
  t + H = split end kept, DST end 2026-10-25, synthetic hole edges, all per type and H. Negative control per type
  (test 12). PARTLY on "29 Aug–2 Sep": that gap is in the official file, not API data; its edges are already tested
  by the official suite, and the hole mechanism is tested synthetically.
- M2 conftest claim — AGREE, it was false. Plan now: project venv by absolute path; a gitignored symlink
  `data -> <main checkout>/data` for the official-data tests (read-only, no copy).
- M3 outputs — AGREE. `leakage_audit.md` (check | PASS/FAIL | evidence), full run_meta fields, §8b close-out
  (reviewer, harness, summary, D-040 draft).

## Disagreements
- Q (D-017 interfaces): not an escalation. `src/config.py` and `scripts/run_all.py` cannot change (bytes pinned by the
  M4 pre-registration fingerprint, `tests/test_improve_models.py`); M6a (`collect/`) and M7 (`improve/`,
  `scripts/run_improve.py`, plans/M7.md:26) already used a separate package + script. Plan §8c records it and the
  summary lists it for the human to ratify.

## Design decisions taken (PROVISIONAL)
1. Blend window = out-of-sample rows only (s ≥ fit cut-off); n = distinct onset events (Q7, Q8).
2. Red-share baseline on common ANY-eligible support (Q9).
3. Holes → national missing-data intervals with the official gap treatment (Q10).
4. Reporting = existing `metric_table` groups, ≥ 10/10 within-oblast AUC, low-n flags (Q12).
5. Validation blend is a retrospective diagnostic; the test-week blend is the causal result.
6. Split-keyed exclusive test reservation under `reports/newregime_test_access/`.
7. `air_raid` only, as in the M4 `new_regime` config.

## Escalations
None.
