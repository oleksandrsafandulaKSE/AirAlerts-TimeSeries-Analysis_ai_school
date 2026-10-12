---
name: codex-plan-review
description: Independent review by Codex (a different model) of a milestone PLAN (plans/M<n>.md, milestone mode) or of the ROADMAP + README (roadmap mode, milestone-protocol step 0). Use before asking the human for approval. One round, no loops.
---

# Codex plan review

Two modes. Each mode has its own command and its own prompt below; everything else (run once,
failure handling, lead judgment, STOP) is the same.

- **Milestone mode:** input = a plan file, e.g. `plans/M1.md`. `<plan-name>` = its basename without `.md`.
- **Roadmap mode:** input = `plans/ROADMAP.md` + `README.md`. Command:

```bash
~/.claude/skills/codex/scripts/ask_codex.sh "$(awk '/^<!-- ROADMAP PROMPT START -->$/{f=1;next} /^<!-- ROADMAP PROMPT END -->$/{f=0} f' .claude/skills/codex-plan-review/SKILL.md)" \
  --read-only --reasoning high -w "$(git rev-parse --show-toplevel)" \
  -f plans/ROADMAP.md -f README.md -f CLAUDE.md -f DECISIONS.md \
  -o reviews/ROADMAP-codex.md
```

## 1. Run Codex once (milestone mode command below)
Call Codex ONLY through this script. Run it ONCE, in the background, from the repo root, and
wait for it to exit:

```bash
~/.claude/skills/codex/scripts/ask_codex.sh "$(awk '/^<!-- CODEX PROMPT START -->$/{f=1;next} /^<!-- CODEX PROMPT END -->$/{f=0} f' .claude/skills/codex-plan-review/SKILL.md)" \
  --read-only --reasoning high -w "$(git rev-parse --show-toplevel)" \
  -f plans/<plan-name>.md -f CLAUDE.md -f DECISIONS.md -f .claude/skills/ts-leakage-audit/SKILL.md \
  -o reviews/<plan-name>-codex.md
```

- If the script exits non-zero, or the output file (`reviews/<plan-name>-codex.md` or
  `reviews/ROADMAP-codex.md`) is missing or empty:
  report the failure and the stderr to the human, then STOP.
- Do NOT review the plan yourself as a substitute. Do NOT re-run or loop.

## 2. Lead judgment
After Codex finishes, show the human Codex's items exactly as written. Then add a section:

```
## Lead judgment
- <item> — AGREE | DISAGREE | PARTLY — <one line of evidence: file:line, D-number, or a command result>
```

Cover every Codex item. Do NOT edit the plan. Then STOP. The human decides what changes.

## Codex prompt, milestone mode (passed verbatim; edit here only)
<!-- CODEX PROMPT START -->
You are an independent, skeptical senior ML reviewer. You are reviewing a PLAN for one
milestone of an air-raid alert onset forecasting project. There is NO code yet; do not look
for it and do not write any. Your job is to find what is wrong with the plan, not to praise it.

Read the priority files: the plan, CLAUDE.md (project rules), DECISIONS.md (decision log,
entries D-000 … D-0xx), and the leakage-audit skill.

Check:
a. Contradictions between the plan and CLAUDE.md / DECISIONS.md (cite D-numbers), and
   contradictions between rules themselves.
b. Definitions vague enough that two developers would code them differently.
c. Leakage the design would allow: (t, t+H] edges, purge at cut-offs, rolling windows,
   finished_at not yet known at t.
d. Planned tests that would still pass if the bug they target existed.
e. Edge cases: DST, recording-gap edges (29 Aug–2 Sep 2026), standing alerts > 24h,
   Kyiv City vs Kyivska.
f. Things CLAUDE.md requires that the plan leaves out (D-017 architecture, data checks that
   raise errors, pinned versions, reports/<run>/ output).
g. Scope and time risk given the deadline tonight at 23:59 Kyiv.

Output format, exactly these four headings:
## BLOCKERS
## AMBIGUITIES
## MISSING
## QUESTIONS FOR THE HUMAN

Each item: cite a plan line (quote a few words) or a D-number, and give a concrete fix.
Under 400 words in total. No code.
<!-- CODEX PROMPT END -->

## Codex prompt, roadmap mode (passed verbatim; edit here only)
<!-- ROADMAP PROMPT START -->
You are an independent, skeptical senior ML reviewer. You are reviewing the ROADMAP (general
milestones M1–M6) and the README draft of an air-raid alert onset forecasting project. There
is NO code yet; do not look for it and do not write any. Your job is to find what is wrong,
not to praise it.

Read the priority files: plans/ROADMAP.md, README.md, CLAUDE.md (project rules), and
DECISIONS.md (decision log, entries D-000 … D-0xx).

Review at ROADMAP level only. Do NOT review implementation details (bin edges, test cases,
interval closure, function names); those belong in the per-milestone plans reviewed later.

Check:
1. Whether the goal, target and evaluation agree across ROADMAP, README, CLAUDE.md and
   DECISIONS.md (cite D-numbers), and whether rules contradict each other.
2. Milestone order and dependencies: wrong order, missing milestone, a deliverable in the wrong milestone.
3. Whether every "done when" can actually be checked (pass/fail), not just stated as a goal.
4. Whether the README claims anything that isn't backed by a decision or by evidence, or
   presents planned work as done.
5. Whether the "decisions needed at roadmap level" are the right ones and complete: what
   is missing, and what must be decided before any milestone plan.
6. Scope and time risk given the deadline tonight at 23:59 Kyiv.

Output format, exactly these four headings:
## BLOCKERS
## AMBIGUITIES
## MISSING
## QUESTIONS FOR THE HUMAN

Each item: cite a ROADMAP/README line (quote a few words) or a D-number, and give a concrete fix.
Under 400 words in total. No code.
<!-- ROADMAP PROMPT END -->
