### Shell: `'cat .claude/skills/ts-leakage-audit/SKILL.md'`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `'cat reviews/M6a-v3-codex-r2.md'`
### Shell: `'cat plans/M6a.md reviews/M6a-v3-codex-r1.md reviews/M6a-v3-claude-r1.md reviews/PROPOSED-DECISIONS-M6.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `'cat reviews/PROPOSED-DECISIONS-M6.md'`
# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow c
### Shell: `'cat plans/M6a.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
Stop losing new-regime history. a
### Shell: `'cat CLAUDE.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'cat reviews/M6a-v3-claude-r2.md'`
# M6a v3 — Claude, round 2 response

Judgements on reviews/M6a-v3-codex-r2.md:
- M1 (the workflow commit routing is only checked statically): AGREE. A local bare repo as `origin` needs no network.
- New issue (recovery when the holes file is untracked): AGREE. Verified: `git ls-files reports/collect` lists only
  `pull_log.csv`.

## Changes made
- §4.4: the holes file always exists and is tracked. Every write, the seed included, writes at least the header,
  and M6a commits the header-only file 
### Shell: `'cat reviews/M6a-v3-codex-r2.md'`
### Shell: `'cat plans/M6a.md reviews/M6a-v3-codex-r1.md reviews/M6a-v3-claude-r1.md reviews/PROPOSED-DECISIONS-M6.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup
### Shell: `'cat reviews/M6a-v3-claude-r2.md'`
# M6a v3 — Claude, round 2 response

Judgements on reviews/M6a-v3-codex-r2.md:
- M1 (the workflow commit routing is only checked statically): AGREE. A local bare repo as `origin` needs no network.
- New issue (recovery when the holes file is untracked): AGREE. Verified: `git ls-files reports/collect` lists only
  `pull_log.csv`.

## Changes made
- §4.4: the holes file always exists and is tracked. Every write, the seed included, writes at least the header,
  and M6a commits the header-only file 
### Shell: `'cat reviews/PROPOSED-DECISIONS-M6.md'`
# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow c
### Shell: `'cat CLAUDE.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"cat .github/workflows/collect_api.yml; sed -n '1,240p' scripts/collect_api.py"`
# M6a: daily alerts.in.ua history pull -> datastore/alerts_in_ua.csv + reports/collect/pull_log.csv (plans/M6a.md §5).
# No push / pull_request triggers: the job holds a secret and may run on a self-hosted runner (public repo).
name: collect-api

on:
  schedule:
    - cron: "17 3 * * *"        # 03:17 UTC daily (off the hour; GitHub may delay scheduled runs)
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: collect-api
  cancel-in-progress: false

jobs:
  collect:
    #
### Shell: `"nl -ba plans/M6a.md | sed -n '175,320p'"`
   175	- 403 fallback (only if the manual run gets 403): the human registers a self-hosted runner (e.g. the human's Mac, label
   176	  `collect`) and sets `COLLECT_RUNNER=collect`. Because the repo is PUBLIC, the runner must only take this workflow:
   177	  no `pull_request` triggers anywhere in the repo for that label, and fork-PR workflows need approval (repo setting).
   178	  The Mac must be awake at 03:17 UTC; a missed day is absorbed by the 30-day window.
   179	
   180	## 6. Tests (`tes
### Shell: `"sed -n '1,100p' DECISIONS.md; sed -n '290,430p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"rg --files -g AGENTS.md -g '*consensus*' -g '*M6*' -g 'test_collect.py' -g 'api_collector.py'"`
collect/api_collector.py
tests/test_collect.py
plans/M6-definition.md
plans/M6a.md
reviews/M6a-claude-r1.md
reviews/M6a-v2-claude-r2.md
reviews/M3b-H3-consensus.md
reviews/M6a-claude-r2.md
reviews/M6a-claude-r3.md
reviews/M6a-v3-claude-r2.md
reviews/M6a-v2-codex-r1.md
reviews/M7-consensus.md
reviews/M6a-codex-r3.md
reviews/M6a-v3-codex-r2.md
reviews/M6a-v2-consensus.md
reviews/M6a-codex-r2.md
reviews/M6a-consensus.md
reviews/M6a-v2-codex-r3.log
reviews/M6a-codex-r1.log
reviews/M5b-consensus.md
r
### Shell: `'for p in /AGENTS.md /Users/AGENTS.md /Users/oleksandrsafandula/AGENTS.md /Users/oleksandrsafandula/Desktop/AGENTS.md /Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/AGENTS.m`

### Shell: `'cat reviews/M6a-v3-claude-r1.md; cat reviews/M6a-v2-consensus.md; cat reviews/M6a-consensus.md'`
# M6a v3 (gap-resume addendum) — Claude, round 1 response

Judgements on reviews/M6a-v3-codex-r1.md:
- B1 the crash repair leaves orphan hole rows: AGREE.
- B2 the workflow doesn't stage the holes file: AGREE. Verified: `.github/workflows/collect_api.yml` lists only the
  CSV and the log.
- A1 hole endpoints: AGREE. A2 stale §9 wording: AGREE.
- M1 executed exit-code tests: PARTLY (see Disagreements). M2 the holes path, missing file and dry-run: AGREE.
  M3 downstream contract: AGREE.

## Change
I’ll read the updated plan and responses first, then check each prior finding and provisional decision against the repository rules.
The revised §6.9 specifies executable workflow tests for exit codes 0, 3 and 1, addressing the remaining test concern. Creating and tracking the holes file from the start also fixes the recovery issue. That provisional choice fits within the recorded D-039 authorization.
## PREVIOUS ITEMS

- B1 — RESOLVED: §4.4/§6.9 cover restoring both files, including crashes with zero new alert rows.
- B2 — RESOLVED: §5 requires detecting, staging and committing all three files together.
- A1 — RESOLVED: open hole intervals have explicit endpoint tests.
- A2 — RESOLVED: §9 explicitly supersedes strict stopping with human-approved D-039.
- M1 — RESOLVED: §6.9 now requires executing the actual workflow shell against a local bare remote for codes 0/3/1, verifying publication, committed paths and failure ordering.
- M2 — RESOLVED: holes-file path, initialization, guards and dry-run copying remain specified.
- M3 — RESOLVED: downstream masking covers holes, post-hole uncertainty, affected features and label windows.
- Human questions — ACCEPTED: recorded human decisions D-038/D-039 settle open-version collection and automatic resume.
- Previous NEW ISSUE — RESOLVED: §4.4 requires a tracked header-only holes file from initialization; §6.9 adds first-hole crash recovery.

## PROVISIONAL DECISIONS

The new header-only, initially tracked holes file is an implementation choice within D-039’s explicit authorization to commit that file. Its schema and exit code 3 also remain within that authorization.

Inherited choices—seeding, version storage with the D-027 latest-version view, first-observation timestamps, requested-UID mapping, alert-type retention, reversible encoding, retry limits, nominal coverage checks, logging, deletion limitations and runner fallback—remain within existing rules. Event-time reconstruction remains explicitly distinguished from observed replay; subsequent training protocol requires its own approval.

Earlier provisional timing/token choices and strict hole stopping are superseded by recorded human decisions, rather than changed through consensus. No additional rule change is introduced.

## NEW ISSUES

None introduced by these revisions. This agreement concerns the updated plan; its specified tests remain implementation requirements.

VERDICT: AGREE
