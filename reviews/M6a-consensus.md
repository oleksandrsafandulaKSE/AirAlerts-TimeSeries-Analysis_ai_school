# M6a — consensus record (codex-plan-review, D-026)

- **Outcome:** CONSENSUS after 4 rounds. Codex VERDICT: AGREE, Claude has no open disagreement, and no escalation
  is needed for the plan as written.
- Plan: `plans/M6a.md`. Rounds: `reviews/M6a-codex-r{1..4}.md`, `reviews/M6a-claude-r{1..3}.md`.
- Infrastructure note: the first round-4 attempt failed before Codex ran (`script: tcgetattr/ioctl: Operation not
  supported on socket`, log kept as `reviews/M6a-codex-r4-failed-attempt.log`). It was re-run once, unchanged, and
  succeeded.
- Nothing was implemented. No API call was made, and no workflow file or data was written.

## Codex's final verdict (round 4, verbatim)
> NEW ISSUES: None introduced by these changes.
>
> VERDICT: AGREE

## What the loop changed (summary)
- R1: added a "known at t" contract (`fetched_at` ≤ t, then the latest `updated_at`, then ends > t hidden) with a
  negative control. Dropped `n_vanished`, which was unreconstructable. Coverage is now NOMINAL with a raising
  window check. Null ↔ empty round-trip is lossless. Added crash-consistency between the CSV and the pull log,
  DST / Kyiv City vs Kyivska / old-open-alert witnesses, and the reviewer + harness in "done".
- R2: hole handling made strict (a detected hole → nothing committed, collection stops) per CLAUDE.md Architecture #6;
  the `accept_hole` override was removed as a rule change. A separate collector token became a deployment
  prerequisite (M8 uses the same API at 1 history request/min). Added a retry budget and a 75 min job timeout.
- R3: the worst-case timing test now fits the retry budget (53 min).

## PROVISIONAL decisions (Claude+Codex consensus, human to ratify)
1. Seed `datastore/alerts_in_ua.csv` from the 2026-10-12T1645Z dump (keeps alerts finished 2026-09-12 → ~09-18,
   no longer fetchable).
2. One CSV row = one record VERSION, key (`id`, `updated_at`), append-only (byte-prefix guard). D-027 view = latest
   `updated_at` per id.
3. Knowledge time = `fetched_at` of the pull that first saw a version; reference selector `collect.as_known_at`.
4. Fetch only the 24 unit UIDs; map rows by the requested UID, never `location_oblast_uid`.
5. Keep all alert types (unknown new types are stored, not raised); keep open alerts.
6. Requests ≥ 65 s apart; retries 2 per UID and 6 per run; HTTP timeout 30 s; job timeout 75 min; daily cron at
   03:17 UTC.
7. Strict holes: a detected coverage hole fails every run and commits nothing, with no built-in recovery.
8. API deletions are not detected (known limitation).
9. Per-pull window check: earliest `finished_at` ≥ fetched_at − 30 d − 1 h, else raise.
10. Pull log at `reports/collect/pull_log.csv` (run metadata, like `run_meta.json`).
11. 403 fallback = self-hosted runner selected by the repo variable `COLLECT_RUNNER` (public repo → no PR triggers).

## For the human (not decided by the loop)
- (a) Confirm that committing OPEN alert versions is covered by D-027 / CLAUDE.md "API merge rule (M4/M6) … KEEP
  open alerts". D-016 still says "closed alerts". Codex accepted it as covered.
- (b) Deployment prerequisite: a second alerts.in.ua token for the collector, stored as the GitHub secret
  `ALERTS_IN_UA_TOKEN`.
- (c) Optional rule exception: allow a human-acknowledged coverage hole to be recorded so collection can resume
  (exception to CLAUDE.md Architecture #6). Not built.

## Unresolved items / escalations
None.
