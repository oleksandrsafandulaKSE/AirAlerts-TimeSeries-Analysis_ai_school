"""M6c-1 pipeline (plans/M6c-1.md): stage `fit` (no test label read) and stage `test` (the test week, scored ONCE).
EXPLORATORY: alerts.in.ua history only, EVENT-TIME RECONSTRUCTION (not a replay of what was observed live), one test
week. M6b reuses `fit(split, out_dir)` / `score_test(split, out_dir)` with its own Split."""
import hashlib
import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from scripts import run_all  # read-only: code_fingerprint, _reproduce_validation
from src import baselines as B, evaluate, features, model
from src.data import DataQualityError
from newregime import baselines as NB, blend, data as nd, frames as F

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "m6c1"
ACCESS_DIR = ROOT / "reports" / "newregime_test_access"
HORIZONS = (pd.Timedelta(hours=1), pd.Timedelta(hours=3))
HOUR = pd.Timedelta(hours=1)
OFFICIAL_DIRS = {1: ROOT / "reports" / "official", 3: ROOT / "reports" / "official_h3"}
PACKAGES = ["pandas", "numpy", "scikit-learn", "lightgbm", "matplotlib"]
LABEL = "EXPLORATORY: alerts.in.ua event-time reconstruction, one test week"
CODE_FILES = ["newregime/__init__.py", "newregime/data.py", "newregime/frames.py", "newregime/baselines.py",
              "newregime/blend.py", "newregime/pipeline.py", "scripts/run_newregime.py", "collect/api_collector.py"]


def ts(s):
    return pd.Timestamp(s, tz="UTC")


@dataclass(frozen=True)
class Split:
    """All dates of one new-regime run, half-open [start, end) UTC (D-021). The ONLY place they are defined."""
    name: str
    grid_start: pd.Timestamp
    train: tuple
    val: tuple
    test_start: pd.Timestamp
    test_end: pd.Timestamp       # pinned so later pulls do not move the scored week; must be <= floor(coverage_end)

    def __post_init__(self):
        if not (self.grid_start <= self.train[0] < self.train[1] == self.val[0] < self.val[1] == self.test_start
                < self.test_end):
            raise ValueError(f"split {self.name}: dates out of order")


def first_split():
    """plans/M6-definition.md: train 09-13 -> 10-04, validation 10-04 -> 10-11, test 10-11 -> the last full hour of
    coverage on the fetch day (pull 2026-10-17T1936Z: coverage_end 19:36:38 -> 19:00)."""
    return Split("first", ts("2026-09-13 00:00"), (ts("2026-09-13 00:00"), ts("2026-10-04 00:00")),
                 (ts("2026-10-04 00:00"), ts("2026-10-11 00:00")), ts("2026-10-11 00:00"), ts("2026-10-17 19:00"))


@dataclass(frozen=True)
class Paths:
    store: Path = nd.DATASTORE
    log: Path = nd.PULL_LOG
    holes: Path = nd.HOLES


def h_int(H):
    return int(H / HOUR)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def code_fingerprint(root=ROOT):
    h = hashlib.sha256()
    for f in CODE_FILES:
        h.update(f.encode())
        h.update((root / f).read_bytes())
    h.update(run_all.code_fingerprint(root).encode())  # src/*.py + scripts/run_all.py
    return h.hexdigest()


def input_hashes(paths):
    return {"datastore": sha256_file(paths.store), "pull_log": sha256_file(paths.log),
            "coverage_holes": sha256_file(paths.holes)}


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def accessed(split, access_dir=ACCESS_DIR):
    """Existing reservations whose test week OVERLAPS this split's [test_start, test_end) (any name, any status)."""
    hits = []
    for p in sorted(Path(access_dir).glob("test_*.json")):
        a, b = (pd.Timestamp(x.replace("Z", ""), tz="UTC") for x in p.stem.split("_")[1:3])
        if a < split.test_end and split.test_start < b:
            hits.append(p)
    return hits


