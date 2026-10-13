"""M8 Python reference for the live offset at an arbitrary time tau (plans/M8.md §2, §5).

r(tau) = (k + 10 q) / (n + 10): k, n over ELIGIBLE hour rows s (unmasked incl. gap/hole zones, label known) with
ceil(tau - 14 d) <= s <= floor(tau - 1 h); q = the unit's expanding eligible-label rate over all hour rows s <= tau - 1 h
(national pooled fallback; none -> NaN)."""
import numpy as np
import pandas as pd

from src import grid as G

ALPHA = 10.0


def live_offset(alerts, tau, history_start, gaps, post_gap=pd.Timedelta(hours=24), units=None):
    H = pd.Timedelta(hours=1)
    start = history_start.ceil("h")
    last = (tau - H).floor("h")
    g = G.build_grid(alerts, start, last + H, H, approved_gaps=gaps, post_gap=post_gap, unit_list=units)
    g["elig"] = (g["mask"] == 0) & g["y"].notna()
    lo = (tau - pd.Timedelta(days=14)).ceil("h")
    out = {}
    nat_k = g.loc[g.elig, "y"].sum()
    nat_n = int(g["elig"].sum())
    q_nat = nat_k / nat_n if nat_n else np.nan
    for u, gu in g.groupby("unit"):
        e = gu[gu.elig]
        q = e["y"].mean() if len(e) else q_nat
        w = e[(e.t >= lo) & (e.t <= last)]
        k, n = float(w["y"].sum()), len(w)
        out[u] = {"k": k, "n": n, "q": float(q) if q == q else None,
                  "rate": (k + ALPHA * q) / (n + ALPHA) if q == q else None}
    return out
