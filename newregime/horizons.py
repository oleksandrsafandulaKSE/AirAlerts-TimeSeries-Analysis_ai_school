"""M12 (plans/M12.md): "any" onset models for H = 6/12/24 h with the M6c-1 recipe, the 9-model registry for the live map,
input pinning by acquisition cut-off, the date-gated test week, the blend seed and the M6c-1 test-week replay.

`newregime/pipeline.py` (M6c-1, fingerprinted) is imported READ-ONLY and never edited; its HORIZONS stay (1 h, 3 h).
EXPLORATORY: alerts.in.ua history only, event-time reconstruction (D-027 latest versions)."""
import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace

import lightgbm as lgb
import numpy as np
import pandas as pd

from collect import api_collector as ac
from src import baselines as B, config as config_mod, data, evaluate, grid, model
from src.data import DataQualityError
from newregime import blend, data as nd, frames as F, pipeline as P

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "m12"
M6C1 = ROOT / "reports" / "m6c1"
HOUR = pd.Timedelta(hours=1)
NEW_H = (6, 12, 24)                                  # fitted here ("any" only)
REGISTRY = [("any", 1), ("any", 3), ("any", 6), ("any", 12), ("any", 24),
            ("yellow", 1), ("yellow", 3), ("red", 1), ("red", 3)]
LABEL = "EXPLORATORY: alerts.in.ua event-time reconstruction (D-027), new-regime M12"
CODE_FILES = ["newregime/horizons.py", "newregime/redshare.py", "scripts/run_m12.py"]


def ts(s):
    return pd.Timestamp(s, tz="UTC")


@dataclass(frozen=True)
class M12Split:
    """All M12 dates, half-open [start, end) UTC. Train / validation = M6c-1's; [val_end, gap_end) is never a fit or
    early-stopping row (the M6c-1 test week + one day); the test week is reserved and scored once."""
    name: str
    grid_start: pd.Timestamp
    train: tuple
    val: tuple
    gap_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp

    def __post_init__(self):
        if not (self.grid_start <= self.train[0] < self.train[1] == self.val[0] < self.val[1] <= self.gap_end
                == self.test_start < self.test_end):
            raise ValueError(f"split {self.name}: dates out of order")


def m12_split():
    f = P.first_split()
    return M12Split("m12", f.grid_start, f.train, f.val, ts("2026-10-18 00:00"), ts("2026-10-18 00:00"),
                    ts("2026-10-25 00:00"))


def view(split, test_end):
    """The attribute set F.run_config reads; test_end may be cut (fit stage: = test start, so no test row exists)."""
    return SimpleNamespace(name=split.name, grid_start=split.grid_start, train=split.train, val=split.val,
                           test_start=split.test_start, test_end=test_end)


def h_td(H):
    return pd.Timedelta(hours=H)


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def code_fingerprint(root=ROOT):
    h = hashlib.sha256()
    for f in CODE_FILES:
        h.update(f.encode())
        h.update((Path(root) / f).read_bytes())
    h.update(P.code_fingerprint(root).encode())      # M6c-1 code (incl. src/ and run_all.py)
    return h.hexdigest()


# ---------------------------------------------------------------- pinning (plan §A)
VERSION_KEY = ("id", "updated_at", "fetched_at", "pull_id")


def _canon(rows, keys):
    """sha256 of rows sorted by `keys`, each row as sorted-key JSON (types as decoded)."""
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda r: tuple(str(r.get(k)) for k in keys)):
        h.update(json.dumps(r, sort_keys=True, default=str).encode())
        h.update(b"\n")
    return h.hexdigest()


def pinned_inputs(A, paths=P.Paths()):
    """Datastore / pull-log / holes rows with fetched_at (holes: hole_from) <= A — the acquisition cut-off."""
    def le(s):
        return nd._ts(s) <= A
    log = [r for r in ac.read_log(paths.log) if le(r["fetched_at"])]
    holes = [h for h in nd.read_holes(paths.holes) if le(h["hole_from"])]
    rows = [r for r in ac.read_datastore(paths.store) if le(r["fetched_at"])]
    return rows, log, holes


