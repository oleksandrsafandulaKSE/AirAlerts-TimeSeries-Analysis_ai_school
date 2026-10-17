"""M6-site parity (plans/M6-site.md §6): the JavaScript per-type (yellow / red) rolling recent-rate baseline and per-type
state on the live site equal the Python definitions on the real API dump (all alert types, as M8) at many moments tau.

Python reference: `improve/live_ref.live_offset` (the M8 offset definition: 14-day window of eligible, already-known
labels, shrunk toward the unit's expanding rate) run on the dump restricted to ONE alert level, so a typed onset is the
start of a merged interval of that level and a label hour is masked only while THAT level is active."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from improve import live_ref
from src import config, data, grid, regions

ROOT = Path(__file__).resolve().parents[1]
CFG = config.new_regime_all_types()
ZONES = config.uncertainty_zones(CFG)
GAPS = config.mask_gaps(CFG)
H = pd.Timedelta(hours=1)


def ms(ts):
    return int(pd.Timestamp(ts).value // 1_000_000)


@pytest.fixture(scope="module")
def api():
    d = ROOT / CFG.data_path
    if not d.exists():
        pytest.fail(f"{d} missing: the saved API dump is required")
    records, _ = data.read_api_dump(d)
    al = data.api_alerts(records, None, CFG)
    raw = {str(r["id"]): r["alert_type"] for r in records}
    al["alert_type"] = al["alert_id"].map(raw)
    assert al["alert_type"].notna().all() and set(al["alert_level"]) == {"yellow", "red"}
    return al


def truncate(al, t):
    a = al[al["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


def pinned(al):
    """Edge moments: a red onset inside a yellow interval, a typed onset at tau and at tau + 1 h, the 14-day window's
    lower and upper edges, an alert exactly 24 h old (+- 1 s), and the history-start zone."""
    out = []
    y, r = al[al.alert_level == "yellow"], al[al.alert_level == "red"]
    yi = grid.unit_intervals(y)
    red_in_yellow = None
    for row in r.sort_values("started_at").itertuples():
        if row.started_at < pd.Timestamp("2026-09-20", tz="UTC") or row.unit not in yi or pd.isna(row.finished_at):
            continue
        if row.finished_at - row.started_at > H:          # short, and the only red of its unit within +- 4 h
            continue
        near = r[(r.unit == row.unit) & (r.alert_id != row.alert_id)
                 & (r.started_at < row.started_at + 4 * H) & (r.finished_at.fillna(row.started_at + 4 * H) > row.started_at - 4 * H)]
        if len(near):
            continue
        ms_, me_ = yi[row.unit][0], yi[row.unit][1]
        s = np.datetime64(row.started_at.tz_convert("UTC").tz_localize(None))
        i = np.searchsorted(ms_, s, side="right") - 1
        if i >= 0 and s < me_[i] and s > ms_[i]:
            red_in_yellow = row
            break
    assert red_in_yellow is not None, "the dump has red onsets inside yellow intervals (31% per M6-definition)"
    out += [red_in_yellow.started_at + 3 * H]
    on = pd.Series(yi["kyiv_city"][2]).dt.tz_localize("UTC")
    o = on[(on >= pd.Timestamp("2026-09-28", tz="UTC")) & (on.dt.minute != 0)].iloc[0]       # a non-hour-aligned onset
    s0 = o.floor("h")                                                                        # label hour holding it
    out += [o, o - H, s0 + pd.Timedelta(days=14), s0 + pd.Timedelta(days=14) + pd.Timedelta(seconds=1),
            s0 + H, s0 + H - pd.Timedelta(seconds=1)]
    long = y[(y.finished_at - y.started_at) > pd.Timedelta(hours=30)]
    s = long[long.started_at > pd.Timestamp("2026-09-22", tz="UTC")].started_at.iloc[0]
    out += [s + pd.Timedelta(hours=24), s + pd.Timedelta(hours=24) - pd.Timedelta(seconds=1),
            s + pd.Timedelta(hours=24) + pd.Timedelta(seconds=1), pd.Timestamp("2026-09-13 17:30", tz="UTC")]
    return out, red_in_yellow


def taus(al):
    rng = np.random.default_rng(11)
    lo, hi = pd.Timestamp("2026-09-21", tz="UTC"), pd.Timestamp("2026-10-12 15:00", tz="UTC")
    rand = [lo + pd.Timedelta(minutes=int(m)) for m in rng.integers(0, int((hi - lo) / pd.Timedelta(minutes=1)), 18)]
    pin, _ = pinned(al)
    return rand + pin


def run_js(al, ts_list):
    payload = {"records": [{"id": r.alert_id, "unit": r.unit, "alert_type": r.alert_type, "level": r.alert_level,
                            "start": ms(r.started_at), "end": None if pd.isna(r.finished_at) else ms(r.finished_at)}
                           for r in al.itertuples()],
               "taus": [ms(t) for t in ts_list], "historyStart": ms(CFG.history_start),
               "zones": [[ms(a), ms(b)] for a, b in ZONES]}
    r = subprocess.run(["node", str(ROOT / "netlify/live/test/typed_parity_cli.mjs")], input=json.dumps(payload),
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def expected_state(tr_level, unit, t, rate):
    iv = grid.unit_intervals(tr_level).get(unit)
    x = np.datetime64(t.tz_convert("UTC").tz_localize(None))
    if iv is not None:
        i = np.searchsorted(iv[0], x, side="right") - 1
        if i >= 0 and x < iv[1][i]:
            return "level_active"
    if any(a <= t < b for a, b in ZONES) or rate is None:     # no eligible label anywhere yet -> no rate (as M8)
        return "data_gap"
    return "forecast"


def test_js_typed_baseline_matches_python(api):
    ts_list = taus(api)
    js = run_js(api, ts_list)
    units = regions.units()
    checked, states = 0, {}
    for t, res in zip(ts_list, js):
        assert res["meta"]["alert_types"] == ["air_raid", "artillery_shelling", "urban_fights", "chemical", "nuclear"]
        for level in ("yellow", "red"):
            tr = truncate(api[api.alert_level == level], t)
            off = live_ref.live_offset(tr, t, CFG.history_start, GAPS, units=units)
            for u in units:
                o, j = off[u], res["units"][u][level]
                assert (o["k"], o["n"]) == (j["recent_k"], j["recent_n"]), (t, u, level)
                assert (o["rate"] is None and j["p_baseline"] is None) or o["rate"] == pytest.approx(j["p_baseline"], abs=1e-12), (t, u, level)
                st = expected_state(tr, u, t, o["rate"])
                assert j["state"] == st, (t, u, level, j["state"], st)
                assert (j["p"] is None) == (st != "forecast") and (j["p"] is None or j["p"] == j["p_baseline"])
                states[st] = states.get(st, 0) + 1
                checked += 1
    assert checked == 2 * 24 * len(ts_list)
    assert states.get("level_active", 0) > 0 and states.get("data_gap", 0) > 0 and states.get("forecast", 0) > 0
    print(f"[typed parity] {len(ts_list)} moments x 24 units x 2 levels; states {states}")


def test_red_onset_during_yellow_counts_for_red(api):
    """The pinned witness: a red onset inside a yellow interval is a red onset (per-type eligibility, M6-definition)."""
    _, row = pinned(api)
    t = row.started_at + 3 * H
    js = run_js(api, [t])[0]["units"][row.unit]["red"]
    without = api[api.alert_id != row.alert_id]
    js_without = run_js(without, [t])[0]["units"][row.unit]["red"]
    assert js["recent_k"] == js_without["recent_k"] + 1, (js, js_without)
