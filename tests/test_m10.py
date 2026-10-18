"""M10 (plans/M10.md): label variant + onset accounting (§A), recency weights (§B), exposure block D (§C),
stability tables (§D), the §E gate. Synthetic fixtures; real-data leakage checks are in tests/test_m10_leakage.py."""
import numpy as np
import pandas as pd
import pytest

from extras import stability as ST
from improve import exposure as EX, features_plus as FP, labels_variant as LV, model_plus as MP, recency as RC
from scripts import run_improve as RI, run_m10
from src import baselines, grid
from src.data import DataQualityError
from tests.test_improve_models import FE, toy

H = pd.Timedelta(hours=1)


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def alerts(rows):
    """rows: (unit, level, start, end or None)."""
    df = pd.DataFrame([{"source": "t", "alert_id": str(i), "unit": u, "level": lv, "started_at": ts(s),
                        "finished_at": ts(e) if e else pd.NaT, "alert_level": ""}
                       for i, (u, lv, s, e) in enumerate(rows)])
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


D = "2025-03-03 "


def classes(rows):
    a0 = alerts(rows)
    a1 = LV.drop_hromada(a0)
    ms0, me0, on0 = grid.unit_intervals(a0)["kyiv_city"]
    e = np.array([], "datetime64[ns]")
    on1 = grid.unit_intervals(a1).get("kyiv_city", (e, e, e))[2]
    c0, c1, sh = LV.onset_accounting(ms0, me0, on0, on1)
    return list(c0), list(c1), list(sh)


# ------------------------------------------------------------------ §A
def test_drop_hromada_drops_exactly_hromada_rows():
    a = alerts([("kyiv_city", "oblast", D + "00:00", D + "01:00"), ("kyiv_city", "raion", D + "02:00", D + "03:00"),
                ("kyiv_city", "hromada", D + "04:00", D + "05:00")])
    assert list(LV.drop_hromada(a)["level"]) == ["oblast", "raion"]
    with pytest.raises(DataQualityError):
        LV.drop_hromada(a[a.level != "hromada"])


def test_a2_hromada_alone_disappears():
    assert classes([("kyiv_city", "hromada", D + "00:00", D + "01:00")]) == (["disappeared"], [], [])


def test_a2_shift_without_new():
    c0, c1, sh = classes([("kyiv_city", "hromada", D + "00:00", D + "02:00"),
                          ("kyiv_city", "raion", D + "01:00", D + "03:00")])
    assert (c0, c1, sh) == (["shifted"], ["shift_target"], [60.0])


def test_a2_shift_and_new():
    c0, c1, _ = classes([("kyiv_city", "hromada", D + "00:00", D + "05:00"),
                         ("kyiv_city", "raion", D + "01:00", D + "02:00"),
                         ("kyiv_city", "raion", D + "03:00", D + "04:00")])
    assert c0 == ["shifted"] and c1 == ["shift_target", "new"]


def test_a2_kept_and_matched():
    c0, c1, _ = classes([("kyiv_city", "raion", D + "00:00", D + "01:00"),
                         ("kyiv_city", "hromada", D + "00:30", D + "02:00")])
    assert c0 == ["kept"] and c1 == ["matched"]


def test_onset_changes_counts_and_hromada_duration():
    per = [("p", ts("2025-03-01"), ts("2025-04-01"))]
    a0 = alerts([("kyiv_city", "hromada", D + "00:00", D + "01:19"),          # disappeared, 79 min
                 ("kyiv_city", "hromada", D + "05:00", D + "07:00"),          # shifted by 30 min
                 ("kyiv_city", "raion", D + "05:30", D + "06:00")])
    ch = LV.onset_changes(a0, LV.drop_hromada(a0), pd.Timedelta(hours=24), per).set_index("unit")
    r = ch.loc["kyiv_city"]
    assert (r.l0_onsets, r.kept, r.shifted, r.disappeared, r.l1_onsets, r.shift_target, r.new_in_l1) == (2, 0, 1, 1, 1, 1, 0)
    assert r.median_shift_min == 30.0 and r.median_hromada_min_disappeared == 79.0
    assert r.median_hromada_min_shifted == 120.0
    # overlapping periods (train vs a quarter inside it): each period counts its own onsets
    both = [("train", ts("2025-01-01"), ts("2025-06-01")), ("q", ts("2025-03-01"), ts("2025-04-01")),
            ("late", ts("2025-03-03 04:00"), ts("2025-03-04"))]
    ch2 = LV.onset_changes(a0, LV.drop_hromada(a0), pd.Timedelta(hours=24), both).set_index("period")
    assert list(ch2["l0_onsets"]) == [2, 2, 1] and ch2.loc["late", "shifted"] == 1


