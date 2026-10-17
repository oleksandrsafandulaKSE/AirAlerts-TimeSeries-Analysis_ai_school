### Shell: `'wc -l plans/M9.md plans/notes/fabricated_1h_ends.md reviews/M1c-exact-1h-check-codex-r1.md reviews/M1c-exact-1h-check-claude-r1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
     167 plans/M9.md
      87 plans/notes/fabricated_1h_ends.md
     201 reviews/M1c-exact-1h-check-codex-r1.md
      43 reviews/M1c-exact-1h-check-claude-r1.md
     156 CLAUDE.md
     301 DECISIONS.md
      30 .claude/skills/ts-leakage-audit/SKILL.md
     985 total

### Shell: `'cat plans/M9.md plans/notes/fabricated_1h_ends.md reviews/M1c-exact-1h-check-codex-r1.md reviews/M1c-exact-1h-check-claude-r1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M9 plan v1 — Research-driven upgrades: data-quality pin, uncertainty, CORP calibration, leakage controls

## Status and authority
- **Human, chat 2026-10-17:**
  - "I choose A for M1c". The exactly-1h check lives OUTSIDE the fingerprinted pipeline code.
  - "make a plan for implementation changes found in research". Source: `air-alert-forecasting-research/`
    (24 items) and `plans/notes/fabricated_1h_ends.md`.
- **Supersedes** `plans/M1c-exact-1h-check.md`. The agreed round-1 items from
  `r
### Shell: `'nl -ba CLAUDE.md; nl -ba DECISIONS.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `'cat reviews/M1c-exact-1h-check-codex-r1.md reviews/M1c-exact-1h-check-claude-r1.md'`
### Shell: `'cat plans/M1c-exact-1h-check.md plans/notes/fabricated_1h_ends.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M1c — exactly-1-hour durations: count, print, raising check

Human decision (2026-10-17, chat): **Option 1** from `plans/notes/fabricated_1h_ends.md`. Keep the alerts as they
are, document the counts in the README and the M1 printing, and add a raising check on the exactly-3600 s count.
No change to the target, mask, features, models, the evaluation p
### Shell: `"rg --files -g AGENTS.md -g '*predictions*' -g '*calibration*' -g '*metrics.csv' -g '*preregistration*' -g '*SKILL.md' . src tests scripts reports; sed -n '96,242p' DECISIONS.md"`
scripts/export_predictions.py
reports/new_regime_all_types/metrics.csv
reports/official/calibration_in_the_large.csv
reports/official/preregistration.json
reports/official/test_predictions.csv
reports/official/val_predictions.csv
reports/official/metrics.csv
reports/official_h3/calibration_in_the_large.csv
reports/official_h3/preregistration.json
reports/official_h3/val_predictions.csv
reports/official_h3/metrics.csv
reports/new_regime/metrics.csv
reports/improve/validation_predictions.csv
./scr
### Shell: `"sed -n '1,280p' tests/test_leakage.py; sed -n '1,240p' src/evaluate.py"`
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
### Shell: `"head -n 4 reports/official/test_predictions.csv reports/official/val_predictions.csv reports/improve/validation_predictions.csv reports/official/calibration_in_the_large.csv reports/official/metrics.`
==> reports/official/test_predictions.csv <==
unit,t,group,status,y,p_model,p_recent_rate
cherkaska,2026-07-27 00:00:00+00:00,rear,scored,0.0,0.1520756582075356,0.182830680447872
cherkaska,2026-07-27 01:00:00+00:00,rear,scored,0.0,0.09939000645108967,0.17944084993939743
cherkaska,2026-07-27 02:00:00+00:00,rear,scored,0.0,0.12860296712182037,0.17944084993939743

