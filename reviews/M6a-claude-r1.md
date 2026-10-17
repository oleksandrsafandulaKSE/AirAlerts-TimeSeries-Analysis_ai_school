# M6a — Claude, round 1 response

Judgements on reviews/M6a-codex-r1.md:
- B1 commit-on-hole vs D-017 #6: AGREE. CLAUDE.md Architecture #6 says detected gaps make the run fail with
  nothing committed.
- B2 "known at t" selection order: AGREE.
- B3 `n_vanished` not reconstructable: AGREE. First-seen versions plus counts lose sightings.
- A1 coverage rests on an undocumented contract: AGREE.
- A2 null → "" vs `api_alerts`: AGREE. `src/data.py:174` parses `finished_at`, and an empty string is not NaT-safe
  the way None is. Also agree to parse timestamps.
- M1 crash between the two writes: AGREE.
- M2 M8 rate coordination: PARTLY (see Disagreements).
- M3 compatibility witnesses: PARTLY (see Disagreements).
- M4 done criteria omit the reviewer, harness and summary: AGREE.
- Q (D-016 "closed" vs D-027): AGREE that the human should confirm it. Not an escalation: CLAUDE.md:139 already
  reads "API merge rule (M4/M6) … KEEP open alerts".

## Changes made
- §4.4: a hole now fails the run with nothing committed (D-017 #6). Recovery is an explicit human re-run with
  `accept_hole=<previous pull_id>`, recorded in `accepted_hole_from/to`. The commit-then-fail logic is gone.
  §5 has the new `workflow_dispatch` input, and a collector exit ≠ 0 stops the job before the commit.
- §4.2: a "known at t" contract with reference function `collect.as_known_at`: filter `fetched_at` ≤ t, take the
  latest parsed `updated_at`, then hide ends > t. Knowledge time is never backdated, and seeded rows are unknown
  before the dump fetch. §6.2 gets a delayed-closure + correction test with a naive-selector NEGATIVE CONTROL.
- §4.4: `n_vanished` removed. Deletions are not detected (listed as a limitation in §8).
- §4.4: coverage renamed NOMINAL, with a `nominal_window_from` column. §4.3 adds a per-pull window check (earliest
  `finished_at` ≥ fetched_at − 30 d − 1 h, else raise) as evidence for the contract. Event coverage and knowledge
  time are separate columns.
- §4.1/§4.3: empty field ↔ None via `collect.read_datastore()`. An API empty string raises, so the round-trip is
  lossless. Timestamps are parsed for validation and the raw strings are stored. Tests in §6.8.
- §4.4: write order (CSV rename, then log rename) and a start-up consistency check (CSV pull_ids ⊆ log pull_ids,
  else raise with the repair). Test in §6.9.
- §3: the M8 interaction is documented, and 429 now gets up to 3 retries of 120 s.
- §6.10: witnesses for Kyiv City 31 vs Kyivska 14, an open alert > 24 h old, and DST-edge UTC strings.
- §7: reviewer + harness + summary + proposed DECISIONS entry added to "done".
- §9: two items for the human (open versions under D-027; a separate token).

## Disagreements
- M2 "test combined traffic with delayed invocations": PARTLY. The two callers run on different platforms
  (Netlify cron, GitHub Actions) with no shared state, so a "combined" test could only test a simulation of both,
  not the real coupling. The plan bounds the collector to ≤ 1/min and makes a collision cost a retry (429 → 120 s
  wait, 3 retries), not data. The real fix (a second token) is the human's choice, listed in §9.
- M3 "preserve gap-edge, rolling-window and cut-off regressions": PARTLY. M6a edits no `src/` file (enforced by the
  code-fingerprint test), and the full `pytest -q` stays in "done", so the existing regressions are kept unchanged.
  M6a adds no grid or feature code, so there is no new causal feature behaviour to test beyond `as_known_at`.

## Design decisions taken
- PROVISIONAL: hole recovery by a human `workflow_dispatch` re-run with `accept_hole=<previous pull_id>`.
- PROVISIONAL: deletions by the API are not detected in M6a.
- PROVISIONAL: the window check (earliest `finished_at` ≥ fetched_at − 30 d − 1 h) raises.
- PROVISIONAL: knowledge time = `fetched_at` (daily granularity); `as_known_at` is the reference contract for M6b.
- PROVISIONAL (from the plan): seed from the 2026-10-12 dump; store new `alert_type` values; 65 s request spacing;
  key = (`id`, `updated_at`); 24 unit UIDs only.

## Escalations
None.
