# Claude response, round 1 — plans/M3b-H3.md

## Changes made
- "Every horizon-dependent rule already reads cfg.H": replaced by an explicit list of the functions that take H, with evidence (M3 harness run at H = 3), plus "any hard-coded 1h found is a bug".
- "Same mask": now "same mask rule; gap rows depend on H"; g0/g1 named from config; recovery row 09-04 00:00 asserted.
- Recent-rate test: exact n = 334 and k, negatives and NaN/masked rows at t−1h/t−2h, both 14-day endpoints.
- Onset at t: separated "not in y(t)", "a 40-min alert at t masks row t", "zero-duration alert at t masks nothing".
- Coverage vs terminal purge: separate table rows; C−3h kept, C−2h/C−1h purged.
- Fitting rules: one line referencing D-025 (unchanged).
- Byte-identical: only the deterministic artifacts; run_meta.json compared on config/count fields.
- Leakage: baseline truncation at H ∈ {1h, 3h} at 6 times + 2 DST times; negative control at H = 3.
- run_all fixture test: exact eligible counts, skill identity, test-label isolation.

## Disagreements
- D-017 acceptance checks (shared schema, regions, configs, pins, raising checks): inherited from M1–M3 and unchanged by M3b (only a new named config). Existing tests cover them (test_regions, test_config, test_data, test_run_all). Not repeated.
- Deadline: the human's M3 decision 12 replaced the timebox with the quality bar; D-026 removes the need to pause for approval. Not a plan issue.
- Terminal purge was already specified in §4 ("C−3h kept, C−2h and C−1h purged"); now also in §3.
- Raw-data truncation for FEATURES at H = 3: features do not depend on H (D-023); M2's test_leakage already covers DST, gap edges, >24h alerts and the 24h cap with negative controls.

## Design decisions taken
- PROVISIONAL: config name `official_h3`, folder `reports/official_h3/`.
- PROVISIONAL: new-regime section stays H = 1 (no change to D-015).
- M4 H = 3 model: out of M3b scope; left to the M4 plan / human (no decision taken).

## Escalations
(none — adding H = 3 as an extra results row was approved by the human in chat on 2026-10-13; M3b changes no rule.)
