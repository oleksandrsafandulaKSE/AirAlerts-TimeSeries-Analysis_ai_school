# M1c — exactly-1-hour durations: count, print, raising check

**SUPERSEDED (2026-10-17) by `plans/M9.md` §A — human chose option A (check outside the fingerprinted code).**

Human decision (2026-10-17, chat): **Option 1** from `plans/notes/fabricated_1h_ends.md`. Keep the alerts as they
are, document the counts in the README and the M1 printing, and add a raising check on the exactly-3600 s count.
No change to the target, mask, features, models, the evaluation protocol or any reported metric.

## Goal
Make the parser artefact (a missing all-clear is closed at `started_at + 1h`) visible and pinned. If the file
changes, the run fails rather than silently shifting the count.

## Files to touch
1. `src/config.py`: new field `expected_exact_1h_rows: int | None = None`. `official()` and `official_h3()`
   set it to **255** (the measured count after dedup and the Luhanska exclusion).
2. `src/data.py`:
   - **`load_official`:** after parsing, count the rows with `finished_at - started_at == 3600 s` exactly.
     - Print `[data] exactly-1h durations (parser-imputed ends, kept as-is): N`.
     - Store `stats["exact_1h_rows"]`.
     - Raise `DataQualityError` if `cfg.expected_exact_1h_rows` is set and differs.
     - The count runs on the deduplicated rows with Luhanska excluded, the same rows the shared format returns.
   - **`alert_counts`** (printed-only diagnostics): add `exactly_1h_total` and `exactly_1h_by_level`, the same
     pattern as the existing 30-minute entries.
3. `scripts/run_all.py`, M1 block: one print line after the 30-min line. It reads `alert_counts` on alerts
   starting before the test, like every other M1 diagnostic.
4. `README.md`, Data section: one bullet with the mechanism, the counts, the sensitivity (test Brier skill
   −0.0101 → −0.0108 excluding the 93 affected rows) and a link to the note. The GENERATED `data_facts` block
   and `scripts/build_site.py` are NOT touched.
5. Tests, `tests/test_data.py`:
   - (a) `alert_counts` counts an exact-3600 s row and not a 3599 s or 3601 s row.
   - (b) `load_official` raises when the expected count differs.
   - (c) `load_official` passes when it matches, and `stats["exact_1h_rows"]` is set.
   - (d) No check runs when the expected count is `None`.
   - The `cfg_for` helper, and the matching helper in `tests/test_run_all.py`, pass the count explicitly, so
     existing tests keep building their own small CSVs.

## Approach and invariants
- **Whole-file count, like the duplicate checks.** The count is a data-quality check, not a model input, so
  counting it over the whole file (including the test period) does not break "no test statistics" (the same
  is true of the existing duplicate-count check).
- **Nothing downstream reads it.** Grid, features, labels and scores are byte-identical.
- **How this is checked:** the full `pytest -q` passes, and `run_all.py --config official` prints the same
  shapes, base rates and metrics as before.

## Testing
`pytest -q`, then `scripts/run_all.py --config official` to confirm that the check passes on the real file (255)
and that M1–M4 numbers are unchanged.

## Risks / assumptions
- **Upstream changes:** the upstream file is frozen (D-007), so 255 should be stable. If Vadimkin re-exports it,
  the run fails on purpose, like the duplicate count.
- **Genuine 1-hour alerts:** about 16 of the 255 are probably genuine. The check counts durations, not intent,
  and the README says so.

## Open questions
None. The design is the human's.
