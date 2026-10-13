# M3b plan v1 — Additional horizon H = 3 (extra results row, never the headline)

Status: v1.3 after consensus round 3 (D-026 loop). Requested and approved by the human (2026-10-13):
"add additional horizon h=3".
Amends D-000 (H = 1 only) and D-013 (multiple horizons skipped). The headline stays H = 1.

## 1. Goal
Run the existing M1–M3 pipeline with H = 3 hours as a second, separate run:
`python scripts/run_all.py --config official_h3` → `reports/official_h3/` with the same files as
`reports/official/` (run_meta, m1/m2/m3 checks, `metrics_validation.*`, reliability plot).
Target: y(t) = 1 if a new alert (merged unit onset, D-023) starts in (t, t+3h]. Same mask RULE (the gap rows
depend on H, §3), same features, same splits, same baselines (D-025 fitting rules: climatology = unit × Kyiv hour ×
Kyiv weekday, calibrated persistence = unit × `minutes_since_last_end` bins, α = 10, eligible train rows only),
VALIDATION only. Whether M4 trains an H = 3 model is OUT OF SCOPE here: it is decided in the M4 plan; if it is
done, its test rows are scored in the same single M4 test scoring as H = 1 (D-021).

## 2. What changes (code)
- `src/config.py`: `official_h3()` = `official()` with `name="official_h3"`, `H=3h`; registered in `get_config`.
- **Label cut-off fix (Codex round 2, blocker):** a label at row t is about (t, t+H], so before M4 no label with
  t + H > C (C = test start) may be read. Today two places use `t < C`, which equals `t + H ≤ C` only at H = 1:
  (a) `grid.base_rate_table` / `check_base_rate` (M1 printout, CSVs and the 50% check) → filter `t + H ≤ C`;
  (b) `evaluate.isolate_test_labels(frame, C, H)` → blank y where `t + H > C` (at H = 3 also rows C−2h, C−1h).
  At H = 1 both rules select exactly the same rows as now, so all H = 1 outputs must stay byte-identical.
- Existing code (M1–M3) already takes H from `cfg.H` in: label window (`grid.build_grid`), gap mask
  (`grid.gap_mask_for`, `config.gap_label_mask_interval`), coverage check, purge (`evaluate.eligibility`),
  recent-rate history (`baselines.recent_rate`), raw persistence (`baselines.persistence_raw`). Evidence: the M3
  harness review ran `run_m3` with H = 3 on real data (purge 48 rows per split, gap 147 h, recent rate dropping
  t−1h and t−2h). The tests below pin this down; any hard-coded 1h found while implementing is a bug to fix.
- No new dependency, no change to features (they do not depend on H, D-023).

## 3. What H = 3 does to each rule (all already implemented via `cfg.H`; now tested at H = 3)
| Rule | H = 1 | H = 3 |
|---|---|---|
| Label | onset in (t, t+1h] | onset in (t, t+3h] |
| Purge at cut-off C | keep t+1h ≤ C (removes 0 rows) | keep t+3h ≤ C → last 2 rows per unit before each cut-off removed (48 per split) |
| Gap mask (g0 = 2026-08-29 00:00, g1 = 09-03 00:00, config) | [g0−1h, g1+24h) = 145 h | [g0−3h, g1+24h) = [08-28 21:00, 09-04 00:00) = 147 h; row 09-04 00:00 not gap-masked |
| Coverage check (grid) | last row 09-06 23:00, label ends 09-07 00:00 ≤ 05:28 | last row 09-06 23:00, label ends 09-07 02:00 ≤ 05:28 |
| Terminal purge at each cut-off C | C−1h kept | C−3h kept; C−2h, C−1h purged (t+H ≤ C, D-022) |
| Recent rate history | s ≤ t−1h | s ≤ t−3h (labels at t−1h, t−2h not yet known) |
| Raw persistence | onset in (t−1h, t] | onset in (t−3h, t] |
| Calibrated persistence / climatology | train rate of the H = 1 label | train rate of the H = 3 label |
| D-024 feature rule, test isolation, allow_test guard | unchanged | unchanged |
| Base-rate check (no quarter ≥ 2025Q1 < 50% of 2024) | applies | applies |

## 4. Tests (hand-written expectations, H = 3)
- Config: `official_h3` has H = 3h and identical dates/gaps to `official`; `official` still has H = 1h.
- Label edges: onset at t+3h → y(t) = 1; onset at t+3h+1min → y(t) = 0; an onset exactly at t is NOT in y(t)
  (window is (t, t+3h]); a 40-min alert starting at t masks row t; a zero-duration alert at t masks nothing (D-022).
