### Shell: `"pwd; rg --files -g 'AGENTS.md' -g 'SKILL.md' -g 'M13*' -g 'CLAUDE.md' -g 'DECISIONS.md' -g 'site-redesign-definition.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
DECISIONS.md
plans/M13.md
plans/site-redesign-definition.md
CLAUDE.md
reviews/M13-codex-r1.md
reviews/M13-claude-r2.md
reviews/M13-codex-r3.log
reviews/M13-claude-r1.md
reviews/M13-codex-r1.log
reviews/M13-codex-r2.log
reviews/M13-codex-r2.md

### Shell: `'cat plans/M13.md reviews/M13-codex-r2.md reviews/M13-claude-r2.md plans/site-redesign-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M13 plan v1 — The redesigned site: one interactive map, the rest in tabs

## Status and authority
- Design: `plans/site-redesign-definition.md` (grilling with the human 2026-10-18 + Claude–Codex consensus round 3;
  D-041 … D-045 proposed, D-045 approved). Human, chat 2026-10-18: "do m13" (after: "so there is no new site yet?").
- Builds on M12 session 1 (`fb251fb`, branch `claude/m12-session1`; this work: branch `claude/m13-site`).
- **The M12 registry is INACTIVE until the switch** (after th
### Shell: `'wc -l reviews/M13-codex-r2.md reviews/M13-claude-r2.md plans/site-redesign-definition.md CLAUDE.md DECISIONS.md; tail -n 55 reviews/M13-codex-r2.md; cat reviews/M13-claude-r2.md; cat CLAUDE.md'`
     125 reviews/M13-codex-r2.md
      15 reviews/M13-claude-r2.md
     124 plans/site-redesign-definition.md
     156 CLAUDE.md
     301 DECISIONS.md
     721 total
  which M6 already uses. Renumber when ratifying; this definition uses D-041 … D-045.
- D-027 latest-version merge vs strict knowledge-at-t: kept as in M6c-1/M6-site (latest version, documented as a
  retrospective limitation); not changed here.

## Open questions for the loop
### Shell: `'nl -ba plans/M13.md'`
     1	# M13 plan v1 
### Shell: `"cat plans/site-redesign-definition.md reviews/M13-claude-r1.md plans/M12.md; rg -n 'D-0(28|29|3[0-9]|4[0-9])|PROVISIONAL|N = 0|m12_state|item_errors' DECISIONS.md plans/M13.md reviews/PROPOSED-DECISI`
# Site redesign — definition (grilling session with the human, 2026-10-18)

Status: agreed with the human in chat ("all agreed", "agreed, also go for round with codex"). Lines marked **[rule]**
change an existing D-entry (proposed or ratified); they are the human's decisions and are proposed in
`reviews/PROPOSED-DECISIONS-site.md`. Lines marked PROVISIONAL are design defaults for the milestone plans (D-026).
Work starts from `main` after the merge of M6a, M6c-1, M6-site and M10/M11 (done: 8f91ab
### Shell: `"sed -n '1,130p' DECISIONS.md; sed -n '68,103p' netlify/live/lib/runner.mjs; sed -n '95,165p' netlify/live/lib/models.mjs; nl -ba plans/M13.md | sed -n '24,46p;91,104p;128,139p'"`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
I’ll compare each previous finding with the updated plan and builder’s response, then check the provisional decisions against the project rules.
The history cutover now has one consistent rule, and the plan separates fatal registry failures from item failures. The unknown-colour fix is incomplete: the tooltip uses observed count M, but §3 still says “no alerts” when classified count N is zero.
## PREVIOUS ITEMS

- **B1 — RESOLVED:** Activation metadata remains available independently of prediction success; active failure cannot silently select M8.
- **B2 — RESOLVED:** §§1 and 6 consistently require mixed, model-labelled M12/M8 history segments.
- **B3 — RESOLVED:** Reconstruction parity and independent live knowledge-at-τ tests remain separate.
- **A1 — RESOLVED:** Replay defines identical-support BSS prefixes, undefined denominators and retrospective labelling.
- **A2 — RESOLVED:** National pooling requires full coverage, excludes unresolved levels and handles an empty pool explicitly.
- **A3 — RESOLVED:** Thresholds, ties and ten fixed-width reliability bins remain specified.
- **A4 — RESOLVED:** The inactive model’s official training provenance, live inputs and all-types target remain explicit.
- **M1 — RESOLVED:** Truncation, negative controls, endpoints, standing cap, DST and unit-separation tests remain required.
- **M2 — RESOLVED:** Reviewer, independent harness review, fixes and human summary remain required.
- **Q — ACCEPTED:** Latest-version merging follows CLAUDE.md/D-027; replay is labelled retrospective reconstruction, while live computation requires knowledge-at-τ.
- **Failure isolation — RESOLVED:** §1 distinguishes fatal registry failures from item failures and requires a failed-red/successful-any test.
- **False absence — OPEN:** [M13.md:97](/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/plans/M13.md:97) still specifies `N = 0 → "no alerts in 7 days"`, contradicting its new M-based condition and §1. With M=3, U=3, N=0, this branch falsely reports no alerts. Remove that instruction; require unknown-kind wording and a rendered-output assertion for this case.

## PROVISIONAL DECISIONS

- **Kind thresholds:** Presentation choice within existing rules.
- **History segmentation:** Within existing rules; explicit provenance and matching observations preserve model separation.
- **Unclassified-onset wording:** Within existing rules; distinguishes missing colour information from observed absence. Its specification remains inconsistent as identified above.
- None constitutes a rule change under CLAUDE.md or D-026.

## NEW ISSUES

None identified beyond the unresolved previous false-absence finding.

VERDICT: CHANGES REQUIRED