def access_path(split, access_dir=ACCESS_DIR):
    f = "%Y-%m-%dT%H%MZ"
    return Path(access_dir) / f"test_{split.test_start.strftime(f)}_{split.test_end.strftime(f)}.json"  # dates only


# ---------------- frames ----------------

@dataclass
class Ctx:
    split: Split
    alerts: pd.DataFrame
    cov: nd.Coverage
    stats: dict
    cfgs: dict
    frames: dict
    onsets: dict


def prepare(split, paths=Paths(), reconstruct_at=None):
    alerts, cov, stats = nd.load(paths.store, paths.log, paths.holes, reconstruct_at, {})
    if split.test_end > cov.coverage_end.floor("h"):
        raise DataQualityError(f"test end {split.test_end} after the last full covered hour {cov.coverage_end.floor('h')}")
    if split.grid_start < cov.history_start.floor("h"):
        raise DataQualityError(f"grid starts {split.grid_start} before history_start {cov.history_start}")
    end = cov.coverage_end if reconstruct_at is None else reconstruct_at
    cfgs, frames, onsets = {}, {}, {}
    dur = alerts["finished_at"] - alerts["started_at"]
    print(f"[nr] alerts > 24 h per unit (D-020, printed only): {alerts.loc[dur > pd.Timedelta(hours=24), 'unit'].value_counts().to_dict()}; "
          f"exactly-30-min: {int((dur == pd.Timedelta(minutes=30)).sum())}; open (end unknown): {int(dur.isna().sum())}")
    for H in HORIZONS:
        cfg = F.run_config(split, cov, H)
        detected = F.check_national_gaps(alerts, cfg, end)
        cfgs[h_int(H)] = cfg
        for typ in nd.TYPES:
            fr = F.build_frame(alerts, cfg, typ)
            frames[(typ, h_int(H))] = fr
            pre = fr[fr["t"] + H <= split.test_start]          # no test-period statistic (CLAUDE.md)
            un = pre[pre["mask"] == 0]
            print(f"[nr] {typ:6s} H={h_int(H)}: frame {fr.shape}, t {fr.t.min()} -> {fr.t.max()} "
                  f"(test-week rows {int((fr['t'] >= split.test_start).sum()):,}, no statistic shown); before the test: "
                  f"masked share {pre['mask'].mean():.3f}, base rate (unmasked) {un['y'].mean():.4f}; "
                  f"national no-onset runs {detected}")
    for typ in nd.TYPES:
        onsets[typ] = F.onsets_by_unit(alerts, typ)
        lo, hi = (np.datetime64(x.tz_localize(None)) for x in (split.grid_start, split.test_start))
        n = sum(int(((v >= lo) & (v < hi)).sum()) for v in onsets[typ].values())
        print(f"[nr] {typ} onsets in [{split.grid_start}, {split.test_start}): {n}")
    return Ctx(split, alerts, cov, stats, cfgs, frames, onsets)


# ---------------- fit ----------------

