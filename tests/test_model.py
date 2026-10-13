"""Model, calibration rule and frozen predictor (M4 plan §2-3)."""
import json

import numpy as np
import pandas as pd
import pytest

from src import features, model
from src.data import DataQualityError


def toy(n=3000, seed=0, shift=0.0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({c: rng.random(n) * 100 for c in features.FEATURES})
    df["unit_code"] = rng.integers(0, 24, n)
    df["hour_kyiv"] = rng.integers(0, 24, n)
    df["weekday_kyiv"] = rng.integers(0, 7, n)
    logit = (df["onsets_last_7d"] - 50) / 15 + shift
    df["y"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(float)
    return df


def test_training_is_deterministic_and_saved_model_is_early_stopped(tmp_path):
    fit, val = toy(seed=1), toy(seed=2)
    b1, curve = model.train(fit, val, features.FEATURES)
    b2, _ = model.train(fit, val, features.FEATURES)
    assert b1.model_to_string(num_iteration=b1.best_iteration) == b2.model_to_string(num_iteration=b2.best_iteration)
    assert 1 <= b1.best_iteration <= model.MAX_ROUNDS and len(curve) >= b1.best_iteration
    sha = model.save_model(b1, tmp_path / "m.txt")
    loaded = model.load_model(tmp_path / "m.txt")
    assert loaded.num_trees() == b1.best_iteration                        # no refit, only early-stopped trees
    assert np.array_equal(loaded.predict(model._matrix(val, features.FEATURES)),
                          b1.predict(model._matrix(val, features.FEATURES), num_iteration=b1.best_iteration))
    assert sha == model.sha256_file(tmp_path / "m.txt")


def test_validation_labels_drive_early_stopping():
    fit, val = toy(seed=1), toy(seed=2)
    b1, _ = model.train(fit, val, features.FEATURES)
    flipped = val.assign(y=1 - val["y"])
    b2, _ = model.train(fit, flipped, features.FEATURES)
    assert b1.best_iteration != b2.best_iteration


def test_nan_feature_and_unknown_label_raise():
    fit, val = toy(seed=1), toy(seed=2)
    with pytest.raises(DataQualityError):
        model.train(fit.assign(onsets_last_7d=np.nan), val, features.FEATURES)
    with pytest.raises(DataQualityError):
        model.train(fit, val.assign(y=np.nan), features.FEATURES)


def test_ece_hand_value():
    assert model.ece([0.05, 0.05, 0.95], [0, 1, 1]) == pytest.approx((2 / 3) * 0.45 + (1 / 3) * 0.05)


def test_calibration_rule_both_branches():
    rng = np.random.default_rng(0)
    p = rng.random(20000)
    y = (rng.random(20000) < p).astype(float)                             # calibrated -> ECE small -> none
    c0 = model.calibration_decision(p, y)
    assert c0["decision"] == "none" and c0["ece"] <= model.ECE_THRESHOLD
    assert np.array_equal(model.apply_calibration(p, c0), p)
    y2 = (rng.random(20000) < p ** 2).astype(float)                       # over-confident -> Platt
    c1 = model.calibration_decision(p, y2)
    assert c1["decision"] == "platt" and c1["slope"] > 0
    assert model.ece(model.apply_calibration(p, c1), y2) < c1["ece"]
    with pytest.raises(DataQualityError):
        model.calibration_decision(np.full(100, 0.9), np.ones(100))       # one class, miscalibrated


def test_predictor_from_files(tmp_path):
    fit, val = toy(seed=1), toy(seed=2)
    b, _ = model.train(fit, val, features.FEATURES)
    model.save_model(b, tmp_path / "model.txt")
    cal = {"decision": "platt", "ece": 0.05, "clip": model.CLIP, "slope": 1.2, "intercept": -0.1}
    (tmp_path / "calibrator.json").write_text(json.dumps(cal))
    pr = model.Predictor(tmp_path / "model.txt", tmp_path / "calibrator.json", features.FEATURES)
    raw = pr.raw(val)
    assert np.allclose(pr.headline(val), 1 / (1 + np.exp(-(1.2 * np.log(raw / (1 - raw)) - 0.1))))


def test_input_guards(tmp_path):
    fit, val = toy(seed=1), toy(seed=2)
    b, _ = model.train(fit, val, features.FEATURES)
    model.save_model(b, tmp_path / "model.txt")
    (tmp_path / "calibrator.json").write_text(json.dumps({"decision": "none", "ece": 0.0, "clip": model.CLIP}))
    with pytest.raises(DataQualityError):
        model.Predictor(tmp_path / "model.txt", tmp_path / "calibrator.json", list(reversed(features.FEATURES)))
    pr = model.Predictor(tmp_path / "model.txt", tmp_path / "calibrator.json", features.FEATURES)
    for bad in (99, -1, 3.7):
        with pytest.raises(DataQualityError):
            pr.raw(val.assign(unit_code=bad))
    with pytest.raises(DataQualityError):
        model.apply_calibration([0.2], {"decision": "isotonic"})
    for y in ([0, np.nan], [2, 3], []):
        with pytest.raises(DataQualityError):
            model.ece([0.1] * len(y), y)
