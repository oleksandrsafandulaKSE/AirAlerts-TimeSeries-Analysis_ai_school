"""M6-site (plans/M6-site.md §2, §4, §6): the seed carries alert levels and typed coverage; the page shows yellow/red only
in the oblast tooltip, card and the "What kind of alert?" tab (D-044, amends D-036: never the main map colours); the built site embeds the same template code."""
import json
import re
from pathlib import Path

import pytest

from scripts import build_live_seed as BLS
from src import config, regions

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "site_src" / "template.html").read_text()


def test_seed_keeps_levels_and_typed_coverage(tmp_path, monkeypatch):
    if not (ROOT / config.new_regime_all_types().data_path).exists():
        pytest.fail("the saved API dump is required")
    monkeypatch.setattr(BLS, "OUT", tmp_path)                       # never overwrite the real (gitignored) seed
    BLS.main()
    s = json.loads((tmp_path / "seed_state.json").read_text())
    assert s["levelCoverage"] == s["coverage"] and set(s["levelCoverage"]) == set(regions.UNITS)
    levels = [r["levels"] for r in s["records"].values()]
    assert all(len(v) == 1 and v[0][1] in ("yellow", "red") for v in levels)
    assert all(v[0][0] == r["firstSeen"] for v, r in zip(levels, s["records"].values()))   # known from the fetch time
    n = {lv: sum(v[0][1] == lv for v in levels) for lv in ("yellow", "red")}
    print(f"[seed] {len(levels):,} records with a level: {n}")
    assert n["yellow"] > n["red"] > 0


def _function(name):
    i = TEMPLATE.index(f"function {name}(")
    j = TEMPLATE.index("\nfunction ", i + 1)
    return TEMPLATE[i:j]


def test_typed_and_kind_never_colour_the_main_map():
    """D-044 (amends D-036, plans/M13.md): yellow/red appear in the tooltip, the card and the "What kind of alert?" tab;
    the main map's colours, labels and legend never use a typed forecast or the kind rule."""
    assert "kindWords(kindOf(u))" in _function("tipHtml") and "kindWords(kindOf(u))" in _function("cardHtml")
    assert "typedValue(" in _function("cardHtml")
    draw = _function("drawLive")
    main_view = draw.replace("tip: u => tipHtml(u)", "").replace("cardHtml(live.sel)", "")
    assert not re.search(r"typed|kind", main_view), "the map fill, labels and legend must not show yellow/red"
    i = TEMPLATE.index('<section class="tab" id="tab-map"')
    map_tab = TEMPLATE[i:TEMPLATE.index("</section>", i)]
    assert not re.search(r"yellow|drones|missiles", map_tab, re.I)
    assert 'id="tab-kind"' in TEMPLATE


def test_built_site_has_the_typed_block():
    site = (ROOT / "site" / "index.html").read_text()
    start, end = "/* typed-block:start", "/* typed-block:end */"
    assert site[site.index(start):site.index(end)] == TEMPLATE[TEMPLATE.index(start):TEMPLATE.index(end)]
