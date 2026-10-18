"""Per type x H: grid (y, mask), features known at t and `other_level_active_at_t` -> one frame (plans/M6c-1.md §4–5).
Everything goes through the unchanged src.grid / src.features code; a type is a pre-filtered alert subset."""
from dataclasses import replace

import numpy as np
import pandas as pd

from src import config as config_mod, data, features, grid, regions
from newregime.data import OTHER, typed

HOUR = pd.Timedelta(hours=1)
OTHER_COL = "other_level_active_at_t"


def feature_list(typ):
    """ANY = the official recipe; YELLOW / RED add the other level's state at t."""
    return list(features.FEATURES) + ([] if typ == "any" else [OTHER_COL])


def run_config(split, cov, H):
    """A src RunConfig for the API source. Holes become national missing-data intervals (D-039 contract) and get the
    official gap treatment through src.config.mask_gaps / uncertainty_zones."""
    test_end = split.test_end
    return replace(config_mod.new_regime(), name=f"m6c1_{split.name}_h{int(H / HOUR)}",
                   grid_start=split.grid_start, grid_end=test_end - H + HOUR, coverage_end=cov.coverage_end,
                   train=split.train, val=split.val, test=(split.test_start, test_end), H=H,
                   history_start=cov.history_start, approved_gaps=tuple(cov.holes),
                   data_path="datastore/alerts_in_ua.csv")


def check_national_gaps(alerts, cfg, end):
    """National runs >= 24 h with no onset in [history_start, end) must lie inside a recorded hole (raise otherwise)."""
    detected = grid.detect_gaps(alerts, cfg.gap_min_hours, cfg.history_start, end)
    for d0, d1 in detected:
        if not any(h0 <= d0 and d1 <= h1 for h0, h1 in cfg.approved_gaps):
            raise data.DataQualityError(f"national no-onset run [{d0}, {d1}) is not a recorded hole")
    return detected


def other_active(alerts, typ, times, zones, cap):
    """The OTHER type's active state per (unit, t) under the 24 h cap; NaN inside uncertainty zones."""
    a = typed(alerts, OTHER[typ])
    ivs = grid.unit_intervals(a, cap)
    t = pd.DatetimeIndex(times).tz_localize(None).to_numpy("datetime64[ns]")
    in_zone = np.zeros(len(t), dtype=bool)
    for z0, z1 in zones:
        in_zone |= (t >= grid._naive(z0)) & (t < grid._naive(z1))
    empty = np.array([], dtype="datetime64[ns]")
    parts = []
    for u in regions.units():
        ms, me, _ = ivs.get(u, (empty, empty, empty))
        act = grid._covered(t, ms, me).astype(float)
        act[in_zone] = np.nan
        parts.append(pd.DataFrame({"unit": u, "t": pd.DatetimeIndex(times), OTHER_COL: act}))
    return pd.concat(parts, ignore_index=True)


def typed_features(alerts, times, zones, typ, cap=pd.Timedelta(hours=24)):
    """Feature rows (unit, t) for type `typ` from `alerts` (any truncation the caller applied). Used by the pipeline AND
    the truncation test, so both test the same code."""
    f = features.build_features(typed(alerts, typ), times, zones, cap, "any")
    if typ != "any":
        f = f.merge(other_active(alerts, typ, times, zones, cap), on=["unit", "t"], how="left", validate="one_to_one")
    return f


def build_frame(alerts, cfg, typ):
    """Grid (y, mask for THIS type) joined 1:1 with the type's features."""
    a = typed(alerts, typ)
    g = grid.build_grid(a, cfg.grid_start, cfg.grid_end, cfg.H, "any", cfg.standing_cap, config_mod.mask_gaps(cfg),
                        cfg.post_gap_mask, coverage_end=cfg.coverage_end)
    if g["unit"].nunique() != 24:
        raise data.DataQualityError("grid does not have 24 units")
    if ((g["mask"] == 0) & (g["active_at_t"] == 1)).any():
        raise data.DataQualityError(f"{typ}: unmasked row is under an alert of its own type")
    times = pd.DatetimeIndex(g["t"].drop_duplicates().sort_values())
    f = typed_features(alerts, times, config_mod.uncertainty_zones(cfg), typ, cfg.standing_cap)
    gf = features.join_to_grid(g, f)
    gf["type"] = typ
    return gf


def onsets_by_unit(alerts, typ, cap=pd.Timedelta(hours=24)):
    """Merged type-T onsets per unit (naive UTC datetime64), as used by the targets."""
    return {u: v[2] for u, v in grid.unit_intervals(typed(alerts, typ), cap).items()}
