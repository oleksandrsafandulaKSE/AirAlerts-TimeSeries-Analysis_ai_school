### Shell: `'cat plans/M8.md reviews/M8-codex-r4.md reviews/M8-claude-r4.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function

Status: v1.4 after consensus round 4 (D-026 loop). Human decisions in chat (2026-10-13): "the UI has to be an
interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
to the recent level); a Netlify scheduled function; geoBoundaries ADM1 boundaries. This starts part of M6 (D-016) by
the human's explicit decision. Further human decis
### Shell: `'wc -l reviews/M8-codex-r4.md reviews/M8-claude-r4.md CLAUDE.md DECISIONS.md plans/M8.md'`
     200 reviews/M8-codex-r4.md
      13 reviews/M8-claude-r4.md
     156 CLAUDE.md
     301 DECISIONS.md
     142 plans/M8.md
     812 total

### Shell: `'tail -n 90 reviews/M8-codex-r4.md'`
- M2 — AGREE: explicit hole propagation: label inputs excl
### Shell: `"cat src/grid.py src/features.py src/improve_features.py; sed -n '140,240p' src/data.py; cat src/config.py"`
"""Per-unit intervals (D-002 union, D-020 causal cap), gap handling (D-013), hourly UTC grid."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError


def filter_levels(alerts, target_levels):
    if target_levels == "any":
        return alerts
    if target_levels == 
### Shell: `'cat reviews/M8-claude-r4.md CLAUDE.md'`
# Claude response, round 4 — plans/M8.md

## Changes made
- M2 — AGREE: holes now carry an EXTENDED zone [h0, h1 + 24 h) handled exactly like config.uncertainty_zones: onset-count windows touching it → unknown; time-since → unknown if τ ≥ h0 and the last event is before h1 + 24 h (features.py D-023 rule); label hours in [h0 − H, h1 + 24 h) excluded from k, n, q (the hours grid.gap_mask_for masks), in addition to requiring confirmed label windows.

## Disagreements
(none)

## Design decisions tak
### Shell: `"rg --files --hidden -g AGENTS.md -g '"'!'"\\.git/**'"`

### Shell: `'cat src/grid.py src/features.py src/config.py'`
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
### Shell: `'cat plans/M7.md reviews/M8-claude-r1.md reviews/M8-claude-r2.md reviews/M8-claude-r3.md'`
# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline

Status: AGREED (consensus round 5, D-026). See reviews/M7-consensus.md. Human approval in chat (2026-10-13): weekly refit,
recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).

## 0. What this milestone may and may not cl
### Shell: `"rg -n 'PROVISIONAL|D-030|D-032|offset|eligible|warming' reviews/PROPOSED* improve/features_plus.py plans/M8.md"`
reviews/PROPOSED-DECISIONS-M4-M5.md:9:  H = 1 none (ECE 0.0123), H = 3 Platt (ECE 0.0304, slope 1.30). PROVISIONAL: params, ECE threshold, low-n flag (< 100 rows).
reviews/PROPOSED-DECISIONS-M4-M5.md:42:## D-030 — M7: post-hoc improvement rows (human-approved exceptions; Claude–Codex consensus → human to ratify)
reviews/PROPOSED-DECISIONS-M4-M5.md:45:  unit/national recent rates (block A), the recent-rate offset, the weekly refit (D-014).
reviews/PROPOSED-DECISIONS-M4-M5.md:51:  V0 frozen −0.010
### Shell: `"sed -n '1,105p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
I’ll read the updated plan and both prior-round documents first, then check each response and provisional decision against the project rules and leakage-audit requirements.
The revision explicitly extends hole uncertainty to onset counts, time-since features, and offset labels, addressing M2. I’ll verify those boundaries against the existing code and check whether any provisional choice changes a project rule.
## PREVIOUS ITEMS

- B1 — RESOLVED: revised forecast interval retains explicit human approval.
- B2 — RESOLVED: versioned observations and replay preserve knowledge at τ.
- B3 — RESOLVED: disjoint coverage preserves fresh intervals and unrecoverable holes.
- B4 — RESOLVED: physical alert status remains separate from the capped mask.
- A1 — RESOLVED: model recipe, export metadata, and offset remain pinned.
- A2 — RESOLVED: exact oblast mapping and separate Kyiv fixtures remain specified.
- M1 — RESOLVED: immature-label negative control retains a concrete witness.
- M2 — RESOLVED: §2 now extends onset/time-since uncertainty through h1 + 24 h and excludes label hours in [h0 − H, h1 + 24 h), matching `features.py`, `config.uncertainty_zones`, and `grid.gap_mask_for`.
- M3 — RESOLVED: raising checks and parsed-update deduplication remain specified.
- M4 — RESOLVED: GET returns failure status alongside the forecast.
- Q1 — RESOLVED: all alert types retain human approval.
- Q2 — RESOLVED: exact dependency pins retain human approval.
- Q3 — RESOLVED: cutoff equality retains human approval.
- Previous NEW exclusions — RESOLVED: deliberate exclusions precede unknown-name rejection.
- Previous NEW header — RESOLVED: wording identifies all alert types.
- Previous NEW cadence — RESOLVED: recomputation consistently specifies every minute.
- Previous NEW poll-only completeness — RESOLVED: labels require history confirmation; the event-tail exception retains recorded human approval.

## PROVISIONAL DECISIONS

- One-minute polling and one history request per run fit the approved scope and history-request limit.
- The 90-minute warming threshold is permissible as presentation policy; it cannot authorize probabilities when §2 requires unknown inputs or no forecast.
- Replacing study tiles with geographic shapes preserves approved scope and saved results.
- Forecast-time and poll-tail exceptions are rule changes, but explicitly human-approved—not provisional consensus decisions. No provisional choice independently changes CLAUDE.md or an existing decision.

## NEW ISSUES

None introduced by the round-four changes. The revised uncertainty rules address both parts of the remaining leakage-audit concern.

VERDICT: AGREE
