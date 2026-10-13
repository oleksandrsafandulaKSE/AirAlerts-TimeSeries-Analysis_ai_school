# Consensus record — plans/M8.md (D-026 loop)

- **Outcome:** CONSENSUS after 5 rounds. Escalations decided by the human in chat (2026-10-13): forecast period = next
  60 minutes from the update; all API alert types; dependencies @netlify/functions@2.8.2 + @netlify/blobs@8.1.0;
  D-014 wording ratified; live-mode exception: the ACTIVE-poll record may stand in for the unconfirmed tail (≤ ~25 min)
  for EVENT inputs only (labels strictly history-confirmed).
- **Codex's final verdict (round 5, verbatim):** "None introduced by the round-four changes. The revised uncertainty rules
  address both parts of the remaining leakage-audit concern." — `VERDICT: AGREE`

## Issues the loop fixed
Forecast-time leakage (inputs ≤ τ); versioned records so later reconciliation can't leak; history-confirmed coverage as
disjoint intervals with holes; hole propagation identical to the official gap (extended 24 h zone for state, onset
windows, time-since, labels; national/neighbour inputs across all involved units); physical alert status separated from
the D-020 mask; exact training pins and offset definition; exact unit mapping incl. Kyiv City/Kyivska and deliberate
exclusions; status delivered with the forecast and greying within 60 s; header wording for all alert types.

## PROVISIONAL design decisions (human to ratify)
1-minute polling with 1 history call per run; "data gap" states; the real map replaces the tile map in the study section.
