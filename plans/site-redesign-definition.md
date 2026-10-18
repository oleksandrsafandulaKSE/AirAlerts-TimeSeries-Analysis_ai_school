# Site redesign — definition (grilling session with the human, 2026-10-18)

Status: agreed with the human in chat ("all agreed", "agreed, also go for round with codex"). Lines marked **[rule]**
change an existing D-entry (proposed or ratified); they are the human's decisions and are proposed in
`reviews/PROPOSED-DECISIONS-site.md`. Lines marked PROVISIONAL are design defaults for the milestone plans (D-026).
Work starts from `main` after the merge of M6a, M6c-1, M6-site and M10/M11 (done: 8f91abe).

## Why
Human: "a lot of useless info for a regular user; the main idea of my project is an interactive map predicting the
chance of an alert in the next n hours — that's the main feature on the main page, with the title explaining it,
not many features and statistics on one page."

## Audience and job
- Primary: an ordinary person in Ukraine. Secondary (one click away): a reviewer of the study.
- Job of the main page: an interactive map of the chance that a NEW air-raid alert starts within the next N hours.

## Pages (tabs, in this order)
1. **Map** (main).
   - Header: title **"Air-Alert Forecasting"**; subtitle **"Will there be an alert in 1 h / 3 h / 6 h / 12 h /
     24 h?"** with those buttons; forecast time; one-line disclaimer. English only. No metrics on this page.
   - Map: **oblasts only** (24 units). Colour = chance of a new alert within the selected horizon; under-alert
     oblasts striped (no forecast while a non-standing alert runs, D-020).
   - Hover: oblast name; chance for the selected horizon; "under alert since HH:MM"; "If it comes: likely
     yellow / red · in testing".
   - Click card: big % for the selected horizon; a **chance ladder** 1 · 3 · 6 · 12 · 24 h (one bar row); state;
     yellow/red line; the 7-day strip (actual alerts vs our forecast, from M11).
   - Removed from the main page: two-week-rule number, neighbour list, caution jargon, 14-day block grid, study
     map, timeline, metrics, calibration, new-regime tables, method, leakage, coverage.
2. **Replay**: the M6c-1 test week (2026-10-11 → 10-17) on the map, hour by hour (frozen M6c-1 "any" blend).
3. **Forecast check**: one headline line ("last N days: our forecast vs the simple two-week rule"), one calibration
   chart, per-day bars, with a horizon selector. No tables. FACT: the M11 scorer hard-codes H = 1
   (`netlify/live/lib/check.mjs:112-120`) and one model; M12 (not M13) versions snapshots and the check archive by
   (model version, target, H), scores (τ, τ + H] only after τ + H + SETTLE with coverage over [τ − 24 h, τ + H], and
   never pools across models or horizons. Snapshots made by the M8 model stay scored as their own series.
4. **How good is it?**: (1) the new-data model's test week vs the simple rule, H = 1 and 3; (2) the official study
   verdict (frozen model did not beat the rolling recent rate, BSS −0.0101) + one calibration chart;
   (3) limitations. Everything else (M7/M9/M10 tables, leakage evidence, coverage) moves to the README, linked.
5. **What kind of alert?**: "if an alert starts, how likely is it red?" Map coloured by that chance; one line of
   explanation; "in training: a red/yellow model is retrained monthly; until it beats the simple rule this page
   uses the rule"; a small chart of how often the rule was right; click → "of its last N alerts, R were red".
   Linked to and from the main map.
6. **About**: what it is, data, method in plain words, disclaimer.
- Look: our current visual system (tokens, SVG geoBoundaries map); structure and content change only.

## Model decisions
- **[rule] Main map model = the M6c-1 "any" model (API data only) blended with the two-week rule**,
  p = w·p_model + (1 − w)·p_baseline (D-035 proposed blend, 28 d window, n₀ = 50), retrained monthly (M6b). It
  replaces the M8 live model (official-data V2 offset, H = 1). The frozen official model stays on "How good is it?"
  as the study result. Evidence (exploratory, one test week, BSS vs rolling recent rate): ANY model +0.085 (H1) /
  +0.118 (H3); frozen official model +0.029 / +0.130.
- **[rule] One alert-type contract: air-raid only, everywhere on the main map.** The M6c-1 "any" model is trained on
  `alert_type == air_raid` (`newregime/data.py:17`), while the M8 live "any" path accepts all API types
  (`netlify/live/lib/live.mjs:17`; D-032 proposed, D-040 "the any map keeps all API alert types"). Since the human chose
  the M6c-1 model, the live labels, masks, features, baseline and scorer for the main map switch to air-raid only, so
  model and inputs match. Amends D-040's "any keeps all types" clause. **APPROVED by the human (chat 2026-10-18): "Approve D-045:
  the main map (any target, masks, features, baseline, scorer) uses air-raid alerts only, matching the M6c-1 model."**
  Artillery/urban-fight alerts are not shown as alerts on the map (FACT to state on About).
- **New "any" horizons H = 6, 12, 24 h** with the M6c-1 pipeline (same target definition: an air-raid onset of any
  level in (t, t+H]; same per-type mask; H is configurable in CLAUDE.md, so not a target-definition change). Yellow and red
  stay at H = 1 and 3. Known: P(onset within 24 h) is close to 1 for many oblasts; the page notes it.
