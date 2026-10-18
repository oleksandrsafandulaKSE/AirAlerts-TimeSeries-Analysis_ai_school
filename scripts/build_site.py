"""Build the results site and the README's generated blocks from saved reports only (M5 plan §2-§5).

  python scripts/build_site.py            # site/index.html + README generated blocks
  python scripts/build_site.py --evidence # also re-run the leakage tests and save reports/leakage_evidence.json

Reads ONLY reports/official, reports/official_h3, reports/new_regime (+ reports/leakage_evidence.json), and (M11) the
OPTIONAL reports/m10 tables: a missing M10 file makes its page section say "not run yet" with the printed reason.
M11 also inlines netlify/live/lib/pattern.mjs (the recent-pattern grid, tested under node). Never reads data/,
never fits or scores, never recomputes a metric: every value is copied from its source file by an exact key
(file, predictor, group, metric). A missing report file raises (no placeholder numbers).
"""
import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "site_src" / "map_ukraine.json"
PATTERN_JS = ROOT / "netlify" / "live" / "lib" / "pattern.mjs"     # M11 §B2b: same code as the node tests
sys.path.insert(0, str(ROOT))

from src import regions  # noqa: E402  (unit/group table only: the single place names are mapped)

RUNS = {"h1": "official", "h3": "official_h3"}
PREDICTORS = ["model", "model_raw", "recent_rate", "climatology", "persistence_calibrated", "persistence_raw"]
GROUPS = ["overall", "kyiv_city", "frontline", "rear"]
METRICS = ["rows", "positives", "base_rate", "brier", "brier_skill_vs_recent", "roc_auc_pooled",
           "roc_auc_within_unit_mean", "within_unit_units_used", "within_unit_units_excluded", "pr_auc",
           "pr_auc_over_base", "low_n"]
LEAKAGE_TESTS = [
    ("Features unchanged when data after t is removed (real data, 33 times: active and standing alerts, gap "
     "edges, DST, cut-offs, off-hour times)", "tests/test_leakage.py::test_real_data_truncation_invariant"),
    ("Negative control caught: a feature using the final alert duration / a centred window",
     "tests/test_leakage.py::test_real_data_negative_control_pinned_witnesses"),
    ("Grid mask unchanged by truncation; the old D-009 rule (final duration) is caught",
     "tests/test_grid.py::test_mask_truncation_invariant"),
    ("Recent rate and raw persistence unchanged by truncation, H = 1 and H = 3",
     "tests/test_leakage.py::test_baselines_truncation_invariant"),
    ("Negative control caught: a recent-rate window that reads not-yet-known labels",
     "tests/test_leakage.py::test_baselines_negative_control"),
    ("Model predictions unchanged by truncation", "tests/test_leakage.py::test_model_predictions_truncation_invariant"),
    ("API loader -> grid -> features -> prediction unchanged by truncating the raw dump",
     "tests/test_leakage.py::test_api_loader_to_predictor_truncation_invariant"),
    ("Negative control caught on API data: final alert duration",
     "tests/test_leakage.py::test_api_negative_control_final_duration"),
    ("M10 hours-under-alert inputs unchanged by truncation (real data, 10 times: active/ending/starting alerts, "
     "standing alert, gap edges, DST, cut-off)", "tests/test_m10_leakage.py::test_block_d_truncation_invariant"),
    ("M10 negative control caught at all 10 pinned times: hours under alert without clipping at t",
     "tests/test_m10_leakage.py::test_block_d_negative_control_pinned"),
    ("Frozen baselines fit on train only; validation labels cannot change them",
     "tests/test_run_all.py::test_frozen_baselines_fit_on_train_only"),
    ("Test labels cannot change any pre-test output (H = 3 label poisoning)",
     "tests/test_run_all.py::test_h3_label_poisoning_changes_nothing"),
    ("Final test: joint access marker written before any test label is read",
     "tests/test_final_test.py::test_marker_written_before_any_test_label"),
    ("Final test: a changed predictor after access is refused",
     "tests/test_final_test.py::test_new_preregistration_after_access_is_refused"),
]


class SiteError(RuntimeError):
    pass


def _need(path):
    if not path.exists():
        raise SiteError(f"required report file missing: {path} (run the pipeline stages first)")
    return path


def clean(v):
    """JSON-safe value: NaN/inf -> None (shown as n/a with its saved reason)."""
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if hasattr(v, "item"):
        return clean(v.item())
    return v


def read_metrics(path):
    """metrics CSV -> {predictor: {group: {metric: value}}} by exact keys."""
    df = pd.read_csv(_need(path), keep_default_na=True)
    dup = df.duplicated(["baseline", "group"])
    if dup.any():
        raise SiteError(f"{path}: duplicate (baseline, group) rows {df.loc[dup, ['baseline', 'group']].values.tolist()}")
    out = {}
    for _, r in df.iterrows():
        cell = {}
        for m in METRICS:
            if m in df.columns:
                v = r[m]
                if m == "within_unit_units_excluded":
                    v = "" if pd.isna(v) else str(v)
                elif m == "low_n":
                    v = bool(v) if not pd.isna(v) else None
                cell[m] = clean(v)
        out.setdefault(r["baseline"], {})[r["group"]] = cell
    for p in ("model", "recent_rate"):                      # rows the page and README always read
        for g in GROUPS:
            if g not in out.get(p, {}):
                raise SiteError(f"{path}: missing row ({p}, {g})")
            for m in ("rows", "base_rate", "brier"):
                if out[p][g].get(m) is None:
                    raise SiteError(f"{path}: ({p}, {g}) has no {m}")
    return out