==> reports/official/val_predictions.csv <==
unit,t,minutes_since_last_start,minutes_since_last_end,onsets_last_24h,onsets_last_7d,neigh
### Shell: `"sed -n '1,170p' src/grid.py; sed -n '1,125p' src/data.py; nl -ba plans/M9.md"`
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
### Shell: `".venv/bin/python -B - <<'PY'
import pandas as pd
from src import config, data, grid
alerts=data.load_official('data/official_data_en.csv',config.official())
ivs=grid.unit_intervals(alerts)
for u,(_,_`
zsh:1: can't create temp file for here document: operation not permitted

### Shell: `".venv/bin/python -B -c 'import pandas as pd
from src import config, data, grid
alerts=data.load_official(\"data/official_data_en.csv\",config.official())
ivs=grid.unit_intervals(alerts)
for u,(_,_,on`
[data] raw rows: 299,275
[data] exact duplicate rows dropped (raw strings): 113,845 -> 185,430 rows
[data] excluded-unit rows dropped: 1 ({'Luhanska oblast': 1})
[data] shared format: (185429, 7), 2022-03-15 16:10:34+00:00 -> 2026-09-07 05:28:22+00:00
scored 13116 hours 791 range 2026-07-27 00:00:00+00:00 2026-08-28 22:00:00+00:00
hourly unit count 1 22
validation keys equal True rows 11160 11160

### Shell: `".venv/bin/python -B -c 'import pandas as pd
p=pd.read_csv(\"reports/official/test_predictions.csv\")
s=p[p.status==\"scored\"].copy()
s[\"d\"]=(s.p_model-s.y)**2-(s.p_recent_rate-s.y)**2
print(\"row_`
row_weighted_d 0.000887068841878874 equal_hour_d 0.0005565244149254389
reports/official/val_predictions.csv duplicate_keys 0
reports/improve/validation_predictions.csv duplicate_keys 0

I’ll read the priority files, then check the existing code and tests for contradictions, leakage risks, and gaps in the proposed checks.
I’m applying the repository’s `ts-leakage-audit` skill. The plan cites D-028 and D-030, but the decision log ends at D-027. I’ll check the saved prediction formats and leakage-test helper next.
Scored hours contain between 1 and 22 eligible units, so B2’s equal weighting of hourly means tests a different quantity from the row-weighted BSS. C4’s decomposition identity also holds for arbitrary recalibrated values; the tests need a miscalibrated example with a known PAV solution.
## BLOCKERS

- L10–11 cites “D-028” and “D-030”, but DECISIONS.md ends at D-027. These cannot authorize fingerprint or post-hoc exceptions. Replace them with verifiable authority; resolve the approval question below before implementation.
- L136, “statistically tied overall”: a CI containing zero does not establish equivalence, especially with five blocks. Replace with “the interval includes no improvement”; require a prespecified equivalence margin before claiming a tie.

## AMBIGUITIES

- L74, “hourly mean differences”: eligible units vary from 1–22 per hour, so this tests a different estimand from row-weighted BSS. Align inference with row-weighted loss, or explicitly label the different estimand.
- L68–70, “partial weeks” / “circular”: specify block-selection probabilities, resample length, partial-block weighting, circular wrap boundaries, and zero-reference-loss handling. Resample eligible rows together without inventing missing unit-hours.
- L77, “joined on unit and t”: an inner join could silently discard or duplicate rows. Require unique keys, identical key sets and labels, UTC timestamps, and group lookup through `src/regions.py`, preserving Kyiv City/Kyivska separation.
- D-014 says purge “last H hours”; D-022/D-023 retain `t+H = cutoff`. State explicitly that `t+H ≤ cutoff` governs.
- D-022 describes detected gap edges but quotes D-024’s wider 145-hour exclusion. Distinguish detected outage, approved mask and feature-uncertainty intervals; keep frozen masks authoritative.

## MISSING

- L100–104, “decomposition identity holds”: algebra makes this pass for arbitrary recalibrated values; returning unchanged predictions could pass every listed C4 test. Add a miscalibrated, hand-calculated PAV fixture with known fitted values and decomposition.
- L46–47, “skipped … like tests/test_leakage.py”: that fixture actually fails when data is absent. Match that behavior, and require `run_extras.py` itself to raise on missing inputs or changed pins.
- L114–118, “pinned witnesses”: define E2’s historical label construction and require nonempty, fixed expected mismatches plus causal companion controls. Test `(t,t+H]` endpoints, label maturity, and Kyiv civil-day boundaries across 23/25-hour DST days.
- L120–125, “25%”: zero earlier onsets leave the ratio undefined and can conceal an already-collapsed unit. Specify zero-count behavior and add deterministic all-level fixtures, including standing-alert caps, that fail under an oblast-only mutation.

## QUESTIONS FOR THE HUMAN

- L21/D-026: does “make a plan” authorize new test statistics and same-test-label PAV fitting despite CLAUDE.md’s restrictions? Obtain explicit, scoped authorization; a proposed D-033 is not approval.

VERDICT: CHANGES REQUIRED
