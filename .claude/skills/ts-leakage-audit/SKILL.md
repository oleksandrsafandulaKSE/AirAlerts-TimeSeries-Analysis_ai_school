---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one after 2025 reform
   and one near a DST change).
2. Build features from the FULL raw data. Take the row for (oblast, t).
3. Cut the raw data so only events known at t remain: drop alerts with started_at > t,
   and set finished_at = NaN where finished_at > t (the end was not yet known).
4. Rebuild features from the cut data. Take the row for (oblast, t).
5. Assert both rows are equal for every feature column.
If this fails, a feature looks into the future. Report which column.

## Checklist
- Rolling windows: right-aligned, end at t, exclude (t, ...].
- No fit on full data: scalers, encoders, climatology tables are fit on train only.
- Split by date. No shuffle. max(train time) < min(test time); also no overlap of target
  windows (t, t+H] across the boundary.
- Early stopping and tuning use validation from the end of train.
- Climatology baseline uses train period only.

## Report format
Table: check | PASS/FAIL | evidence.
