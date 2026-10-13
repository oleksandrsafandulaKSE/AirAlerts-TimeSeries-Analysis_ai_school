import numpy as np
import pandas as pd
import pytest

from src import grid
from src.data import DataQualityError

D = "2024-01-10"
H = pd.Timedelta(hours=1)


def T(s):
    return pd.Timestamp(s if " " in s or "T" in s else f"{D} {s}", tz="UTC")


def alerts(rows):
    """rows: (unit, start, end|None, level='oblast', alert_level='')."""
    out = []
    for r in rows:
        u, s, e = r[0], r[1], r[2]
        lvl = r[3] if len(r) > 3 else "oblast"
        al = r[4] if len(r) > 4 else ""
        out.append({"source": "test", "alert_id": str(len(out)), "unit": u, "level": lvl,
                    "started_at": T(s), "finished_at": T(e) if e else pd.NaT, "alert_level": al})
    cols = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
    df = pd.DataFrame(out, columns=cols)
    df["started_at"] = pd.to_datetime(df["started_at"], utc=True)
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


def g(rows, start=f"{D} 00:00", end=f"{D} 08:00", units=("A",), **kw):
    out = grid.build_grid(alerts(rows), T(start), T(end), H, unit_list=list(units), **kw)
    return out.set_index(["unit", "t"])


def at(df, t, col, unit="A"):
    return df.loc[(unit, T(t)), col]


def test_basic_onset_and_mask():
    df = g([("A", "00:30", "01:10")])
    assert at(df, "00:00", "active_at_t") == 0 and at(df, "00:00", "y") == 1
    assert at(df, "01:00", "active_at_t") == 1 and at(df, "01:00", "mask") == 1
    assert at(df, "02:00", "active_at_t") == 0 and at(df, "02:00", "y") == 0


def test_start_exactly_at_t_plus_h_and_at_t():
    df = g([("A", "02:00", "02:40")])
    assert at(df, "01:00", "y") == 1                 # 02:00 in (01:00, 02:00]
    assert at(df, "02:00", "active_at_t") == 1       # start == t -> active, masked
    assert at(df, "02:00", "y") == 0


def test_end_exactly_at_t():
    df = g([("A", "01:00", "03:00")])
    assert at(df, "02:00", "active_at_t") == 1
    assert at(df, "03:00", "active_at_t") == 0


def test_touching_merges_one_minute_gap_does_not():
    ivs = grid.unit_intervals(alerts([("A", "01:00", "02:00"), ("A", "02:00", "03:00")]))
    assert list(ivs["A"][2]) == [np.datetime64(f"{D}T01:00")]
    assert at(g([("A", "01:00", "02:00"), ("A", "02:00", "03:00")]), "02:00", "active_at_t") == 1
    rows = [("A", "01:00", "02:00"), ("A", "02:01", "03:00")]
    ivs = grid.unit_intervals(alerts(rows))
    assert list(ivs["A"][2]) == [np.datetime64(f"{D}T01:00"), np.datetime64(f"{D}T02:01")]
    df = g(rows)
    assert at(df, "02:00", "active_at_t") == 0 and at(df, "02:00", "y") == 1


def test_cross_level_union():
    df = g([("A", "05:15", "06:00", "hromada")])
    assert at(df, "05:00", "y") == 1
    ivs = grid.unit_intervals(alerts([("A", "01:00", "03:00", "oblast"), ("A", "01:30", "01:50", "raion")]))
    assert list(ivs["A"][2]) == [np.datetime64(f"{D}T01:00")]


def test_standing_alert_d020():
    rows = [("A", f"{D} 00:00", "2024-01-13 00:00", "hromada"), ("A", "2024-01-11 05:30", "2024-01-11 07:00", "hromada")]
    df = g(rows, end="2024-01-11 10:00")
    assert at(df, f"{D} 23:00", "active_at_t") == 1
    assert at(df, "2024-01-11 00:00", "active_at_t") == 0      # exactly start + 24h is outside
    assert at(df, "2024-01-11 05:00", "y") == 1
    assert at(df, "2024-01-11 06:00", "active_at_t") == 1
    unknown_end = g([(rows[0][0], rows[0][1], None, "hromada"), rows[1]], end="2024-01-11 10:00")
    pd.testing.assert_frame_equal(df, unknown_end)
    exactly_24h = g([("A", f"{D} 00:00", "2024-01-11 00:00", "hromada"), rows[1]], end="2024-01-11 10:00")
    pd.testing.assert_frame_equal(df, exactly_24h)


def test_zero_duration_onset_masks_nothing():
    df = g([("A", "02:30", "02:30")])
    assert at(df, "02:00", "y") == 1
    assert df["active_at_t"].sum() == 0


