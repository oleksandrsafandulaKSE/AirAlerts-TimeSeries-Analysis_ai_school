import dataclasses
import json

import pytest

from scripts import run_all
import pandas as pd

from src import config, data, features, grid, regions

HEADER = "oblast,raion,hromada,level,started_at,finished_at,source\n"


def fixture(tmp_path, dup=False):
    rows = []
    for d in range(1, 29):
        for i, v in enumerate(regions.UNITS.values()):
            rows.append(f"{v['official_name']},,,oblast,2024-02-{d:02d} {i % 24:02d}:10:00+00:00,"
                        f"2024-02-{d:02d} {i % 24:02d}:40:00+00:00,official\n")
    if dup:
        rows.append(rows[0])
    p = tmp_path / "f.csv"
    p.write_text(HEADER + "".join(rows))
    return p, len(rows)


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def cfg(n_raw, n_dup):
    return dataclasses.replace(config.official(), grid_start=ts("2024-02-02"), grid_end=ts("2024-02-27"),
                               coverage_end=ts("2024-02-28"), approved_gaps=(),
                               train=(ts("2024-02-02"), ts("2024-02-13")), val=(ts("2024-02-13"), ts("2024-02-20")),
                               test=(ts("2024-02-20"), ts("2024-02-27")),
                               expected_raw_rows=n_raw, expected_duplicate_rows=n_dup)


def test_run_writes_meta(tmp_path, monkeypatch):
    p, n = fixture(tmp_path)
    monkeypatch.setattr(run_all.grid, "check_base_rate", lambda g, before, H: 0.0)
    out = tmp_path / "out"
    run_all.run_pipeline(cfg(n, 0), p, out)
    meta = json.loads((out / "run_meta.json").read_text())
    for k in ["config", "dates", "data_sha256", "row_counts", "git_commit", "python", "packages", "features"]:
        assert k in meta
    assert (out / "m1_checks.json").exists() and (out / "base_rate_by_quarter.csv").exists()
    assert (out / "m2_checks.json").exists()
    m = pd.read_csv(out / "metrics_validation.csv")
    predictors = set(run_all.baselines.BASELINES) | {"model"}
    assert set(m.baseline) - {"model_raw"} == predictors and len(m) == 4 * m.baseline.nunique()
    assert (out / "preregistration.json").exists() and (out / "model.txt").exists()
    assert m.groupby("group")["rows"].nunique().eq(1).all()   # every baseline on the same rows per group
    assert (out / "reliability_validation.png").stat().st_size > 0
    m3 = json.loads((out / "m3_checks.json").read_text())
    assert m3["split"] == "val" and set(m3["split_counts"]) == {"train", "val"}
    assert not (out / "metrics.csv").exists()  # reserved for the M4 test scoring
    assert meta["features"] == run_all.features.FEATURES and "active_at_t" not in meta["features"]


@pytest.mark.parametrize("argv,exc", [(["--config", "new_regime"], data.DataQualityError),
                                      (["--config", "official", "--as-of", "2026-10-01"], ValueError),
                                      (["--config", "nope"], ValueError)])
def test_main_rejects_before_reading_data(argv, exc, tmp_path):
    with pytest.raises(exc):
        run_all.main(argv + ["--data-path", str(tmp_path / "missing.csv"), "--out-dir", str(tmp_path / "o"),
                             "--reports-root", str(tmp_path / "reports")])
    assert not (tmp_path / "o").exists()


def test_m3_output_ignores_test_labels(tmp_path, monkeypatch):
    p, n = fixture(tmp_path)
    c = cfg(n, 0)
    a = data.load_official(p, c)
    g = grid.build_grid(a, c.grid_start, c.grid_end, c.H, coverage_end=c.coverage_end)
    f = features.build_features(a, pd.DatetimeIndex(g.t.drop_duplicates()), ())
    gf = features.join_to_grid(g, f)
    t1, _, _ = run_all.run_m3(gf, a, c)
    poisoned = gf.copy()
    poisoned.loc[poisoned.t >= c.test[0], "y"] = 1.0 - poisoned.loc[poisoned.t >= c.test[0], "y"]
    t2, _, _ = run_all.run_m3(poisoned, a, c)
    pd.testing.assert_frame_equal(t1, t2)


def _frames(tmp_path):
    p, n = fixture(tmp_path)
    c = cfg(n, 0)
    a = data.load_official(p, c)
    g = grid.build_grid(a, c.grid_start, c.grid_end, c.H, coverage_end=c.coverage_end)
    f = features.build_features(a, pd.DatetimeIndex(g.t.drop_duplicates()), ())
    return c, a, features.join_to_grid(g, f)


