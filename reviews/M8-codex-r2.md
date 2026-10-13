### Shell: `'cat plans/M8.md'`
# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function

Status: v1.1 after consensus round 1 (D-026 loop). Human decisions in chat (2026-10-13): "the UI has to be an
interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
to the recent level); a Netlify scheduled function; geoBoundaries ADM1 boundaries. This starts part of M6 (D-016) by
the human's explicit decision. Further human decis
### Shell: `'cat .claude/skills/ts-leakage-audit/SKILL.md'`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `'cat CLAUDE.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'cat reviews/M8-codex-r1.md'`
### Shell: `'cat plans/M8.md CLAUDE.md DECISIONS.md reviews/PROPOSED-DECISIONS-M4-M5.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function

Status: DRAFT for the Claude–Codex consensus loop (D-026). Human decisions in chat (2026-10-13): "the UI has to be an
interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
to the recent level); a Netl
### Shell: `'cat reviews/M8-claude-r1.md'`
# Claude response, round 1 — plans/M8.md

## Changes made
- B1 forecast time — ESCALATED and decided by the human: forecast (τ, τ + 1 h] with inputs ≤ τ (τ = run time); recorded as a deliberate definition change (proposed D-032), labelled on the page.
- B2 reconciliation leakage — AGREE: records are versioned (first_seen_at, end_seen_at, end_source, history_reconciled_at); inputs at τ use only versions known at τ; truncation/replay tests + a negative control for a reconciled end not yet known.
-
### Shell: `"rg --files -g AGENTS.md -g '*M8*' -g '*m8*'"`
reviews/M8-codex-r1.md
reviews/M8-claude-r1.md
reviews/M8-codex-r2.log
reviews/M8-codex-r1.log
plans/M8.md

### Shell: `'cat reviews/M8-claude-r1.md'`
# Claude response, round 1 — plans/M8.md

## Changes made
- B1 forecast time — ESCALATED and decided by the human: forecast (τ, τ + 1 h] with inputs ≤ τ (τ = run time); recorded as a deliberate definition change (proposed D-032), labelled on the page.
- B2 reconciliation leakage — AGREE: records are versioned (first_seen_at, end_seen_at, end_source, history_reconciled_at); inputs at τ use only versions known at τ; truncation/replay tests + a negative control for a reconciled end not yet known.
-
### Shell: `'cat improve/features_plus.py; cat src/grid.py; cat src/features.py'`
"""M7 extra inputs, all known at t (plans/M7.md §2.1, §3). Reads src/ read-only; never changes the headline pipeline.

Block A (labels, s <= t - H; human-approved exception): unit shrunk recent rates over 14 d and 30 d, national 14-d rate.
Offset input: r(t) = the unit's 14-d shrunk rate with the CAUSAL expanding prior q(t).
Block B (onset events up to t): national onsets (t-1h, t] and (t-3h, t]; frontline onsets (t-3h, t]; neighbours' onsets
(t-1h, t]; minutes since the last national onset.
Blo
### Shell: `'tail -n 45 DECISIONS.md'`
  (approved D-017 exception).
- Validation results (overall, measured): recent rate Brier 0.0775; Brier skill vs recent rate: calibrated
  persistence −0.143, climatology −0.214, raw persistence −0.612. Recent rate has the lowest Brier overall, in
  frontline and in rear. Kyiv City (625 rows) is the exception: calibrated persistence beats recent rate (skill +0.019).
- Pooled vs within-unit AUC (measured): pooled ROC-AUC is high (recent rate 0.883, calibrated persistence 0.881,
  climatology 0.85
### Shell: `'cat CLAUDE.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"rg --files src tests scripts improve .claude/skills; rg -n 'D-030|D-032|D-028|D-029|confirmed_through|fetch_time|fetched_at|history_start' plans reviews src scripts improve"`
scripts/export_predictions.py
scripts/run_all.py
scripts/build_site.py
scripts/run_improve.py
scripts/__init__.py
src/__init__.py
src/regions.py
src/config.py
src/grid.py
src/baselines.py
src/model.py
src/features.py
src/evaluate.py
src/data.py
improve/features_plus.py
improve/__init__.py
improve/model_plus.py
.claude/skills/ts-leakage-audit/SKILL.md
.claude/skills/milestone-protocol/SKILL.md
.claude/skills/codex-plan-review/SKILL.md
tests/test_api_loader.py
tests/test_run_all.py
tests/test_new_
### Shell: `'nl -ba plans/M8.md'`
     1	# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function
     2	
     3	Status: v1.1 after consensus round 1 (D-026 loop). Human decisions in chat (2026-10-13): "the UI has to be an
     4	interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
     5	to the recent level); a Netlify scheduled function; geoBoundaries ADM1 boundaries. This starts part of M6 (D-016) by
     6	the huma
### Shell: `"sed -n '40,155p' improve/features_plus.py; cat improve/model_plus.py"`
def _zones_naive(zones):
    return [(np.datetime64(pd.Timestamp(a).tz_convert("UTC").tz_localize(None), "ns"),
             np.datetime64(pd.Timestamp(b).tz_convert("UTC").tz_localize(None), "ns")) for a, b in zones]


def label_rates(g, H, zones=()):
    """Block A + offset rate from the grid's binary labels. g: complete hourly grid (unit, t, mask, y) sorted by unit, t.
    k = sum(y), n = count(y) over ELIGIBLE rows (mask == 0, y known) with s in the window and s <= t - H."""
    if H <= pd.T
### Shell: `"sed -n '1,180p' src/grid.py; sed -n '1,160p' src/features.py; sed -n '185,215p' src/data.py"`
"""Per-unit intervals (D-002 union, D-020 causal cap), gap handling (D-013), hourly UTC grid."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError


def filter_levels(alerts, target_levels):
    if target_levels == "any":
        return alerts
    if target_levels == "red":
        if (alerts["alert_level"].fillna("") == "").all():
            raise ValueError("target_levels='red' needs alert_level (official data has none)")
        return aler
### Shell: `"cat reviews/PROPOSED-DECISIONS-M4-M5.md; sed -n '1,90p' plans/M7.md; rg --files --hidden -g AGENTS.md -g '"'!.git/**'"'"`
# Proposed DECISIONS.md entries (written while the human was asleep; the human edits and commits them)

Numbers are copied from `reports/` (final test scored once, 2026-10-13).

## D-028 — M4: models, the single final-test scoring, new-regime section (Claude–Codex consensus → human to ratify)
- One pooled LightGBM model per horizon (human: "option 1"), fixed settings (lr 0.05, 31 leaves, min_data_in_leaf 100,
  seed 20261013, deterministic, early stopping 100 rounds on pooled validation logloss,
### Shell: `"rg -n 'api_oblast_name|FEATURES|units\\(|_UNITS|def unit_intervals|finished_at|cap|EXCLUDED_API' src/regions.py src/features.py src/grid.py; sed -n '1,58p' src/regions.py; sed -n '1,72p' src/grid.py"`
src/regions.py:4:_UNITS = [
src/regions.py:34:EXCLUDED_API_UIDS = {16: "Luhanska (D-008)", 29: "Crimea (not in the official data)", 30: "Sevastopol (not in the official data)"}
src/regions.py:95:UNITS = {k: {"official_name": n, "api_uid": u, "group": g, "api_oblast_name": _API_OBLAST_NAMES[k]}
src/regions.py:96:         for k, n, u, g in _UNITS}
src/regions.py:104:def units():
src/features.py:12:FEATURES = ["minutes_since_last_start", "minutes_since_last_end", "onsets_last_24h", "onsets_last_7d"
I’ll check each previous finding against the updated plan and builder’s evidence, then assess the provisional decisions against the project rules.
The plan addresses several earlier blockers: it records approval for the new forecast interval, preserves observation-time versions, and separates physical alert status from the 24-hour mask. I’m applying the leakage-audit skill to check the coverage and replay rules, especially during outages.
Two gaps remain: a fresh history fetch can reset coverage without proving that an older outage was recovered, and the GET endpoint only returns `latest.json` even though the page needs the separate failure status. The one-minute cadence and map replacement fit the rules; the 90-minute threshold cannot replace the required treatment of missing data.
## PREVIOUS ITEMS

- B1 — RESOLVED: explicit human approval covers forecasts over `(τ, τ+1h]`.
- B2 — RESOLVED: versioned observations, timestamp filtering, and replay preserve information available at τ.
- B3 — OPEN: `confirmed_through` alone cannot establish continuous coverage. After an outage exceeding the history endpoint’s 30-day window, advancing this timestamp can certify unrecoverable missing hours. Track covered intervals and retain holes.
- B4 — RESOLVED: physical alert status and the capped forecasting mask are separate.
- A1 — RESOLVED: training dates, iteration, feature/category order, and causal offset are pinned.
- A2 — RESOLVED: exact parent-oblast mapping and Kyiv City/Kyivska fixtures are specified.
- M1 — OPEN: §5’s negative control, “s ≤ τ,” includes legitimate historical labels. Specify an immature-label witness with `τ−H < s ≤ τ` and require its detection.
- M2 — OPEN: §2 does not specify recovery of gap-crossing lookbacks, time-since features, or affected national/neighbour inputs. D-022–D-024 require uncertainty propagation until backfill proves completeness; recent coverage alone is insufficient.
- M3 — RESOLVED: raising checks, diagnostics, and parsed deduplication timestamps are specified.
- M4 — OPEN: the GET function returns only `latest.json`, while failure status lives separately. Specify how status reaches the browser and test failure delivery; five-minute polling also contradicts “immediate” greying.
- Q1 — RESOLVED: the human approved all alert types.
- Q2 — RESOLVED: exact Netlify dependency versions are approved.
- Q3 — RESOLVED: the human ratified cutoff equality.

## PROVISIONAL DECISIONS

- One-minute polling with one history request per run stays within the rate limit.
- Replacing the study tile map preserves the approved presentation scope and numbers.
- The 90-minute threshold is permissible as a freshness policy. Using it to waive D-022–D-024 missing-data rules would be a rule change requiring escalation.

## NEW ISSUES

- §2 raises on unmapped national ACTIVE records but omits deliberate exclusions. Handle Luhanska, Crimea, and Sevastopol explicitly using `src/regions.py` before rejecting unknown names.
- §3’s “air-raid alert” header mislabels the newly approved all-types target, including shelling and urban fighting.
- §1 still promises 15-minute recomputation; §2 schedules every minute. Choose consistent wording.

VERDICT: CHANGES REQUIRED
