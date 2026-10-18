# M6-site plan v4 — yellow/red forecasts on oblast hover (M8 live site), baseline only until a model exists

Status: AGREED (consensus round 4, D-026; reviews/M6-site-consensus.md). Human decisions this plan rests on: plans/M6-definition.md (chat,
2026-10-17; proposed D-033–D-037, esp. D-036 "yellow/red only on oblast hover, labelled 'in training', with collection
status and the monthly chart"). M8 rules unchanged (plans/M8.md, proposed D-032). No new dependency, no API request,
no token use, no deploy. Not touched: `src/*.py`, `scripts/run_all.py` (code fingerprint), README.md, extras/,
reports/extras/, collect/, datastore/, reports/collect/, .github/, the M6c-1 model package.

## 1. Goal
On the live map's oblast card (hover / tap only; the map colour, legend, top list and table stay "any alert"), add a
section **"Yellow (drones) / Red (missiles) — in training"** with, per type, the chance that an alert of that level
starts in the next 60 minutes. No typed model exists yet (M6c-1 is building it), so the blend weight is w = 0 and the
section shows the per-type rolling recent-rate baseline, saying so: "baseline only (two-week rate); model in training".
Plus a status line "collecting data: N days of yellow/red history since 12 Sep 2026", and a placeholder + data contract
for the monthly chart (Brier skill vs baseline per type + blend weight), which M6c-1/M6b produce.

## 2. Finding that shapes the plan: the live state does NOT keep `alert_level`
`netlify/live/lib/live.mjs` `normalise()` keeps `id, unit, level (location_type), alert_type, start, end, updated`;
`alert_level` is dropped, and `scripts/build_live_seed.py` does not write it either. The deployed Blobs `state` (if any)
therefore has records without a level. Changes:
- `normalise()` adds `alert_level ∈ {"yellow","red"}`; any other value (missing, null, new string) → `null` and the
  record is still accepted (the "any" forecast never needs the level; rejecting would turn units grey). Counted in
  `status.level_unknown` (no token, no raw record).
- Levels are VERSIONED like ends (truncation-exact): each record keeps `levels = [[knownAt, level], …]`; a level is
  appended when first seen or when it changes, with knownAt = the poll / history-call time that delivered it.
  `levelAt(r, τ)` = the last version with knownAt ≤ τ (null if none). `applyActive`: a new record stores its level at
  the poll time; an existing one appends a changed level when the poll's `updated_at` ≥ the stored one. `applyHistory`:
  same, at the call time, so an old store is backfilled within one rotation (~24 min) for every alert inside the 30-day
  window, and a replay at τ before the backfill still sees "level unknown". The typed path selects records itself
  (first seen ≤ τ, start ≤ τ, end only if known at τ, `levelAt(r, τ)`, `alert_type`); `knownAt()` is unchanged.
- Typed coverage: `state.levelCoverage[unit]` = blocks `[from, to, confirmedAt]`, appended ONLY by history calls made
  by the new code (same merge/compaction as `coverage`). An old store starts with no typed coverage; a rebuilt seed
  (`build_live_seed.py` now writes `alert_level` and `levelCoverage = coverage`) starts with it. The existing `coverage`
  (any-alert labels) is unchanged, so the M8 forecast is byte-identical (tested, §6).

## 3. Per-type baseline at τ (no leakage; D-021 style)
Type T ∈ {yellow, red} = `alert_level` (M6-definition). Alert types counted: the SAME set as M8's approved "any" target
(human decision 2026-10-13: all API types; `TYPED_ALERT_TYPES` is re-exported from live.mjs `ALERT_TYPES`, one list).
So red also contains the few artillery-shelling alerts the API marks red (339 red / 5 yellow rows in the datastore vs
6,931 / 13,025 air-raid); the card says "levels as marked by alerts.in.ua; all alert types, as on the main map".
Restricting to air_raid would change the approved target set → a question for the human, not decided here. The typed
model must declare the same list (§5) or it is rejected.
- Alerts of type T known at τ = `knownAt(state, τ)` restricted to records with `alert_level = T` and `alert_type` in
  `TYPED_ALERT_TYPES` (first seen ≤ τ, end only if known at τ; unchanged M8 truncation).
- Intervals/onsets: `unitIntervals` on those alerts (D-020 24 h cap, D-023 merge, all location levels unioned per unit,
  D-002). A typed onset = start of a merged interval of THAT level (M6-definition PROVISIONAL default).
- Eligibility per type: label hour s is eligible iff level T is not active at s (red during yellow counts, and vice
  versa — M6-definition [rule]), its label window lies in confirmed typed coverage, and s is outside every typed-label
  hole's zone [h0 − 1 h, h1 + 24 h) — the same rule `offsetAt` already applies with per-unit gaps; typed holes =
  complement of `levelCoverage` confirmed at τ within [historyStart, τ), plus [−∞, historyStart), plus one raw hole
  per unresolved-level record (below).
- Unresolved level: a record of a typed alert type, known at τ, with `levelAt(r, τ) = null`. Its counting interval
  [start, e), e = min(end known at τ, start + 24 h) (start + 24 h if the end is unknown), is added to that unit's typed
  holes for BOTH levels. Effect (the existing hole rule): label hours s with s + 1 h ≥ start and s < e + 24 h are
  excluded from k, n and q; the unit's typed state is `data_gap` while τ ∈ [start, e) (it is unknown whether that level
  is active). It stops mattering once a history call delivers the level (then the version is visible from that call on)
  or once the zone leaves the look-back windows; it never blocks indefinitely.
