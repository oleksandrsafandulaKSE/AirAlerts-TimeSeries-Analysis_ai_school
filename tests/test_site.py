"""Results site and README generated blocks (M5 plan §8): values by exact source key, swap mutations, no hand-typed
result numbers, missing files raise, group mapping, Streamlit loader."""
import json
import re
import shutil
from pathlib import Path

import pandas as pd
import pytest

from scripts import build_site as B
from src import regions

ROOT = Path(__file__).resolve().parents[1]
PREDS = ["model", "recent_rate", "climatology", "persistence_calibrated", "persistence_raw"]


def metrics_csv(path, seed):
    rows = []
    for i, p in enumerate(PREDS):
        for j, g in enumerate(B.GROUPS):
            v = seed + 0.01 * i + 0.001 * j
            rows.append({"baseline": p, "group": g, "rows": 1000 + 10 * i + j, "positives": 100 + i + j,
                         "base_rate": 0.1 + 0.001 * j, "brier": v, "brier_skill_vs_recent": (0.0 if p == "recent_rate" else -v),
                         "roc_auc_pooled": 0.8 + 0.01 * i, "roc_auc_within_unit_mean": (None if (i, j) == (4, 1) else 0.5 + 0.01 * i + 0.002 * j),
                         "within_unit_units_used": 3 + j, "within_unit_units_excluded": "lvivska" if j == 3 else "",
                         "pr_auc": 0.3 + 0.01 * i, "pr_auc_over_base": 3.0 + 0.1 * i, "low_n": j == 2})
    pd.DataFrame(rows).to_csv(path, index=False)


