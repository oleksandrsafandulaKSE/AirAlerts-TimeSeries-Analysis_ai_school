# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results reported per group.

## D-001 — Rebuild instead of patching the v1 (previous selection round)
- Context: v1 repo https://github.com/oleksandrsafandulaKSE/AirAlerts-TimeSeries-Analysis-Ukraine
  was built in the previous selection round.
- Audit (supervisor chat flagged; I verified with the commands below) found foundation-level bugs.
- Decision: new repo, new code. Keep the ideas: onset target, masking, neighbor/national state.

## D-002 — Target collapsed after the 2025 admin reform (v1 bug)
- v1 kept only `level == 'oblast'`. Oblast-level records: 9,098 (2025 Q1) → 124 (2026 Q2);
  raion-level: 814 → 23,078. Target rate fell from ~8% to 0.25% in 2026.
- Verified by: `pd.crosstab(df.started_at.dt.to_period('Q'), df.level)`
- Decision: oblast target = union of oblast + raion + hromada intervals.

## D-003 — Masking applied to one region only (v1 bug)
- `return` inside `for region in unique_regions` in clean_grid.py.
- Evidence: 37,403 hours × 25 regions = 935,075; matrix had 933,077 → only 1,998 rows masked.
- Decision: regression test asserting no masked hour has active_at_t == 1.

## D-004 — Stale features via merge_asof on onset events (v1 bug)
- Features were computed at the region's last alert start and carried forward, so the
  "current" national/neighbor state could be days old.
- Decision: compute all state features at every grid hour t.

## D-005 — Early stopping on the test fold (v1 leakage)
- `eval_set=(X_test, y_test)` chose the number of trees using test labels.
- Decision: inner validation slice from the end of train.

## D-006 — No baselines, uncalibrated "risk %" (v1)
- Decision: climatology / recent-rate / persistence baselines; Brier + reliability plot;
  PR-AUC reported with base rate.

## D-007 — Official source froze at the yellow/red reform → Option A
- Context (source: me): from Sept 2026, alerts have two levels: yellow = drones, red = missiles.
- Builder checked (2026-10-12):
  - Vadimkin `official_data_en.csv` ends 2026-09-07 05:28 UTC (last commit 2026-09-08).
    The repo still commits daily, but only `volunteer_data_*` (oblast level, eTryvoga, no colour).
  - alerts.in.ua API: history only via `month_ago` → closed alerts from 2026-09-12 17:16 UTC.
    7–12 Sep is in neither official source. `threats[]` (drones/ballistic/...) is in live data only.
  - Kyiv City, 12 Sep–12 Oct: 202 yellow / 17 red → a red-only target is too sparse to model.
- Options: (A) train + final test on official data up to 7 Sep; new regime as a separate section.
  (B) stitch official + API/volunteer and test on the latest weeks.
- Decision (me): A. Final test = 2026-07-27 → 2026-09-07. API period 2026-09-13 → dump date
  = exploratory: base rates, yellow/red share, and the frozen model scored on "any alert" onsets.
- Why: B would mix a change of data source into every metric, and the API and the official
  file never overlap, so there's no period to line them up.
- Raw API dump for all oblasts saved to `data/raw/alerts_in_ua/` (gitignored), because the API's
  history window moves forward every day. Token in `.env` (gitignored).

## D-008 — Excluded units
- Luhanska: permanent alert since 2022-04-04 (per the dataset README) → no onset task. Excluded.
- Crimea: not in the dataset. → 24 units = 23 oblasts + Kyiv City.
- Decision (me): exclude Luhanska.

## D-009 — Standing alerts (> 24h) excluded from the oblast union
- **SUPERSEDED by D-020** (this rule used the final `finished_at`, which is leakage).
- Builder found (official data): 1,318 intervals > 24h (Dnipropetrovska 700, Donetska 471,
  Zaporizka 72, Kharkivska 26, ...); 20 > 7 days. Longest: Lypetska hromada (Kharkivska)
  604 days, 2024-05-12 → 2026-01-06; Vovchanska hromada 439 days. Some rows are duplicated.
