### Shell: `'cat plans/M13.md plans/site-redesign-definition.md plans/M12.md reviews/PROPOSED-DECISIONS-site.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M13 plan v1 — The redesigned site: one interactive map, the rest in tabs

## Status and authority
- Design: `plans/site-redesign-definition.md` (grilling with the human 2026-10-18 + Claude–Codex consensus round 3;
  D-041 … D-045 proposed, D-045 approved). Human, chat 2026-10-18: "do m13" (after: "so there is no new site yet?").
- Builds on M12 session 1 (`fb251fb`, branch `claude/m12-session1`; this work: branch `claude/m13-site`).
- **The M12 registry is INACTIVE until the switch** (after th
### Shell: `"wc -l plans/M13.md plans/site-redesign-definition.md plans/M12.md reviews/PROPOSED-DECISIONS-site.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md; rg --files -g AGENTS.md -g '*DECI`
     108 plans/M13.md
     124 plans/site-redesign-definition.md
     207 plans/M12.md
      23 reviews/PROPOSED-DECISIONS-site.md
     156 CLAUDE.md
     301 DECISIONS.md
      30 .claude/skills/ts-leakage-audit/SKILL.md
     949 total
DECISIONS.md
reviews/PROPOSED-DECISIONS-M6c-1.md
reviews/PROPOSED-DECISIONS-M4-M5.md
reviews/PROPOSED-DECISIONS-M6.md
reviews/PROPOSED-DECISIONS-site.md
reports/m12/leakage_audit.md
reports/leakage_evidence.json
reports/m6c1/leakage_audit.md
tests/test_leakage.py
### Shell: `'nl -ba CLAUDE.md; nl -ba reviews/PROPOSED-DECISIONS-site.md'`
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
### Shell: `'nl -ba plans/M12.md'`
     1	# M12 plan v1 (AGREED, consensus round 4, D-026; reviews/M12-consensus.md) — New-regime models for the redesigned map: "any" H = 6/12/24, live export, versioned scorer, red-share check, replay data
     2	
     3	## Status and authority
     4	- Definition: `plans/site-redesign-definition.md` (Claude–Codex consensus round 3, `VERDICT: AGREE`;
     5	  `reviews/site-redesign-definition-consensus.md`). Proposed decisions D-041 … D-045 in `reviews/PROPOSED-DECISIONS-site.md`.
     6	- **Huma
### Shell: `"sed -n '1,79p' DECISIONS.md; sed -n '50,145p' plans/M12.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"sed -n '146,220p' plans/M12.md; sed -n '112,145p' plans/site-redesign-definition.md; rg --files newregime netlify/live netlify/functions tests scripts site_src | rg '(redshare|kind|site|replay|check|`
## F. Replay data (retrospective reconstruction of the M6c-1 test week)
- Inputs pinned: the datastore, pull log and holes files at commit aa05529 (`git show`), the M6c-1 artefacts
  (sha256 per `reports/m6c1/preregistration.json`), code commit. Output
  `reports/m12/replay_m6c1_any.csv`: unit, t, status, y, p_model, p_baseline, w, p_blend for H = 1 and 3 over
  [10-11, 10-17 19:00).
- No reservation is created or touched; no new metric is reported. Consistency test: recomputing the published
  
### Shell: `'cat newregime/redshare.py; cat netlify/functions/check.mjs; cat netlify/live/lib/runner.mjs'`
"""M12 §C (plans/M12.md): "if an alert starts, will it be red?" — the 7-day red-share rule, evaluated as the hourly
forecast the page would have shown just before each "any" onset. EXPLORATORY, API data (air-raid only, D-040/D-045).

Event: an "any" onset = the start of a merged air-raid interval (D-020 cap). Colour: red iff a red air-raid alert of that
unit starts at that instant (simultaneous red + yellow -> red); a red that starts inside a running interval is an
escalation, not an onset. For 
### Shell: `"cat netlify/live/lib/typed.mjs; sed -n '1,235p' netlify/live/lib/live.mjs"`
// M6 typed forecasts on the live site (plans/M6-site.md §3, §5): per alert level (yellow = drones, red = missiles), the
// rolling recent-rate baseline at tau, blended with a typed model once one exists (w = 0 until then). Pure functions.
import { unitIntervals, offsetAt, covered } from "./features.mjs";
import { coverageAt, holes, levelAt } from "./live.mjs";     // import cycle is safe: only used inside functions
// Yellow/red count air-raid alerts only (human decision, chat 2026-10-18, D-040
### Shell: `"rg -n 'def build_replay|replay|parity.*red|redshare_rows|redshare' newregime/horizons.py scripts/run_m12.py scripts/build_site.py tests/test_m12*; head -n 5 reports/m12/replay_m6c1_any.csv; head -n 4`
scripts/run_m12.py:4:    python scripts/run_m12.py --redshare   # the 7-day red-share rule check (onsets before the reserved week)
scripts/run_m12.py:5:    python scripts/run_m12.py --replay     # M6c-1 test-week reconstruction for the Replay tab (no new score)
scripts/run_m12.py:24:from newregime import blend, data as nd, frames as F, horizons as HZ, pipeline as P, redshare as RS  # noqa: E402
scripts/run_m12.py:30:def stage_redshare(out):
scripts/run_m12.py:36:    sc.to_csv(out / "redshare_row
### Shell: `"rg --files netlify/live/model/m12 reports/m12 | head -n 55; sed -n '455,525p' newregime/horizons.py; sed -n '25,46p' scripts/run_m12.py; sed -n '1,115p' newregime/data.py; sed -n '565,655p' tests/tes`
netlify/live/model/m12/model_any_h6.json
netlify/live/model/m12/model_yellow_h3.json
netlify/live/model/m12/model_any_h12.json
netlify/live/model/m12/model_any_h1.json
netlify/live/model/m12/model_any_h24.json
netlify/live/model/m12/model_red_h1.json
netlify/live/model/m12/model_yellow_h1.json
netlify/live/model/m12/model_any_h3.json
netlify/live/model/m12/model_red_h3.json
netlify/live/model/m12/blend_seed.json
netlify/live/model/m12/parity_sample.json
netlify/live/model/m12/registry.json
netli
### Shell: `"rg -n 'PARITY_RECORDS|parity_records|firstSeen|endKnown|levels|levelCoverage|def parity' scripts/export_m12_models.py newregime/horizons.py netlify/live/test/m12.test.mjs netlify/live/lib/models.mjs;`
rg: scripts/export_m12_models.py: No such file or directory (os error 2)
netlify/live/lib/models.mjs:65:    if (r.firstSeen > tau || r.start > tau || !MAIN_ALERT_TYPES.includes(r.alert_type)) continue;
netlify/live/lib/models.mjs:66:    const end = r.end !== null && r.endKnown !== null && r.endKnown <= tau && r.end <= tau ? r.end : null;
netlify/live/lib/models.mjs:180:  const covKey = type === "any" ? "coverage" : "levelCoverage";            // typed labels need confirmed levels
netlify/live/li
### Shell: `"sed -n '1,50p' netlify/live/test/m12.test.mjs; rg -n 'function historyPayload|version|return.*units|intervals|p_model' netlify/live/lib/check.mjs; sed -n '325,410p' netlify/live/lib/check.mjs; sed -n`
// M12 (plans/M12.md): the live model registry — parity with the Python pipeline per (type, H) on the real API
// reconstruction, independent truncation tests per H with a negative control, the air-raid filter (D-045), the inactive
// rule, the blend weight and the live labelling of pending rows.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { loadRegistry, registryAt, weightAt, labelRow, gapMasked, recentRate, calibrate
I’ll read the priority files first, then check the plan against the project rules, leakage requirements, and relevant code and tests.
I’m applying the leakage-audit skill to the new red-share path. M13 adds a live calculation, so I’ll check whether its parity tests can detect future-data use, along with the inactive-model and replay behavior.
The plan infers activation from a forecast field that the runner can omit on failure, which could make the page show M8 again after cutover. It also promises an M12 history strip through an unchanged endpoint that reads only M8 snapshots. I’m checking the remaining findings for concrete fixes within M13’s scope.
## BLOCKERS

- **M13:29, “forecast.m12.active === true”:** `runner.mjs` can omit this field when the active path throws. The page could silently revert to M8. Expose activation independently of prediction success; render failures explicitly and test active-but-failed payloads.

- **M13:72, “history unchanged,” versus :103, “until … 7 days”:** `/api/history` reads M8 snapshots only. It cannot deliver the promised M12 strip. Add versioned M12 history with matching air-raid observations, or explicitly retain the labelled M8 strip indefinitely.

- **M13:79–80, “equals Python … exactly”:** the M12 parity fixture assumes records and levels were known at their starts. Agreement cannot establish live knowledge-at-τ correctness. Separate reconstruction parity from independent tests of delayed discovery, level updates, coverage confirmation and unknown ends.

## AMBIGUITIES

- **M13:40–41, “Running pooled Brier … equals … BSS”:** these are different quantities. Specify BSS as `1 − SSE_blend/SSE_baseline`, identical eligible support, and undefined-denominator behavior. Define whether prefixes include forecast origins or only outcomes matured by the slider; label retrospective outcome previews explicitly.

- **M13:77–78, “national share”:** specify inclusion of partially covered units, unresolved levels, pooling by onset versus averaging unit shares, and empty-national-window behavior. Follow M12 §C’s fully covered-unit restriction.

- **M13:32, “likely yellow”:** define the threshold, tie behavior and missing-data wording. **M13:56, “5 bins,”** also conflicts with D-025’s ten fixed-width bins; use ten or identify an approved exception.

- **M13:27, “M8, official data”:** M8 is officially trained but uses live API inputs and accepts non-air-raid types. Label both provenance and the temporary target difference explicitly; the blanket “new air-raid” description is inaccurate before cutover.

## MISSING

- **M13:93, “parity”:** add truncation invariance and a deliberately leaky negative control for `kind.mjs`. Pin seven-day endpoints, future `finished_at`, standing alerts beyond 24h and DST. Retain D-022/D-023 recording-gap regressions and Kyiv City/Kyivska separation.

- **M13 §5:** add CLAUDE.md’s mandatory reviewer, D-026’s harness review, fixes, human summary and proposed decision entry.

## QUESTIONS FOR THE HUMAN

- **D-027 versus CLAUDE.md’s knowledge-at-t rule:** the definition treats latest-version deduplication as permission for later historical revisions. Identify the explicit approved retrospective exception and its scope; otherwise require acquisition-time reconstruction.

VERDICT: CHANGES REQUIRED
