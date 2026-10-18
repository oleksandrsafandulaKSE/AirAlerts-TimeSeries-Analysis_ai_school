# M13 — Claude response, round 1

## Changes made
- B1 active flag: AGREE. `forecast.m12_state` always written; active+error → explicit unavailable state, no silent M8 fallback; test.
- B2 strip: AGREE. `/api/history.v2` (active snapshots only) + air-raid-only onsets; strip segments labelled per model.
- B3 kind parity: AGREE. Parity labelled as reconstruction; independent live tests (delayed discovery, level updates, coverage, unknown ends, standing alerts).
- A1 replay BSS: AGREE. 1 − SSE_blend/SSE_rule over identical rows with t < slider; "—" when undefined; labelled retrospective.
- A2 national share: AGREE. Pooled over fully covered units; unresolved-level onsets excluded; null when empty.
- A3 wording + bins: AGREE. Thresholds/tie/missing wording defined; 10 bins.
- A4 M8 label: AGREE. Provenance and the all-types target stated until the switch.
- M1 kind leakage tests: AGREE (truncation, leaky control, endpoints, DST, cap, Kyiv City/Kyivska). D-022/D-023 official-gap regressions are untouched (no official-data code changes in M13) and keep running in the full suite.
- M2 protocol: AGREE.

## Disagreements
- Q (D-027): not a new exception. CLAUDE.md's API merge rule ("remove duplicates by id, keep the latest updated_at") is the explicit, human-written rule; M6c-1 and M12 already use it as "event-time reconstruction", and M13 only DISPLAYS the M12 replay with that label. The live path (kind.mjs, the map) uses knowledge-at-τ (versions, firstSeen, endKnown). No escalation.

## Design decisions taken
- PROVISIONAL: kind wording thresholds (> / < / = 0.5); strip segments per model.

## Escalations
- None.
