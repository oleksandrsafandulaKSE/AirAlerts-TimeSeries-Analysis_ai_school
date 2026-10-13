# Claude response, round 3 — plans/M4.md

## Changes made
- B1 (test expectation) — AGREE: §7 `test_api_loader` now expects an open alert to be KEPT with `finished_at` = NaT, counted, masking exactly [start, start + 24h) with its start as an onset (hand-checked).
- A2 (exposure) — AGREE: §5.3 exposure excludes only the official gap zone and the API history-start zone; open alerts create no zones (D-027).
- NEW blocker (gap detection over 2024 → 2026) — AGREE, verified in code: `grid.detect_gaps` (src/grid.py) builds the hourly range from min to max start. §5.2 now restricts API gap detection to alerts starting inside [history_start, coverage_end) via a new explicit range argument (official keeps its full range, so H = 1 / H = 3 outputs are unchanged); older open alerts stay in interval construction. Regression fixture added to §7's plan text (§5.2).

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): LightGBM params; ECE 0.02 + Platt; new-regime grid end 2026-10-12 16:00; low-n threshold.

## Escalations
(none)
