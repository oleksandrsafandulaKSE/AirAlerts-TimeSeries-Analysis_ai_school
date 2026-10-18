"""Follow-up to analyze.py (run that first): test-score sensitivity, knowability of fake ends, 30-min check.
Read-only on the already-scored test predictions; no refit, no model or baseline change.
Run from the repo root: .venv/bin/python plans/notes/fabricated_1h_ends/followup.py"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path.cwd()))
from src import regions  # noqa: E402

OUT = Path("data/derived/fake1h")
ph = pd.read_csv(OUT / "phantom_clear_rows.csv")
ph["t"] = pd.to_datetime(ph.t, utc=True)
p = pd.read_csv("reports/official/test_predictions.csv")
p["t"] = pd.to_datetime(p.t, utc=True)
sc = p[p.status == "scored"].merge(ph[["unit", "t"]].assign(ph=1), on=["unit", "t"], how="left").fillna({"ph": 0})

print("== test Brier skill vs recent-rate, with and without phantom-clear rows (post-hoc sensitivity) ==")
for name, x in (("all scored", sc), ("phantom rows", sc[sc.ph == 1]), ("excluding phantom", sc[sc.ph == 0])):
    bm, br = ((x.p_model - x.y) ** 2).mean(), ((x.p_recent_rate - x.y) ** 2).mean()
    print(f"  {name}: n={len(x)} brier model {bm:.5f} recent {br:.5f} BSS {1 - bm / br:+.4f}")

raw = pd.read_csv("data/official_data_en.csv", dtype=str, keep_default_na=False).drop_duplicates()
raw = raw[~raw.oblast.isin(regions.EXCLUDED)].copy()
raw["unit"] = raw.oblast.map(regions.unit_from_official)
raw["s"] = pd.to_datetime(raw.started_at, utc=True, format="ISO8601")
raw["e"] = pd.to_datetime(raw.finished_at.replace("", None), utc=True, format="ISO8601")
raw["dur"] = (raw.e - raw.s).dt.total_seconds()
raw["loc"] = raw.oblast + "|" + raw.raion + "|" + raw.hromada + "|" + raw.level
raw = raw.sort_values(["loc", "s"])
raw["next_s"] = raw.groupby("loc").s.shift(-1)  # the parser writes a fake end only when this start arrives

print("\n== when does a fake end become known? ==")
f = raw[raw.dur == 3600][["unit", "s", "e", "next_s"]].rename(columns={"e": "fake_end", "next_s": "known_at"})
m = pd.merge_asof(ph.sort_values("t"), f.sort_values("fake_end"), left_on="t", right_on="fake_end",
                  by="unit", direction="backward")
m["end_unknown_at_t"] = m.t < m.known_at
ts = m.merge(p[p.status == "scored"][["unit", "t"]], on=["unit", "t"])
print(f"  phantom rows, whole history {len(m)}: end not yet written at t = {int(m.end_unknown_at_t.sum())} "
      f"({m.end_unknown_at_t.mean():.1%})")
print(f"  scored test phantom rows {len(ts)}: end not yet written at t = {int(ts.end_unknown_at_t.sum())}")
print("  whole history by unit (top 6):", m.unit.value_counts().head(6).to_dict())

print("\n== D-010 side check: exactly-1800 s durations ==")
raw["gap"] = (raw.next_s - raw.s).dt.total_seconds() / 3600
near = raw[(raw.dur >= 1740) & (raw.dur <= 1860)]
print(f"  exactly 1800 s: {int((raw.dur == 1800).sum())}; other 29-31 min per second: "
      f"{(near.dur != 1800).sum() / 120:.1f} (no spike if 1800 count is not far above this)")
for nm, x in (("exact 1800", near[near.dur == 1800]), ("other 29-31 min", near[near.dur != 1800])):
    print(f"  {nm}: n={len(x)}, share with next same-location start > 3h after start {(x.gap > 3).mean():.3f}")