def require_rows(rows, keys, path):
    have = {tuple(r[k] for k in keys[0]) for r in rows}
    missing = [k for k in keys[1] if k not in have]
    if missing:
        raise SiteError(f"{path}: missing rows {missing}")
    if len(have) != len(rows):
        raise SiteError(f"{path}: duplicate rows")


def nan_reasons(checks_path):
    if not checks_path.exists():
        return {}
    reasons = json.loads(checks_path.read_text()).get("nan_reasons", [])
    out = {}
    for r in reasons:
        key, _, text = r.partition(": ")
        out.setdefault(key, []).append(text)
    return out


def records(path, cols=None):
    df = pd.read_csv(_need(path))
    if cols:
        df = df[cols]
    return [{k: clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def build_payload(reports):
    reports = Path(reports)
    payload = {"horizons": {}, "groups": {}, "units": {}}
    for g in ("kyiv_city", "frontline", "rear"):
        payload["groups"][g] = [u for u, v in regions.UNITS.items() if v["group"] == g]
    for u, v in regions.UNITS.items():
        payload["units"][u] = {"name": v["official_name"], "group": v["group"]}
    payload["neighbours"] = {u: sorted(regions.NEIGHBOURS[u]) for u in regions.UNITS}     # M11 §B1 (border table)
    payload["map"] = json.loads(_need(MAP).read_text())          # M8: geoBoundaries SVG paths (scripts/build_map.py)
    if sorted(payload["map"]["units"]) != sorted(regions.UNITS):
        raise SiteError("map units differ from regions.py")
    access = json.loads(_need(reports / "final_test_access.json").read_text())
    if "first_access_utc" not in access:
        raise SiteError("final_test_access.json has no first_access_utc (the replay is labelled with it)")
    for key, run in RUNS.items():
        d = reports / run
        prereg = json.loads(_need(d / "preregistration.json").read_text())
        checks = json.loads(_need(d / "final_test_checks.json").read_text())
        payload["horizons"][key] = {
            "run": run, "H": prereg["H"],
            "final": read_metrics(d / "metrics.csv"),
            "validation": read_metrics(d / "metrics_validation.csv"),
            "final_reasons": nan_reasons(d / "final_test_checks.json"),
            "reliability": records(d / "reliability_bins.csv"),
            "citl": records(d / "calibration_in_the_large.csv"),
            "eligibility": checks["eligibility"],
            "prereg": {k: prereg[k] for k in ("best_iteration", "calibration_decision", "calibration_rule",
                                              "primary_metric", "features")},
            "calibrator": json.loads(_need(d / "calibrator.json").read_text()),
            "dates": prereg["dates"],
        }
    payload["new_regimes"] = {}
    for variant in ("new_regime", "new_regime_all_types"):
        nr = reports / variant
        meta = json.loads(_need(nr / "run_meta.json").read_text())
        transfer = records(nr / "transfer.csv")
        require_rows(transfer, (("predictor", "group"), [(p, g) for p in ("model", "recent_rate") for g in GROUPS]),
                     nr / "transfer.csv")
        before_after = records(nr / "before_after.csv")
        require_rows(before_after, (("unit", "window"), [(f"[{g}]", w) for g in GROUPS for w in
                                                         {r["window"] for r in before_after} or {"<none>"}]),
                     nr / "before_after.csv")
        if len({r["window"] for r in before_after}) != 2:
            raise SiteError(f"{nr / 'before_after.csv'}: expected an official and an API window")
        payload["new_regimes"][variant] = {
            "metrics": read_metrics(nr / "metrics.csv"),
            "transfer": transfer,
            "before_after": before_after,
            "reliability": records(nr / "reliability_bins.csv"),
            "meta": {k: meta[k] for k in ("history_start", "coverage_end", "scored_range", "eligibility", "loader",
                                          "alert_counts_in_coverage", "dump", "api_alert_types")},
        }
    m1 = json.loads(_need(reports / "official" / "m1_checks.json").read_text())
    run_meta = json.loads(_need(reports / "official" / "run_meta.json").read_text())
    payload["data"] = {"row_counts": run_meta["row_counts"], "detected_gaps": m1["detected_gaps"],
                       "approved_gaps": run_meta["approved_gaps"], "over_24h_total": m1["over_24h_total"],
                       "exactly_30min_total": m1["exactly_30min_total"], "zero_duration": m1["zero_duration"],
                       "base_rate_2024_avg": m1["base_rate_2024_avg"]}
    ev = reports / "leakage_evidence.json"
    payload["leakage"] = json.loads(_need(ev).read_text())
    payload["transfer_outcome"] = transfer_outcome(payload).replace("**", "")
    imp = reports / "improve"
    v = pd.read_csv(_need(imp / "variants_test_posthoc.csv"), float_precision="round_trip")
    if v.duplicated(["baseline", "group"]).any():
        raise SiteError("variants_test_posthoc.csv: duplicate (variant, group) rows")
    payload["improve"] = {
        "variants": records(imp / "variants_test_posthoc.csv"),
        "blocks": records(imp / "feature_blocks.csv"),
        "selection": json.loads(_need(imp / "validation_selection.json").read_text()),
        "blend": json.loads(_need(imp / "blend_weight.json").read_text()),
        "weekly": records(imp / "weekly_refit.csv"),
    }
    add_public_layer(payload, reports)
    # full precision (round_trip): the replay's end value must equal it to 1e-12
    hm = pd.read_csv(reports / "official" / "metrics.csv", float_precision="round_trip").set_index(["baseline", "group"])
    payload["replay"] = {"scored_once_utc": access["first_access_utc"],
                         "headline_bss": clean(hm.loc[("model", "overall"), "brier_skill_vs_recent"]),
                         "headline_rows": clean(hm.loc[("model", "overall"), "rows"])}
    payload["m10"] = read_m10(reports / "m10")
    return payload


# ---------------- M11 §B5-§B7: optional M10 tables ----------------
M10_FILES = {"stability": "stability_validation.csv", "stability_posthoc": "stability_test_posthoc.csv",
             "labels_variant": "labels_variant.csv", "labels_predictability": "labels_predictability.csv",
             "recency_folds": "recency_folds.csv", "exposure_folds": "exposure_folds.csv",
             "labels_onset_changes": "labels_onset_changes.csv"}
STABILITY_COLS = ["slice_kind", "slice", "group", "baseline", "rows", "positives", "brier", "brier_skill_vs_recent"]
SLICE_KINDS = {"week", "day_night"}
GROUP_KEYS = ("overall", "kyiv_city", "frontline", "rear")


def read_m10(d):
    """Each M10 file is optional: absent -> {"available": False, "reason"} (printed and shown on the page, not hidden).
    A file that exists but is empty or lacks the columns the page needs raises."""
    out = {}
    for key, name in M10_FILES.items():
        path = Path(d) / name
        if not path.exists():
            reason = f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} not found (M10 not run yet)"
            print(f"[site] M10 {key}: not run yet ({reason})")
            out[key] = {"available": False, "reason": reason}
            continue
        df = pd.read_csv(path, float_precision="round_trip")
        if df.empty:
            raise SiteError(f"{path}: empty file")
        if key.startswith("stability"):
            miss = [c for c in STABILITY_COLS if c not in df.columns]
            if miss:
                raise SiteError(f"{path}: missing columns {miss} (contract: {STABILITY_COLS})")
            if df.duplicated(["slice_kind", "slice", "group", "baseline"]).any():
                raise SiteError(f"{path}: duplicate (slice_kind, slice, group, baseline) rows")
            bad = sorted(set(df["slice_kind"]) - SLICE_KINDS)
            if bad:
                raise SiteError(f"{path}: unknown slice_kind {bad}")
        shown = df
        if "unit" in df.columns and key != "labels_onset_changes":     # per-unit totals are summed for the README
            grp = df["unit"].astype(str).isin(GROUP_KEYS) | df["unit"].astype(str).str.startswith("[")
            if grp.any():
                shown = df[grp]
        pos = (f", positives {int(df['positives'].sum()):,}, pooled base rate {df['positives'].sum() / df['rows'].sum():.4f}"
               if {"positives", "rows"} <= set(df.columns) and df["rows"].sum() > 0 else "")
        print(f"[site] M10 {key}: {path.name} shape {df.shape}, {len(shown)} rows shown{pos}")
        out[key] = {"available": True, "file": name, "columns": list(df.columns),
                    "rows": [{k: clean(v) for k, v in r.items()} for r in shown.to_dict(orient="records")]}
    return out


STATUS_CODE = {"scored": 0, "under_alert": 1, "gap_or_missing": 2, "label_unknown": 3, "feature_missing": 4, "purged": 5}


def compare_word(skill):
    if skill is None:
        return "cannot be compared with"
    if skill > 0:
        return "more accurate than"
    if skill < 0:
        return "less accurate than"
    return "as accurate as"


def plain_sentences(payload):
    """Public summary (M5b §3): wording by the sign of the saved skill; every number from a source key."""
    h1 = payload["horizons"]["h1"]
    m = h1["final"]["model"]
    out = []
    s = m["overall"]["brier_skill_vs_recent"]
    pct = "" if s is None else f" by {abs(100 * s):.1f}%"
    out.append({"key": "overall", "skill": s, "rows": m["overall"]["rows"],
                "text": f"Over the six-week test the model was {compare_word(s)} the simple two-week rule{pct} "
                        f"({m['overall']['rows']:,} oblast-hours scored)."})
    for g in ("kyiv_city", "rear", "frontline"):
        c = m[g]
        sg = c["brier_skill_vs_recent"]
        reasons = []
        if c["rows"] is not None and c["rows"] < 100:
            reasons.append("fewer than 100 scored hours")
        if c.get("within_unit_units_excluded"):
            reasons.append("some oblasts had too few alert starts or too few no-start hours to rank")
        pctg = "" if sg is None else f" by {abs(100 * sg):.1f}%"
        text = f"{GROUP_NAMES[g]}: {compare_word(sg)} the two-week rule{pctg} ({c['rows']:,} hours)"
        if reasons:
            text += " — treat with caution: " + "; ".join(reasons)
        out.append({"key": g, "skill": sg, "rows": c["rows"], "low_n_reason": "; ".join(reasons), "text": text + "."})
    cit = next(r for r in h1["citl"] if r["predictor"] == "model" and r["group"] == "overall")
    out.append({"key": "calibration", "mean_pred": cit["mean_pred"], "mean_obs": cit["mean_obs"],
                "text": f"On average it gave a {100 * cit['mean_pred']:.1f}% chance per hour, and a new alert started in "
                        f"{100 * cit['mean_obs']:.1f}% of those hours."})
    return out


def add_public_layer(payload, reports):
    """M5b: per-oblast breakdown (human-authorised, proposed D-031), timeline, plain sentences."""
    off = Path(reports) / "official"
    mu = pd.read_csv(_need(off / "metrics_by_unit.csv"))
    if len(mu) != 24 or mu["unit"].duplicated().any() or set(mu["unit"]) != set(regions.UNITS):
        raise SiteError("metrics_by_unit.csv must have exactly the 24 units once")
    keys = ("scored_hours", "alert_starts", "base_rate", "brier_model", "brier_recent_rate", "brier_skill_vs_recent",
            "roc_auc_within_unit", "low_n")
    payload["by_unit"] = {}
    for _, r in mu.iterrows():
        d = {k: clean(r[k]) for k in keys}
        d["low_n_reason"] = "" if pd.isna(r["low_n_reason"]) else str(r["low_n_reason"])
        payload["by_unit"][r["unit"]] = d
    tp = pd.read_csv(_need(off / "test_predictions.csv"), float_precision="round_trip")
    tp["t"] = pd.to_datetime(tp["t"], utc=True)
    start = pd.Timestamp(payload["horizons"]["h1"]["dates"]["test"][0])
    start = start.tz_localize("UTC") if start.tz is None else start
    hours = int(tp["t"].nunique())
    on = pd.read_csv(_need(off / "test_onsets.csv"))
    on["onset"] = pd.to_datetime(on["onset"], utc=True)
    tl = {}
    for u, g in tp.sort_values(["unit", "t"]).groupby("unit"):
        if len(g) != hours or g["t"].iloc[0] != start:
            raise SiteError(f"test_predictions.csv: {u} is not a complete hourly series from the test start")
        tl[u] = {"status": [STATUS_CODE[x] for x in g["status"]],
                 "p_model": [clean(x) for x in g["p_model"]], "p_recent": [clean(x) for x in g["p_recent_rate"]],
                 "y": [None if pd.isna(x) else int(x) for x in g["y"]],                  # M11 §B4 replay (scored rows)
                 "onsets_min": [round((x - start).total_seconds() / 60, 2) for x in on.loc[on["unit"] == u, "onset"]]}
    payload["timeline"] = {"start": start.isoformat(), "hours": hours, "units": tl, "status_names": list(STATUS_CODE)}
    sc = tp[tp["status"] == "scored"]
    print(f"[site] timeline: {len(tl)} units x {hours} hours from {tp['t'].min()} to {tp['t'].max()}; status counts "
          f"{tp['status'].value_counts().to_dict()}; scored base rate {sc['y'].mean():.4f} on {len(sc):,} rows; "
          f"{len(on):,} test onsets")
    payload["plain"] = plain_sentences(payload)


def run_leakage_evidence(reports):
    rows = []
    for label, node in LEAKAGE_TESTS:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", node], cwd=ROOT, capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or [""])[-1]
        result = "FAIL" if r.returncode != 0 else ("SKIP" if ("skipped" in tail or "deselected" in tail
                                                               or " passed" not in tail) else "PASS")
        rows.append({"check": label, "test": node, "result": result, "pytest": tail})
    (Path(reports) / "leakage_evidence.json").write_text(json.dumps(rows, indent=2))
    if any(x["result"] != "PASS" for x in rows):
        raise SiteError("a leakage test failed or was skipped: " + json.dumps([x for x in rows if x["result"] != "PASS"]))
    return rows


# ---------------- README generated blocks ----------------
NAMES = {"model": "Model (LightGBM)", "model_raw": "Model, before Platt", "recent_rate": "Recent rate (14 d)",
         "climatology": "Climatology", "persistence_calibrated": "Calibrated persistence",
         "persistence_raw": "Raw persistence"}
GROUP_NAMES = {"overall": "All units", "kyiv_city": "Kyiv City", "frontline": "Frontline (8)", "rear": "Rear (15)"}


def fmt(v, nd=4):
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}"
    return f"{v:.{nd}f}"


