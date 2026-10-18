# M10 — consensus record

- Outcome: **consensus**, 3 rounds. No escalation, no deadlock.
- Codex final verdict (round 3): `VERDICT: AGREE` — "None introduced by these revisions."

## PROVISIONAL decisions (Claude+Codex consensus, human to ratify)
1. L1 label variant = drop hromada-level rows before the union; a proxy for non-air-raid rows, measurement only (the target is unchanged).
2. A2 onset accounting: exact-instant matching; L0 onsets kept / shifted / disappeared, L1 onsets matched / shift target / new, with invariants.
3. Group rates pool numerators and denominators; never average unit ratios.
4. Each variant uses its own grid, labels, offset (causal expanding prior) and D-025 reporting baseline (p_unit from that fold's fit rows, frozen).
5. Recency weights 0.5^(age/h), h ∈ {∞, 730, 365, 182}, fit rows only, chosen on the 4 M7 folds with the M7 rule; ties → longer half-life.
6. Exposure block D (hours under alert 3 h / 24 h / 7 d, capped and clipped at t) accepted only by the same rule.
7. Stability slices: Monday-UTC weeks; Kyiv day 06:00–21:59 / night 22:00–05:59.

## For the human (not decided by the loop)
- Label source: scrape @air_alert_ua to label every row by message type (new source), or keep L1 as a proxy?
- Change the target to air-raid-only for a future run if §A shows a large effect (rule change)?
- §E post-hoc test rows: gated on a human-written `reports/m10/posthoc_approval.json`.
- Re-export the live model if §B/§C is accepted?
