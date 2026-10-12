# Full implementation plan, M1–M6

One plan for all milestones, for a single Codex review before implementation starts in a
separate chat. M1 below is copied unchanged from plans/M1.md (already reviewed once, see
reviews/M1-codex.md; its findings are listed under Open decisions, not applied).


---

# M1 — Data, oblast intervals, hourly grid, mask (unchanged from plans/M1.md)

## Part 1 — original M1 plan

**Goal:** turn the raw official data into a clean hourly grid of the 24 units, with the target and the "already under alert" mask. No features yet.

**Files**
- `.venv/` for the environment.
- `src/data.py` with `load_official()`. It downloads to `data/` (gitignored) and re-uses the copy if it's already there. It parses times as UTC, removes duplicate rows, excludes Luhanska, and checks that exactly 24 units remain.
- `src/grid.py` with three steps:
  - `oblast_intervals()`: drop alerts longer than 24h (count printed per oblast), then merge overlapping alerts of all levels into one set of intervals per oblast.
  - `detect_gaps()`: any national period of more than 24h with no alerts starting is flagged as missing. Its edges run from the last alert before the gap to the first alert after it, and are printed for you to review.
  - `build_grid()`: one row per hour per unit from 2022-03-15 to 2026-09-07 05:00 UTC. Columns: `active_at_t`, `y` = 1 if an oblast-level alert starts in (t, t+1h], `mask` (under alert at t, or inside a gap), and `group`.
- `tests/test_data.py` and `tests/test_grid.py`, built on small made-up examples:
  - merging overlapping and touching alerts
  - dropping alerts over 24h
  - the edges of the onset window: an alert starting exactly at t is masked, one starting exactly at t+1h counts
  - no masked row has `active_at_t = 0` unless it's in a gap, and no unmasked row is under alert
  - hours inside a gap are masked
  - duplicates removed
  - Luhanska excluded
- `scripts/run_all.py` runs only the M1 stage for now.

**What it prints**
- row counts before and after removing duplicates
- the number of 30-minute alerts and of alerts over 24h, per oblast
- the detected gaps
- the grid's shape and date range
- the base rate per quarter and per group, to check the target doesn't collapse after 2025

**Assumptions for you to check**
1. **An oblast "onset" is the start of a merged interval.** If raion A is already under alert and raion B's alert starts, that is *not* a new onset, because the oblast is already masked. This follows from the masking rule.
2. **Alerts are merged only if they overlap or touch.** A gap of even one minute between two alerts creates a new onset. There's no smoothing threshold.
3. **API data isn't loaded in M1.** It comes in M4, for the exploratory new-regime section.

**Open question**
- **Neighbour features in M2:** CLAUDE.md says "P-code adjacency", which would need geopandas plus a boundary-file download. I suggest instead a hard-coded table of which of the 24 units border each other, checked once against a map. That removes the geopandas dependency. Your call.

**Risks**
- How Kyiv City is named in the data compared with Kyivska.
- Whether the >24h-in-a-row national gap rule catches the 29 Aug–2 Sep gap cleanly. That will be shown in the printed output.

---

## Part 2 — update: D-017 architecture changes added to M1

- **The original plan:** load the official data, remove duplicates, drop alerts over 24h, merge each oblast's alerts across levels, detect gaps, build the hourly grid with the target and mask, and the tests.
- **Changes #1, #2 (official loader only), #3, #4 and #6 from above:**
  1. New `src/regions.py`: one table of the 24 units with a canonical key, the official English name, the API UID (for example Kyiv City = 31), group, and the neighbour list.
  2. One shared alert format in `src/data.py`: `load_official()` (and later `load_api()`) return the same columns: `source, alert_id, unit, level, started_at, finished_at, alert_level` (`alert_level` is empty for the official data).
  3. New `src/config.py` holding named run configs: `official` (the fixed D-007 dates), `new_regime` (D-015), `monthly(as_of)` (dates computed relative to the run date).
  4. The target takes a level setting: `target_levels = "any"` or `"red"`, and the mask follows it.
  6. Data-quality checks fail the run instead of just printing. Gap detection, duplicate counts, and "≥ 24 units present" raise an error when violated.
