"""M9 §B and §D: block-bootstrap CI on Brier skill vs recent-rate, a row-weighted DM test, and calibration-in-the-large
CIs. Everything reads FROZEN saved predictions; nothing is refit."""
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError

SEED = 20261017
B = 10_000
NW_LAGS = (24, 72)
GROUPS = ("overall", "kyiv_city", "frontline", "rear")
SCHEMES = ("week", "day", "moving24h")
PRIMARY = "week"  # D-013 wording
FEW_BLOCKS = 10  # fewer blocks than this: a percentile interval is unreliable (flagged, never hidden)


def _utc(s):
    t = pd.to_datetime(s, utc=True)
    if str(t.dt.tz) != "UTC":
        raise DataQualityError("timestamps must be UTC")
    return t


def load_test(root):
    """Scored rows of the frozen H=1 final test: unit, t, group, y, p_model, p_rr."""
    path = Path(root) / "reports/official/test_predictions.csv"
    if not path.exists():
        raise DataQualityError(f"{path} missing")
    p = pd.read_csv(path, float_precision="round_trip")
    p["t"] = _utc(p["t"])
    s = p[p["status"] == "scored"].rename(columns={"p_recent_rate": "p_rr"})
    return _finish(s[["unit", "t", "y", "p_model", "p_rr"]])


def load_val(root):
    """Frozen validation rows: V0 p_headline (official) joined with recent_rate (improve), strict key/label checks."""
    a_path, b_path = Path(root) / "reports/official/val_predictions.csv", Path(root) / "reports/improve/validation_predictions.csv"
    for x in (a_path, b_path):
        if not x.exists():
            raise DataQualityError(f"{x} missing")
    a = pd.read_csv(a_path, float_precision="round_trip")
    b = pd.read_csv(b_path, float_precision="round_trip")
    for d in (a, b):
        d["t"] = _utc(d["t"])
        if d.duplicated(["unit", "t"]).any():
            raise DataQualityError("duplicate (unit, t) keys in validation predictions")
    ka, kb = set(zip(a.unit, a.t)), set(zip(b.unit, b.t))
    if ka != kb:
        raise DataQualityError(f"validation key sets differ: {len(ka - kb)} only official, {len(kb - ka)} only improve")
    m = a[["unit", "t", "y", "p_headline"]].merge(b[["unit", "t", "y", "recent_rate"]], on=["unit", "t"],
                                                    suffixes=("", "_i"), validate="one_to_one")
    if not np.array_equal(m["y"].to_numpy(), m["y_i"].to_numpy()):
        raise DataQualityError("validation labels differ between the two prediction files")
    m = m.rename(columns={"p_headline": "p_model", "recent_rate": "p_rr"})
    return _finish(m[["unit", "t", "y", "p_model", "p_rr"]])


def _finish(df):
    df = df.copy()
    if df[["y", "p_model", "p_rr"]].isna().any().any():
        raise DataQualityError("NaN in scored predictions")
    df["group"] = df["unit"].map(regions.group_of)  # canonical groups only (Kyiv City != Kyivska)
    df["lm"] = (df["p_model"] - df["y"]) ** 2
    df["lr"] = (df["p_rr"] - df["y"]) ** 2
    return df.sort_values(["t", "unit"], ignore_index=True)


def bss(df):
    sr = df["lr"].sum()
    if sr == 0:
        raise DataQualityError("reference Brier sum is zero")
    return 1 - df["lm"].sum() / sr


def block_ids(t, scheme):
    """Calendar block per row (UTC): week = Monday 00:00, day = date; moving24h uses hour indices instead."""
    naive = t.dt.tz_convert("UTC").dt.tz_localize(None)
    if scheme == "week":
        return (naive.dt.normalize() - pd.to_timedelta(naive.dt.weekday, unit="D")).to_numpy()
    if scheme == "day":
        return naive.dt.normalize().to_numpy()
    raise ValueError(scheme)


def resample_rows(df, scheme, rng, n_boot=B):
    """Yield arrays of row indices, one per bootstrap resample. All rows of a block (all units) move together."""
    if scheme in ("week", "day"):
        bid = block_ids(df["t"], scheme)
        keys, inv = np.unique(bid, return_inverse=True)
        members = [np.flatnonzero(inv == k) for k in range(len(keys))]
        for _ in range(n_boot):
            pick = rng.integers(0, len(keys), len(keys))
            yield np.concatenate([members[k] for k in pick])
    elif scheme == "moving24h":
        hours, inv = np.unique(df["t"].to_numpy(), return_inverse=True)
        members = [np.flatnonzero(inv == k) for k in range(len(hours))]
        n, L = len(hours), 24
        for _ in range(n_boot):
            starts = rng.integers(0, n, math.ceil(n / L))
            seq = (starts[:, None] + np.arange(L)[None, :]).ravel()[:n] % n  # circular wrap
            yield np.concatenate([members[k] for k in seq])
    else:
        raise ValueError(scheme)


