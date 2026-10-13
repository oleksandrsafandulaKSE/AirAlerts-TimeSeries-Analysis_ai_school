# Claude response, round 2 — plans/M4.md

## Changes made
- B1 / Q2 open alerts — RESOLVED BY THE HUMAN (escalation, D-027, option A): CLAUDE.md's API merge rule now keeps open alerts; `finished_at` = NaT = end unknown, handled by the D-020 24h cap exactly like truncated official alerts. §5.1 drops the missing-data zones; open alerts are counted (per unit, and in-window). Older open alerts (6 standing, started before history_start) are kept; their onsets and 24h caps lie before the window and the history-start zone makes time-since NaN until a post-zone event (asserted).
- M2 API truncation — now consistent: the loader applies no closure-dependent filter, so truncating the RAW dump at t (drop starts > t, hide ends > t) and running loader → grid → features → predictor must equal the full-dump values. The test compares every feature column, the eligibility status and the prediction (not prediction only), at 4 API times, with the final-duration negative control.
- B2 joint lock — AGREE: ONE joint marker `reports/final_test_access.json` holds both preregistration sha256s and is written after verifying BOTH horizons' artifacts and BEFORE any test label of either horizon is read; a differing pair raises.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): LightGBM params; ECE 0.02 + Platt; new-regime grid end 2026-10-12 16:00; low-n threshold.

## Escalations
(none open — the open-alert rule was decided by the human: D-027.)
