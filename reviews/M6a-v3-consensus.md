# M6a v3 (automatic resume after a coverage hole) — consensus record (codex-plan-review, D-026)

- **Outcome:** CONSENSUS after 3 rounds. Codex: VERDICT: AGREE, no open disagreement, no escalation.
- Trigger: the human answered plan §9 in chat (2026-10-17). (a) Commit open versions: yes (proposed D-038).
  (c) Resume after a hole: yes, AUTOMATICALLY (proposed D-039, an exception to CLAUDE.md Architecture #6). These are
  the human's rules, not consensus decisions.
- Files: `reviews/M6a-v3-codex-r{1..3}.md`, `reviews/M6a-v3-claude-r{1,2}.md`. One round-2 call was stopped and
  discarded before it finished: it had started on an unedited plan because of a failed edit, and was re-run on the
  edited plan.

## Codex's final verdict (verbatim)
> NEW ISSUES: None introduced by these revisions. […]
>
> VERDICT: AGREE

## Changes from the loop
- The crash repair restores BOTH the CSV and the holes file. The holes file always exists, is tracked, and starts
  header-only.
- The workflow detects, stages and commits all three files. Exit code 3 commits, then fails the run.
- A hole is an OPEN interval (hole_from, hole_to), with endpoint tests.
- A downstream contract: a hole is missing data (mask, plus a 24 h post-hole mask, look-back features NaN, labels
  touching it dropped).
- Tests execute the CLI's exit codes and the workflow shell against a local bare git origin (codes 0/3/1).

## PROVISIONAL decisions (Claude+Codex, human to ratify)
1. `reports/collect/coverage_holes.csv` (`pull_id, uid, unit, hole_from, hole_to, git_commit`), header-only from the
   start.
2. CLI exit code 3 = "data written, hole recorded".
