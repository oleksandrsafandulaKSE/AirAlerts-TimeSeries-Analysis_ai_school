import numpy as np
import pandas as pd
import pytest

from src import features as F
from src import grid
from src.data import DataQualityError

D = "2024-01-10"
NB = {"A": {"B"}, "B": {"A", "C"}, "C": {"B"}}


def T(s):
    return pd.Timestamp(s if " " in s else f"{D} {s}", tz="UTC")


def alerts(rows):
    cols = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
    out = [{"source": "test", "alert_id": str(i), "unit": r[0], "level": r[3] if len(r) > 3 else "oblast",
            "started_at": T(r[1]), "finished_at": T(r[2]) if r[2] else pd.NaT, "alert_level": ""}
           for i, r in enumerate(rows)]
    df = pd.DataFrame(out, columns=cols)
    df["started_at"] = pd.to_datetime(df["started_at"], utc=True)
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


def nb(units):
    return {u: NB[u] & set(units) for u in units}


def feat(rows, times, zones=(), units=("A",)):
    f = F.build_features(alerts(rows), pd.DatetimeIndex([T(x) for x in times]), zones,
                         unit_list=list(units), neighbours=nb(units))
    return f.set_index(["unit", "t"])


def v(f, t, col, unit="A"):
    return f.loc[(unit, T(t)), col]


def test_time_since():
    f = feat([("A", "01:10", "01:50"), ("A", "03:00", "03:30")], ["02:00", "03:00"])
    assert v(f, "02:00", "minutes_since_last_start") == 50 and v(f, "02:00", "minutes_since_last_end") == 10
    assert v(f, "03:00", "minutes_since_last_start") == 0 and v(f, "03:00", "minutes_since_last_end") == 70
    assert v(f, "03:00", "active_at_t") == 1


def test_standing_cap_end():
    f = feat([("A", f"{D} 00:00", "2024-01-13 00:00", "hromada")], [f"{D} 12:00", "2024-01-11 00:00"])
    assert np.isnan(v(f, f"{D} 12:00", "minutes_since_last_end"))
    assert v(f, "2024-01-11 00:00", "minutes_since_last_end") == 0
    assert v(f, "2024-01-11 00:00", "active_at_t") == 0


@pytest.mark.parametrize("col,w", [("onsets_last_24h", "2024-01-11 00:00"), ("onsets_last_7d", "2024-01-17 00:00")])
def test_window_edges(col, w):
    t = "2024-01-11 00:00" if col == "onsets_last_24h" else "2024-01-17 00:00"
    exact = feat([("A", f"{D} 00:00", f"{D} 00:20")], [t])            # onset exactly t - W: excluded
    inside = feat([("A", f"{D} 00:01", f"{D} 00:20")], [t])           # t - W + 1 min: included
    at_t = feat([("A", t, None)], [t])                                 # onset exactly at t: included
    assert v(exact, t, col) == 0 and v(inside, t, col) == 1 and v(at_t, t, col) == 1


def test_onset_merging_rules():
    touching = feat([("A", "01:00", "02:00"), ("A", "02:00", "03:00")], ["05:00"])
    nested = feat([("A", "01:00", "03:00", "oblast"), ("A", "01:30", "01:50", "raion")], ["05:00"])
    split = feat([("A", "01:00", "02:00"), ("A", "02:01", "03:00")], ["05:00"])
    assert v(touching, "05:00", "onsets_last_24h") == 1
    assert v(nested, "05:00", "onsets_last_24h") == 1
    assert v(split, "05:00", "onsets_last_24h") == 2


def test_neighbours_and_national():
    f = feat([("A", "01:00", "03:00"), ("C", "01:30", "04:00")], ["02:00"], units=("A", "B", "C"))
    assert v(f, "02:00", "neighbors_active_at_t", "B") == 2
    assert v(f, "02:00", "neighbors_active_at_t", "A") == 0
    assert v(f, "02:00", "neighbors_active_at_t", "C") == 0
    assert (f["national_active_count_at_t"] == 2).all()
    assert list(f["unit_code"]) == [0, 1, 2]


