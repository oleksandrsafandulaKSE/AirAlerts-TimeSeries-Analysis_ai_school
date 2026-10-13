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
### Shell: `'cat plans/M5.md'`
# M5 plan v1 — README, figures, results site (Netlify), optional Streamlit

Status: DRAFT for the Claude–Codex consensus loop (D-026). Human instruction (2026-10-13, chat): "implement m4 and m5,
create a great visual, host on netlify, don't commit". The human is asleep: decisions inside the rules are taken by
consensus and marked PROVISIONAL.
Rules: CLAUDE.md, ROADMAP M5, D-006, D-013, D-015 (amended by D-021), D-021, D-024–D-027.

## 1. Goal
Communicate the finished results honestly: a complete
### Shell: `'cat plans/ROADMAP.md'`
# Roadmap M1–M5 (+ M6 future work), general level

What each milestone delivers and when it counts as done, not how. Step-by-step plans are
written per milestone in the implementation chat (`plans/M<n>.md`), each reviewed by Codex
before implementation (D-019). Raw material: `plans/ALL.md`, `reviews/*-codex.md`.

## The question
For each of 24 units (23 oblasts + Kyiv City), at the start of each UTC hour t: what is the
probability that a NEW air-raid alert starts in (t, t+1h], given only what is
### Shell: `"rg --files -g '*SKILL.md' -g '*leak*' -g 'AGENTS.md' -g '"'!*.ipynb'"' . /Users/oleksandrsafandula/.agents/skills /Users/oleksandrsafandula/.codex/skills"`
/Users/oleksandrsafandula/.codex/skills/hatch-pet/SKILL.md
/Users/oleksandrsafandula/.agents/skills/writing-beats/SKILL.md
/Users/oleksandrsafandula/.agents/skills/find-skills/SKILL.md
/Users/oleksandrsafandula/.agents/skills/to-questionnaire/SKILL.md
/Users/oleksandrsafandula/.agents/skills/migrate-to-shoehorn/SKILL.md
/Users/oleksandrsafandula/.agents/skills/improve-codebase-architecture/SKILL.md
/Users/oleksandrsafandula/.agents/skills/grilling/SKILL.md
/Users/oleksandrsafandula/.agents/skill
### Shell: `"sed -n '1,155p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"rg --files --hidden -g '"'!data/**'"' -g '"'!.git/**'"' -g '"'!.venv/**'"' -g '"'!site/**'"' -g '"'!*.ipynb'"' . | rg 'skill|AGENTS|src/|tests/|scripts/|reports/'"`
./src/data.py
./src/evaluate.py
./src/model.py
./src/features.py
./src/__init__.py
./src/regions.py
./src/config.py
./src/grid.py
./src/baselines.py
./reports/official/m1_checks.json
./reports/official/metrics_validation.json
./reports/official/reliability_validation.png
./reports/official/preregistration.json
./reports/official/base_rate_by_group.csv
./reports/official/calibrator.json
./reports/official/m2_checks.json
./reports/official/metrics_validation.csv
./reports/official/val_predictions.
### Shell: `'cat src/config.py'`
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
### Shell: `'cat requirements.txt; cat reports/official/preregistration.json'`
# python==3.13.5  (see .python-version; run_all.py raises on another minor version)
pandas==3.0.6
numpy==2.5.4
scikit-learn==1.9.1
lightgbm==4.7.0
matplotlib==3.11.2
pytest==9.1.1
requests==2.34.2
streamlit==1.65.0
{
  "H": "1h",
  "baselines": [
    "climatology",
    "recent_rate",
    "persistence_raw",
    "persistence_calibrated"
  ],
  "best_iteration": 208,
  "calibration_decision": "none",
  "calibration_rule": "Platt on validation iff validation ECE > 0.02",
  "code_fingerprint": "ecc35
### Shell: `'cat src/grid.py'`
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
### Shell: `"rg -n 'fingerprint|sha256|score_final_test|reproduc|marker|preregistration|reliability|before_after|h3|stage' src/model.py scripts/run_all.py tests/test_final_test.py tests/test_new_regime.py"`
tests/test_new_regime.py:60:def test_frozen_files_must_match_preregistration(tmp_path):
tests/test_new_regime.py:62:        run_all._verify_prereg(tmp_path, tmp_path / "x.csv")              # no preregistration
tests/test_final_test.py:1:"""The single final-test scoring (M4 plan §4): joint pre-registration, hash binding, access marker, guard."""
tests/test_final_test.py:22:    configs = {"official": c1, "official_h3": dataclasses.replace(c1, name="official_h3", H=pd.Timedelta(hours=3))}
tests/te
### Shell: `'nl -ba plans/M5.md'`
     1	# M5 plan v1 — README, figures, results site (Netlify), optional Streamlit
     2	
     3	Status: DRAFT for the Claude–Codex consensus loop (D-026). Human instruction (2026-10-13, chat): "implement m4 and m5,
     4	create a great visual, host on netlify, don't commit". The human is asleep: decisions inside the rules are taken by
     5	consensus and marked PROVISIONAL.
     6	Rules: CLAUDE.md, ROADMAP M5, D-006, D-013, D-015 (amended by D-021), D-021, D-024–D-027.
     7	
     8	## 1. Go
### Shell: `"sed -n '320,505p' scripts/run_all.py"`
# ---------------- M4: the single final-test scoring (stage final-test) ----------------

def _verify_prereg(run_dir, data_path, check_code=True):
    pr_path = run_dir / "preregistration.json"
    if not pr_path.exists():
        raise data.DataQualityError(f"{pr_path} missing: run the fit stage for {run_dir.name} first")
    pr = json.loads(pr_path.read_text())
    for name, h in pr["sha256"].items():
        actual = data.file_sha256(data_path) if name == "data" else model.sha256_file(run_dir
### Shell: `'cat README.md; cat .claude/skills/milestone-protocol/SKILL.md'`
# Air-raid alert onset forecasting — Ukraine

> For each oblast and each hour: the probability that a NEW air-raid alert starts within the
> next hour, using only what is known at that moment. Tested once on the last 6 weeks of
> official data against simple baselines, with a test that proves no future information is used.

## Problem framing
- **Why "a new alert starts" and not "an alert is active":** being under alert at t almost
  guarantees being under alert at t+1h, so "active" targets rewa
### Shell: `"sed -n '1,250p' tests/test_leakage.py"`
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
   
I’ll read the plan, project rules, decision log, roadmap, and leakage-audit skill, then check the existing code and tests for claims that affect the review.
I found scope conflicts: D-012 requires Streamlit, but the plan makes it optional; the roadmap assigns figure generation to `run_all.py`, but the plan adds plots in `build_site.py`. I’ll apply the leakage-audit skill and check the provenance tests and boundary rules next.
## BLOCKERS

- L65, “not required”: contradicts D-012 and ROADMAP M5, which require Streamlit; `milestone-protocol` calls it optional. Make Streamlit mandatory unless the human explicitly changes scope.
- L48, “made by `scripts/build_site.py`”: ROADMAP requires figures generated by `run_all.py`. Copy existing plots, or obtain approval for this change before freezing the pipeline.
- L59, “string match”: swapped horizons, groups, predictors, or metrics would still pass if their numbers occur elsewhere. Compare each cell against its exact source key; require swapped-cell mutations to fail. Extend checks beyond results tables to numerical prose.

## AMBIGUITIES

- L41, “target…purge”: specify merged-unit onsets, exclusion at t, inclusion at t+H, and keeping rows with t+H = cutoff (D-022–D-025). State recent-rate history as [t−14d, t−H], not merely “last 14 days.”
- L42, “gap”: distinguish detected [29 Aug 05:00, 2 Sep 13:00) from the approved masking envelope and extended feature uncertainty (D-022–D-024). Display horizon-specific exclusions; nominal “six weeks” conceals substantial missing coverage.
- L34, “low-n flags”: define unavailable metrics as JSON null and display their reasons, AUC units used/excluded, and saved low-n flags (D-025). Never turn undefined skill into “not better.”
- D-025 specifies persistence calibrated by time-since-end bins; CLAUDE.md specifies calibration conditional on state. Document the implemented bins and reconcile the stale rule.
- L27, “works offline”: specify how `data.json` loads under file URLs and test that mode explicitly. Embedding the payload removes dependence on browser file-fetch permissions.

## MISSING

- L55, “no-leakage guarantee”: the leakage-audit skill requires a check/PASS–FAIL/evidence table before reporting metrics. Link actual truncation and negative-control evidence, including DST, gap edges, unknown future ends, and >24h standing alerts; describe tested coverage rather than claiming universal proof.
- L32, “Kyiv City”: add explicit presentation checks that Kyivska remains rear and separate from Kyiv City (D-011); value membership cannot detect mislabelling.
- L83, “Done when”: add CLAUDE.md’s milestone summary, proposed decision entry, and D-026 consensus record with provisional decisions.

## QUESTIONS FOR THE HUMAN

- L70, “human deploys”: does a prepared folder satisfy “host on Netlify”? Define completion as a verified deployed URL, or explicitly accept deployment as outstanding; the private preview does not resolve this.

VERDICT: CHANGES REQUIRED
