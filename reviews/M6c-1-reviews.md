# M6c-1 — reviewer subagent + harness review (2026-10-18)

## Reviewer (ML validity), run BEFORE the test week was scored
Verdict: SHIP once two cheap fixes are in. FIX FIRST: none (purge, label isolation, causal rolling windows, the
byte-identical fit on data cut at the test start, the per-type negative controls, and red-during-yellow were all
verified).
- SHOULD FIX 1: the fit stage printed base rates and onset counts that included the test week. FIXED before the
  test (prints now cover t + H ≤ test start; test-week rows are counted only). The earlier print had already
  happened once in this session; it mixed train, validation and test, and nothing was tuned on it.
- SHOULD FIX 2: the test lock was keyed by split name. FIXED before the test (keyed by the test dates); after the
  harness review it also refuses any OVERLAPPING week.
- SHOULD FIX 3: the test-week blend weight comes from the validation week, where the model was early-stopped and
  Platt-calibrated (w ≈ 0.93 for any/yellow at test start; n0 = 50 barely shrinks it). Kept (the agreed design);
  stated in the metrics notes, the D-040 draft and the summary.
- Notes fixed: per-predictor notes, `_retrospective` columns in val_predictions, π_u on ANY-eligible train rows, a
  printed count of dropped common-support rows, `test_hole_masks` for every type, val reproduction matches `t` too.
- Note kept: recent rate's within-oblast AUC < 0.5 on validation (stated in reporting).

## Harness review (runtime), run AFTER the test week was scored
Committed first as aa05529 (the exact code that produced reports/m6c1); fixes in the next commit:
1. The official-model check (and package versions) ran after the reservation → a failure there would burn the test
   week. FIXED: every check runs before `reserve()`; package versions are pre-registered.
2. An overlapping test week (e.g. one hour shorter) got a fresh lock. FIXED: `accessed()` refuses any overlap.
3. Adjacent holes covering one gap together raised. FIXED: holes are merged.
4. Inverted pull windows, holes outside coverage, timestamps without 'Z' were accepted/raised a bare TypeError.
   FIXED: they raise.
5. Hard-coded week in plot titles. FIXED: from the split.
Not changed: the rolling red share counts rows with mask == 0 and both labels known (the src `recent_rate` row rule),
while π_u uses eligible train rows; the plan's wording "ANY-eligible" is read as that row rule for the rolling part.
Regression tests added for 1–4.
