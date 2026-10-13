"""Pipeline entry point (M1-M4).

  python scripts/run_all.py --config official      [--stage fit]   # M1-M3 + model + calibration + pre-registration
  python scripts/run_all.py --config official_h3   [--stage fit]   # the same for H = 3 (extra results row)
  python scripts/run_all.py --stage final-test                     # scores the FINAL TEST once, both horizons (D-021)
  python scripts/run_all.py --config new_regime                    # exploratory API section (D-015, D-027)

The fit stage reads no test label. The final-test stage refuses to run unless both horizons are pre-registered and
every pre-registered hash (model, calibrator, baseline tables, data, code) still matches (M4 plan §4)."""
import argparse
import datetime
import hashlib
import json
import platform
import subprocess
import sys
from importlib.metadata import version

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import baselines, config as config_mod, data, evaluate, features, grid, model  # noqa: E402

PACKAGES = ["pandas", "numpy", "scikit-learn", "lightgbm", "matplotlib", "pytest", "requests", "streamlit"]
OFFICIAL_RUNS = ("official", "official_h3")
JOINT_MARKER = "final_test_access.json"


def code_fingerprint(root=ROOT):
    """sha256 over the pipeline code (src/*.py + scripts/run_all.py), pre-registered before the final test."""
    h = hashlib.sha256()
    for p in sorted((root / "src").glob("*.py")) + [root / "scripts" / "run_all.py"]:
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def check_source(alerts, source):
    """Never mix sources in one training set or metric (CLAUDE.md)."""
    bad = set(alerts["source"]) - {source}
    if bad:
        raise data.DataQualityError(f"alerts from source(s) {sorted(bad)} in a {source!r} run")


def _git(*args):
    """stdout of a git command, or None if git fails (e.g. no commit yet) -- never a bogus value."""
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def check_gap_rows(g, cfg):
    """Gap-masked rows must be exactly the hours of config.gap_label_mask_interval (M3 decision 4)."""
    expected = pd.Series(False, index=g.index)
    for a, b in config_mod.gap_label_mask_interval(cfg):
        expected |= (g["t"] >= a) & (g["t"] < b)
    if not (expected.to_numpy() == (g["gap_mask"] == 1).to_numpy()).all():
        raise data.DataQualityError("gap_mask rows differ from gap_label_mask_interval")
    return int(expected.sum() / g["unit"].nunique())


