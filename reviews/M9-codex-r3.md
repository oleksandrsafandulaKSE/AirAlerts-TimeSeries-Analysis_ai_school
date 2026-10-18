### Shell: `"pwd && rg --files -g 'AGENTS.md' -g 'SKILL.md' -g 'M9*' -g 'CLAUDE.md' -g 'DECISIONS.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
CLAUDE.md
DECISIONS.md
plans/M9.md
reviews/M9-claude-r2.md
reviews/M9-claude-r1.md
reviews/M9-codex-r3.log
reviews/M9-codex-r2.log
reviews/M9-codex-r1.md
reviews/M9-codex-r1.log
reviews/M9-consensus.md
reviews/M9-codex-r2.md

### Shell: `'cat plans/M9.md reviews/M9-codex-r2.md reviews/M9-claude-r2.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M9 plan v1 — Research-driven upgrades: data-quality pin, uncertainty, CORP calibration, leakage controls

## Status and authority
- **Human, chat 2026-10-17:**
  - "I choose A for M1c". The exactly-1h check lives OUTSIDE the fingerprinted pipeline code.
  - "make a plan for implementation changes found in research". Source: `air-alert-forecasting-research/`
    (24 items) and `plans/notes/fabricated_1h_ends.md`.
- **Supersedes** `plans/M1c-exact-1h-check.md`. The agreed round-1 items from
  `r
### Shell: `'wc -l plans/M9.md reviews/M9-codex-r2.md reviews/M9-claude-r2.md CLAUDE.md DECISIONS.md; tail -n 65 reviews/M9-codex-r2.md; cat reviews/M9-claude-r2.md; cat CLAUDE.md'`
     224 plans/M9.md
      87 reviews/M9-codex-r2.md
      19 reviews/M9-claude-r2.md
     156 CLAUDE.md
     301 DECISIONS.md
     787 total
- **B2 ("statistically tied"): AGREE.** The README wording is now "the interval in
### Shell: `"sed -n '1,100p' DECISIONS.md; sed -n '1,280p' tests/test_leakage.py; sed -n '1,170p' src/grid.py; rg -n 'calibration_in_the_large|code_fingerprint|p_headline|metrics.csv' src/evaluate.py scripts/run_`
# Decisions and challenge log

Format per entry: **Context → 
### Shell: `"sed -n '1,105p' DECISIONS.md; sed -n '1,235p' tests/test_leakage.py"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"sed -n '1,120p' src/grid.py; rg -n -A14 -B4 'calibration_in_the_large|code_fingerprint|fingerprint_matches|p_headline|validation_predictions' src/evaluate.py scripts/run_all.py tests/test_improve_mod`
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
I’ll compare each previous finding with the updated plan and builder’s response, then check the provisional decisions against the project rules and leakage-audit skill.
The open cutoff issue now has separate checks at t=C−H and t=C. I’m applying the leakage-audit skill to check the timing semantics and confirm the provisional settings stay within the approved scope.
## PREVIOUS ITEMS

- RESOLVED — Unratified authority: §Status denies D-028/D-030 authority and cites the fingerprint implementation.
- RESOLVED — Equivalence claim: README wording avoids calling a zero-containing interval a tie.
- RESOLVED — DM estimand: hourly loss sums preserve the row-weighted comparison.
- RESOLVED — Bootstrap specification: selection, sample length, partial weeks, wraparound and zero-denominator behavior are explicit.
- RESOLVED — Validation join: unique keys, identical key sets and labels, UTC timestamps and canonical groups are required.
- ACCEPTED — Purge disagreement: M9 uses frozen eligibility and introduces no fitting or purge operation.
- ACCEPTED — Gap disagreement: existing masks remain authoritative; reconciling historical descriptions is outside this change.
- RESOLVED — PAV fixture: known fitted values and decomposition reject an unchanged-predictions implementation.
- RESOLVED — Missing inputs: real-data tests fail, and the runner raises on missing inputs or changed pins.
- RESOLVED — E1/E2 controls: §E2 now separately requires t=C−H and t=C at each cutoff, retaining endpoint witnesses and causal companions.
- RESOLVED — E3 coverage: minimum earlier counts, explicit failure and an all-level mutation fixture are specified.
- RESOLVED — Test-statistics authorization: §0 records scoped human approval for B–D with diagnostic-use restrictions.

## PROVISIONAL DECISIONS

- **25% collapse threshold; ≥10 earlier onsets:** within D-017’s data-quality checks. These trigger reporting/failure without redefining targets, masks or eligibility.
- **Seed 20261017; 10,000 resamples:** implementation choices within the approved bootstrap scope.
- **Newey–West lags 24/72:** diagnostic settings within the explicitly approved DM analysis.

All remain provisional under D-026. None changes CLAUDE.md or an existing decision. Changing the primary bootstrap from weeks would require human approval, as the plan acknowledges.

## NEW ISSUES

None introduced by the boundary correction. This resolves the previous review’s sole OPEN item; implementation and its required verification remain pending.

VERDICT: AGREE
