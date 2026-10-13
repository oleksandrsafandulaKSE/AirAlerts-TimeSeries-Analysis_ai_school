### Shell: `'cat CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'cat plans/M7.md reviews/M7-codex-r3.md reviews/M7-claude-r3.md'`
# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline

Status: v1.3 after consensus round 3 (D-026 loop). Human approval in chat (2026-10-13): weekly refit,
recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).

## 0. What this milestone may and may not claim
- The final test 
### Shell: `"rg --files -g AGENTS.md -g '*M7*' -g 'SKILL.md'"`
reviews/M7-codex-r3.md
reviews/M7-claude-r2.md
reviews/M7-claude-r3.md
reviews/M7-codex-r2.md
reviews/M7-codex-r1.md
reviews/M7-claude-r1.md
reviews/M7-codex-r1.log
reviews/M7-codex-r3.log
reviews/M7-codex-r2.log
reviews/M7-codex-r4.log
plans/M7.md

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
### Shell: `'cat reviews/M7-claude-r2.md reviews/M7-claude-r1.md'`
# Claude response, round 2 — plans/M7.md

## Changes made
- A2 — AGREE: every label-based rate (unit 14 d/30 d, national 14 d, offset prior) is sum(y)/count(y) over eligible rows (unmasked, label known, s ≤ t − H), the binary label of grid.build_grid; national pooled over units.
- Q1 — recorded explicitly, no escalation needed: the human approved in chat (i) "recent rates over 14 and 30 days as inputs", (ii) "make the model learn on top of the recent rate", (iii) the weekly refit. §0 now names t
### Shell: `"rg -n 'recent_rate|p_unit|skill|baseline|fingerprint' src/baselines.py src/evaluate.py scripts/run_all.py reviews/PROPOSED-DECISIONS-M4-M5.md; rg --files --hidden -g AGENTS.md -g '"'!.git/**'"'; nl -`
scripts/run_all.py:9:every pre-registered hash (model, calibrator, baseline tables, data, code) still matches (M4 plan §4)."""
scripts/run_all.py:26:from src import baselines, config as config_mod, data, evaluate, features, grid, model  # noqa: E402
scripts/run_all.py:33:def code_fingerprint(root=ROOT):
scripts/run_all.py:85:    preds, p_unit, n_hist = baselines.predict_all(iso, alerts, fit, score, cfg)
scripts/run_all.py:88:        raise data.DataQualityError("baseline predictions are not on th
I’ll read the updated plan and responses against the project rules, then check each prior finding and provisional decision.
The updated plan fixes the three definition issues from round 3. I’m applying the leakage-audit skill and checking one remaining ambiguity: whether “recent rate” in reporting still means the approved D-025 baseline.
## PREVIOUS ITEMS

- B1 RESOLVED: Offset handling covers fitting, early stopping, inference, and reload verification.
- B2 RESOLVED: Expanding priors use only mature historical labels.
- B3 RESOLVED: Feature comparisons and validation selection use identical keys.
- A1 RESOLVED: Greedy order, relative threshold, fold weighting, and tie rejection are explicit.
- A2 RESOLVED: The obsolete merged-onset rate definition is removed; binary-label counts are specified.
- A3 RESOLVED: Weekly fitting boundaries, maturity, and next-week scoring remain explicit.
- M1 RESOLVED: Pinned negative controls and expected-value fixtures cover the requested cases.
- M2 RESOLVED: Required reporting and leakage evidence remain included.
- Q1 RESOLVED: §0 records human authorization for the specified mature test-label inputs.
- Q2 ACCEPTED: Existing configuration and M3 evidence support the unchanged conservative gap mask.
- Oracle RESOLVED: The zero-residual expectation now includes clipping and endpoint cases.
- Previous NEW rate-definition issue RESOLVED: Counts, shrunk unit rates, and unshrunk national rates are distinguished.

## PROVISIONAL DECISIONS

- Fold dates and 0.5%/3-of-4 acceptance rule: within-rule, training-only design.
- Expanding prior: **OPEN reporting boundary.** The previous review requested an explicit unchanged metric reference; this remains absent. `plans/M7.md:43–46` defines “recent rate” using expanding `q(t)`, while line 100 promises only “skill vs recent rate.” D-025 and CLAUDE.md require the reporting baseline to use fixed train `p_unit`; `src/baselines.py:123–131` implements that distinction. Specify that reporting retains this baseline. Substituting `q(t)` in the metric reference would be a baseline rule change requiring human approval, beyond provisional consensus.
- V5 on V3: within-rule validation selection; explicitly identify which recent-rate prediction supplies its other component.
- H=1 only: within the authorized milestone scope.

## NEW ISSUES

None introduced by the round-3 edits.

VERDICT: CHANGES REQUIRED
