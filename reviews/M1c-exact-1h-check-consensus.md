# M1c — consensus record

**Outcome: ESCALATION after round 1. The loop has stopped; waiting for the human.**

## Escalation
The approved Option 1 places the count, the M1 print and the raising check in `src/config.py`, `src/data.py`
and `scripts/run_all.py`. These files make up the code fingerprint stored in both pre-registrations
(`scripts/run_all.py:33`). Editing them would:
- break `tests/test_improve_models.py::test_headline_code_fingerprint_matches_both_preregistrations` (passes
  now);
- make `scripts/run_improve.py` refuse to run;
- leave no way to re-register, because the final test was already scored (D-021).

Choices for the human:
- **A. Keep the pipeline code frozen** (Claude's recommendation). Put the count and raising check in a new
  real-data test, `tests/test_data_quality.py`. It runs under `pytest`, which CLAUDE.md requires before any
  retrain, so a changed count still fails the run. A small non-fingerprinted script prints the M1-style
  numbers. The README documents everything. No fingerprint, registration or score changes.
- **B. Edit the pipeline code as originally planned,** and decide how to treat the fingerprint mismatch, for
  example by recording the current fingerprint as a post-hoc amendment next to the pre-registration. This
  changes the integrity protocol, so it is a rule decision.

## Codex final verdict (round 1, verbatim)
`VERDICT: CHANGES REQUIRED`

## Provisional design decisions
None yet. The agreed items from round 1 are listed in `reviews/M1c-exact-1h-check-claude-r1.md` and apply
under either choice.

## Unresolved
- B3, the delayed-recording witness test (Claude: PARTLY). Goes to round 2 after the human's choice.
