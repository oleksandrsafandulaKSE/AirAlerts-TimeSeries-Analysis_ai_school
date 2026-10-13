# Claude response, round 2 — plans/M8.md

## Changes made
- B3 — AGREE: coverage is a list of confirmed intervals per unit; a history call confirms [c − 30 d, c) only when contiguous with the previous interval; anything else stays a HOLE (incl. outages > 30 days, unrecoverable).
- M1 — AGREE: the negative-control witness is an immature label hour τ − H < s ≤ τ with an onset in (s, s + H]; the real offset equals its truncated value there.
- M2 — AGREE: explicit hole propagation: label inputs exclude holes; own windows unknown if they touch a hole; time-since unknown if the last event could lie in a hole; national/neighbour inputs unknown if any involved unit has a hole in the window; any unknown input → "data gap", no probability; holes clear on backfill or when they leave every window; a failed poll > 5 min is a national hole.
- M4 — AGREE: the GET function returns {status, forecast} in one payload; the page polls every 60 s and greys at that fetch; tested end to end.
- NEW exclusions — AGREE: Luhanska/Crimea/Sevastopol recognised via EXCLUDED_API_NAMES in regions.py, skipped and counted before unknown names raise.
- NEW header — AGREE: "Chance of a new alert in the next 60 minutes — any alert type: air raid, artillery shelling or street fighting".
- NEW interval wording — AGREE: every minute throughout.
- Added §9 limitation: alerts shorter than the poll spacing appear only after the unit's next reconciliation.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): 1-min polling + 1 history call per run; warming-up / data-gap states; real map replaces the tile map in the study section.

## Escalations
(none)
