"""M9 §C: CORP reliability (PAV / isotonic) and the Brier decomposition Brier = MCB − DSC + UNC
(Dimitriadis, Gneiting & Jordan 2021). Diagnostic only: PAV values are never used as forecasts."""
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from extras.uncertainty import B, GROUPS, PRIMARY, SEED, group_frame, resample_rows


def pav(p, y):
    """Isotonic (PAV) recalibration fitted on the same rows it describes; ties in p are pooled."""
    ir = IsotonicRegression(increasing=True, out_of_bounds="clip")
    return ir.fit(np.asarray(p, float), np.asarray(y, float)).predict(np.asarray(p, float))


def decompose(p, y):
    p, y = np.asarray(p, float), np.asarray(y, float)
    ybar = y.mean()
    b_p, b_pav, unc = np.mean((p - y) ** 2), np.mean((pav(p, y) - y) ** 2), np.mean((ybar - y) ** 2)
    out = {"brier": b_p, "mcb": b_p - b_pav, "dsc": unc - b_pav, "unc": unc}
    # MCB >= 0 and DSC >= 0 because the identity map and the constant ybar are both isotonic, so in-sample PAV can
    # only lower the Brier score; a broken PAV (e.g. a non-optimal fit) violates them. The identity itself is algebra.
    if out["mcb"] < -1e-12 or out["dsc"] < -1e-12:
        raise AssertionError(f"CORP terms negative: {out}")
    return out


def corp_table(df, split):
    rows = []
    for grp in GROUPS:
        g = group_frame(df, grp)
        dec = {name: decompose(g[col], g["y"]) for name, col in (("model", "p_model"), ("recent_rate", "p_rr"))}
        m, r = dec["model"], dec["recent_rate"]
        bss_from_dec = ((m["dsc"] - r["dsc"]) - (m["mcb"] - r["mcb"])) / r["brier"]
        for name, d in dec.items():
            rows.append({"split": split, "group": grp, "predictor": name, "rows": len(g), **d,
                         "bss_vs_recent_from_decomposition": bss_from_dec})
    return pd.DataFrame(rows)


def curve_bands(df, n_boot=B, seed=SEED, scheme=PRIMARY, q=99.5, n_grid=200):
    """PAV curves on a fixed grid of forecast values with a 90% week-block bootstrap band."""
    x_max = float(np.percentile(np.concatenate([df["p_model"], df["p_rr"]]), q))
    xs = np.linspace(0, x_max, n_grid)
    y = df["y"].to_numpy()
    out = {"x": xs, "x_max": x_max,
           "share_beyond": {c: float((df[c] > x_max).mean()) for c in ("p_model", "p_rr")}}
    rng = np.random.default_rng(seed)
    curves = {c: np.empty((n_boot, n_grid)) for c in ("p_model", "p_rr")}
    for i, idx in enumerate(resample_rows(df, scheme, rng, n_boot)):
        for c in curves:
            ir = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(df[c].to_numpy()[idx], y[idx])
            curves[c][i] = ir.predict(xs)
    for c in curves:
        full = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(df[c].to_numpy(), y)
        out[c] = {"pav": full.predict(xs), "lo": np.percentile(curves[c], 5, axis=0),
                  "hi": np.percentile(curves[c], 95, axis=0)}
    return out


def plot(bands, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 5))
    xs = bands["x"]
    ax.plot([0, bands["x_max"]], [0, bands["x_max"]], color="0.6", lw=1, ls="--", label="perfect calibration")
    for c, label, color in (("p_model", "model (frozen V0)", "#1f6feb"), ("p_rr", "recent rate", "#d1242f")):
        ax.fill_between(xs, bands[c]["lo"], bands[c]["hi"], color=color, alpha=0.18, lw=0)
        ax.plot(xs, bands[c]["pav"], color=color, lw=2, label=f"{label} (beyond x-axis: {bands['share_beyond'][c]:.1%})")
    ax.set_xlim(0, bands["x_max"])
    ax.set_xlabel("forecast probability")
    ax.set_ylabel("observed onset rate (PAV / isotonic, diagnostic only)")
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.text(0.01, 0.01, "Bands: 90% week-block bootstrap. Recalibrated values are never used as forecasts.", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=130)
    plt.close(fig)
