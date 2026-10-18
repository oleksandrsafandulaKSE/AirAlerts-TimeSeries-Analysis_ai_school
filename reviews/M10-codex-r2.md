### Shell: `"cat 'CLAUDE.md'"`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"cat 'reviews/M10-codex-r1.md'"`
### Shell: `'cat plans/M10.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and 
### Shell: `"cat 'plans/M10.md'"`
# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and day/night tables, live forecast check). The live check and the UI are
  in `plans/M11.md`; this 
### Shell: `"cat '.claude/skills/ts-leakage-audit/SKILL.md'"`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `"cat 'reviews/M10-claude-r1.md'"`
# M10 — Claude response, round 1

## Changes made
- B1 (A3 prior): PARTLY. Each variant now builds its own grid, labels, baseline and offset; the prior is the existing causal EXPANDING q(t) (`improve/features_plus.py:4,71`), so no full-train prior is used. Added variant-isolation label-mutation tests.
- B2 (§D AUC threshold): AGREE. Within-unit AUC uses ≥ 10 positives and ≥ 10 negatives per slice (D-025), exclusions listed, NaN with reason.
- A1 denominators: AGREE. Exact definitions added; grou
### Shell: `"cat 'DECISIONS.md'"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"rg --files -g 'AGENTS.md' -g 'SKILL.md'"`

### Shell: `'tail -n 75 reviews/M10-codex-r1.md'`
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
import pandas
### Shell: `'cat reviews/M10-claude-r1.md'`
# M10 — Claude response, round 1

## Changes made
- B1 (A3 prior): PARTLY. Each variant now builds its own grid, labels, baseline and offset; the prior is the existing causal EXPANDING q(t) (`improve/features_plus.py:4,71`), so no full-train prior is used. Added variant-isolation label-mutation tests.
- B2 (§D AUC threshold): AGREE. Within-unit AUC uses ≥ 10 positives and ≥ 10 negatives per slice (D-025), exclusions listed, NaN with reason.
- A1 denominators: AGREE. Exact definitions added; grou
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
   