def run_m3(gf, alerts, cfg):
    """Baselines on VALIDATION only. Test labels are blanked before anything runs (M3 decision 8)."""
    iso = evaluate.isolate_test_labels(gf, cfg.test[0], cfg.H)
    feats = features.FEATURES
    split_counts, elig = {}, {}
    for split in ("train", "val"):
        a, b = evaluate.split_bounds(cfg, split)
        elig[split], split_counts[split] = evaluate.eligibility(iso, a, b, cfg.H, feats)
        c = split_counts[split]
        base = iso.loc[elig[split], "y"].mean()
        c["base_rate"] = float(base)
        print(f"[m3] {split} [{a}, {b}): in range {c['in_range']:,}, eligible {c['eligible']:,}, "
              f"base rate {base:.4f}")
        print(f"[m3]   excluded (exclusive, sum = {sum(c['excluded_exclusive'].values()):,}): "
              f"{c['excluded_exclusive']}; overlapping: {c['excluded_overlapping']}")
    fit, score = iso[elig["train"]].reset_index(drop=True), iso[elig["val"]].reset_index(drop=True)
    if fit["t"].max() + cfg.H > cfg.train[1] or score["t"].min() < cfg.val[0]:
        raise data.DataQualityError("fit rows must end before the train cut-off; score rows are validation")
    test_avail = evaluate.availability(iso, cfg.test[0], cfg.test[1], cfg.H, feats)  # no labels
    print(f"[m3] test split (NOT scored; counts only, no labels): {test_avail}")
    preds, p_unit, n_hist = baselines.predict_all(iso, alerts, fit, score, cfg)
    if not (preds["unit"].to_numpy() == score["unit"].to_numpy()).all() or \
            not (preds["t"].to_numpy() == score["t"].to_numpy()).all():
        raise data.DataQualityError("baseline predictions are not on the score rows")
    scored = preds.assign(y=score["y"].to_numpy(), group=score["group"].to_numpy())
    for name in baselines.BASELINES:  # identical (unit, t) keys for every baseline, no NaN prediction
        if scored[name].isna().any():
            raise data.DataQualityError(f"{name}: NaN predictions on score rows")
    print(f"[m3] p_unit (train): " + ", ".join(f"{u} {v:.3f}" for u, v in p_unit.sort_values().items()))
    n_stats = {"min": float(n_hist.min()), "median": float(np.median(n_hist)),
               "n_lt_10": int((n_hist < 10).sum()), "n_eq_0": int((n_hist == 0).sum()), "rows": len(n_hist)}
    print(f"[m3] recent-rate history n on val rows: {n_stats}")
    table, reasons = evaluate.metric_table(scored, baselines.BASELINES, "recent_rate", cfg.min_class_per_unit)
    for r in reasons:
        print(f"[m3] NaN reason: {r}")
    cols = ["baseline", "group", "rows", "base_rate", "brier", "brier_skill_vs_recent", "roc_auc_pooled",
            "roc_auc_within_unit_mean", "within_unit_units_used", "pr_auc", "pr_auc_over_base"]
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        print("[m3] VALIDATION baseline table:")
        print(table[cols].to_string(index=False))
    checks = {"split": "val", "split_counts": split_counts, "test_availability_no_labels": test_avail, "p_unit": p_unit.to_dict(),
              "recent_rate_history_n": n_stats, "nan_reasons": reasons, "baselines": baselines.BASELINES}
    return table, scored, checks


def build_frames(cfg, data_path):
    """M1 + M2 for an official config: alerts, grid (y, mask), features, checks (all raising). Reads no file it writes."""
    if cfg.source != "official":
        raise NotImplementedError(f"build_frames is for official configs, got source {cfg.source!r}")
    print(f"[run] config {cfg.name}: horizon H = {cfg.H_label} (label = onset in (t, t+H])")
    stats = {}
    alerts = data.load_official(data_path, cfg, stats)
    check_source(alerts, "official")
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
                        cfg.standing_cap, config_mod.mask_gaps(cfg), cfg.post_gap_mask,
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

    by_q, by_g, pre = grid.base_rate_table(g, before, cfg.H)
    print(f"[m1] base rate on unmasked rows with t + H <= {before} (H = {cfg.H_label}): overall {pre['y'].mean():.4f} "
          f"({len(pre):,} rows)")
    print(by_g.to_string())
    print(by_q.to_string())
    ref = grid.check_base_rate(g, before, cfg.H)
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

    gap_hours = check_gap_rows(g, cfg)
    print(f"[m3] gap-masked hours: {gap_hours} = {[(str(a), str(b)) for a, b in config_mod.gap_label_mask_interval(cfg)]}")
    return {"alerts": alerts, "g": g, "gf": gf, "meta": meta, "checks": checks, "by_q": by_q, "by_g": by_g,
            "m2_checks": m2_checks}


PREREG_KEYS = {"model.txt", "calibrator.json", "baseline_fit.json", "val_predictions.csv", "data"}


