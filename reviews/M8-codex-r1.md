### Shell: `'cat plans/M8.md CLAUDE.md DECISIONS.md reviews/PROPOSED-DECISIONS-M4-M5.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function

Status: DRAFT for the Claude–Codex consensus loop (D-026). Human decisions in chat (2026-10-13): "the UI has to be an
interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
to the recent level); a Netlify scheduled function; geoBoundaries ADM1 boundaries. This starts part of M6 (D-016) by
the human's explicit decision. Rules: CLAU
### Shell: `'nl -ba plans/M8.md; nl -ba DECISIONS.md'`
     1	# M8 plan v1 — Live map of Ukraine: next-hour forecasts, auto-updated by a Netlify scheduled function
     2	
     3	Status: DRAFT for the Claude–Codex consensus loop (D-026). Human decisions in chat (2026-10-13): "the UI has to be an
     4	interactive map of Ukraine that auto-updates, not a Claude artifact"; live next-hour forecast; the OFFSET model (adapts
     5	to the recent level); a Netlify scheduled function; geoBoundaries ADM1 boundaries. This starts part of M6 (D-016) by
     6	
### Shell: `"rg --files -g AGENTS.md -g '*.py' src tests scripts improve; rg -n 'offset|label_rates|MODEL_FEATURES|BASE_FEATURES|load_api|updated_at|history_start|finished_at|cutoff|purge' improve src tests/test_`
tests/test_api_loader.py
src/data.py
tests/test_run_all.py
tests/test_new_regime.py
tests/test_improve_models.py
tests/test_data.py
tests/test_config.py
tests/test_site.py
tests/test_baselines.py
tests/test_evaluate.py
tests/test_regions.py
tests/test_final_test.py
tests/test_leakage.py
tests/test_improve_features.py
tests/test_features.py
tests/test_grid.py
tests/test_improve_leakage.py
tests/conftest.py
tests/test_model.py
scripts/export_predictions.py
scripts/run_all.py
scripts/build_site.py

### Shell: `'cat src/grid.py src/features.py src/regions.py src/data.py'`
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
### Shell: `'cat improve/features_plus.py improve/model_plus.py scripts/run_improve.py'`
"""M7 extra inputs, all known at t (plans/M7.md §2.1, §3). Reads src/ read-only; never changes the headline pipeline.

Block A (labels, s <= t - H; human-approved exception): unit shrunk recent rates over 14 d and 30 d, national 14-d rate.
Offset input: r(t) = the unit's 14-d shrunk rate with the CAUSAL expanding prior q(t).
Block B (onset events up to t): national onsets (t-1h, t] and (t-3h, t]; frontline onsets (t-3h, t]; neighbours' onsets
(t-1h, t]; minutes since the last national onset.
Blo
### Shell: `"cat tests/test_improve_leakage.py; sed -n '150,195p' DECISIONS.md; rg --files -g AGENTS.md -g '*M8*' -g '*consensus*' reviews .claude; cat netlify.toml"`
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
### Shell: `'cat src/regions.py src/features.py src/grid.py'`
"""The single table of the 24 forecast units. The ONLY place names are mapped (D-017 #1)."""

# key, official English name (verbatim from official_data_en.csv), alerts.in.ua UID, group (D-011)
_UNITS = [
    ("kyiv_city", "Kyiv City", 31, "kyiv_city"),
    ("chernihivska", "Chernihivska oblast", 25, "frontline"),
    ("sumska", "Sumska oblast", 20, "frontline"),
    ("kharkivska", "Kharkivska oblast", 22, "frontline"),
    ("donetska", "Donetska oblast", 28, "frontline"),
    ("dnipropetrovska",
I’ll read the priority files first, then check the relevant code and tests for contradictions, leakage, and gaps in the plan’s tests.
I’m applying the leakage-audit skill, especially its truncation test. I’ll also check whether the live polling design preserves what was actually known at each forecast time.
The main blocker is recomputing an hourly forecast from polls received later in that hour. Reconciliation can also overwrite what was known at the original forecast time. I’ve confirmed that the M7 offset uses an expanding causal prior; the JS parity and leakage tests need to specify that behavior and catch deliberately leaky variants.
## BLOCKERS

- L29–30, “t = floor(now)”: a 10:45 poll supplies information unavailable at 10:00. Freeze inputs at the UTC hour boundary and display the actual interval `(t,t+1h]`; changing forecast time requires human approval.
- L27–29, “reconcile exact end times”: later reconciliation can introduce an end unknown at t. Preserve observation timestamps and record versions; reconstruct forecasts from versions available at t.
- L25, “ACTIVE-alerts”: alerts starting and ending between polls disappear entirely. Rebuilding labels then creates false negatives. Require confirmed per-unit history coverage before accepting labels; retain unresolved periods as missing.
- L39–40, “alert running now” → “no forecast”: this masks standing alerts beyond 24h, contradicting D-020. Separate physical alert status from the capped forecasting mask.

## AMBIGUITIES

- L16, “train the M7 V2 recipe”: pin train/validation dates, `t+H≤cutoff` eligibility, selected iteration, feature/category order, and offset semantics. `label_rates` uses an expanding causal prior; specify α=10, clipping, empty-history behavior, and prior initialization.
- L26, “new ids → new alerts”: the existing loader maps units using the requested file UID, unavailable in a national ACTIVE response. Specify exact parent-unit mapping through `regions.py`, including separate Kyiv City/Kyivska fixtures and union across administrative levels.

## MISSING

- L58, “DST-free window,” and L61, “same JS path”: shared bugs can pass parity. Add actual DST transitions, raw-data truncation hiding unknown ends, observation-time replay, and deliberately leaky negative controls. Assert boundary behavior at t, t+H, lookback edges, and the 24h cap.
- D-022–D-024: add official recording-gap edge fixtures, post-gap masking, and NaN lookbacks. For live operation, detect seed-to-start gaps and outages; require confirmed coverage before resuming forecasts.
- D-017 / L59, “History update”: add raising schema/unit/coverage checks and required count/range diagnostics. Preserve `updated_at` for deduplication rather than discarding it in the shared table.
- L33, “last API call failed”: failure may leave `latest.json` unchanged. Persist failure status separately and test immediate greying before the 45-minute threshold.

## QUESTIONS FOR THE HUMAN

- Proposed D-028 leaves alert types unresolved. Approve air-raid-only versus all types explicitly; use that choice consistently for labels, features, and masks.
- L65, “need human approval,” / D-026: approve exact Netlify dependency versions before implementation.
- D-014 says “purge the last H hours,” while D-022 retains `t+H=cutoff`. Ratify the proposed wording correction and standardize on `≤`.

VERDICT: CHANGES REQUIRED