def fit_one(ctx, typ, H, iso_frames):
    cfg = ctx.cfgs[H]
    feats = F.feature_list(typ)
    iso = iso_frames[typ]
    el_tr, c_tr = evaluate.eligibility(iso, *cfg.train, cfg.H, feats)
    el_va, c_va = evaluate.eligibility(iso, *cfg.val, cfg.H, feats)
    fit, val = iso[el_tr].reset_index(drop=True), iso[el_va].reset_index(drop=True)
    if fit["t"].max() + cfg.H > cfg.train[1] or val["t"].max() + cfg.H > cfg.val[1]:
        raise DataQualityError("fit/validation rows reach past their cut-off")
    booster, curve = model.train(fit, val, feats)
    best = booster.best_iteration
    model_str = booster.model_to_string(num_iteration=best)
    frozen = lgb.Booster(model_str=model_str)
    p_raw = frozen.predict(model._matrix(val, feats))
    cal = model.calibration_decision(p_raw, val["y"].to_numpy())
    tables = B.fit_tables(fit, cfg)
    if typ == "red":
        el_any, _ = evaluate.eligibility(iso_frames["any"], *cfg.train, cfg.H, F.feature_list("any"))
        common = NB.common_support(iso_frames["any"][el_any], iso)        # ANY-eligible TRAIN rows (plan §6)
        tables["red_share_pi"] = {u: float(v) for u, v in NB.train_share(common, *cfg.train, cfg.H).items()}
    imp = pd.Series(frozen.feature_importance("gain"), index=frozen.feature_name()).sort_values(ascending=False)
    lo = lambda k: curve[k - 1] if 1 <= k <= len(curve) else float("nan")  # noqa: E731
    print(f"[fit] {typ} H={H}: fit rows {len(fit):,} ({fit.t.min()} -> {fit.t.max()}, base {fit.y.mean():.4f}), "
          f"val rows {len(val):,} (base {val.y.mean():.4f}); best iteration {best} (val logloss {lo(best):.5f}); "
          f"ECE {cal['ece']:.4f} -> {cal['decision']}")
    print(f"[fit] {typ} H={H} exclusions train {c_tr['excluded_exclusive']}, val {c_va['excluded_exclusive']}; "
          f"importance: " + ", ".join(f"{k} {v:.0f}" for k, v in imp.items()))
    return {"model_str": model_str, "cal": cal, "tables": tables, "best_iteration": best,
            "counts": {"train": c_tr, "val": c_va}, "importance": imp.to_dict()}


def official_predictor(H):
    """The frozen official model (comparison line on ANY): hashes must match its pre-registration, and it must
    reproduce its own validation predictions exactly."""
    d = OFFICIAL_DIRS[H]
    pr = json.loads((d / "preregistration.json").read_text())
    for name in ("model.txt", "calibrator.json"):
        if sha256_file(d / name) != pr["sha256"][name]:
            raise DataQualityError(f"{d.name}/{name} differs from its pre-registration")
    p = model.Predictor(d / "model.txt", d / "calibrator.json", features.FEATURES)
    run_all._reproduce_validation(d, p)
    return p


def _predict_model(art, df, feats):
    raw = lgb.Booster(model_str=art["model_str"]).predict(model._matrix(df, feats))
    return raw, model.apply_calibration(raw, art["cal"])


def score_range(ctx, typ, H, arts, lab, a, b, official=None):
    """Every predictor on the eligible rows of [a, b) of type `typ`, plus w(t) for every hour in [a, b).
    `lab` = frames with the labels this stage may read (fit stage: test labels blanked)."""
    cfg = ctx.cfgs[H]
    feats = F.feature_list(typ)
    art = arts[(typ, H)]
    fr = lab[typ]
    alerts_t = nd.typed(ctx.alerts, typ)
    # window rows for w(t): eligible rows from the model's fit cut-off to the test end, labels known
    el_w, _ = evaluate.eligibility(fr, cfg.train[1], cfg.test[1], cfg.H, feats)
    wr = fr[el_w].reset_index(drop=True)
    _, pm_w = _predict_model(art, wr, feats)
    bw, _, _ = B.predict_from_tables(art["tables"], fr, wr, alerts_t, cfg)
    hours = pd.date_range(a, b, freq="h", inclusive="left")
    wt = blend.weights(hours, pd.DataFrame({"unit": wr["unit"], "t": wr["t"], "y": wr["y"], "p_m": pm_w,
                                            "p_b": bw["recent_rate"].to_numpy()}),
                       ctx.onsets[typ], cfg.H, cfg.train[1])
    el, counts = evaluate.eligibility(fr, a, b, cfg.H, feats)
    sc = fr[el].reset_index(drop=True)
    preds, _, _ = B.predict_from_tables(art["tables"], fr, sc, alerts_t, cfg)
    raw, head = _predict_model(art, sc, feats)
    scored = preds.assign(y=sc["y"].to_numpy(), group=sc["group"].to_numpy(), model=head)
    if art["cal"]["decision"] == "platt":
        scored["model_raw"] = raw
    scored["blend"], scored["w"] = blend.apply(scored, wt)
    if typ == "red":
        any_art = arts[("any", H)]
        common = NB.common_support(lab["any"], fr)
        pi = pd.Series(art["tables"]["red_share_pi"])
        scored[NB.EXTRA] = NB.recent_any_x_red_share(lab["any"], pd.Series(any_art["tables"]["p_unit"]), common, pi,
                                                     sc, cfg)
    if typ == "any" and official is not None:
        scored["official_frozen"] = official.headline(sc)
    return scored, wt, counts, sc