def n_blocks(df, scheme):
    """Blocks per resample: calendar blocks, or ceil(scored hours / 24) moving 24 h blocks."""
    if scheme == "moving24h":
        return int(math.ceil(df["t"].nunique() / 24))
    return int(len(np.unique(block_ids(df["t"], scheme))))


def bootstrap_bss(df, scheme, n_boot=B, seed=SEED):
    """Percentile 95% CI of the ratio BSS (recomputed on each resample, never averaged per row/unit)."""
    rng = np.random.default_rng(seed)
    lm, lr = df["lm"].to_numpy(), df["lr"].to_numpy()
    vals = np.empty(n_boot)
    for i, idx in enumerate(resample_rows(df, scheme, rng, n_boot)):
        sr = lr[idx].sum()
        if sr == 0:
            raise DataQualityError("bootstrap resample with zero reference Brier sum")
        vals[i] = 1 - lm[idx].sum() / sr
    lo, hi = np.percentile(vals, [2.5, 97.5])
    k = n_blocks(df, scheme)
    return {"scheme": scheme, "blocks": k, "few_blocks_unreliable": k < FEW_BLOCKS,
            "scored_hours": int(df["t"].nunique()), "bss": float(bss(df)), "ci_low": float(lo),
            "ci_high": float(hi), "boot_mean": float(vals.mean()), "n_boot": n_boot, "seed": seed}


def newey_west(x, lags):
    x = np.asarray(x, float) - np.mean(x)
    n = len(x)
    v = x @ x / n
    for k in range(1, lags + 1):
        v += 2 * (1 - k / (lags + 1)) * (x[k:] @ x[:-k]) / n
    return v


def dm_test(df, lags=NW_LAGS):
    """Row-weighted DM: S_h = sum of d over the rows of hour h; z = sum S_h / sqrt(N_h * NW variance of S_h)."""
    d = df["lm"] - df["lr"]
    S = d.groupby(df["t"]).sum().sort_index().to_numpy()
    n_h = len(S)
    out = {"mean_d_row": float(d.mean()), "hours": n_h, "rows": int(len(d))}
    for L in lags:
        v = newey_west(S, L) if n_h > 2 * L else np.nan  # too few hours for this lag: undefined, reported as NaN
        if not np.isfinite(v):
            z = np.nan
        elif v <= 0:
            z = 0.0 if not np.any(S != 0) else np.nan  # identical forecasts -> 0; degenerate variance -> NaN
        else:
            z = S.sum() / math.sqrt(n_h * v)
        out[f"z_nw{L}"] = float(z)
        out[f"p_nw{L}"] = float(math.erfc(abs(z) / math.sqrt(2))) if np.isfinite(z) else np.nan
    sd = d.std(ddof=1)
    z_iid = 0.0 if sd == 0 else d.mean() / (sd / math.sqrt(len(d)))
    out["z_iid_rows"] = float(z_iid)
    out["p_iid_rows"] = float(math.erfc(abs(z_iid) / math.sqrt(2)))
    return out


def group_frame(df, group):
    return df if group == "overall" else df[df["group"] == group]


def citl_bootstrap(df, scheme=PRIMARY, n_boot=B, seed=SEED):
    """Per group: mean(p) − mean(y) for model and recent-rate, with a block-bootstrap 95% CI."""
    rows = []
    for grp in GROUPS:
        g = group_frame(df, grp).reset_index(drop=True)
        rng = np.random.default_rng(seed)
        y, pm, pr = g["y"].to_numpy(), g["p_model"].to_numpy(), g["p_rr"].to_numpy()
        vm, vr = np.empty(n_boot), np.empty(n_boot)
        for i, idx in enumerate(resample_rows(g, scheme, rng, n_boot)):
            vm[i], vr[i] = pm[idx].mean() - y[idx].mean(), pr[idx].mean() - y[idx].mean()
        for name, p, v in (("model", pm, vm), ("recent_rate", pr, vr)):
            lo, hi = np.percentile(v, [2.5, 97.5])
            rows.append({"group": grp, "predictor": name, "rows": len(g), "mean_pred": float(p.mean()),
                         "mean_obs": float(y.mean()), "pred_minus_obs": float(p.mean() - y.mean()),
                         "ci_low": float(lo), "ci_high": float(hi), "scheme": scheme, "blocks": n_blocks(g, scheme)})
    return pd.DataFrame(rows)