- Problem: under the union rule (D-002), one standing hromada alert keeps the whole oblast
  "under alert" → every hour is masked → that oblast has no onsets for months.
- Options: drop > 24h / drop > 7d (still 1,298 multi-day alerts) / ignore hromada level.
- Decision (me): drop intervals > 24h from the union, and print the count removed per oblast.
- Limitation: a real alert lasting over 24h is also dropped, so its onset is lost too.

## D-010 — Exactly-30-minute durations
- 68 of 299,275 rows (0.02%), 10–20 per year: oblast 48, raion 18, hromada 2.
- Decision (me): keep. The onset time is real even if the end time was imputed. Print the count in M1.
- **Amended (M1 run, 2026-10-12):** after deduplication there are **38** such alerts (oblast 24, raion 13,
  hromada 1); 68 was the count before deduplication.

## D-011 — Frontline / rear groups
- Kyiv City alone. Frontline (8) = Chernihivska, Sumska, Kharkivska, Donetska,
  Dnipropetrovska, Zaporizka, Khersonska, Mykolaivska. Rear = the other 15, incl. Kyivska.
- Decision (me): fixed list (border/front oblasts), not data-driven, so it's easy to explain.

## D-012 — Repo root and scope
- `.git` was in the parent folder (no commits). Decision (me): `git init` inside `repo/`.
  The parent `.git` is left untouched.
- Scope (me): full M1–M5 including the Streamlit page (adds the `streamlit` dependency).

## D-013 — Best practices adopted from related work
- Source: builder's web research (about a dozen public repos plus arXiv:2411.14625), checked
  against our data where possible. Metrics in other repos are self-reported, not rerun.
- Verified by builder: 113,845 of 299,275 official rows are exact duplicates
  (`sort -u` → 185,430 unique). Recording gap: 29 Aug 88 onsets, 30 Aug–1 Sep 0 rows,
  rows resume 2 Sep (normal days have 350–600). D-009 and D-010 counts were made BEFORE
  deduplication and will be recomputed in M1.
- Adopted (me): (1) dedup first; (2) mask the 29 Aug–2 Sep gap as missing; (3) negative
  control in the leakage test; (4) calibrated persistence baseline; (5) within-oblast AUC
  next to pooled AUC.
- If time allows (me): (6) week-block bootstrap CI on the gain over recent-rate;
  (7) reliability plot per oblast group.
- Skipped (me): text/Telegram/weather features, multiple horizons, survival models,
  hyperparameter search, walk-forward retraining inside the test window. All listed as limitations.

## D-014 — Weekly refit as an extra results row
- Context: the recent-rate baseline adapts every day while the frozen model doesn't, so the
  comparison is tilted against the model. maranferij reports 0.329 frozen vs 0.416 walk-forward
  (self-reported).
- Decision (me): if time allows after M4, add weekly refit inside the test window. 6 steps, each
  trains on everything before the cut-off, early-stops on the ~2 weeks before it, official data only.
  The headline result stays the frozen model.
- Note (builder): refit steps use labels from earlier test weeks. That's legitimate (they're in the past at
  each cut-off), but the README must say the two rows use different information. Purge the
  last H hours before every cut-off.

## D-015 — What to do with the yellow zone (new-regime analysis)
- **Amended by D-021:** the (d) conclusion is conditional on the transfer results.
- Context (source: me): before Sept 2026, ANY attack (drone or missile) triggered the single
  (red) alert. Since Sept: yellow = drones, red = missiles. So "yellow or red" is the
  conceptual continuation of the old target.
