"""M8 (plans/M8.md §5): the live function's assets match their sources, and the JavaScript tests pass.

- regions.json == what scripts/build_live_seed.py derives from src/regions.py (no hand edits, no drift);
- the excluded API names are exactly the oblast names inside the excluded files of the saved dump;
- the seed state: only the 24 units, coverage blocks [from, to, confirmed_at] with to == confirmed_at;
- the map: rebuilt from the pinned geoBoundaries file equals site_src/map_ukraine.json; 24 units + 2 grey shapes;
- map helpers (Douglas-Peucker, point-in-polygon, label point) on hand-checked shapes;
- `node --test` over netlify/live/test passes (feature parity, tree evaluator, live state, handler).
"""
import json
import subprocess
from pathlib import Path

import pytest

from scripts import build_live_seed as BLS, build_map as BM
from src import config, data, regions

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "netlify" / "live"


def test_regions_json_matches_regions_py():
    on_disk = json.loads((LIVE / "data" / "regions.json").read_text())
    assert on_disk == json.loads(json.dumps(BLS.regions_json(), ensure_ascii=False))
    assert sorted(on_disk["units"]) == sorted(regions.UNITS)
    assert len(on_disk["api_oblast_name"]) == 24
    for u, nb in on_disk["neighbours"].items():                    # symmetric border table
        assert all(u in on_disk["neighbours"][v] for v in nb)


def test_excluded_names_match_the_dump():
    d = ROOT / config.new_regime_all_types().data_path
    if not d.exists():
        pytest.fail(f"{d} missing: the saved API dump is required")
    records, _ = data.read_api_dump(d)
    names = {}
    for r in records:
        names.setdefault(r["_file_uid"], set()).add(r["location_oblast"])
    assert set(BLS.EXCLUDED_API_NAMES) == set(regions.EXCLUDED_API_UIDS)
    for uid, name in BLS.EXCLUDED_API_NAMES.items():
        assert names.get(uid, {name}) == {name}, (uid, names.get(uid))
    assert not set(BLS.EXCLUDED_API_NAMES.values()) & {v["api_oblast_name"] for v in regions.UNITS.values()}


def test_seed_state_shape():
    p = LIVE / "data" / "seed_state.json"
    if not p.exists():
        pytest.fail(f"{p} missing: run scripts/build_live_seed.py")
    s = json.loads(p.read_text())
    assert set(s["coverage"]) == set(regions.UNITS)
    assert all(len(b) == 3 and b[1] == b[2] and b[1] - b[0] == 30 * 864e5 for v in s["coverage"].values() for b in v)
    units = {r["unit"] for r in s["records"].values()}
    assert units <= set(regions.UNITS)
    assert all((r["end"] is None) == (r["endKnown"] is None) for r in s["records"].values())
    assert s["polls"] == [] and s["rotation"] == 0 and s["rejections"] == [] and s["historyFail"] == {}


def test_map_rebuild_matches_and_covers_units():
    if not BM.SRC.exists():
        pytest.fail(f"{BM.SRC} missing: download it with the command in scripts/build_map.py")
    out, text = BM.build()
    assert text == (ROOT / "site_src" / "map_ukraine.json").read_text()
    assert sorted(out["units"]) == sorted(regions.UNITS)
    assert sorted(out["grey"]) == ["crimea", "luhanska"]
    W, H = out["viewBox"][2], out["viewBox"][3]
    assert all(0 < x < W and 0 < y < H for x, y in out["labels"].values())
    assert len(text) <= BM.MAX_BYTES
    assert "OpenStreetMap" in out["attribution"]


def test_map_helpers_by_hand():
    line = [(0, 0), (1, 0.01), (2, 0), (3, 5), (4, 0)]
    assert BM.dp(line, 0.1) == [(0, 0), (2, 0), (3, 5), (4, 0)]          # tiny wiggle removed, the spike kept
    sq = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    hole = [(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]
    assert BM.inside(1, 1, [sq]) and not BM.inside(11, 1, [sq])
    assert not BM.inside(5, 5, [sq, hole])                                  # even-odd: the hole is outside
    x, y = BM.label_point([sq])
    assert abs(x - 5) < 0.3 and abs(y - 5) < 0.3                            # centre of a square
    x, y = BM.label_point([sq], [hole])
    assert not (4 <= x <= 6 and 4 <= y <= 6)                                # never on the enclave (Kyiv City case)


def test_node_suite_passes():
    r = subprocess.run(["node", "--test", str(LIVE / "test" / "lgb.test.mjs"), str(LIVE / "test" / "live.test.mjs"),
                        str(LIVE / "test" / "runner.test.mjs")], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]
    assert "# fail 0" in r.stdout or "ℹ fail 0" in r.stdout
