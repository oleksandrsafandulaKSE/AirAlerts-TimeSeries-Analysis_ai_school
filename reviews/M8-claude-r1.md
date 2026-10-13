# Claude response, round 1 — plans/M8.md

## Changes made
- B1 forecast time — ESCALATED and decided by the human: forecast (τ, τ + 1 h] with inputs ≤ τ (τ = run time); recorded as a deliberate definition change (proposed D-032), labelled on the page.
- B2 reconciliation leakage — AGREE: records are versioned (first_seen_at, end_seen_at, end_source, history_reconciled_at); inputs at τ use only versions known at τ; truncation/replay tests + a negative control for a reconciled end not yet known.
- B3 missed short alerts — AGREE: per-unit `confirmed_through` from the rotating history endpoint; label-based inputs use only confirmed hours; unconfirmed = missing; a vanished-but-unreconciled id keeps an unknown end (D-027), never a guessed end; warming-up / gap states.
- B4 D-020 — AGREE: physical "alert running" (any age) separated from the capped "no forecast now" mask; standing-only units are forecast.
- A1 recipe pins — AGREE (§2). A2 unit mapping — AGREE: exact `api_oblast_name` match in regions.py; Kyiv City/Kyivska fixtures; union across levels.
- M1 tests — AGREE: DST and gap-edge fixtures on official data, boundary cases, truncation/replay, negative controls. M2 gap/outage rules — AGREE. M3 checks/diagnostics, parsed `updated_at` — AGREE. M4 failure status — AGREE: status stored separately; immediate greying.
- Q1 alert types — decided by the human: all types. Q2 dependencies — approved with exact pins. Q3 D-014 wording — ratified.

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL: poll every minute, 1 history request per run (≈ 24 min reconciliation cycle); warming-up threshold 90 min; real map replaces the tile map in the study section.

## Escalations
(none open)