def results_table(metrics, title):
    cols = [("brier", "Brier"), ("brier_skill_vs_recent", "Brier skill vs recent rate"),
            ("roc_auc_pooled", "ROC-AUC pooled"), ("roc_auc_within_unit_mean", "ROC-AUC within unit"),
            ("pr_auc", "PR-AUC"), ("pr_auc_over_base", "PR-AUC / base rate"), ("rows", "Rows"),
            ("base_rate", "Base rate"), ("low_n", "Low-n")]
    lines = [f"**{title}**", "", "| Predictor | Group | " + " | ".join(c[1] for c in cols) + " |",
             "|" + "---|" * (len(cols) + 2)]
    for p in PREDICTORS:
        if p not in metrics:
            continue
        for g in GROUPS:
            c = metrics[p][g]
            lines.append(f"| {NAMES[p]} | {GROUP_NAMES[g]} | " + " | ".join(fmt(c.get(k)) for k, _ in cols) + " |")
    return "\n".join(lines)


def generated_blocks(payload):
    h1, h3 = payload["horizons"]["h1"], payload["horizons"]["h3"]
    skill = h1["final"]["model"]["overall"]["brier_skill_vs_recent"]
    verdict = ("the model beats the rolling recent-rate baseline" if skill is not None and skill > 0 else
               "the model does NOT beat the rolling recent-rate baseline" if skill is not None else
               "the headline skill is undefined")
    blocks = {}
    blocks["headline"] = (f"Final test, H = 1 (scored once): Brier skill of the model vs the rolling recent-rate "
                          f"baseline = **{fmt(skill)}** on {fmt(h1['final']['model']['overall']['rows'])} rows "
                          f"(base rate {fmt(h1['final']['model']['overall']['base_rate'])}): {verdict}.")
    blocks["final_h1"] = results_table(h1["final"], "Final test, H = 1 hour (headline)")
    blocks["final_h3"] = results_table(h3["final"], "Final test, H = 3 hours (additional horizon; not comparable to H = 1)")
    blocks["validation_h1"] = results_table(h1["validation"], "Validation, H = 1 hour (known before the test was scored)")
    elig = []
    for k, h in (("H = 1", h1), ("H = 3", h3)):
        e = h["eligibility"]
        elig.append(f"| {k} | {e['in_range']:,} | {e['eligible']:,} | "
                    + " | ".join(f"{e['excluded_exclusive'][r]:,}" for r in ("purge", "masked", "y_nan", "feature_nan")) + " |")
    blocks["coverage"] = "\n".join(["| Horizon | Test rows in range | Scored | Purged | Under alert / gap-masked | "
                                    "Label unknown | Feature missing |", "|---|---|---|---|---|---|---|"] + elig)
    tr = ["| API variant | Predictor | Group | Within-unit AUC | Units used | Mean predicted | Mean observed | Predicted − observed |",
          "|---|---|---|---|---|---|---|---|"]
    ba = ["| API variant | Group | Window | Onsets per 30 days | Share of time under alert | Exposed hours |",
          "|---|---|---|---|---|---|"]
    for variant, vlabel in (("new_regime", "air-raid only"), ("new_regime_all_types", "all types")):
        nrv = payload["new_regimes"][variant]
        for r in nrv["transfer"]:
            if r["predictor"] in ("model", "recent_rate"):
                tr.append(f"| {vlabel} | {NAMES.get(r['predictor'], r['predictor'])} | {GROUP_NAMES[r['group']]} | "
                          f"{fmt(r['roc_auc_within_unit_mean'])} | {fmt(r['within_unit_units_used'])} | {fmt(r['mean_pred'])} | "
                          f"{fmt(r['mean_obs'])} | {fmt(r['pred_minus_obs'])} |")
        for r in nrv["before_after"]:
            if str(r["unit"]).startswith("[") and (variant == "new_regime" or not r["window"].startswith("official")):
                ba.append(f"| {vlabel if not r['window'].startswith('official') else 'official'} | {GROUP_NAMES[r['group']]} | "
                          f"{r['window']} | {fmt(r['onsets_per_30d'], 1)} | {fmt(r['share_under_alert'], 3)} | "
                          f"{fmt(r['exposed_hours'])} |")
    blocks["transfer"] = "\n".join(tr)
    blocks["before_after"] = "\n".join(ba)
    nm = ["| API variant | Predictor | Group | Brier | Brier skill vs recent rate | Rows | Base rate | Low-n |",
          "|---|---|---|---|---|---|---|---|"]
    for variant, vlabel in (("new_regime", "air-raid only"), ("new_regime_all_types", "all types")):
        mets = payload["new_regimes"][variant]["metrics"]
        for p in PREDICTORS:
            for g in GROUPS:
                if p in mets and g in mets[p]:
                    c = mets[p][g]
                    nm.append(f"| {vlabel} | {NAMES[p]} | {GROUP_NAMES[g]} | {fmt(c['brier'])} | "
                              f"{fmt(c['brier_skill_vs_recent'])} | {fmt(c['rows'])} | {fmt(c['base_rate'])} | {fmt(c['low_n'])} |")
    blocks["new_regime_metrics"] = "\n".join(nm)
    imp = payload["improve"]
    vt = ["| Variant (post-hoc) | Group | Brier | Brier skill vs recent rate | Within-unit AUC | Rows | Low-n |",
          "|---|---|---|---|---|---|---|"]
    for r in imp["variants"]:
        if r["baseline"] in IMPROVE_NAMES:
            vt.append(f"| {IMPROVE_NAMES[r['baseline']]} | {GROUP_NAMES[r['group']]} | {fmt(r['brier'])} | "
                      f"{fmt(r['brier_skill_vs_recent'])} | {fmt(r['roc_auc_within_unit_mean'])} | {fmt(r['rows'])} | {fmt(r['low_n'])} |")
    blocks["improve_variants"] = "\n".join(vt)
    bt = ["| Feature block | Mean fold Brier, without | Mean fold Brier, with | Relative change | Folds improved | Accepted |",
          "|---|---|---|---|---|---|"]
    for r in imp["blocks"]:
        if r["fold_cut"] == "mean":
            bt.append(f"| {BLOCK_NAMES[r['block']]} | {fmt(r['reference_brier'], 5)} | {fmt(r['candidate_brier'], 5)} | "
                      f"{fmt(r['relative_change'])} | {int(r['folds_improved'])} | {fmt(bool(r['accepted']))} |")
    blocks["improve_blocks"] = "\n".join(bt)
    sel = imp["selection"]
    best = {"V2": "V2 offset", "V3": "V3 offset + accepted blocks", "V5": "V5 blend"}[sel["best_posthoc_by_validation"]]
    blocks["improve_reading"] = improve_reading(payload)
    blocks["improve_selection"] = (f"Chosen on validation only ({sel['rows']:,} rows), not on the test (whose headline results were already known): "
                                   f"**{best}** (blend weight on the model {imp['blend']['w']}). Accepted feature blocks: "
                                   f"{', '.join(sel['accepted_blocks']) or 'none'}.")
    blocks["transfer_outcome"] = transfer_outcome(payload)
    d = payload["data"]
    rc = d["row_counts"]
    blocks["data_facts"] = "\n".join([
        "| Fact (official file) | Value |", "|---|---|",
        f"| Raw rows | {rc['raw_rows']:,} |", f"| Exact duplicate rows removed | {rc['duplicate_rows']:,} |",
        f"| Rows after deduplication | {rc['dedup_rows']:,} |", f"| Luhanska rows excluded | {rc['excluded_rows']:,} |",
        f"| Detected recording gap (UTC) | {', '.join(a[:16] + ' → ' + b[:16] for a, b in d['detected_gaps'])} |",
        f"| Approved gap (UTC) | {', '.join(a[:16] + ' → ' + b[:16] for a, b in d['approved_gaps'])} |",
        f"| Alerts lasting > 24h (before the test) | {d['over_24h_total']:,} |",
        f"| Exactly-30-minute alerts (before the test) | {d['exactly_30min_total']:,} |",
        f"| Zero-duration alerts | {d['zero_duration']:,} |"])
    for key, label in (("new_regime", "air-raid alerts only"), ("new_regime_all_types", "all alert types")):
        if key in payload.get("new_regimes", {}):
            m = payload["new_regimes"][key]["meta"]
            blocks.setdefault("api_facts", [])
            blocks["api_facts"].append(f"| {label} | {m['loader']['alerts']:,} | {m['loader']['open_alerts']:,} | "
                                       f"{m['history_start'][:16]} | {m['scored_range'][0][:16]} → {m['scored_range'][1][:16]} | "
                                       f"{m['eligibility']['eligible']:,} |")
    if "api_facts" in blocks:
        blocks["api_facts"] = "\n".join(["| API variant | Alerts kept | Open alerts kept | Coverage starts (UTC) | Scored window (UTC) | Scored unit-hours |",
                                         "|---|---|---|---|---|---|"] + blocks["api_facts"])
    lk = ["| Check | Result | Evidence (pytest node) |", "|---|---|---|"]
    lk += [f"| {r['check']} | {r['result']} | `{r['test']}` |" for r in payload["leakage"]]
    blocks["leakage"] = "\n".join(lk)
    blocks.update(m10_blocks(payload))
    return blocks


