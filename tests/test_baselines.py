import numpy as np
import pandas as pd
import pytest

from src import baselines as B
from src.data import DataQualityError

H = pd.Timedelta(hours=1)
W = pd.Timedelta(days=14)


def ts(s):
    return pd.Timestamp(s, tz="UTC")


T0 = ts("2024-02-01 00:00")


def history(unit="A", days=20):
    t = pd.date_range(T0 - pd.Timedelta(days=days), T0 + pd.Timedelta(days=1), freq="h", inclusive="left")
    return pd.DataFrame({"unit": unit, "t": t, "mask": 0, "y": 0.0})


def rr(h, t, p_unit=0.0, alpha=0.0):
    score = pd.DataFrame({"unit": ["A"], "t": [t]})
    p, n = B.recent_rate(h, score, pd.Series({"A": p_unit}), alpha, W, H, return_n=True)
    return p[0], n[0]


def set_y(h, t, v):
    h.loc[h.t == t, "y"] = v


def test_recent_rate_window_edges():
    h = history()
    _, n = rr(h, T0)
    assert n == 14 * 24  # s in [t-14d, t-1h] hourly: t-336h ... t-1h = 336 rows
    for s, counts in [(T0 - H, True), (T0, False), (T0 - W, True), (T0 - W - H, False)]:
        h2 = history()
        set_y(h2, s, 1.0)
        p, n = rr(h2, T0)
        assert (p > 0) == counts, s
    h3 = history()
    h3.loc[h3.t == T0 - 2 * H, ["y", "mask"]] = [1.0, 1]   # masked history row: excluded from n and k
    h3.loc[h3.t == T0 - 3 * H, "y"] = np.nan                # unknown label: excluded
    p, n = rr(h3, T0)
    assert p == 0 and n == 14 * 24 - 2


def test_recent_rate_shrinkage_formula():
    h = history()
    h["mask"] = 1
    keep = [T0 - k * H for k in range(1, 11)]                  # n = 10 eligible rows
    h.loc[h.t.isin(keep), "mask"] = 0
    set_y(h, keep[0], 1.0)
    set_y(h, keep[5], 1.0)                                     # k = 2
    p, n = rr(h, T0, p_unit=0.1, alpha=10)
    assert n == 10 and p == pytest.approx((2 + 10 * 0.1) / 20)  # 0.15
    h["mask"] = 1
    p, n = rr(h, T0, p_unit=0.1, alpha=10)
    assert n == 0 and p == pytest.approx(0.1)


def test_recent_rate_label_maturity():
    rng = np.random.default_rng(1)
    h = history()
    h["y"] = (rng.random(len(h)) < 0.2).astype(float)
    p, _ = rr(h, T0, 0.1, 10)
    future = h.t > T0 - H                                      # includes the scored row itself
    h2 = h.copy()
    h2.loc[future, "y"] = 1 - h2.loc[future, "y"]
    assert rr(h2, T0, 0.1, 10)[0] == p
    h3 = h.copy()
    h3.loc[h3.t == T0 - H, "y"] = 1 - h3.loc[h3.t == T0 - H, "y"]   # negative control: a known label
    assert rr(h3, T0, 0.1, 10)[0] != p


def fit_frame():
    rows = []
    for i in range(40):
        rows.append({"unit": "A", "hour_kyiv": 3, "weekday_kyiv": 0, "minutes_since_last_end": 30.0,
                     "y": float(i < 10)})
    for i in range(60):
        rows.append({"unit": "A", "hour_kyiv": 5, "weekday_kyiv": 1, "minutes_since_last_end": 800.0,
                     "y": float(i < 3)})
    return pd.DataFrame(rows)


def test_climatology_and_calibrated_persistence():
    fit = fit_frame()
    p_unit = B.unit_train_rates(fit)
    assert p_unit["A"] == pytest.approx(13 / 100)
    score = pd.DataFrame({"unit": ["A", "A", "A"], "hour_kyiv": [3, 5, 7], "weekday_kyiv": [0, 1, 2],
                          "minutes_since_last_end": [59.9, 720.0, 60.0]})
    clim = B.climatology(fit, score, p_unit, 10)
    assert clim == pytest.approx([(10 + 1.3) / 50, (3 + 1.3) / 70, 0.13])   # empty cell -> p_unit
    pers = B.persistence_calibrated(fit, score, p_unit, 10, (0, 60, 180, 720, float("inf")))
    assert pers == pytest.approx([(10 + 1.3) / 50, (3 + 1.3) / 70, 0.13])  # 59.9->bin0, 720->bin3, 60->bin1 (empty)
    assert list(B.persistence_bin(pd.Series([59.9, 60, 720, 0]), (0, 60, 180, 720, float("inf")))) == [0, 1, 3, 0]


def test_frozen_baselines_ignore_non_fit_labels():
    fit = fit_frame()
    p_unit = B.unit_train_rates(fit)
    score = pd.DataFrame({"unit": ["A"], "hour_kyiv": [3], "weekday_kyiv": [0], "minutes_since_last_end": [30.0],
                          "y": [1.0]})
    a = B.climatology(fit, score, p_unit, 10), B.persistence_calibrated(fit, score, p_unit, 10, (0, 60, 180, 720, float("inf")))
    score["y"] = 0.0
    b = B.climatology(fit, score, p_unit, 10), B.persistence_calibrated(fit, score, p_unit, 10, (0, 60, 180, 720, float("inf")))
    assert a == b


