# Claude response, round 1 — plans/M4.md

## Changes made
- B1 open alerts — AGREE (verified on the dump: 39 open alerts of the 24 units; 12 started inside [history_start, grid_end): Dnipropetrovska 6, Poltavska 1, Kharkivska 5; 6 started before 09-12 and cannot affect the window because their 24h cap ended before it). The CLAUDE.md merge rule ("closed alerts only") is a rule the loop cannot change, so §5.1 keeps closed-only AND treats every in-window open start as missing data with the existing gap machinery (g0 = g1 = s, 24h post-zone, national): label/state mask [s − H, s + 24h), state NaN, windows touching NaN, time-since NaN. D-024 then drops those rows. Scored API window ≈ [09-25 11:00, 10-11 08:00) (printed). The causal alternative (keep open alerts with the 24h cap) is recorded as a recommendation to the human, not applied.
- B2 both horizons frozen first — AGREE: `--stage fit` per run, then one `--stage final-test` that refuses unless both preregistration files exist.
- B3 hash binding — AGREE: preregistration holds sha256 of model, calibrator, baseline tables, data file and a code fingerprint; score_final_test recomputes them from the files it uses, raises on mismatch, and writes an access marker BEFORE reading labels (a crash cannot reopen selection with a different predictor).
- B4 full predictor for transfer — AGREE: model + calibrator.json (clip, logit, Platt) reloaded with hash checks and required to reproduce the saved official validation predictions before API scoring.
- A1 Platt details — AGREE: clip 1e-6, LogisticRegression(penalty=None, lbfgs, max_iter=1000, intercept), raise on non-convergence / one class / slope ≤ 0; without a calibrator only the raw row is reported.
- A2 before/after definitions — AGREE: merged onsets, exposure = hours outside every uncertainty zone, unknown exposure excluded, pooled group sums.
- A3 identity check — AGREE: regions.py gains the API's Ukrainian oblast name per unit; each file's location_oblast must match its UID's unit; swapped 31/14 test.
- M1 exact keys / behavioural isolation for both horizons — AGREE (§7).
- M2 API loader-to-predictor truncation with a negative control — AGREE (§7).
- M3 D-017 outputs for new_regime (metrics.json, reliability.png, run_meta.json, diagnostics) — AGREE (§9).

## Disagreements
- Q1 (gap edges vs 145 h): already reconciled and tested. D-022 records the DETECTED gap [08-29 05:00, 09-02 13:00) inside the APPROVED gap [08-29, 09-03); M3 decision 4 and `config.gap_label_mask_interval` define the label/state mask [08-28 23:00, 09-04 00:00) = 1 h before + 120 h gap + 24 h after = 145 h, asserted on the real grid by `run_all.check_gap_rows` and `tests/test_evaluate.py::test_gap_interval_config`. No change needed.
- Q2 (approve keeping open alerts): not required for this plan — the within-rules missing-data treatment (B1) removes the bias at the cost of window length. Forwarded to the human as a recommendation only.

## Design decisions taken
- PROVISIONAL: LightGBM params; ECE 0.02 + Platt details; new-regime grid end 10-12 16:00; low-n threshold 100 rows; open in-window API alerts as national missing-data zones.

## Escalations
(none required by this plan. Recommendation, not a blocker: amend CLAUDE.md's API merge rule to keep open alerts with the causal 24h cap.)
