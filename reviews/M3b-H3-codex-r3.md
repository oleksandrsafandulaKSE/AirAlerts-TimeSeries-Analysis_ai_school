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
### Shell: `'cat plans/M3b-H3.md'`
# M3b plan v1 — Additional horizon H = 3 (extra results row, never the headline)

Status: v1.2 after consensus round 2 (D-026 loop). Requested and approved by the human (2026-10-13):
"add additional horizon h=3".
Amends D-000 (H = 1 only) and D-013 (multiple horizons skipped). The headline stays H = 1.

## 1. Goal
Run the existing M1–M3 pipeline with H = 3 hours as a second, separate run:
`python scripts/run_all.py --config official_h3` → `reports/official_h3/` with the same files as
`reports/of
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `'cat reviews/M3b-H3-codex-r2.md'`
### Shell: `"pwd && rg --files -g AGENTS.md -g '*SKILL.md' -g 'M3b-H3*' -g 'CLAUDE.md' -g 'DECISIONS.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
plans/M3b-H3.md
DECISIONS.md
CLAUDE.md
reviews/M3b-H3-codex-r1.md
reviews/M3b-H3-codex.md
reviews/M3b-H3-claude-r1.md
reviews/M3b-H3-codex-r2.log
reviews/M3b-H3-codex-r1.log

### Shell: `'cat plans/M3b-H3.md reviews/M3b-H3-codex-r1.md reviews/M3b-H3-claude-r1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-au
### Shell: `'cat reviews/M3b-H3-claude-r2.md'`
# Claude response, round 2 — plans/M3b-H3.md

## Changes made
- NEW BLOCKER (pre-C labels at H = 3) — AGREE. Verified: `grid.base_rate_table` filters `t < before` (src/grid.py) and `evaluate.isolate_test_labels` blanks `t >= test_start`; at H = 3 rows C−2h and C−1h keep labels whose window (t, t+3h] reaches past C. Plan §2 now requires `t + H ≤ C` for every label read before M4: (a) base-rate table/check filter `t + H ≤ C`; (b) `isolate_test_labels(frame, C, H)` blanks y where `t + H > C`. At H 
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
### Shell: `"rg --files -g AGENTS.md -g '*H3*' -g '*leak*' -g '*split*' -g '*baseline*'"`
src/baselines.py
reviews/M3b-H3-codex-r1.md
reviews/M3b-H3-codex.md
reviews/M3b-H3-claude-r2.md
reviews/M3b-H3-claude-r1.md
reviews/M3b-H3-codex-r1.log
reviews/M3b-H3-codex-r2.md
reviews/M3b-H3-codex-r2.log
reviews/M3b-H3-codex-r3.log
tests/test_baselines.py
tests/test_leakage.py
plans/M3b-H3.md

### Shell: `'tail -n 45 reviews/M3b-H3-codex-r2.md'`
    98	    for d0, d1 in detected:
    99	        if not any(a0 <= d0 and d1 <= a1 for a0, a1 in approved):
   100	            raise DataQualityError(f"unapproved gap detected: [{d0}, {d1})")
   101	    for a0, a1 in ap
### Shell: `'rg --files -g AGENTS.md /Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school /Users/oleksandrsafandula/.agents 2>/dev/null'`