- **"If an alert starts, red or yellow?" = the simple rule, as a CONDITIONAL quantity.**
  - Conditioning event: an "any" onset = the start of a merged air-raid interval of any level (D-020 cap) — the same
    event the main map forecasts. Its colour = the level of the alert(s) starting at that instant; if red and yellow
    start at the same instant it is red. A red that starts inside an already-running yellow interval is NOT a new
    "any" onset (it is an escalation) and does not enter this quantity; the page says so in one line.
  - Rule at t: R / N over "any" onsets with start in (t − 7 d, t] (elapsed UTC), N = 0 → "no alerts in 7 days", no %.
    Units with incomplete coverage in that window → "not enough data". Comparator: the national share computed the
    same causal way.
  - This is a different event from the M6c-1 unconditional red-onset model. A model-based replacement must be scored
    on the identical conditional outcome and rows before it can replace the rule.
  - Accuracy (exploratory, API): Brier and within-oblast AUC (≥ 10/10, D-025) of the rule vs the national share.
- **[rule] Yellow/red on the site**: hover note + click card + a separate page (amends D-036/D-040 "hover only").
  Always labelled "in testing / in training".

## Milestones (order agreed)
1. **M12 — models and live export.**
   - Add H = 6, 12, 24 to the "any" pipeline (`newregime/pipeline.py` has `HORIZONS = (1 h, 3 h)` hard-coded).
   - Evaluate them like H = 1/3. FACT: the M6c-1 test reservation refuses any test week overlapping
     2026-10-11 → 10-17, so the new horizons need a NEW, later test week (data collected daily by M6a; the first
     full week after the M6c-1 test ends 10-24, plus 24 h of label maturity for H = 24). Until then they are shown
     validation-only and labelled "not yet tested". PROVISIONAL.
   - Export "any" H = 1…24 and yellow/red H = 1/3 models + blend state to the Netlify function, with JS–Python
     parity tests (as M8).
   - **Cutover order (in M12):** the versioned snapshot store and the (model, target, H) scorer are built and tested
     first; the new export stays INACTIVE (the M8 model keeps serving the map) until both exist; the switch is one
     explicit step, recorded in the live status. No new-model forecast ever reaches the one-hour M11 scorer.
   - Red-share rule accuracy on API data (exploratory): Brier / within-oblast AUC of the rule as P(red | onset)
     vs the national red share.
   - FACT: M6c-1 saved validation predictions only, no per-row test predictions. Replay needs them: a
     **retrospective reconstruction** from the frozen M6c-1 artefacts, labelled as such on the page (the models did
     not exist during that week). Pinned: the datastore commit used by aa05529, sha256 of models, calibrators,
     baseline tables and `blend_weights.csv`, the code commit. No metric is recomputed; the reservation is not
     touched; a test asserts that replaying the reconstructed rows reproduces the published `metrics.csv` values
     (consistency check, not a new score). Revisions arriving after that week are in the inputs (D-027 latest version,
     as M6c-1's own reconstruction); stated on the page.
   - Requirements for the M12 plan: per-model/horizon blend state built only from out-of-sample rows with
     s + H ≤ t, onsets counted once, reset rule on monthly replacement; exact UTC boundaries of the new test week
     (PROVISIONAL default: same fit/validation as M6c-1, test [2026-10-18, 2026-10-25), forecast rows with
     t + H ≤ test end, equality kept per D-022) and a reservation scoped to the new horizons; reliability plots,
     within-oblast AUC, identical eligible support for model vs baseline, exclusion counts and run metadata
     (D-017/D-024); JS–Python parity PLUS independent truncation and mutation controls per horizon (onsets at t and
     t + H, purge equality, future `finished_at`, the 24 h standing cap, DST, coverage holes, Kyiv City vs Kyivska)
     with a negative control each.
2. **M13 — site redesign** (the pages above), on top of the M11 + M6-site live code.
Each milestone: plan → Claude–Codex consensus (D-026) → implement → tests → reviewer + harness → summary.

## Not in scope
- District (raion) map: a new target unit, model and evaluation (rule change); a later milestone if wanted.
- Alert-duration, 24 h alert-count, hours-under-alert and 3-hour-block timing models (new targets).
- A 1–24 h slider (needs 24 models or a time-to-event model).
- UA translation.

## Notes for the human
- Proposed D-numbers collide: D-040 is used by both M6-site and M6c-1, and the M10/M11 summaries proposed D-033/D-034,
  which M6 already uses. Renumber when ratifying; this definition uses D-041 … D-045.
- D-027 latest-version merge vs strict knowledge-at-t: kept as in M6c-1/M6-site (latest version, documented as a
  retrospective limitation); not changed here.

## Open questions for the loop (design inside the rules)
1. How to label horizons that have only validation results on the main map (6/12/24 h until their test week).
2. Whether the M6c-1 blend weight for H = 6/12/24 can use the same pooled 28-day rule when label maturity is 24 h
   (fewer known labels near t).
3. Whether regenerating M6c-1 test-week predictions for Replay is compatible with "scored once".
4. What the live map shows if the M6c-1 model or its export is unavailable (no silent fallback: an explicit state).
