# Proposed DECISIONS.md entries (written while the human was asleep; the human edits and commits them)

Numbers are copied from `reports/` (final test scored once, 2026-10-13).

## D-028 — M4: models, the single final-test scoring, new-regime section (Claude–Codex consensus → human to ratify)
- One pooled LightGBM model per horizon (human: "option 1"), fixed settings (lr 0.05, 31 leaves, min_data_in_leaf 100,
  seed 20261013, deterministic, early stopping 100 rounds on pooled validation logloss, no refit). Best iterations
  208 (H = 1) and 203 (H = 3). Pre-registered calibration rule: Platt on validation iff validation ECE > 0.02 →
  H = 1 none (ECE 0.0123), H = 3 Platt (ECE 0.0304, slope 1.30). PROVISIONAL: params, ECE threshold, low-n flag (< 100 rows).
- Single scoring: both horizons' model, calibrator, baseline tables, validation predictions, data file and code
  fingerprint hashed into `preregistration.json`; one joint marker `reports/final_test_access.json` written before
  any test label was read; refitting and re-registration after access are refused (tested). An exact reproduction
  run gave identical metrics.
- **Final test, H = 1 (headline): Brier skill vs the rolling recent rate −0.0101 overall — the model does NOT beat the
  recent rate overall.** By group: Kyiv City +0.0738, rear +0.0161, frontline −0.0753 (low-n). Within-unit ROC-AUC
  0.632 (model) vs 0.491 (recent rate): the model ranks hours inside an oblast clearly better; pooled AUC is similar.
- Final test, H = 3 (extra row): −0.0031 overall; Kyiv City +0.0904, rear +0.0027, frontline −0.0757.
- New regime (exploratory, H = 1, alerts.in.ua 2026-09-20 18:00 → 10-12 15:00 scored): the frozen model
  under-predicts (mean 0.2216 vs observed 0.2638) but keeps within-unit AUC 0.666 → recalibration/retraining needed
  before use after the reform. Measured: onsets per 30 days rose in Kyiv City and the rear; explanations are hypotheses.
- Implementation corrections found by reality/reviews: API `history_start` = max(fetched_at − 30 d) =
  2026-09-12 17:00:43 (`month_ago` is bounded by finish time; Codex round 5 agreed); API gap detection bounded to coverage;
  new-regime stage bound to the marker's frozen pre-registration; dedup by parsed time.
- **ESCALATED, open for the human:** API alert types. The official feed has no type column and appears to include
  artillery-shelling alerts (Nikopol evidence). Codex judged counting them a target change reserved for the human
  (`reviews/M4-codex-artillery.md`). Both variants are reported: `new_regime` (air-raid only) and
  `new_regime_all_types`; group-level results barely differ.
- Limitation: pre-registration and marker are local, uncommitted files (the human asked not to commit) — they are only
  tamper-evident after a commit.

## D-029 — M5: README, results site, Streamlit (Claude–Codex consensus → human to ratify)
- Every README result number lives in GENERATED blocks written by `scripts/build_site.py` from exact source keys; tests
  verify cells independently, run swap mutations, and reject result numbers in hand-written prose. README figures are only
  PNGs written by `run_all.py`.
- Static, self-contained site `site/index.html` (inline SVG + vanilla JS, data embedded, system fonts, no network requests) + `netlify.toml`;
  required local Streamlit app `app/streamlit_app.py` (reads only `reports/`).
- M5 code lives outside the pre-registered code fingerprint (`src/*.py`, `scripts/run_all.py` unchanged after the test).
- Hosting: the Netlify CLI on this machine is not logged in and the builder may not enter credentials → deployment is
  OUTSTANDING: `npx netlify-cli deploy --dir site --prod` (or link the repo in the Netlify UI). A private claude.ai
  preview exists.

## D-030 — M7: post-hoc improvement rows (human-approved exceptions; Claude–Codex consensus → human to ratify)
- Exceptions approved by the human in chat (2026-10-13): (1) labelled post-hoc rows may be scored on the already-seen
  final test, next to — never replacing — the frozen headline; (2) M7 inputs that read earlier test LABELS (s ≤ t − H only):
  unit/national recent rates (block A), the recent-rate offset, the weekly refit (D-014).
- Code isolation: `improve/` + `scripts/run_improve.py`; `src/*.py` and `scripts/run_all.py` unchanged (code fingerprint
  still equals both pre-registrations; tested).
- Feature blocks judged on 4 backtest folds INSIDE train (≥ 0.5 % relative mean-Brier gain AND ≥ 3/4 folds): A drift
  rates −0.43 % (3/4) rejected, B attack waves +0.13 % rejected, C daily rhythm −0.16 % rejected → no block accepted.
- Post-hoc test (13,116 identical rows, same as the headline; Brier skill vs the unchanged D-025 recent rate):
  V0 frozen −0.0101; V1 weekly refit −0.0035; V2 offset +0.0172; V4 weekly refit + offset +0.0203 (best on test, NOT chosen);
  V5 blend w = 0.6, CHOSEN on validation, +0.0146. The offset variants rank hours worse within an oblast (within-unit AUC
  0.632 → 0.590 / 0.576; frontline 0.604 → 0.520): their gain is recalibration toward the recent alert level.
- A clean evaluation of any M7 variant needs new data (M6a collection → a later post-reform test).

## D-031 — M5b: public results page with a per-oblast breakdown (human decision)
- Audience: general public. Tile map + hour-by-hour timeline added; technical sections collapsed.
- Exception (human, chat): per-oblast numbers from the already-scored final test may be shown — the same frozen predictions,
  re-exported by `scripts/export_predictions.py`, which refuses to write unless it reproduces `metrics.csv` exactly.
- Wording rule-based (sign of the saved skill), every comparison with its scored-hour count and real low-n reason.

## Wording corrections proposed (from the M5b review)
- D-014 "purge the last H hours" → "a training row is kept iff t + H ≤ cut-off" (as implemented, D-022).
- D-016 "closed alerts only" → superseded by D-027 (open alerts kept with the causal 24 h cap).
