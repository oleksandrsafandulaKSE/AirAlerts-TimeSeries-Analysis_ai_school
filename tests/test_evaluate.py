import numpy as np
import pandas as pd
import pytest

from src import config, evaluate, grid
from src.data import DataQualityError

H1 = pd.Timedelta(hours=1)
FEAT = ["f1"]


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def toy_frame(start="2024-01-10 00:00", hours=10, unit="A"):
    t = pd.date_range(ts(start), periods=hours, freq="h")
    return pd.DataFrame({"unit": unit, "t": t, "group": "rear", "mask": 0, "y": 0.0, "f1": 1.0})


def test_eligibility_purge_and_reasons():
    f = toy_frame()
    C = ts("2024-01-10 10:00")
    ok3, c3 = evaluate.eligibility(f, ts("2024-01-10 00:00"), C, pd.Timedelta(hours=3), FEAT)
    t = f["t"]
    assert ok3[t == C - pd.Timedelta(hours=3)].all()                      # t + H == C kept
    assert not ok3[(t == C - pd.Timedelta(hours=2)) | (t == C - H1)].any()  # purged
    ok1, _ = evaluate.eligibility(f, ts("2024-01-10 00:00"), C, H1, FEAT)
    assert ok1[t == C - H1].all()
    f.loc[1, "mask"] = 1
    f.loc[2, "y"] = np.nan
    f.loc[3, "f1"] = np.nan
    f.loc[4, ["mask", "f1"]] = [1, np.nan]                                 # two reasons: counted once
    ok, c = evaluate.eligibility(f, ts("2024-01-10 00:00"), C, H1, FEAT)
    assert c["excluded_exclusive"] == {"purge": 0, "masked": 2, "y_nan": 1, "feature_nan": 1}
    assert c["excluded_overlapping"] == {"purge": 0, "masked": 2, "y_nan": 1, "feature_nan": 2}
    assert c["in_range"] == 10 and c["eligible"] == 6 and ok.sum() == 6
    assert c3["excluded_exclusive"]["purge"] == 2


def test_test_guard():
    with pytest.raises(PermissionError):
        evaluate.score_split("test")
    assert evaluate.score_split("test", allow_test=True) == "test"
    assert evaluate.score_split("val") == "val"


def test_isolation():
    f = toy_frame()
    f["y"] = 1.0
    out = evaluate.isolate_test_labels(f, ts("2024-01-10 05:00"), H1)
    assert out.loc[out.t >= ts("2024-01-10 05:00"), "y"].isna().all()
    assert (out.loc[out.t < ts("2024-01-10 05:00"), "y"] == 1).all()
    assert (f["y"] == 1).all()  # input untouched


def test_boundary_onset_at_test_start():
    """Onset exactly at C: last val row y=1 and eligible; test row C masked; no test y read."""
    C = ts("2024-01-10 05:00")
    al = pd.DataFrame([{"source": "t", "alert_id": "1", "unit": "A", "level": "oblast",
                        "started_at": C, "finished_at": C + pd.Timedelta(minutes=40), "alert_level": ""}])
    g = grid.build_grid(al, ts("2024-01-10 00:00"), ts("2024-01-10 08:00"), H1, unit_list=["A"])
    g["f1"] = 1.0
    last_val = g[g.t == C - H1].iloc[0]
    assert last_val["y"] == 1 and last_val["mask"] == 0
    assert g.loc[g.t == C, "mask"].iloc[0] == 1
    iso = evaluate.isolate_test_labels(g, C, H1)
    ok, _ = evaluate.eligibility(iso, ts("2024-01-10 00:00"), C, H1, FEAT)
    assert ok[(iso.t == C - H1).to_numpy()].all()
    assert iso.loc[iso.t >= C, "y"].isna().all()
    ok_test, ct = evaluate.eligibility(iso, C, ts("2024-01-10 08:00"), H1, FEAT)
    assert ok_test.sum() == 0  # every test row is masked or label-blanked


def test_brier_skill_auc_ap():
    r = []
    assert evaluate.brier([0.2, 0.8], [0, 1]) == pytest.approx(0.04)
    assert evaluate.skill(0.04, 0.08, r, "x") == pytest.approx(0.5)
    assert np.isnan(evaluate.skill(0.04, 0.0, r, "x")) and "reference Brier" in r[-1]
    assert evaluate.auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], r, "x") == 1.0
    assert evaluate.auc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1], r, "x") == 0.0
    assert np.isnan(evaluate.auc([1, 1], [0.1, 0.2], r, "x")) and "one class" in r[-1]
    assert evaluate.avg_precision(np.array([1, 0, 1]), [0.9, 0.8, 0.7], r, "x") == pytest.approx(5 / 6)
    assert np.isnan(evaluate.avg_precision(np.array([0, 0]), [0.9, 0.8], r, "x"))


def scored_toy():
    rng = np.random.default_rng(0)
    rows = []
    for u, grp, npos in [("A", "kyiv_city", 12), ("B", "frontline", 9), ("C", "rear", 15)]:
        for i in range(40):
            y = int(i < npos)
            rows.append({"unit": u, "group": grp, "y": y, "m1": 0.8 if y else 0.2, "m2": rng.random()})
    return pd.DataFrame(rows)