def prefix_hashes(rows, log, holes):
    return {"datastore": _canon(rows, VERSION_KEY), "pull_log": _canon(log, ("fetched_at", "unit", "pull_id")),
            "coverage_holes": _canon(holes, ("hole_from", "unit", "pull_id"))}


def last_pull(paths=P.Paths()):
    return max(nd._ts(r["fetched_at"]) for r in ac.read_log(paths.log))


def load_pinned(A, paths=P.Paths(), stats=None):
    """Filter by A FIRST (as_reconstructed_at keeps the latest version per id and does not cut by fetched_at,
    collect/api_collector.py:580-583), then the same coverage + reconstruction as nd.load at R = floor_hour of the
    FILTERED coverage_end (so newregime/data.py:98's guard holds). -> alerts, cov, stats, R, hashes."""
    stats = {} if stats is None else stats
    rows, log, holes = pinned_inputs(A, paths)
    cov = nd.coverage(log, holes)
    R = cov.coverage_end.floor("h")
    rec = ac.as_reconstructed_at(rows, R.to_pydatetime())
    stats.update(datastore_rows=len(rows), distinct_ids=len({r["id"] for r in rows}), reconstructed_records=len(rec),
                 acquisition_cutoff=str(A), reconstruct_at=str(R))
    cfg = SimpleNamespace(api_alert_types=nd.ALERT_TYPES, history_start=cov.history_start, grid_end=R)
    alerts = data.api_alerts(ac.to_api_records(rec), None, cfg, stats)
    if set(alerts["source"]) != {"api"}:
        raise DataQualityError("non-API rows in an API-only run (never mix sources)")
    print(f"[m12] pinned inputs at A = {A}: {len(rows):,} datastore rows, {len(log):,} pulls, {len(holes)} holes -> "
          f"reconstruction at R = {R}: {len(alerts):,} air-raid alerts, coverage {cov.history_start} -> {cov.coverage_end}")
    return alerts, cov, stats, R, prefix_hashes(rows, log, holes)


# ---------------------------------------------------------------- frames
def build_ctx(split, alerts, cov, stats, end, items=REGISTRY):
    """Frames for every (type, H) in `items` with test_end = `end` (fit stage: the test start)."""
    v = view(split, end)
    cfgs, frames = {}, {}
    for typ, H in items:
        if H not in cfgs:
            cfgs[H] = F.run_config(v, cov, h_td(H))
            F.check_national_gaps(alerts, cfgs[H], cov.coverage_end.floor("h"))   # = R (load_pinned)
        frames[(typ, H)] = F.build_frame(alerts, cfgs[H], typ)
        fr = frames[(typ, H)]
        un = fr[(fr["mask"] == 0) & fr["y"].notna() & (fr["t"] + h_td(H) <= split.test_start)]
        print(f"[m12] {typ:6s} H={H:2d}: frame {fr.shape}, t {fr.t.min()} -> {fr.t.max()}, unmasked labelled rows "
              f"before the test {len(un):,}, base rate {un['y'].mean():.4f}")
    onsets = {typ: F.onsets_by_unit(alerts, typ) for typ in nd.TYPES}
    return P.Ctx(v, alerts, cov, stats, cfgs, frames, onsets)


def isolated(ctx, H, types):
    cfg = ctx.cfgs[H]
    out = {}
    for typ in types:
        f = evaluate.isolate_test_labels(ctx.frames[(typ, H)], cfg.test[0], cfg.H)
        if f.loc[f["t"] + cfg.H > cfg.test[0], "y"].notna().any():
            raise DataQualityError(f"{typ} H={H}: a test label survived isolation")
        out[typ] = f
    return out


def types_at(H):
    return [t for t, h in REGISTRY if h == H]


