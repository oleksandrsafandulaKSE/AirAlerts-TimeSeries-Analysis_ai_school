### Shell: `'cat plans/M8.md reviews/M8-codex-r2.md reviews/M8-claude-r2.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function

Status: v1.2 after consensus round 2 (D-026 loop). Human decisions in chat (2026-10-13): "the UI has to be an
interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
to the recent level); a Netlify scheduled function; geoBoundaries ADM1 boundaries. This starts part of M6 (D-016) by
the human's explicit decision. Further human decis
### Shell: `'wc -l reviews/M8-codex-r2.md reviews/M8-claude-r2.md CLAUDE.md DECISIONS.md; cat reviews/M8-claude-r2.md; tail -n 100 reviews/M8-codex-r2.md; cat CLAUDE.md'`
     203 reviews/M8-codex-r2.md
      20 reviews/M8-claude-r2.md
     156 CLAUDE.md
     301 DECISIONS.md
     680 total
# Claude response, round 2 — plans/M8.md

## Changes made
- B3 — AGREE: coverage is a list of confirmed intervals per unit; a history call confirms [c − 30 d, c) only when contiguous with the previous interval; anything else stays a HOLE (incl. outages > 30 days, unrecoverable).
- M1 — AGREE: the negative-control witness is an immature label hour τ − H < s ≤ τ with an onset in
### Shell: `"cat src/grid.py src/features.py; sed -n '150,290p' src/data.py; cat src/regions.py; rg -n 'D-030|D-032|warming|coverage|fetched|fetch_time' reviews/PROPOSED-DECISIONS* plans/M7.md scripts tests/test_`
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
### Shell: `"nl -ba plans/M8.md | sed -n '26,80p'; sed -n '42,85p' reviews/PROPOSED-DECISIONS-M4-M5.md; sed -n '1,105p' tests/test_api_loader.py; rg --files --hidden -g AGENTS.md -g '"'!.git/**'"'"`
    26	  clipped to [1e-4, 1 − 1e-4] before the logit. Saved: `model_live.json` (`dump_model`, trees up to `best_iteration`) +
    27	  `model_live_meta.json` (features, category order, offset constants, best_iteration, dates, sha256). No tuning; no API
    28	  data in training.
    29	- **Inference in JavaScript:** `netlify/functions/lib/` evaluates the LightGBM trees from the JSON dump (numerical splits
    30	  and the categorical `unit_code` split), computes the 9 base features + the causal
I’ll check each prior finding against the updated plan and builder’s evidence, then check the provisional decisions against the repository rules.
The plan fixes the failure-status delivery, immature-label witness, and earlier wording issues. I’m applying the leakage-audit skill to check whether the new coverage rules preserve uncertainty after an outage.
## PREVIOUS ITEMS

- B1 — RESOLVED: human approval covers the revised forecast interval.
- B2 — RESOLVED: observation versions and replay preserve knowledge at τ.
- B3 — OPEN: M8 §2 confirms a history window only when it overlaps previous coverage. After an outage exceeding 30 days, this prevents recording fresh, valid coverage. Add disjoint confirmed intervals; retain only the unrecoverable gap.
- B4 — RESOLVED: physical alert status and capped mask remain separate.
- A1 — RESOLVED: model recipe, export metadata, and offset are pinned.
- A2 — RESOLVED: exact oblast mapping and Kyiv fixtures are specified.
- M1 — RESOLVED: the negative control now specifies an immature-label witness.
- M2 — OPEN: §2 excludes “hours in holes,” but does not require excluding label windows crossing holes or the following 24-hour uncertainty in masks and spatial state. D-022 and `src/grid.py::gap_mask_for` require both; checking state only at τ misses alerts originating inside a hole.
- M3 — RESOLVED: raising checks and parsed deduplication remain specified.
- M4 — RESOLVED: GET delivers failure status alongside forecasts, with browser tests.
- Q1 — RESOLVED: all alert types have human approval.
- Q2 — RESOLVED: dependency pins have human approval.
- Q3 — RESOLVED: cutoff equality has human approval.
- Previous NEW exclusions — RESOLVED: deliberate exclusions precede unknown-name rejection.
- Previous NEW header — RESOLVED: wording identifies all alert types.
- Previous NEW cadence — RESOLVED: recomputation consistently says every minute.

## PROVISIONAL DECISIONS

- One-minute polling and one history request per run fit existing rules.
- Warming-up/data-gap states and the 90-minute threshold fit only as presentation/freshness policies; they cannot waive completeness requirements.
- Replacing study tiles with geographical shapes preserves scope and saved numbers.

## NEW ISSUES

- §2 certifies ACTIVE-poll hours as covered, while new §9 explicitly admits missed short alerts. Those hours can therefore supply false negative labels to k, n, and q before reconciliation. Calling this a limitation does not satisfy CLAUDE.md’s missing-data rule. Keep completeness unconfirmed until backfill, or escalate this approximation as a rule change.

VERDICT: CHANGES REQUIRED
