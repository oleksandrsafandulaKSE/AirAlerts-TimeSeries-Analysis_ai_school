"""M7 models and selection (plans/M7.md §2, §2.1, §3, §5): offset reload + oracle, acceptance rule, blend on validation
only, weekly-refit windows/keys/isolation, fold boundaries, the headline code-fingerprint guard."""
import lightgbm as lgb
import numpy as np
import pandas as pd
import pytest

from improve import model_plus as MP
from scripts import run_improve as RI
from src import config, features
from src.data import DataQualityError

FE = features.FEATURES


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def toy(n=4000, seed=0, start="2026-06-01"):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({c: rng.random(n) * 100 for c in FE})
    df["unit_code"] = rng.integers(0, 24, n)
    df["hour_kyiv"] = rng.integers(0, 24, n)
    df["weekday_kyiv"] = rng.integers(0, 7, n)
    df["offset_rate"] = np.clip(rng.random(n) * 0.3, 0, 1)
    logit = np.log(df["offset_rate"].clip(1e-4) / (1 - df["offset_rate"])) + (df["onsets_last_7d"] - 50) / 25
    df["y"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(float)
    df["t"] = pd.date_range(ts(start), periods=n, freq="h")
    df["unit"] = "kyiv_city"
    df["mask"] = 0
    return df


def test_offset_model_reload_reproduces_predictions():
    fit, val = toy(seed=1), toy(seed=2)
    b = MP.train_offset(fit, val, FE)
    p1 = MP.predict_offset(b, val, FE)
    b2 = lgb.Booster(model_str=b.model_to_string(num_iteration=b.best_iteration))
    p2 = MP.predict_offset(b2, val, FE, num_iteration=-1)
    assert np.array_equal(p1, p2)


def test_zero_residual_oracle_returns_the_clipped_offset():
    fit, val = toy(seed=1), toy(seed=2)
    b = MP.train_offset(fit, val, FE)
    df = val.head(3).copy()
    df["offset_rate"] = [0.0, 0.2, 1.0]
    assert MP.predict_offset(b, df, FE, num_iteration=0) == pytest.approx([1e-4, 0.2, 1 - 1e-4])


def test_offset_is_used():
    fit, val = toy(seed=1), toy(seed=2)
    b = MP.train_offset(fit, val, FE)
    shifted = val.assign(offset_rate=np.clip(val["offset_rate"] + 0.2, 0, 1))
    assert not np.allclose(MP.predict_offset(b, val, FE), MP.predict_offset(b, shifted, FE))
    with pytest.raises(DataQualityError):
        MP.train_offset(fit.assign(offset_rate=np.nan), val, FE)


@pytest.mark.parametrize("cand,ok", [
    ({1: 0.99, 2: 0.99, 3: 0.99, 4: 1.01}, True),     # -0.5 % mean, 3/4 folds
    ({1: 0.999, 2: 0.999, 3: 0.999, 4: 0.999}, False),  # -0.1 %: too small
    ({1: 0.97, 2: 0.97, 3: 1.01, 4: 1.01}, False),    # -1 % but only 2/4 folds
    ({1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}, False),        # tie rejects
])
def test_acceptance_rule(cand, ok):
    ref = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
    assert RI.accept(ref, cand)[0] == ok


def test_blend_weight_uses_validation_only():
    y = np.array([0, 0, 1, 1.0])
    pm, pr = np.array([0.1, 0.2, 0.8, 0.7]), np.array([0.4, 0.4, 0.4, 0.4])
    w, scores = RI.choose_blend(pm, pr, y)
    assert w == 1.0 and scores[1.0] < scores[0.0]
    w2, _ = RI.choose_blend(pr, pr, y)                    # identical inputs: tie -> larger model weight
    assert w2 == 1.0


def test_refit_windows_and_folds_inside_their_limits():
    C = ts("2026-08-03")
    fit, early, score = RI.refit_windows(C, ts("2026-08-10"), ts("2022-03-23"))
    assert fit == (ts("2022-03-23"), ts("2026-07-20")) and early == (ts("2026-07-20"), C) and score == (C, ts("2026-08-10"))
    train_end = config.official().train[1]
    for c in RI.FOLD_CUTS:
        assert ts(c) + RI.FOLD_SCORE <= train_end          # every backtest fold scores inside train


def refit_frame():
    t = pd.date_range(ts("2026-07-01"), ts("2026-08-17"), freq="h", inclusive="left")
    rng = np.random.default_rng(3)
    rows = []
    for u, code in (("kyiv_city", 0), ("kyivska", 9)):
        d = pd.DataFrame({c: rng.random(len(t)) * 100 for c in FE})
        d["unit_code"], d["hour_kyiv"], d["weekday_kyiv"] = code, t.hour, t.weekday
        d["t"], d["unit"], d["mask"] = t, u, 0
        d["offset_rate"] = 0.1
        d["y"] = (rng.random(len(t)) < 0.15).astype(float)
        rows.append(d)
    return pd.concat(rows, ignore_index=True)


@pytest.mark.parametrize("kind", ["plain", "offset"])
def test_refit_step_keys_and_isolation(kind):
    g = refit_frame()
    C, end, H = ts("2026-08-03"), ts("2026-08-10"), pd.Timedelta(hours=1)
    score = g[(g.t >= C) & (g.t < end)].reset_index(drop=True)
    p, fit, val, week, b = RI.refit_step(g, C, end, ts("2026-07-01"), H, FE, kind, score)
    assert fit["t"].max() + H <= C - RI.REFIT_EARLY and val["t"].min() >= C - RI.REFIT_EARLY
    assert val["t"].max() + H <= C and (val["t"] == C - H).any()          # equality boundary kept
    assert week["t"].min() >= C and week["t"].max() < end and len(p) == len(week)
    flipped = g.copy()
    later = flipped["t"] + H > C                                            # labels not known at the cut-off
    flipped.loc[later, "y"] = 1 - flipped.loc[later, "y"]
    p2, *_ = RI.refit_step(flipped, C, end, ts("2026-07-01"), H, FE, kind, score)
    assert np.array_equal(p, p2)


def test_fingerprint_guard(monkeypatch, tmp_path):
    monkeypatch.setattr(RI.run_all, "code_fingerprint", lambda root=None: "changed")
    with pytest.raises(DataQualityError):
        RI.main(["--out-dir", str(tmp_path / "out")])
    assert not (tmp_path / "out").exists()


def test_headline_code_fingerprint_matches_both_preregistrations():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for run in ("official", "official_h3"):
        pr = root / "reports" / run / "preregistration.json"
        if not pr.exists():
            pytest.skip("not pre-registered in this checkout")
        assert json.loads(pr.read_text())["code_fingerprint"] == RI.run_all.code_fingerprint(), run


def test_saved_blend_weight_recomputes_from_validation_predictions():
    import json
    from pathlib import Path
    imp = Path(__file__).resolve().parents[1] / "reports" / "improve"
    if not (imp / "validation_predictions.csv").exists():
        pytest.skip("M7 not run in this checkout")
    vp = pd.read_csv(imp / "validation_predictions.csv", float_precision="round_trip")
    w, _ = RI.choose_blend(vp["V3"].to_numpy(), vp["recent_rate"].to_numpy(), vp["y"].to_numpy())
    saved = json.loads((imp / "blend_weight.json").read_text())
    sel = json.loads((imp / "validation_selection.json").read_text())
    assert w == saved["w"] and len(vp) == sel["rows"]
    b = {k: RI.brier(vp[k], vp["y"]) for k in ("V2", "V3", "recent_rate")}
    assert b["V2"] == pytest.approx(sel["brier"]["V2"]) and b["V3"] == pytest.approx(sel["brier"]["V3"])


def test_saved_variants_share_identical_rows():
    from pathlib import Path
    f = Path(__file__).resolve().parents[1] / "reports" / "improve" / "variants_test_posthoc.csv"
    if not f.exists():
        pytest.skip("M7 not run in this checkout")
    v = pd.read_csv(f)
    assert v.groupby("group")["rows"].nunique().eq(1).all()
    assert set(v["baseline"]) >= {"V0_frozen_headline", "V1_weekly_refit", "V2_offset", "V5_blend", "recent_rate"}