@pytest.mark.parametrize("t,hour", [("2025-03-30 00:00", 2), ("2025-03-30 01:00", 4),
                                    ("2025-10-26 00:00", 3), ("2025-10-26 01:00", 3)])
def test_dst_calendar(t, hour):
    f = feat([], [t])
    assert v(f, t, "hour_kyiv") == hour and v(f, t, "weekday_kyiv") == 6


def test_gap_nan_edges():
    zone = ((T("2024-01-11 10:00"), T("2024-01-12 14:00")),)  # gap [D+1 10, D+1 14) + 24h
    rows = [("A", "05:00", "05:30"), ("A", "2024-01-12 12:00", "2024-01-12 12:10"),
            ("A", "2024-01-12 15:30", "2024-01-12 15:40")]
    ts = ["2024-01-11 09:00", "2024-01-11 10:00", "2024-01-12 15:00", "2024-01-12 16:00",
          "2024-01-12 13:00", "2024-01-13 13:00", "2024-01-13 14:00"]
    f = feat(rows, ts, zone)
    c = "onsets_last_24h"
    assert not np.isnan(v(f, "2024-01-11 09:00", c)) and np.isnan(v(f, "2024-01-11 10:00", c))
    assert np.isnan(v(f, "2024-01-13 13:00", c)) and v(f, "2024-01-13 14:00", c) == 1
    s = "minutes_since_last_start"
    assert v(f, "2024-01-11 09:00", s) == (24 + 4) * 60
    assert np.isnan(v(f, "2024-01-11 10:00", s))
    assert np.isnan(v(f, "2024-01-12 15:00", s))           # 12:00 event is inside the zone -> still NaN
    assert v(f, "2024-01-12 16:00", s) == 30
    assert np.isnan(v(f, "2024-01-12 15:00", "minutes_since_last_end"))
    assert v(f, "2024-01-12 16:00", "minutes_since_last_end") == 20   # 15:40 end is after the zone
    for col in ["active_at_t", "neighbors_active_at_t", "national_active_count_at_t"]:
        assert np.isnan(v(f, "2024-01-11 10:00", col)) and np.isnan(v(f, "2024-01-12 13:00", col))
        assert not np.isnan(v(f, "2024-01-13 14:00", col))
    assert not f[["hour_kyiv", "weekday_kyiv", "unit_code"]].isna().any().any()


def test_unknown_neighbour_raises():
    with pytest.raises(KeyError):
        F.build_features(alerts([]), pd.DatetimeIndex([T("01:00")]), unit_list=["A"], neighbours=NB)


def test_bad_inputs_raise():
    with pytest.raises(DataQualityError):
        F.build_features(alerts([("Z", "01:00", "02:00")]), pd.DatetimeIndex([T("03:00")]),
                         unit_list=["A"], neighbours={"A": set()})
    with pytest.raises(ValueError):
        F.build_features(alerts([]), pd.DatetimeIndex([T("03:00"), T("03:00")]),
                         unit_list=["A"], neighbours={"A": set()})


def test_toy_lookahead_window_is_caught_by_definition():
    # onset 30 min after t must not be counted at t
    f = feat([("A", "03:30", "03:50")], ["03:00"])
    assert v(f, "03:00", "onsets_last_24h") == 0 and np.isnan(v(f, "03:00", "minutes_since_last_start"))


def test_official_uncertainty_zone():
    from src import config
    assert config.uncertainty_zones(config.official()) == (
        (pd.Timestamp("2026-08-29", tz="UTC"), pd.Timestamp("2026-09-04", tz="UTC")),)


def test_join_to_grid():
    a = alerts([("A", "01:00", "02:00")])
    g = grid.build_grid(a, T("00:00"), T("04:00"), pd.Timedelta(hours=1), unit_list=["A", "B"])
    f = F.build_features(a, g.t.drop_duplicates(), unit_list=["A", "B"], neighbours=nb(["A", "B"]))
    m = F.join_to_grid(g, f)
    assert len(m) == len(g) == 8
    with pytest.raises(DataQualityError):
        F.join_to_grid(g, pd.concat([f, f.iloc[[0]]]))
    with pytest.raises(DataQualityError):
        F.join_to_grid(g, f.iloc[1:])
