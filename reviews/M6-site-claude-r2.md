# M6-site — Claude, round 2 (answer to reviews/M6-site-codex-r2.md)

## Changes made
- M4 — AGREE: contract gains `available_at`; `typedModel` is a list of versions, the one with the latest
  `available_at ≤ τ` is used, later ones are skipped at τ (none → baseline only); a version with
  trained_through + 1 h > available_at is malformed and throws. Tests: a late version is skipped at τ and used after it;
  a single late model alone → baseline only.
- Q1/P1 — AGREE: typed targets now inherit M8's human-approved set (all API types; `TYPED_ALERT_TYPES` re-exported from
  live.mjs `ALERT_TYPES`, one list). The card states it. Parity uses `config.new_regime_all_types()`. Air-raid-only is
  moved to "Open questions for the human" as a possible target change, not decided by the loop.

## Disagreements
(none)

## Design decisions taken (PROVISIONAL)
- P1 (revised): typed alert types = M8's approved set (no new decision; inherits the human's).
- P8 (revised): versioned, causally selected typed-model plug-in.
- P2–P7 unchanged.

## Escalations
(none — the air-raid-only option is listed for the human without being adopted)