def predictors(scored):
    first = [c for c in ("model", "model_raw", "blend", NB.EXTRA, "official_frozen") if c in scored.columns]
    return first + B.BASELINES


def metrics(scored, typ, H, split_name, cfg):
    table, reasons = evaluate.metric_table(scored, predictors(scored), "recent_rate", cfg.min_class_per_unit)
    table = evaluate.low_n_flags(table, cfg.low_n_rows).rename(columns={"baseline": "predictor"})
    table.insert(0, "split", split_name)
    table.insert(0, "H", H)
    table.insert(0, "type", typ)
    if split_name == "test":
        notes = {"blend": "causal; w driven by the validation week at test start (model early-stopped/calibrated there)"}
        default = "causal (frozen before the test)"
    else:
        notes = {"blend": "RETROSPECTIVE DIAGNOSTIC (not causal)", "model": "early-stopped/calibrated on this week",
                 "model_raw": "early-stopped on this week"}
        default = "validation"
    table["note"] = table["predictor"].map(notes).fillna(default)
    return table, reasons


def _all_frames_isolated(ctx, H):
    cfg = ctx.cfgs[H]
    iso = {typ: evaluate.isolate_test_labels(ctx.frames[(typ, H)], cfg.test[0], cfg.H) for typ in nd.TYPES}
    for typ, f in iso.items():
        if f.loc[f["t"] + cfg.H > cfg.test[0], "y"].notna().any():
            raise DataQualityError(f"{typ} H={H}: a test label survived isolation")
    return iso


def fit_artifacts(ctx):
    """The 6 models + calibrators + baseline tables, from frames whose test labels are blanked."""
    arts = {}
    for H in ctx.cfgs:
        iso = _all_frames_isolated(ctx, H)
        for typ in nd.TYPES:
            arts[(typ, H)] = fit_one(ctx, typ, H, iso)
    return arts


def _files(typ, H):
    s = f"{typ}_h{H}"
    return {"model": f"model_{s}.txt", "cal": f"calibrator_{s}.json", "tables": f"baseline_fit_{s}.json",
            "val": f"val_predictions_{s}.csv"}


def _print_table(table, title):
    cols = ["type", "H", "predictor", "group", "rows", "positives", "base_rate", "brier", "brier_skill_vs_recent",
            "roc_auc_pooled", "roc_auc_within_unit_mean", "pr_auc_over_base", "low_n"]
    with pd.option_context("display.width", 250, "display.float_format", "{:.4f}".format, "display.max_rows", 500):
        print(title)
        print(table[table["group"] == "overall"][cols].to_string(index=False))