- Builder found (official 27 Jul–28 Aug vs API 13 Sep–11 Oct, alerts > 24h excluded,
  onsets per month / share of time under alert):
  Kyiv City 90 → 212 / 11% → 33%; Kyivska 121 → 237 / 20% → 69%; Zhytomyrska 58 → 225 / 6% → 34%;
  Rivnenska 15 → 122; Volynska 5 → 61; frontline flat (Kharkivska 147 → 217 / 93% → 92%,
  Donetska 57 → 57). Red-only Kyiv City = 16/month. 83% of new-regime onsets start yellow;
  343 of 942 red onsets (36%) start while a yellow is active.
- Interpretation (builder, unconfirmed): same threat concept, but yellow is declared much more
  widely → the base rate jumps in the rear. Can't fully separate this from a seasonal drone
  campaign or the change of data source.
- Decision (me): (a) before/after table per oblast and group; (b) primary target = any alert
  starts, red-only as an extra row if time allows (mask = red active only); (c) within-oblast AUC +
  calibration-in-the-large; (d) README: the model needs retraining/recalibration after the
  reform, not usable as-is. No training on API data.

## D-016 — M6: automated data workflow (no AI agents)
- **Updated (me, 2026-10-12):** approved as FUTURE WORK, not tonight's scope. The yellow-regime model needs my explicit approval.
- Context (me): keep collecting new-regime data and retrain/evaluate every month automatically.
- Builder found: one full API dump is 7 MB (about 210 MB/month if dumped daily, too big for git);
  `month_ago` keeps only ~30 days → a monthly fetch would lose data whenever a run fails;
  the API docs list 403 "unavailable in your country", and GitHub's servers are mostly US-based.
