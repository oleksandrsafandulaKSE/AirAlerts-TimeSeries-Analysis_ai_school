---
name: codex-plan-review
description: Claude and Codex (a different model) iterate on a milestone PLAN (plans/<name>.md, milestone mode) or on the ROADMAP + README (roadmap mode) until they agree, without the human in the loop. Use whenever a plan is written or changed, before implementation. Max 5 rounds; escalates to the human only for rule changes or deadlock.
---

# Codex plan review — consensus loop (human not in the loop)

Claude (the builder) and Codex (the reviewer) iterate on the plan until both agree it is ready.
The human is NOT asked during the loop. The human reads the final consensus record afterwards.

Two modes, same loop:
- **Milestone mode:** input = a plan file, e.g. `plans/M3b-H3.md`. `<plan-name>` = basename without `.md`.
- **Roadmap mode:** input = `plans/ROADMAP.md` + `README.md`. `<plan-name>` = `ROADMAP`.

## What the loop may and may not decide

The loop decides open DESIGN questions inside the existing rules: thresholds, test cases, names,
file layout, edge-case definitions, which option among those the rules allow.

The loop may NOT change a rule. A rule = anything in `CLAUDE.md` or an existing `DECISIONS.md` entry
(target definition, mask, splits, evaluation protocol, baselines, data sources, dependencies, scope,
milestone order). If the plan needs a rule change that the human has not already approved in chat,
the loop ESCALATES (see "Stop conditions"). Hard limits, never decided by consensus: scoring the final
test before M4, training/tuning on API data, mixing sources in one training set or metric, committing,
deleting data, touching secrets.

Every design decision taken by consensus is written to the consensus record as
`PROVISIONAL (Claude+Codex consensus, human to ratify)` and later proposed as a DECISIONS.md entry.

## The loop

Run from the repo root. Each Codex call runs ONCE per round, in the background, stderr kept in a log.
Never redirect Codex output to /dev/null.

### Round 1 — Codex reviews the plan
```bash
~/.claude/skills/codex/scripts/ask_codex.sh "$(awk '/^<!-- CODEX PROMPT START -->$/{f=1;next} /^<!-- CODEX PROMPT END -->$/{f=0} f' .claude/skills/codex-plan-review/SKILL.md)" \
  --read-only --reasoning high -w "$(git rev-parse --show-toplevel)" \
  -f plans/<plan-name>.md -f CLAUDE.md -f DECISIONS.md -f .claude/skills/ts-leakage-audit/SKILL.md \
  -o reviews/<plan-name>-codex-r1.md > reviews/<plan-name>-codex-r1.log 2>&1
```
(Roadmap mode: use the ROADMAP prompt below and `-f plans/ROADMAP.md -f README.md -f CLAUDE.md -f DECISIONS.md`.)

### Claude's turn (every round k)
1. Judge every Codex item: `AGREE | DISAGREE | PARTLY` with one line of evidence (file:line, D-number,
   a command result). Verify claims by reading code/data where possible; do not judge from memory.
2. Edit the plan: apply every AGREE item and the agreed part of every PARTLY item. Do not edit the
   plan for DISAGREE items.
3. Write `reviews/<plan-name>-claude-r<k>.md` with exactly these sections:
   - `## Changes made` — what changed in the plan, per item.
   - `## Disagreements` — each DISAGREE/PARTLY item: the claim, the evidence, why the plan stays.
   - `## Design decisions taken` — open questions Claude resolved (each marked PROVISIONAL).
   - `## Escalations` — rule changes the plan would need (empty if none).

### Round k ≥ 2 — Codex re-reviews
```bash
~/.claude/skills/codex/scripts/ask_codex.sh "$(awk '/^<!-- CODEX FOLLOWUP START -->$/{f=1;next} /^<!-- CODEX FOLLOWUP END -->$/{f=0} f' .claude/skills/codex-plan-review/SKILL.md)" \
  --read-only --reasoning high -w "$(git rev-parse --show-toplevel)" \
  -f plans/<plan-name>.md -f reviews/<plan-name>-codex-r<k-1>.md -f reviews/<plan-name>-claude-r<k-1>.md \
  -f CLAUDE.md -f DECISIONS.md -f .claude/skills/ts-leakage-audit/SKILL.md \
  -o reviews/<plan-name>-codex-r<k>.md > reviews/<plan-name>-codex-r<k>.log 2>&1
```
Then Claude's turn again.

## Stop conditions
- **Consensus:** Codex's last line is `VERDICT: AGREE` AND Claude has no open DISAGREE item AND
  `## Escalations` is empty → write the consensus record, then continue the milestone protocol.
- **Escalation:** the plan needs a rule change not yet approved by the human → stop the loop, write the
  consensus record with the escalation at the top, STOP and wait for the human.
- **Deadlock:** 5 rounds without consensus → stop, write the consensus record listing the unresolved
  items with both sides' evidence, STOP and wait for the human.
- **Failure:** the script exits non-zero or the output file is missing/empty → report the log to the
  human and STOP. Do not substitute your own review for Codex's.

