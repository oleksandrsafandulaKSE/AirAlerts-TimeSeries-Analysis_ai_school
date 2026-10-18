### Shell: `'cat plans/M6-site.md reviews/M6-site-codex-r1.md reviews/M6-site-claude-r1.md plans/M6-definition.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6-site plan v2 — yellow/red forecasts on oblast hover (M8 live site), baseline only until a model exists

Status: DRAFT for Claude–Codex consensus (D-026). Human decisions this plan rests on: plans/M6-definition.md (chat,
2026-10-17; proposed D-033–D-037, esp. D-036 "yellow/red only on oblast hover, labelled 'in training', with collection
status and the monthly chart"). M8 rules unchanged (plans/M8.md, proposed D-032). No new dependency, no API request,
no token use, no deploy. Not touched: `
### Shell: `'wc -l reviews/M6-site-codex-r1.md reviews/M6-site-claude-r1.md CLAUDE.md DECISIONS.md plans/M6-definition.md; tail -100 reviews/M6-site-codex-r1.md; cat reviews/M6-site-claude-r1.md plans/M6-definiti`
     173 reviews/M6-site-codex-r1.md
      49 reviews/M6-site-claude-r1.md
     156 CLAUDE.md
     301 DECISIONS.md
      57 plans/M6-definition.md
     736 total

async function getJSON(fetchFn, url, token, timeoutMs) {
  const r = await fetchFn(url, { headers: { Authorization: `Bearer ${token}` }, sign
### Shell: `"rg --files -g 'AGENTS.md' -g '*live*' tests improve; rg -n 'liveCard|liveTip|typed|function drawLive|historyStart' site_src/template.html netlify/live/test tests/test_live* improve/
### Shell: `"cat .claude/skills/ts-leakage-audit/SKILL.md; cat netlify/live/lib/live.mjs netlify/live/lib/features.mjs scripts/build_live_seed.py; cat reviews/PROPOSED-DECISIONS-M6.md; rg -n 'all types|all API|al`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
I’ll check each previous finding against the updated plan and builder response, then check the provisional decisions against the project rules.
The plan addresses the level-versioning and hover gaps. I’m checking two remaining concerns: whether restricting typed targets to `air_raid` has human approval, and whether the model contract checks when a model became available as well as its training cutoff.
I’m applying the repository’s `ts-leakage-audit` skill. The proposed truncation tests cover late ends, level backfills and coverage confirmations, but the model contract still lacks an availability timestamp. The builder also presents `air_raid` filtering as provisional without resolving the earlier request for approval of that target restriction.
## PREVIOUS ITEMS

- **B1 RESOLVED** — Timestamped level versions and a separate typed selector preserve information known at τ.
- **B2 RESOLVED** — Tooltip and card both receive typed content, with wiring and browser checks.
- **B3 ACCEPTED** — The builder records an explicit human instruction authorizing a branch commit.
- **A1 RESOLVED** — Collection status uses typed coverage, subtracts unresolved zones and distinguishes live from training history.
- **A2 RESOLVED** — Unresolved levels create bounded exclusions from k/n/q and a defined current-state gap.
- **M1 RESOLVED** — Production truncation witnesses cover late-known ends, levels and coverage, with sensitivity controls.
- **M2 ACCEPTED** — Added typed boundary fixtures and synthetic hole tests address relevant risks; this baseline has no calendar input.
- **M3 RESOLVED** — Frozen pre-change outputs cover migration, rejected records and holes.
- **M4 OPEN** — §5 checks `trained_through + 1 h ≤ τ`, but still lacks model availability/version-selection timestamps. A model built or selected after τ can satisfy that check. Require `available_at ≤ τ`, causal version selection and a late-availability rejection test. The out-of-sample blend requirement addresses the other concern.
- **Q1 OPEN** — “Facts … air_raid” documents a calculation subset, not approval to redefine the target. M6-definition defines type by `alert_level`; M8 explicitly includes all API types. Artillery carrying levels makes the distinction consequential. Obtain explicit human approval for this restriction or inherit the approved set.
- **Q2 ACCEPTED** — The builder records explicit human initiation of baseline-only site work.

## PROVISIONAL DECISIONS

- **P1:** Target restriction requiring human approval; cannot be settled as provisional under D-026.
- **P2:** Versioned levels and visible unknowns fit the causal-information rules.
- **P3:** Separate typed coverage is a migration design within existing rules.
- **P4:** Bounded uncertainty holes implement the approved missing-data treatment.
- **P5:** Explicitly labelled live-history accounting is within scope.
- **P6:** Tooltip/card placement implements the human-approved hover requirement.
- **P7:** Empty monthly-data contract is within scope.
- **P8:** Within scope, but incomplete as detailed in M4.

## NEW ISSUES

None independently identified.

VERDICT: CHANGES REQUIRED
