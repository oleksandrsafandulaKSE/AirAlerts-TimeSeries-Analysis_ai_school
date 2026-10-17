### Shell: `"pwd; rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g 'DECISIONS.md' -g 'M6a.md' -g 'PROPOSED-DECISIONS-M6.md' -g 'SKILL.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/.claude/worktrees/m6a-collection-34a410
DECISIONS.md
CLAUDE.md
reviews/PROPOSED-DECISIONS-M6.md
plans/M6a.md

### Shell: `'cat plans/M6a.md reviews/PROPOSED-DECISIONS-M6.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
Stop losing new-regime history. a
### Shell: `"nl -ba plans/M6a.md | sed -n '130,310p'"`
   130	  ([nominal_window_from, fetched_at]) and knowledge time (`fetched_at`) are separate columns.
   131	- HOLE = a pull whose `nominal_window_from` is later than the unit's previous `fetched_at`. AUTOMATIC RESUME (the
   132	  human, 2026-10-17, proposed D-039; an explicit exception to CLAUDE.md Architecture #6 "detected gaps … nothing is
   133	  committed"): a detected hole does NOT stop collection. The run records one row per affected unit in the
   134	  append-only `reports/collect/cove
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"cat .claude/skills/ts-leakage-audit/SKILL.md; rg --files -g 'AGENTS.md' -g '*M6*consensus*' -g '*collect*' -g '*collect*.yml' -g '*collect*.yaml' -g '*regions*'"`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `'cat reviews/PROPOSED-DECISIONS-M6.md; cat CLAUDE.md'`
# Proposed DECISIONS.md entries — M6 definition (the human edits and commits; see plans/M6-definition.md)
Numbers start at D-033 because D-028–D-032 are already proposed by M4, M5, M7, M5b and M8 (not yet ratified).

## D-033 — M6 scope: yellow/red typed forecasts (me, 2026-10-17, grilling session)
- Decision (me): M6 = M6a collection → M6c-1 first typed training → M6b monthly automatic job → site. Two new
  binary targets (yellow onset, red onset), with per-type eligibility (red during yellow c
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `"sed -n '1,125p' DECISIONS.md; cat .github/workflows/collect_api.yml; cat scripts/collect_api.py"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"nl -ba collect/api_collector.py | sed -n '1,260p'"`
     1	"""alerts.in.ua history collector (plans/M6a.md): fetch -> validate -> append-only merge -> pull log.
     2	
     3	One CSV row = one record VERSION, key (id, updated_at). Knowledge time of a version = `fetched_at` of the pull that
     4	first saw it. Every check raises (D-017 #6); a failed run writes nothing. The token is only ever put in a request
     5	header: it never appears in URLs, prints, exception messages or files.
     6	"""
     7	import csv
     8	import io
     9	import j
### Shell: `"nl -ba collect/api_collector.py | sed -n '260,580p'"`
   260	    closed = [parse_ts(r["finished_at"]) for p in pulls for r in p["records"] if r["finished_at"] is not None]
   261	    first_fetch = min(parse_ts(p["fetched_at"]) for p in pulls)
   262	    if not closed or min(closed) > first_fetch - MIN_WINDOW:
   263	        got = fmt_ts(min(closed)) if closed else "none"
   264	        raise CollectError(f"API window looks shorter than 29 days: earliest finished_at over all units {got} > "
   265	                           f"{fmt_ts(first_fetch - M
### Shell: `"rg -n 'hole|crash|workflow|consisten|dry.run|pull_id|route' tests/test_collect.py reviews/M6a-consensus.md reviews/M6a-v2-consensus.md; cat reviews/M6a-v2-consensus.md"`
reviews/M6a-consensus.md:9:- Nothing was implemented. No API call was made, and no workflow file or data was written.
reviews/M6a-consensus.md:19:  window check. Null ↔ empty round-trip is lossless. Added crash-consistency between the CSV and the pull log,
reviews/M6a-consensus.md:21:- R2: hole handling made strict (a detected hole → nothing committed, collection stops) per CLAUDE.md Architecture #6;
reviews/M6a-consensus.md:22:  the `accept_hole` override was removed as a rule change. A separat
### Shell: `"sed -n '425,475p' tests/test_collect.py; sed -n '1,100p' reviews/M6a-consensus.md; nl -ba plans/M6a.md | sed -n '1,130p'"`
    assert new == []


# ---------------- 9. coverage holes + crash recovery ----------------

def test_coverage_holes(tmp_path):
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    t = datetime(2026, 10, 20, tzinfo=UTC)
    C.apply_pulls(store, log, [pull(31, [], t)], "p0", "c")
    C.apply_pulls(store, log, [pull(31, [], t + timedelta(days=1))], "p1", "c")
    # window_from = day 0.5: later than p0 (day 0) but not than the LATEST previous pull p1 (day 1) -> no hole
    # (fails if chec
I’ll read the priority files, then check the addendum against the approved decisions and current collector behavior.
I’m applying the project’s leakage-audit skill to check coverage-hole semantics. I’ll treat D-038 and D-039 as approved, as instructed.
The addendum’s crash repair omits orphaned hole rows, and its workflow instructions don’t explicitly stage the new holes file. I’m also checking whether the planned tests would catch those failures.
## BLOCKERS

- §4.4, “drop the CSV rows”: after CSV and holes renames succeed but the log rename fails, this repair leaves orphaned hole rows; every subsequent run still fails. Fix: restore **both** CSV and holes to their pre-run state, preserving committed history. Test detection, repair, and successful restart, including a pull with zero new alert rows.

- §5, “if the CSV or log changed”: the commit instructions omit `coverage_holes.csv`; the existing workflow stages only those two files. This allows resumed data and its log to be published without D-039’s required hole record. Explicitly include all three files in change detection, staging, and the same commit.

## AMBIGUITIES

- §4.4, “MINUS the recorded holes”: hole endpoint inclusion is unspecified, although pull windows include both endpoints. Define the missing interval as `(previous fetched_at, new nominal_window_from)` and test coverage exactly at each endpoint and immediately inside it.

- §9, “The plan builds the strict version”: this contradicts the approved automatic-resume rule. Mark the historical questions explicitly superseded and remove that operative sentence; D-038/D-039 govern implementation.

## MISSING

- §6.9, “parses the YAML step conditions”: static conditions can pass while the CLI returns the wrong status, shell handling loses it, or staging omits holes. Add offline execution tests for statuses 0, 3, and another failure: verify commit eligibility, committed paths, and final failure **after** publication for status 3.

- §4.4, “all files”: specify the holes-file path alongside custom `--log`, missing-file initialization, append-only validation, and copying it into `--dry-run` scratch storage. Otherwise developers can accidentally inspect or modify the production holes file during a dry run.

- §4.4, “Consumers compute coverage”: distinguish raw event coverage from modelling eligibility. D-020/D-022/D-023 require uncertainty after gaps and invalidation of affected label/look-back windows. Add an explicit downstream contract; subtracting the hole alone must not authorize those rows.

## QUESTIONS FOR THE HUMAN

- None. D-038/D-039 settle §9(a)/(c); update their stale wording without requesting approval again.

VERDICT: CHANGES REQUIRED
