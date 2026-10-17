# M6a v3 (gap-resume addendum) — Claude, round 1 response

Judgements on reviews/M6a-v3-codex-r1.md:
- B1 the crash repair leaves orphan hole rows: AGREE.
- B2 the workflow doesn't stage the holes file: AGREE. Verified: `.github/workflows/collect_api.yml` lists only the
  CSV and the log.
- A1 hole endpoints: AGREE. A2 stale §9 wording: AGREE.
- M1 executed exit-code tests: PARTLY (see Disagreements). M2 the holes path, missing file and dry-run: AGREE.
  M3 downstream contract: AGREE.

## Changes made
- §4.4: the repair restores BOTH the CSV and the holes file to their last committed state. The consistency check
  covers holes pull_ids. §6.9 tests detection, repair and restart, including a pull with 0 alert rows but a hole row.
- §5: change detection and `git add` name all three files, committed together.
- §4.4: a hole is the OPEN interval (hole_from, hole_to); pull windows are closed. An endpoint test uses the helper
  `covered()`.
- §4.4: a downstream contract for M6b/M6c. A hole is missing data, handled like the official gap: masked, with a
  24 h post-hole mask, look-back features touching it set to NaN, and labels touching it dropped. Subtracting the
  hole doesn't make rows eligible.
- §4.4: `--holes PATH` (default `reports/collect/coverage_holes.csv`). A missing file means no holes. It gets the
  same guards as the log, and the dry run copies it.
- §9: (a)/(c) are marked answered (D-038/D-039) and the strict-version sentence is superseded.
- §6.9: executed exit-code tests (CLI `main()` 0/3/failure; the collect-step shell run with bash and a stub).

## Disagreements
- M1, PARTLY: running the full commit step needs a real git remote, which the existing harness review already
  simulated once (a clone with `pull --rebase` + push). The tests will execute the collect-step shell (where the
  exit code can be lost) and check the routing conditions and the three-file staging text. They won't execute
  `git push`. Evidence: no git remote is available offline in tests, and a push simulation would need network-free
  bare repos with more fixture code than the step itself.

## Design decisions taken
- PROVISIONAL: hole file `reports/collect/coverage_holes.csv` with columns `pull_id, uid, unit, hole_from, hole_to,
  git_commit`; exit code 3 = "data written, hole recorded".

## Escalations
None. D-038/D-039 are the human's (2026-10-17, chat).