# ---------------------------------------------------------------- artefacts
def m6c1_artifacts(m6c1_dir=M6C1):
    """The 6 M6c-1 artefact sets, sha256-checked against reports/m6c1/preregistration.json (no refit)."""
    pr = json.loads((Path(m6c1_dir) / "preregistration.json").read_text())
    arts = {}
    for typ, H in REGISTRY:
        if H not in (1, 3):
            continue
        fn = P._files(typ, H)
        for k in ("model", "cal", "tables"):
            if sha256_file(Path(m6c1_dir) / fn[k]) != pr["sha256"][fn[k]]:
                raise DataQualityError(f"reports/m6c1/{fn[k]} differs from the M6c-1 pre-registration")
        arts[(typ, H)] = {"model_str": (Path(m6c1_dir) / fn["model"]).read_text(),
                          "cal": json.loads((Path(m6c1_dir) / fn["cal"]).read_text()),
                          "tables": json.loads((Path(m6c1_dir) / fn["tables"]).read_text()), "source": "m6c1"}
    return arts, pr


def m12_artifacts(out_dir=OUT, check=True):
    out_dir = Path(out_dir)
    pr = json.loads((out_dir / "preregistration.json").read_text())
    arts = {}
    for H in NEW_H:
        fn = P._files("any", H)
        for k in ("model", "cal", "tables"):
            if check and sha256_file(out_dir / fn[k]) != pr["sha256"][fn[k]]:
                raise DataQualityError(f"{fn[k]} differs from the M12 pre-registration")
        arts[("any", H)] = {"model_str": (out_dir / fn["model"]).read_text(),
                            "cal": json.loads((out_dir / fn["cal"]).read_text()),
                            "tables": json.loads((out_dir / fn["tables"]).read_text()), "source": "m12"}
    return arts, pr


def predict(art, df, feats):
    return P._predict_model(art, df, feats)


