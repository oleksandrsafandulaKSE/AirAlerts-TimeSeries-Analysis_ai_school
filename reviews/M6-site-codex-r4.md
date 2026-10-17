### Shell: `'cat plans/M6-site.md reviews/M6-site-codex-r3.md reviews/M6-site-claude-r3.md plans/M6-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6-site plan v4 — yellow/red forecasts on oblast hover (M8 live site), baseline only until a model exists

Status: DRAFT for Claude–Codex consensus (D-026). Human decisions this plan rests on: plans/M6-definition.md (chat,
2026-10-17; proposed D-033–D-037, esp. D-036 "yellow/red only on oblast hover, labelled 'in training', with collection
status and the monthly chart"). M8 rules unchanged (plans/M8.md, proposed D-032). No new dependency, no API request,
no token use, no deploy. Not touched: `
### Shell: `"cat reviews/M6-site-claude-r3.md plans/M6-definition.md CLAUDE.md; tail -35 reviews/M6-site-codex-r3.md; rg --files -g AGENTS.md -g '*consensus*' -g '*PROPOSED*'; wc -l reviews/M6-site-codex-r3.md"`
# M6-site — Claude, round 3 (answer to reviews/M6-site-codex-r3.md)

## Changes made
- Q1 — AGREE: the two leftover air_raid-only statements are fixed. Payload `alert_types` = `TYPED_ALERT_TYPES`
  (= live.mjs `ALERT_TYPES`); §7 now says the model must declare M8's approved set; tests assert payload == typed ==
  live list and reject a model with another set.

## Disagreements
(none)

## Design decisions taken (PROVISIONAL)
P1–P8 as in round 2.

## Escalations
(none)
# M6 — definition (grilling 
### Shell: `'cat reviews/M6-site-claude-r2.md reviews/M6-site-claude-r1.md reviews/PROPOSED-DECISIONS-M6.md plans/M8.md; cat netlify/live/lib/features.mjs netlify/live/lib/typed.mjs'`
# M6-site — Claude, round 2 (answer to reviews/M6-site-codex-r2.md)

## Changes made
- M4 — AGREE: contract gains `available_at`; `typedModel` is a list of versions, the one with the latest
  `available_at ≤ τ` is used, later ones are skipped at τ (none → baseline only); a version with
  trained_through + 1 h > available_at is malformed and throws. Tests: a late version is skipped at τ and used after it;
  a single late model alone → baseline only.
- Q1/P1 — AGREE: typed targets now inherit M8's
I’ll check each prior finding against the updated plan, then review the provisional decisions and any new issues against the project rules.
The plan now consistently uses M8’s alert-type list in the baseline, payload and model checks, resolving Q1. I’m checking P1–P8 and the coverage and model contracts for any remaining rule changes or leakage risks.
## PREVIOUS ITEMS

- **B1 RESOLVED** — Versioned levels preserve information known at τ.
- **B2 RESOLVED** — Both tooltip and card receive typed content and verification.
- **B3 ACCEPTED** — Recorded human instructions authorize the branch commit.
- **A1 RESOLVED** — Collection counts distinguish confirmed typed coverage from training history.
- **A2 RESOLVED** — Unknown levels receive bounded exclusions and explicit current-state gaps.
- **M1 RESOLVED** — Production truncation witnesses include sensitivity controls.
- **M2 ACCEPTED** — Boundary fixtures and synthetic holes cover this baseline’s relevant risks.
- **M3 RESOLVED** — Pre-change golden outputs protect existing forecasts across migration and failures.
- **M4 RESOLVED** — Availability timestamps and causal version selection address replay leakage.
- **Q1 RESOLVED** — §§3–7 consistently use M8’s approved alert-type list; tests require payload/model/baseline agreement.
- **Q2 ACCEPTED** — Recorded human initiation authorizes baseline-only site work now.

## PROVISIONAL DECISIONS

- **P1:** Inheriting M8’s human-approved alert types stays within rules. Air-raid-only remains a human question, without changing the target.
- **P2:** Versioned levels and explicit unknowns implement causal-information rules.
- **P3:** Separate typed coverage is a migration design within scope.
- **P4:** Bounded uncertainty holes follow existing missing-data treatment.
- **P5:** Clearly labelled live-history accounting implements the authorized collection-status requirement.
- **P6:** Tooltip/card placement implements the human-approved hover requirement.
- **P7:** An empty monthly-data contract stays within the authorized milestone.
- **P8:** Causal model-version selection implements leakage prevention; model-side truncation and out-of-sample weight enforcement remain explicitly assigned to later milestones.

None introduces an additional change to CLAUDE.md or existing DECISIONS.md rules. Typed-target and site-scope exceptions derive from recorded human decisions in M6-definition, rather than consensus authority.

## NEW ISSUES

None identified in this revision.

VERDICT: AGREE
