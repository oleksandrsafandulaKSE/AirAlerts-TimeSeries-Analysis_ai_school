# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr makes design decisions. You implement them. Never start a new milestone,
change the target definition, the evaluation protocol, or add a dependency without
explicit approval in chat. If you disagree with an instruction, say so with evidence,
then wait.

## Workflow (mandatory — see skill `milestone-protocol`)
Plan → wait for approval → implement → tests → run `reviewer` subagent → fix →
summary for the human. One milestone per cycle. Never chain milestones.

## Data
- Main source (train + final test): https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset
  (`datasets/official_data_en.csv`). Download at run time via `src/data.py`. Never commit data.
  This file FROZE at 2026-09-07 05:28 UTC (the yellow/red reform). Do not use
  `volunteer_data_*` (different collection channel).
- New-regime source (exploratory only): alerts.in.ua API, `/v1/regions/{uid}/alerts/month_ago.json`.
  Read it from the saved raw dump in `data/raw/alerts_in_ua/` (gitignored), not live.
  History covers closed alerts from 2026-09-12 17:16 UTC; 7–12 Sep is missing from both sources.
  Has `alert_level` red (missile) / yellow (drone); `threats[]` exists only in live data.
- API token: env var `ALERTS_IN_UA_TOKEN`, loaded from `.env` (gitignored). Never print,
  log, hardcode or commit it. Max 2 history requests/min.
- Never mix the two sources in one training set or one test metric.
- Timestamps are UTC. All grid work in UTC. Convert to Europe/Kyiv ONLY for calendar features.
- Admin reform: alerts moved from oblast level to raion/hromada level during 2025.
  Target unit = oblast. An oblast is "under alert" if ANY oblast/raion/hromada alert in it
  is active. Build per-oblast intervals as the UNION of all levels, using the dataset's
  `oblast` column. No fuzzy name matching. Deduplicate identical rows FIRST: 113,845 of
  299,275 rows are exact duplicates. Print the count. All other counts are computed after deduplication.
- Recording gap: the official file has no rows 2026-08-30 → 2026-09-01, and 29 Aug / 2 Sep
  are partial. Treat the gap as MISSING, not "no alert": mask those hours from evaluation
  (exact edges detected and printed in M1, D-013). Features that would read across the gap must
  be NaN or flagged, not computed as if nothing happened.
- Standing alerts (D-020, supersedes D-009): CAUSAL rule. An alert counts toward its oblast
  being "under alert" only during its first 24h after start (known at t without its end time).
  Its start still counts as an onset. Estimand: "under alert" = at least one active
  NON-standing alert (active ≤ 24h). Hours where only standing alerts are active are NOT masked.
  Without this, single hromada alerts lasting 439–604 days would keep all of Kharkivska
  "under alert" from May 2024 to Jan 2026. Never use the final `finished_at` to classify an
  alert as standing. Print the number of alerts that ran past 24h, per oblast.
- Units: 24 = 23 oblasts + Kyiv City. Luhanska oblast is EXCLUDED (permanent alert since
  Apr 2022). Crimea is not in the data.
- Exactly-30-minute durations (38 after dedup; 68 before): KEEP as-is; print the count (D-010).

## Target
- Hourly grid per oblast, UTC. Forecast time t = start of hour.
- y(t) = 1 if a new alert starts in (t, t+H]. Default H = 1 (configurable).
- Rows where the oblast is already under alert at t are excluded (masked) from training
  and evaluation for the onset task. Assert this with a test.

## Features — everything must be computable from data with timestamp <= t
- Own state: active_at_t, minutes_since_last_end, minutes_since_last_start,
  onsets_last_24h / 7d (windows end at t, exclusive of the future).
- Spatial: neighbors_active_at_t (border table in `src/regions.py`), national_active_count_at_t.
- Calendar (Kyiv local): hour, weekday.
- Forbidden: centered windows, scalers/encoders fit on full data, alert end times not yet
  observed at t, any statistic computed over the test period.

## Evaluation
- Walk-forward by DATE (not row index). Final test = the last 6 weeks of the official
  dataset, 2026-07-27 00:00 UTC → 2026-09-07 00:00 UTC. The model and fitted baselines are frozen
  at that point (exception: the rolling recent-rate baseline, see below).
- Train = all history, 2022-03-23 → 2026-06-29 (D-023). Validation = the last 4 weeks before the test,
  [2026-06-29, 2026-07-27). All intervals are half-open [start, end) in UTC (D-021).
- The final test is scored ONCE, at the end of M4, for the model and all baselines together.
  M3 reports baselines on validation only. Nobody looks at final-test numbers before then.
- New-regime section (API, 2026-09-13 → latest dump), labelled exploratory, never the headline (D-015):
  (a) before/after table per oblast and group: onsets per 30 days + share of time under alert,
      official 2026-07-27 → 08-29 vs API 2026-09-13 → 10-12;
  (b) frozen model + baselines scored on the primary target = ANY alert (yellow or red) starts,
      mask = any level active. Extra row if time allows: red-only onset, mask = red active only
      (red starting during a yellow counts as an onset);
  (c) within-oblast AUC + calibration-in-the-large (mean predicted vs observed) per group;
  (d) README conclusion CONDITIONAL on (b)/(c): if transfer fails, the model needs
      retraining/recalibration after the reform. Measured differences are stated as facts,
      interpretations as hypotheses (D-015 amended).
  No training or tuning on API data.