def test_frozen_baselines_fit_on_train_only(tmp_path):
    c, a, gf = _frames(tmp_path)
    _, s1, k1 = run_all.run_m3(gf, a, c)
    flipped = gf.copy()
    v = (flipped.t >= c.val[0]) & (flipped.t < c.val[1]) & flipped.y.notna()
    flipped.loc[v, "y"] = 1.0 - flipped.loc[v, "y"]
    _, s2, k2 = run_all.run_m3(flipped, a, c)
    for name in ["climatology", "persistence_calibrated"]:
        assert (s1[name].to_numpy() == s2[name].to_numpy()).all(), name
    assert k1["p_unit"] == k2["p_unit"]
    assert not (s1["recent_rate"].to_numpy() == s2["recent_rate"].to_numpy()).all()  # rolling: does read val


def test_m3_applies_feature_rule_and_reference(tmp_path):
    c, a, gf = _frames(tmp_path)
    row = gf[(gf.t >= c.val[0]) & (gf.t < c.val[1]) & (gf["mask"] == 0)].index[0]
    gf.loc[row, "onsets_last_7d"] = float("nan")
    table, _, checks = run_all.run_m3(gf, a, c)
    assert checks["split_counts"]["val"]["excluded_exclusive"]["feature_nan"] == 1
    sk = table.set_index(["baseline", "group"])["brier_skill_vs_recent"]
    assert (sk.loc["recent_rate"] == 0).all()
    assert (sk.loc["climatology"] != 0).any()


def test_check_gap_rows(tmp_path):
    c, a, gf = _frames(tmp_path)
    gap = ((ts("2024-02-10 00:00"), ts("2024-02-11 00:00")),)
    c2 = dataclasses.replace(c, approved_gaps=gap)
    g = grid.build_grid(a, c.grid_start, c.grid_end, c.H, approved_gaps=gap)
    assert run_all.check_gap_rows(g, c2) == 1 + 24 + 24      # 1h before + gap + 24h after
    g.loc[g.index[0], "gap_mask"] = 1
    with pytest.raises(data.DataQualityError):
        run_all.check_gap_rows(g, c2)


def test_failed_check_writes_nothing(tmp_path):
    p, n = fixture(tmp_path, dup=True)
    out = tmp_path / "out"
    with pytest.raises(data.DataQualityError):
        run_all.run_pipeline(cfg(n, 0), p, out)
    assert not out.exists()


# ---------------- H = 3 (M3b) ----------------
H3 = pd.Timedelta(hours=3)


def _frames_h3(tmp_path, extra_rows=()):
    p, n = fixture(tmp_path)
    if extra_rows:
        with open(p, "a") as fh:
            fh.writelines(extra_rows)
        n += len(extra_rows)
    c = dataclasses.replace(cfg(n, 0), H=H3)
    a = data.load_official(p, c)
    g = grid.build_grid(a, c.grid_start, c.grid_end, c.H, coverage_end=c.coverage_end)
    f = features.build_features(a, pd.DatetimeIndex(g.t.drop_duplicates()), ())
    return c, a, g, features.join_to_grid(g, f)


def _m1_diag(g, c):
    by_q, by_g, pre = grid.base_rate_table(g, c.test[0], c.H)
    return by_q, by_g, len(pre)


def test_h3_fixture_counts_skill_isolation(tmp_path):
    c, a, g, gf = _frames_h3(tmp_path)
    table, scored, checks = run_all.run_m3(gf, a, c)
    for split in ("train", "val"):
        assert checks["split_counts"][split]["excluded_exclusive"]["purge"] == 2 * 24   # C-2h, C-1h per unit
    assert len(table) == 16
    sk = table.set_index(["baseline", "group"])["brier_skill_vs_recent"]
    assert (sk.loc["recent_rate"] == 0).all()
    assert scored["t"].max() + c.H <= c.val[1]


def test_h3_label_poisoning_changes_nothing(tmp_path):
    """End-to-end: post-cut-off labels cannot change M1 base rates or M3 outputs at H = 3.
    Note: in M3 the purge (t + H <= val end = C) and the recent-rate rule (s <= t - H) already keep rows
    C-2h and C-1h out, so this test pins the base-rate fix; isolate_test_labels(t + H > C) is a second
    safety layer pinned by test_evaluate::test_isolation_h3_blanks_immature_labels."""
    c, a, g, gf = _frames_h3(tmp_path)
    hidden = gf["t"] + c.H > c.test[0]
    assert hidden.sum() == 24 * (2 + 7 * 24)               # C-2h, C-1h + the 7-day test window, all units
    poisoned = gf.copy()
    poisoned.loc[hidden & poisoned.y.notna(), "y"] = 1.0 - poisoned.loc[hidden & poisoned.y.notna(), "y"]
    for x, y in zip(_m1_diag(gf, c), _m1_diag(poisoned, c)):
        if isinstance(x, pd.DataFrame):
            pd.testing.assert_frame_equal(x, y)
        else:
            assert x == y
    t1, s1, k1 = run_all.run_m3(gf, a, c)
    t2, s2, k2 = run_all.run_m3(poisoned, a, c)
    pd.testing.assert_frame_equal(t1, t2)
    pd.testing.assert_frame_equal(s1, s2)
    assert k1["p_unit"] == k2["p_unit"]


