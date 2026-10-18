### Shell: `"pwd; rg --files -g 'AGENTS.md' -g 'SKILL.md' -g 'M6c-1*' -g 'CLAUDE.md' -g 'DECISIONS.md' -g 'M6-definition.md' -g 'PROPOSED-DECISIONS-M6.md' -g '"'!data/**'"' -g '"'!artifacts/**'"'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/.claude/worktrees/m6c1-typed-model-eace7a
DECISIONS.md
reviews/M6c-1-codex-r2.log
reviews/M6c-1-codex-r1.log
reviews/M6c-1-claude-r1.md
reviews/PROPOSED-DECISIONS-M6.md
reviews/M6c-1-codex-r1.md
CLAUDE.md
plans/M6c-1.md
plans/M6-definition.md

### Shell: `'cat plans/M6c-1.md reviews/M6c-1-codex-r1.md reviews/M6c-1-claude-r1.md'`
# M6c-1 — first new-regime models: any / yellow / red onset, with the blend and the chart

Status: PLAN (Claude–Codex consensus loop, D-026). Started by the main session on the human's M6 definition
(`plans/M6-definition.md`, 2026-10-17). All results are EXPLORATORY (one test week).

Rules used (the human's chat decisions of 2026-10-17, proposed as D-033…D-039 in `reviews/PROPOSED-DECISIONS-M6.md`;
they amend CLAUDE.md and are cited, NOT re-decided here):
- D-033: typed targets (yellow onset, re
### Shell: `'cat CLAUDE.md DECISIONS.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'cat .claude/skills/ts-leakage-audit/SKILL.md plans/M6-definition.md reviews/PROPOSED-DECISIONS-M6.md'`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `'for dir in / /Users /Users/oleksandrsafandula /Users/oleksandrsafandula/Desktop /Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school /Users/oleksandrsafandula/Desktop/AirAlerts-T`

### Shell: `'cat src/features.py src/model.py'`
"""Features known at t (M2). Built only from the D-020 merged unit intervals/onsets of grid.py."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError
from src.grid import _covered, check_units, unit_intervals

WINDOWS = {"onsets_last_24h": pd.Timedelta(hours=24), "onsets_last_7d": pd.Timedelta(days=7)}

# model feature list; active_at_t stays in the frame for audit only (constant 0 on unmasked rows)
FEATURES = ["minutes_since_last_start", "minut
### Shell: `'cat src/grid.py src/config.py'`
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
### Shell: `'cat src/baselines.py src/evaluate.py'`
"""The four baselines (M3). Frozen ones fit on eligible TRAIN rows only; the rolling recent rate
reads only labels of rows s <= t - H (known at t). Every function returns one value per score row."""
import numpy as np
import pandas as pd

from src.data import DataQualityError
from src.grid import unit_intervals

BASELINES = ["climatology", "recent_rate", "persistence_raw", "persistence_calibrated"]


def _naive(ts):
    return ts.dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]
### Shell: `"rg -n 'commit|fingerprint|D-017|script|test_access|def as_reconstructed_at|def read_datastore|def read_log|nominal_window' tests/test_improve_models.py plans/M7.md collect/api_collector.py plans/M6c-`
plans/M7.md:25:`src/*.py` and `scripts/run_all.py` are frozen by the pre-registered code fingerprint (D-028). M7 code lives in a new
plans/M7.md:26:package `improve/` (+ `scripts/run_improve.py`, `tests/test_improve_*.py`) that imports `src` read-only. Outputs go to
plans/M7.md:27:`reports/improve/`. A test asserts that the code fingerprint still matches both pre-registrations and that an exact
plans/M7.md:112:(both branches), fingerprint/reproduction guard, README/site generated blocks verified
### Shell: `"sed -n '1,160p' src/grid.py"`
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
### Shell: `"sed -n '140,195p' DECISIONS.md; sed -n '1,160p' src/config.py; sed -n '1,165p' tests/test_new_regime.py"`

## D-016 — M6: automated data workflow (no AI agents)
- **Updated (me, 2026-10-12):** approved as FUTURE WORK, not tonight's scope. The yellow-regime model needs my explicit approval.
- Context (me): keep collecting new-regime data and retrain/evaluate every month automatically.
- Builder found: one full API dump is 7 MB (about 210 MB/month if dumped daily, too big for git);
  `month_ago` keeps only ~30 days → a monthly fetch would lose data whenever a run fails;
  the API docs list 403 "unavai
### Shell: `"sed -n '1,135p' src/features.py; sed -n '565,605p' collect/api_collector.py"`
"""Features known at t (M2). Built only from the D-020 merged unit intervals/onsets of grid.py."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError
from src.grid import _covered, check_units, unit_intervals

WINDOWS = {"onsets_last_24h": pd.Timedelta(hours=24), "onsets_last_7d": pd.Timedelta(days=7)}

# model feature list; active_at_t stays in the frame for audit only (constant 0 on unmasked rows)
FEATURES = ["minutes_since_last_start", "minut
### Shell: `"rg --files .claude/skills; rg -n 'def api_alerts|def to_api_records' src/data.py collect/api_collector.py; ls -l /Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/.venv/b`
.claude/skills/ts-leakage-audit/SKILL.md
.claude/skills/milestone-protocol/SKILL.md
.claude/skills/codex-plan-review/SKILL.md
collect/api_collector.py:586:def to_api_records(rows):
src/data.py:137:def api_alerts(records, manifest, cfg, stats=None, require_all_units=True):
lrwxr-xr-x@ 1 oleksandrsafandula  staff  10 Oct 12 22:20 /Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/.venv/bin/python -> python3.13

### Shell: `"sed -n '130,220p' src/data.py; sed -n '195,210p' collect/api_collector.py; sed -n '1,3p' datastore/alerts_in_ua.csv; sed -n '1,3p' reports/collect/pull_log.csv; nl -ba plans/M6c-1.md | sed -n '140,16`
            continue
        payload = json.loads((dump_dir / f"uid_{m['uid']}.json").read_text())
        for a in payload["alerts"]:
            records.append({**a, "_file_uid": m["uid"]})
    return records, manifest


def api_alerts(records, manifest, cfg, stats=None, require_all_units=True):
    """Raw API records -> shared alert format. Dedup by id keeping the latest updated_at; open alerts are KEPT
    (finished_at = NaT = end unknown; the D-020 cap handles them, D-027). Checks raise."""
I’ll check each previous finding against the updated plan and governing decisions, then review the provisional choices and any new issues.
I’m applying the repository’s leakage-audit skill. The updated plan addresses the three original statistical blockers. I’m checking the remaining protocol questions, especially the D-017 interface exception and the order of test reservation and frame construction.
## PREVIOUS ITEMS

- **B1 — RESOLVED:** §6 counts distinct merged onset events, including explicit H=3 deduplication.
- **B2 — RESOLVED:** §6 defines ANY-rate predictions on RED scoring rows and common-support share counts; the approximation is disclosed.
- **B3 — RESOLVED:** Validation blend results are retrospective diagnostics; test results use frozen fitted components and causal rolling updates.
- **A1 — RESOLVED:** §7 specifies a split-keyed, exclusive reservation covering all six models, with interrupted runs blocked.
- **A2 — RESOLVED:** Pre-registration now hashes the datastore, coverage inputs and collector implementation.
- **M1 — ACCEPTED:** Typed boundary witnesses and negative controls are added; existing official-gap tests plus synthetic API holes appropriately cover the separate sources.
- **M2 — RESOLVED:** The plan specifies the project interpreter and a read-only data-cache symlink.
- **M3 — RESOLVED:** Audit evidence, run metadata and the reviewer/fix cycle are specified.
- **Q/D-017 — OPEN:** §8c explicitly introduces an exception to CLAUDE.md Architecture #3/#5, yet defers ratification until after implementation. D-026 requires rule changes to return to the human. Fingerprint constraints and M6a/M7 precedents justify the proposal; they do not authorize this exception. Obtain the narrow amendment before implementation.

## PROVISIONAL DECISIONS

All seven listed choices were checked against the rules, including the authorized 2026-10-17 amendments:

1. Out-of-sample blend window and distinct-onset counting: within scope.
2. Common-support red-share baseline: within scope.
3. National masking of recorded holes: conservative implementation of missing-data treatment.
4. Existing groups, AUC thresholds and low-n flags: consistent.
5. Retrospective validation blend: appropriate disclosure.
6. Exclusive split reservation: consistent with test-once evaluation.
7. `air_raid` filtering: preserves the existing scope and pending artillery decision.

The additional D-017 exception is a **rule change**, not a provisional implementation choice.

## NEW ISSUES

- **Unauthorized commit:** §8b adds “Commit on the branch.” D-026 explicitly states “no commits by Claude”; the M6 amendments do not override that restriction. Remove the instruction or obtain explicit human authorization.

VERDICT: CHANGES REQUIRED