def fixture_reports(tmp):
    r = tmp / "reports"
    for run, H, seed in (("official", "1h", 0.07), ("official_h3", "3h", 0.09)):
        d = r / run
        d.mkdir(parents=True)
        metrics_csv(d / "metrics.csv", seed)
        metrics_csv(d / "metrics_validation.csv", seed + 0.005)
        (d / "preregistration.json").write_text(json.dumps({"H": H, "best_iteration": 7, "calibration_decision": "none",
            "calibration_rule": "Platt iff ECE > 0.02", "primary_metric": "skill", "features": ["a"],
            "dates": {"train": ["2022-03-23", "2026-06-29"], "val": ["2026-06-29", "2026-07-27"], "test": ["2026-07-27", "2026-09-07"]}}))
        (d / "final_test_checks.json").write_text(json.dumps({"eligibility": {"in_range": 100, "eligible": 60,
            "excluded_exclusive": {"purge": 0, "masked": 30, "y_nan": 5, "feature_nan": 5}},
            "nan_reasons": ["persistence_raw/kyiv_city: within-unit AUC NaN (no unit with >= 10 pos and neg)"]}))
        pd.DataFrame([{"baseline": "model", "bin": 0, "lo": 0.0, "hi": 0.1, "n": 50, "mean_p": 0.05, "mean_y": 0.06}]).to_csv(d / "reliability_bins.csv", index=False)
        pd.DataFrame([{"predictor": "model", "group": "overall", "rows": 60, "mean_pred": 0.1, "mean_obs": 0.12,
                       "pred_minus_obs": -0.02}]).to_csv(d / "calibration_in_the_large.csv", index=False)
        (d / "calibrator.json").write_text(json.dumps({"decision": "none", "ece": 0.01}))
    (r / "official" / "m1_checks.json").write_text(json.dumps({"detected_gaps": [["2026-08-29 05:00", "2026-09-02 13:00"]],
        "over_24h_total": 757, "exactly_30min_total": 38, "zero_duration": 2, "base_rate_2024_avg": 0.1}))
    (r / "official" / "run_meta.json").write_text(json.dumps({"row_counts": {"raw_rows": 299275, "duplicate_rows": 113845,
        "dedup_rows": 185430, "excluded_rows": 1, "final_rows": 185429}, "approved_gaps": [["2026-08-29", "2026-09-03"]]}))
    for v in ("new_regime", "new_regime_all_types"):
        d = r / v
        d.mkdir()
        metrics_csv(d / "metrics.csv", 0.05)
        pd.DataFrame([{"predictor": pr, "group": g, "rows": 10, "mean_pred": 0.1 + 0.01 * k, "mean_obs": 0.2,
                       "pred_minus_obs": -0.1 + 0.01 * k, "roc_auc_within_unit_mean": 0.6, "within_unit_units_used": 5,
                       "within_unit_units_excluded": "", "roc_auc_pooled": 0.8, "low_n": False}
                      for k, pr in enumerate(["model", "recent_rate"]) for g in B.GROUPS]).to_csv(d / "transfer.csv", index=False)
        pd.DataFrame([{"unit": f"[{g}]", "group": g, "exposed_hours": 700, "onsets": 9, "active_hours": 70,
                       "onsets_per_30d": 9.26, "share_under_alert": 0.1, "window": w}
                      for g in B.GROUPS for w in ("official_2026-07-27_08-29", "api_2026-09-13_10-12")]).to_csv(d / "before_after.csv", index=False)
        pd.DataFrame([{"baseline": "model", "bin": 0, "lo": 0, "hi": 0.1, "n": 5, "mean_p": 0.05, "mean_y": 0.1}]).to_csv(d / "reliability_bins.csv", index=False)
        (d / "run_meta.json").write_text(json.dumps({"history_start": "2026-09-12 17:00:43+00:00", "coverage_end": "2026-10-12 16:45:36+00:00",
            "scored_range": ["2026-09-20 18:00", "2026-10-12 15:00"], "eligibility": {"eligible": 5000},
            "loader": {"alerts": 16448, "open_alerts": 32}, "alert_counts_in_coverage": {}, "dump": "x", "api_alert_types": ["air_raid"]}))
    units = list(regions.UNITS)
    pd.DataFrame([{"unit": u, "group": regions.UNITS[u]["group"], "scored_hours": 50 + i, "alert_starts": i,
                   "base_rate": i / (50 + i), "brier_model": 0.05, "brier_recent_rate": 0.06,
                   "brier_skill_vs_recent": round(0.01 * (i - 12), 4), "roc_auc_within_unit": (None if i % 5 == 0 else 0.6),
                   "low_n": i % 5 == 0 or 50 + i < 100,
                   "low_n_reason": "fewer than 100 scored hours" if 50 + i < 100 else ""} for i, u in enumerate(units)]
                 ).to_csv(r / "official" / "metrics_by_unit.csv", index=False)
    t = pd.date_range(pd.Timestamp("2026-07-27", tz="UTC"), pd.Timestamp("2026-09-07", tz="UTC"), freq="h", inclusive="left")
    tp = []
    for i, u in enumerate(units):
        for k, x in enumerate(t):
            st = ["scored", "under_alert", "gap_or_missing", "feature_missing"][(k + i) % 4]
            tp.append({"unit": u, "t": x, "group": regions.UNITS[u]["group"], "status": st,
                       "y": float(k % 7 == 0) if st == "scored" else None,
                       "p_model": 0.1 + 0.001 * i if st == "scored" else None,
                       "p_recent_rate": 0.12 if st == "scored" else None})
    pd.DataFrame(tp).to_csv(r / "official" / "test_predictions.csv", index=False)
    pd.DataFrame([{"unit": "kyiv_city", "onset": "2026-07-27 05:00:00+00:00"},
                  {"unit": "kyiv_city", "onset": "2026-07-28 10:30:00+00:00"},
                  {"unit": "kyivska", "onset": "2026-08-01 23:59:00+00:00"}]).to_csv(r / "official" / "test_onsets.csv", index=False)
    imp = r / "improve"
    imp.mkdir()
    vrows = []
    for i, v in enumerate(["V0_frozen_headline", "V1_weekly_refit", "V2_offset", "V3_offset_plus",
                           "V4_weekly_refit_offset_plus", "V5_blend", "recent_rate"]):
        for j, g in enumerate(B.GROUPS):
            vrows.append({"baseline": v, "group": g, "rows": 900 + j, "brier": 0.08 + 0.001 * i + 0.0001 * j,
                          "brier_skill_vs_recent": 0.0 if v == "recent_rate" else 0.01 * (i - 2) + 0.001 * j,
                          "roc_auc_within_unit_mean": 0.6 + 0.01 * i, "low_n": j == 2})
    pd.DataFrame(vrows).to_csv(imp / "variants_test_posthoc.csv", index=False)
    brows = []
    for k, (blk, ok) in enumerate((("A", False), ("B", False), ("C", True))):
        brows.append({"block": blk, "fold_cut": "mean", "reference_brier": 0.074 + k * 0.001,
                      "candidate_brier": 0.0735 + k * 0.001, "relative_change": -0.006 + 0.001 * k,
                      "folds_improved": 3 - (k == 1), "accepted": ok})
    pd.DataFrame(brows).to_csv(imp / "feature_blocks.csv", index=False)
    (imp / "validation_selection.json").write_text(json.dumps({"rows": 11160, "best_posthoc_by_validation": "V5",
                                                                "accepted_blocks": ["C"], "brier": {}}))
    (imp / "blend_weight.json").write_text(json.dumps({"w": 0.6, "grid": {}}))
    pd.DataFrame([{"variant": v, "cut": c, "rows": (0 if c == "2026-08-31" else 100)}
                  for v in ("V1_weekly_refit", "V4_weekly_refit_offset_plus")
                  for c in ("2026-07-27", "2026-08-03", "2026-08-10", "2026-08-17", "2026-08-24", "2026-08-31")]
                 ).to_csv(imp / "weekly_refit.csv", index=False)
    (r / "final_test_access.json").write_text("{}")
    (r / "leakage_evidence.json").write_text(json.dumps([{"check": "c", "test": "tests/t.py::x", "result": "PASS", "pytest": "1 passed"}]))
    return r