def run_pipeline(cfg, data_path, out_dir, fit_model=True):
    """Stage `fit`: M1-M3 (+ M4 model, calibration and pre-registration when fit_model). Reads no test label.
    Refuses once the final test has been accessed: a model fitted after seeing the test must never replace the
    pre-registered one (M4 harness review)."""
    marker = Path(out_dir).parent / JOINT_MARKER
    if fit_model and marker.exists():
        raise data.DataQualityError(f"the final test was already accessed ({marker}): refitting is not allowed")
    fr = build_frames(cfg, data_path)
    alerts, g, gf, meta = fr["alerts"], fr["g"], fr["gf"], fr["meta"]
    checks, by_q, by_g, m2_checks = fr["checks"], fr["by_q"], fr["by_g"], fr["m2_checks"]

    # ---------------- M3: baselines on validation ----------------
    table, scored, m3_checks = run_m3(gf, alerts, cfg)
    meta["m3"] = {"split": "val", "baselines": baselines.BASELINES,
                  "recent_rate": f"(k + {cfg.shrink_alpha}*p_unit)/(n + {cfg.shrink_alpha}), window "
                                 f"{cfg.recent_window}, s <= t - H"}
    m4 = run_m4_fit(gf, alerts, cfg, scored, data_path) if fit_model else None
    if m4 is not None:
        table, scored = m4["table"], m4["scored"]
        meta["m4"] = {"best_iteration": m4["best_iteration"], "calibration": m4["calibrator"]["decision"]}

    # everything computed and checked; only now write
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    (out_dir / "m1_checks.json").write_text(json.dumps(checks, indent=2, default=str))
    by_q.rename(index=str).to_csv(out_dir / "base_rate_by_quarter.csv")
    by_g.to_csv(out_dir / "base_rate_by_group.csv")
    (out_dir / "m2_checks.json").write_text(json.dumps(m2_checks, indent=2, default=str))
    table.to_csv(out_dir / "metrics_validation.csv", index=False)
    (out_dir / "metrics_validation.json").write_text(table.to_json(orient="records", indent=2))
    predictors = (m4["predictors"] if m4 is not None else []) + baselines.BASELINES
    bins = evaluate.reliability_plot(scored, predictors, out_dir / "reliability_validation.png",
                                     "Reliability on validation" + (" (model + baselines)" if m4 else " (baselines)"))
    bins.to_csv(out_dir / "reliability_validation_bins.csv", index=False)
    (out_dir / "m3_checks.json").write_text(json.dumps(m3_checks, indent=2, default=str))
    if m4 is not None:
        write_m4_fit(m4, cfg, data_path, out_dir)
    print(f"[run] wrote {out_dir}")
    return g


# ---------------- M4: model, calibration, pre-registration (stage fit) ----------------

def _keys_equal(a, b):
    return (a["unit"].to_numpy() == b["unit"].to_numpy()).all() and (a["t"].to_numpy() == b["t"].to_numpy()).all()