- **Pinned `requirements.txt` without geopandas,** and `.venv`.
- **Extra tests:** the regions table covers exactly 24 units with no duplicate UIDs or names, and its border table is symmetric; the red-only setting masks only red hours; the data-quality checks raise an error on bad input.

It adds about 40 minutes to M1. In exchange, M4's API loader and all of M6 become small additions rather than rewrites.

---

# M2 — Features at t + truncation leakage test

**Goal:** one feature row per (unit, hour t), using only information known at t.

**Files:** `src/features.py`, `tests/test_features.py`, `tests/test_leakage.py`.

**Features (CLAUDE.md list)**
- Own state:
  - `minutes_since_last_end`: the last merged interval with end ≤ t.
  - `minutes_since_last_start`
  - `onsets_last_24h` and `onsets_last_7d`: merged-interval starts in (t−24h, t] and (t−7d, t].
  - `active_at_t`: kept for completeness. It is constant (0) on unmasked rows, so it carries no signal for the model.
- Spatial:
  - `neighbors_active_at_t`: the number of neighbours from `regions.py` under alert at t, using only alerts with start ≤ t and no end observed by t.
  - `national_active_count_at_t`: the number of units under alert at t.
- Calendar: `hour` and `weekday` in Europe/Kyiv, derived from the UTC t.
- `unit` as a categorical feature, with codes taken from the fixed `regions.py` table, not fitted on data.
- Recording gap: any feature whose look-back window overlaps an approved gap becomes NaN. "Time since" features become NaN if the last event could have fallen inside the gap.

**Truncation test (ts-leakage-audit):** pick 5 forecast times t from different periods, including one after the 2025 reform and one near the gap. For each t, rebuild the data as it was known at t:
- drop alerts with start > t;
- clear the end time of any alert that ended after t.

Recompute the features at t, and assert they equal the full-data features at t.

**Negative control:** a deliberately leaky feature (the duration of the current alert using its final `finished_at`, or a centred 3h window). The same checker must flag it. The test asserts that the checker fails on it.

**Other tests:**
- Hand-made examples for every feature.
- DST: the repeated and skipped local hours in Mar/Oct still give a unique UTC grid, with correct local hours.
- Neighbour counts on a 3-unit toy map.

**Prints:** feature matrix shape, NaN rate per feature, date range.

**Timebox:** 60 min.

---

# M3 — Baselines + walk-forward evaluation

**Goal:** honest baseline numbers on the final test, and the evaluation code M4 reuses.

**Files:** `src/baselines.py`, `src/evaluate.py`, `src/config.py` (splits), `tests/test_baselines.py`, `tests/test_evaluate.py`.

**Splits (config `official`)**
- Train: 2022-03-15 → 2026-06-29.
- Validation slice: 2026-06-29 → 2026-07-27, the last 4 weeks of train.
- Final test: 2026-07-27 → 2026-09-07.
- Purge at every cut-off: drop rows whose (t, t+H] window crosses the cut-off.
- Masked rows and gap rows are excluded everywhere.

**Baselines**, all scored on exactly the same rows as the model:
1. **Climatology:** a per-unit hour × weekday onset rate (Kyiv time) from train, Laplace-smoothed toward the unit's train rate (pseudo-count 10).
2. **Recent rate:** the per-unit onset rate over the 14 days before t (rolling), counted on unmasked rows only. *Rolling vs frozen is an open decision.*
3. **Raw persistence:** 1 if a merged-interval start happened in (t−H, t], otherwise 0.
4. **Calibrated persistence:** a per-unit train rate of y, binned by `minutes_since_last_end` (0–1h, 1–3h, 3–12h, >12h).

