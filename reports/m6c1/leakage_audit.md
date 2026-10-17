# M6c-1 leakage audit (ts-leakage-audit)

EXPLORATORY: alerts.in.ua event-time reconstruction, one test week.

PASS = the named test passes in `pytest -q` on the commit in run_meta.json, and the run's own assertions did not raise.

| check | PASS/FAIL | evidence |
|---|---|---|
| Features use only data with timestamp <= t (truncation invariance, real datastore, per type) | PASS | tests/test_newregime_leakage.py::test_truncation_invariance_real_datastore |
| Negative control: a leaky feature is caught, per type | PASS | tests/test_newregime_leakage.py::test_negative_control_is_caught |
| Rolling windows right-aligned; recent rate, red share and w(t) read only labels of s <= t - H | PASS | tests/test_newregime_leakage.py::test_rolling_quantities_are_causal |
| Fitted models / calibrators / baseline tables do not see test-week events | PASS | tests/test_newregime_leakage.py::test_fit_ignores_test_week |
| Test labels blanked before the fit stage (t + H > test start) | PASS | tests/test_newregime_leakage.py::test_label_isolation + run assertion in pipeline._all_frames_isolated |
| Split by date, half-open, purge t + H <= split end | PASS | tests/test_newregime.py::test_purge_edges |
| Baseline tables, calibration and early stopping use train / validation only | PASS | pipeline.fit_one (train rows -> fit_tables; validation -> early stopping + Platt rule) |
| Blend window uses out-of-sample rows only; validation blend = retrospective diagnostic | PASS | tests/test_newregime.py::test_blend_ignores_rows_before_cutoff |
| Test scored once (exclusive reservation before any test label is read) | PASS | tests/test_newregime.py::test_test_once_guard |
| Missing data (history start, holes) masked, look-back features NaN | PASS | tests/test_newregime.py::test_hole_masks |
