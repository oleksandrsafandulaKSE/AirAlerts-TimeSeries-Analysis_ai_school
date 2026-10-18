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
    (r / "final_test_access.json").write_text(json.dumps({"first_access_utc": "2026-10-13T00:16:53+00:00"}))
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
    # M8 + M11: only same-origin requests to the three live endpoints; nothing external is loaded
    assert sorted(re.findall(r"fetch\(([^,)]+)", html)) == ["CHECK_URL", "HISTORY_URL", "LIVE_URL"]
    assert 'const LIVE_URL = "/api/forecast"' in html and 'HISTORY_URL = "/api/history"' in html and 'CHECK_URL = "/api/check"' in html
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
    # M8 + M11: the only requests are the same-origin live endpoints (relative URLs); no external scripts, styles or fetches
    html = (ROOT / "site_src" / "template.html").read_text()
    assert not re.search(r"""(src|href)=["']https?://""", html) and "@import" not in html
    assert sorted(re.findall(r"fetch\(([^,)]+)", html)) == ["CHECK_URL", "HISTORY_URL", "LIVE_URL"]
    assert 'const LIVE_URL = "/api/forecast"' in html and 'HISTORY_URL = "/api/history"' in html and 'CHECK_URL = "/api/check"' in html


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


# ---------------- M11 §C: replay, gap pins, M10 blocks, exploratory labels, token ----------------
import os  # noqa: E402
import subprocess  # noqa: E402

REAL = ROOT / "reports"
HEADLINE_BSS = -0.010064344018558602
needs_real = pytest.mark.skipif(not (REAL / "official" / "test_predictions.csv").exists(),
                                reason="final test not scored in this checkout")