def complete_grid(start="2025-03-01", hours=24 * 20, units=("kyiv_city",)):
    t = pd.date_range(ts(start), periods=hours, freq="h")
    return pd.concat([pd.DataFrame({"unit": u, "t": t, "mask": 0, "y": 0.0}) for u in units], ignore_index=True)


def test_variant_isolation_label_maturity():
    g = complete_grid()
    rng = np.random.default_rng(3)
    g["y"] = (rng.random(len(g)) < 0.2).astype(float)
    t = ts("2025-03-18 12:00")
    base = FP.label_rates(g, H)
    at = lambda r: r.loc[r["t"] == t, ["offset_rate", "prior_q"]].to_numpy()  # noqa: E731
    later = g.copy()
    later.loc[later["t"] > t - H, "y"] = 1 - later.loc[later["t"] > t - H, "y"]       # labels not yet known at t
    assert np.array_equal(at(base), at(FP.label_rates(later, H)))
    edge = g.copy()
    edge.loc[edge["t"] == t - H, "y"] = 1 - edge.loc[edge["t"] == t - H, "y"]          # s = t - H: known at t
    assert not np.array_equal(at(base), at(FP.label_rates(edge, H)))


def test_fold_keys_keep_equality_drop_beyond():
    g = complete_grid(start="2025-06-30 20:00", hours=6)
    g["offset_rate"] = 0.1
    for c in FE:
        g[c] = 1.0
    C = ts("2025-07-01 00:00")
    fit = RI.eligible(g, g["t"].min(), C, H, FE)
    assert fit["t"].max() == C - H                     # t + H = C kept
    assert (fit["t"] + H <= C).all() and len(RI.eligible(g, C - H, C + H, H, FE)) == 2


def test_onset_endpoints_in_label():
    a = alerts([("kyiv_city", "oblast", "2025-03-03 10:00", "2025-03-03 10:20"),
                ("kyiv_city", "oblast", "2025-03-03 13:00", "2025-03-03 13:20")])
    g = grid.build_grid(a, ts("2025-03-03 09:00"), ts("2025-03-03 14:00"), H, unit_list=["kyiv_city"]).set_index("t")
    assert g.loc[ts("2025-03-03 09:00"), "y"] == 1          # onset at t + H = 10:00 counts for t = 09:00
    assert g.loc[ts("2025-03-03 12:00"), "y"] == 1          # onset at 13:00 = t + H
    assert g.loc[ts("2025-03-03 13:00"), "mask"] == 1       # onset exactly at t: under alert at t, not y(t)


def test_reporting_baseline_prior_from_fit_rows_only():
    g = complete_grid(units=("kyiv_city", "kyivska"))
    rng = np.random.default_rng(5)
    g["y"] = (rng.random(len(g)) < 0.15).astype(float)
    for c in FE:
        g[c] = 1.0
    F = ts("2025-03-12")
    fb = RI.eligible(g, g["t"].min(), F, H, FE, need_offset=False)
    mut = g.copy()
    mut.loc[mut["t"] >= F, "y"] = 1.0
    fb2 = RI.eligible(mut, mut["t"].min(), F, H, FE, need_offset=False)
    pd.testing.assert_series_equal(baselines.unit_train_rates(fb), baselines.unit_train_rates(fb2))


# ------------------------------------------------------------------ §B
def test_recency_weight_values():
    F = ts("2026-01-01")
    t = [F, F - pd.Timedelta(days=365), F - pd.Timedelta(days=730)]
    assert RC.recency_weights(t, F, 365) == pytest.approx([1.0, 0.5, 0.25], abs=1e-15)
    assert np.array_equal(RC.recency_weights(t, F, None), np.ones(3))
    with pytest.raises(ValueError):
        RC.recency_weights([F + H], F, 365)


def test_exact_weights_reach_fit_dataset_only():
    fit, val = toy(seed=1), toy(seed=2)
    w = RC.recency_weights(fit["t"], fit["t"].max(), 30)
    ds, dv = RC.make_datasets(fit, val, FE, w)
    ds.construct()
    dv.construct()
    assert len(ds.get_weight()) == len(w) and np.allclose(ds.get_weight(), w, rtol=1e-6, atol=0)
    assert dv.get_weight() is None
    p_w = MP.predict_offset(RC.train_offset_weighted(fit, val, FE, w), val, FE)
    p_1 = MP.predict_offset(RC.train_offset_weighted(fit, val, FE, None), val, FE)
    assert not np.allclose(p_w, p_1)                    # finite weights are actually used


