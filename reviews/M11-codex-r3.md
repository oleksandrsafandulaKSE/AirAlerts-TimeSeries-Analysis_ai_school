### Shell: `'cat plans/M11.md reviews/M11-codex-r2.md reviews/M11-claude-r2.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M11 plan v1 — Live forecast check and analytics UI (unit panel, history strip, test replay, stability charts)

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things, also liked his UI, do same, but not how it looks
  but the analytics and maps, the design is different". "His UI" = air-alert-forecast-ua.netlify.app
  (github.com/yehor-o/time_series_air_alerts, `site/`). We copy the ANALYTICS, not the look: our own design
  tokens, our SVG geoBoundaries map (`
### Shell: `"wc -l reviews/M11-codex-r2.md reviews/M11-claude-r2.md CLAUDE.md DECISIONS.md; cat reviews/M11-claude-r2.md; tail -65 reviews/M11-codex-r2.md; cat CLAUDE.md; rg --files -g AGENTS.md -g '*leakage*'"`
      86 reviews/M11-codex-r2.md
      15 reviews/M11-claude-r2.md
     156 CLAUDE.md
     301 DECISIONS.md
     558 total
# M11 — Claude response, round 2

## Changes made
- Rejections after issue (OPEN): AGREE (verified `live.mjs:16` REJECT_KEEP = 1 day, `applyHistory` calls `markRejected`). New persistent `rejection_log` (35 days); any rejection for the unit logged at ≥ τ − 24 h excludes the row; tests for a post-issue rejection, the boundary, and survival past the 24 h expiry.
- DST / partia
### Shell: `"cat netlify/live/lib/live.mjs netlify/live/lib/runner.mjs netlify/live/lib/features.mjs; sed -n '1,38p' plans/M8.md; cat reviews/M11-claude-r1.md; rg -n 'PROVISIONAL|retention|35|check_epoch|rejectio`
// Live state and forecasts (plans/M8.md §2). Pure functions: no network, no storage, no token.
import { unitIntervals, featuresAt, offsetAt, covered } from "./features.mjs";
import { predictOffset } from "./lgb.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR, CAP = DAY;
export const HISTORY_WINDOW = 30 * DAY;
export const POLL_GAP_MAX = 5 * MIN;          // polls further apart leave a hole (plans/M8.md §2: a failed ACTIVE poll > 5 min)
export const STALE_AFTER = 5 * MIN;
export const 
I’ll check each prior finding and provisional decision against the updated plan and project rules, then report any remaining gaps.
I’m applying the supplied leakage-audit skill. The plan now includes the requested rejection log, DST fixtures, and exact lateness boundary; I’m checking whether the rejection log remains valid throughout the 35-day scoring window.
## PREVIOUS ITEMS

- **RESOLVED — Coverage holes:** A2 requires continuous coverage over [τ − 24 h, τ + 1 h].
- **RESOLVED — Rejected records/reconciliation:** Persistent rejection logging excludes later-contaminated rows; A4 tests discovery after issuance and survival beyond marker expiry.
- **RESOLVED — History length:** A3 supplies 14 days for the pattern display.
- **RESOLVED — Snapshot semantics:** First-write selection, races, migration and lateness are explicit.
- **RESOLVED — Undefined BSS/bins:** Null reasons and probability endpoints are specified.
- **RESOLVED — Physical/capped alerts:** Both representations and neighbour semantics remain explicit.
- **RESOLVED — Replay precision:** Validation uses the full-precision published metric.
- **RESOLVED — Scorer isolation:** Stored predictions remain unchanged under reconciliation; a leaky negative control is required.
- **RESOLVED — Replay validation:** Prefix, alignment, filtering and gap assertions remain specified.
- **RESOLVED — DST fixtures/Kyiv separation:** A4 now covers repeated/skipped hours, partial days, incomplete coverage and distinct Kyiv units.
- **RESOLVED — Completion protocol:** Reviews, fixes, human summary and proposed decision entries remain required.
- **RESOLVED — Estimand question:** A2 explicitly selects intersected issued/reconciled eligibility.
- **RESOLVED — Late boundary:** Exactly +15 minutes is excluded; both adjacent boundary cases are tested.

## PROVISIONAL DECISIONS

All remain within the authorized exploratory live scope:

- Intersection eligibility preserves D-003’s exclusion of active rows.
- Three-hour settlement and the rejection exclusion window are conservative label-quality filters.
- The 15-minute cutoff and snapshot selection policy define archive sampling.
- Thirty-five-day retention changes storage duration.

None changes the official target, baseline, source separation, splits or frozen evaluation protocol. No disguised rule change identified. Under D-026, these remain provisional until human ratification; consensus must not edit CLAUDE.md or DECISIONS.md.

## NEW ISSUES

None introduced by these revisions. This agreement concerns the plan; implementation must satisfy its specified tests.

VERDICT: AGREE
