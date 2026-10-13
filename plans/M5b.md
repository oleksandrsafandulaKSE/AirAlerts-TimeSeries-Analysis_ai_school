# M5b plan v1 — Results page for the general public: plain summary, tile map, forecast timeline

Status: AGREED (consensus round 3, D-026). See reviews/M5b-consensus.md. Human decisions in chat (2026-10-13): audience = GENERAL
PUBLIC; add a tile map of the 24 units and a forecast timeline; no M7 section and no language toggle on the site.
Rules: CLAUDE.md, D-011, D-021, D-024, D-025, M5 plan (every number from reports/, no hand-typed result numbers,
no network requests, code fingerprint untouched).

## 1. Goal
Re-layer `site/index.html` for non-specialists: a plain-language answer first, then a map and a timeline that make the
forecast tangible; all existing technical sections stay, collapsed under "For the technically curious". The README keeps
its technical structure (unchanged rules); only the site changes.

## 2. New data: frozen-model test predictions (no re-scoring)
- `scripts/export_predictions.py` (outside the code fingerprint) rebuilds the H = 1 frames with `run_all.build_frames`,
  loads the FROZEN predictor (`model.txt` + `calibrator.json`, sha256 checked against `preregistration.json` and the joint
  marker) and the frozen baseline tables, and computes predictions exactly as `score_final_test` does.
- Guard: before writing, the exported predictions must reproduce `reports/official/metrics.csv` exactly (overall and per
  group: rows, Brier of the model and of recent rate, equal to the saved values bit for bit); otherwise it raises. This is
  the same single scoring, broken down — no model, rule or threshold changes; no new model is selected.
- Outputs: `reports/official/test_predictions.csv` (unit, t, mask, gap_mask, y, eligible, p_model, p_recent_rate; all test
  hours, so masked hours can be shaded) and `reports/official/metrics_by_unit.csv` (per unit: eligible rows, base rate,
  model Brier, recent-rate Brier, Brier skill vs recent rate, within-unit ROC-AUC with NaN reason if < 10 pos or < 10 neg,
  low-n flag if rows < 100 or AUC undefined).
- Per-unit numbers are a breakdown of the already-scored test; they are labelled "per oblast, noisy" and low-n units are
  marked, never ranked as winners/losers.
- **Human-authorised exception (chat, 2026-10-13):** "Yes, full breakdown" — the page may show per-oblast numbers from
  the already-scored final test (same frozen predictions, reproduced exactly; no new model; nothing re-selected). This
  amends M5's "no new metric on the test" for this breakdown only (proposed D-031).
- Export columns, per test hour and unit: unit, t, status ∈ {scored, under_alert, gap_or_missing, feature_missing,
  purged} (the exclusive D-024 reason), y (null unless scored), p_model and p_recent_rate (null unless scored), and the
  D-023 merged ONSET timestamps of the test window in a separate `test_onsets.csv` (unit, onset_time) — so the timeline
  plots real alert starts, not label windows.

## 3. Page structure (public first)
1. **Plain answer:** "Can we predict new air-raid alerts an hour ahead?" — one generated sentence each for: overall vs the
   simple two-week rule, where it is better, where it is worse, and what "probability" means here. All numbers inserted
   from data. Wording by sign: skill > 0 "more accurate than", skill < 0 "less accurate than", skill = 0 exactly "as
   accurate as", undefined "cannot be compared". Every group comparison carries its scored-hours count, and a low-n group
   carries its ACTUAL reason from the saved table: "fewer than 100 scored hours" (rows < 100) and/or "some oblasts had too
   few alert starts or too few no-start hours to rank" (units left out of the within-unit AUC) — no comparison without it.