def test_every_value_comes_from_its_exact_source_key(tmp_path):
    r = fixture_reports(tmp_path)
    p = B.build_payload(r)
    for key, run in B.RUNS.items():
        df = pd.read_csv(r / run / "metrics.csv")
        for _, row in df.iterrows():
            cell = p["horizons"][key]["final"][row["baseline"]][row["group"]]
            for m in ("brier", "brier_skill_vs_recent", "roc_auc_pooled", "pr_auc", "rows", "base_rate"):
                assert cell[m] == row[m], (key, row["baseline"], row["group"], m)
    assert p["horizons"]["h1"]["final"]["persistence_raw"]["kyiv_city"]["roc_auc_within_unit_mean"] is None   # NaN -> null
    assert "persistence_raw/kyiv_city" in p["horizons"]["h1"]["final_reasons"]


@pytest.mark.parametrize("swap", ["predictors", "groups", "horizons", "metrics"])
def test_swap_mutations_change_the_output(tmp_path, swap):
    r = fixture_reports(tmp_path)
    before = B.build_payload(r)
    f1, f3 = r / "official" / "metrics.csv", r / "official_h3" / "metrics.csv"
    df = pd.read_csv(f1)
    if swap == "predictors":
        df["baseline"] = df["baseline"].replace({"model": "climatology", "climatology": "model"})
        df.to_csv(f1, index=False)
    elif swap == "groups":
        df["group"] = df["group"].replace({"rear": "frontline", "frontline": "rear"})
        df.to_csv(f1, index=False)
    elif swap == "horizons":
        tmp = f1.read_text(); f1.write_text(f3.read_text()); f3.write_text(tmp)
    else:
        df = df.rename(columns={"brier": "pr_auc", "pr_auc": "brier"})
        df.to_csv(f1, index=False)
    after = B.build_payload(r)
    assert after["horizons"]["h1"]["final"]["model"]["rear"] != before["horizons"]["h1"]["final"]["model"]["rear"]
    blocks_a, blocks_b = B.generated_blocks(before), B.generated_blocks(after)
    assert blocks_a["final_h1"] != blocks_b["final_h1"]