def run_m4_fit(gf, alerts, cfg, scored_val, data_path):
    """Train on eligible TRAIN rows, early-stop on eligible VALIDATION rows, no refit; pre-registered calibration
    rule on validation. Test labels are blanked before anything runs (t + H > test start)."""
    iso = evaluate.isolate_test_labels(gf, cfg.test[0], cfg.H)
    feats = features.FEATURES
    el_tr, _ = evaluate.eligibility(iso, *evaluate.split_bounds(cfg, "train"), cfg.H, feats)
    el_va, _ = evaluate.eligibility(iso, *evaluate.split_bounds(cfg, "val"), cfg.H, feats)
    fit, val = iso[el_tr].reset_index(drop=True), iso[el_va].reset_index(drop=True)
    if not _keys_equal(val, scored_val):
        raise data.DataQualityError("model validation rows differ from the M3 scored rows")
    if fit["t"].max() + cfg.H > cfg.train[1] or val["t"].max() + cfg.H > cfg.val[1]:
        raise data.DataQualityError("fit/validation rows reach past their cut-off")
    booster, curve = model.train(fit, val, feats)
    best = booster.best_iteration
    model_str = booster.model_to_string(num_iteration=best)
    frozen = model.lgb.Booster(model_str=model_str)  # every prediction below comes from the frozen trees
    p_raw = frozen.predict(model._matrix(val, feats))
    cal = model.calibration_decision(p_raw, val["y"].to_numpy())
    p_head = model.apply_calibration(p_raw, cal)
    tables = baselines.fit_tables(fit, cfg)
    bpreds, _, _ = baselines.predict_from_tables(tables, iso, val, alerts, cfg)
    for name in baselines.BASELINES:  # the frozen tables reproduce the M3 baseline predictions exactly
        if not np.array_equal(bpreds[name].to_numpy(), scored_val[name].to_numpy()):
            raise data.DataQualityError(f"{name}: frozen tables do not reproduce the M3 validation predictions")
    predictors = ["model"] + (["model_raw"] if cal["decision"] == "platt" else [])
    scored = scored_val.assign(model=p_head)
    if cal["decision"] == "platt":
        scored = scored.assign(model_raw=p_raw)
    table, reasons = evaluate.metric_table(scored, predictors + baselines.BASELINES, "recent_rate",
                                           cfg.min_class_per_unit)
    table = evaluate.low_n_flags(table, cfg.low_n_rows)
    lo = lambda k: curve[k - 1] if 1 <= k <= len(curve) else float("nan")  # noqa: E731
    print(f"[m4] fit rows {len(fit):,}, early-stopping rows {len(val):,}; best iteration {best} "
          f"(val logloss {lo(best):.5f}; at best-100 {lo(best - 100):.5f}; at best+100 {lo(best + 100):.5f})")
    print(f"[m4] validation ECE {cal['ece']:.4f} -> calibration decision: {cal['decision']}"
          + (f" (Platt slope {cal['slope']:.4f}, intercept {cal['intercept']:.4f})" if cal["decision"] == "platt" else ""))
    imp = pd.Series(frozen.feature_importance("gain"), index=frozen.feature_name()).sort_values(ascending=False)
    print("[m4] feature importance (gain): " + ", ".join(f"{k} {v:.0f}" for k, v in imp.items()))
    cols = ["baseline", "group", "rows", "base_rate", "brier", "brier_skill_vs_recent", "roc_auc_pooled",
            "roc_auc_within_unit_mean", "pr_auc", "pr_auc_over_base", "low_n"]
    with pd.option_context("display.width", 220, "display.float_format", "{:.4f}".format):
        print(f"[m4] VALIDATION table (H = {cfg.H_label}; Platt rows are in-sample for the calibrator):")
        print(table[cols].to_string(index=False))
    val_pred = val[["unit", "t"] + feats].assign(y=val["y"].to_numpy(), p_raw=p_raw, p_headline=p_head)
    return {"table": table, "scored": scored, "predictors": predictors, "model_str": model_str, "best_iteration": best,
            "curve": curve, "calibrator": cal, "tables": tables, "val_pred": val_pred, "importance": imp,
            "nan_reasons": reasons}


def write_m4_fit(m4, cfg, data_path, out_dir):
    (out_dir / "model.txt").write_text(m4["model_str"])
    (out_dir / "calibrator.json").write_text(json.dumps(m4["calibrator"], indent=2, sort_keys=True))
    (out_dir / "baseline_fit.json").write_text(json.dumps(m4["tables"], indent=2, sort_keys=True))
    m4["val_pred"].to_csv(out_dir / "val_predictions.csv", index=False)
    pd.DataFrame({"iteration": range(1, len(m4["curve"]) + 1), "val_logloss": m4["curve"]}).to_csv(
        out_dir / "model_curve.csv", index=False)
    m4["importance"].rename("gain").to_csv(out_dir / "feature_importance.csv")
    sha = lambda name: model.sha256_file(out_dir / name)  # noqa: E731
    prereg = {
        "config": cfg.name, "H": cfg.H_label,
        "dates": {k: [str(x) for x in v] for k, v in {"train": cfg.train, "val": cfg.val, "test": cfg.test}.items()},
        "features": features.FEATURES, "lightgbm_params": model.PARAMS, "max_rounds": model.MAX_ROUNDS,
        "early_stopping_rounds": model.EARLY_STOPPING, "best_iteration": m4["best_iteration"],
        "calibration_rule": f"Platt on validation iff validation ECE > {model.ECE_THRESHOLD}",
        "calibration_decision": m4["calibrator"]["decision"],
        "sha256": {"model.txt": sha("model.txt"), "calibrator.json": sha("calibrator.json"),
                   "baseline_fit.json": sha("baseline_fit.json"), "val_predictions.csv": sha("val_predictions.csv"),
                   "data": data.file_sha256(data_path)},
        "code_fingerprint": code_fingerprint(),
        "eligibility": "t in [test start, test end), t + H <= test end, mask == 0, label known, all features known (D-024)",
        "headline_predictor": "model (raw LightGBM, or raw -> Platt if calibration_decision == 'platt')",
        "baselines": baselines.BASELINES, "reference": "recent_rate",
        "primary_metric": "Brier skill vs the rolling recent-rate baseline (D-021)",
        "secondary_metrics": ["brier", "roc_auc_pooled", "roc_auc_within_unit_mean", "pr_auc", "pr_auc_over_base",
                              "reliability (overall)", "calibration_in_the_large"],
    }
    (out_dir / "preregistration.json").write_text(json.dumps(prereg, indent=2, sort_keys=True))
    print(f"[m4] pre-registered: {out_dir / 'preregistration.json'}")


