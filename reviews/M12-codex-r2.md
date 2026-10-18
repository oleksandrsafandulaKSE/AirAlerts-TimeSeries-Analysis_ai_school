### Shell: `'cat plans/M12.md reviews/M12-codex-r1.md reviews/M12-claude-r1.md plans/site-redesign-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M12 plan v1 — New-regime models for the redesigned map: "any" H = 6/12/24, live export, versioned scorer, red-share check, replay data

## Status and authority
- Definition: `plans/site-redesign-definition.md` (Claude–Codex consensus round 3, `VERDICT: AGREE`;
  `reviews/site-redesign-definition-consensus.md`). Proposed decisions D-041 … D-045 in `reviews/PROPOSED-DECISIONS-site.md`.
- **Human, chat 2026-10-18:** "Approve D-045: the main map (any target, masks, features, baseline, scorer) uses
### Shell: `'tail -n 90 reviews/M12-codex-r1.md'`
   245	
   246	def metrics(scored, typ, H, split_name, cfg):
   247	    table, reasons = evaluate.metric_table(scored, predictors(scored), "recent_rate", cfg.min_class_per_unit)
   248	    table = evaluate.low_n_flags(table, cfg.low_n_rows).rename(columns={"baseline": "predictor"})
   249	    table.insert(0, "split", split_name)
   250	    table.insert(0, "H", H)
   251	    table.insert(0, "type", typ)
   252	    if split_name == "test":
   253	        notes = {"blend": "causal; w driven by the 
### Shell: `'cat reviews/M12-claude-r1.md'`
# M12 — Claude response, round 1

## Changes made
- B1 Split: AGREE (verified pipeline.py:49 val end = test start). New frozen `M12Split` with an unused gap [10-11, 10-18); order check stated.
- B2 blend history: AGREE. Operational weight cut-off = validation end; seed starts 10-11; M6c-1 train-end weights only for replay.
- B3 reserved-week exposure: AGREE. Seed T_seed = test start; parity τ + H ≤ test start; no m12-series metric computed/stored/shown while the flag is absent; switch only after
### Shell: `'cat CLAUDE.md plans/site-redesign-definition.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"rg --files -g AGENTS.md -g '*DECISIONS*' -g '*blend*' -g '*pipeline*' -g '*data*' -g '*check*' -g '*preregistration*' .claude newregime netlify reports/m6c1 reviews"`
newregime/data.py
newregime/pipeline.py
newregime/blend.py
reports/m6c1/blend_weights.csv
reports/m6c1/preregistration.json
netlify/functions/check.mjs
reviews/M1c-exact-1h-check-codex-r1.md
reviews/M1c-exact-1h-check-consensus.md
reviews/M1c-exact-1h-check-claude-r1.md
reviews/PROPOSED-DECISIONS-M6c-1.md
reviews/PROPOSED-DECISIONS-M4-M5.md
reviews/M1c-exact-1h-check-codex-r1.log
netlify/live/lib/check.mjs
reviews/PROPOSED-DECISIONS-site.md
reviews/PROPOSED-DECISIONS-M6.md
netlify/live/test/chec
### Shell: `'nl -ba netlify/live/lib/check.mjs'`
     1	// Live forecast check and history (plans/M11.md §A2-§A3). Pure functions: no network, no storage, no token.
     2	// EXPLORATORY: API data, its own section, never mixed with the study's official metrics (D-007, D-015).
     3	import { unitIntervals, covered } from "./features.mjs";
     4	import { knownAt, coverageAt } from "./live.mjs";
     5	
     6	const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR;
     7	export const SETTLE = 3 * HOUR;               // a snapshot is scored only fr
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
### Shell: `'cat newregime/blend.py newregime/data.py reviews/PROPOSED-DECISIONS-M6c-1.md reports/m6c1/preregistration.json'`
"""Rolling Brier-optimal blend weight (plans/M6-definition.md "Blend"; plans/M6c-1.md §6).

p_blend(t) = w(t) p_model(t) + (1 - w(t)) p_recent(t);  w(t) = n / (n + N0) * clip(w*, 0, 1);
w* = sum (p_b - y)(p_b - p_m) / sum (p_m - p_b)^2 over the window rows W(t): eligible rows s of all units with
s in [t - 28 d, t - H] and s >= the model's fit cut-off (no in-sample predictions); n = distinct type-T onset events
(unit, o) with o in (s, s + H] for some positive s in W(t). Before the cut-off, w = 0.
### Shell: `"rg --files -g AGENTS.md -g '"'!air-alert-forecasting-research/**'"' -g '"'!node_modules/**'"' .; nl -ba plans/M12.md"`
     1	# M12 plan v1 — New-regime models for the redesigned map: "any" H = 6/12/24, live export, versioned scorer, red-share check, replay data
     2	
     3	## Status and authority
     4	- Definition: `plans/site-redesign-definition.md` (Claude–Codex consensus round 3, `VERDICT: AGREE`;
     5	  `reviews/site-redesign-definition-consensus.md`). Proposed decisions D-041 … D-045 in `reviews/PROPOSED-DECISIONS-site.md`.
     6	- **Human, chat 2026-10-18:** "Approve D-045: the main map (any targe
### Shell: `"sed -n '1,155p' netlify/live/lib/check.mjs; rg -n 'tau:|snapshot|forecastAll|hour' netlify/live/lib/runner.mjs netlify/live/lib/live.mjs | head -n 65; sed -n '140,245p' newregime/pipeline.py"`
// Live forecast check and history (plans/M11.md §A2-§A3). Pure functions: no network, no storage, no token.
// EXPLORATORY: API data, its own section, never mixed with the study's official metrics (D-007, D-015).
import { unitIntervals, covered } from "./features.mjs";
import { knownAt, coverageAt } from "./live.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR;
export const SETTLE = 3 * HOUR;               // a snapshot is scored only from tau + 1 h + SETTLE on
export const LATE_AFTER 
### Shell: `"cat reviews/PROPOSED-DECISIONS-M6.md; sed -n '550,605p' collect/api_collector.py; sed -n '265,345p' newregime/pipeline.py; head -n 3 reports/m6c1/blend_weights.csv; git status --short"`
# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow c
I’ll read the updated plan and response against the previous review, then check the provisional decisions against the project rules and leakage requirements.
The update addresses most earlier concerns. Two need closer checking: replay tests still lack an explicit check of each row’s predictions, and scoring all nine models may expand the definition’s reservation “scoped to the new horizons.”
The loader exposes a material gap: `nd.load(reconstruct_at=...)` does not filter by `fetched_at`, so the proposed fit pinning needs an explicit filter. The plan also retains conflicting cutover and red-share instructions. I’m applying the leakage-audit skill to the snapshot timing check: M11 scores from the actual issue time, while M12’s blend history uses the hour boundary.
## PREVIOUS ITEMS

- B1 — RESOLVED: `M12Split` permits the unused gap.
- B2 — RESOLVED: operational blend history starts at validation end.
- B3 — RESOLVED: seed, parity and shadow-metric gates protect reserved-week outcomes.
- B4 — OPEN: §A incorrectly assumes `nd.load(reconstruct_at=T_fit)` filters `fetched_at`. `newregime/data.py` passes all versions to `collect/api_collector.py::as_reconstructed_at`, which selects latest versions without that filter. Explicitly filter the pinned inputs before reconstruction; prefix hashes alone cannot prevent later versions changing the fit.
- A1 — RESOLVED: version keys and prefix-hash checks replace `first_seen`.
- A2 — OPEN: §B keys live rows by the snapshot’s hour; M11 scores from actual `snap.tau` (`check.mjs`). A 10:05 prediction assigned to 10:00 can use information inside its supposed outcome window. Preserve actual issue time for labels, maturity and blending; use the hour only for identity.
- A3 — OPEN: §C retains onset-time windows for coverage, exclusions and the national comparator, alongside hourly windows for the displayed rule. Apply the hourly timestamp consistently to both predictors and eligibility.
- M1 — RESOLVED: feature/mask equality and independent mutations are required.
- M2 — OPEN: Testing checks keys and hourly weights, neither of which changes when prediction values alone are swapped. Require independent, keyed per-row prediction comparisons.
- M3 — RESOLVED: the leakage report is required before metrics.
- Q1 — ACCEPTED: the agreed definition permits retrospective revisions with separate provenance.
- Q2 — OPEN: §E restores cutover within M12, but §0 still explicitly excludes it. Remove that contradiction.

## PROVISIONAL DECISIONS

- Gap, two-session schedule and validation-end blend history stay within the agreed design; reconstruction provenance adds no exception.
- Scoring all nine models expands the definition’s reservation “scoped to the new horizons.” This changes evaluation scope; D-026 requires human approval or restoration of the agreed scope.

## NEW ISSUES

- §B’s seed/live boundary loses rows: seed eligibility ends at `T_seed − H`, while live inclusion requires `s > T_seed`. Rows in `(T_seed − H, T_seed]` never enter blend history after maturing. Specify backfill and test this seam.

VERDICT: CHANGES REQUIRED
