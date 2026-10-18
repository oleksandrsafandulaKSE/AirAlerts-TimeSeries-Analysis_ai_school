# Fabricated 1-hour alert ends in the official data

Analysis only, 2026-10-17. No rule, feature, model or report was changed. D-010 and D-020 are Oleksandr's
decision; this note gives the measurements and the options.

Reproduce from the repo root (writes intermediate CSVs to the gitignored `data/derived/fake1h/`):

```bash
.venv/bin/python plans/notes/fabricated_1h_ends/analyze.py
```

```bash
.venv/bin/python plans/notes/fabricated_1h_ends/followup.py
```

All counts are after deduplication (185,430 rows) with Luhanska excluded (185,429 alerts), on the local
`data/official_data_en.csv`.

## Mechanism (from the parser source)

In the dataset's parser (`processors/official_channel_processor.py`, lines 132–138), when a new alert starts for
a location L, and L still has an alert with no all-clear that started more than 3 hours before, the old alert is
written with `finished_at = started_at + 1h`. If the new start comes within 3 hours, the old alert is overwritten
and never written at all.

So a fake end at E means:
- no all-clear was ever sent for that alert;
- the next alert at the same location starts after E + 2h;
- the end is only written when that next start arrives, so before then it is future information.

## Measured facts

| Check | Result | Script |
|---|---|---|
| Durations of exactly 3600 s | **255**, vs 16.1 expected per second from the other 59–61 min durations, so **≈239 excess** | analyze §1 |
| Neighbouring seconds | 3598: 25, 3599: 23, 3601: 14, 3602: 15 (no spike) | analyze §1 |
| By year | 2022: 10, 2023: 17, 2024: 32, 2025: 48, **2026: 148** | analyze §1 |
| By level | hromada 109, raion 87, oblast 59 | analyze §1 |
| By oblast (top) | Dnipropetrovska 67, Zaporizka 59, Odeska 19, Kharkivska 14, Khersonska 12 | analyze §1 |
| Next same-location start > 3h after start | **97.3%** for exactly-3600 s, vs 53.1% for other 59–61 min alerts | analyze §2 |
| Exactly-3600 s alerts that break the rule (next start ≤ 3h) | 7, consistent with the ≈16 that are genuine | analyze §2 |
| Fake ends that are also the end of the oblast's merged interval (D-020 union) | **106 / 255**; the rest are covered by other alerts in the same oblast | analyze §3 |
| For those 106, time to next oblast onset | median 9.0 h; within 1 h: 5.7%; within 2 h: 10.4% | analyze §3 |
| Phantom-clear oblast-hours, whole history (data says clear, but without the fake end the alert would still count as active under D-020) | **1,656** | analyze §3 |
| Of those, hours where the fake end was not yet written at t | **987 (59.6%)** | followup |
| Phantom-clear rows among scored **validation** rows | **0** of 11,160 | analyze §4 |
| Phantom-clear rows among scored **test** rows | **93** of 13,116 (0.71%), 21 positives; Cherkaska 23, Kyivska 22, Chernihivska 17, Khersonska 17, Mykolaivska 14 | analyze §4 |
| … of which the fake end was not yet written at t | 48 | followup |
| Onset rate on those 93 test rows | 0.226, vs 0.139 on all scored test rows | analyze §4 |
| Test Brier skill vs recent-rate, all scored rows | −0.0101 (unchanged headline) | followup |
| … excluding the 93 phantom rows (post-hoc sensitivity, no refit) | **−0.0108** | followup |
| Fake-end alerts by split (by start time) | train 147, val 24, test 84 | analyze §4 |
| D-010 side check: exactly-1800 s durations | 38, vs 51.3 per second nearby: **no spike**, so the 30-minute durations are not a parser artefact | followup |

## What this means

- **Is it a rule break?** Yes, formally. For 59.6% of affected hours, features and the at-risk mask use an end
  time that was not written by t. CLAUDE.md forbids "alert end times not yet observed at t", and the D-020 cap
  doesn't catch this because the alert has a recorded end of under 24 h.
- **Does it change the score?** Barely. Validation is untouched. On test, dropping the 93 affected rows moves
  Brier skill vs recent-rate from −0.0101 to −0.0108. The conclusion "does not beat recent-rate" stands either way.
- **What kind of error is it?** At oblast level these rows are not easy negatives. Their onset rate (0.226) is
  higher than the test average, so the effect is a few rows that a real-time forecaster would have masked as
  under alert. It is not a quiet period the model could exploit.
- **Hypothesis (not tested):** fake ends cluster in busy periods, when the Telegram channel skips all-clears.
  That would explain the rise to 148 in 2026 and the concentration in Dnipropetrovska and Zaporizka.
- **Not measurable from the file:** alerts silently overwritten when the next start came within 3 h, and messages
  dropped for unknown hashtags. The onset count is a lower bound by an unknown amount.

## Options for Oleksandr (no recommendation that changes a rule)

1. **Keep as is and document.** Add the counts above to the README data-quality section and to M1 printing.
   Cheapest, and justified by the −0.0101 → −0.0108 sensitivity, but the formal rule break stays.
2. **Flag and treat as end-unknown.** In `load_official`, set `finished_at` to empty for exactly-3600 s alerts
   whose next same-location start is more than 3 h after their start. D-020 then treats them as open, active
   for 24 h from start. This is closest to what a real-time observer saw: no all-clear. About 16 genuine
   1-hour alerts would also be capped, but the next-start test already excludes the 7 obvious ones. This needs
   a D-020/D-010 amendment, a leakage-test case, and a re-run of M1–M4. The final test was already scored once,
   so the re-run would be a post-hoc row, not a new headline.
3. **Start-only features.** Drop `minutes_since_last_end`, and build the mask from starts plus the 24 h cap
   alone. This removes all end-time dependence (the cohort repo ceo-of-second-hand did this), but discards real
   all-clear information for every oblast. It is a larger protocol change.
4. **Sensitivity row only.** Report the "excluding phantom rows" figure next to the headline, labelled
   post-hoc. No pipeline change.

Whichever option is chosen, a raising data-quality check would keep the count visible: print the exactly-3600 s
count in M1 and fail if it moves away from a recorded expected value, like `expected_duplicate_rows`.
