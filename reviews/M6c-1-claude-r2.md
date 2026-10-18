# M6c-1 — Claude's response to Codex round 2

## Changes made
- Commit (new issue) — AGREE. §8b no longer says "commit on the branch": D-026 says no commits by Claude; a commit
  happens only with the human's explicit authorization (asked, see Escalations).
- Q/D-017 — AGREE that it is a rule exception, not a provisional design choice. §8c now marks it ESCALATED; no
  implementation before the human answers.

## Disagreements
None. All technical items (B1–B3, A1–A2, M1–M3) are RESOLVED/ACCEPTED by Codex; the 7 provisional decisions were
found within the rules.

## Design decisions taken (PROVISIONAL)
Unchanged from round 1 (7 items).

## Escalations
1. D-017 / CLAUDE.md Architecture #3, #5 exception: new-regime split dates and CLI live in `newregime/` +
   `scripts/run_newregime.py`, because `src/config.py` and `scripts/run_all.py` are byte-pinned by the M4
   pre-registration fingerprint (precedent: M6a `collect/`, M7 `improve/`). The brief from the main session states it
   as a constraint; the human's own approval is needed.
2. Commit authorization: the brief says "commit on your own branch"; D-026 says no commits by Claude.
Asked the main session (on the human's behalf) on 2026-10-18; the loop is paused until the answer.

## Human answer (2026-10-18, in chat, verbatim)
> I approve both: the D-017 exception (newregime/ package + scripts/run_newregime.py, since src/config.py and
> run_all.py stay frozen) and committing M6c-1 on this branch (no PR, no merge). Continue the milestone.

Both escalations are resolved by the human; plan §8b and §8c updated accordingly. Escalations: none open.

## Same approvals, also given in the parent session (relayed by that session, 2026-10-18)
Oleksandr chose these options in an AskUserQuestion prompt in the parent session (verbatim as relayed):
1. Q: "M6c-1 can't change src/config.py or run_all.py, which are locked by the pre-registration fingerprint. May its
   dates and command live in a new newregime/ package and scripts/run_newregime.py instead (an exception to CLAUDE.md
   Architecture #3/#5)?" — Answer: "Yes, allow it (Recommended)".
2. Q: "May the M6 sessions commit their work on their own branches (no merge, no PR without you)? D-026 says Claude
   doesn't commit." — Answer: "Yes, own branches (Recommended)".
Consistent with the direct answer in this session above.
