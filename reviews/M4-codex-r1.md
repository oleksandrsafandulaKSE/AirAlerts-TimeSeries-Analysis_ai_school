### Shell: `'cat plans/M4.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M4 plan v1 — Models (H = 1, H = 3) + the single final-test scoring + new-regime section

Status: DRAFT for the Claude–Codex consensus loop (D-026). Human decisions already given in chat
(2026-10-13): one model per horizon ("option 1") → train an H = 1 model (headline) and an H = 3 model
(extra results row); the new-regime section stays H = 1 (M3b provisional decision).
Rules: CLAUDE.md, D-005, D-006, D-007, D-011, D-013, D-015 (amended by D-021), D-017, D-020–D-025, M3b plan.

## 1. Goal
1. Tr
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `'nl -ba plans/M4.md'`
     1	# M4 plan v1 — Models (H = 1, H = 3) + the single final-test scoring + new-regime section
     2	
     3	Status: DRAFT for the Claude–Codex consensus loop (D-026). Human decisions already given in chat
     4	(2026-10-13): one model per horizon ("option 1") → train an H = 1 model (headline) and an H = 3 model
     5	(extra results row); the new-regime section stays H = 1 (M3b provisional decision).
     6	Rules: CLAUDE.md, D-005, D-006, D-007, D-011, D-013, D-015 (amended by D-021), D-017
### Shell: `'nl -ba DECISIONS.md'`
     1	# Decisions and challenge log
     2	
     3	Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
     4	Mark the source honestly (builder / reviewer subagent / supervisor chat / me).
     5	
     6	---
     7	
     8	## D-000 — Forecast region scope and horizon
     9	- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
    10	- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
    11
### Shell: `"sed -n '96,244p' DECISIONS.md"`
## D-013 — Best practices adopted from related work
- Source: builder's web research (about a dozen public repos plus arXiv:2411.14625), checked
  against our data where possible. Metrics in other repos are self-reported, not rerun.
- Verified by builder: 113,845 of 299,275 official rows are exact duplicates
  (`sort -u` → 185,430 unique). Recording gap: 29 Aug 88 onsets, 30 Aug–1 Sep 0 rows,
  rows resume 2 Sep (normal days have 350–600). D-009 and D-010 counts were made BEFORE
  deduplication 
### Shell: `"rg --files -g AGENTS.md -g '*.py' src tests scripts; cat requirements.txt; cat plans/M3b.md"`
tests/test_run_all.py
tests/test_data.py
tests/test_config.py
tests/test_baselines.py
tests/test_evaluate.py
tests/test_regions.py
tests/test_leakage.py
tests/test_features.py
tests/test_grid.py
tests/conftest.py
src/regions.py
src/config.py
src/grid.py
src/baselines.py
src/features.py
src/__init__.py
src/evaluate.py
src/data.py
scripts/__init__.py
scripts/run_all.py
# python==3.13.5  (see .python-version; run_all.py raises on another minor version)
pandas==3.0.6
numpy==2.5.4
scikit-learn==1.9.1
### Shell: `'cat scripts/run_all.py src/baselines.py'`
"""Pipeline entry point: python scripts/run_all.py --config official [--as-of DATE]. Stages M1-M3.
M3 scores baselines on VALIDATION only; the final test is scored once, in M4 (D-021)."""
import argparse
import json
import platform
import subprocess
import sys
from importlib.metadata import version

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import baselines, config as config_mod, data, evalu
### Shell: `'cat tests/test_leakage.py'`
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
### Shell: `'cat src/config.py src/evaluate.py'`
"""Named run configs (D-017 #3). No dates are hard-coded anywhere else."""
from dataclasses import dataclass, field, replace

import pandas as pd


def _ts(s):
    return pd.Timestamp(s, tz="UTC")


@dataclass(frozen=True)
class RunConfig:
    name: str
    source: str
    grid_start: pd.Timestamp
    grid_end: pd.Timestamp            # exclusive
    coverage_end: pd.Timestamp        # last moment the source is known to be recording
    train: tuple                      # half-open [start, end) 
### Shell: `'cat src/data.py src/grid.py'`
"""Load sources into the one shared alert format (D-017 #2). Data checks RAISE (D-017 #6)."""
import hashlib
from pathlib import Path

import pandas as pd
import requests

from src import regions

SHARED_COLUMNS = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
OFFICIAL_COLUMNS = ["oblast", "raion", "hromada", "level", "started_at", "finished_at", "source"]


class DataQualityError(RuntimeError):
    pass


