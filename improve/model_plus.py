"""M7 models (plans/M7.md §2): the headline recipe (src.model, unchanged) and a residual model on top of the causal
recent-rate offset: p = sigmoid(offset + residual_margin)."""
import lightgbm as lgb
import numpy as np

from src import model as M
from src.data import DataQualityError

from improve.features_plus import offset_logit


def _check(df, name):
    if df["y"].isna().any():
        raise DataQualityError(f"{name}: unknown labels")
    if df["offset_rate"].isna().any():
        raise DataQualityError(f"{name}: missing offset")


def train_plain(fit, val, feats):
    return M.train(fit, val, feats)[0]


def predict_plain(booster, df, feats):
    return booster.predict(M._matrix(df, feats), num_iteration=booster.best_iteration)


def train_offset(fit, val, feats):
    """LightGBM learns the residual on top of logit(r(t)); fit and early-stopping sets both carry init_score."""
    _check(fit, "fit")
    _check(val, "val")
    ds = lgb.Dataset(M._matrix(fit, feats), fit["y"].to_numpy(float), init_score=offset_logit(fit["offset_rate"]),
                     categorical_feature=M.CATEGORICAL, free_raw_data=False)
    dv = lgb.Dataset(M._matrix(val, feats), val["y"].to_numpy(float), init_score=offset_logit(val["offset_rate"]),
                     reference=ds, categorical_feature=M.CATEGORICAL)
    return lgb.train(M.PARAMS, ds, num_boost_round=M.MAX_ROUNDS, valid_sets=[dv], valid_names=["val"],
                     callbacks=[lgb.early_stopping(M.EARLY_STOPPING, verbose=False)])


def predict_offset(booster, df, feats, num_iteration=None):
    if df["offset_rate"].isna().any():
        raise DataQualityError("missing offset at prediction time")
    it = booster.best_iteration if num_iteration is None else num_iteration
    raw = booster.predict(M._matrix(df, feats), num_iteration=it, raw_score=True) if it != 0 else np.zeros(len(df))
    z = offset_logit(df["offset_rate"]) + raw
    return 1.0 / (1.0 + np.exp(-z))