def test_unit_without_train_rows_raises():
    fit = fit_frame()
    score = pd.DataFrame({"unit": ["Z"], "hour_kyiv": [3], "weekday_kyiv": [0]})
    with pytest.raises(DataQualityError):
        B.climatology(fit, score, B.unit_train_rates(fit), 10)


def test_persistence_raw():
    t = ts("2024-01-10 05:00")
    al = pd.DataFrame([
        {"source": "t", "alert_id": "1", "unit": "A", "level": "oblast", "started_at": t - pd.Timedelta(minutes=30),
         "finished_at": t - pd.Timedelta(minutes=10), "alert_level": ""},
        {"source": "t", "alert_id": "2", "unit": "B", "level": "oblast", "started_at": t - H,
         "finished_at": t - pd.Timedelta(minutes=50), "alert_level": ""},
        {"source": "t", "alert_id": "3", "unit": "C", "level": "oblast", "started_at": t,
         "finished_at": t + pd.Timedelta(minutes=50), "alert_level": ""},
    ])
    score = pd.DataFrame({"unit": ["A", "B", "C"], "t": [t, t, t]})
    assert list(B.persistence_raw(al, score, H)) == [1.0, 0.0, 1.0]


def test_climatology_uses_hour_and_weekday_independently():
    rows = []
    for h, w, k, n in [(3, 0, 8, 20), (3, 1, 1, 20), (5, 0, 4, 20)]:
        rows += [{"unit": "A", "hour_kyiv": h, "weekday_kyiv": w, "y": float(i < k)} for i in range(n)]
    fit = pd.DataFrame(rows)
    p_unit = B.unit_train_rates(fit)                       # 13 / 60
    score = pd.DataFrame({"unit": ["A"] * 3, "hour_kyiv": [3, 3, 5], "weekday_kyiv": [0, 1, 0]})
    a = 10 * 13 / 60
    assert B.climatology(fit, score, p_unit, 10) == pytest.approx([(8 + a) / 30, (1 + a) / 30, (4 + a) / 30])


def test_positional_writes_with_repeated_index_labels():
    h = history()
    h.loc[h.t == T0 - H, "y"] = 1.0
    score = pd.DataFrame({"unit": ["A", "A"], "t": [T0, T0]}, index=[0, 0])
    p = B.recent_rate(h, score, pd.Series({"A": 0.1}), 10, W, H)
    assert p[0] == p[1] == pytest.approx((1 + 1) / (336 + 10))
    al = pd.DataFrame([{"source": "t", "alert_id": "1", "unit": "A", "level": "oblast",
                        "started_at": T0 - pd.Timedelta(minutes=30), "finished_at": T0 - pd.Timedelta(minutes=10),
                        "alert_level": ""}])
    assert list(B.persistence_raw(al, pd.DataFrame({"unit": ["A", "A"], "t": [T0, T0]}, index=[3, 3]), H)) == [1.0, 1.0]


def test_bad_baseline_inputs_raise():
    h = history()
    with pytest.raises(DataQualityError):
        B.recent_rate(pd.concat([h, h.iloc[[5]]]), pd.DataFrame({"unit": ["A"], "t": [T0]}),
                      pd.Series({"A": 0.1}), 10, W, H)
    fit = fit_frame()
    score = pd.DataFrame({"unit": ["A"], "hour_kyiv": [np.nan], "weekday_kyiv": [0]})
    with pytest.raises(DataQualityError):
        B.climatology(fit, score, B.unit_train_rates(fit), 10)


H3 = pd.Timedelta(hours=3)


def rr3(h, t=T0, p_unit=0.0, alpha=0.0):
    score = pd.DataFrame({"unit": ["A"], "t": [t]})
    p, n = B.recent_rate(h, score, pd.Series({"A": p_unit}), alpha, W, H3, return_n=True)
    return p[0], n[0]


def test_recent_rate_h3_exact_k_n():
    h = history()
    assert rr3(h)[1] == 334                                        # s in [t-336h, t-3h]
    for s, k in [(T0 - H3, 1), (T0 - W, 1), (T0 - W - H, 0)]:
        h2 = history()
        set_y(h2, s, 1.0)
        p, n = rr3(h2)
        assert (p * n, n) == (k, 334), s
    h3 = history()
    set_y(h3, T0 - H, 1.0)
    set_y(h3, T0 - 2 * H, 1.0)                                     # immature positives
    assert rr3(h3) == (0.0, 334)
    h4 = history()
    h4.loc[h4.t.isin([T0 - H, T0 - 2 * H]), "y"] = np.nan          # immature missing labels: n unchanged
    assert rr3(h4)[1] == 334
    h5 = history()
    h5.loc[h5.t == T0 - 5 * H, "y"] = np.nan
    assert rr3(h5)[1] == 333
    h6 = history()
    h6.loc[h6.t == T0 - 5 * H, "mask"] = 1
    assert rr3(h6)[1] == 333


def test_persistence_raw_h3():
    t = ts("2024-01-10 05:00")
    mk = lambda u, s: {"source": "t", "alert_id": u, "unit": u, "level": "oblast", "started_at": s,  # noqa: E731
                       "finished_at": s + pd.Timedelta(minutes=5), "alert_level": ""}
    al = pd.DataFrame([mk("A", t - pd.Timedelta(hours=2, minutes=59)), mk("B", t - H3)])
    score = pd.DataFrame({"unit": ["A", "B"], "t": [t, t]})
    assert list(B.persistence_raw(al, score, H3)) == [1.0, 0.0]
