# Claude response, round 2 — plans/M5.md

## Changes made
- B1 stale headings — AGREE: title and §6 heading now say Streamlit is required.
- B2 — AGREE: §9 no longer mentions reports/figures; build_site writes no figure files.
- B3 — AGREE: README generated tables are parsed into (row label, column label, value) cells and each cell is verified independently against the source file at the key named by its labels; swap mutations are applied to the README path; hand-written sections reject result numbers in every format (decimals, integers ≥ 10 not on an allow-list of dates/years/D-numbers/H values, percentages).
- A5 — AGREE: the smoke check parses the EMBEDDED payload and renders from a file:// URL and over http; no data.json.
- Provisional-decision note — AGREE: the CDN alternative is removed (inline SVG + vanilla JS only, no network requests).

## Disagreements
(none)

## Design decisions taken
- PROVISIONAL (unchanged): static self-contained site + required local Streamlit; inline SVG/vanilla JS; private claude.ai preview (supplementary; Netlify deployment stays OUTSTANDING until a URL is verified).

## Escalations
(none)
