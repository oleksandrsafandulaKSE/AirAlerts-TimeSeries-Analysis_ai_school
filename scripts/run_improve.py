"""M7: post-hoc improvement rows (plans/M7.md). The frozen headline (reports/official) is NOT changed.

    python scripts/run_improve.py            # -> reports/improve/

Order: build frames (headline code, read-only) -> M7 inputs -> feature-block acceptance on backtest folds INSIDE train
(no validation/test labels) -> V2/V3 frozen fits (early stopping on validation) -> V5 blend weight on validation ->
weekly refits V1/V4 (D-014) -> post-hoc scoring on the already-seen test (human-approved exception, proposed D-030).
"""
import argparse
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import run_all  # noqa: E402  (build_frames, code_fingerprint; read-only use)
from src import baselines, config as config_mod, data, evaluate, features, model  # noqa: E402
from improve import features_plus as FP, model_plus as MP  # noqa: E402

BASE = features.FEATURES
FOLD_CUTS = ["2025-07-01", "2025-10-01", "2026-01-01", "2026-04-01"]
FOLD_SCORE = pd.Timedelta(weeks=8)
REFIT_EARLY = pd.Timedelta(days=14)
WEEKLY_CUTS = ["2026-07-27", "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31"]
ACCEPT_REL = 0.005
BLEND_GRID = [round(0.1 * i, 1) for i in range(11)]


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def eligible(df, a, b, H, feats, need_offset=True):
    """t in [a, b), t + H <= b, unmasked, label known, every listed feature (and the offset) known."""
    ok = (df["t"] >= a) & (df["t"] < b) & (df["t"] + H <= b) & (df["mask"] == 0) & df["y"].notna()
    ok &= df[feats].notna().all(axis=1)
    if need_offset:
        ok &= df["offset_rate"].notna()
    return df[ok].reset_index(drop=True)


def brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y, float)) ** 2))


def fit_predict(kind, fit, val, score, feats):
    if kind == "plain":
        b = MP.train_plain(fit, val, feats)
        return MP.predict_plain(b, score, feats), b
    b = MP.train_offset(fit, val, feats)
    return MP.predict_offset(b, score, feats), b


def accept(ref, cand, rel=ACCEPT_REL):
    """Plan §3 rule: equal-weighted mean fold Brier drops by >= rel (relative) AND the fold Brier drops in >= 3 of 4
    folds; ties reject. ref/cand: {fold: brier}."""
    m_ref, m_cand = float(np.mean(list(ref.values()))), float(np.mean(list(cand.values())))
    wins = sum(cand[c] < ref[c] for c in ref)
    return (m_cand <= m_ref * (1 - rel)) and m_cand < m_ref and wins >= 3, m_ref, m_cand, wins


def choose_blend(p_model_val, p_recent_val, y_val, grid=BLEND_GRID):
    """V5 weight from VALIDATION only; ties -> the larger weight on the model."""
    scores = {w: brier(w * np.asarray(p_model_val) + (1 - w) * np.asarray(p_recent_val), y_val) for w in grid}
    return min(grid, key=lambda w: (round(scores[w], 12), -w)), scores   # float noise below 1e-12 counts as a tie


def refit_windows(C, end, start):
    """Weekly refit step at cut-off C: fit [start, C - 14 d) with t + H <= C - 14 d; early stopping [C - 14 d, C) with
    t + H <= C; scores [C, end) only."""
    return (start, C - REFIT_EARLY), (C - REFIT_EARLY, C), (C, end)


def refit_step(gfp, C, end, start, H, feats, kind, score_rows):
    (fa, fb), (va, vb), (sa, sb) = refit_windows(C, end, start)
    fit = eligible(gfp, fa, fb, H, feats, need_offset=(kind == "offset"))
    val = eligible(gfp, va, vb, H, feats, need_offset=(kind == "offset"))
    week = score_rows[(score_rows["t"] >= sa) & (score_rows["t"] < sb)]
    if not len(week):
        return None, fit, val, week, None
    p, b = fit_predict(kind, fit, val, week, feats)
    return p, fit, val, week, b


