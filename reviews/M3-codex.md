### Shell: `'cat plans/M3.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M3 plan v1 — Baselines + evaluation framework (validation only)

Status: DRAFT for approval. Implements ROADMAP M3 under CLAUDE.md, D-006, D-011, D-013, D-021,
D-022 (purge), D-023 (features), D-024 (rows with missing features). Builds on M1 (grid, mask, y)
and M2 (features known at t). The final test is NOT scored in M3 (D-021).

## 1. Goal
Split rules with purge and label maturity, four baselines, the metric suite (incl. the overall
reliability plot), and `reports/official/` output, so that 
I’ll read the four priority files, then check the plan for conflicting rules, leakage risks, weak tests, and deadline scope.
I’m applying the leakage-audit skill. The main conflict is at the validation/test boundary: keeping a label whose horizon ends exactly at test start can require an onset recorded at test start, while M3 promises to read no test-period labels.
## BLOCKERS

- **“t + H ≤ b”** (D-022) permits the last validation label to include an onset exactly at test start, contradicting **“run reads no test label”** (D-021). Obtain a decision: strict validation-end purge, or an explicit boundary exception; test an onset exactly at that boundary.
- **“Empty or tiny n: see §9 Q1”** leaves the PRIMARY comparator undefined. Option A changes D-024’s scoring population; B/C change D-021’s baseline. Approve one formula and eligibility policy before implementation.
- **D-003** says “no masked hour has active_at_t == 1,” contradicting CLAUDE’s requirement to mask active hours. Correct it to “no eligible hour is active”; gap-masked hours may be inactive.

## AMBIGUITIES

- **D-022 “24h post-gap” versus D-024 “145 gap hours”** imply different mask intervals. Publish separate canonical target, state, and lookback uncertainty intervals; assert exact UTC boundary rows.
- **“computed from the M1 unit onsets”** needs D-023’s merged-onset semantics. Specify touching/overlapping interval handling, exact 24h cap behavior, and whether capped ends reset `minutes_since_last_end`; test standing alerts with unknown `finished_at`.
- **“reasons can overlap” / “first matching reason wins”** describes two counting schemes. Report exclusive exclusion counts plus separate overlapping diagnostics.
- **“Brier skill” / “PR-AUC / base rate”** lack zero-denominator policies. Define undefined outputs and reasons, including empty groups and units without training observations.

## MISSING

- **“Recent-rate causality”** perturbs labels only; it can miss future-end leakage through upstream masks/features. Extend the leakage skill’s raw-data truncation test through all baseline predictions, with a deliberately leaky negative control, DST transitions, and gap edges.
- **“all baselines share row counts”** passes when different rows are scored. Assert identical `(unit,t)` keys; explicitly verify Kyiv City versus Kyivska assignments (D-011).
- **“no file contains test-period metrics”** passes if test labels were read or metrics discarded. Test label-access isolation and fail before any report write.
- **D-017** requires configurable runs/levels, complete metadata, fatal data checks, and `metrics.*`; D-022 grants output exceptions only for M1. Document M3 compliance or obtain exceptions. Verify `.venv`, exact dependency/Python pins, and approval for new dependencies.

## QUESTIONS FOR THE HUMAN

- **CLAUDE “Mon 12 Oct 2026, 23:59”** conflicts with today, 13 October. Confirm the actual deadline date.
- **“15…35…25…10…30 min”** totals 115 minutes before reviews/fixes and remaining milestones. Approve a time budget and defer optional choices before implementation.