# ---------------- M4: the single final-test scoring (stage final-test) ----------------

def _verify_prereg(run_dir, data_path, check_code=True):
    pr_path = run_dir / "preregistration.json"
    if not pr_path.exists():
        raise data.DataQualityError(f"{pr_path} missing: run the fit stage for {run_dir.name} first")
    pr = json.loads(pr_path.read_text())
    if set(pr.get("sha256", {})) != PREREG_KEYS:
        raise data.DataQualityError(f"{run_dir.name}: pre-registration must hash exactly {sorted(PREREG_KEYS)}")
    for name, h in pr["sha256"].items():
        actual = data.file_sha256(data_path) if name == "data" else model.sha256_file(run_dir / name)
        if actual != h:
            raise data.DataQualityError(f"{run_dir.name}: {name} sha256 differs from the pre-registration")
    if check_code and pr["code_fingerprint"] != code_fingerprint():
        raise data.DataQualityError(f"{run_dir.name}: code changed since the pre-registration")
    return pr, model.sha256_file(pr_path)


def _reproduce_validation(run_dir, predictor):
    vp = pd.read_csv(run_dir / "val_predictions.csv", float_precision="round_trip")
    if not (np.array_equal(predictor.raw(vp), vp["p_raw"].to_numpy())
            and np.array_equal(predictor.headline(vp), vp["p_headline"].to_numpy())):
        raise data.DataQualityError(f"{run_dir.name}: frozen predictor does not reproduce its validation predictions")


