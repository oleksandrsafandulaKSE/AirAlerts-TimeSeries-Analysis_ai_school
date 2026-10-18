# M11 — consensus record

- Outcome: **consensus**, 3 rounds. No escalation, no deadlock.
- Codex final verdict (round 3): `VERDICT: AGREE` — "No disguised rule change identified."

## PROVISIONAL decisions (Claude+Codex consensus, human to ratify)
1. Snapshots: first successful write in a UTC hour wins; τ ≥ hour + 15 min → `late`, not scored; legacy snapshots not scored; retention 35 days.
2. Live estimand: rows eligible BOTH as issued (state "forecast", no rejected caution) AND after reconciliation (not under a non-standing alert at τ); coverage continuous over [τ − 24 h, τ + 1 h]; SETTLE = 3 h.
3. Persistent `rejection_log` (35 days); any rejection for the unit at ≥ τ − 24 h excludes the row.
4. Live BSS pooled; null with reason for no rows / zero reference loss; 10 bins, p = 1 in the last.
5. "Neighbours under alert" on the panel = capped state (model definition); physical standing alerts listed separately.
6. Recent-pattern grid is descriptive (Kyiv-time 3-hour blocks, "no data" ≠ 0), code shared between test and page.
7. Not built: week-ahead blocks, duration, 24 h counts, red/yellow, UA translation, live H = 3.

## For the human
- Snapshot retention 35 days OK?
- Live H = 3 would need a new exported model (separate decision).
