"""M8 parity (plans/M8.md §5): the JavaScript live inputs and offset equal the Python definitions on the real API dump
(all alert types) at many moments tau, incl. edge cases; the JS tree evaluator is covered by node tests."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from improve import live_ref
from src import config, data, features, grid

ROOT = Path(__file__).resolve().parents[1]
CFG = config.new_regime_all_types()
ZONES = config.uncertainty_zones(CFG)
GAPS = config.mask_gaps(CFG)


def ms(ts):
    return int(pd.Timestamp(ts).value // 1_000_000)


@pytest.fixture(scope="module")
def api():
    d = ROOT / CFG.data_path
    if not d.exists():
        pytest.fail(f"{d} missing: the saved API dump is required")
    records, _ = data.read_api_dump(d)
    return data.api_alerts(records, None, CFG)


def taus(al):
    rng = np.random.default_rng(8)
    lo, hi = pd.Timestamp("2026-09-21", tz="UTC"), pd.Timestamp("2026-10-12 15:00", tz="UTC")
    out = [lo + pd.Timedelta(minutes=int(m)) for m in rng.integers(0, int((hi - lo) / pd.Timedelta(minutes=1)), 18)]
    on = grid.unit_intervals(al)["kyiv_city"][2]
    o = pd.Timestamp(on[on >= np.datetime64("2026-09-25")][0]).tz_localize("UTC")
    long = al[(al.finished_at - al.started_at) > pd.Timedelta(hours=30)]
    s = long[long.started_at > pd.Timestamp("2026-09-22", tz="UTC")].started_at.iloc[0]
    out += [o, o + pd.Timedelta(seconds=1), s + pd.Timedelta(hours=24), s + pd.Timedelta(hours=24) - pd.Timedelta(seconds=1),
            pd.Timestamp("2026-10-11 12:00", tz="UTC"), pd.Timestamp("2026-10-12 09:00", tz="UTC"),
            pd.Timestamp("2026-09-13 17:30", tz="UTC")]       # inside the history-start uncertainty zone
    return out


def truncate(al, t):
    a = al[al["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


def run_js(al, ts_list, history_start=CFG.history_start, gaps=GAPS, zones=ZONES):
    payload = {"alerts": [{"unit": r.unit, "start": ms(r.started_at), "end": None if pd.isna(r.finished_at) else ms(r.finished_at)}
                          for r in al.itertuples()],
               "taus": [ms(t) for t in ts_list], "historyStart": ms(history_start),
               "gaps": [[ms(a), ms(b)] for a, b in gaps], "zones": [[ms(a), ms(b)] for a, b in zones]}
    r = subprocess.run(["node", str(ROOT / "netlify/live/test/parity_cli.mjs")], input=json.dumps(payload),
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def test_js_inputs_and_offset_match_python(api):
    ts_list = taus(api)
    js = run_js(api, ts_list)
    checked = 0
    for t, res in zip(ts_list, js):
        tr = truncate(api, t)
        f = features.build_features(tr, pd.DatetimeIndex([t]), ZONES).set_index("unit")
        off = live_ref.live_offset(tr, t, CFG.history_start, GAPS)
        for u, row in res["features"].items():
            for col in ["active_at_t"] + features.FEATURES:
                pv, jv = f.loc[u, col], row[col]
                jv = np.nan if jv == "NaN" else jv
                assert (np.isnan(pv) and np.isnan(jv)) or pv == pytest.approx(jv, abs=1e-9), (t, u, col, pv, jv)
            o, jo = off[u], res["offset"][u]
            assert (o["k"], o["n"]) == (jo["k"], jo["n"]), (t, u)
            assert (o["rate"] is None and jo["rate"] is None) or o["rate"] == pytest.approx(jo["rate"], abs=1e-12), (t, u)
            checked += 1
    assert checked == 24 * len(ts_list)


def test_kyiv_city_and_kyivska_are_separate(api):
    t = pd.Timestamp("2026-10-05 07:00", tz="UTC")
    res = run_js(api, [t])[0]["features"]
    assert res["kyiv_city"]["unit_code"] != res["kyivska"]["unit_code"]
    assert res["kyiv_city"]["neighbors_active_at_t"] in (0, 1)       # only Kyivska borders Kyiv City


def test_js_matches_python_on_official_data_at_dst_and_gap_edges():
    """Official data (the training source): DST switches (Kyiv calendar inputs) and the recording-gap edges
    (gap [08-29, 09-03), uncertainty zone to 09-04, 24 h post-gap rule), incl. one second either side."""
    cfg = config.official()
    path = ROOT / "data" / "official_data_en.csv"
    if not path.exists():
        pytest.fail(f"{path} missing: run the pipeline download first")
    al = data.load_official(path, cfg)
    al = al[al["started_at"] >= pd.Timestamp("2025-01-01", tz="UTC")]           # keeps the parity run short
    hs = pd.Timestamp("2025-01-01", tz="UTC")
    gaps, zones = config.mask_gaps(cfg), config.uncertainty_zones(cfg)
    T = lambda x: pd.Timestamp(x, tz="UTC")
    ts_list = [T("2025-03-30 00:30"), T("2025-03-30 01:00"), T("2025-03-30 01:30"), T("2025-10-26 00:00"),
               T("2025-10-26 01:00:01"), T("2026-08-28 23:59:59"), T("2026-08-29 00:00"), T("2026-09-03 00:00"),
               T("2026-09-03 23:59:59"), T("2026-09-04 00:00"), T("2026-09-04 01:00"), T("2026-09-05 06:30")]
    js = run_js(al, ts_list, hs, gaps, zones)
    for t, res in zip(ts_list, js):
        tr = truncate(al, t)
        f = features.build_features(tr, pd.DatetimeIndex([t]), zones).set_index("unit")
        off = live_ref.live_offset(tr, t, hs, gaps)
        for u, row in res["features"].items():
            for col in ["active_at_t"] + features.FEATURES:
                pv, jv = f.loc[u, col], row[col]
                jv = np.nan if jv == "NaN" else jv
                assert (np.isnan(pv) and np.isnan(jv)) or pv == pytest.approx(jv, abs=1e-9), (t, u, col, pv, jv)
            o, jo = off[u], res["offset"][u]
            assert (o["k"], o["n"]) == (jo["k"], jo["n"]), (t, u, o, jo)
            assert (o["rate"] is None and jo["rate"] is None) or o["rate"] == pytest.approx(jo["rate"], abs=1e-12), (t, u)
    hours = {t: js[i]["features"]["kyiv_city"]["hour_kyiv"] for i, t in enumerate(ts_list[:3])}
    assert list(hours.values()) == [2, 4, 4]                                   # 02:30 EET, then 04:00 / 04:30 EEST
