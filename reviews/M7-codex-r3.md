### Shell: `'cat plans/M7.md reviews/M7-codex-r2.md reviews/M7-claude-r2.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline

Status: v1.2 after consensus round 2 (D-026 loop). Human approval in chat (2026-10-13): weekly refit,
recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).

## 0. What this milestone may and may not claim
- The final test 
### Shell: `'tail -n 70 reviews/M7-codex-r2.md'`
    grid_start: pd.Timestamp
    grid_end: pd.Timestamp            # exclusive
    coverage_end: pd.Timestamp        # last moment the source is known to be recording
    train: tuple                      # half-open [start, end) 
### Shell: `"sed -n '1,125p' src/evaluate.py; rg -n 'decision 4|gap|145|conservative|D-028|fingerprint' plans/M3.md reviews/PROPOSED-DECISIONS-M4-M5.md scripts/run_all.py tests/test_config.py tests/test_leakage.p`
"""Splits, eligibility, test-label isolation and the me
### Shell: `'cat reviews/M7-claude-r2.md CLAUDE.md'`
# Claude response, round 2 — plans/M7.md

## Changes made
- A2 — AGREE: every label-based rate (unit 14 d/30 d, national 14 d, offset prior) is sum(y)/count(y) over eligible rows (unmasked, label known, s ≤ t − H), the binary label of grid.build_grid; national pooled over units.
- Q1 — recorded explicitly, no escalation needed: the human approved in chat (i) "recent rates over 14 and 30 days as inputs", (ii) "make the model learn on top of the recent rate", (iii) the weekly refit. §0 now names t
### Shell: `"rg --files --hidden -g AGENTS.md -g '"'!.git/**'"'; rg -n 'D-028|D-030|recent rate|recent-rate|baseline|q\\(t\\)|PROVISIONAL' plans/M7.md reviews/M7-claude-r2.md reviews/PROPOSED-DECISIONS-M4-M5.md; `
plans/M7.md:1:# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline
plans/M7.md:4:recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
plans/M7.md:5:Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).
plans/M7.md:14:  exception to D-021's score-once rule FOR LABELLED POST-HOC ROWS ONLY (proposed D-030); it does not touch the
p
### Shell: `"nl -ba plans/M7.md; rg -n 'gap_label_mask_interval|check_gap_rows|145|conservative' src/config.py tests/test_leakage.py plans/M3.md; cat reviews/PROPOSED-DECISIONS-M4-M5.md; rg -n 'recent_rate|skill|`
     1	# M7 plan v1 — Improvement rows (post-hoc): weekly refit, recent-rate offset, blend, richer features, frontline
     2	
     3	Status: v1.2 after consensus round 2 (D-026 loop). Human approval in chat (2026-10-13): weekly refit,
     4	recent-rate offset, blend, better features ("logical patterns, if they just work"), frontline handled separately.
     5	Rules: CLAUDE.md, D-013, D-014, D-021, D-023–D-025, D-028 (proposed). H = 1 only (the headline horizon).
     6	
     7	## 0. What this 
I’ll compare each previous finding with the updated plan and builder response, then check the provisional decisions against the project rules and leakage audit.

The rate definition and test-label authorization are now explicit. The offset oracle is still inconsistent with the clipping formula. I’ll check whether the provisional prior also changes the required reporting baseline, using the leakage-audit skill.

## PREVIOUS ITEMS

- B1 RESOLVED: Offset handling covers fitting, early stopping, inference, and reload verification.
- B2 RESOLVED: Expanding priors use only mature historical labels.
- B3 RESOLVED: Feature comparisons and validation selection use identical keys.
- A1 RESOLVED: Greedy selection, relative improvement, fold weighting, and tie rejection are explicit.
- A2 OPEN: `plans/M7.md:62–63` still defines national rate using merged-onset counts, contradicting the binary-label definition at lines 66–68. Multiple merged onsets within one horizon count once in `grid.build_grid`. Remove the obsolete numerator definition.
- A3 RESOLVED: Weekly fitting boundaries, maturity, and next-week scoring are specified.
- M1 RESOLVED: Pinned negative controls and expected-value fixtures cover the requested cases.
- M2 RESOLVED: Required reporting and leakage evidence are included.
- Q1 RESOLVED: §0 explicitly records human authorization for mature test-label inputs and offsets.
- Q2 ACCEPTED: The existing configuration and M3 protocol support the unchanged conservative gap mask.
- Previous oracle issue OPEN: Lines 48–51 still require zero residual to return unclipped `r(t)`. The specified formula returns the clipped rate; at `r=0`, prediction is `0.0001`. Correct the oracle and include endpoint cases.

## PROVISIONAL DECISIONS

- Fold dates and the 0.5%/3-of-4 acceptance rule: within-rule training-only design.
- Expanding prior: within-rule for the new offset/features. Using it instead of D-025’s fixed `p_unit` reporting baseline would be a rule change requiring human approval; explicitly identify the unchanged metric reference.
- V5 on V3: within-rule validation selection.
- H=1 only: within the authorized milestone scope.

## NEW ISSUES

- Lines 66–68 now define **every** label-based rate as `sum(y)/count(y)`, including unit rates. This contradicts §2.1’s shrinkage formula and block A’s “shrunk” rates. Define `k=sum(y)` and `n=count(y)` as components; retain the specified shrinkage for unit rates and identify national rates as pooled, unshrunk proportions.

VERDICT: CHANGES REQUIRED
