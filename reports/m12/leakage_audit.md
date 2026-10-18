# M12 leakage audit (ts-leakage-audit) — session 1

EXPLORATORY: alerts.in.ua event-time reconstruction (D-027), air-raid alerts only (D-045). No label of the reserved test
week [2026-10-18, 2026-10-25) was read in session 1.

PASS = the named test passes in `pytest -q` / `node --test 'netlify/live/test/*.test.mjs'` on the commit in
`reports/m12/run_meta.json`, and the run's own assertions did not raise.

| check | PASS/FAIL | evidence |
|---|---|---|
| Features at t unchanged when raw data after t is removed (Python, H = 6 and 24, real pinned data) | PASS | tests/test_m12.py::test_features_truncation_invariant |
| Recent-rate baseline reads only labels with s <= t - H (H = 6/12/24, real data); negative control: a window ending at t is caught | PASS | tests/test_m12.py::test_recent_rate_uses_only_labels_known_at_t_and_negative_control |
| JS: feature vectors, mask state, p_model, p_baseline unchanged by truncation at 6 pinned tau, every (type, H) | PASS | netlify/live/test/m12.test.mjs "truncation per (type, H)" |
| JS negative control: a feature reading an end after tau is caught at a pinned witness | PASS | m12.test.mjs "truncation negative control" |
| JS negative control INSIDE registryAt, every (type, H): future onsets pulled before tau are caught by the same truncation comparison that passes for the real inputs | PASS | m12.test.mjs "negative control inside registryAt, per (type, H)" |
| Test stage can never be reached past its gate from pytest; no test writes into reports/m12 | PASS | tests/test_m12.py::test_test_stage_gate_runs_before_reserve_and_writes_nothing, ::test_test_ready_gate |
| Parity fixture = alerts as known at T_seed (no reserved-week start or end committed) | PASS | scripts/run_m12.py stage_export; m12_parity_records.json `known_at` |
| Activation refused before 2026-10-26 03:00 UTC or without the test metrics sha256 | PASS | m12.test.mjs "registry: 9 models …" |
| JS mutations: later finished_at, exact 24 h cap, Kyiv City vs Kyivska, artillery alert (D-045) | PASS | m12.test.mjs "mutations", "D-045" |
| JS = Python per (type, H): features, raw, calibrated model, D-025 baseline, operational blend weight | PASS | m12.test.mjs "parity …" (4 tests) |
| Label window (t, t + H]: onset at t is not y(t), at t + H is; purge t + H <= cut-off (equality kept), H = 6/12/24 | PASS | tests/test_m12.py::test_label_window_endpoints_and_purge, ::test_fit_rows_respect_cutoffs |
| Fit / validation rows end before their cut-offs; no frame row's label reaches the reserved week | PASS | tests/test_m12.py::test_fit_rows_respect_cutoffs + `HZ.isolated` assertion |
| Fit inputs pinned by acquisition cut-off; appends allowed, edits / deletions refused; R from filtered coverage | PASS | tests/test_m12.py::test_pinning_appends_allowed_edits_refused, ::test_reconstruction_time_from_filtered_coverage |
| M6c-1 H = 1/3 artefacts copied, not refitted; a changed byte is refused | PASS | tests/test_m12.py::test_artifact_copy_refuses_a_changed_byte |
| Test stage: refuses before coverage reaches 10-25, refuses an overlapping reservation, never reserves on a failed check; fit refused after access | PASS | tests/test_m12.py::test_test_stage_* , ::test_fit_refuses_after_the_week_was_accessed |
| Blend: operational cut-off = validation end; seed labelled rows have s + H <= T_seed = test start; pending rows carry no label | PASS | m12.test.mjs "seed: …", "blend weight: …"; `HZ.blend_seed` assertion |
| Inactive path: no w, no blended p, no metric, /latest byte-identical to the M8 run | PASS | m12.test.mjs "runner, INACTIVE …", "scoreSeries: inactive computes nothing …" |
| Live labels: settle τ + H + 3 h, coverage over [s − 24 h, s + H], reconciled under-alert excluded, forbidden window | PASS | m12.test.mjs "labelRow …" |
| Replay = reconstruction, no new score: keys, y and per-row p / w equal an independent `pipeline.score_range`; published metrics reproduced | PASS | tests/test_m12.py::test_replay_matches_an_independent_score_range_per_row; run assertion (max diff 1e-16) |
| M6c-1 code and the official headline code untouched | PASS | tests/test_m12.py::test_m6c1_and_official_code_untouched |
| Red-share rule: windows (τ − 7 d, τ] strictly before the onset, coverage, simultaneous → red, escalation excluded | PASS | tests/test_m12.py::test_redshare_fixtures, ::test_redshare_coverage_hole_excludes_and_window_anchor |

Known limitations (not leaks, documented): D-027 latest versions in every reconstruction (live snapshots are as issued);
the parser-free API source has no imputed ends, but later API revisions are included in the replay and seed.
