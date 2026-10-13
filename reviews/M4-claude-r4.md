# Claude response, round 4 → round 5 — plans/M4.md (implementation correction)

Round 4 reached VERDICT: AGREE. While implementing, reality differed from §5.2, so this round reviews one change only.

## Changes made
- §5.2 `history_start`: the plan defined it as "earliest start among CLOSED alerts" and asserted ≥ 2026-09-12. The data gives 2026-09-11 05:50 → the assertion would fail, and the definition is wrong. Evidence (dump 2026-10-12T1645Z): `month_ago` is bounded by FINISH time: for every one of the 24 units' files, earliest `finished_at` ≥ `fetched_at − 30 days` (closest margin 3.3 min); 53 closed alerts started before the cutoff and are present only because they ended after it (survivorship). Completeness holds only for alerts starting ≥ the cutoff. New definition: `history_start` = max over the 24 files of (`fetched_at` − 30 days) = 2026-09-12 17:00:43 UTC, fixed in config and asserted against the manifest. Earlier-starting alerts are kept for interval construction; the existing history-start uncertainty zone [−∞, history_start + 24h) keeps their incompleteness out of every scored row (state/labels masked, windows and time-since NaN).
- Consequence: the scored API window is essentially unchanged (warm-up still ends ≈ 7 days after history_start + 24h).

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL: history_start = max(fetched_at − 30 days) over the 24 units' files (implements §5.2's intent "the start of the month_ago window"; no rule change).

## Escalations
(none)
