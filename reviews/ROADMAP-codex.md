### Shell: `pwd`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo

### Shell: `'nl -ba plans/ROADMAP.md'`
     1	# Roadmap M1–M6 (general level)
     2	
     3	What each milestone delivers and when it counts as done, not how. Step-by-step plans are
     4	written per milestone later (`plans/M<n>.md`), each reviewed by Codex before implementation.
     5	Detailed raw material from the first planning pass: `plans/ALL.md`, `reviews/M1-codex.md`,
     6	`reviews/ALL-codex.md`.
     7	
     8	## The question
     9	For each of 24 units (23 oblasts + Kyiv City), at the start of each UTC hour t: what is th
### Shell: `'nl -ba README.md'`
     1	# Air-raid alert onset forecasting — Ukraine
     2	
     3	> For each oblast and each hour: the probability that a NEW air-raid alert starts within the
     4	> next hour, using only what is known at that moment. Tested on the last 6 weeks of official
     5	> data against simple baselines, with a test that proves no future information is used.
     6	
     7	**Status (12 Oct 2026):** design and decisions are done (`DECISIONS.md`, `plans/ROADMAP.md`);
     8	implementation is in progress
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
### Shell: `'nl -ba CLAUDE.md'`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `"rg --files -g AGENTS.md -g '"'!data/**'"' -g '"'!src/**'"' -g '"'!tests/**'"' -g '"'!app/**'"'"`

I’ll read the four priority documents and check their agreement, milestone gates, and deadline risks. I’ll keep the review at roadmap level and make no changes.
The main conflicts concern standing-alert handling, baseline updates during the test, and when the final test is opened. The README also presents several planned outcomes as established. It is about 21:53 Kyiv, leaving roughly two hours against the roadmap’s 5–6-hour estimate.
## BLOCKERS

- **D-009; ROADMAP “first 24h”:** the approved rule uses future duration; the proposed replacement permits forecasts while an actual alert remains active, contradicting README “already under alert are excluded.” Approve an explicit standing-alert estimand, supersede D-009, and align all four documents.
- **ROADMAP “rolling … or frozen”; D-014:** CLAUDE freezes baselines, while D-014 assumes recent-rate adapts. Decide which observations may update each baseline during evaluation; record the exception consistently.
- **M3 “table … for the final test” precedes M4:** inspecting these results risks influencing model choices despite README “used once.” Develop baselines on validation; freeze the complete protocol before evaluating model and baselines together on the final test.
- **ROADMAP “5–6 hours”; D-012:** full M1–M5 scope exceeds roughly two hours remaining tonight. Replace the estimate with a deadline deliverable and explicit deferrals, including Streamlit and automation.

## AMBIGUITIES

- **README “Tested,” “handled,” “design … done,” “How to run”:** these imply completed work despite no code and unresolved decisions. Mark implementation as not started, commands as planned, and data findings as preliminary observations.
- **D-015 “unconfirmed”; README “declared much more widely” and “Expected conclusion”:** an interpretation becomes a fact and the conclusion is predetermined. Separate measured differences from hypotheses; make retraining recommendations conditional on transfer results.

## MISSING

- **M1 “doesn’t collapse”; M4 “tables … exist”; M5 “every number”; M6 “successful manual run”:** acceptance gates are underspecified. Define measurable data checks, required evaluation artifacts, reproducible project-derived figures, and demonstrated collection/reporting behavior. Restore the required overall reliability plot from D-006.
- **ROADMAP “Decisions needed”:** add validation-period selection, calibration policy, primary comparison metric, and whether failure to beat recent-rate still constitutes a completed project. Decide these before milestone planning.
- **M6a “after M1”; M4 “API loader”; D-016:** collection depends on functionality scheduled later, while API history expires. Move collection prerequisites earlier; resolve the documented hosting-access risk and define the future monthly evaluation protocol.

## QUESTIONS FOR THE HUMAN

- **D-012; ROADMAP “Scope at the deadline”:** what must be submitted tonight? Record a minimum deliverable and defer everything outside it.
- **ROADMAP “D-019”; D-016 “confirm”:** D-019 is absent and automation approval remains qualified. Record the approved workflow and clarify whether M6 is committed scope.
