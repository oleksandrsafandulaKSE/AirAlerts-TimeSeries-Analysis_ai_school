"""Splits, eligibility, test-label isolation and the metric suite (M3; reused unchanged in M4)."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from src.data import DataQualityError

GROUPS = ["overall", "kyiv_city", "frontline", "rear"]
REASONS = ["purge", "masked", "y_nan", "feature_nan"]


def split_bounds(cfg, split, allow_test=False):
    """The only way to get split dates; the test split needs allow_test=True (M4, D-021)."""
    score_split(split, allow_test)
    return {"train": cfg.train, "val": cfg.val, "test": cfg.test}[split]


def isolate_test_labels(frame, test_start, H):
    """Blank every label whose window (t, t+H] reaches past the test start (t + H > C), so nothing
    downstream can read a test-period outcome (M3 decision 8; M3b: t + H <= C for every pre-M4 label)."""
    if "y" not in frame.columns:
        raise KeyError("isolate_test_labels: frame has no 'y' column")
    if not isinstance(test_start, pd.Timestamp) or test_start.tz is None:
        raise TypeError("test_start must be a tz-aware pd.Timestamp")
    hidden = frame["t"] + H > test_start
    out = frame.copy()
    out.loc[hidden, "y"] = np.nan
    if out.loc[hidden, "y"].notna().any():
        raise DataQualityError("test labels still present after isolation")
    return out


def availability(frame, a, b, H, feature_cols):
    """Row counts WITHOUT labels (for the test split before M4), D-024. Overlapping counts per reason, and
    exclusive counts (first failing reason in the order purge -> masked -> feature NaN)."""
    r = (frame["t"] >= a) & (frame["t"] < b)
    fails = {"purge": ~(frame["t"] + H <= b), "masked": frame["mask"] != 0,
             "feature_nan": frame[feature_cols].isna().any(axis=1)}
    remaining = r.copy()
    overlapping, exclusive = {}, {}
    for k, f in fails.items():
        overlapping[k] = int((r & f).sum())
        exclusive[k] = int((remaining & f).sum())
        remaining &= ~f
    return {"in_range": int(r.sum()), "available": int(remaining.sum()),
            "excluded_overlapping": overlapping, "excluded_exclusive": exclusive}


def eligibility(frame, a, b, H, feature_cols):
    """Eligible rows in [a, b) and exclusion counts (exclusive: first failing reason; and overlapping)."""
    in_range = (frame["t"] >= a) & (frame["t"] < b)
    fails = {
        "purge": ~(frame["t"] + H <= b),
        "masked": frame["mask"] != 0,
        "y_nan": frame["y"].isna(),
        "feature_nan": frame[feature_cols].isna().any(axis=1),
    }
    remaining = in_range.copy()
    exclusive, overlapping = {}, {}
    for r in REASONS:
        hit = in_range & fails[r]
        overlapping[r] = int(hit.sum())
        exclusive[r] = int((remaining & fails[r]).sum())
        remaining &= ~fails[r]
    counts = {"in_range": int(in_range.sum()), "eligible": int(remaining.sum()),
              "excluded_exclusive": exclusive, "excluded_overlapping": overlapping}
    if counts["in_range"] - sum(exclusive.values()) != counts["eligible"]:
        raise DataQualityError("exclusion counts do not add up")
    return remaining.to_numpy(), counts


def score_split(split, allow_test=False):
    """Guard: the final test is scored once, in M4 (D-021)."""
    if split == "test" and not allow_test:
        raise PermissionError("the final test is scored only in M4, by run_all.score_final_test")
    if split not in ("train", "val", "test"):
        raise ValueError(f"unknown split {split!r}")
    return split


# ---------------- metrics ----------------

def brier(p, y):
    return float(np.mean((np.asarray(p, float) - np.asarray(y, float)) ** 2)) if len(y) else np.nan


def skill(b, b_ref, reasons, label):
    if not np.isfinite(b_ref) or b_ref == 0:
        reasons.append(f"{label}: Brier skill NaN (reference Brier = {b_ref})")
        return np.nan
    return 1.0 - b / b_ref


def auc(y, p, reasons, label):
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        reasons.append(f"{label}: ROC-AUC NaN (one class only)")
        return np.nan
    return float(roc_auc_score(y, p))


def avg_precision(y, p, reasons, label):
    if np.sum(y) == 0:
        reasons.append(f"{label}: PR-AUC NaN (no positives)")
        return np.nan
    return float(average_precision_score(y, p))


def within_unit_auc(df, col, min_class, reasons, label):
    aucs, excluded = [], []
    for u, g in df.groupby("unit"):
        pos = int(g["y"].sum())
        neg = len(g) - pos
        if pos < min_class or neg < min_class:
            excluded.append(u)
            continue
        aucs.append(roc_auc_score(g["y"], g[col]))
    if not aucs:
        reasons.append(f"{label}: within-unit AUC NaN (no unit with >= {min_class} pos and neg)")
    return (float(np.mean(aucs)) if aucs else np.nan), len(aucs), sorted(excluded)


def metric_table(scored, baselines, ref, min_class):
    """Rows baseline x group. `scored` has unit, group, y and one column per baseline."""
    for name in baselines:
        p = scored[name].to_numpy(float)
        if np.isnan(p).any() or (p < 0).any() or (p > 1).any():
            raise ValueError(f"{name}: predictions must be in [0, 1] without NaN")
    rows, reasons = [], []
    for grp in GROUPS:
        g = scored if grp == "overall" else scored[scored["group"] == grp]
        y = g["y"].to_numpy(float)
        base = float(y.mean()) if len(y) else np.nan
        b_ref = brier(g[ref], y) if len(y) else np.nan
        for name in baselines:
            label = f"{name}/{grp}"
            if len(g) == 0:
                reasons.append(f"{label}: empty group, all metrics NaN")
                rows.append({"baseline": name, "group": grp, "rows": 0})
                continue
            b = brier(g[name], y)
            ap = avg_precision(y, g[name], reasons, label)
            if base == 0:
                reasons.append(f"{label}: PR-AUC/base NaN (base rate 0)")
            wu, n_used, excl = within_unit_auc(g, name, min_class, reasons, label)
            rows.append({
                "baseline": name, "group": grp, "rows": len(g), "positives": int(y.sum()),
                "base_rate": base, "brier": b, "brier_skill_vs_recent": skill(b, b_ref, reasons, label),
                "roc_auc_pooled": auc(y, g[name], reasons, label),
                "roc_auc_within_unit_mean": wu, "within_unit_units_used": n_used,
                "within_unit_units_excluded": ";".join(excl),
                "pr_auc": ap, "pr_auc_over_base": (ap / base) if base and np.isfinite(ap) else np.nan,
            })
    return pd.DataFrame(rows), reasons


def reliability_bins(p, y, n_bins=10):
    """Fixed-width bins [0,0.1), ..., [0.9,1.0]; p = 1.0 goes to the last bin."""
    p = np.asarray(p, float)
    y = np.asarray(y, float)
    if np.isnan(p).any() or (p < 0).any() or (p > 1).any():
        raise ValueError("reliability_bins: p must be in [0, 1] without NaN")
    idx = np.minimum((p * n_bins).astype(int), n_bins - 1)
    out = []
    for i in range(n_bins):
        m = idx == i
        if m.any():
            out.append({"bin": i, "lo": i / n_bins, "hi": (i + 1) / n_bins, "n": int(m.sum()),
                        "mean_p": float(p[m].mean()), "mean_y": float(y[m].mean())})
    return pd.DataFrame(out)


def reliability_plot(scored, baselines, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--", label="perfect calibration")
    tables = []
    for name in baselines:
        rb = reliability_bins(scored[name], scored["y"])
        rb.insert(0, "baseline", name)
        tables.append(rb)
        ax.plot(rb["mean_p"], rb["mean_y"], marker="o", lw=1, label=name)
        ax.scatter(rb["mean_p"], rb["mean_y"], s=10 + 200 * rb["n"] / rb["n"].max(), alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("mean predicted probability")
    ax.set_ylabel("observed onset rate")
    ax.set_title(title)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return pd.concat(tables, ignore_index=True)


# ---------------- M4 helpers ----------------

def low_n_flags(table, min_rows):
    """Flag groups with few eligible rows or with units left out of the within-unit AUC (D-025, M4 plan §4)."""
    out = table.copy()
    excl = out.get("within_unit_units_excluded", pd.Series("", index=out.index)).fillna("")
    out["low_n"] = (out["rows"] < min_rows) | (excl != "")
    return out


def calibration_in_the_large(scored, predictors):
    """Per group and predictor: mean predicted, mean observed, difference (D-015 c)."""
    rows = []
    for grp in GROUPS:
        g = scored if grp == "overall" else scored[scored["group"] == grp]
        for name in predictors:
            rows.append({"predictor": name, "group": grp, "rows": len(g),
                         "mean_pred": float(g[name].mean()) if len(g) else np.nan,
                         "mean_obs": float(g["y"].mean()) if len(g) else np.nan})
    out = pd.DataFrame(rows)
    out["pred_minus_obs"] = out["mean_pred"] - out["mean_obs"]
    return out


def exposure_summary(grid_df, onsets_by_unit, start, end, zones):
    """D-015 (a) per unit: exposed hours = grid hours t in [start, end) whose hour [t, t+1h) lies outside every
    uncertainty zone; onsets counted when they start inside an exposed hour; active hours = exposed hours with
    active_at_t = 1 (D-020 state). Unknown exposure is excluded, never counted as quiet (M4 plan §5.3)."""
    g = grid_df[(grid_df["t"] >= start) & (grid_df["t"] < end)].copy()
    hour_end = g["t"] + pd.Timedelta(hours=1)
    exposed = pd.Series(True, index=g.index)
    for z0, z1 in zones:
        exposed &= ~((g["t"] < z1) & (hour_end > z0))
    g = g[exposed]
    rows = []
    for u, gu in g.groupby("unit"):
        on = pd.to_datetime(onsets_by_unit.get(u, [])).tz_localize("UTC") if len(onsets_by_unit.get(u, [])) else \
            pd.DatetimeIndex([], tz="UTC")
        hours = set(gu["t"])
        n_on = int(sum(o.floor("h") in hours for o in on))
        rows.append({"unit": u, "group": gu["group"].iloc[0], "exposed_hours": len(gu), "onsets": n_on,
                     "active_hours": int(gu["active_at_t"].sum())})
    out = pd.DataFrame(rows)
    out["onsets_per_30d"] = out["onsets"] / (out["exposed_hours"] / 720)
    out["share_under_alert"] = out["active_hours"] / out["exposed_hours"]
    return out


def pooled_by_group(per_unit):
    rows = []
    for grp in GROUPS:
        g = per_unit if grp == "overall" else per_unit[per_unit["group"] == grp]
        e = g["exposed_hours"].sum()
        rows.append({"unit": f"[{grp}]", "group": grp, "exposed_hours": int(e), "onsets": int(g["onsets"].sum()),
                     "active_hours": int(g["active_hours"].sum()),
                     "onsets_per_30d": g["onsets"].sum() / (e / 720) if e else np.nan,
                     "share_under_alert": g["active_hours"].sum() / e if e else np.nan})
    return pd.DataFrame(rows)