def test_equal_weights_reproduce_v2_exactly():
    fit, val = toy(seed=1), toy(seed=2)
    a = MP.predict_offset(MP.train_offset(fit, val, FE), val, FE)
    b = MP.predict_offset(RC.train_offset_weighted(fit, val, FE, None), val, FE)
    assert np.max(np.abs(a - b)) <= 1e-12


def test_choose_half_life():
    assert RC.choose_half_life({730: (False, 0.1), 365: (False, 0.09)}) is None
    assert RC.choose_half_life({730: (True, 0.1), 365: (True, 0.09), 182: (False, 0.08)}) == 365
    assert RC.choose_half_life({730: (True, 0.09), 365: (True, 0.09 + 5e-7)}) == 730   # tie -> longer
    with pytest.raises(ValueError):
        RC.choose_half_life({None: (True, 0.08), 730: (True, 0.09)})


def test_covered_until_rejects_overlap_and_nat():
    ms = np.array(["2025-01-01T00:00", "2025-01-01T01:00"], "datetime64[ns]")
    me = np.array(["2025-01-01T03:00", "2025-01-01T02:00"], "datetime64[ns]")
    with pytest.raises(ValueError):
        EX.covered_until(ms, me, ms)
    with pytest.raises(ValueError):
        EX.covered_until(ms[:1], np.array(["NaT"], "datetime64[ns]"), ms)


# ------------------------------------------------------------------ §C
def hgrid(start, end):
    t = pd.date_range(ts(start), ts(end), freq="h", inclusive="left")
    return pd.DataFrame({"unit": "kyiv_city", "t": t})


def test_exposure_hand_calculated():
    a = alerts([("kyiv_city", "raion", "2025-03-02 20:00", "2025-03-03 01:00"),     # carried in from before the window
                ("kyiv_city", "raion", "2025-03-03 00:30", "2025-03-03 02:00"),     # overlaps the first
                ("kyiv_city", "raion", "2025-03-03 04:30", None),                   # unknown end, running past t
                ("kyiv_city", "hromada", "2025-03-01 05:00", "2025-03-05 00:00")])  # > 24 h, capped at 03-02 05:00
    ex = EX.exposure_features(a, hgrid("2025-03-03 05:00", "2025-03-03 06:00")).iloc[0]
    # t = 05:00. (02:00, 05:00]: 04:30-05:00 -> 0.5 h
    assert ex["under_alert_hours_3h"] == pytest.approx(0.5)
    # (03-02 05:00, 05:00]: capped hromada ends exactly at 03-02 05:00 -> 0; 20:00-02:00 = 6 h; + 0.5 h
    assert ex["under_alert_hours_24h"] == pytest.approx(6.5)
    # 7 d: hromada 03-01 05:00 -> 03-02 05:00 = 24 h; + 6.5 h
    assert ex["under_alert_hours_7d"] == pytest.approx(30.5)


def test_exposure_gap_edges():
    z0, z1 = ts("2026-08-29 00:00"), ts("2026-09-04 00:00")
    a = alerts([("kyiv_city", "raion", "2026-08-20 10:00", "2026-08-20 11:00")])
    g = hgrid("2026-08-28 00:00", "2026-09-12 00:00")
    ex = EX.exposure_features(a, g, zones=((z0, z1),)).set_index("t")
    for name, w in EX.WINDOWS.items():
        w = pd.Timedelta(w)
        assert not np.isnan(ex.loc[z0 - H, name])
        assert np.isnan(ex.loc[z0, name])
        assert np.isnan(ex.loc[z1 + w - H, name])
        assert not np.isnan(ex.loc[z1 + w, name])


def test_covered_until_matches_brute_force():
    rng = np.random.default_rng(0)
    base = np.datetime64("2025-01-01T00:00", "ns")
    s = np.sort(rng.integers(0, 10_000, 30)) * np.timedelta64(1, "m") + base
    e = s + rng.integers(1, 300, 30) * np.timedelta64(1, "m")
    ms, me = grid.merge_intervals(s, e)
    xs = base + rng.integers(-100, 11_000, 50) * np.timedelta64(1, "m")
    got = EX.covered_until(ms, me, xs)
    for x, v in zip(xs, got):
        brute = sum(max(0, (min(b, x) - a) / np.timedelta64(1, "ns")) for a, b in zip(ms, me))
        assert v == brute


# ------------------------------------------------------------------ §D
def scored_frame(rows):
    df = pd.DataFrame(rows, columns=["unit", "t", "y", "m", "recent_rate"])
    df["t"] = pd.to_datetime(df["t"], utc=True)
    df["group"] = [ST.regions.group_of(u) for u in df["unit"]]
    return df


