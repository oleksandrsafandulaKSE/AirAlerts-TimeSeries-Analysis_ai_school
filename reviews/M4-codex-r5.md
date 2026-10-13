### Shell: `'cat plans/M4.md reviews/M4-codex-r4.md reviews/M4-claude-r4.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M4 plan v1 — Models (H = 1, H = 3) + the single final-test scoring + new-regime section

Status: v1.5 — round-4 consensus + one implementation correction (history_start) under review in round 5. Human decisions already given in chat
(2026-10-13): one model per horizon ("option 1") → train an H = 1 model (headline) and an H = 3 model
(extra results row); the new-regime section stays H = 1 (M3b provisional decision).
Rules: CLAUDE.md, D-005, D-006, D-007, D-011, D-013, D-015 (amended by D-021), 
### Shell: `'wc -l reviews/M4-codex-r4.md reviews/M4-claude-r4.md; tail -70 reviews/M4-codex-r4.md; cat reviews/M4-claude-r4.md'`
     114 reviews/M4-codex-r4.md
      16 reviews/M4-claude-r4.md
     130 total
### Shell: `"cat CLAUDE.md; sed -n '1,82p' DECISIONS.md; rg --files src tests scripts .claude/skills/ts-leakage-audit; rg --files --hidden -g AGENTS.md -g '"'!'"\\.git' /Users/oleksandrsafandula/Desktop /Users/ol`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast
### Shell: `"cat CLAUDE.md; rg --files --hidden -g AGENTS.md -g '"'!'"\\.git' .; cat src/config.py; rg -n 'history_start|detect_gaps|uncertainty|coverage_end' src tests scripts"`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"sed -n '1,83p' DECISIONS.md; cat src/grid.py src/features.py; ls data/raw/alerts_in_ua/2026-10-12T1645Z; head -8 data/raw/alerts_in_ua/2026-10-12T1645Z/manifest.tsv; rg -n 'month_ago|history_start|fe`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `".venv/bin/python - <<'PY'
import json,csv
from datetime import datetime,timedelta
from pathlib import Path
from src import regions
p=Path('data/raw/alerts_in_ua/2026-10-12T1645Z')
manifest=list(csv.D`
zsh:1: can't create temp file for here document: operation not permitted

### Shell: `".venv/bin/python -c 'import json,csv; from datetime import datetime,timedelta; from pathlib import Path; from src import regions
p=Path(\"data/raw/alerts_in_ua/2026-10-12T1645Z\")
manifest=list(csv.D`
{'units': 24, 'history_start': '2026-09-12 17:00:43+00:00', 'earliest_closed_start': '2026-09-11 05:50:03.250000+00:00', 'closed_start_before_own_cutoff': 42, 'min_finish_margin_seconds': 196.0, 'total_alerts': 16737}

### Shell: `".venv/bin/python -c 'import csv,json; from pathlib import Path; from datetime import datetime,timedelta; from src import regions
p=Path(\"data/raw/alerts_in_ua/2026-10-12T1645Z\"); uids={str(regions.`
{'closed_starts_before_global_cutoff': 50}

### Shell: `".venv/bin/python -c 'import csv,json; from pathlib import Path; from datetime import datetime,timedelta
p=Path(\"data/raw/alerts_in_ua/2026-10-12T1645Z\");rows=[r for r in csv.DictReader((p/\"manifes`
{'all_successful_files_before_own_cutoff': 42, 'all_successful_files_before_global_cutoff': 50}

I’ll read the updated plan and response against the prior findings, then check each provisional decision against the project rules and leakage-audit skill.
The prior findings remain addressed in the plan. The new change is the API history boundary; I’m applying the leakage-audit skill to check whether the 24-hour uncertainty zone keeps incomplete earlier history out of scored rows.
## PREVIOUS ITEMS

- **B1 RESOLVED:** Open-alert retention, causal masking, and onset preservation remain tested.
- **B2 RESOLVED:** Both horizons are frozen and jointly recorded before test-label access.
- **B3 RESOLVED:** Artifact, data, and code hashes are checked before access.
- **B4 RESOLVED:** Transfer reloads the complete predictor and checks validation reproduction.
- **A1 RESOLVED:** Platt fitting, failure conditions, and reporting branches remain explicit.
- **A2 RESOLVED:** Exposure excludes history uncertainty, consistent with D-027.
- **A3 RESOLVED:** Requested UID is checked against oblast identity.
- **M1 RESOLVED:** Fit/validation keys and purge boundaries remain tested for both horizons.
- **M2 RESOLVED:** Raw-API truncation checks features, eligibility, and predictions with a negative control.
- **M3 RESOLVED:** Required outputs, diagnostics, and proposed decision entry remain specified.
- **Q1 ACCEPTED:** Approved versus detected gap boundaries explain the mask duration.
- **Q2 RESOLVED:** D-027 authorizes causal open-alert handling.
- **Previous new blocker RESOLVED:** Gap detection remains bounded to API coverage with a regression fixture.

## PROVISIONAL DECISIONS

- Fixed LightGBM parameters remain within D-013.
- ECE threshold and Platt calibration remain within D-021.
- API grid end remains bounded by manifest coverage under D-015.
- Low-n flags supplement D-025 without changing AUC eligibility.
- Inherited API H=1 scope and `official_h3` naming remain authorized.
- **New history boundary ACCEPTED:** Independently recomputed maximum cutoff is `2026-09-12 17:00:43 UTC`. This implements coverage handling within D-007/D-015/D-023/D-024. The 24-hour uncertainty extension covers missing earlier intervals under D-020; window and time-since exclusions protect scored rows. It changes no project rule.

## NEW ISSUES

- **Nonblocking evidence correction:** §5.2 and the response claim **53 closed alerts** started before the cutoff. Reading the saved dump gives **42** before their respective file cutoffs, or **50** before the common maximum cutoff, across the 24 canonical units. Correct the count and specify which cutoff it describes. The boundary calculation and survivorship argument still hold.

VERDICT: AGREE