def block_acceptance(gfp, H):
    """Greedy A, B, C on 4 backtest folds inside train; identical keys per fold (all candidate features known)."""
    every = BASE + FP.BLOCK_A + FP.BLOCK_B + FP.BLOCK_C
    accepted, rows = [], []
    fold_data = []
    for c in FOLD_CUTS:
        C = ts(c)
        fit = eligible(gfp, gfp["t"].min(), C - REFIT_EARLY, H, every)
        val = eligible(gfp, C - REFIT_EARLY, C, H, every)
        score = eligible(gfp, C, C + FOLD_SCORE, H, every)
        fold_data.append((c, fit, val, score))
    ref = {}
    for c, fit, val, score in fold_data:
        p, _ = fit_predict("offset", fit, val, score, BASE)
        ref[c] = brier(p, score["y"])
    for name in ("A", "B", "C"):
        cand = {}
        feats = BASE + [f for blk in accepted for f in FP.BLOCKS[blk]] + FP.BLOCKS[name]
        for c, fit, val, score in fold_data:
            p, _ = fit_predict("offset", fit, val, score, feats)
            cand[c] = brier(p, score["y"])
        ok, m_ref, m_cand, wins = accept(ref, cand)
        for c in FOLD_CUTS:
            rows.append({"block": name, "fold_cut": c, "reference_brier": ref[c], "candidate_brier": cand[c],
                         "score_rows": len(fold_data[FOLD_CUTS.index(c)][3])})
        rows.append({"block": name, "fold_cut": "mean", "reference_brier": m_ref, "candidate_brier": m_cand,
                     "relative_change": m_cand / m_ref - 1, "folds_improved": wins, "accepted": ok})
        print(f"[m7] block {name}: mean Brier {m_ref:.5f} -> {m_cand:.5f} ({100 * (m_cand / m_ref - 1):+.2f} %), "
              f"{wins}/4 folds better -> {'ACCEPT' if ok else 'reject'}")
        if ok:
            accepted.append(name)
            ref = cand
    return accepted, pd.DataFrame(rows)