- Baseline = `offsetAt` unchanged on these intervals and gaps: hours s with ceil(τ − 14 d) ≤ s ≤ floor(τ − 1 h), so
  only labels known by τ (label window (s, s + 1 h] ends ≤ τ); r = (k + 10·q)/(n + 10), q = the unit's expanding
  eligible typed-label rate since historyStart (national pooled fallback, exactly as M8 and `improve/live_ref.py`).
- Per-type state at τ (in this order): `level_active` if level T is active at τ under the capped intervals (no forecast
  of that type — its mask); `data_gap` if τ is in an event-hole extended zone (same `zones` as M8), or the unit has no
  typed coverage confirmed at τ, or τ is inside an unresolved-level record's [start, e), or the rate is null; else
  `forecast`. Caution
  `few_hours` if n < 48 (M8 constant). The typed section is computed for every unit, also when the "any" state is
  `alert_running` (e.g. red can be forecast during yellow).
- Blend (M6-definition): p = w·p_model + (1 − w)·p_base, w = n/(n + n₀)·clip(w*, 0, 1). Implemented as pure functions
  `blendWeight({n, n0, wStar})` and `blend(pModel, pBase, w)`; with no model w = 0 and p = p_base exactly. Computing
  w* live (it needs the model's past predictions on [τ − 28 d, τ − 1 h]) belongs to the model milestone; this milestone
  only defines where it plugs in (§5).

## 4. Payload (GET /api/forecast, same single request) and page
- `forecast.units[u].typed = {yellow: X, red: X}`, X = `{state, p, p_baseline, p_model: null, w: 0, recent_k, recent_n,
  caution[]}`; `forecast.typed = {label: "in training", mode: "baseline_only" | "blend", model: null | {version,
  trained_through}, weights: {yellow: {w, n, n0, w_star} | null, red: …}, alert_types: TYPED_ALERT_TYPES (= live.mjs ALERT_TYPES), horizon_minutes:
  60, history_days: N, history_since: historyStart}`.
- N days: N = floor(L / 1 day), L = length of ∩ over the 24 units of the typed coverage (`levelCoverage` confirmed at
  τ) within [historyStart, τ), minus the unresolved-level zones of any unit; `history_since` = the earliest moment of
  that intersection (derived, not hard-coded; 12 Sep 2026 17:00 with a rebuilt seed, ~30 days back on an old store).
  The page says "Live collection: N days of yellow/red history (complete for all oblasts) since <date>"; the training
  copy is the separate M6a datastore (collected daily on GitHub), which the page names but does not count. PROVISIONAL.
- Page (`site_src/template.html`, then `site/index.html` rebuilt with `build_site.py --readme <scratch copy>` so README.md
  is not touched). "On hover" = the oblast's own details, which on this page are two places: the hover/focus TOOLTIP
  (`liveTip`, mouse and keyboard) and the oblast CARD (`liveCard`, opened by click/tap/Enter — the only way on a phone).
  - Tooltip: two extra lines "Yellow (drones): 12% · Red (missiles): 3% — in training, baseline only".
  - Card: a block "Yellow (drones) / Red (missiles)" with the badge "in training", two rows (percent, or "yellow alert
    running", or "data gap"), "baseline only: two-week rate per type; model in training (blend weight 0)" (or "blend:
    model weight w = …" in blend mode), the collection status line, and the monthly-chart placeholder "Monthly track
    record (Brier skill vs the two-week rate per type, and the blend weight): available after the first monthly
    retrain."
  - Both texts come from pure functions `typedTipHtml(x, meta)` / `typedCardHtml(x, meta, monthly)` in one marked block
    of the template script, used by `liveTip`/`liveCard`. Map fill, labels, legend, top list, table and header do not
    change (not the main view, D-036). Stale rule: typed lines are shown only when the payload is not stale (the card
    already greys). Escaping as today (`esc`, numbers via `Number`).

## 5. Contracts for the later milestones (no data produced here)
- **Typed model plug-in:** `runUpdate`/`forecastAll` take an optional `typedModel` (default `null`). Contract:
  `{version, trained_through (ms), available_at (ms), alert_types, horizon_minutes: 60, predict(type, unit, tau, ctx) -> p ∈ (0,1),
  weight(type, tau, ctx) -> {n, n0, wStar}}`, with `ctx = {state, regions, zones}` = the same state the baseline sees
  (the model must apply the same "known at τ" selection; the plug-in's own truncation test is the model milestone's
  job). `forecastAll` throws on: `alert_types` ≠ `TYPED_ALERT_TYPES`, horizon ≠ 60, `trained_through + 1 h > τ` (a model
  whose labels reach past τ cannot forecast τ), `trained_through + 1 h > available_at` (malformed version),
  p outside (0, 1), n < 0, n0 ≤ 0. Version selection is causal: `typedModel` is a LIST of versions; at τ the one with
  the latest `available_at ≤ τ` is used; versions with `available_at > τ` are never used at τ (skipped, not an error);
  none → baseline only (w = 0, mode "baseline_only"). Replays of past
  τ therefore use the model that existed then. Tested with stubs: a late-available version is skipped at τ and used
  after it, a single late model alone → baseline only. Contract text (enforced by M6c-1/M6b,
  stated in the hand-over): the w* window [τ − 28 d, τ − 1 h] uses model predictions made out of sample (by a model
  trained before each predicted hour) and labels known by τ. Tested here with a stub model: p = blend,
  w = blendWeight, `mode = "blend"`, and each rejection.
- **Monthly chart:** file `netlify/live/data/typed_monthly.json`, committed as `{"schema": 1, "months": []}` (no data),
  imported by the read function and returned as `payload.typed_monthly`. Schema: `months[] = {month: "YYYY-MM",
  type: "any"|"yellow"|"red", brier_skill_vs_baseline, w_mean, n_rows, n_onsets}`; validated by `validMonthly()` (throws
  on a bad file; tested). Page: `months` empty → the placeholder text; non-empty → "n months available" (the chart
  itself is M6b's).
- A hand-over note for M6c-1/M6b goes to the shared notes folder.

## 6. Tests (node suite + Python; all existing tests must still pass)
- JS unit (`netlify/live/test/typed.test.mjs`): level kept from ACTIVE and history; backfill of an old record without
  level; unknown level → null, accepted, counted, "any" unaffected; levelCoverage only from new history calls; per-type
  eligibility (red onset during yellow counts; hour with red active masked for red only); `level_active`, `data_gap`
  (no typed coverage; null-level record in window; event zone) and `forecast` states; blend/blendWeight by hand (w = 0 →
  p = baseline exactly; clip; n/(n+n₀)); stub model mode; mismatched model rejected; monthly validator.
- **Truncation (leakage), on the production path:** `typedAt(fullState, τ)` equals `typedAt(truncate(fullState, τ), τ)`
  (records first seen after τ dropped; ends with endKnown > τ and level versions with knownAt > τ removed; coverage
  blocks confirmed after τ dropped) at pinned witnesses where the future information exists and would change the
  value: (a) an alert with finished_at < τ but endKnown > τ; (b) a level backfilled after τ for a record first seen
  before τ; (c) a coverage block confirmed after τ. Negative controls: an "oracle" state where those facts are made
  known at τ (endKnown/knownAt/confirmedAt set ≤ τ) gives a DIFFERENT value at each witness — so the witnesses are
  sensitive — and a leaky window variant counting immature hours τ − 1 h < s ≤ τ differs at its witness.
- **Python parity** (`tests/test_live_typed_parity.py`): on the saved API dump (all types, `config.new_regime_all_types()`), the JS
  typed k, n, rate and state per unit and type equal `improve/live_ref.live_offset` on the dump filtered to that level
  (and the typed mask from `grid`), at 18 random moments plus pinned ones: a red onset inside a yellow interval; a typed
  onset exactly at τ and at τ + 1 h; a typed onset exactly at the 14-day window's lower edge and at τ − 1 h; an alert
  exactly 24 h old (and ± 1 s); Kyiv City vs Kyivska; a moment in the history-start zone. Reads `improve/live_ref.py`
  only (not edited). DST and the official recording gap are out of range here: the API dump is 12 Sep – 12 Oct 2026
  (DST switch 25 Oct) and the official data has no levels; the baseline has no calendar input. Typed HOLES (coverage
  hole edges, post-hole 24 h boundary, unresolved-level zones) are covered by JS unit tests with hand-computed values.
- **"Any" unchanged (golden):** a golden file produced by the PRE-change code (`git show HEAD:netlify/live/lib/*.mjs`
  into a scratch dir) on fixed scenarios — normal, migration (old store without levels, then new history calls), a
  rejected ACTIVE and a rejected history record, a poll hole and its backfill — is committed under
  `netlify/live/test/golden_any.json`; the new code must reproduce every M8 field exactly.
- Page: a node test extracts the marked block (`typedTipHtml`, `typedCardHtml`) from the template and checks the output
  for baseline-only, level-active, data-gap and blend payloads (labels "in training", "baseline only", N days, the
  placeholder, escaping). A Python test checks that `liveTip` and `liveCard` call them, and that the map fill/value,
  legend, top list and table code in `drawLive` do not reference `typed` (hover-only rule). A browser check on the local
  dev server (`netlify/live/dev_server.mjs`, mocked data, no API): hover shows the tooltip lines, click shows the card
  block, the main view is unchanged. Token and
  no-external-request tests unchanged and passing.

Files: `netlify/live/lib/live.mjs`, `netlify/live/lib/typed.mjs` (new), `netlify/live/lib/runner.mjs`,
`netlify/functions/forecast.mjs`, `netlify/live/data/typed_monthly.json` (new), `netlify/live/test/typed.test.mjs`
(new), `netlify/live/test/typed_parity_cli.mjs` (new), `scripts/build_live_seed.py`, `site_src/template.html`,
`site/index.html` (rebuilt), `tests/test_live_typed_parity.py` (new), `tests/test_live_assets.py` (seed shape).

## 7. Risks / assumptions
- Old deployed store: typed shows "data gap" per unit until its first new history call (≤ ~24 min), then baseline from a
  30-day window (q from 30 days, not since 12 Sep) — stated in the hand-over and summary. A fresh seed avoids it.
- `site/index.html` may also be rebuilt by the parallel M9 session → merge conflict risk; I rebuild it last.
- Typed targets use M8's approved alert-type set; the M6c-1 model must declare the same set (contract check).
  Tests assert payload `alert_types` == `TYPED_ALERT_TYPES` == live.mjs `ALERT_TYPES`, and a model with another set
  is rejected.

## 8. Done when
`npm test` and `pytest -q` green (incl. parity, truncation with negative controls, "any" golden); site rebuilt;
reviewer + harness review run and fixed or argued; summary (< 250 words) + proposed DECISIONS entry. Commit: the task
brief from the human's session says "Commit on your own branch. Do not open a PR, do not merge" — one commit on
`claude/m6-site-hover-*`, nothing on main, no PR, no deploy (the human merges and deploys).

## Decided by the human (chat, 2026-10-18): yellow/red count AIR-RAID alerts only
"Yes: yellow/red count air_raid alerts only, matching M6c-1." `TYPED_ALERT_TYPES = ["air_raid"]` in typed.mjs; the
"any" map keeps all API types (M8). §3's "same set as M8" is superseded. Evidence that led to it is kept below.

## Open questions for the human (resolved 2026-10-18, above)
1. Typed targets inherit M8's set (all API types), so "red" includes artillery-shelling alerts marked red. Should
   typed targets be air_raid only (drones / missiles)? That is a target change for the human; the code has one switch.
   Checked 2026-10-18 against the human's parallel work (datastore, starts from 13 Sep, deduplicated by id):
   - In the API data, artillery alerts REMOVE onsets instead of adding them: air-raid-only gives 1,119 red / 4,509
     yellow onsets, all types 1,086 / 4,498. All 33 + 11 lost onsets are in Dnipropetrovska, where red artillery
     alerts (city/hromada level, 327 red rows, Nikopol/Marhanets area) keep the unit "under red", so a missile alert
     starting then is not an onset.
   - M10 §A (main checkout) measures the same artillery problem in the official data (hromada rows, Nikopol top) and
     leaves "air-raid-only target" as its question 2 for the human.
   - M6c-1 trained the typed models on air_raid only (`newregime.data.load()`); with the current switch the site would
     REJECT that model (alert_types mismatch) until the two agree.
   - M8/M11 keep all types for the "any" map; nothing here changes that.

## Deviation after review (implementation)
- Reviewer finding 2: a typed error (bad model version, model p outside (0, 1)) no longer throws out of `forecastAll`;
  the "any" forecast is written as before, every unit shows a typed data gap (caution `typed_error`), the payload carries
  `typed.mode = "error"` + the message and `status.typed_error` repeats it. A bad `typed_monthly.json` no longer breaks
  GET /api/forecast: `typed_monthly = null` + `typed_monthly_error`. Loud, not hidden; the "in training" part cannot
  take down the main forecast. (§5 said "throws"; the checks are unchanged, only where the error lands.)
- Reviewer finding 1: a rejected ACTIVE record makes that unit's typed state a data gap (as for "any").
- Harness finding 1: a known level changes only with a strictly newer `updated_at`.
