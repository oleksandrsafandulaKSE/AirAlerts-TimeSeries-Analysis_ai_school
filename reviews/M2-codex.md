### Shell: `"nl -ba 'DECISIONS.md'"`
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
### Shell: `"nl -ba 'plans/M2.md'"`
     1	# M2 plan v1 — Features known at t + truncation leakage test
     2	
     3	Status: DRAFT for approval. Implements ROADMAP M2 under CLAUDE.md, D-004, D-013, D-017, D-020, D-021,
     4	on top of M1 (`plans/M1.md` v1.1: half-open intervals, D-020 counting interval
     5	`[start, min(finished_at, start+24h))`, merged unit intervals, approved gap `[2026-08-29, 2026-09-03)`).
     6	
     7	## 1. Goal
     8	One feature row per (unit, UTC hour t) on the M1 grid, using only information with t
### Shell: `"nl -ba '.claude/skills/ts-leakage-audit/SKILL.md'"`
     1	---
     2	name: ts-leakage-audit
     3	description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
     4	---
     5	
     6	# Time-series leakage audit
     7	
     8	## Core rule
     9	A forecast made at time t may only use information with timestamp <= t.
    10	
    11	## Required test: truncation invariance (tests/test_leakage.
### Shell: `"nl -ba 'CLAUDE.md'"`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
I’ll read the four priority files, then check for rule conflicts, leakage risks, weak tests, and deadline risk. I won’t inspect or write code.
The feature-only truncation test cannot verify label edges or purge behavior. I also found a conflict in D-003’s masking assertion and an inconsistency between the plan’s treatment of the recording gap and the start of history. I’m applying the leakage-audit skill’s checklist to the proposed tests.
## BLOCKERS

- M2 L76–89, “truncation_check(real features),” cannot detect label or purge leakage. Add integration assertions for onset at t (excluded), t+H (included), and cut-off C: retain t+H=C; reject t+H>C.
- D-003’s “no masked hour has active_at_t == 1” contradicts CLAUDE.md’s exclusion of active hours. Correct it to **no retained row is active**; test every unit.
- M2 L42, “U_start … history_start,” ignores pre-file alerts still counting during the following 24h under D-020. Extend initial state/onset uncertainty through history_start+24h, then propagate it into windows and time-since features.

## AMBIGUITIES

- M2 L14, “onsets = merged starts,” can suppress individual starts; D-020 says a standing alert’s start “still” counts. Specify whether an onset means a union transition or each constituent start, consistently for labels and features.
- D-014 says “Purge the last H hours”; D-021 permits labels mature exactly at C. Replace the prose with the explicit eligibility condition t+H≤C.
- M2 L107, “overall” NaN statistics, includes test-period statistics forbidden literally by CLAUDE.md. Define which structural diagnostics are permitted before M4; restrict distribution summaries to training.
- M2 L85, “still open in the full data,” conflicts with D-009’s January 2026 finish. Require finished_at>forecast t, then censor it in the truncated copy.

## MISSING

- M2 L90–93’s negative controls lack guaranteed witnesses. Use fixtures guaranteeing a future onset and an unknown finish; assert specific mismatches. Add touching/overlapping intervals, future extensions, finished_at=t, and exactly-24h cap cases.
- M2 L65–69 tests toy neighbours and DST, but not Kyiv City versus Kyivska. Add canonical-unit separation and distinct neighbour/group assertions under D-017/D-011.
- M2 L97–103 lacks explicit D-017 acceptance checks: shared format, source-independent features, any/red consistency, named configurations, and reports/<run>/ paths with required metadata.
- M2 “Done when” omits error-raising data checks, join uniqueness/completeness, pinned Python/packages, and the project .venv. Require these as inherited prerequisites, plus the decision-log proposal.

## QUESTIONS FOR THE HUMAN

- M2 L127–131 leaves uncertainty handling and an extra feature undecided. Approve explicit choices before implementation; record them.
- M2 L124, “Implementation + tests 35 min,” provides no contingency or remaining-milestone budget. What fits before 23:59 Kyiv? Reserve verification time and explicitly defer optional work.