**Metrics (`evaluate.py`):**
- Brier score.
- ROC-AUC, both pooled and as the mean within-unit AUC. Units with fewer than 10 test positives are left out, and that count is reported.
- PR-AUC, and PR-AUC divided by the base rate.
- Reliability plot: 10 quantile bins.
- Everything reported overall and per group (Kyiv City / frontline / rear).

**Output:** written to `reports/<run>/metrics.json`, `metrics.csv` and plots, plus `run_meta.json` (D-017 #5).

**Optional (D-013 #6):** a week-block bootstrap with 1,000 resamples for the CI on (model − recent-rate) for Brier and PR-AUC.

**Tests:**
- Metric functions checked on hand-made cases.
- Each baseline uses only train data, or data ≤ t for the rolling one: a truncation check.
- The purge drops exactly the rows whose label window crosses a cut-off.

**Timebox:** 60 min.

---

# M4 — LightGBM + calibration + per-group results + new-regime section

**Goal:** the frozen headline model, plus the exploratory D-015 analysis.

**Files:** `src/model.py`, `src/data.py` (adds `load_api()`), `tests/test_model.py`, `tests/test_api_loader.py`.

**Model**
- LightGBM binary classifier, one pooled model on the M2 features.
- Default settings except learning rate 0.05 and up to 2,000 trees, with early stopping (100 rounds) on the validation slice.
- Then refit on train + validation with the best iteration count. *Open decision.*
- Seed fixed.

**Calibration:** check the reliability on the validation slice. If ECE > 0.02, fit Platt scaling on the early-stopping model's validation predictions. *Open decision.*

**Results:** the M3 metric table with the model added, per group. Optional: a reliability plot per group (D-013 #7).

**New regime (D-015)**
- `load_api()` reads the raw dump in `data/raw/alerts_in_ua/<stamp>/`. It removes duplicates by `id` (keeping the latest `updated_at`), keeps closed alerts only, maps UIDs through `regions.py`, applies the standing-alert rule, and returns the shared alert format with `alert_level`.
- Build the grid and features from API data only.
- **Warm-up:** the API history starts 2026-09-12. The 7-day features need 7 days of history and the recent-rate baseline needs 14, so scoring runs from 2026-09-27 → the dump date. *Open decision.*
- (a) A before/after table.
- (b) The frozen model and the baselines (climatology and calibrated persistence come from official train) scored on "any alert starts". Optional extra row: red-only (filter to red before merging; raise an error if a red-only run is attempted on official data).
- (c) Within-unit AUC and calibration-in-the-large per group.

**Optional (D-014):** weekly refit inside the test window as an extra results row.

**Tests:**
- `load_api` on a JSON fixture: duplicate ids, open alerts, unknown UIDs (must raise an error).
- The model isn't fitted on any test or API rows; this is checked from the row indices.

**Timebox:** 75 min.

---

# M5 — README, figures, Streamlit

**Files:** `README.md`, `reports/figures/`, `reports/related_work.md`, `app/streamlit_app.py`.

**README:** fills every TODO section:
- framing
- data, including the admin reform, the freeze, duplicates, the recording gap and standing alerts
- method
- the no-leakage guarantee
- results versus baselines per group
- the new-regime section and its conclusion (D-015 d)
- limitations, including the skipped items from D-013
- related work, from the web research
- status: what was finished at the deadline

**Streamlit:** reads only the saved `reports/<run>/` artifacts and the saved model. No live API calls and no token. It shows:
- per-unit probabilities for a chosen test hour;
- the metric tables;
- the reliability plots.

**Tests:** a smoke test that the app module imports, and that the artifact loader finds the files it expects.

**Timebox:** 60 min.

---

# M6 — Automated data workflow (GitHub Actions, no AI agents; D-016)

**M6a — daily fetch**
- `scripts/fetch_api.py`:
  - Reads `ALERTS_IN_UA_TOKEN` from the environment.
  - Calls UIDs 3–31 at 31 s spacing. On a 429 it retries once after 70 s; any other non-200 except the known-empty UIDs raises an error.
  - Merges into `datastore/alerts_in_ua.csv`: removes duplicates by `id` keeping the latest `updated_at`, keeps closed alerts only, sorts the rows, and changes nothing if no new alerts arrived.
  - Seeded once from today's raw dump.
- `.github/workflows/fetch_alerts.yml`: runs daily at 03:00 UTC and can also be started by hand (`workflow_dispatch`). It uses the repo secret, and commits only if the CSV changed.
- First step: one manual run, to check whether the API returns 403 to GitHub's servers. If it does, the fallback is a self-hosted runner.
- Tests: the merge on fixtures (duplicates, updates, an open alert that later closes).
- **Timebox:** 45 min. Proposed for tomorrow.

**M6b — monthly retrain + evaluation**
- `.github/workflows/retrain.yml`: runs on the 1st of each month at 04:00 UTC, installing the pinned dependencies. Steps:
  1. `pytest` (any failure means a failed run and no retrain);
  2. `run_all.py --config monthly --as-of <today>`;
  3. commit `reports/monthly/<YYYY-MM>/`.
- Config `monthly(as_of)`:
  - While there's less than 3 months of `datastore` history: the D-015 evaluation only, scoring the official-trained frozen model on the last full month. The model is retrained in CI from the run-time Vadimkin download, so no model file is committed. *Open decision.*
  - From 3 months on: train on API data only (post-reform), test = the last full month, validation = the 2 weeks before it, same pipeline and settings.
- Tests: `monthly(as_of)` date arithmetic, and the switch at 3 months.
- **Timebox:** 60 min. After M5.

---

# Open decisions (for the human, before or during implementation)

1. **D-009 standing alerts.**
   - The retrospective >24h drop uses the final `finished_at`, which is leakage (Codex M1 review).
   - Builder proposes a causal rule instead: an alert counts toward "under alert" only for its first 24h, and its start still counts as an onset.
2. **Recent-rate baseline:** rolling (builder proposes) or frozen. The human will answer separately.
3. **Purge rule** at every cut-off: confirm.
4. **D-016 points** (commit only the deduplicated CSV, fetch daily, ≥ 3 months before a yellow model): confirm.
5. **D-003 wording** is backwards: it should be "no *unmasked* hour has active_at_t == 1". The human's entry.
6. **Codex M1 review items** (reviews/M1-codex.md), not yet decided:
   - the wording "oblast-level alert starts";
   - checks raise errors only on *unexpected* duplicates or gaps; exactly 24 units;
   - interval closure `[start, end)`;
   - gap edges fixed in config;
   - red-only filtering before merging;
   - #5 (`--config`, `run_meta.json`) moved into M1;
   - extra M1 tests.
7. **Train start:** all history from 2022-03-15 (proposed) or a later start because of drift.
8. **Refit on train + validation** with the best iteration (proposed), or keep the train-only model.
9. **Calibration rule:** Platt scaling if validation ECE > 0.02 (proposed), or always, or never.
10. **New-regime scoring window:** 27 Sep → dump date, to allow the 14-day warm-up (proposed), or 20 Sep with a shorter recent-rate window.
11. **M6b in CI:** retrain the official model from the run-time download (proposed), or commit a model file.
12. **Process:** all milestones are planned here, and implementation happens in a separate chat. The milestone protocol currently says plan → approve → implement *per milestone*, so it needs an update (proposed D-019).

# Timeline
- Now: 21:40 Kyiv.
- Estimates: M1 75 min, M2 60, M3 60, M4 75, M5 60. That's about 5.5 h for M1–M5, so it won't all finish by 23:59.
- M6a: tomorrow. M6b: after M5.
- At the deadline: commit honestly whatever is finished, with a status section in the README.
