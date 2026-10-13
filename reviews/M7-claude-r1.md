# Claude response, round 1 — plans/M7.md

## Changes made
- B1 offset inference — AGREE: §2.1 specifies offsets for fit, early-stopping, validation and test rows, clipped logits, p = sigmoid(offset + raw residual), save/reload reproduction, and a zero-residual oracle test.
- B2 prior leakage — AGREE: the shrink prior is now CAUSAL — the unit's expanding onset rate over rows with s ≤ t − H (national fallback; undefined → dropped, counted). No fold or early training row sees later outcomes; no per-fold fitting needed.
- B3 identical keys — AGREE: every paired block comparison and the V2/V3/V5 validation selection use identical scoring keys.
- A1 greedy rule — AGREE: candidate = accepted set + block vs reference = accepted set; relative 0.5 %; equal-weighted fold mean; ≥ 3 of 4 folds; ties reject.
- A2 definitions — AGREE: merged onsets; pooled national rate; "yesterday" in UTC; Kyiv hour ±1 mod 24 from each onset's UTC time; insufficient history → NaN → dropped.
- A3 boundaries — AGREE: t + H ≤ end for every fit/early-stopping slice; each refit scores only its next week.
- M1 witnesses/fixtures — AGREE (§5). M2 reporting extras, decision entry, evidence table — AGREE (§6, §8).
- Q1 score-once — the human approved post-hoc labelled rows in chat ("agreed" to my recommendation that explicitly said "two clearly labelled extra rows … the frozen headline"); recorded in §0 as an authorised exception (proposed D-030) for labelled post-hoc rows only; the CLAUDE.md ban on test statistics in FEATURES still holds.

## Disagreements
- Q2 (gap bounds): already reconciled and tested in M3 (M3 decision 4; config.gap_label_mask_interval; check_gap_rows asserts 145 h on the real grid). M7 reuses the headline's config unchanged; no new ratification needed.

## Design decisions taken
- PROVISIONAL: fold cut-offs and the 0.5 % / 3-of-4 rule; causal expanding prior; V5 on V3; H = 1 only.

## Escalations
(none — the post-hoc exception was approved by the human in chat.)