def test_within_unit_auc_and_table():
    s = scored_toy()
    r = []
    mean, used, excl = evaluate.within_unit_auc(s, "m1", 10, r, "x")
    assert (mean, used, excl) == (1.0, 2, ["B"])  # B has 9 positives -> excluded
    table, reasons = evaluate.metric_table(s, ["m1", "m2"], "m2", 10)
    assert list(table["group"].unique()) == evaluate.GROUPS
    assert len(table) == 8
    assert (table.loc[table.baseline == "m2", "brier_skill_vs_recent"] == 0).all()
    ov = table[(table.baseline == "m1") & (table.group == "overall")].iloc[0]
    assert ov["rows"] == 120 and ov["base_rate"] == pytest.approx(36 / 120)
    assert ov["brier"] == pytest.approx(0.04)
    assert ov["pr_auc_over_base"] == pytest.approx(ov["pr_auc"] / (36 / 120))


def test_empty_group_and_zero_base_rate():
    s = scored_toy()
    s = s[s.group != "rear"].copy()
    s.loc[s.group == "kyiv_city", "y"] = 0
    table, reasons = evaluate.metric_table(s, ["m1", "m2"], "m2", 10)
    assert table.loc[table.group == "rear", "rows"].eq(0).all()
    assert any("empty group" in r for r in reasons)
    assert any("PR-AUC/base NaN" in r and "kyiv_city" in r for r in reasons)
    assert table.loc[table.group == "kyiv_city", "pr_auc_over_base"].isna().all()


def test_reliability_bins():
    rb = evaluate.reliability_bins([0.05, 0.05, 0.95, 1.0], [0, 1, 1, 1])
    b0 = rb[rb.bin == 0].iloc[0]
    b9 = rb[rb.bin == 9].iloc[0]
    assert (b0.n, b0.mean_p, b0.mean_y) == (2, pytest.approx(0.05), 0.5)
    assert (b9.n, b9.mean_p, b9.mean_y) == (2, pytest.approx(0.975), 1.0)
    assert len(rb) == 2


def test_gap_interval_config():
    c = config.official()
    assert config.gap_label_mask_interval(c) == ((ts("2026-08-28 23:00"), ts("2026-09-04 00:00")),)
    assert config.uncertainty_zones(c) == ((ts("2026-08-29 00:00"), ts("2026-09-04 00:00")),)


def test_within_unit_threshold_is_inclusive():
    rows = [{"unit": "A", "y": int(i < 10), "m": 0.9 if i < 10 else 0.1} for i in range(20)]  # 10 pos, 10 neg
    rows += [{"unit": "B", "y": int(i < 9), "m": 0.9 if i < 9 else 0.1} for i in range(20)]   # 9 pos
    mean, used, excl = evaluate.within_unit_auc(pd.DataFrame(rows), "m", 10, [], "x")
    assert used == 1 and excl == ["B"]


def test_split_bounds_guard_and_input_checks():
    c = config.official()
    assert evaluate.split_bounds(c, "val") == c.val
    with pytest.raises(PermissionError):
        evaluate.split_bounds(c, "test")
    assert evaluate.split_bounds(c, "test", allow_test=True) == c.test
    with pytest.raises(ValueError):
        evaluate.reliability_bins([-0.1, 0.5], [0, 1])
    with pytest.raises(ValueError):
        evaluate.reliability_bins([np.nan, 0.5], [0, 1])
    with pytest.raises(KeyError):
        evaluate.isolate_test_labels(toy_frame().drop(columns="y"), ts("2024-01-10 05:00"), H1)
    with pytest.raises(TypeError):
        evaluate.isolate_test_labels(toy_frame(), "2024-01-10 05:00", H1)
    s = scored_toy()
    s.loc[0, "m1"] = 1.2
    with pytest.raises(ValueError):
        evaluate.metric_table(s, ["m1", "m2"], "m2", 10)


def test_availability_counts_without_labels():
    f = toy_frame()
    f["y"] = np.nan
    f.loc[1, "mask"] = 1
    f.loc[2, "f1"] = np.nan
    c = evaluate.availability(f, ts("2024-01-10 00:00"), ts("2024-01-10 10:00"), pd.Timedelta(hours=3), FEAT)
    assert c == {"in_range": 10, "available": 6,
                 "excluded_overlapping": {"purge": 2, "masked": 1, "feature_nan": 1},
                 "excluded_exclusive": {"purge": 2, "masked": 1, "feature_nan": 1}}
    f.loc[1, "f1"] = np.nan                                    # masked AND feature NaN: counted once
    c = evaluate.availability(f, ts("2024-01-10 00:00"), ts("2024-01-10 10:00"), pd.Timedelta(hours=3), FEAT)
    assert c["excluded_overlapping"]["feature_nan"] == 2 and c["excluded_exclusive"]["feature_nan"] == 1


def test_isolation_h3_blanks_immature_labels():
    f = toy_frame()
    f["y"] = 1.0
    C = ts("2024-01-10 05:00")
    out = evaluate.isolate_test_labels(f, C, pd.Timedelta(hours=3))
    assert out.loc[out.t >= C - pd.Timedelta(hours=2), "y"].isna().all()
    assert (out.loc[out.t <= C - pd.Timedelta(hours=3), "y"] == 1).all()