# ---------------------------------------------------------------- fit stage (no test label read)
def fit(out_dir=OUT, paths=P.Paths(), access_dir=P.ACCESS_DIR, m6c1_dir=M6C1):
    split = m12_split()
    sp = view(split, split.test_end)
    if P.accessed(sp, access_dir):
        raise DataQualityError(f"the M12 test week was already accessed ({P.accessed(sp, access_dir)}): refit refused")
    A = last_pull(paths)
    alerts, cov, stats, R, hashes = load_pinned(A, paths)
    if R < split.val[1]:
        raise DataQualityError(f"reconstruction time {R} before the validation end {split.val[1]}")
    end = min(split.test_start, R)
    ctx = build_ctx(split, alerts, cov, stats, end)
    arts, m6pr = m6c1_artifacts(m6c1_dir)
    for H in NEW_H:
        iso = isolated(ctx, H, ["any"])
        arts[("any", H)] = {**P.fit_one(ctx, "any", H, iso), "source": "m12"}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for H in NEW_H:
        fn, art = P._files("any", H), arts[("any", H)]
        (out_dir / fn["model"]).write_text(art["model_str"])
        (out_dir / fn["cal"]).write_text(json.dumps(art["cal"], indent=2, sort_keys=True))
        (out_dir / fn["tables"]).write_text(json.dumps(art["tables"], indent=2, sort_keys=True))
    tables, reasons, scored_all = [], {}, {}
    official = {H: P.official_predictor(H) for H in (1, 3)}
    for typ, H in REGISTRY:
        iso = isolated(ctx, H, types_at(H))
        cfg = ctx.cfgs[H]
        scored, wt, counts, sc = P.score_range(ctx, typ, H, arts, iso, *cfg.val, official.get(H))
        t, r = P.metrics(scored, typ, H, "val", cfg)
        t["model_source"] = arts[(typ, H)]["source"]
        tables.append(t)
        reasons[f"{typ}_h{H}"] = {"nan_reasons": r, "exclusions": counts}
        scored_all[(typ, H)] = scored
        if (typ, H) in [("any", h) for h in NEW_H]:
            fn = P._files(typ, H)
            raw, head = predict(arts[(typ, H)], sc, F.feature_list(typ))
            sc[["unit", "t"] + F.feature_list(typ)].assign(y=sc["y"].to_numpy(), p_raw=raw, p_model=head,
                                                           blend_retrospective=scored["blend"].to_numpy(),
                                                           w_retrospective=scored["w"].to_numpy()).to_csv(out_dir / fn["val"], index=False)
    for H in NEW_H:
        for k, v in P._files("any", H).items():
            files[v] = sha256_file(out_dir / v)
    table = pd.concat(tables, ignore_index=True)
    P._print_table(table, f"[m12 fit] VALIDATION (overall; {LABEL}; blend rows = retrospective diagnostic):")
    table.to_csv(out_dir / "metrics_validation.csv", index=False)
    reliability_panels(scored_all, out_dir / "reliability_validation.png", "Validation (M12 registry; exploratory)")
    prereg = {"label": LABEL, "split": {k: str(v) for k, v in asdict(split).items()},
              "acquisition_cutoff": str(A), "reconstruct_at": str(R), "inputs_prefix_sha256": hashes,
              "coverage": {"history_start": str(cov.history_start), "coverage_end": str(cov.coverage_end),
                           "holes": [[str(a), str(b)] for a, b in cov.holes]},
              "sha256": files, "m6c1_preregistration_sha256": sha256_file(Path(m6c1_dir) / "preregistration.json"),
              "m6c1_code_fingerprint_preregistered": m6pr["code_fingerprint"],
              "m6c1_code_fingerprint_current": P.code_fingerprint(), "code_fingerprint": code_fingerprint(),
              "best_iteration": {f"any_h{H}": arts[("any", H)]["best_iteration"] for H in NEW_H},
              "calibration": {f"any_h{H}": arts[("any", H)]["cal"]["decision"] for H in NEW_H},
              "lightgbm_params": model.PARAMS, "blend": {"n0": blend.N0, "window": str(blend.WINDOW),
                                                         "operational_cutoff": str(split.val[1])},
              "test_scope": [f"any_h{H}" for H in NEW_H],
              "packages": {p: version(p) for p in P.PACKAGES}, "python": platform.python_version()}
    (out_dir / "preregistration.json").write_text(json.dumps(prereg, indent=2, sort_keys=True, default=str))
    meta = {"label": LABEL, "stage": "fit", "split": prereg["split"], "acquisition_cutoff": str(A),
            "reconstruct_at": str(R), "stats": stats, "frames": {f"{k[0]}_h{k[1]}": list(v.shape) for k, v in ctx.frames.items()},
            "exclusions_and_reasons": reasons, "git_commit": P._git("rev-parse", "--verify", "HEAD"),
            "git_dirty": bool(P._git("status", "--porcelain")), "features": {t: F.feature_list(t) for t in nd.TYPES}}
    (out_dir / "run_meta_fit.json").write_text(json.dumps(meta, indent=2, default=str))
    print(f"[m12 fit] wrote {out_dir}")
    return ctx, arts, table


