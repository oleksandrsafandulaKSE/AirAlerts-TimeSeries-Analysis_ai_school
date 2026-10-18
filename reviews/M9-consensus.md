# M9 — consensus record

**Outcome: CONSENSUS after 3 rounds** (round 1 escalated to the human, who resolved it in chat).

## Escalation history
- **Round 1:** new statistics on the already-scored TEST needed an explicit exception to CLAUDE.md's "no
  statistic computed over the test period".
- **Resolved by the human (chat 2026-10-17):** "i approve each m9 in b-d". Scope and guardrails are recorded in
  `plans/M9.md` §0: report every pre-declared output, label it post-hoc, and take no model decision from a test
  number.

## Codex final verdict (round 3, verbatim)
`VERDICT: AGREE`

## Provisional design decisions (Claude+Codex consensus, human to ratify)
- E3 onset-collapse check: fails if any unit's later onset rate is below 25% of its earlier rate; each unit needs
  ≥ 10 onsets in the earlier window or the check raises.
- Bootstrap: seed 20261017, B = 10,000, percentile 95% CI. Week blocks are primary (D-013); day and 24 h circular
  blocks are sensitivity.
- DM test: Newey–West Bartlett lags 24 and 72 on hourly loss sums.

## Accepted disagreements
- D-014 vs D-022/D-023 purge wording, and D-022 vs D-024 gap-interval wording: out of scope. M9 fits nothing and
  builds no mask; Codex ACCEPTED this.

## Proposed DECISIONS.md entry
D-033 (proposed): see `plans/M9.md` §F.