def embedded_payload(html):
    m = re.search(r'<script id="payload" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))


def replay_js(html, payload, prefixes, tmp_path):
    """Run the page's own replayStats (between the <replay-stats> markers of the BUILT page) under node."""
    m = re.search(r"// <replay-stats>[^\n]*\n(.*?)// </replay-stats>", html, re.S)
    assert m, "replayStats markers missing from the page"
    f = tmp_path / "timeline.json"
    f.write_text(json.dumps(payload["timeline"]))
    js = m.group(1) + (f"\nconst T = JSON.parse(require('fs').readFileSync({json.dumps(str(f))}, 'utf8'));\n"
                       f"console.log(JSON.stringify({json.dumps(prefixes)}.map(n => replayStats(T, n))));")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def pandas_prefix(tp, start, n):
    s = tp[(tp["status"] == "scored") & (tp["t"] < start + pd.Timedelta(hours=n))]
    return len(s), 1 - ((s["p_model"] - s["y"]) ** 2).sum() / ((s["p_recent_rate"] - s["y"]) ** 2).sum()


@pytest.fixture(scope="module")
def real_build():
    payload = B.build_payload(REAL)
    html = B.render_site(payload, ROOT / "site_src" / "template.html")
    tp = pd.read_csv(REAL / "official" / "test_predictions.csv", float_precision="round_trip")
    tp["t"] = pd.to_datetime(tp["t"], utc=True)
    return payload, html, tp


@needs_real
def test_timeline_is_1008_hours_by_24_units_with_status_codes(real_build):
    payload, html, tp = real_build
    T = embedded_payload(html)["timeline"]
    assert T["hours"] == 1008 and len(T["units"]) == 24 and set(T["units"]) == set(regions.UNITS)
    assert T["status_names"] == list(B.STATUS_CODE)
    for u, U in T["units"].items():
        assert len(U["status"]) == len(U["p_model"]) == len(U["p_recent"]) == len(U["y"]) == 1008
        assert set(U["status"]) <= set(B.STATUS_CODE.values())
        for k, s in enumerate(U["status"]):                     # y and both forecasts exist exactly on scored rows
            assert (s == 0) == (U["y"][k] is not None) == (U["p_model"][k] is not None)


@needs_real
def test_replay_prefixes_equal_pandas_and_end_equals_headline(real_build, tmp_path):
    payload, html, tp = real_build
    page = embedded_payload(html)
    start = pd.Timestamp(page["timeline"]["start"])
    prefixes = [24, 336, 700, 1008]
    got = replay_js(html, page, prefixes, tmp_path)
    for n, g in zip(prefixes, got):
        rows, bss = pandas_prefix(tp, start, n)
        assert g["rows"] == rows
        assert abs(g["bss"] - bss) <= 1e-12, (n, g["bss"], bss)
    m = pd.read_csv(REAL / "official" / "metrics.csv", float_precision="round_trip").set_index(["baseline", "group"])
    assert abs(got[-1]["bss"] - m.loc[("model", "overall"), "brier_skill_vs_recent"]) <= 1e-12
    assert abs(got[-1]["bss"] - HEADLINE_BSS) <= 1e-12
    assert got[-1]["rows"] == 13116 and page["replay"]["headline_bss"] == m.loc[("model", "overall"), "brier_skill_vs_recent"]
    assert page["replay"]["scored_once_utc"].startswith("2026-10-13")


@needs_real
@pytest.mark.parametrize("mut", ["shuffle_hours", "misalign_units"])
def test_replay_prefix_check_catches_a_broken_payload(real_build, tmp_path, mut):
    payload, html, tp = real_build
    page = embedded_payload(html)
    U = page["timeline"]["units"]
    if mut == "shuffle_hours":                                   # p_model moved to other scored hours of the same unit
        for u in U:
            idx = [k for k, s in enumerate(U[u]["status"]) if s == 0]
            vals = [U[u]["p_model"][k] for k in idx]
            for k, v in zip(idx, vals[::-1]):
                U[u]["p_model"][k] = v
    else:                                                        # Kyiv City's forecasts paired with Kyivska's outcomes
        a, b = U["kyiv_city"], U["kyivska"]
        for k in range(1008):
            if a["status"][k] == 0 and b["status"][k] == 0:
                a["p_model"][k], b["p_model"][k] = b["p_model"][k], a["p_model"][k]
    start = pd.Timestamp(page["timeline"]["start"])
    prefixes = [24, 336, 700]
    got = replay_js(html, page, prefixes, tmp_path)
    assert any(abs(g["bss"] - pandas_prefix(tp, start, n)[1]) > 1e-12 for n, g in zip(prefixes, got))


@needs_real
def test_gap_pins_and_replay_status_counts(real_build):
    payload, html, tp = real_build
    assert tp["status"].value_counts().to_dict() == {"scored": 13116, "under_alert": 6397, "gap_or_missing": 3480,
                                                       "feature_missing": 1199}
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    gap = tp[(tp["t"] >= ts("2026-08-28 23:00")) & (tp["t"] < ts("2026-09-04 00:00"))]
    assert len(gap) == 24 * (24 * 5 + 25) and set(gap["status"]) == {"gap_or_missing"}
    after = tp[(tp["t"] >= ts("2026-09-04 00:00")) & (tp["t"] < ts("2026-09-07 00:00"))]
    assert len(after) == 24 * 72 and set(after["status"]) <= {"feature_missing", "under_alert"}
    assert tp.loc[tp["status"] == "scored", "t"].max() <= ts("2026-08-28 22:00")
    T = embedded_payload(html)["timeline"]
    inv = {v: k for k, v in B.STATUS_CODE.items()}
    counts = {}
    for U in T["units"].values():
        for s in U["status"]:
            counts[inv[s]] = counts.get(inv[s], 0) + 1
    assert counts == tp["status"].value_counts().to_dict()
    gap_h = int((ts("2026-08-28 23:00") - pd.Timestamp(T["start"])) / pd.Timedelta(hours=1))
    for U in T["units"].values():
        assert set(U["status"][gap_h:gap_h + 145]) == {B.STATUS_CODE["gap_or_missing"]}      # 28 Aug 23:00 -> 4 Sep 00:00
        assert 0 not in U["status"][gap_h:]
    kc, kv = T["units"]["kyiv_city"], T["units"]["kyivska"]
    assert kc["status"] != kv["status"] and kc["p_model"] != kv["p_model"] and kc["onsets_min"] != kv["onsets_min"]
    for u, U in (("kyiv_city", kc), ("kyivska", kv)):
        g = tp[tp["unit"] == u].sort_values("t")
        assert U["p_model"] == [None if pd.isna(v) else v for v in g["p_model"]]


def m10_fixture(r):
    d = r / "m10"
    d.mkdir()
    rows = []
    for kind, slices in (("week", ["2026-06-29", "2026-07-06"]), ("day_night", ["day", "night"])):
        for sl in slices:
            for g in B.GROUPS:
                for k, p in enumerate(["V0", "recent_rate", "V2"]):
                    rows.append({"slice_kind": kind, "slice": sl, "group": g, "baseline": p, "rows": 100 + k,
                                 "positives": 10 + k, "base_rate": (10 + k) / (100 + k), "brier": 0.08 + 0.001 * k,
                                 "brier_skill_vs_recent": 0.0 if p == "recent_rate" else 0.0123456789 * (k + 1) * (1 if sl != "night" else -1),
                                 "low_n": g == "kyiv_city"})
    pd.DataFrame(rows).to_csv(d / "stability_validation.csv", index=False)
    pd.DataFrame([{"period": "train", "unit": u, "group": "frontline", "onsets_L0": 10, "onsets_L1": 9, "base_rate_diff": -0.00123}
                  for u in ("[frontline]", "kharkivska")]).to_csv(d / "labels_variant.csv", index=False)
    pd.DataFrame([{"half_life_days": h, "fold_cut": "mean", "brier": 0.07 + i / 1000, "accepted": False}
                  for i, h in enumerate(["inf", "730", "365", "182"])]).to_csv(d / "recency_folds.csv", index=False)
    return d


def test_m10_blocks_present_equal_the_csvs_and_absent_say_not_run_yet(tmp_path, capsys):
    r = fixture_reports(tmp_path)
    p0 = B.build_payload(r)
    for k in B.M10_FILES:
        assert p0["m10"][k]["available"] is False and "not run yet" in p0["m10"][k]["reason"]
    assert "not run yet" in capsys.readouterr().out                 # the reason is printed by the build
    d = m10_fixture(r)
    p = B.build_payload(r)
    st = pd.read_csv(d / "stability_validation.csv", float_precision="round_trip")
    assert p["m10"]["stability"]["available"] and len(p["m10"]["stability"]["rows"]) == len(st)
    for got, want in zip(p["m10"]["stability"]["rows"], st.to_dict(orient="records")):
        assert got == want
    lv = p["m10"]["labels_variant"]
    assert [x["unit"] for x in lv["rows"]] == ["[frontline]"] and lv["rows"][0]["base_rate_diff"] == -0.00123
    assert len(p["m10"]["recency_folds"]["rows"]) == 4
    assert p["m10"]["exposure_folds"]["available"] is False and p["m10"]["stability_posthoc"]["available"] is False
    html = B.render_site(p, ROOT / "site_src" / "template.html")
    assert embedded_payload(html)["m10"] == json.loads(json.dumps(p["m10"]))
    tmpl = (ROOT / "site_src" / "template.html").read_text()
    assert "Not run yet.</b> ${esc(S.reason)}" in tmpl and "Not run yet.</b> ${esc(T.reason)}" in tmpl


@pytest.mark.parametrize("bad", ["missing_column", "empty", "duplicate", "unknown_kind"])
def test_m10_malformed_stability_raises(tmp_path, bad):
    r = fixture_reports(tmp_path)
    d = m10_fixture(r)
    f = d / "stability_validation.csv"
    df = pd.read_csv(f)
    if bad == "missing_column":
        df = df.drop(columns=["brier_skill_vs_recent"])
    elif bad == "empty":
        df = df.iloc[:0]
    elif bad == "duplicate":
        df = pd.concat([df, df.iloc[:1]])
    else:
        df.loc[0, "slice_kind"] = "month"
    df.to_csv(f, index=False)
    with pytest.raises(B.SiteError):
        B.build_payload(r)


def _ids_written_by(tmpl, fn):
    body = re.search(rf"function {fn}\(.*?\n}}\n", tmpl, re.S).group(0)
    return set(re.findall(r'\$\("([\w-]+)"\)', body)) | set(re.findall(r'getElementById\("([\w-]+)"\)', body))


def _section(tmpl, open_tag):
    i = tmpl.index(open_tag)
    tag = "section" if open_tag.startswith("<section") else "div"
    if tag == "section":
        return tmpl[i:tmpl.index("</section>", i)]
    j, depth = i, 0
    for m in re.finditer(r"<(/?)div\b", tmpl[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return tmpl[i:i + m.end()]
    raise AssertionError(open_tag)


OFFICIAL_TABLES = ["tbl", "tbl-units", "tbl-citl", "tbl-tr", "tbl-nrm", "tbl-cov", "tbl-leak", "plain", "map", "tl"]
EXPLORATORY_TAG = "Exploratory · live API data · not part of the study"


def test_every_api_block_carries_the_exploratory_label_and_stays_out_of_official_tables():
    tmpl = (ROOT / "site_src" / "template.html").read_text()
    check = _section(tmpl, '<section class="exploratory" id="live-check">')
    detail = _section(tmpl, '<div class="panel" id="live-detail">')
    assert EXPLORATORY_TAG in check and EXPLORATORY_TAG in detail
    check_ids = _ids_written_by(tmpl, "drawCheck")
    detail_ids = _ids_written_by(tmpl, "drawStrip") | _ids_written_by(tmpl, "drawPattern") | _ids_written_by(tmpl, "drawDetail")
    assert check_ids and detail_ids
    for i in check_ids:
        assert f'id="{i}"' in check, i
    for i in detail_ids:
        assert f'id="{i}"' in detail, i
    for i in OFFICIAL_TABLES:
        assert f'id="{i}"' in tmpl and f'id="{i}"' not in check and f'id="{i}"' not in detail
        assert i not in check_ids | detail_ids
    # the study payload never contains live API data (it is built from reports/ only)
    for i in ("drawCheck", "drawStrip", "drawPattern"):
        assert re.search(rf"function {i}\(\) {{\n  const [^\n]*live\.(check|history)", tmpl), i


def test_replay_and_m10_sections_are_study_sections_with_their_labels():
    tmpl = (ROOT / "site_src" / "template.html").read_text()
    rep = _section(tmpl, '<section id="replay">')
    assert "official data" in rep and EXPLORATORY_TAG not in rep
    assert "Frozen predictions, test scored once on ${D.replay.scored_once_utc.slice(0, 10)}" in tmpl
    assert "Post-hoc · test already seen" in _section(tmpl, '<section id="stability">')


def test_pattern_code_is_inlined_verbatim(tmp_path):
    r = fixture_reports(tmp_path)
    html = B.render_site(B.build_payload(r), ROOT / "site_src" / "template.html")
    src = (ROOT / "netlify" / "live" / "lib" / "pattern.mjs").read_text()
    assert re.sub(r"^export ", "", src, flags=re.M) in html and "/*__PATTERN_JS__*/" not in html
    assert "function recentPattern(onsets, coverage, now, nDays = 14)" in html


def test_neighbours_in_payload_match_both_border_tables(tmp_path):
    p = B.build_payload(fixture_reports(tmp_path))
    live = json.loads((ROOT / "netlify" / "live" / "data" / "regions.json").read_text())["neighbours"]
    assert p["neighbours"] == {u: sorted(regions.NEIGHBOURS[u]) for u in regions.UNITS}
    assert p["neighbours"] == {u: sorted(v) for u, v in live.items()}
    assert "kyivska" in p["neighbours"]["kyiv_city"] and p["neighbours"]["kyiv_city"] == ["kyivska"]


def _env_token():
    env = ROOT / ".env"
    if not env.exists():
        return None
    for line in env.read_text().splitlines():
        k, _, v = line.partition("=")
        if k.strip() == "ALERTS_IN_UA_TOKEN" and v.strip():
            return v.strip().strip('"').strip("'")
    return None


def test_built_site_contains_no_token():
    out = ROOT / "site" / "index.html"
    if not out.exists():
        pytest.skip("site not built")
    html = out.read_text()
    if re.search(r"Bearer\s+[A-Za-z0-9._\-]{8,}", html) or re.search(r"ALERTS_IN_UA_TOKEN\s*[=:]\s*\S{8,}", html):
        pytest.fail("a bearer/token-like string is in the built site")
    for tok in (_env_token(), os.environ.get("ALERTS_IN_UA_TOKEN")):
        if tok and tok in html:
            pytest.fail("the API token value is in the built site")   # never print the value


@pytest.mark.skipif(not (ROOT / "site" / "index.html").exists(), reason="site not built")
def test_committed_site_matches_a_fresh_build():
    if not (REAL / "official" / "test_predictions.csv").exists():
        pytest.skip("final test not scored in this checkout")
    html = B.render_site(B.build_payload(REAL), ROOT / "site_src" / "template.html")
    assert (ROOT / "site" / "index.html").read_text() == html, "site/index.html is stale: run scripts/build_site.py"
