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
### Shell: `'nl -ba .claude/skills/ts-leakage-audit/SKILL.md'`
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
### Shell: `'nl -ba plans/ALL.md'`
     1	# Full implementation plan, M1–M6
     2	
     3	One plan for all milestones, for a single Codex review before implementation starts in a
     4	separate chat. M1 below is copied unchanged from plans/M1.md (already reviewed once, see
     5	reviews/M1-codex.md; its findings are listed under Open decisions, not applied).
     6	
     7	
     8	---
     9	
    10	# M1 — Data, oblast intervals, hourly grid, mask (unchanged from plans/M1.md)
    11	
    12	## Part 1 — original M1 plan
    13	
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
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
I’ll read the four priority files, then check the plan for contradictions, leakage paths, weak tests, and deadline risk.
I’m applying the leakage-audit skill. The plan leaves the causal standing-alert rule unresolved, and its training dates conflict with its validation and refit steps. I’ll also check whether the planned tests would catch those failures.
## BLOCKERS

- **D-009; ALL:20 “drop alerts longer than 24h”:** final duration leaks into historical masks/features, contradicting CLAUDE’s information-at-t rule. Approve a causal expiry rule and update D-009 before implementation.
- **ALL:115–116 “last 4 weeks of train”:** validation actually follows training. Specify disjoint UTC intervals. ALL:159 calibration also becomes mismatched after refitting; reserve separate calibration data or retain the calibrated model.
- **D-013; ALL:21 “last alert … first alert”:** silence cannot establish recording completeness. Fix conservative 29 Aug–2 Sep boundaries; exclude overlapping label windows and invalidate contaminated lookbacks and uncertain state.
- **ALL:123 “rolling”:** contradicts CLAUDE’s frozen baselines/no test-period statistics, although D-014 assumes adaptation. Authorize an explicit exception; use only historical rows whose labels have matured by t.

## AMBIGUITIES

- **ALL:22 “oblast-level alert starts” versus D-002:** explicitly require starts of unions across oblast/raion/hromada. Define intervals as [start,end), labels as (t,t+H], and onset/end equality tests.
- **ALL:118 “crosses the cut-off”:** specify equality. Conservatively require training label endpoints before the cutoff; censor incomplete final horizons. Keep D-007’s midnight test end despite ALL:22’s 05:00 grid.
- **ALL:62 “≥ 24 units”; D-017:** require the exact canonical set. Known duplicates/gaps must be accepted explicitly; otherwise mandatory error checks reject the approved dataset.
- **ALL:125,159:** define bin endpoints, missing-history handling, empty rolling denominators, PR-AUC convention and ECE bins before implementation.

## MISSING

- **ALL:89–95:** five times can miss leakage; final-duration controls can be inert on unmasked rows. Truncate raw data before preprocessing; force active, >24h, cutoff and gap cases across units, including DST as the skill requires.
- **D-003; ALL:27:** D-003’s assertion is reversed. Correct it; test masks against independently expected states, since mutually wrong mask/state columns can satisfy existing assertions.
- **D-011/D-017; ALL:64,99:** add exact Kyiv City/Kyivska mapping/group fixtures and explicit UTC/local DST expectations; symmetry alone cannot verify borders.
- **D-017; ALL:63,134,196:** pin Python; move CLI/run metadata into M1; specify saved model/predictions, module tests and stage diagnostics. Keep outputs under `reports/<run>/`.

## QUESTIONS FOR THE HUMAN

- **D-012; ALL:259:** 330 minutes exceed tonight’s 139-minute budget. Which deliverables are deferred? Approve reduced scope explicitly.
- **ALL:166,255; D-015/D-016:** approve the changed scoring window, monthly-training exception and milestone-protocol revision; none is settled by listing it as open.
