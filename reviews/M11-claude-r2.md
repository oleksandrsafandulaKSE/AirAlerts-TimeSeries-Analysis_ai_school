# M11 — Claude response, round 2

## Changes made
- Rejections after issue (OPEN): AGREE (verified `live.mjs:16` REJECT_KEEP = 1 day, `applyHistory` calls `markRejected`). New persistent `rejection_log` (35 days); any rejection for the unit logged at ≥ τ − 24 h excludes the row; tests for a post-issue rejection, the boundary, and survival past the 24 h expiry.
- DST / partial-day / incomplete-block fixtures (OPEN): AGREE. B2b function moved to `netlify/live/lib/pattern.mjs`, inlined into the page by build_site.py so the tested code is the shipped code; fixtures for 2025-10-26, 2026-03-29, a partial first day, a 30-min coverage hole, and a covered empty block.
- Late boundary (new issue): AGREE. τ ≥ hour + 15 min is late; tests at 14:59.999 and 15:00.000.

## Disagreements
- None.

## Design decisions taken
- PROVISIONAL: rejection exclusion window "at ≥ τ − 24 h", conservative.

## Escalations
- None.