def reliability_panels(scored_all, path, title, items=REGISTRY):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(items)
    fig, axes = plt.subplots((n + 2) // 3, 3, figsize=(11, 3.7 * ((n + 2) // 3)), squeeze=False)
    for ax, (typ, H) in zip(axes.flat, items):
        sc = scored_all[(typ, H)]
        ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--")
        for col in ("model", "blend", "recent_rate"):
            rb = evaluate.reliability_bins(sc[col], sc["y"])
            ax.plot(rb["mean_p"], rb["mean_y"], marker="o", lw=1, label=col)
        ax.set_title(f"{typ} H={H} (n={len(sc):,}, base {sc.y.mean():.3f})", fontsize=9)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    axes.flat[0].legend(fontsize=7)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------- blend window with an explicit cut-off (plan §A/§B)
def window_rows(ctx, typ, H, art, lab, a, b):
    """Eligible rows in [a, b) with labels known, p_model and the D-025 recent-rate baseline (no blend)."""
    cfg = ctx.cfgs[H]
    feats = F.feature_list(typ)
    fr = lab[typ]
    el, counts = evaluate.eligibility(fr, a, b, cfg.H, feats)
    rows = fr[el].reset_index(drop=True)
    _, pm = predict(art, rows, feats)
    pb, _, _ = B.predict_from_tables(art["tables"], fr, rows, nd.typed(ctx.alerts, typ), cfg)
    return rows.assign(p_m=pm, p_b=pb["recent_rate"].to_numpy()), counts


def operational_weights(ctx, typ, H, art, lab, hours, cutoff, end):
    """w(t) with the OPERATIONAL cut-off (the validation end): validation rows never enter the weight."""
    wr, _ = window_rows(ctx, typ, H, art, lab, cutoff, end)
    return blend.weights(hours, wr[["unit", "t", "y", "p_m", "p_b"]], ctx.onsets[typ], h_td(H), cutoff)


# ---------------------------------------------------------------- test stage (date-gated, scored once)
def test_ready(split, cov):
    """Every check that can fail BEFORE the reservation."""
    if cov.coverage_end.floor("h") < split.test_end:
        raise DataQualityError(f"test week not complete: coverage ends {cov.coverage_end} < {split.test_end} "
                               "(run after the collector has pulled through 2026-10-25)")


def score_test(out_dir=OUT, paths=P.Paths(), access_dir=P.ACCESS_DIR, m6c1_dir=M6C1):
    """The reserved week, scored ONCE for "any" H = 6/12/24 (plan §A). Every check that can fail runs BEFORE the
    reservation. Frames (and so test-week labels) are BUILT before it, as in M6c-1's prepare, but no test-week value is
    read, printed or written before the reservation exists."""
    split = m12_split()
    out_dir = Path(out_dir)
    pr_path = out_dir / "preregistration.json"
    if not pr_path.exists():
        raise DataQualityError(f"{pr_path} missing: run the fit stage first")
    pr = json.loads(pr_path.read_text())
    if pr["split"] != {k: str(v) for k, v in asdict(split).items()}:
        raise DataQualityError("split differs from the pre-registered one")
    A_fit = pd.Timestamp(pr["acquisition_cutoff"])
    if prefix_hashes(*pinned_inputs(A_fit, paths)) != pr["inputs_prefix_sha256"]:
        raise DataQualityError("a pinned input row (fetched_at <= A_fit) was edited or deleted since the fit")
    if pr["code_fingerprint"] != code_fingerprint():
        raise DataQualityError("M12 code changed since the pre-registration")
    if pr["packages"] != {p: version(p) for p in P.PACKAGES}:
        raise DataQualityError("package versions changed since the pre-registration")
    arts, _ = m12_artifacts(out_dir)
    alerts, cov, stats, R, _ = load_pinned(last_pull(paths), paths)      # later revisions consumed (D-027), recorded
    test_ready(split, cov)
    sp = view(split, split.test_end)
    if P.accessed(sp, access_dir):
        raise DataQualityError(f"overlapping test reservation exists: {P.accessed(sp, access_dir)}")
    ctx = build_ctx(split, alerts, cov, stats, split.test_end, items=[("any", H) for H in NEW_H])
    for H in NEW_H:                                  # validation predictions must reproduce from the files
        cfg, fr = ctx.cfgs[H], ctx.frames[("any", H)]
        el, _ = evaluate.eligibility(fr, *cfg.val, cfg.H, F.feature_list("any"))
        vsc = fr[el].reset_index(drop=True)
        vp = pd.read_csv(out_dir / P._files("any", H)["val"], float_precision="round_trip")
        raw, head = predict(arts[("any", H)], vsc, F.feature_list("any"))
        same = len(vp) == len(vsc) and (vp["unit"].to_numpy() == vsc["unit"].to_numpy()).all() and \
            (pd.to_datetime(vp["t"], utc=True).to_numpy() == vsc["t"].to_numpy()).all()
        if not (same and np.array_equal(raw, vp["p_raw"].to_numpy()) and np.array_equal(head, vp["p_model"].to_numpy())):
            raise DataQualityError(f"any H={H}: validation predictions not reproduced (inputs or code changed)")
    res = P.reserve(sp, sha256_file(pr_path), access_dir)                 # the first test-week value is read below
    if res is None or not Path(res).exists():
        raise DataQualityError("no reservation file: refusing to score")
    print(f"[m12 test] reserved {res}; {LABEL}")
    tables, scored_all, counts_all, citl = [], {}, {}, []
    for H in NEW_H:
        cfg, lab = ctx.cfgs[H], {"any": ctx.frames[("any", H)]}
        el, counts = evaluate.eligibility(lab["any"], split.test_start, split.test_end, cfg.H, F.feature_list("any"))
        sc = lab["any"][el].reset_index(drop=True)
        preds, _, _ = B.predict_from_tables(arts[("any", H)]["tables"], lab["any"], sc, alerts, cfg)
        _, head = predict(arts[("any", H)], sc, F.feature_list("any"))
        scored = preds.assign(y=sc["y"].to_numpy(), group=sc["group"].to_numpy(), model=head)
        hours = pd.date_range(split.test_start, split.test_end, freq="h", inclusive="left")
        wt = operational_weights(ctx, "any", H, arts[("any", H)], lab, hours, split.val[1], split.test_end)
        scored["blend"], scored["w"] = blend.apply(scored, wt)
        t, _ = P.metrics(scored, "any", H, "test", cfg)
        tables.append(t)
        scored_all[("any", H)] = scored
        counts_all[f"any_h{H}"] = counts
        citl.append(evaluate.calibration_in_the_large(scored, ["model", "blend", "recent_rate"]).assign(H=H))
        scored.to_csv(out_dir / f"test_predictions_any_h{H}.csv", index=False)
        print(f"[m12 test] any H={H}: eligible {counts['eligible']:,} of {counts['in_range']:,} "
              f"(excluded {counts['excluded_exclusive']})")
    table = pd.concat(tables, ignore_index=True)
    table.to_csv(out_dir / "metrics.csv", index=False)
    pd.concat(citl, ignore_index=True).to_csv(out_dir / "calibration_in_the_large.csv", index=False)
    reliability_panels(scored_all, out_dir / "reliability.png", "Test week (scored once; exploratory)",
                       items=[("any", H) for H in NEW_H])
    P._print_table(table, f"[m12 test] TEST WEEK {split.test_start} -> {split.test_end} (scored once; {LABEL}):")
    (out_dir / "run_meta_test.json").write_text(json.dumps(
        {"label": LABEL, "stage": "test", "reconstruct_at": str(R), "stats": stats, "exclusions": counts_all,
         "git_commit": P._git("rev-parse", "--verify", "HEAD"), "git_dirty": bool(P._git("status", "--porcelain"))},
        indent=2, default=str))
    Path(res).write_text(json.dumps({**json.loads(Path(res).read_text()), "status": "done",
                                     "metrics_sha256": sha256_file(out_dir / "metrics.csv"),
                                     "finished_at": pd.Timestamp.now(tz="UTC").isoformat(), "reconstruct_at": str(R)},
                                    indent=2))
    return table


# ---------------------------------------------------------------- blend seed (plan §B)
def blend_seed(ctx, arts, T_seed, val_end):
    """Per (type, H): eligible rows s in [val_end, T_seed] with p_model, p_baseline; labelled (y + onset ids) when
    s + H <= T_seed, else `pending`. No label with s + H > T_seed is read (those rows carry no y)."""
    out = {}
    for typ, H in REGISTRY:
        cfg, art, feats = ctx.cfgs[H], arts[(typ, H)], F.feature_list(typ)
        fr = ctx.frames[(typ, H)]
        lab_rows, _ = window_rows(ctx, typ, H, art, {typ: fr}, val_end, T_seed)
        if (lab_rows["t"] + h_td(H) > T_seed).any():
            raise DataQualityError("a labelled seed row reaches past T_seed")
        on = ctx.onsets[typ]
        labelled = []
        for r in lab_rows.itertuples():
            s = np.datetime64(r.t.tz_convert("UTC").tz_localize(None), "ns")
            o = on.get(r.unit, np.array([], "datetime64[ns]"))
            ev = o[(o > s) & (o <= s + np.timedelta64(h_td(H)))]
            if bool(r.y) != (len(ev) > 0):
                raise DataQualityError(f"seed row {r.unit} {r.t}: label and onsets disagree")
            labelled.append({"unit": r.unit, "s": int(r.t.value // 10**6), "p_model": float(r.p_m),
                             "p_baseline": float(r.p_b), "y": int(r.y),
                             "events": [f"{r.unit}|{int(pd.Timestamp(e).tz_localize('UTC').value // 10**6)}" for e in ev]})
        pend = pending_rows(ctx, typ, H, art, T_seed)
        out[f"{typ}_h{H}"] = {"labelled": labelled, "pending": pend, "T_seed": int(T_seed.value // 10**6),
                              "cutoff": int(val_end.value // 10**6)}
        print(f"[m12 seed] {typ} H={H}: {len(labelled):,} labelled rows, {len(pend):,} pending")
    return out


def pending_rows(ctx, typ, H, art, T_seed):
    """Rows s in (T_seed - H, T_seed] (hourly): predictions from inputs <= s only; label pending (never read here)."""
    cfg, feats = ctx.cfgs[H], F.feature_list(typ)
    times = pd.date_range(T_seed - h_td(H) + HOUR, T_seed, freq="h")
    zones = config_mod.uncertainty_zones(cfg)
    f = F.typed_features(ctx.alerts, times, zones, typ, cfg.standing_cap)
    ivs = grid.unit_intervals(nd.typed(ctx.alerts, typ), cfg.standing_cap)
    empty = np.array([], "datetime64[ns]")
    tn = pd.DatetimeIndex(f["t"]).tz_convert("UTC").tz_localize(None).to_numpy("datetime64[ns]")
    act = np.array([grid._covered(np.array([x]), *ivs.get(u, (empty, empty, empty))[:2])[0] for u, x in zip(f["unit"], tn)])
    ok = ~act & f[feats].notna().all(axis=1).to_numpy()
    rows = f[ok].reset_index(drop=True)
    if not len(rows):
        return []
    _, pm = predict(art, rows, feats)
    hist = ctx.frames[(typ, H)]
    pb = B.recent_rate(hist, rows, pd.Series(art["tables"]["p_unit"]), art["tables"]["alpha"], cfg.recent_window, cfg.H)
    return [{"unit": u, "s": int(t.value // 10**6), "p_model": float(a), "p_baseline": float(b)}
            for u, t, a, b in zip(rows["unit"], rows["t"], pm, pb)]


# ---------------------------------------------------------------- replay of the M6c-1 test week (plan §F)
def git_blob(commit, path, dest):
    import subprocess
    blob = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout
    Path(dest).write_bytes(blob)
    return dest


def pinned_m6c1_paths(tmp, commit="aa05529"):
    tmp = Path(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    return P.Paths(store=git_blob(commit, "datastore/alerts_in_ua.csv", tmp / "alerts_in_ua.csv"),
                   log=git_blob(commit, "reports/collect/pull_log.csv", tmp / "pull_log.csv"),
                   holes=git_blob(commit, "reports/collect/coverage_holes.csv", tmp / "coverage_holes.csv"))


def build_replay(ctx, arts, weights_csv=M6C1 / "blend_weights.csv"):
    """Per-row M6c-1 test-week predictions for "any" H = 1/3, computed WITHOUT pipeline.score_range: model ->
    calibrator, the D-025 recent rate from the frozen tables, and the PUBLISHED per-hour weights."""
    split = ctx.split
    w = pd.read_csv(weights_csv, parse_dates=["t"])
    out = []
    for H in (1, 3):
        cfg, fr, art = ctx.cfgs[H], ctx.frames[("any", H)], arts[("any", H)]
        el, _ = evaluate.eligibility(fr, split.test_start, split.test_end, cfg.H, F.feature_list("any"))
        sc = fr[el].reset_index(drop=True)
        _, pm = predict(art, sc, F.feature_list("any"))
        pb, _, _ = B.predict_from_tables(art["tables"], fr, sc, ctx.alerts, cfg)
        wh = w[(w["split"] == "test") & (w["type"] == "any") & (w["H"] == H)].set_index("t")["w"]
        ww = sc["t"].map(wh)
        if ww.isna().any():
            raise DataQualityError(f"H={H}: replay rows without a published weight")
        scored = pd.DataFrame({"H": H, "unit": sc["unit"], "t": sc["t"], "status": "scored", "y": sc["y"].to_numpy(),
                               "p_model": pm, "p_baseline": pb["recent_rate"].to_numpy(), "w": ww.to_numpy(),
                               "p_blend": ww.to_numpy() * pm + (1 - ww.to_numpy()) * pb["recent_rate"].to_numpy()})
        # every other unit-hour of the week with its reason, so the map can draw under-alert / gap hours (plan §F)
        wk = fr[(fr["t"] >= split.test_start) & (fr["t"] < split.test_end)]
        rest = wk[~wk.set_index(["unit", "t"]).index.isin(scored.set_index(["unit", "t"]).index)]
        status = np.where(rest["active_at_t"] == 1, "under_alert",
                          np.where(rest["gap_mask"] == 1, "gap", np.where(rest["t"] + cfg.H > split.test_end, "purged",
                                                                           "feature_missing")))
        out.append(scored)
        out.append(pd.DataFrame({"H": H, "unit": rest["unit"].to_numpy(), "t": rest["t"].to_numpy(), "status": status}))
    return pd.concat(out, ignore_index=True).sort_values(["H", "t", "unit"]).reset_index(drop=True)


def compare_replay(rep, ctx, arts, tol=1e-12):
    """Keyed per-row check of the replay against an INDEPENDENT recomputation through pipeline.score_range (its own
    blend weights): same (H, unit, t) keys and y, and p_model / p_baseline / w / p_blend within tol. Raises."""
    for H in (1, 3):
        cfg = ctx.cfgs[H]
        lab = {t: ctx.frames[(t, H)] for t in nd.TYPES}
        ref, _, _, _ = P.score_range(ctx, "any", H, arts, lab, cfg.test[0], cfg.test[1], None)
        a = rep[(rep["H"] == H) & (rep["status"] == "scored")].reset_index(drop=True)
        b = ref.rename(columns={"model": "p_model", "recent_rate": "p_baseline", "blend": "p_blend"})
        m = a.merge(b[["unit", "t", "y", "p_model", "p_baseline", "w", "p_blend"]], on=["unit", "t"], how="outer",
                    suffixes=("", "_ref"), indicator=True, validate="one_to_one")
        if (m["_merge"] != "both").any():
            raise DataQualityError(f"replay H={H}: keys differ from score_range ({int((m['_merge'] != 'both').sum())} rows)")
        if not np.array_equal(m["y"].to_numpy(float), m["y_ref"].to_numpy(float)):
            raise DataQualityError(f"replay H={H}: y differs")
        for c in ("p_model", "p_baseline", "w", "p_blend"):
            d = float(np.max(np.abs(m[c].to_numpy(float) - m[f"{c}_ref"].to_numpy(float))))
            if d > tol:
                raise DataQualityError(f"replay H={H}: {c} differs from score_range by {d}")
    return True