def metrics(scored, preds, cfg):
    t, reasons = evaluate.metric_table(scored, preds, "recent_rate", cfg.min_class_per_unit)
    t = evaluate.low_n_flags(t, cfg.low_n_rows)
    extra = []
    for p in preds:
        for grp in evaluate.GROUPS:
            g = scored if grp == "overall" else scored[scored["group"] == grp]
            e = model.ece(g[p].to_numpy(), g["y"].to_numpy()) if len(g) else np.nan
            extra.append({"baseline": p, "group": grp, "ece": e,
                          "mean_pred_minus_obs": float(g[p].mean() - g["y"].mean()) if len(g) else np.nan})
    return t.merge(pd.DataFrame(extra), on=["baseline", "group"]), reasons


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-path", default=str(ROOT / "data" / "official_data_en.csv"))
    ap.add_argument("--reports-root", default=str(ROOT / "reports"))
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    reports = Path(args.reports_root)
    out = Path(args.out_dir) if args.out_dir else reports / "improve"
    cfg = config_mod.official()
    H = cfg.H
    off_dir = reports / "official"
    pr = json.loads((off_dir / "preregistration.json").read_text())
    if pr["code_fingerprint"] != run_all.code_fingerprint():
        raise data.DataQualityError("headline code changed since the pre-registration: M7 must not touch src/ or run_all.py")

    fr = run_all.build_frames(cfg, args.data_path)
    alerts, gf = fr["alerts"], fr["gf"]
    plus = FP.compute_plus(alerts, fr["g"], H, cfg.standing_cap, config_mod.uncertainty_zones(cfg))
    gfp = gf.merge(plus, on=["unit", "t"], how="left", validate="one_to_one")
    print(f"[m7] inputs joined: {gfp.shape}")

    # 1) feature blocks (train only)
    accepted, blocks = block_acceptance(gfp[gfp["t"] < cfg.train[1]].copy(), H)
    v3_feats = BASE + [f for b in accepted for f in FP.BLOCKS[b]]
    print(f"[m7] accepted blocks: {accepted or 'none'}; V3 features {len(v3_feats)}")

    # 2) frozen V2 / V3 (early stopping on validation), selection keys = rows where V3 features are known
    fit2, val2 = eligible(gfp, cfg.train[0], cfg.train[1], H, BASE), eligible(gfp, cfg.val[0], cfg.val[1], H, BASE)
    fit3, val3 = eligible(gfp, cfg.train[0], cfg.train[1], H, v3_feats), eligible(gfp, cfg.val[0], cfg.val[1], H, v3_feats)
    base_fit = eligible(gfp, cfg.train[0], cfg.train[1], H, BASE, need_offset=False)
    base_val = eligible(gfp, cfg.val[0], cfg.val[1], H, BASE, need_offset=False)
    drops = {"train": [len(base_fit) - len(fit3), len(base_fit)], "validation": [len(base_val) - len(val3), len(base_val)]}
    print(f"[m7] rows dropped for a missing M7 input (offset / new features): train {drops['train'][0]:,} of "
          f"{drops['train'][1]:,}; validation {drops['validation'][0]:,} of {drops['validation'][1]:,}")
    b2, b3 = MP.train_offset(fit2, val2, BASE), MP.train_offset(fit3, val3, v3_feats)
    sel = val3
    tables = json.loads((off_dir / "baseline_fit.json").read_text())
    rr_val, _, _ = baselines.predict_from_tables(tables, gf, sel, alerts, cfg)
    p_v2, p_v3 = MP.predict_offset(b2, sel, BASE), MP.predict_offset(b3, sel, v3_feats)
    predictor = model.Predictor(off_dir / "model.txt", off_dir / "calibrator.json", BASE)
    p_v0 = predictor.headline(sel)
    w_best, blend = choose_blend(p_v3, rr_val["recent_rate"].to_numpy(), sel["y"])
    val_briers = {"V0": brier(p_v0, sel["y"]), "V2": brier(p_v2, sel["y"]), "V3": brier(p_v3, sel["y"]),
                  "V5": blend[w_best], "recent_rate": brier(rr_val["recent_rate"], sel["y"])}
    best = min(["V2", "V3", "V5"], key=lambda v: val_briers[v])
    val_pred = sel[["unit", "t", "y"]].assign(V2=p_v2, V3=p_v3, recent_rate=rr_val["recent_rate"].to_numpy())
    print(f"[m7] validation Brier on {len(sel):,} identical rows: " + ", ".join(f"{k} {v:.5f}" for k, v in val_briers.items())
          + f"; blend w = {w_best}; best post-hoc (by validation) = {best}")

    # 3) post-hoc test scoring (human-approved exception) on identical keys
    test = eligible(gfp, cfg.test[0], cfg.test[1], H, v3_feats)
    rr_test, _, _ = baselines.predict_from_tables(tables, gf, test, alerts, cfg)
    scored = test[["unit", "t", "y", "group"]].copy()
    scored["recent_rate"] = rr_test["recent_rate"].to_numpy()
    scored["V0_frozen_headline"] = predictor.headline(test)
    scored["V2_offset"] = MP.predict_offset(b2, test, BASE)
    scored["V3_offset_plus"] = MP.predict_offset(b3, test, v3_feats)
    scored["V5_blend"] = w_best * scored["V3_offset_plus"] + (1 - w_best) * scored["recent_rate"]
    weekly = []
    for kind, feats, col in (("plain", BASE, "V1_weekly_refit"), ("offset", v3_feats, "V4_weekly_refit_offset_plus")):
        scored[col] = np.nan
        for i, c in enumerate(WEEKLY_CUTS):
            C = ts(c)
            end = ts(WEEKLY_CUTS[i + 1]) if i + 1 < len(WEEKLY_CUTS) else cfg.test[1]
            p, fit, val, week, b = refit_step(gfp, C, end, cfg.train[0], H, feats, kind, test)
            idx = (scored["t"] >= C) & (scored["t"] < end)
            if p is None:
                weekly.append({"variant": col, "cut": c, "rows": 0})
                continue
            scored.loc[idx, col] = p
            weekly.append({"variant": col, "cut": c, "fit_rows": len(fit), "early_rows": len(val), "rows": int(idx.sum()),
                           "best_iteration": b.best_iteration, "brier": brier(p, week["y"]),
                           "recent_rate_brier": brier(scored.loc[idx, "recent_rate"], week["y"])})
            print(f"[m7] {col} cut {c}: fit {len(fit):,}, early {len(val):,}, scored {int(idx.sum()):,}")
    if scored.drop(columns=["unit", "t", "y", "group"]).isna().any().any():
        raise data.DataQualityError("a variant has no prediction on some identical-key test rows")
    preds = ["V0_frozen_headline", "V1_weekly_refit", "V2_offset", "V3_offset_plus", "V4_weekly_refit_offset_plus",
             "V5_blend", "recent_rate"]
    table, reasons = metrics(scored, preds, cfg)
    cols = ["baseline", "group", "rows", "brier", "brier_skill_vs_recent", "roc_auc_within_unit_mean", "pr_auc", "low_n"]
    with pd.option_context("display.width", 220, "display.float_format", "{:.4f}".format):
        print("[m7] POST-HOC test table (test already seen; identical rows for every variant):")
        print(table[cols].to_string(index=False))
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "variants_test_posthoc.csv", index=False)
    blocks.to_csv(out / "feature_blocks.csv", index=False)
    pd.DataFrame(weekly).to_csv(out / "weekly_refit.csv", index=False)
    (out / "blend_weight.json").write_text(json.dumps({"grid": blend, "w": w_best}, indent=2))
    val_pred.to_csv(out / "validation_predictions.csv", index=False)
    (out / "validation_selection.json").write_text(json.dumps(
        {"rows": len(sel), "brier": val_briers, "best_posthoc_by_validation": best, "accepted_blocks": accepted,
         "v3_features": v3_feats}, indent=2))
    evaluate.reliability_plot(scored, [best_col(best), "V0_frozen_headline", "recent_rate"], out / "reliability_best_posthoc.png",
                              "Post-hoc (test already seen): best M7 variant vs headline")
    meta = {"plan": "plans/M7.md", "posthoc": True, "test_rows_identical_keys": len(test), "nan_reasons": reasons,
            "rows_dropped_missing_m7_input": drops,
            "code_fingerprint_headline": pr["code_fingerprint"], "python": platform.python_version(),
            "packages": {p: version(p) for p in run_all.PACKAGES}, "fold_cuts": FOLD_CUTS, "weekly_cuts": WEEKLY_CUTS}
    (out / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"[run] wrote {out}")
    return table


def best_col(v):
    return {"V2": "V2_offset", "V3": "V3_offset_plus", "V5": "V5_blend"}[v]


if __name__ == "__main__":
    main()