def m10_blocks(payload):
    """README blocks for M10 (plans/M10.md), every number copied from reports/m10; 'not run yet' when absent."""
    m = payload.get("m10", {})

    def missing(*keys):
        gone = [m[k]["reason"] for k in keys if not m.get(k, {}).get("available")]
        return f"Not run yet: {'; '.join(gone)}." if gone else None

    out = {}
    out["m10_labels"] = missing("labels_variant", "labels_onset_changes", "labels_predictability") or "\n".join(
        ["| Period | Group | Onsets L0 → L1 | Share of hours under alert L0 → L1 | Base rate L0 → L1 |", "|---|---|---|---|---|"]
        + [f"| {r['period']} | {GROUP_NAMES[r['group']]} | {fmt(r['onsets_L0'])} → {fmt(r['onsets_L1'])} | "
           f"{fmt(r['share_under_alert_L0'])} → {fmt(r['share_under_alert_L1'])} | {fmt(r['base_rate_L0'])} → {fmt(r['base_rate_L1'])} |"
           for r in m["labels_variant"]["rows"] if r["period"] in ("train", "validation") and str(r["unit"]).startswith("[")]
        + ["", "| Train onsets, L0 → L1 matching | Kept | Shifted later | Disappeared | New in L1 |", "|---|---|---|---|---|",
           "| all units | " + " | ".join(f"{sum(int(r[c]) for r in m['labels_onset_changes']['rows'] if r['period'] == 'train'):,}"
                                        for c in ("kept", "shifted", "disappeared", "new_in_l1")) + " |",
           "", "| Variant | Split | Group | BSS vs its own recent rate | Within-unit AUC | Rows | Base rate |",
           "|---|---|---|---|---|---|---|"]
        + [f"| {r['variant']} | {r['split']} | {GROUP_NAMES[r['group']]} | {fmt(r['brier_skill_vs_recent'])} | "
           f"{fmt(r['roc_auc_within_unit_mean'])} | {fmt(r['rows'])} | {fmt(r['base_rate'])} |"
           for r in m["labels_predictability"]["rows"] if r["baseline"] == "model" and r["group"] in ("overall", "frontline")])
    if missing("recency_folds", "exposure_folds"):
        out["m10_folds"] = missing("recency_folds", "exposure_folds")
    else:
        ft = ["| Candidate (vs reference) | Mean fold Brier, reference | Mean fold Brier, candidate | Relative change | Folds improved | Passes the rule |",
              "|---|---|---|---|---|---|"]
        for r in m["recency_folds"]["rows"]:
            if r["fold_cut"] == "mean":
                ft.append(f"| recency half-life {int(float(r['half_life_days']))} d (vs equal weights) | {fmt(r['reference_brier'], 5)} | "
                          f"{fmt(r['brier'], 5)} | {fmt(r['relative_change'])} | {int(r['folds_improved'])} | {fmt(bool(r['accepted']))} |")
        for r in m["exposure_folds"]["rows"]:
            if r["fold_cut"] == "mean":
                ft.append(f"| hours under alert, block D (vs V2 + chosen recency) | {fmt(r['reference_brier'], 5)} | "
                          f"{fmt(r['candidate_brier'], 5)} | {fmt(r['relative_change'])} | {int(r['folds_improved'])} | "
                          f"{fmt(bool(r['accepted']))} |")
        out["m10_folds"] = "\n".join(ft)
    out["m10_stability"] = missing("stability") or "\n".join(
        ["| Slice | Frozen headline (V0): BSS vs recent rate | M10 variant: BSS vs recent rate | Rows | Base rate |",
         "|---|---|---|---|---|"]
        + [f"| {r['slice']} | {fmt(r['brier_skill_vs_recent'])} | "
           f"{fmt(next(x['brier_skill_vs_recent'] for x in m['stability']['rows'] if x['slice'] == r['slice'] and x['group'] == 'overall' and x['baseline'] == 'M10'))} | "
           f"{fmt(r['rows'])} | {fmt(r['base_rate'])} |"
           for r in m["stability"]["rows"] if r["group"] == "overall" and r["baseline"] == "V0"])
    return out


