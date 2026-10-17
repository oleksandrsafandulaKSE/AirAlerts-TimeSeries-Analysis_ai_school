### Shell: `'cat plans/M6a.md reviews/M6a-codex-r3.md reviews/M6a-claude-r3.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
Stop losing new-regime history. a
### Shell: `'wc -l plans/M6a.md reviews/M6a-codex-r3.md reviews/M6a-claude-r3.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md; rg --files -g AGENTS.md; cat reviews/M6a-claude-r3.md; tail -100 r`
     206 plans/M6a.md
     102 reviews/M6a-codex-r3.md
      21 reviews/M6a-claude-r3.md
     156 CLAUDE.md
     301 DECISIONS.md
      30 .claude/skills/ts-leakage-audit/SKILL.md
     816 total
# M6a — Claude, round 3 response

Judgement on reviews/M6a-codex-r3.md:
- New: impossible timing test + arithmetic: AGREE. 24 timeouts cannot fit a 6-retry budget, and
  24 × 65 + 24 × 30 + 6 × 150 s = 53 min, not 51.

## Changes made
- §3: the worst SUCCESSFUL run is defined: 24 successful requests at t
### Shell: `"cat reviews/M6a-claude-r2.md reviews/M6a-claude-r1.md; sed -n '1,110p' DECISIONS.md"`
# M6a — Claude, round 2 response

Judgements on reviews/M6a-codex-r2.md:
- B1 hole acceptance = rule exception: AGREE. CLAUDE.md Architecture #6 has no exception, and D-026 forbids
  consensus rule changes.
- M2 retries cannot enforce the cap: AGREE. Rate isolation is now a deployment prerequisite.
- New: retry budget vs timeout: AGREE.

## Changes made
- §4.4: `accept_hole` removed (input, columns, test). A detected hole fails every run with nothing committed, and
  collection stops until the h
### Shell: `"sed -n '120,245p' src/data.py; cat .claude/skills/ts-leakage-audit/SKILL.md; rg -n '"'^## |'"\\*\\*|OPEN|RESOLVED|ACCEPTED|PROVISIONAL' reviews/M6a-codex-r2.md"`
                    for r in csv.DictReader(fh, delimiter="\t")]
    uids = {m["uid"] for m in manifest}
    if uids != set(range(3, 32)):
        raise DataQualityError(f"manifest UIDs {sorted(uids)} != 3..31")
    not_found = {m["uid"] for m in manifest if m["http"] == 404}
    if not_found != regions.API_404_UIDS or any(m["http"] not in (200, 404) for m in manifest):
        raise DataQualityError(f"unexpected HTTP statuses: 404 for {sorted(not_found)}")
    records = []
    for m in manifest
I’ll read the updated plan, prior review, and builder’s response, then check each provisional decision against the project rules.
## PREVIOUS ITEMS

- **B1 RESOLVED:** §4.4 stops collection on detected holes; recovery exceptions remain outside implementation.
- **B2 RESOLVED:** Knowledge-time filtering precedes version selection, with a delayed-correction negative control.
- **B3 RESOLVED:** Unreconstructable disappearance counts are removed; undetected deletions remain explicit.
- **A1 RESOLVED:** Coverage remains nominal and conditional on the assumed API contract.
- **A2 RESOLVED:** Null decoding and parsed timestamp validation remain specified.
- **M1 RESOLVED:** Write ordering, incomplete-run detection, repair instructions, and interruption testing remain specified.
- **M2 RESOLVED:** Separate collector credentials and runner IP are deployment prerequisites; local fetching requires isolation or paused M8 scheduling.
- **M3 ACCEPTED:** Compatibility witnesses, unchanged source, and the full regression suite adequately cover this milestone.
- **M4 RESOLVED:** Reviewer, harness, fixes, and milestone summary remain required.
- **Q ACCEPTED:** D-027 and CLAUDE.md’s explicit M4/M6 rule authorize retaining open alerts.
- **Retry/timeout finding RESOLVED:** Bounded retries and the 75-minute workflow allocation remain consistent.
- **Impossible timing test/arithmetic RESOLVED:** §6.6 separates budget exhaustion from six failures plus 24 successful responses; §3 correctly totals its stated timing allowance as 53 minutes.

## PROVISIONAL DECISIONS

All current provisional decisions remain within CLAUDE.md and DECISIONS.md: strict hole handling; retry budgets and timeouts; 65-second request spacing with deployment isolation; seed ingestion; retaining unknown alert types; 24 forecast UIDs; version keys with the D-027 latest-version view; `fetched_at` knowledge time and its selector; undetected deletions; and the raising window check.

The selector’s delayed-correction negative control supports the leakage-audit skill’s known-at-t requirement. The window check still establishes no completeness guarantee.

A second token requires human provisioning, without changing rules. Hole recovery **would change** Architecture #6/D-017; §9 correctly reserves that decision for the human and excludes it from this build. The superseded provisional `accept_hole` mechanism is removed.

## NEW ISSUES

None introduced by these changes.

VERDICT: AGREE
