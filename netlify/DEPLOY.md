# Deploying the live map (M8)

The steps below need your Netlify login and the API token. Claude does not run them.

## 1. Build the assets locally

These are already built. Rebuild them only if a source changed.

```bash
.venv/bin/python scripts/export_live_model.py
```

```bash
.venv/bin/python scripts/build_live_seed.py
```

```bash
.venv/bin/python scripts/build_map.py
```

```bash
.venv/bin/python scripts/build_site.py
```

`netlify/live/data/seed_state.json` is gitignored (API data). Deploy only with the CLI from this folder, so that it gets bundled.

A Git-connected Netlify build would fail with `Could not resolve "../live/data/seed_state.json"`. Do not connect the repo for automatic builds.

## 2. Install, log in, link

```bash
npm ci
```

```bash
npx netlify-cli login
```

```bash
npx netlify-cli link
```

## 3. Set the token

Set it in the Netlify UI, not on the command line, so it stays out of your shell history:

- Path: Site configuration → Environment variables → Add variable.
- Key: `ALERTS_IN_UA_TOKEN`.
- Scope: Functions.

## 4. Deploy to production

Scheduled functions run on production deploys only.

```bash
npx netlify-cli deploy --prod
```

## 5. Check

- Netlify UI → Functions → `update-forecast` should show "Scheduled: every minute".
- `https://<your-site>/api/forecast` returns `{status, forecast}` within about 1–2 minutes.
- During the first ~24 minutes many oblasts show "data gap". Each run reconciles one oblast's history (24 oblasts in rotation), and the gap since the seed closes once every oblast has been reconciled.
- If `status.ok` is false (for example, a bad token returns HTTP 401), the page turns grey and says the last update failed.
- Broken records from the feed are listed in `status.rejected`, and the affected oblast shows a data gap or a caution.
- Oblasts whose history check has failed at least twice in a row are listed in `status.history_failing` and named on the page.
- M11: `https://<your-site>/api/history` returns the last 7 days of saved hourly forecasts and the last 14 days of alert intervals (HTTP 503 until the first run has stored a state). `https://<your-site>/api/check` returns the live check, recomputed at most once per UTC hour (HTTP 503 until the first computation). The check needs a few days of uptime before it scores anything: a saved forecast is scored only 4 hours after its hour starts, and only once every oblast's history covers the 24 hours before it.
- Hourly snapshots made before the M11 deploy are marked `legacy` and never scored (the `check_epoch` blob records the first M11 run).

## Local preview without a token

```bash
node netlify/live/dev_server.mjs
```

With no `ALERTS_IN_UA_TOKEN` in the environment, it replays the saved dump through the same runner (about 90 seconds), then serves http://localhost:8888 as of the dump's end, so the page shows "out of date". No network calls are made.

## Limits

- Each run makes 1 ACTIVE request and 1 history request per minute (the API limit is 2 history requests per minute).
- Snapshots are kept 35 days (about 840 small blobs). The check is cumulative since launch: one day before a day's snapshots expire, its summed losses are frozen into the `check_archive` blob (about 2 KB per day, never deleted), and a snapshot is deleted only after its day is frozen. Do not delete `check_archive`: the check then reports an error instead of silently restarting. Once per hour the scheduled run reads all of them to recompute the check; `/api/history` reads the last 168 on each request (cached for 5 minutes). If either gets slow, cache the assembled history in a blob (plans/M11.md, risks).
- The whole state is read and written as one blob every run, with strong consistency.
- The state grows by about 4 MB per month of alerts. The harness review measured a full run at about 8 s after 12 months and 9 s after 24 months (on a laptop; Netlify allows 30 s).
- Pruning old records needs the expanding prior kept as running per-oblast counts. That is proposed as follow-up work and is not built.