def render_readme(text, blocks):
    for name, body in blocks.items():
        start, end = f"<!-- GENERATED:{name} START -->", f"<!-- GENERATED:{name} END -->"
        if text.count(start) != 1 or text.count(end) != 1:
            raise SiteError(f"README needs exactly one pair of markers for block {name!r}")
        text = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: f"{start}\n{body}\n{end}", text, flags=re.S)
    return text


IMPROVE_NAMES = {"V0_frozen_headline": "V0 frozen headline (pre-registered)", "V1_weekly_refit": "V1 weekly refit",
                 "V2_offset": "V2 recent-rate offset", "V3_offset_plus": "V3 offset + accepted blocks",
                 "V4_weekly_refit_offset_plus": "V4 weekly refit + offset", "V5_blend": "V5 blend (model + recent rate)",
                 "recent_rate": "Recent rate (14 d)"}
BLOCK_NAMES = {"A": "A drift rates", "B": "B attack waves", "C": "C daily rhythm"}
def improve_reading(payload):
    """M7 reviewer: state the facts that change how the post-hoc rows read, all from saved values."""
    imp = payload["improve"]
    v = {(r["baseline"], r["group"]): r for r in imp["variants"]}
    sk = lambda n, g="overall": v[(n, g)]["brier_skill_vs_recent"]  # noqa: E731
    au = lambda n, g="overall": v[(n, g)]["roc_auc_within_unit_mean"]  # noqa: E731
    cands = [n for n in ("V1_weekly_refit", "V2_offset", "V3_offset_plus", "V4_weekly_refit_offset_plus", "V5_blend")]
    test_best = max(cands, key=lambda n: sk(n))
    chosen = {"V2": "V2_offset", "V3": "V3_offset_plus", "V5": "V5_blend"}[imp["selection"]["best_posthoc_by_validation"]]
    steps = [r for r in imp.get("weekly", []) if r.get("variant") == "V4_weekly_refit_offset_plus"]
    scored_steps = sum(1 for r in steps if (r.get("rows") or 0) > 0)
    lines = [
        f"- Best on the test: {IMPROVE_NAMES[test_best]} (skill {fmt(sk(test_best))}); it was NOT chosen. The variant chosen "
        f"on validation, {IMPROVE_NAMES[chosen]}, scores {fmt(sk(chosen))}. Picking the test-best row would be selection on the test.",
        f"- Ranking within an oblast gets WORSE with the offset: within-unit AUC {fmt(au('V0_frozen_headline'))} (headline) vs "
        f"{fmt(au('V2_offset'))} (V2) and {fmt(au(chosen))} (chosen); frontline {fmt(au('V0_frozen_headline', 'frontline'))} vs "
        f"{fmt(au('V2_offset', 'frontline'))}. The Brier gain comes from matching the recent alert LEVEL (recalibration toward the "
        f"recent rate), not from ranking hours better.",
        f"- Weekly refit: {scored_steps} of {len(steps)} weekly steps scored rows (the last step falls in the recording gap and "
        f"its aftermath, where inputs are missing).",
    ]
    gb = imp["blend"]["grid"]
    ws = sorted(gb, key=lambda k: gb[k])
    if len(ws) > 1:
        lines.append(f"- The blend weight {imp['blend']['w']} won on validation by a very small margin "
                     f"({gb[ws[1]] - gb[ws[0]]:.1e} in Brier over weight {ws[1]}); nearby weights are practically equivalent.")
    lines.append("- These rows cover the same scored hours as the headline (27 Jul – 28 Aug; the recording gap and the days "
                 "after it have missing inputs and are not scored).")
    if not imp["selection"]["accepted_blocks"]:
        lines.append("- No feature block was accepted, so V3 is the same model as V2, and the blend (which includes "
                     "weight 1 on the model) can only match or beat it on validation by construction.")
    return "\n".join(lines)