- Decision (me, approving the builder's proposal — confirm): GitHub Actions.
  (1) Daily fetch → commit ONLY a deduplicated append-only CSV of closed alerts (about 2–3 MB/month);
      raw JSON stays gitignored. This is an exception to "never commit data" for that one file.
  (2) Monthly retrain + evaluation with the approved, fixed pipeline: no model search, and
      metrics are committed so the history accumulates.
  (3) Yellow-regime training starts only once >= 3 months of API history exist (about mid-Dec 2026);
      until then the monthly job produces the D-015 new-regime evaluation only.
- Order: M6a (daily fetch) right after M1 or tomorrow; M6b after M5.

## D-017 — Architecture changes so M6 fits
- Builder proposed, me approved: (1) `src/regions.py` with one table of the 24 units (names,
  API UIDs, groups, hard-coded border table → geopandas dropped); (2) one shared alert format for
  official and API data; (3) named run configs (`official` / `new_regime` / `monthly(as_of)`);
  (4) a level setting for the target (`any` / `red`); (5) machine-readable `reports/<run>/`
  output + run_meta.json; (6) data-quality checks that raise errors. Plus pinned versions, a committed
  `datastore/` folder separate from the gitignored `data/`, and pytest gating the monthly retrain.
- Why: M6 needs two sources, rolling dates and a configurable target. Retrofitting after M5
  would mean rewriting most modules; doing it in M1 costs about 40 min.
- Unchanged: target, masking, features, evaluation rules.

## D-019 — Two-level planning
- Decision (me): Level 1 (planning chat): general roadmap `plans/ROADMAP.md` + README framing →
  one Codex review (`codex-plan-review`, roadmap mode) → my corrections. Level 2 (implementation chat, per
  milestone): detailed `plans/M<n>.md` → Codex review (milestone mode) → my decisions → Claude
  implements → tests → `reviewer`. `plans/ALL.md` and its reviews are raw material for level 2.

## D-020 — Causal standing-alert rule (supersedes D-009)
- Found by: Codex (reviews/M1-codex.md, ALL-codex.md): dropping alerts whose FINAL duration is
  > 24h uses `finished_at`, which isn't known at t → leakage in the mask and the features.
- Codex (ROADMAP-codex.md): the causal fix changes the meaning of "under alert", so it must be explicit.
- Decision (me): an alert counts toward "under alert" only during its first 24h; its start is
  still an onset. Estimand: "under alert" = at least one active non-standing alert (≤ 24h).
  Hours with only standing alerts active stay in training and evaluation.

## D-021 — Evaluation protocol decisions
- Decisions (me), after the Codex roadmap review and the builder's lead judgment:
  - Recent-rate baseline is ROLLING (14 days, only labels known by t: s ≤ t−H). Recorded as an
    explicit exception to "baselines frozen".
  - Train = all history from 2022-03-15. Validation = [2026-06-29, 2026-07-27). Half-open UTC intervals.
    **Amended by D-023:** train (and the grid) start 2022-03-23 00:00.
  - No refit after early stopping. Calibration is fitted, if at all, on validation for the same model.
  - The final test is scored once, at the end of M4, for the model and all baselines together; M3 reports on
    validation only (Codex: seeing baselines on test in M3 could steer M4).
  - Primary metric = Brier skill vs recent-rate. Not beating it is a valid result.
  - The overall reliability plot is required (D-006). Measurable done-criteria in the roadmap.
  - D-015(d) is conditional: measured differences = facts, interpretations = hypotheses.
  - M6 = future work (D-016).

## D-022 — M1 data rules (Codex M1 review → me)
- Dedup on raw strings before parsing: dropped 113,845 (expected 113,845); raw rows 299,275 (measured by
  pandas `read_csv`; `wc -l` gives 299,276 incl. the header). Hard checks: the run fails on any change.
- Missing `finished_at` = end unknown → D-020 24h cap (0 rows in the official file). Zero-duration alerts:
  2 found → the start is an onset, the alert masks nothing.
- Gap: detected [2026-08-29 05:00, 2026-09-02 13:00) UTC, inside the approved [2026-08-29, 2026-09-03).
  Plus a 24h post-gap mask, because state is unknowable while an unrecorded alert could still be inside its
  first 24h. Rows masked, y = NaN. Cost: 145 test hours (3,480 grid rows). Look-back windows: M2 (D-023).
- Coverage end is fixed at 2026-09-07 05:28 (D-007), not taken from the latest timestamp in the file
  (the latest `finished_at` is 05:39).
- Base-rate check uses rows before 2026-07-27 only (no test labels before M4, D-021).
- Purge: a training row with t+H = cutoff is kept.
- Limitation: outages hitting only some units can't be detected.
- Exceptions to D-017 in M1: `monthly()` stub; no metrics.json, metrics.csv or plots.
- Evidence of causality: the truncation test catches the old D-009 mask (negative control).

## D-023 — M2 features known at t (builder → me)
- Onset = start of a merged unit interval, for both labels and features. D-020's "start still counts" means
  a standing alert's start is not dropped; it does not mean every start inside an alert counts.
- The grid and train start move to 2022-03-23 00:00, amending D-021. Reason: the file's first row is
  2022-03-15 16:10, plus 7 days for the longest look-back. New grid 938,304 rows (24 × 39,096); base rate
  before the test 0.0907 (2024 average 0.1007), base-rate check PASS.
- Features: time since the last onset and the last end (D-020 capped), onset counts over (t−24h, t] and
  (t−7d, t], neighbours under alert, national count under alert, hour and weekday in Kyiv time, unit code.
  `active_at_t` stays in the table but is not a model feature.
- Uncertainty zone [2026-08-29, 2026-09-04): windows that touch it, time-since values whose last event falls
  before its end, and state features inside it are all NaN. Before the test there are 116/117 NaN in the
  time-since features (Khersonska, no alert yet, 2022-03-23 → 03-27).
- Leakage proof: the truncation test on real data passes at about 33 times (active alert, Lypetska standing
  alert, gap edges, DST, cut-offs, times off the hour). The negative control is caught at exactly the pinned
  pairs. The reviewer's mutation tests (look-ahead from 1 minute to 1 hour) all fail the test.
- Purge rule for M3: a training row is kept if t+H ≤ cut-off.
- Open: how NaN `onsets_last_7d` is handled on test rows from 09-04 to 09-07.
