### Shell: `'cat plans/M3b-H3.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M3b plan v1 — Additional horizon H = 3 (extra results row, never the headline)

Status: DRAFT for approval. Requested by the human (2026-10-13): "add additional horizon h=3".
Amends D-000 (H = 1 only) and D-013 (multiple horizons skipped). The headline stays H = 1.

## 1. Goal
Run the existing M1–M3 pipeline with H = 3 hours as a second, separate run:
`python scripts/run_all.py --config official_h3` → `reports/official_h3/` with the same files as
`reports/official/` (run_meta, m1/m2/m3 checks,
### Shell: `'nl -ba plans/M3b-H3.md'`
     1	# M3b plan v1 — Additional horizon H = 3 (extra results row, never the headline)
     2	
     3	Status: DRAFT for approval. Requested by the human (2026-10-13): "add additional horizon h=3".
     4	Amends D-000 (H = 1 only) and D-013 (multiple horizons skipped). The headline stays H = 1.
     5	
     6	## 1. Goal
     7	Run the existing M1–M3 pipeline with H = 3 hours as a second, separate run:
     8	`python scripts/run_all.py --config official_h3` → `reports/official_h3/` with the same 
I’ll read the four priority files and check the plan for contradictions, leakage risks, ineffective tests, and deadline scope.

I’m applying the leakage-audit skill. The main concerns are the undefined gap boundary, tests that may miss leaked negative labels, and the stale deadline. D-025 already approves `metrics_validation.*`, so that output naming is consistent with the decision log.

## BLOCKERS

- “Every horizon-dependent rule already reads `cfg.H`” assumes implementation despite this being a pre-code review. Replace that assumption and “5 min…30 min” with explicit implementation requirements, dependencies, and a realistic estimate.
- “Same mask” contradicts the expanded 147-hour gap mask. D-022 distinguishes detected missingness from D-023’s conservative uncertainty interval. Define `g0` explicitly, derive the H-dependent mask, and assert both boundaries and post-gap recovery.
- “Positives at t−1h and t−2h do not count” can pass while immature negatives inflate the denominator. Assert exact eligible history indices, **k and n**, including negative labels, missing labels, and both 14-day endpoints.

## AMBIGUITIES

- “Onset at t → row t masked” conflicts with D-022’s zero-duration alerts, which mask nothing. Test separately that an onset at t is excluded from y(t), and masking follows causal activity.
- “Last label ends…same (grid end unchanged)” confuses grid coverage with eligible-label coverage. Specify terminal purge: C−3h survives; C−2h and C−1h do not. Reconcile D-014’s “last H hours” shorthand with D-022/D-023’s inclusive equality.
- “Train rate” omits D-025’s unit × Kyiv-hour × weekday climatology, persistence bins, and α=10 shrinkage. Restate these fitting rules and train-only eligibility.
- “Byte-identical” conflicts with D-017 metadata containing a changed git commit. Define deterministic artifacts and compare metadata fields separately.

## MISSING

- “Same 6 real times” does not require masking future `finished_at`. Apply the leakage skill’s raw-data truncation; compare features, masks, and baseline predictions. Include DST transitions, gap edges, >24h alerts, the exact 24h boundary, and negative controls that demonstrably fail.
- “16 rows” verifies file size, not correctness. Assert metric identities, eligible counts, test-label isolation, and D-008/D-011’s separate Kyiv City/Kyivska mappings and groups.
- “Same files” lacks acceptance checks for D-017’s shared schema, centralized regions/configs, target-level setting, pinned Python/packages, and error-raising data checks. Specify `reports/<run>/` metadata and audit evidence; retain D-025’s approved validation-output exception.

## QUESTIONS FOR THE HUMAN

- CLAUDE.md says **12 October**, while the plan is dated **13 October** and your request says tonight. Confirm the governing deadline and reserve time for remaining milestones; defer H=3 if necessary.
- “M4 later trains” pre-decides the plan’s unanswered question. Approve D-026’s exact scope—baselines, model, exploratory horizon—and amend D-021’s single final-test scoring batch before implementation.
