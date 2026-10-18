### Shell: `'cat plans/M6-site.md reviews/M6-site-codex-r2.md reviews/M6-site-claude-r2.md plans/M6-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6-site plan v3 — yellow/red forecasts on oblast hover (M8 live site), baseline only until a model exists

Status: DRAFT for Claude–Codex consensus (D-026). Human decisions this plan rests on: plans/M6-definition.md (chat,
2026-10-17; proposed D-033–D-037, esp. D-036 "yellow/red only on oblast hover, labelled 'in training', with collection
status and the monthly chart"). M8 rules unchanged (plans/M8.md, proposed D-032). No new dependency, no API request,
no token use, no deploy. Not touched: `
### Shell: `'wc -l reviews/M6-site-codex-r2.md reviews/M6-site-claude-r2.md plans/M6-definition.md CLAUDE.md DECISIONS.md; tail -70 reviews/M6-site-codex-r2.md; cat reviews/M6-site-claude-r2.md plans/M6-definitio`
      64 reviews/M6-site-codex-r2.md
      21 reviews/M6-site-claude-r2.md
      57 plans/M6-definition.md
     156 CLAUDE.md
     301 DECISIONS.md
     599 total
### Shell: `'cat plans/M6-site.md reviews/M6-site-codex-r1.md reviews/M6-site-claude-r1.md plans/M6-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6-site plan v2 — yellow/red forecasts on oblast hover (M8 live site), baseline only until a model exists

Status: DRAFT for Claude–Codex consensus (D-026)
### Shell: `"rg --files -g AGENTS.md -g '*PROPOSED*' -g 'M8.md'; cat netlify/live/lib/live.mjs netlify/live/lib/features.mjs"`
plans/M8.md
reviews/PROPOSED-DECISIONS-M6.md
reviews/PROPOSED-DECISIONS-M4-M5.md
// Live state and forecasts (plans/M8.md §2). Pure functions: no network, no storage, no token.
import { unitIntervals, featuresAt, offsetAt, covered } from "./features.mjs";
import { predictOffset } from "./lgb.mjs";
import { typedAt } from "./typed.mjs";

const MIN = 60e3, HOUR = 60 * MIN, DAY = 24 * HOUR, CAP = DAY;
export const HISTORY_WINDOW = 30 * DAY;
export const POLL_GAP_MAX = 5 * MIN;          // polls fur
### Shell: `'cat reviews/M6-site-claude-r1.md reviews/PROPOSED-DECISIONS-M6.md; cat plans/M8.md; rg --files -g AGENTS.md; git status --short'`
# M6-site — Claude, round 1 (answer to reviews/M6-site-codex-r1.md)

## Changes made
- B1 versioned levels — AGREE (live.mjs applies only `updated_at`-gated overwrites; no timestamp → replay leak). Plan §2:
  `levels = [[knownAt, level]]`, `levelAt(r, τ)`; the typed path selects its own records (first seen ≤ τ, end known at τ,
  `levelAt`, `alert_type`); `knownAt()` unchanged so "any" is untouched.
- B2 hover vs card — AGREE (template.html:356 `hover(p, o.tip(u))` = tooltip; :357 click/Enter → `
### Shell: `"cat DECISIONS.md; sed -n '110,170p' CLAUDE.md; nl -ba plans/M6-site.md | sed -n '68,130p'; nl -ba plans/M6-site.md | tail -24"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
I’ll check each previous finding against the updated plan and builder’s response, then assess the provisional decisions and any new issues against the project rules.
I’m applying the repository’s `ts-leakage-audit` skill to the causal checks. The plan now addresses the two previously open findings; I’m checking the revised target metadata and model contract for contradictions.
## PREVIOUS ITEMS

- **B1 RESOLVED** — Versioned levels preserve information known at τ.
- **B2 RESOLVED** — Tooltip and card both receive typed content and verification.
- **B3 ACCEPTED** — Recorded human instructions authorize the branch commit.
- **A1 RESOLVED** — Collection counts distinguish confirmed typed coverage from training history.
- **A2 RESOLVED** — Unknown levels cause bounded exclusions and explicit current-state gaps.
- **M1 RESOLVED** — Production truncation witnesses include sensitivity controls.
- **M2 ACCEPTED** — Boundary fixtures and synthetic holes cover this baseline’s relevant risks.
- **M3 RESOLVED** — Pre-change golden outputs protect existing forecasts across migration and failures.
- **M4 RESOLVED** — Availability timestamps, causal version selection and late-availability tests address the remaining concern.
- **Q1 OPEN** — §3 adopts all approved API types, but the [payload contract](plans/M6-site.md:75) still declares only `air_raid`, and [§7](plans/M6-site.md:160) still requires the model to match air-raid-only targets. These contradict the revised target and permit incompatible implementation. Derive payload metadata from `TYPED_ALERT_TYPES`, correct §7, and assert metadata/model/baseline target-set equality.
- **Q2 ACCEPTED** — Recorded human initiation authorizes baseline-only site work now.

## PROVISIONAL DECISIONS

- **P1:** Inheriting M8’s approved types stays within rules; the surviving air-raid-only requirement would change the target and needs human approval.
- **P2:** Versioned levels and explicit unknowns implement causal-information rules.
- **P3:** Separate typed coverage is an allowed migration design.
- **P4:** Bounded uncertainty holes follow existing missing-data treatment.
- **P5:** Clearly labelled live-history accounting stays within scope.
- **P6:** Tooltip/card placement implements the human-approved hover requirement.
- **P7:** An empty monthly-data contract stays within the authorized milestone.
- **P8:** Causal model-version selection implements leakage prevention without changing evaluation rules.

## NEW ISSUES

None independently identified beyond the contradictory target declarations tracked under Q1.

VERDICT: CHANGES REQUIRED
