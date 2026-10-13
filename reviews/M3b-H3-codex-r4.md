### Shell: `"pwd; rg --files -g 'AGENTS.md' -g 'SKILL.md' plans reviews .claude /Users/oleksandrsafandula/.agents/skills/code-review 2>/dev/null"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
/Users/oleksandrsafandula/.agents/skills/code-review/SKILL.md
.claude/skills/ts-leakage-audit/SKILL.md
.claude/skills/codex-plan-review/SKILL.md
.claude/skills/milestone-protocol/SKILL.md

### Shell: `'cat plans/M3b-H3.md'`
# M3b plan v1 — Additional horizon H = 3 (extra results row, never the headline)

Status: v1.3 after consensus round 3 (D-026 loop). Requested and approved by the human (2026-10-13):
"add additional horizon h=3".
Amends D-000 (H = 1 only) and D-013 (multiple horizons skipped). The headline stays H = 1.

## 1. Goal
Run the existing M1–M3 pipeline with H = 3 hours as a second, separate run:
`python scripts/run_all.py --config official_h3` → `reports/official_h3/` with the same files as
`reports/of
### Shell: `'cat reviews/M3b-H3-codex-r3.md reviews/M3b-H3-claude-r3.md'`
### Shell: `'cat .claude/skills/ts-leakage-audit/SKILL.md'`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 ran
### Shell: `'cat CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'tail -n 60 reviews/M3b-H3-codex-r3.md; cat reviews/M3b-H3-claude-r3.md'`
  fit uses train rows only (same perturbation check).
- Raw persistence: onset at t − 30 min → 1; onset exactly at t − H → 0 (outside (t−H, t]); onset at t → 1.

**test_run_all.py**: on the existing fixture, the M3 stage writes `metrics_validation.csv` with
4 baselines × 4 groups, the PNG and `m3_checks.json`; and no file contains test-period metrics.

## 7. Printed
Per split (train, va
### Shell: `"sed -n '1,165p' tests/test_run_all.py"`
import dataclasses
import json

import pytest

from scrip
### Shell: `'cat CLAUDE.md .claude/skills/ts-leakage-audit/SKILL.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"rg --files -g AGENTS.md /Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school /Users/oleksandrsafandula/.agents 2>/dev/null; sed -n '1,75p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"sed -n '75,310p' DECISIONS.md"`
  "under alert" → every hour is masked → that oblast has no onsets for months.
- Options: drop > 24h / drop > 7d (still 1,298 multi-day alerts) / ignore hromada level.
- Decision (me): drop intervals > 24h from the union, and print the count removed per oblast.
- Limitation: a real alert lasting over 24h is also dropped, so its onset is lost too.

## D-010 — Exactly-30-minute durations
- 68 of 299,275 rows (0.02%), 10–20 per year: oblast 48, raion 18, hromada 2.
- Decision (me): keep. The onset 
### Shell: `'cat src/evaluate.py'`
"""Splits, eligibility, test-label isolation and the metric suite (M3; reused unchanged in M4)."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from src.data import DataQualityError

GROUPS = ["overall", "kyiv_city", "frontline", "rear"]
REASONS = ["purge", "masked", "y_nan", "feature_nan"]


def split_bounds(cfg, split, allow_test=False):
    """The only way to get split dates; the test split needs allow_test=True (M4, D-021)."""
   
### Shell: `"rg -n 'base_rate|isolate_test|run_m3|test_availability|availability|before|cfg.H|check_base' scripts/run_all.py src/grid.py src/baselines.py tests/test_baselines.py; sed -n '155,225p' src/grid.py; se`
src/grid.py:146:def base_rate_table(grid, before):
src/grid.py:147:    g = grid[(grid["mask"] == 0) & (grid["t"] < before)]
src/grid.py:149:    by_q = g.groupby(q)["y"].agg(["mean", "size"]).rename(columns={"mean": "base_rate", "size": "rows"})
src/grid.py:150:    by_g = g.groupby("group")["y"].agg(["mean", "size"]).rename(columns={"mean": "base_rate", "size": "rows"})
src/grid.py:154:def check_base_rate(grid, before, ratio=0.5):
src/grid.py:155:    by_q, _, g = base_rate_table(grid, before)
src
I’ll compare each previous finding with the updated plan and builder response, then check the provisional decisions against the project rules and leakage-audit skill.
I’m applying the repository’s leakage-audit skill to the revised checks. The plan now separates label poisoning from raw-event changes and allows availability counts to change; I’m checking that this preserves the cutoff rule and validation results.
## PREVIOUS ITEMS

1. Implementation assumption/estimate — ACCEPTED: existing horizon handling supports the extension.
2. Gap boundaries — RESOLVED: masking interval and recovery endpoint remain explicit.
3. Recent-rate denominator — RESOLVED: counts, endpoints and missingness cases are specified.
4. Onset-at-t masking — RESOLVED: positive-duration and zero-duration alerts are distinguished.
5. Coverage/terminal purge — RESOLVED: observation coverage and cutoff eligibility are separately defined.
6. Fitting rules — RESOLVED: D-025’s train-only fitting and shrinkage remain explicit.
7. Reproducibility — RESOLVED: deterministic artifacts and commit-dependent metadata have separate comparisons.
8. Leakage coverage — ACCEPTED: H=3 baseline checks supplement unchanged M2 feature tests.
9. Fixture correctness — RESOLVED: hand counts, reference skill and label isolation are required.
10. D-017 checks — ACCEPTED: existing architecture and raising checks remain applicable.
11. Deadline — ACCEPTED: the previously accepted human override remains applicable.
12. M4 scope/test batch — RESOLVED: model scope remains deferred; test scoring joins the single M4 batch.
13. Pre-C label leakage — RESOLVED: §2 requires label maturity, `t+H ≤ C`, for diagnostics and isolation.
14. Overbroad acceptance test — RESOLVED: §4 separates fixed-mask label poisoning from raw-event perturbation and explicitly excludes legitimately changing availability counts/source metadata.

## PROVISIONAL DECISIONS

- `official_h3` / `reports/official_h3/`: within D-017’s named-config/output architecture; no rule change.
- New-regime analysis remaining H=1: preserves D-015’s existing scope; no rule change.
- H=3 itself changes D-000/D-013, but the plan records explicit human authorization; it is not an unauthorized provisional decision.
- Proposed rule-file entries remain human-owned, consistent with CLAUDE.md and D-026.

## NEW ISSUES

None introduced by this revision. The narrowed assertions preserve pre-test label diagnostics, fitted quantities, validation predictions and metrics while respecting D-024’s permitted availability reporting.

VERDICT: AGREE
