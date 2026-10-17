"""M6-site (plans/M6-site.md §2, §4, §6): the seed carries alert levels and typed coverage; the page shows yellow/red only
in the oblast tooltip and card (D-036: never the main view); the built site embeds the same template code."""
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


def test_typed_only_in_tooltip_and_card():
    assert "typedTipHtml(x.typed, F.typed)" in _function("liveTip")
    assert "typedCardHtml(x.typed, F.typed" in _function("liveCard")
    draw = _function("drawLive")
    main_view = draw.replace("tip: u => liveTip(u, F)", "").replace("liveCard(u, F)", "").replace("liveCard(live.sel, F)", "")
    assert "typed" not in main_view, "the map fill, labels, legend, top list and table must not show typed forecasts"
    # the live section's static header and text do not mention typed forecasts (the study section further down has its
    # own pre-existing exploratory yellow/red analysis, which is not the live view)
    i = TEMPLATE.index('<section class="live" id="live">')
    live_section = TEMPLATE[i:TEMPLATE.index("</section>", i)]
    assert not re.search(r"yellow|drones|missiles", live_section, re.I)


def test_built_site_has_the_typed_block():
    site = (ROOT / "site" / "index.html").read_text()
    start, end = "/* typed-block:start", "/* typed-block:end */"
    assert site[site.index(start):site.index(end)] == TEMPLATE[TEMPLATE.index(start):TEMPLATE.index(end)]
