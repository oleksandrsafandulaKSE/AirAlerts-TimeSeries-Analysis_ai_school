### Shell: `'cat plans/site-redesign-definition.md reviews/site-redesign-definition-codex-r1.md reviews/site-redesign-definition-claude-r1.md reviews/PROPOSED-DECISIONS-site.md CLAUDE.md DECISIONS.md .claude/skil`
# Site redesign — definition (grilling session with the human, 2026-10-18)

Status: agreed with the human in chat ("all agreed", "agreed, also go for round with codex"). Lines marked **[rule]**
change an existing D-entry (proposed or ratified); they are the human's decisions and are proposed in
`reviews/PROPOSED-DECISIONS-site.md`. Lines marked PROVISIONAL are design defaults for the milestone plans (D-026).
Work starts from `main` after the merge of M6a, M6c-1, M6-site and M10/M11 (done: 8f91ab
### Shell: `'wc -l plans/site-redesign-definition.md reviews/site-redesign-definition-codex-r1.md reviews/site-redesign-definition-claude-r1.md reviews/PROPOSED-DECISIONS-site.md CLAUDE.md DECISIONS.md'`
     120 plans/site-redesign-definition.md
     204 reviews/site-redesign-definition-codex-r1.md
      18 reviews/site-redesign-definition-claude-r1.md
      23 reviews/PROPOSED-DECISIONS-site.md
     156 CLAUDE.md
     301 DECISIONS.md
     822 total

### Shell: `'cat reviews/site-redesign-definition-claude-r1.md reviews/PROPOSED-DECISIONS-site.md'`
# Site-redesign definition — Claude response, round 1

## Changes made
- B1 alert-type contract: AGREE (verified newregime/data.py:17 air_raid only vs live.mjs:17 all types). One contract: air-raid only on the main map; listed as D-045, a consequence of the human's D-042 choice.
- B2 P(red | onset): AGREE. Defined as conditional on an "any" onset (merged-interval start); colour = level starting at that instant, ties → red; escalations inside yellow excluded; N = 0 / incomplete coverage states; r
### Shell: `'cat CLAUDE.md; rg --files -g AGENTS.md; tail -n 100 reviews/site-redesign-definition-codex-r1.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `"sed -n '1,180p' src/regions.py; sed -n '1,210p' newregime/data.py; sed -n '1,130p' newregime/blend.py; sed -n '360,490p' newregime/pipeline.py"`
"""The single table of the 24 forecast units. The ONLY place names are mapped (D-017 #1)."""

# key, official English name (verbatim from official_data_en.csv), alerts.in.ua UID, group (D-011)
_UNITS = [
    ("kyiv_city", "Kyiv City", 31, "kyiv_city"),
    ("chernihivska", "Chernihivska oblast", 25, "frontline"),
    ("sumska", "Sumska oblast", 20, "frontline"),
    ("kharkivska", "Kharkivska oblast", 22, "frontline"),
    ("donetska", "Donetska oblast", 28, "frontline"),
    ("dnipropetrovska",
### Shell: `'nl -ba plans/site-redesign-definition.md; nl -ba reviews/site-redesign-definition-claude-r1.md; nl -ba reviews/PROPOSED-DECISIONS-site.md'`
     1	# Site redesign — definition (grilling session with the human, 2026-10-18)
     2	
     3	Status: agreed with the human in chat ("all agreed", "agreed, also go for round with codex"). Lines marked **[rule]**
     4	change an existing D-entry (proposed or ratified); they are the human's decisions and are proposed in
     5	`reviews/PROPOSED-DECISIONS-site.md`. Lines marked PROVISIONAL are design defaults for the milestone plans (D-026).
     6	Work starts from `main` after the merge of M6a
### Shell: `"rg -n 'unknown|alert_level|red|yellow|national|HORIZONS|test_start|test_end|reserve|overlap' newregime/data.py newregime/pipeline.py newregime/blend.py tests/test_newregime.py tests/test_newregime_le`
tests/test_newregime_leakage.py:99:    common = h.rename(columns={"y": "y_any"}).assign(y_red=h["y"] * (np.arange(len(h)) % 2))
tests/test_newregime_leakage.py:104:        sh = NB.red_share(cc, score, pi, 10.0, pd.Timedelta(days=14), H)[0]
tests/test_newregime_leakage.py:112:    c2.loc[fut, ["y_any", "y_red"]] = 1 - c2.loc[fut, ["y_any", "y_red"]]
tests/test_newregime_leakage.py:117:    c3.loc[past, "y_red"] = 1 - c3.loc[past, "y_red"]
tests/test_newregime_leakage.py:133:            assert f.loc
### Shell: `"rg -n -C 5 'alert_level|unknown' src/data.py; sed -n '36,112p' newregime/pipeline.py; sed -n '1,75p' newregime/frames.py"`
5-import pandas as pd
6-import requests
7-
8-from src import regions
9-
10:SHARED_COLUMNS = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
11-OFFICIAL_COLUMNS = ["oblast", "raion", "hromada", "level", "started_at", "finished_at", "source"]
12-
13-
14-class DataQualityError(RuntimeError):
15-    pass
--
52-
53-    excl = dedup["oblast"].isin(regions.EXCLUDED)
54-    print(f"[data] excluded-unit rows dropped: {int(excl.sum())} "
55-          f"({dedup.loc[excl,
### Shell: `"nl -ba DECISIONS.md | tail -65; rg -n -C 2 'split|ratif|D-040|test week|national|conditional|baseline' reviews/PROPOSED-DECISIONS-M6c-1.md reviews/PROPOSED-DECISIONS-M6.md plans/M6c-1.md"`
   237	  Missing counts on non-gap test rows: `onsets_last_7d` 1,728 (= 72 × 24), `onsets_last_24h` 576,
   238	  `minutes_since_last_start` 470, `minutes_since_last_end` 459.
   239	- Counts of missing features in the test period may be printed: they describe which inputs exist, not labels
   240	  or results. This is an exception to decision 4 (M2).
   241	- Optional extra: score the 09-04 → 09-07 rows separately, labelled "feature missing after the gap"; never
   242	  part of the headline.
 
### Shell: `"rg -n 'M12|M13|deploy|cutover|atomic|unavailable|ratif|approve|gate|version' plans/site-redesign-definition.md reviews/site-redesign-definition-claude-r1.md reviews/PROPOSED-DECISIONS-site.md; nl -ba`
reviews/PROPOSED-DECISIONS-site.md:21:## D-045 — Main map is air-raid only (consequence of D-042; me to ratify)
reviews/site-redesign-definition-claude-r1.md:6:- B3 scorer: AGREE (verified check.mjs:112-120 hard-codes 1 h). Versioning by (model version, target, H), maturity τ + H + SETTLE, coverage [τ − 24 h, τ + H], no pooling across models/horizons.
reviews/site-redesign-definition-claude-r1.md:9:- A2 blend state, A3 test-week boundaries, M1 parity controls, M2 metadata/reliability/AUC: AGREE,
I’ll read the priority files, check each prior finding and provisional decision against the project rules, then inspect code where the evidence needs it.
I’m applying the leakage-audit skill’s causality and cutoff checks. The update addresses most prior findings; I’m checking the rolling national comparator and whether any provisional choices change project rules.
The target, scorer and replay definitions are clearer now. Two checks remain material: the air-raid-only switch is still marked “me to ratify,” and the plan puts archive versioning in M13 after M12’s live export. I’m checking whether the plan explicitly gates that cutover.
## PREVIOUS ITEMS

- B1 — RESOLVED: one air-raid-only contract now covers labels, masks, features, baseline and scorer.
- B2 — RESOLVED: merged-onset conditioning, simultaneous colours, escalations and replacement-model comparability are defined.
- B3 — RESOLVED: model/target/horizon separation, label maturity and coverage requirements are explicit.
- B4 — RESOLVED: retrospective replay pins inputs and artefacts and checks published-metric consistency.
- A1 — ACCEPTED: a causal rolling national comparator need not be train-fitted; bounds, coverage and empty-window behaviour are defined. Unknown levels already raise (`src/data.py:186–187`).
- A2 — RESOLVED: M12 must specify model/horizon state, maturity, distinct events and replacement resets.
- A3 — RESOLVED: proposed UTC boundaries, target-window containment and reservation scope are specified.
- M1 — RESOLVED: independent truncation, mutation and negative controls are required per horizon.
- M2 — RESOLVED: metadata, exclusions, common support, reliability and within-oblast AUC are explicit.
- Human Q1 — ACCEPTED: later revisions are explicitly disclosed as a retrospective limitation.
- Human Q2 — OPEN: recording collisions does not reconcile them. D-045 explicitly says “me to ratify,” while Claude reports “None new” under escalations. Choosing M6c-1 does not establish explicit approval to amend D-040’s alert-type contract. Identify amendments unambiguously and gate their implementation on human approval under D-026.

## PROVISIONAL DECISIONS

- Red precedence for simultaneous starts and excluding escalations are consistent with D-023’s merged-onset event; they do not redefine the existing unconditional red model.
- Validation-only labels are presentation defaults.
- The later test-week dates implement D-043’s stated later-week scope. Horizon-scoped reservations must preserve protection against previously accessed weeks.
- D-045 is a rule amendment, not an inferable provisional design choice.

## NEW ISSUES

- **Cutover dependency:** the plan assigns live export to M12 (lines 75–82), but snapshot/archive migration to M13 (lines 32–34). Explicitly keep exports inactive until compatible scoring and storage exist, or move that migration into M12. Otherwise the proposed rollout permits new forecasts to reach the existing one-hour scorer before its replacement.

VERDICT: CHANGES REQUIRED
