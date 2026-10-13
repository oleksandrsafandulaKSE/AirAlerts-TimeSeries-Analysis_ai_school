"""New-regime helpers (M4 plan §5): exposure, calibration-in-the-large, source separation, frozen-file checks."""
import dataclasses

import numpy as np
import pandas as pd
import pytest

from scripts import run_all
from src import config, data, evaluate, features, grid

ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731


def test_exposure_summary_by_hand():
    t = pd.date_range(ts("2026-09-13 00:00"), periods=10, freq="h")
    g = pd.DataFrame({"unit": "A", "group": "rear", "t": t, "active_at_t": [0, 0, 1, 1, 0, 0, 0, 1, 0, 0]})
    onsets = {"A": np.array(["2026-09-13T01:30", "2026-09-13T06:40", "2026-09-13T00:20"], dtype="datetime64[ns]")}
    zone = ((ts("2026-09-12 00:00"), ts("2026-09-13 00:30")),)   # hour 00:00 partly unknown -> not exposed
    out = evaluate.exposure_summary(g, onsets, t[0], t[-1] + pd.Timedelta(hours=1), zone).iloc[0]
    assert out["exposed_hours"] == 9 and out["onsets"] == 2 and out["active_hours"] == 3
    assert out["onsets_per_30d"] == pytest.approx(2 / (9 / 720))
    assert out["share_under_alert"] == pytest.approx(3 / 9)
    pooled = evaluate.pooled_by_group(pd.DataFrame([out]))
    assert pooled.set_index("group").loc["rear", "onsets"] == 2


def test_calibration_in_the_large_by_hand():
    s = pd.DataFrame({"group": ["rear", "rear", "frontline"], "y": [0, 1, 1], "m": [0.2, 0.4, 0.9]})
    c = evaluate.calibration_in_the_large(s, ["m"]).set_index("group")
    assert c.loc["rear", "mean_pred"] == pytest.approx(0.3) and c.loc["rear", "mean_obs"] == 0.5
    assert c.loc["overall", "pred_minus_obs"] == pytest.approx(0.5 - 2 / 3)


def test_sources_never_mix():
    a = pd.DataFrame({"source": ["api", "official"]})
    with pytest.raises(data.DataQualityError):
        run_all.check_source(a, "api")
    run_all.check_source(a.iloc[[0]], "api")


def test_history_start_zone_masks_and_nans():
    c = dataclasses.replace(config.new_regime(), H=pd.Timedelta(hours=1))
    hs = c.history_start                                                   # 2026-09-12 17:00:43
    al = pd.DataFrame([{"source": "api", "alert_id": "1", "unit": "kyiv_city", "level": "raion",
                        "started_at": ts("2026-09-14 10:10"), "finished_at": ts("2026-09-14 10:40"), "alert_level": "yellow"}])
    g = grid.build_grid(al, ts("2026-09-13 00:00"), ts("2026-09-22 00:00"), c.H, unit_list=["kyiv_city"],
                        approved_gaps=config.mask_gaps(c)).set_index("t")
    assert g.loc[ts("2026-09-13 17:00"), "gap_mask"] == 1                  # t < hs + 24h
    assert g.loc[ts("2026-09-13 18:00"), "gap_mask"] == 0
    f = features.build_features(al, pd.DatetimeIndex([ts("2026-09-14 12:00"), ts("2026-09-20 17:00"),
                                                      ts("2026-09-20 18:00")]), config.uncertainty_zones(c),
                                unit_list=["kyiv_city"], neighbours={"kyiv_city": set()}).set_index("t")
    # zone ends at hs + 24h = 09-13 17:00:43, so a 7-day window is clean from 09-20 17:00:43 on
    assert np.isnan(f.loc[ts("2026-09-14 12:00"), "onsets_last_7d"])
    assert np.isnan(f.loc[ts("2026-09-20 17:00"), "onsets_last_7d"])
    assert f.loc[ts("2026-09-20 18:00"), "onsets_last_7d"] == 1
    assert f.loc[ts("2026-09-14 12:00"), "minutes_since_last_start"] == 110  # event after the zone: known


def test_frozen_files_must_match_preregistration(tmp_path):
    with pytest.raises(data.DataQualityError):
        run_all._verify_prereg(tmp_path, tmp_path / "x.csv")              # no preregistration
