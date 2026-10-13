# Consensus record — plans/M5.md (D-026 loop)

- **Outcome:** CONSENSUS after 4 rounds. The human was asleep and had delegated decisions to the Claude–Codex loop
  ("you and codex decide ... implement m4 and m5, create a great visual, host on netlify, don't commit").
- **Codex's final verdict (round 4, verbatim):** "Hosting remains explicitly OUTSTANDING until a deployed Netlify URL is verified." … `VERDICT: AGREE`

## Issues the loop fixed
- Round 1: Streamlit is REQUIRED (ROADMAP M5, D-012), not optional; README figures only from run_all.py PNGs; README
  numbers only in generated blocks with per-cell source verification and swap mutations; precise method text; gap /
  coverage per horizon; nulls with reasons; offline embedded data; leakage evidence table; Kyiv City/Kyivska check.
- Round 2: stale `reports/figures/` and `data.json` mentions removed; README cells verified independently by label.
- Round 3: hand-written prose may contain no result number in any format (allow-list of rule constants and dates;
  mutations with 0/1/7/9 must fail).

## PROVISIONAL design decisions (Claude+Codex consensus, human to ratify)
1. Static, self-contained results site (inline SVG + vanilla JS, embedded data, no network requests) + a REQUIRED local
   Streamlit app reading only reports/.
2. A private claude.ai preview of the same page as a supplement.
3. Netlify: deployed only if the CLI is already authenticated; otherwise OUTSTANDING with the exact command.

## Escalations
None.
