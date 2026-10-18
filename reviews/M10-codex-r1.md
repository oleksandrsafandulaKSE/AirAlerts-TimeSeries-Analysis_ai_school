### Shell: `'cat plans/M10.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and day/night tables, live forecast check). The live check and the UI are
  in `plans/M11.md`; this 
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
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
### Shell: `'nl -ba plans/M10.md'`
     1	# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables
     2	
     3	## Status and authority
     4	- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
     5	  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
     6	  hours-under-alert features, per-week and day/night tables, live forecast check). The live check
### Shell: `"rg --files -g AGENTS.md -g '*leakage*' -g '*improve*' -g '*stability*' -g M7.md -g M9.md -g '*milestone*' -g '*reviewer*' -g '*protocol*' . .claude"`
./tests/test_improve_models.py
./tests/test_leakage.py
./tests/test_improve_features.py
./tests/test_improve_leakage.py
./plans/M9.md
./plans/M7.md
./scripts/run_improve.py
./reports/leakage_evidence.json
.claude/agents/reviewer.md

### Shell: `'rg --files src improve extras scripts tests .claude/skills | sort'`
.claude/skills/codex-plan-review/SKILL.md
.claude/skills/milestone-protocol/SKILL.md
.claude/skills/ts-leakage-audit/SKILL.md
extras/__init__.py
extras/corp.py
extras/data_quality.py
extras/uncertainty.py
improve/__init__.py
improve/features_plus.py
improve/live_ref.py
improve/model_plus.py
scripts/__init__.py
scripts/build_live_seed.py
scripts/build_map.py
scripts/build_site.py
scripts/export_live_model.py
scripts/export_predictions.py
scripts/run_all.py
scripts/run_extras.py
scripts/run_improv
### Shell: `'cat plans/M7.md'`
# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline

Status: AGREED (consensus round 5, D-026). See reviews/M7-consensus.md. Human approval in chat (2026-10-13): weekly refit,
recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).

## 0. What this milestone may and may not cl
### Shell: `'cat improve/models.py improve/features.py'`
cat: improve/models.py: No such file or directory
cat: improve/features.py: No such file or directory

### Shell: `'cat improve/model_plus.py'`
"""M7 models (plans/M7.md §2): the headline recipe (src.model, unchanged) and a residual model on top of the causal
recent-rate offset: p = sigmoid(offset + residual_margin)."""
import lightgbm as lgb
import numpy as np

from src import model as M
from src.data import DataQualityError

from improve.features_plus import offset_logit


def _check(df, name):
    if df["y"].isna().any():
        raise DataQualityError(f"{name}: unknown labels")
    if df["offset_rate"].isna().any():
        raise Da
### Shell: `'cat tests/test_improve_leakage.py'`
"""M7 leakage (plans/M7.md §5): every new input is unchanged when the RAW data after t is removed (starts > t dropped,
ends > t hidden); a deliberately leaky version of each block is caught at a pinned witness."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from improve import features_plus as FP
from src import config, data, grid

ROOT = Path(__file__).resolve().parents[1]
CFG = config.official()
H = CFG.H
ZONES = config.uncertainty_zones(CFG)
COLS = FP.BLOCK
### Shell: `'cat src/grid.py src/evaluate.py'`
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
### Shell: `'cat plans/M9.md'`
# M9 plan v1 — Research-driven upgrades: data-quality pin, uncertainty, CORP calibration, leakage controls

## Status and authority
- **Human, chat 2026-10-17:**
  - "I choose A for M1c". The exactly-1h check lives OUTSIDE the fingerprinted pipeline code.
  - "make a plan for implementation changes found in research". Source: `air-alert-forecasting-research/`
    (24 items) and `plans/notes/fabricated_1h_ends.md`.
- **Supersedes** `plans/M1c-exact-1h-check.md`. The agreed round-1 items from
  `r
### Shell: `"sed -n '1,110p' tests/test_leakage.py"`
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
### Shell: `'cat scripts/run_improve.py'`
"""M7: post-hoc improvement rows (plans/M7.md). The frozen headline (reports/official) is NOT changed.

    python scripts/run_improve.py            # -> reports/improve/

