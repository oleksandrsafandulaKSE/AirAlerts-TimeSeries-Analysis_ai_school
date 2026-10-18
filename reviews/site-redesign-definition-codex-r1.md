### Shell: `'cat plans/site-redesign-definition.md reviews/PROPOSED-DECISIONS-site.md plans/M6-definition.md reviews/PROPOSED-DECISIONS-M6.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# Site redesign — definition (grilling session with the human, 2026-10-18)

Status: agreed with the human in chat ("all agreed", "agreed, also go for round with codex"). Lines marked **[rule]**
change an existing D-entry (proposed or ratified); they are the human's decisions and are proposed in
`reviews/PROPOSED-DECISIONS-site.md`. Lines marked PROVISIONAL are design defaults for the milestone plans (D-026).
Work starts from `main` after the merge of M6a, M6c-1, M6-site and M10/M11 (done: 8f91ab
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
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
### Shell: `"rg --files -g 'AGENTS.md' -g '*site*' -g '*M6*' -g '*leak*' -g '*newregime*' -g '*reserve*' -g '*regions*'"`
src/regions.py
reviews/M6c-1-codex-r3.log
reviews/M6a-v2-claude-r2.md
reviews/M6-site-codex-r3.md
reviews/M6-site-claude-r2.md
reviews/M6c-1-codex-r2.log
reviews/M6c-1-codex-r2.md
reviews/M6a-claude-r2.md
reviews/M6c-1-codex-r1.log
reviews/M6-site-codex-r3-failed-attempt.log
reviews/M6c-1-codex-r3.md
reviews/M6a-claude-r3.md
reviews/M6a-v3-claude-r2.md
reviews/M6a-v2-codex-r1.md
reviews/M6-site-codex-r2.md
reviews/M6-site-claude-r3.md
reviews/M6a-codex-r3.md
reviews/PROPOSED-DECISIONS-M6c-1.md
r
### Shell: `'rg --files src/newregime src/live tests scripts | sort'`
rg: src/newregime: No such file or directory (os error 2)
rg: src/live: No such file or directory (os error 2)
scripts/__init__.py
scripts/build_live_seed.py
scripts/build_map.py
scripts/build_site.py
scripts/collect_api.py
scripts/export_live_model.py
scripts/export_predictions.py
scripts/run_all.py
scripts/run_extras.py
scripts/run_improve.py
scripts/run_m10.py
scripts/run_newregime.py
tests/conftest.py
tests/test_api_loader.py
tests/test_baselines.py
tests/test_collect.py
tests/test_config.py
### Shell: `'nl -ba src/newregime/pipeline.py'`
nl: src/newregime/pipeline.py: No such file or directory

### Shell: `'nl -ba plans/site-redesign-definition.md; nl -ba src/regions.py'`
     1	# Site redesign — definition (grilling session with the human, 2026-10-18)
     2	
     3	Status: agreed with the human in chat ("all agreed", "agreed, also go for round with codex"). Lines marked **[rule]**
     4	change an existing D-entry (proposed or ratified); they are the human's decisions and are proposed in
     5	`reviews/PROPOSED-DECISIONS-site.md`. Lines marked PROVISIONAL are design defaults for the milestone plans (D-026).
     6	Work starts from `main` after the merge of M6a
### Shell: `'cat tests/test_newregime_leakage.py'`
"""M6c-1 leakage audit (ts-leakage-audit skill; plans/M6c-1.md §8 tests 11–15) on the REAL datastore, with per-type
negative controls."""
import numpy as np
import pandas as pd
import pytest

from src import baselines as B, config, grid, regions
from newregime import blend, data as nd, frames as F, pipeline as P
from newregime import baselines as NB

ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
H1 = pd.Timedelta(hours=1)
SPLIT = P.first_split()
# one in each split, right after the 7-d 
### Shell: `'cat newregime/blend.py newregime/data.py'`
"""Rolling Brier-optimal blend weight (plans/M6-definition.md "Blend"; plans/M6c-1.md §6).

p_blend(t) = w(t) p_model(t) + (1 - w(t)) p_recent(t);  w(t) = n / (n + N0) * clip(w*, 0, 1);
w* = sum (p_b - y)(p_b - p_m) / sum (p_m - p_b)^2 over the window rows W(t): eligible rows s of all units with
s in [t - 28 d, t - H] and s >= the model's fit cut-off (no in-sample predictions); n = distinct type-T onset events
(unit, o) with o in (s, s + H] for some positive s in W(t). Before the cut-off, w = 0.
### Shell: `'nl -ba newregime/pipeline.py'`
     1	"""M6c-1 pipeline (plans/M6c-1.md): stage `fit` (no test label read) and stage `test` (the test week, scored ONCE).
     2	EXPLORATORY: alerts.in.ua history only, EVENT-TIME RECONSTRUCTION (not a replay of what was observed live), one test
     3	week. M6b reuses `fit(split, out_dir)` / `score_test(split, out_dir)` with its own Split."""
     4	import hashlib
     5	import json
     6	import os
     7	import platform
     8	import subprocess
     9	from dataclasses import asdict, dataclas
### Shell: `"rg -n 'reserve|overlap|test_start|test_end|version|first_seen|reconstruct|red_share' newregime tests/test_newregime.py scripts/build_live_seed.py netlify/live"`
newregime/data.py:78:    merged = _merge(holes)   # adjacent / overlapping holes cover a gap together
newregime/data.py:92:def load(store_path=DATASTORE, log_path=PULL_LOG, holes_path=HOLES, reconstruct_at=None, stats=None):
newregime/data.py:97:    at = cov.coverage_end if reconstruct_at is None else reconstruct_at
newregime/data.py:99:        raise data.DataQualityError(f"reconstruction time {at} after coverage_end {cov.coverage_end}")
newregime/data.py:101:    rec = ac.as_reconstructed_at(row
### Shell: `'cat newregime/blend.py newregime/data.py'`
"""Rolling Brier-optimal blend weight (plans/M6-definition.md "Blend"; plans/M6c-1.md §6).

p_blend(t) = w(t) p_model(t) + (1 - w(t)) p_recent(t);  w(t) = n / (n + N0) * clip(w*, 0, 1);
w* = sum (p_b - y)(p_b - p_m) / sum (p_m - p_b)^2 over the window rows W(t): eligible rows s of all units with
s in [t - 28 d, t - H] and s >= the model's fit cut-off (no in-sample predictions); n = distinct type-T onset events
(unit, o) with o in (s, s + H] for some positive s in W(t). Before the cut-off, w = 0.
### Shell: `"rg -n 'as_reconstructed_at|def .*version|latest' collect/api_collector.py; cat newregime/frames.py"`
562:def _latest_per_id(rows):
572:    """OBSERVED view: what this collector had seen at t. (1) fetched_at <= t, (2) latest updated_at per id (D-027),
575:        return _latest_per_id(rows)
577:    return [r2 for r in _latest_per_id(seen) if (r2 := _hide_future(r, t)) is not None]
580:def as_reconstructed_at(rows, t):
583:    return [r2 for r in _latest_per_id(rows) if (r2 := _hide_future(r, t)) is not None]
"""Per type x H: grid (y, mask), features known at t and `other_level_active_at_t` -> on
### Shell: `"rg -n 'test_|HORIZONS|H1|hours=3|purge|gap|DST|share|overlap' tests/test_newregime.py tests/test_live_parity.py tests/test_live_typed_parity.py; rg --files netlify | rg 'check|forecast|archive|histor`
tests/test_live_typed_parity.py:23:GAPS = config.mask_gaps(CFG)
tests/test_live_typed_parity.py:84:    long = y[(y.finished_at - y.started_at) > pd.Timedelta(hours=30)]
tests/test_live_typed_parity.py:118:        return "data_gap"
tests/test_live_typed_parity.py:122:def test_js_typed_baseline_matches_python(api):
tests/test_live_typed_parity.py:142:    assert states.get("level_active", 0) > 0 and states.get("data_gap", 0) > 0 and states.get("forecast", 0) > 0
tests/test_live_typed_parity.py:146:
### Shell: `"rg -n --glob '*.py' --glob '*.mjs' 'HORIZON|horizon|alert_types|model_version|forecast_time|red_share|trained_through|28' netlify/live/lib netlify/functions scripts/build_live_seed.py scripts/export_`
netlify/live/lib/live.mjs:276:  return { tau, horizon_minutes: 60, units, model: { features: model.feature_names }, typed: typed.meta };
netlify/live/lib/typed.mjs:12:export const HORIZON_MINUTES = 60;
netlify/live/lib/typed.mjs:31:  if (!Array.isArray(m.alert_types) || JSON.stringify([...m.alert_types].sort()) !== JSON.stringify([...TYPED_ALERT_TYPES].sort()))
netlify/live/lib/typed.mjs:32:    throw new Error(`typed model ${m.version}: alert_types ${m.alert_types} != ${TYPED_ALERT_TYPES}`);
net
### Shell: `"sed -n '350,490p' newregime/pipeline.py; cat reviews/PROPOSED-DECISIONS-M6c-1.md"`
                         "holes": [[str(a), str(b)] for a, b in ctx.cov.holes]},
            "loader": ctx.stats, "alert_range": [str(ctx.alerts.started_at.min()), str(ctx.alerts.started_at.max())],
            "frames": {f"{k[0]}_h{k[1]}": list(v.shape) for k, v in ctx.frames.items()},
            "eligibility": {f"{k[0]}_h{k[1]}": v["counts"] for k, v in arts.items()},
            "inputs_sha256": input_hashes(paths), "code_fingerprint": code_fingerprint(),
            "features": {typ: F.feat
### Shell: `"sed -n '1,130p' netlify/live/lib/check.mjs; sed -n '1,155p' netlify/functions/update-forecast.mjs; sed -n '560,590p' collect/api_collector.py"`
// Live forecast check and history (plans/M11.md §A2-§A3). Pure functions: no network, no storage, no token.
// EXPLORATORY: API data, its own section, never mixed with the study's official metrics (D-007, D-015).
import { unitIntervals, covered } from "./features.mjs";
import { knownAt, coverageAt } from "./live.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR;
export const SETTLE = 3 * HOUR;               // a snapshot is scored only from tau + 1 h + SETTLE on
export const LATE_AFTER 
### Shell: `"sed -n '1,140p' tests/test_live_parity.py; sed -n '1,90p' netlify/live/lib/typed.mjs; rg -n 'HOUR|horizon|model|key|tau|forecast' netlify/live/lib/check.mjs | tail -65"`
"""M8 parity (plans/M8.md §5): the JavaScript live inputs and offset equal the Python definitions on the real API dump
(all alert types) at many moments tau, incl. edge cases; the JS tree evaluator is covered by node tests."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from improve import live_ref
from src import config, data, features, grid

ROOT = Path(__file__).resolve().parents[1]
CFG = config.new_regime_all_types()
ZONES = c
I’ll read the priority documents and leakage-audit rules, then check relevant code for claims the plans rely on.
I’m applying the leakage-audit skill’s causality and cutoff checks. The site definition records human approval for several rule changes, so I’ll distinguish those amendments from unresolved contradictions.
The definitions leave unresolved how to align the live map’s alert types with M6c-1, define “red given an onset,” and replay the test week from frozen inputs. I’m checking the existing scorer and tests for assumptions that could break when adding horizons.
## BLOCKERS

- “Same target … same mask” (site L49) conflicts with proposed D-040: live “any” includes all API alert types; M6c-1 uses air-raid only. Specify one alert-type contract for labels, masks, features, baseline and scorer; explicitly amend D-040.
- “P(red | onset)” (site L67) is undefined when red starts during yellow or both start together. The typed red model predicts a different, unconditional event. Define the conditioning event, colour assignment and simultaneous-onset policy; compare replacement models on identical conditional outcomes.
- “M11 scorer, counted since launch” (site L31) cannot support the proposed horizons unchanged: `check.mjs` hard-codes one-hour labels and aggregates without model/target separation. Version snapshots and archives by target, horizon and model; score through t+H with maturity and coverage checks.
- “Regenerate … from the frozen … models” (site L70) does not freeze inputs or blend history. Later corrections can change replay. Pin original input hashes, code, calibrators, baseline tables and weight histories; label this retrospective reconstruction, since the models were unavailable during that week.

## AMBIGUITIES

- “Last 7 days” (site L52): define elapsed UTC bounds, merged onset counting, incomplete coverage, unknown colours and N=0 behaviour. Fit the national comparison share using training data only.
- “Export … blend state” (site L65): specify state per model/horizon, exclude in-sample predictions, deduplicate onset counts and admit labels only where s+H≤t. Define reset/reconstruction on monthly replacement.
- “NEW, later test week” (site L62): pin exact UTC train/validation/test boundaries and reservation scope. State whether test-end limits forecast times or target windows; retain t+H=cutoff under D-022/D-025.

## MISSING

- “JS–Python parity tests” (site L66) can pass with identical leakage in both implementations. Require independent truncation and mutation controls for every horizon: starts at t/t+H, purge equality, future `finished_at`, standing-alert cap, DST, 29 Aug–2 Sep gap edges and separate Kyiv City/Kyivska identities.
- D-017/D-024: require run metadata, exclusion counts and identical eligible support for model/baseline comparisons. “Evaluate them like H=1/3” should explicitly require reliability plots and within-oblast AUC.

## QUESTIONS FOR THE HUMAN

- D-027’s latest-version merge conflicts with strict knowledge-at-t when revisions arrive later; the existing reconstruction audit retains those revisions on both sides. Authorize observed-version replay or explicitly document the retrospective exception.
- Proposed D-040 names both M6-site and M6c-1 decisions. Assign unique numbers and reconcile approved amendments with CLAUDE.md before implementation.

VERDICT: CHANGES REQUIRED
