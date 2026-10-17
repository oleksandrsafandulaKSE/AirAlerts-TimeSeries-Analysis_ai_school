### Shell: `'cat plans/M9.md reviews/M9-codex-r1.md reviews/M9-claude-r1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M9 plan v1 — Research-driven upgrades: data-quality pin, uncertainty, CORP calibration, leakage controls

## Status and authority
- **Human, chat 2026-10-17:**
  - "I choose A for M1c". The exactly-1h check lives OUTSIDE the fingerprinted pipeline code.
  - "make a plan for implementation changes found in research". Source: `air-alert-forecasting-research/`
    (24 items) and `plans/notes/fabricated_1h_ends.md`.
- **Supersedes** `plans/M1c-exact-1h-check.md`. The agreed round-1 items from
  `r
### Shell: `'wc -l reviews/M9-codex-r1.md reviews/M9-claude-r1.md CLAUDE.md DECISIONS.md; cat reviews/M9-claude-r1.md; tail -n 100 reviews/M9-codex-r1.md; cat CLAUDE.md; rg --files -g AGENTS.md -g SKILL.md . ..'`
     153 reviews/M9-codex-r1.md
      45 reviews/M9-claude-r1.md
     156 CLAUDE.md
     301 DECISIONS.md
     655 total
# M9 — Claude response, round 1

## Changes made
- **B1 (D-028 / D-030 not ratified): AGREE.** `grep "^## D-" DECISIONS.md` ends at D-027. The plan now cites
  the fingerprint as a code fact (`scripts/run_all.py:33` plus the fingerprint test), and states that D-028 and
  D-030 authorize nothing.
- **B2 ("statistically tied"): AGREE.** The README wording is now "the interval in
### Shell: `"sed -n '1,100p' DECISIONS.md; sed -n '1,280p' tests/test_leakage.py; sed -n '1,170p' src/grid.py; rg -n 'calibration_in_the_large|code_fingerprint|p_headline|metrics.csv' src/evaluate.py scripts/run_`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `".venv/bin/python -B -c 'import pandas as pd; from src import config,data,grid; c=config.official(); a=data.load_official(\"data/official_data_en.csv\",c); iv=grid.unit_intervals(a,c.standing_cap); wi`
[data] raw rows: 299,275
[data] exact duplicate rows dropped (raw strings): 113,845 -> 185,430 rows
[data] excluded-unit rows dropped: 1 ({'Luhanska oblast': 1})
[data] shared format: (185429, 7), 2022-03-15 16:10:34+00:00 -> 2026-09-07 05:28:22+00:00
[('cherkaska', [198, 238]), ('chernihivska', [302, 423]), ('chernivetska', [43, 42]), ('dnipropetrovska', [58, 56]), ('donetska', [233, 172]), ('ivano_frankivska', [38, 38]), ('kharkivska', [466, 479]), ('khersonska', [298, 483]), ('khmelnytska', [
### Shell: `"sed -n '1,100p' src/grid.py; sed -n '28,50p' scripts/run_all.py; rg -n -A15 -B5 'calibration_in_the_large' src/evaluate.py scripts/run_all.py; head -n 3 reports/official/calibration_in_the_large.csv;`
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
I’ll read the updated plan, prior review, builder response, and project rules, then check disputed claims against the relevant code and tests.
The main round-one fixes are present: DM uses hourly sums, the validation join has strict checks, and the PAV fixture has known answers. I’ll now check the provisional choices against the project rules and look for remaining gaps in the revised tests.
## PREVIOUS ITEMS

- RESOLVED — Unratified authority: §Status explicitly denies D-028/D-030 authority and cites the fingerprint implementation.
- RESOLVED — Equivalence claim: README wording no longer calls a zero-containing CI a tie.
- RESOLVED — DM estimand: hourly sums preserve the row-weighted loss comparison.
- RESOLVED — Bootstrap details: block selection, resample length, partial weeks, wrap and zero-denominator behavior are specified.
- RESOLVED — Validation join: unique keys, identical key sets/labels, UTC timestamps and canonical groups are required.
- ACCEPTED — Purge wording disagreement: M9 consumes frozen eligibility and introduces no fitting or purge operation.
- ACCEPTED — Gap wording disagreement: M9 preserves frozen masks; reconciling historical descriptions is outside this change.
- RESOLVED — PAV fixture: known fitted values and decomposition reject an unchanged-predictions implementation.
- RESOLVED — Missing inputs: real-data tests fail, and the runner raises on missing inputs or changed pins.
- OPEN — E1/E2 controls: plans/M9.md:168–169 requires both “t = the val/test cut-offs” and “t+H equals the cut-off.” With H=1 hour these cannot coincide. Require separate checks at **t=C−H**, where the label matures exactly at C, and **t=C**. Otherwise the requested boundary test is impossible.
- RESOLVED — E3 denominator/mutation coverage: minimum earlier counts, explicit failure and an all-level synthetic mutation fixture are specified.
- RESOLVED — Test-statistics escalation: §0 records explicit human approval for B–D and limits diagnostic use.

## PROVISIONAL DECISIONS

- **25% collapse threshold and ≥10 earlier onsets:** within D-017’s raising data-quality checks; no target, mask or eligibility change. Checked against the frozen loader/union: all 24 units meet these conditions.
- **Seed 20261017 and 10,000 resamples:** implementation choices within the approved bootstrap scope.
- **Newey–West lags 24 and 72:** design choices within the explicitly approved DM diagnostic.

None is a concealed rule change. Switching the primary bootstrap away from weeks would require human approval, as the plan recognizes.

## NEW ISSUES

None beyond the incomplete E2 boundary correction above.

VERDICT: CHANGES REQUIRED
