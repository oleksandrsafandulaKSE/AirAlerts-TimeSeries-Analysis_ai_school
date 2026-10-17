# M6-site — consensus record

Outcome: **consensus** after 4 Codex rounds (rounds 3 and 4 each needed a second attempt: the wrapper failed with
"tcgetattr/ioctl: Operation not supported on socket" before Codex ran; logs kept as `*-failed-attempt.log`).

Codex final verdict (reviews/M6-site-codex-r4.md), verbatim: `VERDICT: AGREE`
("None introduces an additional change to CLAUDE.md or existing DECISIONS.md rules.")

## Human ratification (chat, 2026-10-18)
- P2–P8: **approved** ("approve p2-p8").
- P1 (alert types for yellow/red): **open**. The human asked to check it against M10 (non-air-raid rows); findings in
  plans/M6-site.md "Open questions for the human".
- Levels changed in place by the API: **keep the latest version** (the current behaviour).
- D-040 entry: **yes** (reviews/PROPOSED-DECISIONS-M6.md).

## PROVISIONAL (Claude+Codex consensus, human to ratify)
- P1 Typed targets count the same alert types as M8's approved "any" target (all API types; one list). Red therefore
  includes artillery-shelling alerts marked red. Air-raid only is a question for the human (a target change).
- P2 `alert_level` stored as timestamped versions (`levels = [[knownAt, level]]`); an unknown level is stored as null,
  never a rejection (the "any" forecast never needs it).
- P3 Typed coverage `levelCoverage` comes only from history calls made by the new code (an old store starts without it;
  a rebuilt seed has it for the dump window).
- P4 A record whose level is unknown at τ is a bounded typed hole [start, min(end, start + 24 h)) for both levels.
- P5 "Collecting data: N days" = intersection of typed coverage over the 24 units minus unresolved zones; start derived.
- P6 Typed details only in the oblast tooltip (hover/focus) and the oblast card (click/tap); map, legend, top list and
  table unchanged.
- P7 Monthly chart contract: `netlify/live/data/typed_monthly.json` (schema 1, empty), served in the same GET payload.
- P8 Typed model plug-in = a list of versions with `available_at`, causally selected; checks on alert types, horizon,
  trained_through, p range; out-of-sample w* is the model milestone's job.

## Accepted disagreements
- B3: D-026 "no commits by Claude" vs the task brief "Commit on your own branch" → one branch commit, no PR, no merge.
- M2: no typed DST / official-gap fixtures (API dump has no DST switch; official data has no levels).

## Escalations / unresolved
(none)
