"""Fabricated 1-hour ends in the official file: counts, mechanism check, oblast-level impact. Read-only.
Run from the repo root: .venv/bin/python <this file>"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path.cwd()))
from src import config, regions  # noqa: E402
from src.grid import _covered, unit_intervals  # noqa: E402

cfg = config.official()
OUT = Path("data/derived/fake1h")
OUT.mkdir(parents=True, exist_ok=True)
raw = pd.read_csv("data/official_data_en.csv", dtype=str, keep_default_na=False)
d = raw.drop_duplicates().copy()
print(f"raw {len(raw):,} -> dedup {len(d):,}")
d = d[~d["oblast"].isin(regions.EXCLUDED)].copy()
d["unit"] = d["oblast"].map(regions.unit_from_official)
d["s"] = pd.to_datetime(d["started_at"], utc=True, format="ISO8601")
d["e"] = pd.to_datetime(d["finished_at"].replace("", None), utc=True, format="ISO8601")
d["dur"] = (d["e"] - d["s"]).dt.total_seconds()
d["loc"] = d["oblast"] + "|" + d["raion"] + "|" + d["hromada"] + "|" + d["level"]
print(f"after excluding {regions.EXCLUDED}: {len(d):,} alerts")

# 1. spike at exactly 3600 s
print("\n== 1. duration spike ==")
for sec in (3598, 3599, 3600, 3601, 3602):
    print(f"  dur == {sec}s: {int((d.dur == sec).sum())}")
near = d[(d.dur >= 3540) & (d.dur <= 3660) & (d.dur != 3600)]
per_sec = len(near) / 120
n3600 = int((d.dur == 3600).sum())
print(f"  59-61 min excl. 3600: {len(near)} -> {per_sec:.1f}/s expected at 3600; excess = {n3600 - per_sec:.0f}")
f = d[d.dur == 3600].copy()
print("  by year:", f.s.dt.year.value_counts().sort_index().to_dict())
print("  by level:", f.level.value_counts().to_dict())
print("  by unit (top 8):", f.unit.value_counts().head(8).to_dict())

# 2. mechanism: next start at the SAME location must be > start + 3h for an imputed end
print("\n== 2. next start at same location ==")
d = d.sort_values(["loc", "s"])
d["next_s_loc"] = d.groupby("loc")["s"].shift(-1)
d["gap_from_start_h"] = (d["next_s_loc"] - d["s"]).dt.total_seconds() / 3600
f = d[d.dur == 3600]
g = d[(d.dur >= 3540) & (d.dur <= 3660) & (d.dur != 3600)]
for name, x in (("exact 3600 s", f), ("other 59-61 min", g)):
    gh = x["gap_from_start_h"]
    print(f"  {name}: n={len(x)}, next same-location start known for {gh.notna().sum()}; "
          f"share > 3h after start = {(gh > 3).mean():.3f}; share <= 3h = {(gh <= 3).mean():.3f}; "
          f"median gap from fake end = {(gh - 1).median():.1f} h")
print("  exact-3600 with next same-location start <= 3h after start:", int((f.gap_from_start_h <= 3).sum()))

# 3. oblast-level impact under the project's own D-020 union
print("\n== 3. oblast-level impact ==")
al = pd.DataFrame({"unit": d["unit"], "level": d["level"], "started_at": d["s"], "finished_at": d["e"],
                   "alert_level": ""})
ivs = unit_intervals(al, cfg.standing_cap, "any")
naive = lambda ts: ts.tz_convert("UTC").tz_localize(None).to_datetime64()  # noqa: E731
rows = []
for _, r in d[d.dur == 3600].iterrows():
    ms, me, on = ivs[r.unit]
    fe = naive(r.e)
    ends_unit = bool(np.isin(fe, me))  # the fake end is where the oblast's merged interval ends
    nxt = on[on > fe]
    rows.append({"unit": r.unit, "s": r.s, "fake_end": r.e, "ends_unit_interval": ends_unit,
                 "next_unit_onset_h": (nxt[0] - fe) / np.timedelta64(1, "h") if len(nxt) else np.nan})
imp = pd.DataFrame(rows)
print(f"  fake ends that END the oblast's merged interval: {int(imp.ends_unit_interval.sum())} / {len(imp)}")
e = imp[imp.ends_unit_interval]
print(f"  for those, time to next oblast onset: median {e.next_unit_onset_h.median():.1f} h; "
      f"<=1h {(e.next_unit_onset_h <= 1).mean():.3f}; <=2h {(e.next_unit_onset_h <= 2).mean():.3f}")

# real-time counterfactual: with no all-clear, the alert stays active under D-020 until start + 24h.
# phantom-clear hours = grid hours t in [fake_end, start+24h) where the data says the oblast is clear.
phantom = []
for _, r in e.iterrows():
    ms, me, on = ivs[r.unit]
    t0, t1 = r.fake_end.ceil("h"), r.s + cfg.standing_cap
    ts = pd.date_range(t0, t1, freq="h", inclusive="left", tz="UTC")
    if len(ts) == 0:
        continue
    tn = ts.tz_localize(None).to_numpy("datetime64[ns]")
    clear = ~_covered(tn, ms, me)
    for t, c in zip(ts, clear):
        if c:
            phantom.append({"unit": r.unit, "t": t, "quiet_guaranteed": t + cfg.H <= r.s + pd.Timedelta(hours=3),
                            "mins_since_fake_end": (t - r.fake_end).total_seconds() / 60})
ph = pd.DataFrame(phantom).drop_duplicates(["unit", "t"])
print(f"  phantom-clear (unit, hour) rows, whole history: {len(ph):,}; "
      f"of which label window inside the guaranteed-quiet 3h: {int(ph.quiet_guaranteed.sum())}")

# 4. which of those rows were actually scored in validation / test
print("\n== 4. scored rows touched ==")
for split, fn in (("val", "reports/official/val_predictions.csv"), ("test", "reports/official/test_predictions.csv")):
    p = pd.read_csv(fn)
    p["t"] = pd.to_datetime(p["t"], utc=True)
    sc = p[p.status == "scored"] if "status" in p else p
    m = sc.merge(ph, on=["unit", "t"], how="inner")
    print(f"  {split}: scored rows {len(sc):,}; phantom-clear among them {len(m)} "
          f"({len(m) / len(sc):.2%}); positives among those {int(m.y.sum())}; units {m.unit.value_counts().to_dict()}")
    if len(m):
        print(f"    mean y on phantom rows {m.y.mean():.3f} vs all scored {sc.y.mean():.3f}; "
              f"guaranteed-quiet {int(m.quiet_guaranteed.sum())}")
for split, (a, b) in (("train", cfg.train), ("val", cfg.val), ("test", cfg.test)):
    n = int(((imp.s >= a) & (imp.s < b)).sum())
    print(f"  fake-end alerts starting in {split}: {n}")
imp.to_csv(OUT / "fake_1h_alerts.csv", index=False)
ph.to_csv(OUT / "phantom_clear_rows.csv", index=False)
