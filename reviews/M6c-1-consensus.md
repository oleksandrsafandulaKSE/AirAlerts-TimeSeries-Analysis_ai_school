# M6c-1 — consensus record (codex-plan-review, D-026)

- **Outcome:** CONSENSUS after 3 rounds. Codex: `VERDICT: AGREE`; no open disagreement; no open escalation.
- Round 2 escalated two items to the human; the human answered in chat on 2026-10-18 (verbatim in
  `reviews/M6c-1-claude-r2.md`): "I approve both: the D-017 exception (newregime/ package + scripts/run_newregime.py,
  since src/config.py and run_all.py stay frozen) and committing M6c-1 on this branch (no PR, no merge)."
- Files: `reviews/M6c-1-codex-r{1,2,3}.md` (+ `.log`), `reviews/M6c-1-claude-r{1,2}.md`.

## Codex's final verdict (verbatim)
> NEW ISSUES: None introduced by the round-2 changes. No remaining blocker identified.
>
> VERDICT: AGREE

## Changes from the loop
- Blend `n` = distinct type-T onset EVENTS (an H = 3 onset counts once), window rows W(t) defined precisely.
- Red-share baseline on common support (ANY-eligible rows; rr_any exists on ANY-masked RED rows).
- The validation-week blend is a RETROSPECTIVE DIAGNOSTIC (model early-stopped/calibrated on that week); the
  test-week blend is the causal result. End-to-end test: fitting on data reconstructed at the test start gives
  byte-identical models.
- Test-once reservation keyed by split, exclusive create before any test label is read.
- Pre-registration hashes the datastore, pull log, holes file and `collect/api_collector.py` too.
- Typed boundary witnesses (24 h cap, (t, t+H] edges, purge edge, DST end, synthetic hole), per-type negative control.
- Official-data tests run through a gitignored, read-only `data` symlink to the main checkout; project venv.

## Human-approved (not consensus)
- D-017 / CLAUDE.md Architecture #3, #5 exception: `newregime/` + `scripts/run_newregime.py`.
- Commit M6c-1 on this branch; no PR, no merge (exception to D-026's "no commits by Claude").

## PROVISIONAL decisions (Claude+Codex consensus, human to ratify)
1. Blend window = out-of-sample rows only (s ≥ the model's fit cut-off); n = distinct onset events; pooled; n0 = 50;
   28 days (Q7, Q8).
2. Red-share extra baseline on common ANY-eligible support (Q9).
3. Coverage holes → national missing-data intervals with the official gap treatment (Q10).
4. Reporting = existing `metric_table` groups, within-oblast AUC only with ≥ 10 pos and ≥ 10 neg, low-n flags (Q12).
5. Validation-week blend reported only as a retrospective diagnostic.
6. Split-keyed exclusive test reservation under `reports/newregime_test_access/`.
7. `air_raid` only (the artillery question from M4 stays with the human).

## Unresolved items / escalations
None.
