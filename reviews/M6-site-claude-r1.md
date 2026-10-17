# M6-site — Claude, round 1 (answer to reviews/M6-site-codex-r1.md)

## Changes made
- B1 versioned levels — AGREE (live.mjs applies only `updated_at`-gated overwrites; no timestamp → replay leak). Plan §2:
  `levels = [[knownAt, level]]`, `levelAt(r, τ)`; the typed path selects its own records (first seen ≤ τ, end known at τ,
  `levelAt`, `alert_type`); `knownAt()` unchanged so "any" is untouched.
- B2 hover vs card — AGREE (template.html:356 `hover(p, o.tip(u))` = tooltip; :357 click/Enter → `onPick` → card). Plan §4:
  typed lines in the hover/focus tooltip AND the card (the card is the only way on a phone); pure functions
  `typedTipHtml`/`typedCardHtml`; test checks both are wired; browser check on the dev server.
- A1 N days — AGREE: from `levelCoverage` (typed), minus unresolved-level zones, start derived (no hard-coded date);
  the datastore is named, not counted.
- A2 null-level records — AGREE: a bounded raw hole [start, e) per unresolved record (e = end known at τ or start + 24 h),
  both levels; the existing hole rule excludes s with s + 1 h ≥ start and s < e + 24 h; state `data_gap` only while
  τ ∈ [start, e). Ends when backfilled or out of the windows.
- M1 truncation witnesses — AGREE: production `typedAt(full)` == `typedAt(truncated)` at three pinned witnesses
  (end known later, level backfilled later, coverage confirmed later) + oracle-state negative controls proving each
  witness is sensitive + the immature-window control.
- M2 more parity moments — PARTLY: added onset at τ and τ + 1 h, both 14-day window edges, 24 h cap ± 1 s. Hole edges and
  post-hole boundaries go to JS unit tests (typed holes are live-state constructs). DST / official gap: see Disagreements.
- M3 golden "any" — AGREE: golden produced by the pre-change code (git HEAD) over normal, migration, rejected-record and
  hole scenarios.
- M4 model contract — AGREE (partly enforceable now): `ctx` defined; reject trained_through + 1 h > τ, alert_types,
  horizon, out-of-range p/n/n0; out-of-sample w* requirement stated in the contract + hand-over note.

## Disagreements
- B3 "no commits by Claude" (D-026) — PARTLY. The rule stands for the loop; this milestone was started by the human's
  session with the explicit instruction "Commit on your own branch. Do not open a PR, do not merge … the human
  deploys". Plan keeps one branch commit, nothing on main, no PR. Not a plan-design matter; flagged in the summary.
- M2 DST + gap fixtures — PARTLY: the API dump spans 12 Sep–12 Oct 2026 (no DST switch; next is 25 Oct) and the
  official data has no `alert_level`, so there is no real typed data at those edges; the typed baseline has no calendar
  input. Synthetic hole edges are tested in JS.
- Q1 air_raid only — not a blocker: M8's "all types" decision is for the "any" target; M6-definition defines types by
  `alert_level` and its numbers were computed on air_raid (plans/M6-definition.md "Facts … air_raid"). Kept PROVISIONAL,
  enforced by the model contract, and listed for the human.
- Q2 milestone order — the human's session started this milestone now, explicitly baseline-only ("Until a model exists,
  the blend weight is w = 0"). No order change by the loop.

## Design decisions taken (PROVISIONAL)
- P1 typed alert types = air_raid only.
- P2 versioned levels; unknown level stored as null, never a rejection.
- P3 `levelCoverage` only from history calls made by the new code; an old store starts without typed coverage.
- P4 unresolved-level record → bounded typed hole for both levels.
- P5 N days = ∩ of typed coverage over 24 units minus unresolved zones; start derived.
- P6 typed details in tooltip + card only; map/legend/list/table unchanged.
- P7 monthly chart contract `netlify/live/data/typed_monthly.json` (schema 1, empty), served in the same GET payload.
- P8 typed model plug-in contract with the rejections above.

## Escalations
(none)