def file_sha256(path):
    return hashlib.sha256(Path
### Shell: `'cat scripts/run_all.py'`
"""Pipeline entry point: python scripts/run_all.py --config official [--as-of DATE]. Stages M1-M3.
M3 scores baselines on VALIDATION only; the final test is scored once, in M4 (D-021)."""
import argparse
import json
import platform
import subprocess
import sys
from importlib.metadata import version

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import baselines, config as config_mod, data, evalu
### Shell: `"sed -n '55,240p' src/grid.py"`
    for unit, g in a.groupby("unit"):
        s = g["started_at"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")
        e = effective_end(g, cap).dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")
        ms, me = merge_intervals(s, e)
        zero = s[e <= s]  # zero-duration alerts: onset kept, mask nothing (human decision Q10)
        extra = zero[~_covered(zero, ms, me)] if len(zero) else zero
        onsets = np.unique(np.concatenate([ms, extra]))
  
### Shell: `"rg -n 'api_uid|kyiv|run_meta|gap|purge|DST|cutoff|cut.off|boundary' src/regions.py tests/test_grid.py tests/test_evaluate.py tests/test_features.py tests/test_run_all.py; rg --files plans .claude/ski`
tests/test_evaluate.py:21:def test_eligibility_purge_and_reasons():
tests/test_evaluate.py:27:    assert not ok3[(t == C - pd.Timedelta(hours=2)) | (t == C - H1)].any()  # purged
tests/test_evaluate.py:35:    assert c["excluded_exclusive"] == {"purge": 0, "masked": 2, "y_nan": 1, "feature_nan": 1}
tests/test_evaluate.py:36:    assert c["excluded_overlapping"] == {"purge": 0, "masked": 2, "y_nan": 1, "feature_nan": 2}
tests/test_evaluate.py:38:    assert c3["excluded_exclusive"]["purge"] == 2
tes
### Shell: `'cat plans/M3b-H3.md; cat .claude/skills/codex-plan-review/SKILL.md; cat .claude/skills/milestone-protocol/SKILL.md'`
# M3b plan v1 — Additional horizon H = 3 (extra results row, never the headline)

Status: v1.3 after consensus round 3 (D-026 loop). Requested and approved by the human (2026-10-13):
"add additional horizon h=3".
Amends D-000 (H = 1 only) and D-013 (multiple horizons skipped). The headline stays H = 1.

## 1. Goal
Run the existing M1–M3 pipeline with H = 3 hours as a second, separate run:
`python scripts/run_all.py --config official_h3` → `reports/official_h3/` with the same files as
`reports/of
### Shell: `"sed -n '1,180p' src/features.py; sed -n '1,85p' tests/test_evaluate.py; sed -n '1,88p' src/regions.py"`
"""Features known at t (M2). Built only from the D-020 merged unit intervals/onsets of grid.py."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError
from src.grid import _covered, check_units, unit_intervals

WINDOWS = {"onsets_last_24h": pd.Timedelta(hours=24), "onsets_last_7d": pd.Timedelta(days=7)}

# model feature list; active_at_t stays in the frame for audit only (constant 0 on unmasked rows)
FEATURES = ["minutes_since_last_start", "minut
I’ll read the four priority files, then check relevant code and tests for contradictions, leakage risks, and tests that could miss their target bugs.
I’m applying the repository’s leakage-audit skill, particularly its truncation test for alert end times that were unknown at forecast time.
Two substantive risks stand out: filtering to closed API alerts uses future closure status, and the transfer stage doesn’t explicitly reload the fitted calibrator. I’m checking whether the proposed guard protects both horizons before either test result is exposed.
## BLOCKERS

- §5.1 “closed alerts only” conditions historical inputs on future closure status. Dropping the 41 open alerts can erase onsets, masks and spatial state, including standing alerts’ first 24h. Retain known starts with unknown ends capped causally; this requires resolving CLAUDE.md’s merge rule against D-020.
- §4 “reports/<run>/preregistration.json” permits scoring H=1 before freezing H=3, contrary to M3b’s single scoring requirement and D-021. Freeze both models, calibrators and baseline tables before exposing either horizon’s results.
- §4 “SAME sha256 → allowed” checks the manifest, not whether scoring actually uses its artifacts. Verify model/table/calibrator hashes and bind data and scoring-code fingerprints; record test access before reading labels so a crash cannot reopen selection.
- §5.3 “loaded from … model.txt” omits Platt scaling. Transfer must reload the complete headline predictor, including coefficients and logit transformation, and reproduce its official predictions before API scoring.

## AMBIGUITIES

- §3 “logit(p) … no regularisation”: clipping, intercept, solver, convergence and single-class/separation behavior are unspecified. Fix these choices; fail explicitly when fitting is undefined. Clarify “both raw and calibrated … either way” when no calibrator exists.
- §5.3 “onsets per 30 days and share”: specify merged onsets (D-023), duration intersections, denominators and group aggregation. Exclude unknown API warm-up exposure consistently; do not count it as quiet time.
- §5.1 “one location_oblast” accepts a consistently misfiled oblast. Validate identity against the requested UID through regions.py; explicitly test swapped Kyiv City (31) and Kyivska (14), preserving D-011 groups.

## MISSING

- §7 “flipping validation labels changes best_iteration” also passes when validation contaminates training; “grep-style” guards miss direct date access. Assert exact fit/validation keys and behavioral label isolation, including purged rows and equality boundaries for both horizons.
- §7 “4 real times” does not audit the API loader. Add loader-to-predictor truncation checks hiding unknown ends, including >24h alerts; retain DST, recording-gap and rolling-window boundary checks with negative controls.
- §9 lists only three API CSVs. Explicitly require D-017’s metrics.json, plots and run_meta.json, plus CLAUDE.md’s shapes/date ranges/base rates, standing/30-minute diagnostics and proposed decision entry.

## QUESTIONS FOR THE HUMAN

- D-022 names detected gap edges; D-023/D-024 and existing configuration use broader conservative exclusions. Confirm that distinction and reconcile the recorded 145-hour count.
- CLAUDE.md requires closed-only API merging while D-020 requires causal starts. Approve retaining open alerts with unknown ends, or define defensible censoring.

VERDICT: CHANGES REQUIRED
