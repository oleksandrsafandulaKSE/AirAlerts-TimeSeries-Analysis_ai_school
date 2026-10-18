### Shell: `'cat plans/M1c-exact-1h-check.md plans/notes/fabricated_1h_ends.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M1c — exactly-1-hour durations: count, print, raising check

Human decision (2026-10-17, chat): **Option 1** from `plans/notes/fabricated_1h_ends.md`. Keep the alerts as they
are, document the counts in the README and the M1 printing, and add a raising check on the exactly-3600 s count.
No change to the target, mask, features, models, the evaluation protocol or any reported metric.

## Goal
Make the parser artefact (a missing all-clear is closed at `started_at + 1h`) visible and pinned. If the
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
### Shell: `'nl -ba plans/M1c-exact-1h-check.md;'`
     1	# M1c — exactly-1-hour durations: count, print, raising check
     2	
     3	Human decision (2026-10-17, chat): **Option 1** from `plans/notes/fabricated_1h_ends.md`. Keep the alerts as they
     4	are, document the counts in the README and the M1 printing, and add a raising check on the exactly-3600 s count.
     5	No change to the target, mask, features, models, the evaluation protocol or any reported metric.
     6	
     7	## Goal
     8	Make the parser artefact (a missing all-clear is
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `"rg --files -g AGENTS.md -g '*leakage*' -g '*data*' -g '*config*' -g '*run_all*' -g '*review*' src tests scripts .claude plans reviews"`
src/data.py
src/config.py
tests/test_run_all.py
tests/test_data.py
tests/test_config.py
tests/test_leakage.py
tests/test_improve_leakage.py
scripts/run_all.py
.claude/agents/reviewer.md

### Shell: `'cat src/data.py src/config.py'`
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
"""Pipeline entry point (M1-M4).

  python scripts/run_all.py --config official      [--stage fit]   # M1-M3 + model + calibration + pre-registration
  python scripts/run_all.py --config official_h3   [--stage fit]   # the same for H = 3 (extra results row)
  python scripts/run_all.py --stage final-test                     # scores the FINAL TEST once, both horizons (D-021)
  python scripts/run_all.py --config new_regime                    # exploratory API section (D-015, D-027)

The fit stage 
### Shell: `'cat tests/test_data.py tests/test_run_all.py'`
import dataclasses

import pandas as pd
import pytest

from src import config, data, regions

HEADER = "oblast,raion,hromada,level,started_at,finished_at,source\n"


def row(oblast, start, end, level="oblast", raion="", hromada=""):
    return f"{oblast},{raion},{hromada},{level},{start}+00:00,{end}+00:00,official\n"


def base_rows():
    # one row per canonical unit so the 24-unit check passes
    return [row(v["official_name"], "2024-01-01 10:00:00", "2024-01-01 11:00:00")
            for v i
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
### Shell: `"sed -n '95,123p' DECISIONS.md; rg -n 'Data|30.min|1.hour|3600|Brier|GENERATED|imput|causal|leak' README.md; rg --files -g AGENTS.md -g '*M1c*' -g '*consensus*' -g '*SKILL.md' .claude reviews plans"`

## D-013 — Best practices adopted from related work
- Source: builder's web research (about a dozen public repos plus arXiv:2411.14625), checked
  against our data where possible. Metrics in other repos are self-reported, not rerun.
- Verified by builder: 113,845 of 299,275 official rows are exact duplicates
  (`sort -u` → 185,430 unique). Recording gap: 29 Aug 88 onsets, 30 Aug–1 Sep 0 rows,
  rows resume 2 Sep (normal days have 350–600). D-009 and D-010 counts were made BEFORE
  deduplication
### Shell: `"rg -n 'def run_pipeline|def main|stage|exists|prereg|print|m1_checks|alert_counts' scripts/run_all.py"`
3:  python scripts/run_all.py --config official      [--stage fit]   # M1-M3 + model + calibration + pre-registration
4:  python scripts/run_all.py --config official_h3   [--stage fit]   # the same for H = 3 (extra results row)
5:  python scripts/run_all.py --stage final-test                     # scores the FINAL TEST once, both horizons (D-021)
8:The fit stage reads no test label. The final-test stage refuses to run unless both horizons are pre-registered and
33:def code_fingerprint(root=ROOT)
### Shell: `"sed -n '1,175p' tests/test_leakage.py; sed -n '300,450p' scripts/run_all.py; sed -n '25,45p' README.md; cat .claude/skills/ts-leakage-audit/SKILL.md"`
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
### Shell: `"nl -ba plans/notes/fabricated_1h_ends.md | sed -n '14,104p'; sed -n '1,180p' plans/notes/fabricated_1h_ends/followup.py"`
    14	```
    15	
    16	All counts are after deduplication (185,430 rows) with Luhanska excluded (185,429 alerts), on the local
    17	`data/official_data_en.csv`.
    18	
    19	## Mechanism (from the parser source)
    20	
    21	In the dataset's parser (`processors/official_channel_processor.py`, lines 132–138), when a new alert starts for
    22	a location L, and L still has an alert with no all-clear that started more than 3 hours before, the old alert is
    23	written with `finished_at 
### Shell: `"sed -n '108,166p' scripts/run_all.py; sed -n '200,217p' scripts/run_all.py; sed -n '515,555p' scripts/run_all.py; rg --files reports -g '*access*' -g '*prereg*'; rg --files -g AGENTS.md -g '"'!data/*`


def build_frames(cfg, data_path):
    """M1 + M2 for an official config: alerts, grid (y, mask), features, checks (all raising). Reads no file it writes."""
    if cfg.source != "official":
        raise NotImplementedError(f"build_frames is for official configs, got source {cfg.source!r}")
    print(f"[run] config {cfg.name}: horizon H = {cfg.H_label} (label = onset in (t, t+H])")
    stats = {}
    alerts = data.load_official(data_path, cfg, stats)
    check_source(alerts, "official")
    be
I’ll read the priority files first, then check the plan against the relevant code and tests for rule conflicts, leakage, and tests that could miss the bugs they target.
I’m applying the repository’s `ts-leakage-audit` skill. The note identifies ends that were recorded only after forecast time; I’ll check whether the plan’s “keep as-is” decision explicitly resolves that conflict with the causality rule.
The planned run command defaults to fitting and is blocked once the final-test marker exists. I also found that the truncation test leaves fabricated ends earlier than t untouched, so it can pass despite the delayed-recording leakage described in the note.
## BLOCKERS

- L3–5, “Keep the alerts as they are”: the note identifies retrospective ends unavailable at t. D-020’s cap does not prevent their use in masks/features. Preserve the approved retention, but explicitly document the causality exception in the README and proposed decision entry; small score sensitivity does not establish absence of leakage.
- L44, “`run_all.py --config official`”: defaults to fitting and refuses because `reports/final_test_access.json` exists. Code changes also invalidate preregistered code fingerprints. Replace this validation with frame comparisons and frozen-artifact checks; preserve registrations and access markers.
- L40, “full `pytest -q` passes”: `tests/test_leakage.py::truncate` hides only ends **later** than t. A fabricated end earlier than t survives despite being recorded later. Add a delayed-recording witness and report this retained limitation explicitly; passing the current audit cannot establish causality.

## AMBIGUITIES

- L16, “parser-imputed ends”: labels all 255 as imputed, contradicting L50’s probable genuine alerts. Print “exactly-3600-second durations; includes suspected imputed ends.”
- L36–38, “does not break ‘no test statistics’”: CLAUDE.md forbids test-period statistics; D-022 authorizes specific checks, not every diagnostic. State the new count’s explicit exception and prohibit downstream use.
- D-022 describes detected gap edges plus 24h but quotes 145 hours; D-024’s 145 hours use the wider approved gap. Specify that existing conservative masks remain authoritative, separately from detected edges.

## MISSING

- L28–31’s tests can pass with counting before deduplication/exclusion or incorrect level breakdowns. Add duplicate exact-hour rows, an exact-hour Luhanska row, mixed levels, unknown ends, and a zero expected count; assert totals and breakdowns.
- L39–41, “byte-identical”: matching rounded metrics and shapes cannot prove this. Compare keyed alerts, labels, masks and features before/after, including DST, gap boundaries, 24h caps, Kyiv City/Kyivska, `(t,t+H]` endpoints, cutoff equality and rolling-window boundaries for both horizons.
- L24–25: label the sensitivity **post-hoc, frozen predictions, no refit**, with both predictors evaluated on the same remaining rows.
- L43–45 omits mandatory reviewer/harness review, human summary and proposed decision entry (CLAUDE.md; D-026). Add them.

## QUESTIONS FOR THE HUMAN

- L54, “None”: does the recorded Option 1 decision also cover the whole-file diagnostic exception? Include its scope in the human-ratified decision entry under D-026.

VERDICT: CHANGES REQUIRED
