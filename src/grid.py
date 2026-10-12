"""Per-unit intervals (D-002 union, D-020 causal cap), gap handling (D-013), hourly UTC grid."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError


def filter_levels(alerts, target_levels):
    if target_levels == "any":
        return alerts
    if target_levels == "red":
        if (alerts["alert_level"].fillna("") == "").all():
            raise ValueError("target_levels='red' needs alert_level (official data has none)")
        return alerts[alerts["alert_level"] == "red"]
    raise ValueError(f"unknown target_levels {target_levels!r}")


def effective_end(alerts, cap):
    """D-020: an alert counts only during its first `cap`; a missing end = unknown -> cap."""
    capped = alerts["started_at"] + cap
    return alerts["finished_at"].where(alerts["finished_at"] < capped, capped).fillna(capped)


def merge_intervals(starts, ends):
    """Merge half-open intervals that overlap or touch. Empty intervals are ignored."""
    order = np.argsort(starts, kind="stable")
    ms, me = [], []
    for s, e in zip(starts[order], ends[order]):
        if e <= s:
            continue
        if ms and s <= me[-1]:
            if e > me[-1]:
                me[-1] = e
        else:
            ms.append(s)
            me.append(e)
    return np.array(ms, dtype="datetime64[ns]"), np.array(me, dtype="datetime64[ns]")


def _covered(x, ms, me):
    idx = np.searchsorted(ms, x, side="right") - 1
    ok = idx >= 0
    out = np.zeros(len(x), dtype=bool)
    out[ok] = x[ok] < me[idx[ok]]
    return out


def unit_intervals(alerts, cap=pd.Timedelta(hours=24), target_levels="any"):
    """{unit: (merged_starts, merged_ends, onsets)} as numpy datetime64[ns] (UTC, naive)."""
    a = filter_levels(alerts, target_levels)
    if (a["finished_at"] < a["started_at"]).any():
        raise DataQualityError("finished_at < started_at reached unit_intervals")
    out = {}
    for unit, g in a.groupby("unit"):
        s = g["started_at"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")
        e = effective_end(g, cap).dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")
        ms, me = merge_intervals(s, e)
        zero = s[e <= s]  # zero-duration alerts: onset kept, mask nothing (human decision Q10)
        extra = zero[~_covered(zero, ms, me)] if len(zero) else zero
        onsets = np.unique(np.concatenate([ms, extra]))
        out[unit] = (ms, me, onsets)
    return out


def check_units(alerts, unit_list):
    """No silent drop: every alert must belong to a unit being built."""
    unknown = set(alerts["unit"]) - set(unit_list)
    if unknown:
        raise DataQualityError(f"alerts for units not in unit_list: {sorted(unknown)}")


def _naive(ts):
    return np.datetime64(pd.Timestamp(ts).tz_convert("UTC").tz_localize(None), "ns")


def detect_gaps(alerts, min_hours=24):
    """Runs of >= min_hours consecutive UTC hours with zero alert starts nationally: [first empty, first non-empty)."""
    hours = alerts["started_at"].dt.floor("h")
    counts = hours.value_counts()
    full = pd.date_range(hours.min(), hours.max(), freq="h")
    empty = ~full.isin(counts.index)
    gaps, i = [], 0
    while i < len(full):
        if empty[i]:
            j = i
            while j < len(full) and empty[j]:
                j += 1
            if j - i >= min_hours:
                gaps.append((full[i], full[j]))
            i = j
        else:
            i += 1
    return gaps


def check_gaps(detected, approved):
    for d0, d1 in detected:
        if not any(a0 <= d0 and d1 <= a1 for a0, a1 in approved):
            raise DataQualityError(f"unapproved gap detected: [{d0}, {d1})")
    for a0, a1 in approved:
        if not any(a0 <= d0 and d1 <= a1 for d0, d1 in detected):
            raise DataQualityError(f"approved gap [{a0}, {a1}) not detected")


def gap_mask_for(t, H, approved_gaps, post_gap):
    m = np.zeros(len(t), dtype=bool)
    for g0, g1 in approved_gaps:
        g0, g1, pg = _naive(g0), _naive(g1), np.timedelta64(post_gap)
        m |= (t < g1) & (t + H >= g0)          # label window (t, t+H] touches [g0, g1)
        m |= (t >= g1) & (t < g1 + pg)        # post-gap: unrecorded alerts may still count (D-020)
    return m


def build_grid(alerts, grid_start, grid_end, H=pd.Timedelta(hours=1), target_levels="any",
               cap=pd.Timedelta(hours=24), approved_gaps=(), post_gap=pd.Timedelta(hours=24),
               unit_list=None, coverage_end=None):
    if coverage_end is not None and grid_end - pd.Timedelta(hours=1) + H > coverage_end:
        raise DataQualityError("last label window reaches past coverage_end")
    unit_list = regions.units() if unit_list is None else unit_list
    check_units(alerts, unit_list)
    for name, x in (("grid_start", grid_start), ("grid_end", grid_end)):
        if x.tz is None or x != x.floor("h"):
            raise ValueError(f"{name} must be tz-aware and on the hour, got {x}")
    t_idx = pd.date_range(grid_start, grid_end, freq="h", inclusive="left", tz="UTC")
    t = t_idx.tz_localize(None).to_numpy("datetime64[ns]")
    h = np.timedelta64(H)
    ivs = unit_intervals(alerts, cap, target_levels)
    gm = gap_mask_for(t, h, approved_gaps, post_gap)
    empty = np.array([], dtype="datetime64[ns]")
    parts = []
    for u in unit_list:
        ms, me, on = ivs.get(u, (empty, empty, empty))
        active = _covered(t, ms, me)
        n_on = np.searchsorted(on, t + h, side="right") - np.searchsorted(on, t, side="right")
        y = (n_on > 0).astype(float)
        y[gm] = np.nan
        parts.append(pd.DataFrame({
            "unit": u, "t": t_idx, "group": regions.UNITS[u]["group"] if u in regions.UNITS else "",
            "active_at_t": active.astype(np.int8), "gap_mask": gm.astype(np.int8),
            "mask": (active | gm).astype(np.int8), "y": y,
        }))
    return pd.concat(parts, ignore_index=True)


def base_rate_table(grid, before):
    g = grid[(grid["mask"] == 0) & (grid["t"] < before)]
    q = g["t"].dt.tz_localize(None).dt.to_period("Q")
    by_q = g.groupby(q)["y"].agg(["mean", "size"]).rename(columns={"mean": "base_rate", "size": "rows"})
    by_g = g.groupby("group")["y"].agg(["mean", "size"]).rename(columns={"mean": "base_rate", "size": "rows"})
    return by_q, by_g, g


def check_base_rate(grid, before, ratio=0.5):
    by_q, _, g = base_rate_table(grid, before)
    ref = g.loc[g["t"].dt.year == 2024, "y"].mean()
    late = by_q[by_q.index >= pd.Period("2025Q1", "Q")]
    bad = late[late["base_rate"] < ratio * ref]
    if len(bad):
        raise DataQualityError(f"base rate collapse vs 2024 avg {ref:.4f}: {bad['base_rate'].to_dict()}")
    return ref