def score_final_test(reports_root, data_path, configs=None):
    """The ONLY place that reads final-test labels (D-021). Verifies BOTH horizons' pre-registrations, writes ONE
    joint access marker, then scores model + baselines on the test, once. `configs` (name -> RunConfig) defaults to
    the official H = 1 and H = 3 runs; tests pass fixture configs."""
    reports_root = Path(reports_root)
    configs = {n: config_mod.get_config(n) for n in OFFICIAL_RUNS} if configs is None else configs
    runs = list(configs)
    verified = {name: _verify_prereg(reports_root / name, data_path) for name in runs}
    pair = {name: sha for name, (_, sha) in verified.items()}
    marker = reports_root / JOINT_MARKER
    if marker.exists():
        old = json.loads(marker.read_text())
        if old["preregistration_sha256"] != pair:
            raise data.DataQualityError("final test already accessed with a DIFFERENT pre-registration: refusing")
        print(f"[final] joint marker exists with the same pre-registrations -> exact reproduction run")
    else:
        marker.write_text(json.dumps({"first_access_utc": datetime.datetime.now(datetime.UTC).isoformat(),
                                      "preregistration_sha256": pair}, indent=2, sort_keys=True))
        print(f"[final] joint access marker written BEFORE reading any test label: {marker}")
    results = {}
    for name in runs:
        cfg = configs[name]
        run_dir = reports_root / name
        predictor = model.Predictor(run_dir / "model.txt", run_dir / "calibrator.json", features.FEATURES)
        _reproduce_validation(run_dir, predictor)
        fr = build_frames(cfg, data_path)
        gf, alerts = fr["gf"], fr["alerts"]
        a, b = evaluate.split_bounds(cfg, "test", allow_test=True)
        el, counts = evaluate.eligibility(gf, a, b, cfg.H, features.FEATURES)
        score = gf[el].reset_index(drop=True)
        tables = json.loads((run_dir / "baseline_fit.json").read_text())
        bpreds, _, n_hist = baselines.predict_from_tables(tables, gf, score, alerts, cfg)
        if not _keys_equal(bpreds, score):
            raise data.DataQualityError("baseline predictions are not on the test rows")
        scored = bpreds.assign(y=score["y"].to_numpy(), group=score["group"].to_numpy(),
                               model=predictor.headline(score))
        predictors = ["model"]
        if predictor.cal["decision"] == "platt":
            scored = scored.assign(model_raw=predictor.raw(score))
            predictors.append("model_raw")
        allp = predictors + baselines.BASELINES
        table, reasons = evaluate.metric_table(scored, allp, "recent_rate", cfg.min_class_per_unit)
        table = evaluate.low_n_flags(table, cfg.low_n_rows)
        citl = evaluate.calibration_in_the_large(scored, allp)
        print(f"[final] {name} (H = {cfg.H_label}) test [{a}, {b}): in range {counts['in_range']:,}, eligible "
              f"{counts['eligible']:,}; excluded exclusive {counts['excluded_exclusive']}, "
              f"overlapping {counts['excluded_overlapping']}")
        cols = ["baseline", "group", "rows", "base_rate", "brier", "brier_skill_vs_recent", "roc_auc_pooled",
                "roc_auc_within_unit_mean", "within_unit_units_used", "pr_auc", "pr_auc_over_base", "low_n"]
        with pd.option_context("display.width", 220, "display.float_format", "{:.4f}".format):
            print(f"[final] FINAL TEST table, {name}:")
            print(table[cols].to_string(index=False))
        table.to_csv(run_dir / "metrics.csv", index=False)
        (run_dir / "metrics.json").write_text(table.to_json(orient="records", indent=2))
        citl.to_csv(run_dir / "calibration_in_the_large.csv", index=False)
        bins = evaluate.reliability_plot(scored, allp, run_dir / "reliability.png",
                                         f"Reliability on the final test, H = {cfg.H_label}")
        bins.to_csv(run_dir / "reliability_bins.csv", index=False)
        (run_dir / "final_test_checks.json").write_text(json.dumps(
            {"eligibility": counts, "nan_reasons": reasons, "predictors": allp,
             "recent_rate_history_n": {"min": float(n_hist.min()), "median": float(np.median(n_hist))}},
            indent=2, default=str))
        results[name] = table
    return results


# ---------------- M4: new-regime section (D-015, exploratory, H = 1) ----------------