- Baselines required: climatology (hour × weekday rate from train), recent rate (last 14d),
  persistence (raw), AND calibrated persistence (per-oblast train rate of P(onset in next H |
  state at t)). The recent-rate baseline is the main bar to beat.
- Recent rate is ROLLING (D-021, an explicit exception to "baselines frozen"): at t, the unit's
  onset rate over unmasked rows s in [t−14d, t−H], so only labels that are already known by t.
  It updates through the test using past observations only. Same label-maturity rule for any
  training rows near a cut-off.
- PRIMARY metric: Brier skill score vs the rolling recent-rate baseline (D-021). Secondary: Brier,
  ROC-AUC (pooled AND mean within-oblast), PR-AUC (= average precision) AND PR-AUC / base rate.
  An overall reliability plot is REQUIRED (D-006). Not beating recent-rate is a valid,
  reportable result: report it honestly.
- Purge at every cut-off (train/val, train/test, each refit): drop training rows whose
  label window (t, t+H] reaches past the cut-off. Otherwise the first H hours after the
  cut-off leak into training.
- If time allows, after M4 (D-014): weekly refit inside the test window as an EXTRA results row.
  6 steps with cut-offs 2026-07-27, 08-03, 08-10, 08-17, 08-24, 08-31 (00:00 UTC). Each step
  trains on everything before its cut-off, early-stops on the ~2 weeks before it, and scores
  only the next week. Official data only. The headline stays the frozen model.
- If time allows (D-013): week-block bootstrap CI on the model's gain over recent-rate (Brier, PR-AUC);
  reliability plot per oblast group.
- Early stopping / tuning uses the validation slice. Never the test. NO refit on train+val
  after early stopping. A calibration check on validation; if calibration is fitted, it is
  fitted on validation and applied to that same model (D-021).
- Report per oblast group: Kyiv City; frontline = Chernihivska, Sumska, Kharkivska,
  Donetska, Dnipropetrovska, Zaporizka, Khersonska, Mykolaivska; rear = the other 15
  (Kyivska is in rear, separate from Kyiv City).

## Code standards
- Layout: `src/` (regions.py, config.py, data.py, grid.py, features.py, baselines.py,
  model.py, evaluate.py), `tests/`, `scripts/run_all.py`, `reports/`, `app/streamlit_app.py` (M5),
  `.github/workflows/` + `datastore/` (M6).
- Run inside a project `.venv` (the system Python's pandas is broken). Pin exact package
  versions and the Python version in `requirements.txt`. geopandas is not used.

## Architecture (D-017): built so M6 plugs in without rewrites
1. `src/regions.py`: the single table of the 24 units: canonical key, official English name,
   API UID, group, neighbours (hard-coded border table, symmetric). The ONLY place names
   are mapped. No fuzzy matching.
2. One shared alert format. `load_official()` and `load_api()` both return:
   `source, alert_id, unit, level, started_at, finished_at, alert_level` (`alert_level` is empty for
   official data). Nothing after `data.py` knows which source a row came from.
3. `src/config.py`: named run configs: `official` (D-007 dates), `new_regime` (D-015),
   `monthly(as_of)` (dates relative to the run date). No dates hardcoded elsewhere.
4. The target takes a level setting, `target_levels = "any" | "red"`; the mask follows the same setting.
5. `run_all.py --config <name> [--as-of DATE]` writes `reports/<run>/` with metrics.json,
   metrics.csv, plots and run_meta.json (data range, row counts, git commit, feature list).
   Printing stays as well.
6. Data-quality checks RAISE errors, not just print: detected gaps, duplicate counts,
   exactly 24 units present. A failing check means a failed run and nothing is committed.
- API merge rule (M4/M6): remove duplicates by `id`, keep the latest `updated_at`, closed alerts only,
  and apply the > 24h rule.
- `data/` stays gitignored (cache + raw JSON). The only committed data is
  `datastore/alerts_in_ua.csv` (M6, D-016).
- The monthly job runs `pytest` (including the leakage test) before retraining. A failing test means no retrain.
- Every module has a test. `tests/test_leakage.py` (truncation test) must always pass, AND
  must include a negative control: a deliberately leaky feature that the test must catch.
- No silent fallbacks (no synthetic data, no try/except that hides errors).
- Print shapes, date ranges, and base rates at each stage.

## Logging decisions
After each milestone, propose an entry for `DECISIONS.md`. The human edits and commits it.

## Scope
- M1–M5 = project scope. M6 (automated data workflow) = FUTURE WORK (D-016): not built
  unless the human starts it. A yellow-regime model is trained only with the human's explicit approval.
- Planning has two levels (D-019): roadmap here → Codex → human; then for each milestone plan → Codex
  → human → implement → tests → reviewer.
