"""Pooled LightGBM onset model (M4): train on eligible TRAIN rows, early-stop on eligible VALIDATION rows, no refit
(D-021); validation-only calibration check with a pre-registered Platt rule (M4 plan §3)."""
import hashlib
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.data import DataQualityError
from src.evaluate import reliability_bins

PARAMS = {
    "objective": "binary", "learning_rate": 0.05, "num_leaves": 31, "min_data_in_leaf": 100,
    "feature_fraction": 1.0, "bagging_fraction": 1.0, "bagging_freq": 0, "seed": 20261013,
    "deterministic": True, "num_threads": 1, "force_row_wise": True, "verbose": -1, "metric": "binary_logloss",
}
MAX_ROUNDS = 2000
EARLY_STOPPING = 100
CATEGORICAL = ["unit_code"]
ECE_THRESHOLD = 0.02
CLIP = 1e-6


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


N_UNITS = 24


def _matrix(df, features):
    X = df[features].copy()
    if X.isna().any().any():
        raise DataQualityError("NaN feature reached the model (D-024 eligibility must remove these rows)")
    u = X["unit_code"].to_numpy(float)
    if (u != np.round(u)).any() or (u < 0).any() or (u >= N_UNITS).any():
        raise DataQualityError("unit_code must be an integer code 0..23 from regions.units()")
    X["unit_code"] = X["unit_code"].astype(int)
    return X


def train(fit, val, features):
    """Returns (booster, validation logloss curve). Only `fit` and `val` rows are ever given to LightGBM."""
    for name, df in (("fit", fit), ("val", val)):
        if df["y"].isna().any():
            raise DataQualityError(f"{name} rows with unknown labels")
    ds = lgb.Dataset(_matrix(fit, features), fit["y"].to_numpy(float), categorical_feature=CATEGORICAL,
                     free_raw_data=False)
    dv = lgb.Dataset(_matrix(val, features), val["y"].to_numpy(float), reference=ds,
                     categorical_feature=CATEGORICAL)
    curve = {}
    booster = lgb.train(PARAMS, ds, num_boost_round=MAX_ROUNDS, valid_sets=[dv], valid_names=["val"],
                        callbacks=[lgb.early_stopping(EARLY_STOPPING, verbose=False), lgb.record_evaluation(curve)])
    return booster, curve["val"]["binary_logloss"]


def save_model(booster, path):
    """Saves only the early-stopped trees (no refit, D-021)."""
    booster.save_model(str(path), num_iteration=booster.best_iteration)
    return sha256_file(path)


def load_model(path):
    return lgb.Booster(model_file=str(path))


def predict_raw(booster, df, features):
    return booster.predict(_matrix(df, features))


def ece(p, y):
    """Expected calibration error over the 10 fixed-width reliability bins (M3)."""
    y = np.asarray(y, float)
    if len(y) == 0 or np.isnan(y).any() or not set(np.unique(y)) <= {0.0, 1.0}:
        raise DataQualityError("ece: labels must be a non-empty 0/1 array")
    rb = reliability_bins(p, y)
    return float((rb["n"] / rb["n"].sum() * (rb["mean_p"] - rb["mean_y"]).abs()).sum())


def _logit(p):
    p = np.clip(np.asarray(p, float), CLIP, 1 - CLIP)
    return np.log(p / (1 - p))


def calibration_decision(p_val, y_val):
    """Pre-registered rule (M4 plan §3): Platt on validation only if validation ECE > 0.02."""
    e = ece(p_val, y_val)
    if e <= ECE_THRESHOLD:
        return {"decision": "none", "ece": e, "clip": CLIP}
    y = np.asarray(y_val, float)
    if len(np.unique(y)) < 2:
        raise DataQualityError("Platt: validation has one class")
    lr = LogisticRegression(C=np.inf, fit_intercept=True, solver="lbfgs", max_iter=1000)  # no regularisation
    lr.fit(_logit(p_val).reshape(-1, 1), y)
    if lr.n_iter_[0] >= 1000:
        raise DataQualityError("Platt: logistic regression did not converge")
    slope, intercept = float(lr.coef_[0, 0]), float(lr.intercept_[0])
    if slope <= 0:
        raise DataQualityError(f"Platt: non-positive slope {slope}")
    return {"decision": "platt", "ece": e, "clip": CLIP, "slope": slope, "intercept": intercept}


def apply_calibration(p, cal):
    if cal["decision"] not in ("none", "platt"):
        raise DataQualityError(f"unknown calibration decision {cal['decision']!r}")
    if cal["decision"] == "none":
        return np.asarray(p, float)
    z = cal["slope"] * _logit(p) + cal["intercept"]
    return 1.0 / (1.0 + np.exp(-z))


class Predictor:
    """The frozen headline predictor rebuilt only from files: model.txt -> raw p -> calibrator.json."""

    def __init__(self, model_path, calibrator_path, features):
        self.booster = load_model(model_path)
        self.cal = json.loads(Path(calibrator_path).read_text())
        if self.booster.feature_name() != list(features):
            raise DataQualityError(f"model features {self.booster.feature_name()} != {list(features)}")
        self.features = features

    def raw(self, df):
        return predict_raw(self.booster, df, self.features)

    def headline(self, df):
        return apply_calibration(self.raw(df), self.cal)
