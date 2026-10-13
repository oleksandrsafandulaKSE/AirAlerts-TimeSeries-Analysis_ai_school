### Shell: `"pwd; rg --files -g 'AGENTS.md' -g '*leak*' -g 'SKILL.md' -g 'CLAUDE.md' -g 'DECISIONS.md' -g 'M5*.md' -g 'PROPOSED-DECISIONS-M4-M5.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
DECISIONS.md
CLAUDE.md
tests/test_leakage.py
plans/M5b.md
plans/M5.md
reports/leakage_evidence.json
reviews/PROPOSED-DECISIONS-M4-M5.md
reviews/M5-claude-r1.md
reviews/M5-codex-r1.md
reviews/M5-codex-r4.md
reviews/M5-claude-r3.md
reviews/M5-codex-r3.md
reviews/M5-claude-r2.md
reviews/M5-codex-r2.md
reviews/M5-consensus.md

### Shell: `'cat plans/M5b.md plans/M5.md'`
# M5b plan v1 — Results page for the general public: plain summary, tile map, forecast timeline

Status: DRAFT for the Claude–Codex consensus loop (D-026). Human decisions in chat (2026-10-13): audience = GENERAL
PUBLIC; add a tile map of the 24 units and a forecast timeline; no M7 section and no language toggle on the site.
Rules: CLAUDE.md, D-011, D-021, D-024, D-025, M5 plan (every number from reports/, no hand-typed result numbers,
no network requests, code fingerprint untouched).

## 1. Goa
### Shell: `'cat CLAUDE.md DECISIONS.md reviews/PROPOSED-DECISIONS-M4-M5.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
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
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"rg --files --hidden -g '*SKILL.md' -g 'AGENTS.md' -g '*leakage*' . /Users/oleksandrsafandula/.agents/skills /Users/oleksandrsafandula/.claude/skills /Users/oleksandrsafandula/.codex/skills"`
/Users/oleksandrsafandula/.claude/skills/plan-review/SKILL.md
/Users/oleksandrsafandula/.agents/skills/writing-beats/SKILL.md
/Users/oleksandrsafandula/.codex/skills/.system/imagegen/SKILL.md
/Users/oleksandrsafandula/.agents/skills/migrate-to-shoehorn/SKILL.md
/Users/oleksandrsafandula/.agents/skills/grilling/SKILL.md
/Users/oleksandrsafandula/.codex/skills/.system/skill-creator/SKILL.md
/Users/oleksandrsafandula/.codex/skills/.system/review-agent/SKILL.md
/Users/oleksandrsafandula/.codex/skill
### Shell: `"cat .claude/skills/ts-leakage-audit/SKILL.md; rg -n 'def build_frames|def score_final_test|preregistration|fingerprint|test_predictions|eligible|data_sha|joint|load_official' scripts/run_all.py src/m`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `"sed -n '1,175p' scripts/run_all.py; sed -n '295,418p' scripts/run_all.py"`
"""Pipeline entry point (M1-M4).

  python scripts/run_all.py --config official      [--stage fit]   # M1-M3 + model + calibration + pre-registration
  python scripts/run_all.py --config official_h3   [--stage fit]   # the same for H = 3 (extra results row)
  python scripts/run_all.py --stage final-test                     # scores the FINAL TEST once, both horizons (D-021)
  python scripts/run_all.py --config new_regime                    # exploratory API section (D-015, D-027)

The fit stage 
### Shell: `'cat tests/test_leakage.py; cat src/config.py'`
"""Truncation-invariance leakage test (ts-leakage-audit) on the REAL official data, with a negative control."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import config, data, evaluate, features as F, grid, regions

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "official_data_en.csv"
CFG = config.official()
ZONES = config.uncertainty_zones(CFG)
NB = {"A": {"B"}, "B": {"A"}}


def truncate(alerts, t):
    """Alerts as known at t: d
### Shell: `'cat src/evaluate.py; cat src/baselines.py'`
"""Splits, eligibility, test-label isolation and the metric suite (M3; reused unchanged in M4)."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from src.data import DataQualityError

GROUPS = ["overall", "kyiv_city", "frontline", "rear"]
REASONS = ["purge", "masked", "y_nan", "feature_nan"]


def split_bounds(cfg, split, allow_test=False):
    """The only way to get split dates; the test split needs allow_test=True (M4, D-021)."""
   
