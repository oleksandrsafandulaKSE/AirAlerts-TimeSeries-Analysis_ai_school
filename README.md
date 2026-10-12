# Air-raid alert onset forecasting — Ukraine

> For each oblast and each hour: the probability that a NEW air-raid alert starts within the
> next hour, using only what is known at that moment. Tested once on the last 6 weeks of
> official data against simple baselines, with a test that proves no future information is used.

## Problem framing
- **Why "a new alert starts" and not "an alert is active":** being under alert at t almost
  guarantees being under alert at t+1h, so "active" targets reward persistence and give
  inflated scores (PR-AUC 0.8–0.9 in some public projects). We predict onsets only. Hours
  already under alert are excluded from training and testing.
- **Why oblast level:** that's how people experience alerts and how the groups compare
  (Kyiv City / frontline / rear). Since the 2025 admin reform alerts are issued per raion or
  hromada, so an oblast counts as under alert if any non-standing alert anywhere in it is active.
- **Why probabilities:** a forecast is only useful if "20%" means 20%. Calibration is
  measured (Brier score, reliability plots), not assumed.

## Data
- **Main source:** Vadimkin/ukrainian-air-raid-sirens-dataset, `official_data_en.csv`,
  downloaded at run time. Mar 2022 → **7 Sep 2026**, when the official export stopped.
- **Issues found in the data** (evidence in `DECISIONS.md`):
  - **Duplicates:** 113,845 of 299,275 rows (38%) are exact duplicates and are removed first.
  - **2025 admin reform:** alerts moved to raion/hromada level, so using oblast-level rows alone
    makes the target collapse (the v1 bug). All levels are merged per oblast instead (D-002).
  - **Standing alerts:** some hromada alerts last months (up to 604 days) and would mark a whole
    oblast as permanently under alert. An alert therefore counts as "under alert" only for its first
    24 hours, which is known at t without its end time; its start still counts as an onset (D-020).
  - **Recording gap 29 Aug–2 Sep 2026:** no rows for three days. Treated as missing, not as calm:
    those hours are left out of scoring, and features reading across the gap are marked missing (D-013).
  - **Excluded units:** Luhanska (permanent alert since 2022) is excluded, and Crimea is not in
    the data. That leaves 24 units (D-008).
  - **Exactly-30-minute alerts:** 38 alerts (after deduplication) last exactly 30 minutes, which may be imputed end
    times. They are kept and counted (D-010).
- **New system since September 2026:** yellow = drones, red = missiles. Before September, any
  attack triggered the single alert. A one-month history from the alerts.in.ua API is used only
  for the exploratory section and is never mixed with the official data (D-007).

## Method
- **Grid and target:** an hourly UTC grid for the 24 units, 2022-03-23 → 2026-09-07. The target y(t) = 1
  if a new merged alert interval starts in (t, t+1h]. Hours under alert at t are masked.
- **Features**, all computed from data with timestamp ≤ t:
  - time since the last alert started and ended;
  - alerts in the last 24h and 7d;
  - neighbouring oblasts under alert, from a fixed border table;
  - national active count;
  - hour and weekday in Kyiv time.
- **Baselines:**
  - hour × weekday climatology from train;
  - **rolling 14-day recent rate**, the main bar to beat. It updates through the test, using only
    labels already known at t;
  - raw persistence;
  - calibrated persistence, binned by time since the last alert ended.
- **Model:** one LightGBM model across all units, early-stopped on the validation slice, with no
  refit. Calibration is checked on validation.
- **Splits:**
  - train = all history up to 2026-06-29;
  - validation = 29 Jun–27 Jul 2026;
  - **final test = 27 Jul–7 Sep 2026, scored once**, for the model and all baselines together.
  - Training rows whose label window crosses a cut-off are purged.
- **Metrics:**
  - **Primary: Brier skill score against the rolling recent-rate baseline.**
  - Secondary: Brier score, ROC-AUC (pooled and within-oblast), PR-AUC and PR-AUC divided by the
    base rate, plus the overall reliability plot.
  - All are reported overall and per group: Kyiv City / frontline (8 oblasts) / rear (15 oblasts).

## No-leakage guarantee
A truncation test cuts the **raw** data at a forecast time t, as if it were the moment of
forecasting: alerts starting after t are dropped, and end times after t are cleared. All
preprocessing and features are then rebuilt, and the test checks that every feature at t is
unchanged. It covers many times, including active alerts, standing alerts, cut-offs, the gap
edges and DST switches. A deliberately leaky feature is included as a control. The test must
catch it, which proves the test can actually fail.

## Results
Final-test results (27 Jul–7 Sep 2026) are in `reports/official/`:
- `metrics.csv`: the model vs the four baselines, overall and per group;
- `reliability.png`: the overall reliability plot.

The headline is Brier skill against the rolling recent-rate baseline. Not beating that baseline
is a valid result and is reported as such.

## New alert system (Sept–Oct 2026, exploratory)
- **Measured** (official 27 Jul–28 Aug vs API 13 Sep–11 Oct; alerts per month / share of time under alert):

| Unit | Before | After |
|---|---|---|
| Kyiv City | 90 / 11% | 212 / 33% |
| Kyivska | 121 / 20% | 237 / 69% |
| Zhytomyrska | 58 / 6% | 225 / 34% |
| Kharkivska (frontline) | 147 / 93% | 217 / 92% |
| Donetska (frontline) | 57 / 57% | 57 / 52% |

- **Also measured:**
  - 83% of new alerts now start yellow.
  - 36% of red alerts start while a yellow alert is already active.
- **Hypothesis (not confirmed):** the threat concept is the same, but yellow is declared much more
  widely. Seasonal effects and the change of data source can't be fully separated from this.
- **Transfer test:** the model trained before the reform is scored on the new data. Results are in
  `reports/new_regime/`: within-oblast AUC, and mean predicted vs observed rate per group.
- **Conclusion depends on that test:** if transfer fails, the model needs retraining or
  recalibration before it can be used under the new system.

## Limitations
- No text, Telegram or weather features.
- A single horizon (1 hour).
- No hyperparameter search.
- The test period is short (6 weeks).
- The rolling baseline adapts during the test while the frozen model doesn't.
- The new-regime data has a different source and only one month of history.
- Comparing before and after the reform can't fully separate the reform from seasonal effects.

## Future work
An automated data workflow (GitHub Actions): daily API collection and monthly re-evaluation
(D-016). Weekly refit inside the test window (D-014).

## Previous attempt
v1 (previous selection round): <https://github.com/oleksandrsafandulaKSE/AirAlerts-TimeSeries-Analysis-Ukraine>.
What was wrong and why this version is better: see `DECISIONS.md` (D-001 – D-006).

## How to run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_all.py --config official
pytest -q
```