### Shell: `'cat improve/features_plus.py'`
"""M7 extra inputs, all known at t (plans/M7.md §2.1, §3). Reads src/ read-only; never changes the headline pipeline.

Block A (labels, s <= t - H; human-approved exception): unit shrunk recent rates over 14 d and 30 d, national 14-d rate.
Offset input: r(t) = the unit's 14-d shrunk rate with the CAUSAL expanding prior q(t).
Block B (onset events up to t): national onsets (t-1h, t] and (t-3h, t]; frontline onsets (t-3h, t]; neighbours' onsets
(t-1h, t]; minutes since the last national onset.
Blo
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
### Shell: `'cat plans/M7.md'`
# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline

Status: AGREED (consensus round 5, D-026). See reviews/M7-consensus.md. Human approval in chat (2026-10-13): weekly refit,
recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).

## 0. What this milestone may and may not cl
### Shell: `"rg -n 'validation_predictions|p_headline|recent_rate|label_rates|FOLD_CUTS|def .*fold|V2' scripts/run_improve.py scripts/export_predictions.py tests/test_improve_models.py"`
tests/test_improve_models.py:81:def test_refit_windows_and_folds_inside_their_limits():
tests/test_improve_models.py:86:    for c in RI.FOLD_CUTS:
tests/test_improve_models.py:138:def test_saved_blend_weight_recomputes_from_validation_predictions():
tests/test_improve_models.py:142:    if not (imp / "validation_predictions.csv").exists():
tests/test_improve_models.py:144:    vp = pd.read_csv(imp / "validation_predictions.csv", float_precision="round_trip")
tests/test_improve_models.py:145:    w,
### Shell: `"sed -n '30,130p' scripts/run_improve.py"`
WEEKLY_CUTS = ["2026-07-27", "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31"]
ACCEPT_REL = 0.005
BLEND_GRID = [round(0.1 * i, 1) for i in range(11)]


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def eligible(df, a, b, H, feats, need_offset=True):
    """t in [a, b), t + H <= b, unmasked, label known, every listed feature (and the offset) known."""
    ok = (df["t"] >= a) & (df["t"] < b) & (df["t"] + H <= b) & (df["mask"] == 0) & df["y"].notna()
    ok &= df[feats].notn
### Shell: `"sed -n '1,105p' src/grid.py"`
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
### Shell: `"rg -n 'val_predictions|test_predictions|p_headline' scripts/run_all.py plans/M9.md tests/test_m9* extras/*.py"`
zsh:1: no matches found: tests/test_m9*

### Shell: `"sed -n '1,75p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `'nl -ba plans/M10.md'`
     1	# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables
     2	
     3	## Status and authority
     4	- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
     5	  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
     6	  hours-under-alert features, per-week and day/night tables, live forecast check). The live check
### Shell: `'cat .claude/skills/codex-plan-review/SKILL.md'`
---
name: codex-plan-review
description: Claude and Codex (a different model) iterate on a milestone PLAN (plans/<name>.md, milestone mode) or on the ROADMAP + README (roadmap mode) until they agree, without the human in the loop. Use whenever a plan is written or changed, before implementation. Max 5 rounds; escalates to the human only for rule changes or deadlock.
---

# Codex plan review — consensus loop (human not in the loop)

Claude (the builder) and Codex (the reviewer) iterate on the pla
### Shell: `"rg -n 'val_predictions|test_predictions|p_headline' scripts/run_all.py plans/M9.md extras tests"`
plans/M9.md:21:  - `reports/official/test_predictions.csv` (V0 headline `p_model`, `p_recent_rate`, `status`, `y`);
plans/M9.md:22:  - `reports/official/val_predictions.csv` (`p_headline`);
plans/M9.md:107:- **B3. The same for validation** (V0 `p_headline` vs `recent_rate`).
scripts/run_all.py:198:PREREG_KEYS = {"model.txt", "calibrator.json", "baseline_fit.json", "val_predictions.csv", "data"}
scripts/run_all.py:291:    val_pred = val[["unit", "t"] + feats].assign(y=val["y"].to_numpy(), p_raw=p
I’ll check each previous finding against the updated plan and builder’s response, then audit the provisional decisions against the project rules and leakage guidance.
Most requested fixes are explicit now. I’m verifying the expanding-prior claim in the code and checking whether the revised onset categories actually separate disappearance from timing shifts.
## PREVIOUS ITEMS

- **ACCEPTED — B1, prior leakage:** `improve/features_plus.py::label_rates` uses a causal expanding prior; the full-train-offset allegation was incorrect.
- **RESOLVED — B2, AUC:** §D requires ≥10 positives and ≥10 negatives, exclusions, and explained NaNs.
- **RESOLVED — A1, denominators:** §A1 defines unit denominators and pooled group aggregation.
- **OPEN — A2, shifted onsets:** §A2’s categories still overlap. With hromada [00:00,02:00) and raion [01:00,03:00), L0’s 00:00 onset satisfies both “disappeared” and “shifted”; L1’s 01:00 onset also satisfies “new.” The planned fixture expects “disappeared + new,” preserving the original conflation. Make disappeared versus shifted mutually exclusive, define how shifted arrivals relate to “new,” and correct the fixture and duration-median population.
- **RESOLVED — A3, uncertainty zones:** §C specifies applied bounds, endpoint predicates, and recovery times.
- **RESOLVED — M1, weight/BSS tests:** Exact finite Dataset weights and unequal-error BSS fixtures are required.
- **RESOLVED — M2, execution boundaries:** Label mutations, maturity boundaries, cutoff equality, and onset endpoints are specified.
- **RESOLVED — M3, exposure fixtures:** Expected gap-edge values, carry-in intervals, unknown ends, and capped intervals are covered.
- **RESOLVED — M4, calendar/group tests:** Explicit day/night boundaries, DST transitions, and Kyiv separation are covered.
- **RESOLVED — M5, artifacts:** Required metrics, reliability plot, leakage evidence, metadata, and proposed decision entry are listed.
- **RESOLVED — Human authorization:** §E remains disabled pending explicit human authorization.

## PROVISIONAL DECISIONS

- **Exact-instant matching:** Within existing rules; no rule change. Its category definitions remain OPEN above.
- **Pooled group rates:** Within existing rules and consistent with `evaluate.pooled_by_group`; no rule change.

## NEW ISSUES

- **Reporting baseline change:** §A3 now assigns expanding q(t) to both the offset and recent-rate reporting baseline. M7 §2 explicitly separates them; D-025 specifies train-rate shrinkage for the reporting baseline. Keep the expanding offset, but specify variant-specific reporting priors fitted on eligible fold-fit rows and frozen during scoring. Otherwise this is an unapproved baseline-rule change under D-026.

VERDICT: CHANGES REQUIRED
