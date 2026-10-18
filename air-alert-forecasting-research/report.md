# GitHub projects and academic papers on forecasting air-raid alerts with time series: best practices

Compiled 24 items. Values marked [uncertain] are omitted; each item lists its uncertain fields at the end.

## Table of Contents

1. [Pavlyshenko & Pavlyshenko, Predictive Analytics of Air Alerts in the Russian-Ukrainian War (arXiv:2411.14625)](#pavlyshenko_2024) - Target type: Mixed state/persistence target, effectively… | Peer review status: preprint | Year: 2024
2. [Vadimkin/ukrainian-air-raid-sirens-dataset (+ issues #3-#7)](#vadimkin_dataset) - Target type: Not applicable | Peer review status: Not peer-reviewed | Year: Created 2022-03-17
3. [ceo-of-second-hand/air-raid-alerts-forecast](#cohort_ceo_of_second_hand) - Target type: Onset-style | Peer review status: student repo, self-reported claims | Year: 2026 | Popularity: 0 stars, no forks
4. [Dashulya-coder/AlertForecast](#cohort_dashulya) - Target type: State label | Peer review status: student repo, self-reported results | Year: 2026 | Popularity: 0 GitHub stars
5. [Vladislawww/air-raid-alert-forecast](#cohort_vladislawww) - Target type: onset | Peer review status: student repo | Year: 2026 | Popularity: 0 GitHub stars at time of review
6. [IvanSnezhok/air-raid-forecast-ua](#cohort_ivansnezhok) - Target type: Both, reported side by side: 'active' | Peer review status: student repo, self-reported results | Year: 2026 | Popularity: 0 GitHub stars
7. [nazar-andriievych/ukraine-air-alerts-analysis](#cohort_nazar) - Target type: STATE target, not onset: label = 1 if the ra… | Peer review status: student repo, self-reported results | Year: 2026 | Popularity: 0 stars, 0 forks
8. [Other cohort repos (Kamenqq, gklymenko, mykhailoisupov, yeliena-bochagova, endrusmah, MaksimPrykhodko)](#cohort_others) - Target type: A mix, and the mix is the lesson | Peer review status: student repos | Year: 2026 | Popularity: 0 GitHub stars on every repo except MaksimPr…
9. [Pre-2026 student repos (HliebOcheretianyi/AirAlert_predictions, TeamMLPythonAM2/AirAlarmsApp, shymanskyimarian-ux, sortafreel/dmbm)](#pre2026_student_repos) - Target type: Hlieb: STATE target | Peer review status: student repos / hobby projects | Year: Hlieb: created 2025-03-16, last commit 2025-… | Popularity: Checked 2026-10-17: Hlieb 0 stars, 0 forks
10. [alerts.in.ua API + alerts-ua/alerts-in-ua-py, PaulAnnekov/uasiren (ukrainealarm)](#api_ecosystem) - Target type: Not applicable | Peer review status: Not peer-reviewed | Year: alerts-in-ua-py: created 2023-02-06, v0.4.0… | Popularity: alerts-in-ua-py 29 stars / 3 forks
11. [Yellow/red alert reform primary documents (CabMin No.1092, ArmyInform, Euromaidan Press)](#yellow_red_reform) - Target type: Not applicable | Peer review status: Primary legal document | Year: 2026 | Popularity: Not applicable
12. [External covariate datasets (Kaggle Massive Missile Attacks, VIINA, DiXi Energy Map, time-machine-data)](#external_covariates) - Target type: Not applicable: these are covariate sources,… | Peer review status: Kaggle: self-curated dataset, not peer-revie… | Popularity: Kaggle: 138 votes, 22,592 downloads, 49,225…
13. [Beck, Katz & Tucker 1998 'Taking Time Seriously' + Carter & Signorino 2010 'Back to the Future'](#btscs_hazard) - Target type: Onset | Peer review status: peer-reviewed | Year: 1998
14. [Self-exciting point processes: Mohler et al. 2011, Lewis et al. 2012 (Iraq), Zammit-Mangion et al. 2012, Cseke et al. 2016, Euromaidan Hawkes 2024](#hawkes_conflict_crime) - Target type: Event intensity | Peer review status: peer-reviewed | Year: 2011
15. [CSEP / ETAS next-day earthquake forecast testing (Lombardi & Marzocchi 2010)](#csep_etas) - Target type: Count/onset target | Peer review status: peer-reviewed | Year: 2010 | Popularity: Crossref citations
16. [ViEWS early-warning system + 2023/24 Prediction Challenge (Hegre et al. 2025)](#views_challenge) - Target type: Count target | Peer review status: peer-reviewed | Popularity: As of 2026-10-17: Crossref 7 citations, Sema…
17. [Spatio-temporal deep models for conflict (Radford 2022 ConvLSTM, Brandt et al. 2022 ST-GCN, von der Maase 2025, DynAttn 2025)](#spatiotemporal_deep) - Target type: None of the four is a binary onset target in… | Peer review status: Radford 2022 and Brandt et al | Year: Radford 2022
18. [Gradient boosting on lag + calendar features (M5 competition lessons, LightGBM)](#gbm_lag_features) - Target type: Not an onset target in the source domain | Peer review status: peer-reviewed | Year: M5 competition ran Mar-Jun 2020
19. [Clinical event-onset prediction review (Moor et al. 2021, sepsis)](#sepsis_onset) - Target type: Onset | Peer review status: peer-reviewed | Year: 2021 | Popularity: 239 citations on Semantic Scholar
20. [Proper scoring rules + CORP reliability diagrams (Gneiting & Raftery 2007; Dimitriadis, Gneiting & Jordan 2021)](#scoring_rules_corp) - Target type: Not a forecasting application | Peer review status: peer-reviewed | Year: 2007 | Popularity: Semantic Scholar citations
21. [Time-series CV, purging & embargo (Bergmeir & Benitez 2012; Lopez de Prado 2018)](#ts_cv_purging) - Target type: Not applicable
22. [Rare-event calibration and PR-AUC vs ROC-AUC; pooled vs within-unit AUC](#rare_event_metrics) - Target type: Generic binary event | Peer review status: peer-reviewed: PLoS ONE
23. [Comparing forecasts: Diebold-Mariano, Giacomini-White, block bootstrap](#forecast_comparison_tests) - Target type: Not a forecasting application: the methods t… | Peer review status: peer-reviewed
24. [Distribution shift and online recalibration (Gupta & Ramdas 2023 Online Platt + Calibeating)](#drift_recalibration) - Target type: Not an air-alert application | Peer review status: peer-reviewed | Year: 2023 | Popularity: Semantic Scholar

---

<a id="pavlyshenko_2024"></a>
## 1. Pavlyshenko & Pavlyshenko, Predictive Analytics of Air Alerts in the Russian-Ukrainian War (arXiv:2411.14625)

*Category: ukraine_alerts* — Only academic paper forecasting UA alerts; state target, per-region RF, no baselines.

### Basic Info

**Name**

> Predictive Analytics of Air Alerts in the Russian-Ukrainian War (Pavlyshenko & Pavlyshenko, arXiv:2411.14625)

**Type**

paper

**Url**

> https://arxiv.org/abs/2411.14625 ; HTML: https://arxiv.org/html/2411.14625v1 ; DOI 10.48550/arXiv.2411.14625

**Year**

2024 (v1 submitted 21 Nov 2024; no later version found as of 2026-10-17)

**Peer review status**

preprint (arXiv cs.LG / cs.AI / cs.CY, no journal ref)

### Problem Framing

**Target type**

> Mixed state/persistence target, effectively a STATE target: label = 1 if the oblast is under alert 5 (or 15) minutes ahead, i.e. an alert starts within the window when none is active, OR an ongoing alert lasts at least 5 more minutes. Rows already under alert are included, so the label is dominated by persistence of the current state. Test positive rates (5-min horizon): Lviv 1.4%, Vinnytsia 9.1%, Kyiv oblast 19.3%, Kharkiv 55.2%. These are shares of time under alert, not onset rates.

**Target definition**

> Binary per-minute label per region: 'alert will be in the region within the next 5 minutes' (appendix: 15 minutes). The paper describes it in prose. If no alert is active, the label is 1 if an alert starts in the window. If an alert is active, the label is 1 if it lasts at least the horizon. The label is 0 if no alert starts or the alert ends within the window. H = 5 min (main) and 15 min (appendix). No target-construction code is published, and the exact shift/lag indexing is unspecified.

**Spatial unit**

> oblast. Separate models for 4 oblasts: Lvivska, Vinnytska, Kyivska, Kharkivska. Features use all oblasts plus Kyiv City.

**At risk masking**

> No. Test support is 184,316 minute rows per region, which equals every minute from 2024-07-01 to 2024-11-06 (128 days x 1440). Minutes already under alert are therefore kept in both training and scoring. Kharkiv has 101,748 positive test minutes out of 184,316, so most 'positives' are continuation of an active alert. This is the key reason the reported accuracy/AUC are inflated relative to an onset task.

### Data

**Data sources**

> Vadym Klymenko (Vadimkin) 'ukrainian-air-raid-sirens-dataset' on GitHub, resampled to a 1-minute time series from 2022-03-25 to 2024-11-06. No other sources (no ISW, Telegram, weather, launch counts) are used in the model. The intro mentions the authors' earlier Telegram/NLP alert-prediction channel, but it is not used here.

**Preprocessing**

> Each region is converted to a binary 1-minute series (1 = alert active). They also build a cumulative 'alert time' feature equal to the running duration of the current alert (0 when there is none), and calendar features. No deduplication, gap detection, admin-level union, standing-alert handling or duration-artefact handling is described. Luhansk is noted to have short coverage but is kept as a feature, where it gets zero importance.

**Known label artefacts**

> None of the known artefacts are discussed. (1) Duplicates: not mentioned. Duplicates would not change a binary 'active' series much, but they matter for onset counts. (2) Exactly-30-minute/naive end times: not mentioned. (3) Standing alerts (multi-month hromada alerts): not mentioned. They are less relevant to a 2022-2024 oblast-level series, but any raion-level rows would inflate the 'active' state. (4) Recording gaps: not mentioned. Gaps would be silently encoded as 'no alert'. (5) Luhansk permanent alert: kept as a feature, not excluded. (6) Paper-level artefacts: Fig. 20-21 (Kharkiv 5-min importance/ROC) reuse the Kyivska image files, so the Kharkiv 5-min ROC is not actually shown. Fig. 30's caption is wrong.

### Method

**Model family**

> Random Forest (scikit-learn RandomForestClassifier, n_estimators=500, random_state=15, other hyperparameters default). One model per target region. Hard-threshold predictions (predict) give accuracy/classification report. predict_proba gives ROC. No tuning and no other model families are compared.

**Features**

> (a) Binary alert-active features for all oblasts plus Kyiv City at the forecast time, described as 'lagged values'. The number of lags and the lag step are not specified, and the importance plots show one feature per region, suggesting one lag. The target region's OWN current state is included and is the top feature for Lviv (about 0.20 importance). Neighbours follow (Volynska 0.14, Ivano-Frankivska 0.13, Zakarpatska, Ternopilska, Rivnenska). (b) Cumulative current-alert duration ('alert time'/'f' features). (c) Calendar: hour, weekday, month. (d) 'ndays' = days since dataset start, a trend/time-index feature that can encode regime but extrapolates poorly. No external features.

**External feature timing**

Not applicable. No external features (ISW, Telegram, weather, launch counts) are used.

**Ablation design**

> None. There is no feature ablation, and the only interpretability evidence is RF impurity feature importances. The claims that neighbouring regions and seasonality matter rest on impurity importance only (which is biased toward high-cardinality/continuous features).

### Evaluation

**Split scheme**

> Single chronological hold-out: train = all minutes before 2024-07-01 (from 2022-03-25), test = 2024-07-01 to 2024-11-06. No validation set, no walk-forward, no refits, no purge at the cut-off. With a 5-min horizon the leak across the boundary is negligible.

**Metrics**

> Accuracy, sklearn classification report (precision/recall/F1 per class, macro/weighted averages), confusion matrix, ROC-AUC. No Brier, log loss, BSS or PR-AUC.

**Unit of metric**

> Per-region (within-oblast) metrics. Each oblast's model is scored separately on its own minute rows. No pooled metric.

**Calibration**

Not assessed. No reliability plot or calibration method. RF predict_proba is used only for ROC.

**Calibration under drift**

> Not assessed. The paper notes that 'ndays' is important for some regions, i.e. the alert pattern shifts over time. The Kyiv oblast alert-time plot shows much longer alerts from August 2024 (inside the test period), which is a visible base-rate shift between train and test. It is not quantified and there is no recalibration.

**Uncertainty of gain**

None. No CIs, bootstrap or significance tests. Single seed, single split.

**Regime coverage**

> Covers 2022-03 to 2024-11 only. The test window (Jul-Nov 2024) includes the summer/autumn-2024 increase in long drone alerts. It predates the Jan-2025 drone surge, the 2025 raion/hromada reform (Dec-2025) and the Sep-2026 yellow/red reform, so none of these shifts is covered.

### Leakage & Hygiene

**Test window hygiene**

> Single test split. No validation set, so any choices (horizon, n_estimators = 500, feature set) could only have been made by looking at the test set or not at all. No pre-registration. Model trained once per region with fixed hyperparameters.

### Reproducibility

**Code available**

> Partial. Only the train/validate function (RandomForest fit, classification report, ROC plot) is printed in Appendix A.2. There is no repository, no target/feature-construction code and no data snapshot. The paper is licensed CC BY 4.0 on arXiv. The underlying dataset is public on GitHub (Vadimkin).

### Relevance

**Takeaways for project**

> (1) This is the only academic paper found on forecasting UA alerts, and it uses a STATE target with no at-risk masking. It is the anti-example motivating our onset target plus mask ('rows already under alert are excluded', CLAUDE.md Target; leakage test asserts the mask). Its high AUCs (0.96-0.99) must not be cited as a benchmark for our onset AUC. (2) No baselines: our D-021 requirement (BSS vs rolling recent rate, plus climatology, raw and calibrated persistence) directly addresses this gap. When citing this paper we should note that persistence likely matches it. (3) The finding that neighbouring regions dominate (Lviv <- Volyn, Ivano-Frankivsk, Zakarpattia, Ternopil, Rivne) supports our neighbors_active_at_t and national_active_count_at_t features (D-017 border table in src/regions.py). Under an onset target, the useful signal is neighbours turning on while the target is still off. (4) Their 'ndays' trend feature and visibly longer alerts in the test period (Aug-Nov 2024) illustrate drift. We prefer the rolling recent-rate baseline and calibration-in-the-large checks (D-015/D-021) over a raw time index, which extrapolates out of range. (5) They do no deduplication, gap masking, standing-alert handling or admin-level union, which we do (dedup count, D-013 gap mask, D-020 causal 24h cap, union of levels). This is a methodological contrast for the README's related-work section. (6) Their minute resolution and 5-15 min horizon are a different use case (imminence) from our hourly H = 1. Our results are not comparable in scale either.

**Best practices**

> Adopt: chronological split by date rather than random rows; per-region evaluation; spatial-neighbour features; simple, interpretable models; publishing the training function. Anti-patterns to avoid: (a) a state target that includes in-alert rows, which inflates accuracy/AUC through persistence; (b) accuracy on heavily imbalanced data (Lviv 98.6% negatives gives 0.99 'accuracy'); (c) no naive baselines; (d) no probabilistic metrics (Brier/BSS, PR-AUC) and no calibration/reliability plots; (e) a single split with no validation set, so hyperparameters cannot be selected without test peeking; (f) impurity-based feature importance as the sole evidence of feature value, without ablation on the same sample; (g) an unbounded time-index feature (ndays) that the model must extrapolate in the test set; (h) no data-quality handling (duplicates, gaps, permanent alerts like Luhansk kept as features); (i) no uncertainty on results (single seed, no bootstrap); (j) unpublished label-construction code, so the horizon alignment cannot be audited; mislabeled/duplicated figures.

### Other Info

**Uncertain fields (omitted above)**

- authors
- baseline_strength
- data_source_variant
- headline_results
- leakage_handling
- popularity

---

<a id="vadimkin_dataset"></a>
## 2. Vadimkin/ukrainian-air-raid-sirens-dataset (+ issues #3-#7)

*Category: ukraine_alerts* — Our data source; Telegram-parser provenance, swapped columns, wrong durations, 2026-09-07 freeze.

### Basic Info

**Name**

> Vadimkin/ukrainian-air-raid-sirens-dataset (Dataset of air raid sirens in the Ukraine-Russia war), incl. issues #3-#7

**Type**

dataset (GitHub repo with a Telegram-parser that regenerates CSVs daily via GitHub Actions)

**Url**

> https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset ; issues: https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/issues/3 , /issues/4 , /pull/5 , /issues/6 , /issues/7 ; parser: processors/official_channel_processor.py

**Year**

> Created 2022-03-17; last repo push 2026-10-17 (volunteer files only); official_data_*.csv last commit 2026-09-08 03:44 UTC, last record started 2026-09-07 05:28:22 UTC (checked 2026-10-17)

**Authors**

> Vadym Klymenko (GitHub: Vadimkin), sole human maintainer (38 commits); github-actions[bot] (1628 'Add new data' commits); Copilot agent (3 commits, PR #5)

**Peer review status**

> Not peer-reviewed; volunteer-maintained open dataset (MIT license). Accuracy is not validated against an official ground truth; maintainer himself pointed users to the official API for 'more reliable data' (issue #3).

### Problem Framing

**Target type**

> Not applicable (dataset, not a model). Provides alert intervals (started_at, finished_at) from which either onset or state targets can be built; our project builds an ONSET target.

**Target definition**

> Not applicable. Raw unit of record = one alert interval for one location (oblast, raion or hromada) with started_at/finished_at in UTC; no horizon.

**Spatial unit**

> Mixed: oblast, raion and hromada rows (column `level`). After dedup: raion 99,304, oblast 65,314, hromada 20,812. Since Dec 2025 mostly raion-level (per datasets/README). Volunteer files are oblast-only.

**At risk masking**

> Not applicable (dataset). Note for users: the dataset records only CLOSED alerts; alerts still open at each daily run are kept in a pickle (processors/pkl/official_active_alerts.pkl) and are not in the CSV, so 'currently under alert' cannot be read from the CSV at its end edge.

### Data

**Data sources**

> Official file: parsed from the official Telegram channel t.me/air_alert_ua (Telethon client, OfficialAirAlertProcessor), records from 2022-03-15 16:10 UTC to 2026-09-07 05:28 UTC. Volunteer file: parsed from the eTryvoga Telegram channel, from 2022-02-25, oblast level only, still updating daily as of 2026-10-17. Permanent alerts in Luhansk (since 2022-04-04 16:45 UTC) and Crimea (since 2022-12-10 22:22 UTC) are NOT listed.

**Data source variant**

> Two variants: official_data_{en,uk}.csv (official channel; oblast+raion+hromada levels; columns oblast, raion, hromada, level, started_at, finished_at, source) and volunteer_data_{en,uk}.csv (eTryvoga; oblast only; has `naive` flag where finished_at = started_at + 30 min when no end message). English files are transliterations (translitua) of the Ukrainian ones; 'm. Kyiv' -> 'Kyiv City'. Snapshot used by our project: official_data_en.csv, 299,275 rows (frozen 2026-09-07).

**Preprocessing**

> Done by the dataset itself: none beyond parsing. Parser maps hashtags in the message's last line to (oblast, raion, hromada, level) via states.json + legacy_states renames + a hard-coded hromada_special_rules dict for duplicate hromada names; messages with any unknown hashtag or the 'Testovyi Region' are dropped entirely (logged, not raised). Appends to CSV in 'a' mode each daily run. Required on the user side (verified on our snapshot): exact-duplicate removal (113,845 of 299,275 rows, duplicates spread over all years 2022-2026), union of oblast/raion/hromada levels per oblast, gap masking 2026-08-30..09-01, standing-alert handling (897 alerts > 24h, 13 > 7 days after dedup), manual handling of Luhansk/Crimea permanent alerts.

### Method

**Model family**

Not applicable (dataset).

**Features**

> Not applicable (dataset). Raw fields usable for features: oblast, raion, hromada, level, started_at, finished_at (UTC). No threat type, no yellow/red level, no alert id, no update timestamp (unlike alerts.in.ua API).

**External feature timing**

> Not applicable. Publication timing note: CSVs are committed once a day (~03:40 UTC) and only contain alerts already closed, so a live system using this file sees end times with up to ~24 h delay and never sees open alerts.

**Ablation design**

Not applicable (dataset).

### Evaluation

**Split scheme**

Not applicable (dataset).

**Metrics**

Not applicable (dataset).

**Unit of metric**

Not applicable (dataset).

**Baseline strength**

Not applicable (dataset).

**Calibration**

Not applicable (dataset).

**Calibration under drift**

> Not applicable directly. Relevant drift in the data itself: the share of raion-level alerts rises sharply from Dec 2025 (admin reform), synthetic 1-h ends grow ~15x 2022->2026, and the file ends at the Sep-2026 yellow/red reform, so no post-reform official data exists in this source.

**Uncertainty of gain**

Not applicable (dataset).

**Regime coverage**

> Covers 2022-03-15 to 2026-09-07: includes the Jan-2025 drone surge period and the Dec-2025 raion-level reform, but ends at the 2026-09-06/07 yellow/red reform (no new-regime data). 7-12 Sep 2026 is missing from both this file and alerts.in.ua history.

### Leakage & Hygiene

**Leakage handling**

> Not applicable (dataset). Leakage-relevant properties for users: (a) finished_at is the FINAL end time, only known after the fact; using it to classify alerts (e.g. 'standing') at forecast time leaks (our D-020 avoids this); (b) synthetic +1 h ends are written retroactively when the next alert arrives >3 h later, so the 'end' is a fabrication created with future information; (c) daily append + duplicates mean row order is not a reliable time index; (d) no per-row publication/ingestion timestamp exists, so a true as-of-t reconstruction of what the file contained at t is impossible; the closest causal proxy is started_at <= t and finished_at <= t.

**Test window hygiene**

> Not applicable (dataset). Note: the official file can still change retroactively (e.g. PR #5 rewrote line 18 in Jan 2026), so a test window must be pinned to a dated snapshot.

### Results

**Headline results**

> Not applicable (dataset). Key verified numbers on our snapshot (2026-10-17 check): 299,275 rows; 113,845 exact duplicates; 185,430 unique rows; started_at range 2022-03-15 16:10:34 -> 2026-09-07 05:28:22 UTC; 897 alerts > 24 h; 255 exactly-1 h durations (mostly synthetic); 38 exactly-30 min; 453 < 1 min; 0 negative durations; 0 missing finished_at.

### Reproducibility

**Code available**

> Yes. MIT license. Python 3.10 + Telethon parser (process.py, processors/), GitHub Actions daily cron 00:00 UTC + on push; requires Telegram API credentials to regenerate. Maintenance: official stream broken since 2026-09-07 with open issues #6/#7 unanswered as of 2026-10-17; volunteer stream active.

### Relevance

**Takeaways for project**

> 1. Keep 'dedup first and print the count' (CLAUDE.md data rule): duplicates are 38% of rows and spread across all years, so any count before dedup is wrong. 2. Add an explicit data-quality print/flag for exactly-3600 s durations: ~235 are fabricated by the parser's 3-hour rule; they distort minutes_since_last_end and the D-020 'active' state (a real alert lasting e.g. 5 h is truncated to 1 h). Consider a test that counts them and a note in the README; do NOT silently drop them (no silent fallbacks). Changing how they are handled is a rule change for Oleksandr. 3. Onsets are undercounted where the parser overwrote unclosed alerts (<3 h rule) or dropped messages with unknown hashtags; these losses are invisible in the CSV, so the onset base rate from this source is a lower bound; state this as a limitation in README. 4. The D-010 '30-min ends' concern comes from the VOLUNTEER naive rule; in the official file the analogous artefact is the 1-hour synthetic end, so D-010 wording should reference the right mechanism. 5. Issue #3 (4-second Ivano-Frankivsk alert) and 453 sub-minute alerts: sub-minute alerts still create onsets in our target; worth a printed count and a sensitivity check (onset rate with/without < 1 min alerts). 6. Freeze at 2026-09-07 05:28 confirms D-007/D-015: the official file cannot cover the yellow/red regime; the end edge is right-censored (open alerts never written), so the last hours before 2026-09-07 05:28 should be masked or the test end kept at 2026-09-07 00:00 as now. 7. Use the dataset's oblast column for the union (D-017), but pin the snapshot: the file was edited retroactively (PR #5) and our raw download should record its git commit SHA / download date in run_meta.json. 8. Never mix with volunteer_data_* (different channel and naive-end rule), confirmed by the code.

**Best practices**

> Adopt: (a) treat community-parsed alert data as noisy: dedup, flag synthetic durations (exactly 3600 s, exactly 1800 s), flag sub-minute and > 24 h alerts, and print each count at load time; (b) record source snapshot provenance (repo commit SHA of datasets/official_data_en.csv, download date) because the file can be rewritten; (c) read the parser code before modelling: it reveals fabricated ends (+1 h after 3 h), dropped messages and right-censoring of open alerts that are not documented in the README; (d) treat the gap and the freeze as missing data, not zero alerts; (e) keep Luhansk excluded and Crimea absent. Anti-patterns: using raw row counts before dedup; computing durations or 'standing' status from final finished_at at forecast time; treating 1-h synthetic ends as real all-clears; assuming the CSV is a complete record of onsets; mixing official and volunteer files; using row order as time order; assuming the official stream continues past 2026-09-07.

### Other Info

**Uncertain fields (omitted above)**

- known_label_artefacts
- popularity

---

<a id="cohort_ceo_of_second_hand"></a>
## 3. ceo-of-second-hand/air-raid-alerts-forecast

*Category: peer_repo* — Onset 3h; BSS +10.4% vs recency; pooled AUC 0.91 vs within-oblast 0.70; purging; test seen 3x.

### Basic Info

**Name**

ceo-of-second-hand/air-raid-alerts-forecast (Air Raid Alerts in Ukraine - Time Series Forecasting)

**Type**

repo (student course project, peer cohort)

**Url**

https://github.com/ceo-of-second-hand/air-raid-alerts-forecast

**Year**

2026 (created 2026-10-12 19:00 UTC; last push 2026-10-12 20:30 UTC; 4 commits, all on 2026-10-12)

**Popularity**

0 stars, no forks; no license file (licenseInfo null) as of 2026-10-17

**Peer review status**

> student repo, self-reported claims; not peer-reviewed. We re-checked some numbers from the committed reports/final_predictions.csv.

### Problem Framing

**Target type**

> Onset-style (an alert start), but NOT at-risk masked: any raion- or oblast-level alert start in the window counts, including starts while the oblast is already under alert. So it sits between onset and state. Base rates are very high (3h: 0.37 pooled, 0.87 Kharkivska, 0.84 Dnipropetrovska, 0.82 Sumska), so frontline scores partly reflect the high activity level.

**Target definition**

> y_h(T) = 1 if at least one raion- or oblast-level alert row in oblast r starts in the hourly bins [T, T+h), where T = start of the hour and starts are floored to the hour. Main horizon h = 3 h; 1 h and 6 h also reported. A new forecast every hour. Hromada-level rows are excluded from events (mostly strike-drone threat posts). The target was chosen over daily counts and duration in d2_target_comparison.py, which scored the test period.

**Spatial unit**

oblast (24 units = 23 oblasts + Kyiv City; Luhanska and Crimea/Sevastopol excluded)

**At risk masking**

> No. Every hour of every oblast is trained on and scored ('every hour', 24,120 rows at 3 h in the test). Rows already under alert are not excluded. The 'active_at_T' feature was dropped as leaky (L37), so the model does not even know whether the oblast is under alert. This differs from our CLAUDE.md target rule (mask rows already under alert).

### Data

**Data sources**

> Vadimkin/ukrainian-air-raid-sirens-dataset official_data_en.csv (MIT; parsed from the @air_alert_ua Telegram channel), downloaded from a pinned upstream commit with SHA-256 checks. Window used: 2025-12-01 to 2026-09-06 21:00 UTC (about 9 months, the raion-level era); 7-day feature warm-up drops 1-7 Dec. Volunteer CSV used only for a cross-check (D1); alerts.in.ua API not used (future work). District boundaries from the dataset repo's ukr_admin2.geojson were used to build oblast adjacency.

**Data source variant**

> Official file only. Admin levels: union of raion + oblast rows per oblast (hromada rows dropped; no interval union because only starts are used). Snapshot: official file frozen at 2026-09-07; cut at 2026-09-06 21:00 UTC (midnight Kyiv). Training restricted to post-Dec-2025 to avoid the raion-reform definition change.

**Preprocessing**

> Exact duplicate rows dropped (about 38% of official rows), Luhansk/Crimea/Sevastopol excluded with a test, hromada level dropped, starts floored to hourly bins. No standing-alert rule: 623 alerts over 24 h left as-is (L34), which no longer matters once only start times are used. No handling of the 2026-08-30 to 09-01 recording gap: those hours are kept and scored as 'no alert start' (we checked: 0 positive labels on 30 Aug, 31 Aug and 1 Sep in final_predictions.csv, and 51/576 on 29 Aug).

**Known label artefacts**

> Documented: (1) 38% exact duplicates, removed. (2) 623 alerts lasting over 24 h (possibly missed all-clears, e.g. Synelnykivskyi raion up to 115 h), left as-is, made irrelevant by using start times only. (3) The parser closes a missing all-clear at start + 1 h without a flag when a new start comes more than 3 h later, and overwrites the first start when the new alert comes within 3 h. So some starts are lost. Listed as a limitation; cannot be fixed from the CSV. (4) Volunteer parser mis-assigns about 1/30 messages to the wrong oblast (Podilskyi -> Lviv, Prylutskyi -> Volyn). They found this by replaying the parser and rejected the volunteer file. (5) Alerts still open when the channel stopped (2026-09-07 06:09 UTC) are never written. Not handled: the 30 Aug to 1 Sep recording gap is treated as true zeros, not masked. Not discussed: exactly-30-min durations (irrelevant to start-only features).

### Method

**Model family**

> sklearn HistGradientBoostingClassifier (max_iter=300, learning_rate=0.05, region_code as categorical, seed 0), not tuned, no early stopping. Logistic regression (one-hot oblast/hour/weekday, log1p counts, scaling inside each fold) compared and rejected by a pre-registered rule (L27: prefer LR unless GBM beats it by more than 1 pp of skill). Separate models per horizon.

**Features**

> Final set (start times only, L37): region_code (categorical); own alert starts in previous 1/3/6/24/168 h (windows end strictly before T); national starts in previous 1 h and 3 h; neighbour-oblast starts in previous 1 h and 3 h (adjacency computed from raion polygons by build_adjacency.py); Kyiv-local hour of day and weekday. Dropped: active_at_T and nb_active (alerts active now, own and neighbours), because the official parser fills missing end times using later starts. They cost +4.6% Brier at 3 h in validation. Dropped by reasoning: distance to border/occupied territory (fixed per oblast, so it adds nothing beyond oblast identity). No time-since-last-start/end features. No external features.

**External feature timing**

> Not applicable: no external features. Weather explicitly rejected because only forecast weather at T would be leak-free and they had no archive of forecasts. Telegram launch reports listed as future work with the publication-before-T rule (L8).

**Ablation design**

> Yes, on the same rows. D7/D8: four variants (LR/GBM x with/without neighbours) trained on identical rows in each of the same 10 walk-forward folds, rules fixed before running (neighbours kept if they improve Brier in >= 8/10 folds; GBM only if it beats LR by more than 1 pp). Neighbours improved both models in 9/10 folds (+1.3% LR, +1.6% GBM). The end-time-feature ablation (L37) also used the same 10 folds and was adopted 'whatever it scores'.

### Evaluation

**Split scheme**

> Chronological. Walk-forward on pre-test data: 10 folds of 2 weeks each (2026-03-08 to 2026-07-26), expanding window starting 2025-12-01, minimum 12 weeks of training (first fold has 14). They planned 11 folds, an arithmetic error they disclosed. Purged by h at each cut-off, baselines refitted per fold. Final: train on everything before 2026-07-26 21:00 UTC minus h, test = last 6 weeks 2026-07-26 21:00 to 2026-09-06 21:00 UTC. No refit inside the test. No separate validation slice for early stopping (none used).

**Metrics**

> Primary: Brier skill score vs the best start-only recency rule (chosen on validation). Secondary: skill vs climatology, Brier, ROC-AUC pooled AND mean within-oblast, log-loss, accuracy@0.5 next to majority-class accuracy, calibration table and plot, weekly and per-oblast breakdowns, fold-win counts with a sign test. No PR-AUC.

**Unit of metric**

> Both: pooled AUC (0.907 at 3 h) and mean per-oblast AUC (0.699). They explicitly call pooled AUC inflated by between-oblast differences and say it is not a headline number.

**Baseline strength**

> Climatology: oblast x hour x weekday rate from train. Recency rule: a lookup P(y | oblast, any start in the last k h) fitted on train and frozen (not rolling). k picked on validation from 1/3/6 h (1h->k=3, 3h->k=6, 6h->k=6). An earlier '3h + active' variant was dropped as leaky. Hard 0/1 persistence shown only as a warning example (-63% skill). No calibrated persistence under that name, though the recency lookup is close to it. Test skill at 3 h: +10.4% vs recency, +19.2% vs climatology. Validation mean at 3 h with the final features: +3.0% vs recency, 10/10 folds.

**Calibration**

> No calibration fitted (raw GBM probabilities). Test reliability table in 10 bins plus calibration_test.png and calibration_dryrun.png. The test calibration is close to the diagonal (for example, predicted 0.036 vs observed 0.027; 0.748 vs 0.802; 0.951 vs 0.951). They slightly over-predict in the lowest bins and under-predict at 0.5-0.8.

**Calibration under drift**

> No explicit calibration-in-the-large test vs validation and no recalibration. They do report the base rate per split (3 h test base rate 0.369). The validation-vs-test gap in skill (+3.0% vs +10.4%) is discussed. They do not check the new yellow/red regime after 2026-09-07 at all.

**Uncertainty of gain**

> No CI or DM test. Uncertainty is shown by fold/week counts: 10/10 validation folds won (sign test p = 0.001 claimed; they note it is approximate because neighbouring folds are correlated), 6/6 test weeks won, and the min/max fold skill (+0.7% to +9.3% in the earlier walk-forward). They state that a realistic gain lies between the validation +3.0% and the test +10.4%.

**Regime coverage**

> Narrow. Only post-Dec-2025 (raion-level) data, so the Dec-2025 raion reform is avoided rather than spanned, and the Jan-2025 drone surge is outside the data. The Sep-2026 yellow/red regime is not evaluated (data ends 2026-09-06). Listed as future work: alerts.in.ua API as a prospective test.

### Leakage & Hygiene

**Leakage handling**

> Strong for a 1-day project. (1) All counts use starts strictly before T (shift(1)). (2) Purging: training rows with hour < cutoff - h, asserted in code and in a pytest test over every fold, the dry run and the final split. (3) Truncation test: delete every alert starting at or after T0 and push later end times later, then check features at hours <= T0 are unchanged. No negative control (no deliberately leaky feature that the test must catch). (4) An independent review (H1) found that end-time features leak because the official parser imputes missing ends from future starts, so active_at_T/nb_active were removed and the recency opponent was made start-only too. Climatology and lookups are fitted on train only, and the LR scaler is fitted inside the pipeline. Missed: the recording gap is scored as true zeros (a data-validity problem, not a leak, but it inflates the result; see headline_results). Also, the hour-floored label [T, T+h) and features from bins < T are consistent, but there is no masking for the oblast already being under alert.

**Test window hygiene**

> Weak by their own disclosure. The test period was looked at 3 times before the final run: #1 target selection (d2_target_comparison.py scored the test, and the 3 h target was chosen with test results), #2 adding recency baselines on test (+9%), and #4 a re-run for report text. Then the final run #8, with a lock file reports/.test_scored and a --rerun-reason guard. experiments.md logs every look. Model choice, features and the recency k were frozen on validation before #8, and the #8 log entry was written before metrics were computed. d2 script now refuses to run without --i-know-this-scores-the-test-period.

### Reproducibility

**Code available**

> Yes, public on GitHub, no license file. Python 3.12, pinned requirements (numpy 2.4.6, pandas 3.0.3, scikit-learn 1.8.0, shapely, matplotlib, pytest). Scripts chain-import each other (no shared module yet, so the final model depends on the frozen d2 script). Data downloaded by script from a pinned upstream commit with SHA-256 checks. Predictions CSV and reports committed. A one-day project, not maintained after 2026-10-12.

### Relevance

**Takeaways for project**

> 1) The recording gap really matters (supports our D-013 masking): in this peer's test, 3 unmasked gap days inflate the headline 3 h BSS from about +5.8% to +10.4% and week-6 skill from about +6% to +26%. We must keep masking the gap and features that read across it (D-013), and mention this peer result in the README as outside evidence. 2) Their lack of at-risk masking plus raion-level starts gives base rates of 0.8-0.9 in frontline oblasts. With our mask (D-020 causal rule) the base rates and skills are not comparable to theirs; compare only qualitatively. 3) The pooled vs within-oblast AUC gap (0.91 vs 0.70; validation 0.88 vs 0.66) matches our rule of reporting both. Expect within-oblast AUC around 0.65-0.70 to be a realistic range. 4) A frozen recency lookup is a weaker opponent than our rolling 14-day recency (D-021). Their +10% gain over a frozen lookup does not mean the same over our rolling, shrunken baseline. 5) Their L37 finding: official end times are imputed using future starts (missing all-clear closed at start + 1 h when the next start comes more than 3 h later). This is a concrete leakage risk for our minutes_since_last_end and active_at_t features. Our D-020 24h causal cap does not fix imputed ends, so we should check whether our end-time features carry this leak, or at least name it as a limitation. 6) Their validation-vs-test gap (+3.0% vs +10.4%) suggests reporting the validation skill next to the test skill, plus our week-block bootstrap CI (D-013), to avoid over-reading one 6-week window. 7) Western low-rate oblasts are where the GBM loses to recency. Expect the same in our rear group and report per group. 8) Their test was seen 3 times before the final run. Our protocol of scoring it once at M4 (CLAUDE.md) is stricter; keep the lock-file idea (a .test_scored guard with a --rerun-reason) as cheap hygiene.

**Best practices**

> Adopt: a pre-registered decision rule before each experiment (fold-win thresholds, an LR-vs-GBM margin, 'adopt whatever it scores' for the leak fix); experiments.md logging every look at the test; a lock file plus a rerun-reason guard on the test-scoring script; a dry run of the final code path on the last validation fold that must reproduce the validation number exactly; making the baseline leak-free too when a leaky feature is removed from the model; reporting within-oblast AUC and calling pooled AUC inflated; per-oblast and per-week tables; replaying the upstream parser on raw channel messages to check label quality; data pinned to an upstream commit with SHA-256; disclosing arithmetic errors instead of fixing them silently. Avoid: choosing the target on the test period; scoring a recording gap as true zeros; no at-risk masking (it mixes 'already active' persistence with onset skill); a frozen rather than rolling recency opponent; a truncation test without a negative control; chained script imports instead of a shared module; a sign test on correlated folds presented with a precise p-value; no CI on the skill gain; and no check after the regime change.

### Other Info

**Uncertain fields (omitted above)**

- authors
- headline_results

---

<a id="cohort_dashulya"></a>
## 4. Dashulya-coder/AlertForecast

*Category: peer_repo* — Kyiv-only; naive 30-min flag leak inflates persistence PR-AUC; planted-leak tests.

### Basic Info

**Name**

Dashulya-coder/AlertForecast

**Type**

repo (student / cohort peer project, same course)

**Url**

https://github.com/Dashulya-coder/AlertForecast

**Year**

2026 (created 2026-10-12, last push 2026-10-12 20:54 UTC, at the 12 Oct deadline; 17 commits)

**Authors**

Dashulya-coder (GitHub handle, single author)

**Popularity**

0 GitHub stars (checked 2026-10-17); no license file

**Peer review status**

student repo, self-reported results; not peer reviewed

### Problem Framing

**Target type**

> State label ('an alert is active at any moment in (t, t+h]'), reported in two views: (a) all origins, which the author calls inflated by ongoing alerts; (b) 'Kyiv clear at t' in the real-time state, which is the headline. Because clear-at-t is defined in the real-time state, view (b) works out to an onset target, which is directly comparable to ours.

**Target definition**

> y(t) = 1 if Kyiv City has an alert active at any moment in (t, t+h], half-open alerts [start, end), and an alert starting exactly at t+h counts. Origins every 30 minutes (UTC). Horizons h in {1, 3, 6} hours, one model per horizon. Headline = view (b), origins where Kyiv is clear at t as known at t.

**Spatial unit**

> city: Kyiv City only (not Kyivska oblast). Other oblasts are used only as candidate neighbour features.

**At risk masking**

> Partly. Rows are not dropped from training (the GBM is fit on all purged rows, both views), but scoring is reported separately on the clear-at-t subset, and that subset is the headline. The logistic baseline is fit on clear-at-t rows only. 'Clear' uses the real-time state, in which a naive alert stays open until the next activation, so the 'naive shadow' does not count as clear.

### Data

**Data sources**

> Vadimkin/ukrainian-air-raid-sirens-dataset, volunteer file volunteer_data_en.csv (eTryvoga Telegram channel), snapshot 2026-10-12 05:05 UTC. Train 2022-03 to 2026-08-16, validation 2026-08-17..09-13, test 2026-09-14..10-11 (28 days, Kyiv-local days). The official file was rejected because it stops 2026-09-07 and has a feed failure from 30 Aug to 1 Sep. The alerts.in.ua API cross-check was deferred and never done.

**Data source variant**

> volunteer file (NOT official, NOT API); oblast-level only (the volunteer file has no raion/hromada level, so no admin-level union). Snapshot 2026-10-12 05:05 UTC. The author measured large disagreement between sources over 28 days (2026-08-09..09-06): only 32% of alert-minutes overlap, and about 20% of 30-min origins get a different label, partly because of the official outage.

**Known label artefacts**

> (1) Naive / 30-min ends: the main finding. The volunteer processor (volunteer_etryvoga_processor.py) writes naive=True with end = start + 30 min ONLY when the region's next activation comes more than 3h later. A next activation within 3h overwrites the open alert. Check: 0 of 5,828 naive alerts have a next start within 3h (minimum gap exactly 3.000h), against 45.6% of non-naive alerts; only 43 of 110,340 non-naive alerts last exactly 1800s. So a 30-min duration leaks 'no alert for >= 3h'. Fix: features and clear-at-t state use the real-time view; dataset ends are used for labels only; naive, dataset durations and dataset ends are banned as features. Effect: validation persistence PR-AUC at 1h fell from 0.55 to 0.31, and the neighbour-region lift fell from up to 3.1x to 1.9-2.3x. The naive share rose from 6% in train to 28% of test alerts. A sensitivity run that excludes origins touching naive alerts leaves the conclusion unchanged. (2) Late starts: when an open alert is overwritten by a new activation within 3h, the earlier start is lost, so start times can be late. Acknowledged, not fixed. (3) Missing open alerts at the snapshot: handled with the completeness cutoff. (4) Official-file gap (30 Aug to 1 Sep) and duplicates: avoided by not using the official file. (5) Standing alerts / admin reform: not addressed (volunteer file is oblast-level).

### Method

**Model family**

> scikit-learn HistGradientBoostingClassifier, fixed hyperparameters (no tuning, no random early stopping), one model per horizon. Baselines: persistence, hour climatology, hour x weekday climatology, a 'recent activity' logistic regression (frac_alert_24h, log1p(n_starts_24h)), and a diagnostic constant set to the evaluation window's own rate. No calibrator adopted.

**Features**

> All from the real-time state, clipped at t: Kyiv-local hour and weekday; alert open at t and open age; time since last start and last end; alert counts over 1/3/6/24h; share of time under alert over 6/24h. Rejected after pre-registered tests: recent-rate features (neutral), recency weighting (significantly worse log loss), neighbour-region alerts (Stage C: a hint at 1h only, within noise; the lift was 1.9-2.3x for Volynska, Rivnenska, Cherkaska, Zhytomyrska; Kyivska oblast lift was 0.83; national count gave no lift until 11+ regions were active). No external features (Telegram and news were skipped).

**External feature timing**

Not applicable: no external features used (Telegram/news phase skipped and listed as a limitation).

**Ablation design**

> Yes, and it is strong. Each feature or recipe change (Stage A recency weighting and recent-rate group, 8 configs; Stage B calibrators; Stage C neighbours; final GBM vs logistic) is compared on the same three 28-day windows (val 2026-08-17..09-13, w1 07-20..08-16, w2 06-22..07-19), each fit strictly before the window with the same purge, using paired multi-window day-block bootstrap CIs. Adoption rules were written into CLAUDE.md before running and applied as written.

### Evaluation

**Split scheme**

> Chronological, Kyiv-local days. Train before 2026-08-17; validation 2026-08-17..09-13; test 2026-09-14..10-11. Method selection on three rolling 28-day windows (val, w1, w2), each refit before the window. For the test: refit on train+val (strict purge), no refit during the 28 test days. Strict per-horizon purge: a fit row is kept only if t + h < the first evaluation origin. Test lock: allow_test=True flag plus a marker file (.test_run_done) that refuses a second run.

**Metrics**

> PR-AUC (with base rate), Brier, Brier skill score vs climatology, log loss, precision/recall at frozen thresholds (recall targets 0.5/0.8/0.9, thresholds from pooled out-of-time predictions of the 3 blocks before the window), reliability curves, weekly calibration drift (mean prediction / observed rate). No ROC-AUC.

**Unit of metric**

single unit (Kyiv City), so pooled = within-unit; no cross-unit aggregation.

**Baseline strength**

> Persistence (real-time state), hour climatology, hour x weekday climatology, recent-activity logistic (24h activity), and a non-deployable constant at the test rate. No rolling recent-rate or calibrated-persistence baseline in our sense; the recent-activity logistic is the closest to our recent-rate bar. Test result (view b): the GBM beats climatology on Brier (1h -0.014 [-0.028, -0.004], 3h -0.079, 6h -0.146; significant) but NOT on PR-AUC. Not significantly different from the logistic baseline at any horizon. Significantly worse than a constant at the test rate (Brier +0.013 / +0.071 / +0.105). On validation the recent-activity logistic already had the best Brier among baselines.

**Calibration**

> Reliability curves on the test (figure reports/figures/test_reliability.png) in both views. Calibration candidates (none, intercept shift, Platt, Platt with recency weights 1/0.5/0.25; isotonic excluded on purpose for about 4,000 clustered rows) fitted on pooled out-of-time predictions from K=3 28-day blocks before each window. None qualified under the pre-registered rule; intercept shift was a near miss (better at 3h/6h, worse at 1h). The final model is uncalibrated.

**Calibration under drift**

> Explicitly measured. Weekly calibration-in-the-large on the test: mean prediction / observed rate 0.55-0.88 at 1h, 0.53-0.80 at 3h, 0.59-0.78 at 6h, so the model under-predicts in every test week. Base rate shifted from 1.5 Kyiv alerts/day (train) to 4.5 (val) and 4.6 (test). On validation the base model was at 0.63-0.67, and recency weighting made it worse (0.38-0.55) because it followed the quieter pre-surge regime. Frozen thresholds also failed to transfer: achieved recall was 0.89-0.99 against targets 0.8/0.9.

**Uncertainty of gain**

> Yes: day-block bootstrap (1,000 resamples for the test; 300 resamples, seed 0, for multi-window selection), 95% CIs on metrics and on paired differences (GBM minus climatology, logistic, constant). No DM test. The author notes that days are treated as independent blocks.

### Leakage & Hygiene

**Test window hygiene**

> Very good. Test split locked in code (allow_test flag); a marker file stops a second run; a validation dry run of the full test script was done first. Rules for every choice (Stages A-C and final model GBM vs logistic) were pre-registered in CLAUDE.md before running and applied as written, including a rule set by the user before the run. Test evaluated once. Provenance: commit 15b25a3 plus uncommitted changes, recorded with a code hash in reports/.test_run_done, which the author admits is weak provenance. Several corrections are logged in CLAUDE.md (for example the completeness claim and the base rates redone after the naive fix).

### Results

**Headline results**

> A null result, reported honestly. Test view (b), Kyiv clear at t, n=776/776/770: GBM PR-AUC 0.232 [0.170, 0.311] vs base rate 0.227 (1h); 0.551 vs 0.553 (3h); 0.784 vs 0.791 (6h). So there is no ranking skill above the base rate. Brier 0.188/0.318/0.270, better than climatology (significant) but worse than a constant at the test rate (0.175/0.247/0.165). GBM vs logistic baseline: no significant difference. Precision at frozen recall-0.8 thresholds is within 0.007 of the base rate. View (a), all origins: PR-AUC 0.555/0.667/0.845 vs base 0.284/0.576/0.807 and persistence 0.327/0.590/0.817; most of the gain comes from knowing an alert is open. Validation persistence PR-AUC at 1h was inflated from 0.31 to 0.55 by the naive leak before the fix. Naive-excluded sensitivity: 1h PR-AUC 0.191 vs base 0.185; conclusion unchanged.

### Relevance

**Takeaways for project**

> (1) The naive / 30-min end artefact is a LEAK in the volunteer file, not just noise: the 30-min end is written only when no new alert follows within 3h. We use the official file and KEEP the 38 exactly-30-minute durations (D-010). We should state in the README that the official file is a different channel (the leak mechanism is the volunteer processor's), and ideally run a quick check of the same signature on the official data: next-start gap after a 30-min alert, minimum gap, against the other alerts. If the official 30-min alerts also never have a next start within some window, then minutes_since_last_end can leak through them and D-010 should be revisited (needs the human's approval). (2) Persistence inflated by state leakage: their validation persistence PR-AUC went from 0.55 to 0.31 once the leak was removed. This supports our onset target + at-risk masking and our D-020 causal 24h cap (also a 'what is known at t' state rule). (3) Their perturb-the-future test with a cutoff placed INSIDE a running alert, plus a 'has teeth' check, is a good model for our tests/test_leakage.py negative control (CLAUDE.md requires one). Adopt the 'cutoff inside a running alert' case explicitly. (4) Under-prediction in every test week, after a base-rate tripling, is likely in our new-regime check (D-015 (b)/(c)). Their result supports our rolling recent-rate as the main bar (D-021), and supports reporting calibration-in-the-large per group. (5) Their logistic on 24h activity equalled the GBM: we should expect that the recent-rate baseline may not be beaten (a valid result under our rules). (6) Pre-registered adoption rules with paired block-bootstrap CIs across several windows are a cheap way to make ablations honest; this matches our D-013 week-block bootstrap. (7) The completeness cutoff (closed alerts only) matters for the D-027 API merge rule and M6: open alerts must be kept or the end of the window treated as incomplete.

**Best practices**

> Adopt: a real-time state view separate from the label view (features never read dataset end times that are not yet observed at t); perturb-the-future tests with dense and sparse seeds and a cutoff inside an open alert; negative controls that prove the test catches a planted leak; strict per-horizon purge with a boundary-row test; a code-level test lock plus a one-shot marker file; pre-registered decision rules written before running; selection on several windows from different regimes, not one validation slice; paired day/week-block bootstrap CIs on differences; weekly calibration-in-the-large drift plots; a non-deployable 'constant at the test rate' diagnostic to show how much of the Brier score is level error; reporting the null result plainly; a completeness cutoff for snapshot data. Anti-patterns or weaknesses to avoid: a state label with an all-origins view (inflated; the author reports it only as secondary); thresholds frozen from quieter periods (did not transfer); a single unit (Kyiv only), so wide CIs and no cross-unit pooling; a test run on a commit plus uncommitted changes (weak provenance); depending on a volunteer source with an imputed-end artefact; no ROC-AUC reported.

### Other Info

**Uncertain fields (omitted above)**

- code_available
- leakage_handling
- preprocessing
- regime_coverage

---

<a id="cohort_vladislawww"></a>
## 5. Vladislawww/air-raid-alert-forecast

*Category: peer_repo* — RF + Platt; base-rate shift 6% -> 10.6% caused under-prediction on test.

### Basic Info

**Name**

Vladislawww/air-raid-alert-forecast (Air Raid Alert Forecast, Kyiv)

**Type**

repo (student / cohort peer project)

**Url**

https://github.com/Vladislawww/air-raid-alert-forecast

**Year**

2026 (repo created 2026-10-11, single commit 00e7e77 on 2026-10-12, the cohort deadline day)

**Authors**

Vladislawww (commit author 'Vlad'); README states it was built in dialogue with Claude and Gemini

**Popularity**

0 GitHub stars at time of review (2026-10-17); no license file

**Peer review status**

student repo; all numbers self-reported, not independently reproduced here (data not shipped)

### Problem Framing

**Target type**

> onset (new start). The README explicitly documents switching away from a trivial 'is there an alert' state target to 'will a new alert start'.

**Target definition**

> For each UTC hour t where Kyiv city is not under alert, y(t)=1 if at least one merged Kyiv-city alert interval starts in (t, t+1h]. H=1 (constant in main.py). Grid runs from the first Kyiv alert to floor(max finished_at) - H.

**Spatial unit**

> city: Kyiv City (oblast value 'm. Kyiv' in official_data_uk.csv) only; other oblasts are used only as features

**At risk masking**

> Yes. Hours where Kyiv is active at t (merged interval start <= t < finish) are dropped from training, validation and test ('eligible' rows). No explicit unit test asserts this; it is a single filter in pipeline.load_eligible().

### Data

**Data sources**

> Vadimkin/ukrainian-air-raid-sirens-dataset, official_data_uk.csv (Ukrainian-name variant), 2022-03-15 to 2026-09-07; model trained only on data from 2024-01-01. An exploratory script (build_combined.py) tried to append JustJimer/ukraine-air-alert-stats archive/alerts_in_ua.csv after 2026-09-07, but the author did not use it for the final model.

**Data source variant**

> Official channel (Ukrainian-language file), not volunteer data. Admin levels: all rows sharing the 'oblast' column value are unioned via merge_intervals (so for other oblasts raion/hromada alerts are included in the union; for Kyiv City only city-level rows exist). Snapshot ends 2026-09-07 (frozen at the yellow/red reform). The unused alerts.in.ua stitch kept only alert_type == air_raid and excluded Crimea and Luhanska.

**Preprocessing**

> Per-region dedup on (started_at, finished_at) (not full-row dedup); Kyiv: 4141 records -> 2267 unique alerts (README says pre-2026 alerts were all doubled, found from even monthly counts). Overlapping intervals merged into a union per region. No gap handling: the 2026-08-30 to 09-01 recording gap falls inside the test window and its hours are treated as 'no alert' eligible negatives. No standing-alert handling for neighbour features (multi-month hromada alerts would keep e.g. Kharkivska act flag permanently 1). Luhanska is NOT excluded in the final pipeline (only in the unused stitching script). Calendar in Europe/Kyiv; everything else UTC.

**Known label artefacts**

> Duplicates: handled (dedup on start/finish pair per oblast; diagnose.py counts extra copies by year). Recording gap 30 Aug - 1 Sep 2026 (and partial 29 Aug / 2 Sep): NOT handled; hours counted as unmasked negatives inside the test, slightly depressing the test base rate and biasing Brier/PR-AUC. Standing alerts (439-604 day hromada alerts): NOT handled; affects neighbour 'act_o*' and 'n_active_oblasts' features rather than the Kyiv target. Exactly-30-minute ('naive') durations: not discussed; they enter kyiv_last_dur_h and the merged intervals unchanged. Luhanska permanent alert: kept as a near-constant feature. Swapped columns: not discussed. In build_combined.py open alerts older than 1 day at snapshot time were dropped as occupied-territory standing alerts and fresh open alerts closed at snapshot time (uses snapshot time, not causal), but that file was not used for the model.

### Method

**Model family**

> Random Forest (sklearn, 300 trees, min_samples_leaf=30, max_features='sqrt') + Platt scaling (logistic regression on logit(p), C=1e6). Compared in walk-forward against logistic regression, LightGBM and HistGradientBoosting (compare_models.py). NOTE: the README 'How it works' section and final_eval.py print labels still say 'LightGBM', but pipeline.make_model() returns a RandomForestClassifier and the results table says 'Random Forest + Platt' - documentation inconsistency.

**Features**

> Kyiv own history: alert starts in last 1/3/6/24/72 h (windows (t-w, t]), hours since last merged alert ended (capped at 720 h), duration of the last finished alert. Spatial: for EVERY other oblast (about 25 incl. Kyivska and Luhanska), binary active-at-t flag and count of starts in the last hour (~50 columns, no border table); n_active_oblasts count. Calendar (Kyiv local): hour, day of week, hour_sin, hour_cos; 'month' built but dropped after walk-forward ablation (risk of memorising months). No external features (no ISW, Telegram, weather, launches).

**External feature timing**

Not applicable - no external features used. All features come from the alert log itself.

**Ablation design**

> Yes, on the same sample: evaluate_folds.py and compare_models.py evaluate all variants (constant, hour, Kyiv-oblast-only, logistic regression, LightGBM with/without month, RF, HGB) on identical 6 walk-forward 2-month windows before the test, with identical training data starting 2024-01-01. Training-start choice (2022-03 / 2023-07 / 2024-01 / 2024-07) compared only with naive baselines on a 2-month validation window (baseline.py); the author admits differences were within noise.

### Evaluation

**Split scheme**

> Chronological by date. Test = last 2 months: from eligible.index.max() - 2 months, i.e. ~2026-07-07 to 2026-09-07 (1346 eligible hours, 143 onsets). Model selection: 6 consecutive 2-month walk-forward windows before the test (~2025-07 to 2026-07), each trained on 2024-01-01 up to the window start minus a 1-hour gap (expanding window). Final model: one fit on 2024-01-01 to test start minus 1 h; no refit inside test.

**Metrics**

> PR-AUC (average precision), lift = PR-AUC / base rate, Brier, log loss, mean predicted probability, top-k% capture and precision (top 5/10/20%), 5-bin quantile reliability table. No ROC-AUC, no Brier skill score reported explicitly.

**Unit of metric**

Single unit (Kyiv City), so pooled = within-unit; not comparable to multi-oblast pooled AUCs.

**Calibration**

> Platt scaling fitted on pooled out-of-fold predictions from the 6 walk-forward windows (fold models), then applied to a DIFFERENT final model trained on all pre-test data (calibrator/model mismatch). calibrate.py compared Platt vs isotonic by fitting on folds 1-4 and evaluating on folds 5-6; README says raw RF probabilities were ~25% too high on validation. Reliability shown only as a 5-quantile-bin table (no plot).

**Calibration under drift**

> Explicitly reported failure: the base rate rose from ~6% (train) to 10.6% (test), and the calibrated model under-predicts on test (e.g. top quintile predicted 13.5% vs 19.8% observed). Mean prediction printed for each model, which is effectively calibration-in-the-large, but no recalibration on recent data was done; the author recommends recalibrating on fresh data and frames output as a relative-risk indicator.

**Uncertainty of gain**

> None. No bootstrap, no DM test; README only notes 'few events (143 positives), all numbers approximate'.

**Regime coverage**

> Training 2024-01 onward spans the Jan-2025 drone surge and the Dec-2025 raion reform (the latter barely matters for a Kyiv-City target, but affects neighbour union features). Test (Jul-Sep 2026) ends at the Sep-2026 yellow/red reform; the new regime is not evaluated. The 6% -> 10.6% base-rate shift within the official data is itself a regime shift the model did not adapt to.

### Leakage & Hygiene

**Leakage handling**

> Causal features: active/start counts use searchsorted with start <= t; 'hours since end' only uses intervals with finish <= t. Truncation test (test_no_leakage.py, a script not a pytest test): 25 random hours since 2024, data truncated to started_at <= t and future finish times replaced by t+365d, features recomputed and compared -> 0 differences. No negative control (no deliberately leaky feature shown to be caught). Purge: 1-hour GAP between train end and each validation/test start, correct for H=1. Missed: (1) recording gap not masked; (2) Platt calibrator fitted on fold-model predictions applied to a different final model; (3) predict.py reports a probability even if t is during the training period (only warns); (4) data_end = max finished_at, a statistic over the whole file used to set the grid end (benign); (5) standing alerts in neighbour features are not causally capped, but that is noise, not leakage, since the truncation test maps open alerts to 'still active'.

### Results

**Headline results**

> Test (2026-07-07 to 09-07, 1346 eligible hours, 143 onsets, base rate 10.6%): RF + Platt PR-AUC 0.247 (lift 2.33), Brier 0.0918; constant 0.106 / 1.00 / 0.0971; hour of day 0.131 / 1.24 / 0.0966; 'Kyiv oblast active' 0.146 / 1.37 / 0.0938. Top 10% riskiest hours capture 26.6% of onsets, top 20% capture 38.5%; top-5% precision 36.8% (3.5x base). Beats all included naive baselines on ranking and Brier, but the Brier gain is small (BSS ~0.02 vs the best baseline) and no rolling recent-rate baseline was tried. Walk-forward validation suggested ~3x lift; test is lower. Probabilities are under-calibrated on test due to the base-rate shift. README is internally inconsistent: headline sentence says ~1.8x, table says 2.33x.

### Reproducibility

**Code available**

> Yes: ~870 lines of Python in a flat layout (main, features, pipeline, final_eval, predict, research scripts) plus a committed model artifact (artifacts/model.joblib). Data not included; user downloads official_data_uk.csv manually. requirements.txt is unpinned (pandas, numpy, scikit-learn, lightgbm, joblib), no Python version, no license, no tests framework (leakage check is a script). Single commit; comments and outputs in Ukrainian. Not maintained after the deadline.

### Relevance

**Takeaways for project**

> 1) Strong evidence for our D-021 rule that the ROLLING recent-rate baseline is the main bar: their frozen constant baseline used the ~6% train rate against a 10.6% test rate, so 'beating the constant' overstates skill; we must report BSS vs rolling recent rate. 2) Same failure mode we expect in the D-015 new-regime check: a frozen Platt calibrator under-predicts when the base rate shifts; our calibration-in-the-large row (mean predicted vs observed) per group is the right diagnostic, and we should show it on the official test too. 3) Fit any calibrator on validation predictions of the SAME frozen model (D-021), not on OOF predictions of different fold models. 4) Mask the 30 Aug - 1 Sep recording gap (D-013): their test silently includes it as negatives. 5) Neighbour features without the D-020 24h standing cap become constant flags (Kharkivska/Luhanska); keep the cap and exclude Luhanska. 6) Use a border table (D-017) rather than ~50 per-oblast columns, which overfit on a single target unit. 7) Their truncation test is a good template but lacks the negative control our tests/test_leakage.py requires. 8) Their 1h purge gap matches our purge rule for H=1. 9) Peer comparison caution: their metrics are for one city, so PR-AUC/lift are not comparable with our pooled 24-unit numbers; compare with our Kyiv City row only. 10) Top-k capture tables are an intuitive add-on for the README/app (M5).

**Best practices**

> Adopt: onset target with at-risk masking; dedup before counting (they rediscovered the duplicate issue); identical walk-forward windows for all model/feature ablations; dropping features that can memorise time (month); truncation-based leakage check; honest Limitations section reporting under-calibration and validation-vs-test optimism; lift = PR-AUC / base rate as an interpretable secondary metric; top-k% capture tables. Avoid: stale train-mean constant as the only no-skill reference; calibrator fitted on a different model than the one deployed; no CI on the gain with only 143 positives; documentation drift (LightGBM vs RF, 1.8x vs 2.33x); unpinned requirements; leakage check as an ad-hoc script instead of a CI test; ignoring the recording gap; un-capped standing alerts in spatial features; choosing the training start by reasoning when validation differences are within noise without saying so up front (they did say so - good).

### Other Info

**Uncertain fields (omitted above)**

- baseline_strength
- test_window_hygiene

---

<a id="cohort_ivansnezhok"></a>
## 6. IvanSnezhok/air-raid-forecast-ua

*Category: peer_repo* — Learned region lead-lag; Telegram/news ablation with time-fair baseline.

### Basic Info

**Name**

IvanSnezhok/air-raid-forecast-ua

**Type**

> repo (student / cohort peer project, same course), with a live GitHub Actions pipeline, a GitHub Pages / FastAPI web app, and a separate raion-level layer

**Url**

> https://github.com/IvanSnezhok/air-raid-forecast-ua (site: https://ivansnezhok.github.io/air-raid-forecast-ua/)

**Year**

> 2026 (created 2026-10-11, last push 2026-10-17, i.e. work continued after the 12 Oct deadline; about 126 commits)

**Authors**

> IvanSnezhok (single human author); 'claude' is listed as a co-contributor (AI-assisted, several parallel Claude threads per docs/PROCESS_uk.md)

**Popularity**

0 GitHub stars (checked 2026-10-17); no license file

**Peer review status**

student repo, self-reported results; not peer reviewed

### Problem Framing

**Target type**

> Both, reported side by side: 'active' (state: alert active at any moment of hour T+h) and 'onset' (a new alert starts within [T, T+h)). The author explicitly says the active target is inflated by running alerts and added onset after reviewing related work. However the onset target is NOT restricted to rows clear at T, so it is a hybrid: in the volunteer file any new 'alert' post restarts the oblast alert, so an 'onset' can occur while an alert is running.

**Target definition**

> Origins at top of hour T (UTC; live pipeline also at any minute, every 10 min). Horizons h in {1, 2, 3, 6} hours, one model per target and horizon. active_h: region has an alert at any moment of [T+(h-1)h, T+h h). onset_h: max of hourly alert-start indicators over [T, T+h) (src/airraid/features.py labels()). Labels NaN beyond the data end. Test base rates: active 33%; onset 23% / 39% / 50% / 67% for h = 1/2/3/6.

**Spatial unit**

> oblast (23 oblasts + Kyiv City = 24 units, Luhansk excluded); a separate raion layer forecasts 119 units (118 raions + Kyiv City)

### Data

**Data sources**

> Vadimkin/ukrainian-air-raid-sirens-dataset volunteer (eTryvoga) file, 116k oblast-level alerts 2022-02-25 to 2026-10-11 04:36 UTC (training and headline test). Official raion-level file of the same repo used for the raion layer (Dec 2025 - 2026-09-07) and for the live-definition check. alerts.in.ua API (live polls every 10 min plus daily history pull, backfilled from 2026-09-11) stored in a point-in-time store on the 'live-data' branch. Telegram: kpszsu (Air Force), deraketaua, monitorwarr, war_monitor via public web preview, complete from 2025-01-01, stored on a 'text-data' branch. RSS and GDELT news collected but not used. Kaggle 'Massive Missile Attacks' only to validate the morning-summary parser.

**Data source variant**

> Volunteer file (NOT official) for the oblast model, oblast-level only, snapshot 2026-10-11. The official file was rejected because it froze on 2026-09-07 and changed meaning in Dec 2025 (raion-level declarations). Live alerts.in.ua records of any level (oblast/raion/hromada/city) are replayed into oblast intervals by a measured rule (latest activation starts the oblast alert, any all-clear ends it, 1h expiry with no new activation). Raion layer uses the official file (union of hromada/city records into their raion; oblast records to all raions) plus alerts.in.ua.

### Method

**Model family**

> LightGBM (pooled over regions, one per target x horizon) as main model; also logistic regression (last 12 months), LightGBM without spatial features (ablation), lightgbm_cov (Telegram-period rows only) and lightgbm_text (+ Telegram). Baselines: 28-day same-hour climatology, raw persistence, 'Markov' persistence (P(event | region, alert running now) fitted on train). A survival-hazard model was tried separately and lost by 0.002-0.005 Brier. Raion layer: LightGBM 'current state' and '+28-day history', oblast probability, oblast x share. Live: Platt recalibration from verified forecasts.

**Features**

> Own state: alert running now, elapsed duration, minutes since last end, starts in last 6h/24h/7d. Own history: share of each of the last 24 hours under alert, share of last 24h/7d/28d. National: number of regions under alert now, nationwide starts in last 1h/3h, national share of last 24h. Spatial (learned lead-lag): now__<region> and lag1__<region> for each of the 24 regions (state now and in the last hour), instead of a hand-coded neighbour map; the ablation without them scored the same. Calendar: Kyiv-local hour and weekday of the target hour; same-hour climatology over 7/28 days (active and onset versions). Telegram (lightgbm_text only): posts naming the oblast in last 30/60/180 min total and by threat (drones, missiles, ballistic, KABs, all-clear), minutes since oblast last named with a threat, nationwide threat posts by class, number of oblasts named in last hour, strategic bomber / MiG-31K take-offs, ballistic threats, launch reports, 'massed attack' wording, drone/missile counts of the latest morning summary; NaN plus tg_covered=0 outside archive coverage. Top features by gain: onset climatology, starts in last 7d, hour climatology, alert running now, elapsed time. Text features took 16% of gain.

**External feature timing**

> Carefully handled. Each post has an available_at: publish time if not edited when first seen; first sighting if already edited (so backfilled edited posts are unusable in history); RSS news at first sighting; GDELT at crawl time (seendate), never claimed publish time. Features use a strict '< T' window. Morning launch counts are taken from the Air Force summaries with their publish time (not from Kaggle, whose row timing is unknown). A deliberately leaky 'permissive' variant (all posts at publish time with final text) bounds the edit-rule effect: at most 0.3-0.4 points of Brier improvement. Timing analysis: Air Force posts naming an oblast are at background rate until ~1h before onset, +15-25% in the last hour, and double only in the last 15 min, i.e. mostly concurrent rather than leading signals.

**Ablation design**

> Yes, time-fair. lightgbm_cov (history only) and lightgbm_text (history + Telegram) are trained on exactly the same rows (origins from 2025-01-03, the archive start, to each fold start minus 6h embargo), same weekly folds, trees chosen on the validation month for each separately; delta Brier with a 95% day-block bootstrap CI. This avoids the common confound of comparing a text model trained on a short window against a history model trained on all data. Also a spatial ablation (lightgbm_no_spatial vs lightgbm) and channel ablation (kpszsu only vs all 4 channels) on validation, and an edit-rule sensitivity run. The live serving rule (text model where it beat history-only on validation) was fixed before looking at the test.

### Evaluation

**Split scheme**

> Chronological walk-forward. Validation month 2026-08-15 to 2026-09-12 for model selection (training window 3/6/12/24 months/all, number of trees by early stopping). Test: origins 2026-09-12 23:00 to 2026-10-10 23:00 UTC, four weekly folds; every model refit on data up to each fold start. Embargo: training origins stop 6h (max horizon) before the first evaluated origin. Raion layer: same protocol on the official file's last 4 weeks (2026-08-09 to 09-06) and on alerts.in.ua labels (2026-09-13 to 10-10). Live: daily refit plus 10-min forecasts.

**Metrics**

> Brier score, Brier skill score vs 28-day same-hour climatology, log loss, ROC-AUC, PR-AUC, reliability diagrams, per-region skill and within-region AUC. Live verification: Brier vs climatology over 24h/7d/all time, hit rate, recall and false alarm ratio at p >= 0.5.

**Unit of metric**

> Pooled over regions for headline numbers; per-region skill and within-region AUC reported separately (onset-3h within-region AUC 0.52-0.74, median about 0.6), with the explicit note that pooled AUC flatters the model.

**Baseline strength**

> Climatology (28-day same-hour, the skill reference, effectively a rolling recent-rate by hour), raw persistence, calibrated 'Markov' persistence, logistic regression. Onset results: LightGBM beats climatology by only +5% / +4% / +3% / +3% Brier skill (h = 1/2/3/6); logistic regression is within 0.003 Brier. Persistence is worse than climatology at every horizon; Markov persistence helps only at 1h for active. No CI reported for the model vs climatology gain (only for text vs no-text). Active-1h skill +28% is mostly 'alert running now'.

**Calibration**

> Reliability diagrams on the test (reports/figures/reliability.png, text_reliability.png); author reports curves on the diagonal and reliability error <= 0.0012 for both text and no-text models. No post-hoc calibration in evaluation. Live: Platt map p = sigmoid(a + b logit(p_raw)) fitted per target x horizon on the last 7 days of verified forecasts, shrunk toward identity (ridge 20*h pseudo region-hours), weighted to one row per region x clock hour, served only if it improves Brier by >= 1% on a held-out check day; applied point-in-time (as_of=T), tested in tests/test_recalibration.py. A sub-hour backtest checks calibration at :00 vs :10..:50 origins.

**Uncertainty of gain**

> Day-block bootstrap 95% CI only for the Telegram ablation delta (text minus cov). Results: interval excludes zero only for onset 2h (-0.0018 [-0.0037, -0.0001]); onset 1h touches zero (-0.0012 [-0.0024, +0.0000]); others include zero. No CI or DM test for the main model vs climatology.

### Leakage & Hygiene

**Leakage handling**

> Strong and well tested. (1) Construction: features use minutes strictly before T plus 'alert running at T and its elapsed time'; end of a running alert never used. (2) Truncation test (tests/test_leakage.py): features rebuilt from data truncated at T must equal full-data features; negative controls: injected lag-0 feature and 'minutes since last end' using the running alert's end both make it fail. (3) Sub-hour truncation test at :10/:23/:40/:50 origins with a mutation test. (4) Label test: wiping history before T must not change labels. (5) Text leakage tests on a synthetic archive (posts at T, T+1, T+60 change nothing, T-1 does; '<= T' mutation fails; edited-when-first-seen rule; live path equals evaluation path), plus a real-archive truncation check at 25 origins. (6) Raion leakage tests with two injected leaks. (7) 6h embargo at every fold. (8) Live: never train on live data; store rows used only as known at T. (9) Found and fixed a label-as-feature bug (validation Brier 0.0000, AUC 1.0) that the truncation test missed; added a guard that aborts if validation AUC > 0.995. Missed or limits: no at-risk mask for onset; naive 30-min ends not analysed as a leak channel; the 12h cap and live 1h expiry are causal by construction.

### Results

**Headline results**

> Oblast, test 2026-09-12..10-10, about 16k forecasts per target x horizon. Onset Brier (skill vs 28-day climatology): LightGBM 0.146 (+5%), 0.176 (+4%), 0.176 (+3%), 0.132 (+3%) at h = 1/2/3/6; climatology 0.153/0.183/0.182/0.137; logistic 0.149/0.180/0.180/0.136; persistence 0.311-0.363 (much worse). Active: LightGBM 0.132 (+28%) at 1h, then +2 to +4%. ROC-AUC onset 0.78/0.80/0.81/0.86 (pooled); within-region onset-3h AUC 0.52-0.74, median about 0.6; per-region skill from -4% (Zaporizhzhia) to +10% (Ternopil). Spatial (learned lead-lag) features gave no gain. Telegram: onset 1-3h Brier -0.0012/-0.0018/-0.0017 (skill +4.7->+5.5, +4.1->+5.1, +3.9->+4.9), AUC +0.006-0.009; CI excludes zero only at onset 2h; nearly all from the Air Force channel. Raion layer: raion model beats raion climatology (onset 1h +16% on official file, +10% on alerts.in.ua labels), while the oblast probability used as-is is worse than raion climatology (-19% to -56%). Beats naive persistence clearly; beats climatology only modestly; no recent-rate or calibrated-persistence-at-risk baseline in our sense.

### Reproducibility

**Code available**

> Yes, public on GitHub, no license; Python package (src/airraid, src/airraid_app), extensive pytest suite, GitHub Actions pipeline (10-min poll, daily train), data on orphan branches live-data and text-data; actively maintained as of 2026-10-17.

### Relevance

**Takeaways for project**

> (1) Learned lead-lag via per-region now/lag1 state columns did NOT beat national counts plus own history; supports keeping our simple neighbours_active + national_active_count features and not adding a 24-column region-state block. (2) Their onset skill over a same-hour 28-day climatology is only +3-5%, even WITHOUT at-risk masking; expect our masked onset BSS vs the rolling recent-rate baseline (D-021) to be small or negative, and report it honestly. (3) Pooled vs within-region AUC gap (0.78 pooled vs ~0.6 within) confirms our requirement to report both. (4) Their live-rule finding (1h expiry after the latest activation, any-level all-clear ends) is an empirical cousin of our D-020 24h standing cap and D-027 'keep open alerts'; useful evidence that long frontline hromada alerts must be capped causally for the alerts.in.ua exploratory section. (5) The label-as-feature bug that passed the truncation test is a concrete reason to keep our leakage test's negative control (CLAUDE.md) and to add an AUC>0.995 abort guard. (6) Their 6h embargo equals our purge rule; our purge is horizon-specific. (7) Telegram time-fair ablation design (same rows, same folds, bootstrap CI) is the right template if external features are ever considered, but they are out of our scope and add ~1% Brier. (8) Their results are on volunteer data; never compare their numbers to ours (official data, masked onset) directly.

**Best practices**

> Adopt: truncation test with injected-leak negative controls (lag-0 and running-alert end); a separate label test; a sanity guard that aborts on implausibly perfect validation AUC; horizon-sized embargo at every refit; time-fair ablations (same rows and folds for with/without feature sets) with day-block bootstrap CIs; reporting within-unit AUC and per-unit skill alongside pooled numbers; honest 'what this means' sections; measuring a live definition against training labels before using it; point-in-time store with first_seen_at for any live data; available_at per external record and never trusting claimed publish times. Avoid: onset target without at-risk masking (inflated base rate, not a true onset estimand); scoring the same test weeks repeatedly while adding components; no CI on the headline gain vs the reference baseline; using naive 30-min ends without analysing their leak; mixing sources (volunteer training, alerts.in.ua live state) without a scored transfer check (they did measure it, which is good); large scope (web app, raions, Telegram) in a one-day build at the expense of a locked test.

### Other Info

**Uncertain fields (omitted above)**

- at_risk_masking
- calibration_under_drift
- known_label_artefacts
- preprocessing
- regime_coverage
- test_window_hygiene

---

<a id="cohort_nazar"></a>
## 7. nazar-andriievych/ukraine-air-alerts-analysis

*Category: peer_repo* — Raion-level; weather oracle-vs-forecast ablation template.

### Basic Info

**Name**

nazar-andriievych/ukraine-air-alerts-analysis

**Type**

repo (student / cohort peer project, same KSE Agentic AI School Stage 2 task)

**Url**

> https://github.com/nazar-andriievych/ukraine-air-alerts-analysis (key docs: docs/PROBLEM.md, README.md, reports/)

**Year**

> 2026 (created 2026-10-12 08:48 UTC, last push 2026-10-12 17:36 UTC, deadline day; 12 commits on main incl. merged 'weather' branch)

**Authors**

nazar-andriievych (GitHub handle, single author)

**Popularity**

0 stars, 0 forks (checked 2026-10-17); no license file

**Peer review status**

student repo, self-reported results; not peer reviewed

### Problem Framing

**Target type**

> STATE target, not onset: label = 1 if the raion was under alert at any moment in the UTC hour. 24% of raion-hours are positive overall, 34% in the test weeks. No at-risk masking, so the +1 h gain is mostly 'an ongoing alert continues'. The author states this limitation openly: the models 'rarely foresee when a new alert starts'. Not directly comparable to our onset target (D-020 estimand).

**Target definition**

> Unit = raion x UTC hour. Origin = end of hour t (the full hour t is known). Horizons h = 1..24: the hour starting at origin + (h-1) h. y = 1 if any alert (union of oblast/raion/hromada alerts mapped to that raion) is active at any moment in that hour. Multi-horizon (24 outputs) probability forecast. An earlier target (daily alert hours per raion, next 7 days) was dropped.

**Spatial unit**

> raion: 119 units (the raions of 23 oblasts plus Kyiv City as one unit; Luhanska and Crimea excluded). Oblast alert -> all its raions; hromada alert -> its whole raion.

**At risk masking**

> No. All origins are kept in training and scoring, both alert and clear at t. Because the target is a state, this inflates short-horizon skill: +1 h Brier drops 43% against the 28-day rate. Persistence is also strong at +1 h (0.081 on validation). No onset-only or clear-at-t view is reported.

### Data

**Data sources**

> (1) Vadimkin ukrainian-air-raid-sirens-dataset, datasets/official_data_en.csv, pinned to commit d10c80fa (2022-03-15 -> 2026-09-07), used up to 2026-09-07 00:00 UTC (last complete day 2026-09-06). (2) Reference hierarchy data/reference/regions.json (oblast->raion->hromada IDs, transliterated from regions_uk.json). (3) Weather, only for the experiment: Open-Meteo ERA5 archive (actual, 2022-03-16 -> 2026-09-06, 24 oblast centres) and the Previous Runs API '_previous_day2' day-ahead forecasts (complete from 2024-01-20). Volunteer data was compared but not used. The UkraineAlarm 48h log was not used.

**Data source variant**

> Official dataset only, ALL admin levels mapped to raion (union, oblast alert -> every raion, hromada -> whole raion), merged into non-overlapping intervals per raion. Snapshot pinned by commit hash with a checksum. Does NOT use alerts.in.ua or the post-2026-09-07 yellow/red regime.

**Preprocessing**

> Silver: removes exact duplicates (113,845 of 299,275 rows = 38%), drops Luhanska and Crimea, removes zero-length alerts and alerts starting after the data end, cuts alerts running at 2026-09-07 00:00 off there, and fixes rows with a raion name in the hromada field. Gold: spreads alerts to raions, merges overlaps per raion, and splits at UTC hour and day boundaries. It has every raion for every hour from 2022-03-16 to 2026-09-06, with 0 where there is no alert. No duration-based filtering: standing alerts are kept as-is on purpose.

### Method

**Model family**

> Logistic regression (scikit-learn, one model per horizon = 24 models, L2, scaled numerics, one-hot raion/oblast/hour) = final model. LightGBM (one global model over raions and horizons, log loss, early stopped at 203 trees) = challenger, not adopted: its gain over LR was +0.4% (CI -0.5 .. 1.2%), and the choice rule needs a gain larger than the bootstrap uncertainty.

**Features**

> All computed at the origin from data before it. State: alert_now (from merged intervals), spell_hours (current alert or quiet spell length, capped at 48 h for LR), alerts_24h (starts in the last 24 h). History: share of the last 1, 3, 6, 24, 168, 672 h under alert, origin hour excluded (672 h = the 28-day-rate baseline, so the model can start from it). Spatial context: share of the raion's oblast and of the whole country under alert now (no neighbour/border table). Calendar: hour of day and weekday of the TARGET hour in Kyiv local time, plus the horizon. Kyiv vs UTC tested once on validation: 3.3% vs 3.1% skill, Kyiv kept. IDs: raion and oblast as categories. LightGBM importance: 28-day share 59%, 7-day share 20%, target hour 7%. External: weather (wind, gusts, log1p precipitation, low cloud, temperature at the oblast centre at the target hour), tested only as an experiment and not adopted.

**External feature timing**

> Exemplary two-stage weather design. Stage 1 = ORACLE: actual ERA5 weather at the target hour. It is deliberately leaky and labelled 'upper bound, uses future weather, not a result'. ERA5 is also published about 5 days late, so it could not be used live even for past hours. Stage 2 = clean forecasts: the Open-Meteo Previous Runs '_previous_day2' value, from a run started at least 48 h before the target hour, so at least 24 h before the origin. The code assumes publication within 12 h and checks every row (weather_models.check_published). '_previous_day1' was rejected as unsafe at h = 24. The Historical Forecast API was rejected because it joins the newest run per hour, which is after the origin. Open-Meteo's end-of-hour stamping was aligned (value stamped 01:00 = hour 00:00-01:00). A stop rule (oracle gain < 1% and CI includes 0) was set before running. The oracle gain was -0.02% (-0.21 .. +0.21%), so stage 2 was never run: a forecast cannot carry more information than the truth.

**Ablation design**

> Yes, matched. The with/without-weather comparison uses the same 4.27M training rows (same seed), the same model and settings, and the same validation rows. The no-weather row reproduces the main model exactly (3.35%), which shows the rows match. The paired skill difference (with vs without) gets its own day-block bootstrap CI, overall and per alert-rate band. Kyiv vs UTC calendar and LightGBM vs LR are also paired on the same rows. Caveat (stated by the author): the weather enters the LR only linearly per horizon; LightGBM was not tried with weather. The sample is not time-restricted to the weather-forecast era (from 2024-01-21) for the oracle stage, because ERA5 covers everything.

### Evaluation

**Split scheme**

> Chronological fixed splits by date, half-open [start, end), UTC. Train 2022-03-16 -> 2026-05-17. Validation 2026-05-18 -> 2026-07-12 (8 weeks). Test 2026-07-13 -> 2026-09-06 (8 weeks, scored once). An origin belongs to a split only if all 24 target hours fall inside it (a purge), and it needs at least 28 days of history. Training origins = a random third of hours, each with one random horizon from each of the bands 1-8, 9-16, 17-24 (4.27M rows); a full 24-horizon expansion (34M rows) does not fit in memory. Test = every hour (rolling origin, 1,321 origins x 119 raions x 24 h = 3.77M forecasts). The final model is REFIT on train + validation (2022-04-13 -> 2026-07-11, 4.43M rows) before the test. No refits within the test.

**Unit of metric**

> Pooled over raions x origins x horizons; additionally pooled within alert-rate bands. No within-unit averaged AUC reported.

**Baseline strength**

> Baselines: persistence (state at origin for all 24 h), 28-day rate (share of the last 28 days under alert; the 'baseline to beat', a rolling recent rate), and hour-of-day rate (same, only the target hour of day). No calibrated persistence; no climatology fit on train. Test skill vs the 28-day rate: LR +3.6% (CI 1.5 .. 6.5%); hour-of-day -1.3%; persistence -71% overall, but persistence beats the 28-day rate at +1 h (0.087 vs 0.107). On a state target, persistence at +1 h is a strong reference that the skill vs the 28-day rate hides. LR +1 h 0.061 beats persistence 0.087.

**Calibration**

> Reliability diagrams on validation and test (reports/reliability.png, reports/final_test_reliability.png). The author reports both models well calibrated. No post-hoc calibration fitted.

**Calibration under drift**

> Not explicitly tested. No calibration-in-the-large comparison test vs validation, no recalibration. The base rate shift is noted descriptively: 34% of hours under alert in test, and test weeks are 'more uneven' with wider CIs. The post-2026-09-07 regime is not evaluated.

**Uncertainty of gain**

> Yes. Day-block bootstrap (1,000 resamples, whole UTC days, because forecasts from neighbouring origins overlap) gives 95% intervals on the skill vs the 28-day rate, overall and per band. A paired bootstrap on model-vs-model differences (LightGBM vs LR, weather vs no weather) drives the choice rules. No Diebold-Mariano test.

**Regime coverage**

> Train spans 2022 -> mid-May 2026, so it covers the Jan-2025 drone surge and the Dec-2025 raion-level reform. Both validation and test fall after the reform (raion-only alerts except Kyiv City), which suits a raion target. The author documents the reform as a data finding. The Sep-2026 yellow/red reform is not covered: the data ends 2026-09-07 and no API data is used.

### Leakage & Hygiene

**Test window hygiene**

> Good, and documented. The test was scored once (python -m pipeline final). The code was committed and pushed before the run (commit 1a87ca9). The pipeline was checked by reproducing the validation result exactly with the final code before scoring test. The weather branch never touched test. Choice rules (LGBM vs LR; the weather stop rule) were fixed before seeing the results. No pre-registration document beyond PROBLEM.md, but the decisions there are dated. All work happened on 2026-10-12 (single day), so the target changed mid-day (daily 7-day -> hourly 24 h) before modelling.

### Results

**Headline results**

> Test (2026-07-13 -> 09-06), LR: Brier 0.1033 vs 28-day rate 0.1072, skill +3.6% (95% CI 1.5 .. 6.5%). Positive in every band: <10% +1.9%, 10-20% +4.7%, 20-60% +2.3%, >=60% +5.7%; all CIs above 0. By horizon: +1 h Brier 0.061 vs 0.107 (43% skill), +2 h 9%, +6 h 2.5%, +24 h 0.7%. Validation: LR 3.3% (2.3 .. 4.4%), LightGBM 3.7% (2.1 .. 5.3%). Weather oracle on validation: -0.02% (-0.21 .. +0.21%), so it gives no gain. An extra raw-data check: in 2025-2026, the share of hours under alert falls from 32.6% (calmest fifth of hours) to 26.3% (gustiest), but the rate of NEW alerts stays flat at 5.4-5.9%. Weather relates to place/season, not to onset timing. It beats naive baselines, but almost all of the gain is the persistence of ongoing alerts at +1-2 h; beyond about 8 h it is about 1% better than the 28-day rate.

### Reproducibility

**Code available**

> Yes, public on GitHub. Python 3.13, pinned requirements (pandas 3.0.6, scikit-learn 1.9.1, lightgbm 4.7.0, etc.). Medallion pipeline (bronze/silver/gold/features), `python -m pipeline`, pytest tests per step, generated data not committed, dataset commit pinned. No license. Deadline-day project, not maintained after 2026-10-12.

### Other Info

**Uncertain fields (omitted above)**

- best_practices
- known_label_artefacts
- leakage_handling
- metrics
- takeaways_for_project

---

<a id="cohort_others"></a>
## 8. Other cohort repos (Kamenqq, gklymenko, mykhailoisupov, yeliena-bochagova, endrusmah, MaksimPrykhodko)

*Category: peer_repo* — Count targets, oblast-only filter pitfall, volunteer data, misused accuracy metrics.

### Basic Info

**Name**

> Other cohort repos: Kamenqq/air-raid-alerts-forecast, gklymenko/ukraine-air-raid-alerts-time-series, mykhailoisupov/kyiv-air-alert-forecast (+ mykhailoisupov/air-raid-alert-forecast, national), yeliena-bochagova/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine, endrusmah/air-raid-alert-analysis, MaksimPrykhodko/Ukraine-air-raid-prediction

**Type**

> repo (7 student / cohort peer repositories from the same KSE Agentic AI School task; mykhailoisupov also has an empty air-raid-alert-forecast-v2 with one commit and only a .gitignore)

**Url**

> https://github.com/Kamenqq/air-raid-alerts-forecast ; https://github.com/gklymenko/ukraine-air-raid-alerts-time-series ; https://github.com/mykhailoisupov/kyiv-air-alert-forecast ; https://github.com/mykhailoisupov/air-raid-alert-forecast ; https://github.com/yeliena-bochagova/Time-Series-Analysis-of-air-raid-alerts-in-Ukraine ; https://github.com/endrusmah/air-raid-alert-analysis ; https://github.com/MaksimPrykhodko/Ukraine-air-raid-prediction

**Year**

> 2026. Last pushes (UTC): Kamenqq 2026-10-12 18:06 (39 commits); gklymenko 2026-06-21 (8 commits, an earlier cohort/stage); mykhailoisupov kyiv 2026-10-12 21:59 (18 commits) and national 2026-10-12 17:10 (14 commits); yeliena-bochagova 2026-10-12 20:25 (10 commits); endrusmah 2026-10-11 19:20 (5 commits); MaksimPrykhodko 2026-06-24 (3 commits). Checked 2026-10-17.

**Authors**

> Kamenqq (single author); Galyna Klymenko (gklymenko, per commit metadata; not the dataset maintainer Vadym Klymenko); Mykhailo Isupov (mykhailoisupov); Yeliena Bochagova; endrusmah (license reads 'Ukraine Alerts As-of project contributors'); Maksim Prykhodko. All built with AI coding agents (Claude Code / Codex), as their READMEs say.

**Popularity**

> 0 GitHub stars on every repo except MaksimPrykhodko/Ukraine-air-raid-prediction (1 star), checked 2026-10-17. Licenses: MIT (endrusmah, MaksimPrykhodko); none for the others.

**Peer review status**

student repos; all results self-reported; nothing peer reviewed

### Problem Framing

**Target type**

> A mix, and the mix is the lesson. COUNT targets: Kamenqq (alert starts per oblast per Kyiv day, 1-7 days ahead) and endrusmah (Kyiv City starts per UTC day). gklymenko uses a continuous ACTIVITY target (alert minutes per day, Kyiv City). STATE targets: mykhailoisupov national ('alert active for at least one minute in hour t+h', 24 regions) and Kamenqq's hourly 'chance an alert is active at some moment in each hour'. ONSET targets: mykhailoisupov/kyiv-air-alert-forecast (new alert within 1/3/6 h, quiet city only; the closest match to ours), yeliena-bochagova (at least one new start in the region on day D+1) and MaksimPrykhodko (an alert start in the next hour, Kyiv City, but without masking). The national mykhailoisupov repo measured state inflation directly on one model: Brier skill vs climatology at 1 h is 0.267 on all rows but only 0.065 on rows with no alert at forecast time, and within-region AUC is 0.758 vs 0.620.

**Target definition**

> Kamenqq: count of merged alert episodes starting per oblast per Kyiv calendar day D+k, k=1..7, forecast made at 00:00 Kyiv; hourly 'active at some moment in hour' probabilities. gklymenko: total alert minutes per day for Kyiv City, h=1 day, 80% intervals. mykhailoisupov kyiv: at the top of each hour with no alert active in Kyiv, y=1 if a new alert starts within H in {1,3,6} h. mykhailoisupov national: y=1 if the hour t+h has at least one minute of alert, h in {1,3,6,12,24}. yeliena-bochagova: y=1 if at least one alert STARTS in the region on Kyiv day D+1, info cutoff = end of day D. endrusmah: Kyiv City alert-start count on UTC day D, issued D-1 at 12:00 UTC. MaksimPrykhodko: has_alert(hour)=1 if any Kyiv City alert started in that Kyiv-local hour bin; predicted from lagged hours (H=1).

**Spatial unit**

> Oblast (24 units): Kamenqq, mykhailoisupov national, yeliena-bochagova. Kyiv City only: gklymenko (computed for 25 oblasts but focal Kyiv City), mykhailoisupov kyiv, endrusmah, MaksimPrykhodko.

**At risk masking**

> Only mykhailoisupov/kyiv-air-alert-forecast masks properly: origins are only quiet hours (940 test origins). It explains why: 57% of hours with an alert in the next hour already had one active. mykhailoisupov national does not mask during training, but reports a 'no alert at forecast time' subset (88% of forecasts). yeliena-bochagova does not need a mask (daily start target; ongoing alerts do not make the label positive). MaksimPrykhodko has no mask, and its lags are on the start series, so hours inside an alert stay in the data as negatives. The count/minutes repos (Kamenqq, gklymenko, endrusmah) have no at-risk concept.

### Data

**Data sources**

> Vadimkin/ukrainian-air-raid-sirens-dataset in every repo except mykhailoisupov/kyiv. Volunteer file (eTryvoga) as the target: Kamenqq (snapshot 2025-09-01 -> 2026-10-11, plus Telegram air_alert_ua and tryvoga_chomu), mykhailoisupov national (2025-01-01 -> 2026-10-11, plus 26,338 @kpszsu Telegram posts from 2026-04-01), yeliena-bochagova (2022-02-25 -> 2026-10-10), endrusmah (200 commit-pinned daily snapshots 2026-03-24 -> 2026-10-09, plus GDELT GKG headlines), MaksimPrykhodko (2022-02-25 -> 2026-06-24). Official file only: gklymenko (2022-03-15 -> 2026-06-21, oblast-level subset; volunteer used only as a cross-check). mykhailoisupov kyiv: Kyiv Digital open API (Kyiv City, Feb 2022 -> 2026-10-12, minute resolution, no key), checked against the city's weekly open-data file (all 2,641 alerts match), plus @kpszsu posts for a text ablation.

**Data source variant**

> Most of the cohort moved to the VOLUNTEER file, because the official file froze on 2026-09-07 and they wanted a test window that ran to October. That breaks two of our rules: volunteer data only covers oblast level, and about 5% of its end times are imputed 'naive' +30 min. Kamenqq first mixed the sources and got -16% skill and a -0.57 bias, because the target's meaning changed when the official file stopped. It then switched to eTryvoga alone, a choice made after seeing the test (the author says so). mykhailoisupov national measured volunteer vs official agreement at 82-89% of region-hours. OBLAST-ONLY FILTER PITFALL (gklymenko): it keeps the official file's level=='oblast' rows only. We checked its committed snapshot after removing exact duplicates: oblast-level rows per quarter fall from about 4,500 (2024) to 3,588 (2025Q3), 903 (2025Q4), 138 (2026Q1) and 124 (2026Q2). Every remaining 2026 oblast-level row is Kyiv City. The README's claim that the oblast series 'survives the December-2025 transition intact' holds only for Kyiv City, which has no raions. For every other oblast the filter wipes out the series after late 2025. Kyiv-only repos (mykhailoisupov kyiv, endrusmah, MaksimPrykhodko) give the same reason for picking Kyiv City: it stayed one alert unit through the admin reform.

**Preprocessing**

> Deduplication: gklymenko dedupes on (region, started_at, finished_at) and raises an error if duplicates remain (about 50% exact duplicates in the oblast subset); Kamenqq calls drop_duplicates() on both files; yeliena-bochagova only prints the exact-duplicate count and counts starts without deduping; MaksimPrykhodko does not dedupe. Admin union: none of them build a raion/hromada union. Kamenqq maps raion -> oblast only for Telegram posts (data/region_map.csv). Long or standing alerts: gklymenko flags 'always-on' alerts longer than 12 h; mykhailoisupov national cuts all 18 alerts longer than 12 h to start + 30 min (it admits this uses the final length, which is not known live); MaksimPrykhodko drops alerts shorter than 1 min or longer than 7 days; Kamenqq merges intervals into episodes. Gaps: Kamenqq and mykhailoisupov note the 2026-08-30..09-01 official/air_alert_ua outage; mykhailoisupov national drops the last 12 h of the snapshot because running alerts are missing. Time zone: gklymenko keeps the hour-of-day profile in UTC (listed as a limitation); MaksimPrykhodko bins hours in Europe/Kyiv local time, which is fragile around DST changes; mykhailoisupov kyiv converts Kyiv wall-clock API times to UTC and resolves the repeated autumn hour by order.

**Known label artefacts**

> Naive (+30 min) ends: Kamenqq imputes naive eTryvoga ends with the oblast's median duration, estimated on Sep-Nov 2025 only, before the training window (H6: error 23.9 vs 24.9 min against the +30 default, on 27,846 alerts with a real end). endrusmah and yeliena-bochagova read only started_at, so naive ends cannot leak. mykhailoisupov kyiv avoids the problem with a fully observed city API. Standing / fake long alerts: mykhailoisupov national found that all 18 volunteer alerts longer than 12 h (Jan 2024 - Aug 2026) had almost no matching official alert and treated them as missed all-clears; the cut uses the final length, a stated look-ahead. gklymenko flags them with a 12 h heuristic and excludes always-on frontline oblasts from volume modelling. Gaps: Kamenqq and mykhailoisupov document the 2026-08-30..09-01 outage, but nobody masks it explicitly in evaluation; mykhailoisupov kyiv and endrusmah avoid it by source choice. Duplicates: about 50% exact duplicates in the official oblast subset (gklymenko); in 2022 the Kyiv API stream has 47 repeated starts and 6 repeated all-clears, repaired with an 'all-clear closes the start before it' rule. Source disagreement: Kamenqq reports that since July 2026 eTryvoga records far more Lviv/Volyn alerts than the official data (cause unknown). Live-only fields: mykhailoisupov kyiv uses post-reform alert causes (drone/missile/ballistic) only for alerts that have already ended, because the cause list grows during an alert.

### Method

**Model family**

> Kamenqq: HistGradientBoostingRegressor(loss='poisson'), defaults, retrained for every forecast date; the hourly chances are a 56-day shrunk empirical hour profile scaled by the predicted count. gklymenko: baselines only (Naive, SeasonalNaive, MovingAverage(7)) with empirical-residual intervals. mykhailoisupov kyiv: logistic regression refitted weekly on the previous 16 weeks; challengers are logistic regression on all history and HistGradientBoosting (with and without a CalibratedClassifierCV sigmoid wrapper); a separate conditional-quantile estimator for the remaining alert time. mykhailoisupov national: HistGradientBoostingClassifier per horizon (300 trees, lr 0.05, fixed before the first run), logistic regression on 4 inputs, persistence. yeliena-bochagova: class-balanced logistic regression with a validation-tuned threshold; a constrained random forest was rejected. endrusmah: Poisson GLM with a log link plus a 7-day-level exposure offset (sklearn PoissonRegressor fit on y/exposure with sample_weight=exposure); 36-candidate grid. MaksimPrykhodko: XGBoost tuned with Optuna (n_estimators 116, depth 8, scale_pos_weight 4.9, threshold 0.633), after LR and RF.

**Features**

> Lag / own state: counts yesterday, last 7 and 28 days, same weekday last week (Kamenqq); starts in the last 1 h-28 d, minutes under alert in the last 24 h/7 d, time since the last start and all-clear, duration and threat type of the last finished alert, trailing hour-of-day rate (mykhailoisupov kyiv); alert on now, minutes under alert, alert share over 3-168 h, hours since the last alert and the last quiet hour (mykhailoisupov national); rolling start counts and alert-day counts over 3/7/14/30 days, days since the last alert (yeliena-bochagova); city lag 1 and 7, trailing means 3/7/28, collector age (endrusmah); lags 1/2/3/24 h, rolling 3-24 h sums, hours_since_last_alert (MaksimPrykhodko). Spatial: neighbouring oblasts yesterday / 7-day mean from a border table (Kamenqq, H4: small validation gain, no gain on test); current state of all 24 regions and national share now, 1 h ago and over 6 h (mykhailoisupov national; dropping the other regions cost 0.006 skill at 1 h); national context on day D (yeliena-bochagova; rejected); neighbour aggregate lag 1 and mean 7 (endrusmah); 5 Kyiv neighbours at 1-3 h lags (MaksimPrykhodko). Calendar: Kyiv hour and weekday (most repos); sin/cos encodings (endrusmah, MaksimPrykhodko); month (yeliena-bochagova). External: Telegram keyword counts from tryvoga_chomu (Kamenqq) and @kpszsu (both mykhailoisupov repos); GDELT GKG headline count, tone, conflict-theme share and up to 50 TF-IDF unigrams (endrusmah).

**External feature timing**

> Better than in pre-2026 repos. mykhailoisupov (both repos): posts strictly before t, from the public t.me/s preview; edited posts keep their timestamp but their text is ignored. Text added +4.0% Brier skill at 1 h on Kyiv (CI +0.4 to +7.3) and nothing at 3/6 h. In the national repo it added 0.025 on validation but only 0.004 on test (CI -0.004 to 0.013), and the gain faded within a week because the channel drifted from 101 to 255 posts/day and named known regions less often (88% -> 79%). Kamenqq: Telegram posts published before 00:00 Kyiv of D; the live repo's ~05:00 UTC daily update delay is not simulated (stated). endrusmah has the strictest timing: an alert snapshot can be used only once the upstream GitHub publisher workflow has completed + 6 h, before the origin; GDELT records need an explicit publication timestamp plus a 2 h buffer for index/archive availability (1,349 records without it were excluded). Its news model did not help: MAE difference +0.046, 7-day block bootstrap CI [-0.059, +0.106]. All Telegram backfills are after-the-fact: deleted posts are missing and only final text is visible.

**Ablation design**

> Mostly fair: additions are compared on the same folds and windows. mykhailoisupov kyiv runs text with/without on the same weekly folds at hourly and 15-minute origins, a training-window sensitivity (8/16/32 weeks/all history), and trees with/without the calibration wrapper. That last comparison exposed a false claim ('trees failed outright'): with the wrapper, Brier 0.270 and AUC 0.51; without it, 0.250 and AUC 0.63. mykhailoisupov national ablates on validation only: other regions on/off, training history from 2023 / 2025 / May 2026, richer text features (0.3133 vs 0.3130 -> dropped). Kamenqq decided H4 neighbours on the validation window (2.028 -> 2.010 MAE), then saw a tie on test. endrusmah compares history-only vs news Poisson on the same origins with a paired block bootstrap. MaksimPrykhodko's 'ablation' (LR -> LR+features -> RF -> XGB) is not interpretable: thresholds were tuned on the test set and the hours_since_last_alert leak enters at the LR+features step.

### Evaluation

**Split scheme**

> Kamenqq: validation 2026-08-16..09-12, test 2026-09-13..10-10 (28 days, 4,704 forecasts); Poisson retrained for every forecast date. gklymenko: expanding-window walk-forward, h=1 day, 2022-03-15..2026-06-21, no fixed test. mykhailoisupov kyiv: test = latest 8 weeks, 17 Aug - 12 Oct 2026, weekly folds; each fold trains on origins whose label window closed before the fold starts. mykhailoisupov national: fit 2025-01-01 -> validation 2026-08-16..09-13 -> test 2026-09-13..10-11, model fitted once and frozen 4 weeks; training rows kept only if their label was known before the window's first forecast. yeliena-bochagova: latest 30 days = evaluation, the 30 days before = validation, with a one-forecast-day purge gap; plus a 6-fold rolling backtest (30 d validation / 30 d evaluation, 90-day steps). endrusmah: validation targets 13 Aug - 9 Sep, selection instant 10 Sep 12:00 UTC (10 Sep target purged), test targets 11 Sep - 8 Oct with daily as-of refits under locked settings. MaksimPrykhodko: chronological 80/20 split by ROW INDEX (iloc), no purge, Optuna with TimeSeriesSplit(3) on train.

**Metrics**

> Count/continuous: MAE, RMSE, bias, skill vs 7-day average (Kamenqq); MAE, RMSE, MASE, 80% PI coverage, interval width, pinball loss (gklymenko); MAE/RMSE, interval coverage (endrusmah). Probabilistic: Brier, Brier skill, reliability (Kamenqq hourly chances; mykhailoisupov kyiv); Brier skill vs climatology, log loss, PR-AUC, ROC-AUC pooled and within-region (mykhailoisupov national). MISUSED ACCURACY METRICS: yeliena-bochagova's primary metric is balanced accuracy at a threshold, with recall, precision, F1 and FP/FN. That throws away the probabilities, and with an 87.2% positive rate in the last 30 days (Zakarpatska 0%, Ivano-Frankivska 27%, most oblasts ~97-100%) much of the score is just telling regions apart. MaksimPrykhodko headlines F1 0.87, precision 100%, recall 77% and accuracy 98% at a 6-8% base rate, with the F1-optimal threshold picked on the test set; its only baseline is 'always predict 0'.

**Unit of metric**

> Pooled in most repos. mykhailoisupov national reports both: pooled AUC 0.86 vs within-region 0.76 at 1 h, and says outright that pooled AUC mostly reflects knowing which regions are busy. Single-unit repos (Kyiv City) avoid the question. yeliena-bochagova shows per-region balanced accuracy only as a diagnostic, and warns that some regions have one class in 30 days.

**Baseline strength**

> Strong baselines in mykhailoisupov kyiv: flat 28-day rate, hour-of-day rate over 28 days (the pre-registered reference), hour-of-day rate over all history, and a recent-onset rate (28-day rate conditional on a start in the previous H). The author found the pre-registered reference was weaker than a flat rate, so skill vs that reference overstated the model. Headlines then moved to the 'best simple forecast chosen after the fact on the same period', which deliberately raises the bar. Kamenqq: last-7-days average (ties the model: 1.97 vs 1.97 MAE) and same weekday last week; for hourly chances, a flat rate (wins on Brier: 0.1870 vs 0.1871 at 1 day). gklymenko: Naive, SeasonalNaive, MA(7); MASE ~1, SeasonalNaive worst. mykhailoisupov national: 28-day hour-of-day climatology and calibrated persistence (per-region alert rate given state now, last 90 days); no rolling recent-rate baseline. endrusmah: the 28-day mean benchmark beats every Poisson (final MAE 1.297 vs 1.518 for the deployed choice). Rolling means were kept OUT of the selection pool by design, so the deployed model is knowingly worse. yeliena-bochagova: always-alert and persistence only. MaksimPrykhodko: always 0 only.

**Calibration**

> Kamenqq: reliability check at 1 day ahead (35% -> 35%, 45% -> 46%, 74% -> 76%; low chances run too low, 3% -> 6%, and 25% -> 38% for 2-hour windows). mykhailoisupov kyiv: reliability plot; calibration 'rough' bin by bin; the highest 1 h forecasts are too high. Its sigmoid CalibratedClassifierCV (3 folds) wrecked the trees: mean forecast 12% vs 33% observed. mykhailoisupov national: within 0.04 in every 10-point band at 1 h. endrusmah: empirical residual intervals cover all 28 outcomes, but they are 9.11 starts/day wide. gklymenko: 80% PI covers only ~72% (heavy tails); lower bound goes negative. yeliena-bochagova and MaksimPrykhodko: no calibration; class_weight='balanced' / scale_pos_weight distort the probabilities by construction.

**Calibration under drift**

> mykhailoisupov kyiv checks calibration-in-the-large under the regime change: after the 7 Sep reform, the all-history logistic averages a 74% 6 h forecast against 87% observed; the 16-week model averages 82%. Kyiv starts per day went from 1.2-1.9 to 5.5 since August 2026, and the median quiet gap fell from 5-11 h to 1.4 h. endrusmah: the label mean rose from 1.85 in the initial training portion to 3.75 in validation; the fix was a 7-day-level exposure offset (multiplicative adjustment to the known recent level). Kamenqq: count bias -0.09/day on test; per-oblast skill ranges from +11% (Chernivetska) to -32% (Kyiv City). The national mykhailoisupov repo shows the Telegram gain fading over the 4 frozen weeks (0.018, 0.002, 0.002, -0.003). No repo fits a recalibration on a later window.

**Uncertainty of gain**

> mykhailoisupov kyiv: 1,000-draw day-block bootstrap on Brier skill. vs best simple forecast: +3.2% (-2.5 to +8.5) at 1 h, +3.3% (-4.7 to +11.1) at 3 h, +5.1% (-4.6 to +13.6) at 6 h, all CIs include zero; since the reform +10.2% (+0.2 to +22.9) at 3 h and +11.8% (+1.2 to +19.9) at 6 h. mykhailoisupov national: 2,000-draw day-block bootstrap; Telegram gain CI -0.004 to 0.013 on test. endrusmah: paired 7-day moving-block bootstrap on the MAE difference [-0.059, +0.106]. Kamenqq, gklymenko, yeliena-bochagova and MaksimPrykhodko report no CI on gains.

**Regime coverage**

> Several repos test inside the Sep-2026 yellow/red regime because they use volunteer data or the Kyiv API up to October: Kamenqq (13 Sep-10 Oct), mykhailoisupov national (13 Sep-11 Oct), endrusmah (11 Sep-8 Oct), yeliena-bochagova (last 30 days to 10 Oct), and mykhailoisupov kyiv (17 Aug-12 Oct, with a separate 'since 7 Sep reform' slice; only 25 red-level alerts). The Aug-2026 surge (Kyiv 5.5 starts/day) falls inside most test windows. gklymenko marks the Dec-2025 aggregation change but does not see that it breaks every oblast series except Kyiv City. MaksimPrykhodko's test is the last 20% of rows ending 2026-06-24, before the reform. None evaluates a pre-reform frozen model on post-reform data the way our D-015 does; the closest is mykhailoisupov kyiv's 'since reform' slice.

### Leakage & Hygiene

**Leakage handling**

> Strong examples. mykhailoisupov kyiv: a hide-the-future recompute test on synthetic and real data, a NEGATIVE CONTROL (a planted leaky feature must be caught, and exactly that one), fold labels must close before each test fold, every still-open label is flipped and baselines must not change, truncate() blanks running alerts' end and final cause list, and the live forecast equals the backtest for the same instant. mykhailoisupov national: future values flipped at 3 cut points; 9 planted leaks all caught. Kamenqq: full-data vs truncated-data recompute must be identical; deliberate breaks each fail a test; two review agents rebuilt 8 real forecast days from cut data. endrusmah: 25 temporal/provenance tests (future label/text injection, final-truth isolation, test-era corruption, lock integrity), selection stage physically cannot construct test rows, SHA-256 lock on the selection. yeliena-bochagova: one-day purge gap and invariant tests. Missed / leaky: mykhailoisupov national cuts fake long alerts using their final length (stated look-ahead). MaksimPrykhodko has a direct TARGET LEAK in hours_since_last_alert: on label=1 rows the feature is set to the gap to the previous alert, and on label=0 rows it is the previous row's value + 1. So the feature drops exactly in the hours whose own label is 1. We re-implemented it on Kamenqq's committed volunteer snapshot (Kyiv City, the same 80/20 row split, a HistGradientBoosting classifier, F1-optimal threshold on test). With the leaky feature: F1 0.82, precision 0.98, recall 0.71. With a causal version (shifted ffill of the last alert position): F1 0.14, precision 0.08, recall 0.48 (base rate 8.3%). That matches the repo's '100% precision, 0.87 F1' and its 'most important feature (SHAP 0.66)'. It also tunes the threshold on the test set and splits by row index without a purge.

**Test window hygiene**

> Mixed, and most authors say so honestly. Kamenqq: H4 and the 'when' method were chosen on validation and test was scored once, but the target-source switch (official+Telegram -> eTryvoga only) came after seeing test results; the extra 'details' checks were measured once with nothing changed. mykhailoisupov kyiv: the window, inputs and reference were fixed in advance, but the final model (16-week window) replaced the first attempt AFTER test results were seen, and the headline bar ('best simple forecast') is chosen ex post. The README and REFLECTION.txt document both. mykhailoisupov national: choices committed on validation, test run once (git history: 'Fix the model choice on validation' at 18:31, 'Score the test window once' at 18:35). endrusmah: v1 had already scored 11 Sep - 8 Oct; v0.2 locked selection with a SHA-256 hash and passed 25 tests before re-scoring, and calls it a 'reused historical holdout'. yeliena-bochagova: 'the latest period was inspected during development', so it points to the rolling backtest as the stronger evidence. MaksimPrykhodko: threshold tuned on test; no hygiene.

### Results

**Headline results**

> Kamenqq: count MAE 1.97 vs 1.97 for the 7-day average (tie, skill ~0%); hourly chance Brier 0.1871 vs flat 0.1870 at 1 day (does not beat the flat rate), well calibrated. gklymenko: Kyiv City minutes/day MAE MA(7) 96.3 vs Naive 110.2 vs SeasonalNaive 116.6; MASE 1.03-1.25 (no baseline beats seasonal naive meaningfully); PI coverage 72% vs nominal 80%. mykhailoisupov kyiv (onset, quiet hours): Brier 0.218 / 0.217 / 0.157 at 1/3/6 h vs best simple 0.225 / 0.225 / 0.165, edges +3.2% / +3.3% / +5.1% with CIs including zero; since reform +10-12% at 3-6 h (CIs exclude zero); base rates 33% / 60% / 75%; ROC-AUC 0.63 at 1 h. mykhailoisupov national (state): BSS vs climatology 0.267 at 1 h, but 0.065 on quiet rows and 0.007 at 24 h; within-region AUC 0.76 (all) / 0.62 (quiet). yeliena-bochagova: balanced accuracy 0.932 latest vs persistence 0.865; rolling backtest 0.855 vs 0.764, with more false negatives than persistence (594 vs 386). endrusmah: the deployed Poisson loses to the 28-day mean (final MAE 1.518 vs 1.297). MaksimPrykhodko: F1 0.87 / precision 1.00 / accuracy 0.98, an artefact of the target leak (see leakage_handling). Across the cohort, wherever a strong rolling baseline exists, the model ties it or beats it by a small margin that is not significant.

### Reproducibility

**Code available**

> All public on GitHub. Licenses: endrusmah MIT (+ upstream license preserved); MaksimPrykhodko MIT; the others have no license. Data committed in the repo: Kamenqq (frozen data/snapshot/ with volunteer, official and Telegram CSVs, ~24 MB), gklymenko (data/raw/ CSVs), yeliena-bochagova (processed panel), endrusmah (compact commit-pinned snapshot extracts + GDELT JSON with SHA-256). mykhailoisupov downloads at run time (uv.lock / pinned). CI: Kamenqq (GitHub Actions on 3 OS x Python 3.9-3.15, 98 tests). Test counts: Kamenqq 98, gklymenko 62, mykhailoisupov national 47, endrusmah 25. Maintenance: all are deadline snapshots (Oct 2026, or June 2026 for gklymenko and MaksimPrykhodko); no ongoing maintenance expected.

### Relevance

**Takeaways for project**

> 1) Target: our onset + at-risk mask (CLAUDE.md Target section) is supported by two cohort measurements. One model's state-target skill falls from 0.267 to 0.065 on quiet rows (mykhailoisupov national), and 57% of hours with an alert in the next hour already had one active (mykhailoisupov kyiv). Cite both in the README as external motivation for the mask. 2) Oblast-only filter: gklymenko's level=='oblast' series is empty for every oblast except Kyiv City after 2025Q4 (138 rows/quarter, all Kyiv City). This validates our union of all levels via the `oblast` column, and suggests a data-quality check that raises if any unit's onsets per month collapse by more than ~90% across Dec 2025 (D-017 item 6). 3) Volunteer data: the cohort's move to volunteer data to reach October is the trap our 'never use volunteer_data' rule and D-007/D-015 avoid. Kamenqq showed that mixing sources across a source stop gives -16% skill and -0.57 bias; that is evidence for 'never mix the two sources in one training set or one test metric'. 4) Baselines: every repo with a rolling recent baseline (7/28-day mean, flat 28-day rate, recent-onset rate) found the model ties it or beats it within noise. Expect the same against our rolling recent-rate baseline (D-021), and treat a tie as a valid result. mykhailoisupov's finding that a pre-registered hour-of-day reference was weaker than a flat rate suggests adding a flat recent rate as a sanity row, so skill vs climatology is not overstated. 5) Metrics: avoid balanced accuracy / F1 / precision at a threshold as headlines (yeliena-bochagova, MaksimPrykhodko); keep Brier/BSS primary and report within-oblast AUC next to pooled AUC (mykhailoisupov national: 0.86 pooled vs 0.76 within). 6) Leakage: MaksimPrykhodko's hours_since_last_alert bug is a ready template for our negative control in tests/test_leakage.py: a 'time since last onset' feature that resets on the current row's label must be caught by the truncation test. Our minutes_since_last_start must use only onsets at or before t. 7) Calibration: do not wrap GBMs in CalibratedClassifierCV on the training folds. mykhailoisupov saw it collapse the mean forecast from 27% to 12%. Our D-021 rule (calibration fitted on validation, applied to the same model) is the safer design. 8) Drift: mean predicted vs observed after the reform (74% vs 87% for an all-history model) is exactly the calibration-in-the-large check in our D-015(c); expect a frozen pre-reform model to under-forecast onsets after Aug-Sep 2026. 9) Uncertainty: day- or week-block bootstrap on skill (mykhailoisupov, endrusmah) is the norm in the better repos; adopt the D-013 week-block CI if time allows.

**Best practices**

> ADOPT: (a) a negative-control leaky feature that the truncation test must catch, plus planted-leak counts (mykhailoisupov: 9 planted leaks all caught); (b) flipping every not-yet-closed label and asserting baselines do not change (a direct test of D-021 label maturity); (c) live forecast == backtest forecast for the same instant (useful for M5/M6); (d) a locked selection artefact with a SHA-256 hash checked before the final scoring (endrusmah), which fits our 'final test scored ONCE' rule; (e) source provenance with an availability buffer, i.e. data usable only after the publisher workflow has finished + 6 h (endrusmah), relevant to M6 monthly runs; (f) reporting results on all rows next to a quiet-now subset, so the state-target inflation is visible; (g) a REFLECTION / corrections section stating which claims failed (mykhailoisupov's 'boosted trees failed outright' correction); (h) a per-oblast skill table showing the spread (Kamenqq: +11% to -32%). AVOID: (1) filtering the official file to level=='oblast' (gklymenko); (2) volunteer data as the target, or mixing official and volunteer across a source stop (Kamenqq v1); (3) thresholded accuracy metrics as headlines, class_weight='balanced' on a probability model, and thresholds tuned on test (yeliena-bochagova, MaksimPrykhodko); (4) splitting by row index (iloc 80/20) with no purge (MaksimPrykhodko); (5) features computed with the current row's label (hours_since_last_alert); (6) cutting long alerts using their final duration (mykhailoisupov national), which our causal 24 h rule (D-020) avoids; (7) choosing the headline baseline or the model window after seeing test results, even when disclosed (mykhailoisupov kyiv, Kamenqq); (8) keeping strong baselines out of the selection pool and then deploying a model that loses to them (endrusmah); (9) hour-of-day profiles in UTC (gklymenko) or hourly bins in Kyiv local time across DST changes (MaksimPrykhodko); our rule (UTC grid, Kyiv only for calendar features) is right.

---

<a id="pre2026_student_repos"></a>
## 9. Pre-2026 student repos (HliebOcheretianyi/AirAlert_predictions, TeamMLPythonAM2/AirAlarmsApp, shymanskyimarian-ux, sortafreel/dmbm)

*Category: peer_repo* — ISW + weather + Telegram features; publication-lag look-ahead risk.

### Basic Info

**Name**

> Pre-2026 student repos: HliebOcheretianyi/AirAlert_predictions, TeamMLPythonAM2/AirAlarmsApp, shymanskyimarian-ux/air-raid-prediction, sortafreel/dmbm

**Type**

repo (4 student / hobby repos, reviewed together as one peer group)

**Url**

> https://github.com/HliebOcheretianyi/AirAlert_predictions ; https://github.com/TeamMLPythonAM2/AirAlarmsApp ; https://github.com/shymanskyimarian-ux/air-raid-prediction ; https://github.com/sortafreel/dmbm

**Year**

> Hlieb: created 2025-03-16, last commit 2025-05-06 (pushed 2025-05-21). TeamML: created 2025-03-17, last commit 2025-05-06 (pushed 2026-01-08). shymanskyi: one-day repo, 2026-06-25 (5 commits; data only to 2022-10-15). dmbm: 2022-09-18 (5 commits, data 2022-02-25..09-15).

**Popularity**

> Checked 2026-10-17: Hlieb 0 stars, 0 forks; TeamML 2 stars, 1 fork; shymanskyi 0 stars; dmbm 4 stars. No licenses on any of the four.

**Peer review status**

> student repos / hobby projects; self-reported results only; no peer review. Two of four (shymanskyi, dmbm) report no forecast evaluation at all.

### Problem Framing

**Target type**

> Hlieb: STATE target (alert active in the hour; start floored and end CEILED to the hour, so every alert covers at least 2 hourly rows), which inflates scores. TeamML: ONSET-like target (is_alarm = 1 if an alert's start falls in that hour [t, t+1)), but evaluated with accuracy and no at-risk mask. shymanskyi: COUNT (daily national alert count, ARIMA) plus a hand-made per-oblast 'will there be an alert' table. dmbm: descriptive only (counts per hour/weekday/month), no target.

**Target definition**

> Hlieb: event_all_region(region, hour h) = 1 if any oblast-level alert interval [floor_h(start), ceil_h(end)] covers h; same-hour label, the 'forecast' for the next 24h is produced by feeding forecast weather for each future hour into the same classifier, so H is implicitly 0..24h with no lag structure. TeamML: is_alarm(city, hour h) = 1 if an alert starts in hour h (alarms joined to the weather grid on floor_h(start)); the app predicts 'probability of an alert for a selected region and N hours ahead' and 'hourly predictions for the next 24h' with hard 0/1 model.predict outputs. shymanskyi: ARIMA(7,1,1) on daily national alert counts, 7-day horizon (code commented out); the shipped weekly table (2022-10-16..22) lists one 'Yes' alert per oblast per day with a probability, start-hour window, duration and threat type, generated outside the repo code. dmbm: none.

**Spatial unit**

> Hlieb: oblast (24 incl. Kyiv City and Crimea in labels; weather by oblast centre city; Kyiv City reuses Kyiv oblast weather). TeamML: oblast via its centre city (24 'city_address' units incl. 'Kyiv oblast'). shymanskyi: national daily count + oblast table. dmbm: oblast (Kyiv City merged into Kyiv region) and Lviv region.

**At risk masking**

> None of the four. Hlieb trains and scores on all hours including hours already under alert (the state target makes this the main source of skill). TeamML does not drop hours where the oblast is already under alert; with an onset target that matters less, but there is no mask. shymanskyi/dmbm: not applicable.

### Method

**Model family**

> Hlieb: XGBoost, LightGBM (scale_pos_weight), Random Forest (class_weight balanced), Logistic Regression, SGD; final = custom stacking (XGB+RF+LGBM base, LogisticRegression meta, SMOTE on training data) pickled as 3__MUSE__v1. TeamML: LinearRegression and LogisticRegression in the notebook; deployed model = sklearn HistGradientBoostingClassifier v4 (training notebook not in the repo). shymanskyi: statsmodels ARIMA(7,1,1) on daily counts (commented out) + rule-based threat-type table. dmbm: none (descriptive statistics and animated maps).

**Features**

> Hlieb (about 1,040 columns): region_id; day_datetimeEpoch and hour_datetimeEpoch (raw time as a trend feature); ~30 Visual Crossing hourly and DAILY weather fields (temp, dew, humidity, precip, wind, pressure, cloudcover, visibility, uvindex, sunrise/sunset, moonphase, conditions, preciptype dummies); 1,000 ISW TF-IDF/PCA components from the previous day's report; event_lastDay_region (number of alert hours on the SAME calendar day, kept in X); ru_holiday, ua_holiday. event_1h_ago, event_2h_ago and alarms_in_regions were built but dropped from X. TeamML (~224 columns): hourly and daily weather; day_hour; dist_from_front (hand-coded 0..1 per city); alarm_num_atm (number of oblasts with an onset in the SAME hour, nationwide); alarm_num_region (onsets in the same oblast on the SAME day); duration_in_min of the alert itself (equal to the label; logistic coefficient 13.2, by far the top feature, later dropped); 100 ISW and 100 Telegram TF-IDF/PCA components shifted +1 day; in production also alarms_hourly (current national alert count), city_hour_score (hard-coded city x hour alarm-rate table) and holiday coefficients. shymanskyi: lags 1-7 of daily count (ARIMA). dmbm: none. No repo uses own-state features like minutes since last start/end or neighbour-oblast state.

**Ablation design**

> None in a controlled sense. Hlieb compares five model families on the same row-index fold but never ablates ISW/weather/holiday groups. TeamML drops leaky columns one at a time inside the same notebook (duration_in_min, alarm_num_atm) without reporting before/after metrics. No repo compares 'with vs without external features' on the same time-restricted sample, so the value of ISW/weather/Telegram is unproven.

### Evaluation

**Metrics**

> Hlieb: accuracy, F1, precision/recall (classification_report), confusion matrix at the default 0.5 threshold; weighted F1 for stacking. TeamML: accuracy and confusion matrix (logistic); MAE/MSE/RMSE/R^2 for the linear-regression-on-binary model. No Brier, log loss, ROC-AUC, PR-AUC, or calibration in any repo. shymanskyi and dmbm: no metrics.

**Unit of metric**

Pooled across all oblasts and hours (Hlieb, TeamML); no within-oblast metrics.

**Baseline strength**

> No explicit baselines anywhere. Implied no-skill baselines show how weak the claims are: TeamML logistic accuracy 0.8999 vs majority-class accuracy 1 - 15,016/151,874 = 0.9011, so it is no better than always predicting 'no alarm'. Hlieb XGBoost accuracy 0.903 vs majority-class 0.826 (17.4% positives in the test fold); but with a state target, persistence (alert active in the previous hour) would very likely beat it, and event_1h_ago was deliberately dropped so this was never measured. No climatology, rolling recent rate, or calibrated persistence.

**Calibration under drift**

> Not examined by any repo. The base rate is pooled 2022-2025 for Hlieb/TeamML; the Jan-2025 drone surge sits at the very end of their data and is not analysed.

**Uncertainty of gain**

None: no CIs, bootstrap, or significance tests.

**Regime coverage**

> Hlieb/TeamML: 2022-02-24 .. 2025-03-01, so they include the start of the 2025 drone surge but none of the 2025 raion/hromada reform effects (oblast-level data) and nothing of the Sep-2026 yellow/red reform. Hlieb's test fold is regional, not temporal, so regime change is not tested at all. shymanskyi: Mar-Oct 2022 only (the forecast week 2022-10-16..22 is right after the 10 Oct 2022 missile campaign began). dmbm: Feb-Sep 2022.

### Leakage & Hygiene

**Test window hygiene**

> Poor. Test folds were used for repeated model comparison and feature dropping in notebooks; hyperparameter searches (commented RandomizedSearchCV with TimeSeriesSplit on the train fold) are not separated from the test; no pre-registration, no frozen test date, no record of how many times the test was viewed.

### Results

**Headline results**

> Hlieb (test fold of 103,776 rows, 17.4% positive): XGBoost accuracy 0.903, F1 0.681 (precision 0.80, recall 0.59); LightGBM accuracy 0.865, F1 0.671; stacking (SMOTE, weighted metrics) accuracy 0.846, weighted F1 0.858, weighted precision 0.885. These do not beat a persistence baseline in any demonstrated way and are inflated by a state target, same-day leakage and a regional (not temporal) split. TeamML: logistic accuracy 0.8999, which is BELOW the majority-class rate 0.9011 (no skill); linear regression R^2 0.028; deployed HGB model has no reported test metrics. shymanskyi: no evaluation; the weekly forecast table predicts an alert for every oblast every day (168/168 'Yes'), which is trivially true for that period and uninformative. dmbm: descriptive only, e.g. Lviv region averaged 0.97 air alerts per day (Feb-Sep 2022). None of the four shows skill over a naive baseline.

### Relevance

**Takeaways for project**

> (1) State vs onset: Hlieb's state label with ceil-to-hour ends shows exactly why we keep the onset target with the at-risk mask (CLAUDE.md Target section); report persistence on both views only if we want to show the inflation. (2) External features: the ISW/Telegram/weather setups illustrate the publication-lag and oracle risks. If we ever add an ISW feature, use the report for day D only from its actual publication time (conservatively D+1 06:00 Kyiv, then convert to UTC per our rule that grid work is UTC), never full-day weather aggregates, and only forecast (not observed) weather valid at t; any such addition is a new dependency/feature group and needs Oleksandr's approval. (3) Same-day and same-hour aggregates (event_lastDay_region, alarm_num_region, alarm_num_atm) are the dominant leak class; our tests/test_leakage.py truncation test plus its negative control should include a planted 'same calendar day count' feature, since that is the most common real mistake in peer repos. (4) Row-index TimeSeriesSplit on panel data sorted by unit is a silent spatial split; our walk-forward by DATE (D-021, D-023) with purge avoids it. Add an assertion that max(train t) < min(val t) < min(test t) across all units. (5) Fits on full data (median imputation, TF-IDF/PCA, target-encoded city x hour tables) are the 'scalers/encoders fit on full data' forbidden in CLAUDE.md; climatology must be computed from train only, which we already do. (6) Accuracy at 0.5 hides no-skill models (TeamML 0.8999 vs 0.9011 majority); our primary metric BSS vs the rolling recent-rate (D-021) plus PR-AUC/base rate is the right antidote. (7) Treating partial-oblast alerts as whole-oblast (Hlieb all_region 0 -> 1) is consistent with our union rule, but without dedup and the D-020 24h causal cap it would mis-state 2025-2026 data. (8) shymanskyi's file mixes oblast/raion/hromada rows and counts them, a concrete example of why we dedup first and build the per-oblast union. (9) Nothing in these repos contradicts our design; they serve as anti-pattern references for the README's related-work section.

**Best practices**

> Worth adopting: lag text features by at least one publication cycle (TeamML's +1 day shift is the right instinct); keep a live inference path that uses the same feature-timing rules as training (both teams had train/serve skew, a warning for M5/M6); the dedup on (unit, start) and collapse of repeated Telegram announcements (TeamML, dmbm) mirror our dedup-first rule; end-to-end hourly cron deployment (TeamML) is a reference for M6 future work. Anti-patterns to avoid: state targets with ceil-rounded ends; same-day or same-hour aggregate features; using the target's own duration as a feature; observed future weather and full-day daily aggregates as predictors; median imputation or TF-IDF/PCA fit on all data, and PCA refit on the test set; row-index TimeSeriesSplit on unit-sorted panel data; raw timestamps (epoch) as features; SMOTE/class weights without recalibration; hard 0/1 outputs labelled as probabilities; accuracy/F1 at 0.5 as the only metric with no baseline; mixing naive local times with UTC epochs; forecasting 'Yes' for every unit (uninformative); unreproducible forecast tables not produced by the code.

### Other Info

**Uncertain fields (omitted above)**

- authors
- calibration
- code_available
- data_source_variant
- data_sources
- external_feature_timing
- known_label_artefacts
- leakage_handling
- preprocessing
- split_scheme

---

<a id="api_ecosystem"></a>
## 10. alerts.in.ua API + alerts-ua/alerts-in-ua-py, PaulAnnekov/uasiren (ukrainealarm)

*Category: ukraine_alerts* — New-regime data access; relevant to M6.

### Basic Info

**Name**

> Ukrainian alert API ecosystem: alerts.in.ua API (+ official Python client alerts-ua/alerts-in-ua-py) and UkraineAlarm API (api.ukrainealarm.com) with PaulAnnekov/uasiren (siren.pp.ua public wrapper) and PaulAnnekov/ukrainealarm

**Type**

document / API + client libraries (repos); data-access infrastructure, not a model

**Url**

> https://devs.alerts.in.ua/ (API docs) ; https://github.com/alerts-ua/alerts-in-ua-py (PyPI: alerts_in_ua) ; https://api.ukrainealarm.com/ (swagger behind Cloudflare, 403 to scripts on 2026-10-17) ; https://github.com/PaulAnnekov/uasiren ; https://siren.pp.ua/api/v3 ; https://github.com/PaulAnnekov/ukrainealarm ; https://github.com/UkraineAlarm/UkraineAlarm-python ; HA integration https://www.home-assistant.io/integrations/ukraine_alarm

**Year**

> alerts-in-ua-py: created 2023-02-06, v0.4.0 pushed 2026-10-13 (adds alert_level red/yellow, threats[], v2 IoT). uasiren: created 2022-05-11, last code commit 2022-05-25 (issues active through 2026-09). PaulAnnekov/ukrainealarm: last push 2022-05-03. HA 'Add air alert levels to Ukraine Alarm' PR #181558 merged 2026-09-10. Checked 2026-10-17.

**Popularity**

> alerts-in-ua-py 29 stars / 3 forks; PaulAnnekov/ukrainealarm 36 stars; uasiren 27 stars / 2 forks; FOUREX/alerts_in_ua.py (unofficial) 11 stars; Fyennyi/alerts-in-ua-php 6 stars; UkraineAlarm official generated clients 2-3 stars (all as of 2026-10-17).

**Peer review status**

> Not peer-reviewed. Operational public-alert APIs and volunteer/official client libraries; accuracy self-reported; alerts.in.ua disclaims liability and warns updates may be delayed and must not be used for critical infrastructure.

### Problem Framing

**Target type**

> Not applicable (data APIs). They expose alert intervals (history) and current state (active/IoT), from which our ONSET target is built; IoT status strings are pure STATE snapshots and cannot give onsets unless polled continuously.

**Target definition**

> Not applicable. Record unit (alerts.in.ua): one alert for one location with id, started_at, finished_at (null if open), updated_at, alert_type, alert_level (red/yellow), location_type, location_uid, location_oblast. UkraineAlarm: per region activeAlerts[] with type (AIR, ARTILLERY, URBAN_FIGHTS, ...) and activeAlertLevels[] (alertLevel Red/Yellow, createdAt).

**Spatial unit**

> alerts.in.ua: oblast, raion, hromada, city (history dump 2026-10-12: raion 14,366, hromada 1,080, city 1,072, oblast 221 rows); queried per oblast UID. UkraineAlarm/siren.pp.ua: State / District / Community regionType with regionId.

**At risk masking**

> Not applicable (APIs). For users: the history endpoint returns open alerts too (41 open in our dump, incl. Luhansk since 2022-04-04 and Crimea since 2022-12-10, and multi-year Vovchanska/Lypetska hromada alerts), so at-risk masks must apply the D-020 causal 24h cap rather than 'finished_at is null'.

### Data

**Data source variant**

> Three distinct channels, never to be mixed with each other or with Vadimkin official_data (Telegram air_alert_ua parse): (1) alerts.in.ua (own aggregation; has alert_level, threats, location_title_en, updated_at); (2) UkraineAlarm API (feeds the official 'Povitriana Tryvoha' app; key on request; Red/Yellow activeAlertLevels since the Sep-2026 reform); (3) siren.pp.ua = keyless public proxy of (2), 50 req/min per IP. All are union-of-levels-capable (oblast/raion/hromada rows) but only alerts.in.ua offers a 30-day bulk history; UkraineAlarm history is capped at 25 alerts per region.

### Method

**Model family**

Not applicable (APIs / client libraries).

**Features**

> Not applicable. Fields usable for features: alert_level (red/yellow), alert_type, location_type, started_at, finished_at, updated_at (alerts.in.ua); live-only threats[] with threat_type in {drones, ballistic_missiles, cruise_missiles, unspecified_missiles, guided_aerial_bombs, tactic_aircraft_activity, strategic_aircraft_activity, mig31k_departure, air_defense, unknown}, threat level and started_at, source_message; UkraineAlarm activeAlertLevels[] with reason and createdAt. Threat features are only causally valid if logged live at time t by our own collector.

**External feature timing**

> Live endpoints are near real-time (alerts.in.ua soft limit 8-10 req/min, hard 12 req/min per IP; history 2 req/min, not for real-time). updated_at gives a per-record change time, so a collector can reconstruct 'known at t' for ends, but not for edits made before the first fetch. UkraineAlarm via siren.pp.ua exhibited multi-minute publication lag in Sep 2026. For M6, end times observed only at the next daily pull must be treated as unknown until then (D-020 cap covers this).

**Ablation design**

Not applicable.

### Evaluation

**Split scheme**

> Not applicable. Constraint for M6: alerts.in.ua history depth is 30 days, so a monthly job must persist every pull (datastore/alerts_in_ua.csv, D-016) or history is lost; a missed month cannot be backfilled from this API.

**Metrics**

Not applicable.

**Unit of metric**

Not applicable.

**Baseline strength**

Not applicable.

**Calibration**

Not applicable.

**Calibration under drift**

> Not applicable directly. The ecosystem itself documents the regime shift: alert_level red/yellow appeared with the Sep-2026 reform (v2 IoT R/Y codes; HA PR merged 2026-09-10; alerts-in-ua-py 0.4.0 on 2026-10-13). In our dump 63% of alerts are yellow (10,559 vs 6,180 red), so an 'any level' onset target in the new regime is not comparable in base rate to the pre-reform official target; supports D-015 exploratory framing.

**Uncertainty of gain**

Not applicable.

**Regime coverage**

> alerts.in.ua history only covers a rolling 30 days, so it can cover only the post-2026-09-06 yellow/red regime from the date pulls began; it cannot cover the Jan-2025 drone surge or the Dec-2025 raion reform. UkraineAlarm regionHistory (25 alerts/region) is too short for any regime analysis.

### Leakage & Hygiene

**Leakage handling**

> Not applicable (APIs). Leakage-relevant properties: (a) history returns FINAL finished_at; using it to classify standing alerts at t leaks (D-020); (b) records can be updated after the fact (updated_at), so a dump is a post-hoc view; to be causal, keep each pull's fetch timestamp (manifest.tsv already records fetched_at_utc per UID) and dedupe by id with latest updated_at only for the training store, not for as-of-t reconstruction; (c) threats[] are point-in-time and disappear when closed, so any historical threat feature built from a later snapshot is impossible/leaky; (d) the Python client silently caches with If-Modified-Since and converts timezone; for reproducible dumps, store the raw JSON (as the project does) rather than client objects.

**Test window hygiene**

> Not applicable. Note: because the history window rolls daily, a new-regime evaluation must be pinned to a dated raw dump (data/raw/alerts_in_ua/2026-10-12T1645Z/) and never re-fetched live; re-fetching changes the window and the open-alert set.

### Results

**Headline results**

> Not applicable (no models). Verified facts (2026-10-17): alerts.in.ua history limit 2 req/min (docs), general 8-10 soft / 12 hard req/min per IP, 429 on excess, token/IP blocking for systematic abuse; only month_ago documented; our dump 16,739 records over 26 UIDs, 0 duplicate ids, 41 open, yellow 63%, 289 non-air_raid rows. siren.pp.ua is live (35 regions with alerts, fresh lastUpdate 2026-10-17 13:05 UTC) and already returns activeAlertLevels Red/Yellow; api.ukrainealarm.com swagger returns 403/Cloudflare challenge to scripts (also reported in uasiren #6, open since 2025-09).

### Reproducibility

**Code available**

> alerts-in-ua-py: MIT, active (0.4.0, 2026-10-13), sync (requests) + async clients, unit tests + opt-in live tests via ALERTS_IN_UA_TOKEN (same env var name as our project). uasiren: no license file, ~40-line aiohttp wrapper, unmaintained since 2022-05 but the siren.pp.ua service is live. PaulAnnekov/ukrainealarm: no license, unmaintained since 2022-05. UkraineAlarm-python: swagger-generated client (v3 API), key required.

### Relevance

**Takeaways for project**

> 1. Keep reading API data from the saved raw dump (CLAUDE.md data rule / D-015): the 30-day rolling window makes live re-fetch non-reproducible. 2. In load_api() (src/data.py) map to oblast via the requested UID from the filename or location_oblast name through src/regions.py, never via location_oblast_uid (wrong for 16,518 sub-oblast rows); add a raising data-quality check that each file's location_oblast is a single value matching the requested UID (D-017 item 6). 3. Filter alert_type == 'air_raid' explicitly and print the dropped count (289 in the dump); artillery_shelling/urban_fights rows would otherwise create spurious onsets in frontline hromadas. 4. Start the new-regime scored window after the earliest finished_at in the dump plus margin (current 2026-09-13 is consistent with min finished_at 2026-09-12 16:52 UTC) because of left-censoring; document this. 5. Keep open alerts (D-027) and rely on the D-020 cap; exclude Luhansk 16, Crimea 29, Sevastopol 30. 6. Red-only extra row (D-015 b): alert_level is per alert, while red threats can sit inside yellow alerts and threats[] are not in history, so state that 'red' = alert_level red, not 'missile threat'. 7. If the alerts_in_ua package is ever used (new dependency needs Oleksandr's approval), convert its Kyiv-aware datetimes back to UTC; the project's own raw-JSON reader avoids this. 8. M6 (future work, D-016): the monthly job must pull at most 2 history requests/min (24 oblast UIDs = about 12-13 min, as the 2026-10-12 dump took 15 min for 29 UIDs), run at least every ~25 days so the 30-day windows overlap, persist to datastore/alerts_in_ua.csv with fetch timestamps, dedupe by id with latest updated_at (D-027). 9. Do not substitute UkraineAlarm/siren.pp.ua as a history source: 25-alert history cap and a different channel; usable at most as a live cross-check, never mixed into a training set or metric.

**Best practices**

> Adopt: store raw JSON per UID with HTTP status, bytes and fetch time (manifest.tsv pattern already in use); keep the token in env/.env and send it as a Bearer header, not a query string (docs allow both; query strings leak into logs); respect 2 req/min for history and use If-Modified-Since for live polling; treat 404 UIDs and empty files as explicit errors or documented exclusions, not silent skips; filter by alert_type; keep open alerts with a causal cap; record API/library version and dump timestamp in run_meta.json. Anti-patterns: trusting location_oblast_uid; using finished_at IS NULL as 'currently under alert'; computing onset rates from the first day of a rolling-window dump; building threat-type features from history; mixing alerts.in.ua with UkraineAlarm or the Telegram-derived official CSV; relying on an unmaintained keyless proxy (siren.pp.ua) for anything production-like; polling faster than the documented limits (risk of token/IP ban).

### Other Info

**Uncertain fields (omitted above)**

- authors
- data_sources
- known_label_artefacts
- preprocessing

---

<a id="yellow_red_reform"></a>
## 11. Yellow/red alert reform primary documents (CabMin No.1092, ArmyInform, Euromaidan Press)

*Category: ukraine_alerts* — Criteria set weekly -> new regime itself non-stationary (D-015).

### Basic Info

**Name**

> Yellow/red air-threat-level reform: Cabinet of Ministers Resolution No. 1092 of 4 Sep 2026 ('Certain issues of optimizing population protection and responding to threats of air attack means'), amended by No. 1128 of 15 Sep 2026; announced via ArmyInform and Euromaidan Press

**Type**

> document (primary legal act + official/semi-official news coverage); defines the regime change, not a model

**Url**

> Resolution text/metadata: https://zakon.rada.gov.ua/laws/show/1092-2026-п (body returned 403 to scripts on 2026-10-17; metadata only) ; ArmyInform 2 Sep announcement: https://armyinform.com.ua/2026/09/02/zhovtyj-i-chervonyj-rivni-v-ukrayini-zminyat-systemu-opovishhennya-pro-povitryani-zagrozy/ ; ArmyInform 4 Sep 'Two levels introduced': https://armyinform.com.ua/2026/09/04/dva-rivni-povitryanyh-tryvog-zaprovadyly-v-ukrayini-yak-cze-praczyuvatyme/ (EN: https://armyinform.com.ua/en/2026/09/08/two-levels-of-air-raid-alerts-introduced-in-ukraine-how-will-they-work/) ; Euromaidan Press 4 Sep: https://euromaidanpress.com/?p=424042 ; Kyiv launch (UNN): https://unn.ua/en/amp/a-differentiated-color-coded-threat-alert-system-has-been-launched-in-kyiv ; Mykolaiv pilot: https://korabelov.info/en/?p=613036 ; MVS explanation via Ministry of Economy: https://me.gov.ua/Documents/Detail/9d4bebb9-1580-4d6e-98a4-edfac4ea3f47?lang=uk-UA ; No.1128 coverage: https://news.dtkt.ua/society/economics/114792-z-18-veresnia-diiut-onovleni-pravila-roboti-biznesu-ta-biudzetnix-ustanov-pid-cas-trivog-postanova-kmu-1128

**Year**

> 2026. Announced by President Zelensky 2 Sep 2026; Cabinet decision announced 3 Sep; Resolution No. 1092 dated 4 Sep 2026 per zakon.rada.gov.ua (some outlets say 3 Sep), published in Uriadovyi Kurier 4 Sep; Kyiv differentiated alerts from 6 Sep 2026 06:00 local; Mykolaiv oblast pilot reported 8 Sep; amendment No. 1128 of 15 Sep 2026 in force from 18 Sep 2026 (current Rada version dated 18.09.2026); MVS explanations 5 Oct and updated 14 Oct 2026. Checked 2026-10-17.

**Authors**

> Cabinet of Ministers of Ukraine (PM Serhii Koretskyi announced); President Volodymyr Zelensky (initial announcement); ArmyInform (Ministry of Defence news agency, no byline on the 4/8 Sep piece); Euromaidan Press article by Zoriana Katola; Ministry of Internal Affairs (explanatory notes published on me.gov.ua by the Ministry of Economy's security-and-defence economic policy department).

**Popularity**

> Not applicable (legal act and news). Widely covered by Ukrainian media (Mind, TSN, DOU, Ligazakon, Debet-Kredit, Kadroland, Interfax-Ukraine, Ukranews).

**Peer review status**

> Primary legal document (official act) plus official/state-media news; not peer-reviewed. The operational criteria behind each level are NOT published: they are set weekly by the military.

### Problem Framing

**Target type**

> Not applicable (regime definition). Relevance: splits the single 'air alert' STATE into two levels (yellow = drone threat; red = missile / combined / massive drone threat). For our onset target this changes what an 'onset' is: yellow and red become separate signals, a red can start during a yellow, and the any-level onset rate is a different quantity from pre-reform onsets.

**Target definition**

> Not applicable. Level definitions as reported: YELLOW = threat of attack by strike drones; RED = elevated threat of missile (incl. ballistic) or combined missile-and-drone strike, and also massive drone attacks (Kyiv: red covers 'massive drone threat', 'missile threat', 'missile-and-drone threat'). The concrete threat indicators that map to each level are set WEEKLY by the General Staff and Air Force together with the Cabinet, MoD, MVS and DSNS (State Emergency Service) and are not public. All-clear is given when none of the listed threats is recorded.

**At risk masking**

> Not applicable. Implication: the mask must follow the target level (any-level mask for any-level onset; red-only mask for red onset, where red starting during a yellow counts as an onset) as in CLAUDE.md D-015 / architecture item 4.

### Data

**Preprocessing**

> Not applicable. Implied: treat 2026-09-07 to 2026-09-12 as missing in both sources; do not concatenate pre- and post-reform series; represent alert_level explicitly; level transitions (yellow->red, red->yellow) inside one episode must be handled by the target-level setting, not by merging.

**Known label artefacts**

> (1) Criteria are set WEEKLY and not published, so the yellow/red labelling rule itself drifts week to week: the new regime is non-stationary by design (D-015 note). (2) Staggered, pilot-mode rollout (Kyiv 6 Sep with district coverage gaps; Mykolaiv 'pilot mode' 8 Sep), so cross-oblast comparability of levels in the first weeks is weak. (3) Repeated all-clear siren cancelled (siren only at alert start) and level-specific sounds planned later: changes the public signal, not necessarily the data feed. (4) Geographic narrowing of alerts is a stated goal; if implemented, per-oblast union intervals will shrink in share of time, independent of threat. (5) Behavioural/economic incentive: yellow lets business operate, red stops it, so there is pressure on how often red is declared. (6) Amendment No. 1128 (18 Sep) changed business/signal-duration rules mid-sample. None of these were 'handled' by the source; they are caveats for our exploratory section.

### Method

**Model family**

Not applicable (legal act / news).

**Features**

> Not applicable. Implication: pre-reform features (onsets_last_24h/7d, minutes_since_last_start, neighbours active) are computed on a single-level signal; after the reform their meaning changes (yellow onsets are more frequent and longer drone raids), so a frozen model sees a shifted feature distribution.

**External feature timing**

> Not applicable. Note: the weekly criteria are not published, so they cannot be used as a feature or covariate; any 'regime week' indicator would be unobserved.

**Ablation design**

Not applicable.

### Evaluation

**Split scheme**

> Not applicable. Implication: the reform date is a hard structural break; the official-data test (2026-07-27 to 2026-09-07) ends at the break, and any post-reform scoring is a transfer test, not part of the same split.

**Metrics**

> Not applicable. Implication: report calibration-in-the-large and within-oblast AUC separately for the new regime, since base rates change by construction.

**Unit of metric**

Not applicable.

**Baseline strength**

> Not applicable. Implication: the rolling 14-day recent-rate baseline adapts to the post-reform base rate within two weeks, while a frozen model does not, so recent-rate is expected to be relatively stronger after the reform.

**Calibration**

Not applicable.

**Uncertainty of gain**

> Not applicable. Implication: post-reform window is short (2026-09-13 to 2026-10-12) and its labelling rule shifts weekly, so any measured gain/loss should be treated as exploratory with wide uncertainty.

**Regime coverage**

> This document DEFINES the Sep-2026 yellow/red shift: decision 3-4 Sep 2026, Kyiv live 6 Sep, oblast pilots ~8 Sep, amendment 18 Sep. Our official data end 2026-09-07 05:28 UTC, so they contain at most ~1 day of partial post-reform Kyiv data.

### Leakage & Hygiene

**Leakage handling**

> Not applicable (document). Implication for us: do not use post-reform API data to choose features, thresholds or calibration of the headline model (no tuning on API data, D-015); do not use 'final' level labels revised after the fact; red-only target must use red-active mask built causally from data known at t.

**Test window hygiene**

> Not applicable. Implication: the new-regime section must be labelled exploratory and kept out of the headline (D-015); the official test window ends before the nationwide rollout, which keeps the headline test within one regime.

### Results

**Headline results**

> No model results (legal act). Key facts: two levels introduced by Resolution No. 1092 (4 Sep 2026); yellow = drone threat, businesses with shelter access may operate; red = missile/combined/massive threat, work stops and people go to shelters; businesses without shelters got 3 months (Ministry of Economy deadline 4 Dec 2026); level criteria set weekly by General Staff + Air Force with Cabinet, MoD, MVS, DSNS; all-clear siren repeat cancelled; Kyiv differentiated alerts from 6 Sep 2026 06:00; amendment No. 1128 in force 18 Sep 2026; No. 1129 sets railway operation by level (yellow: trains run; red: boarding and departures suspended). Euromaidan Press (4 Sep) states the business list and full criteria were not finalized and geographic targeting was not yet part of the system.

### Reproducibility

**Code available**

> Not applicable. Official text on zakon.rada.gov.ua (in force, current version 18.09.2026); body not machine-retrievable on 2026-10-17 (HTTP 403 for print view).

### Relevance

**Takeaways for project**

> (1) Treat 2026-09-07 as a hard regime break; never mix pre- and post-reform data in one training set or metric (CLAUDE.md data rule; D-007/D-015). (2) The post-reform labelling rule is set weekly by the military and is unpublished, so the new regime is itself non-stationary (D-015 note); README must state any transfer result as a fact for that window only, with interpretations as hypotheses (D-015 amended). (3) Primary new-regime target = any level onset with any-level mask; red-only onset (red during yellow counts) as an extra row (D-015 (b), architecture item 4 target_levels). (4) Expect calibration-in-the-large failure of the frozen model a priori; this justifies the conditional README conclusion 'retraining/recalibration needed after the reform' (D-015 (d)). (5) Staggered rollout (Kyiv 6 Sep, pilots ~8 Sep) plus the 7-12 Sep data hole means the first post-reform days are unreliable; starting the API window at 2026-09-13 is justified. (6) Geographic narrowing would reduce share of time under alert without a change in threat; the before/after table (D-015 (a)) should be read with this caveat. (7) Any future yellow-regime model requires the human's explicit approval (Scope).

**Best practices**

> Adopt: cite the primary act (No. 1092 + No. 1128) with dates when describing the regime break; record the rollout timeline in DECISIONS/README; keep the target-level and mask settings consistent; report post-reform results as exploratory with calibration-in-the-large; prefer adaptive baselines (rolling recent rate) as the bar in a drifting regime. Avoid: treating 'yellow' as equivalent to the pre-reform alert; using weekly-changing criteria as if fixed; claiming causal effects of the reform on attack intensity from alert counts (alert counts reflect declaration rules, not only threats); relying on unverified media statistics (e.g. 61/39 yellow/red share) in the report.

### Other Info

**Uncertain fields (omitted above)**

- calibration_under_drift
- data_source_variant
- data_sources
- spatial_unit

---

<a id="external_covariates"></a>
## 12. External covariate datasets (Kaggle Massive Missile Attacks, VIINA, DiXi Energy Map, time-machine-data)

*Category: ukraine_alerts* — Future-work features / regime-shift explanation; timing constraints.

### Basic Info

**Name**

> External covariate datasets for Ukrainian air-raid alert forecasting: (1) Kaggle 'Massive Missile Attacks on Ukraine' (piterfm), (2) VIINA 2.0 (Violent Incident Information from News Articles, zhukovyuri), (3) DiXi Group Energy Map 'massive strikes on critical infrastructure' dataset, (4) mdniprovskyi/time-machine-data (derived pipeline joining VIINA + Kaggle + alert seconds)

**Type**

dataset (1-3: primary/secondary datasets; 4: derived student/hobby data repo of pre-aggregated JSON)

**Url**

> Kaggle: https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine (overview notebook https://www.kaggle.com/code/piterfm/massive-missile-attacks-on-ukraine-data-review) ; VIINA: https://github.com/zhukovyuri/VIINA (paper doi:10.1016/j.jce.2023.06.003) ; DiXi Energy Map dataset: https://map.ua-energy.org/en/datasets/9091d6f9-564f-434a-a9d2-bba9657ca2c1 (now 301-redirects to energy-map.info; page is JS-rendered) ; time-machine-data: https://github.com/mdniprovskyi/time-machine-data

**Popularity**

> Kaggle: 138 votes, 22,592 downloads, 49,225 views, 18 notebooks, usability 1.0; cited by BBC, USA Today, CSIS, War Quants. VIINA: 360 GitHub stars, JCE 2023 paper. Energy Map: portal claims 420+ datasets; strike dataset widely quoted by Interfax-Ukraine in DiXi reports. time-machine-data: 0 stars.

**Peer review status**

> Kaggle: self-curated dataset, not peer-reviewed (but transcribes official military reports). VIINA: peer-reviewed methodology paper (Zhukov 2023, Journal of Comparative Economics); data itself is ML-classified news, self-reported accuracy tables in README. DiXi Energy Map: NGO/think-tank compilation, not peer-reviewed. time-machine-data: unreviewed derived repo, no README, no license.

### Problem Framing

**Target type**

> Not applicable: these are covariate sources, not forecasting studies. Relevant to our ONSET target only as candidate exogenous features (attack intensity, front activity) and as explanation of regime shifts in onset rate. Note time-machine-data's 'time-under-alert' metric is a STATE aggregate (seconds under alert per city-day), not onsets.

**Target definition**

> Not applicable. Kaggle unit = one attack record (time_start, time_end, model, launch_place, target, launched, destroyed, not_reach_goal, still_attacking, affected_region, ...). VIINA unit = one geocoded news report (date, time HH:MM of report, ADM1_NAME oblast, lat/lon, GEO_PRECISION, source, url, text) with BERT labels (t_airstrike, t_uav, t_aad, t_airalert, t_artillery, ...; actor a_rus_init, ...). Energy Map = daily counts of missiles/drones fired and shot down during massive strikes. time-machine-data = city x calendar-date (Europe/Kyiv) records: airAttackRecorded, viinaEventCount, nightRaid (00:00-07:00), missiles, attackDrones, civilianDeaths, airAlertSeconds, explosionReports.

**Spatial unit**

> Kaggle: national per attack, with free-text target/affected_region (city, oblast, 'direction' or all Ukraine) - not a clean oblast panel. VIINA: populated place / point with ADM1 (oblast) name+code; control data at GeoNames (33,141) or KATOTTH (29,724) places. Energy Map: national daily. time-machine-data: 23 canonical cities (oblast capitals; exact-city geocode only).

**At risk masking**

> Not applicable (no forecasting target). For our use: any join must happen on the hourly oblast grid AFTER our at-risk mask; covariates do not change which rows are masked.

### Data

**Data sources**

> Kaggle: official UA Air Force Command and General Staff daily reports since Oct 2022 (massive strikes) plus some single shot-down UAVs; companion table missiles_and_uavs.csv (category, origin, guidance, unit cost). VIINA: 16 UA/RU outlets (24tv, Espreso, Forbes UA, Interfax-UA, KP, Liga, Liveuamap, Militarnyi, Mediazona, Meduza, NV, NG, NTV, Ukrainska Pravda, RIA, UNIAN), scraped every 6 h, geocoded via Yandex/OSM; control layers from DeepStateMap, ISW, Wikipedia; yearly files 2022-2026. Energy Map: official Armed Forces reports, 2022-09-11 to 2024-11-17 (listed). time-machine-data: VIINA + Kaggle + OHCHR casualty floors + air-alarms.in.ua explosion reports + an alert-seconds file + GeoConfirmed geojson; 2022-02-24 to 2026-08-31.

**Preprocessing**

> Kaggle: if only destroyed is published, launched := destroyed as a lower bound (status_data flags it; 'hidden' = not published); null = unknown. VIINA: 'one-per-day' filter (event_1pd) merges same actor+tactic reports in the same place on the same day; manual inspection of geocodes. time-machine-data: VIINA attack rule = Russian initiator AND (airstrike OR UAV), exact-city geocode, max casualty count per location/date, weapons attributed only when a single city/oblast is confirmed; null vs 0 explicitly distinguished; no extrapolation.

### Method

**Model family**

> Not applicable (datasets). Downstream use would be extra columns in our GBM/LR onset model, or a regime-shift explanatory analysis (descriptive regression of weekly onset rate on weekly launched drones).

**Features**

> Candidate features, all lagged so known at t: (1) Kaggle: launched/destroyed drones and missiles in the last 24h/7d nationally (by category Shahed-type UAV vs cruise vs ballistic), attacks completed before t; rolling 30-day drone launch rate as a regime indicator. (2) VIINA: count of t_airstrike/t_uav/t_artillery reports per oblast in the last 24h/7d with report time < t; frontline proximity / share of oblast places CONTESTED or RU from control data (slow, daily). (3) Energy Map: count of massive strikes in last 30d (only to 2024). (4) time-machine-data: daily city-level attack flags - only usable as day-lagged features for 23 cities. Avoid VIINA t_airalert (target proxy).

**Ablation design**

> Not applicable (no study). For our project: any covariate ablation must use the same time-restricted sample - Kaggle starts Oct 2022, Energy Map ends Nov 2024, time-machine-data ends Aug 2026, VIINA control files are yearly - so compare model with vs without covariates on the intersection period only, with identical train/val/test cut-offs.

### Evaluation

**Split scheme**

> Not applicable. Coverage vs our splits: Kaggle covers train (from 2022-10) and the full test window, but with the 2026-08-10 reporting break; VIINA covers everything; Energy Map does not cover validation or test; time-machine-data stops 2026-08-14/20/29 depending on metric, i.e. mid-test - not usable for the frozen test.

**Metrics**

Not applicable (datasets).

**Unit of metric**

Not applicable.

**Baseline strength**

> Not applicable. Relevant point: the rolling recent-rate baseline (D-021) already absorbs slow regime shifts like the Jan-2025 drone surge that Kaggle launch counts would explain, so external intensity features are unlikely to beat it unless they lead the alert process by hours.

**Calibration**

Not applicable.

**Calibration under drift**

> Useful for EXPLAINING drift, not for calibration: Kaggle monthly launched-UAV totals document the large rise in drone volume in 2025-2026 (BBC: attacks doubled after Jan 2025), which is a plausible cause of base-rate shifts between train and test and of the yellow (drone) dominance after the Sep-2026 reform. Stated as hypothesis per D-015.

**Uncertainty of gain**

Not applicable.

**Regime coverage**

> Kaggle spans the Jan-2025 drone surge and the 2026-08-10 reporting change, and is current to 2026-10-17, so it overlaps the new yellow/red regime (2026-09-13 onward) - the only covariate that could descriptively compare drone volume before vs after the reform. VIINA spans all regimes. Energy Map covers 2022-2024 only. time-machine-data ends before the reform.

### Leakage & Hygiene

**Leakage handling**

> Main leakage risks if adopted: (1) event-time vs availability-time: Kaggle time_start/time_end and VIINA report time must be shifted to when the record was observable; (2) retroactive revision: Kaggle versions and VIINA 'latest' files are rewritten, so backtests use future-corrected values - the leakage truncation test (tests/test_leakage.py) cannot catch this because the file itself is post-hoc; (3) VIINA t_airalert and same-hour UAV news are near-copies of the label; (4) daily aggregates (time-machine-data, Kaggle per-day) read across the whole calendar day including hours after t; (5) whole-file statistics (e.g. normalising launch counts by series max) fit on test. Mitigation: fixed conservative lag (>= 24 h for daily data), features computed only from records with availability_time <= t, add each covariate to the truncation test.

**Test window hygiene**

> Not applicable. For our project the covariates would have to be chosen before seeing final-test numbers; adding them post-M4 would be a new milestone requiring Oleksandr's approval and a new dependency/data source decision.

### Results

**Headline results**

> No forecasting results (datasets). Descriptive facts: Kaggle v215 (2026-10-17), 916 KB, CC BY-NC-SA 4.0, two tables; reporting of some missile types stopped 2026-08-10. VIINA 2.0: daily updates, ODbL, minute-precision report time, oblast ADM1 codes. DiXi: 25 massive missile-drone attacks on energy Sep 2022-Sep 2024 (>1,400 missiles, ~500 UAVs); early-2026 report: >= 64 massive energy attacks since Feb 2022 with ~12,700 UAVs and ~2,900 missiles (headline elsewhere says 12,900 UAVs - inconsistent). time-machine-data: 2026 records 913 city-days (to 2026-08-20) of attack flags; mostly null missile/drone attributions.

### Relevance

**Takeaways for project**

> 1) Do NOT add any of these to the frozen M4 model: CLAUDE.md forbids new data/dependencies without Oleksandr's approval, and the features must be computable from data with timestamp <= t, which none of them guarantees without vintages. Log as FUTURE WORK. 2) Best use is explanatory (D-015 hypotheses): plot Kaggle weekly launched UAVs vs our national weekly onset rate to explain the Jan-2025 surge and the post-reform yellow-dominated regime; state as hypothesis, not cause. 3) Kaggle's 2026-08-10 reporting break falls inside our final test window: any feature from it would shift distribution mid-test. 4) If ever used as features: shift to availability time with a conservative >= 24 h lag, aggregate in UTC (not Kyiv-day), map oblast names only via src/regions.py (no fuzzy matching, D-017), and extend tests/test_leakage.py with a negative control that uses un-lagged event times. 5) Never use VIINA t_airalert (label proxy). 6) Energy Map and time-machine-data do not cover the test window - discard for modelling. 7) Mixing sources: keep covariates out of the new-regime exploratory scoring unless the same lag rule applies in both periods.

**Best practices**

> Adopt: explicit availability timestamps per external record; null-vs-zero distinction (as time-machine-data does); conservative fixed lags when no vintage archive exists; ablation on the common coverage period; snapshot/version pinning (Kaggle version number, VIINA download date) recorded in run_meta.json. Avoid: joining by event time (oracle); daily-local aggregates on an hourly UTC grid; treating imputed lower bounds (Kaggle launched := destroyed) as true counts; using news-derived alert labels; relying on unlicensed/unversioned derived repos (time-machine-data) instead of primary sources; claiming causal explanation of regime shifts from correlated intensity series.

### Other Info

**Uncertain fields (omitted above)**

- authors
- code_available
- data_source_variant
- external_feature_timing
- known_label_artefacts
- year

---

<a id="btscs_hazard"></a>
## 13. Beck, Katz & Tucker 1998 'Taking Time Seriously' + Carter & Signorino 2010 'Back to the Future'

*Category: methods* — Discrete-time hazard / duration dependence; justifies time-since-last features.

### Basic Info

**Name**

> Beck, Katz & Tucker (1998) 'Taking Time Seriously: Time-Series-Cross-Section Analysis with a Binary Dependent Variable' + Carter & Signorino (2010) 'Back to the Future: Modeling Time Dependence in Binary Data' (plus Beck 2010 'Time Is Not a Theoretical Variable' and the Carter-Signorino reply)

**Type**

> method family (two peer-reviewed methods papers on discrete-time hazard / duration dependence in binary panel data)

**Url**

> BKT 1998: https://doi.org/10.2307/2991857 (AJPS 42(4):1260-1288); author PDF: https://websites.umich.edu/~franzese/BeckKatzTucker.TakingTimeSeriously.AJPS1998.pdf ; working paper 'Beyond Ordinary Logit' (1997): https://authors.library.caltech.edu/80367/ . Carter & Signorino 2010: https://doi.org/10.1093/pan/mpq013 (Political Analysis 18(3):271-292); https://www.cambridge.org/core/journals/political-analysis/article/back-to-the-future-modeling-time-dependence-in-binary-data/9E4BCC2A63726C4ECD63F236C49AF9FA ; web appendix with R/Stata code: https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S1047198700012456/resource/name/S1047198700012456sup001.pdf

**Year**

> 1998 (BKT; working paper 1997); 2010 (Carter & Signorino, online 15 Jun 2010; Beck's comment and the authors' reply appeared in the same 2010 issue)

**Authors**

Nathaniel Beck, Jonathan N. Katz, Richard Tucker (1998); David B. Carter, Curtis S. Signorino (2010)

**Peer review status**

peer-reviewed (American Journal of Political Science; Political Analysis)

### Problem Framing

**Target type**

> Onset (event start). In the canonical application (militarized interstate dispute onset in dyad-years, from Oneal & Russett 1997), the dependent variable is the START of a new dispute. Years of an ongoing dispute after its first year are dropped, so the unit is not 'at risk' of a new onset in those years. This is a hazard (onset) target, not a state target, so it matches our project's target type.

**Target definition**

> y_it = 1 if an event starts for unit i in discrete period t (here year t), else 0. The horizon is one discrete period: H = 1 interval of the grouping (a year in BKT). BKT show that this binary TSCS set-up is identical to grouped (discrete-time) duration data: P(y_it = 1 | no event since last one) is a discrete hazard h(t - t0). With a cloglog link this is exactly a grouped continuous-time Cox/proportional-hazards model. A logit link is a close approximation when events are rare.

**Spatial unit**

> Cross-sectional unit = dyad (country pair) in BKT and in most replications. C&S also replicate country-level and organisation-level data (Crowley & Skocpol 2001 on US civic associations; Palmer, London & Regan 2004). No geographic grid.

**At risk masking**

> Yes, in the canonical application: ongoing-event periods are excluded and only onset periods count, so the risk set is units not currently in an event. This is the discrete-time-hazard version of our D-rule 'rows already under alert at t are masked'. BKT discuss that the counter of 'peace years' restarts after each event ends. That makes the risk set and the time-since counter depend on knowing when the previous event ENDED. In our setting the end must be observed by t (D-020 causal 24h cap).

### Data

**Data source variant**

> Not applicable (no air-alert data). The methods are generic for binary panels where an event can recur within a unit.

**Preprocessing**

> Construct a per-unit counter of periods since the last event ('peace years'), which resets after each event. Drop ongoing-event periods after onset. Handle left censoring: the counter at the start of the panel is unknown, because events before the observation window are not seen. BKT note this issue and use the panel start (or an earlier known event) as the origin. Optionally add the number of previous events (a repeated-failure covariate).

**Known label artefacts**

> Not about alerts. Analogous issues they raise: (1) left-censored duration counters at series start, the analogue of our 2022-03-23 start where the first 'time since last end' is unknown; (2) ties and the coarseness of grouping, since a yearly grid hides within-period timing (our hourly grid hides within-hour timing, and multiple sub-oblast onsets within an hour collapse to one); (3) with time dummies, separation arises at durations where all observations are 0 (or 1). Those rows are dropped by logit software or yield infinite coefficients, the problem C&S highlight; (4) events whose end is ambiguous, which shift the counter. None of these papers has alert-specific artefacts such as 30-min ends, standing alerts or recording gaps.

### Method

**Model family**

> Discrete-time hazard via binary GLM (logit, or cloglog for exact grouped proportional hazards). Duration dependence is modelled in three ways. (a) BKT: a full set of time-since-last-event dummies (a non-parametric baseline hazard), or a natural cubic spline of the counter (BKT used 3 knots, the best smoother available in Stata then). (b) C&S: a cubic polynomial t, t^2, t^3 of time since last event. (c) C&S also compare auto-smoothing methods (GAM-type splines) and LOWESS.

**External feature timing**

> Not applicable. Covariates are annual and lagged one period in the application, so they are observed before the outcome period.

### Evaluation

**Split scheme**

> No out-of-sample or walk-forward evaluation. Both papers estimate in-sample (inference-oriented political science). C&S evaluate methods by Monte Carlo recovery of known hazard shapes.

**Metrics**

> In-sample coefficients, standard errors, likelihood-ratio tests, and recovery of the true baseline hazard in simulation (bias/MSE of the fitted hazard curve). C&S compare logit and cloglog fits in the appendix. No Brier, AUC or PR-AUC.

**Unit of metric**

Not applicable (no predictive metric). Inference is pooled across units.

**Baseline strength**

> The implicit baseline is ordinary pooled logit that ignores duration dependence. Their main finding is that it gives over-confident standard errors and biased coefficients. No climatology or rolling-rate forecasting baseline.

**Calibration**

> Not addressed as forecast calibration. C&S check fit of the baseline hazard shape and note logit vs cloglog differences are small for rare events.

**Calibration under drift**

> Not addressed. The methods assume a stable baseline hazard in t across the panel, apart from covariates. Calendar-time trends are a separate issue: C&S's appendix tests the polynomial and splines with a time-trended covariate. Beck (2010) argues that duration terms are a stand-in for unmodelled processes. That warns that a fitted hazard shape may not transfer when the process changes, for example after the Sep-2026 yellow/red reform.

**Uncertainty of gain**

Standard errors and likelihood-ratio tests only. No forecast skill CI.

**Regime coverage**

> Not applicable to air alerts. Methodologically they assume a stationary duration-dependence shape. Regime shifts would need interactions of t with period indicators (non-proportional hazards in calendar time). C&S say their method makes such interactions straightforward.

### Leakage & Hygiene

**Leakage handling**

> Not a forecasting paper, so leakage is not discussed in ML terms. The construction is causal by design: the counter at period t uses only the timing of past events, so it is a legitimate 'known at t' feature if (i) the end of the previous event is known by t and (ii) no future information sets the counter. Our project-specific traps: (1) 'time since last END' needs the end to be observed by t. Under D-020 an alert still running is either active (masked) or past 24h (standing). The end of a standing alert is not known at t, so the counter must use the causal end (min(observed end, start+24h)) and never the final finished_at. (2) Left censoring at series start and after the 2026-08-30 to 09-01 gap: the counter must be NaN or flagged, not computed as if no alert happened during the gap (D-013). (3) Time dummies or splines fit on the full data (knots chosen from full-data quantiles) are a mild leak. Knots or bins should be chosen on train only, in line with the 'no scalers fit on full data' rule.

**Test window hygiene**

> Not applicable (in-sample inference). Note: BKT's diagnostic (joint significance of duration terms) can be done on train/validation only, keeping the final test untouched.

### Relevance

**Takeaways for project**

> 1) Theoretical justification for the own-state features: our hourly per-oblast onset task is exactly BKT's binary TSCS = grouped duration data. P(onset in (t, t+1h] | not under alert at t) is a discrete-time hazard, so minutes_since_last_end and minutes_since_last_start are the duration-dependence terms BKT say must be included. Without them a pooled classifier assumes hours are independent, which they are not. 2) The at-risk mask (target rule: drop rows under alert at t) is the risk-set definition of a discrete hazard model, the same as BKT dropping ongoing-dispute years. Cite BKT in the README to explain why masking is principled, not a convenience. 3) Counter reset and causal end: BKT's counter restarts at the event END. Ours must use the causal end under D-020 (an alert stops counting at start+24h if no end is observed by then). Never use the final finished_at. Add a leakage-test case for that. 4) Left censoring: the first alert history of each oblast (2022-03-23) and the 2026-08-30 to 09-01 recording gap (D-013) make the counter unknown. Set it to NaN or flag it, which BKT and the survival literature support. Do not fill it with large values as if there were peace. 5) Functional form: for a GBM, raw minutes_since_* is enough (trees approximate the hazard non-parametrically). For a logistic baseline or interpretable model, use log(1 + minutes) or C&S's cubic polynomial / a natural spline with train-only knots. Avoid one-hot time dummies at fine resolution (separation, C&S). 6) Repeated events: BKT's 'number of prior events' maps to onsets_last_24h / 7d. These capture self-excitation (clustering of waves) that a single time-since counter misses (link to Hawkes-type models). 7) Link: with H = 1h and rare onsets in rear oblasts, logit ~ cloglog. If H becomes configurable and large, cloglog is the exact grouped-hazard link. Optionally note this when H > 1. 8) Non-proportional hazards: C&S recommend t x covariate interactions. The analogue is letting the time-since effect differ by group (frontline vs rear vs Kyiv City) or by hour of day. A GBM gets this for free; a logistic baseline needs explicit interactions. 9) Diagnostic / ablation: reproduce BKT's test as an ablation on the SAME masked train/validation rows: model without vs with time-since features, compared on validation Brier/BSS (never the final test). That gives empirical evidence that duration dependence matters, rather than relying only on feature importance. 10) Beck's 2010 caution: the fitted hazard shape is a reduced-form proxy for unobserved attack dynamics. After the Sep-2026 yellow/red reform the shape may change, so the D-015 transfer section should say a failure of time-since effects to transfer is expected, not a contradiction.

**Best practices**

> Adopt: (a) treat the onset task explicitly as a discrete-time hazard with a proper risk set (mask rows under alert); (b) include time since last event (end and/or start) as a core feature, causally constructed; (c) smooth duration terms: cubic polynomial or natural spline for linear models, raw or log values for trees; choose knots/bins on train only; (d) include a count of recent events for multiple-failure / self-exciting dynamics; (e) test duration dependence by ablation on an identical sample; (f) handle left censoring and data gaps explicitly (NaN or flag); (g) consider cloglog when the horizon is coarse; (h) allow non-proportional effects (interactions with group or calendar). Avoid: (i) ordinary pooled logit/classifier with no temporal terms, treated as if rows were independent; (ii) fine-grained time dummies that cause separation and dropped rows; (iii) counters reset by an end time that is not yet observed (leakage), or that silently run through recording gaps; (iv) interpreting the fitted hazard curve causally ('time is not a theoretical variable'); (v) keeping ongoing-event rows in an onset model, which conflates state persistence with onset and inflates scores; (vi) assuming the duration-dependence shape is stable across regime changes without checking.

### Other Info

**Uncertain fields (omitted above)**

- ablation_design
- code_available
- data_sources
- features
- headline_results
- popularity

---

<a id="hawkes_conflict_crime"></a>
## 14. Self-exciting point processes: Mohler et al. 2011, Lewis et al. 2012 (Iraq), Zammit-Mangion et al. 2012, Cseke et al. 2016, Euromaidan Hawkes 2024

*Category: methods* — Self-excitation analogs; no Hawkes study of UA alerts exists.

### Basic Info

**Name**

> Self-exciting point processes for crime and conflict: Mohler et al. 2011 (crime/ETAS), Lewis et al. 2012 (Iraq civilian deaths), Zammit-Mangion et al. 2012 (Afghan War Diary), Cseke et al. 2016 (sparse inference for spatio-temporal LGCP), Bahid et al. 2024 (Euromaidan Hawkes)

**Type**

method family (five peer-reviewed papers)

**Url**

> Mohler 2011: https://doi.org/10.1198/jasa.2011.ap09546 ; Lewis 2012: https://www.math.ucla.edu/~bertozzi/papers/iraq.pdf (CAM report https://ww3.math.ucla.edu/camreport/cam10-38.pdf) ; Zammit-Mangion 2012: https://pmc.ncbi.nlm.nih.gov/articles/PMC3411944 ; Cseke 2016: https://arxiv.org/abs/1305.4152 (JASA DOI 10.1080/01621459.2015.1115357) ; Bahid 2024: https://arxiv.org/abs/2405.12253 (PLOS ONE 19(5): e0301639)

**Year**

> 2011 (Mohler, JASA 106(493):100-108); 2012 (Lewis, Security Journal 25(3):244-264); 2012 (Zammit-Mangion, PNAS 109(31):12414-12419); 2016 (Cseke, JASA 111(516):1746-1763); 2024 (Bahid, PLOS ONE)

**Authors**

> Mohler, Short, Brantingham, Schoenberg, Tita (2011); Lewis, Mohler, Brantingham, Bertozzi (2012); Zammit-Mangion, Dewar, Kadirkamanathan, Sanguinetti (2012); Cseke, Zammit-Mangion, Heskes, Sanguinetti (2016); Bahid, Kutsenko, Rodriguez, White (2024)

**Peer review status**

peer-reviewed (JASA, Security Journal, PNAS, JASA, PLOS ONE)

### Problem Framing

**Target type**

> Event intensity (count/rate of new events), i.e. an ONSET-type target by construction: a Hawkes/ETAS model predicts the conditional rate of new event arrivals lambda(t, s | history). There is no 'state' (ongoing) label, so state-target inflation does not arise. Cseke/Zammit-Mangion model a latent log-Gaussian Cox intensity (counts per cell per time step), not explicit self-excitation, but still a count/onset target.

**Target definition**

> Mohler 2011: lambda(t,x,y) = mu(x,y) + sum over past events of g(t - t_i, x - x_i, y - y_i) (ETAS-style branching); forecasts are next-day intensity per 150 m grid cell, ranked to flag hotspots. Lewis 2012: temporal Hawkes lambda(t) = mu(t) + sum k*omega*exp(-omega*(t-t_i)) on daily civilian-death event counts per district, with three variants for a time-varying background mu(t). Zammit-Mangion 2012: discrete-time spatio-temporal LGCP, monthly/yearly event counts on a spatial basis over Afghanistan; forward prediction of 2010 counts from 2004-2009. Cseke 2016: same LGCP class, sparse discretised state, intensity reconstruction. Bahid 2024: multivariate Hawkes over Ukrainian oblasts for daily protest events, 2013. None uses a 1-hour binary onset label; horizons range from one day to one year.

**Spatial unit**

> Mohler: grid cells (~150 m) in Los Angeles (San Fernando Valley burglary). Lewis: four Iraqi districts (Karkh, Mosul, Fallujah, Najaf), modelled separately. Zammit-Mangion/Cseke: continuous space on a basis/grid over Afghanistan (province-level summaries). Bahid: Ukrainian oblasts incl. Kyiv (multivariate, cross-oblast excitation).

**At risk masking**

> Not applicable in the same sense: point-process likelihoods are defined over the full timeline and count arrivals, not states. There is no 'already under event' state because events are instantaneous. For alerts (events with duration) a Hawkes onset model would need an explicit choice: either treat onsets as points and ignore duration (intensity can be positive while an alert is active), or censor intensity during active alerts, which is the analogue of our at-risk mask. None of these papers addresses this.

### Data

**Data source variant**

> Not applicable (no Ukrainian air-raid alert data). All datasets are event logs with reporting biases (police reports, media-based IBC counts, military logs, protest monitors). Bahid 2024 is the only Ukrainian, oblast-level example, but the events are protests, not alerts.

**Known label artefacts**

> Generic issues these papers flag that transfer to alerts: (1) tied timestamps from coarse time binning (daily data) distort Hawkes kernel estimation; our alerts have minute timestamps but 113,845 exact duplicate rows must be removed first, otherwise duplicates look like extreme self-excitation (CLAUDE.md data rule: deduplicate first). (2) Reporting/collection artefacts (IBC media coverage, military logging intensity) are confounded with true intensity; analogous to the 2025 raion/hromada reform, which multiplies alert rows per oblast and would inflate a naive Hawkes branching ratio unless intervals are unioned per oblast first. (3) Non-stationary background: Lewis shows a constant mu wrongly attributes trend to self-excitation; analogous to the Jan-2025 drone surge and the Sep-2026 yellow/red reform. (4) Bahid needed a spike threshold to fit, i.e. results are sensitive to event-definition choices. None of the papers deals with event durations, so standing alerts (D-020) and the Aug-30 to Sep-1 recording gap have no direct analogue; a gap must be handled as an unobserved window in the likelihood, not as zero events.

### Method

**Model family**

> Hawkes / ETAS self-exciting point processes (Mohler 2011 non-parametric stochastic-declustering EM with kernel density estimates of background and triggering; Lewis 2012 parametric exponential-kernel Hawkes with time-varying background; Bahid 2024 multivariate Hawkes with oblast interaction matrices based on distance vs political/voting affinity). Spatio-temporal log-Gaussian Cox processes with integro-difference dynamics (Zammit-Mangion 2012; Cseke 2016 adds sparse expectation-propagation / message passing plus structured variational Bayes for parameters).

**Features**

> Point-process models have no feature table; the analogues are: (a) background rate mu - Mohler spatial KDE, Lewis constant / piecewise / smoothed time-varying mu, Bahid per-oblast mu; maps to climatology + recent-rate baselines; (b) self-excitation kernel g(t - t_i) - exponential decay in time (Lewis: excitation lasts at most 2-6 weeks; Mohler: near-repeat on the scale of days and ~100s of metres); maps to minutes_since_last_start and exponentially-weighted onset counts; (c) cross-excitation between units - Bahid's oblast-to-oblast matrix (political affinity beat geographic distance; Kyiv activity drove nationwide dynamics); maps to neighbors_active_at_t and national_active_count_at_t; (d) external covariates - Bahid adds government use of force and injury counts as exogenous excitation; Zammit-Mangion uses spatial diffusion/relocation dynamics. No calendar features in these papers.

**External feature timing**

> Bahid 2024 uses observed (same-period) government-force and injury counts as covariates in an in-sample fit; these are not forecast-time-safe in a real-time setting and would be oracle features if used for prediction. The other papers use only past events (fully causal by construction of the Hawkes conditional intensity). For our project: any Hawkes-style feature is causal only if computed from onsets with start time <= t.

### Evaluation

**Metrics**

> Mohler 2011: fraction of next-day crimes captured in the top-k% of flagged cells (hit-rate vs area curve), compared with prospective hotspot maps. Lewis 2012: log-likelihood/AIC and estimated branching ratio. Zammit-Mangion 2012: posterior predictive coverage of 2010 counts (claims 'strikingly statistically accurate' forward prediction). Cseke 2016: approximation accuracy vs MCMC, runtime. Bahid 2024: NLL and AIC. None reports Brier, BSS, ROC-AUC or PR-AUC.

**Unit of metric**

> Mohler: pooled over the city grid; Lewis: per district; Zammit-Mangion: pooled/aggregated spatial counts; Bahid: pooled likelihood over all oblasts.

**Baseline strength**

> Mohler 2011 beats a prospective hotspot (recency-weighted KDE) baseline, which is a strong recent-rate-type baseline; reported gains are modest in absolute crime capture. Lewis 2012 explicitly shows that a constant background is a weak baseline and that self-excitation share drops when background is allowed to vary - i.e. part of 'self-excitation' is really a slowly changing recent rate. Zammit-Mangion and Bahid do not compare against a rolling recent-rate or climatology forecaster. None uses calibrated persistence.

**Calibration under drift**

> Lewis 2012 is the most relevant: it shows the background rate in Iraq is non-stationary (surge periods) and that ignoring this inflates the estimated self-excitation fraction. No paper tests calibration-in-the-large on a later regime. Bahid finds self-excitation already present before Euromaidan and intensifying during it - a parameter shift across regimes, which implies a fitted kernel would need refitting after a regime change.

**Uncertainty of gain**

> No block bootstrap or Diebold-Mariano test on forecast-skill differences. Bayesian papers give posterior uncertainty on parameters/intensity; Lewis/Bahid give likelihood-based comparisons only.

**Regime coverage**

> Not applicable to UA alert regimes. Within their domains: Lewis spans the 2006-2007 Iraq surge (non-stationary background); Zammit-Mangion forecasts 2010 (escalation year) from 2004-2009; Bahid spans pre-protest to protest onset in 2013.

### Leakage & Hygiene

**Leakage handling**

> Hawkes conditional intensity is causal by construction (depends only on events before t), so feature leakage is structurally hard. Remaining risks visible in these papers: (1) parameters (mu, kernel, branching ratio) fitted on the full period and then used to 'explain' the same period - in-sample (Lewis, Bahid, Cseke); (2) non-parametric background KDEs (Mohler) must be fitted only on the past for each forecast day - Mohler does a prospective fit; (3) Bahid's exogenous covariates are contemporaneous. For our project the analogues are D-021 (fit on train only, freeze), the purge rule at cut-offs, and the truncation leakage test: an exponentially-decayed onset count must give identical values when the data are truncated at t.

**Test window hygiene**

> No pre-registration in any paper. Zammit-Mangion 2012 has a clean one-shot forward test (2010 held out). Mohler uses a rolling prospective evaluation. Lewis and Bahid are explanatory model comparisons without a held-out test.

### Relevance

**Takeaways for project**

> 1) Self-excitation is the right mental model for alert onsets: an onset raises the short-term onset probability in the same and nearby oblasts, decaying over hours. Our D-017 own-state features (minutes_since_last_start, onsets_last_24h/7d) and spatial features (neighbors_active_at_t, national_active_count_at_t) are a discretised, binary-target approximation of a multivariate Hawkes intensity. A cheap, approved-scope extension is an exponentially-decayed onset count with 2-3 fixed half-lives (e.g. 1h, 6h, 24h), computed from starts <= t - stays within 'features from data <= t' but adding features may need human approval per CLAUDE.md. 2) Lewis 2012 warning: without a time-varying background, self-excitation absorbs trend. Our rolling 14-day recent-rate baseline (D-021) is exactly the time-varying background; the model must beat it, not a constant climatology, to claim any excitation signal. 3) Bahid 2024: cross-unit excitation need not follow geography; Kyiv dominated. For alerts, wave-level national coupling (missile/drone waves cross many oblasts) is likely stronger than neighbour adjacency - keep national_active_count_at_t and report per group (Kyiv City / frontline / rear). 4) Dedup first (CLAUDE.md data rule: 113,845 duplicates) and union admin levels per oblast before any excitation statistic; duplicated or raion-split rows masquerade as self-excitation and inflate any branching ratio. 5) Point processes have no duration; alerts do. Our at-risk mask (exclude rows already under alert) and D-020 24h causal cap are necessary additions that the Hawkes literature does not supply. 6) The recording gap must be treated as unobserved (D-013): in Hawkes terms, the likelihood/compensator should skip the gap, and decayed counts spanning it should be NaN/flagged. 7) Regime shifts (Sep-2026 yellow/red) change parameters (Bahid: excitation intensified with the regime); the D-015 calibration-in-the-large check on API data is the right test, and a failed transfer implies refit, consistent with the conditional conclusion rule. 8) Do not add a full Hawkes model as a new model family without explicit approval; at most mention it as future work or as a feature-engineering justification in the README.

**Best practices**

> Adopt: causal-by-construction intensity features (only past onsets); time-varying background (rolling rate) as the null against which excitation is judged; separate in-sample explanation from out-of-sample forecast skill (Zammit-Mangion's one-shot held-out year is the model); prospective day-ahead re-fitting as in Mohler maps to the optional D-014 weekly refit row; report a branching-ratio-like descriptive (share of onsets within X hours of a previous onset) as an EDA fact, not a model claim; residual checks (time-rescaling) as a calibration analogue. Avoid: judging models by in-sample likelihood/AIC only (Lewis, Bahid); contemporaneous exogenous covariates (Bahid's force/injury counts) as predictors; constant background (overstates self-excitation); fitting background KDEs/parameters on the whole period then reporting forecast skill; ignoring tied/duplicate timestamps; treating data gaps as zero events; claiming causal 'contagion' from a fitted kernel - excitation is a statistical clustering summary and common shocks (attack waves) produce the same signature.

### Other Info

**Uncertain fields (omitted above)**

- ablation_design
- calibration
- code_available
- data_sources
- headline_results
- popularity
- preprocessing
- split_scheme

---

<a id="csep_etas"></a>
## 15. CSEP / ETAS next-day earthquake forecast testing (Lombardi & Marzocchi 2010)

*Category: methods* — Prospective testing of P(event in window) under clustering; error bars too narrow.

### Basic Info

**Name**

> CSEP / ETAS next-day earthquake forecast testing. Core: Lombardi & Marzocchi (2010a), 'The ETAS model for daily forecasting of Italian seismicity in the CSEP experiment' (Annals of Geophysics 53(3):155-164). Companion: Lombardi & Marzocchi (2010b), 'The Assumption of Poisson Seismic-Rate Variability in CSEP/RELM Experiments' (BSSA 100(5A):2293-2300). Follow-ups: Taroni et al. (2018), prospective CSEP-Italy evaluation (SRL 89(4):1251-1261), and Brehmer, Kraus, Gneiting, Herrmann & Marzocchi (2024), 'Enhancing the statistical evaluation of earthquake forecasts - an application to Italy' (SRL, arXiv:2405.10712)

**Type**

> method family (paper cluster: ETAS point-process forecaster plus the CSEP prospective-testing protocol and its critiques)

**Url**

> https://doi.org/10.4401/ag-4848 (PDF: https://www.annalsofgeophysics.eu/index.php/annals/article/view/4848/4915 ; repository: https://www.earth-prints.org/handle/2122/6419) ; companion BSSA: https://doi.org/10.1785/0120100012 (https://www.earth-prints.org/handle/2122/6420) ; Taroni et al. 2018: https://doi.org/10.1785/0220180031 ; Brehmer et al. 2024: https://arxiv.org/abs/2405.10712 (https://doi.org/10.1785/0220240209) ; Werner et al. 2010 CSEP-Italy retrospective (shows the Poisson count intervals are too narrow): https://arxiv.org/abs/1003.1092

**Year**

> 2010 (both Lombardi & Marzocchi papers); follow-ups 2018 (prospective 5-year results) and 2024 (re-evaluation with proper scoring rules and the Diebold-Mariano test)

**Authors**

> Anna Maria Lombardi, Warner Marzocchi (INGV Rome). Follow-ups: M. Taroni, W. Marzocchi, D. Schorlemmer, M.J. Werner, S. Wiemer, J.D. Zechar, L. Heiniger, F. Euchner (2018); J.R. Brehmer, K. Kraus, T. Gneiting, M. Herrmann, W. Marzocchi (2024)

**Popularity**

> Crossref citations (retrieved 2026-10-17): Annals paper 19, BSSA Poisson paper 28. Semantic Scholar: Taroni et al. 2018 has 70 citations, Brehmer et al. 2024 has 5. The CSEP protocol itself is the standard testbed in statistical seismology.

**Peer review status**

> peer-reviewed (Annals of Geophysics; BSSA; SRL). Brehmer et al. is peer-reviewed in SRL, with an arXiv post-print.

### Problem Framing

**Target type**

> Count/onset target (a new event occurs), not a state target. CSEP daily forecasts give the expected number of new M>=4 earthquakes, or P(at least one event), in each 0.1 x 0.1 degree cell for the next day. There is no 'state' analogue, because an earthquake has no duration. The closest match to our task is P(at least one new onset in (t, t+H]) per unit.

**Target definition**

> Daily probability of at least one earthquake with ML >= 4.0 in each 0.1 x 0.1 degree cell of the CSEP-Italy testing region, at depth < 30 km. H = 1 day. Forecasts are issued every day using all seismicity up to the start of the window. The ETAS model is fitted on ML >= 2.5 events and rescaled to ML >= 4.0 with Gutenberg-Richter (b = 1.0). The Brehmer et al. 2024 re-evaluation used 7-day expected counts, issued daily, over 8,993 cells.

**Spatial unit**

> grid cell (0.1 x 0.1 degree, CSEP-Italy testing region); also evaluated region-wide (number test) and over the spatial distribution (reliability / S-test)

**At risk masking**

> Not applicable in the usual sense. Earthquakes are instantaneous, so no 'already under event' state needs masking. The analogous hygiene is about the conditioning history: forecasts condition only on events before the window start, and ETAS explicitly simulates the events expected during the window (secondary triggering) instead of reading them from the catalogue.

### Data

**Data sources**

> INGV Italian seismic bulletin (Bollettino Sismico Italiano). Learning set: 16 Apr 2005 to 1 Jun 2009, 2,100 events with ML >= 2.5 and depth < 30 km. Testing set: 1 Jun 2009 to 1 Sep 2009, 179 events (retrospective, out-of-sample in time). Prospective CSEP-Italy experiment from 1 Aug 2009. Over 5 years Taroni et al. 2018 counted 83 target events with 3.95 <= M < 4.95 and 14 larger shocks.

**Data source variant**

> Single official catalogue (INGV). The start date 16 Apr 2005 was chosen deliberately: the network and the data processing changed then, so earlier data were not mixed in. This is the analogue of our 'never mix the official file with alerts.in.ua' rule (D-007/D-015) and of starting the series at a regime boundary.

**Preprocessing**

> Magnitude-of-completeness analysis (Cao and Gao b-value stability, ZMAP). Mc = 2.0 overall, but Mc rises to about 2.5 right after the L'Aquila Mw 6.3 mainshock and varies in space; Mc = 2.5 chosen as reliable for most of Italy. Depth < 30 km filter. Events restricted to the CSEP collection polygon. No declustering: clustering is modelled, not removed.

**Known label artefacts**

> (1) Incompleteness after large events: detection drops right after a mainshock, so small aftershocks are missing. The authors list this as a known weakness and suggest a modified magnitude distribution. This mirrors our recording gap (2026-08-30 to 09-01), which must be treated as missing, not as zero (D-013). (2) Spatial heterogeneity of completeness: Mc is higher in southern Apulia and western Sicily, and the authors accepted this as a known limitation. (3) Network change in April 2005: handled by cutting the series at that date. (4) Regime failure: the Italy-wide ETAS fit did not reproduce the early L'Aquila sequence. The local alpha (1.5 to 2.0) exceeds the national 1.3, and the Runs test on learning residuals rejected independence (p = 0.007) until the L'Aquila sequence was removed (p = 0.07). The analogue for us is that a pooled model can misfit one oblast during an unusual campaign. Duplicates and swapped columns were not discussed.

### Method

**Model family**

> Epidemic-Type Aftershock Sequence (ETAS) model: a self-exciting (Hawkes) space-time-magnitude point process. Conditional intensity = background rate nu*u(x,y) + the sum over past events of K*exp(alpha*(Mi - Mc)) * (t - ti + c)^(-p) * spatial kernel (d, q) * the Gutenberg-Richter magnitude density. Fitted by maximum likelihood with the Zhuang et al. 2002 iterative stochastic-declustering algorithm. Forecasts are the average over 1,000 simulated catalogues per window (Ogata thinning), so the triggering during the window is included.

**Features**

> No engineered features. The model uses only the past event history (times, locations, magnitudes). Fitted parameters: nu = 237 +/- 8 per year; K = 0.011 +/- 0.001; p = 1.16 +/- 0.02; c = 4e-5 years; alpha = 1.3 +/- 0.1; d = 1.10 +/- 0.05 km; q fixed at 1.5 because of the q-d trade-off; log-likelihood -7808.1. 46% of events were classed as triggered, 54% as background. The background spatial density u(x,y) comes from a Gaussian kernel with variable bandwidth. The Omori decay implies P(an M3 event triggers an M2.5+ event) < 1% after 5-6 hours, against 2-3 days for M5 and about 1 month for M7. The analogues for us are 'minutes_since_last_start', 'onsets_last_24h/7d' and 'neighbors_active', which are crude, non-parametric stand-ins for the triggering kernel.

**External feature timing**

> None. The model is purely endogenous (catalogue only), with no tectonic, geodetic or geological inputs. All conditioning history ends at the start of the forecast window, which is causal by construction.

**Ablation design**

> No feature ablation. Later CSEP-Italy comparisons ranked whole models (LM = this ETAS, FCM = another ETAS variant, LG = STEP-based, and SMA/LRWA ensembles) on the same cells, days and target events. That is a like-for-like comparison on one common sample, which is the property we need for ablations.

### Evaluation

**Split scheme**

> Retrospective: fit on 16 Apr 2005 to 1 Jun 2009, test on 1 Jun to 1 Sep 2009, both chronological. The parameters re-estimated on the whole catalogue did not differ significantly from the learning-set values, which serves as a stability check. Prospective: the model was frozen and submitted to the independent CSEP testing centre (ETH Zurich), which ran it daily from 1 Aug 2009 with no modeller access to the outcomes. This was a true pre-registered prospective test, assessed after 5 years (Taroni et al. 2018) and again in 2024.

**Metrics**

> Lombardi & Marzocchi 2010a: residual analysis with Ogata's transformed time (should be a unit-rate Poisson process), the KS1 test for exponential inter-event residuals, the Runs test for independence, a U(k+1) vs U(k) scatter plot, and a cumulative reliability diagram of the spatial distribution. CSEP standard tests: N-test (number), L-test and CL-test (likelihood), S-test (space), M-test (magnitude), and T/W-tests (pairwise information gain per earthquake). Brehmer et al. 2024: the Poisson log score and quadratic (Brier-type) score as proper scoring rules, Diebold-Mariano tests on score differences, and mean-reliability diagrams with consistency bands.

**Unit of metric**

> Pooled over all cells and days (CSEP likelihood tests). Number tests are region-wide. Brehmer et al. use mean scores over all bins, including bins with zero events, and treat per-cell score differences as diagnostics only.

**Baseline strength**

> CSEP compares models against each other and against time-independent (smoothed-seismicity) reference models. In 2018 the 1-day ETAS models were consistent with the observed number and magnitudes, and one ETAS version was also consistent in space. Ensembles were as good as the best single model. In Brehmer et al. 2024 (Poisson score, lower is better): LRWA 2.69, LM 2.71, SMA 2.73, FCM 2.80, LG 3.02. The DM test could not separate LM (this paper's ETAS) from LRWA, SMA or FCM, but it beat LG. So the 'best' model was statistically tied with the ensembles.

**Calibration**

> Lombardi & Marzocchi 2010a used a cumulative reliability diagram of the spatial forecast (forecast cell fractions in 10 equally populated bins vs observed fractions). Its 95% error bars came from applying the same analysis to 1,000 synthetic catalogues simulated from the fitted ETAS model, conditioned on the real learning history. The bars therefore reflect clustering-induced variability, not a Poisson or binomial approximation. Observed points: 1.6e-3 -> 1.8e-3, 1.2e-2 -> 1.4e-2, 1.1e-1 -> 1.3e-1, 1.7e-1 -> 2.2e-1, all close to the diagonal. Brehmer et al. 2024: LM stays near the diagonal of the mean-reliability diagram; FCM, LG and SMA often leave the consistency bands. No recalibration was fitted.

**Calibration under drift**

> There was no formal calibration-in-the-large test against a validation period. The number test is a calibration-in-the-large check (total forecast vs observed count), and the papers show that it is badly misjudged when counts are treated as Poisson. Werner et al. 2010 found that 4 of the yearly counts fell outside the 95% Poisson interval (about 1 in 20 expected) and one fell beyond the 99.99% quantile. A negative binomial fitted much better. Non-stationarity (time-varying background, local alpha) is named as the main source of misfit. No recalibration method was proposed.

**Uncertainty of gain**

> This is the key lesson. (1) Lombardi & Marzocchi 2010b (BSSA) simulated ETAS seismicity and scored the TRUE model with the CSEP tests, which rejected it more often than the nominal rate. The reason is that ETAS forecasts vary more than Poisson allows, so independent Poisson errors per cell give intervals that are too narrow. They called for revising the testing procedures. (2) Werner et al. 2010 found the same problem for counts (overdispersion) and proposed a negative binomial number test, now implemented in floatCSEP. (3) Brehmer et al. 2024 showed that the CSEP T-test (paired information-gain comparison) uses a misspecified variance and rejected 46.5% of the time at a nominal 10% level. Its p-values are not uniform under the null. Their fix is the Diebold-Mariano test on mean score differences over all bins. They note that dependence (for example overlapping windows) needs further adjustment. Restricting to non-overlapping weekly issues did not by itself fix the miscalibrated p-values (104 and 108 of 400 p-values in the extreme tails vs 20 expected each), which points to space-time clustering as the remaining cause. (4) Lombardi & Marzocchi 2010a avoided analytic error bars and built them by simulating 1,000 catalogues from the model.

### Leakage & Hygiene

**Leakage handling**

> Strong by design. (1) Prospective protocol: the model code was frozen and submitted to an independent testing centre before the outcomes existed, so neither test-period tuning nor peeking was possible. (2) Causal conditioning: each daily forecast uses only events before the window start, and in-window triggering is simulated rather than observed. (3) Retrospective test: chronological split with the parameters fixed from the learning set, while the history used for conditioning still includes the learning period. This is valid because past events are known at forecast time. (4) A known catalogue artefact (the 2005 network change) was handled by truncating the series, not by mixing regimes. Missed or acknowledged: Mc is optimistic in some zones, and the short-term incompleteness after large shocks is not modelled. For us, the CSEP 'frozen code, scored by someone else' protocol is the gold-standard version of our 'score the final test ONCE at the end of M4' rule.

### Results

**Headline results**

> Retrospective (Lombardi & Marzocchi 2010a): learning residuals passed KS1 (p = 0.8) but failed the Runs test (p = 0.007) because of L'Aquila; they passed it without L'Aquila (p = 0.07). Testing residuals: KS1 p = 0.14 and Runs p = 0.81, so neither test rejected. The spatial reliability diagram lay on the diagonal and inside the simulated 95% bands. Prospective (Taroni et al. 2018): the 1-day ETAS forecasts were consistent with the observed numbers and magnitudes, and one ETAS version was also consistent in space. Ensembles matched the best single model. None of the time-independent 3-month models were consistent. Brehmer et al. 2024 (Poisson score): LRWA 2.69, LM 2.71, SMA 2.73, FCM 2.80, LG 3.02. LM was best under the quadratic score. DM could not separate LM from LRWA, SMA or FCM, but showed that the clustering models beat the STEP-based LG. Methodological headline (2010b, 2024): the standard CSEP tests reject correct models too often, because Poisson-based and T-test variances ignore clustering and overdispersion. The error bars are too narrow.

### Relevance

**Takeaways for project**

> 1) Our D-013 bootstrap CI must resample whole time blocks across ALL 24 oblasts together. Alert onsets are a self-exciting space-time process: one mass drone or missile attack starts alerts in many oblasts within the same hour or two. Treating the 24 x ~1,000 test oblast-hours as independent rows (a Poisson/binomial or naive t-test CI on the Brier difference) repeats the CSEP error, with intervals that are too narrow and a true null rejected too often. The effective sample size is closer to the number of attack waves, or of test days or weeks, than to the number of rows. Resample by week (6 test weeks is very few: report the CI as wide and indicative) or by day with a moving-block bootstrap. Keep all oblasts of a block together.
> 2) For the primary metric (D-021, BSS vs rolling recent-rate), compare model and baseline with a Diebold-Mariano-style test on the per-hour score differences d_t = mean over oblasts of (Brier_model - Brier_recent), aggregated to one value per hour or day. Use a HAC (Newey-West) variance or a block bootstrap, never the iid variance (Brehmer et al. 2024: the iid-variance T-test rejected 46.5% at a nominal 10%). Include all scored rows, as Brehmer et al. include zero-event bins, not only hours with onsets.
> 3) Reliability plot (D-006): copy the Lombardi & Marzocchi idea of consistency bands. Draw the band by resampling (block bootstrap of test weeks, or Gneiting-Resin consistency bands), not by binomial sqrt(p(1-p)/n) per bin. Binomial bars per bin assume independent rows and will look falsely tight.
> 4) Calibration-in-the-large under drift (D-015 (c), D-021): the N-test analogue is mean predicted vs observed onset rate. Judge the size of the gap against a clustering-aware spread (for example week-to-week variability of the rolling recent-rate within the training period), not against a Poisson interval. Werner et al. found 4 of their yearly counts outside 95% Poisson limits, where about 1 in 20 is expected.
> 5) Rolling recent-rate as the bar to beat (D-021) is the right choice. In seismology the strong baseline for short-term forecasting is a clustering model, and a smoothed time-independent rate is the weak one. Our recent-rate baseline plays the role of a crude 'clustering-aware' reference, and climatology plays the time-independent role. Beating climatology alone proves little.
> 6) Features: ETAS shows that the triggering effect of the most recent events decays as a power law, (t - ti + c)^(-p). This supports keeping minutes_since_last_start, onsets_last_24h/7d and the neighbour/national-active counts, and suggests that a log transform of 'minutes since' or several decay windows may beat a single linear feature. A Hawkes-style baseline is a possible future extension but needs the human's approval (scope rule).
> 7) Regime boundaries: INGV cut the series at the April 2005 network change. This matches our D-007/D-015 rule never to mix the official file and alerts.in.ua in one training set or metric, and the D-020 causal standing-alert cap.
> 8) Pooled-model misfit: the Italy-wide ETAS failed on the start of the L'Aquila sequence because the local alpha differed. Report per-group and per-oblast results (frontline, rear, Kyiv City) and per-oblast reliability (D-013), because a pooled reliability curve can hide a badly miscalibrated unit.
> 9) Test hygiene: CSEP's frozen, independently scored, prospective protocol is the ideal that our 'score the final test ONCE at end of M4' rule approximates. The new-regime API check (D-015) is the only truly prospective part of our evaluation and should be described that way.

**Best practices**

> ADOPT: (a) Pre-register and freeze the model before scoring. Score once, ideally by automated code that is not edited afterwards. (b) Causal conditioning: forecasts use only history before the window start. (c) Get uncertainty bands by simulating or resampling under the actual dependence structure (synthetic catalogues or a block bootstrap), not from Poisson or binomial formulas. (d) Compare forecasts with proper scoring rules (log or Brier score) averaged over ALL scored rows, and test differences with Diebold-Mariano using HAC or block variance. (e) Use a negative binomial or other overdispersed reference when checking total counts (calibration-in-the-large). (f) Use reliability diagrams with consistency bands. (g) Start the training series at known regime or recording changes instead of mixing regimes. (h) Treat per-unit score differences as descriptive diagnostics, not formal tests, because spatial dependence and multiple testing make per-unit inference unreliable. AVOID: (1) Treating every unit-hour as an independent trial when computing CIs or p-values, which repeats the CSEP Poisson mistake. (2) The paired t-test on information gain or score difference with iid variance, which is the CSEP T-test flaw. (3) Normalising by the number of observed events (information gain per earthquake), which is undefined or unstable when there are no events, as in quiet blocks of rear oblasts. (4) Declaring a model 'rejected' or 'significantly better' from a test whose null distribution ignores clustering. (5) Generalising a pooled fit to units with different local dynamics without per-unit checks.

### Other Info

**Uncertain fields (omitted above)**

- code_available
- regime_coverage
- test_window_hygiene

---

<a id="views_challenge"></a>
## 16. ViEWS early-warning system + 2023/24 Prediction Challenge (Hegre et al. 2025)

*Category: methods* — Pre-registered benchmarks, fixed scoring rules, true out-of-sample windows.

### Basic Info

**Name**

> ViEWS (Violence Early-Warning System) and the 2023/24 VIEWS Prediction Challenge. Core paper: Hegre, Vesco, Colaresi et al. (2025), 'The 2023/24 VIEWS Prediction challenge: Predicting the number of fatalities in armed conflict, with uncertainty', Journal of Peace Research 62(6):2070-2087. System context: Hegre et al. (2019) 'ViEWS: A political Violence Early-Warning System' (JPR 56(2)) and Hegre et al. (2021) 'ViEWS2020: Revising and evaluating the ViEWS political Violence Early-Warning System' (JPR 58(3):599-611). Predecessor: Hegre, Vesco & Colaresi (2022) and Vesco et al. (2022), the escalation prediction competition (International Interactions 48(4)).

**Type**

> paper + benchmark/challenge protocol (method family: pre-registered, multi-team prospective forecasting challenge with fixed proper scoring rules, public benchmarks and a true-future window), with an open evaluation repository

**Url**

> https://doi.org/10.1177/00223433241300862 (open-access PDF, CC BY: https://eprints.whiterose.ac.uk/id/eprint/226622/1/hegre-et-al-2025-the-2023-24-views-prediction-challenge-predicting-the-number-of-fatalities-in-armed-conflict-with.pdf) ; preprint (pre-analysis-plan function, 8 Jul 2024): https://arxiv.org/abs/2407.11045 ; online appendix: https://viewsforecasting.org/wp-content/uploads/2025/12/OnlineAppendix_PredictionChallenge_2023-1.pdf ; original invitation v1.2 (Apr 2023): https://viewsforecasting.org/wp-content/uploads/VIEWS_2023.24_Prediction_Competition_Invitation.pdf ; leaderboard: https://viewsforecasting.org/leaderboard/ ; dashboard: https://predcomp.viewsforecasting.org ; evaluation and benchmark code: https://github.com/prio-data/prediction_competition_2023 ; ViEWS2020: https://doi.org/10.1177/0022343320962157

**Authors**

> Havard Hegre, Paola Vesco, Michael Colaresi, Jonas Vestby and about 37 co-authors from the 13 contributing teams (PRIO, Uppsala, KIT, CCEW Munich, Trinity College Dublin, UT Dallas, UCL, Essex, Turin, CSIC Barcelona, Georgia Tech, West Virginia, among others). Scoring committee: Philip Schrodt, Celine Cunen, Thomas Mayer (PREVIEW, German Foreign Office), Seth Caldwell (formerly UN OCHA). Funded by the German Foreign Office, ERC (ANTICIPATE, 101055176) and the Research Council of Norway.

**Popularity**

> As of 2026-10-17: Crossref 7 citations, Semantic Scholar 10 citations. GitHub prio-data/prediction_competition_2023: 7 stars, 7 forks, no license file, last push 2025-12-08. 24 contributions from 13 teams. The parent ViEWS system papers (2019, 2021) are widely cited in conflict forecasting, and ViEWS forecasts appear in UN and government dashboards.

**Peer review status**

> peer-reviewed (Journal of Peace Research, 2025; ViEWS 2019/2021 also JPR). The individual team write-ups are working papers or self-reported. The leaderboard is a live web page, not peer-reviewed.

### Problem Framing

**Target type**

> Count target (monthly number of state-based conflict fatalities), forecast as a full predictive distribution (15 to 1,000 samples per unit-month). It is neither a pure onset target nor a state target. Because counts persist strongly (the 'conflict trap'), the task rewards persistence in much the same way a state target does: most of the score comes from ongoing wars, and the hardest cases are outbreaks in previously peaceful units. Earlier ViEWS (2019/2020) used binary targets: P(at least 25 battle-related deaths) per country-month, and later P(at least 1 BRD) at both levels.

**Target definition**

> y = UCDP 'best' estimate of state-based conflict fatalities in unit i in month t, on the raw (non-logged) count scale. The predecessor competition used ln(y+1) change. Horizons: true future July 2024 (s=3) to June 2025 (s=14), from data up to and including April 2024. The 2-month gap reflects the release lag of UCDP Candidate data. Retrospective test windows: each month of calendar years 2018 to 2023, from data up to October of the preceding year (s=3..14). Contributors could submit identical predictions for all 12 months or fine-tune each step. ViEWS2020 trains a separate model for each step s = 1..36 months.

**Spatial unit**

> country-month (cm, global, Gleditsch-Ward country list with CShapes borders) and PRIO-GRID-month (pgm, 0.5 x 0.5 degree cells, about 55 x 55 km at the equator; Africa and the Middle East only).

**At risk masking**

> None. Every unit-month is scored, including units already in ongoing war, and there is no onset/at-risk mask. Most of each score therefore comes from continuing conflicts: 9 of the 10 largest CRPS values for the exactly-zero benchmark were Ethiopia and Ukraine. This is the reason persistence-type benchmarks are so strong. The contrast with our design is that D-020 plus the onset mask (rows already under alert are excluded) deliberately removes this persistence credit. ViEWS results are therefore not directly comparable to an onset metric.

### Data

**Data sources**

> UCDP Georeferenced Event Dataset (GED, final, vetted) for the retrospective test windows 2018 to 2023. UCDP Candidate Events Dataset (monthly preliminary release) for 2024 onward and for scoring the true future. The VIEWS team supplied about 100 features at each level: training data 1990 to 2017, prediction inputs for the test windows, and updated data up to April 2024 (released June 2024). Contributors could add their own data, for example a corpus of 6 million news articles (ConflictForecast LDA topics) and actor/dyad data (HCD_dyad).

**Data source variant**

> Two label versions are mixed across windows. The test windows are scored against final UCDP-GED, and the true future against UCDP-Candidate. ViEWS2020 itself notes that Candidate data are vetted less carefully than GED, so 'some systematic differences between the two periods may be reflected in the evaluation'. It also reports a Candidate reporting error that was later corrected. This is the analogue of our official-file vs alerts.in.ua split (D-007/D-015): a label-source change between the development windows and the prospective window.

**Preprocessing**

> VIEWS aggregates UCDP events to cm and pgm. Assignment rules differ between levels: a pgm cell spanning several countries aggregates all its events, while cm assigns events to the country where they happened, so the two levels are not fully compatible. A country enters cm only for the months it exists in the Gleditsch-Ward list. Submissions were standardised to 1,000 samples: point predictions were converted to Poisson(mean = variance = prediction), and odd sample counts were up-sampled with scipy.signal.resample. The int32 sample format was fixed in advance.

### Method

**Model family**

> Benchmarks: exactly-zero; last-historical with Poisson noise; conflictology_country12 (the empirical distribution of the unit's last 12 monthly values); conflictology_neighbors12 (last 12 months in the cell plus first-order neighbours); conflictology_bootstrap240 (global draws from the last 20 years). Contributions: empirical-quantile and negative binomial history models (Drauz & Becker; Bodentien & Rueter); Bayesian Tweedie/NB/Poisson GLMM and GAM (Brandt); hurdle tree ensembles and AutoML (CCEW trees; D'Orazio); a three-stage hierarchical hurdle with Platt scaling (Fritz et al.); zero-inflated GAM and stacked ML (Muchlinski & Thornhill); observed, hidden and Gaussian-process Markov models (Randahl & Vegelius); random forest with news LDA topics (ConflictForecast); Dynamic Time Warping shape matching (PaCE; HCD_dyad); temporal fusion transformer (CCEW_tft); a pre-trained transformer with NB likelihood (UNITO). The ViEWS core system (2020) uses step-specific random forests and logits combined by EBMA ensembling.

**Features**

> Common VIEWS feature sets (about 100 per level): conflict history (lags and decay functions of fatalities by violence type), spatial lags and neighbourhood conflict, and structural covariates (demography, economy, V-Dem regime indicators, geography). Team additions: rolling 3/6/8-month averages and temporal lags (Muchlinski & Thornhill); 15 LDA news topics (ConflictForecast); actor-dyad clusters (HCD_dyad); time-invariant covariates and known future inputs (TFT). The strongest true-future entries rely mostly on the unit's own recent history: the 12-month empirical distribution, Markov states, and NB fits to recent history.

**Ablation design**

> No formal ablation in the challenge paper. All models are scored on the same units, months and windows (like-for-like), which allows clean cross-model comparison. ViEWS2020 contains an ensemble 'drop-one' analysis: the change in ensemble AUPR when each constituent model is removed, with 'harm' defined as more than 0.5 bootstrapped standard errors. Some team papers compare variants internally, for example local vs global trees and NB vs hurdle vs neural network.

### Evaluation

**Split scheme**

> Challenge: (a) six retrospective calendar-year test windows 2018 to 2023, each forecast from data up to October of the prior year, all in the same s=3..14 format; (b) one true-future window, Jul 2024 to Jun 2025, from data up to April 2024, submitted by 23 June 2024 before any outcome existed. The scoring committee gives roughly equal weight to the test windows and the true future. The protocol changed mid-challenge. The April 2023 invitation planned a true future of calendar 2024 (data to October 2023), test windows 2018-2021, final forecasts due 10 Dec 2023, and an evaluation article in May 2025. The final protocol extended the test windows to 2023 and moved the true future to Jul 2024 to Jun 2025. ViEWS2020 core system: evaluation periodisation trains Jan 1990 to Dec 2012, calibrates and tunes on Jan 2013 to Dec 2015, and tests on Jan 2016 to Dec 2018. Forecast periodisation trains 1990 to Dec 2015, calibrates on Jan 2016 to Dec 2018, then RETRAINS on train+calibration and forecasts Jan 2020 to Dec 2022. Published monthly forecasts from Jul 2018 to Dec 2019 were later scored against actuals (retrospective evaluation of true forecasts).

**Metrics**

> Main: CRPS (properscoring/xskillscore crps_ensemble, equal sample weights, empirical CDF; for counts this is effectively the ranked probability score). Secondary I: adjusted binned log score (ab-Log). Bins are [0], [1-2], [3-5], [6-10], [11-25], [26-50], [51-100], [101-250], [251-500], [501-1000], [1001+], with one pseudo-sample (omega = 1) per bin, so the formula is -log((p*1000+1)/1011). The cap stops a zero-probability outcome giving an infinite score. Secondary II: Mean Interval Score at 90% (NumPy linear quantiles). 90% was chosen because quantiles of overdispersed distributions beyond it are unreliable with 1,000 samples. A candidate pseudo-Earth-Mover divergence was discussed in the invitation. The four target qualities are calibration, sharpness, focus/locality and propriety. ViEWS 2019/2020: AUROC, AUPR, Brier, separation and model-criticism plots.

**Unit of metric**

> Pooled: the mean score over all unit-months in a window, per level (cm, pgm), reported per year and as a six-year average. The dashboard offers per-country, per-cell and per-month breakdowns, but the ranking is pooled.

**Baseline strength**

> Strong and decisive. Retrospective 2018-2023 cm averages (CRPS / ab-Log / MIS): exactly_zero 56.84 / 1.59 / 1136.80; last_historical 158.16 / 1.14 / 3137.09 (2023 alone gave CRPS 678.96); conflictology_country12 49.36 / 0.65 / 873.53, the best benchmark; bootstrap240 56.17 / 1.14 / 1101.02. At pgm, exactly_zero and bootstrap240 tie at CRPS 0.45, and neighbors12 is slightly better (0.45 CRPS, MIS 8.61 vs 8.98). True future, Jul 2024 to Jun 2025 (leaderboard, CRPS): at cm the post-hoc benchmark conflictology_country12 ranks 1st with 24.92, ahead of Brandt_NB_GLMM 25.17, Randahl_Vegelius OMM 25.27, ConflictForecast 25.96 and CCEW_tft 26.23. last_historical (26.32) beats 11 of the 17 contributed models. At pgm conflictology_country12 is again 1st (0.27), ahead of the CCEW tree ensembles (0.29) and neighbors12 (0.30). Several complex models score worse than exactly_zero at cm (zero-inflated GAM 61.16, UNITO transformer 64.10), and some Brandt GAMs blew up (CRPS 4.9e5 to 7.8e6). On the secondary metrics, contributions do beat the benchmark: at cm the OMM ab-Log 0.68 beats 0.76 and ConflictForecast MIS 329.7 beats 376.3; at pgm the CCEW trees reach ab-Log 0.09 vs 0.11 and MIS 4.43 vs 4.58. The predecessor competition (Vesco et al. 2022) found the same pattern: most models were beaten by a 'no-change' model. Caveat: the conflictology benchmarks are labelled 'post-hoc' (ph). They were added on scoring-committee advice after the start and are therefore 'not used as scoring rule'. The Drauz & Becker entry used the same logic from the start.

**Calibration**

> The challenge itself publishes no reliability diagrams. Calibration is assessed only implicitly, through CRPS and MIS (both reward calibration and sharpness) and through the coverage penalty term of MIS. One contribution (Fritz et al., three-stage hurdle) uses Platt scaling to match the observed relative frequency. ViEWS 2019 calibrated the ensemble so that the mean predicted probability matched the observed frequency (calibration-in-the-large) on the calibration partition, but it separated cases poorly: very few predictions were above 0.75 or below 0.05. ViEWS2020 fitted calibration, EBMA weights and hyper-parameters on the calibration period, then retrained the constituent models on train+calibration before forecasting.

**Regime coverage**

> Good across the conflict regime. The six retrospective years span a low-violence period (2018-2019) and the sharp 2021-2022 escalation (Ethiopia, Ukraine, Yemen), and the score swings make the effect visible. The true future (Jul 2024 to Jun 2025) covers a further real-time regime. None of the Ukrainian alert-specific shifts (Jan-2025 drone surge, Dec-2025 raion reform, Sep-2026 yellow/red) apply. The analogous lesson is that a model ranked on one regime (the 2018-2020 calm) can reverse on the next (last_historical went from best to worst).

### Leakage & Hygiene

**Leakage handling**

> (1) True-future protocol: forecasts for Jul 2024 to Jun 2025 were submitted on 23 Jun 2024, before the outcomes existed, and a preprint was published at the window start as a pre-analysis plan, so neither leakage nor test peeking is possible for that window. (2) Fixed data cut-offs per window: inputs end in October of the prior year (or April 2024), and forecasts start at s=3, which respects the data release lag. This is a label-maturity rule, like our purge rule and D-021's [t-14d, t-H] window. (3) Scoring code and benchmarks are public and fixed in advance (invitation v1.2, Apr 2023), and the organisers compute all scores centrally from submitted samples. MISSED or weak: (a) The retrospective 2018-2023 windows are only pseudo-out-of-sample. Their outcomes (final UCDP-GED) were public, contributors had them during development, and at least one entry (Bodentien & Rueter) tuned its history length 'by minimizing the CRPS in the test set'. Test-window scores can therefore be optimistic, and only the true future is clean. (b) Real-time vintage of external covariates in the retrospective windows is not documented. (c) ViEWS2020 retrains on train+calibration after tuning, so the deployed model differs from the validated one. (d) Benchmarks and the evaluation timeline were changed after the start (post-hoc benchmarks, extended windows).

**Test window hygiene**

> True future: best practice. It was frozen and submitted before the window, with a public pre-analysis-plan preprint (arXiv 2407.11045, 8 Jul 2024), centrally scored, and continuously monitored on a public dashboard as UCDP Candidate data arrived. An independent scoring committee is planned, weighting test windows and true future roughly equally. Retrospective test windows: poor hygiene, because they were visible and tunable. Contributors received preliminary scores at the October 2023 Berlin workshop and resubmitted final test forecasts in June 2024, so they could iterate on the test windows. Timeline amendments: the invitation (v1.2, 18 Apr 2023) foresaw final submissions on 10 Dec 2023 and a calendar-2024 true future. The actual deadline was 23 Jun 2024 for Jul 2024 to Jun 2025. The 'ph' benchmarks were added later and excluded from the formal ranking for that reason.

### Relevance

**Takeaways for project**

> 1) Our D-021 choice is directly validated. VIEWS' winning true-future model, conflictology_country12, is literally a rolling recent-history empirical distribution per unit: the cm-level twin of our rolling 14-day recent-rate baseline. A large field of ML, transformer and Bayesian models could not beat it on the primary metric. Treat 'not beating recent-rate' as a likely, legitimate outcome and report it honestly, as CLAUDE.md requires. Also report persistence (raw and calibrated), because last_historical beat most entries.
> 2) Freeze the baselines before seeing the test. VIEWS had to demote its best benchmark to 'post-hoc, not a scoring rule' because it was added after the start. Our four baselines (climatology, rolling recent-rate with shrinkage (k + 10*p_unit)/(n + 10), raw persistence, calibrated persistence) are fixed in M3 on validation, which is the right call. Do not add or re-specify a baseline after M4 scoring; if one is added, label it post-hoc as VIEWS did.
> 3) Only a truly unseen window is clean. VIEWS' retrospective windows were visible, and at least one team tuned on them. Our 'score the final test ONCE at end of M4' rule is the equivalent of their true future, and the 2026-07-27 to 09-07 window must never feed tuning. The API new-regime check (D-015) resembles their true-future window most closely, because the model is frozen before that data is scored. Describe it as such, while keeping it exploratory.
> 4) Label-version shift: VIEWS scores the true future on preliminary UCDP-Candidate data and the test windows on final GED, and flags this as a possible source of systematic differences. This supports D-007/D-015: never mix the official file and alerts.in.ua in one metric, and state that the new-regime numbers use a different label source.
> 5) Label maturity / purge: VIEWS starts forecasts at s=3 because of the data release lag. Our equivalents are the D-021 [t-14d, t-H] rule and the purge at every cut-off. Keep the truncation/leakage test, with its negative control, as a hard gate.
> 6) Uncertainty of gain is the gap VIEWS left open. The top three true-future cm models are within 1.5% CRPS, with no CI or significance test, yet they are ranked. Do the D-013 week-block bootstrap CI on the Brier gain over recent-rate (and a DM/HAC test if time allows), keep all 24 units of a block together, and do not claim a winner when the CI covers zero.
> 7) Persistence credit: VIEWS scores every unit-month, so ongoing wars dominate the scores and persistence wins. Our onset mask (rows already under alert are excluded) and the D-020 24h causal cap remove most of this credit. Do not compare our skill numbers with state-target results from other projects, and cite VIEWS as the example of why state targets inflate skill.
> 8) Pooled scores can be dominated by a few units (9 of the 10 largest CRPS values came from Ethiopia and Ukraine). Report per group (Kyiv City, frontline, rear), within-oblast mean AUC, and per-oblast reliability (D-013), not only pooled numbers.
> 9) Single-window volatility: VIEWS benchmark scores swing about 5x across years, and last_historical went from best to worst. Our 6-week test is one short window. Add a per-week breakdown and the optional weekly-refit row (D-014) to show stability, and phrase conclusions as specific to the summer-2026 regime.
> 10) Metric choice: CRPS for a binary event reduces to the Brier score, so our primary metric (Brier skill score, D-021) is the binary analogue of VIEWS' main metric. Their ab-Log idea (cap the penalty by adding a pseudo-count) mirrors clipping probabilities before computing log loss, if we ever report log loss. Keep PR-AUC / base rate as the secondary 'focus' view, since rankings changed with the metric in VIEWS.
> 11) Do not refit on train+val after early stopping. ViEWS2020 does this (step 4: retrain on training + calibration), which means the deployed model was never itself validated. Our CLAUDE.md rule (no refit after early stopping; calibration fitted on validation and applied to the same model, D-021) is stricter and should stay.
> 12) Calibration-in-the-large: ViEWS 2019 calibrated mean predicted to observed frequency but still separated cases poorly. Report both reliability (D-006) and discrimination, and for D-015(c) compare mean predicted vs observed per group in the new regime.

**Best practices**

> ADOPT: (a) A true-future, pre-registered window: freeze the model and baselines, publish or commit the plan before the outcomes exist, and score centrally with fixed code. (b) Fixed proper scoring rules announced up front, with one designated main metric for the ranking (CRPS there, BSS vs recent-rate for us) and secondary metrics for diagnosis. (c) Strong, simple, public benchmarks shipped from day one, especially rolling recent-history and persistence baselines; in VIEWS these were the bar that mattered. (d) Several evaluation windows across regimes, reported per window, plus a six-year average, to expose instability. (e) Fixed data cut-offs that respect publication or label lag (s >= 3 there; purge and [t-14d, t-H] here). (f) Score submissions from full distributions or probabilities, never point forecasts alone, and convert point forecasts explicitly with a documented rule (VIEWS: Poisson). (g) Cap infinite penalties with a pre-specified adjustment (ab-Log pseudo-count) instead of dropping rows. (h) Publish all forecasts, code and data for re-scoring. (i) An independent scoring committee or reviewer (our `reviewer` subagent plays this role). AVOID: (1) Treating historical 'test' windows whose outcomes are public as out-of-sample after teams or authors have tuned on them. (2) Adding benchmarks or changing windows after the start without labelling them post-hoc. (3) Ranking models whose score differences are within noise, without CIs or a DM test. (4) Scoring all unit-periods, including ongoing events, and then presenting the skill as an early-warning (onset) skill. (5) Mixing label versions (preliminary vs final, or official vs API) inside one comparison without flagging it. (6) Retraining on train+validation after tuning, so the deployed model was never validated. (7) Generalising from a single year or regime when benchmark scores swing several-fold between years. (8) Complex models without sanity checks: several GAM/transformer entries were worse than predicting all zeros, and some diverged by 5 orders of magnitude.

### Other Info

**Uncertain fields (omitted above)**

- calibration_under_drift
- code_available
- external_feature_timing
- headline_results
- known_label_artefacts
- uncertainty_of_gain
- year

---

<a id="spatiotemporal_deep"></a>
## 17. Spatio-temporal deep models for conflict (Radford 2022 ConvLSTM, Brandt et al. 2022 ST-GCN, von der Maase 2025, DynAttn 2025)

*Category: methods* — Small gains over strong baselines; supports 'simple + correct'.

### Basic Info

**Name**

> Spatio-temporal deep models for conflict forecasting: Radford 2022 (ConvLSTM), Brandt et al. 2022 (ST-GCN), von der Maase 2025 (HydraNet, MC-dropout ConvLSTM U-Net), Iacus et al. 2025 (DynAttn, gated self-attention + ZINB); context from the ViEWS 2020 competition summary (Vesco et al. 2022) and the 2023/24 VIEWS challenge (Hegre et al. 2025)

**Type**

> method family (four papers: two peer-reviewed journal articles, two preprints/working papers) plus two peer-reviewed competition-summary papers used for context

**Url**

> Radford 2022: https://doi.org/10.1080/03050629.2022.2031182 (closed access; RePEc https://ideas.repec.org/a/taf/ginixx/v48y2022i4p739-758.html) ; Brandt et al. 2022: https://doi.org/10.1080/03050629.2022.2036987 (open access CC BY-NC-ND; repository copy http://hdl.handle.net/10150/663780) ; von der Maase 2025: https://arxiv.org/abs/2506.14817 (code https://github.com/views-platform/views-hydranet) ; DynAttn: https://arxiv.org/abs/2512.21435 ; context: Vesco et al. 2022 https://doi.org/10.1080/03050629.2022.2029856 (OA PDF via https://www.prio.org/publications/13337), Hegre et al. 2025 JPR https://doi.org/10.1177/00223433241300862

**Year**

> Radford 2022 (International Interactions 48(4):739-758, online 15 Mar 2022); Brandt et al. 2022 (International Interactions 48(4):800-822, online 14 Mar 2022); von der Maase 2025 (arXiv 2506.14817 v1, 8 Jun 2025, PRIO working paper dated 19 Jun 2025); Iacus et al. 2025 (arXiv 2512.21435 v1, 24 Dec 2025, only version as of 2026-10-17)

**Authors**

> Benjamin J. Radford (UNC Charlotte); Patrick T. Brandt, Vito D'Orazio, Latifur Khan, Yi-Fan Li, Javier Osorio, Marcus Sianan (UT Dallas / Arizona / WVU); Simon P. von der Maase (PRIO / VIEWS, sole author); Stefano M. Iacus, Haodong Qi, Marcello Carammia, Thomas Juneau (DynAttn)

**Peer review status**

> Radford 2022 and Brandt et al. 2022: peer-reviewed (International Interactions special issue on the ViEWS 2020 competition, with an external scoring committee). von der Maase 2025: preprint / PRIO working paper, not peer-reviewed; results partly benchmark against published ViEWS 2020 numbers rather than a re-run. DynAttn 2025: preprint, not peer-reviewed.

### Problem Framing

**Target type**

> None of the four is a binary onset target in our sense. Radford and Brandt: continuous CHANGE target (log change in monthly state-based fatalities, ln(y_{t+s}+1) - ln(y_t+1)), i.e. an escalation/de-escalation target, scored by MSE/TADDA. HydraNet: multi-task - regression on log fatalities plus binary classification of 'any fatality' (>=1 death) per cell-month for three violence types; this binary label is a STATE-type indicator (violence present in month t+s), not 'new onset after peace', so persistent conflict cells inflate AUC/AP. DynAttn: COUNT target (monthly fatalities, ZINB) plus exceedance probabilities P(Y >= tau). The ViEWS organisers themselves note that the log(y+1) change target conflates onset and escalation.

**Target definition**

> Radford 2022: log change in UCDP battle-related deaths (state-based) per PRIO-GRID cell-month, Africa, steps s = 2..7 months ahead (true future Oct 2020-Mar 2021 from data to Aug 2020; test 2017-2019). Brandt et al. 2022: same ViEWS 2020 competition target at pgm level; model predicts Q = 6 future steps from P = 54 past months. von der Maase 2025: cm = ln(fatalities+1) per type (sb/ns/os) at PRIO-GRID-month, plus binary any-violence per type; autoregressive forecasts up to 36 months ahead; metrics averaged over the 36-month test window. DynAttn: monthly fatality counts, horizons 1-12 months; exceedance thresholds tau = 25 (country) and tau = 1 (grid). All horizons are MONTHS; nothing below monthly resolution.

**Spatial unit**

> PRIO-GRID cells (0.5 x 0.5 degree, ~55 km) over Africa (Radford, Brandt; HydraNet Africa + Middle East 180x180 grid, with ME excluded for the ViEWS comparison); DynAttn uses both 191 countries and 13,110 PRIO-GRID cells.

**At risk masking**

> No. None of the papers excludes units already in conflict from training or scoring. HydraNet's binary 'any violence' task scores all cell-months, including cells with ongoing violence, which makes persistence highly predictive (state-target inflation). The change targets of Radford/Brandt implicitly condition on the current level via ln(y_t+1), but no explicit at-risk set is defined. DynAttn's exceedance probabilities are also unconditional on current state.

### Data

**Data sources**

> UCDP-GED fatalities (via ViEWS / VIEWSER API), PRIO-GRID covariates. Radford: ViEWS 2020 competition data (training to Aug 2020; test 2017-2019; true future Oct 2020-Mar 2021). Brandt: 48 ViEWS pgm features (conflict history, protest, land use, socio-economic, resources, distance/accessibility) plus monthly ICEWS events aggregated to the 20 CAMEO root codes per cell-month (via UTD Event Data R package); train Jan 2000-Dec 2016, validation 2017, out-of-sample Jan 2018-Aug 2020. HydraNet: UCDP-GED only (sb/ns/os log fatalities, the ONLY inputs), 1990-2018 in partitions. DynAttn: VIEWS 'fast forward' competition dataset, UCDP monthly fatalities 1990-Jul 2025, several hundred covariates (conflict history and decay terms, climate indices, demographics, accessibility); test Aug 2024-Jul 2025.

**Data source variant**

> Not applicable (no Ukrainian air-raid alert data). Domain analogue: UCDP-GED 'final' vs 'candidate' releases (ViEWS 2020 competitors trained on the candidate dataset up to Aug 2020, later revised) is the conflict-data counterpart of official-vs-volunteer-vs-API variants; none of the papers quantifies the effect of revisions. ICEWS (Brandt) is a machine-coded news-event source with its own coverage drift.

**Known label artefacts**

> Relevant artefacts reported or implied: (1) Extreme zero-inflation (~99.5% zeros at pgm; HydraNet AP random baseline ~0.005) makes 'exactly zero' and 'no-change' baselines very hard to beat on absolute-error metrics; Hegre et al. 2025 note the exactly-zero model is hard to beat at pgm. Analogous to our low hourly onset base rate. (2) The log(y+1) change target treats 0->10 deaths the same as 10->100 (Vesco et al. 2022), conflating onset with escalation - analogous to why we separate onset from state. (3) TADDA metric as parametrised in 2020 could not be beaten by no-change on the test set; the organisers changed the metric after the fact (TADDA1 vs TADDA2) - a metric-design artefact. (4) Single extreme events (Tigray Nov 2020-Feb 2021, >1,300 deaths in one month) dominate short true-future evaluation windows. (5) UCDP candidate vs final data revisions (not handled). None of these papers has duration-based artefacts (30-min ends, standing alerts, recording gaps, duplicate rows); for our project those remain governed by D-010, D-020, D-013 and the dedup-first rule.

### Method

**Model family**

> Deep spatio-temporal neural networks: Radford - ConvLSTM (convolutional LSTM over the grid raster). Brandt - STGCN-TCN (3 stacked TCN-GCN-TCN 'sandwich' blocks, kernel 3, 1-hop graph conv per block => up to 3-hop spatial / ~5-month temporal receptive field, FC output head) and STGCN-LSTM; baseline is a random-forest regressor on ViEWS features. HydraNet - Monte Carlo Dropout LSTM U-Net (convolutional encoder-decoder with recurrent layers), multi-task (3 regression + 3 classification heads, Kendall uncertainty-weighted loss), autoregressive rollout with frozen cell state, 128 MC samples per forecast. DynAttn - shared softplus elastic-net feature gates + compact weight-tied self-attention encoder ([CLS] pooling, sinusoidal positions) + ZINB likelihood heads, ~0.88M parameters, rolling-window training with carried-forward optimizer state.

**Ablation design**

> Brandt: same-sample comparison of RF vs STGCN-LSTM vs STGCN-TCN, each with ViEWS features only (v) vs ViEWS + ICEWS (v+u), on the same Jan 2018-Aug 2020 rolling window; plus backward-elimination of six feature groups (retrain, average MSE over steps 1-6). Model and feature rankings flip between MSE and CRPS. HydraNet: no feature ablation (single input set); 12 training seeds, the run closest to the mean reported. DynAttn: feature-group ablations and elasticities per conflict system on the same rolling setup; baseline comparisons use different valid-prediction counts in some cells (e.g. 106 vs 191 countries), so not all comparisons are same-sample.

### Evaluation

**Split scheme**

> Radford/ViEWS 2020: two tasks - (1) one-shot TRUE future Oct 2020-Mar 2021 (forecasts made from data to Aug 2020, submitted before outcomes existed), (2) time-shifted test set Jan 2017-Dec 2019. Brandt: train 2000-2016, early-stopping validation 2017, rolling 6-month forecasts over Jan 2018-Aug 2020 using the previous 54 months, plus submitted true-future forecasts. HydraNet: ViEWS-style partitions - calibration (train 1990-2012, test 2013-2015) for hyperparameter tuning; validation (train 1990-2015, test 2016-2018) for the reported numbers; model retrained from scratch on the validation partition with frozen hyperparameters (no tuning on the final test). DynAttn: rolling monthly anchors (expanding window, optional cap on most recent K windows), test Aug 2024-Jul 2025.

**Unit of metric**

> Pooled over all cell-months (or country-months) in every paper; no within-unit averaged AUC/AP. HydraNet averages metrics over the 36 test months (pooled over cells within each month).

**Calibration under drift**

> Not tested as calibration-in-the-large in any paper. Evidence of drift: ViEWS 2020 benchmark degraded substantially from the 2017-2019 test set to the true future; Tigray escalation dominated the true-future errors; HydraNet AP for sb decays from ~0.6 to <0.25 over the 36-month horizon; Hegre et al. 2025 note 2021 (Ethiopia, Ukraine) broke the exactly-zero baseline's CRPS. No recalibration method is applied; DynAttn's rolling monthly re-anchoring is the only adaptive mechanism.

**Uncertainty of gain**

> Vesco et al. 2022 bootstrap (1,000 resamples of predicted/observed pairs, i.i.d., not block) the MSE difference to the best model: at cm many intervals cross zero; at pgm Radford, Lindholm et al. and the ensemble are closest to the winner. Brandt, HydraNet and DynAttn report no CI or DM test on skill differences; HydraNet reports a single representative seed out of 12 (variability described as negligible after curriculum learning).

**Regime coverage**

> Not applicable to UA alert regimes (Jan-2025 drone surge, Dec-2025 raion reform, Sep-2026 yellow/red). Domain regime shifts covered: ViEWS 2020 true future includes the Tigray war onset (Nov 2020); DynAttn's Aug 2024-Jul 2025 test spans ongoing Sudan/Sahel/Ukraine wars at country level; HydraNet's 2016-2018 test is a comparatively stable period.

### Relevance

**Takeaways for project**

> 1) Supports 'simple + correct' (CLAUDE.md goal): in the field's own benchmark competitions, deep spatio-temporal models produced only small, metric-dependent gains and most models lost to no-change on some metrics. Do not add a ConvLSTM/GNN/attention model; it would need a new dependency and human approval, and the evidence does not justify it at 24 units x hourly. 2) The learned signal in all four papers is short-term own and neighbour history - exactly our D-017/feature list (minutes_since_last_start, onsets_last_24h/7d, neighbors_active_at_t, national_active_count_at_t). Brandt's 1-hop graph convolution is a learned version of our hand-coded symmetric border table in src/regions.py; with 24 nodes a GBM on neighbour aggregates captures the same structure. 3) HydraNet is the key warning for our metric choice: it 'wins' on AP but loses on Brier, even to no-change. Our primary metric is Brier skill vs the rolling recent-rate baseline (D-021), with PR-AUC/AUC secondary - keep that order, and do not tune on AP or use focal loss/class reweighting, which distorts probabilities and would hurt BSS and the required reliability plot (D-006). 4) Baseline discipline: Brandt compares only to RF, DynAttn's deep baselines are broken (near-zero R^2, Inf RMSE) - weak baselines inflate gains. Our required baselines (climatology, rolling recent rate, raw and calibrated persistence; D-021) are stronger than any used here; report honestly if the model does not beat recent rate. 5) Target design: HydraNet's binary 'any violence in month' is a state target, and the ViEWS log-change target conflates onset with escalation. Our onset target with the at-risk mask (rows under alert at t excluded; asserted by a test) avoids both inflations. 6) Same-script evaluation: HydraNet copies ViEWS numbers from an earlier paper; we score model and all baselines together in one run, once, at the end of M4 (D-021/CLAUDE.md test rule). 7) Proper scoring and metric choice change rankings (Brandt MSE vs CRPS; ViEWS TADDA changed post hoc): fix metrics before looking at the test (already done in CLAUDE.md), and never change them after seeing results. 8) Regime drift is large in conflict data (benchmark collapsed on the true future; AP decays with horizon); our D-015 new-regime check with calibration-in-the-large is the right analogue, and a failed transfer should be reported as such. 9) Ensembling diverse simple models helped most in ViEWS 2020; if time allows, averaging the model with the recent-rate baseline is a cheap, explainable variant - but only as an extra row with human approval, not a new milestone.

**Best practices**

> Adopt: prospective/true-future scoring and an independent, pre-fixed evaluation (ViEWS 2020); separate tuning partition from final-scoring partition and retrain with frozen hyperparameters (HydraNet; matches our train/val/test with no refit on train+val per D-021); report several seeds and pick a representative run, not the best; per-anchor standardisation and lagged predictors only (DynAttn; matches 'scalers fit on train only'); exponential decay-of-violence terms at several half-lives as features (DynAttn/ViEWS) - cheap and causal; ablate feature groups on the same sample (Brandt backward elimination); bootstrap CIs on skill differences (Vesco; we should use week-block, not i.i.d., bootstrap per D-013); report forecast degradation by horizon. Avoid: ranking-only headline metrics (AP/AUC) without a proper score; focal loss or reweighting when probabilities are the product; benchmarking against numbers copied from another paper instead of re-running baselines in the same pipeline; weak or broken baselines (RF-only, under-tuned LSTMs); state-type binary targets without an at-risk mask; changing the metric after seeing results; non-causal (centered/zero-padded) temporal convolutions unless a truncation test proves no leakage across the forecast origin; unacknowledged data vintages/revisions; claiming 'calibrated uncertainty' from MC dropout or a likelihood form without a reliability diagram.

### Other Info

**Uncertain fields (omitted above)**

- baseline_strength
- calibration
- code_available
- external_feature_timing
- features
- headline_results
- leakage_handling
- metrics
- popularity
- preprocessing
- test_window_hygiene

---

<a id="gbm_lag_features"></a>
## 18. Gradient boosting on lag + calendar features (M5 competition lessons, LightGBM)

*Category: methods* — Dominant practical model family for tabular time-series.

### Basic Info

**Name**

> Gradient boosting (LightGBM) on lag + rolling + calendar features for tabular time-series forecasting: M5 Accuracy competition lessons (Makridakis, Spiliotis & Assimakopoulos 2022), 'Forecasting with trees' (Januschowski et al. 2022), Kaggle forecasting review (Bojer & Meldgaard 2021), LightGBM (Ke et al. 2017), plus calibration (Niculescu-Mizil & Caruana 2005) and an event-forecasting analogue (Vestby et al. 2022)

**Type**

> method family (peer-reviewed competition-analysis papers + the LightGBM library/paper; not an air-alert study)

**Url**

> M5 Accuracy results: https://doi.org/10.1016/j.ijforecast.2021.11.013 (IJF 38(4):1346-1364; preprint PDF https://statmodeling.stat.columbia.edu/wp-content/uploads/2021/10/M5_accuracy_competition.pdf ); M5 Uncertainty: https://ideas.repec.org/a/eee/intfor/v38y2022i4p1365-1385.html ; Forecasting with trees: https://doi.org/10.1016/j.ijforecast.2021.10.004 (open PDF https://cdn.amazon.science/17/31/0d99831d4add92e711a56abc75f8/forecasting-with-trees.pdf ); Bojer & Meldgaard: https://doi.org/10.1016/j.ijforecast.2020.07.007 (arXiv https://arxiv.org/abs/2009.07701 ); LightGBM paper: https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf ; LightGBM repo: https://github.com/microsoft/LightGBM ; M5 winners' code: https://github.com/Mcompetitions/M5-methods ; top-4% simple direct LightGBM write-up: https://github.com/btrotta/kaggle-m5 ; Niculescu-Mizil & Caruana 2005: https://mlanthology.org/icml/2005/niculescumizil2005icml-predicting ; Vestby et al. 2022: https://www.prio.org/publications/13037 ; Hewamalage et al. (forecast evaluation pitfalls, leakage): https://arxiv.org/abs/2203.10716

**Year**

> M5 competition ran Mar-Jun 2020; results paper IJF 2022 (preprint Oct 2020). Forecasting with trees: IJF 2022 (online 2021). Bojer & Meldgaard: IJF 2021. LightGBM: NeurIPS 2017; library latest release v4.7.0 (2026-07-18), repo pushed 2026-10-17. Niculescu-Mizil & Caruana: ICML 2005. Vestby et al.: International Interactions 2022.

**Authors**

> Spyros Makridakis, Evangelos Spiliotis, Vassilios Assimakopoulos (M5); Tim Januschowski, Yuyang Wang, Kari Torkkola, Timo Erkkila, Hilaf Hasson, Jan Gasthaus (Amazon Research; Forecasting with trees); Casper Solheim Bojer, Jens Peder Meldgaard (Kaggle review); Guolin Ke, Qi Meng, Thomas Finley, Taifeng Wang, Wei Chen, Weidong Ma, Qiwei Ye, Tie-Yan Liu (LightGBM, Microsoft Research); M5 winner YeonJun In (YJ_STU, a senior undergraduate student in South Korea)

**Peer review status**

> peer-reviewed (IJF 2021/2022 papers; NeurIPS 2017; ICML 2005; International Interactions 2022). Competition rankings are organiser-verified (the M5 organisers reproduced the top-5 forecasts). Individual Kaggle write-ups (e.g. btrotta/kaggle-m5) are self-reported.

### Problem Framing

**Target type**

> Not an onset target in the source domain. M5 is a COUNT target (daily unit sales, highly intermittent, many zeros) evaluated as point forecasts (WRMSSE) over a 28-day horizon across 42,840 hierarchical series. The method family transfers directly to a binary onset target by switching the objective to binary log-loss (as our src/model.py already does). Note: the M5 tricks that exploit count structure (Tweedie/Poisson objectives, hierarchy multipliers) have no direct equivalent for our onset label.

**Target definition**

> M5 Accuracy: point forecasts of daily unit sales for the 30,490 product-store series, days 1,942-1,969 (H = 1..28 days), aggregated bottom-up to 12 hierarchy levels (42,840 series); scored by WRMSSE. M5 Uncertainty: 9 quantiles (0.005-0.995) of the same series. Generic GBM framing: y(i, t+h) regressed on features computed at origin t; either direct (one model per horizon or horizon band, lags >= h) or recursive (feed predictions back as lags). For our project the analogous definition is y(t) = 1 if a new alert starts in (t, t+H], H = 1 (or 3), per oblast.

**Spatial unit**

> M5: product x store (10 stores in 3 US states: CA, TX, WI), with category/department/state aggregates. No geography beyond state/store. For our use: oblast (24 units) as a pooled 'global' model with a unit categorical.

**At risk masking**

> Not applicable to M5 (count target, every day is 'at risk'). One analogous hygiene step in the top-4% write-up (btrotta): rows before a product's first sale in a store were EXCLUDED from training and from aggregate features, i.e. rows where the series was not yet 'live' were removed rather than treated as zeros. GBM libraries do not mask anything themselves: the at-risk mask (oblast not under alert at t) must be applied upstream, before the rows reach the booster (our project does this in the grid and asserts it in tests).

### Data

**Data sources**

> M5: Walmart daily unit sales, 1,941 days of history (29 Jan 2011 - 22 May 2016 for train+validation), 3,049 products, 10 stores, plus calendar (holidays, SNAP days, special events) and weekly sell prices. Validation phase: days 1,914-1,941 with a live public leaderboard (3 Mar - 31 May 2020); test phase: days 1,942-1,969, no leaderboard, ranks revealed 30 Jun 2020. Bojer & Meldgaard review six Kaggle forecasting competitions (e.g. Favorita grocery, Recruit restaurant visitors, Rossmann, Wikipedia traffic).

**Data source variant**

> Not applicable (retail sales, not air-alert data). The analogue for us: one official source (Vadimkin official_data_en.csv, frozen 2026-09-07) for train/val/test, alerts.in.ua API kept as a separate exploratory regime; never mixed (CLAUDE.md data rules).

**Preprocessing**

> M5 winners did little classic preprocessing; the M5 paper lists 'does not depend on data pre-processing and transformations' as a LightGBM advantage (trees are invariant to monotone transforms, handle NaN natively and categorical features natively). Real preprocessing effort went into feature construction: lags of sales, rolling means/std over several windows, price features (relative price, price momentum), calendar/event/SNAP flags, ID categoricals. btrotta excluded pre-first-sale rows and December. For our data the important preprocessing (dedup of 113,845 exact duplicate rows, admin-level union per oblast, D-020 causal 24h standing-alert cap, gap masking) is upstream of the GBM and is unaffected by model choice.

**Known label artefacts**

> M5-specific artefacts: heavy intermittency (many zero-sales days), out-of-stock zeros that look like zero demand, products entering the assortment late (leading zeros), Christmas store closures. Handling: Tweedie/Poisson objectives for the zero mass (winner: Tweedie negative log-likelihood; 4th place: Tweedie; 5th place: Poisson); excluding leading zeros (btrotta); excluding December or Christmas days. Transfer to our project: the equivalent artefacts (exact duplicate rows, exactly-30-minute durations kept per D-010, standing hromada alerts of 439-604 days handled causally by D-020, the 2026-08-30 to 09-01 recording gap masked per D-013) must be fixed in the label pipeline; a GBM will happily learn any artefact that is predictive (e.g. a feature that encodes a '30-minute naive end' or reads across the gap), so artefact handling matters MORE with flexible learners, not less.

### Method

**Model family**

> Gradient-boosted decision trees, predominantly LightGBM (histogram-based GBDT with leaf-wise growth, GOSS sampling and exclusive feature bundling; Ke et al. 2017 report up to 20x faster training than conventional GBDT at nearly the same accuracy). M5 top 5: (1) YJ_STU, equal-weight mean of LightGBM models trained per store (10), per store-category (30) and per store-department (70), each in a recursive and a non-recursive version, 220 models in total, each series forecast as the mean of 6 models; Tweedie loss; NO early stopping; (2) Matthias Anderer, LightGBM per store with calendar/price features only (no past sales), adjusted by multipliers from N-BEATS forecasts at the top 5 aggregation levels, custom asymmetric loss; (3) mf, ensemble of 43 LSTM-based DeepAR-style networks (the only non-GBM top-3 entry); (4) monsaraida, non-recursive LightGBM per store and per forecast week (40 models), Tweedie, no early stopping, no hyperparameter tuning; (5) Alan Lahoud, recursive LightGBM per department, Poisson, early stopping, store-department level multiplier matching the last 28-day mean. Almost all of the top 50 with a known method used recursive and/or non-recursive LightGBM per store/department.

**Features**

> Canonical M5 / Kaggle GBM feature set (Makridakis et al. 2022 sec. 4.2; Bojer & Meldgaard 2021; btrotta): (a) LAG features of the target: sales at lags 1..7, 14, 28 etc. (direct models only use lags >= the horizon, e.g. lag 28+ for a single 28-day model, or lags >= h for horizon-specific models; recursive models use short lags fed with their own predictions); (b) ROLLING statistics on lagged values: rolling mean/std/max over 7, 14, 28, 56, 180 days, always computed on data shifted so the window ends at or before the forecast origin; (c) CALENDAR: day of week, week, month, year, holiday/special-event flags, SNAP days (known in advance, so legitimately 'future' covariates); (d) PRICE/exogenous: sell price, relative price vs item mean, price change, promotions (top teams found price features important; Finding 7 'importance of exogenous/explanatory variables'); (e) IDENTIFIERS as categoricals: item, department, category, store, state (cross-learning across series: Finding 3, all top-50 used cross-learning, i.e. pooled 'global' models); (f) recency/zero-run features: days since last sale, length of zero-sales run (3rd place used zero-sales-period features). Mapping to our project: lags/rolling = onsets_last_24h, onsets_last_7d; recency = minutes_since_last_start / minutes_since_last_end (discrete-time hazard duration dependence); calendar = Kyiv hour, weekday; cross-series = neighbors_active_at_t, national_active_count_at_t; identifier = unit_code categorical. These are exactly the features in src/features.py.

**External feature timing**

> In M5 the exogenous inputs were either known in advance (calendar, events, SNAP days, announced prices) or lagged, so no publication-lag problem arose; the competition supplied future calendar and price files. For GBM in general, any exogenous series must be aligned at its PUBLICATION time, not its event time (Hewamalage et al. 2022 warn that features computed from the full series leak). For our onset model there are no external features (D-013 skipped Telegram/ISW/weather); if added, they must carry their real publication lag and be ablated against the same time-restricted sample.

**Ablation design**

> M5 paper does not report controlled feature ablations; evidence for feature value is from organiser benchmark comparisons (e.g. ESX with promotions/events was 6% better than ES_td without them; ARIMAX vs ARIMA similar) and from teams' own CV. The winner's selection criterion is the instructive part: candidate models were compared on the SAME last four 28-day rolling windows and judged by BOTH the mean and the standard deviation of error across windows; recursive models were more accurate on average but less stable, so they were combined with non-recursive ones. Our project's improve stage (feature blocks A/B/C compared on the same folds, 'folds improved' count, no block accepted) follows the same pattern.

### Evaluation

**Split scheme**

> M5: chronological; train days 1-1,913, public validation 1,914-1,941 (28 days, live leaderboard, max 5 submissions/day), then validation labels released and a blind 28-day test (1,942-1,969); one final submission selected per team. Top-4 teams and most of the top 50 used a private rolling-origin CV over at least the last four 28-day windows (4th place: last five windows; 3rd place: last fourteen windows; 5th place: a random sample of 500 days for validation, which is NOT a time-ordered split). Retraining on all data up to the origin before the final forecast was standard in M5 (teams re-estimated after validation labels were released). For our project, D-021 forbids a refit on train+val after early stopping; weekly refit is only an extra row (D-014).

**Metrics**

> M5 Accuracy: WRMSSE (weighted root mean squared scaled error, scaled by the in-sample one-step naive error, weighted by dollar sales, averaged over 12 hierarchy levels). M5 Uncertainty: WSPL (weighted scaled pinball loss over 9 quantiles). Improvements reported as % over the best benchmark (ES_bu, bottom-up exponential smoothing). No probabilistic classification metrics; for a binary onset target the corresponding proper scores are Brier / log loss and Brier skill vs a strong baseline (our D-021 primary metric).

**Unit of metric**

> M5: weighted average across all 42,840 series and 12 aggregation levels (dollar-weighted), i.e. pooled-with-weights; per-level scores also reported (Table 3). Not applicable to within-unit AUC; our project reports pooled AND mean within-oblast AUC, which matters because a pooled GBM with a unit categorical can earn pooled AUC just by ranking oblasts by base rate.

**Baseline strength**

> Strong and explicit in M5: 24 benchmarks (Naive, seasonal Naive, SES, MA, Croston, SBA, TSB, ADIDA, iMAPA, ES and ARIMA in bottom-up/top-down variants, ESX/ARIMAX, combinations, MLP and RF benchmarks). Of 5,507 teams only 2,666 (48.4%) beat Naive, 1,972 (35.8%) beat seasonal Naive and 415 (7.5%) beat the best benchmark ES_bu with their selected submission; the majority of teams were worse than ES_bu by more than 13%. Only the top 50 beat ES_bu by > 14%, the top 5 by > 20%, the winner by 22.4%. Lesson: a well-chosen simple baseline beats most GBM entries; GBM wins only with careful CV and features. The event-forecasting analogue is sobering: Vestby et al. (2022) gradient boosting for sub-national violence (de-)escalation was marginally WORSE than the ViEWS baseline on MSE. Our own result is consistent: pooled LightGBM Brier skill vs the rolling 14-day recent rate = -0.0101 on the final test (H = 1).

**Calibration under drift**

> Tree models cannot extrapolate outside the range of the training target/leaf values, so a level or base-rate shift after training shows up as calibration-in-the-large error. The M5 2nd and 5th place teams handled level/trend with EXTERNAL MULTIPLIERS (5th: rescale so each store-department mean matches the previous 28 days; 2nd: multipliers from N-BEATS at upper levels); the organisers list 'beneficial effect of external adjustments' as one of the three new M5 findings. Direct analogue in our project: the post-hoc 'V2 recent-rate offset' variant raised Brier skill from -0.0101 to +0.0172 (weekly refit + offset V4: +0.0203) but LOWERED within-unit AUC (0.6320 -> 0.5897), i.e. the gain came from matching the recent level, not better ranking. These were post-hoc and not the pre-registered headline.

**Uncertainty of gain**

> M5 reported no confidence intervals on rank differences between top teams; the winner's distinctive step was looking at the standard deviation of errors across four CV windows, a crude stability measure. The large gap between teams' 'best ever' submission and their selected submission (672 vs 415 teams would have beaten ES_bu) shows that single-window validation differences are noisy. No DM test or block bootstrap in the source papers. For our project, the D-013 week-block bootstrap CI on the gain over recent-rate is the appropriate tool; small Brier differences (e.g. blend weight 0.6 vs 0.7 differing by 2.1e-06) are within noise.

**Regime coverage**

> M5 test covered a single 28-day window (May-June 2016) with no regime change; robustness to regime shifts was not tested, and the organisers note that conclusions may not hold for non-retail data. Januschowski et al. emphasise that trees are robust black-box learners but are weak at extrapolating trends. For our air-alert setting, regime shifts (Jan-2025 drone surge, 2025 raion/hromada admin reform, Sep-2026 yellow/red reform) are the main threat to a GBM frozen at 2026-07-27; our new-regime check found Brier skill vs recent rate -0.0323 and mean predicted minus observed -0.0421, i.e. transfer failed.

### Leakage & Hygiene

**Leakage handling**

> GBM-specific leakage sources documented in this literature and in practice: (1) lag/rolling features computed without shifting to the forecast origin (a rolling mean that includes the target period); direct models must use lags >= horizon, otherwise in-sample training rows see values that are not available at forecast time; (2) recursive models evaluated on training data look better than they are (btrotta: forum evidence that the recursive approach was good on the training period 'by coincidence'); (3) features or scalers computed over the full series before splitting (Hewamalage et al. 2022: smoothing, decomposition, normalisation or tsfeatures/catch22-style features on the whole series leak); (4) public-leaderboard tuning (M5 paper: the leaderboard should be used for assessing methods, not for indirect hyperparameter or feature selection); (5) random-day validation (5th place sampled 500 random days) mixes future and past; (6) early stopping on the test window. Trees add one specific risk: they will exploit any feature that encodes future information perfectly (e.g. final alert duration), so truncation tests are essential. Our project addresses all of these: features are causal by construction, a truncation-invariance test covers features, baselines and model predictions, a negative control (final-duration feature, centred window) must be caught, purge at every cut-off (t + H <= cut-off), early stopping on validation only, no refit on train+val.

**Test window hygiene**

> M5 enforced hygiene structurally: the test labels were hidden, no leaderboard during the test phase, and each team had to SELECT ONE submission before ranks were revealed; the organisers reproduced the top-5 forecasts. They report that many teams picked a worse submission than their best one ('probably due to misleading validation scores'). Lesson: pre-commit one model and score the test once. Our project mirrors this with preregistration hashes and a joint access marker written before any test label is read (reports/final_test_access.json).

### Reproducibility

**Code available**

> Yes. LightGBM: https://github.com/microsoft/LightGBM (MIT, actively maintained, v4.7.0 released 2026-07-18; pinned as lightgbm==4.7.0 in our requirements.txt). M5 winning methods: https://github.com/Mcompetitions/M5-methods (organiser-collected code, last push 2023-04). Simple direct-LightGBM reference: https://github.com/btrotta/kaggle-m5. Lag/rolling feature tooling with origin-aware transforms: https://github.com/Nixtla/mlforecast (Apache-2.0, active). M5 data available on Kaggle (m5-forecasting-accuracy).

### Relevance

**Takeaways for project**

> 1) Our model choice is the community default: a single pooled ('global', cross-learning) LightGBM with a unit categorical and lag/recency/calendar/spatial features matches M5 Finding 3 and Bojer & Meldgaard; no need to justify a fancier model, and D-013's decision to skip hyperparameter search is consistent with the 4th-place team (no tuning) and btrotta's 'simple features, no magic'. 2) Beating a strong simple baseline is the exception, not the rule: in M5 92.5% of teams lost to ES_bu. Our negative BSS vs the rolling recent rate (-0.0101) is a normal outcome and must be reported honestly as D-021 requires. 3) The main GBM weakness is level/base-rate drift: trees cannot extrapolate. M5's 2nd and 5th place fixed it with multipliers matching recent level; our post-hoc recent-rate offset (V2) is the same idea and produced BSS +0.0172, but it was selected after the test was seen, so it can only be reported as post-hoc and proposed as a pre-registered component for any future model (needs the human's approval as a protocol/scope change). 4) Combining is the most robust gain (M5 Finding 2): the winner averaged 6 models per series; a pre-registered equal-weight blend of the LightGBM and the rolling recent rate (our V5 idea) is the most M5-consistent next step, chosen on validation only. 5) Validate on several rolling windows and look at the spread, not just the mean (winner's mean + std over 4 x 28-day windows); our single 4-week validation slice is thin, so the D-014 weekly refit row and the D-013 week-block bootstrap give the needed stability evidence. 6) Do not use class reweighting (is_unbalance/scale_pos_weight) on the onset label: it distorts probabilities and hurts Brier; keep objective='binary' and check calibration on validation (D-006, D-021). 7) Recursive multi-step is irrelevant at H = 1; for H = 3 use a direct label (y over (t, t+3]) as we do, avoiding recursive error accumulation. 8) External features: M5 Finding 7 says exogenous variables matter, but only when their timing is known; any future Telegram/ISW/launch features must use publication time and a time-fair ablation (D-013 lists them as limitations).

**Best practices**

> ADOPT: (a) one pooled global GBM across units with an ID categorical (cross-learning); (b) causal lag and rolling features shifted to the forecast origin, plus time-since-last-event features; (c) calendar features in local time (known in advance, safe); (d) direct (non-recursive) targets for multi-hour horizons; (e) rolling-origin CV over several recent windows, judging mean AND spread of the error; (f) early stopping on a time-later validation slice only (or a fixed number of rounds as the M5 winner and 4th place did, which avoids overfitting the validation slice); (g) equal-weight combinations of a few diverse models, including a strong simple baseline; (h) explicit level adjustment toward the recent rate if pre-registered; (i) pick ONE final submission before seeing the test and score it once; (j) check calibration with a reliability plot and recalibrate (Platt/isotonic) on validation only. AVOID: (1) rolling/lag features that include the target window or are computed on the full series before splitting; (2) tuning on the test or a public leaderboard (M5: many teams selected a worse submission due to misleading validation); (3) random-day validation splits for time series (5th place used 500 random days); (4) class reweighting when probabilities are the product; (5) reading pooled AUC as skill when the unit categorical alone separates high- and low-rate units (report within-unit AUC); (6) assuming M5 conclusions transfer: M5 is retail counts with a single 28-day regime-free test window, while our onset process has hard regime shifts and a much stronger naive competitor (recent rate); (7) refitting on train+val after early stopping without re-validating the number of rounds (forbidden by D-021).

### Other Info

**Uncertain fields (omitted above)**

- calibration
- headline_results
- popularity

---

<a id="sepsis_onset"></a>
## 19. Clinical event-onset prediction review (Moor et al. 2021, sepsis)

*Category: methods* — Label definition, horizon, indirect-labelling leakage; analog to at-risk masking.

### Basic Info

**Name**

> Moor, Rieck, Horn, Jutzeler & Borgwardt (2021) 'Early Prediction of Sepsis in the ICU Using Machine Learning: A Systematic Review'. Used here as a methods analogue for event-onset forecasting: label definition, horizon, case-control onset matching, and label circularity (indirect-labelling leakage).

**Type**

paper (systematic review, PRISMA) / method family (clinical event-onset prediction)

**Url**

> https://doi.org/10.3389/fmed.2021.607952 ; PMC full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC8193357/ ; medRxiv preprint (2020-08-31): https://www.medrxiv.org/content/10.1101/2020.08.31.20185207 ; review data/code: https://github.com/BorgwardtLab/sepsis-prediction-review

**Year**

2021 (Frontiers in Medicine 8:607952, published 28 May 2021); medRxiv preprint Aug 2020

**Authors**

> Michael Moor, Bastian Rieck, Max Horn, Catherine R. Jutzeler, Karsten Borgwardt (ETH Zurich, D-BSSE; SIB Swiss Institute of Bioinformatics)

**Popularity**

> 239 citations on Semantic Scholar (queried 2026-10-17). The companion GitHub repo BorgwardtLab/sepsis-prediction-review has 5 stars, no license file, last push 2020-08-31.

**Peer review status**

> peer-reviewed (Frontiers in Medicine). It reviews 22 peer-reviewed studies; preprints and gray literature were excluded.

### Problem Framing

**Target type**

> Onset. Every reviewed study predicts the START of sepsis, an event that is unobserved and is approximated by clinical criteria, within a horizon before onset. Patients already septic at or near admission are excluded from the cohort. That is the clinical analogue of our at-risk masking. The review notes that a state-like framing inflates scores. Example: Futoma et al. compared cases against controls at discharge (stable patients) and saw a 'drastic drop in performance' once that easy contrast was removed.

**Target definition**

> Heterogeneous across studies. 12/22 (54.5%) used Sepsis-2-type definitions: SIRS plus suspected or confirmed infection, ICD-9 995.9 plus a 5-h persisting SIRS window, or SIRS plus a blood culture plus an abnormal vital sign. 9/22 (40.9%) used Sepsis-3: suspected infection (antibiotics plus culture) together with an acute SOFA increase of 2 or more within a 72-h window, from 48 h before to 24 h after suspected infection, often with modified windows. One study used clinician tags (daily labels only). One defined onset as the earliest of an antibiotic prescription or qSOFA criteria. Horizon H: 19/22 (86.4%) used 'offline training + horizon evaluation'. Predictions are made at fixed lead times before the (matched) onset, typically 0 to 4 h, with one 'next day' study. Some used one fixed 4-h horizon. 2/22 used online training and evaluation, which predicts at every hour and needs a choice of how many hours before or after onset count as positive. The PhysioNet 2019 challenge shifted labels to 6 h before onset. The review recommends always reporting H = 3 h or 4 h.

**Spatial unit**

> Not spatial. The unit is the ICU patient stay (encounter), with hourly or irregular time stamps inside the stay.

**At risk masking**

> Partly, through cohort exclusion rather than row masking. Studies removed patients whose onset falls too early: Moor et al. dropped onset within the first 7 h (the review notes this 'drastically reduced' the cohort), Nemati required onset at least 4 h after admission, Desautels kept onset between 7 and 500 h, and Schamoni and Sheetrit excluded onset before day 2 or day 3. Bloch and Calvert excluded patients meeting SIRS at admission. After onset, case time series are truncated at onset, so post-onset hours are never scored. This is equivalent to our rule 'rows already under alert at t are excluded'. The difference: an ICU stay has a single onset, whereas our units have recurrent events and need a recurring risk set.

### Data

**Data sources**

> Literature search of Embase, Google Scholar, PubMed/Medline, Scopus and Web of Science. 974 records yielded 22 included studies (21 in the quality assessment). Underlying cohorts were mostly MIMIC-II/III, eICU, PhysioNet 2019 challenge data, and single-centre hospital EHRs (US/Europe). Only one non-Western cohort was included. Prevalence ranged from 3.3% to 63.6%, and 10/22 studies had 10% or less.

**Data source variant**

> Not applicable (no air-alert data). The analogue issue is that the same 'event' is labelled by different definitions (Sepsis-2 vs Sepsis-3 vs ICD codes vs clinician tags), and results are not comparable across definitions. Air alerts have the same problem across sources: official vs volunteer vs alerts.in.ua, oblast-only vs union of levels, and after Sep 2026 yellow vs red.

**Preprocessing**

> Typical pipeline in the reviewed studies: hourly binning or resampling of vitals and labs, forward filling or imputation (some use Gaussian-process imputation, as in Moor et al.'s MGP-TCN), cohort inclusion by age and length of stay, exclusion of early-onset cases, and truncation of case series at onset. Controls are assigned a pseudo-onset ('onset matching') and truncated there. Only 2/21 studies with computer-derived labels shared the label code, so the exact preprocessing is mostly not reproducible.

**Known label artefacts**

> 1) Onset time ambiguity: 'the exact sepsis onset is usually unknown', so onset is a proxy built from criteria with look-back windows (SOFA uses the worst values over the preceding 24 h; Sepsis-3 uses a 72-h window). The labelled onset time can therefore move relative to the true event. Analogue: an alert onset is an administrative announcement time, not the threat time, and sub-oblast alerts were merged into oblast intervals. 2) Indirect labelling / circularity: the label is computed from the same vitals and labs used as predictors, so classifiers 'may just confirm existing criteria'. The review argues it may be virtually impossible to separate label data from predictor data, and that even clinician tags carry indirect circularity. It notes no study had tested this empirically. 3) Control alignment: comparing cases against controls at discharge makes the task too easy. Random onset matching can create distributions that differ systematically, because onsets are not uniform over the stay. Moor et al. proposed absolute matching (same hours since admission) to avoid length-of-stay bias. 16/22 studies did not report how controls were matched. 4) Early-onset exclusion shrinks and biases the cohort. 5) Definition heterogeneity prevents meta-analysis. No alert-specific artefacts (duplicates, 30-min ends, standing alerts, recording gaps) apply.

### Method

**Model family**

> Across the 22 studies: gradient-boosted trees (e.g., InSight / XGBoost-type), random forests, logistic and ElasticNet regression, SVMs, Weibull-Cox proportional hazards (Nemati's AISE), RNN/LSTM (e.g., SepLSTM), temporal convolutional networks with multitask Gaussian-process imputation (Moor et al. MGP-TCN), and others. The review does not rank model families, because heterogeneity precludes that.

**Features**

> Hourly vital signs (heart rate, blood pressure, respiratory rate, temperature, SpO2), laboratory values (lactate, white cell count, creatinine, bilirubin, platelets, etc.), demographics, sometimes interventions and medications, plus derived trend and variability features (e.g., heart-rate variability, windowed statistics) and missingness indicators. Feature engineering was described in 81% of studies; predictor importance was explained in 38%. Spatial, calendar and external features are not applicable.

**Ablation design**

> Not part of the review. Individual studies rarely ran controlled ablations on identical samples. The key comparison the review highlights, Futoma's discharge-matched vs relative-matched controls, is effectively an evaluation-design ablation: same model, different control alignment, with a large change in measured performance.

### Evaluation

**Metrics**

> AUROC in almost all studies. AUPRC in only 6. Sensitivity, specificity and PPV at chosen thresholds in some. The PhysioNet 2019 utility score (rewards early, penalises late or false alarms) for challenge-based studies. The review warns that AUROC 'depends on class prevalence', can look high when minority-class detection is poor, and recommends reporting prevalence and AUPRC.

**Unit of metric**

> Pooled over patient time points or prediction instances within each study. No within-unit averaging (each patient contributes one onset), and no cross-study pooling, because no meta-analysis was done.

**Baseline strength**

> Weak. Most studies compared against clinical scores (SIRS, qSOFA, MEWS, SOFA) or other ML models, not against a strong naive forecaster. No climatology or recent-rate baseline exists in this literature. The review's main point is that weak or easy comparisons, especially discharge-time controls, overstate skill.

**Calibration**

> Not discussed in the review. Calibration of predicted probabilities is absent from the 14-item quality checklist, which is itself a gap.

**Uncertainty of gain**

> The review reports no CIs on skill differences. Stability or variance of results was reported by 62% of studies (a quality criterion). No study-level significance test on the gain over baselines is summarised.

**Regime coverage**

> Not applicable to air alerts. The analogue is the definition change from Sepsis-2 to Sepsis-3 (2016), which split the literature into incomparable groups. This mirrors how the Sep-2026 yellow/red reform changes what an 'onset' is, so pre- and post-reform metrics should not be pooled (our D-015 and D-007).

### Leakage & Hygiene

**Leakage handling**

> Discussed, or missed in the reviewed studies: 1) Label circularity: labels derived from features (SOFA from labs and vitals over 24-72 h windows) mean that data used to label onset overlap the data used to predict it. Within a horizon of a few hours, the inputs may already contain the label-defining abnormalities, so 'prediction' partly re-detects the criteria. Untested empirically in the literature. 2) Control alignment as hidden leakage: discharge-time controls encode 'patient is stable and leaving', information unavailable at a matched real-time point. Random matching can encode length-of-stay differences, and absolute matching is recommended. 3) Truncation at onset: case inputs must stop at the prediction time before onset, i.e. horizon evaluation. The review notes that predicting closer to onset is progressively easier, so reporting only H = 0 inflates skill. 4) Code to reproduce labels was released by only 2 studies, so leakage cannot be audited. Not covered: purging across temporal cut-offs, truncation tests, and causal feature audits.

**Test window hygiene**

> Not systematically reported. Hyperparameters were reported in only 29% of studies, platforms in 19%, analysis code in 10% and label code in 10%, so it is usually unknowable how often test sets were consulted. No pre-registration was reported. The review cites probable publication bias (no negative results).

### Results

**Headline results**

> 22 studies were included. Quality ranged from 36% to 93% of 14 criteria; Kaji et al. and Moor et al. were best at 93%, and none met all criteria. Reported AUROC in early-prediction setups ranged from 0.78 (Shashikumar, ElasticNet, 4 h) to 0.99 (Kam and Kim, SepLSTM, 0 h, only 360 encounters). Massive heterogeneity in sepsis definition, horizon, onset matching and outcomes precluded meta-analysis. 72.7% of studies gave no onset-matching details. Only 2 shared code and only 4 reported on public data. Whether the models beat naive baselines is generally unknown, since no strong naive forecaster was used.

### Relevance

**Takeaways for project**

> 1) Our at-risk masking (target rule; assert test) is the analogue of truncating case series at onset and excluding already-septic patients. Cite this as standard practice: scoring rows under alert would turn onset forecasting into state detection and inflate AUC, just as discharge-matched controls inflated sepsis scores (Futoma's 'drastic drop'). 2) Indirect-labelling leakage maps to our label-defining data: the onset label and features like active_at_t, minutes_since_last_end and neighbors_active are built from the same alert intervals. That is fine only if every feature uses data with timestamp <= t and the label uses (t, t+H]. The hidden analogue is the D-020 standing-alert rule: classifying an alert as standing via its final finished_at would be the same circularity (label logic reading the future). Keep the causal 24h cap and the negative-control leaky feature in tests/test_leakage.py. 3) Horizon reporting: performance gets easier closer to onset, so H must be fixed and stated (default H = 1). If H is varied, report all values rather than the best. Sepsis papers that reported only H = 0 looked best. 4) Control alignment maps to row sampling: we score ALL unmasked hourly rows (no sampling of negatives). That avoids the random or discharge-matching biases the review criticises. Do not subsample negatives for evaluation, and if negatives are downsampled for training, re-weight or recalibrate. 5) Prevalence and PR-AUC: the review's recommendation to report prevalence and AUPRC alongside AUROC matches our D-rule (PR-AUC and PR-AUC / base rate; print base rates at each stage). Report the base rate per group (Kyiv City / frontline / rear), since rear oblasts are rare-event. 6) Strong baselines: the sepsis literature's weakness is comparing against clinical scores only. Our rolling recent-rate baseline as primary BSS reference (D-021) is exactly the strong naive baseline that literature lacks. Say so in the README. 7) Definition changes: the Sepsis-2 to Sepsis-3 split shows that a target-definition change breaks comparability. That supports keeping the official and API (yellow/red) sources apart (D-007, D-015) and stating the onset definition (union of levels, D-020) precisely, with code. 8) Reproducibility checklist: release the label code (grid.py and the target builder), hyperparameters, package versions (pinned requirements.txt) and data-access instructions. These are criteria that 80-90% of sepsis studies failed. 9) Early-in-series exclusion: like dropping onset in the first 7 h of a stay, the first days after the 2022-03-23 series start and after the 2026-08-30 to 09-01 recording gap have unknown history. Mask or flag them (D-013) rather than treating them as 'no prior alert'. 10) Calibration is missing from the sepsis checklist; our required reliability plot (D-006) and calibration-in-the-large check go beyond that literature.

**Best practices**

> Adopt: (a) define the onset label in code and publish it; (b) state the horizon explicitly and report a fixed, pre-declared H (the review asks for 3-4 h; ours is 1 h); (c) exclude units already in the event state at prediction time (risk set) and truncate inputs at prediction time; (d) report prevalence plus AUPRC alongside AUROC; (e) describe exactly how negatives are formed, preferring full-population scoring or absolute alignment over random or end-of-stay matching; (f) validate externally or out of time (for us: walk-forward and the exploratory new-regime check); (g) publish hyperparameters, package versions and code; (h) explicitly discuss label circularity and test for it (our truncation test with a negative control is a direct empirical answer to the review's 'untested' gap). Avoid: (i) easy negatives (stable or discharge-time controls; for us, scoring rows under alert or quiet nights only); (ii) reporting only the easiest horizon; (iii) AUROC alone on rare events; (iv) labels computed with look-back or look-ahead windows that overlap the forecast origin without an audit; (v) comparing models only against weak rule-based scores; (vi) pooling results across different event definitions (Sepsis-2/3; for us official vs yellow/red); (vii) unreported test-set usage and no released code.

### Other Info

**Uncertain fields (omitted above)**

- calibration_under_drift
- code_available
- external_feature_timing
- split_scheme

---

<a id="scoring_rules_corp"></a>
## 20. Proper scoring rules + CORP reliability diagrams (Gneiting & Raftery 2007; Dimitriadis, Gneiting & Jordan 2021)

*Category: evaluation* — Brier skill, PAV reliability, Brier decomposition; upgrade for D-006 plot.

### Basic Info

**Name**

> Proper scoring rules and CORP reliability diagrams. Core: Gneiting & Raftery (2007), 'Strictly Proper Scoring Rules, Prediction, and Estimation' (JASA 102(477):359-378), and Dimitriadis, Gneiting & Jordan (2021), 'Stable reliability diagrams for probabilistic classifiers' (PNAS 118(8):e2016191118; arXiv preprint title 'Evaluating probabilistic classifiers: Reliability diagrams and score decompositions revisited'). Companions: Dimitriadis, Gneiting, Jordan & Vogel (2024), 'Evaluating probabilistic classifiers: The triptych' (IJF 40(3):1101-1122), and Dimitriadis, Duembgen, Henzi, Puke & Ziegel (2023), 'Honest calibration assessment for binary outcome predictions' (Biometrika 110(3):663-680)

**Type**

> method family (forecast-evaluation theory: proper scoring rules, skill scores, PAV/isotonic reliability diagrams, the CORP score decomposition MCB - DSC + UNC)

**Url**

> Gneiting & Raftery 2007: https://doi.org/10.1198/016214506000001437 (author PDF: https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) ; CORP: https://doi.org/10.1073/pnas.2016191118 (open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC7923594/ ; preprint: https://arxiv.org/abs/2008.03033) ; Triptych: https://arxiv.org/abs/2301.10803 (replication code: https://github.com/TimoDimi/replication_triptych) ; Honest calibration bands: https://arxiv.org/abs/2203.04065 (https://doi.org/10.1093/biomet/asac068) ; R package: https://CRAN.R-project.org/package=reliabilitydiag ; Python implementation with isotonic reliability diagrams and score decomposition: https://lorentzenchr.github.io/model-diagnostics/

**Year**

> 2007 (Gneiting & Raftery); 2021 (CORP, PNAS, published 17 Feb 2021; arXiv v1 7 Aug 2020); 2023 (honest calibration bands, Biometrika); 2024 (triptych, IJF). R package reliabilitydiag 0.2.1, last published 2022-06-29.

**Authors**

> Tilmann Gneiting, Adrian E. Raftery (2007). Timo Dimitriadis, Tilmann Gneiting, Alexander I. Jordan (CORP, 2021; HITS and KIT). Plus Peter Vogel (triptych, 2024). Timo Dimitriadis, Lutz Duembgen, Alexander Henzi, Marius Puke, Johanna Ziegel (honest bands, 2023). reliabilitydiag is maintained by Alexander I. Jordan.

**Popularity**

> Semantic Scholar citations (retrieved 2026-10-17): Gneiting & Raftery 2007 = 7,406; CORP (PNAS) = 111; triptych = 22. Gneiting & Raftery is one of the most cited papers in forecast evaluation. CORP is the current reference method for reliability diagrams in the probabilistic-forecasting literature (statistics, meteorology, economics).

**Peer review status**

peer-reviewed (JASA; PNAS; IJF; Biometrika). CORP and the triptych also have arXiv preprints.

### Problem Framing

**Target type**

> Not a forecasting application. The methods are generic for binary-event probability forecasts and suit our onset target directly: y in {0,1}, forecast p in [0,1]. Proper scoring rules and CORP diagrams do not stop a state target from inflating scores. They score whatever label they are given, so the onset vs state choice and the at-risk mask (CLAUDE.md Target) must be fixed before scoring. A state target would have a high-persistence, easy-to-discriminate structure, and CORP would report it as high DSC rather than flag it.

**Target definition**

> Generic binary event Y = 1 with forecast probability p. The Brier (quadratic) score is S(p, y) = (p - y)^2, negatively oriented. The log score is -log p if y = 1 and -log(1 - p) if y = 0. In the CORP paper's worked example the event is 'precipitation occurs' at Niamey, Niger, issued 24 h ahead daily, July-September 2016, n = 92. For our project the event is 'a new alert starts in (t, t+H]', H = 1 h, per oblast-hour.

**Spatial unit**

> Not applicable (method papers). The CORP example is a single station (Niamey). The methods apply to any pooled or per-unit set of forecast-observation pairs, so for us: pooled, per group (Kyiv City / frontline / rear), and per oblast.

**At risk masking**

> Not applicable in the papers. The scoring theory assumes a fixed set of evaluation cases, and all comparisons are valid only on the IDENTICAL set of rows. For us, the model and every baseline must be scored on exactly the same unmasked rows: the same at-risk mask, the same gap mask, and the same label-maturity rule. Then mean Brier, BSS and the CORP terms are directly comparable.

### Data

**Data source variant**

Not applicable (no air-alert data).

**Preprocessing**

> Not applicable. Method note: CORP needs no binning choice. The PAV algorithm pools forecast values into flat segments automatically, and identical forecast values (ties) stay in the same segment. That matters for our tie-heavy baselines: climatology takes one of only 168 hour x weekday values per oblast, raw persistence is 0/1, and the shrunken recent rate is discrete.

**Known label artefacts**

> Not applicable to air alerts. The relevant artefact is in the EVALUATION method: binning-and-counting instability. In the CORP paper, the EMOS reliability diagram for Niamey looks 'drastically distinct' with 9, 10 or 11 equal-width bins, one version showing a spurious spike in a sparsely populated bin. Equal-population bins do not fully fix this, because identical forecast values often fall on bin edges. The instability carries over to the binned Brier reliability component and to the Hosmer-Lemeshow statistic. Our current reliability_bins() in src/evaluate.py uses 10 fixed-width bins on [0,1]. With hourly onset base rates of a few percent, most rows fall in the [0, 0.1) bin, so the D-006 plot is controlled by bin choice. This is the artefact CORP removes.

### Method

**External feature timing**

> Not applicable. One timing caveat applies to how we use CORP. The UNC reference y_bar is the marginal event frequency OF THE EVALUATION SET, and the PAV recalibration is fitted in-sample on the evaluation set. Both are diagnostics computed after the fact. They are not causal forecasts and must never be reported as a baseline or applied as a recalibration (CLAUDE.md forbids statistics computed over the test period). Recalibration, if used, is fitted on validation only (D-021).

**Ablation design**

> Not applicable. The triptych paper recommends comparing competitors on the same cases with an MCB-DSC scatter plot. Isolines of equal mean score are diagonal lines DSC - MCB = constant, so one plot shows whether a model wins through better ranking (DSC) or better calibration (MCB). The same plot works for feature ablations evaluated on identical rows.

### Evaluation

**Split scheme**

> Not applicable. All the CORP inference (bands and asymptotics) assumes independent, or at least exchangeable, forecast cases. The authors say this 'may or may not be warranted' and call for future work on serially dependent data. Our test rows are strongly dependent in time (attack waves) and across oblasts (mass attacks), so the default iid resampling bands will be too narrow.

**Metrics**

> Brier score, log score, Brier skill score, CORP MCB / DSC / UNC (with the corresponding Murphy REL / RES / UNC), the in-sample R*, and reliability diagrams with consistency or confidence bands. The triptych adds ROC curves (discrimination) and Murphy curves. The area under the Murphy curve equals the mean Brier score (up to scaling), and the curve shows the economic value across cost-loss ratios. The CORP paper names the MCB measure as a candidate for a calibration test. The R package ships miscalibration_test(). Dimitriadis et al. 2023 give isotonicity-based calibration bands with finite-sample coverage guarantees, which also support a test of perfect calibration.

**Unit of metric**

> Pooled over the evaluation set. The decomposition must be recomputed (a new PAV fit) for every subset, because MCB and DSC are not additive across groups: per-group MCBs do not sum to the pooled MCB.

**Baseline strength**

> CORP Table 2 (Niamey, Brier, UNC = 0.244 for all): ENS mean score 0.266 (MCB 0.066, DSC 0.044), EPC 0.234 (0.022, 0.032), EMOS 0.232 (0.018, 0.030), Logistic 0.206 (0.017, 0.056). The raw ensemble does WORSE than the climatological uncertainty 0.244 because its miscalibration (0.066) exceeds its discrimination (0.044). EMOS and Logistic are equally well calibrated, and Logistic wins on discrimination. This shows how the decomposition explains a skill difference against a reference.

**Calibration**

> Main contribution. A CORP reliability diagram plots the PAV-recalibrated probability against the forecast probability, with no tuning parameters. It is consistent (it converges to the true conditional event probability), optimally binned (at rate n^(-2/3) in simulation it has lower MSE than 5, 10 or 50 fixed bins or quantile bins), and reproducible (the same data always give the same diagram). Recommended display: the CORP step curve, a 90% consistency band around the diagonal, a histogram or rug of the forecast values, and the MCB, DSC, UNC numbers in the panel. In simulations with 1,000 replicates, 90% bands had accurate or slightly conservative coverage under independence. The PAV fit is also the in-sample isotonic recalibration map. It may be used as a recalibrator only when it is fitted on a separate (validation) slice.

**Uncertainty of gain**

> Gneiting & Raftery 2007 recommend comparing mean scores on the same cases. Formal tests of equal predictive performance (Diebold-Mariano) are in the wider literature, not in CORP. CORP gives bands for the reliability curve, not for score differences. Its bands assume independence, so for dependent data they understate uncertainty. This is the authors' own caveat, not an empirical finding about alert data.

**Regime coverage**

> Not applicable (no alert data). Note that the Niamey example covers a single monsoon season (Jul-Sep 2016), and the methods say nothing about non-stationarity.

### Leakage & Hygiene

**Leakage handling**

> Not applicable as a forecasting pipeline. The leakage risks in using these tools are: (1) Fitting the PAV recalibration map on the test set and reporting the recalibrated Brier as model performance. In-sample PAV is optimistic: S_bar(p_hat) is the best any monotone recalibration could reach on those rows, and DSC is mildly over-estimated in small samples. Report MCB/DSC as diagnostics only. (2) Using the evaluation-set marginal rate y_bar as a 'climatology' baseline, which uses future labels. Our climatology baseline must stay the train-fitted hour x weekday rate (CLAUDE.md Baselines). (3) Choosing bin counts or plotting options after looking at test results, which CORP removes because it has no free parameters. That also supports the 'score the final test once' rule.

**Test window hygiene**

> Not applicable. Because CORP is parameter-free, the D-006 reliability plot can be specified fully in the M4 plan BEFORE the final test is scored. No bin count or band level is chosen after seeing test numbers. Fix the band level (90%) and the resampling scheme (block bootstrap, see takeaways) in advance.

### Reproducibility

**Code available**

> Yes. R: reliabilitydiag 0.2.1 on CRAN (GPL-3), with reliabilitydiag(), summary() for the MCB/DSC/UNC decomposition, plot() and miscalibration_test(). Replication code: GitHub TimoDimi/replication_DGJ20 (CORP) and TimoDimi/replication_triptych. Python: model-diagnostics (MIT), with plot_reliability_diagram(..., n_bootstrap=, confidence_level=) built on isotonic regression and decompose(y_obs, y_pred, scoring_function=...) for miscalibration/discrimination/uncertainty. No new dependency is needed for this project: CORP for Brier is about 15 lines with sklearn.isotonic.IsotonicRegression, already available through the pinned scikit-learn==1.9.1. Adding model-diagnostics would need the human's approval (CLAUDE.md).

### Relevance

**Takeaways for project**

> 1) Upgrade the D-006 reliability plot from 10 fixed-width bins to a CORP (PAV) reliability diagram. Our base rate is a few percent per oblast-hour, so the current reliability_bins() puts nearly all rows in [0, 0.1) and its shape depends on the bin choice. That is the instability the CORP paper documents. PAV handles our tie-heavy baselines (0/1 persistence, 168-value climatology, discrete shrunken recent rate) correctly by keeping ties together. Use a log-scaled or zoomed x-axis (for example 0-0.3) plus a rug or histogram of forecast values. Report MCB, DSC and UNC in each panel.
> 2) Decompose the PRIMARY metric (D-021). On identical rows, UNC is shared, so S_ref - S_model = (DSC_model - DSC_ref) - (MCB_model - MCB_ref), and BSS_vs_recent = [(DSC_m - DSC_r) - (MCB_m - MCB_r)] / S_ref. The README can then say whether the model beats (or fails to beat) the rolling recent-rate through ranking (DSC) or through calibration (MCB). The diagnosis is concrete: a high-DSC but high-MCB model needs recalibration on validation (D-021), not new features. Add one MCB-DSC scatter plot (triptych style) for the model and all four baselines, with iso-score lines.
> 3) Compute BSS as a ratio of MEAN Brier scores on the same rows, 1 - mean(BS_model) / mean(BS_recent), per group, as metric_table() already does. Never average per-row or per-oblast skill ratios. Per-case skill scores are improper (Gneiting & Raftery, after Murphy 1973), and averaging per-oblast ratios gives quiet rear oblasts with tiny reference Brier the same weight as busy ones. Because the reference (rolling recent-rate) does not depend on the model, ranking by aggregate BSS equals ranking by mean Brier, so the primary metric stays a proper comparison.
> 4) Keep the Brier score as the proper headline score. If log loss is added, clip p to [eps, 1 - eps] and say so. PAV-recalibrated probabilities can be exactly 0 or 1, so the log-score version of the CORP decomposition can be infinite on small per-oblast subsets. ROC-AUC and PR-AUC are not proper scores (they ignore calibration), so they stay secondary, as CLAUDE.md already says.
> 5) Bands under dependence (D-013). CORP's default bands assume independent cases, but onsets cluster across oblasts in the same hour and in time. The default 'resample y* ~ Bernoulli(p) per row' consistency band treats a mass attack as 24 independent coin flips and will look too tight. Use a confidence band from a week-block (or day-block) bootstrap that resamples whole time blocks across all 24 units together, refitting PAV in each replicate. Six test weeks are few, so label the band 'indicative'. If an iid consistency band is shown as well, label it as such. [Interpretation: the authors only flag the independence assumption; they did not test it on clustered data.]
> 6) Use CORP on the API new-regime check (D-015 (c)) and per group (D-013): a CORP curve per group (Kyiv City, frontline, rear), and the pooled one in addition. A curve below the diagonal means the frozen model over-predicts after the reform. Report calibration-in-the-large (mean predicted - observed) next to MCB, because MCB mixes the level shift with shape errors. MCB/DSC are not additive across groups, so compute each group with its own PAV fit.
> 7) Never treat CORP's in-sample outputs as forecasts. The PAV-recalibrated test Brier and the test-set y_bar reference use test labels. They are diagnostics, not a model or a baseline (CLAUDE.md forbids test-period statistics). If isotonic recalibration is adopted, fit it on validation [2026-06-29, 2026-07-27) and apply it to the same frozen model (D-021). Note that isotonic calibration on ~4 weeks of rare positives is step-like and can overfit, so prefer a check over a fitted calibration unless validation MCB is clearly large.
> 8) Fix the CORP settings (band level 90%, block length = 1 week, bootstrap reps, x-axis range) in the M4 plan before scoring. CORP has no bin count to tune after seeing test results, which fits the 'score the final test ONCE' rule.

**Best practices**

> ADOPT: (a) Strictly proper scores (Brier) as the headline and mean score over a fixed, identical row set for every forecaster. (b) CORP/PAV reliability diagrams instead of fixed or quantile bins, with forecast-value histograms and the MCB / DSC / UNC numbers printed. (c) Report the exact decomposition S = MCB - DSC + UNC, and explain skill gains against the reference as a DSC gain minus an MCB change. (d) An MCB-DSC plot (triptych) to compare all predictors in one figure. (e) Optionally, Murphy curves to show value across decision thresholds, e.g. for whom a 5% vs 20% alert-risk threshold matters. (f) Uncertainty bands by resampling that respects the dependence structure (time blocks across all units). (g) Fit any recalibration out of sample (validation only), and use in-sample PAV only for diagnosis. (h) Implement with sklearn IsotonicRegression, which is already pinned, rather than adding a dependency. AVOID: (1) Fixed-width bins at low base rates, where nearly everything falls in the first bin. (2) Choosing the bin count after seeing results. (3) Averaging per-case or per-oblast skill ratios; use the ratio of mean scores instead. (4) Treating the in-sample PAV-recalibrated score or the test y_bar as an achievable forecast or a baseline. (5) iid Bernoulli bands on clustered spatio-temporal events presented as definitive. (6) Using AUC or PR-AUC as the deciding metric, since they ignore calibration and are not proper scores. (7) Unclipped log loss on near-0/1 probabilities.

### Other Info

**Uncertain fields (omitted above)**

- calibration_under_drift
- data_sources
- features
- headline_results
- model_family

---

<a id="ts_cv_purging"></a>
## 21. Time-series CV, purging & embargo (Bergmeir & Benitez 2012; Lopez de Prado 2018)

*Category: evaluation* — Walk-forward and cut-off purging.

### Basic Info

**Name**

> Time-series cross-validation, purging and embargo. Core: Bergmeir & Benitez (2012), 'On the use of cross-validation for time series predictor evaluation' (Information Sciences 191:192-213), and Lopez de Prado (2018), 'Advances in Financial Machine Learning' (Wiley), ch. 7 'Cross-Validation in Finance' (purged k-fold + embargo) and ch. 12 (combinatorial purged CV, CPCV). Companions: Bergmeir, Hyndman & Koo (2018), 'A note on the validity of cross-validation for evaluating autoregressive time series prediction' (CSDA 120:70-83); Cerqueira, Torgo & Mozetic (2020), 'Evaluating time series forecasting models: an empirical study on performance estimation methods' (Machine Learning 109:1997-2028); Tashman (2000), 'Out-of-sample tests of forecasting accuracy: an analysis and review' (IJF 16(4):437-450); Racine (2000), hv-block CV (J. Econometrics); Hewamalage, Ackermann & Bergmeir (2023), 'Forecast evaluation for data scientists: common pitfalls and best practices' (DMKD 37(2):788-832); Roberts et al. (2017), CV for temporal/spatial structure (Ecography).

**Type**

> method family (evaluation protocol: walk-forward / rolling-origin evaluation, blocked and hv-block CV, purging of overlapping labels at cut-offs, embargo after test folds, CPCV)

**Authors**

> Christoph Bergmeir, Jose M. Benitez (Univ. Granada); Marcos Lopez de Prado; Christoph Bergmeir, Rob J. Hyndman, Bonsoo Koo (Monash); Vitor Cerqueira, Luis Torgo, Igor Mozetic; Leonard J. Tashman; Jeff Racine; Hansika Hewamalage, Klaus Ackermann, Christoph Bergmeir; David R. Roberts et al.

### Problem Framing

**Target type**

> Not applicable (method literature). Relevance to target type: purging is defined on the LABEL interval [t0, t1] of each row. For our onset target y(t) = 1 if a new alert starts in (t, t+H], the label interval is (t, t+H], so the purge width equals H. A state target ('under alert at t+H') would have the same label interval but much stronger serial dependence between neighbouring rows, which makes leakage through adjacent rows (the embargo argument) more damaging; the at-risk mask removes most of that persistence.

**Target definition**

> Generic: each observation i has features known at t_i,0 and a label determined by outcomes up to t_i,1 (Lopez de Prado's 't1' series). Bergmeir & Benitez use autoregressive embeddings: predict x_t from (x_{t-1}, ..., x_{t-p}), one-step horizon. For us: t_i,0 = t (hour start, UTC), t_i,1 = t + H, H = 1 default (H = 3 tested in M3b).

**Spatial unit**

> Not applicable (single series in Bergmeir/Cerqueira; single asset in Lopez de Prado). Roberts et al. 2017 extend blocking to spatial/hierarchical structure. For us: a panel of 24 oblast-level units sharing one clock; split blocks must contain all 24 units for the same hours.

**At risk masking**

> Not applicable in the papers. Interaction with our protocol: the masked (already-under-alert) rows are dropped AFTER purging; a purged row and a masked row are counted separately in src/evaluate.py eligibility() (exclusive order purge -> masked -> y_nan -> feature_nan), so the purge count is reported honestly even when the row would also be masked.

### Data

**Data source variant**

Not applicable (no air-alert data).

**Preprocessing**

> Not applicable directly. Method rules relevant to preprocessing (Hewamalage et al. 2023, Sec. 3): normalising, smoothing or decomposing the full series before splitting leaks the future; transformations and summary features must be fit on each training window only or recomputed over the input window; global models across unaligned series can leak when one series carries future information about another. These match CLAUDE.md 'Forbidden: centered windows, scalers/encoders fit on full data, any statistic computed over the test period'.

### Method

**Features**

> Not applicable (no forecasting features). Key distinction: purging and embargo act on LABEL overlap, not on feature look-back. A test-row feature that looks back into the training period (e.g. our onsets_last_7d at the first test hour) is legitimate, because that information is known at t. Feature-side leakage (a feature reading data after t) is not fixed by any split scheme; it needs causal construction plus a truncation test (our tests/test_leakage.py with its negative control).

**External feature timing**

> Not applicable. General rule from Hewamalage et al. 2023: summary statistics that will not be available at forecast time (e.g. full-day aggregates used for a next-day forecast) create a horizon mismatch; the label-maturity analogue for any rolling statistic built from labels is that a label for row s becomes known only at s + H.

**Ablation design**

> Cerqueira et al. 2020 and Tashman 2000 favour repeated out-of-sample evaluation over several origins for model/feature selection on non-stationary data. Feature or model comparisons must use identical rows per fold (our M7 block_acceptance does this: every candidate feature is known on the same eligible rows; 4 inner folds with cut-offs 2025-07-01, 2025-10-01, 2026-01-01, 2026-04-01, 14-day early-stopping slices and 8-week scoring windows, all before validation).

### Evaluation

**Split scheme**

> Recommendations by condition: (a) stationary series, pure AR model with uncorrelated residuals: standard or blocked K-fold CV is valid and uses data more efficiently (Bergmeir et al. 2018; check residual autocorrelation with Ljung-Box first, as forecast::CVar does). (b) Non-stationary real-world series: out-of-sample methods that preserve temporal order, especially hold-out repeated over several test periods, give the most accurate performance estimates (Cerqueira et al. 2020); rolling-origin is preferred whenever non-stationarity is present, and abrupt structural breaks in the unseen future cannot be handled by any scheme (Hewamalage et al. 2023). (c) Overlapping labels or serially correlated features with K-fold: purge plus embargo (Lopez de Prado 2018). (d) Walk-forward with train strictly before test: purging at the cut-off is required when H > 1 step; embargo is unnecessary because no training data lies after the test block.

**Unit of metric**

> Single series (pooled) in the papers. For panels, Roberts et al. 2017 stress blocking on the dependence structure; for us metrics are pooled and per unit/group, but the SPLIT is always by date over all 24 units together.

**Baseline strength**

> Hewamalage et al. 2023: always compare with the naive (no-change) forecast and, for seasonal data, the seasonal naive; in their leakage experiment a leaky setup made a random-walk forecast appear to beat the naive model (p of about 0.067), while the non-leaky version was significantly worse. Our analogue: the rolling recent-rate baseline (D-021) is the naive bar, and it must itself obey label maturity (s <= t - H).

**Calibration**

> Not addressed. Implication: any calibration map must be fitted on a slice that is purged with respect to the scored slice (our D-021: fitted on validation, which ends with t + H <= test start, and applied to the same frozen model).

**Calibration under drift**

> Indirect. Cerqueira et al. 2020 and Hewamalage et al. 2023 show that CV with future data in training underestimates error under non-stationarity; rolling-origin and repeated hold-out reveal drift that a single random split hides. Our measured base-rate shift (train 0.0903 vs validation 0.1179, D-025) is exactly the case where K-fold or blocked CV with future training data would be optimistic.

**Regime coverage**

> Not applicable (no alert data). General result: under regime change, CV schemes that train on data after the test fold leak the future regime level; only forward-only evaluation reflects deployment. Our test window (27 Jul - 7 Sep 2026) lies after the Jan-2025 drone surge and the 2025 raion reform; the Sep-2026 yellow/red reform is evaluated separately (D-015), and no CV scheme makes a pre-reform test informative about a post-reform regime.

### Leakage & Hygiene

**Leakage handling**

> Mechanisms documented in the literature: (1) Purging: drop training rows whose label window overlaps any test label window; for train-before-test this is 'keep a training row iff t + H <= cut-off'. (2) Embargo: drop training rows right after a test fold (only when training follows testing). (3) hv-block/non-dependent CV: drop rows within the lag/dependence distance of the test block. (4) Causal preprocessing: fit transformations per training window (Hewamalage et al.). (5) Row-index splitting pitfalls: scikit-learn TimeSeriesSplit gap counts rows; on a stacked panel (24 rows per hour) a row-index split can cut through an hour and put same-hour rows of other oblasts (strongly correlated in mass attacks) on both sides. What our project does (verified in code, 2026-10-17): src/evaluate.py eligibility()/availability() apply purge as ~(t + H <= b) at every slice end; isolate_test_labels() blanks every y with t + H > test start before M3; D-022/D-023 fix 'a training row with t + H = cut-off is kept'; tests/test_evaluate.py and tests/test_run_all.py assert purge counts (0 at H = 1; 2 x 24 = 48 rows per cut-off at H = 3, rows C-2h and C-1h); the rolling recent-rate baseline uses s in [t - 14d, t - H] (label maturity, D-021/D-025), which is purging applied online; the M7 weekly refit (scripts/run_improve.py refit_windows) fits on [start, C - 14d) with t + H <= C - 14d, early-stops on [C - 14d, C) with t + H <= C, and scores [C, next cut-off) only, so it purges at both inner cut-offs. Not needed in the project: an embargo, because no split ever trains on data after its scored block. Feature-side leakage is covered separately by the truncation test with a negative control (tests/test_leakage.py).

**Test window hygiene**

> Lopez de Prado's main warning is backtest overfitting: repeated trials on the same test path inflate apparent skill, so the number of trials should be recorded and the test should not guide model choice. Our analogues: D-021 'score the final test once', the code fingerprint pre-registration (D-028) and the run_all guard that refuses refits after the test marker exists; M7 post-hoc variants were pre-declared and are labelled post-hoc next to the frozen headline (proposed D-030), which is the honest reporting Lopez de Prado recommends.

### Reproducibility

**Code available**

> Not applicable for the papers (no code for Bergmeir & Benitez 2012). Implementations: R forecast::CVar (K-fold CV for AR models with Ljung-Box check); scikit-learn TimeSeriesSplit(gap, test_size, max_train_size), BSD-3; Lopez de Prado-style PurgedKFold / CPCV in temporalcv, skfolio, mizarlabs, fynance (mlfinlab went closed-source). No new dependency is needed for this project: purge and maturity rules are already a few lines in src/evaluate.py, src/baselines.py and scripts/run_improve.py.

### Relevance

**Takeaways for project**

> 1) Our purge rule is exactly Lopez de Prado purging specialised to forward-only splits: keep a training/early-stopping row iff t + H <= cut-off (D-022, D-023, ratified for D-014 in M8). Write it in the README in these terms and cite Lopez de Prado 2018 ch. 7. State plainly that at H = 1 on an hourly grid the purge removes 0 rows (labels (t, t+1] end at or before the cut-off), and that it binds at H = 3 (48 rows per cut-off), which the tests already pin. Keep those tests; they are the guard if H changes.
> 2) No embargo is needed and none should be claimed: no split in M3/M4/M7 trains on data after its scored block (train < validation < test; weekly refit fits only before C). Document why (embargo protects training data that FOLLOWS a test fold). If anyone proposes blocked or K-fold CV over the whole history, embargo would become necessary AND would still not fix regime leakage.
> 3) Do not adopt K-fold or blocked CV for this project. Bergmeir et al. 2018's validity conditions (stationary, purely autoregressive, uncorrelated residuals) fail: we have calendar and spatial features, a measured base-rate shift (train 0.0903 vs validation 0.1179, D-025), and known regime breaks (Jan-2025 drone surge, 2025 raion reform, Sep-2026 reform). Cerqueira et al. 2020 show forward-only, repeated hold-out is the most accurate estimator on non-stationary real data, which supports our walk-forward-by-date design (CLAUDE.md Evaluation) and the M7 inner rolling folds.
> 4) Split by DATE across all 24 units at once (CLAUDE.md). Never use sklearn TimeSeriesSplit on the stacked panel by row index: gap counts rows, not hours, and a row cut inside an hour separates same-hour oblasts that are strongly correlated during mass attacks (cross-sectional leakage, Roberts et al. 2017).
> 5) Label maturity is purging done online. Every rolling statistic built from labels (recent-rate baseline D-021/D-025, M7 offset and 14/30-day rate features, proposed D-030) must use s <= t - H. Keep the existing test (tests/test_baselines.py::test_recent_rate_label_maturity) and add the same check for any new label-derived feature.
> 6) Purging handles labels only. Feature look-back across a cut-off is legitimate (known at t); feature look-AHEAD is not fixed by any split, so the truncation test with its negative control (tests/test_leakage.py) remains the main leakage proof (D-023).
> 7) Embargo-like exclusions already exist for a different reason: the 24h post-gap mask (D-022) and NaN features after the gap (D-024) exclude rows whose state or inputs are unknowable, not rows that leak. Apply the same logic to the new-regime API window (D-015): the dump starts at 2026-09-12 17:16 UTC after a 7-12 Sep hole, so state is unknowable for the first 24h (D-020 cap) and 7-day look-back features are incomplete for the first 7 days; mask or NaN them and print the count, as D-024 does [recommendation; not checked against the M4 new-regime code].
> 8) Weekly refit (D-014): the current design (fit [start, C - 14d) with t + H <= C - 14d; early stopping [C - 14d, C) with t + H <= C; score [C, next C)) purges correctly at both inner cut-offs and respects 'no refit on train+val after early stopping' (D-021). Note in the README that each step therefore never trains on its most recent 14 days.
> 9) Uncertainty of the gain (D-013): use week blocks spanning all 24 units; if H > 1 is ever reported, note that overlapping labels reduce the effective sample size (Lopez de Prado's uniqueness argument), so row-level iid tests would be overconfident.
> 10) Backtest overfitting: the M7 post-hoc variants on the seen test are a multiple-trial situation (Lopez de Prado; Bailey et al. on PBO). Keep the pre-declared list, report every variant and the number tried, and keep the frozen headline (D-021, D-028); a clean estimate of any M7 winner needs new post-reform data.

**Best practices**

> ADOPT: (a) Forward-only, date-based walk-forward evaluation with all panel units in the same block (Tashman; Cerqueira et al.). (b) Purge at every cut-off with the rule t + H <= cut-off, applied to training AND early-stopping AND calibration slices, and report the purge count per cut-off (Lopez de Prado). (c) Label maturity (s <= t - H) for every rolling label-derived statistic. (d) Inner rolling-origin folds for model/feature selection, identical rows per candidate, all before validation. (e) A pre-registered, once-only final test and a recorded count of trials (anti-backtest-overfitting). (f) Separate tests for label leakage (purge counts) and feature leakage (truncation test with negative control). (g) Block bootstrap over time blocks for CIs; account for label overlap when H > 1. (h) Check residual autocorrelation (Ljung-Box) before ever trusting K-fold CV on a time series. AVOID: (1) Random K-fold or shuffled splits on time-series rows. (2) Blocked K-fold that trains on data after the test block for non-stationary series, even with purge+embargo, because it leaks the future regime level. (3) Row-index splits or row-count gaps on a stacked panel (sklearn TimeSeriesSplit default use). (4) Claiming 'purged' when H = 1 makes the purge a no-op, or omitting the purge when H > 1. (5) Fitting scalers, encoders, calibration maps or rate priors on data that includes the scored period. (6) Treating embargo as a fix for feature look-ahead. (7) Reporting the best of many variants tried on the same test path without disclosing the number of trials.

### Other Info

**Uncertain fields (omitted above)**

- data_sources
- headline_results
- known_label_artefacts
- metrics
- model_family
- peer_review_status
- popularity
- uncertainty_of_gain
- url
- year

---

<a id="rare_event_metrics"></a>
## 22. Rare-event calibration and PR-AUC vs ROC-AUC; pooled vs within-unit AUC

*Category: evaluation* — Imbalanced metrics; pooled AUC mostly measures which oblast is active.

### Basic Info

**Name**

> Rare-event calibration and PR-AUC vs ROC-AUC; pooled vs within-unit AUC. Core sources: Saito & Rehmsmeier (2015) 'The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets'; Davis & Goadrich (2006) 'The Relationship Between Precision-Recall and ROC Curves'; Boyd, Santos Costa, Davis & Page (2012) 'Unachievable Region in Precision-Recall Space and Its Effect on Empirical Evaluation'; Flach & Kull (2015) 'Precision-Recall-Gain Curves: PR Analysis Done Right'; McDermott, Zhang, Hansen, Angelotti & Gallifant (2024) 'A Closer Look at AUROC and AUPRC under Class Imbalance'; van Klaveren, Steyerberg, Perel & Vergouwe (2014) 'Assessing discriminative ability of risk models in clustered data'; Michael & Tian 'The Population and Personalized Areas Under the ROC Curve' (Statistica Sinica); Janes & Pepe (2008/2009) covariate-adjusted ROC; Hand (2009) H-measure; Van Calster et al. (2016) calibration hierarchy; van den Goorbergh et al. (2022) harm of class-imbalance corrections; Wilks (2010) Brier score sampling under serial dependence.

**Type**

> method family (evaluation methodology for imbalanced binary probability forecasts: discrimination metrics ROC-AUC / PR-AUC, clustered or within-unit concordance, calibration levels, effect of imbalance corrections on calibration)

**Url**

> Saito & Rehmsmeier 2015: https://doi.org/10.1371/journal.pone.0118432 (https://pmc.ncbi.nlm.nih.gov/articles/PMC4349800/) ; Davis & Goadrich 2006: https://doi.org/10.1145/1143844.1143874 (https://mlanthology.org/icml/2006/davis2006icml-relationship) ; Boyd et al. 2012: https://arxiv.org/abs/1206.4667 ; Flach & Kull 2015: https://papers.nips.cc/paper/2015/file/33e8075e9970de0cfea955afd4644bb2-Paper.pdf (project page https://www.cs.bris.ac.uk/~flach/PRGcurves/) ; McDermott et al. 2024: https://arxiv.org/abs/2401.06091 (NeurIPS 2024 poster https://neurips.cc/virtual/2024/poster/95133) ; van Klaveren et al. 2014: https://doi.org/10.1186/1471-2288-14-5 (https://pmc.ncbi.nlm.nih.gov/articles/PMC3897966/) ; van Klaveren et al. 2019 (calibrated model-based concordance): https://doi.org/10.1186/s41512-019-0055-8 ; Michael & Tian: https://www3.stat.sinica.edu.tw/statistica/fp/SS-2024-0100.html ; Janes & Pepe 2008 (Am J Epidemiol 168(1)) and the AROC working paper: https://biostats.bepress.com/uwbiostat/paper283 ; Hand 2009 (Machine Learning 77:103-123) and the hmeasure package: https://search.r-project.org/CRAN/packages/hmeasure/hmeasure.pdf ; Van Calster et al. 2016 (J Clin Epidemiol 74:167-176): https://repub.eur.nl/pub/87511 ; van den Goorbergh et al. 2022: https://doi.org/10.1093/jamia/ocac093 (https://pmc.ncbi.nlm.nih.gov/articles/PMC9382395/) ; Wilks 2010: https://doi.org/10.1002/qj.709 ; Baddeley et al. 2025 (spatial ROC): https://arxiv.org/abs/2506.03414 ; scikit-learn average_precision_score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html

**Authors**

> Takaya Saito, Marc Rehmsmeier (Univ. Bergen); Jesse Davis, Mark Goadrich; Kendrick Boyd, Vitor Santos Costa, Jesse Davis, C. David Page; Peter Flach, Meelis Kull; Matthew B. A. McDermott, Haoran Zhang, Lasse Hyldig Hansen, Giovanni Angelotti, Jack Gallifant; David van Klaveren, Ewout W. Steyerberg, Pablo Perel, Yvonne Vergouwe; Haben Michael, Lu Tian; Holly Janes, Margaret S. Pepe; David J. Hand (and Christoforos Anagnostopoulos for the H-measure follow-up); Ben Van Calster et al.; Ruben van den Goorbergh, Maarten van Smeden, Dirk Timmerman, Ben Van Calster; Daniel S. Wilks.

**Peer review status**

> peer-reviewed: PLoS ONE (Saito), ICML (Davis & Goadrich; Boyd), NeurIPS (Flach & Kull; McDermott), BMC Med Res Methodol (van Klaveren), Statistica Sinica (Michael & Tian), Am J Epidemiol / Biometrika (Janes & Pepe), Machine Learning (Hand), J Clin Epidemiol (Van Calster), JAMIA (van den Goorbergh), QJRMS (Wilks). Baddeley et al. 2025 is an arXiv preprint.

### Problem Framing

**Target type**

> Generic binary event; not an air-alert application. The metric issues bite hardest on our ONSET target with an at-risk mask: masking removes the easy 'already under alert' rows, so discrimination must come from genuinely predicting new starts. A state target would raise every metric (ROC-AUC, PR-AUC and Brier skill against a weak reference) through persistence, which none of these metrics flags by itself.

**Target definition**

> Generic: Y in {0,1}, score or probability p. For the project: y(t) = 1 if a new alert starts in (t, t+H], H = 1 h (H = 3 h in reports/official_h3), on unmasked oblast-hours only. Project base rates from reports/official/metrics_validation.csv (validation [2026-06-29, 2026-07-27)): overall 0.118 (1,316 positives of 11,160 rows). From reports/official/metrics.csv (6-week final test, first accessed 2026-10-13 per reports/final_test_access.json): overall 0.139, Kyiv City 0.123, frontline 0.479, rear 0.088. So this is a MODERATELY imbalanced problem overall, with very different prevalence across groups. The cross-group prevalence spread matters more for metric choice than the overall imbalance.

**Spatial unit**

> Not applicable in the method papers. The clustered-AUC papers treat 'cluster' generically (hospital centres in van Klaveren; police districts or areas in Michael & Tian's urban policing application). For us: cluster = oblast (24 units minus exclusions), with groups Kyiv City / frontline / rear.

**At risk masking**

> Not applicable in the papers. For us: all metrics must be computed on exactly the same unmasked rows for the model and all baselines (src/evaluate.py metric_table already does this). The mask changes prevalence per oblast in a way that depends on how often the oblast is under alert. Frontline oblasts lose most of their hours to the mask, and the remaining at-risk hours have a base rate near 0.48. This makes PR-AUC levels not comparable across groups.

### Data

**Data source variant**

> Not applicable (no air-alert data in the sources). Project numbers are from the official Vadimkin dataset only (D-007), with no mixing with API data.

**Preprocessing**

> Not applicable. Metric-computation note: scikit-learn average_precision_score computes AP = sum_n (R_n - R_{n-1}) P_n, a step-wise sum with no interpolation, which the docs contrast with trapezoidal area under the PR curve as 'too optimistic'. Davis & Goadrich show that linear interpolation in PR space is invalid. So the project's 'PR-AUC' is AP (CLAUDE.md already says PR-AUC = average precision), and it should never be computed with sklearn.metrics.auc(recall, precision).

### Method

**Model family**

> Evaluation methods, not models. (1) ROC-AUC = P(score of a random positive > score of a random negative). It is invariant to prevalence and to any monotone transform, so it ignores calibration. (2) PR-AUC / average precision: depends on prevalence. A random classifier's precision equals the base rate, and the unachievable-region floor rises with skew (Boyd 2012). PR-Gain (Flach & Kull 2015) rescales precision and recall against the always-positive baseline to give a universal baseline. (3) McDermott et al. 2024, Theorem 1: AUROC = 1 - E[FPR at positive scores], while AUPRC = 1 - P(y=0) E[FPR / firing rate], so AUPRC up-weights false positives at high thresholds. Theorem 2: AUROC rewards fixing any misordered pair equally, while AUPRC rewards fixes at high scores more. Theorem 3: under calibration and a large prevalence gap between subgroups, the fix that most raises AUPRC lies inside the HIGH-prevalence subgroup. (4) Clustered AUC: between-cluster vs within-cluster concordance (van Klaveren 2014), and population vs personalized AUC (Michael & Tian), which can diverge in either direction (Simpson-type paradox). (5) Covariate-adjusted ROC, AROC (Janes & Pepe): a weighted average of covariate-specific ROC curves, i.e. ROC conditional on the stratifier. (6) H-measure (Hand 2009): AUC implicitly averages misclassification costs with a model-dependent weight. H uses a fixed Beta prior over costs; Hand & Anagnostopoulos suggest Beta(pi1+1, pi0+1) for unbalanced data. (7) Calibration hierarchy (Van Calster 2016): mean (calibration-in-the-large), weak (logistic intercept 0 and slope 1), moderate (event rate R% among forecasts of R%), strong (calibrated for every covariate pattern). They prove moderate calibration guarantees non-harmful decisions.

**Features**

> Not applicable (no forecasting features). Implementation pieces for the project: sklearn.metrics.roc_auc_score and average_precision_score (already used in src/evaluate.py); a groupby('unit') loop for within-unit ROC-AUC (already present, unweighted mean); optionally the same loop for within-unit AP and AP / unit base rate; optionally a groupby('t') loop for a cross-sectional 'within-hour' AUC that ranks oblasts against each other at the same forecast time (an interpretation added here, not from a source). No new dependency is needed.

**External feature timing**

Not applicable.

**Ablation design**

> Not applicable in the sources. Implication: feature ablations should be judged on Brier / BSS and within-unit AUC on identical rows. Pooled ROC-AUC barely moves for features that only add within-oblast timing signal, because it is dominated by between-oblast separation.

### Evaluation

**Split scheme**

> Not applicable. Wilks (2010): serial correlation inflates the sampling variance of the Brier score and BSS, so iid confidence intervals are too narrow and p-values too small. The same applies to AUC and AP computed on hourly, clustered rows.

**Metrics**

> ROC-AUC (pooled, within-cluster, covariate-adjusted), PR-AUC / average precision (raw, relative to prevalence, PR-Gain), H-measure, calibration-in-the-large, calibration intercept and slope, moderate-calibration (reliability) curves, Brier score and Brier skill score.

**Unit of metric**

> This is the core issue. A pooled AUC over oblast-hours mixes (a) between-oblast separation (frontline vs rear), (b) between-period separation within an oblast (active vs quiet weeks), and (c) hour-to-hour timing. The project's own numbers show it. Validation: model pooled ROC-AUC 0.884 vs within-unit mean 0.606; rolling recent-rate pooled 0.883 vs within-unit 0.491; climatology 0.850 vs 0.516; calibrated persistence 0.881 vs 0.588. Final test: model 0.875 vs 0.632; recent-rate 0.870 vs 0.491. A 14-day rolling rate is nearly constant within an oblast over a few weeks, so it ranks at chance within an oblast, yet it matches the model on pooled AUC. Pooled AUC here mostly measures 'which oblast is busy', as the outline note says. Within-group (rear) numbers repeat the pattern (final test: model pooled 0.878 vs within 0.642), because rear oblasts also differ a lot in base rate.

**Baseline strength**

> Not applicable in the sources. For the project, the pooled-vs-within gap is itself a baseline diagnostic. A forecaster whose pooled AUC is near the model's but whose within-unit AUC is near 0.5 (recent-rate) shows that pooled AUC cannot separate the model from a per-oblast constant. Brier skill vs the rolling recent rate (D-021) is the right headline. On it, the model is at -0.0097 on validation and -0.010 on the final test overall, i.e. it does NOT beat recent-rate on the primary metric while still winning on within-unit AUC (0.606-0.632 vs 0.491). This is a reportable 'better ranking within oblasts, slightly worse overall Brier' result.

**Calibration under drift**

> Not addressed directly by the discrimination papers. In the calibration hierarchy, calibration-in-the-large (mean predicted - observed) is the level that drifts first under a base-rate shift, and ROC-AUC is blind to it. Project final-test calibration-in-the-large (reports/official/calibration_in_the_large.csv): model -0.006 overall, but -0.075 frontline, -0.030 Kyiv City and +0.006 rear. The overall number hides group-level miscalibration of opposite sign, so calibration-in-the-large must be reported per group (as D-015 (c) already requires for the new regime). PR-AUC also shifts mechanically with base rate (Boyd 2012), so before/after-reform PR-AUC differences must be read through PR-AUC / base rate or PR-Gain, not raw AP.

**Uncertainty of gain**

> Wilks 2010: serial dependence inflates the variance of Brier and BSS, so iid intervals are too narrow. van Klaveren 2014: cluster-specific c-indexes vary a lot (IQR 0.70-0.81 across 35 centres), and they recommend pooling them by meta-analysis (fixed or random effects) to get a summary and a heterogeneity estimate. The 2019 paper warns that c-indexes in small clusters are too extreme and proposes a calibrated model-based concordance. For the project: within-unit AUCs from units with only 10-30 positives in a 4-6 week window are noisy. Report the spread (or a week-block bootstrap, D-013) together with the mean.

**Regime coverage**

> Not applicable (no alert data). Note: McDermott's Theorem 3 matters for regime comparisons. After the yellow/red reform the per-oblast prevalence pattern changes, so pooled AP shifts toward whatever subgroup became higher-prevalence, independent of model quality.

### Leakage & Hygiene

**Leakage handling**

> Not a leakage topic in the sources, but three metric-hygiene risks are leakage-like: (1) Normalising PR-AUC by the TEST base rate is fine as a descriptive ratio, but a 'prevalence-adjusted' score must not be fed back into model selection on test. (2) Choosing min_class_per_unit, the set of units, or the weighting of the within-unit mean after seeing test numbers is a forking-paths risk. Fix them in the pre-registration (reports/official/preregistration.json exists for that). (3) Any fitted recalibration (Platt or isotonic) must be fitted on validation and applied to the frozen model (D-021), never fitted on test rows. Diagnostic calibration curves on test are fine.

### Reproducibility

**Code available**

> Yes, for what the project needs: scikit-learn (already pinned) has roc_auc_score and average_precision_score. Within-unit AUC is in src/evaluate.py within_unit_auc. Optional extras would need a new dependency and the human's approval: hmeasure (R/Python), prg (Flach's PR-Gain code, linked from https://www.cs.bris.ac.uk/~flach/PRGcurves/), reliabilitydiag (R). PR-Gain and within-unit AP are a few lines each without any dependency.

### Relevance

**Takeaways for project**

> 1) Treat pooled ROC-AUC as a between-oblast metric, not a skill metric. Our own validation numbers show recent-rate tying the model on pooled AUC (0.883 vs 0.884) while ranking at chance within oblasts (0.491 vs 0.606). The README should say so explicitly and lead discrimination results with the within-unit mean AUC (CLAUDE.md already requires both). [Interpretation: the gap comes mainly from between-oblast base-rate differences plus slow between-week variation.]
> 2) Keep Brier skill vs rolling recent-rate (D-021) as the headline. Neither AUC nor PR-AUC is a proper score or sensitive to calibration, and both are rank-based. The current result (BSS about -0.01 overall, positive in Kyiv City +0.074 on the test) should be reported as 'does not beat recent-rate on the primary metric overall' (D-021 says this is valid and reportable), with within-unit AUC as supporting evidence that the model adds within-oblast timing signal.
> 3) Do not compare raw PR-AUC across groups or regimes. Frontline at-risk base rate is 0.479 vs rear 0.088, and Boyd's unachievable region makes raw AP rise with prevalence. Keep PR-AUC / base rate (already in metric_table), and say that it is still not fully prevalence-free (the floor is not linear in prevalence). This matters most for the D-015 before/after comparison, where the base rate changes with the reform.
> 4) Pooled PR-AUC is dominated by the high-prevalence frontline rows (McDermott Theorem 3). Overall model PR-AUC (0.466 validation) mainly reflects frontline performance. Report PR-AUC per group, and optionally an unweighted within-unit mean AP / unit base rate.
> 5) Report the within-unit selection explicitly. The within-unit mean currently drops 8-10 units (min 10 positives and 10 negatives), including Kharkivska and Dnipropetrovska. Print the dropped list next to the number (metric_table already stores it) and consider a sensitivity row with min_class = 5, labelled post hoc, or a positives-weighted mean. Small-cluster c-indexes are noisy and too extreme (van Klaveren 2019), so also show the spread (min / median / max, or a per-unit table from reports/official/metrics_by_unit.csv).
> 6) Consider a cross-sectional 'within-hour' AUC (rank the oblasts at each forecast time t, average over t with at least one positive and one negative). It isolates the spatial-targeting skill that within-unit AUC averages out, so the three numbers (pooled, within-unit, within-hour) separate 'which oblast', 'when' and 'where, given a wave'. This is a suggestion from this review, not from a source, and it is post hoc on the test window, so label it as such.
> 7) Calibration: report calibration-in-the-large per group, not only overall. On the final test the overall -0.006 hides -0.075 frontline and +0.006 rear. Keep the plain binary objective (no class weights, no resampling) per van den Goorbergh 2022. If recalibration is ever fitted, fit it on validation only (D-021). Since group-level CITL errors have opposite signs, a single global Platt fit would not fix them; a per-group intercept fitted on validation would be the minimal option and needs the human's approval as a model change.
> 8) Uncertainty: per-unit and per-group AUC and Brier from 4-6 weeks of hourly, clustered data have iid standard errors that are too small (Wilks 2010). Use the D-013 week-block bootstrap for the model-minus-recent-rate gain, and do not claim significance from iid DeLong tests.
> 9) For the new-regime check (D-015 (c)), within-oblast AUC plus per-group calibration-in-the-large is the right pair: AUC tells whether the ranking transferred, CITL tells whether the level transferred. Raw PR-AUC changes would mostly reflect prevalence change.

**Best practices**

> ADOPT: (a) A strictly proper score (Brier, BSS vs the strongest baseline) as the headline; rank metrics as secondary. (b) Report pooled AND within-unit ROC-AUC side by side, and treat a large gap as a sign that pooled AUC measures between-unit differences. (c) Report the within-unit eligibility rule and the excluded units with the number. (d) Report AP (step-wise, not trapezoidal) together with its prevalence, and the ratio AP / prevalence or PR-Gain when comparing settings with different base rates. (e) Per-group metrics whenever prevalence differs a lot between groups. (f) Calibration at the 'moderate' level (reliability curve) plus calibration-in-the-large per group. (g) Train on the natural class balance; fit any recalibration out of sample. (h) Dependence-aware uncertainty (block bootstrap) for clustered, autocorrelated rows. (i) Fix metric definitions before the test is opened. AVOID: (1) Calling a high pooled AUC 'skill' when a per-unit constant reaches the same value. (2) Choosing PR-AUC over ROC-AUC 'because the data are imbalanced' without a decision-based reason (McDermott 2024). (3) Comparing raw PR-AUC across groups, horizons (H = 1 vs H = 3) or regimes with different base rates. (4) Trapezoidal PR area via sklearn.metrics.auc(recall, precision). (5) Undersampling, oversampling, SMOTE or class weights when probabilities are the product. (6) An overall calibration number only, which can hide opposite-sign group errors. (7) iid confidence intervals or DeLong tests on hourly clustered data. (8) Adding new metrics after seeing the test results without labelling them as post hoc.

### Other Info

**Uncertain fields (omitted above)**

- calibration
- data_sources
- headline_results
- known_label_artefacts
- popularity
- test_window_hygiene
- year

---

<a id="forecast_comparison_tests"></a>
## 23. Comparing forecasts: Diebold-Mariano, Giacomini-White, block bootstrap

*Category: evaluation* — Is the gain over recent-rate real? Clustered events need block resampling.

### Basic Info

**Name**

> Comparing forecasts: tests of equal predictive accuracy and dependence-aware resampling. Core: Diebold & Mariano (1995), 'Comparing Predictive Accuracy' (JBES 13(3):253-263); Harvey, Leybourne & Newbold (1997), 'Testing the equality of prediction mean squared errors' (IJF 13(2):281-291); Giacomini & White (2006), 'Tests of Conditional Predictive Ability' (Econometrica 74(6):1545-1578); Diebold (2015), 'Comparing Predictive Accuracy, Twenty Years Later: A Personal Perspective on the Use and Abuse of Diebold-Mariano Tests' (JBES 33(1)). Resampling: Kuensch (1989) moving-block bootstrap; Politis & Romano (1994) stationary bootstrap; Politis & White (2004) automatic block length, corrected by Patton, Politis & White (2009). Panel / spatial / verification extensions: Qu, Timmermann & Zhu (2024), 'Comparing forecasting performance with panel data' (IJF 40(3):918-941); Hering & Genton (2011), 'Comparing spatial predictions' (Technometrics 53(4):414-425); Gilleland, Hering, Fowler & Brown (2018), 'Testing the tests' (MWR 146(6):1685-1703); DelSole & Tippett (2014, 2016) skill-comparison and random-walk/sign tests; Coroneo & Iacone (2020) fixed-smoothing DM. Multiple comparisons: Hansen (2005) SPA test; Hansen, Lunde & Nason (2011) Model Confidence Set. Related caveats: Clark & West (2007) nested models; Lerch et al. (2017) forecaster's dilemma.

**Type**

> method family (statistical inference on forecast-score differences: DM-type t tests with HAC variance, conditional predictive ability tests, block/stationary bootstrap of score differences, panel and spatial variants, multiple-comparison corrections)

**Url**

> DM 1995: https://doi.org/10.1080/07350015.1995.10524599 ; Diebold 2015 retrospective: https://www.nber.org/papers/w18391 (https://ideas.repec.org/a/taf/jnlbes/v33y2015i1p1-1.html) ; HLN 1997: https://doi.org/10.1016/S0169-2070(96)00719-4 ; GW 2006: https://econometricsociety.org/publications/econometrica/2006/11/01/tests-conditional-predictive-ability ; GW critique (Zhu & Timmermann): https://arxiv.org/abs/2006.03238 ; Panel DM (Qu, Timmermann & Zhu 2024): https://ideas.repec.org/a/eee/intfor/v40y2024i3p918-941.html (working paper: https://rady.ucsd.edu/_files/faculty-research/timmermann/Panel_DM.pdf) ; Hering & Genton 2011: https://doi.org/10.1198/TECH.2011.10136 (R: https://rdrr.io/cran/verification/man/predcomp.test.html) ; Gilleland et al. 2018: https://doi.org/10.1175/MWR-D-17-0295.1 ; DelSole & Tippett 2016 random-walk test: https://repository.library.noaa.gov/view/noaa/65048 ; Coroneo & Iacone 2020: https://doi.org/10.1002/jae.2756 (https://eprints.whiterose.ac.uk/155897/) ; Patton, Politis & White 2009: https://public.econ.duke.edu/~ap172/Patton_Politis_White_2009.pdf ; Hansen 2005 SPA / MCS 2011: https://ideas.repec.org/a/ecm/emetrp/v79y2011i2p453-497.html ; Clark & West 2007: https://www.nber.org/papers/t0326 ; Lerch et al. 2017: https://doi.org/10.1214/16-STS588 ; Software: statsmodels diebold_mariano_test https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.diebold_mariano_test.html ; arch time-series bootstraps https://arch.readthedocs.io/en/latest/bootstrap/timeseries-bootstraps.html and multiple comparison (SPA, StepM, MCS) https://arch.readthedocs.io/en/latest/multiple-comparison/multiple-comparison-reference.html ; R forecast::dm.test https://pkg.robjhyndman.com/forecast/reference/dm.test.html ; scores (Python) DM tutorial https://scores.readthedocs.io/en/stable/tutorials/Diebold_Mariano_Test_Statistic.html

**Authors**

> Francis X. Diebold, Roberto S. Mariano; David Harvey, Stephen Leybourne, Paul Newbold; Raffaella Giacomini, Halbert White; Hans R. Kuensch; Dimitris N. Politis, Joseph P. Romano; Andrew Patton; Ritong Qu, Allan Timmermann, Yinchu Zhu; Amanda S. Hering, Marc G. Genton; Eric Gilleland, Tressa L. Fowler, Barbara G. Brown; Timothy DelSole, Michael K. Tippett; Laura Coroneo, Fabrizio Iacone; Peter R. Hansen, Asger Lunde, James M. Nason; Todd E. Clark, Kenneth D. West; Sebastian Lerch, Thordis L. Thorarinsdottir, Francesco Ravazzolo, Tilmann Gneiting. Software: statsmodels developers; Kevin Sheppard (arch); Rob Hyndman (forecast).

**Peer review status**

> peer-reviewed (JBES, IJF, Econometrica, JASA, Annals of Statistics, Econometric Reviews, Technometrics, MWR, J. Applied Econometrics, J. Econometrics, Statistical Science). The illustrative numbers computed for our project in this entry (see headline_results) are this researcher's own unreviewed computation on already-scored predictions, not a pipeline output.

### Problem Framing

**Target type**

> Not a forecasting application: the methods test whether the expected loss of two forecasts differs, for any target. They apply directly to our onset target with Brier loss, d_it = (p_model,it - y_it)^2 - (p_recent,it - y_it)^2. Like proper scores, they do not protect against a state target: a state target with strong persistence would give a large and 'significant' gain over a weak baseline. The test is only as meaningful as the target and the at-risk mask fixed beforehand (CLAUDE.md Target).

**Target definition**

> Generic: null H0: E[d_t] = 0 (DM, unconditional equal predictive accuracy), or H0: E[d_{t+1} | F_t] = 0 (GW, conditional: no information known at t predicts which forecast will win). For us: y(t) = 1 if a new alert starts in (t, t+1h], per oblast-hour, forecast at the start of the hour; loss = Brier; d < 0 means the model beats the rolling recent-rate baseline. Since H = 1, the label of row t is known at t+1h, so the GW instruments may use d up to t-1h. For H = 3 (official_h3), d is serially correlated by construction (overlapping label windows), so the HAC lag must be at least H-1 even without clustering.

**Spatial unit**

> Not applicable to the papers; DM is for a single series. For our panel (24 units x hours) the right resampling/variance unit is the TIME CLUSTER (one forecast hour across all 24 units, or one day / one week across all units), because mass attacks create a common component in d across oblasts. The panel DM paper (Qu, Timmermann & Zhu 2024) shows that a strong common component invalidates a cross-sectional CLT over units. Hering & Genton 2011 and Gilleland et al. 2018 treat the spatial-field case.

**At risk masking**

> Not addressed in the papers, but it matters for validity. The DM statistic must be computed on the IDENTICAL row set for both forecasts (same at-risk mask, gap mask, feature-availability mask). Masking on 'under alert at t' is conditioning on information known at t, which is allowed (it is a GW-style conditioning set). Restricting the evaluation set by the OUTCOME (e.g. only hours with onsets, or 'busy days' chosen after the fact) is the forecaster's dilemma (Lerch et al. 2017) and makes the comparison improper. Masking makes the hourly cluster sizes uneven (N_t ranges up to 24), so the statistic should be a ratio of sums, linearised as u_t = (D_t - dbar * N_t) / Nbar, not a plain mean of per-hour means.

### Data

**Data source variant**

> Not applicable to the papers. Our check: official source only (D-007), H = 1, target_levels = any, 13,116 scored rows. Important finding: although the test window is nominally 2026-07-27 -> 2026-09-07 (6 weeks), scored rows only span 2026-07-27 00:00 -> 2026-08-28 22:00 UTC: 791 forecast hours, 33 days, 5 calendar-week blocks (the last one partial, 1,898 rows). The rest is gap_or_missing (3,480 rows) or feature_missing (1,199 rows, features whose lookback crosses the 29 Aug - 2 Sep gap), plus 6,397 under_alert rows. So the effective test length for inference is about 4.7 weeks, not 6.

**Preprocessing**

> Method-level: (1) Form the loss differential per row on the shared eligible set. (2) Aggregate to time clusters: per forecast hour, D_t = sum over units of d_it, N_t = number of scored units. (3) Estimate the long-run variance of the cluster series with a HAC kernel (Newey-West/Bartlett), or resample whole time blocks. (4) For small numbers of blocks, use small-sample corrections (HLN t with T-1 df) or fixed-smoothing (fixed-b) critical values (Coroneo & Iacone 2020). (5) Choose block length by a rule fixed in advance (e.g. 24h for daily attack cycles, plus 72h and 168h as sensitivity), or Politis-White with the 2009 correction (arch.bootstrap.optimal_block_length).

**Known label artefacts**

> Not applicable to the papers. Artefacts that affect inference in our setting: (a) Mass-attack hours produce simultaneous onsets in many oblasts, i.e. cross-sectional dependence in d; iid-over-rows inference treats one mass attack as many independent trials. (b) The recording gap (29 Aug - 2 Sep) and its feature-missing tail cut the last week, leaving 5 uneven week-blocks; a week-block bootstrap on 5 blocks has only 5^5 = 3,125 distinct resamples and a lumpy percentile distribution. (c) The rolling recent-rate baseline and the model share inputs (both depend on recent onsets), so their errors are positively correlated; this is exactly why a PAIRED test on d is needed and why comparing two separate CIs is wrong (DelSole & Tippett 2014; Gilleland et al. 2018). (d) Standing-alert cap (D-020) and at-risk mask shift which rows are scored; any re-masking changes d and must be identical for both forecasts.

### Method

**Model family**

> Inference procedures, not models. (1) DM: t = dbar / sqrt(LRV_hat / T), LRV via HAC (Bartlett/Newey-West), asymptotically N(0,1) under covariance stationarity of d; designed to compare FORECASTS treated as primitives (Diebold 2015), not to test which population model is better. (2) HLN: multiply DM by sqrt((T + 1 - 2h + h(h-1)/T) / T) and use Student t(T-1); reduces over-rejection in small samples and multi-step horizons. (3) GW: Wald test that E[h_t d_{t+1}] = 0 for instruments h_t known at t (constant + e.g. recent activity level, lagged loss differential); valid with rolling/fixed estimation windows and nested or non-nested models, because it targets forecasts produced by a given estimation method, including estimation noise; a later critique (Zhu & Timmermann 2020) argues the GW null cannot hold under rolling windows and that it can be size-distorted for unconditional tests. (4) Block bootstraps: moving-block (Kuensch 1989), circular, stationary (Politis-Romano 1994, random geometric block lengths); resample time blocks of the paired differential (or of paired losses, to get a CI for the BSS ratio). (5) Panel DM (Qu-Timmermann-Zhu 2024): tests pooled over units and time, over subsets of time periods, or clusters of units; handles common factors in loss differentials. (6) Spatial/verification: Hering-Genton fit a parametric autocovariance to d to stabilise the LRV, and were the most robust test under both temporal and between-model correlation in Gilleland et al. 2018; DelSole-Tippett random-walk/sign test counts wins and is distribution-free but loses power and is only partially robust to serial correlation. (7) Multiple comparisons: Hansen SPA (is any competitor better than the benchmark?) and the MCS (set of forecasts containing the best with given confidence), both via stationary bootstrap. (8) Nested models: Clark-West adjustment.

**Features**

> Not applicable (no forecasting features). Method components relevant to us: the loss function (Brier, the PRIMARY metric's building block; DM works for any loss, including log loss with clipping); the HAC lag/bandwidth (L = 0, 6, 24, 72, 168 hours tried in our check); block length (24h, 72h, 168h, stationary mean 24h, calendar day, calendar week); GW instruments known at t (mean recent-rate level across units, model-baseline disagreement p_model - p_recent, rolling 24h mean of past d). Python options without new dependencies: numpy/scipy are enough (our check used only the pinned venv: numpy 2.5.4, pandas 3.0.6, scipy 1.18.1). statsmodels and arch are NOT in the project venv; adding them requires the human's approval (CLAUDE.md).

**External feature timing**

> Not applicable. Timing rule for GW instruments: every instrument must be known at forecast time t. With H = 1 the loss of row t-1h is known at t, so lagged d up to t-1h is legitimate; with H = 3 only d up to t-3h. Using the CURRENT hour's realised national onset count as a conditioning variable would condition on the outcome (forecaster's dilemma), not on information.

**Ablation design**

> DM/bootstrap tests are the right tool for ablations evaluated on the same rows: each feature block vs the base model gives a paired d series. But many ablations or variants compared on the same test set create a multiple-testing / data-snooping problem: use Hansen SPA or MCS (stationary bootstrap) or a Holm correction, and treat any variant chosen AFTER seeing test results as exploratory. Nested ablations (model with extra features vs without) under a fixed-parameter view would need Clark-West; under the GW view (forecasts from a given estimation scheme) plain DM-type tests are acceptable.

### Evaluation

**Split scheme**

> Not applicable to the papers. Implications for us: the frozen model (fixed estimation at 2026-07-27) vs a rolling baseline is exactly the GW setting (forecasts from different estimation schemes, estimation noise included). The weekly-refit row (D-014) is a different forecast and needs its own paired test against recent-rate on the same rows. Coroneo-Iacone show DM is over-sized with few out-of-sample observations unless fixed-smoothing asymptotics are used; with 33 days / 5 weeks we are in that regime for daily and weekly blocks.

**Metrics**

> Test statistics and outputs: DM t statistic and p-value (two-sided, and one-sided 'model better'); HLN-adjusted t; GW Wald chi-square with q degrees of freedom; bootstrap percentile CI for the mean Brier difference and for BSS = 1 - mean(BS_model)/mean(BS_ref) (resampling paired losses keeps the ratio correct); bootstrap P(diff < 0); sign/random-walk test on per-day or per-week wins; SPA p-value and MCS membership for many variants.

**Unit of metric**

> Pooled over all eligible rows, with inference clustered on time (hour, day or week across all units). Per-unit DM tests are possible but have few positives per unit and should be multiplicity-corrected; per-group (Kyiv City / frontline / rear) tests are the sensible subset level (panel DM 'clusters of units').

**Baseline strength**

> Not a baseline paper. Key point for us: the reference in the test should be the strongest baseline, which is the rolling recent-rate (D-021). Testing against a weak baseline (raw persistence, BSS -0.72 vs recent-rate in our test) gives trivially significant results and says nothing about whether the model is useful.

**Calibration**

> Not addressed by DM/GW. A significant Brier gain can come from discrimination or calibration; combine the test with the CORP decomposition (see scoring_rules_corp) so the README can say why the model wins or loses. A DM test can also be applied to the calibration-in-the-large gap if needed, using the same block scheme.

**Calibration under drift**

> GW is the natural tool for drift questions: an instrument such as 'weeks since cut-off' or 'recent activity level' tests whether relative performance changes over the test window. In our check the per-week Brier difference (model minus recent-rate) was +0.0018, +0.0034, +0.0026, -0.0004, -0.0049 for the weeks starting 27 Jul, 3 Aug, 10 Aug, 17 Aug, 24 Aug: the frozen model lost in the first three weeks and won in the last two. By recent-rate level tercile (hour-level means): low -0.0018, mid -0.0007, high +0.0041, i.e. the model loses mainly in high-activity hours. These are descriptive; see headline_results for the formal tests.

**Uncertainty of gain**

> Main subject of this entry. Recommended for us: a paired, time-clustered test of the Brier difference vs rolling recent-rate, with (i) a circular or stationary block bootstrap over forecast hours with all 24 units kept together, block length fixed in advance (24h primary; 72h and 168h sensitivity), (ii) a calendar-day block bootstrap, (iii) a week-block bootstrap only as a sensitivity row because we have 5 week-blocks, and (iv) a DM t statistic on the hourly cluster series with Newey-West lag 24 and HLN-style t(T-1) critical values. Our illustrative numbers show the iid-row standard error (0.000589) understates the time-clustered HAC standard error (0.000897 at lag 24, 0.00105 at lag 72) by a factor of about 1.5-1.8; even hour-clustering alone (lag 0, 0.000677) widens it by about 1.15x.

**Regime coverage**

> Not applicable to the papers. For us: the test window (33 scored days, late Jul - Aug 2026) contains no major regime shift; the Sep-2026 yellow/red reform is outside it and its API data must not be mixed into the same test (CLAUDE.md). A DM/bootstrap CI on the new-regime check (D-015 (b)) is possible but must be computed separately and labelled exploratory. The GW framework is the principled way to ask 'is the gain stable across regimes', using an instrument that marks regime or activity level.

### Leakage & Hygiene

**Leakage handling**

> Not a pipeline. Inference-specific leakage and snooping risks: (1) Choosing the block length, HAC lag, or test variant after seeing which gives the smallest p-value; fix them in the plan / preregistration before scoring. (2) Selecting the best of several post-hoc variants on the test (reports/improve/variants_test_posthoc.csv: V2 offset +0.017, V4 weekly refit + offset +0.020 BSS) and then reporting a DM p-value for the winner: the p-value ignores the selection and is invalid; use SPA/MCS across all variants tried, or treat as exploratory. (3) GW instruments that use the current hour's outcome or labels not yet matured at t. (4) Bootstrap that resamples rows independently across units within an hour, which breaks the cross-sectional dependence and gives falsely narrow intervals. (5) Treating the test-set y_bar or a test-fitted recalibration as a reference forecast.

**Test window hygiene**

> Not applicable to the papers. For us: the final test was first accessed 2026-10-13 00:16 UTC (reports/final_test_access.json) with preregistration hashes. The illustrative check in this entry only re-analyses the already-scored frozen predictions (no model selection, no refit), so it does not change the frozen headline. If the project adopts a bootstrap CI (D-013 item 6), the scheme, block lengths, B and seed should be written into the plan and the README should say it was specified after the first scoring, as an inference-only addition.

### Relevance

**Takeaways for project**

> 1) Answer to 'is the gain over recent-rate real?': on the official frozen test it is not a gain at all. BSS = -0.010, and every dependence-aware scheme gives a 95% CI of roughly [-0.03, +0.01] that contains zero. The honest README statement is 'the frozen model is statistically indistinguishable from the rolling recent-rate baseline on the official test (BSS -0.010, 95% block-bootstrap CI about -0.031 to +0.010, 24h blocks)'. That supports the D-021 wording that not beating recent-rate is a valid result.
> 2) Implement D-013 item 6 as a paired, time-clustered bootstrap: resample whole time blocks with all 24 units kept together; resample PAIRED losses (lm, lr) per block, and compute diff = sum(lm - lr)/sum(N) and BSS = 1 - sum(lm)/sum(lr) per replicate. Never compare two separate CIs (one per forecaster): the errors are positively correlated because both use recent onsets.
> 3) Change the planned block from 'week' to 'day' (or 24h circular/stationary) as primary, with week blocks as sensitivity. Reason: the scored test is only 33 days (27 Jul -> 28 Aug 22:00 UTC) because the gap and feature-lookback mask remove 29 Aug -> 7 Sep, leaving 5 uneven week-blocks; a 5-block percentile bootstrap is lumpy. This needs the human's approval since D-013 says 'week-block'. Also correct any README text that calls the scored test '6 weeks'.
> 4) Report a DM t statistic on the hourly cluster series with Newey-West lag 24 (and 72 as sensitivity) and t(T-1) critical values, next to the bootstrap CI. Fix lag, block lengths, B and seed in the plan before running (preregistration spirit). The iid-row SE is about 1.5-1.8x too small, so never report a row-level paired t-test.
> 5) The rate ratio form matters: masking gives uneven units per hour, so linearise the ratio (u_t = (D_t - dbar N_t)/Nbar) for DM and resample (lm, lr, N) sums for the bootstrap, so the bootstrap target equals the reported pooled BSS (ratio of mean Briers, consistent with metric_table()).
> 6) Post-hoc variants (reports/improve: V2 +0.017, V4 +0.020) cannot be tested with DM on the same test: they were chosen after seeing test results. Either run Hansen SPA / MCS over all variants tried (needs arch or a hand-rolled stationary bootstrap) or label them exploratory and wait for fresh data (monthly re-evaluation, M6) for a confirmatory test. A +0.02 BSS gain is about the size of the CI half-width, so even a clean test would be borderline.
> 7) Use a GW-style conditional test (or simply a preregistered split) to ask 'when does the model beat recent-rate?' with instruments known at t (recent activity level, weeks since cut-off). Our exploratory result (model worse in high-activity hours, better in quiet hours; worse in weeks 1-3, better in weeks 4-5) is a hypothesis that motivates D-014 refit or a blend, not a finding.
> 8) For the new-regime check (D-015 (b)), compute a separate paired block-bootstrap CI on API data, labelled exploratory, never pooled with the official test (CLAUDE.md). Per-group CIs (Kyiv City, frontline, rear) use the same time blocks; Kyiv City alone has 709 rows and 87 positives, so expect very wide intervals and say so.
> 9) Do not add statsmodels or arch without approval; numpy/scipy suffice. Put the inference code in src/evaluate.py with a unit test (e.g. a synthetic panel with a common shock where the iid SE is known to be too narrow, plus a test that the bootstrap BSS equals the point BSS at B = 1 with identity resampling).

**Best practices**

> ADOPT: (a) Paired tests on the loss differential, on identical rows, against the strongest baseline (rolling recent-rate). (b) Cluster on time: aggregate to forecast hours across all units, then HAC or block-resample over time; the panel-DM result is that common shocks across units break cross-sectional averaging. (c) Block length chosen by a rule fixed in advance (24h primary, 72h/168h sensitivity; or Politis-White with the 2009 correction), and stated in the README. (d) Small-sample care: HLN t(T-1) or fixed-b critical values when there are few independent blocks. (e) Report the CI of the BSS from resampled paired sums, plus P(diff < 0), plus a simple sign/random-walk count of winning days or weeks as an intuitive check. (f) Multiple-comparison control (SPA, MCS, Holm) whenever more than one variant is compared on the same test. (g) Conditional (GW) analysis only with instruments known at t, labelled exploratory unless preregistered. (h) Say clearly that DM compares forecasts, not models (Diebold 2015). AVOID: (1) iid row-level t-tests or iid row bootstraps on clustered spatio-temporal events. (2) Comparing two marginal CIs instead of the paired difference. (3) Week-block bootstraps with only 5 blocks presented as precise. (4) Choosing block length, lag or test after seeing results. (5) Reporting a p-value for a variant selected on the same test. (6) Restricting evaluation to outcome-selected subsets (forecaster's dilemma). (7) Pooling official and API rows in one test. (8) Treating 'not significant' as 'equal': report the CI so readers see the plausible range of gain or loss.

### Other Info

**Uncertain fields (omitted above)**

- code_available
- data_sources
- headline_results
- popularity
- year

---

<a id="drift_recalibration"></a>
## 24. Distribution shift and online recalibration (Gupta & Ramdas 2023 Online Platt + Calibeating)

*Category: evaluation* — Post-reform recalibration story; analog to rolling recent-rate shrinkage.

### Basic Info

**Name**

> Distribution shift and online recalibration. Core: Gupta & Ramdas (2023), 'Online Platt Scaling with Calibeating' (ICML 2023, PMLR 202:12182-12204; arXiv:2305.00070). Theory companion: Foster & Hart (2023), '"Calibeating": Beating Forecasters at Their Own Game' (Theoretical Economics 18(4):1441-1474; arXiv:2209.04892). Antecedent: Kuleshov & Ermon (2017), online recalibration by binning + hedging of a black-box forecaster.

**Type**

> method family (post-hoc online recalibration under distribution drift: Online Platt Scaling (OPS) via online logistic regression, plus calibeating wrappers TOPS (tracking) and HOPS (hedging); beta-scaling extension OBS/TOBS/HOBS)

**Url**

> Paper: https://arxiv.org/abs/2305.00070 ; PMLR: https://proceedings.mlr.press/v202/gupta23c.html ; HTML: https://ar5iv.labs.arxiv.org/html/2305.00070 ; Code: https://github.com/aigen/df-posthoc-calibration (folder 'Online Platt Scaling with Calibeating') ; Foster & Hart: https://doi.org/10.3982/TE5330 and https://arxiv.org/abs/2209.04892

**Year**

> 2023 (arXiv v1 28 Apr 2023, v3 16 Aug 2023; ICML 2023). Foster & Hart: arXiv Sep 2022, Theoretical Economics Nov 2023. Code repo last pushed 2023-10-20.

**Authors**

> Chirag Gupta, Aaditya Ramdas (Carnegie Mellon University). Foster & Hart: Dean P. Foster, Sergiu Hart. Code maintained by Chirag Gupta (GitHub 'aigen').

**Popularity**

> Semantic Scholar (retrieved 2026-10-17): Gupta & Ramdas 2023 = 12 citations (1 influential); Foster & Hart 'Calibeating' = 23 citations. GitHub aigen/df-posthoc-calibration = 41 stars, MIT license. A niche but well-founded line of work; not a mainstream forecasting tool.

**Peer review status**

peer-reviewed (ICML 2023 conference paper; Theoretical Economics journal paper). Both also on arXiv.

### Problem Framing

**Target type**

> Not an air-alert application. Generic binary classification / probability forecast y in {0,1} with a black-box score f(x) in [0,1]. Recalibration does not change the target, so the onset-vs-state choice and our at-risk mask (CLAUDE.md Target) are fixed upstream. Note: a recalibrator fitted on a state target would happily learn the high base rate of 'already under alert' rows, so the mask must be applied BEFORE any online update, not only at scoring.

**Target definition**

> Generic: Y_t = 1 if the event occurs at stream step t; forecast p_t issued before Y_t is revealed, then Y_t is observed and the recalibrator updates (one point per step, labels revealed immediately). For our project the event is 'a new alert starts in (t, t+H]', H = 1 h, per oblast-hour, and labels mature only at t+H (D-021 label-maturity rule), which the paper's protocol does not model.

**Spatial unit**

> Not applicable (tabular UCI/Kaggle datasets and synthetic streams). For us the natural choices are a single pooled recalibrator across the 24 units, one per group (Kyiv City / frontline / rear), or a per-unit intercept; per-unit 2-parameter OPS would be noisy for quiet rear oblasts.

**At risk masking**

> Not addressed (no at-risk concept). Applied to our task, masked rows (already under alert at t, gap hours D-013) must be excluded from BOTH the prediction set and the online update stream, exactly as for the rolling recent-rate baseline (unmasked rows s in [t-14d, t-H]).

### Data

**Data source variant**

> Not applicable (no air-alert data). Drift on real data is INDUCED by sorting on one covariate with small noise, i.e. a constructed covariate shift, not a naturally occurring regime change such as the 2026-09-07 yellow/red reform.

**Preprocessing**

> Base-model scores clipped to f(x) in [0.01, 0.99] for the regret theorem (Thm 2.1); the logit of the score is the single pseudo-feature for online logistic regression. Real-data streams are created by sorting rows on a chosen covariate after adding noise from {-1, 0, 1}; the i.i.d. control is a random shuffle. 100 repetitions per real-data experiment.

**Known label artefacts**

> Not applicable to air alerts (no duplicates, gaps, standing alerts or 30-min artefacts). Method-level artefacts worth noting: (1) Fixed-width epsilon-bins (epsilon = 0.1, m = 10) are used for both the calibeating wrappers and the CE metric. At our hourly onset base rates in the official regime (a few percent), nearly all forecasts fall in [0, 0.1), so TOPS would degenerate to one running mean for almost all rows; this is the same instability CORP documents for reliability diagrams. (2) Covariate-free hedging (Appendix D) can look perfectly calibrated while being uninformative (converges to climatology). (3) The CE metric itself is a binned estimate and inherits bin-choice sensitivity (paper shows epsilon = 0.05 / 0.2 give qualitatively the same ranking).

### Method

**Model family**

> Post-hoc recalibration layered on a frozen base model. (1) OPS: the Platt map m_{a,b}(f) = sigmoid(a * logit(f) + b) with (a_t, b_t) learned by ONLINE logistic regression on the stream (d = 2). Implementation uses Online Newton Step (ONS) with gamma = 0.1, rho = 100 (A_0 = rho I), projection onto K = {||(a,b)||_2 <= 100}, initialisation (a_1, b_1) = (1, 0), i.e. the identity map = the uncalibrated base model. Hyperparameters were fixed once, not tuned per dataset. Alternatives compared in Table 1: OGD, ONS, AIOLI, Aggregating Algorithm; FTL is O(T^2) so a windowed refit (WPS, refit every ~100 steps on the last W points) is used as a comparator. Regret vs best Platt model in an l2-ball of radius B: ONS R_T <= 2(e^B + 10B) log T + 1; AIOLI R_T <= 22 B log(BT). (2) Calibeating (after Foster & Hart 2023): TOPS = for each epsilon-bin of the OPS forecast, output the running mean of past outcomes whose OPS forecast fell in that bin (bin midpoint if empty); HOPS = a separate Foster (1999) randomized hedging forecaster inside each bin. (3) Beta scaling: sigmoid(a log f + b log(1-f) + c) (b = -a recovers Platt), learned online by ONS in R^3 (rho = 25, init (1,1,0)), with tracking/hedging variants TOBS/HOBS. Baselines: base model (BM), fixed Platt scaling fitted once on T_cal (FPS), windowed Platt scaling (WPS), windowed histogram binning (WHB, Appendix A.3).

**Features**

> One pseudo-feature: logit(f(x_t)) from a frozen base model, plus intercept (Platt); log f and log(1-f) plus intercept (beta scaling). Base models: random forest (sklearn, n_estimators = 1000) on real data; logistic regression on synthetic data (48-dim sinusoidal featurisation for covariate drift). For us the analogue is the frozen LightGBM output (src/model.py) as f, and the recalibrator never sees the raw features, so it cannot add feature leakage; its only new information is past matured labels.

**External feature timing**

> Not applicable (no external covariates). Timing issue that DOES matter for us: the paper assumes the label of step t is revealed before step t+1. With 24 units per forecast hour and H-hour label windows, a causal implementation must (a) predict all 24 unit-rows at t with parameters frozen before t, then (b) update only with rows whose label window (s, s+H] ended by t, i.e. s <= t - H. Updating within an hour across units in arbitrary order would leak same-hour onsets (mass attacks hit many oblasts in the same hour).

**Ablation design**

> Methods are compared on identical streams (same base model, same T_train / T_cal split, same 100 repetitions), with an i.i.d. (shuffled) control vs drifting (sorted) version of the same data. This is a clean same-sample design. Sensitivity analysis on the only calibeating hyperparameter (epsilon in {0.05, 0.1, 0.2}, Appendix A.3).

### Evaluation

**Split scheme**

> Chronological stream: first T_train points train the base model (frozen thereafter, no refit on the stream); next T_cal points fit FPS and warm up the windowed methods; the remaining points form the online test stream, where each method predicts then updates. Online methods update every step; WPS/WBS refit on a sliding window of W points. No purge needed because labels are instantaneous.

**Metrics**

> Sharpness SHP (eq. 14, the observed refinement-type quantity: higher is better) and l1 calibration error CE over epsilon-bins (eq. 17). Synthetic experiments use the TRUE conditional probabilities for CE and accuracy over time windows (e.g. t = 5501-6000). Brier score enters the theory via the Foster-Hart decomposition Brier = calibration + refinement; TOPS/HOPS keep refinement (sharpness) within O(epsilon) of OPS while improving calibration. No ROC-AUC or PR-AUC (recalibration by a monotone map leaves AUC unchanged; calibeating's binning can only coarsen ranking).

**Unit of metric**

> Pooled over the stream (or over time windows of the stream); means over 100 repetitions. No per-group breakdown.

**Baseline strength**

> Baselines: uncalibrated base model (BM), fixed Platt scaling (FPS), windowed Platt scaling (WPS), windowed histogram binning (WHB), and windowed beta scaling (WBS). Under drift, BM and FPS are the worst non-calibeating methods; OPS has the lowest CE among non-calibeating methods; TOPS is best overall 'by a margin' with sharpness losses of about 0.005 or less. On i.i.d. data the gaps shrink; WHB beats OPS/OBS on i.i.d. data and is mixed under drift. WPS is described as much worse than OPS/TOPS on synthetic drift. No comparison with a simple rolling-base-rate forecaster, which is our strongest bar (rolling recent-rate, D-021).

**Calibration**

> The paper IS a calibration method. Calibration is fitted ONLINE on the evaluation stream itself, but causally (predict-then-update), so it is legitimate out-of-sample. Fixed Platt (FPS) is fitted once on a held-out calibration slice, the analogue of our M4 rule (Platt on validation if validation ECE > 0.02; our official run gave ECE = 0.0123, decision 'none', reports/official/calibrator.json). Calibration quality is reported as binned CE; no reliability diagrams in the CORP sense. Guarantees: OPS has only a REGRET guarantee relative to the best fixed Platt map (no absolute calibration bound); TOPS has a sharpness guarantee SHP(TOPS) >= SHP(OPS) - epsilon - epsilon^2/4 - (log T + 1)/(epsilon T) but no calibration guarantee; HOPS (randomized) has E[CE] <= epsilon/2 + 2 sqrt(1/(epsilon^2 T)) even for adversarial outcome sequences.

**Calibration under drift**

> Central topic. Drift types studied: covariate drift, label (base-rate) drift, regression-function drift. Under label drift (Fig. 10, t = 5500-6000) accuracy/CE go from base 59.38% / 0.42 to OPS 92.82% / 0.049; covariate drift (Fig. 3, t = 5501-6000) 23.60% / 0.64 -> 87.76% / 0.13; regression-function drift (Fig. 11) 44.39% / 0.34 -> 51.43% / 0.049. A pure base-rate shift is exactly what the Platt intercept b_t absorbs, so OPS behaves like an online calibration-in-the-large correction plus an online slope correction. Our own new-regime transfer table (reports/new_regime/transfer.csv, API 2026-09-13 -> 2026-10-12, any-level target, 7,146 at-risk rows, low_n flagged) shows exactly this pattern: the frozen model UNDER-predicts (mean predicted 0.222 vs observed 0.264, -4.2 pp overall; Kyiv City -12.3 pp, frontline -6.7 pp, rear -3.4 pp), keeps within-unit AUC 0.666 vs 0.485 for recent-rate, yet loses on Brier (BSS vs recent-rate = -0.032). That is a 'discrimination preserved, scale wrong' signature that an online intercept/slope recalibration targets. [Interpretation, not tested: OPS on the frozen model would likely close most of that Brier gap.]

**Regime coverage**

> Synthetic smooth drifts and induced covariate shift by sorting; no real-world abrupt regime change. Nothing comparable to the Jan-2025 drone surge, the 2025 raion/hromada reform or the Sep-2026 yellow/red reform. The method's online adaptivity is relative to the best FIXED Platt map over the whole stream (static regret); the authors list adaptive/strongly-adaptive regret on recent data (Hazan & Seshadhri 2009; Zhang et al. 2018) as future work, which is what an abrupt reform would need.

### Leakage & Hygiene

**Leakage handling**

> Causal by construction: each forecast uses only (a_t, b_t) learned from steps before t, and the base model is frozen after T_train, so no future label enters a prediction. Nothing to purge because labels are instantaneous. What the paper does NOT cover and we must add: (1) label maturity with H-hour windows (update only with rows s <= t - H, the D-021 rule already used by recent-rate); (2) simultaneous rows (24 units at the same t: batch predict, then batch update); (3) masked rows (at-risk, gap hours) excluded from updates; (4) the recalibrator state at the frozen cut-off (2026-07-27) must be initialised from validation or identity, never warmed up on test labels before the first test forecast; (5) a truncation test for the recalibrated predictor (CLAUDE.md test_leakage.py): truncating the stream after t must not change p_t. Calibeating tracking means are also causal (past outcomes only).

**Test window hygiene**

> Hyperparameters (ONS gamma = 0.1, rho = 100, K radius 100, init (1,0); epsilon = 0.1) were set once and reported as untuned across all datasets, which is the right posture for a pre-registered extra row. Results are fully reproducible from notebooks (fixed randomisation). No notion of a single-look final test; the stream is evaluated in full each time.

### Results

**Headline results**

> (1) OPS, online logistic regression on logit(f) with ONS, adapts to covariate, label and regression-function drift and has logarithmic regret vs the best Platt map: ONS R_T <= 2(e^B + 10B) log T + 1. (2) Under synthetic drift, OPS sharply improves on the frozen base model (label drift: CE 0.42 -> 0.049, accuracy 59.38% -> 92.82%; covariate drift: CE 0.64 -> 0.13). (3) On four real datasets with induced drift, OPS has the lowest CE among non-calibeating methods, fixed Platt (FPS) and the base model are worst, and TOPS (OPS + tracking calibeating) is best in every scenario, losing at most ~0.005 sharpness. On shuffled (i.i.d.) data the gaps shrink and TOPS still wins. (4) HOPS gives an adversarial calibration guarantee E[CE] <= epsilon/2 + 2 sqrt(1/(epsilon^2 T)) at a small sharpness cost. (5) Online beta scaling (OBS) beats OPS and WBS; TOBS is best in each plot. (6) Foster & Hart: any forecaster can be 'calibeaten' (made calibrated while keeping its refinement score), deterministically for the tracking version. No result is reported against a rolling base-rate forecaster, so 'beats naive baselines' is only shown vs the frozen base model and fixed/windowed Platt.

### Reproducibility

**Code available**

> Yes. https://github.com/aigen/df-posthoc-calibration (MIT, 41 stars, last push 2023-10-20, not actively maintained). Folder 'Online Platt Scaling with Calibeating' holds sec_1_*_drift_1d.ipynb (synthetic drift), sec_4_experiments_core.py/_run.ipynb (real data), beta_scaling_experiments.py, eps_core.py (epsilon sensitivity), app_a3_hb_experiments_* (histogram binning) and calibration.py/utils.py. The authors state all figures reproduce exactly. For this project no new dependency is needed: ONS for d = 2 is ~20 lines of NumPy (2x2 matrix update + projection), and TOPS is a running per-bin mean. Adding the repo as a dependency would need Oleksandr's approval (CLAUDE.md).

### Relevance

**Takeaways for project**

> 1) Our rolling recent-rate baseline (D-021: (k + 10 p_unit)/(n + 10) over unmasked rows in [t-14d, t-H]) is already an online, intercept-only recalibration of a constant forecaster. OPS is the principled generalisation: an online intercept AND slope applied to the frozen model's logit. This gives the README a clean story for why recent-rate is hard to beat after drift: it adapts its level every hour, while the frozen model (and fixed Platt, FPS) cannot. The paper confirms empirically that frozen and fixed-Platt forecasters are the worst under drift.
> 2) The new-regime transfer result (reports/new_regime/transfer.csv) fits the 'discrimination preserved, scale wrong' case OPS is designed for: frozen model mean predicted 0.222 vs observed 0.264 (-4.2 pp; Kyiv City -12.3 pp), within-unit AUC 0.666 vs 0.485 for recent-rate, BSS vs recent-rate -0.032. The D-015(d) conclusion can then say, as a hypothesis, 'recalibration (not necessarily retraining) is the first remedy', and cite OPS as the method. State the measured numbers as facts and the OPS remedy as an untested hypothesis (D-015 amended).
> 3) RULE CONFLICT, needs Oleksandr: running OPS on API data is fitting 2 parameters on API labels, which CLAUDE.md forbids ('No training or tuning on API data'), even though it is as causal as the rolling recent-rate baseline that is allowed. Likewise, on the official test window it would be a second exception to 'baselines/model frozen', like D-021's recent-rate exception and the D-014 weekly-refit EXTRA row. If approved, report it ONLY as an extra row ('frozen model + online Platt'), never the headline.
> 4) If approved, pre-register the implementation exactly as in the paper to avoid test-time tuning: ONS with gamma = 0.1, rho = 100, ||(a,b)|| <= 100, init (a,b) = (1,0) (identity = the frozen model on day one), logit computed on clipped p (we already clip at 1e-6 in src/model.py; the paper's theorem assumes [0.01, 0.99]). One POOLED (a,b) across units, optionally plus a per-group intercept; per-unit slopes would be noise for quiet rear oblasts. Fix all of this in the plan before scoring (D-026 consensus, then human ratification).
> 5) Causality details the paper does not handle and we must: batch-predict all 24 units at t with parameters frozen before t; update only with matured rows s <= t - H (D-021); skip masked rows (at-risk at t, gap hours 2026-08-29 -> 09-02, D-013); never update within the same hour across units (mass attacks would leak). Add a truncation test to tests/test_leakage.py: p_t from the online recalibrator must be identical when the stream is cut after t.
> 6) Do NOT use calibeating with the paper's 10 fixed-width bins on the official regime: onset base rates of a few percent put almost all rows in [0, 0.1), so TOPS collapses to a single running mean, i.e. a worse recent-rate. If tracking is tried, use pre-registered log-spaced or quantile bins from validation, and note TOPS uses all-history bin means that adapt slowly to an abrupt reform. In the new regime (base rate ~0.26 at-risk) fixed bins are less degenerate.
> 7) Do NOT use HOPS (randomised hedging) for a public-facing forecast: its guarantee is in expectation over the forecaster's own coin flips, and a randomly jittered alert probability is hard to explain to users. The paper's Appendix D also shows covariate-free hedging converges to climatology, calibrated but useless; calibration alone is not the goal (Foster & Hart: judge by Brier, i.e. calibration + refinement).
> 8) Monotone recalibration leaves ROC-AUC unchanged, so the D-015(c) within-oblast AUC is a fair check of whether discrimination transferred, independent of any recalibration; any Brier gain from OPS is pure calibration (MCB in CORP terms). Report OPS gains as an MCB reduction against the frozen model.
> 9) For M6 (future work, D-016): an online recalibrator updated monthly (or hourly) from the datastore is a cheaper first response to drift than a full retrain, and fits the 'pytest before retrain' gate. The paper's static-regret guarantee is weak for abrupt reforms; a sliding-window or discounted variant (adaptive regret, cited as future work in the paper) would be the honest choice, and must be pre-registered.

**Best practices**

> ADOPT: (a) Treat recalibration as a separate, causal layer on a frozen model, with its own leakage test, rather than retraining after every shift. (b) Initialise the online recalibrator at the identity map so that day-one predictions equal the frozen model, and fix all hyperparameters before scoring (the paper uses one untuned setting for every dataset). (c) Compare against the frozen model, fixed Platt AND a windowed/rolling competitor on the identical stream, with an i.i.d.-shuffled control to separate drift effects from generic miscalibration. (d) Judge by a proper score (Brier = calibration + refinement, Foster & Hart), not by calibration error alone. (e) Report calibration-in-the-large (mean predicted - observed) per group before and after recalibration; a base-rate shift shows up as a level offset that an online intercept absorbs. (f) Respect label delay (s <= t - H) and simultaneous units (batch updates). AVOID: (1) Fixed Platt fitted once and assumed valid after a regime change. (2) Fixed-width 0.1 bins (for calibeating or CE) at low base rates. (3) Randomised hedging forecasts in a user-facing product. (4) Treating a calibrated-but-flat forecaster (climatology-like) as success. (5) Warm-starting the recalibrator on test labels before the first scored forecast, or tuning gamma/rho/epsilon on the test or API window. (6) Calling an online-recalibrated row 'the frozen model': it is a different predictor and must be labelled as an extra row. (7) Assuming static-regret guarantees cover abrupt reforms; they compete only with the best single Platt map over the whole stream.

### Other Info

**Uncertain fields (omitted above)**

- data_sources
- uncertainty_of_gain
