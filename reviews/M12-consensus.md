# M12 — consensus record

- Outcome: **consensus**, 4 rounds. No escalation, no deadlock.
- Codex final verdict (round 4): `VERDICT: AGREE` — "None identified in the revisions."

## PROVISIONAL decisions (Claude+Codex consensus, human to ratify)
1. `M12Split`: train/validation as M6c-1 (09-13 → 10-04 → 10-11), an unused gap [10-11, 10-18), test week [2026-10-18, 2026-10-25), scored once after coverage reaches 10-25.
2. Reservation scoped to "any" H = 6/12/24 only (the definition's scope).
3. Fit inputs pinned by acquisition cut-off A_fit (fetched_at filter before reconstruction); reconstruction time R_fit = floor_hour(filtered coverage_end); later revisions only in the test-stage reconstruction (D-027), recorded.
4. Operational blend history starts at the validation end (validation rows used for early stopping/Platt never enter w); M6c-1's train-end weights only for the replay.
5. Live export ships INACTIVE: it stores p_model / p_baseline only (no w, no blended p, no reserved-week label, no m12 metric) until the §A test is scored; then the seed is rebuilt and the human runs the switch (deploy).
6. Blend seed/live seam: pending rows retained and labelled later; live rows use the actual issue time τ_s.
7. Red-share rule evaluated as the displayed hourly forecast just before each onset; all windows anchored at the same τ; reserved week excluded.
8. M12 runs in two sessions: now (fit, export inactive, red-share check, versioned scorer, replay data) and after 2026-10-25 (test, seed rebuild, switch).

## For the human
- Score the frozen H = 1/3 M6c-1 models on the same new week too (a second test week for them)? Not in the agreed scope; the overlap rule would block it later on this week.
