"""M10 §C leakage (plans/M10.md): block D (hours under alert) is unchanged when the RAW data after t is removed
(starts > t dropped, ends > t hidden), at pinned real witnesses; a deliberately leaky version (no clipping at t:
the full capped duration of every interval that starts in the window) is caught at an exact, non-empty witness set.
Plus the real-data L0 onset pin (§A: L0 = the frozen rule)."""
import numpy as np
import pandas as pd
import pytest

from improve import exposure as EX, labels_variant as LV
from src import grid
from tests.test_improve_leakage import CFG, ZONES, lypetska, real, truncate, ts  # noqa: F401  (fixture reuse)

H = CFG.H
UNIT = "kyiv_city"


def block_d(alerts, t):
    g = pd.DataFrame({"unit": list(dict.fromkeys(alerts["unit"])), "t": t})
    return EX.exposure_features(alerts, g, CFG.standing_cap, ZONES).set_index("unit")[EX.BLOCK_D]


def leaky_d(alerts, t):
    """Leaky, all units: full capped duration (hours) of every merged interval STARTING in (t - 24 h, t], NOT clipped
    at t (reads ends not yet known at t)."""
    tt = np.datetime64(t.tz_convert("UTC").tz_localize(None), "ns")
    out = {}
    for u, (ms, me, _) in grid.unit_intervals(alerts, CFG.standing_cap).items():
        sel = (ms > tt - np.timedelta64(24, "h")) & (ms <= tt)
        out[u] = float(((me[sel] - ms[sel]) / np.timedelta64(1, "h")).sum())
    return pd.Series(out)


def caught_at(alerts, t):
    return not leaky_d(alerts, t).equals(leaky_d(truncate(alerts, t), t))


def witnesses(alerts):
    """Pinned (t) cases in Kyiv City validation + Kharkivska standing alert + gap edges + DST day."""
    _, _, on = grid.unit_intervals(alerts[alerts.unit == UNIT], CFG.standing_cap)[UNIT]
    a = alerts[(alerts.unit == UNIT) & (alerts.started_at >= CFG.val[0] + pd.Timedelta(days=2))
               & (alerts.started_at < CFG.test[0]) & alerts.finished_at.notna()].sort_values("started_at")
    running = next(r for _, r in a.iterrows() if r.finished_at.floor("h") > r.started_at.ceil("h"))
    t_active = running.started_at.ceil("h")                                   # alert active at t, ends after t
    k = alerts[(alerts.unit == UNIT) & alerts.finished_at.notna()]
    ends_at = k[k.finished_at == k.finished_at.dt.floor("h")].sort_values("finished_at")
    t_end = ends_at.iloc[0].finished_at if len(ends_at) else None             # an alert ending exactly at t
    on = pd.to_datetime(on).tz_localize("UTC")
    nxt = on[(on >= CFG.val[0] + pd.Timedelta(days=2)) & (on.minute != 0)][0]
    t_before_start = nxt.floor("h")                                           # an alert starts in (t, t + 1 h]
    L = lypetska(alerts)
    (g0, g1), = CFG.approved_gaps
    out = [t_active, t_before_start, (L.started_at + pd.Timedelta(hours=30)).floor("h"), g0, g0 - H,
           g1 + pd.Timedelta(hours=24), ts("2025-10-26 01:00"), ts("2026-03-29 02:00"), CFG.test[0] - H]
    return [x for x in out + ([t_end] if t_end is not None else []) if x is not None]


def test_block_d_truncation_invariant(real):
    for t in witnesses(real):
        full, cut = block_d(real, t), block_d(truncate(real, t), t)
        pd.testing.assert_frame_equal(full, cut, check_dtype=False, obj=f"block D at {t}")


CAUGHT = ["2026-07-01 17:00:00+00:00", "2026-07-01 16:00:00+00:00", "2024-05-13 14:00:00+00:00",   # pinned on the
          "2026-08-29 00:00:00+00:00", "2026-08-28 23:00:00+00:00", "2026-09-04 00:00:00+00:00",   # official file
          "2025-10-26 01:00:00+00:00", "2026-03-29 02:00:00+00:00", "2026-07-26 23:00:00+00:00",   # (all 10 witnesses)
          "2026-08-05 07:00:00+00:00"]
L0_ONSETS = 84_581          # all merged-unit onsets of the official file under the frozen rule (D-020 cap)


def test_block_d_negative_control_pinned(real):
    t = witnesses(real)[0]                         # the alert active at t that ends after t
    assert caught_at(real, t)
    full, cut = block_d(real, t), block_d(truncate(real, t), t)
    assert full.loc[UNIT, "under_alert_hours_24h"] == cut.loc[UNIT, "under_alert_hours_24h"]
    assert [str(w) for w in witnesses(real) if caught_at(real, w)] == CAUGHT


def test_l0_is_the_frozen_rule(real):
    """L0 = the input frame; L1 removes exactly the hromada rows (real counts pinned after M10's first run)."""
    assert LV.variant_alerts(real, "L0") is real
    a1 = LV.variant_alerts(real, "L1")
    assert len(real) - len(a1) == int((real.level == "hromada").sum()) == 20_812
    assert set(a1.level) == {"oblast", "raion"}
    on = grid.unit_intervals(LV.variant_alerts(real, "L0"), CFG.standing_cap)
    assert sum(len(v[2]) for v in on.values()) == L0_ONSETS