Order: build frames (headline code, read-only) -> M7 inputs -> feature-block acceptance on backtest folds INSIDE train
(no validation/test labels) -> V2/V3 frozen fits (early stopping on validation) -> V5 blend weight on validation ->
weekly refits V1/V4 (D-014) -> post-hoc scoring on the already-seen test (human-approved exce
### Shell: `'cat tests/test_improve_models.py'`
"""M7 models and selection (plans/M7.md §2, §2.1, §3, §5): offset reload + oracle, acceptance rule, blend on validation
only, weekly-refit windows/keys/isolation, fold boundaries, the headline code-fingerprint guard."""
import lightgbm as lgb
import numpy as np
import pandas as pd
import pytest

from improve import model_plus as MP
from scripts import run_improve as RI
from src import config, features
from src.data import DataQualityError

FE = features.FEATURES


def ts(s):
    return pd.Timest
### Shell: `'cat src/baselines.py src/config.py'`
"""The four baselines (M3). Frozen ones fit on eligible TRAIN rows only; the rolling recent rate
reads only labels of rows s <= t - H (known at t). Every function returns one value per score row."""
import numpy as np
import pandas as pd

from src.data import DataQualityError
from src.grid import unit_intervals

BASELINES = ["climatology", "recent_rate", "persistence_raw", "persistence_calibrated"]


def _naive(ts):
    return ts.dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]
### Shell: `"sed -n '150,244p' DECISIONS.md"`
  (2) Monthly retrain + evaluation with the approved, fixed pipeline: no model search, and
      metrics are committed so the history accumulates.
  (3) Yellow-regime training starts only once >= 3 months of API history exist (about mid-Dec 2026);
      until then the monthly job produces the D-015 new-regime evaluation only.
- Order: M6a (daily fetch) right after M1 or tomorrow; M6b after M5.

## D-017 — Architecture changes so M6 fits
- Builder proposed, me approved: (1) `src/regions.py` with 
### Shell: `"sed -n '1,180p' .claude/skills/milestone-protocol/SKILL.md"`
---
name: milestone-protocol
description: Mandatory work cycle for every task in this repo. Use at the start of any implementation work, any milestone, or when the human says "next step".
---

# Milestone protocol

Two planning levels (D-019).

0. ROADMAP (planning chat, once, and again only if the roadmap changes): general M1–M6 roadmap
   in `plans/ROADMAP.md` + README framing → `codex-plan-review` in roadmap mode (consensus loop) →
   show the human the consensus record → STOP. The human corr
I’ll read the four priority files, then check the relevant code and tests for contradictions, leakage risks, and gaps in the proposed checks.
I’m using the repository’s leakage-audit skill to check causality and split boundaries. I’ll also verify whether the planned tests would catch their stated failure cases.
The stability table’s AUC rule conflicts with D-025. I also found tests that could pass even if finite recency weights were ignored or BSS were calculated incorrectly. I’m checking fold priors and boundary handling before drafting the review.
## BLOCKERS

- §A3 “ITS OWN recent-rate baseline” conflicts with reusing M7’s frozen full-train prior: within historical folds, that prior contains later outcomes. Specify variant-specific priors fitted only on each fold’s eligible fit rows; test invariance to later-label changes.
- §D “units with both classes” contradicts D-025’s **≥10 positives and ≥10 negatives**. Apply the configured threshold in every slice, list exclusions, and return NaN when no unit qualifies.

## AMBIGUITIES

- §A1 “onsets per 30 days” and “share of hours under alert” lack denominators for groups. Define pooled unit-hours versus calendar hours, eligibility, and aggregation explicitly.
- §A2 “Hromada-only onsets” includes shifted onsets: removing a hromada start can expose a later oblast start. Separate disappearance from timing shifts; define which contributing raw rows enter the duration median.
- §C “intersects an uncertainty zone”: D-022 gives detected edges, while D-023/D-024 use broader applied masks. State the applied UTC intervals and exact endpoint predicates; distinguish detection from masking.

## MISSING

- Testing “h = ∞ … reproduces V2” passes if finite weights are ignored. Assert the exact finite weight vector reaches the fit Dataset. “BSS exactly 0” also passes with reversed sign or denominator; add unequal predictions with hand-calculated BSS.
- §A3/§B reuse does not test the new execution paths. Add cutoff-key and label-mutation checks: retain `t+H=C`, reject `t+H>C`, include recent-rate history through `s=t−H`; test onsets exactly at `t` and `t+H`.
- §C truncation agreement cannot establish correct gap handling. Pin expected NaN/numeric results around both zone edges and window recovery; include carry-in intervals, unknown ends, and a >24h alert spanning the window boundary.
- Testing “a DST night” can miss incorrect day/night boundaries. Assert local 06:00/22:00 transitions and repeated/missing hours; add distinct Kyiv City/Kyivska values to detect accidental pooling (D-011).
- “Done when” omits required PR-AUC/base-rate reporting, overall reliability plots (D-006/D-021), the leakage evidence table, metadata ranges/counts, and a proposed decision entry. Add these artifacts.

## QUESTIONS FOR THE HUMAN

- §E “If approved”: authorize the scoped D-021 exception for new test scoring? Also clarify CLAUDE’s blanket test-statistics prohibition against its required test reporting. Keep §E disabled until authorization is explicit.

VERDICT: CHANGES REQUIRED
