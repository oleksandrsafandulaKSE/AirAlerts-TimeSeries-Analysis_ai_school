### Shell: `'cat plans/M6a.md reviews/M6a-v2-codex-r2.md reviews/M6a-v2-claude-r2.md plans/M6-definition.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
Stop losing new-regime history. a
### Shell: `"cat CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md; rg --files -g AGENTS.md -g '*SKILL.md' .claude"`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'cat reviews/M6a-v2-codex-r2.md reviews/M6a-v2-claude-r2.md'`
### Shell: `"pwd; rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g 'DECISIONS.md' -g 'M6a*' -g 'M6-definition.md' -g 'SKILL.md' plans reviews .claude 2>/dev/null"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/.claude/worktrees/m6a-collection-34a410
plans/M6-definition.md
reviews/M6a-claude-r2.md
plans/M6a.md
reviews/M6a-claude-r3.md
reviews/M6a-v2-codex-r1.md
reviews/M6a-codex-r3.md
reviews/M6a-codex-r2.md
reviews/M6a-consensus.md
reviews/M6a-codex-r1.log
reviews/M6a
### Shell: `'cat plans/M6-definition.md CLAUDE.md; cat plans/M6a.md | tail -90'`
# M6 — definition (grilling session with the human, 2026-10-17)

Status: agreed with the human in chat ("Yes, record it"). Lines marked **[rule]** change CLAUDE.md or an existing
D-entry. They are the human's decisions and are proposed as D-entries in `reviews/PROPOSED-DECISIONS-M6.md`; the human
edits and commits DECISIONS.md / CLAUDE.md. Lines marked PROVISIONAL are design defaults to be reviewed in the
milestone plans (Claude–Codex consensus, D-026).

## Goal
Keep collecting new-regime (yello
### Shell: `"pwd; rg --files -g AGENTS.md -g '*collect*' -g '*regions*'; cat .claude/skills/codex-plan-review/SKILL.md"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/.claude/worktrees/m6a-collection-34a410
src/regions.py
netlify/live/data/regions.json
tests/test_regions.py
---
name: codex-plan-review
description: Claude and Codex (a different model) iterate on a milestone PLAN (plans/<name>.md, milestone mode) or on the ROADMAP + README (roadmap mode) until they agree, without the human in the loop. Use whenever a plan is written or changed, before implementation. Max 5 rounds; es
### Shell: `"cat reviews/PROPOSED-DECISIONS-M6.md; sed -n '100,155p' CLAUDE.md; sed -n '110,265p' src/data.py"`
# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow c
### Shell: `"nl -ba plans/M6a.md | sed -n '65,110p'; nl -ba plans/M6a.md | sed -n '181,202p'; rg -n 'PROVISIONAL|D-03|escape|encoding|reconstruction' reviews/M6a-v2-claude-r1.md reviews/M6a-consensus.md DECISIONS`
    65	## 4. Datastore and merge
    66	### 4.1 `datastore/alerts_in_ua.csv`, one row = one record VERSION
    67	Columns, fixed order: `id, updated_at, requested_uid, unit, fetched_at, pull_id, location_type, location_uid,
    68	location_oblast, location_oblast_uid, location_raion, location_title, location_title_en, alert_type, alert_level,
    69	started_at, finished_at, notes, country`.
    70	- Canonical types (checked at validation, raise otherwise): `id`, `location_oblast_uid` = int; `loc
I’ll read the updated plan and round-two exchange, then check each prior item and provisional decision against the repository rules and leakage-audit skill.
The revised escape scheme handles the reserved-string collision, and the raion test now distinguishes an absent field from explicit null. I’m checking that the remaining provisional choices stay within M6a’s collection scope.
## PREVIOUS ITEMS

- B1 — RESOLVED: Empty notes survive serialization and reload (§4.1, §6.8).
- A1 — RESOLVED: Decoded canonical values govern comparisons and remerging.
- A2 — RESOLVED: Dispatch requires 24 additional log rows for its pull.
- A3 — RESOLVED: `git_commit` identifies checkout HEAD before collection.
- M1 — RESOLVED: Separate future-start/end witnesses cover truncation boundaries.
- M2 — RESOLVED: Retry counts and sanitized diagnostics cover exhausted attempts.
- M3 — RESOLVED: Per-unit ranges, overall ranges and EMPTY responses are specified.
- Q — RESOLVED: Observed replay and event-time reconstruction remain explicitly distinguished.
- Serialization blocker — RESOLVED: Backslash escaping represents every allowed string, including the former reserved literal (§4.1).
- Raion test contradiction — RESOLVED: §6.8 tests absence separately from explicitly null values, which still raise.

## PROVISIONAL DECISIONS

- **Backslash encoding:** Within D-016/D-017. This changes storage representation, preserves source values and introduces no dependency or modelling rule change.
- **Event-time reconstruction:** Compatible with D-027 and the existing leakage-audit truncation procedure as retrospective analysis. It does not establish historical availability of corrections or approve M6c-1’s evaluation protocol.
- **Future M6 defaults:** Pooled blend weight, 28-day window, n₀=50, typed merged onsets, per-type recent-rate baseline, red-share comparison, reporting thresholds and feature defaults remain deferred to their milestone plans. Typed targets/masking, API training, immediate training, milestone order and site scope are rule changes, separately identified as human decisions in M6-definition and proposed D-033–D-037. M6a consensus does not authorize those amendments.

## NEW ISSUES

None introduced by these changes. The encoding’s null, empty-string and leading-backslash representations are distinct; rejecting an unescaped reserved prefix on disk detects corruption without rejecting valid API strings.

VERDICT: AGREE