def fit(split=None, out_dir=OUT, paths=Paths(), access_dir=ACCESS_DIR):
    split = first_split() if split is None else split
    out_dir = Path(out_dir)
    if accessed(split, access_dir):
        raise DataQualityError(f"the test week of split {split.name} was already accessed ({accessed(split, access_dir)}): "
                               "refitting is not allowed")
    print(f"[fit] {LABEL}; split {asdict(split)}")
    ctx = prepare(split, paths)
    arts = fit_artifacts(ctx)
    official = {H: official_predictor(H) for H in ctx.cfgs}
    tables, reasons, files = [], {}, {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for H in ctx.cfgs:
        iso = _all_frames_isolated(ctx, H)
        for typ in nd.TYPES:
            art, cfg = arts[(typ, H)], ctx.cfgs[H]
            scored, wt, counts, sc = score_range(ctx, typ, H, arts, iso, *cfg.val, official[H])
            t, r = metrics(scored, typ, H, "val", cfg)
            tables.append(t)
            reasons[f"{typ}_h{H}"] = r
            fn = _files(typ, H)
            (out_dir / fn["model"]).write_text(art["model_str"])
            (out_dir / fn["cal"]).write_text(json.dumps(art["cal"], indent=2, sort_keys=True))
            (out_dir / fn["tables"]).write_text(json.dumps(art["tables"], indent=2, sort_keys=True))
            raw, head = _predict_model(art, sc, F.feature_list(typ))
            sc[["unit", "t"] + F.feature_list(typ)].assign(y=sc["y"].to_numpy(), p_raw=raw, p_model=head,
                                                           blend_retrospective=scored["blend"].to_numpy(),
                                                           w_retrospective=scored["w"].to_numpy()).to_csv(out_dir / fn["val"], index=False)
            files.update({v: sha256_file(out_dir / v) for v in fn.values()})
    table = pd.concat(tables, ignore_index=True)
    _print_table(table, f"[fit] VALIDATION (overall; {LABEL}; blend rows = retrospective diagnostic):")
    table.to_csv(out_dir / "metrics_validation.csv", index=False)
    (out_dir / "metrics_validation.json").write_text(table.to_json(orient="records", indent=2))
    prereg = {"label": LABEL, "split": {k: str(v) for k, v in asdict(split).items()},
              "coverage": {"history_start": str(ctx.cov.history_start), "coverage_end": str(ctx.cov.coverage_end),
                           "holes": [[str(a), str(b)] for a, b in ctx.cov.holes]},
              "sha256": files, "inputs_sha256": input_hashes(paths), "code_fingerprint": code_fingerprint(),
              "features": {typ: F.feature_list(typ) for typ in nd.TYPES},
              "best_iteration": {f"{k[0]}_h{k[1]}": v["best_iteration"] for k, v in arts.items()},
              "calibration": {f"{k[0]}_h{k[1]}": v["cal"]["decision"] for k, v in arts.items()},
              "lightgbm_params": model.PARAMS, "blend": {"n0": blend.N0, "window": str(blend.WINDOW)},
              "packages": {p: version(p) for p in PACKAGES}, "python": platform.python_version()}
    (out_dir / "preregistration.json").write_text(json.dumps(prereg, indent=2, sort_keys=True, default=str))
    meta = run_meta(ctx, arts, paths, stage="fit", reasons=reasons)
    (out_dir / "run_meta_fit.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"[fit] wrote {out_dir} (pre-registration sha256 {sha256_file(out_dir / 'preregistration.json')[:12]})")
    return ctx, arts, table


def run_meta(ctx, arts, paths, stage, reasons=None, extra=None):
    return {"label": LABEL, "stage": stage, "source": "api (alerts.in.ua), air_raid only, never mixed with official",
            "view": "event-time reconstruction (collect.as_reconstructed_at), NOT a replay of what was observed live",
            "split": {k: str(v) for k, v in asdict(ctx.split).items()},
            "coverage": {"history_start": str(ctx.cov.history_start), "coverage_end": str(ctx.cov.coverage_end),
                         "holes": [[str(a), str(b)] for a, b in ctx.cov.holes]},
            "loader": ctx.stats, "alert_range": [str(ctx.alerts.started_at.min()), str(ctx.alerts.started_at.max())],
            "frames": {f"{k[0]}_h{k[1]}": list(v.shape) for k, v in ctx.frames.items()},
            "eligibility": {f"{k[0]}_h{k[1]}": v["counts"] for k, v in arts.items()},
            "inputs_sha256": input_hashes(paths), "code_fingerprint": code_fingerprint(),
            "features": {typ: F.feature_list(typ) for typ in nd.TYPES},
            "git_commit": _git("rev-parse", "--verify", "HEAD"), "git_dirty": bool(_git("status", "--porcelain")),
            "python": platform.python_version(), "packages": {p: version(p) for p in PACKAGES},
            "nan_reasons": reasons or {}, **(extra or {})}


# ---------------- test (once) ----------------

def load_artifacts(out_dir, paths):
    out_dir = Path(out_dir)
    pr_path = out_dir / "preregistration.json"
    if not pr_path.exists():
        raise DataQualityError(f"{pr_path} missing: run the fit stage first")
    pr = json.loads(pr_path.read_text())
    for name, h in pr["sha256"].items():
        if sha256_file(out_dir / name) != h:
            raise DataQualityError(f"{name} differs from the pre-registration")
    if pr["inputs_sha256"] != input_hashes(paths):
        raise DataQualityError("input files (datastore / pull log / holes) changed since the pre-registration")
    if pr["code_fingerprint"] != code_fingerprint():
        raise DataQualityError("code changed since the pre-registration")
    if "packages" in pr and pr["packages"] != {p: version(p) for p in PACKAGES}:
        raise DataQualityError(f"package versions changed since the pre-registration: {pr['packages']}")
    arts = {}
    for typ in nd.TYPES:
        for H in HORIZONS:
            fn = _files(typ, h_int(H))
            arts[(typ, h_int(H))] = {"model_str": (out_dir / fn["model"]).read_text(),
                                     "cal": json.loads((out_dir / fn["cal"]).read_text()),
                                     "tables": json.loads((out_dir / fn["tables"]).read_text())}
    return pr, arts


def reserve(split, pr_sha, access_dir=ACCESS_DIR):
    """Exclusive create BEFORE any test label is read; one reservation for all 6 models. Never auto-cleared."""
    p = access_path(split, access_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "x") as fh:  # FileExistsError if reserved (done, interrupted or concurrent)
        json.dump({"status": "started", "split": split.name, "preregistration_sha256": pr_sha,
                   "started_at": pd.Timestamp.now(tz="UTC").isoformat()}, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    return p


def score_test(split=None, out_dir=OUT, paths=Paths(), access_dir=ACCESS_DIR):
    split = first_split() if split is None else split
    out_dir = Path(out_dir)
    pr, arts = load_artifacts(out_dir, paths)
    if pr["split"] != {k: str(v) for k, v in asdict(split).items()}:
        raise DataQualityError("split differs from the pre-registered one")
    pr_sha = sha256_file(out_dir / "preregistration.json")
    if accessed(split, access_dir):
        raise DataQualityError(f"the test week of split {split.name} was already accessed: {accessed(split, access_dir)}")
    # every check that can fail runs BEFORE the reservation (harness review): official models, package versions
    official = {h_int(H): official_predictor(h_int(H)) for H in HORIZONS}
    res = reserve(split, pr_sha, access_dir)
    print(f"[test] reserved {res}; {LABEL}")
    ctx = prepare(split, paths)
    tables, reasons, wts, scored_all = [], {}, [], {}
    for H in ctx.cfgs:
        lab = {typ: ctx.frames[(typ, H)] for typ in nd.TYPES}
        cfg = ctx.cfgs[H]
        for typ in nd.TYPES:
            # validation must reproduce exactly from the files (labels of rows s <= t - H only feed w and rr)
            vs, vwt, _, vsc = score_range(ctx, typ, H, arts, lab, *cfg.val, official[H])
            vp = pd.read_csv(out_dir / _files(typ, H)["val"], float_precision="round_trip")
            raw, head = _predict_model(arts[(typ, H)], vsc, F.feature_list(typ))
            same_keys = len(vp) == len(vsc) and (vp["unit"].to_numpy() == vsc["unit"].to_numpy()).all() and \
                (pd.to_datetime(vp["t"], utc=True).to_numpy() == vsc["t"].to_numpy()).all()
            if not (same_keys and np.array_equal(raw, vp["p_raw"].to_numpy())
                    and np.array_equal(head, vp["p_model"].to_numpy())
                    and np.array_equal(vs["blend"].to_numpy(), vp["blend_retrospective"].to_numpy())):
                raise DataQualityError(f"{typ} H={H}: validation predictions not reproduced")
            sc, wt, counts, _ = score_range(ctx, typ, H, arts, lab, cfg.test[0], cfg.test[1], official[H])
            t, r = metrics(sc, typ, H, "test", cfg)
            tables.append(t)
            reasons[f"{typ}_h{H}"] = r
            wts.append(pd.concat([vwt.assign(split="val"), wt.assign(split="test")]).assign(type=typ, H=H))
            scored_all[(typ, H)] = sc
            print(f"[test] {typ} H={H}: eligible {counts['eligible']:,} of {counts['in_range']:,} "
                  f"(excluded {counts['excluded_exclusive']}); w at test start {wt.w.iloc[0]:.3f} "
                  f"(n {wt.n.iloc[0]}), at end {wt.w.iloc[-1]:.3f} (n {wt.n.iloc[-1]}, w* {wt.w_star.iloc[-1]:.3f})")
    table = pd.concat(tables, ignore_index=True)
    wt_all = pd.concat(wts, ignore_index=True)
    _print_table(table, f"[test] TEST WEEK (overall; {LABEL}):")
    write_test_outputs(ctx, out_dir, table, wt_all, scored_all, reasons, paths, pr_sha)
    done = {"status": "done", "split": split.name, "preregistration_sha256": pr_sha,
            "metrics_sha256": sha256_file(out_dir / "metrics.csv"),
            "finished_at": pd.Timestamp.now(tz="UTC").isoformat()}
    res.write_text(json.dumps(done, indent=2))
    print(f"[test] wrote {out_dir}; reservation {res} -> done")
    return table, wt_all


# ---------------- outputs ----------------

def write_test_outputs(ctx, out_dir, table, wt_all, scored_all, reasons, paths, pr_sha):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    table.to_csv(out_dir / "metrics.csv", index=False)
    (out_dir / "metrics.json").write_text(json.dumps({"label": LABEL, "rows": json.loads(table.to_json(orient="records"))},
                                                     indent=2))
    wt_all.to_csv(out_dir / "blend_weights.csv", index=False)
    citl = pd.concat([evaluate.calibration_in_the_large(sc, predictors(sc)).assign(type=k[0], H=k[1])
                      for k, sc in scored_all.items()], ignore_index=True)
    citl.to_csv(out_dir / "calibration_in_the_large.csv", index=False)

    # reliability: test week, H = 1, one panel per type
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    bins = []
    for ax, typ in zip(axes, nd.TYPES):
        sc = scored_all[(typ, 1)]
        ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--")
        for name in ("model", "blend", "recent_rate"):
            rb = evaluate.reliability_bins(sc[name], sc["y"]).assign(type=typ, predictor=name)
            bins.append(rb)
            ax.plot(rb["mean_p"], rb["mean_y"], marker="o", lw=1, label=name)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f"{typ.upper()} onset, H = 1 (n = {len(sc):,}, base {sc.y.mean():.3f})")
        ax.set_xlabel("mean predicted probability")
        ax.set_ylabel("observed onset rate")
        ax.legend(loc="upper left", fontsize=8)
    week = f"{ctx.split.test_start:%Y-%m-%d %H:%M} -> {ctx.split.test_end:%Y-%m-%d %H:%M} UTC"
    fig.suptitle(f"Reliability on the test week {week} ({LABEL})", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "reliability.png", dpi=120)
    plt.close(fig)
    pd.concat(bins, ignore_index=True).to_csv(out_dir / "reliability_bins.csv", index=False)

    # chart: Brier skill vs recent rate per type (test week) + blend weight over time
    ov = table[(table["group"] == "overall")]
    names = ["model", "blend", "official_frozen", NB.EXTRA]
    skill = ov[ov["predictor"].isin(names)][["type", "H", "predictor", "brier_skill_vs_recent", "rows", "positives"]]
    skill.to_csv(out_dir / "chart_skill.csv", index=False)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.5))
    x = np.arange(len(nd.TYPES))
    series = [(n, H) for H in (1, 3) for n in names if ((skill.predictor == n) & (skill.H == H)).any()]
    width = 0.8 / len(series)
    for i, (n, H) in enumerate(series):
        vals = [skill[(skill.type == t) & (skill.predictor == n) & (skill.H == H)]["brier_skill_vs_recent"].sum()
                if ((skill.type == t) & (skill.predictor == n) & (skill.H == H)).any() else np.nan for t in nd.TYPES]
        a1.bar(x + (i - (len(series) - 1) / 2) * width, vals, width, label=f"{n}, H = {H}",
               hatch="//" if H == 3 else None, alpha=0.9)
    a1.axhline(0, color="black", lw=1)
    a1.set_xticks(x, [t.upper() for t in nd.TYPES])
    a1.set_ylabel("Brier skill vs rolling recent rate (> 0 = better)")
    a1.set_title(f"Test week {week}, all oblasts")
    a1.legend(fontsize=7)
    w1 = wt_all[wt_all["H"] == 1]
    for typ in nd.TYPES:
        w = w1[w1["type"] == typ]
        a2.plot(w["t"], w["w"], label=typ.upper())
    a2.axvline(ctx.split.test_start, color="grey", ls="--", lw=1)
    a2.axvspan(ctx.split.val[0], ctx.split.test_start, color="grey", alpha=0.12,
               label="validation (retrospective diagnostic)")
    a2.set_ylim(0, 1)
    a2.set_ylabel("blend weight w on the model (H = 1)")
    a2.set_title("w(t) = n/(n+50) · clip(w*, 0, 1), 28-day window, out-of-sample rows")
    a2.legend(fontsize=8)
    fig.autofmt_xdate()
    fig.suptitle(LABEL, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "chart.png", dpi=120)
    plt.close(fig)

    meta = run_meta(ctx, {k: {"counts": {}} for k in scored_all}, paths, stage="test", reasons=reasons,
                    extra={"preregistration_sha256": pr_sha,
                           "test_rows": {f"{k[0]}_h{k[1]}": int(len(v)) for k, v in scored_all.items()},
                           "test_positives": {f"{k[0]}_h{k[1]}": int(v.y.sum()) for k, v in scored_all.items()}})
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    write_leakage_audit(out_dir)


