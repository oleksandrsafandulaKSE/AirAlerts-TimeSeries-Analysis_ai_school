"""M10 §D (plans/M10.md): stability tables from SAVED predictions only — per Monday-00:00-UTC week and per Kyiv
day (06:00-21:59) / night (22:00-05:59), per group and predictor. Metrics come from src.evaluate.metric_table
(pooled BSS ratio, pooled and within-unit AUC with >= 10 pos and neg per unit, PR-AUC, NaN with reasons)."""
import numpy as np
import pandas as pd

from src import evaluate, regions
from src.data import DataQualityError


def _keys(df, name):
    if df.duplicated(["unit", "t"]).any():
        raise DataQualityError(f"{name}: duplicate (unit, t)")
    return set(zip(df["unit"], df["t"]))


def join_predictions(frames):
    """frames: {name: DataFrame(unit, t, y, <prediction columns>)}. Inner join on (unit, t) with UTC-aware t;
    raises unless every frame has unique keys, the SAME key set and bit-identical y."""
    names = list(frames)
    out = None
    ref_keys = None
    for name in names:
        df = frames[name].copy()
        df["t"] = pd.to_datetime(df["t"], utc=True)
        k = _keys(df, name)
        if ref_keys is None:
            ref_keys = k
        elif k != ref_keys:
            raise DataQualityError(f"{name}: key set differs from {names[0]} ({len(k ^ ref_keys)} keys)")
        if out is None:
            out = df
            continue
        m = out.merge(df, on=["unit", "t"], suffixes=("", f"__{name}"), validate="one_to_one")
        if not np.array_equal(m["y"].to_numpy(float), m[f"y__{name}"].to_numpy(float), equal_nan=True):
            raise DataQualityError(f"{name}: y differs from {names[0]}")
        out = m.drop(columns=[f"y__{name}"])
    out["group"] = [regions.group_of(u) for u in out["unit"]]
    return out


def day_night(t):
    """'day' for Kyiv local hours 06..21, else 'night' (local clock, so DST days follow the wall clock)."""
    h = pd.DatetimeIndex(pd.to_datetime(t, utc=True)).tz_convert("Europe/Kyiv").hour
    return np.where((h >= 6) & (h <= 21), "day", "night")


def week_start(t):
    """Monday 00:00 UTC of the week containing t."""
    t = pd.DatetimeIndex(pd.to_datetime(t, utc=True))
    return (t.normalize() - pd.to_timedelta(t.weekday, unit="D"))


def slice_tables(scored, predictors, ref="recent_rate", min_class=10, low_n_rows=100):
    """metric_table per slice: 'week' (Monday UTC) and 'day_night'. Returns (table, reasons)."""
    s = scored.copy()
    s["week"] = week_start(s["t"]).strftime("%Y-%m-%d")
    s["day_night"] = day_night(s["t"])
    parts, reasons = [], []
    for kind in ("week", "day_night"):
        for val, g in s.groupby(kind, sort=True):
            t, r = evaluate.metric_table(g, predictors, ref, min_class)
            t = evaluate.low_n_flags(t, low_n_rows)
            t.insert(0, "slice", val)
            t.insert(0, "slice_kind", kind)
            parts.append(t)
            reasons += [f"{kind}={val}: {x}" for x in r]
    return pd.concat(parts, ignore_index=True), reasons
