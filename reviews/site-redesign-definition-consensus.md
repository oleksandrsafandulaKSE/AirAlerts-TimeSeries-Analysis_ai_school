# Site-redesign definition — consensus record

- Outcome: **consensus, round 3** (after an escalation at round 2, resolved by the human: D-045 approved in chat
  2026-10-18). Every item RESOLVED or ACCEPTED.
- Codex round-3 verdict: `VERDICT: AGREE` — "None introduced by this round's approval record or cutover changes."
- Codex round-2 verdict: `VERDICT: CHANGES REQUIRED` — remaining: (1) D-045 is a rule amendment needing explicit human
  approval; (2) cutover dependency (fixed after round 2: scorer/storage versioning moved into M12, export inactive until
  then).

## Escalation (resolved: APPROVED by the human 2026-10-18)
- **D-045:** switch the main map's "any" target, masks, features, baseline and scorer to `alert_type == air_raid`, so the
  live inputs match the M6c-1 model. Amends D-040 ("the any map keeps all API alert types").

## PROVISIONAL decisions (Claude+Codex, human to ratify)
1. "If an alert starts, red or yellow?" = conditional on an "any" onset; simultaneous red+yellow → red; red escalation
   inside a running yellow is not counted; (t − 7 d, t] UTC; N = 0 and incomplete coverage shown as states.
2. Replay = labelled retrospective reconstruction from pinned M6c-1 artefacts; no new score.
3. Default new test week for H = 6/12/24: [2026-10-18, 2026-10-25), same fit/validation as M6c-1; horizon-scoped reservation.
4. Scorer and snapshots versioned by (model version, target, H); M12 cutover order as in the definition.

## Notes
- D-number collisions (D-040 twice; M10/M11 summaries used D-033/D-034) to renumber at ratification.
