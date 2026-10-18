### Shell: `'cat plans/M10.md reviews/M10-codex-r2.md reviews/M10-claude-r2.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and day/night tables, live forecast check). The live check and the UI are
  in `plans/M11.md`; this 
### Shell: `'wc -l plans/M10.md reviews/M10-codex-r2.md reviews/M10-claude-r2.md CLAUDE.md DECISIONS.md
cat reviews/M10-claude-r2.md
cat CLAUDE.md
 tail -n 100 reviews/M10-codex-r2.md'`
     186 plans/M10.md
     263 reviews/M10-codex-r2.md
      14 reviews/M10-claude-r2.md
     156 CLAUDE.md
     301 DECISIONS.md
     920 total
# M10 — Claude response, round 2

## Changes made
- A2 (OPEN): AGREE. Classes rewritten as mutually exclusive (L0: kept / shifted / disappeared; L1: matched / shift target / new) with asserted invariants; four fixtures incl. Codex's [00:00,02:00)+[01:00,03:00) case (→ shifted + shift target, 0 new); duration medians split by disappeared / shifted.
- New
### Shell: `"cat DECISIONS.md
cat .claude/skills/ts-leakage-audit/SKILL.md
rg --files -g AGENTS.md -g '*consensus*'
sed -n '1,180p' src/grid.py
sed -n '1,180p' src/baselines.py
sed -n '1,150p' improve/features_pl`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"rg -n '"'^##|PROVISIONAL|RESOLVED|ACCEPTED|OPEN|Reporting baseline|VERDICT'"' reviews/M10-codex-r2.md reviews/M10-claude-r1.md reviews/M10-claude-r2.md
rg --files -g AGENTS.md -g '*M10*'"`
reviews/M10-claude-r1.md:3:## Changes made
reviews/M10-claude-r1.md:12:## Disagreements
reviews/M10-claude-r1.md:15:## Design decisions taken
reviews/M10-claude-r1.md:16:- PROVISIONAL: A2 matching is exact-instant (±0 s), since L1 onsets are a subset of L0 rows' starts.
reviews/M10-claude-r1.md:17:- PROVISIONAL: group rates pool, never average.
reviews/M10-claude-r1.md:19:## Escalations
reviews/M10-claude-r2.md:3:## Changes made
reviews/M10-claude-r2.md:4:- A2 (OPEN): AGREE. Classes rewritten as
### Shell: `"sed -n '1,115p' src/grid.py
sed -n '1,125p' src/baselines.py"`
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
### Shell: `"sed -n '41,94p' plans/M10.md
sed -n '1,90p' improve/features_plus.py
rg -n 'zero|duration' tests/test_grid.py src/data.py
ls data"`
  `features.build_features` path, same D-020 cap, same gap mask):
  - **L0** = current rule (all levels).
  - **L1** = the same after dropping `level == "hromada"` rows from the shared-format frame BEFORE the union.
    Proxy only: it removes all artillery warnings if the other project's finding holds here, and also some real
    air-raid hromada alerts. No name lists, no fuzzy matching.
- **A1. Descriptive table** `reports/m10/labels_variant.csv`, per unit and per group (Kyiv City / frontline /
I’ll read the updated plan, prior review, and builder’s response first, then check the fixes and provisional decisions against the project rules and leakage-audit requirements.
The two outstanding fixes are explicit: §A2 separates shifted from disappeared onsets, and §A3 restores the frozen reporting prior while retaining the causal offset. I’m applying the leakage-audit skill to check whether either change creates a new boundary problem or exceeds the project rules.
## PREVIOUS ITEMS

- **ACCEPTED — B1, prior leakage:** Existing `label_rates` uses a causal expanding prior.
- **RESOLVED — B2, AUC:** §D preserves class-count thresholds, exclusions, and explained NaNs.
- **RESOLVED — A1, denominators:** Unit denominators and pooled group aggregation remain explicit.
- **RESOLVED — A2, shifted onsets:** §A2 now separates kept/shifted/disappeared and matched/shift-target/new, asserts reconciliation, corrects fixtures, and separates duration populations.
- **RESOLVED — A3, uncertainty zones:** Applied bounds, endpoint predicates, and recovery times remain specified.
- **RESOLVED — M1, weight/BSS tests:** Exact Dataset weights and unequal-error BSS fixtures remain required.
- **RESOLVED — M2, execution boundaries:** Label maturity, cutoff equality, variant isolation, and target endpoints remain covered.
- **RESOLVED — M3, exposure fixtures:** Carry-in, unknown ends, caps, and gap boundaries remain covered.
- **RESOLVED — M4, calendar/group tests:** Day/night boundaries, DST, and Kyiv City separation remain covered.
- **RESOLVED — M5, artifacts:** Required outputs, reliability plot, leakage evidence, and metadata remain listed.
- **RESOLVED — Human authorization:** §E remains gated on explicit human approval.
- **RESOLVED — Reporting baseline change:** §A3 confines expanding q(t) to the offset; reporting uses variant-specific eligible-fit p_unit, frozen during scoring, with an isolation test.

## PROVISIONAL DECISIONS

- **Exact-instant matching:** Within existing rules; compares observed onset timestamps without redefining the target.
- **Pooled group rates:** Within existing aggregation rules; no baseline or evaluation-rule change.
- **Revised A2 classes:** Within CLAUDE.md and D-023/D-026 as descriptive accounting. L1 remains a proxy; adopting it as the target still requires human approval.

## NEW ISSUES

None introduced by these revisions.

VERDICT: AGREE
