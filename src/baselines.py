"""The four baselines (M3). Frozen ones fit on eligible TRAIN rows only; the rolling recent rate
reads only labels of rows s <= t - H (known at t). Every function returns one value per score row."""
import numpy as np
import pandas as pd

from src.data import DataQualityError
from src.grid import unit_intervals

BASELINES = ["climatology", "recent_rate", "persistence_raw", "persistence_calibrated"]


def _naive(ts):
    return ts.dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")


def unit_train_rates(fit):
    """p_unit = onset rate per unit on the fit set (eligible train rows)."""
    if fit["y"].isna().any():
        raise DataQualityError("fit set contains NaN labels")
    return fit.groupby("unit")["y"].mean()


def _p_unit_for(score, p_unit):
    p = score["unit"].map(p_unit)
    if p.isna().any():
        raise DataQualityError(f"units without train rows: {sorted(score.loc[p.isna(), 'unit'].unique())}")
    return p.to_numpy(float)


def _no_nan_keys(df, keys, name):
    if df[keys].isna().any().any():
        raise DataQualityError(f"{name}: NaN in keys {keys}")


def _cells(fit, keys):
    _no_nan_keys(fit, keys, "fit")
    return fit.groupby(keys)["y"].agg(k="sum", n="size").reset_index()


def _rate_from_cells(cells, score, keys, p_unit, alpha):
    _no_nan_keys(score, keys, "score")
    look = score[keys].merge(cells.set_index(keys)[["k", "n"]], left_on=keys, right_index=True, how="left")
    k = look["k"].fillna(0).to_numpy(float)
    n = look["n"].fillna(0).to_numpy(float)
    p0 = _p_unit_for(score, p_unit)
    return (k + alpha * p0) / (n + alpha)


CLIM_KEYS = ["unit", "hour_kyiv", "weekday_kyiv"]
PERS_KEYS = ["unit", "_bin"]


def climatology(fit, score, p_unit, alpha):
    """Per unit x Kyiv hour x Kyiv weekday train rate, shrunk toward p_unit."""
    return _rate_from_cells(_cells(fit, CLIM_KEYS), score, CLIM_KEYS, p_unit, alpha)


def persistence_bin(minutes, edges):
    b = pd.cut(minutes, bins=list(edges), right=False, labels=False)
    if pd.isna(b).any():
        raise DataQualityError("minutes_since_last_end outside the persistence bins (NaN or negative)")
    return np.asarray(b, dtype=int)


def persistence_calibrated(fit, score, p_unit, alpha, edges):
    """Per unit x bin(minutes_since_last_end) train rate, shrunk toward p_unit."""
    f = fit.assign(_bin=persistence_bin(fit["minutes_since_last_end"], edges))
    s = score.assign(_bin=persistence_bin(score["minutes_since_last_end"], edges))
    return _rate_from_cells(_cells(f, PERS_KEYS), s, PERS_KEYS, p_unit, alpha)


def recent_rate(history, score, p_unit, alpha, window, H, return_n=False):
    """Rolling rate over history rows s with t - window <= s <= t - H, mask(s) == 0, y(s) known,
    shrunk toward p_unit: (k + alpha * p_unit) / (n + alpha)."""
    p0 = _p_unit_for(score, p_unit)
    if history.duplicated(["unit", "t"]).any():
        raise DataQualityError("recent_rate: duplicate (unit, t) in history")
    k_out = np.zeros(len(score))
    n_out = np.zeros(len(score))
    hist = history[(history["mask"] == 0) & history["y"].notna()]
    for u, idx in score.groupby("unit").indices.items():  # positional, independent of the index labels
        sc = score.iloc[idx]
        h = hist[hist["unit"] == u].sort_values("t")
        ts = _naive(h["t"])
        ck = np.concatenate([[0.0], np.cumsum(h["y"].to_numpy(float))])
        t = _naive(sc["t"])
        lo = np.searchsorted(ts, t - window.to_timedelta64(), side="left")
        hi = np.searchsorted(ts, t - H.to_timedelta64(), side="right")
        k_out[idx] = ck[hi] - ck[lo]
        n_out[idx] = hi - lo
    p = (k_out + alpha * p0) / (n_out + alpha)
    return (p, n_out) if return_n else p


def persistence_raw(alerts, score, H, cap=pd.Timedelta(hours=24), target_levels="any"):
    """1 if a merged unit onset (D-023) lies in (t - H, t], else 0."""
    ivs = unit_intervals(alerts, cap, target_levels)
    out = np.zeros(len(score))
    empty = np.array([], dtype="datetime64[ns]")
    for u, idx in score.groupby("unit").indices.items():  # positional
        sc = score.iloc[idx]
        on = ivs.get(u, (empty, empty, empty))[2]
        t = _naive(sc["t"])
        n = np.searchsorted(on, t, side="right") - np.searchsorted(on, t - H.to_timedelta64(), side="right")
        out[idx] = (n > 0).astype(float)
    return out


def fit_tables(fit, cfg):
    """The frozen baseline state fitted on eligible TRAIN rows (M4: saved as baseline_fit.json, sha256 pre-registered)."""
    p_unit = unit_train_rates(fit)
    f = fit.assign(_bin=persistence_bin(fit["minutes_since_last_end"], cfg.persistence_bins))
    as_int = lambda c: c.astype({"k": int, "n": int})  # noqa: E731
    return {
        "alpha": cfg.shrink_alpha, "persistence_bins": list(cfg.persistence_bins),
        "p_unit": {u: float(v) for u, v in p_unit.items()},
        "climatology": as_int(_cells(fit, CLIM_KEYS)).to_dict(orient="records"),
        "persistence": as_int(_cells(f, PERS_KEYS)).to_dict(orient="records"),
    }


def predict_from_tables(tables, history, score, alerts, cfg):
    """All four baselines for the score rows from frozen tables + the rolling recent rate over `history`
    (labels of rows s <= t - H only) + raw persistence from the merged onsets."""
    if score.duplicated(["unit", "t"]).any():
        raise DataQualityError("score rows contain duplicate (unit, t)")
    p_unit = pd.Series(tables["p_unit"])
    alpha, edges = tables["alpha"], tables["persistence_bins"]
    clim = pd.DataFrame(tables["climatology"], columns=CLIM_KEYS + ["k", "n"])
    pers = pd.DataFrame(tables["persistence"], columns=PERS_KEYS + ["k", "n"])
    rr, n = recent_rate(history, score, p_unit, alpha, cfg.recent_window, cfg.H, return_n=True)
    s_bin = score.assign(_bin=persistence_bin(score["minutes_since_last_end"], edges))
    preds = pd.DataFrame({
        "unit": score["unit"].to_numpy(), "t": score["t"].to_numpy(),
        "climatology": _rate_from_cells(clim, score, CLIM_KEYS, p_unit, alpha),
        "recent_rate": rr,
        "persistence_raw": persistence_raw(alerts, score, cfg.H, cfg.standing_cap, cfg.target_levels),
        "persistence_calibrated": _rate_from_cells(pers, s_bin, PERS_KEYS, p_unit, alpha),
    })
    preds["t"] = pd.to_datetime(preds["t"], utc=True)
    return preds, p_unit, n


def predict_all(frame, alerts, fit, score, cfg):
    """All four baselines for the score rows. `frame` is the full (label-isolated) grid+features."""
    tables = fit_tables(fit, cfg)
    preds, p_unit, n = predict_from_tables(tables, frame, score, alerts, cfg)
    return preds, p_unit, n