## Consensus record
Write `reviews/<plan-name>-consensus.md`:
- outcome (consensus / escalation / deadlock) and number of rounds;
- Codex's final verdict, verbatim;
- every PROVISIONAL design decision (to be proposed as DECISIONS.md entries);
- unresolved items and escalations, if any.
Show the human a short summary of this record with the milestone summary. Never edit DECISIONS.md or
CLAUDE.md from inside the loop.

## Codex prompt, milestone mode, round 1 (passed verbatim; edit here only)
<!-- CODEX PROMPT START -->
You are an independent, skeptical senior ML reviewer. You are reviewing a PLAN for one
milestone of an air-raid alert onset forecasting project. Judge the plan; do not write code.
Your job is to find what is wrong with the plan, not to praise it.

Read the priority files: the plan, CLAUDE.md (project rules), DECISIONS.md (decision log,
entries D-000 … D-0xx), and the leakage-audit skill. You may read existing code in src/, tests/
and scripts/ to check the plan's claims about it.

Check:
a. Contradictions between the plan and CLAUDE.md / DECISIONS.md (cite D-numbers), and
   contradictions between rules themselves.
b. Definitions vague enough that two developers would code them differently.
c. Leakage the design would allow: (t, t+H] edges, purge at cut-offs, rolling windows,
   finished_at not yet known at t.
d. Planned tests that would still pass if the bug they target existed.
e. Edge cases: DST, recording-gap edges (29 Aug–2 Sep 2026), standing alerts > 24h,
   Kyiv City vs Kyivska.
f. Things CLAUDE.md requires that the plan leaves out.

Output format, exactly these four headings:
## BLOCKERS
## AMBIGUITIES
## MISSING
## QUESTIONS FOR THE HUMAN

Each item: cite a plan line (quote a few words) or a D-number, and give a concrete fix.
Under 400 words in total. No code.
End with ONE final line, exactly `VERDICT: AGREE` (no blockers left; the plan can be implemented)
or `VERDICT: CHANGES REQUIRED`.
<!-- CODEX PROMPT END -->

## Codex prompt, follow-up rounds (passed verbatim; edit here only)
<!-- CODEX FOLLOWUP START -->
You are the same independent, skeptical senior ML reviewer, in a follow-up round. You previously
reviewed this plan; the builder (Claude) has answered. Files: the UPDATED plan, your previous review,
the builder's response (changes made, disagreements with evidence, provisional design decisions,
escalations), CLAUDE.md, DECISIONS.md and the leakage-audit skill. You may read src/, tests/, scripts/.

For each item of your previous review, decide: RESOLVED (the plan now handles it), ACCEPTED (you accept
the builder's disagreement and evidence), or OPEN (still wrong: say exactly why, with evidence).
Check every PROVISIONAL design decision: it must stay inside CLAUDE.md and DECISIONS.md; flag any that
is really a rule change. Then list any NEW problems introduced by the changes.

Output format, exactly these headings:
## PREVIOUS ITEMS
## PROVISIONAL DECISIONS
## NEW ISSUES

Under 350 words. No code. Do not repeat items you mark RESOLVED or ACCEPTED beyond one line.
End with ONE final line, exactly `VERDICT: AGREE` (nothing OPEN and no new blocker) or
`VERDICT: CHANGES REQUIRED`.
<!-- CODEX FOLLOWUP END -->

## Codex prompt, roadmap mode, round 1 (passed verbatim; edit here only)
<!-- ROADMAP PROMPT START -->
You are an independent, skeptical senior ML reviewer. You are reviewing the ROADMAP (general
milestones M1–M6) and the README draft of an air-raid alert onset forecasting project. Your job
is to find what is wrong, not to praise it.

Read the priority files: plans/ROADMAP.md, README.md, CLAUDE.md (project rules), and
DECISIONS.md (decision log, entries D-000 … D-0xx).

Review at ROADMAP level only. Do NOT review implementation details (bin edges, test cases,
interval closure, function names); those belong in the per-milestone plans.

Check:
1. Whether the goal, target and evaluation agree across ROADMAP, README, CLAUDE.md and
   DECISIONS.md (cite D-numbers), and whether rules contradict each other.
2. Milestone order and dependencies: wrong order, missing milestone, a deliverable in the wrong milestone.
3. Whether every "done when" can actually be checked (pass/fail), not just stated as a goal.
4. Whether the README claims anything that isn't backed by a decision or by evidence, or
   presents planned work as done.
5. Whether the roadmap-level decisions are the right ones and complete.

Output format, exactly these four headings:
## BLOCKERS
## AMBIGUITIES
## MISSING
## QUESTIONS FOR THE HUMAN

Each item: cite a ROADMAP/README line (quote a few words) or a D-number, and give a concrete fix.
Under 400 words in total. No code.
End with ONE final line, exactly `VERDICT: AGREE` or `VERDICT: CHANGES REQUIRED`.
<!-- ROADMAP PROMPT END -->
