# Site-redesign definition — Claude response, round 1

## Changes made
- B1 alert-type contract: AGREE (verified newregime/data.py:17 air_raid only vs live.mjs:17 all types). One contract: air-raid only on the main map; listed as D-045, a consequence of the human's D-042 choice.
- B2 P(red | onset): AGREE. Defined as conditional on an "any" onset (merged-interval start); colour = level starting at that instant, ties → red; escalations inside yellow excluded; N = 0 / incomplete coverage states; replacement models must be scored on the identical conditional outcome.
- B3 scorer: AGREE (verified check.mjs:112-120 hard-codes 1 h). Versioning by (model version, target, H), maturity τ + H + SETTLE, coverage [τ − 24 h, τ + H], no pooling across models/horizons.
- B4 replay: AGREE. Labelled retrospective reconstruction; pinned datastore commit, artefact hashes, code; consistency test reproduces published metrics; no new score.
- A1 seven days: AGREE (elapsed UTC (t − 7 d, t], merged onsets, coverage, N = 0). PARTLY on "fit the national share on training data": the comparator is a causal rolling share, not a fitted baseline, so it uses no future data.
- A2 blend state, A3 test-week boundaries, M1 parity controls, M2 metadata/reliability/AUC: AGREE, written as explicit requirements for the M12 plan with a PROVISIONAL default test week [10-18, 10-25).

## Disagreements
- A1 (partly): national comparator is causal rolling, not train-fitted (it is not one of the CLAUDE.md fitted baselines).

## Design decisions taken
- PROVISIONAL: tie (red and yellow start together) → red; escalation not counted; default new test week [2026-10-18, 2026-10-25).

## Escalations
- None new: D-045 follows from the human's explicit choice of the M6c-1 model (Q2) and is listed for ratification. D-027 and D-number collisions recorded as notes for the human.
