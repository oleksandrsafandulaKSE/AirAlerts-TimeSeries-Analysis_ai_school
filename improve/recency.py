"""M10 §B (plans/M10.md): recency-weighted training of the M7 V2 recipe (residual on top of the recent-rate offset).
Weights only on the FIT rows; the early-stopping slice is unweighted. model.PARAMS unchanged."""
import lightgbm as lgb
import numpy as np
import pandas as pd

from src import model as M

from improve.features_plus import offset_logit
from improve.model_plus import _check

HALF_LIVES = [None, 730, 365, 182]          # days; None = equal weights (the current recipe)


def recency_weights(t, F, h):
    """w = 0.5 ** (age_days / h), age_days = (F - t) / 1 day; h None -> all ones. Rows after F are an error."""
    t = pd.to_datetime(pd.Series(t), utc=True)
    age = ((F - t) / pd.Timedelta(days=1)).to_numpy(float)
    if (age < 0).any():
        raise ValueError("fit rows after the fit-slice end F")
    if h is None:
        return np.ones(len(age))
    if h <= 0:
        raise ValueError(f"half-life must be positive, got {h}")
    return 0.5 ** (age / h)


def make_datasets(fit, val, feats, weight=None):
    """The V2 datasets (model_plus.train_offset) with an optional fit weight vector."""
    _check(fit, "fit")
    _check(val, "val")
    if weight is not None and len(weight) != len(fit):
        raise ValueError("weight length differs from the fit rows")
    ds = lgb.Dataset(M._matrix(fit, feats), fit["y"].to_numpy(float), init_score=offset_logit(fit["offset_rate"]),
                     weight=None if weight is None else np.asarray(weight, float),
                     categorical_feature=M.CATEGORICAL, free_raw_data=False)
    dv = lgb.Dataset(M._matrix(val, feats), val["y"].to_numpy(float), init_score=offset_logit(val["offset_rate"]),
                     reference=ds, categorical_feature=M.CATEGORICAL)
    return ds, dv


def train_offset_weighted(fit, val, feats, weight=None):
    ds, dv = make_datasets(fit, val, feats, weight)
    return lgb.train(M.PARAMS, ds, num_boost_round=M.MAX_ROUNDS, valid_sets=[dv], valid_names=["val"],
                     callbacks=[lgb.early_stopping(M.EARLY_STOPPING, verbose=False)])


def choose_half_life(results):
    """results: {h: (ok, mean_brier)} for the FINITE candidates (each judged against equal weights by the M7 rule).
    Lowest mean Brier among passing candidates; a tie (<= 1e-6) -> the longer half-life. None passes -> None."""
    if None in results:
        raise ValueError("pass only finite candidates; equal weights are the reference")
    passing = [h for h, (ok, _) in results.items() if ok]
    if not passing:
        return None
    best = min(results[h][1] for h in passing)
    tied = [h for h in passing if results[h][1] - best <= 1e-6]
    return max(tied)