### Shell: `".venv/bin/python -B - <<'PY'
import pandas as pd
from src import grid
C = pd.Timestamp('2026-07-27', tz='UT
### Shell: `'cat reviews/M3b-H3-claude-r2.md'`
# Claude response, round 2 — plans/M3b-H3.md

## Changes made
- NEW BLOCKER (pre-C labels at H = 3) — AGREE. Verified: `grid.base_rate_table` filters `t < before` (src/grid.py) and `evaluate.isolate_test_labels` blanks `t >= test_start`; at H = 3 rows C−2h and C−1h keep labels whose window (t, t+3h] reaches past C. Plan §2 now requires `t + H ≤ C` for every label read before M4: (a) base-rate table/check filter `t + H ≤ C`; (b) `isolate_test_labels(frame, C, H)` blanks y where `t + H > C`. At H 
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
### Shell: `'cat src/grid.py src/evaluate.py scripts/run_all.py'`
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
### Shell: `"sed -n '106,180p' src/grid.py"`
def gap_mask_for(t, H, approved_gaps, post_gap):
    m = np.zeros(len(t), dtype=bool)
    for g0, g1 in approved_gaps:
        g0, g1, pg = _naive(g0), _naive(g1), np.timedelta64(post_gap)
        m |= (t < g1) & (t + H >= g0)          # label window (t, t+H] touches [g0, g1)
        m |= (t >= g1) & (t < g1 + pg)        # post-gap: unrecorded alerts may still count (D-020)
    return m


def build_grid(alerts, grid_start, grid_end, H=pd.Timedelta(hours=1), target_levels="any",
               ca
### Shell: `"sed -n '1,52p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"sed -n '1,55p' src/evaluate.py"`
"""Splits, eligibility, test-label isolation and the metric suite (M3; reused unchanged in M4)."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from src.data import DataQualityError

GROUPS = ["overall", "kyiv_city", "frontline", "rear"]
REASONS = ["purge", "masked", "y_nan", "feature_nan"]


def split_bounds(cfg, split, allow_test=False):
    """The only way to get split dates; the test split needs allow_test=True (M4, D-021)."""
   
### Shell: `"sed -n '125,165p' plans/M3.md"`
- Calibrated persistence: bin edges (59.9 → bin 0, 60 → bin 1, 720 → bin 3) and the shrinkage formula by hand;
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

from scripts import run_all
import pandas as pd

from src import config, data, features, grid, regions

HEADER = "oblast,raion,hromada,level,started_at,finished_at,source\n"


def fixture(tmp_path, dup=False):
    rows = []
    for d in range(1, 29):
        for i, v in enumerate(regions.UNITS.values()):
            rows.append(f"{v['official_name']},,,oblast,2024-02-{d:02d} {i % 24:02d}:10:00+00:00,"
                        f"2024-02-{d:02d} {i % 2
### Shell: `".venv/bin/python -B -c 'import pandas as pd; from src import grid,evaluate; C=pd.Timestamp(\"2026-07-27\",tz=\"UTC\"); H=pd.Timedelta(hours=3); a=pd.DataFrame({\"unit\":[\"kyiv_city\"],\"started_at\"`
[{'in_range': 6, 'available': 4, 'excluded_overlapping': {'purge': 2, 'masked': 0, 'feature_nan': 0}, 'excluded_exclusive': {'purge': 2, 'masked': 0, 'feature_nan': 0}}, {'in_range': 6, 'available': 3, 'excluded_overlapping': {'purge': 2, 'masked': 1, 'feature_nan': 0}, 'excluded_exclusive': {'purge': 2, 'masked': 1, 'feature_nan': 0}}]

I’ll read the updated plan, prior review, builder’s response, and governing rules first, then check the disputed and provisional decisions against the code where needed.
The cutoff fix handles the prior leakage blocker, and the two provisional choices remain within the existing rules. I’m checking one new concern: the proposed “every M1/M3 output unchanged” test may also require invariance of test-period availability counts, which can legitimately change when an alert is added.
## PREVIOUS ITEMS

1. Implementation assumption/estimate — ACCEPTED: existing horizon handling supports the proposed extension.
2. Gap boundaries — RESOLVED: interval and recovery endpoint are explicit.
3. Recent-rate denominator — RESOLVED: counts, missingness and endpoints are specified.
4. Onset-at-t masking — RESOLVED: positive-duration and zero-duration cases are distinguished.
5. Coverage/terminal purge — RESOLVED: coverage and cutoff eligibility are separately defined.
6. Fitting rules — RESOLVED: D-025’s train-only fitting and shrinkage remain explicit.
7. Reproducibility — RESOLVED: deterministic artifacts and metadata comparisons are distinguished.
8. Leakage coverage — ACCEPTED: H=3 baseline checks supplement unchanged M2 feature coverage.
9. Fixture correctness — RESOLVED: hand counts, skill identity and isolation are required.
10. D-017 checks — ACCEPTED: existing architecture and raising checks remain applicable.
11. Deadline — ACCEPTED: M3 §9 records the human’s quality-bar override.
12. M4 scope/test batch — RESOLVED: scope remains deferred; scoring joins the single M4 batch.
13. Pre-C label leakage — RESOLVED: §2 requires `t+H ≤ C` for base-rate diagnostics and label isolation.

## PROVISIONAL DECISIONS

- `official_h3` / `reports/official_h3/` stays within D-017’s named-config architecture.
- Keeping new-regime analysis at H=1 preserves D-015’s existing scope.
- Neither provisional decision changes a rule. H=3 itself changes D-000/D-013 under the plan’s recorded human approval; rule-file updates remain human-owned under D-026.

## NEW ISSUES

- **Acceptance-test blocker:** §4 and the response require a synthetic onset at C+1h to leave *every M1/M3 output* unchanged. That assertion is overbroad for positive-duration alerts: D-024 explicitly permits test availability counts, and `run_m3` exports them in `m3_checks.json`. A synthetic 40-minute alert at C+1h changed `availability` from four available rows to three, with masked rows increasing from zero to one—without reading labels. Require invariance of pre-test label diagnostics, fitted quantities, validation predictions and metrics; allow test availability counts and source metadata to reflect changed raw data. Separately poison inaccessible labels while holding masks/features fixed to verify isolation.

VERDICT: CHANGES REQUIRED
