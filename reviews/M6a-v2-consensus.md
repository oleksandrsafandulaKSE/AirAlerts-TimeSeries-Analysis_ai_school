# M6a v2 — consensus record (codex-plan-review, D-026)

- **Outcome:** CONSENSUS after 3 rounds on the plan as changed by the human's M6 definition (`plans/M6-definition.md`,
  2026-10-17). Codex: VERDICT: AGREE, Claude has no open disagreement, no escalation.
- The first loop is in `reviews/M6a-consensus.md` (4 rounds, AGREE). This loop: `reviews/M6a-v2-codex-r{1..3}.md`,
  `reviews/M6a-v2-claude-r{1,2}.md`. The first round-3 attempt failed before Codex ran (`script: tcgetattr/ioctl`,
  log kept as `reviews/M6a-v2-codex-r3-failed-attempt.log`); it was re-run unchanged.

## Codex's final verdict (verbatim)
> NEW ISSUES: None introduced by these changes. […]
>
> VERDICT: AGREE

## What changed vs the first consensus
- The human's decision: the same token as M8, collector at 1 request / 2 min (worst successful run ≈ 64 min; job
  timeout 90 min). The first fetch is local and committed in M6a. The plan states why `alert_level` / `alert_type`
  must be kept (the future yellow/red forecast).
- Found by Codex and verified on the dump: 5 records have `notes == ""` (3 in collected UIDs), and `id` and
  `location_oblast_uid` are ints. The fix is canonical types plus a reversible backslash cell encoding.
- `as_known_at` now also drops future starts, with witnesses for the future start and end. There are two named
  views: OBSERVED vs EVENT-TIME RECONSTRUCTION (M6c-1 can only use the latter for Sept–Oct history).
- Retry diagnostics on every attempt; `n_retries_429` / `n_retries_other`; per-unit date ranges; `git_commit` =
  HEAD before collection; "24 ADDITIONAL log rows" per pull.

## PROVISIONAL decisions (Claude+Codex, human to ratify) — in addition to reviews/M6a-consensus.md
1. Cell encoding: empty = null (or absent raion); `\e` = ""; a leading `\` is escaped by doubling.
2. Sept–Oct history is used through the event-time reconstruction (as with the official data); never described as an
   observed replay.

## Human decisions this plan depends on (proposed D-033..D-037, not authorized by consensus)
Typed targets, API training, train-now/fully automatic, site scope, shared token. See `reviews/PROPOSED-DECISIONS-M6.md`.
