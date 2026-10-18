"""M10 (plans/M10.md): label-variant measurement, recency weighting, exposure features, stability tables.
The frozen headline (reports/official) and src/ are NOT changed. No test label is read (§E is gated and off).

    python scripts/run_m10.py                 # all stages: --labels --recency --exposure --stability
    python scripts/run_m10.py --stability     # one stage (later stages read earlier outputs from reports/m10/)

Everything below is computed on rows with t + H <= test start; the test period is cut off right after the build.
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

from scripts import run_all, run_improve as RI  # noqa: E402  (read-only use)
from src import baselines, config as config_mod, data, evaluate, features, regions  # noqa: E402
from improve import exposure as EX, features_plus as FP, labels_variant as LV, model_plus as MP, recency as RC  # noqa: E402
from extras import stability as ST  # noqa: E402

BASE = features.FEATURES
STAGES = ["labels", "recency", "exposure", "stability"]
QUARTERS = ["2025-01-01", "2025-04-01", "2025-07-01", "2025-10-01", "2026-01-01", "2026-04-01", "2026-07-01"]
APPROVAL = "posthoc_approval.json"


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def periods(cfg):
    q = [(f"{ts(a).year}Q{(ts(a).month - 1) // 3 + 1}", ts(a), ts(b)) for a, b in zip(QUARTERS, QUARTERS[1:])]
    return [("train", *cfg.train), ("validation", *cfg.val)] + q


def cut_before_test(df, cfg):
    """Keep rows whose label window ends by the test start (no test label may be read in M10)."""
    out = df[df["t"] + cfg.H <= cfg.test[0]].reset_index(drop=True)
    if (out["t"] + cfg.H > cfg.test[0]).any():
        raise data.DataQualityError("a row's label window reaches into the test period")
    return out


def with_plus(alerts, g, gf, cfg):
    g, gf = cut_before_test(g, cfg), cut_before_test(gf, cfg)
    plus = FP.compute_plus(alerts, g, cfg.H, cfg.standing_cap, config_mod.uncertainty_zones(cfg))
    return gf.merge(plus, on=["unit", "t"], how="left", validate="one_to_one"), g


def folds(gfp, H, feats):
    """The 4 M7 backtest folds inside train (fit t + H <= C - 14 d; early stop [C - 14 d, C), t + H <= C)."""
    out = []
    for c in RI.FOLD_CUTS:
        C = ts(c)
        F = C - RI.REFIT_EARLY
        out.append({"cut": c, "F": F,
                    "fit": RI.eligible(gfp, gfp["t"].min(), F, H, feats),
                    "val": RI.eligible(gfp, F, C, H, feats),
                    "score": RI.eligible(gfp, C, C + RI.FOLD_SCORE, H, feats),
                    "fit_base": RI.eligible(gfp, gfp["t"].min(), F, H, BASE, need_offset=False)})
    return out


def fit_score(fit, val, score, feats, F, h):
    b = RC.train_offset_weighted(fit, val, feats, RC.recency_weights(fit["t"], F, h) if h is not None else None)
    return MP.predict_offset(b, score, feats), b


def reporting_rr(gfp, fit_base, score, cfg):
    """D-025 reporting baseline: (k + 10 p_unit) / (n + 10), p_unit from the eligible FIT rows, frozen."""
    p_unit = baselines.unit_train_rates(fit_base)
    return baselines.recent_rate(gfp, score, p_unit, cfg.shrink_alpha, cfg.recent_window, cfg.H)


def scored_table(score, p, rr, cfg, tag):
    s = score[["unit", "t", "y"]].assign(group=[regions.group_of(u) for u in score["unit"]], model=p, recent_rate=rr)
    t, reasons = evaluate.metric_table(s, ["model", "recent_rate"], "recent_rate", cfg.min_class_per_unit)
    t = evaluate.low_n_flags(t, cfg.low_n_rows)
    for k, v in tag.items():
        t.insert(0, k, v)
    return t, reasons


# ------------------------------------------------------------------------------------------------ stages
def stage_labels(ctx, out):
    cfg, H = ctx["cfg"], ctx["cfg"].H
    a0 = ctx["alerts"]
    a1 = LV.drop_hromada(a0)
    print(f"[m10:A] L0 alerts {len(a0):,}; L1 alerts {len(a1):,} (dropped {len(a0) - len(a1):,} hromada rows)")
    g1, gf1 = LV.build_variant_frames(a1, cfg)
    gfp1, g1c = with_plus(a1, g1, gf1, cfg)
    ctx["gfp1"] = gfp1
    zones = config_mod.uncertainty_zones(cfg)
    per = periods(cfg)
    d0 = LV.describe(ctx["g0c"], a0, cfg.standing_cap, per, zones, H)
    d1 = LV.describe(g1c, a1, cfg.standing_cap, per, zones, H)
    tab = LV.side_by_side(d0, d1)
    tab.to_csv(out / "labels_variant.csv", index=False)
    grp = tab[tab["unit"].str.startswith("[") & tab["period"].isin(["train", "validation"])]
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        print("[m10:A1] pooled groups, L0 vs L1:")
        print(grp[["period", "group", "onsets_L0", "onsets_L1", "base_rate_L0", "base_rate_L1",
                   "share_under_alert_L0", "share_under_alert_L1"]].to_string(index=False))
    ch = LV.onset_changes(a0, a1, cfg.standing_cap, per)
    ch.to_csv(out / "labels_onset_changes.csv", index=False)
    tot = ch[ch["period"] == "train"][["l0_onsets", "kept", "shifted", "disappeared", "l1_onsets", "new_in_l1"]].sum()
    print(f"[m10:A2] train onsets: {tot.to_dict()}")
    rows, reasons, counts = [], [], {}
    for variant, gfp in (("L0", ctx["gfp0"]), ("L1", gfp1)):
        for f in folds(gfp, H, BASE):
            if variant == "L0" and "fold_pred_inf" in ctx:
                p = ctx["fold_pred_inf"][f["cut"]]
            else:
                p, _ = fit_score(f["fit"], f["val"], f["score"], BASE, f["F"], None)
            rr = reporting_rr(gfp, f["fit_base"], f["score"], cfg)
            t, r = scored_table(f["score"], p, rr, cfg, {"variant": variant, "split": f"fold {f['cut']}"})
            rows.append(t)
            reasons += r
        fit = RI.eligible(gfp, cfg.train[0], cfg.train[1], H, BASE)
        val = RI.eligible(gfp, cfg.val[0], cfg.val[1], H, BASE)
        p, _ = fit_score(fit, val, val, BASE, cfg.train[1], None)
        rr = reporting_rr(gfp, RI.eligible(gfp, cfg.train[0], cfg.train[1], H, BASE, need_offset=False), val, cfg)
        t, r = scored_table(val, p, rr, cfg, {"variant": variant, "split": "validation"})
        rows.append(t)
        reasons += r
        print(f"[m10:A3] {variant}: validation rows {len(val):,}, base rate {val['y'].mean():.4f}")
        counts[variant] = {"validation_rows": len(val), "validation_base_rate": float(val["y"].mean()),
                           "frame_shape": list(gfp.shape)}
    pr = pd.concat(rows, ignore_index=True)
    pr.to_csv(out / "labels_predictability.csv", index=False)
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        print("[m10:A3] predictability (each variant vs ITS OWN recent rate; Brier NOT comparable across variants):")
        print(pr[(pr["baseline"] == "model")][["variant", "split", "group", "rows", "base_rate",
                                                "brier_skill_vs_recent", "roc_auc_within_unit_mean"]].to_string(index=False))
    return {"nan_reasons": reasons, "counts": counts, "l1_alerts": len(a1), "l0_alerts": len(a0)}


def stage_recency(ctx, out):
    cfg, H, gfp = ctx["cfg"], ctx["cfg"].H, ctx["gfp0"]
    fl = folds(gfp, H, BASE)
    briers, rows = {}, []
    ctx["fold_pred_inf"] = {}
    for h in RC.HALF_LIVES:
        briers[h] = {}
        for f in fl:
            p, b = fit_score(f["fit"], f["val"], f["score"], BASE, f["F"], h)
            briers[h][f["cut"]] = RI.brier(p, f["score"]["y"])
            if h is None:
                ctx["fold_pred_inf"][f["cut"]] = p
            rows.append({"half_life_days": h if h is not None else "inf", "fold_cut": f["cut"], "fit_rows": len(f["fit"]),
                         "score_rows": len(f["score"]), "best_iteration": b.best_iteration,
                         "brier": briers[h][f["cut"]]})
    results = {}
    for h in RC.HALF_LIVES[1:]:
        ok, m_ref, m_cand, wins = RI.accept(briers[None], briers[h])
        results[h] = (ok, m_cand)
        rows.append({"half_life_days": h, "fold_cut": "mean", "brier": m_cand, "reference_brier": m_ref,
                     "relative_change": m_cand / m_ref - 1, "folds_improved": wins, "accepted": ok})
        print(f"[m10:B] h = {h} d: mean Brier {m_ref:.5f} -> {m_cand:.5f} ({100 * (m_cand / m_ref - 1):+.2f} %), "
              f"{wins}/4 folds better -> {'PASS' if ok else 'fail'}")
    chosen = RC.choose_half_life(results)
    print(f"[m10:B] chosen half-life: {chosen if chosen is not None else 'none (equal weights stay)'}")
    pd.DataFrame(rows).to_csv(out / "recency_folds.csv", index=False)
    # validation rows: V2 rebuilt (h = inf) must reproduce M7's saved V2; chosen h next to it
    fit = RI.eligible(gfp, cfg.train[0], cfg.train[1], H, BASE)
    val = RI.eligible(gfp, cfg.val[0], cfg.val[1], H, BASE)
    p_inf, _ = fit_score(fit, val, val, BASE, cfg.train[1], None)
    m7 = pd.read_csv(ctx["reports"] / "improve" / "validation_predictions.csv", parse_dates=["t"])
    chk = val[["unit", "t"]].assign(p=p_inf).merge(m7, on=["unit", "t"], validate="one_to_one")
    if len(chk) != len(m7) or len(chk) != len(val) or np.max(np.abs(chk["p"] - chk["V2"])) > 1e-12:
        raise data.DataQualityError("rebuilt V2 does not reproduce reports/improve V2 on validation (1e-12)")
    print(f"[m10:B] V2 rebuilt on {len(val):,} validation rows reproduces M7 V2 to 1e-12: PASS")
    p_h = p_inf if chosen is None else fit_score(fit, val, val, BASE, cfg.train[1], chosen)[0]
    ctx["val_rows"] = val
    ctx["val_V2"] = p_inf
    ctx["val_after_B"] = p_h
    ctx["chosen_h"] = chosen
    ctx["fold_rows"] = {f["cut"]: {"fit": len(f["fit"]), "early": len(f["val"]), "score": len(f["score"]),
                                   "score_base_rate": float(f["score"]["y"].mean())} for f in fl}
    (out / "recency_choice.json").write_text(json.dumps(
        {"candidates": [h for h in RC.HALF_LIVES], "chosen_half_life_days": chosen,
         "validation_brier": {"V2": RI.brier(p_inf, val["y"]), "V2_recency": RI.brier(p_h, val["y"])}}, indent=2))
    return {"chosen_half_life_days": chosen, "folds": ctx["fold_rows"],
            "validation_rows": len(val), "validation_base_rate": float(val["y"].mean())}


def stage_exposure(ctx, out):
    cfg, H = ctx["cfg"], ctx["cfg"].H
    if "chosen_h" not in ctx:
        ctx["chosen_h"] = json.loads((out / "recency_choice.json").read_text())["chosen_half_life_days"]
    h = ctx["chosen_h"]
    ex = EX.exposure_features(ctx["alerts"], ctx["g0c"], cfg.standing_cap, config_mod.uncertainty_zones(cfg))
    gfp = ctx["gfp0"].merge(ex, on=["unit", "t"], how="left", validate="one_to_one")
    pre = gfp[gfp["t"] < cfg.val[0]]
    print(f"[m10:C] block D NaN before validation: {pre[EX.BLOCK_D].isna().sum().to_dict()}; "
          f"medians {pre[EX.BLOCK_D].median().round(3).to_dict()}")
    every = BASE + EX.BLOCK_D
    fl = folds(gfp, H, every)
    ref, cand, rows = {}, {}, []
    for f in fl:
        p_r, _ = fit_score(f["fit"], f["val"], f["score"], BASE, f["F"], h)
        p_c, _ = fit_score(f["fit"], f["val"], f["score"], every, f["F"], h)
        ref[f["cut"]], cand[f["cut"]] = RI.brier(p_r, f["score"]["y"]), RI.brier(p_c, f["score"]["y"])
        rows.append({"block": "D", "fold_cut": f["cut"], "reference_brier": ref[f["cut"]],
                     "candidate_brier": cand[f["cut"]], "score_rows": len(f["score"])})
    ok, m_ref, m_cand, wins = RI.accept(ref, cand)
    rows.append({"block": "D", "fold_cut": "mean", "reference_brier": m_ref, "candidate_brier": m_cand,
                 "relative_change": m_cand / m_ref - 1, "folds_improved": wins, "accepted": ok,
                 "half_life_days": h})
    print(f"[m10:C] block D: mean Brier {m_ref:.5f} -> {m_cand:.5f} ({100 * (m_cand / m_ref - 1):+.2f} %), "
          f"{wins}/4 folds better -> {'ACCEPT' if ok else 'reject'}")
    pd.DataFrame(rows).to_csv(out / "exposure_folds.csv", index=False)
    ctx["exposure_accepted"] = bool(ok)
    ctx["gfp0_D"] = gfp
    return {"accepted": bool(ok), "score_rows": {f["cut"]: len(f["score"]) for f in fl}}


def stage_final_validation(ctx, out):
    """The M10 chosen variant (V2 + chosen h [+ block D]) on validation, next to V2; saved for §D and M11."""
    cfg, H = ctx["cfg"], ctx["cfg"].H
    h, use_d = ctx["chosen_h"], ctx["exposure_accepted"]
    gfp = ctx["gfp0_D"] if use_d else ctx["gfp0"]
    feats = BASE + (EX.BLOCK_D if use_d else [])
    fit = RI.eligible(gfp, cfg.train[0], cfg.train[1], H, feats)
    val = RI.eligible(gfp, cfg.val[0], cfg.val[1], H, feats)
    base_val = ctx["val_rows"]
    if len(val) != len(base_val) or not val[["unit", "t"]].equals(base_val[["unit", "t"]]):
        raise data.DataQualityError(f"chosen variant validation keys differ from V2 ({len(val):,} vs {len(base_val):,})")
    p = fit_score(fit, val, val, feats, cfg.train[1], h)[0] if (use_d or h is not None) else ctx["val_V2"]
    vp = val[["unit", "t", "y"]].assign(V2=ctx["val_V2"], M10=p)
    vp.to_csv(out / "validation_predictions.csv", index=False)
    m7 = pd.read_csv(ctx["reports"] / "improve" / "validation_predictions.csv", parse_dates=["t"])
    sc = vp.merge(m7[["unit", "t", "recent_rate"]], on=["unit", "t"], validate="one_to_one")
    sc["group"] = [regions.group_of(u) for u in sc["unit"]]
    evaluate.reliability_plot(sc, ["M10", "V2", "recent_rate"], out / "reliability_validation_m10.png",
                              "Validation: M10 chosen variant vs V2 and recent rate")
    desc = f"V2{' + recency h=' + str(h) + ' d' if h is not None else ''}{' + block D' if use_d else ''}"
    print(f"[m10] chosen variant: {desc}; validation Brier V2 {RI.brier(ctx['val_V2'], val['y']):.5f} -> "
          f"{RI.brier(p, val['y']):.5f} on {len(val):,} rows")
    return {"chosen_variant": desc, "features": feats, "validation_rows": len(val),
            "validation_base_rate": float(val["y"].mean())}


def stage_stability(ctx, out):
    rep = ctx["reports"]
    off = pd.read_csv(rep / "official" / "val_predictions.csv")[["unit", "t", "y", "p_headline"]]
    imp = pd.read_csv(rep / "improve" / "validation_predictions.csv")[["unit", "t", "y", "V2", "recent_rate"]]
    m10 = pd.read_csv(out / "validation_predictions.csv")[["unit", "t", "y", "M10"]]
    scored = ST.join_predictions({"official": off, "improve": imp, "m10": m10}).rename(columns={"p_headline": "V0"})
    preds = ["V0", "V2", "M10", "recent_rate"]
    tab, reasons = ST.slice_tables(scored, preds, "recent_rate", ctx["cfg"].min_class_per_unit, ctx["cfg"].low_n_rows)
    tab.to_csv(out / "stability_validation.csv", index=False)
    print(f"[m10:D] validation stability on {len(scored):,} rows, {scored['t'].min()} -> {scored['t'].max()}, "
          f"base rate {scored['y'].mean():.4f}")
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        v = tab[(tab["group"] == "overall") & tab["baseline"].isin(["V0", "M10"])]
        print(v[["slice_kind", "slice", "baseline", "rows", "base_rate", "brier_skill_vs_recent",
                 "roc_auc_within_unit_mean"]].to_string(index=False))
    return {"nan_reasons": reasons, "rows": len(scored), "base_rate": float(scored["y"].mean()),
            "t_range": [str(scored["t"].min()), str(scored["t"].max())]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    for s in STAGES:
        ap.add_argument(f"--{s}", action="store_true")
    ap.add_argument("--posthoc-test", action="store_true")
    ap.add_argument("--data-path", default=str(ROOT / "data" / "official_data_en.csv"))
    ap.add_argument("--reports-root", default=str(ROOT / "reports"))
    args = ap.parse_args(argv)
    reports = Path(args.reports_root)
    out = reports / "m10"
    if args.posthoc_test:
        if not (out / APPROVAL).exists():
            raise PermissionError(f"§E is gated: {out / APPROVAL} must be written by the human first (plans/M10.md §E)")
        raise NotImplementedError("§E post-hoc test rows are off by human decision (chat 2026-10-18)")
    todo = [s for s in STAGES if getattr(args, s)] or STAGES
    cfg = config_mod.official()
    pr = json.loads((reports / "official" / "preregistration.json").read_text())
    if pr["code_fingerprint"] != run_all.code_fingerprint():
        raise data.DataQualityError("headline code changed since the pre-registration: M10 must not touch src/ or run_all.py")
    out.mkdir(parents=True, exist_ok=True)
    ctx = {"cfg": cfg, "reports": reports}
    prev = json.loads((out / "run_meta.json").read_text()) if (out / "run_meta.json").exists() else {}
    stage_runs = dict(prev.get("stage_runs", {}))
    prov = {"git_commit": run_all._git("rev-parse", "--verify", "HEAD"), "git_dirty": bool(run_all._git("status", "--porcelain")),
            "at": pd.Timestamp.now(tz="UTC").isoformat(), "invocation": todo}
    meta = {"plan": "plans/M10.md", "test_labels_read": False, "posthoc": False}
    if todo != ["stability"]:
        fr = run_all.build_frames(cfg, args.data_path)
        ctx["alerts"] = fr["alerts"]
        ctx["gfp0"], ctx["g0c"] = with_plus(fr["alerts"], fr["g"], fr["gf"], cfg)
        print(f"[m10] L0 frame (t + H <= test start) {ctx['gfp0'].shape}, t {ctx['gfp0']['t'].min()} -> "
              f"{ctx['gfp0']['t'].max()}")
        prov.update({"data_sha256": fr["meta"]["data_sha256"], "data_range": fr["meta"]["alert_range"],
                     "row_counts": fr["meta"]["row_counts"], "l0_frame_shape": list(ctx["gfp0"].shape),
                     "l0_frame_t_range": [str(ctx["gfp0"]["t"].min()), str(ctx["gfp0"]["t"].max())]})
    def run(stage, fn):
        stage_runs[stage] = {**prov, **fn(ctx, out)}
    if "recency" in todo:          # first, so A3's L0 rows reuse the h = inf fold predictions
        run("recency", stage_recency)
    if "labels" in todo:
        run("labels", stage_labels)
    if "exposure" in todo:
        if "val_rows" not in ctx:
            raise data.DataQualityError("--exposure needs --recency in the same run (validation rows)")
        run("exposure", stage_exposure)
        run("final_validation", stage_final_validation)
    if "stability" in todo:
        run("stability", stage_stability)
    meta.update({"stage_runs": stage_runs, "code_fingerprint_headline": pr["code_fingerprint"],
                 "python": platform.python_version(),
                 "packages": {p: version(p) for p in run_all.PACKAGES}, "fold_cuts": RI.FOLD_CUTS,
                 "half_lives": RC.HALF_LIVES, "block_d": EX.BLOCK_D, "base_features": BASE})
    (out / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"[run] wrote {out}")


if __name__ == "__main__":
    main()
