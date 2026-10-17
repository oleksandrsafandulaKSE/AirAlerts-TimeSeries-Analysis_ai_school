# M6a — daily alerts.in.ua collection into `datastore/alerts_in_ua.csv`

Status: PLAN (Claude–Codex consensus loop, D-026). The human started M6a (2026-10-17, via the main session).
Rules used: D-016 (M6 workflow, the one committed data file), D-017 #6 (checks raise), D-020 (24h cap), D-027 (keep
open alerts; dedup by `id`, keep latest `updated_at`), CLAUDE.md Data/Architecture (token, ≤ 2 history requests/min,
`data/` gitignored, no new dependency).

## 1. Goal
Stop losing new-regime history. alerts.in.ua `month_ago` keeps ~30 days, so every day not collected after
2026-10-12 + 30 d is gone for good. M6a delivers:
1. a collector that fetches `/v1/regions/{uid}/alerts/month_ago.json` for the 24 forecast units and appends every new
   record VERSION to an append-only CSV;
2. a seed of that CSV from the saved dump `data/raw/alerts_in_ua/2026-10-12T1645Z/` (covers alerts finished from
   2026-09-12 16:52 UTC, which no live fetch can return any more);
3. a daily GitHub Actions workflow that runs the collector and commits the CSV + a pull log;
4. one manual test run (local dry run, then one `workflow_dispatch` run), with the 403 fallback documented.

Out of scope: any loader of the datastore into `src.data` / the shared format for modelling, retraining, evaluation
(M6b, needs the human), README text (the M9 session edits README; a README paragraph is a follow-up).

## 2. Files
New only. `src/*.py` and `scripts/run_all.py` are NOT edited (they are hashed by `scripts/run_all.py::code_fingerprint`,
pinned by `tests/test_improve_models.py::test_headline_code_fingerprint_matches_both_preregistrations`).
- `collect/__init__.py`, `collect/api_collector.py`: fetch, validate, merge, pull log. Imports `src.regions` read-only
  (UIDs, `api_oblast_name`, `API_404_UIDS`, `EXCLUDED_API_UIDS`).
- `scripts/collect_api.py`: CLI. `--datastore DIR` (default `datastore/`), `--log PATH` (default
  `reports/collect/pull_log.csv`), `--seed-from DUMP_DIR` (one-off seed, no network), `--dry-run` (fetch + validate +
  merge into a scratch copy, print counts, write nothing in the repo).
- `tests/test_collect.py`: offline tests (§6). No network in tests.
- `.github/workflows/collect_api.yml`: the daily job (§5).
- `datastore/alerts_in_ua.csv` (seeded), `reports/collect/pull_log.csv`.
- `.gitignore`: add `!datastore/alerts_in_ua.csv` (the repo ignores `*.csv`; `reports/**/*.csv` is already allowed).
- `requirements.txt`: unchanged (stdlib `csv`/`json` + pinned `requests`; no new dependency).

## 3. Fetch
- UIDs: exactly the 24 unit UIDs from `src.regions.UNITS[*]["api_uid"]`. Excluded UIDs (16, 29, 30) and the 404 UIDs
  (6, 7) are not requested (never used, D-008). Fixed order (ascending UID).
- Rate: the collector spaces its requests ≥ 65 s apart (≤ 1/min; 24 requests ≈ 26 min). Sleep is injected (testable).
- Auth: `Authorization: Bearer <token>` header from env `ALERTS_IN_UA_TOKEN` (locally loaded from `.env`; in Actions
  from the repo secret). Missing/empty → raise before any request. Token never in URLs, prints, exception messages,
  files or the pull log. Error messages contain only the UID, HTTP status and the path.
