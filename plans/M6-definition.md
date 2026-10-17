# M6 — definition (grilling session with the human, 2026-10-17)

Status: agreed with the human in chat ("Yes, record it"). Lines marked **[rule]** change CLAUDE.md or an existing
D-entry. They are the human's decisions and are proposed as D-entries in `reviews/PROPOSED-DECISIONS-M6.md`; the human
edits and commits DECISIONS.md / CLAUDE.md. Lines marked PROVISIONAL are design defaults to be reviewed in the
milestone plans (Claude–Codex consensus, D-026).

## Goal
Keep collecting new-regime (yellow/red) alert history from alerts.in.ua, and forecast per oblast, at every hour t:
P(any alert starts in (t, t+H]), P(a YELLOW alert starts …), P(a RED alert starts …).
Type = `alert_level` (yellow = drones, red = missiles). The live-only `threats[]` field is not used.

## Milestones (order agreed)
1. **M6a**: collection. Seed `datastore/alerts_in_ua.csv` from the 2026-10-12 dump, build the collector and daily
   GitHub job, and do the first fetch (12 Oct → today). Plan: `plans/M6a.md`.
2. **M6c-1**: first training now (any / yellow / red; H = 1 headline, H = 3 also reported) with blend, results vs
   baseline on one test week, and the chart.
3. **M6b**: monthly automatic job: fetch → pytest → retrain → evaluate → update chart and site.
4. **Site**: on the M8 live site, oblast hover shows yellow/red probabilities labelled "in training", the
   collection status, and the monthly chart section.
Each is its own plan + Codex consensus + reviewer, with a summary to the human after each.

## Decisions
- **[rule] Targets.** Two new binary targets per oblast: yellow onset and red onset in (t, t+H]. The "any" target
  stays. Eligibility per type: a row is masked only if THAT level is active at t, so red starting during yellow
  counts, and so does yellow during red. (Measured on the dump: 31% of red onsets start inside yellow.)
- **[rule] Training on API data allowed** (amends "No training or tuning on API data"). API only, never mixed with
  official data in one training set or metric.
- **"Any" model on new data:** same recipe as the official model (features, settings, target "any" = yellow ∪ red),
  trained FROM SCRATCH on API data only. The frozen official model is kept as a comparison line, and its prediction
  may be tested as an input feature.
- **[rule] Train now, retrain monthly, fully automatic** (amends D-016 "≥ 3 months" and CLAUDE.md "a yellow-regime
  model is trained only with the human's explicit approval"). Gate: the monthly job runs `pytest` (incl. the
  leakage test) first; a failing test keeps last month's model.
- **First split** (exact dates fixed on the fetch day): train 2026-09-13 → 10-04, validation 10-04 → 10-11 (early
  stopping + blend weights), test 10-11 → 10-17 (scored once). Labelled EXPLORATORY (one test week).
- **Blend shown on the site.** Per type, at t: p = w·p_model + (1 − w)·p_baseline,
  w = n/(n + n₀) · clip(w*, 0, 1), with w* = Σ(p_base − y)(p_base − p_model) / Σ(p_model − p_base)² over the
  already-known labels in [t − 28 d, t − H]; n = onsets of that type in that window. Before a model exists, w = 0.
  The hover states the weights. Evaluation reports model, baseline and blend separately.
  PROVISIONAL: one weight pooled over all oblasts, 28-day window, n₀ = 50.
- **[rule] Live site** (M8) shows yellow/red on hover only (not the main view), labelled "in training", plus
  "collecting data: N days" and the monthly chart.
- **Chart:** monthly Brier skill vs the recent-rate baseline per type (any / yellow / red) + blend weight w over
  time, in `reports/monthly/` and on the site.
- **Collector token:** the same `ALERTS_IN_UA_TOKEN` as M8, collector slowed to 1 history request / 2 min
  (M8 uses 1/min; the limit is 2/min). A 429 is retried and logged; a second token only if 429s show up.
- PROVISIONAL (defaults for the M6c plan): typed onset = start of a merged interval of that level's alerts (all
  location levels, D-020 24h cap); main baseline = rolling recent rate per type (14 d, shrunk to the oblast's rate),
  extra row = recent-rate P(any) × recent red share; reporting pooled + per group, within-oblast AUC only with
  ≥ 10 positives and ≥ 10 negatives; features = per-type versions of the current features + "the other level is
  active at t".

## Facts behind it (2026-10-12 dump, air_raid, starts 13 Sep → 12 Oct, 24 units)
Onsets: any 3,896 / yellow 3,720 / red 962. Base rate at H = 1: any 0.25, yellow 0.22, red 0.05. Red is concentrated
in Kharkivska, Sumska and Kirovohradska (488 of 962), with 3–4 red onsets per western oblast. 83% of "any" onsets
begin with yellow.
