"""M8: train the live model with the M7 V2 recipe and export it for JavaScript inference (plans/M8.md §2).

    python scripts/export_live_model.py   # -> netlify/live/model/{model_live.json, model_live_meta.json, parity_sample.json}

Official data only; fit = eligible rows in [2022-03-23, 2026-06-29) with t + H <= 2026-06-29; early stopping on eligible
rows in [2026-06-29, 2026-07-27) with t + H <= 2026-07-27; model.PARAMS unchanged; no tuning; no API data.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import run_all, run_improve as RI  # noqa: E402
from src import config as config_mod, features, model, regions  # noqa: E402
from improve import features_plus as FP, model_plus as MP  # noqa: E402

OUT = ROOT / "netlify" / "live" / "model"


def main(out=OUT, data_path=ROOT / "data" / "official_data_en.csv"):
    cfg = config_mod.official()
    fr = run_all.build_frames(cfg, data_path)
    plus = FP.compute_plus(fr["alerts"], fr["g"], cfg.H, cfg.standing_cap, config_mod.uncertainty_zones(cfg))
    gfp = fr["gf"].merge(plus, on=["unit", "t"], how="left", validate="one_to_one")
    fit = RI.eligible(gfp, cfg.train[0], cfg.train[1], cfg.H, features.FEATURES)
    val = RI.eligible(gfp, cfg.val[0], cfg.val[1], cfg.H, features.FEATURES)
    booster = MP.train_offset(fit, val, features.FEATURES)
    best = booster.best_iteration
    dump = booster.dump_model(num_iteration=best)
    out.mkdir(parents=True, exist_ok=True)
    text = json.dumps(dump, separators=(",", ":"))
    (out / "model_live.json").write_text(text)
    meta = {
        "recipe": "M7 V2 (offset model), plans/M8.md §2", "features": features.FEATURES,
        "unit_codes": regions.units(), "categorical": ["unit_code"], "best_iteration": best,
        "offset": {"alpha": FP.ALPHA, "window_hours": 14 * 24, "h_hours": 1, "clip": FP.CLIP,
                   "prior": "expanding eligible-label rate of the unit up to tau - H; national pooled fallback"},
        "standing_cap_hours": 24, "train": [str(x) for x in cfg.train], "val": [str(x) for x in cfg.val],
        "fit_rows": len(fit), "early_stopping_rows": len(val),
        "sha256_model_json": hashlib.sha256(text.encode()).hexdigest(),
        "trained_on": "official data only (no API data)",
    }
    (out / "model_live_meta.json").write_text(json.dumps(meta, indent=2))
    # parity sample for the JS evaluator: validation rows (+ NaN-free), raw margins and probabilities from LightGBM
    rng = np.random.default_rng(20261013)
    idx = rng.choice(len(val), size=min(5000, len(val)), replace=False)
    smp = val.iloc[np.sort(idx)].reset_index(drop=True)
    X = model._matrix(smp, features.FEATURES)
    raw = booster.predict(X, num_iteration=best, raw_score=True)
    p = MP.predict_offset(booster, smp, features.FEATURES)
    rows = [{"x": [float(v) for v in X.iloc[i].to_numpy()], "offset_rate": float(smp["offset_rate"].iloc[i]),
             "raw": float(raw[i]), "p": float(p[i])} for i in range(len(smp))]
    (out / "parity_sample.json").write_text(json.dumps({"features": features.FEATURES, "rows": rows}))
    print(f"[live] model: best_iteration {best}, {len(fit):,} fit rows, {len(val):,} early-stopping rows -> {out}")
    return booster


if __name__ == "__main__":
    main()