CITL_TOLERANCE = 0.02  # same size as the ECE threshold of the pre-registered calibration rule


def transfer_outcome(payload):
    """D-015 (d): resolve the conditional conclusion from the saved numbers with a stated rule (M5, provisional):
    transfer is judged NOT good enough if, on either API variant, the frozen model's overall Brier skill vs the recent
    rate is < 0 OR |mean predicted − observed| > CITL_TOLERANCE."""
    parts, fails = [], []
    for variant, vlabel in (("new_regime", "air-raid only"), ("new_regime_all_types", "all types")):
        nrv = payload["new_regimes"][variant]
        skill = nrv["metrics"]["model"]["overall"]["brier_skill_vs_recent"]
        t = next(r for r in nrv["transfer"] if r["predictor"] == "model" and r["group"] == "overall")
        bad = (skill is not None and skill < 0) or abs(t["pred_minus_obs"]) > CITL_TOLERANCE
        fails.append(bad)
        parts.append(f"{vlabel}: Brier skill vs recent rate {fmt(skill)}, mean predicted − observed "
                     f"{fmt(t['pred_minus_obs'])}, within-unit AUC {fmt(t['roc_auc_within_unit_mean'])}")
    verdict = ("transfer is NOT good enough: the frozen model needs recalibration or retraining on post-reform data "
               "before use" if any(fails) else "transfer holds by this rule")
    return (f"Measured ({'; '.join(parts)}). Rule (provisional, set after these numbers were seen; the skill < 0 part "
            f"alone decides here): transfer fails if Brier skill < 0 or |predicted − observed| > {CITL_TOLERANCE} overall. "
            f"Outcome: **{verdict}**. Causes are hypotheses.")


