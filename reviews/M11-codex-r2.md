### Shell: `'cat plans/M11.md reviews/M11-codex-r1.md reviews/M11-claude-r1.md CLAUDE.md DECISIONS.md .claude/skills/ts-leakage-audit/SKILL.md'`
# M11 plan v1 — Live forecast check and analytics UI (unit panel, history strip, test replay, stability charts)

## Status and authority
- **Human, chat 2026-10-18:** "plan implementing all those things, also liked his UI, do same, but not how it looks
  but the analytics and maps, the design is different". "His UI" = air-alert-forecast-ua.netlify.app
  (github.com/yehor-o/time_series_air_alerts, `site/`). We copy the ANALYTICS, not the look: our own design
  tokens, our SVG geoBoundaries map (`
### Shell: `"wc -l plans/M11.md reviews/M11-codex-r1.md reviews/M11-claude-r1.md CLAUDE.md DECISIONS.md; tail -45 reviews/M11-codex-r1.md; cat reviews/M11-claude-r1.md; cat CLAUDE.md; cat .claude/skills/ts-leakag`
     161 plans/M11.md
      89 reviews/M11-codex-r1.md
      24 reviews/M11-claude-r1.md
     156 CLAUDE.md
     301 DECISIONS.md
     731 total
  comparison with github.com/yehor-o/time_series_air_alerts (artillery/non-air-raid rows, recency weighting,
  hours-under-alert features, per-week and day/night tables, live forecast check). The live check and the UI are
  in `plans/M11.md`; this 
### Shell: `"sed -n '1,35p' plans/M10.md; sed -n '44,62p' netlify/live/test/live.test.mjs; head -4 reports
### Shell: `'cat DECISIONS.md; cat plans/M8.md; cat reviews/M8-consensus.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"cat netlify/live/lib/runner.mjs; cat netlify/live/lib/live.mjs; cat netlify/live/lib/features.mjs; sed -n '200,300p' scripts/build_site.py; rg -n 'timeline|round|DST|Kyiv' tests/test_site.py plans/M1`
// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";

export const API = "https://api.alerts.in.ua/v1";
const HOUR = 3600e3, SNAPSHOT_DAYS = 7, FETCH_TIMEOUT = 8000;
export const STORE_NAME = "airalert-live";

async function getJSON(fetchFn, url, token, timeoutMs) {
  const r = await fetchFn(url, { headers: { Authorization: `Bearer ${token}` }, sign
### Shell: `"nl -ba netlify/live/lib/runner.mjs | sed -n '1,155p'; nl -ba netlify/live/lib/live.mjs | sed -n '1,70p'; rg -n 'retain|retent|historyStart|35|30|SNAP|epoch|forecast time|τ|D-032' plans/M8.md reviews/`
     1	// One scheduled update (plans/M8.md §2), with injected fetch / store / clock so it can be tested without network.
     2	import { applyActive, applyHistory, forecastAll, nextRotationUnit } from "./live.mjs";
     3	
     4	export const API = "https://api.alerts.in.ua/v1";
     5	const HOUR = 3600e3, SNAPSHOT_DAYS = 7, FETCH_TIMEOUT = 8000;
     6	export const STORE_NAME = "airalert-live";
     7	
     8	async function getJSON(fetchFn, url, token, timeoutMs) {
     9	  const r = await fet
### Shell: `"nl -ba netlify/live/lib/live.mjs | sed -n '65,163p'; nl -ba plans/M11.md | sed -n '28,96p'; nl -ba plans/M11.md | sed -n '103,158p'; rg -n 'negative|ends|reconcil|immature' netlify/live/test/live.tes`
    65	// Validate a batch record by record. A bad record of a KNOWN unit is rejected and marked (that unit shows "data gap"
    66	// while marked); an unknown oblast name cannot be attributed, so it fails the whole batch (a schema change needs a human).
    67	function validated(state, alerts, t, regions, where) {
    68	  if (!Array.isArray(alerts)) throw new DataError(`${where}: alerts is not an array`);
    69	  const ok = [], rejected = [];
    70	  for (const raw of alerts) {
    71	    t
I’ll read the six priority files, check each prior finding and provisional decision against the project rules, then inspect relevant code where needed.
I’m applying the supplied leakage-audit skill to the archive-to-score boundary. The updated plan addresses most prior findings, but it still lacks explicit DST test fixtures; I’ll also check whether state retention supports the longer archive.
The rejection safeguard is still incomplete: it checks only cautions saved at issue time, while `applyHistory` can later reject records and still confirm coverage. The planned scorer could therefore count an unknown outcome as negative. I also found a boundary mismatch: exactly +15 minutes is allowed by the lateness rule but excluded by its stated scoring interval.
## PREVIOUS ITEMS

- **RESOLVED — Coverage holes:** A2 requires continuous coverage across the label window and preceding 24 hours.
- **OPEN — Rejected records/reconciliation:** Reconciled masking is fixed, but rejection checks cover only issue-time cautions. Later history can reject a label-window record while confirming coverage ([live.mjs](/Users/oleksandrsafandula/Desktop/AirAlerts-TimeSeries-Analysis_ai_school/repo/netlify/live/lib/live.mjs:120)); rejection markers expire after 24 hours. A clean snapshot can therefore receive an unknown outcome scored as negative. Preserve reconciliation-side contamination until resolved; exclude affected rows and test rejection discovered after issuance.
- **RESOLVED — History length:** A3 supplies 14 days of alerts and coverage.
- **RESOLVED — Snapshot semantics:** Concurrency limitations, migration, and lateness policy are documented.
- **RESOLVED — Undefined BSS/bins:** Null reasons and probability endpoints are specified.
- **RESOLVED — Physical/capped alerts:** Both representations and neighbour semantics are explicit.
- **RESOLVED — Replay precision:** Assertions use the full-precision saved metric.
- **RESOLVED — Scorer isolation:** Archive mutation checks and a leaky-scorer negative control are specified.
- **RESOLVED — Replay validation:** Prefix, alignment, filtering, and gap assertions are specified.
- **OPEN — DST fixtures/Kyiv separation:** Kyiv separation is covered. B2b defines DST behaviour, but A4/C still omit the requested tests for repeated/skipped hours, partial days, and incomplete block coverage. The builder’s “AGREE” does not supply those fixtures.
- **RESOLVED — Completion protocol:** Reviews, fixes, human summary, proposed decisions, and stage logging are included.
- **RESOLVED — Estimand question:** A2 explicitly selects the intersection of issued and reconciled eligibility.

## PROVISIONAL DECISIONS

The intersection estimand, three-hour settlement delay, 15-minute cutoff, 35-day retention, and snapshot selection policy remain within the authorized exploratory live scope. None changes official targets, baselines, splits, or scoring. D-003 remains enforced; D-026 requires recording these as provisional without editing CLAUDE.md or DECISIONS.md.

## NEW ISSUES

- A1 says forecasts become late **more than** 15 minutes after the hour, but specifies eligibility ending exclusively at +15 minutes. Choose one boundary and test exactly +15 minutes.

VERDICT: CHANGES REQUIRED
