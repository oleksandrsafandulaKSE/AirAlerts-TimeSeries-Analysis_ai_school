# M6a v2 — Claude, round 1 response

Judgements on reviews/M6a-v2-codex-r1.md:
- B1 empty strings: AGREE. Verified: the dump has `notes == ""` for ids 266250 (UID 14), 262685, 262686 (UID 15),
  plus 2 records in UIDs that are not collected. All other nullable fields are None or str.
- A1 types: AGREE. Verified: `id` and `location_oblast_uid` are int, and every other present field is str or None.
- A2 log rows: AGREE. A3 `git_commit`: AGREE. M1 the known-at-t future start + witnesses: AGREE.
- M2 retry diagnostics: AGREE. M3 date ranges + empty response: AGREE.
- Q (seeded rows unknown before 12 Oct): AGREE that the distinction must be explicit. Resolved within the rules (see
  Design decisions), not sent to the human.

## Changes made
- §4.1: canonical types, plus a reversible cell encoding (null/absent → empty cell; `""` → literal `""`; an API
  string equal to that literal raises). The reader decodes to canonical types, and keys/comparisons use the decoded
  values. Present-but-null `location_raion` raises.
- §4.2: `as_known_at` drops selected versions with `started_at` > t. Two named views: OBSERVED (`as_known_at`) and
  EVENT-TIME RECONSTRUCTION (full history truncated by event timestamps, as the official data is used). Results from
  (B) are never described as an observed replay, and M6c-1 defines its protocol.
- §4.3: per-UID min/max `started_at`, min `finished_at`, EMPTY responses, overall date range, and sanitized
  per-attempt retry diagnostics.
- §4.4: `n_retries_429` / `n_retries_other`. `git_commit` = checkout HEAD before collection.
- §6.2: witnesses for the future end and the future start, with boundaries. §6.5: exhausted-429 output + unchanged
  files. §6.8: wrong types, present-null raion, the literal `""`, and a real-data witness for the 3 records with
  `notes = ""` covering reload + re-merge.
- §7: "exactly 24 ADDITIONAL rows with that run's pull_id".

## Disagreements
None.

## Design decisions taken
- PROVISIONAL: cell encoding (empty = null/absent; literal `""` = empty string).
- PROVISIONAL: M6c-1 training on Sept–Oct history uses the EVENT-TIME RECONSTRUCTION. This is the same treatment
  the official dataset already gets (CLAUDE.md features "computable from data with timestamp <= t", leakage audit
  "hide ends > t"), so it needs no new rule. The OBSERVED view is for audits of live operation.

## Escalations
None.
