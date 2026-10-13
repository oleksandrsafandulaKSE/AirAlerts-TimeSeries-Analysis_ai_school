# Consensus record — plans/M4.md (D-026 loop)

- **Outcome:** CONSENSUS after 4 rounds, re-confirmed in round 5 after an implementation correction. Round 2 escalated the open-API-alert rule; the human chose option A (D-027); rounds 3–4 closed the remaining items.
- **Codex's final verdict (round 4, verbatim):** "None identified in these revisions. Approval concerns the plan; bounded gap detection and the specified tests still require implementation and verification." — `VERDICT: AGREE`
- Earlier status (kept for the record): ESCALATION after round 2.
- **Codex's round-2 verdict (verbatim, key line):** "National censoring around dump-open alerts changes the mask and evaluation protocol based on future closure status. D-024 does not authorize manufacturing unknown features from known starts. Under D-026, this requires human resolution; it cannot be approved as an ordinary provisional design choice." — `VERDICT: CHANGES REQUIRED`

## Escalation — open API alerts vs CLAUDE.md's "closed alerts only" merge rule
- Facts (dump 2026-10-12T1645Z): 41 open alerts; 39 belong to the 24 units; 12 started inside the API window
  (Dnipropetrovska 6, Poltavska 1, Kharkivska 5; 09-17 10:06, 10-11 08:33, 10-12 05:35, 10-12 14:16–15:53).
- Problem: "closed only" decides whether an alert exists from its FUTURE closure. Under the leakage audit (truncate at t,
  hide ends > t) every alert ongoing at t looks open, so a closed-only loader drops it in the truncated copy but keeps
  it in the full dump → the truncation test fails by construction; and dropping the 12 erases real onsets/masks.
- Option A (recommended by Claude and consistent with Codex): amend the CLAUDE.md API merge rule to "dedup by id
  keeping the latest updated_at; KEEP open alerts with an unknown end, handled by the D-020 causal 24h cap" — the same
  treatment as truncated official alerts. No zones needed; the API window stays ≈ [09-20 17:00, 10-12 16:00).
- Option B: keep "closed only" + national missing-data zones around in-window open starts (Claude's round-1 proposal).
  Codex rejects it: the zones depend on future closure status and break the loader-to-predictor truncation test.
  Cost: scored window ≈ [09-25 11:00, 10-11 08:00).

## Resolved in rounds 1–2 (no human action needed)
Hash-bound pre-registration (model, calibrator, baseline tables, data, code fingerprint); access marker before labels;
ONE joint marker for both horizons (fixed after round 2); full calibrated predictor reloaded for transfer; Platt details;
before/after definitions with exposure; API identity check against the requested UID; exact fit/validation keys and
behavioural isolation for H = 1 and H = 3; D-017 outputs for new_regime; gap 145 h reconciliation (accepted by Codex).

## PROVISIONAL design decisions (Claude+Codex, human to ratify)
LightGBM params (lr 0.05, 31 leaves, min_data_in_leaf 100, seed 20261013, deterministic, early stopping 100 on pooled
validation logloss, max 2,000 rounds); ECE threshold 0.02 + Platt; new-regime grid end 2026-10-12 16:00; low-n flag
(< 100 eligible rows in a group, or units excluded from within-unit AUC).

## Rounds 3–4
Round 3: open-alert test expectation, exposure wording, and a NEW blocker (gap detection over the 2024 → 2026 span created by old open alerts) → fixed by bounding API gap detection to [history_start, coverage_end). Round 4: everything RESOLVED/ACCEPTED.

## Round 5 (implementation correction)
Reality differed from §5.2: "earliest closed start" gave history_start 2026-09-11 05:50. Evidence showed `month_ago` is
bounded by finish time (earliest `finished_at` ≥ `fetched_at − 30 d` in every file), so history_start =
max(fetched_at − 30 d) = 2026-09-12 17:00:43 UTC. Codex recomputed it independently and ACCEPTED (`VERDICT: AGREE`);
its one correction (42/50 early closed alerts, not 53) is applied. PROVISIONAL: this history_start definition.
