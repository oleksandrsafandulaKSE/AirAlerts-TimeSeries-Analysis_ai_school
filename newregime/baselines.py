"""Extra RED baseline `recent_any_x_red_share` (plans/M6c-1.md §6): rr_any(t) x share(t), share on COMMON support =
the unit's ANY-eligible rows s in [t - 14 d, t - H] with both labels known. The four src baselines are reused as is."""
import numpy as np
import pandas as pd

from src import baselines as B
from src.data import DataQualityError

EXTRA = "recent_any_x_red_share"


def common_support(any_frame, red_frame):
    """ANY-unmasked rows with both labels known: (unit, t, y_any, y_red). ANY inactive implies RED inactive."""
    a = any_frame.loc[(any_frame["mask"] == 0) & any_frame["y"].notna(), ["unit", "t", "y"]]
    r = red_frame[["unit", "t", "y", "mask"]].rename(columns={"y": "y_red", "mask": "mask_red"})
    m = a.rename(columns={"y": "y_any"}).merge(r, on=["unit", "t"], how="left", validate="one_to_one")
    if (m["mask_red"] != 0).any():
        raise DataQualityError("an ANY-unmasked row is RED-masked (RED active while ANY is not)")
    dropped = int(m["y_red"].isna().sum())
    if dropped:
        print(f"[nr-baseline] common support: {dropped} ANY rows without a RED label dropped")
    return m[m["y_red"].notna()].drop(columns="mask_red")


def train_share(common, a, b, H):
    """pi_u = k_red / k_any on the unit's common-support TRAIN rows (t in [a, b), t + H <= b); 0 if k_any = 0."""
    c = common[(common["t"] >= a) & (common["t"] < b) & (common["t"] + H <= b)]
    k = c.groupby("unit")[["y_red", "y_any"]].sum()
    return (k["y_red"] / k["y_any"]).where(k["y_any"] > 0, 0.0)


def red_share(common, score, pi, alpha, window, H):
    """share(t) = (k_red + alpha * pi_u) / (k_any + alpha) over common rows s in [t - window, t - H]."""
    out = np.zeros(len(score))
    for u, idx in score.groupby("unit").indices.items():
        if u not in pi.index:
            raise DataQualityError(f"{u}: no train share")
        h = common[common["unit"] == u].sort_values("t")
        ts = B._naive(h["t"])
        cr = np.concatenate([[0.0], np.cumsum(h["y_red"].to_numpy(float))])
        ca = np.concatenate([[0.0], np.cumsum(h["y_any"].to_numpy(float))])
        t = B._naive(score.iloc[idx]["t"])
        lo = np.searchsorted(ts, t - window.to_timedelta64(), side="left")
        hi = np.searchsorted(ts, t - H.to_timedelta64(), side="right")
        out[idx] = (cr[hi] - cr[lo] + alpha * pi[u]) / (ca[hi] - ca[lo] + alpha)
    return np.clip(out, 0.0, 1.0)


def recent_any_x_red_share(any_history, p_unit_any, common, pi, red_score, cfg):
    """rr_any is computed from past ANY labels only, so it exists on every RED row (also where ANY is masked)."""
    rr_any = B.recent_rate(any_history, red_score, p_unit_any, cfg.shrink_alpha, cfg.recent_window, cfg.H)
    return rr_any * red_share(common, red_score, pi, cfg.shrink_alpha, cfg.recent_window, cfg.H)
