"""M7 inputs (plans/M7.md §2.1, §3, §5): hand-checked values, edges, DST, gap NaN, offset oracle."""
import numpy as np
import pandas as pd
import pytest

from improve import features_plus as FP, model_plus as MP
from src import grid

H = pd.Timedelta(hours=1)


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def toy_grid(units=("A", "B"), start="2024-01-01 00:00", hours=24 * 40, y_fn=None, mask_fn=None):
    t = pd.date_range(ts(start), periods=hours, freq="h")
    rows = []
    for u in units:
        for i, x in enumerate(t):
            rows.append({"unit": u, "t": x, "group": "rear", "mask": mask_fn(u, i) if mask_fn else 0,
                         "y": float(y_fn(u, i)) if y_fn else 0.0})
    return pd.DataFrame(rows)


def at(df, u, t, col):
    return df.set_index(["unit", "t"]).loc[(u, ts(t)), col]


def test_rates_by_hand():
    # unit A: label 1 every 10th hour; unit B: never. Day 15 00:00 = index 336.
    g = toy_grid(y_fn=lambda u, i: (u == "A" and i % 10 == 0))
    r = FP.label_rates(g, H)
    t = "2024-01-15 00:00"                    # index 336; window [t-14d, t-1h] = indices 0..335 -> 336 rows
    kA = sum(1 for i in range(0, 336) if i % 10 == 0)          # 34
    qA = kA / 336                                                # expanding prior = same rows here
    assert at(r, "A", t, "rate_14d") == pytest.approx((kA + 10 * qA) / (336 + 10))
    assert at(r, "B", t, "rate_14d") == pytest.approx(0.0)       # q_B = 0, k = 0
    assert at(r, "A", t, "national_rate_14d") == pytest.approx(kA / (2 * 336))
    assert np.isnan(at(r, "A", "2024-01-14 23:00", "rate_14d"))  # window starts before the grid
    assert np.isnan(at(r, "A", t, "rate_30d"))                   # 30 d not available yet


def test_rates_use_only_mature_eligible_labels():
    g = toy_grid(y_fn=lambda u, i: (u == "A" and i % 10 == 0))
    base = FP.label_rates(g, H)
    t_idx = 400
    g2 = g.copy()
    later = g2["t"] > ts("2024-01-01") + pd.Timedelta(hours=t_idx - 1)   # labels of s > t - H
    g2.loc[later, "y"] = 1 - g2.loc[later, "y"]
    r2 = FP.label_rates(g2, H)
    t = (ts("2024-01-01") + pd.Timedelta(hours=t_idx)).strftime("%Y-%m-%d %H:%M")
    for c in ("rate_14d", "national_rate_14d", "prior_q"):
        assert at(base, "A", t, c) == at(r2, "A", t, c)
    g3 = g.copy()
    g3.loc[(g3.unit == "A") & (g3.t == ts(t) - H), "y"] = 1 - g3.loc[(g3.unit == "A") & (g3.t == ts(t) - H), "y"]
    assert at(FP.label_rates(g3, H), "A", t, "rate_14d") != at(base, "A", t, "rate_14d")   # s = t - H counts
    g4 = g.copy()
    g4.loc[(g4.unit == "A") & (g4.t == ts(t) - 2 * H), ["mask", "y"]] = [1, 1.0]          # masked rows ignored
    g4.loc[(g4.unit == "A") & (g4.t == ts(t) - 2 * H), "y"] = 1.0
    b4 = FP.label_rates(g4, H)
    ref = g.copy()
    ref.loc[(ref.unit == "A") & (ref.t == ts(t) - 2 * H), "mask"] = 1
    assert at(b4, "A", t, "rate_14d") == pytest.approx(at(FP.label_rates(ref, H), "A", t, "rate_14d"))


def test_gap_zone_nan_rates():
    g = toy_grid(hours=24 * 60)
    zone = ((ts("2024-02-10"), ts("2024-02-12")),)
    r = FP.label_rates(g, H, zone)
    assert not np.isnan(at(r, "A", "2024-02-09 23:00", "rate_14d"))
    assert np.isnan(at(r, "A", "2024-02-10 00:00", "rate_14d"))
    assert np.isnan(at(r, "A", "2024-02-25 23:00", "rate_14d"))      # u1 + 14 d - 1 h
    assert not np.isnan(at(r, "A", "2024-02-26 00:00", "rate_14d"))


def alerts(rows):
    df = pd.DataFrame([{"source": "t", "alert_id": str(i), "unit": u, "level": "oblast", "started_at": ts(s),
                        "finished_at": ts(e) if e else pd.NaT, "alert_level": ""} for i, (u, s, e) in enumerate(rows)])
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


NB = {"kyiv_city": {"kyivska"}, "kyivska": {"kyiv_city"}, "kharkivska": set()}


def ev(rows, start="2025-03-25 00:00", hours=24 * 10, zones=()):
    g = toy_grid(units=("kyiv_city", "kyivska", "kharkivska"), start=start, hours=hours)
    return FP.event_features(alerts(rows), g, zones=zones, neighbours=NB)


