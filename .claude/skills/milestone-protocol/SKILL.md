---
name: milestone-protocol
description: Mandatory work cycle for every task in this repo. Use at the start of any implementation work, any milestone, or when the human says "next step".
---

# Milestone protocol

Two planning levels (D-019).

0. ROADMAP (planning chat, once, and again only if the roadmap changes): general M1–M6 roadmap
   in `plans/ROADMAP.md` + README framing → `codex-plan-review` in roadmap mode (one round) →
   show the human Codex's items plus your lead judgment → STOP. The human corrects the roadmap.

Then, for each milestone (implementation chat):

1. PLAN — write: goal, files to touch, approach, how it will be tested, risks/assumptions,
   open questions for the human. Save it to `plans/M<n>.md` → run the `codex-plan-review`
   skill (one round) → show the human Codex's items plus your lead judgment → STOP and wait
   for approval.
2. IMPLEMENT — only the approved plan. If reality differs from the plan, stop and report.
3. TEST — run `pytest -q`. Print key numbers (shapes, date ranges, base rates).
4. REVIEW — invoke the `reviewer` subagent (ML validity), then run `code-review-harness` on the diff
   (runtime bugs). Fix FIX FIRST / high-severity issues, or explain why not. Never auto-commit.
5. SUMMARY for the human (keep it pasteable, under 250 words):
   - What changed (files)
   - Key numbers
   - Reviewer + harness verdicts, and what was fixed
   - Assumptions I made that you should check
   - Proposed DECISIONS.md entry
6. Wait. Do not start the next milestone.

Milestones:
M1 data + dedup + standing-alert/outage handling + oblast-union intervals + hourly grid + masking (+ tests)
M2 features at t + truncation leakage test with negative control
M3 baselines (incl. calibrated persistence) + walk-forward evaluation + within-oblast AUC
   [optional: week-block bootstrap CI vs recent-rate]
M4 LightGBM + inner-validation early stopping + calibration + per-group results
   [optional: reliability plot per group]
   + new-regime section (D-015): before/after table, frozen model on "any alert" target,
   within-oblast AUC + calibration-in-the-large [optional: red-only row]
   [optional after M4: weekly refit row (D-014)]
M5 README, figures, optional Streamlit page
M6 FUTURE WORK — only if the human starts it (D-016). Automated data workflow (GitHub Actions, no AI agents):
   M6a daily API fetch → append-only deduplicated CSV of closed alerts, committed (+ one manual test run;
       if the API returns 403 to GitHub's servers, fall back to a self-hosted runner)
   M6b monthly retrain + evaluation with the approved pipeline → reports/monthly/<YYYY-MM>/;
       the yellow-regime model trains only once >= 3 months of API history exist