# ---------- truncation invariance of the state (mask) + negative control ----------

def random_alerts(seed=0, n=200):
    rng = np.random.default_rng(seed)
    base = pd.Timestamp("2024-01-01", tz="UTC")
    rows = []
    for i in range(n):
        s = base + pd.Timedelta(minutes=int(rng.integers(0, 20 * 24 * 60)))
        dur = pd.Timedelta(minutes=int(rng.integers(0, 3 * 60)))
        if rng.random() < 0.1:
            dur = pd.Timedelta(hours=int(rng.integers(20, 72)))
        e = s + dur
        if rng.random() < 0.05:
            e = pd.NaT
        rows.append({"source": "test", "alert_id": str(i), "unit": "ABC"[i % 3],
                     "level": ["oblast", "raion", "hromada"][int(rng.integers(0, 3))],
                     "started_at": s, "finished_at": e, "alert_level": ""})
    df = pd.DataFrame(rows)
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


def truncate(a, t):
    a = a[a["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


def d020_state(a, t, unit):
    df = grid.build_grid(a[a["unit"] == unit], t, t + H, H, unit_list=[unit])
    return int(df["mask"].iloc[0])


def d009_state(a, t, unit):
    """Old leaky rule: drop alerts whose FINAL duration > 24h, else count [start, finished_at)."""
    a = a[a["unit"] == unit]
    dur = a["finished_at"] - a["started_at"]
    a = a[~(dur > pd.Timedelta(hours=24))]
    end = a["finished_at"].fillna(pd.Timestamp.max.tz_localize("UTC"))
    return int(((a["started_at"] <= t) & (t < end)).any())


def truncation_mismatches(state_fn, a, times):
    bad = []
    for t in times:
        for u in "ABC":
            if state_fn(a, t, u) != state_fn(truncate(a, t), t, u):
                bad.append((t, u))
    return bad


def sample_times(a, seed=1):
    rng = np.random.default_rng(seed)
    base = pd.Timestamp("2024-01-01", tz="UTC")
    times = [base + pd.Timedelta(hours=int(h)) for h in rng.integers(0, 20 * 24, 20)]
    long = a[(a["finished_at"] - a["started_at"]) > pd.Timedelta(hours=24)]
    for s in long["started_at"].head(5):
        times.append(s.ceil("h") + pd.Timedelta(hours=2))  # inside first 24h of a standing alert
    return times


def test_mask_truncation_invariant():
    a = random_alerts()
    assert truncation_mismatches(d020_state, a, sample_times(a)) == []


def test_fixed_truncation_cases():
    a = alerts([("A", "00:00", "05:00"), ("A", f"{D} 06:00", "2024-01-13 06:00")])
    for t in ["04:00", "05:00", f"{D} 06:00", "2024-01-11 05:00", "2024-01-11 06:00"]:
        assert d020_state(a, T(t), "A") == d020_state(truncate(a, T(t)), T(t), "A"), t
    assert d020_state(a, T("04:00"), "A") == 1 and d020_state(a, T("05:00"), "A") == 0
    assert d020_state(a, T("2024-01-11 05:00"), "A") == 1 and d020_state(a, T("2024-01-11 06:00"), "A") == 0


def test_negative_control_d009_is_caught():
    a = random_alerts()
    assert len(truncation_mismatches(d009_state, a, sample_times(a))) > 0


# ---------- independent brute force ----------

def test_brute_force_matches():
    a = random_alerts(seed=3)
    start, end = pd.Timestamp("2023-12-31", tz="UTC"), pd.Timestamp("2024-01-24", tz="UTC")
    df = grid.build_grid(a, start, end, H, unit_list=list("ABC"))
    cap = pd.Timedelta(hours=24)
    exp_rows = []
    for u in "ABC":
        au = a[a.unit == u]
        for t in pd.date_range(start, end, freq="h", inclusive="left"):
            active = False
            ystart = False
            for s, e in zip(au.started_at, au.finished_at):
                eff = s + cap if pd.isna(e) else min(e, s + cap)
                active |= (s <= t < eff)
                ystart |= (t < s <= t + H)
            exp_rows.append((u, t, int(active), int(active), float(ystart)))
    exp = pd.DataFrame(exp_rows, columns=["unit", "t", "active_at_t", "mask", "y"])
    got = df[["unit", "t", "active_at_t", "mask", "y"]].reset_index(drop=True)
    assert (got.active_at_t.values == exp.active_at_t.values).all()
    assert (got["mask"].values == exp["mask"].values).all()
    un = exp["mask"].values == 0
    assert (got.y.values[un] == exp.y.values[un]).all()
    assert not ((got["mask"] == 0) & (got.active_at_t == 1)).any()
    assert 0 < got["mask"].mean() < 1


# ---------- level filter ----------

def test_red_filter():
    rows = [("A", "01:00", "04:00", "oblast", "yellow"), ("A", "02:30", "03:30", "oblast", "red")]
    anyg = g(rows, target_levels="any")
    assert list(grid.unit_intervals(alerts(rows))["A"][2]) == [np.datetime64(f"{D}T01:00")]
    assert at(anyg, "02:00", "mask") == 1 and at(anyg, "03:00", "mask") == 1
    red = g(rows, target_levels="red")
    assert at(red, "02:00", "y") == 1 and at(red, "02:00", "active_at_t") == 0
    assert at(red, "03:00", "active_at_t") == 1
    with pytest.raises(ValueError):
        g([("A", "01:00", "02:00")], target_levels="red")


# ---------- gap ----------

def test_gap_mask_edges():
    gap = ((T("2024-01-11 10:00"), T("2024-01-11 14:00")),)
    df = g([], start="2024-01-11 00:00", end="2024-01-13 00:00", approved_gaps=gap)
    assert at(df, "2024-01-11 08:00", "gap_mask") == 0
    assert at(df, "2024-01-11 09:00", "gap_mask") == 1      # t+H == g0
    assert at(df, "2024-01-11 13:00", "gap_mask") == 1
    for h in ["2024-01-11 14:00", "2024-01-12 00:00", "2024-01-12 13:00"]:
        assert at(df, h, "gap_mask") == 1                      # post-gap 24h
    assert at(df, "2024-01-12 14:00", "gap_mask") == 0
    assert df.loc[df.gap_mask == 1, "y"].isna().all()
    assert df.loc[df.gap_mask == 0, "y"].notna().all()
    assert (df["mask"] == (df.gap_mask | df.active_at_t)).all()


def test_detect_and_check_gaps():
    rows = [("A", "2024-01-10 00:10", "2024-01-10 00:20"), ("B", "2024-01-10 01:10", "2024-01-10 01:20"),
            ("A", "2024-01-11 07:05", "2024-01-11 07:20"), ("A", "2024-01-12 06:30", "2024-01-12 06:40")]
    # empty hours: 02:00 on 10th .. 06:00 on 11th = 29h -> gap; 08:00 11th .. 05:00 12th = 22h -> none
    det = grid.detect_gaps(alerts(rows))
    assert det == [(T("2024-01-10 02:00"), T("2024-01-11 07:00"))]
    grid.check_gaps(det, ((T("2024-01-10 00:00"), T("2024-01-11 12:00")),))
    with pytest.raises(DataQualityError):
        grid.check_gaps(det, ())                                          # unapproved
    with pytest.raises(DataQualityError):
        grid.check_gaps(det, ((T("2024-01-10 00:00"), T("2024-01-11 12:00")),
                              (T("2024-02-01"), T("2024-02-02"))))     # approved, not detected


# ---------- grid shape, DST, alignment, coverage ----------

@pytest.mark.parametrize("s,e", [("2024-03-30 00:00", "2024-04-02 00:00"), ("2024-10-26 00:00", "2024-10-29 00:00")])
def test_grid_dst_shape(s, e):
    df = grid.build_grid(alerts([("A", "01:00", "02:00")]), T(s), T(e), H, unit_list=["A", "B"])
    for _, sub in df.groupby("unit"):
        d = sub.t.diff().dropna()
        assert (d == pd.Timedelta(hours=1)).all() and sub.t.is_unique
    assert len(df) == 72 * 2 and str(df.t.dt.tz) == "UTC"
    assert (df.t + H <= T(e)).all()


def test_alignment_parsed_string_on_dst_night():
    a = alerts([("A", "2024-10-27 00:30", "2024-10-27 01:30")])
    a["started_at"] = pd.to_datetime(["2024-10-27 00:30:00+00:00"], utc=True, format="ISO8601")  # parsed string
    df = grid.build_grid(a, T("2024-10-26 22:00"), T("2024-10-27 03:00"), H, unit_list=["A"]).set_index(["unit", "t"])
    assert at(df, "2024-10-27 00:00", "y") == 1
    assert at(df, "2024-10-27 01:00", "active_at_t") == 1
    assert at(df, "2024-10-26 23:00", "y") == 0


def test_unknown_unit_and_bad_inputs_raise():
    with pytest.raises(DataQualityError):
        grid.build_grid(alerts([("Z", "01:00", "02:00")]), T("00:00"), T("06:00"), H, unit_list=["A"])
    with pytest.raises(DataQualityError):
        grid.unit_intervals(alerts([("A", "02:00", "01:00")]))
    with pytest.raises(ValueError):
        grid.build_grid(alerts([]), T("00:30"), T("06:00"), H, unit_list=["A"])
    with pytest.raises(ValueError):
        grid.build_grid(alerts([]), pd.Timestamp(f"{D} 00:00"), T("06:00"), H, unit_list=["A"])


def test_coverage_end_raises():
    with pytest.raises(DataQualityError):
        grid.build_grid(alerts([("A", "01:00", "02:00")]), T("00:00"), T("06:00"), H,
                        unit_list=["A"], coverage_end=T("05:30"))
    grid.build_grid(alerts([("A", "01:00", "02:00")]), T("00:00"), T("06:00"), H,
                    unit_list=["A"], coverage_end=T("06:00"))


# ---------- base-rate check ----------

def toy_grid(rate_2024, rate_2025, rate_test=0.0):
    rows = []
    for year, rate in [(2024, rate_2024), (2025, rate_2025)]:
        for q in range(4):
            t0 = pd.Timestamp(f"{year}-{3 * q + 1:02d}-01", tz="UTC")
            for i in range(100):
                rows.append({"t": t0 + pd.Timedelta(hours=i), "mask": 0, "group": "rear",
                             "y": float(i < rate * 100)})
    t0 = pd.Timestamp("2026-08-01", tz="UTC")
    for i in range(100):
        rows.append({"t": t0 + pd.Timedelta(hours=i), "mask": 0, "group": "rear", "y": float(i < rate_test * 100)})
    return pd.DataFrame(rows)


def test_base_rate_check():
    before = pd.Timestamp("2026-07-27", tz="UTC")
    with pytest.raises(DataQualityError):
        grid.check_base_rate(toy_grid(0.10, 0.04), before, H)
    assert grid.check_base_rate(toy_grid(0.10, 0.06), before, H) == pytest.approx(0.10)
    grid.check_base_rate(toy_grid(0.10, 0.06, rate_test=0.0), before, H)  # test-period quarter ignored


# ---------------- H = 3 (M3b) ----------------
H3 = pd.Timedelta(hours=3)


def test_h3_label_edges_and_onset_at_t():
    on_edge = grid.build_grid(alerts([("A", "05:00", "05:40")]), T("00:00"), T("08:00"), H3, unit_list=["A"])
    after = grid.build_grid(alerts([("A", "05:01", "05:40")]), T("00:00"), T("08:00"), H3, unit_list=["A"])
    e, a = on_edge.set_index("t"), after.set_index("t")
    assert e.loc[T("02:00"), "y"] == 1 and a.loc[T("02:00"), "y"] == 0      # t+3h included, t+3h+1min not
    assert e.loc[T("05:00"), "y"] == 0 and e.loc[T("05:00"), "active_at_t"] == 1   # onset at t: not in y(t), masks t
    z = grid.build_grid(alerts([("A", "05:00", "05:00")]), T("00:00"), T("08:00"), H3, unit_list=["A"]).set_index("t")
    assert z["active_at_t"].sum() == 0 and z.loc[T("02:00"), "y"] == 1     # zero-duration: onset, masks nothing


def test_h3_gap_mask_edges():
    gap = ((T("2024-01-11 10:00"), T("2024-01-11 14:00")),)
    df = grid.build_grid(alerts([]), T("2024-01-11 00:00"), T("2024-01-13 00:00"), H3, unit_list=["A"],
                         approved_gaps=gap).set_index("t")
    assert df.loc[T("2024-01-11 06:00"), "gap_mask"] == 0          # g0 - 4h
    assert df.loc[T("2024-01-11 07:00"), "gap_mask"] == 1          # g0 - 3h
    assert df.loc[T("2024-01-12 13:00"), "gap_mask"] == 1
    assert df.loc[T("2024-01-12 14:00"), "gap_mask"] == 0          # g1 + 24h: recovered
    assert int(df.gap_mask.sum()) == 3 + 4 + 24


def test_h3_base_rate_uses_mature_labels_only():
    C = T("2024-01-10 10:00")
    g = pd.DataFrame({"t": pd.date_range(T("00:00"), periods=10, freq="h"), "mask": 0, "group": "rear", "y": 0.0})
    g.loc[g.t >= C - pd.Timedelta(hours=2), "y"] = 1.0           # rows C-2h, C-1h: windows reach past C
    _, _, used = grid.base_rate_table(g, C, H3)
    assert used["t"].max() == C - H3 and used["y"].sum() == 0
    _, _, used1 = grid.base_rate_table(g, C, H)
    assert used1["t"].max() == C - H
