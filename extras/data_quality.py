"""M9 §A and §E3: raising data-quality pins that live outside the fingerprinted pipeline code."""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError
from src.grid import unit_intervals

# Whole-file pins on the frozen official file (after dedup + Luhanska exclusion), M9 §A.
# 3600 s: the parser closes an alert without an all-clear at started_at + 1h (plans/notes/fabricated_1h_ends.md).
# 1800 s: D-010, kept as-is (no parser rule produces them).
EXPECTED_EXACT = {
    3600: {"total": 255, "by_level": {"hromada": 109, "raion": 87, "oblast": 59}},
    1800: {"total": 38, "by_level": {"oblast": 24, "raion": 13, "hromada": 1}},
}
NOTE = "plans/notes/fabricated_1h_ends.md"

# E3 onset-collapse check across the Dec-2025 admin reform (PROVISIONAL thresholds, M9 consensus)
COLLAPSE_EARLY = (pd.Timestamp("2025-09-01", tz="UTC"), pd.Timestamp("2025-12-01", tz="UTC"))
COLLAPSE_LATE = (pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-04-01", tz="UTC"))
COLLAPSE_MIN_EARLY = 10
COLLAPSE_RATIO = 0.25


def exact_duration_counts(alerts, seconds):
    """Alerts lasting exactly `seconds` (open alerts never count): {total, by_level}."""
    dur = alerts["finished_at"] - alerts["started_at"]
    m = (dur == pd.Timedelta(seconds=seconds)).fillna(False).astype(bool)
    return {"total": int(m.sum()), "by_level": {k: int(v) for k, v in alerts.loc[m, "level"].value_counts().items()}}


def check_exact_durations(alerts, expected=EXPECTED_EXACT):
    """Raise if any pinned exact-duration count moved; return the counts."""
    out = {}
    for sec, exp in expected.items():
        got = exact_duration_counts(alerts, sec)
        out[sec] = got
        if got != exp:
            raise DataQualityError(f"exactly-{sec} s durations changed: got {got}, expected {exp} (see {NOTE})")
    return out


def onset_rate_ratios(alerts, cap, early=COLLAPSE_EARLY, late=COLLAPSE_LATE, unit_list=None):
    """Per unit: onsets per 30 days in `early` and `late` (D-020 union onsets) and late/early."""
    unit_list = regions.units() if unit_list is None else list(unit_list)
    ivs = unit_intervals(alerts, cap)
    days = lambda w: (w[1] - w[0]) / pd.Timedelta(days=30)  # noqa: E731
    naive = lambda x: np.datetime64(x.tz_convert("UTC").tz_localize(None), "ns")  # noqa: E731
    rows = []
    for u in unit_list:
        on = ivs[u][2] if u in ivs else np.array([], dtype="datetime64[ns]")
        n_e = int(((on >= naive(early[0])) & (on < naive(early[1]))).sum())
        n_l = int(((on >= naive(late[0])) & (on < naive(late[1]))).sum())
        r_e, r_l = n_e / days(early), n_l / days(late)
        rows.append({"unit": u, "early_onsets": n_e, "late_onsets": n_l, "early_per_30d": r_e,
                     "late_per_30d": r_l, "ratio": r_l / r_e if n_e else np.nan})
    return pd.DataFrame(rows)


def check_onset_collapse(alerts, cap, min_early=COLLAPSE_MIN_EARLY, threshold=COLLAPSE_RATIO, **kw):
    """Raise if a unit has < min_early early onsets or its later rate fell below threshold × earlier."""
    r = onset_rate_ratios(alerts, cap, **kw)
    few = r[r.early_onsets < min_early]
    if len(few):
        raise DataQualityError(f"units with < {min_early} onsets in the early window: {few.unit.tolist()}")
    low = r[r.ratio < threshold]
    if len(low):
        raise DataQualityError(f"onset collapse across the admin reform (ratio < {threshold}): "
                               f"{dict(zip(low.unit, low.ratio.round(3)))}")
    return r
