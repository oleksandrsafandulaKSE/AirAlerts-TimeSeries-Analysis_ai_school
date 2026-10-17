"""M9 §B–§D: block bootstrap, DM test, CORP decomposition, calibration CIs; and code isolation (fingerprint)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extras import corp, uncertainty as U

ROOT = Path(__file__).resolve().parents[1]


def synth(n_weeks=4, units=("kyiv_city", "sumska", "lvivska"), seed=0, better=False, same=False):
    rng = np.random.default_rng(seed)
    t = pd.date_range("2026-06-29", periods=24 * 7 * n_weeks, freq="h", tz="UTC")
    df = pd.DataFrame([(u, x) for x in t for u in units], columns=["unit", "t"])
    p_true = rng.uniform(0.02, 0.4, len(df))
    df["y"] = (rng.uniform(size=len(df)) < p_true).astype(float)
    df["p_rr"] = df["y"].mean()
    df["p_model"] = df["p_rr"] if same else (p_true if better else rng.uniform(0.02, 0.4, len(df)))
    return U._finish(df)


# ---------------- §B ----------------

def test_identical_forecasts_give_zero_skill_and_zero_ci():
    df = synth(same=True)
    r = U.bootstrap_bss(df, "week", n_boot=200)
    assert r["bss"] == 0 and r["ci_low"] == 0 and r["ci_high"] == 0
    assert U.dm_test(df)["z_nw24"] == 0.0


def test_strictly_better_model_ci_above_zero():
    df = synth(better=True)
    for scheme in U.SCHEMES:
        r = U.bootstrap_bss(df, scheme, n_boot=300)
        assert r["ci_low"] > 0, scheme
    assert U.dm_test(df)["z_nw24"] < -3  # model loss lower -> negative z


@pytest.mark.parametrize("scheme", U.SCHEMES)
def test_blocks_keep_all_units_together(scheme):
    df = synth(n_weeks=3)
    per_hour = df.groupby("t").size()
    for idx in U.resample_rows(df, scheme, np.random.default_rng(1), n_boot=20):
        c = df.iloc[idx].groupby("t").size()
        assert ((c % per_hour.loc[c.index]) == 0).all()  # an hour enters only with ALL its rows


def test_week_blocks_are_monday_utc_and_count():
    df = synth(n_weeks=2)  # 2026-06-29 is a Monday
    assert U.n_blocks(df, "week") == 2 and U.n_blocks(df, "day") == 14 and U.n_blocks(df, "moving24h") == 14
    ids = U.block_ids(df["t"], "week")
    assert pd.Timestamp(ids.min()).weekday() == 0


def test_seed_reproduces():
    df = synth()
    assert U.bootstrap_bss(df, "day", n_boot=100) == U.bootstrap_bss(df, "day", n_boot=100)


def test_newey_west_lag0_is_variance():
    x = np.random.default_rng(3).normal(size=500)
    assert abs(U.newey_west(x, 0) - x.var()) < 1e-12


def test_dm_is_row_weighted():
    df = synth(better=True)
    d = df["lm"] - df["lr"]
    S = d.groupby(df["t"]).sum()
    assert abs(S.sum() / len(df) - U.dm_test(df)["mean_d_row"]) < 1e-15


def test_real_full_sample_bss_reproduces_frozen_metrics():
    test, val = U.load_test(ROOT), U.load_val(ROOT)
    m = pd.read_csv(ROOT / "reports/official/metrics.csv")
    mv = pd.read_csv(ROOT / "reports/official/metrics_validation.csv")
    pick = lambda t: float(t[(t.baseline == "model") & (t.group == "overall")]["brier_skill_vs_recent"].iloc[0])  # noqa: E731
    assert abs(U.bss(test) - pick(m)) < 1e-12 and abs(U.bss(val) - pick(mv)) < 1e-12
    assert len(test) == 13116 and len(val) == 11160


def test_validation_join_rejects_mismatched_labels(tmp_path):
    for sub in ("reports/official", "reports/improve"):
        (tmp_path / sub).mkdir(parents=True)
    a = pd.read_csv(ROOT / "reports/official/val_predictions.csv").head(50)
    b = pd.read_csv(ROOT / "reports/improve/validation_predictions.csv").head(50)
    b.loc[0, "y"] = 1 - b.loc[0, "y"]
    a.to_csv(tmp_path / "reports/official/val_predictions.csv", index=False)
    b.to_csv(tmp_path / "reports/improve/validation_predictions.csv", index=False)
    with pytest.raises(Exception, match="labels differ"):
        U.load_val(tmp_path)
    b.loc[0, "y"] = 1 - b.loc[0, "y"]
    b.iloc[1:].to_csv(tmp_path / "reports/improve/validation_predictions.csv", index=False)
    with pytest.raises(Exception, match="key sets differ"):
        U.load_val(tmp_path)


# ---------------- §C ----------------

def test_corp_hand_calculated_fixture():
    p, y = np.array([0.1, 0.2, 0.3, 0.4]), np.array([0, 1, 0, 1.0])
    assert np.allclose(corp.pav(p, y), [0, 0.5, 0.5, 1], atol=1e-12)
    d = corp.decompose(p, y)
    for k, v in {"brier": 0.275, "mcb": 0.150, "dsc": 0.125, "unc": 0.25}.items():
        assert abs(d[k] - v) < 1e-12, k


def test_corp_calibrated_and_constant_forecasts():
    rng = np.random.default_rng(5)
    p = rng.uniform(0, 1, 20000)
    y = (rng.uniform(size=p.size) < p).astype(float)
    assert corp.decompose(p, y)["mcb"] < 0.003
    c = corp.decompose(np.full(p.size, y.mean()), y)
    assert abs(c["dsc"]) < 1e-12 and abs(c["mcb"]) < 1e-12


def test_corp_terms_non_negative_and_broken_pav_caught(monkeypatch):
    rng = np.random.default_rng(11)
    for _ in range(20):
        p = rng.uniform(size=300)
        y = (rng.uniform(size=300) < rng.uniform(size=300)).astype(float)
        d = corp.decompose(p, y)
        assert d["mcb"] >= -1e-12 and d["dsc"] >= -1e-12
    # a "PAV" that returns a worse-than-identity fit must be rejected
    monkeypatch.setattr(corp, "pav", lambda p, y: 1 - np.asarray(p, float))
    with pytest.raises(AssertionError, match="negative"):
        corp.decompose(np.array([0.1, 0.2, 0.8, 0.9]), np.array([0, 0, 1, 1.0]))


def test_pav_is_non_decreasing():
    rng = np.random.default_rng(7)
    p = rng.uniform(size=500)
    y = (rng.uniform(size=500) < p).astype(float)
    f = corp.pav(p, y)
    assert np.all(np.diff(f[np.argsort(p)]) >= -1e-12)


def test_corp_bss_matches_ratio_bss():
    df = synth()
    tab = corp.corp_table(df, "s")
    got = tab[(tab.group == "overall")]["bss_vs_recent_from_decomposition"].iloc[0]
    assert abs(got - U.bss(df)) < 1e-12


# ---------------- §D ----------------

def test_real_test_calibration_matches_frozen_csv():
    from scripts import run_extras
    c = U.citl_bootstrap(U.load_test(ROOT), n_boot=50)
    run_extras.check_citl(c)  # raises on any mismatch > 1e-12


# ---------------- code isolation (D-028 is proposed only; this is the code fact) ----------------

def test_m9_keeps_the_preregistered_code_fingerprint():
    from scripts import run_all
    assert not (ROOT / "src" / "extras").exists() and (ROOT / "extras" / "uncertainty.py").exists()
    for run in ("official", "official_h3"):
        pr = json.loads((ROOT / "reports" / run / "preregistration.json").read_text())
        assert pr["code_fingerprint"] == run_all.code_fingerprint(), run


def test_few_blocks_flagged_and_dm_small_samples():
    df = synth(n_weeks=2)
    assert U.bootstrap_bss(df, "week", n_boot=50)["few_blocks_unreliable"] is True
    one_hour = df[df.t == df.t.min()]
    d = U.dm_test(one_hour)
    assert np.isnan(d["z_nw24"]) and np.isnan(d["p_nw24"])  # too few hours: undefined, not an error or a fake z
    assert np.isnan(U.dm_test(df[df.t < df.t.min() + pd.Timedelta(hours=40)])["z_nw24"])


def test_facts_mode_needs_only_the_data_file(tmp_path, monkeypatch):
    from scripts import run_extras as RE
    monkeypatch.setattr(RE, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["run_extras.py", "--facts"])
    with pytest.raises(Exception, match="official_data_en.csv"):  # data missing -> raises on the data file only
        RE.main()
