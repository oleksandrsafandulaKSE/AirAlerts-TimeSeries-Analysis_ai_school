# M1c — Claude response, round 1

## Changes made
None yet: the plan is paused on the escalation below. These items will be applied once the human chooses where
the check lives:
- B1 (document the causality exception): AGREE. The README bullet and the proposed decision entry will say
  plainly that these ends are retrospective, unknown at t for 59.6% of affected hours, and kept by human choice.
- AMB1 (print wording): AGREE. Print "exactly-3600 s durations (includes suspected parser-imputed ends)".
- AMB2 (whole-file count): AGREE. State that it is a data-quality check only, never read downstream, and
  include its scope in the decision entry.
- MISSING tests: AGREE. Use duplicate exact-hour rows, an exact-hour Luhanska row, mixed levels, an open
  alert, and expected = 0; assert totals and per-level counts after dedup and exclusion.
- MISSING sensitivity label: AGREE. "Post-hoc, frozen predictions, no refit, both predictors on the same
  remaining rows" (that is how followup.py computes it).
- MISSING protocol steps: AGREE. Reviewer, harness, human summary and proposed decision entry will be added.

## Disagreements
- B3 (add a delayed-recording witness to the leakage test): PARTLY. The current `truncate` in
  `tests/test_leakage.py` cannot see a fabricated end that is earlier than t (line 18–21). That is a real
  limitation, but Option 1 keeps the leak by the human's decision, so a test asserting the leak would only
  restate the note. The plan adds a docstring line to `truncate` and a README sentence instead. Codex may
  re-raise this.
- AMB3 (D-022 vs D-024, 145 hours): DISAGREE as out of scope. No mask changes in this plan, and the existing
  masks stay authoritative.
- MISSING "byte-identical": PARTLY. Instead of re-running the fit stage, compare hashes of the grid and
  feature frames from `run_all.build_frames` before and after, for both configs. That covers labels, masks,
  features and boundaries without touching registrations.

## Design decisions taken
None (paused).

## Escalations
- **B2 — the change as approved touches fingerprinted, pre-registered code.**
  `scripts/run_all.py:33` `code_fingerprint()` hashes every `src/*.py` file plus `scripts/run_all.py`. Both
  `reports/official*/preregistration.json` store that hash. Editing `src/config.py`, `src/data.py` or
  `scripts/run_all.py` (the plan's files 1–3) would:
  - fail `tests/test_improve_models.py::test_headline_code_fingerprint_matches_both_preregistrations` (passes
    now: `pytest -q tests/test_improve_models.py -k fingerprint` → 2 passed);
  - make `scripts/run_improve.py:151` refuse to run;
  - and, because the final test was already scored, it could not be re-registered without breaking the
    score-once protocol (D-021).

  The human must choose where the check lives (see the consensus record).