def parse_md_table(block):
    lines = [l for l in block.splitlines() if l.startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    return [dict(zip(head, [c.strip() for c in l.strip("|").split("|")])) for l in lines[2:]]


def test_readme_cells_verified_independently(tmp_path):
    r = fixture_reports(tmp_path)
    p = B.build_payload(r)
    blocks = B.generated_blocks(p)
    inv_names = {v: k for k, v in B.NAMES.items()}
    inv_groups = {v: k for k, v in B.GROUP_NAMES.items()}
    src = pd.read_csv(r / "official" / "metrics.csv").set_index(["baseline", "group"])
    for row in parse_md_table(blocks["final_h1"]):
        pred, grp = inv_names[row["Predictor"]], inv_groups[row["Group"]]
        s = src.loc[(pred, grp)]
        assert row["Brier"] == f"{s['brier']:.4f}"
        assert row["Brier skill vs recent rate"] == f"{s['brier_skill_vs_recent']:.4f}"
        assert row["ROC-AUC pooled"] == f"{s['roc_auc_pooled']:.4f}"
        assert row["Rows"] == f"{int(s['rows']):,}"
        wu = s["roc_auc_within_unit_mean"]
        assert row["ROC-AUC within unit"] == ("n/a" if pd.isna(wu) else f"{wu:.4f}")


def test_readme_blocks_regenerate_exactly(tmp_path):
    r = fixture_reports(tmp_path)
    readme = tmp_path / "README.md"
    shutil.copy(ROOT / "README.md", readme)
    blocks = B.generated_blocks(B.build_payload(r))
    t1 = B.write_readme_blocks(readme, blocks)
    t2 = B.write_readme_blocks(readme, blocks)
    assert t1 == t2


UNITS_AFTER = r"\s*(?:-?hours?|-?h\b|-?d\b|-?days?|-?weeks?|oblasts?|units|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"


def hand_written_numbers(text):
    """Number tokens in hand-written README text that are not rule constants/dates by CONTEXT (M5 plan §8)."""
    text = re.sub(r"<!-- GENERATED:(\w+) START -->.*?<!-- GENERATED:\1 END -->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\(https?://[^)]*\)|<https?://[^>]*>|`[^`]*`|\]\([^)]*\)", "", text)
    text = re.sub(r"y\(t\) = 1|D-\d{3}|\bM[1-6][ab]?\b|§\d+|\bH = \d+|\bt \+ H|\b(?:19|20)\d\d\b", "", text)
    bad = []
    for m in re.finditer(r"(?<![\w.-])\d[\d,.]*%?", text):
        tok = m.group(0).rstrip(".,")
        after = text[m.end():m.end() + 16]
        if re.match(r"\s*(?:units|oblasts?)\b", after):          # only the fixed unit counts are rule constants
            if tok in {"24", "23", "15", "8"}:
                continue
        elif re.match(UNITS_AFTER, after):
            continue
        bad.append(tok)
    return bad


def test_no_result_numbers_in_hand_written_readme():
    assert hand_written_numbers((ROOT / "README.md").read_text()) == []


@pytest.mark.parametrize("phrase", ["0 units used", "1 positive", "7 positives", "9 rows", "Brier 0.0782", "38%"])
def test_prose_number_mutations_are_caught(phrase):
    text = (ROOT / "README.md").read_text() + f"\nThe model had {phrase} in Kyiv City.\n"
    assert hand_written_numbers(text) != []


def test_missing_report_file_raises(tmp_path):
    r = fixture_reports(tmp_path)
    (r / "official_h3" / "metrics.csv").unlink()
    with pytest.raises(B.SiteError):
        B.build_payload(r)
    r2 = fixture_reports(tmp_path / "b")
    (r2 / "final_test_access.json").unlink()
    with pytest.raises(B.SiteError):
        B.build_payload(r2)


def test_groups_follow_regions():
    p = B.build_payload(fixture_reports(Path(__import__("tempfile").mkdtemp())))
    assert p["groups"]["kyiv_city"] == ["kyiv_city"]
    assert "kyivska" in p["groups"]["rear"] and "kyivska" not in p["groups"]["kyiv_city"]
    assert set(p["groups"]["frontline"]) == {"chernihivska", "sumska", "kharkivska", "donetska", "dnipropetrovska",
                                            "zaporizka", "khersonska", "mykolaivska"}
    assert len(p["groups"]["rear"]) == 15


def test_site_embeds_data_and_has_no_placeholder(tmp_path):
    r = fixture_reports(tmp_path)
    out = B.build_site(B.build_payload(r), ROOT / "site_src" / "template.html", tmp_path / "site" / "index.html")
    html = out.read_text()
    assert "/*__DATA__*/null" not in html and '"horizons"' in html
    # M8: exactly one network request, same-origin, to the live forecast endpoint; nothing external is loaded
    assert html.count("fetch(") == 1 and "fetch(LIVE_URL" in html and 'const LIVE_URL = "/api/forecast"' in html
    assert re.search(r'<(script|link|img)[^>]+(src|href)="https?://', html) is None


def test_streamlit_loader(tmp_path):
    from app import streamlit_app as S
    r = fixture_reports(tmp_path)
    assert S.missing_files(r)  # fixture lacks pngs -> reported, not hidden
    for p in S.missing_files(r):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x") if p.suffix == ".png" else p.write_text("{}")
    assert S.missing_files(r) == []


# ---------------- M5 harness review: every block verified, committed README fresh, robustness ----------------

def _check_metrics_block(block, src_csv):
    inv_names = {v: k for k, v in B.NAMES.items()}
    inv_groups = {v: k for k, v in B.GROUP_NAMES.items()}
    src = pd.read_csv(src_csv).set_index(["baseline", "group"])
    rows = parse_md_table(block)
    assert rows
    for row in rows:
        s = src.loc[(inv_names[row["Predictor"]], inv_groups[row["Group"]])]
        exp = {"Brier": f"{s['brier']:.4f}", "Brier skill vs recent rate": f"{s['brier_skill_vs_recent']:.4f}",
               "ROC-AUC pooled": f"{s['roc_auc_pooled']:.4f}", "PR-AUC": f"{s['pr_auc']:.4f}",
               "Rows": f"{int(s['rows']):,}", "Base rate": f"{s['base_rate']:.4f}",
               "Low-n": "yes" if bool(s["low_n"]) else "no",
               "ROC-AUC within unit": "n/a" if pd.isna(s["roc_auc_within_unit_mean"]) else f"{s['roc_auc_within_unit_mean']:.4f}"}
        for k, v in exp.items():
            assert row[k] == v, (row["Predictor"], row["Group"], k)


def _check_all_blocks(r, blocks):
    _check_metrics_block(blocks["final_h1"], r / "official" / "metrics.csv")
    _check_metrics_block(blocks["final_h3"], r / "official_h3" / "metrics.csv")
    _check_metrics_block(blocks["validation_h1"], r / "official" / "metrics_validation.csv")
    cov = {row["Horizon"]: row for row in parse_md_table(blocks["coverage"])}
    for h, run in (("H = 1", "official"), ("H = 3", "official_h3")):
        e = json.loads((r / run / "final_test_checks.json").read_text())["eligibility"]
        assert cov[h]["Test rows in range"] == f"{e['in_range']:,}" and cov[h]["Scored"] == f"{e['eligible']:,}"
        for col, k in (("Purged", "purge"), ("Under alert / gap-masked", "masked"), ("Label unknown", "y_nan"),
                       ("Feature missing", "feature_nan")):
            assert cov[h][col] == f"{e['excluded_exclusive'][k]:,}", (h, col)
    inv_groups = {v: k for k, v in B.GROUP_NAMES.items()}
    inv_names = {v: k for k, v in B.NAMES.items()}
    variants = {"air-raid only": "new_regime", "all types": "new_regime_all_types"}
    for row in parse_md_table(blocks["transfer"]):
        src = pd.read_csv(r / variants[row["API variant"]] / "transfer.csv").set_index(["predictor", "group"])
        s = src.loc[(inv_names[row["Predictor"]], inv_groups[row["Group"]])]
        assert row["Mean predicted"] == f"{s['mean_pred']:.4f}" and row["Mean observed"] == f"{s['mean_obs']:.4f}"
        assert row["Predicted − observed"] == f"{s['pred_minus_obs']:.4f}"


def test_every_readme_block_verified_independently(tmp_path):
    r = fixture_reports(tmp_path)
    _check_all_blocks(r, B.generated_blocks(B.build_payload(r)))


@pytest.mark.parametrize("mut", ["swap_pred_obs", "swap_cov", "invert_low_n", "val_from_h3"])
def test_block_mutations_are_caught(tmp_path, mut):
    r = fixture_reports(tmp_path)
    blocks = B.generated_blocks(B.build_payload(r))
    if mut == "swap_pred_obs":
        blocks["transfer"] = blocks["transfer"].replace("| Mean predicted | Mean observed |", "| Mean observed | Mean predicted |")
    elif mut == "swap_cov":
        blocks["coverage"] = blocks["coverage"].replace("| Under alert / gap-masked | Label unknown |", "| Label unknown | Under alert / gap-masked |")
    elif mut == "invert_low_n":
        blocks["final_h1"] = blocks["final_h1"].replace("| yes |", "| tmp |").replace("| no |", "| yes |").replace("| tmp |", "| no |")
    else:
        blocks["validation_h1"] = B.results_table(B.build_payload(r)["horizons"]["h3"]["validation"], "x")
    with pytest.raises((AssertionError, KeyError)):
        _check_all_blocks(r, blocks)


def test_committed_readme_matches_real_reports():
    reports = ROOT / "reports"
    if not (reports / "final_test_access.json").exists():
        pytest.skip("final test not scored in this checkout")
    payload = B.build_payload(reports)
    blocks = B.generated_blocks(payload)
    text = (ROOT / "README.md").read_text()
    assert B.render_readme(text, blocks) == text           # a hand-edited generated number fails here
    _check_all_blocks(reports, blocks)


def test_duplicate_or_missing_rows_raise(tmp_path):
    r = fixture_reports(tmp_path)
    f = r / "official" / "metrics.csv"
    df = pd.read_csv(f)
    pd.concat([df, df.iloc[[0]].assign(brier_skill_vs_recent=0.4)]).to_csv(f, index=False)
    with pytest.raises(B.SiteError):
        B.build_payload(r)
    r2 = fixture_reports(tmp_path / "b")
    t = r2 / "new_regime" / "transfer.csv"
    pd.read_csv(t).iloc[0:0].to_csv(t, index=False)
    with pytest.raises(B.SiteError):
        B.build_payload(r2)


def test_build_is_atomic(tmp_path):
    r = fixture_reports(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text((ROOT / "README.md").read_text().replace("<!-- GENERATED:coverage START -->", ""))
    out = tmp_path / "site" / "index.html"
    with pytest.raises(B.SiteError):
        B.main(["--reports", str(r), "--out", str(out), "--readme", str(readme)])
    assert not out.exists()


def test_page_makes_no_external_request():
    # M8: the only request is the same-origin live forecast (relative URL); no external scripts, styles or fetches
    html = (ROOT / "site_src" / "template.html").read_text()
    assert not re.search(r"""(src|href)=["']https?://""", html) and "@import" not in html
    assert re.findall(r"fetch\(([^,)]+)", html) == ["LIVE_URL"] and 'const LIVE_URL = "/api/forecast"' in html


# ---------------- M5 reviewer: headline + every remaining block verified from source keys ----------------

def _verify_rest(r, blocks):
    src = pd.read_csv(r / "official" / "metrics.csv").set_index(["baseline", "group"])
    s = src.loc[("model", "overall"), "brier_skill_vs_recent"]
    want = "does NOT beat" if s <= 0 else "the model beats"
    assert f"**{s:.4f}**" in blocks["headline"] and want in blocks["headline"]
    meta = json.loads((r / "official" / "run_meta.json").read_text())["row_counts"]
    facts = {row["Fact (official file)"]: row["Value"] for row in parse_md_table(blocks["data_facts"])}
    assert facts["Raw rows"] == f"{meta['raw_rows']:,}" and facts["Exact duplicate rows removed"] == f"{meta['duplicate_rows']:,}"
    assert facts["Luhanska rows excluded"] == f"{meta['excluded_rows']:,}"
    m1 = json.loads((r / "official" / "m1_checks.json").read_text())
    assert facts["Alerts lasting > 24h (before the test)"] == f"{m1['over_24h_total']:,}"
    variants = {"air-raid only": "new_regime", "all types": "new_regime_all_types"}
    inv_groups = {v: k for k, v in B.GROUP_NAMES.items()}
    inv_names = {v: k for k, v in B.NAMES.items()}
    for row in parse_md_table(blocks["before_after"]):
        v = "new_regime" if row["API variant"] in ("official", "air-raid only") else "new_regime_all_types"
        ba = pd.read_csv(r / v / "before_after.csv").set_index(["unit", "window"])
        sr = ba.loc[(f"[{inv_groups[row['Group']]}]", row["Window"])]
        assert row["Onsets per 30 days"] == f"{sr['onsets_per_30d']:.1f}"
        assert row["Share of time under alert"] == f"{sr['share_under_alert']:.3f}"
    for row in parse_md_table(blocks["transfer"]):
        tsrc = pd.read_csv(r / variants[row["API variant"]] / "transfer.csv").set_index(["predictor", "group"])
        t = tsrc.loc[(inv_names[row["Predictor"]], inv_groups[row["Group"]])]
        assert row["Within-unit AUC"] == f"{t['roc_auc_within_unit_mean']:.4f}"
    for row in parse_md_table(blocks["new_regime_metrics"]):
        msrc = pd.read_csv(r / variants[row["API variant"]] / "metrics.csv").set_index(["baseline", "group"])
        c = msrc.loc[(inv_names[row["Predictor"]], inv_groups[row["Group"]])]
        assert row["Brier skill vs recent rate"] == f"{c['brier_skill_vs_recent']:.4f}" and row["Brier"] == f"{c['brier']:.4f}"
    for row in parse_md_table(blocks["api_facts"]):
        meta_v = json.loads((r / variants[row["API variant"].replace("air-raid alerts only", "air-raid only").replace("all alert types", "all types")] / "run_meta.json").read_text())
        assert row["Alerts kept"] == f"{meta_v['loader']['alerts']:,}" and row["Open alerts kept"] == f"{meta_v['loader']['open_alerts']:,}"


def test_headline_and_remaining_blocks_verified(tmp_path):
    r = fixture_reports(tmp_path)
    _verify_rest(r, B.generated_blocks(B.build_payload(r)))
    real = ROOT / "reports"
    if (real / "final_test_access.json").exists():
        _verify_rest(real, B.generated_blocks(B.build_payload(real)))


@pytest.mark.parametrize("mut", ["flip_verdict", "swap_ba_cols", "swap_variant_labels", "pooled_for_within"])
def test_remaining_block_mutations_are_caught(tmp_path, mut):
    r = fixture_reports(tmp_path)
    df = pd.read_csv(r / "official" / "metrics.csv")
    df.loc[(df.baseline == "model") & (df.group == "overall"), "brier_skill_vs_recent"] = -0.05
    df.to_csv(r / "official" / "metrics.csv", index=False)
    ba = pd.read_csv(r / "new_regime_all_types" / "before_after.csv")
    ba["onsets_per_30d"] = ba["onsets_per_30d"] + 50
    ba.to_csv(r / "new_regime_all_types" / "before_after.csv", index=False)
    blocks = B.generated_blocks(B.build_payload(r))
    if mut == "flip_verdict":
        blocks["headline"] = blocks["headline"].replace("does NOT beat", "the model beats")
    elif mut == "swap_ba_cols":
        blocks["before_after"] = blocks["before_after"].replace("| Onsets per 30 days | Share of time under alert |",
                                                                "| Share of time under alert | Onsets per 30 days |")
    elif mut == "swap_variant_labels":
        blocks["before_after"] = blocks["before_after"].replace("| all types |", "| tmp |").replace("| air-raid only |", "| all types |").replace("| tmp |", "| air-raid only |")
    else:
        blocks["transfer"] = blocks["transfer"].replace("| 0.6000 |", "| 0.8000 |")
    with pytest.raises((AssertionError, KeyError)):
        _verify_rest(r, blocks)


def test_page_verdict_reads_the_model_skill():
    html = (ROOT / "site_src" / "template.html").read_text()
    assert "s = m.brier_skill_vs_recent" in html and "h1.final.model.overall" in html
    assert '(s > 0 ? "yes" : "no")' in html and 'state === "na"' in html


@pytest.mark.parametrize("skill,gap,fails", [(0.01, -0.03, True), (0.01, -0.01, False), (-0.01, -0.01, True)])
def test_transfer_rule_branches(tmp_path, skill, gap, fails):
    r = fixture_reports(tmp_path)
    for v in ("new_regime", "new_regime_all_types"):
        m = pd.read_csv(r / v / "metrics.csv")
        m.loc[(m.baseline == "model") & (m.group == "overall"), "brier_skill_vs_recent"] = skill
        m.to_csv(r / v / "metrics.csv", index=False)
        t = pd.read_csv(r / v / "transfer.csv")
        t.loc[(t.predictor == "model") & (t.group == "overall"), "pred_minus_obs"] = gap
        t.to_csv(r / v / "transfer.csv", index=False)
    text = B.transfer_outcome(B.build_payload(r))
    assert ("NOT good enough" in text) == fails and "provisional, set after these numbers were seen" in text


def test_page_verdict_label_mapping():
    html = (ROOT / "site_src" / "template.html").read_text()
    assert 'const yes = state === "yes";' in html
    assert '${yes ? "Beats the recent rate" : "Does not beat the recent rate overall"}' in html


# ---------------- M5b public layer ----------------

def test_by_unit_and_timeline_traced_to_sources(tmp_path):
    r = fixture_reports(tmp_path)
    p = B.build_payload(r)
    mu = pd.read_csv(r / "official" / "metrics_by_unit.csv").set_index("unit")
    assert set(p["by_unit"]) == set(regions.UNITS)
    for u, d in p["by_unit"].items():
        assert d["scored_hours"] == mu.loc[u, "scored_hours"] and d["brier_skill_vs_recent"] == mu.loc[u, "brier_skill_vs_recent"]
        assert (d["roc_auc_within_unit"] is None) == pd.isna(mu.loc[u, "roc_auc_within_unit"])
    tp = pd.read_csv(r / "official" / "test_predictions.csv", float_precision="round_trip")
    tp["t"] = pd.to_datetime(tp["t"], utc=True)
    for u in ("kyiv_city", "kyivska", "lvivska"):
        g = tp[tp.unit == u].sort_values("t")
        tl = p["timeline"]["units"][u]
        assert tl["status"] == [B.STATUS_CODE[x] for x in g["status"]]
        assert [None if pd.isna(v) else v for v in g["p_model"]] == tl["p_model"]
    assert p["timeline"]["units"]["kyiv_city"]["onsets_min"] == [300.0, 24 * 60 + 630.0]
    assert p["timeline"]["units"]["kyivska"]["onsets_min"] == [5 * 24 * 60 + 23 * 60 + 59.0]
    assert p["timeline"]["units"]["lvivska"]["onsets_min"] == []


@pytest.mark.parametrize("skill,word", [(0.05, "more accurate than"), (-0.05, "less accurate than"),
                                        (0.0, "as accurate as"), (None, "cannot be compared with")])
def test_plain_sentence_follows_sign(tmp_path, skill, word):
    r = fixture_reports(tmp_path)
    m = pd.read_csv(r / "official" / "metrics.csv")
    m.loc[(m.baseline == "model") & (m.group == "overall"), "brier_skill_vs_recent"] = skill
    m.to_csv(r / "official" / "metrics.csv", index=False)
    first = B.build_payload(r)["plain"][0]
    assert word in first["text"] and f"{int(m.loc[(m.baseline == 'model') & (m.group == 'overall'), 'rows'].iloc[0]):,}" in first["text"]
    if skill not in (None, 0.0):
        assert f"{abs(100 * skill):.1f}%" in first["text"]


def test_plain_low_n_reason_shown(tmp_path):
    r = fixture_reports(tmp_path)
    p = B.build_payload(r)
    front = next(x for x in p["plain"] if x["key"] == "frontline")
    m = pd.read_csv(r / "official" / "metrics.csv").set_index(["baseline", "group"])
    if m.loc[("model", "frontline"), "rows"] < 100 or str(m.loc[("model", "frontline"), "within_unit_units_excluded"]) not in ("", "nan"):
        assert "treat with caution" in front["text"] and front["low_n_reason"]


def test_by_unit_must_have_24_units(tmp_path):
    r = fixture_reports(tmp_path)
    f = r / "official" / "metrics_by_unit.csv"
    pd.read_csv(f).iloc[:-1].to_csv(f, index=False)
    with pytest.raises(B.SiteError):
        B.build_payload(r)


# ---------------- M7 post-hoc blocks ----------------

def _verify_improve(r, blocks):
    inv = {v: k for k, v in B.IMPROVE_NAMES.items()}
    inv_groups = {v: k for k, v in B.GROUP_NAMES.items()}
    src = pd.read_csv(r / "improve" / "variants_test_posthoc.csv", float_precision="round_trip").set_index(["baseline", "group"])
    rows = parse_md_table(blocks["improve_variants"])
    assert len(rows) == len(src)
    for row in rows:
        c = src.loc[(inv[row["Variant (post-hoc)"]], inv_groups[row["Group"]])]
        assert row["Brier"] == f"{c['brier']:.4f}" and row["Brier skill vs recent rate"] == f"{c['brier_skill_vs_recent']:.4f}"
        assert row["Within-unit AUC"] == f"{c['roc_auc_within_unit_mean']:.4f}" and row["Rows"] == f"{int(c['rows']):,}"
    fb = pd.read_csv(r / "improve" / "feature_blocks.csv")
    fb = fb[fb.fold_cut == "mean"].set_index("block")
    inv_b = {v: k for k, v in B.BLOCK_NAMES.items()}
    for row in parse_md_table(blocks["improve_blocks"]):
        c = fb.loc[inv_b[row["Feature block"]]]
        assert row["Relative change"] == f"{c['relative_change']:.4f}" and row["Accepted"] == ("yes" if c["accepted"] else "no")
    sel = json.loads((r / "improve" / "validation_selection.json").read_text())
    want = {"V2": "V2 offset", "V3": "V3 offset + accepted blocks", "V5": "V5 blend"}[sel["best_posthoc_by_validation"]]
    assert f"**{want}**" in blocks["improve_selection"]


def test_improve_blocks_verified(tmp_path):
    r = fixture_reports(tmp_path)
    _verify_improve(r, B.generated_blocks(B.build_payload(r)))
    real = ROOT / "reports"
    if (real / "improve" / "variants_test_posthoc.csv").exists():
        _verify_improve(real, B.generated_blocks(B.build_payload(real)))


@pytest.mark.parametrize("mut", ["swap_variant", "flip_accept", "wrong_selection"])
def test_improve_mutations_caught(tmp_path, mut):
    r = fixture_reports(tmp_path)
    blocks = B.generated_blocks(B.build_payload(r))
    if mut == "swap_variant":
        blocks["improve_variants"] = blocks["improve_variants"].replace("V2 recent-rate offset", "TMP").replace(
            "V4 weekly refit + offset", "V2 recent-rate offset").replace("TMP", "V4 weekly refit + offset")
    elif mut == "flip_accept":
        blocks["improve_blocks"] = blocks["improve_blocks"].replace("| yes |", "| tmp |").replace("| no |", "| yes |").replace("| tmp |", "| no |")
    else:
        blocks["improve_selection"] = blocks["improve_selection"].replace("V5 blend", "V2 offset")
    with pytest.raises((AssertionError, KeyError)):
        _verify_improve(r, blocks)
