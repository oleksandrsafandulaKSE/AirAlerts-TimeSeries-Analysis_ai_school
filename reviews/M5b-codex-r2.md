### Shell: `"pwd; rg --files -g 'AGENTS.md' -g '*leak*' -g 'SKILL.md' -g 'M5*' -g 'CLAUDE.md' -g 'DECISIONS.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
DECISIONS.md
CLAUDE.md
reviews/M5b-codex-r2.log
reviews/M5b-codex-r1.log
reviews/M5-codex-r4.md
reviews/M5-claude-r3.md
reviews/M5-codex-r3.md
reviews/M5-claude-r2.md
reviews/M5-codex-r2.md
reviews/M5b-claude-r1.md
reviews/M5-codex-r4.log
reviews/M5b-codex-r1.md
reviews/M5-codex-r1.log
reviews/M5-codex-r3.log
reviews/M5-codex-r2.log
reviews/M5-claude-r1.md
reviews/M5-codex-r1.md
reviews/M5-consensus.md
reports/leakage
### Shell: `'cat plans/M5b.md reviews/M5b-codex-r1.md reviews/M5b-claude-r1.md plans/M5.md CLAUDE.md DECISIONS.md'`
# M5b plan v1 — Results page for the general public: plain summary, tile map, forecast timeline

Status: v1.1 after consensus round 1 (D-026 loop). Human decisions in chat (2026-10-13): audience = GENERAL
PUBLIC; add a tile map of the 24 units and a forecast timeline; no M7 section and no language toggle on the site.
Rules: CLAUDE.md, D-011, D-021, D-024, D-025, M5 plan (every number from reports/, no hand-typed result numbers,
no network requests, code fingerprint untouched).

## 1. Goal
Re-lay
### Shell: `'cat CLAUDE.md plans/M5.md .claude/skills/ts-leakage-audit/SKILL.md reviews/PROPOSED-DECISIONS-M4-M5.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"rg --files --hidden -g AGENTS.md -g SKILL.md .; rg -n 'def build_frames|def score_final_test|joint|fingerprint|sha256' scripts/run_all.py src/model.py src/evaluate.py; cat src/grid.py src/baselines.p`
./.claude/skills/codex-plan-review/SKILL.md
./.claude/skills/milestone-protocol/SKILL.md
./.claude/skills/ts-leakage-audit/SKILL.md
src/model.py:27:def sha256_file(path):
src/model.py:28:    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
src/model.py:31:def sha256_text(text):
src/model.py:32:    return hashlib.sha256(text.encode()).hexdigest()
src/model.py:67:    return sha256_file(path)
scripts/run_all.py:33:def code_fingerprint(root=ROOT):
scripts/run_all.py:34:    """sha256 over t
### Shell: `'cat .claude/skills/ts-leakage-audit/SKILL.md; cat reviews/PROPOSED-DECISIONS-M4-M5.md; cat src/evaluate.py'`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
### Shell: `"sed -n '50,140p' scripts/run_all.py; sed -n '285,418p' scripts/run_all.py; sed -n '1,130p' src/grid.py; rg -n 'check_frozen|load_frozen|preregister|artifact|sha256|fingerprint' src/model.py"`
    """stdout of a git command, or None if git fails (e.g. no commit yet) -- never a bogus value."""
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def check_gap_rows(g, cfg):
    """Gap-masked rows must be exactly the hours of config.gap_label_mask_interval (M3 decision 4)."""
    expected = pd.Series(False, index=g.index)
    for a, b in config_mod.gap_label_mask_interval(cfg):
        expected |= (g
### Shell: `"nl -ba plans/M5b.md; sed -n '130,190p' src/grid.py; sed -n '1,155p' src/features.py; rg -n 'PROVISIONAL|D-031|frequency' plans/M5b.md reviews/M5b-claude-r1.md DECISIONS.md CLAUDE.md"`
     1	# M5b plan v1 — Results page for the general public: plain summary, tile map, forecast timeline
     2	
     3	Status: v1.1 after consensus round 1 (D-026 loop). Human decisions in chat (2026-10-13): audience = GENERAL
     4	PUBLIC; add a tile map of the 24 units and a forecast timeline; no M7 section and no language toggle on the site.
     5	Rules: CLAUDE.md, D-011, D-021, D-024, D-025, M5 plan (every number from reports/, no hand-typed result numbers,
     6	no network requests, code 
I’ll compare each prior finding with the updated plan and builder response, then check the provisional decisions against the project rules and leakage-audit skill.
The plan addresses most prior findings, including the recorded human exception for per-unit metrics. I’m checking two remaining points: whether the exporter leakage check tests meaningful predictions, and whether “quiet hours” accurately describes the scoring mask.
I’m applying the project’s `ts-leakage-audit` skill. The exporter check still omits DST coverage, and comparing null predictions at a gap edge can pass without testing the inputs. The new “quiet hours” wording also needs correction: D-020 includes hours when a standing alert remains active.
## PREVIOUS ITEMS

- **B1 — RESOLVED:** M5b §2 records the human’s explicit per-unit metric exception, with proposed D-031.
- **B2 — RESOLVED:** Explicit exclusion statuses, null predictions, broken lines and distinct bands are specified.
- **B3 — OPEN:** M5b §5 derives `status` through `grid.build_grid` alone, but that function produces no feature-availability information. Independently rebuild features and apply eligibility precedence to validate `feature_missing`; retain assignment mutations.
- **A1 — RESOLVED:** Separate merged-onset timestamps and an exact-hour boundary check are specified.
- **A2 — OPEN:** Scored-hour denominators and tile reasons are addressed, but public group comparisons still call every low-n group “few hours.” `src/evaluate.py::low_n_flags` also flags groups because units lack sufficient positive/negative cases, regardless of group row count. Show the actual reason there too.
- **A3 — RESOLVED:** Positive, negative, zero and undefined skill cases now have explicit wording and accompanying counts.
- **A4 — RESOLVED:** D-014/D-016 corrections are proposed for human-owned decision records.
- **A5 — RESOLVED:** Proposed D-029 now specifies system fonts and no network requests.
- **M1 — OPEN:** Exporter checks cover only six test times, omitting the requested DST case. Prediction equality alone also permits null-versus-null comparisons at excluded gap rows. The leakage-audit skill requires feature-column equality: compare inputs and causal state before suppression, add DST coverage, and retain the recent-rate negative control.
- **M2 — RESOLVED:** Summary, proposed decisions, consensus record and retained M5 checks are included.
- **Human question — RESOLVED:** The builder records explicit authorization for the breakdown.

## PROVISIONAL DECISIONS

- Frequency as the default map view stays within CLAUDE.md/D-026: presentation only, pending ratification.
- Per-unit metrics are a rule exception, correctly identified as human-authorized rather than provisional consensus.

## NEW ISSUES

- M5b §3’s “oblast was quiet” misstates the estimand. D-020 explicitly includes hours with standing alerts still active after 24 hours. Explain that forecasts exclude alerts within their first 24 hours; use this meaning consistently in map and timeline labels.

VERDICT: CHANGES REQUIRED
