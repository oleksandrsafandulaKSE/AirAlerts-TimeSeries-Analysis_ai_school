# Consensus record — plans/M3b-H3.md (D-026 loop)

- **Outcome:** CONSENSUS after 4 rounds (Codex r1 review → Claude r1 → Codex r2 → Claude r2 → Codex r3 → Claude r3 → Codex r4).
- **Codex's final verdict (round 4, verbatim):** "None introduced by this revision. The narrowed assertions preserve pre-test label diagnostics, fitted quantities, validation predictions and metrics while respecting D-024's permitted availability reporting." — `VERDICT: AGREE`
- **Process note:** the first round-2 Codex call failed before producing a review (environment error `script: tcgetattr/ioctl: Operation not supported on socket`, log in `reviews/M3b-H3-codex-r2.log` was overwritten by the retry). It was retried once with stdin detached; that run produced the round-2 review. No review result was discarded.

## Real issues found by the loop
- Round 2 (blocker): at H = 3, M1's base-rate diagnostics and the test-label isolation used `t < C`, so rows C−2h and C−1h could carry post-cut-off onsets. Fix: every label read before M4 must satisfy `t + H ≤ C` (identical to the current rule at H = 1).
- Round 3: the invariance test was overbroad (test-availability counts legitimately change with raw data); split into label-poisoning and raw-event checks.

## PROVISIONAL design decisions (Claude+Codex consensus, human to ratify)
1. Config name `official_h3`, output folder `reports/official_h3/`.
2. The new-regime section (D-015) stays H = 1 only.

## Deferred to the human (not decided by the loop)
- Whether M4 trains an H = 3 model (M4 plan). If yes, its test rows are scored in the same single M4 test scoring.
- DECISIONS.md entry D-027 and a CLAUDE.md Target line for the extra horizon (rule files are human-owned).

## Escalations
None. Adding H = 3 as an extra results row was approved by the human in chat (2026-10-13).
