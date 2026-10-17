### Shell: `'cat plans/M6a.md reviews/M6a-codex-r2.md reviews/M6a-claude-r2.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
Stop losing new-regime history. a
### Shell: `"wc -l reviews/M6a-codex-r2.md reviews/M6a-claude-r2.md CLAUDE.md DECISIONS.md plans/M6a.md; rg --files -g AGENTS.md -g '*M6a*' -g '*manifest*'"`
     182 reviews/M6a-codex-r2.md
      37 reviews/M6a-claude-r2.md
     156 CLAUDE.md
     301 DECISIONS.md
     204 plans/M6a.md
     880 total
reviews/M6a-claude-r2.md
reviews/M6a-codex-r2.md
reviews/M6a-codex-r1.log
reviews/M6a-codex-r1.md
reviews/M6a-codex-r2.log
reviews/M6a-codex-r3.log
reviews/M6a-claude-r1.md
plans/M6a.md

### Shell: `'cat reviews/M6a-codex-r2.md reviews/M6a-claude-r2.md'`
### Shell: `'cat plans/M6a.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
S
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
### Shell: `"sed -n '1,110p' DECISIONS.md; sed -n '110,225p' DECISIONS.md"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"sed -n '225,320p' DECISIONS.md; sed -n '120,230p' src/data.py; sed -n '1,100p' netlify/functions/update-forecast.mjs; rg -n 'timeout|fetch|history' netlify/live/lib/runner.mjs"`
  pairs. The reviewer's mutation tests (look-ahead from 1 minute to 1 hour) all fail the test.
- Purge rule for M3: a training row is kept if t+H ≤ cut-off.
- Open: how NaN `onsets_last_7d` is handled on test rows from 09-04 to 09-07. **Resolved by D-024.**

## D-024 — Rows with missing features in the test period
- Headline scoring (model and all baselines) uses only test rows where every model feature is known at t.
  After the gap, `onsets_last_7d` is missing from 09-04 00:00 to the end of th
### Shell: `"nl -ba plans/M6a.md | sed -n '35,65p'; nl -ba plans/M6a.md | sed -n '150,185p'; cat requirements.txt; rg -n 'PROVISIONAL' reviews/M6a-claude-r1.md reviews/M6a-claude-r2.md"`
    35	## 3. Fetch
    36	- UIDs: exactly the 24 unit UIDs from `src.regions.UNITS[*]["api_uid"]`. Excluded UIDs (16, 29, 30) and the 404 UIDs
    37	  (6, 7) are not requested (never used, D-008). Fixed order (ascending UID).
    38	- Rate: the collector spaces its requests ≥ 65 s apart (≤ 1/min; 24 requests ≈ 26 min). Sleep is injected (testable).
    39	- Auth: `Authorization: Bearer <token>` header from env `ALERTS_IN_UA_TOKEN` (locally loaded from `.env`; in Actions
    40	  from the repo s
I’ll compare each previous finding with the updated plan and builder’s response, then check the provisional decisions against the project rules.
## PREVIOUS ITEMS

- **B1 RESOLVED:** §4.4 removes hole acceptance; detected gaps stop collection without commits.
- **B2 RESOLVED:** Knowledge-time filtering precedes version selection, with a delayed-correction negative control.
- **B3 RESOLVED:** Disappearance counts are removed; undetected deletions remain explicit.
- **A1 RESOLVED:** Coverage remains explicitly nominal and conditional on the assumed API contract.
- **A2 RESOLVED:** Null decoding and parsed timestamp validation remain specified.
- **M1 RESOLVED:** Write ordering, incomplete-run detection, repair instructions, and interruption testing remain specified.
- **M2 RESOLVED:** Separate collector credentials and runner IP replace the unsupported combined-rate claim as deployment prerequisites.
- **M3 ACCEPTED:** Compatibility witnesses and unchanged-source regression coverage remain adequate.
- **M4 RESOLVED:** Reviewer, harness, fixes, and milestone summary remain required.
- **Q ACCEPTED:** D-027 and CLAUDE.md’s explicit M4/M6 rule authorize keeping open alerts.
- **Retry/timeout finding RESOLVED:** Six retries per run and a 75-minute workflow timeout address the previous unbounded runtime allocation.

## PROVISIONAL DECISIONS

All listed decisions remain within existing rules: strict hole handling; retry and timeout settings; seed ingestion; retaining unknown alert types; 24 forecast UIDs; version keys with the D-027 latest-version view; `fetched_at` knowledge time and its selector; undetected deletions; and the raising window check. The check still cannot establish completeness.

The second token requires human provisioning, without changing project rules. Optional hole recovery would change Architecture #6/D-017; §9 correctly leaves that exception outside the implementation.

## NEW ISSUES

- **Impossible required timing test:** §6.6 specifies “every UID times out once … 6 retries used.” Recovering from one timeout for each of 24 UIDs requires 24 retries, violating §3’s six-retry budget; collection must abort before completing that scenario. Specify a successful maximum-budget schedule with six retryable failures plus 24 successful responses, and separately test budget exhaustion. Also correct §3’s displayed calculation: its terms total **53 minutes**, not 51. The 75-minute allocation remains adequate under those stated bounds.

VERDICT: CHANGES REQUIRED
