"""M10 §A (plans/M10.md): the L1 label variant (hromada-level rows dropped before the union) as a MEASUREMENT.
L0 = the current rule. Nothing here changes the target, the mask or the headline; src/ is used read-only."""
import numpy as np
import pandas as pd

from src import config as config_mod, evaluate, features, grid
from src.data import DataQualityError

VARIANTS = ("L0", "L1")


def drop_hromada(alerts):
    """L1: the shared-format frame without level == 'hromada' rows (a proxy for non-air-raid rows; no name lists)."""
    levels = set(alerts["level"].unique())
    if "hromada" not in levels:
        raise DataQualityError(f"no hromada rows to drop (levels {sorted(levels)})")
    return alerts[alerts["level"] != "hromada"].copy()


def variant_alerts(alerts, variant):
    if variant == "L0":
        return alerts
    if variant == "L1":
        return drop_hromada(alerts)
    raise ValueError(f"unknown variant {variant!r}")


def build_variant_frames(alerts, cfg):
    """Grid + features for one variant with the frozen M1/M2 functions (same D-020 cap, gaps, post-gap mask)."""
    g = grid.build_grid(alerts, cfg.grid_start, cfg.grid_end, cfg.H, cfg.target_levels, cfg.standing_cap,
                        config_mod.mask_gaps(cfg), cfg.post_gap_mask, coverage_end=cfg.coverage_end)
    if ((g["mask"] == 0) & (g["active_at_t"] == 1)).any():
        raise DataQualityError("unmasked row is under alert")
    times = pd.DatetimeIndex(g["t"].drop_duplicates().sort_values())
    f = features.build_features(alerts, times, config_mod.uncertainty_zones(cfg), cfg.standing_cap, cfg.target_levels)
    return g, features.join_to_grid(g, f)


# ---------------------------------------------------------------- A2: onset accounting
def onset_accounting(ms0, me0, on0, on1):
    """Mutually exclusive classes for one unit (plan §A2). ms0/me0: L0 merged (capped) intervals; on0/on1: onsets.
    Returns (l0_class, l1_class, shift_minutes) with l0_class[i] in {kept, shifted, disappeared} for on0[i] and
    l1_class[j] in {matched, shift_target, new} for on1[j]."""
    on0, on1 = np.asarray(on0, "datetime64[ns]"), np.asarray(on1, "datetime64[ns]")
    start_to_end = dict(zip(ms0.tolist(), me0.tolist()))
    set1 = set(on1.tolist())
    l0, shifts = [], []
    l1 = np.array(["new"] * len(on1), dtype=object)
    for s in on0:
        e = start_to_end.get(s.tolist(), s)          # zero-duration onset (not a merged start): empty interval
        if s.tolist() in set1:
            l0.append("kept")
            l1[np.searchsorted(on1, s)] = "matched"
            continue
        lo, hi = np.searchsorted(on1, s, side="right"), np.searchsorted(on1, e, side="left")
        if hi > lo:                                   # >= 1 L1 onset in (s, e)
            l0.append("shifted")
            l1[lo] = "shift_target"
            shifts.append((on1[lo] - s) / np.timedelta64(1, "m"))
        else:
            l0.append("disappeared")
    l0 = np.array(l0, dtype=object)
    n = {k: int((l0 == k).sum()) for k in ("kept", "shifted", "disappeared")}
    m = {k: int((l1 == k).sum()) for k in ("matched", "shift_target", "new")}
    if sum(n.values()) != len(on0) or sum(m.values()) != len(on1) or m["matched"] != n["kept"] \
            or m["shift_target"] != n["shifted"]:
        raise DataQualityError(f"A2 invariants failed: L0 {n} of {len(on0)}, L1 {m} of {len(on1)}")
    return l0, l1, np.array(shifts, float)


def _in(x, a, b):
    """Boolean mask x in [a, b) for naive UTC datetime64 x and tz-aware bounds (periods may overlap)."""
    lo, hi = (np.datetime64(v.tz_convert("UTC").tz_localize(None), "ns") for v in (a, b))
    return (x >= lo) & (x < hi)


