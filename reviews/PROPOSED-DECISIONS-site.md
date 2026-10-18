# Proposed DECISIONS.md entries — site redesign (the human edits and commits; see plans/site-redesign-definition.md)

## D-041 — Site redesign: one job per page (me, 2026-10-18, grilling session)
- The main page is the interactive oblast map "Will there be an alert in 1 / 3 / 6 / 12 / 24 h?"; study evidence moves to
  tabs (Replay, Forecast check, How good is it?, What kind of alert?, About) and the README. Oblasts only; English only;
  current visual system.

## D-042 — Live map model = M6c-1 "any" blend (me, 2026-10-18)
- Replaces the M8 live model (official-data V2 offset, H = 1). The frozen official model remains the study headline on
  "How good is it?". Exploratory evidence: one test week.

## D-043 — "Any" horizons 6, 12, 24 h (me, 2026-10-18)
- Same target and mask as H = 1/3, M6c-1 pipeline; yellow/red stay at H = 1/3. New horizons need their own later test
  week (the M6c-1 reservation refuses overlapping weeks); until then validation-only, labelled.

## D-044 — Yellow/red beyond the hover (me, 2026-10-18)
- Amends D-036/D-040: hover note + click card + a separate "What kind of alert?" page, always "in testing / in training".
  "If an alert starts, red or yellow" = the oblast's 7-day red share of air-raid onsets (simple rule) until a red model
  beats it in the monthly chart.

## D-045 — Main map is air-raid only (me, 2026-10-18: "Approve D-045")
- Live labels, masks, features, baseline and scorer for the main map use `alert_type == air_raid`, matching the M6c-1
  models. Amends D-040's clause "the any map keeps all API alert types".
