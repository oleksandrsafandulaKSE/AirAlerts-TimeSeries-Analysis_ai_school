# Consensus record — plans/M7.md (D-026 loop)

- **Outcome:** CONSENSUS after 5 rounds (the maximum).
- **Codex's final verdict (round 5, verbatim):** "None introduced by the round-4 change. Plan agreement does not establish implementation correctness; the specified leakage and reproduction checks remain required." — `VERDICT: AGREE`

## Issues the loop fixed
- R1: offset inference fully specified (train/val/test offsets, clipping, save/reload, zero-residual oracle); the shrink
  prior made CAUSAL (expanding rate up to t − H) so backtest folds and early rows cannot see later outcomes; identical
  scoring keys for every comparison; precise greedy acceptance rule; exact feature definitions (UTC "yesterday", Kyiv
  hour ±1 with wraparound, DST); boundaries t + H ≤ end; pinned negative-control witnesses and hand fixtures.
- R2–R3: label-based rates defined as k = sum(y), n = count(y) over eligible mature rows (binary label); unit rates
  shrunk, prior/national rates pooled unshrunk; the human-approved exceptions recorded explicitly.
- R4: the reporting baseline for "skill vs recent rate" stays the unchanged D-025 baseline with the frozen train p_unit.

## Human-approved exceptions (recorded, proposed D-030)
1. Post-hoc scoring of labelled M7 rows on the already-seen test (the headline is unchanged).
2. M7 inputs that read earlier test LABELS (s ≤ t − H only): block A rates, the V2 offset, the weekly refit.

## PROVISIONAL design decisions (Claude+Codex, human to ratify)
Fold cut-offs 2025-07-01 / 10-01 / 2026-01-01 / 04-01 and the ≥ 0.5 % relative, ≥ 3-of-4-folds acceptance rule; causal
expanding prior; V5 blends V3 with the recent rate; H = 1 only; no dedicated frontline model (reported as low-n).

## Escalations
None.
