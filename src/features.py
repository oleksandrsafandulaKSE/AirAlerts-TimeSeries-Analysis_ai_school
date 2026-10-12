"""Features known at t (M2). Built only from the D-020 merged unit intervals/onsets of grid.py."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError
from src.grid import _covered, check_units, unit_intervals

WINDOWS = {"onsets_last_24h": pd.Timedelta(hours=24), "onsets_last_7d": pd.Timedelta(days=7)}

# model feature list; active_at_t stays in the frame for audit only (constant 0 on unmasked rows)
FEATURES = ["minutes_since_last_start", "minutes_since_last_end", "onsets_last_24h", "onsets_last_7d",
            "neighbors_active_at_t", "national_active_count_at_t", "hour_kyiv", "weekday_kyiv", "unit_code"]
ALL_COLUMNS = ["active_at_t"] + FEATURES


def _last_le(sorted_events, t):
    """Last event <= t for each t (NaT if none)."""
    idx = np.searchsorted(sorted_events, t, side="right") - 1
    out = np.full(len(t), np.datetime64("NaT", "ns"), dtype="datetime64[ns]")
    ok = idx >= 0
    out[ok] = sorted_events[idx[ok]]
    return out


def _minutes(t, last):
    return (t - last) / np.timedelta64(1, "m")  # NaT -> NaN


def build_features(alerts, times, zones=(), cap=pd.Timedelta(hours=24), target_levels="any",
                   unit_list=None, neighbours=None):
    """One row per (unit, t) for t in `times` (tz-aware UTC). Uses only alerts as known at each t."""
    unit_list = regions.units() if unit_list is None else list(unit_list)
    neighbours = regions.NEIGHBOURS if neighbours is None else neighbours
    times = pd.DatetimeIndex(times)
    if str(times.tz) != "UTC":
        raise ValueError("times must be tz-aware UTC")
    if times.has_duplicates:
        raise ValueError("duplicate times")
    check_units(alerts, unit_list)
    t = times.tz_localize(None).to_numpy("datetime64[ns]")
    ivs = unit_intervals(alerts, cap, target_levels)
    empty = np.array([], dtype="datetime64[ns]")

    # uncertainty-zone masks (M2 plan §4), naive UTC
    z = [(np.datetime64(a.tz_convert("UTC").tz_localize(None), "ns"),
          np.datetime64(b.tz_convert("UTC").tz_localize(None), "ns")) for a, b in zones]
    in_zone = np.zeros(len(t), dtype=bool)
    for u0, u1 in z:
        in_zone |= (t >= u0) & (t < u1)

    kyiv = times.tz_convert("Europe/Kyiv")
    hour, weekday = kyiv.hour.to_numpy(), kyiv.weekday.to_numpy()

    per_unit, active = {}, {}
    for code, u in enumerate(unit_list):
        ms, me, on = ivs.get(u, (empty, empty, empty))
        act = _covered(t, ms, me)
        active[u] = act
        last_on, last_end = _last_le(on, t), _last_le(me, t)
        cols = {"active_at_t": act.astype(float),
                "minutes_since_last_start": _minutes(t, last_on),
                "minutes_since_last_end": _minutes(t, last_end)}
        for u0, u1 in z:  # last event may hide inside the zone
            after = t >= u0
            cols["minutes_since_last_start"][after & ~(last_on >= u1)] = np.nan
            cols["minutes_since_last_end"][after & ~(last_end >= u1)] = np.nan
        for name, w in WINDOWS.items():
            wv = np.timedelta64(w)
            n = (np.searchsorted(on, t, side="right") - np.searchsorted(on, t - wv, side="right")).astype(float)
            for u0, u1 in z:  # (t-W, t] intersects [u0, u1)
                n[(t >= u0) & (t - wv < u1)] = np.nan
            cols[name] = n
        cols["active_at_t"][in_zone] = np.nan
        cols["unit_code"] = np.full(len(t), code)
        per_unit[u] = cols

    national = np.sum([active[u] for u in unit_list], axis=0).astype(float)
    national[in_zone] = np.nan
    parts = []
    for u in unit_list:
        nb = np.zeros(len(t))
        for v in neighbours.get(u, ()):
            if v not in active:
                raise KeyError(f"neighbour {v!r} of {u!r} is not in unit_list")
            nb = nb + active[v]
        nb[in_zone] = np.nan
        c = per_unit[u]
        parts.append(pd.DataFrame({
            "unit": u, "t": times, "active_at_t": c["active_at_t"],
            "minutes_since_last_start": c["minutes_since_last_start"],
            "minutes_since_last_end": c["minutes_since_last_end"],
            "onsets_last_24h": c["onsets_last_24h"], "onsets_last_7d": c["onsets_last_7d"],
            "neighbors_active_at_t": nb, "national_active_count_at_t": national,
            "hour_kyiv": hour, "weekday_kyiv": weekday, "unit_code": c["unit_code"],
        }))
    return pd.concat(parts, ignore_index=True)


def join_to_grid(grid, feats):
    """1:1 join on (unit, t); raises on duplicates or missing pairs (M2 decision 8)."""
    key = ["unit", "t"]
    for name, df in (("grid", grid), ("features", feats)):
        if df.duplicated(key).any():
            raise DataQualityError(f"duplicate (unit, t) in {name}: {int(df.duplicated(key).sum())}")
    f = feats.drop(columns=["active_at_t"])
    m = grid.merge(f, on=key, how="outer", indicator=True, validate="one_to_one")
    if (m["_merge"] != "both").any():
        raise DataQualityError(f"join incomplete: {m['_merge'].value_counts().to_dict()}")
    gf = feats.set_index(key)["active_at_t"].reindex(pd.MultiIndex.from_frame(grid[key]))
    ok = gf.isna().to_numpy() | (gf.to_numpy() == grid["active_at_t"].to_numpy())
    if not ok.all():
        raise DataQualityError("feature active_at_t disagrees with grid active_at_t")
    return m.drop(columns="_merge")
