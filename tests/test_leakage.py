"""Truncation-invariance leakage test (ts-leakage-audit) on the REAL official data, with a negative control."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import config, data, evaluate, features as F, grid, regions

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "official_data_en.csv"
CFG = config.official()
ZONES = config.uncertainty_zones(CFG)
NB = {"A": {"B"}, "B": {"A"}}


def truncate(alerts, t):
    """Alerts as known at t: drop starts after t; ends after t are not yet known."""
    a = alerts[alerts["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


def truncation_check(feature_fn, alerts, times, units=None, columns=None):
    """Mismatches (t, unit, column) between features from full data and from data truncated at t."""
    times = pd.DatetimeIndex(times)
    full = feature_fn(alerts, times).set_index(["unit", "t"])
    columns = [c for c in full.columns] if columns is None else columns
    bad = []
    for t in times:
        cut = feature_fn(truncate(alerts, t), pd.DatetimeIndex([t])).set_index(["unit", "t"])
        for u in (full.index.get_level_values("unit").unique() if units is None else units):
            for c in columns:
                x, y = full.loc[(u, t), c], cut.loc[(u, t), c]
                if not ((pd.isna(x) and pd.isna(y)) or x == y):
                    bad.append((t, u, c))
    return bad


def real_features(alerts, times):
    return F.build_features(alerts, times, ZONES)


def leaky_features(alerts, times, unit_list=None):
    """Negative control. (a) uses an end not known at t; (b) a centred window that reads (t, t+90min]."""
    ivs = grid.unit_intervals(alerts)
    rows = []
    for t in times:
        for u in (regions.units() if unit_list is None else unit_list):
            g = alerts[alerts.unit == u]
            act = g[(g.started_at <= t) & ~(g.finished_at <= t)]
            dur = (act.finished_at - act.started_at).dt.total_seconds() / 60
            on = pd.to_datetime(ivs[u][2]).tz_localize("UTC") if u in ivs else pd.DatetimeIndex([], tz="UTC")
            rows.append({"unit": u, "t": t,
                         "current_alert_final_minutes": dur.max() if dur.notna().any() else np.nan,
                         "onsets_centered_3h": int(((on > t - pd.Timedelta(minutes=90)) &
                                                    (on <= t + pd.Timedelta(minutes=90))).sum())})
    return pd.DataFrame(rows)


# ---------------- fixed toy cases (M2 decision 7) ----------------

def toy(rows):
    cols = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
    df = pd.DataFrame([{"source": "t", "alert_id": str(i), "unit": u, "level": "hromada",
                        "started_at": pd.Timestamp(s, tz="UTC"),
                        "finished_at": pd.Timestamp(e, tz="UTC") if e else pd.NaT, "alert_level": ""}
                       for i, (u, s, e) in enumerate(rows)], columns=cols)
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


def toy_features(alerts, times):
    return F.build_features(alerts, times, unit_list=["A", "B"], neighbours=NB)


@pytest.mark.parametrize("name,rows,t", [
    ("touching", [("A", "2024-01-10 01:00", "2024-01-10 02:00"), ("A", "2024-01-10 02:00", "2024-01-10 03:00")],
     ["2024-01-10 02:00", "2024-01-10 03:00", "2024-01-10 04:00"]),
    ("extended_after_t", [("A", "2024-01-10 01:00", "2024-01-10 03:00"), ("A", "2024-01-10 02:30", "2024-01-10 06:00")],
     ["2024-01-10 02:00", "2024-01-10 03:00", "2024-01-10 04:00", "2024-01-10 07:00"]),
    ("finished_eq_t", [("A", "2024-01-10 01:00", "2024-01-10 03:00")], ["2024-01-10 03:00"]),
    ("finished_t_plus_1min", [("A", "2024-01-10 01:00", "2024-01-10 03:01")], ["2024-01-10 03:00"]),
    ("exactly_24h", [("A", "2024-01-10 01:00", "2024-01-11 01:00")],
     ["2024-01-11 00:00", "2024-01-11 01:00", "2024-01-11 02:00"]),
    ("t_at_cap", [("A", "2024-01-10 01:00", "2024-01-13 00:00"), ("B", "2024-01-10 05:00", "2024-01-10 06:00")],
     ["2024-01-11 00:00", "2024-01-11 01:00", "2024-01-11 02:00"]),
])
def test_fixed_truncation_cases(name, rows, t):
    times = pd.DatetimeIndex([pd.Timestamp(x, tz="UTC") for x in t])
    assert truncation_check(toy_features, toy(rows), times) == [], name


def test_negative_control_catches_toy():
    a = toy([("A", "2024-01-10 01:00", "2024-01-13 00:00"), ("B", "2024-01-10 02:20", "2024-01-10 02:40")])
    times = pd.DatetimeIndex([pd.Timestamp("2024-01-10 02:00", tz="UTC")])
    leaky = lambda al, ts: leaky_features(al, ts, ["A", "B"])  # noqa: E731
    assert set(truncation_check(leaky, a, times)) == {
        (times[0], "A", "current_alert_final_minutes"), (times[0], "B", "onsets_centered_3h")}


# ---------------- real data ----------------

@pytest.fixture(scope="module")
def real():
    if not DATA.exists():
        pytest.fail(f"{DATA} missing: run scripts/run_all.py --config official once to download it")
    return data.load_official(DATA, CFG)


def first_covering_hour(alerts, unit, after):
    ms, me, _ = grid.unit_intervals(alerts[alerts.unit == unit])[unit]
    for s, e in zip(ms, me):
        s, e = pd.Timestamp(s, tz="UTC"), pd.Timestamp(e, tz="UTC")
        if s >= after and s.ceil("h") < e:
            return s.ceil("h")
    raise AssertionError("no covering hour found")


def lypetska(alerts):
    a = alerts[(alerts.unit == "kharkivska") & (alerts.level == "hromada")
               & (alerts.started_at.dt.strftime("%Y-%m-%d") == "2024-05-12")
               & ((alerts.finished_at - alerts.started_at) > pd.Timedelta(days=400))]
    assert len(a) == 1, len(a)
    return a.iloc[0]


def witness_b(alerts):
    _, _, on = grid.unit_intervals(alerts[alerts.unit == "kyiv_city"])["kyiv_city"]
    on = pd.to_datetime(on).tz_localize("UTC")
    o = on[(on >= pd.Timestamp("2025-06-01", tz="UTC")) & (on.minute != 0)][0]
    return o.floor("h")


def real_times(alerts):
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    rng = np.random.default_rng(20261012)
    times = []
    for lo, hi in [("2022-04-01", "2022-12-31"), ("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-31"),
                   ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-06-28")]:
        n = int((ts(hi) - ts(lo)) / pd.Timedelta(hours=1))
        times.append(ts(lo) + pd.Timedelta(hours=int(rng.integers(0, n))))
    times += [first_covering_hour(alerts, "kyiv_city", ts("2025-06-01")),
              first_covering_hour(alerts, "kharkivska", ts("2025-06-01"))]
    L = lypetska(alerts)
    for h in (2, 30):
        t = (L.started_at + pd.Timedelta(hours=h)).floor("h")
        assert L.finished_at > t  # the truncated copy hides this end
        times.append(t)
    (g0, g1), = CFG.approved_gaps
    H = pd.Timedelta(hours=1)
    times += [g0 - H, g0, g1 - H, g1, g1 + pd.Timedelta(hours=24) - H, g1 + pd.Timedelta(hours=24),
              g1 + pd.Timedelta(hours=48) - H, g1 + pd.Timedelta(hours=48)]
    times += [ts("2025-03-30 00:00"), ts("2025-03-30 01:00"), ts("2025-10-26 00:00"), ts("2025-10-26 01:00")]
    for c in (CFG.val[0], CFG.test[0]):
        times += [c - H, c]
    # off-grid witnesses for small look-ahead (reviewer M2 #3): just before / exactly at a real
    # Kyiv City onset and a real merged end; plus the hour of an onset at minute 0
    ms, me, on = grid.unit_intervals(alerts[alerts.unit == "kyiv_city"])["kyiv_city"]
    on, me = pd.to_datetime(on).tz_localize("UTC"), pd.to_datetime(me).tz_localize("UTC")
    o = on[on >= ts("2025-06-01")][0]
    e = me[me >= ts("2025-06-01")][0]
    sec = pd.Timedelta(seconds=1)
    times += [o - sec, o, e - sec, e]
    # first real onset exactly on the hour (any unit) after 2025-06-01: the hour before it and the hour itself
    on_hour = sorted(o for _, _, ons in grid.unit_intervals(alerts).values()
                     for o in pd.to_datetime(ons).tz_localize("UTC")
                     if o >= ts("2025-06-01") and o == o.floor("h"))
    assert on_hour, "no onset exactly on the hour after 2025-06-01"
    times += [on_hour[0] - H, on_hour[0]]
    return pd.DatetimeIndex(sorted(set(times)))


def test_real_data_truncation_invariant(real):
    times = real_times(real)
    assert len(times) >= 25
    f = real_features(real, times)
    act = f.set_index(["unit", "t"])["active_at_t"]
    assert act.loc[("kyiv_city", first_covering_hour(real, "kyiv_city", pd.Timestamp("2025-06-01", tz="UTC")))] == 1
    assert act.loc[("kharkivska", first_covering_hour(real, "kharkivska", pd.Timestamp("2025-06-01", tz="UTC")))] == 1
    assert truncation_check(real_features, real, times) == []


def test_real_data_negative_control_pinned_witnesses(real):
    L = lypetska(real)
    t_a = (L.started_at + pd.Timedelta(hours=2)).floor("h")
    t_b = witness_b(real)
    found = set(truncation_check(leaky_features, real, [t_a], units=["kharkivska"],
                                 columns=["current_alert_final_minutes"]))
    found |= set(truncation_check(leaky_features, real, [t_b], units=["kyiv_city"],
                                  columns=["onsets_centered_3h"]))
    assert found == {(t_a, "kharkivska", "current_alert_final_minutes"),
                     (t_b, "kyiv_city", "onsets_centered_3h")}
    # the real features are clean at the same witnesses
    assert truncation_check(real_features, real, [t_a, t_b]) == []


# ---------------- M3: time-dependent baselines (recent rate, raw persistence) ----------------
from src import baselines as B  # noqa: E402

P_UNIT = pd.Series(0.1, index=regions.units())  # frozen constant: causality does not depend on its value


def baseline_features(alerts, times, H_hist=None, H=None):
    """recent_rate and persistence_raw at each t, rebuilt from the given (possibly truncated) alerts."""
    H = CFG.H if H is None else H
    out = []
    for t in pd.DatetimeIndex(times):
        g = grid.build_grid(alerts, (t - CFG.recent_window - pd.Timedelta(days=1)).floor("h"), t + H, H,
                            approved_gaps=CFG.approved_gaps)
        score = g[g["t"] == t].reset_index(drop=True)
        rr = B.recent_rate(g, score, P_UNIT, CFG.shrink_alpha, CFG.recent_window,
                           H if H_hist is None else H_hist)
        out.append(pd.DataFrame({"unit": score["unit"], "t": score["t"], "recent_rate": rr,
                                 "persistence_raw": B.persistence_raw(alerts, score, H)}))
    return pd.concat(out, ignore_index=True)


def leaky_recent_rate(alerts, times, H=None, H_hist=pd.Timedelta(0)):
    """Negative control: history window reaches past s <= t - H, i.e. reads labels not yet known at t."""
    return baseline_features(alerts, times, H_hist=H_hist, H=H).rename(
        columns={"recent_rate": "recent_rate_leaky"})[["unit", "t", "recent_rate_leaky"]]


def baseline_times(H=None):
    """Val start, mid-validation, the H-dependent edges before the cut-off (C - H ... C), and the
    H-dependent gap-mask edges, so each horizon is checked at its own boundaries."""
    import dataclasses
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    c = CFG if H is None else dataclasses.replace(CFG, H=H)
    C = c.test[0]
    edges = [C - k * pd.Timedelta(hours=1) for k in range(int(c.H / pd.Timedelta(hours=1)), 0, -1)]
    return pd.DatetimeIndex([c.val[0], ts("2026-07-10 13:00"), *edges, C,
                             *[x for iv in config.gap_label_mask_interval(c) for x in iv]])


@pytest.mark.parametrize("hours", [1, 3])
def test_baselines_truncation_invariant(real, hours):
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    H = pd.Timedelta(hours=hours)
    times = baseline_times(H).append(pd.DatetimeIndex([ts("2025-03-30 00:00"), ts("2025-03-30 01:00"),
                                                       ts("2025-10-26 00:00"), ts("2025-10-26 01:00")]))
    assert len(times) == 9 + hours
    if hours == 3:  # the H = 3 boundaries are really visited
        assert {CFG.test[0] - pd.Timedelta(hours=k) for k in (1, 2, 3)} <= set(times)
        assert ts("2026-08-28 21:00") in set(times)
    fn = lambda al, t: baseline_features(al, t, H=H)  # noqa: E731
    assert truncation_check(fn, real, times) == []


def test_baselines_negative_control_h3(real):
    """At H = 3 a history window ending at t - 1h reads labels of rows t-2h, t-1h whose windows reach past t."""
    H3 = pd.Timedelta(hours=3)
    _, _, on = grid.unit_intervals(real[real.unit == "kyiv_city"])["kyiv_city"]
    on = pd.to_datetime(on).tz_localize("UTC")
    g = grid.build_grid(real, CFG.val[0], CFG.test[0], H3, unit_list=regions.units(),
                        approved_gaps=CFG.approved_gaps).set_index(["unit", "t"])
    t_w = None
    for o in on[(on >= CFG.val[0] + pd.Timedelta(days=1)) & (on < CFG.test[0]) & (on.minute != 0)]:
        s = o.floor("h") - pd.Timedelta(hours=1)  # row s: o in (s, s+3h]; no onset in (s, o.floor("h")]
        if g.loc[("kyiv_city", s), "mask"] == 0 and not ((on > s) & (on <= o.floor("h"))).any():
            t_w = o.floor("h")
            break
    assert t_w is not None
    leaky = lambda al, t: leaky_recent_rate(al, t, H=H3, H_hist=pd.Timedelta(hours=1))  # noqa: E731
    assert set(truncation_check(leaky, real, [t_w], units=["kyiv_city"])) == {(t_w, "kyiv_city", "recent_rate_leaky")}
    clean = lambda al, t: baseline_features(al, t, H=H3)  # noqa: E731
    assert truncation_check(clean, real, [t_w]) == []


def test_h3_real_gap_rows_and_purge(real):
    from scripts import run_all
    c3 = config.official_h3()
    g = grid.build_grid(real, c3.grid_start, c3.grid_end, c3.H, approved_gaps=c3.approved_gaps,
                        coverage_end=c3.coverage_end)
    assert run_all.check_gap_rows(g, c3) == 147
    for a, b in (c3.train, c3.val):
        _, counts = evaluate.eligibility(g, a, b, c3.H, [])
        assert counts["excluded_exclusive"]["purge"] == 2 * 24


def test_baselines_negative_control(real):
    _, _, on = grid.unit_intervals(real[real.unit == "kyiv_city"])["kyiv_city"]
    on = pd.to_datetime(on).tz_localize("UTC")
    cand = on[(on >= CFG.val[0]) & (on < CFG.test[0]) & (on.minute != 0)]
    g = grid.build_grid(real, CFG.val[0], CFG.test[0], CFG.H, unit_list=regions.units(),
                        approved_gaps=CFG.approved_gaps).set_index(["unit", "t"])
    t_w = next(o.floor("h") for o in cand if g.loc[("kyiv_city", o.floor("h")), "mask"] == 0)
    assert g.loc[("kyiv_city", t_w), "y"] == 1  # the label the leaky window reads early
    found = set(truncation_check(leaky_recent_rate, real, [t_w], units=["kyiv_city"]))
    assert found == {(t_w, "kyiv_city", "recent_rate_leaky")}
    assert truncation_check(baseline_features, real, [t_w]) == []


# ---------------- M4: model predictions and the API loader-to-predictor path ----------------
from src import model as M  # noqa: E402

NR = config.new_regime()


@pytest.fixture(scope="module")
def small_model(real):
    """A tiny model on real March 2025 rows: only used to check that predictions inherit causality."""
    t = pd.date_range(pd.Timestamp("2025-03-01", tz="UTC"), periods=24 * 20, freq="h")
    f = real_features(real, t)
    g = grid.build_grid(real, t[0], t[-1] + CFG.H, CFG.H, approved_gaps=CFG.approved_gaps)
    df = f.drop(columns="active_at_t").merge(g[["unit", "t", "y", "mask"]], on=["unit", "t"])
    df = df[(df["mask"] == 0) & df[F.FEATURES].notna().all(axis=1)]
    cut = t[0] + pd.Timedelta(days=14)
    booster, _ = M.train(df[df.t < cut], df[df.t >= cut], F.FEATURES)
    return booster


def with_prediction(booster, feats_df):
    ok = feats_df[F.FEATURES].notna().all(axis=1)
    p = np.full(len(feats_df), np.nan)
    if ok.any():
        p[ok.to_numpy()] = booster.predict(M._matrix(feats_df[ok], F.FEATURES))
    return feats_df.assign(p_model=p)


def test_model_predictions_truncation_invariant(real, small_model):
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    times = [CFG.val[0], ts("2025-06-15 13:00"), ts("2025-10-26 01:00"), CFG.test[0] - CFG.H]
    fn = lambda al, t: with_prediction(small_model, real_features(al, t))  # noqa: E731
    assert truncation_check(fn, real, times) == []


@pytest.fixture(scope="module")
def api_records():
    d = ROOT / NR.data_path
    if not d.exists():
        pytest.fail(f"{d} missing: the saved API dump is required (CLAUDE.md, D-007)")
    records, _ = data.read_api_dump(d)
    return records


def api_state(records, t, booster):
    """Loader -> grid -> features -> prediction at hour t, from (possibly truncated) raw records. Labels excluded."""
    al = data.api_alerts(records, None, NR, require_all_units=False)
    g = grid.build_grid(al, t, t + NR.H, NR.H, approved_gaps=config.mask_gaps(NR))
    f = F.build_features(al, pd.DatetimeIndex([t]), config.uncertainty_zones(NR))
    out = f.drop(columns="active_at_t").merge(g[["unit", "t", "active_at_t", "gap_mask", "mask"]], on=["unit", "t"])
    return with_prediction(booster, out).set_index(["unit", "t"])


def api_times():
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    # dnipropetrovska has an alert open in the dump since 2026-10-11 08:33 (D-027)
    return [ts("2026-09-25 13:00"), ts("2026-10-05 07:00"), ts("2026-10-11 12:00"), ts("2026-10-12 09:00")]


def test_api_loader_to_predictor_truncation_invariant(api_records, small_model):
    for t in api_times():
        full = api_state(api_records, t, small_model)
        cut = api_state(data.truncate_api_records(api_records, t), t, small_model)
        pd.testing.assert_frame_equal(full, cut, check_dtype=False, obj=f"API state at {t}")
    open_dn = [r for r in api_records if r["_file_uid"] == 9 and r["finished_at"] is None
               and r["started_at"].startswith("2026-10-11T08:33")]
    assert open_dn, "the open Dnipropetrovska alert used as a witness is missing"
    assert api_state(api_records, api_times()[2], small_model).loc[("dnipropetrovska", api_times()[2]), "mask"] == 1


def test_api_negative_control_final_duration(api_records):
    al = data.api_alerts(api_records, None, NR, require_all_units=False)
    long = al[(al.finished_at - al.started_at > pd.Timedelta(hours=2)) & (al.started_at >= pd.Timestamp("2026-09-25", tz="UTC"))]
    w = long.iloc[0]
    t_w = w.started_at.ceil("h")
    assert t_w < w.finished_at
    full = leaky_features(al, [t_w], [w.unit]).set_index("unit")
    cut_al = data.api_alerts(data.truncate_api_records(api_records, t_w), None, NR, require_all_units=False)
    cut = leaky_features(cut_al, [t_w], [w.unit]).set_index("unit")
    assert full.loc[w.unit, "current_alert_final_minutes"] != cut.loc[w.unit, "current_alert_final_minutes"]