def write_readme_blocks(readme, blocks):
    text = render_readme(readme.read_text(), blocks)
    readme.write_text(text)
    return text


def render_site(payload, template):
    html = Path(template).read_text()
    data = json.dumps(payload, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    if html.count("/*__DATA__*/null") != 1:
        raise SiteError("template needs exactly one /*__DATA__*/null placeholder")
    if html.count("/*__PATTERN_JS__*/") != 1:
        raise SiteError("template needs exactly one /*__PATTERN_JS__*/ placeholder")
    pattern = re.sub(r"^export ", "", _need(PATTERN_JS).read_text(), flags=re.M)
    if re.search(r"^\s*import ", pattern, flags=re.M) or "</script" in pattern:
        raise SiteError(f"{PATTERN_JS} must be self-contained to be inlined")
    return html.replace("/*__PATTERN_JS__*/", pattern).replace("/*__DATA__*/null", data)


def build_site(payload, template, out):
    html = render_site(payload, template)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", default=str(ROOT / "reports"))
    ap.add_argument("--template", default=str(ROOT / "site_src" / "template.html"))
    ap.add_argument("--out", default=str(ROOT / "site" / "index.html"))
    ap.add_argument("--readme", default=str(ROOT / "README.md"))
    ap.add_argument("--evidence", action="store_true")
    args = ap.parse_args(argv)
    if args.evidence:
        run_leakage_evidence(args.reports)
    payload = build_payload(args.reports)
    html = render_site(payload, args.template)                                   # everything computed first ...
    readme_text = render_readme(Path(args.readme).read_text(), generated_blocks(payload))
    out = Path(args.out)                                                         # ... then written (atomic build)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    Path(args.readme).write_text(readme_text)
    print(f"[site] wrote {args.out} and the README generated blocks")


if __name__ == "__main__":
    main()