def onset_changes(alerts0, alerts1, cap, periods):
    """A2 per unit x period: L0 kept / shifted / disappeared, L1 matched / shift target / new, the median shift, and
    the median duration of the hromada rows starting at a disappeared (resp. shifted) L0 onset."""
    iv0, iv1 = grid.unit_intervals(alerts0, cap), grid.unit_intervals(alerts1, cap)
    h = alerts0[alerts0["level"] == "hromada"]
    hs = h["started_at"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")
    hd = ((h["finished_at"] - h["started_at"]) / pd.Timedelta(minutes=1)).to_numpy(float)   # NaN for open ends
    hu = h["unit"].to_numpy()
    empty = np.array([], "datetime64[ns]")
    rows = []
    for u in sorted(iv0):
        ms0, me0, on0 = iv0[u]
        on1 = iv1.get(u, (empty, empty, empty))[2]
        c0, c1, _ = onset_accounting(ms0, me0, on0, on1)
        sh_t, sh_m = [], []
        for s, cls in zip(on0, c0):                # shift minutes aligned with on0 rows for per-period medians
            if cls == "shifted":
                lo = np.searchsorted(on1, s, side="right")
                sh_t.append(s)
                sh_m.append((on1[lo] - s) / np.timedelta64(1, "m"))
        sh_t, sh_m = np.array(sh_t, "datetime64[ns]"), np.array(sh_m, float)
        hu_s, hu_d = hs[hu == u], hd[hu == u]
        for name, a, b in periods:
            i0, i1 = _in(on0, a, b), _in(on1, a, b)
            k0, k1 = c0[i0], c1[i1]
            dis = on0[i0 & (c0 == "disappeared")]
            shf = on0[i0 & (c0 == "shifted")]
            d_dis = hu_d[np.isin(hu_s, dis)] if len(dis) else np.array([])
            d_shf = hu_d[np.isin(hu_s, shf)] if len(shf) else np.array([])
            in_p = _in(sh_t, a, b)
            rows.append({"unit": u, "period": name, "l0_onsets": len(k0), "kept": int((k0 == "kept").sum()),
                         "shifted": int((k0 == "shifted").sum()), "disappeared": int((k0 == "disappeared").sum()),
                         "l1_onsets": len(k1), "matched": int((k1 == "matched").sum()),
                         "shift_target": int((k1 == "shift_target").sum()), "new_in_l1": int((k1 == "new").sum()),
                         "median_shift_min": float(np.median(sh_m[in_p])) if in_p.any() else np.nan,
                         "median_hromada_min_disappeared": float(np.nanmedian(d_dis)) if np.isfinite(d_dis).any() else np.nan,
                         "median_hromada_min_shifted": float(np.nanmedian(d_shf)) if np.isfinite(d_shf).any() else np.nan})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- A1: descriptive table
def describe(g, alerts, cap, periods, zones, H):
    """A1 per unit and pooled group x period. Onsets per 30 days and share under alert use evaluate.exposure_summary
    (hours outside the applied uncertainty zone); base rate = mean y over eligible rows with t + H <= period end."""
    ivs = grid.unit_intervals(alerts, cap)
    onsets = {u: v[2] for u, v in ivs.items()}
    dur = alerts["finished_at"] - alerts["started_at"]
    rows = []
    for name, a, b in periods:
        per = evaluate.exposure_summary(g, onsets, a, b, zones)
        per = pd.concat([per, evaluate.pooled_by_group(per)], ignore_index=True)
        el = g[(g["t"] >= a) & (g["t"] < b) & (g["t"] + H <= b) & (g["mask"] == 0) & g["y"].notna()]
        el = el.assign(group=el["group"])
        long = alerts[(alerts["started_at"] >= a) & (alerts["started_at"] < b) & (dur > pd.Timedelta(hours=24))]
        for _, r in per.iterrows():
            if r["unit"].startswith("["):
                grp = r["group"]
                sel = el if grp == "overall" else el[el["group"] == grp]
                lg = long if grp == "overall" else long[long["unit"].map(dict(zip(g["unit"], g["group"]))) == grp]
            else:
                sel, lg = el[el["unit"] == r["unit"]], long[long["unit"] == r["unit"]]
            rows.append({"period": name, "unit": r["unit"], "group": r["group"], "onsets": int(r["onsets"]),
                         "exposed_hours": int(r["exposed_hours"]), "onsets_per_30d": r["onsets_per_30d"],
                         "share_under_alert": r["share_under_alert"], "unmasked_rows": len(sel),
                         "positives": int(sel["y"].sum()), "base_rate": float(sel["y"].mean()) if len(sel) else np.nan,
                         "alerts_over_24h": len(lg),
                         "alerts_over_24h_by_level": ";".join(f"{k}:{v}" for k, v in
                                                              sorted(lg["level"].value_counts().items()))})
    return pd.DataFrame(rows)


def side_by_side(t0, t1, keys=("period", "unit", "group")):
    keys = list(keys)
    m = t0.merge(t1, on=keys, suffixes=("_L0", "_L1"), how="outer", validate="one_to_one")
    for c in ("onsets", "onsets_per_30d", "share_under_alert", "unmasked_rows", "base_rate", "alerts_over_24h"):
        m[f"{c}_diff"] = m[f"{c}_L1"] - m[f"{c}_L0"]
    return m
