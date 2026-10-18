# M13 — consensus record

- Outcome: **consensus**, 4 rounds. No escalation, no deadlock.
- Codex final verdict (round 4): `VERDICT: AGREE` — "None introduced by the round-three changes."

## PROVISIONAL decisions (Claude+Codex consensus, human to ratify)
1. `forecast.m12_state` always written; fatal registry failure → explicit "new model unavailable", never a silent M8 fallback; an item failure disables only that horizon / the yellow-red line.
2. 7-day strip: mixed, model-labelled segments (M12 where active snapshots exist, M8 before), each against the observations its model forecasts (air-raid only for M12).
3. Kind wording: > 0.5 likely red, < 0.5 likely yellow, = 0.5 equal; "no alerts here in 7 days" only when no onset was observed; "alert kinds not known yet" when onsets exist but none is classified.
4. Kind national share pooled over fully covered units; unresolved-level onsets excluded from R and N and reported.
5. Replay running BSS = 1 − SSE_blend/SSE_rule on identical rows, labelled retrospective.
6. Testing the active state with a dev-server-only activation fixture (never committed active).