def test_h3_raw_alert_after_cutoff_changes_no_label_output(tmp_path):
    c, a, g, gf = _frames_h3(tmp_path)
    C = c.test[0]
    # Zhytomyrska's fixture alerts are at 10:10 daily, so nothing else falls near C
    late = (f"Zhytomyrska oblast,,,oblast,{(C + pd.Timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')}+00:00,"
            f"{(C + pd.Timedelta(hours=1, minutes=40)).strftime('%Y-%m-%d %H:%M:%S')}+00:00,official\n")
    (tmp_path / "late").mkdir()
    c2, a2, g2, gf2 = _frames_h3(tmp_path / "late", [late])
    key = lambda df: df.set_index(["unit", "t"])["y"]  # noqa: E731
    leaked_rows = [("zhytomyrska", C - pd.Timedelta(hours=2)), ("zhytomyrska", C - pd.Timedelta(hours=1))]
    for r in leaked_rows:  # the event DOES change these raw labels: without isolation it would leak
        assert key(g)[r] == 0 and key(g2)[r] == 1
    for x, y in zip(_m1_diag(g, c), _m1_diag(g2, c2)):
        if isinstance(x, pd.DataFrame):
            pd.testing.assert_frame_equal(x, y)
        else:
            assert x == y
    t1, s1, k1 = run_all.run_m3(gf, a, c)
    t2, s2, k2 = run_all.run_m3(gf2, a2, c2)
    pd.testing.assert_frame_equal(t1, t2)
    pd.testing.assert_frame_equal(s1, s2)
    assert k1["p_unit"] == k2["p_unit"] and k1["split_counts"] == k2["split_counts"]
    # availability counts of the test split may legitimately differ (D-024): not compared


# ---------------- M4 fit stage: exact keys and isolation (plan §7) ----------------

@pytest.mark.parametrize("hours", [1, 3])
def test_m4_fit_exact_keys_and_post_cutoff_isolation(tmp_path, monkeypatch, hours):
    p, n = fixture(tmp_path)
    c = dataclasses.replace(cfg(n, 0), H=pd.Timedelta(hours=hours))
    a = data.load_official(p, c)
    g = grid.build_grid(a, c.grid_start, c.grid_end, c.H, coverage_end=c.coverage_end)
    f = features.build_features(a, pd.DatetimeIndex(g.t.drop_duplicates()), ())
    gf = features.join_to_grid(g, f)
    seen = {}
    real_train = run_all.model.train

    def spy(fit, val, feats):
        seen["fit"] = set(zip(fit.unit, fit.t))
        seen["val"] = set(zip(val.unit, val.t))
        return real_train(fit, val, feats)
    monkeypatch.setattr(run_all.model, "train", spy)
    _, scored, _ = run_all.run_m3(gf, a, c)
    m1 = run_all.run_m4_fit(gf, a, c, scored, p)
    H = c.H
    exp_fit = {(u, t) for u, t, m, y in zip(gf.unit, gf.t, gf["mask"], gf.y)
               if c.train[0] <= t and t + H <= c.train[1] and m == 0 and y == y}
    exp_val = {(u, t) for u, t, m, y in zip(gf.unit, gf.t, gf["mask"], gf.y)
               if c.val[0] <= t and t + H <= c.val[1] and m == 0 and y == y}
    feat_ok = {(u, t) for u, t, ok in zip(gf.unit, gf.t, gf[features.FEATURES].notna().all(axis=1)) if ok}
    assert seen["fit"] == exp_fit & feat_ok and seen["val"] == exp_val & feat_ok
    last_kept, first_purged = c.val[1] - H, c.val[1] - H + pd.Timedelta(hours=1)
    assert any(t == last_kept for _, t in seen["val"]) and not any(t >= first_purged for _, t in seen["val"])
    flipped = gf.copy()
    hide = flipped["t"] + H > c.val[1]                     # purged rows + the whole test period
    flipped.loc[hide & flipped.y.notna(), "y"] = 1 - flipped.loc[hide & flipped.y.notna(), "y"]
    m2 = run_all.run_m4_fit(flipped, a, c, scored, p)
    assert m1["model_str"] == m2["model_str"]
