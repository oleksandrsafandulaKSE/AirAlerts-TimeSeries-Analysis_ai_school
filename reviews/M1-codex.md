### Shell: `'cat plans/M1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M1 plan v1 — Clean data → hourly grid with target and mask

Status: DRAFT for approval. Supersedes `plans/archive/M1-v0.md`.
Implements ROADMAP M1 under CLAUDE.md and D-002, D-008, D-010, D-011, D-013, D-017, D-020, D-021.

## 1. Goal
From the official file only, produce per unit (24 units) and per UTC hour t:
`active_at_t`, `gap_mask`, `mask`, `y` (onset in (t, t+H]), plus the shared alert table and the
per-unit onset/interval lists that M2 will reuse. No features, no baselines, no model.

##
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `'nl -ba plans/M1.md'`
     1	# M1 plan v1 — Clean data → hourly grid with target and mask
     2	
     3	Status: DRAFT for approval. Supersedes `plans/archive/M1-v0.md`.
     4	Implements ROADMAP M1 under CLAUDE.md and D-002, D-008, D-010, D-011, D-013, D-017, D-020, D-021.
     5	
     6	## 1. Goal
     7	From the official file only, produce per unit (24 units) and per UTC hour t:
     8	`active_at_t`, `gap_mask`, `mask`, `y` (onset in (t, t+H]), plus the shared alert table and the
     9	per-unit onset/interval lis
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
### Shell: `"sed -n '73,153p' plans/M1.md"`
3. **data.py (15 min).** Parse times as UTC (`utc=True`; if strings carry no offset they are UTC
   per CLAUDE.md). Order of operations, each with a printed count:
   (1) raw rows → raise if ≠ expected (the file is frozen; a change means re-check, not continue);
   (2) drop exact duplicate rows → raise if dropped ≠ expected; then re-check 0 duplicates remain;
   (3) drop excluded units (Luhanska) → print rows dropped;
   (4) map names via `regions.py` → unknown name raises;
   (5) raise if the u
I’ll read the four priority files and check the plan for conflicting rules, leakage, ineffective tests, and deadline risk.
I’m applying the project’s ts-leakage-audit skill. The plan’s gap formula already contradicts its boundary test: the formula leaves 09:00 unmasked, while the test requires it masked because `(09:00,10:00]` includes the gap’s start.
## BLOCKERS

- §2 “t + H > g0” contradicts test 11 and `(t,t+H]`: onset at g0 remains unmasked. Fix to `t+H ≥ g0`.
- D-003 requires “no masked hour” active—the reverse of CLAUDE.md. Correct the decision; assert exact masks across multiple units. Test 9’s invariant still passes with every row masked.
- §4 “per UTC quarter” exposes final-test labels before M4, conflicting with CLAUDE.md and D-021. Restrict diagnostics to train/validation or explicitly approve a descriptive-QA exception.
- §2 “max observed timestamp” cannot establish recording coverage: a standing alert’s end can extend beyond reliable onset collection. Use an explicit coverage endpoint and test misleading late ends.

## AMBIGUITIES

- §8 “Purge … M3”: CLAUDE.md says “past” cutoff, D-014 says purge the last H hours. Specify whether `t+H=cutoff` survives; add an onset exactly at cutoff to split tests.
- §2 “finished_at … nothing else” contradicts its use in interval construction. Permit observed ends for state; prohibit future endpoints in M2 features. Add deterministic truncation cases immediately before/at ends and the 24h cap.
- §4 “Parse times” before “exact duplicate rows” can collapse textually distinct timestamps. Specify raw-field deduplication before parsing and stable-hash serialization.
- §4 “finished_at < started_at” permits zero-duration alerts, undermining §2’s raw-start equivalence. Reject them or explicitly define their onset semantics.

## MISSING

- D-013/§4 “national … zero starts” misses partial/unit-specific outages. Preserve approved 29 Aug–2 Sep coverage boundaries; propagate uncertainty into M2 windows and D-021’s 14-day baseline.
- §5 “Grid shape/DST” passes despite incorrectly parsed alert timestamps; UID-set tests pass with Kyiv City/Kyivska IDs swapped. Assert timestamp-to-row alignment and exact IDs 31/14.
- §3 “leakage … M2” omits CLAUDE.md’s mandatory negative control. Add a deterministic deliberately leaky state calculation that the audit catches.
- D-017/§4 outputs omit required metrics filenames/plots; §3’s Python comment does not enforce the interpreter. Specify milestone-specific output exceptions, runtime version checks, and failure tests for every required data check.

## QUESTIONS FOR THE HUMAN

- §11 “~5.2 days”: proposed masking covers six days plus one preceding hour, in a 42-day test. Approve corrected boundaries/cost.
- D-017’s monthly-config requirement conflicts with §3’s stub and D-016’s deferral. Explicitly approve the M1 interface exception.
- §10 “M2–M5 cannot all fit” conflicts with D-012 scope. Approve a reduced submission now and reserve verification time before 23:59 Kyiv.
