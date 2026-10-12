# Planning session log — 12 Oct 2026 (planning chat, Claude Code)

A summary of the planning conversation between Oleksandr (architect) and Claude (builder).
Not a word-for-word transcript. The API token is deliberately left out.
Decision details and evidence: `DECISIONS.md`. Current roadmap: `plans/ROADMAP.md`.

---

## 1. Starting point
- The repo had only rules and scaffolding: `CLAUDE.md`, `DECISIONS.md` (D-000 open, D-001–D-006 = v1 bugs),
  a skeleton README, the milestone-protocol skill, the `reviewer` agent and the leakage-audit skill. No code, no commits.
- `.git` was in the parent folder → `git init` inside `repo/` (D-012).

## 2. New alert system and data sources
- **Oleksandr:** since Sept 2026 alerts have two levels: yellow = drones, red = missiles. Before
  September, any attack (drone or missile) triggered the single alert.
- **Checked by Claude:**
  - Vadimkin `official_data_en.csv` **froze at 2026-09-07 05:28 UTC**. The repo still updates daily, but
    only `volunteer_data_*`, which is oblast-level only, from eTryvoga, with no colour.
  - alerts.in.ua API (token requested by Oleksandr, tested OK): history only via `month_ago` →
    closed alerts from 2026-09-12 17:16 UTC; it has `alert_level` red/yellow and raion/hromada records;
    `threats[]` appears only in live data. 7–12 Sep is missing from both sources.
  - The full API month for all oblasts was saved to `data/raw/alerts_in_ua/` (gitignored): 16,739 alerts,
    10,559 yellow / 6,180 red. The token is kept in `.env` (gitignored).
- **Decision D-007 (Option A):** train and run the final test on official data only (test 27 Jul–7 Sep 2026);
  the API period is a separate exploratory section. The sources are never mixed.

## 3. Data issues found
- **Standing alerts:** hromada alerts lasting up to 604 days would mark a whole oblast as under alert for months.
- **30-minute alerts:** 68 alerts last exactly 30 minutes (0.02%) → kept (D-010).
- **Luhanska** is excluded (permanent alert); Crimea isn't in the data → 24 units (D-008).
- **Groups:** Kyiv City / frontline (8 oblasts) / rear (15 oblasts) (D-011).
- **Duplicates (from the web research, then verified):** 113,845 of 299,275 official rows are exact duplicates.
- **Recording gap:** 29 Aug has only 88 onsets, 30 Aug–1 Sep have no rows at all, and data resumes 2 Sep (D-013).

## 4. Related work (web research, items since 2024, Ukraine only)
- **Typical models:** LightGBM pooled across oblasts, logistic regression, Random Forest (arXiv:2411.14625),
  CatBoost on counts, survival models.
- **Honest results:** PR-AUC about 0.30–0.34, against a base rate of about 0.09–0.15. The rolling recent-rate
  baseline is hard to beat.
- **Common mistakes:** an "alert active" target (PR-AUC 0.8–0.9 that means nothing), no baselines, summing
  every admin level, choosing the model on the test set.
- **Adopted (D-013):**
  - remove duplicates first;
  - mask the recording gap;
  - a leakage test with a negative control;
  - a calibrated-persistence baseline;
  - within-oblast AUC.

  Optional: bootstrap CI and per-group reliability plots.
- **Skipped:** text, Telegram and weather features, several horizons, survival models, hyperparameter search.

## 5. Yellow-zone analysis (D-015)
- **Before vs after the reform (alerts per month):**
  - rear oblasts rose 2–12× (Kyiv City 90 → 212, Zhytomyrska 58 → 225);
  - frontline oblasts stayed flat;
  - 83% of new alerts start yellow;
  - 36% of red alerts start while a yellow is already active.
- **Decision:**
  - before/after table;
  - the frozen model scored on "any alert starts" (red-only as an optional row);
  - within-oblast AUC and calibration-in-the-large;
  - the conclusion depends on the results (amended in D-021).

## 6. Extra rows and automation
- **D-014:** a weekly refit inside the test window, as an optional extra row. The headline stays the frozen model.
- **D-016:** an automated GitHub Actions workflow (daily API fetch, monthly retrain). Later set to
  **future work**; a yellow-alert model needs Oleksandr's approval.
- **D-017:** architecture prepared so M6 fits later:
  - `regions.py`;
  - one shared alert format for both sources;
  - named run configs;
  - a target level setting (any / red);
  - `reports/<run>/` output;
  - data checks that raise errors;
  - pinned versions;
  - geopandas dropped.
- Backdating commits was declined. Oleksandr will commit honestly and state manually what wasn't implemented.

## 7. Review process
- The `reviewer` subagent stays as the post-implementation code reviewer.
- **Codex** (a different model) reviews plans through `.claude/skills/codex-plan-review`
  (read-only, high reasoning, one round, then a lead judgment by Claude; Oleksandr decides).
- **Reviews run:**
  - `reviews/M1-codex.md`;
  - `reviews/ALL-codex.md` (the detailed M1–M6 plan);
  - `reviews/ROADMAP-codex.md` (the roadmap and README).
- **Key Codex catches:**
  - the >24h standing-alert rule used the final `finished_at`, which is leakage → **D-020, a causal rule**;
  - M3 scoring baselines on the final test could steer M4 → **the final test is scored once, in M4**;
  - the rolling baseline needs only labels already known at t;
  - the planned leaky control would be empty on unmasked rows;
  - D-003's wording is backwards.
- **D-019, two-level planning:**
  - roadmap → Codex → Oleksandr;
  - then for each milestone: plan → Codex → Oleksandr → implement → tests → reviewer.

## 8. Final roadmap-level decisions (D-020, D-021)
- **Standing alerts:** an alert counts as "under alert" only for its first 24h; its start is still an onset.
- **Recent-rate baseline:** rolling over 14 days, using only labels known by t. Recorded as an explicit
  exception to "baselines frozen".
- **Train start:** all history from 2022-03-15. Validation = [2026-06-29, 2026-07-27).
- **No refit** after early stopping. Calibration is checked on validation.
- **Final test** scored once, at the end of M4. **Primary metric:** Brier skill against recent-rate.
  Not beating it is a valid result.
- **Scope:** M1–M5. M6 is future work.

## 9. Outcome
- **Files written in this session:**
  - `CLAUDE.md`, `DECISIONS.md` (D-007–D-021), `plans/ROADMAP.md`, `plans/ALL.md`, the old `plans/M1.md`;
  - the README, written as the full design;
  - `.claude/skills/codex-plan-review/` and the milestone-protocol update;
  - `reviews/*.md`.
- **Implementation** happens in a separate chat. M1 is implemented there.
- **Models per step:** Opus for plans and reviews, Codex for plan critique, Sonnet for implementation.
  Opus is also used for the M2 leakage test.

## Open items at the end of the session
- `reviewer.md` line 19 still checks the old ">24h excluded" rule; it should check D-020.
- D-003's wording ("masked" → "unmasked") is Oleksandr's entry to fix.
- D-018 (Codex as plan reviewer) was proposed in chat; Oleksandr writes it.
- The next API fetch must happen before ~10 Nov 2026, or history from after 12 Sep is lost.
