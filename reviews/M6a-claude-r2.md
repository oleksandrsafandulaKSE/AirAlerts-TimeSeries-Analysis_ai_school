# M6a — Claude, round 2 response

Judgements on reviews/M6a-codex-r2.md:
- B1 hole acceptance = rule exception: AGREE. CLAUDE.md Architecture #6 has no exception, and D-026 forbids
  consensus rule changes.
- M2 retries cannot enforce the cap: AGREE. Rate isolation is now a deployment prerequisite.
- New: retry budget vs timeout: AGREE.

## Changes made
- §4.4: `accept_hole` removed (input, columns, test). A detected hole fails every run with nothing committed, and
  collection stops until the human decides. This complies with Architecture #6. The consequence is stated: a hole
  needs ~29 consecutive failed days. The recovery path is now a question for the human (§9 c), not part of the build.
- §3: the collector runs only with its own token, distinct from the Netlify/M8 one (separate token and separate IP
  isolate it whether the API limit is per token or per IP). The collector alone stays ≤ 1/min. The local dry run
  happens only with the collector token or with M8's schedule paused. The "combined ≤ 2/min" claim is removed.
- §3: retry budget is at most 2 retries per UID and 6 per run, with a 30 s per-request HTTP timeout (retryable).
  An exhausted budget fails the run and commits nothing. The worst supported run is ≈ 51 min. "Costs time, not data"
  is replaced by the true statement: the 29-day window overlap re-covers a failed day.
- §5: `timeout-minutes: 75`. The pull log gains `n_retries`.
- §6.6: spacing holds across retries. Budget exhaustion raises with nothing written. The worst schedule is
  simulated and its duration asserted < 55 min. §6.9 checks a 29-day gap (no hole), a 31-day gap (raises), and that
  a repeat attempt raises again.

## Disagreements
None.

## Design decisions taken
- PROVISIONAL: strict hole handling (collection stops; no built-in recovery).
- PROVISIONAL: retry budget 2/UID, 6/run; HTTP timeout 30 s; job timeout 75 min.
- PROVISIONAL (unchanged, Codex: within rules): seed ingestion, store unknown alert types, 24 unit UIDs,
  key (`id`, `updated_at`), `fetched_at` knowledge time + `as_known_at`, deletions undetected, raising window check.
- Deployment prerequisite (needs the human's action, not a rule change): a second alerts.in.ua token for the
  collector, stored under the existing secret name `ALERTS_IN_UA_TOKEN`.

## Escalations
None that the plan depends on. §9 (c) asks the human whether to ADD a hole-recovery exception to Architecture #6.
The plan as written does not need it.