def run_new_regime(cfg, out_dir, reports_root, official_data_path):
    reports_root = Path(reports_root)
    if not (reports_root / JOINT_MARKER).exists():
        raise data.DataQualityError("the final test has not been scored yet: run --stage final-test first")
    off_dir = reports_root / "official"
    _, pr_sha = _verify_prereg(off_dir, official_data_path, check_code=False)
    frozen_sha = json.loads((reports_root / JOINT_MARKER).read_text())["preregistration_sha256"]["official"]
    if pr_sha != frozen_sha:  # the predictor must be the one that was scored on the final test
        raise data.DataQualityError("official pre-registration differs from the one frozen at the final test")
    predictor = model.Predictor(off_dir / "model.txt", off_dir / "calibrator.json", features.FEATURES)
    _reproduce_validation(off_dir, predictor)
    print(f"[api] frozen H = 1 predictor loaded and reproduced on validation ({predictor.cal['decision']})")
    stats = {}
    alerts = data.load_api(ROOT / cfg.data_path, cfg, stats)
    check_source(alerts, "api")
    print(f"[api] alert types kept: {cfg.api_alert_types}; present {stats['alert_types']}; dropped {stats['alert_types_dropped']}")
    print(f"[api] loader: {stats}")
    detected = grid.detect_gaps(alerts, cfg.gap_min_hours, cfg.history_start, cfg.coverage_end)
    grid.check_gaps(detected, cfg.approved_gaps)
    counts = data.alert_counts(alerts[alerts["started_at"] >= cfg.history_start])
    print(f"[api] history_start {cfg.history_start}, coverage_end {cfg.coverage_end}; gaps detected: {detected}")
    print(f"[api] alerts starting in coverage: >24h {counts['over_24h_total']} {counts['over_24h_by_unit']}; "
          f"exactly-30-min {counts['exactly_30min_total']}; open {counts['missing_finished_at']}")
    g = grid.build_grid(alerts, cfg.grid_start, cfg.grid_end, cfg.H, cfg.target_levels, cfg.standing_cap,
                        config_mod.mask_gaps(cfg), cfg.post_gap_mask, coverage_end=cfg.coverage_end)
    masked_hours = check_gap_rows(g, cfg)
    zones = config_mod.uncertainty_zones(cfg)
    f = features.build_features(alerts, pd.DatetimeIndex(g["t"].drop_duplicates().sort_values()), zones,
                                cfg.standing_cap, cfg.target_levels)
    gf = features.join_to_grid(g, f)
    a, b = cfg.test
    el, el_counts = evaluate.eligibility(gf, a, b, cfg.H, features.FEATURES)
    score = gf[el].reset_index(drop=True)
    print(f"[api] grid {g.shape}, t {g.t.min()} -> {g.t.max()}; history-zone masked hours {masked_hours}; "
          f"eligible {el_counts['eligible']:,} (first scored row {score.t.min()}, last {score.t.max()}); "
          f"excluded exclusive {el_counts['excluded_exclusive']}")
    tables = json.loads((off_dir / "baseline_fit.json").read_text())
    bpreds, _, n_hist = baselines.predict_from_tables(tables, gf, score, alerts, cfg)
    if not _keys_equal(bpreds, score):
        raise data.DataQualityError("baseline predictions are not on the API rows")
    scored = bpreds.assign(y=score["y"].to_numpy(), group=score["group"].to_numpy(), model=predictor.headline(score))
    allp = ["model"] + baselines.BASELINES
    table, reasons = evaluate.metric_table(scored, allp, "recent_rate", cfg.min_class_per_unit)
    table = evaluate.low_n_flags(table, cfg.low_n_rows)
    citl = evaluate.calibration_in_the_large(scored, allp)
    transfer = citl.merge(table.rename(columns={"baseline": "predictor"})[
        ["predictor", "group", "roc_auc_within_unit_mean", "within_unit_units_used", "within_unit_units_excluded",
         "roc_auc_pooled", "low_n"]], on=["predictor", "group"])
    # (a) before/after, official [07-27, 08-29) vs API [09-13, 10-12 16:00): computed after the final test (marker above)
    ocfg = config_mod.official()
    oal = data.load_official(official_data_path, ocfg)
    og = grid.build_grid(oal, ocfg.grid_start, ocfg.grid_end, ocfg.H, "any", ocfg.standing_cap,
                         config_mod.mask_gaps(ocfg), ocfg.post_gap_mask, coverage_end=ocfg.coverage_end)
    on_o = {u: v[2] for u, v in grid.unit_intervals(oal, ocfg.standing_cap).items()}
    on_a = {u: v[2] for u, v in grid.unit_intervals(alerts, cfg.standing_cap).items()}
    before = evaluate.exposure_summary(og, on_o, ocfg.test[0], pd.Timestamp("2026-08-29", tz="UTC"),
                                       config_mod.uncertainty_zones(ocfg))
    after = evaluate.exposure_summary(g, on_a, cfg.grid_start, cfg.grid_end, zones)
    ba = []
    for label, df in (("official_2026-07-27_08-29", before), ("api_2026-09-13_10-12", after)):
        ba.append(pd.concat([df, evaluate.pooled_by_group(df)], ignore_index=True).assign(window=label))
    ba = pd.concat(ba, ignore_index=True)
    with pd.option_context("display.width", 220, "display.float_format", "{:.4f}".format):
        print("[api] TRANSFER (exploratory, frozen H = 1 model on 'any alert' onsets):")
        print(table[["baseline", "group", "rows", "base_rate", "brier", "brier_skill_vs_recent",
                     "roc_auc_pooled", "roc_auc_within_unit_mean", "pr_auc", "low_n"]].to_string(index=False))
        print(citl.to_string(index=False))
        piv = ba[ba.unit.str.startswith("[")].pivot(index="group", columns="window",
                                                    values=["onsets_per_30d", "share_under_alert"])
        print("[api] BEFORE/AFTER (groups):")
        print(piv.to_string())
    out_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_dir / "metrics.csv", index=False)
    (out_dir / "metrics.json").write_text(table.to_json(orient="records", indent=2))
    transfer.to_csv(out_dir / "transfer.csv", index=False)
    ba.to_csv(out_dir / "before_after.csv", index=False)
    bins = evaluate.reliability_plot(scored, allp, out_dir / "reliability.png",
                                     "Reliability on the new regime (exploratory, H = 1)")
    bins.to_csv(out_dir / "reliability_bins.csv", index=False)
    meta = {"config": cfg.name, "source": "api", "dump": cfg.data_path, "H": cfg.H_label,
            "api_alert_types": list(cfg.api_alert_types),
            "history_start": str(cfg.history_start), "coverage_end": str(cfg.coverage_end),
            "grid": [str(cfg.grid_start), str(cfg.grid_end)], "grid_shape": list(g.shape),
            "loader": stats, "alert_counts_in_coverage": counts, "eligibility": el_counts,
            "scored_range": [str(score.t.min()), str(score.t.max())], "nan_reasons": reasons,
            "frozen_predictor": json.loads((off_dir / "preregistration.json").read_text())["sha256"],
            "git_commit": _git("rev-parse", "--verify", "HEAD"), "git_dirty": bool(_git("status", "--porcelain")),
            "python": platform.python_version(), "packages": {p: version(p) for p in PACKAGES},
            "features": features.FEATURES}
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"[run] wrote {out_dir}")
    return table, transfer, ba