### Shell: `"sed -n '105,178p' DECISIONS.md; cat src/evaluate.py"`
  next to pooled AUC.
- If time allows (me): (6) week-block bootstrap CI on the gain over recent-rate;
  (7) reliability plot per oblast group.
- Skipped (me): text/Telegram/weather features, multiple horizons, survival models,
  hyperparameter search, walk-forward retraining inside the test window. All listed as limitations.

## D-014 — Weekly refit as an extra results row
- Context: the recent-rate baseline adapts every day while the frozen model doesn't, so the
  comparison is tilted against 
### Shell: `"rg -n 'google|font|fonts|new_regime_all_types|open.decision|artillery|low_n|truncation|leakage' scripts/build_site.py tests/test_site.py; sed -n '1,155p' src/grid.py; sed -n '1,145p' src/baselines.py`
tests/test_site.py:27:                         "pr_auc": 0.3 + 0.01 * i, "pr_auc_over_base": 3.0 + 0.1 * i, "low_n": j == 2})
tests/test_site.py:52:    for v in ("new_regime", "new_regime_all_types"):
tests/test_site.py:58:                       "within_unit_units_excluded": "", "roc_auc_pooled": 0.8, "low_n": False}
tests/test_site.py:68:    (r / "leakage_evidence.json").write_text(json.dumps([{"check": "c", "test": "tests/t.py::x", "result": "PASS", "pytest": "1 passed"}]))
tests/test_site.py:
I’ll read the plans, project rules, decision log, and leakage-audit skill first, then check the existing code for claims that affect the review.
I’m using the project’s `ts-leakage-audit` skill. M5b introduces a prediction export and per-unit test metrics despite M5’s ban on new test metrics; I’m checking the frozen-artifact guards and whether the timeline preserves the scoring exclusions.
## BLOCKERS

- M5b §2 “metrics_by_unit.csv” adds test metrics despite M5’s “no new metric on the test.” Exact reproduction of aggregate scores does not authorize this extension. Under D-026, obtain an explicit exception before implementing it.
- M5b §3 “grey bands … under alert or missing” omits D-024’s unmasked rows with missing features. Export exclusion reasons; render gaps, unknown features, and active alerts distinctly. Set predictions to null on ineligible rows and break lines across them.
- M5b §5 “recomputed independently … from test_predictions.csv” still passes if exported rows are assigned to the wrong rear unit: group scores and subsequent recomputation remain consistent. Check `(unit,t)` assignments against independently derived source rows; require unit-swap and timestamp-shift mutations to fail.

## AMBIGUITIES

- M5b §3 “hours where a new alert actually started” cannot be recovered precisely from `y(t)`, which describes `(t,t+H]`. Export merged onset timestamps under D-023, or explicitly plot outcome windows; test onsets exactly at both endpoints.
- M5b §3 “How often new alerts start” uses base rate conditional on eligibility, not all hours. Label its denominator and show eligible hours. “few hours” also misdescribes AUC undefined through insufficient positives/negatives; display the actual reason.
- M5b §3 “wording chosen by sign only” leaves zero, undefined skill, and low-n groups unspecified. Define all three cases and preserve uncertainty beside public comparisons.
- D-014 “Purge the last H hours” conflicts with D-022’s retained equality boundary. D-016’s “closed alerts” conflicts with D-027’s open-alert rule. Propose amendments making `t+H≤cutoff` and causal open-alert retention explicit.
- Proposed D-029 “Google Fonts only” contradicts M5/M5b “no network requests.” Remove remote fonts and correct the proposed entry.

## MISSING

- M5b §5 lacks exporter-specific leakage evidence. Apply truncation invariance to the actual export path: hide future ends; cover standing alerts beyond 24h, DST, gap edges, and cutoffs. Include negative controls for future-label windows; verify recent-rate history remains `[t−14d,t−H]`.
- M5b §6 “Done when” omits the required milestone summary, proposed decision entry, and D-026 consensus record. Add these; retain M5’s required Streamlit and technical-section checks.

## QUESTIONS FOR THE HUMAN

- M5b §7 “acceptable under D-021”: do you authorize the per-unit test-metric extension to M5? Record that exception explicitly; consensus cannot amend evaluation rules.

VERDICT: CHANGES REQUIRED
