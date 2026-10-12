"""Truncation-invariance leakage test (ts-leakage-audit) on the REAL official data, with a negative control."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import config, data, features as F, grid, regions

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "official_data_en.csv"
CFG = config.official()
ZONES = config.uncertainty_zones(CFG)
NB = {"A": {"B"}, "B": {"A"}}


def truncate(alerts, t):
    """Alerts as known at t: drop starts after t; ends after t are not yet known."""
    a = alerts[alerts["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


def truncation_check(feature_fn, alerts, times, units=None, columns=None):
    """Mismatches (t, unit, column) between features from full data and from data truncated at t."""
    times = pd.DatetimeIndex(times)
    full = feature_fn(alerts, times).set_index(["unit", "t"])
    columns = [c for c in full.columns] if columns is None else columns
    bad = []
    for t in times:
        cut = feature_fn(truncate(alerts, t), pd.DatetimeIndex([t])).set_index(["unit", "t"])
        for u in (full.index.get_level_values("unit").unique() if units is None else units):
            for c in columns:
                x, y = full.loc[(u, t), c], cut.loc[(u, t), c]
                if not ((pd.isna(x) and pd.isna(y)) or x == y):
                    bad.append((t, u, c))
    return bad


def real_features(alerts, times):
    return F.build_features(alerts, times, ZONES)


def leaky_features(alerts, times, unit_list=None):
    """Negative control. (a) uses an end not known at t; (b) a centred window that reads (t, t+90min]."""
    ivs = grid.unit_intervals(alerts)
    rows = []
    for t in times:
        for u in (regions.units() if unit_list is None else unit_list):
            g = alerts[alerts.unit == u]
            act = g[(g.started_at <= t) & ~(g.finished_at <= t)]
            dur = (act.finished_at - act.started_at).dt.total_seconds() / 60
            on = pd.to_datetime(ivs[u][2]).tz_localize("UTC") if u in ivs else pd.DatetimeIndex([], tz="UTC")
            rows.append({"unit": u, "t": t,
                         "current_alert_final_minutes": dur.max() if dur.notna().any() else np.nan,
                         "onsets_centered_3h": int(((on > t - pd.Timedelta(minutes=90)) &
                                                    (on <= t + pd.Timedelta(minutes=90))).sum())})
    return pd.DataFrame(rows)


# ---------------- fixed toy cases (M2 decision 7) ----------------

def toy(rows):
    cols = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
    df = pd.DataFrame([{"source": "t", "alert_id": str(i), "unit": u, "level": "hromada",
                        "started_at": pd.Timestamp(s, tz="UTC"),
                        "finished_at": pd.Timestamp(e, tz="UTC") if e else pd.NaT, "alert_level": ""}
                       for i, (u, s, e) in enumerate(rows)], columns=cols)
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


def toy_features(alerts, times):
    return F.build_features(alerts, times, unit_list=["A", "B"], neighbours=NB)


@pytest.mark.parametrize("name,rows,t", [
    ("touching", [("A", "2024-01-10 01:00", "2024-01-10 02:00"), ("A", "2024-01-10 02:00", "2024-01-10 03:00")],
     ["2024-01-10 02:00", "2024-01-10 03:00", "2024-01-10 04:00"]),
    ("extended_after_t", [("A", "2024-01-10 01:00", "2024-01-10 03:00"), ("A", "2024-01-10 02:30", "2024-01-10 06:00")],
     ["2024-01-10 02:00", "2024-01-10 03:00", "2024-01-10 04:00", "2024-01-10 07:00"]),
    ("finished_eq_t", [("A", "2024-01-10 01:00", "2024-01-10 03:00")], ["2024-01-10 03:00"]),
    ("finished_t_plus_1min", [("A", "2024-01-10 01:00", "2024-01-10 03:01")], ["2024-01-10 03:00"]),
    ("exactly_24h", [("A", "2024-01-10 01:00", "2024-01-11 01:00")],
     ["2024-01-11 00:00", "2024-01-11 01:00", "2024-01-11 02:00"]),
    ("t_at_cap", [("A", "2024-01-10 01:00", "2024-01-13 00:00"), ("B", "2024-01-10 05:00", "2024-01-10 06:00")],
     ["2024-01-11 00:00", "2024-01-11 01:00", "2024-01-11 02:00"]),
])
def test_fixed_truncation_cases(name, rows, t):
    times = pd.DatetimeIndex([pd.Timestamp(x, tz="UTC") for x in t])
    assert truncation_check(toy_features, toy(rows), times) == [], name


def test_negative_control_catches_toy():
    a = toy([("A", "2024-01-10 01:00", "2024-01-13 00:00"), ("B", "2024-01-10 02:20", "2024-01-10 02:40")])
    times = pd.DatetimeIndex([pd.Timestamp("2024-01-10 02:00", tz="UTC")])
    leaky = lambda al, ts: leaky_features(al, ts, ["A", "B"])  # noqa: E731
    assert set(truncation_check(leaky, a, times)) == {
        (times[0], "A", "current_alert_final_minutes"), (times[0], "B", "onsets_centered_3h")}


# ---------------- real data ----------------

@pytest.fixture(scope="module")
def real():
    if not DATA.exists():
        pytest.fail(f"{DATA} missing: run scripts/run_all.py --config official once to download it")
    return data.load_official(DATA, CFG)


def first_covering_hour(alerts, unit, after):
    ms, me, _ = grid.unit_intervals(alerts[alerts.unit == unit])[unit]
    for s, e in zip(ms, me):
        s, e = pd.Timestamp(s, tz="UTC"), pd.Timestamp(e, tz="UTC")
        if s >= after and s.ceil("h") < e:
            return s.ceil("h")
    raise AssertionError("no covering hour found")


def lypetska(alerts):
    a = alerts[(alerts.unit == "kharkivska") & (alerts.level == "hromada")
               & (alerts.started_at.dt.strftime("%Y-%m-%d") == "2024-05-12")
               & ((alerts.finished_at - alerts.started_at) > pd.Timedelta(days=400))]
    assert len(a) == 1, len(a)
    return a.iloc[0]


def witness_b(alerts):
    _, _, on = grid.unit_intervals(alerts[alerts.unit == "kyiv_city"])["kyiv_city"]
    on = pd.to_datetime(on).tz_localize("UTC")
    o = on[(on >= pd.Timestamp("2025-06-01", tz="UTC")) & (on.minute != 0)][0]
    return o.floor("h")


def real_times(alerts):
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    rng = np.random.default_rng(20261012)
    times = []
    for lo, hi in [("2022-04-01", "2022-12-31"), ("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-31"),
                   ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-06-28")]:
        n = int((ts(hi) - ts(lo)) / pd.Timedelta(hours=1))
        times.append(ts(lo) + pd.Timedelta(hours=int(rng.integers(0, n))))
    times += [first_covering_hour(alerts, "kyiv_city", ts("2025-06-01")),
              first_covering_hour(alerts, "kharkivska", ts("2025-06-01"))]
    L = lypetska(alerts)
    for h in (2, 30):
        t = (L.started_at + pd.Timedelta(hours=h)).floor("h")
        assert L.finished_at > t  # the truncated copy hides this end
        times.append(t)
    (g0, g1), = CFG.approved_gaps
    H = pd.Timedelta(hours=1)
    times += [g0 - H, g0, g1 - H, g1, g1 + pd.Timedelta(hours=24) - H, g1 + pd.Timedelta(hours=24),
              g1 + pd.Timedelta(hours=48) - H, g1 + pd.Timedelta(hours=48)]
    times += [ts("2025-03-30 00:00"), ts("2025-03-30 01:00"), ts("2025-10-26 00:00"), ts("2025-10-26 01:00")]
    for c in (CFG.val[0], CFG.test[0]):
        times += [c - H, c]
    # off-grid witnesses for small look-ahead (reviewer M2 #3): just before / exactly at a real
    # Kyiv City onset and a real merged end; plus the hour of an onset at minute 0
    ms, me, on = grid.unit_intervals(alerts[alerts.unit == "kyiv_city"])["kyiv_city"]
    on, me = pd.to_datetime(on).tz_localize("UTC"), pd.to_datetime(me).tz_localize("UTC")
    o = on[on >= ts("2025-06-01")][0]
    e = me[me >= ts("2025-06-01")][0]
    sec = pd.Timedelta(seconds=1)
    times += [o - sec, o, e - sec, e]
    # first real onset exactly on the hour (any unit) after 2025-06-01: the hour before it and the hour itself
    on_hour = sorted(o for _, _, ons in grid.unit_intervals(alerts).values()
                     for o in pd.to_datetime(ons).tz_localize("UTC")
                     if o >= ts("2025-06-01") and o == o.floor("h"))
    assert on_hour, "no onset exactly on the hour after 2025-06-01"
    times += [on_hour[0] - H, on_hour[0]]
    return pd.DatetimeIndex(sorted(set(times)))


def test_real_data_truncation_invariant(real):
    times = real_times(real)
    assert len(times) >= 25
    f = real_features(real, times)
    act = f.set_index(["unit", "t"])["active_at_t"]
    assert act.loc[("kyiv_city", first_covering_hour(real, "kyiv_city", pd.Timestamp("2025-06-01", tz="UTC")))] == 1
    assert act.loc[("kharkivska", first_covering_hour(real, "kharkivska", pd.Timestamp("2025-06-01", tz="UTC")))] == 1
    assert truncation_check(real_features, real, times) == []


def test_real_data_negative_control_pinned_witnesses(real):
    L = lypetska(real)
    t_a = (L.started_at + pd.Timedelta(hours=2)).floor("h")
    t_b = witness_b(real)
    found = set(truncation_check(leaky_features, real, [t_a], units=["kharkivska"],
                                 columns=["current_alert_final_minutes"]))
    found |= set(truncation_check(leaky_features, real, [t_b], units=["kyiv_city"],
                                  columns=["onsets_centered_3h"]))
    assert found == {(t_a, "kharkivska", "current_alert_final_minutes"),
                     (t_b, "kyiv_city", "onsets_centered_3h")}
    # the real features are clean at the same witnesses
    assert truncation_check(real_features, real, [t_a, t_b]) == []