def main(argv=None):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError(f"Python 3.13 required (requirements.txt), got {platform.python_version()}")
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--stage", choices=["fit", "final-test"], default="fit")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--data-path", default=None)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--reports-root", default=str(ROOT / "reports"))
    args = ap.parse_args(argv)
    if args.as_of is not None and args.config != "monthly":
        raise ValueError("--as-of is only valid with --config monthly")
    if args.stage == "final-test":
        if args.config is not None:
            raise ValueError("--stage final-test scores both horizons; do not pass --config")
        data_path = Path(args.data_path) if args.data_path else data.download_official(config_mod.official(), ROOT / "data")
        score_final_test(args.reports_root, data_path)
        return
    if args.config is None:
        raise ValueError("--config is required for the fit stage")
    cfg = config_mod.get_config(args.config, args.as_of)
    if cfg.source == "api":
        out_dir = Path(args.out_dir) if args.out_dir else Path(args.reports_root) / cfg.name
        if not (Path(args.reports_root) / JOINT_MARKER).exists():
            raise data.DataQualityError("the final test has not been scored yet: run --stage final-test first")
        official_path = Path(args.data_path) if args.data_path else data.download_official(config_mod.official(), ROOT / "data")
        run_new_regime(cfg, out_dir, args.reports_root, official_path)
        return
    if cfg.source != "official":
        raise NotImplementedError(f"unknown source {cfg.source!r}")
    if (Path(args.reports_root) / JOINT_MARKER).exists():  # refit guard independent of --out-dir
        raise data.DataQualityError("the final test was already accessed: refitting is not allowed")
    data_path = Path(args.data_path) if args.data_path else data.download_official(cfg, ROOT / "data")
    out_dir = Path(args.out_dir) if args.out_dir else Path(args.reports_root) / cfg.name
    run_pipeline(cfg, data_path, out_dir)


if __name__ == "__main__":
    main()
