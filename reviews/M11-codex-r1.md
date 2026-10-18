### Shell: `'pwd; wc -l plans/M11.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md; cat plans/M11.md; cat CLAUDE.md; cat DECISIONS.md; cat .claude/skills/ts-leakage-audit/SKILL.md'`
/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo
     117 plans/M11.md
     156 CLAUDE.md
     301 DECISIONS.md
      30 .claude/skills/ts-leakage-audit/SKILL.md
     604 total
# M11 plan v1 — Live forecast check and analytics UI (unit panel, history strip, test replay, stability charts)

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things, also liked his UI, do same, but not how it looks
  but the analytics and maps, the design
### Shell: `"nl -ba CLAUDE.md; nl -ba DECISIONS.md | sed -n '1,90p'; nl -ba plans/M11.md; rg --files -g 'AGENTS.md' -g '*M8*' -g '*M10*' -g '*consensus*' -g '*live*' -g '*site*' -g '*.mjs' netlify src tests scrip`
     1	# Air-raid alert forecasting — project rules for Claude Code
     2	
     3	## Goal
     4	Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
     5	next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
     6	of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
     7	new yellow/red regime (see D-007).
     8	Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained be
### Shell: `"cat netlify/live/lib/runner.mjs; cat netlify/live/lib/live.mjs; cat netlify/live/lib/features.mjs; rg -n 'timeline|p_model|p_recent_rate|status|round|BSS|brier|metrics.csv|gap' scripts/build_site.py `
// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";

export const API = "https://api.alerts.in.ua/v1";
const HOUR = 3600e3, SNAPSHOT_DAYS = 7, FETCH_TIMEOUT = 8000;
export const STORE_NAME = "airalert-live";

async function getJSON(fetchFn, url, token, timeoutMs) {
  const r = await fetchFn(url, { headers: { Authorization: `Bearer ${token}` }, sign
### Shell: `"sed -n '1,95p' scripts/build_site.py; sed -n '205,285p' scripts/build_site.py; sed -n '1,180p' netlify/live/lib/features.mjs; cat netlify/functions/update-forecast.mjs; cat netlify/live/test/runner.t`
"""Build the results site and the README's generated blocks from saved reports only (M5 plan §2-§5).

  python scripts/build_site.py            # site/index.html + README generated blocks
  python scripts/build_site.py --evidence # also re-run the leakage tests and save reports/leakage_evidence.json

Reads ONLY reports/official, reports/official_h3, reports/new_regime (+ reports/leakage_evidence.json). Never reads data/,
never fits or scores, never recomputes a metric: every value is copied from
### Shell: `"cat plans/M10.md; sed -n '1,210p' tests/test_live_parity.py; rg -n 'coverage|reject|gap|negative|standing|Kyiv|compact' netlify/live/test/live.test.mjs; rg --files -g 'AGENTS.md' -g 'test_predictions`
# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and day/night tables, live forecast check). The live check and the UI are
  in `plans/M11.md`; this 
### Shell: `"sed -n '1,35p' plans/M10.md; sed -n '44,62p' netlify/live/test/live.test.mjs; head -4 reports/official/test_predictions.csv; head -4 reports/official/test_onsets.csv; rg -n 'onset|test_predictions|te`
# M10 plan v1 — Insights from a related project: label check, recency weighting, exposure features, stability tables

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things", referring to the ranked insights from the
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and day/night tables, live forecast check). The live check and the UI are
  in `plans/M11.md`; this 
### Shell: `"rg -n 'gap_or_missing|under_alert|test_onsets|test_predictions|status.*=' src scripts extras improve | head -100; rg -n 'test_replay|cumulative|M11' reviews/M11-codex-r1.log | head -12; sed -n '80,11`
scripts/run_extras.py:25:INPUTS = ["data/official_data_en.csv", "reports/official/test_predictions.csv",
scripts/run_extras.py:113:    dirty = subprocess.run(["git", "status", "--porcelain", "--", "extras", "scripts/run_extras.py"], cwd=ROOT,
extras/uncertainty.py:30:    path = Path(root) / "reports/official/test_predictions.csv"
extras/uncertainty.py:35:    s = p[p["status"] == "scored"].rename(columns={"p_recent_rate": "p_rr"})
src/evaluate.py:242:    out["share_under_alert"] = out["active_hou
I’ll read the four priority files first, then check relevant code and tests for leakage and rule conflicts.
I’m applying the leakage-audit skill to check the scoring design and its tests, especially coverage confirmation and forecasts made during ongoing alerts.
I found two concrete inconsistencies: the 14-day heatmap gets only seven days of history, and `state == "forecast"` does not exclude rejected history records—it can carry a caution instead. I’m checking whether the planned scoring tests would catch incomplete coverage and replay errors.
## BLOCKERS

- **A2 “coverage confirmed until”** permits holes before that endpoint. Require continuous label-window coverage and D-022/D-023 post-hole uncertainty masking; test a hole despite a sufficiently late confirmation.
- **A2 “rejected records are already excluded”** is false: `forecastAll` permits `state="forecast"` with `rejected_history_record`. Reconciliation can also discover an alert active at τ. Exclude unresolved label contamination and enforce D-003’s reconciled mask, unless the human approves another estimand.
- **A3 “last 7 days” / B2b “14-day”** cannot deliver the promised heatmap. Return 14 days of alert history, including coverage metadata; distinguish unavailable periods from zero onsets.

## AMBIGUITIES

- **A1 “first successful write”** lacks concurrency and migration semantics. Specify atomic creation, treatment of existing last-write snapshots, and an explicit maximum delay from the hour boundary.
- **A2 “BSS” / A4 “exactly 0”** omits undefined cases. Following D-025, return null with a reason for empty samples or zero reference loss; define bin endpoints, including p=1.
- **B1 “neighbours under alert now” / B2 “actual alert bands”** conflates physical alerts with D-020 capped state. Specify both separately, including exactly 24 hours and overlapping alerts.
- **B4 “−0.0101 … 1e-9”** conflicts with the saved value, −0.010064344018558602. Assert against the full-precision CSV; round only for display.

## MISSING

- **A4 “existing … parity … still pass”** does not test the new scorer’s isolation. Add archive-to-score tests proving later ends/reconciliation cannot change stored p/recent_rate; include negative controls using future ends and immature rolling labels. Preserve D-022/D-023’s `t+H ≤ cutoff`.
- **C “final cumulative BSS equals”** passes with shuffled hours or hardcoded totals. Test actual replay prefixes, unit alignment, and status filtering. Pin D-022–D-024 gap/post-gap/missing-feature exclusions around 29 August–2 September.
- **B2b “Kyiv time”** needs DST fixtures: repeated/skipped hours, partial days, and missing coverage. Test Kyiv City/Kyivska independently through history, grouping and replay (D-011/D-017).
- **D “Verification”** omits CLAUDE.md’s reviewer → fixes → human summary, proposed decision entry, and stage shapes/date ranges/base-rate logging. Add these completion requirements.

## QUESTIONS FOR THE HUMAN

- **A2 “snapshot’s state” / D-003:** Is live skill conditional on eligibility as issued or reconciled eligibility? Specify the estimand; approve any exception to D-003 explicitly.

VERDICT: CHANGES REQUIRED
