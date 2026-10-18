"""M9 extras (post-hoc analysis of FROZEN predictions; no refit).

  python scripts/run_extras.py --facts   # data-quality pins + M1-style lines only (no test statistics)
  python scripts/run_extras.py           # + §B CI / DM, §C CORP, §D calibration CIs on validation AND test

Test-period outputs are post-hoc analysis of frozen predictions, approved by the human (plans/M9.md §0). They never
change the headline, and no model, calibration or feature decision may be taken from them.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from extras import corp, data_quality as dq, uncertainty as U  # noqa: E402
from src import config, data  # noqa: E402

OUT = ROOT / "reports" / "extras"
INPUTS = ["data/official_data_en.csv", "reports/official/test_predictions.csv",
          "reports/official/val_predictions.csv", "reports/improve/validation_predictions.csv",
          "reports/official/metrics.csv", "reports/official/metrics_validation.csv",
          "reports/official/calibration_in_the_large.csv"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def facts():
    cfg = config.official()
    path = ROOT / "data" / "official_data_en.csv"
    if not path.exists():
        raise data.DataQualityError(f"{path} missing: run scripts/run_all.py --config official once")
    alerts = data.load_official(path, cfg)
    counts = dq.check_exact_durations(alerts)  # raises if a pin moved
    pre = alerts[alerts["started_at"] < cfg.test[0]]
    for sec, label in ((3600, "exactly-3600 s durations (includes suspected parser-imputed ends)"),
                       (1800, "exactly-1800 s durations (D-010, kept)")):
        c, cp = counts[sec], dq.exact_duration_counts(pre, sec)
        print(f"[extras] {label}: {c['total']} by level {c['by_level']}; before the test start: {cp['total']}")
    ratios = dq.check_onset_collapse(alerts, cfg.standing_cap)  # raises on collapse
    print(f"[extras] onset-collapse check (Dec-2025 reform): PASS, lowest late/early ratio "
          f"{ratios.ratio.min():.3f} ({ratios.loc[ratios.ratio.idxmin(), 'unit']})")
    return counts, ratios


def check_reproduces(df, metrics_csv, split):
    m = pd.read_csv(ROOT / metrics_csv)
    want = float(m[(m.baseline == "model") & (m.group == "overall")]["brier_skill_vs_recent"].iloc[0])
    got = U.bss(df)
    if abs(got - want) > 1e-12:
        raise data.DataQualityError(f"{split}: BSS {got} does not reproduce {metrics_csv} ({want})")
    return got


def check_citl(citl):
    ref = pd.read_csv(ROOT / "reports/official/calibration_in_the_large.csv")
    for _, r in citl.iterrows():
        want = ref[(ref.predictor == r.predictor) & (ref.group == r.group)]["pred_minus_obs"]
        if len(want) != 1 or abs(float(want.iloc[0]) - r.pred_minus_obs) > 1e-12:
            raise data.DataQualityError(f"calibration-in-the-large differs for {r.predictor}/{r.group}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", action="store_true", help="data-quality pins only")
    args = ap.parse_args()
    for p in (INPUTS[:1] if args.facts else INPUTS):  # --facts needs only the data file
        if not (ROOT / p).exists():
            raise data.DataQualityError(f"missing input {p}")
    counts, ratios = facts()
    if args.facts:
        return
    OUT.mkdir(parents=True, exist_ok=True)
    splits = {"validation": U.load_val(ROOT), "test_posthoc": U.load_test(ROOT)}
    check_reproduces(splits["validation"], "reports/official/metrics_validation.csv", "validation")
    check_reproduces(splits["test_posthoc"], "reports/official/metrics.csv", "test")
    ci, dm, cp, ct = [], [], [], []
    for split, df in splits.items():
        print(f"[extras] {split}: {len(df):,} rows, {df.t.nunique()} hours, {df.t.min()} -> {df.t.max()}, "
              f"base rate {df.y.mean():.4f}")
        for scheme in U.SCHEMES:
            r = U.bootstrap_bss(df, scheme)
            ci.append({"split": split, "primary": scheme == U.PRIMARY, **r})
            print(f"[extras]   BSS {r['bss']:+.4f}  95% CI [{r['ci_low']:+.4f}, {r['ci_high']:+.4f}]  "
                  f"({scheme}, {r['blocks']} blocks{'; FEW BLOCKS: interval unreliable' if r['few_blocks_unreliable'] else ''})")
        d = U.dm_test(df)
        dm.append({"split": split, **d})
        print(f"[extras]   DM z (NW24) {d['z_nw24']:+.2f} p {d['p_nw24']:.3f}; (NW72) {d['z_nw72']:+.2f} "
              f"p {d['p_nw72']:.3f}; iid rows z {d['z_iid_rows']:+.2f} (ignores clustering)")
        tab = corp.corp_table(df, split)
        cp.append(tab)
        c = U.citl_bootstrap(df)
        c.insert(0, "split", split)
        ct.append(c)
        bands = corp.curve_bands(df)
        corp.plot(bands, OUT / f"corp_{split}.png",
                  f"CORP reliability, {split.replace('_', ' ')} (H = 1"
                  + (", post-hoc analysis of frozen predictions)" if split != "validation" else ")"))
    check_citl(ct[1].drop(columns="split"))
    pd.DataFrame(ci).to_csv(OUT / "bss_ci.csv", index=False)
    pd.DataFrame(dm).to_csv(OUT / "dm_test.csv", index=False)
    pd.concat(cp).to_csv(OUT / "corp.csv", index=False)
    pd.concat(ct).to_csv(OUT / "calibration_ci.csv", index=False)
    ratios.to_csv(OUT / "onset_collapse_check.csv", index=False)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "extras", "scripts/run_extras.py"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip() != ""
    code = hashlib.sha256()
    for f in sorted((ROOT / "extras").glob("*.py")) + [ROOT / "scripts" / "run_extras.py"]:
        code.update(f.name.encode())
        code.update(f.read_bytes())
    meta = {"label": "post-hoc analysis of frozen predictions (M9; plans/M9.md §0)", "git_commit": commit or None,
            "git_dirty_extras_code": dirty, "extras_code_sha256": code.hexdigest(),
            "inputs_sha256": {p: sha(p) for p in INPUTS}, "seed": U.SEED, "n_boot": U.B, "nw_lags": list(U.NW_LAGS),
            "primary_scheme": U.PRIMARY, "exact_duration_pins": {str(k): v for k, v in counts.items()}}
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"[extras] wrote {OUT}")


if __name__ == "__main__":
    main()