- Rate isolation from M8 = DEPLOYMENT PREREQUISITE. M8's cron (`netlify/functions/update-forecast.mjs`, `* * * * *`)
  makes 1 history request per run with the Netlify token, has no limiter shared with GitHub, and delayed invocations
  can bunch. Whether the API limit is per token or per IP is undocumented. So the collector runs ONLY with its own
  alerts.in.ua token, distinct from the Netlify one: separate token + separate IP (GitHub runner vs Netlify) isolate
  it under either reading, and the collector alone stays ≤ 1/min (CLAUDE.md "max 2 history requests/min"). The human
  obtains it and stores it as the GitHub secret `ALERTS_IN_UA_TOKEN` (same env name, CLAUDE.md). Until then the
  workflow is not enabled (the schedule starts only after the human merges, §5). The local dry run (§7.3) happens
  only while M8's scheduled function is paused or with the collector token.
- Errors: 429 or 5xx → wait 120 s and retry, at most 2 retries per UID and at most 6 retries per run. Per-request
  HTTP timeout 30 s (a timeout counts as a retryable error). A budget exhausted → the run fails and commits
  nothing; the next daily run re-covers the day via the 29-day window overlap (a hole arises only after ~29 failed
  days, §4.4). Worst SUCCESSFUL run = 24 successful requests each taking the full 30 s, plus 6 retryable failures
  (each a 30 s timeout + 120 s wait): 24 × (65 s + 30 s) + 6 × (30 s + 120 s) = 38 + 15 = 53 min. 403 → raise immediately with "403: likely geo-block
  of the runner; see self-hosted fallback (plans/M6a.md §5)". 401 → raise ("token rejected"). Any other non-200,
  invalid JSON or a missing `alerts` list → raise. One UID failing = the whole run fails: nothing is written, nothing
  committed (D-017 #6). The 29-day overlap of daily windows absorbs a failed day.
- `fetched_at` = UTC time the response for that UID arrived (ISO `...Z`, second precision), stored per UID.

## 4. Datastore and merge
### 4.1 `datastore/alerts_in_ua.csv`, one row = one record VERSION
Columns, fixed order: `id, updated_at, requested_uid, unit, fetched_at, pull_id, location_type, location_uid,
location_oblast, location_oblast_uid, location_raion, location_title, location_title_en, alert_type, alert_level,
started_at, finished_at, notes, country`.
- API values are stored as the raw strings the API returned (no parsing, no tz conversion). JSON null → empty field,
  and the reader `collect.read_datastore()` decodes an empty field back to `None` (so `finished_at` is `None`, as
  `src.data.api_alerts` expects). Lossless because an API value that is the empty string `""` raises at validation.
  `location_raion` exists only on hromada rows (1,080 of 16,739 in the dump) → empty (= absent) elsewhere.
- `unit` = canonical key of `requested_uid` (`src.regions`), NEVER `location_oblast_uid` (wrong for sub-oblast rows).
- `fetched_at`, `pull_id` = the pull in which THIS version was first seen (the "known at" time of this version).
  `pull_id` = the run's start time `YYYY-MM-DDTHHMMZ` (seed: `seed-2026-10-12T1645Z`).
- All alert types are kept (air_raid, artillery_shelling, urban_fights, any new type); consumers filter on
  `alert_type`. Open alerts (empty `finished_at`) are kept (D-027). D-016 says "CSV of closed alerts"; D-027 later
  amended the CLAUDE.md API merge rule "(M4/M6)" to KEEP open alerts, and storing open versions is required for
  "known at t". Read as already decided by D-027; flagged to the human for confirmation, not an escalation.
### 4.2 Merge rule (append-only)
- Key = (`id`, `updated_at`). A fetched record whose key is already in the file is skipped. A new key is appended.
  So an alert seen open on day d and closed on day d+1 has two rows.
- "Known at t" contract (reference function `collect.as_known_at(rows, t)`, for M6b): (1) keep rows with
  `fetched_at` ≤ t; (2) per `id`, keep the row with the latest PARSED `updated_at` (D-027); (3) an end with
  `finished_at` > t is hidden (end unknown → D-020 cap), as `src.data.truncate_api_records` does. Knowledge time is
  ALWAYS `fetched_at`, never backdated to `updated_at`; seeded rows are unknown before the dump's fetch time
  (2026-10-12 16:45–17:00 UTC). The D-027 full-history view = `as_known_at(rows, +inf)`.
- Same key with different content in any API column → raise (the API changed a record without bumping `updated_at`).
- The same `id` under two `requested_uid` → raise (as `src.data.api_alerts` does).
- Appended rows are sorted by (`requested_uid`, `id`, `updated_at`) for deterministic diffs.
- Append-only guard: before writing, the existing file's bytes must be an exact prefix of the new file; else raise.
  Write to a temp file, fsync, rename (atomic).
### 4.3 Validation of each pull (all raise, before anything is written)
- every requested UID returned 200;
- every record has exactly the 14 known API fields, plus optionally `location_raion` (a new or missing field = schema
  change → raise);
- `location_oblast` == `regions.UNITS[unit]["api_oblast_name"]` for every record of that UID (file identity);
- `started_at`, `updated_at`, non-null `finished_at` parse as ISO-8601 with a `Z` suffix (parsed for validation and
  comparisons; the raw strings are stored); `finished_at` ≥ `started_at`; no field holds the empty string;
- `alert_level` ∈ {yellow, red}. A new `alert_type` value is NOT an error: stored, and printed in the type counts;
- window check (evidence for the assumed API contract, §8): per UID, the earliest non-null `finished_at` must be
  ≥ `fetched_at − 30 d − 1 h`; else raise (the API window is not what the coverage rule assumes);
- printed per run: records per UID, new rows, skipped duplicates, open alerts, counts per `alert_type` × `alert_level`.
### 4.4 Pull log `reports/collect/pull_log.csv` (append-only, run metadata like `run_meta.json`)
One row per UID per successful run: `pull_id, uid, unit, http, fetched_at, nominal_window_from (= fetched_at − 30 d),
n_records, n_new_rows, n_open, n_retries, git_commit`.
- Deleted alerts: the API may drop a record; its rows stay. Detecting deletions would need per-pull id membership
  (a second data file or one row per sighting), so M6a does NOT detect them (known limitation, §8).
- Coverage is NOMINAL: unit u is assumed covered on [nominal_window_from, fetched_at] of each pull, under the API
  contract of §8 (not documented; checked per pull only by the window check of §4.3). Event coverage
  ([nominal_window_from, fetched_at]) and knowledge time (`fetched_at`) are separate columns.
- HOLE = a pull whose `nominal_window_from` is later than the unit's previous `fetched_at`. Per D-017 #6 a detected
  gap fails the run and NOTHING is committed. Within the current rules there is no automatic recovery: every later
  run fails the same way (the previous `fetched_at` never moves), so collection STOPS until the human decides
  (GitHub e-mails the owner on every failed run). A hole needs ~29 consecutive failed days. A recovery path (a
  human-acknowledged hole recorded in the log, then commit) would be an exception to CLAUDE.md Architecture #6 and
  is asked of the human in §9, NOT built by default. The `accepted_hole_from/to` columns are therefore dropped.
- Write order and crash recovery: both files are written to temp files, then the CSV is renamed, then the log.
  At start, every `pull_id` in the CSV must exist in the log (a pull with 0 new rows has log rows only); otherwise
  raise "incomplete previous run" with the repair (drop the CSV rows of that pull_id; nothing was committed). In
  Actions the checkout is fresh and the commit happens only after both writes, so a crash commits nothing.
- The seed writes the log rows from the dump's `manifest.tsv` (24 unit UIDs, their real `fetched_at`).

## 5. Workflow `.github/workflows/collect_api.yml`
- Triggers: `schedule` daily at 03:17 UTC (off the hour; GitHub cron may be delayed) + `workflow_dispatch`. NO
  `push`/`pull_request` triggers (the job holds a secret; and see the self-hosted note).
- `runs-on: ${{ vars.COLLECT_RUNNER || 'ubuntu-latest' }}` → the fallback is a repo variable, no code change.
- `permissions: contents: write`; `concurrency: collect-api` (no overlapping runs); `timeout-minutes: 75` (the
  worst successful collector run 53 min (§3) + setup/pytest/commit ≈ 5 min + margin).
- Steps: checkout → setup-python 3.13 → `pip install -r requirements.txt` → `pytest -q tests/test_collect.py`
  (collector tests gate the fetch; failing test = no fetch, no commit) → `python scripts/collect_api.py` with
  `ALERTS_IN_UA_TOKEN: ${{ secrets.ALERTS_IN_UA_TOKEN }}` → if the CSV or log changed: commit
  `data: alerts.in.ua pull <pull_id>` as `github-actions[bot]`, `git pull --rebase` then push (retry once). A
  collector exit ≠ 0 stops the job before the commit step.
- No raw JSON is committed or uploaded; the CSV holds every field.
- Scheduled workflows run from the default branch only, so the schedule starts once the human merges to `main`.
- 403 fallback (only if the manual run gets 403): the human registers a self-hosted runner (e.g. the human's Mac, label
  `collect`) and sets `COLLECT_RUNNER=collect`. Because the repo is PUBLIC, the runner must only take this workflow:
  no `pull_request` triggers anywhere in the repo for that label, and fork-PR workflows need approval (repo setting).
  The Mac must be awake at 03:17 UTC; a missed day is absorbed by the 30-day window.

## 6. Tests (`tests/test_collect.py`, offline; HTTP via an injected fake session, sleep via a fake clock)
1. Seed from a small fixture dump (manifest + 3 UID files built in the test): rows carry the manifest `fetched_at`,
   `unit` from the requested UID even when `location_oblast_uid` is a raion id; artillery/urban rows and open alerts kept.
2. Merge: re-merging the same pull adds 0 rows; open→closed adds exactly 1 row; `as_known_at(+inf)` shows the closed
   version. Known-at-t with a NEGATIVE CONTROL: alert opens (pull 1, day d), its end at d 10:00 is first fetched on
   d+1 03:17 (pull 2), and a correction of `started_at` arrives in pull 3. `as_known_at(d 12:00)` must return the open
   version with the original start; at d+1 04:00 the closed one; a naive "latest `updated_at` regardless of
   `fetched_at`" selector must FAIL these assertions. Seeded rows are absent from `as_known_at(2026-10-12 16:00)`.
3. Append-only guard, with a NEGATIVE CONTROL: a merge function that rewrites an old row must be caught by the guard.
4. Same key, different content → raises; same id under two UIDs → raises.
5. Any UID non-200 (403, 401, 404, 500 after retries, bad JSON) → raises and the datastore and log are byte-identical
   to before. 403 message names the self-hosted fallback.
6. Rate and budget: the fake clock shows ≥ 65 s between ANY two consecutive requests (retries included); a 429
   retry waits 120 s. Budget exhaustion (separate cases): a 3rd failure of one UID, and a 7th retryable failure in
   one run, each raise with nothing written. Worst SUCCESSFUL schedule (separate case): 6 retryable failures (30 s
   timeouts, spread over ≤ 3 UIDs, ≤ 2 each) plus 24 successful responses each taking 30 s → the run succeeds and
   its fake-clock duration is ≤ 53 min (below the 75 min job timeout).
7. Token: with a fake token `TEST-SECRET-XYZ`, run success and failure paths; capture stdout/stderr, exception text,
   written files: the token appears nowhere. Missing token → raises before any request.
8. Schema: an extra field, a missing field, `alert_level` = "green", a non-`Z` timestamp, a malformed timestamp
   ending in `Z` (`2026-13-40T..Z`), an empty-string field, a wrong `location_oblast`, an earliest `finished_at` older
   than the window → raise; a new `alert_type` → stored. Null round-trip: `finished_at`/`notes`/`location_raion`
   null → empty → `None`.
9. Coverage: pulls 1 day apart → no hole; 29 days apart → no hole; 31 days apart → raises, CSV and log
   byte-identical, and a second attempt raises again.
   Crash recovery: CSV renamed but log not (simulated) → the next run raises "incomplete previous run".
10. Compatibility: rows of the datastore, deduplicated by D-027, converted to records with `_file_uid =
   requested_uid`, go through `src.data.api_alerts` (read-only import) and give the same frame as the fixture dump
   read with `src.data.read_api_dump`. Proves M6b can load the file without `src` changes to the alert format.
   Fixture witnesses: Kyiv City (UID 31) and Kyivska (UID 14) rows stay separate units; an open alert started > 24 h
   before the fetch is kept with `finished_at = None`; timestamps on both sides of the DST change
   (2026-10-25 00:59:59Z / 01:00:00Z) stay UTC strings unchanged. Feature/grid behaviour is unchanged by construction
   (`src/` is not edited) and stays covered by the existing suite (`pytest -q`).
- The full `pytest -q` must still pass (incl. the code-fingerprint test: `src/` untouched).

## 7. Manual test run and milestone close (done = all true)
1. `pytest -q` passes. 2. Seed: `python scripts/collect_api.py --seed-from data/raw/alerts_in_ua/2026-10-12T1645Z`
→ row count printed and equal to the dump's records for the 24 units (expect 16,739 minus the excluded/404 UIDs'
records; printed, not assumed). 3. Local `--dry-run` (one real fetch, ~26 min, token from `.env`): 24 × 200, new rows
and overlap with the seed printed (most seed ids must be skipped as duplicates). 4. After the human merges to `main`
and adds the secret: `gh workflow run collect_api.yml`; the run is green, a bot commit appears, the log has 24 rows,
the Actions log contains no token. If step 4 gets 403 → §5 fallback, then re-run.
5. `reviewer` subagent + `code-review-harness` on the diff; FIX-FIRST items fixed or explained. 6. Summary for the
human (< 250 words) with a proposed DECISIONS.md entry and the PROVISIONAL decisions; then stop (milestone-protocol).
Steps 3–4 need the human (API calls, merge to `main`, the repo secret); the human may order 5–6 before 4.
Every API call is made only after the human approves it at implementation time (CLAUDE.md: token).

