### Shell: `'wc -l plans/M12.md plans/site-redesign-definition.md reviews/PROPOSED-DECISIONS-site.md plans/M6-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
     145 plans/M12.md
     124 plans/site-redesign-definition.md
      23 reviews/PROPOSED-DECISIONS-site.md
      57 plans/M6-definition.md
     156 CLAUDE.md
     301 DECISIONS.md
      30 .claude/skills/ts-leakage-audit/SKILL.md
     836 total

### Shell: `'cat plans/M12.md plans/site-redesign-definition.md reviews/PROPOSED-DECISIONS-site.md plans/M6-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M12 plan v1 — New-regime models for the redesigned map: "any" H = 6/12/24, live export, versioned scorer, red-share check, replay data

## Status and authority
- Definition: `plans/site-redesign-definition.md` (Claude–Codex consensus round 3, `VERDICT: AGREE`;
  `reviews/site-redesign-definition-consensus.md`). Proposed decisions D-041 … D-045 in `reviews/PROPOSED-DECISIONS-site.md`.
- **Human, chat 2026-10-18:** "Approve D-045: the main map (any target, masks, features, baseline, scorer) uses
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `'nl -ba DECISIONS.md | head -n 115'`
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
### Shell: `'cat reviews/PROPOSED-DECISIONS-site.md plans/M6-definition.md'`
# Proposed DECISIONS.md entries — site redesign (the human edits and commits; see plans/site-redesign-definition.md)

## D-041 — Site redesign: one job per page (me, 2026-10-18, grilling session)
- The main page is the interactive oblast map "Will there be an alert in 1 / 3 / 6 / 12 / 24 h?"; study evidence moves to
  tabs (Replay, Forecast check, How good is it?, What kind of alert?, About) and the README. Oblasts only; English only;
  current visual system.

## D-042 — Live map model = M6c-1 "
### Shell: `'nl -ba plans/site-redesign-definition.md | tail -n 54
'`
    71	  - Accuracy (exploratory, API): Brier and within-oblast AUC (≥ 10/10, D-025) of the rule vs the national share.
    72	- **[rule] Yellow/red on the site**: hover note + click card + a separate page (amends D-036/D-040 "hover only").
    73	  Always labelled "in testing / in training".
    74	
    75	## Milestones (order agreed)
    76	1. **M12 — models and live export.**
    77	   - Add H = 6, 12, 24 to the "any" pipeline (`newregime/pipeline.py` has `HORIZONS = (1 h, 3 h)` hard-coded).

### Shell: `"rg --files -g AGENTS.md -g '*DECISIONS*' -g '*blend*' -g '*leakage*' -g '*preregistration*' -g '*pipeline*' -g '*data*' -g '*check*' -g '*typed*' -g '*live*' -g '*runner*' -g '*access*' newregime net`
newregime/data.py
newregime/pipeline.py
newregime/blend.py
netlify/functions/check.mjs
reports/extras/onset_collapse_check.csv
tests/test_live_assets.py
tests/test_data.py
tests/test_live_typed_site.py
tests/test_live_typed_parity.py
tests/test_newregime_leakage.py
tests/test_m10_leakage.py
tests/test_leakage.py
tests/test_live_parity.py
tests/test_data_quality.py
tests/test_improve_leakage.py
reports/final_test_access.json
netlify/live/data/typed_monthly.json
netlify/live/lib/check.mjs
netlify/
### Shell: `'nl -ba newregime/pipeline.py | head -n 245'`
     1	"""M6c-1 pipeline (plans/M6c-1.md): stage `fit` (no test label read) and stage `test` (the test week, scored ONCE).
     2	EXPLORATORY: alerts.in.ua history only, EVENT-TIME RECONSTRUCTION (not a replay of what was observed live), one test
     3	week. M6b reuses `fit(split, out_dir)` / `score_test(split, out_dir)` with its own Split."""
     4	import hashlib
     5	import json
     6	import os
     7	import platform
     8	import subprocess
     9	from dataclasses import asdict, dataclas
