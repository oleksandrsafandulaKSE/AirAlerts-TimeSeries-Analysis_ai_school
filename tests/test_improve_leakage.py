"""M7 leakage (plans/M7.md §5): every new input is unchanged when the RAW data after t is removed (starts > t dropped,
ends > t hidden); a deliberately leaky version of each block is caught at a pinned witness."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from improve import features_plus as FP
from src import config, data, grid

ROOT = Path(__file__).resolve().parents[1]
CFG = config.official()
H = CFG.H
ZONES = config.uncertainty_zones(CFG)
COLS = FP.BLOCK_A + FP.BLOCK_B + FP.BLOCK_C + ["offset_rate", "prior_q"]


def ts(s):
    return pd.Timestamp(s, tz="UTC")


@pytest.fixture(scope="module")
def real():
    p = ROOT / "data" / "official_data_en.csv"
    if not p.exists():
        pytest.fail(f"{p} missing: run scripts/run_all.py --config official once to download it")
    return data.load_official(p, CFG)


def truncate(alerts, t):
    a = alerts[alerts["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


def plus_at(alerts, t, H_rates=H):  # noqa: D401
    g = grid.build_grid(alerts, CFG.grid_start, t + H, H, approved_gaps=config.mask_gaps(CFG))
    lr = FP.label_rates(g.sort_values(["unit", "t"]), H_rates, ZONES)
    ev = FP.event_features(alerts, g.sort_values(["unit", "t"]), CFG.standing_cap, ZONES)
    out = lr.merge(ev, on=["unit", "t"])
    return out[out["t"] == t].set_index("unit")[COLS], g


def lypetska(alerts):
    a = alerts[(alerts.unit == "kharkivska") & (alerts.level == "hromada")
               & (alerts.started_at.dt.strftime("%Y-%m-%d") == "2024-05-12")
               & ((alerts.finished_at - alerts.started_at) > pd.Timedelta(days=400))]
    assert len(a) == 1
    return a.iloc[0]


def audit_times(alerts):
    L = lypetska(alerts)
    (g0, g1), = CFG.approved_gaps
    return [CFG.val[0], ts("2025-06-15 13:00"), ts("2025-10-26 01:00"),
            (L.started_at + pd.Timedelta(hours=2)).floor("h"), (L.started_at + pd.Timedelta(hours=30)).floor("h"),
            g0, g1 + pd.Timedelta(hours=24), CFG.test[0] - H, CFG.test[0]]


def test_m7_inputs_truncation_invariant(real):
    for t in audit_times(real):
        full, _ = plus_at(real, t)
        cut, _ = plus_at(truncate(real, t), t)
        pd.testing.assert_frame_equal(full, cut, check_dtype=False, obj=f"M7 inputs at {t}")


def witness(real):
    """A Kyiv City onset o in validation with a non-zero minute whose hour row floor(o) is eligible (y = 1)."""
    _, _, on = grid.unit_intervals(real[real.unit == "kyiv_city"], CFG.standing_cap)["kyiv_city"]
    on = pd.to_datetime(on).tz_localize("UTC")
    g = grid.build_grid(real[real.unit == "kyiv_city"], CFG.val[0], CFG.test[0], H, unit_list=["kyiv_city"]).set_index("t")
    for o in on[(on >= CFG.val[0] + pd.Timedelta(days=2)) & (on < CFG.test[0]) & (on.minute != 0)]:
        t = o.floor("h")
        if g.loc[t, "mask"] == 0 and g.loc[t, "y"] == 1:
            return o, t
    raise AssertionError("no witness")


def leaky_label_sum(alerts, t):
    """Negative control A: a 14-day label window that ends AT t, i.e. includes y(t) (onset in (t, t+1h], unknown at t)."""
    g = grid.build_grid(alerts[alerts.unit == "kyiv_city"], t - pd.Timedelta(days=15), t + H, H, unit_list=["kyiv_city"],
                        approved_gaps=config.mask_gaps(CFG))
    w = g[(g["t"] >= t - pd.Timedelta(days=14)) & (g["t"] <= t) & (g["mask"] == 0) & g["y"].notna()]
    return float(w["y"].sum())


def test_negative_control_A_rate_reading_label_of_t(real):
    o, t = witness(real)
    assert leaky_label_sum(real, t) != leaky_label_sum(truncate(real, t), t)
    ok_full, _ = plus_at(real, t)
    ok_cut, _ = plus_at(truncate(real, t), t)
    assert ok_full.loc["kyiv_city", "rate_14d"] == ok_cut.loc["kyiv_city", "rate_14d"]


def national_onsets_window(alerts, t, lo, hi):
    ivs = grid.unit_intervals(alerts, CFG.standing_cap)
    on = pd.to_datetime(np.concatenate([v[2] for v in ivs.values()])).tz_localize("UTC")
    return int(((on > t + lo) & (on <= t + hi)).sum())


def test_negative_control_B_wave_window_reaching_past_t(real):
    o, t = witness(real)
    leaky = lambda al: national_onsets_window(al, t, -pd.Timedelta(hours=3), pd.Timedelta(hours=1))  # noqa: E731
    assert leaky(real) != leaky(truncate(real, t))
    full, _ = plus_at(real, t)
    cut, _ = plus_at(truncate(real, t), t)
    assert full.loc["kyiv_city", "national_onsets_3h"] == cut.loc["kyiv_city", "national_onsets_3h"]


def test_negative_control_C_same_time_tomorrow(real):
    o, _ = witness(real)
    t = o.floor("h") - pd.Timedelta(hours=24)
    def tomorrow(al):
        _, _, on = grid.unit_intervals(al[al.unit == "kyiv_city"], CFG.standing_cap)["kyiv_city"]
        on = pd.to_datetime(on).tz_localize("UTC")
        return int(((on >= t + pd.Timedelta(hours=23)) & (on <= t + pd.Timedelta(hours=25))).sum())
    assert tomorrow(real) >= 1 and tomorrow(truncate(real, t)) == 0
    full, _ = plus_at(real, t)
    cut, _ = plus_at(truncate(real, t), t)
    assert full.loc["kyiv_city", "onset_same_time_yesterday"] == cut.loc["kyiv_city", "onset_same_time_yesterday"]
