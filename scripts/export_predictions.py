"""M5b: export the FROZEN headline predictor's final-test predictions per hour and unit (plans/M5b.md §2).

    python scripts/export_predictions.py   # -> reports/official/{test_predictions,metrics_by_unit,test_onsets}.csv

Not a new scoring: the predictor and baseline tables are the pre-registered files (hashes checked against the joint
marker), predictions are computed exactly as in run_all.score_final_test, and the export refuses to write unless it
reproduces reports/official/metrics.csv bit for bit. Per-oblast numbers are a human-authorised breakdown (proposed D-031).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import run_all  # noqa: E402
from src import baselines, config as config_mod, data, evaluate, features, grid, model  # noqa: E402

STATUS = ["scored", "under_alert", "gap_or_missing", "label_unknown", "feature_missing", "purged"]


class ExportError(RuntimeError):
    pass


def row_status(df, a, b, H, feats):
    """Exclusive D-024 reason, precedence purge -> mask (gap vs alert) -> label unknown -> feature missing -> scored."""
    st = np.full(len(df), "scored", dtype=object)
    feat_nan = df[feats].isna().any(axis=1).to_numpy()
    y_nan = df["y"].isna().to_numpy()
    masked = (df["mask"] != 0).to_numpy()
    gap = (df["gap_mask"] == 1).to_numpy()
    purge = ~((df["t"] + H) <= b).to_numpy()
    st[feat_nan] = "feature_missing"
    st[y_nan] = "label_unknown"
    st[masked & ~gap] = "under_alert"
    st[masked & gap] = "gap_or_missing"
    st[purge] = "purged"
    return st


def frozen(reports, data_path):
    off = Path(reports) / "official"
    _, pr_sha = run_all._verify_prereg(off, data_path)
    marker = json.loads((Path(reports) / run_all.JOINT_MARKER).read_text())
    if marker["preregistration_sha256"]["official"] != pr_sha:
        raise ExportError("official pre-registration differs from the one frozen at the final test")
    predictor = model.Predictor(off / "model.txt", off / "calibrator.json", features.FEATURES)
    run_all._reproduce_validation(off, predictor)
    tables = json.loads((off / "baseline_fit.json").read_text())
    return off, predictor, tables


def predict_rows(gf, alerts, rows, predictor, tables, cfg):
    bp, _, _ = baselines.predict_from_tables(tables, gf, rows, alerts, cfg)
    return predictor.headline(rows), bp["recent_rate"].to_numpy()


def unit_metrics(pred, min_class=10, low_n_rows=100):
    out = []
    for u, g in pred[pred["status"] == "scored"].groupby("unit"):
        y = g["y"].to_numpy(float)
        bm = float(np.mean((g["p_model"] - y) ** 2))
        br = float(np.mean((g["p_recent_rate"] - y) ** 2))
        pos, neg = int(y.sum()), int(len(y) - y.sum())
        auc = float(roc_auc_score(y, g["p_model"])) if pos >= min_class and neg >= min_class else np.nan
        reasons = []
        if len(g) < low_n_rows:
            reasons.append("fewer than 100 scored hours")
        if np.isnan(auc):
            reasons.append("too few alert starts or too few no-start hours to rank")
        out.append({"unit": u, "group": g["group"].iloc[0], "scored_hours": len(g), "alert_starts": pos,
                    "base_rate": float(y.mean()), "brier_model": bm, "brier_recent_rate": br,
                    "brier_skill_vs_recent": (1 - bm / br) if br > 0 else np.nan, "roc_auc_within_unit": auc,
                    "low_n": bool(reasons), "low_n_reason": "; ".join(reasons)})
    return pd.DataFrame(out)


def export(reports, data_path, out_dir=None):
    cfg = config_mod.official()
    off, predictor, tables = frozen(reports, data_path)
    out_dir = Path(out_dir) if out_dir else off
    fr = run_all.build_frames(cfg, data_path)
    gf, alerts = fr["gf"], fr["alerts"]
    a, b = cfg.test
    rows = gf[(gf["t"] >= a) & (gf["t"] < b)].reset_index(drop=True)
    rows["status"] = row_status(rows, a, b, cfg.H, features.FEATURES)
    sc = rows["status"] == "scored"
    p_model, p_recent = predict_rows(gf, alerts, rows[sc].reset_index(drop=True), predictor, tables, cfg)
    rows["p_model"], rows["p_recent_rate"] = np.nan, np.nan
    rows.loc[sc, "p_model"], rows.loc[sc, "p_recent_rate"] = p_model, p_recent
    rows.loc[~sc, "y"] = np.nan
    # guard: the same single scoring -> reproduce metrics.csv exactly
    scored = rows[sc].rename(columns={"p_model": "model", "p_recent_rate": "recent_rate"})
    table, _ = evaluate.metric_table(scored, ["model", "recent_rate"], "recent_rate", cfg.min_class_per_unit)
    saved = pd.read_csv(off / "metrics.csv", float_precision="round_trip").set_index(["baseline", "group"])
    for _, r in table.iterrows():
        s = saved.loc[(r["baseline"], r["group"])]
        if int(s["rows"]) != int(r["rows"]) or float(s["brier"]) != float(r["brier"]):
            raise ExportError(f"export does not reproduce metrics.csv for {r['baseline']}/{r['group']}")
    per_unit = unit_metrics(rows, cfg.min_class_per_unit, cfg.low_n_rows)
    if len(per_unit) != 24 or per_unit["scored_hours"].sum() != int(saved.loc[("model", "overall"), "rows"]):
        raise ExportError("per-unit breakdown does not add up to the overall scored rows")
    ivs = grid.unit_intervals(alerts, cfg.standing_cap)
    on = []
    for u, (_, _, ons) in ivs.items():
        o = pd.to_datetime(ons).tz_localize("UTC")
        on += [{"unit": u, "onset": x} for x in o[(o >= a) & (o < b)]]
    onsets = pd.DataFrame(on).sort_values(["unit", "onset"], ignore_index=True)
    cols = ["unit", "t", "group", "status", "y", "p_model", "p_recent_rate"]
    rows[cols].to_csv(out_dir / "test_predictions.csv", index=False)
    per_unit.to_csv(out_dir / "metrics_by_unit.csv", index=False)
    onsets.to_csv(out_dir / "test_onsets.csv", index=False)
    print(f"[export] {len(rows):,} test unit-hours ({int(sc.sum()):,} scored), 24 units, {len(onsets):,} onsets -> {out_dir}")
    return rows, per_unit, onsets


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports-root", default=str(ROOT / "reports"))
    ap.add_argument("--data-path", default=str(ROOT / "data" / "official_data_en.csv"))
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    export(args.reports_root, args.data_path, args.out_dir)


if __name__ == "__main__":
    main()