2. **Tile map (24 tiles, approximate geography, no external map data):** fixed grid positions per unit kept in the
   template (a layout table, not data). Two views: "How often a new alert starts within the next hour, in hours with
   no recent alert running" — with the one-line explanation used everywhere on the page: "an alert counts as running only in
   its first 24 hours, so hours under a months-long standing alert are still forecast (D-020)" (base rate over SCORED hours; the denominator — scored hours — is shown on hover and in the table),
   sequential single hue, and
   "Model vs the two-week rule" (per-unit Brier skill, diverging two hues with a grey midpoint at 0). Low-n tiles get a
   hatch texture and the ACTUAL reason ("fewer than 100 scored hours" or "too few alert starts / quiet hours to rank"); hover/tap shows the unit's numbers; a table view lists all 24 values. Luhanska and
   Crimea are drawn as greyed, labelled "not forecast" (D-008) so the map isn't misleading.
3. **Forecast timeline:** pick an oblast (default Kyiv City) and a test week; line = model probability per hour, second line
   = two-week rule (both null and broken on non-scored hours), markers = real merged onset timestamps (an onset exactly at
   an hour boundary is drawn at that instant), bands drawn distinctly for "under alert", "recording gap / missing" and
   "feature missing" (the D-024 rows). One y-axis (probability 0–max). Week selector limited to the test window; the recording-gap week shows the gap.
4. **What changed in September (exploratory):** the existing section, simplified copy, the open-decision note kept.
5. **For the technically curious** (`<details>`): the current metric tables, calibration, method, leakage evidence,
   coverage, limitations.

## 4. Design rules
Dataviz skill: validated palette (sequential + diverging + series), legends for ≥ 2 series, direct labels selective,
hover + keyboard focus, table views; light/dark; phone width (map tiles scale; timeline scrolls horizontally inside its
own container only). Copy: plain words ("chance", "the simple two-week rule"), no jargon above the fold.

## 5. Tests
- `export_predictions.py`: reproduces metrics.csv exactly (else raises); refuses if any frozen hash differs; per-unit table
  recomputed from test_predictions.csv equals metrics_by_unit.csv; sum of per-unit scored rows = overall rows; 24 units.
  Assignment check independent of the export: for sampled (unit, t), y, mask/gap status are re-derived from the RAW alerts
  via `grid.build_grid` for that unit alone, the features via `features.build_features` at those times, and the exclusive
  status via the D-024 precedence (purge → under_alert/gap → label unknown → feature missing); all must match; mutations that swap two rear units' rows or shift timestamps by
  one hour must fail. Kyiv City and Kyivska separate. Onsets in test_onsets.csv equal `grid.unit_intervals` merged starts,
  incl. one exactly at an hour boundary.
- Leakage on the export path: the exporter's per-row prediction at a time t equals the prediction from data truncated at t
  (drop starts > t, hide ends > t) at 7 times incl. a standing alert past 24 h, a gap edge, the cut-off and a DST switch
  (2025-10-26 01:00 UTC, a historical audit time run through the same exporter function, since the test window has
  no DST change). The comparison covers every model INPUT column and the causal state (mask, gap_mask) before suppression — not
  only the prediction, so null-vs-null rows cannot hide a difference; the recent-rate history window stays [t − 14 d, t − H]
  (negative control: a window to t is caught at a pinned witness).
- build_site: map/timeline payload values traced to metrics_by_unit.csv / test_predictions.csv by key; low-n flags carried;
  the plain-answer sentence's numbers equal source keys and its wording follows the sign (mutation: flipped sign → test fails).
- Page smoke: no console errors for every control state (map view toggle, each oblast, each week), no horizontal overflow at
  375 px, no network request.

## 6. Done when
Export script + guard pass; site rebuilt; `pytest -q` green; headline reproduction still passes (fingerprint unchanged);
M5's Streamlit app and technical sections still pass their checks; reviewer SHIP; harness review fixed or argued; preview
republished; Netlify deploy remains OUTSTANDING (needs the human); milestone summary, proposed decision entry (D-031, and
corrections: D-029 "Google Fonts only" → no remote fonts; D-014 purge wording → t + H ≤ cut-off; D-016 "closed alerts" →
D-027), and the D-026 consensus record.

## 7. Decisions (round 1)
1. Per-unit breakdown — AUTHORISED by the human (proposed D-031).
2. Map default view: frequency (intuitive for the public) — PROVISIONAL.