## 8. Risks / assumptions
- `month_ago` is assumed to filter by `finished_at` ≥ fetch − 30 d and to always return open alerts (dump evidence,
  not documented). The coverage definition depends on it; the dry run checks the earliest `finished_at` per UID.
- An open standing alert whose `updated_at` changes daily would add one row per day (Lypetska since 2026-03-10…).
  Measured in the dry run; acceptable (a few rows/day).
- Size: the dump as CSV ≈ 3.9 MB per 30 days → ≈ 47 MB/year. GitHub warns at 50 MB and refuses at 100 MB per file:
  fine for ~2 years; splitting by year would need the human (D-016 names one file).
- Public repo: the committed CSV republishes alerts.in.ua data (D-016 approved committing it; licence not re-checked).
- GitHub disables schedules in public repos after 60 days without repository activity; daily bot commits should keep
  it active (to verify after the first month).
- If M8's live function is not deployed, the 65 s spacing is merely conservative.
- Record deletions by the API are not detected (§4.4).

## 9. Open questions (design, for the loop)
- Seed or not: the plan seeds (saves 2026-09-12 → 09-18, unrecoverable otherwise).
- New `alert_type` values: store (plan) vs raise.
- For the human (not decided by the loop): (a) confirm that committing OPEN versions is covered by D-027 /
  CLAUDE.md line 139 "API merge rule (M4/M6) … KEEP open alerts" (D-016 still says "closed alerts");
  (b) obtain a second alerts.in.ua token for the collector (deployment prerequisite, §3);
  (c) RULE-EXCEPTION QUESTION: after a coverage hole (~29 failed days), should a human-acknowledged hole be
  recorded and collection resume (exception to CLAUDE.md Architecture #6 "detected gaps … nothing is committed"),
  or does collection stay stopped until a rule change? The plan builds the strict version.
