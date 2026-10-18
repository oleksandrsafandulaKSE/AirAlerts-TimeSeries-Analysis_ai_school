# M12 — Claude response, round 1

## Changes made
- B1 Split: AGREE (verified pipeline.py:49 val end = test start). New frozen `M12Split` with an unused gap [10-11, 10-18); order check stated.
- B2 blend history: AGREE. Operational weight cut-off = validation end; seed starts 10-11; M6c-1 train-end weights only for replay.
- B3 reserved-week exposure: AGREE. Seed T_seed = test start; parity τ + H ≤ test start; no m12-series metric computed/stored/shown while the flag is absent; switch only after the test stage; scorer counts m12 series from activation.
- B4 reconstruction pinning: AGREE (nd.load has reconstruct_at; versions filtered by fetched_at). Fit pinned at T_fit; canonical key (id, updated_at, fetched_at, pull_id); prefix hashes of datastore/pull log/holes; edits/deletions refuse, appends allowed; test evaluates on a later reconstruction (recorded).
- A1 keys: AGREE ("first_seen" removed; datastore columns verified).
- A2 seed/live identity: AGREE. Keys (unit, s); no overlap by construction; eligibility, 28 d eviction, reset per version.
- A3 red share: AGREE. Evaluates the displayed hourly forecast just before each onset (τ with o ∈ (τ, τ + 1 h], window (τ − 7 d, τ]).
- M1 tests: AGREE. Feature vectors + mask + p equality; mutation list per H; official gap regressions kept.
- M2 replay: AGREE. Exact key set and per-hour weights vs blend_weights.csv; swap test.
- M3 leakage report: AGREE. Required before any metric.
- Q2 (§E deferred): resolved inside the definition: the switch stays in M12 but is date-gated (two sessions), because B3 forbids activation before the reserved test; deploy itself is the human's (outward-facing).

## Disagreements
- Q1 (D-027): not a new question — the definition and the approved M6 decisions already restrict later revisions to reconstruction with separate live provenance. Recorded, no escalation.

## Design decisions taken
- PROVISIONAL: one reservation for all 9 models on [10-18, 10-25); unused gap week [10-11, 10-18); M12 in two sessions.

## Escalations
- None.
