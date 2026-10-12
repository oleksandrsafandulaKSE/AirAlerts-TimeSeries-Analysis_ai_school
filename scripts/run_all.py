"""Pipeline entry point: python scripts/run_all.py --config official [--as-of DATE]. Stages M1 + M2."""
import argparse
import json
import platform
import subprocess
import sys
from importlib.metadata import version

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config as config_mod, data, features, grid  # noqa: E402

PACKAGES = ["pandas", "numpy", "scikit-learn", "lightgbm", "matplotlib", "pytest", "requests", "streamlit"]


def _git(*args):
    """stdout of a git command, or None if git fails (e.g. no commit yet) -- never a bogus value."""
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def run_pipeline(cfg, data_path, out_dir):
    if cfg.source != "official":
        raise NotImplementedError(f"source {cfg.source!r} loader arrives in M4")
    stats = {}
    alerts = data.load_official(data_path, cfg, stats)
    before = cfg.test[0]  # no test-period statistics in M1 (human decision Q2/Q11, reviewer #1)
    counts = data.alert_counts(alerts[alerts["started_at"] < before])
    print(f"[m1] diagnostics below use alerts starting before {before} only")
    print(f"[m1] rows per level: {counts['rows_by_level']}")
    print(f"[m1] missing finished_at (24h cap applies): {counts['missing_finished_at']}")
    print(f"[m1] zero-duration alerts (onset kept, mask nothing): {counts['zero_duration']}")
    print(f"[m1] exactly-30-min alerts (D-010, kept): {counts['exactly_30min_total']} "
          f"by level {counts['exactly_30min_by_level']}")
    print(f"[m1] alerts lasting > 24h (D-020, printed only): {counts['over_24h_total']} "
          f"by unit {counts['over_24h_by_unit']}")

    detected = grid.detect_gaps(alerts, cfg.gap_min_hours)
    print(f"[m1] detected gaps: {[(str(a), str(b)) for a, b in detected]}")
    print(f"[m1] approved gaps: {[(str(a), str(b)) for a, b in cfg.approved_gaps]} + post-gap {cfg.post_gap_mask}")
    grid.check_gaps(detected, cfg.approved_gaps)

    g = grid.build_grid(alerts, cfg.grid_start, cfg.grid_end, cfg.H, cfg.target_levels,
                        cfg.standing_cap, cfg.approved_gaps, cfg.post_gap_mask,
                        coverage_end=cfg.coverage_end)
    print(f"[m1] grid {g.shape}, t {g.t.min()} -> {g.t.max()}, units {g.unit.nunique()}, "
          f"rows/unit {g.groupby('unit').size().unique().tolist()}")
    pre_t = g[g["t"] < before]
    print(f"[m1] masked share (t < test start): active {pre_t.active_at_t.mean():.4f}, "
          f"any {pre_t['mask'].mean():.4f}; gap rows in grid: {int(g.gap_mask.sum())}")
    if g["unit"].nunique() != 24:
        raise data.DataQualityError("grid does not have 24 units")
    if ((g["mask"] == 0) & (g["active_at_t"] == 1)).any():
        raise data.DataQualityError("unmasked row is under alert")

    by_q, by_g, pre = grid.base_rate_table(g, before)
    print(f"[m1] base rate on unmasked rows with t < {before}: overall {pre['y'].mean():.4f} "
          f"({len(pre):,} rows)")
    print(by_g.to_string())
    print(by_q.to_string())
    ref = grid.check_base_rate(g, before)
    print(f"[m1] base-rate check PASS: no quarter >= 2025Q1 below 50% of 2024 avg {ref:.4f}")

    meta = {
        "config": cfg.name, "source": cfg.source,
        "dates": {k: [str(x) for x in v] for k, v in
                  {"train": cfg.train, "val": cfg.val, "test": cfg.test}.items()},
        "grid": [str(cfg.grid_start), str(cfg.grid_end)], "coverage_end": str(cfg.coverage_end),
        "H": str(cfg.H), "target_levels": cfg.target_levels, "standing_cap": str(cfg.standing_cap),
        "approved_gaps": [[str(a), str(b)] for a, b in cfg.approved_gaps],
        "data_url": cfg.data_url, "data_sha256": data.file_sha256(data_path),
        "row_counts": stats, "alert_range": [str(alerts.started_at.min()), str(alerts.started_at.max())],
        "grid_shape": list(g.shape),
        "git_commit": _git("rev-parse", "--verify", "HEAD"), "git_dirty": bool(_git("status", "--porcelain")),
        "python": platform.python_version(), "packages": {p: version(p) for p in PACKAGES},
        "features": features.FEATURES,
    }
    checks = {**{k: v for k, v in counts.items()}, "detected_gaps": [[str(a), str(b)] for a, b in detected],
              "masked_share_before_test": {"active": float(pre_t.active_at_t.mean()),
                                           "any": float(pre_t["mask"].mean())},
              "gap_rows": int(g.gap_mask.sum()),
              "base_rate_2024_avg": float(ref)}
    # ---------------- M2: features known at t ----------------
    zones = config_mod.uncertainty_zones(cfg)
    times = pd.DatetimeIndex(g["t"].drop_duplicates().sort_values())
    f = features.build_features(alerts, times, zones, cfg.standing_cap, cfg.target_levels)
    gf = features.join_to_grid(g, f)  # raises unless 1:1 and complete
    print(f"[m2] features {f.shape}; joined {gf.shape}; join 1:1 complete: PASS; "
          f"uncertainty zones {[(str(a), str(b)) for a, b in zones]}")
    pre_f = gf[gf["t"] < before][features.FEATURES]  # no test-period statistics (M2 decision 4)
    nan = pre_f.isna().sum()
    desc = pre_f.describe(percentiles=[0.5]).T[["min", "50%", "max"]]
    print(f"[m2] rows with t < {before}: {len(pre_f):,}; NaN count / rate and min/median/max per feature:")
    print(pd.concat([nan.rename("nan"), (nan / len(pre_f)).round(6).rename("nan_rate"), desc], axis=1).to_string())
    m2_checks = {"feature_shape": list(f.shape), "joined_shape": list(gf.shape),
                 "uncertainty_zones": [[str(a), str(b)] for a, b in zones],
                 "nan_before_test": {k: int(v) for k, v in nan.items()},
                 "nan_rate_before_test": {k: float(v / len(pre_f)) for k, v in nan.items()},
                 "summary_before_test": desc.to_dict(orient="index")}

    # everything computed and checked; only now write
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    (out_dir / "m1_checks.json").write_text(json.dumps(checks, indent=2, default=str))
    by_q.rename(index=str).to_csv(out_dir / "base_rate_by_quarter.csv")
    by_g.to_csv(out_dir / "base_rate_by_group.csv")
    (out_dir / "m2_checks.json").write_text(json.dumps(m2_checks, indent=2, default=str))
    print(f"[run] wrote {out_dir}")
    return g


def main(argv=None):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError(f"Python 3.13 required (requirements.txt), got {platform.python_version()}")
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--data-path", default=None)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    if args.as_of is not None and args.config != "monthly":
        raise ValueError("--as-of is only valid with --config monthly")
    cfg = config_mod.get_config(args.config, args.as_of)
    if cfg.source != "official":
        raise NotImplementedError(f"source {cfg.source!r} loader arrives in M4")
    data_path = Path(args.data_path) if args.data_path else data.download_official(cfg, ROOT / "data")
    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "reports" / cfg.name
    run_pipeline(cfg, data_path, out_dir)


if __name__ == "__main__":
    main()