def test_wave_and_neighbour_counts():
    rows = [("kharkivska", "2025-03-26 09:10", "2025-03-26 09:40"),     # frontline
            ("kyivska", "2025-03-26 11:20", "2025-03-26 11:50"),
            ("kyiv_city", "2025-03-26 11:50", "2025-03-26 12:20")]
    f = ev(rows)
    t = "2025-03-26 12:00"
    assert at(f, "kyiv_city", t, "national_onsets_1h") == 2           # 11:20, 11:50 in (11:00, 12:00]
    assert at(f, "kyiv_city", t, "national_onsets_3h") == 3           # + 09:10
    assert at(f, "kyiv_city", t, "frontline_onsets_3h") == 1          # only Kharkivska is frontline
    assert at(f, "kyiv_city", t, "neighbour_onsets_1h") == 1          # Kyivska's 11:20, not its own 11:50
    assert at(f, "kyivska", t, "neighbour_onsets_1h") == 1            # Kyiv City's 11:50 (separate units)
    assert at(f, "kharkivska", t, "neighbour_onsets_1h") == 0
    assert at(f, "kyiv_city", t, "minutes_since_national_onset") == 10
    assert at(f, "kyiv_city", "2025-03-26 09:00", "national_onsets_1h") == 0   # onset at 09:10 is after t


def test_periodicity_and_dst():
    # 2025-03-30: Kyiv switches 03:00 EET -> 04:00 EEST at 01:00 UTC.
    rows = [("kyiv_city", "2025-03-29 00:10", "2025-03-29 00:30"),     # Kyiv 02:10 (EET)
            ("kyiv_city", "2025-03-28 23:30", "2025-03-28 23:45")]     # Kyiv 01:30 (EET)
    f = ev(rows)
    assert at(f, "kyiv_city", "2025-03-30 00:00", "onset_same_time_yesterday") == 1    # 00:10 in [t-25h, t-23h]
    assert at(f, "kyiv_city", "2025-03-30 03:00", "onset_same_time_yesterday") == 0
    # t = 2025-03-30 00:00 UTC is Kyiv 02:00 -> hours 1..3 count: both onsets (01:30, 02:10)
    assert at(f, "kyiv_city", "2025-03-30 00:00", "onsets_same_kyiv_hour_7d") == 2
    # t = 2025-03-30 01:00 UTC is Kyiv 04:00 (EEST) -> hours 3..5: none
    assert at(f, "kyiv_city", "2025-03-30 01:00", "onsets_same_kyiv_hour_7d") == 0
    wrap = ev([("kyivska", "2025-03-26 21:30", "2025-03-26 21:50")])   # Kyiv 23:30 (EET)
    assert at(wrap, "kyivska", "2025-03-27 22:00", "onsets_same_kyiv_hour_7d") == 1    # t Kyiv 00:00, 23 wraps


def test_event_gap_rules_and_unknown_end():
    rows = [("kyiv_city", "2025-03-26 05:10", None)]                   # unknown end: onset still counted once
    f = ev(rows, zones=((ts("2025-03-27 00:00"), ts("2025-03-28 00:00")),))
    assert at(f, "kyiv_city", "2025-03-26 06:00", "national_onsets_1h") == 1
    assert np.isnan(at(f, "kyiv_city", "2025-03-27 00:00", "national_onsets_1h"))
    assert np.isnan(at(f, "kyiv_city", "2025-03-28 05:00", "minutes_since_national_onset"))   # last onset before zone end
    assert np.isnan(at(f, "kyiv_city", "2025-03-28 00:00", "onset_same_time_yesterday"))      # window touches the zone
    assert not np.isnan(at(f, "kyiv_city", "2025-03-29 02:00", "onset_same_time_yesterday"))


def test_standing_alert_cap_does_not_create_onsets():
    rows = [("kyiv_city", "2025-03-26 05:10", "2025-03-29 05:10")]     # > 24 h: one onset only
    f = ev(rows)
    assert at(f, "kyiv_city", "2025-03-27 06:00", "national_onsets_3h") == 0
    assert at(f, "kyiv_city", "2025-03-26 06:00", "national_onsets_1h") == 1


def test_offset_oracle_and_endpoints():
    df = pd.DataFrame({"offset_rate": [0.0, 0.2, 1.0]})
    z = FP.offset_logit(df["offset_rate"])
    p = 1 / (1 + np.exp(-z))
    assert p == pytest.approx([1e-4, 0.2, 1 - 1e-4])


def test_input_guards():
    from src.data import DataQualityError
    g = toy_grid(hours=24 * 20)
    with pytest.raises(DataQualityError):
        FP.label_rates(g, pd.Timedelta(minutes=90))
    holes = g[~g["t"].between(ts("2024-01-05"), ts("2024-01-07"))]
    with pytest.raises(DataQualityError):
        FP.label_rates(holes, H)
    with pytest.raises(DataQualityError):                      # an alert for a unit not in the grid
        FP.event_features(alerts([("kharkivska", "2024-01-03 05:00", "2024-01-03 06:00")]), g, neighbours={"A": set(), "B": set()})
    with pytest.raises(DataQualityError):                      # compute_plus needs all 24 units
        FP.compute_plus(alerts([("A", "2024-01-03 05:00", "2024-01-03 06:00")]), g, H)
    for bad in ([-0.5], [1.7], [np.inf], [np.nan]):
        with pytest.raises(DataQualityError):
            FP.offset_logit(bad)
