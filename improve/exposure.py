"""M10 §C (plans/M10.md): hours under alert in (t - w, t] for w = 3 h, 24 h, 7 d.

Per unit: the D-020-capped merged intervals (grid.unit_intervals, end = min(finished_at, started_at + 24 h)), each
clipped at t. A capped end <= t is known at t (either the alert finished by t or its 24 h cap passed), and nothing
after t is read, so the value is causal. Gap rule (D-023): NaN iff (t - w, t] meets an applied uncertainty zone.
Known limitation (M9 A5): an end written later by the parser's 1-hour imputation is invisible to truncation tests."""
import numpy as np
import pandas as pd

from src.grid import check_units, unit_intervals

from improve.features_plus import _naive, _zone_nan, _zones_naive

WINDOWS = {"under_alert_hours_3h": np.timedelta64(3, "h"), "under_alert_hours_24h": np.timedelta64(24, "h"),
           "under_alert_hours_7d": np.timedelta64(7 * 24, "h")}
BLOCK_D = list(WINDOWS)
HOUR_NS = np.timedelta64(1, "h").astype("timedelta64[ns]").astype(float)


def covered_until(ms, me, x):
    """Total covered length (ns, float) of the disjoint sorted intervals [ms, me) inside (-inf, x]."""
    if not len(ms):
        return np.zeros(len(x))
    if np.isnat(ms).any() or np.isnat(me).any() or (me < ms).any() or (ms[1:] < me[:-1]).any():
        raise ValueError("covered_until needs sorted, disjoint intervals without NaT")
    ln = (me - ms).astype("timedelta64[ns]").astype(float)
    cum = np.concatenate([[0.0], np.cumsum(ln)])
    j = np.searchsorted(ms, x, side="right")              # intervals starting at or before x
    out = cum[np.clip(j - 1, 0, None)]
    k = np.clip(j - 1, 0, None)
    part = np.minimum((x - ms[k]).astype("timedelta64[ns]").astype(float), ln[k])
    out = np.where(j > 0, out + np.maximum(part, 0.0), 0.0)
    return out


def exposure_features(alerts, g, cap=pd.Timedelta(hours=24), zones=()):
    """Block D for every grid row (unit, t)."""
    units = list(dict.fromkeys(g["unit"]))
    check_units(alerts, units)
    ivs = unit_intervals(alerts, cap)
    empty = np.array([], dtype="datetime64[ns]")
    zn = _zones_naive(zones)
    parts = []
    for u in units:
        gu = g[g["unit"] == u]
        t = _naive(gu["t"])
        ms, me, _ = ivs.get(u, (empty, empty, empty))
        c_t = covered_until(ms, me, t)
        f = {"unit": u, "t": gu["t"].to_numpy()}
        for name, w in WINDOWS.items():
            v = (c_t - covered_until(ms, me, t - w)) / HOUR_NS
            v[_zone_nan(t, w, zn)] = np.nan
            f[name] = v
        parts.append(pd.DataFrame(f))
    return pd.concat(parts, ignore_index=True)
