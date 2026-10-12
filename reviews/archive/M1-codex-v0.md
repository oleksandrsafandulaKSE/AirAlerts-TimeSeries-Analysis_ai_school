### Shell: `'cat plans/M1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M1 plan (as proposed in chat, unedited)

Two parts, both as originally proposed: the first M1 plan, then the update that added the
D-017 architecture changes. Nothing has been fixed or reworded.

---

## Part 1 — original M1 plan

**Goal:** turn the raw official data into a clean hourly grid of the 24 units, with the target and the "already under alert" mask. No features yet.

**Files**
- `.venv/` for the environment.
- `src/data.py` with `load_official()`. It downloads to `data/` (gitignored)
I’ll read the four priority files and review the plan for contradictions, leakage risks, weak tests, and deadline scope. I won’t inspect or write code.
I’m applying the leakage-audit skill. The main conflict is that dropping alerts by their eventual duration uses information unavailable at forecast time. The gap and duplicate checks also need explicit acceptance criteria: raising on any occurrence would reject the known official dataset.
## BLOCKERS

- **D-009 / “drop alerts longer than 24h”:** eventual duration requires `finished_at` unavailable at t. This contradicts the leakage rule and can change historical masks and features. Resolve the policy before implementation; require truncation invariance for preprocessing and state.
- **“y … oblast-level alert starts”** contradicts D-002 and the merged-onset assumption. Define y from union starts across oblast, raion, and hromada records.
- **“Gap detection, duplicate counts … raise an error”:** the official dataset contains both. Define accepted gap boundaries and duplicate expectations; raise on unexpected deviations, after deduplication. Replace “≥ 24” with exactly the canonical 24 units.
- **D-003** says no *masked* hour has `active_at_t == 1`, contradicting CLAUDE.md and the plan. Correct it to no *unmasked* hour being active; independently test every unit.

## AMBIGUITIES

- **“last alert before … first alert after”:** start or end timestamps? National silence cannot establish exact recording coverage. Specify conservative, approved boundaries covering partial 29 August/2 September; mask labels whose `(t,t+H]` intersects missing coverage and invalidate rolling windows crossing it.
- **“overlap or touch” / “active_at_t”:** specify interval closure, simultaneous ends/starts, exactly 24h, and unknown ends. For example, activity uses `[start,end)`; test these boundaries independently.
- **“target_levels … red”:** specify filtering before union so red starting during yellow remains an onset (D-015); reject red-only official runs because colour is absent.

## MISSING

- **D-017 / “Changes … #6”:** #5 is omitted. Specify `--config`, `--as-of`, `reports/<run>/`, run metadata, and which artifacts M1 produces. Pin Python as well as package versions; test config and runner modules.
- **“edges of the onset window”:** two examples miss just-after-H events, configurable H, and cutoff leakage. Add independent expected labels and purge cases at every cutoff, explicitly settling equality at the cutoff.
- **“Extra tests”:** add leakage truncation plus a caught negative control, standing-alert preprocessing, gap-edge horizons, Kyiv City/Kyivska mapping and groups, and DST repeated/skipped local hours while retaining a unique UTC grid.

## QUESTIONS FOR THE HUMAN

- **D-009:** approve causal standing-alert handling, or explicitly accept retrospective exclusion and its deployment mismatch? Record the resolution before coding.
- **“adds about 40 minutes” / D-012, D-016:** what time remains for M2–M5 tonight? Set milestone timeboxes and move M6a to tomorrow; require a revised estimate including unresolved policies and tests.