- Gap mask edges: t = g0−3h → gap_mask 1; t = g0−4h → 0; t = g1+24h → 0 (recovery);
  `gap_label_mask_interval(official_h3)` = [08-28 21:00, 09-04 00:00); `check_gap_rows` = 147 on the real grid.
- Purge: rows C−3h kept, C−2h and C−1h purged (already in test_evaluate). Real run: exclusive purge count =
  2 rows × 24 units = 48 for train and for validation (asserted in the H = 3 printout check).
- Recent rate at H = 3, exact k and n: hourly history, window s ∈ [t−336h, t−3h] → n = 334. Cases:
  (a) a positive at t−3h counts (k = 1) and one at t−336h counts; t−337h does not; (b) positives AND negatives at
  t−1h and t−2h change neither k nor n; (c) a NaN label at t−5h reduces n to 333; a masked row likewise.
- Raw persistence: onset at t−2h59m → 1; onset exactly at t−3h → 0.
- Leakage: `test_baselines_truncation_invariant` parametrized over H ∈ {1h, 3h} at the same 6 real times plus the
  two 2025 DST times (raw-data truncation: starts > t dropped, ends > t hidden), and the leaky-window negative
  control at H = 3 (window reading s ≤ t−1h must be caught at a pinned witness). Features do not depend on H;
  their truncation/DST/24h-cap coverage is M2's test_leakage.
- Label cut-off, two separate checks at H = 3:
  (1) **label poisoning** (masks and features held fixed): flip every y with t + H > C in the frame passed to the
  M1 base-rate step and to `run_m3` → the base-rate tables, the 50% check result, `p_unit`, every validation
  prediction and the validation metric table are identical;
  (2) **raw event after C**: add a 40-min alert at C + 1h to the raw data → the same label diagnostics, fitted
  quantities, validation predictions and metrics are identical. Test-availability counts (D-024) and source
  metadata MAY change (they describe raw data, not labels) and are not compared.
  Plus exact rows: `isolate_test_labels(..., H=3h)` blanks exactly t ≥ C − 2h; `base_rate_table` with H = 3
  ignores rows C−2h and C−1h.
- run_all on the fixture with H = 3 writes `metrics_validation.csv` with 16 rows, the eligible counts equal the
  hand count (purge 2 rows per unit per cut-off), recent rate's skill is 0, and test labels are isolated.

## 5. Printed / reported
Same printout as `official`, with H shown in every header line and in `run_meta.json`.
The README will present H = 3 as a separate table labelled "additional horizon", next to the H = 1 headline.

## 6. Interpretation caveats (go into the README)
- Base rate is higher at H = 3, so Brier and PR-AUC are not comparable across horizons; compare each model
  with the baselines of the SAME horizon (Brier skill vs the H = 3 recent rate).
- Consecutive rows share label windows (one onset is positive for up to 3 rows), so rows are strongly
  autocorrelated and the effective sample size is smaller than the row count.
- The mask still only looks at t: a row counts if the unit is quiet at t. At H = 3 the frontline validation
  subset is strongly selected (1,347 eligible rows, base rate 0.761): a skill score there describes "quiet hours
  in frontline units", not frontline hours in general.
- The recent-rate reference itself changes with H (it drops the 2 freshest hours at H = 3; min history n 2,
  13 validation rows with n < 10), so Brier skill vs recent rate is not comparable across horizons.
- Any confidence interval at H = 3 must use week blocks (D-013), never a row-level bootstrap.
- Code rule added after review: H must be a positive whole number of hours (`RunConfig` raises otherwise).

## 7. Done when
- `pytest -q` green, including the new H = 3 tests and the H-parametrized leakage test.
- `run_all.py --config official_h3` exits 0 and writes `reports/official_h3/`; two runs identical.
- `run_all.py --config official`: metrics_validation.{csv,json}, reliability bins and m1/m2/m3 checks are
  byte-identical to before (H = 1 untouched); `run_meta.json` is compared on its config/count fields only
  (it records the git commit).
- Reviewer SHIP; harness review findings fixed or argued.

## 8. Effort
Small: config (5 min), tests (30 min), run + reviews. No change to M1–M3 logic expected.

## 9. Decisions (round 1)
1. Config name `official_h3`, output `reports/official_h3/` — PROVISIONAL (Claude+Codex consensus, human to ratify).
2. M4 scope for H = 3 (model or baselines only) — OUT OF SCOPE for M3b; decided in the M4 plan (human). If a model
   is trained, its test rows are scored in the same single M4 test scoring (D-021).
3. New-regime section (D-015) stays H = 1 only: no change to D-015 — PROVISIONAL.
4. Records: proposed DECISIONS entry D-027 (D-026 is now the consensus loop) and a CLAUDE.md Target line, both
   for the human (the loop never edits them).
