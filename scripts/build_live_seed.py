"""M8: initial live state from the saved alerts.in.ua dump (plans/M8.md §2) + regions.json for the functions.

    python scripts/build_live_seed.py   # -> netlify/live/data/{seed_state.json, regions.json}

Records: all alert types (human decision), first seen and end known at their file's fetch time; coverage per unit =
[fetched_at - 30 d, fetched_at). Excluded units (Luhanska, Crimea, Sevastopol) are dropped.
M6 (plans/M6-site.md §2): each record keeps its alert_level as a version [[fetched_at, level]], and the typed coverage
`levelCoverage` equals `coverage` (the dump has the levels for its whole window).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config, data, regions  # noqa: E402

OUT = ROOT / "netlify" / "live" / "data"
# API oblast names of the deliberately excluded units (D-008); checked against the dump files in tests
EXCLUDED_API_NAMES = {16: "Луганська область", 29: "Автономна Республіка Крим", 30: "м. Севастополь"}


def ms(t):
    return int(pd.Timestamp(t).value // 1_000_000)


def regions_json():
    return {"units": regions.units(), "groups": {u: v["group"] for u, v in regions.UNITS.items()},
            "neighbours": {u: sorted(v) for u, v in regions.NEIGHBOURS.items()},
            "api_oblast_name": {v["api_oblast_name"]: u for u, v in regions.UNITS.items()},
            "api_uid": {u: v["api_uid"] for u, v in regions.UNITS.items()},
            "excluded_api_names": list(EXCLUDED_API_NAMES.values()),
            "official_name": {u: v["official_name"] for u, v in regions.UNITS.items()}}


def main():
    cfg = config.new_regime_all_types()
    records, manifest = data.read_api_dump(ROOT / cfg.data_path)
    fetched = {m["uid"]: m["fetched_at"] for m in manifest}
    al = data.api_alerts(records, manifest, cfg)
    uid_of = {u: v["api_uid"] for u, v in regions.UNITS.items()}
    raw_by_id = {str(r["id"]): r for r in records}
    state = {"records": {}, "coverage": {}, "polls": [], "rotation": 0, "historyStart": ms(cfg.history_start),
             "rejections": [], "historyFail": {}}
    for r in al.itertuples():
        f = ms(fetched[uid_of[r.unit]])
        raw = raw_by_id[r.alert_id]
        state["records"][r.alert_id] = {
            "id": r.alert_id, "unit": r.unit, "level": r.level, "alert_type": raw["alert_type"],
            "start": ms(r.started_at), "end": None if pd.isna(r.finished_at) else ms(r.finished_at),
            "updated": ms(pd.Timestamp(raw["updated_at"])), "firstSeen": f,
            "endKnown": None if pd.isna(r.finished_at) else f, "endSource": None if pd.isna(r.finished_at) else "history",
            "absent": [], "levels": [[f, r.alert_level]] if r.alert_level in ("yellow", "red") else []}
    for u in regions.units():
        f = ms(fetched[uid_of[u]])
        state["coverage"][u] = [[f - 30 * 24 * 3600 * 1000, f, f]]   # [from, to, confirmed at]
    state["levelCoverage"] = {u: [list(b) for b in v] for u, v in state["coverage"].items()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "seed_state.json").write_text(json.dumps(state, separators=(",", ":")))
    (OUT / "regions.json").write_text(json.dumps(regions_json(), ensure_ascii=False, indent=1))
    print(f"[seed] {len(state['records']):,} records, 24 units, historyStart {cfg.history_start} -> {OUT}")


if __name__ == "__main__":
    main()