### Shell: `'cat newregime/blend.py'`
"""Rolling Brier-optimal blend weight (plans/M6-definition.md "Blend"; plans/M6c-1.md §6).

p_blend(t) = w(t) p_model(t) + (1 - w(t)) p_recent(t);  w(t) = n / (n + N0) * clip(w*, 0, 1);
w* = sum (p_b - y)(p_b - p_m) / sum (p_m - p_b)^2 over the window rows W(t): eligible rows s of all units with
s in [t - 28 d, t - H] and s >= the model's fit cut-off (no in-sample predictions); n = distinct type-T onset events
(unit, o) with o in (s, s + H] for some positive s in W(t). Before the cut-off, w = 0.
### Shell: `'cat reviews/PROPOSED-DECISIONS-M6.md'`
# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow c
### Shell: `'cat newregime/data.py newregime/frames.py'`
"""Datastore -> shared alert format via the EVENT-TIME RECONSTRUCTION (plans/M6a.md §4.2); coverage and holes from the
pull log (plans/M6c-1.md §3); typed alert subsets (§4). Checks raise."""
import csv
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from collect import api_collector as ac
from src import data, regions

ROOT = Path(__file__).resolve().parents[1]
DATASTORE = ROOT / "datastore" / "alerts_in_ua.csv"
PULL_LOG = ROOT 
### Shell: `"rg --files -g AGENTS.md -g '*M11*' -g '*M12*' -g '*M6c*' -g '*audit*' -g '*forecast*' ."`
./air-alert-forecasting-research/results/forecast_comparison_tests.json
./plans/M6c-1.md
./plans/M12.md
./netlify/functions/update-forecast.mjs
./netlify/functions/forecast.mjs
./plans/M11.md
./reviews/M6c-1-codex-r3.log
./reviews/M12-codex-r1.log
./reviews/M6c-1-codex-r2.log
./reviews/M6c-1-codex-r2.md
./reviews/M6c-1-codex-r1.log
./reviews/M6c-1-codex-r3.md
./reviews/M11-codex-r1.md
./reviews/M11-consensus.md
./reviews/PROPOSED-DECISIONS-M6c-1.md
./reviews/M11-claude-r2.md
./reviews/M6c-1-clau
### Shell: `'cat netlify/live/lib/runner.mjs'`
// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";
import { scoreSnapshots, checkBlob, historyPayload, dayOfKey, KEEP, LATE_AFTER, LOOKBACK } from "./check.mjs";
import { validMonthly } from "./typed.mjs";

export const API = "https://api.alerts.in.ua/v1";
const HOUR = 3600e3, FETCH_TIMEOUT = 8000;
export const STORE_NAME = "airalert-live";

async
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
### Shell: `'cat netlify/live/lib/check.mjs'`
// Live forecast check and history (plans/M11.md §A2-§A3). Pure functions: no network, no storage, no token.
// EXPLORATORY: API data, its own section, never mixed with the study's official metrics (D-007, D-015).
import { unitIntervals, covered } from "./features.mjs";
import { knownAt, coverageAt } from "./live.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR;
export const SETTLE = 3 * HOUR;               // a snapshot is scored only from tau + 1 h + SETTLE on
export const LATE_AFTER 
### Shell: `"nl -ba newregime/pipeline.py | sed -n '245,510p'"`
   245	
   246	def metrics(scored, typ, H, split_name, cfg):
   247	    table, reasons = evaluate.metric_table(scored, predictors(scored), "recent_rate", cfg.min_class_per_unit)
   248	    table = evaluate.low_n_flags(table, cfg.low_n_rows).rename(columns={"baseline": "predictor"})
   249	    table.insert(0, "split", split_name)
   250	    table.insert(0, "H", H)
   251	    table.insert(0, "type", typ)
   252	    if split_name == "test":
   253	        notes = {"blend": "causal; w driven by the 
### Shell: `'nl -ba netlify/live/lib/runner.mjs | head -n 220'`
     1	// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
     2	import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";
     3	import { scoreSnapshots, checkBlob, historyPayload, dayOfKey, KEEP, LATE_AFTER, LOOKBACK } from "./check.mjs";
     4	import { validMonthly } from "./typed.mjs";
     5	
     6	export const API = "https://api.alerts.in.ua/v1";
     7	const HOUR = 3600e3, FETCH_TIMEOUT = 8000;

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
### Shell: `"rg -n 'as_reconstructed_at|first_seen|version_seen|updated_at|as_known_at' collect/api_collector.py
rg -n 'history|28|14|coverage|model|typed' netlify/live/lib/live.mjs netlify/live/lib/typed.mjs net`
3:One CSV row = one record VERSION, key (id, updated_at). Knowledge time of a version = `fetched_at` of the pull that
34:API_FIELDS = ("id", "location_title", "location_type", "started_at", "finished_at", "updated_at", "alert_type",
40:TIME_FIELDS = ("started_at", "updated_at", "finished_at")
43:COLUMNS = ["id", "updated_at", "requested_uid", "unit", "fetched_at", "pull_id", "location_type", "location_uid",
236:    parse_ts(rec["updated_at"], f"uid {uid} id {rec['id']} updated_at")
347:    by_ke
### Shell: `"sed -n '35,48p' collect/api_collector.py
sed -n '550,603p' collect/api_collector.py
sed -n '1,145p' netlify/live/lib/typed.mjs
cat .claude/skills/ts-leakage-audit/SKILL.md"`
              "location_oblast", "location_uid", "notes", "country", "alert_level", "location_title_en",
              "location_oblast_uid")
OPTIONAL_FIELDS = ("location_raion",)
INT_FIELDS = {"id", "location_oblast_uid"}
NULLABLE_FIELDS = {"finished_at", "notes", "country"}
TIME_FIELDS = ("started_at", "updated_at", "finished_at")
ALERT_LEVELS = {"yellow", "red"}

COLUMNS = ["id", "updated_at", "requested_uid", "unit", "fetched_at", "pull_id", "location_type", "location_uid",
           "locat
### Shell: `"rg -n 'leakage|baselines|required|out.of.sample|cut.off|reset' plans/M6c-1.md reviews/PROPOSED-DECISIONS-M6c-1.md
rg --files -g 'AGENTS.md' -g '"'!air-alert-forecasting-research/**'"' . /Users/oleksa`
plans/M6c-1.md:17:  feature / leakage / reporting rules.
plans/M6c-1.md:21:P(an ANY / YELLOW / RED alert starts in (t, t+H]), for H = 1 (headline) and H = 3. Report model, baselines and the
plans/M6c-1.md:24:with explicit cut-off dates so M6b (monthly job) reuses it unchanged.
plans/M6c-1.md:36:- `newregime/baselines.py` — per-type baselines (reuses `src.baselines`) + the red-share extra baseline.
plans/M6c-1.md:42:- `tests/test_newregime.py` (units, synthetic), `tests/test_newregime_leakage.py`
I’ll read the priority files first, then check relevant code for rule conflicts, leakage risks, and tests that could miss their target bugs.
The approved definitions already amend the older ban on API training. The key issue so far is that M12 leaves blend seeding unresolved, while the site definition explicitly requires out-of-sample rows. I’ll check the existing pipeline and live scorer to see which safeguards they actually provide.
I’m applying the leakage-audit skill. I found a concrete implementation conflict: M12’s validation ends on 11 October and its test starts on 18 October, but the `Split` class it proposes to reuse requires those boundaries to be equal. I’m also checking whether shadow scoring could expose the held-out week before its reserved test.
## BLOCKERS

- M12 §A “validation IDENTICAL” plus test starting 18 October cannot use the proposed `Split`: `pipeline.py:49` requires validation end = test start. Define an M12-specific split permitting the intervening week; keep the frozen pipeline untouched.
- §A “s ≥ the fit cut-off” and §B “blend_seed” include validation rows used for early stopping/calibration. This contradicts the site definition’s “only from out-of-sample rows.” Start operational blend history at validation end; retain historical M6c-1 weights only for faithful replay.
- §B “computes and archives” and §D automatic scoring allow inspection of the reserved week before §A’s once-only test (D-021/D-026). Gate shadow metrics, parity samples and seed rebuilds that expose held-out outcomes until the reserved evaluation.
- §A “hash of that prefix” cannot freeze reconstruction: later versions can change pre-fit alerts while leaving old rows intact (D-027). Pin fit/validation reconstruction to the fit snapshot; specify which later revisions evaluation may consume.

## AMBIGUITIES

- §A “first_seen” names no datastore column; versions use `fetched_at`. Define canonical version keys, ordering and hashes for datastore, pull-log and hole prefixes; test appends separately from edits/deletions.
- §B “extends it with archived live snapshots” leaves duplicate precedence, hourly versus actual issue times, and model replacement undefined. Specify row/event identity, overlap precedence, eligibility, 28-day eviction and reset per model version.
- §C “Rule at each onset” differs from the definition’s rule at forecast time t. Specify whether this evaluates onset-time classification or the displayed hourly conditional forecast; construct evaluation rows accordingly.

## MISSING

- Testing “identical p” can pass when a leaking feature stays within the same tree leaf. Assert feature and mask equality. Add independent mutations per horizon for future ends, the exact 24-hour cap, purge equality, DST folds, Kyiv City/Kyivska and coverage-hole edges; preserve D-022/D-023’s official August–September gap regressions.
- §F “metrics reproduction” can pass after swapping predictions between equivalent rows. Assert row keys, eligibility and pinned per-row predictions/weights.
- “Done when” omits the leakage skill’s required `check | PASS/FAIL | evidence` report. Require it before reporting metrics.

## QUESTIONS FOR THE HUMAN

- D-027 permits later revisions, conflicting with strict knowledge-at-t. Confirm reconstruction-only use and separate live provenance; retain the approved M6 exceptions to older API-training bans.
- §E “NOT executed in M12” differs from the agreed definition’s cutover within M12. Explicitly approve deferred activation or restore that deliverable.

VERDICT: CHANGES REQUIRED
