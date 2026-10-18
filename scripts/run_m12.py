"""M12 (plans/M12.md). EXPLORATORY, API data only (air-raid alerts, D-045).

    python scripts/run_m12.py --fit        # H = 6/12/24 "any" fits + validation of the 9-model registry (no test label)
    python scripts/run_m12.py --redshare   # the 7-day red-share rule check (onsets before the reserved week)
    python scripts/run_m12.py --replay     # M6c-1 test-week reconstruction for the Replay tab (no new score)
    python scripts/run_m12.py --export     # live models + blend seed (T_seed = test start) + parity sample, INACTIVE
    python scripts/run_m12.py --test       # the reserved week [2026-10-18, 10-25), scored ONCE; refuses before 10-25
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import evaluate, regions  # noqa: E402
from src.data import DataQualityError  # noqa: E402
from newregime import blend, data as nd, frames as F, horizons as HZ, pipeline as P, redshare as RS  # noqa: E402

LIVE = ROOT / "netlify" / "live" / "model" / "m12"
PARITY_RECORDS = ROOT / "netlify" / "live" / "test" / "m12_parity_records.json"


def stage_redshare(out):
    split = HZ.m12_split()
    pr = json.loads((out / "preregistration.json").read_text())
    alerts, cov, stats, R, _ = HZ.load_pinned(pd.Timestamp(pr["acquisition_cutoff"]))
    end = min(split.test_start, R)
    sc, counts, table, reasons = RS.evaluate_rule(alerts, cov, end)
    sc.to_csv(out / "redshare_rows.csv", index=False)
    table.to_csv(out / "redshare.csv", index=False)
    print(f"[m12 redshare] onsets before {end}: {counts}; share red {sc['y'].mean():.4f}")
    cols = ["predictor", "group", "rows", "positives", "base_rate", "brier", "brier_skill_vs_national",
            "roc_auc_pooled", "roc_auc_within_unit_mean", "pred_minus_obs", "low_n"]
    with pd.option_context("display.width", 220, "display.float_format", "{:.4f}".format):
        print(table[cols].to_string(index=False))
    return {"counts": counts, "nan_reasons": reasons, "end": str(end)}


def stage_replay(out, tmp):
    paths = HZ.pinned_m6c1_paths(tmp)
    ctx = P.prepare(P.first_split(), paths)
    arts, _ = HZ.m6c1_artifacts()
    rep = HZ.build_replay(ctx, arts)
    rep.to_csv(out / "replay_m6c1_any.csv", index=False)
    pub = pd.read_csv(HZ.M6C1 / "metrics.csv")
    checks = {}
    for H in (1, 3):
        r = rep[(rep["H"] == H) & (rep["status"] == "scored")].assign(group=lambda d: [regions.group_of(u) for u in d["unit"]])
        r = r.rename(columns={"p_model": "model", "p_blend": "blend", "p_baseline": "recent_rate"})
        t, _ = evaluate.metric_table(r, ["model", "blend", "recent_rate"], "recent_rate", 10)
        p = pub[(pub["type"] == "any") & (pub["H"] == H) & pub["predictor"].isin(["model", "blend", "recent_rate"])]
        m = t.merge(p, left_on=["baseline", "group"], right_on=["predictor", "group"], suffixes=("", "_pub"))
        if len(m) != len(p) or not len(m):
            raise DataQualityError(f"replay H={H}: published rows not matched")
        cols = ["rows", "positives", "base_rate", "brier", "brier_skill_vs_recent", "roc_auc_pooled",
                "roc_auc_within_unit_mean", "pr_auc", "pr_auc_over_base"]
        diff = max(float(np.nanmax(np.abs(m[c].astype(float) - m[f"{c}_pub"].astype(float)))) for c in cols)
        checks[f"any_h{H}"] = {"rows": int(len(r)), "max_abs_diff_vs_published": diff}
        if diff > 1e-12:
            raise DataQualityError(f"replay H={H} does not reproduce the published M6c-1 metrics (max diff {diff})")
    print(f"[m12 replay] {len(rep):,} rows; published metrics reproduced: {checks}")
    return {"checks": checks, "pinned_commit": "aa05529", "label": "retrospective reconstruction (D-027 latest versions)"}


def dump(art):
    return lgb.Booster(model_str=art["model_str"]).dump_model()


def stage_export(out, now):
    split = HZ.m12_split()
    pr = json.loads((out / "preregistration.json").read_text())
    A = pd.Timestamp(pr["acquisition_cutoff"])
    alerts, cov, stats, R, _ = HZ.load_pinned(A)
    T_seed = split.test_start
    if R < T_seed:
        raise DataQualityError(f"reconstruction {R} before T_seed {T_seed}")
    ctx = HZ.build_ctx(split, alerts, cov, stats, T_seed)
    arts, _ = HZ.m6c1_artifacts()
    a12, _ = HZ.m12_artifacts(out)
    arts.update(a12)
    LIVE.mkdir(parents=True, exist_ok=True)
    reg = []
    ms = lambda x: int(pd.Timestamp(x).value // 10**6)  # noqa: E731
    for typ, H in HZ.REGISTRY:
        art = arts[(typ, H)]
        key = f"{typ}_h{H}"
        text = json.dumps(dump(art), separators=(",", ":"))
        (LIVE / f"model_{key}.json").write_text(text)
        reg.append({"key": key, "type": typ, "H": H, "version": f"m12-{now.strftime('%Y%m%dT%H%MZ')}-{key}",
                    "source": art["source"], "features": F.feature_list(typ), "unit_codes": regions.units(),
                    "calibration": art["cal"], "p_unit": art["tables"]["p_unit"], "alpha": art["tables"]["alpha"],
                    "recent_window_hours": 14 * 24, "grid_start": ms(split.grid_start),
                    "trained_through": ms(split.train[1]), "early_stopping": [ms(split.val[0]), ms(split.val[1])],
                    "blend_cutoff": ms(split.val[1]), "available_at": ms(now), "alert_types": list(nd.ALERT_TYPES),
                    "sha256_model_json": HZ.hashlib.sha256(text.encode()).hexdigest()})
    earliest = split.test_end + pd.Timedelta(hours=24) + pd.Timedelta(hours=3)      # last H = 24 label + SETTLE
    (LIVE / "registry.json").write_text(json.dumps({"schema": 1, "label": HZ.LABEL, "earliest_activation": ms(earliest),
                                                    "models": reg}, indent=1))
    act = LIVE / "activation.json"
    if not act.exists():
        act.write_text(json.dumps({"active": False, "note": "switch only after the M12 test stage (plans/M12.md §E)"}, indent=1))
    seed = HZ.blend_seed(ctx, arts, T_seed, split.val[1])
    (LIVE / "blend_seed.json").write_text(json.dumps({"label": "reconstruction (D-027)", "items": seed}, separators=(",", ":")))
    parity = parity_sample(ctx, arts, seed, T_seed, split)
    (LIVE / "parity_sample.json").write_text(json.dumps(parity, separators=(",", ":")))
    # parity fixture = the alerts as known at T_seed (starts after T_seed dropped, ends after it hidden): no
    # reserved-week alert or label is committed (review F2/harness #2)
    cut = alerts[alerts["started_at"] <= T_seed]
    recs = [{"id": str(r.alert_id), "unit": r.unit, "alert_type": "air_raid", "level": r.alert_level,
             "start": ms(r.started_at), "end": None if pd.isna(r.finished_at) or r.finished_at > T_seed else ms(r.finished_at)}
            for r in cut.itertuples()]
    PARITY_RECORDS.write_text(json.dumps({"historyStart": ms(cov.history_start), "known_at": ms(T_seed),
                                          "holes": [[ms(a), ms(b)] for a, b in cov.holes], "records": recs},
                                         separators=(",", ":")))
    print(f"[m12 export] {len(reg)} models -> {LIVE} (INACTIVE: {json.loads(act.read_text())})")
    return {"T_seed": str(T_seed), "available_at": str(now), "models": [r["key"] for r in reg]}


def parity_sample(ctx, arts, seed, T_seed, split, n=200):
    """Per (type, H): >= n eligible rows (tau + H <= T_seed) with features, raw, calibrated, baseline; plus rows whose
    unit is under an alert of that type at tau (expected state alert_running); plus seed-only blend weights."""
    rng = np.random.default_rng(20261018)
    out = {}
    for typ, H in HZ.REGISTRY:
        cfg, art, feats = ctx.cfgs[H], arts[(typ, H)], F.feature_list(typ)
        fr = ctx.frames[(typ, H)]
        lo = split.grid_start + pd.Timedelta(days=8)
        el, _ = evaluate.eligibility(fr, lo, T_seed, cfg.H, feats)
        rows = fr[el].reset_index(drop=True)
        rows = rows.iloc[np.sort(rng.choice(len(rows), size=min(n, len(rows)), replace=False))].reset_index(drop=True)
        raw, cal = HZ.predict(art, rows, feats)
        from src import baselines as B
        pb, _, _ = B.predict_from_tables(art["tables"], fr, rows, nd.typed(ctx.alerts, typ), cfg)
        act = fr[(fr["active_at_t"] == 1) & (fr["t"] >= lo) & (fr["t"] + cfg.H <= T_seed)]
        act = act.iloc[np.sort(rng.choice(len(act), size=min(40, len(act)), replace=False))] if len(act) else act
        lab = pd.DataFrame(seed[f"{typ}_h{H}"]["labelled"])
        wt = []
        if len(lab):
            lab_df = pd.DataFrame({"unit": lab["unit"], "t": pd.to_datetime(lab["s"], unit="ms", utc=True), "y": lab["y"],
                                   "p_m": lab["p_model"], "p_b": lab["p_baseline"]})
            hours = pd.date_range(split.val[1] + pd.Timedelta(days=1), T_seed, freq="6h")
            w = blend.weights(hours, lab_df, ctx.onsets[typ], cfg.H, split.val[1])
            wt = [{"tau": int(t.value // 10**6), "w": float(a), "w_star": float(b), "n": int(c)}
                  for t, a, b, c in zip(w["t"], w["w"], w["w_star"].fillna(0.0), w["n"])]
        out[f"{typ}_h{H}"] = {
            "rows": [{"unit": u, "tau": int(t.value // 10**6), "x": [None if pd.isna(v) else float(v) for v in xv],
                      "raw": float(r), "p_model": float(c), "p_baseline": float(b)}
                     for u, t, xv, r, c, b in zip(rows["unit"], rows["t"], rows[feats].to_numpy(), raw, cal,
                                                  pb["recent_rate"].to_numpy())],
            "under_alert": [{"unit": u, "tau": int(t.value // 10**6)} for u, t in zip(act["unit"], act["t"])],
            "weights": wt}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for s in ("fit", "redshare", "replay", "export", "test"):
        ap.add_argument(f"--{s}", action="store_true")
    ap.add_argument("--out", type=Path, default=HZ.OUT)
    args = ap.parse_args(argv)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    meta_p = out / "run_meta.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {"label": HZ.LABEL, "stages": {}}
    prov = {"git_commit": P._git("rev-parse", "--verify", "HEAD"), "git_dirty": bool(P._git("status", "--porcelain")),
            "at": pd.Timestamp.now(tz="UTC").isoformat(), "code_fingerprint": HZ.code_fingerprint()}
    if args.test:
        HZ.score_test(out)
        meta["stages"]["test"] = prov
    if args.fit:
        _, arts, table = HZ.fit(out)
        meta["stages"]["fit"] = {**prov, "validation_rows": int(table[(table.group == "overall") & (table.predictor == "model")]["rows"].sum())}
    if args.redshare:
        meta["stages"]["redshare"] = {**prov, **stage_redshare(out)}
    if args.replay:
        with tempfile.TemporaryDirectory() as tmp:
            meta["stages"]["replay"] = {**prov, **stage_replay(out, tmp)}
    if args.export:
        meta["stages"]["export"] = {**prov, **stage_export(out, pd.Timestamp.now(tz="UTC").floor("min"))}
    meta_p.write_text(json.dumps(meta, indent=2, default=str))
    print(f"[run] wrote {out}")


if __name__ == "__main__":
    main()