def test_bss_hand_calculated_sign_and_denominator():
    # B_model = (0.2^2 + 0.2^2) / 2 = 0.04; B_rr = (0.4^2 + 0.4^2) / 2 = 0.16 -> BSS = 1 - 0.04/0.16 = 0.75
    df = scored_frame([("kyiv_city", "2026-07-01 10:00", 1, 0.8, 0.6), ("kyiv_city", "2026-07-01 11:00", 0, 0.2, 0.4)])
    tab, _ = ST.slice_tables(df, ["m", "recent_rate"])
    r = tab[(tab.slice_kind == "day_night") & (tab.group == "overall") & (tab.baseline == "m")].iloc[0]
    assert r["brier_skill_vs_recent"] == pytest.approx(0.75)
    same = df.assign(m=df["recent_rate"])
    t2, _ = ST.slice_tables(same, ["m", "recent_rate"])
    assert (t2.loc[t2.baseline == "m", "brier_skill_vs_recent"].dropna() == 0).all()


def test_day_night_boundaries_and_dst():
    # summer (UTC+3): 03:00 UTC = 06:00 Kyiv (day), 02:00 UTC = 05:00 (night), 18:00 = 21:00 (day), 19:00 = 22:00 (night)
    t = ["2026-07-01 02:00", "2026-07-01 03:00", "2026-07-01 18:00", "2026-07-01 19:00"]
    assert list(ST.day_night(t)) == ["night", "day", "day", "night"]
    # 2025-10-26: 00:00 and 01:00 UTC are both 03:00 Kyiv (repeated hour) -> night; 03:00 UTC = 05:00 EET -> night,
    # 04:00 UTC = 06:00 -> day
    assert list(ST.day_night(["2025-10-26 00:00", "2025-10-26 01:00", "2025-10-26 03:00", "2025-10-26 04:00"])) == \
        ["night", "night", "night", "day"]
    # 2026-03-29: 01:00 UTC = 04:00 EEST (03:00 skipped); 03:00 UTC = 06:00 -> day; 02:00 UTC = 05:00 -> night
    assert list(ST.day_night(["2026-03-29 01:00", "2026-03-29 02:00", "2026-03-29 03:00"])) == ["night", "night", "day"]


def test_week_start_monday_utc():
    assert list(ST.week_start(["2026-06-29 00:00", "2026-07-05 23:00", "2026-07-06 00:00"]).strftime("%Y-%m-%d")) == \
        ["2026-06-29", "2026-06-29", "2026-07-06"]


def test_kyiv_city_and_kyivska_stay_separate():
    df = scored_frame([("kyiv_city", "2026-07-01 10:00", 1, 0.9, 0.5), ("kyiv_city", "2026-07-01 11:00", 0, 0.1, 0.5),
                       ("kyivska", "2026-07-01 10:00", 1, 0.2, 0.5), ("kyivska", "2026-07-01 11:00", 0, 0.8, 0.5)])
    tab, _ = ST.slice_tables(df, ["m", "recent_rate"])
    k = tab[(tab.slice_kind == "day_night") & (tab.baseline == "m")].set_index("group")
    assert k.loc["kyiv_city", "rows"] == 2 and k.loc["kyiv_city", "brier"] == pytest.approx(0.01)
    assert k.loc["rear", "brier"] == pytest.approx(0.64)


def test_within_unit_auc_nan_with_reason():
    df = scored_frame([("kyiv_city", "2026-07-01 10:00", 1, 0.9, 0.5), ("kyiv_city", "2026-07-01 11:00", 0, 0.1, 0.5)])
    tab, reasons = ST.slice_tables(df, ["m", "recent_rate"])
    assert tab["roc_auc_within_unit_mean"].isna().all()
    assert any("within-unit AUC NaN" in r for r in reasons)


def test_join_raises_on_key_or_y_mismatch():
    a = pd.DataFrame({"unit": ["kyiv_city"] * 2, "t": ["2026-07-01 10:00+00:00", "2026-07-01 11:00+00:00"],
                      "y": [1.0, 0.0], "p": [0.5, 0.5]})
    b = a.rename(columns={"p": "q"})
    assert len(ST.join_predictions({"a": a, "b": b})) == 2
    with pytest.raises(DataQualityError):
        ST.join_predictions({"a": a, "b": b.iloc[:1]})
    with pytest.raises(DataQualityError):
        ST.join_predictions({"a": a, "b": b.assign(y=[0.0, 0.0])})
    with pytest.raises(DataQualityError):
        ST.join_predictions({"a": pd.concat([a, a]), "b": b})


# ------------------------------------------------------------------ §E
def test_posthoc_stage_is_gated(tmp_path):
    with pytest.raises(PermissionError):
        run_m10.main(["--posthoc-test", "--reports-root", str(tmp_path)])
