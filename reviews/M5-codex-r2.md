### Shell: `"pwd && rg --files -g 'AGENTS.md' -g '*leak*' -g 'SKILL.md' -g 'M5*' -g 'CLAUDE.md' -g 'DECISIONS.md' -g 'ROADMAP.md'"`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
DECISIONS.md
reviews/M5-codex-r1.log
reviews/M5-codex-r2.log
reviews/M5-claude-r1.md
reviews/M5-codex-r1.md
tests/test_leakage.py
plans/ROADMAP.md
plans/M5.md
CLAUDE.md

### Shell: `'cat plans/M5.md reviews/M5-codex-r1.md reviews/M5-claude-r1.md CLAUDE.md DECISIONS.md plans/ROADMAP.md'`
# M5 plan v1 — README, figures, results site (Netlify), optional Streamlit

Status: v1.1 after consensus round 1 (D-026 loop). Human instruction (2026-10-13, chat): "implement m4 and m5,
create a great visual, host on netlify, don't commit". The human is asleep: decisions inside the rules are taken by
consensus and marked PROVISIONAL.
Rules: CLAUDE.md, ROADMAP M5, D-006, D-013, D-015 (amended by D-021), D-021, D-024–D-027.

## 1. Goal
Communicate the finished results honestly: a complete README,
### Shell: `'cat reviews/M5-claude-r1.md; tail -90 reviews/M5-codex-r1.md'`
# Claude response, round 1 — plans/M5.md

## Changes made
- B1 Streamlit — AGREE: REQUIRED (ROADMAP M5, D-012); minimal app reading only reports/, smoke test.
- B2 figures — PARTLY: README figures are ONLY PNGs written by run_all.py (reliability plots for H = 1, H = 3, new regime, validation). build_site.py makes no figure files; the site draws charts in the browser from the same saved CSV values. This satisfies "every figure comes from a reports/<run>/ file produced by run_all.py" without chang
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"cat CLAUDE.md .claude/skills/ts-leakage-audit/SKILL.md; rg --files --hidden -g AGENTS.md -g '"'!.git/**'"' -g '"'!.venv/**'"'"`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"sed -n '320,505p' scripts/run_all.py; rg -n 'reliability|before_after|transfer|write|metrics|reason|within_unit' scripts/run_all.py src/evaluate.py src/baselines.py; sed -n '1,110p' DECISIONS.md"`
# ---------------- M4: the single final-test scoring (stage final-test) ----------------

def _verify_prereg(run_dir, data_path, check_code=True):
    pr_path = run_dir / "preregistration.json"
    if not pr_path.exists():
        raise data.DataQualityError(f"{pr_path} missing: run the fit stage for {run_dir.name} first")
    pr = json.loads(pr_path.read_text())
    for name, h in pr["sha256"].items():
        actual = data.file_sha256(data_path) if name == "data" else model.sha256_file(run_dir
### Shell: `"rg -n '"'^def test_|negative|mutation|cutoff|DST|truncat'"' tests/test_leakage.py tests/test_final_test.py tests/test_new_regime.py; rg --files scripts app tests .claude/skills"`
tests/test_leakage.py:1:"""Truncation-invariance leakage test (ts-leakage-audit) on the REAL official data, with a negative control."""
tests/test_leakage.py:17:def truncate(alerts, t):
tests/test_leakage.py:24:def truncation_check(feature_fn, alerts, times, units=None, columns=None):
tests/test_leakage.py:25:    """Mismatches (t, unit, column) between features from full data and from data truncated at t."""
tests/test_leakage.py:31:        cut = feature_fn(truncate(alerts, t), pd.DatetimeIndex(
### Shell: `'cat .claude/skills/ts-leakage-audit/SKILL.md; nl -ba plans/M5.md'`
---
name: ts-leakage-audit
description: Leakage audit for time-series features and evaluation. Use whenever features, the grid, the target, the train/test split or the evaluation code are created or changed, and before any metric is reported.
---

# Time-series leakage audit

## Core rule
A forecast made at time t may only use information with timestamp <= t.

## Required test: truncation invariance (tests/test_leakage.py)
1. Pick 5 random forecast times t from different periods (include one aft
I’ll compare each prior finding with the updated plan and builder’s response, then check the provisional decisions against the project rules and leakage-audit skill.
The plan addresses most prior findings. Two stale requirements remain: the done criterion still generates figure files, and the HTML smoke check still loads `data.json`, despite the revised choices to reuse saved PNGs and embed JSON. I’m checking whether the source-key tests and deployment criteria leave any substantive gaps.
The provisional choices fit the existing rules: Streamlit remains required, SVG/JavaScript adds no dependency, and the preview is supplementary. Applying the leakage-audit skill, I found the revised evidence wording appropriately limited to tested cases. The remaining provenance gap is that the proposed README checks miss integer results and verify regeneration consistency without independently checking source mappings.
## PREVIOUS ITEMS

- **B1 — RESOLVED:** Streamlit is mandatory in §§2, 6 and 9; remove the stale “optional” headings.
- **B2 — OPEN:** Reusing pipeline PNGs is acceptable, but [M5.md:98](/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/plans/M5.md:98) still requires `build_site.py` to regenerate `reports/figures/`, contradicting §4’s “no new figure files.” Remove that requirement.
- **B3 — OPEN:** §8 independently checks embedded JSON against source keys, but README checks only compare regeneration with itself. A consistently mislabelled README passes; the decimal-only regex also misses integer counts and percentages. Independently verify README values and labels against source keys and cover all numerical result formats.
- **A1 — RESOLVED:** §3.6 specifies merged onsets, target endpoints, purge equality and the mature-label history window.
- **A2 — RESOLVED:** §3.6 distinguishes gap boundaries, uncertainty and horizon-specific exclusions.
- **A3 — RESOLVED:** §3 requires nulls, reasons, low-n flags and AUC inclusion/exclusion information.
- **A4 — ACCEPTED:** D-025 explicitly defines time-since-end bins; documenting these as the implemented state requires no rule amendment.
- **A5 — OPEN:** Inline JSON addresses file-URL loading, but [M5.md:94](/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/plans/M5.md:94) still tests loading `data.json`. Test the embedded payload and actual file-URL rendering.
- **M1 — RESOLVED:** §3.6 requires actual leakage-test evidence and limits claims to tested cases.
- **M2 — RESOLVED:** §8 checks Kyiv City, Kyivska and frontline mappings.
- **M3 — RESOLVED:** §9 includes the summary, proposed decision entry and consensus record.
- **Q — ACCEPTED:** Authentication is an external blocker; deployment must remain explicitly outstanding until a Netlify URL is verified.

## PROVISIONAL DECISIONS

- Static site plus required Streamlit: within D-012 and the user’s hosting instruction.
- Inline SVG/JavaScript: within dependency rules; remove §3’s contradictory CDN alternative.
- Private preview: within scope as a supplementary deliverable; it cannot satisfy Netlify hosting.
- Authentication-dependent deployment: an execution constraint, not permission to redefine hosting as completed.

## NEW ISSUES

None beyond the unresolved inconsistencies above.

VERDICT: CHANGES REQUIRED
