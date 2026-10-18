# M9 — Claude response, round 1

## Changes made
- **B1 (D-028 / D-030 not ratified): AGREE.** `grep "^## D-" DECISIONS.md` ends at D-027. The plan now cites
  the fingerprint as a code fact (`scripts/run_all.py:33` plus the fingerprint test), and states that D-028 and
  D-030 authorize nothing.
- **B2 ("statistically tied"): AGREE.** The README wording is now "the interval includes zero: no evidence of
  improvement". It never says "tied" or "equivalent", since no equivalence margin was set in advance.
- **AMB hourly-mean estimand: AGREE.** DM now runs on hourly SUMS S_h with a Newey–West variance. ΣS_h /
  N_rows is the row-weighted mean, the same estimand as BSS's numerator.
- **AMB block details: AGREE.** Selection probabilities, K, variable resample length, partial weeks, circular
  wrap, and the ΣBrier_rr = 0 rule (raise) are now spelled out. Rows are never invented.
- **AMB validation join: AGREE.** Unique keys, identical key sets, identical `y`, UTC-aware timestamps, and
  groups via `regions.group_of`. Any mismatch raises.
- **MISSING PAV fixture: AGREE.** A hand-calculated miscalibrated fixture (p = .1/.2/.3/.4, y = 0/1/0/1 →
  MCB 0.150, DSC 0.125, UNC 0.25) fails if p is returned unchanged.
- **MISSING skip vs fail: AGREE.** Real-data tests now behave exactly like `tests/test_leakage.py`'s `real`
  fixture, and `run_extras.py` raises on missing inputs or changed pins.
- **MISSING E2 / E1 details: AGREE.** E2's leaky and causal label construction is defined. Witnesses are exact,
  non-empty and pinned, including the t+H right endpoint and the cut-off equality, and each leaky feature has a
  causal companion. E1 adds the 23 h and 25 h Kyiv DST days and the midnight hours.
- **MISSING E3 zero counts: AGREE.** Each unit needs ≥ 10 earlier onsets or the check raises. A synthetic
  all-levels fixture, with a > 24 h standing alert, must fail under an oblast-only mutation.

## Disagreements
- **AMB D-014 vs D-022/D-023 purge wording: DISAGREE (out of scope).** M9 has no cut-off, no fit and no purge.
  It reads the frozen `status` column, and the frozen masks stay authoritative. Not edited.
- **AMB D-022 vs D-024 interval wording: DISAGREE (out of scope),** for the same reason. M9 neither builds nor
  changes any mask.

## Design decisions taken
Each is PROVISIONAL (Claude+Codex consensus, human to ratify):
- the E3 threshold of 25%, with ≥ 10 earlier onsets per unit;
- the bootstrap seed 20261017 and B = 10,000;
- Newey–West lags 24 and 72.

## Escalations
- **QUESTION FOR THE HUMAN (Codex), also B1: AGREE, escalated.** CLAUDE.md forbids "any statistic computed over
  the test period", and "make a plan" is not an explicit exception. §§B–D on TEST rows need explicit, scoped
  approval:
  - the block-bootstrap CI and DM test on frozen test predictions;
  - CORP/PAV curves fitted on test labels, as a diagnostic only;
  - per-group calibration-in-the-large CIs on test.

  Without approval, §§B–D run on validation only, and §A and §E proceed as planned.
