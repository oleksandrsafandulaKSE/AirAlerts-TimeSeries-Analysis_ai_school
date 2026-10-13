# Claude response, round 1 — plans/M5.md

## Changes made
- B1 Streamlit — AGREE: REQUIRED (ROADMAP M5, D-012); minimal app reading only reports/, smoke test.
- B2 figures — PARTLY: README figures are ONLY PNGs written by run_all.py (reliability plots for H = 1, H = 3, new regime, validation). build_site.py makes no figure files; the site draws charts in the browser from the same saved CSV values. This satisfies "every figure comes from a reports/<run>/ file produced by run_all.py" without changing run_all.py after the final test (code fingerprint).
- B3 string match — AGREE: README result numbers live only in GENERATED blocks written from exact source keys; tests compare cell-by-cell by key, regenerate the README blocks exactly, run swap mutations (predictors, groups, horizons, metric columns), and reject decimal numbers in hand-written prose.
- A1 method precision — AGREE (§3.6). A2 gap/coverage — AGREE: detected vs approved vs masked envelope per horizon, eligible/excluded counts shown. A3 null + reasons — AGREE. A5 offline — AGREE: data embedded inline.
- A4 calibrated persistence "state" — PARTLY: no rule conflict; CLAUDE.md says "P(onset | state at t)" and D-025 defines the implemented state as minutes_since_last_end bins; the site/README state this explicitly.
- M1 leakage evidence table — AGREE (check | PASS/FAIL | evidence from an actual pytest run; "tested at these cases" wording).
- M2 Kyiv City/Kyivska presentation check — AGREE (test against regions.py).
- M3 summary, decision entry, consensus record — AGREE (§9).

## Disagreements
- Q (Netlify): deployment needs the human's Netlify login; the CLI here is not authenticated and the builder must not enter credentials. This is an external blocker, not a rule change: done-criterion = verified URL if authenticated, else OUTSTANDING with the exact command. The private claude.ai preview is an addition, not a substitute.

## Design decisions taken
- PROVISIONAL: static self-contained site + required local Streamlit; inline SVG/vanilla JS; private claude.ai preview.

## Escalations
(none)