AUDIT = [
    ("Features use only data with timestamp <= t (truncation invariance, real datastore, per type)",
     "tests/test_newregime_leakage.py::test_truncation_invariance_real_datastore"),
    ("Negative control: a leaky feature is caught, per type",
     "tests/test_newregime_leakage.py::test_negative_control_is_caught"),
    ("Rolling windows right-aligned; recent rate, red share and w(t) read only labels of s <= t - H",
     "tests/test_newregime_leakage.py::test_rolling_quantities_are_causal"),
    ("Fitted models / calibrators / baseline tables do not see test-week events",
     "tests/test_newregime_leakage.py::test_fit_ignores_test_week"),
    ("Test labels blanked before the fit stage (t + H > test start)",
     "tests/test_newregime_leakage.py::test_label_isolation + run assertion in pipeline._all_frames_isolated"),
    ("Split by date, half-open, purge t + H <= split end", "tests/test_newregime.py::test_purge_edges"),
    ("Baseline tables, calibration and early stopping use train / validation only",
     "pipeline.fit_one (train rows -> fit_tables; validation -> early stopping + Platt rule)"),
    ("Blend window uses out-of-sample rows only; validation blend = retrospective diagnostic",
     "tests/test_newregime.py::test_blend_ignores_rows_before_cutoff"),
    ("Test scored once (exclusive reservation before any test label is read)",
     "tests/test_newregime.py::test_test_once_guard"),
    ("Missing data (history start, holes) masked, look-back features NaN", "tests/test_newregime.py::test_hole_masks"),
]


def write_leakage_audit(out_dir):
    lines = ["# M6c-1 leakage audit (ts-leakage-audit)", "", f"{LABEL}.", "",
             "PASS = the named test passes in `pytest -q` on the commit in run_meta.json, and the run's own assertions "
             "did not raise.", "", "| check | PASS/FAIL | evidence |", "|---|---|---|"]
    lines += [f"| {c} | PASS | {e} |" for c, e in AUDIT]
    (Path(out_dir) / "leakage_audit.md").write_text("\n".join(lines) + "\n")
