"""M6c-1 unit tests (plans/M6c-1.md §8): typed targets and masks, other-level feature, coverage and holes, split edges,
blend weight, red-share baseline, test-once guard, real-datastore smoke."""
import json
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from src import config, evaluate, grid, regions
from src.data import DataQualityError
from newregime import blend, data as nd, frames as F, pipeline as P
from newregime import baselines as NB

ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
H1, H3 = pd.Timedelta(hours=1), pd.Timedelta(hours=3)


def alerts(rows):
    """rows: (unit, alert_level, start, end-or-None)."""
    out = pd.DataFrame([{"source": "api", "alert_id": str(i), "unit": u, "level": "oblast", "started_at": ts(s),
                         "finished_at": ts(e) if e else pd.NaT, "alert_level": lv}
                        for i, (u, lv, s, e) in enumerate(rows)])
    out["finished_at"] = pd.to_datetime(out["finished_at"], utc=True)
    return out


def syn_cfg(H=H1, gs="2026-09-20 00:00", ge="2026-09-23 00:00", holes=()):
    return replace(config.new_regime(), grid_start=ts(gs), grid_end=ts(ge), coverage_end=ts(ge) + pd.Timedelta(days=1),
                   H=H, history_start=ts("2026-09-01 00:00"), approved_gaps=tuple(holes))


def row(fr, unit, t):
    r = fr[(fr["unit"] == unit) & (fr["t"] == ts(t))]
    assert len(r) == 1
    return r.iloc[0]


# ---------------- 1-3 typed targets, masks, other-level feature ----------------

A = alerts([("kyiv_city", "yellow", "2026-09-21 10:00", "2026-09-21 12:00"),
            ("kyiv_city", "red", "2026-09-21 10:30", "2026-09-21 11:00"),      # red during yellow
            ("kyiv_city", "red", "2026-09-21 14:00", "2026-09-21 16:00"),
            ("kyiv_city", "yellow", "2026-09-21 14:30", "2026-09-21 15:00")])  # yellow during red


@pytest.fixture(scope="module")
def fr1():
    return {typ: F.build_frame(A, syn_cfg(), typ) for typ in nd.TYPES}


def test_red_during_yellow_counts_for_red(fr1):
    r = row(fr1["red"], "kyiv_city", "2026-09-21 10:00")
    assert r["mask"] == 0 and r["y"] == 1 and r["other_level_active_at_t"] == 1
    assert row(fr1["yellow"], "kyiv_city", "2026-09-21 10:00")["mask"] == 1
    assert row(fr1["any"], "kyiv_city", "2026-09-21 10:00")["mask"] == 1


def test_yellow_during_red_counts_for_yellow(fr1):
    r = row(fr1["yellow"], "kyiv_city", "2026-09-21 14:00")
    assert r["mask"] == 0 and r["y"] == 1 and r["other_level_active_at_t"] == 1
    assert row(fr1["red"], "kyiv_city", "2026-09-21 14:00")["mask"] == 1
    assert row(fr1["any"], "kyiv_city", "2026-09-21 13:00")["y"] == 1   # ANY onset at 14:00 = start of the union


def test_no_unmasked_row_active_for_its_own_type(fr1):
    for typ, fr in fr1.items():
        assert not ((fr["mask"] == 0) & (fr["active_at_t"] == 1)).any(), typ


def test_red_prefilter_equals_src_filter_levels():
    a = nd.typed(A, "red")
    b = grid.filter_levels(A, "red")
    for u, (ms, me, on) in grid.unit_intervals(a).items():
        ms2, me2, on2 = grid.unit_intervals(b)[u]
        assert (ms == ms2).all() and (me == me2).all() and (on == on2).all()


def test_other_level_equals_other_grid_active_and_nan_in_zone(fr1):
    for typ in ("yellow", "red"):
        other = fr1[nd.OTHER[typ]].set_index(["unit", "t"])["active_at_t"]
        mine = fr1[typ].set_index(["unit", "t"])[F.OTHER_COL]
        assert (mine == other.reindex(mine.index)).all()
    cfg = syn_cfg(gs="2026-09-01 00:00", ge="2026-09-03 00:00")
    fr = F.build_frame(A, cfg, "red")
    assert fr.loc[fr["t"] < ts("2026-09-02 00:00"), F.OTHER_COL].isna().all()   # history zone + 24 h


# ---------------- 4 coverage and holes ----------------

def log_rows(windows):
    return [{"unit": u, "nominal_window_from": a, "fetched_at": b} for u, a, b in windows]


def full_log(extra=()):
    base = [(u, "2026-09-12T17:00:00Z", "2026-10-12T17:00:00Z") for u in regions.units()]
    return log_rows(base + list(extra))


def test_coverage_values_and_errors():
    cov = nd.coverage(full_log([("kyiv_city", "2026-09-17T19:00:00Z", "2026-10-17T19:00:00Z")]), [])
    assert cov.history_start == ts("2026-09-12 17:00") and cov.coverage_end == ts("2026-10-12 17:00")
    with pytest.raises(DataQualityError, match="without any pull"):
        nd.coverage(log_rows([(u, "2026-09-12T17:00:00Z", "2026-10-12T17:00:00Z") for u in regions.units()[1:]]), [])
    # every unit pulled again later, but kyiv_city's second window leaves a gap after its first fetch
    later = [(u, "2026-09-20T00:00:00Z", "2026-10-20T00:00:00Z") for u in regions.units() if u != "kyiv_city"]
    gap = [("kyiv_city", "2026-10-15T00:00:00Z", "2026-11-14T00:00:00Z")]
    with pytest.raises(DataQualityError, match="unrecorded coverage gap"):
        nd.coverage(full_log(later + gap), [])
    hole = [{"hole_from": "2026-10-12T17:00:00Z", "hole_to": "2026-10-15T00:00:00Z"}]
    cov = nd.coverage(full_log(later + gap), hole)
    assert cov.holes == ((ts("2026-10-12 17:00"), ts("2026-10-15 00:00")),)


@pytest.mark.parametrize("typ", nd.TYPES)
def test_hole_masks(typ):
    """A hole is missing data: rows whose (t, t+H] touches it are masked, plus 24 h after it; 7-d features are NaN
    while their window touches it (D-039 downstream contract, at both edges)."""
    hole = (ts("2026-09-25 06:00"), ts("2026-09-25 18:00"))
    for H in (H1, H3):
        fr = F.build_frame(A, syn_cfg(H, gs="2026-09-20 00:00", ge="2026-10-05 00:00", holes=[hole]), typ)
        k = fr[fr["unit"] == "lvivska"].set_index("t")
        assert k.loc[hole[0] - H - H1, "gap_mask"] == 0          # (t, t+H] ends 1 h before the hole
        assert k.loc[hole[0] - H, "gap_mask"] == 1               # (t, t+H] reaches the hole start
        assert k.loc[hole[1] + pd.Timedelta(hours=23), "gap_mask"] == 1
        assert k.loc[hole[1] + pd.Timedelta(hours=24), "gap_mask"] == 0
        # the uncertainty zone is [hole_from, hole_to + 24 h); (t - 7 d, t] must clear it
        assert np.isnan(k.loc[hole[1] + pd.Timedelta(days=8) - H1, "onsets_last_7d"])
        assert not np.isnan(k.loc[hole[1] + pd.Timedelta(days=8), "onsets_last_7d"])
        assert not np.isnan(k.loc[hole[0] - H1, "onsets_last_7d"])            # before the hole: known
        assert np.isnan(k.loc[hole[0], "onsets_last_7d"])


# ---------------- 5, 10 split edges and typed witnesses ----------------

def test_purge_edges():
    al = alerts([("lvivska", "red", "2026-09-15 10:00", "2026-09-15 11:00"),   # so time-since features are known
                 ("lvivska", "red", "2026-09-22 23:30", "2026-09-22 23:45")])
    for H in (H1, H3):
        fr = F.build_frame(al, syn_cfg(H, ge="2026-09-24 00:00"), "red")
        end = ts("2026-09-23 00:00")
        el, _ = evaluate.eligibility(fr, ts("2026-09-21 00:00"), end, H, F.feature_list("red"))
        e = fr[el]
        assert len(e) > 0
        assert (e["t"] + H <= end).all()
        assert ((e["unit"] == "lvivska") & (e["t"] == end - H)).any()               # t + H = cut-off: kept
        assert not ((e["unit"] == "lvivska") & (e["t"] == end - H + H1)).any()       # one hour later: purged
        assert row(fr, "lvivska", str(end - H))["y"] == 1                             # onset 23:30 in (t, t+H]


def test_onset_edges_and_open_alert_cap():
    al = alerts([("odeska", "yellow", "2026-09-21 05:00", None),                     # open: end unknown -> 24 h cap
                 ("odeska", "red", "2026-09-21 03:00", "2026-09-22 03:00")])         # ends exactly at start + 24 h
    for typ, start in (("yellow", "2026-09-21 05:00"), ("red", "2026-09-21 03:00")):
        fr = F.build_frame(al, syn_cfg(), typ)
        s = ts(start)
        assert row(fr, "odeska", str(s - H1))["y"] == 1                # onset exactly at t + H is in (t, t+H]
        assert row(fr, "odeska", str(s))["mask"] == 1                  # onset exactly at t: active, masked
        assert row(fr, "odeska", str(s + pd.Timedelta(hours=23)))["mask"] == 1
        assert row(fr, "odeska", str(s + pd.Timedelta(hours=24)))["mask"] == 0   # D-020 cap
    fr3 = F.build_frame(al, syn_cfg(H3), "yellow")
    assert row(fr3, "odeska", "2026-09-21 02:00")["y"] == 1 and row(fr3, "odeska", "2026-09-21 01:00")["y"] == 0


def test_dst_end_calendar_features():
    fr = F.build_frame(A, syn_cfg(gs="2026-10-24 22:00", ge="2026-10-25 03:00"), "red")
    k = fr[fr["unit"] == "kyiv_city"].set_index("t")["hour_kyiv"]
    assert k[ts("2026-10-25 00:00")] == 3 and k[ts("2026-10-25 01:00")] == 3 and k[ts("2026-10-25 02:00")] == 4


# ---------------- 6 blend ----------------

def wrows(ts_list, y, pm, pb, unit="lvivska"):
    return pd.DataFrame({"unit": unit, "t": [ts(t) for t in ts_list], "y": y, "p_m": pm, "p_b": pb})


def test_w_star_hand_computation():
    y, pm, pb = np.array([1, 0, 1, 0.]), np.array([.8, .2, .6, .1]), np.array([.5, .5, .5, .5])
    want = np.sum((pb - y) * (pb - pm)) / np.sum((pm - pb) ** 2)
    assert blend.w_star(y, pm, pb) == pytest.approx(want)
    assert blend.w_star(y, pb, pb) == 0.0


def test_blend_weight_n0_clip_and_onset_count():
    times = ["2026-10-04 00:00", "2026-10-04 01:00", "2026-10-04 02:00", "2026-10-04 03:00"]
    r = wrows(times, [0, 1, 1, 1], [.1, .9, .9, .9], [.2, .2, .2, .2])
    on = {"lvivska": np.array([np.datetime64("2026-10-04T03:30", "ns")])}   # one onset, three H = 3 rows positive
    w = blend.weights([ts("2026-10-04 07:00")], r, on, H3, ts("2026-10-04 00:00"))
    assert w["n"].iloc[0] == 1                                     # counted once, not 3
    ws = blend.w_star(r.y, r.p_m, r.p_b)
    assert w["w"].iloc[0] == pytest.approx(1 / 51 * min(max(ws, 0), 1))


def test_blend_ignores_rows_before_cutoff():
    times = ["2026-10-03 22:00", "2026-10-03 23:00", "2026-10-04 00:00"]
    r = wrows(times, [1, 1, 0], [.9, .9, .1], [.5, .5, .5])
    on = {"lvivska": np.array(["2026-10-03T22:30", "2026-10-03T23:30"], dtype="datetime64[ns]")}
    w = blend.weights([ts("2026-10-03 23:00"), ts("2026-10-04 05:00")], r, on, H1, ts("2026-10-04 00:00"))
    assert w["w"].iloc[0] == 0 and w["rows_used"].iloc[0] == 0      # before the cut-off: w = 0
    assert w["rows_used"].iloc[1] == 1 and w["n"].iloc[1] == 0      # only the out-of-sample row
    assert w["w"].iloc[1] == 0


# ---------------- 7 red-share baseline ----------------

def test_red_share_hand_computation():
    t0 = ts("2026-10-05 00:00")
    common = pd.DataFrame({"unit": "lvivska", "t": [t0 + i * H1 for i in range(4)],
                           "y_any": [1., 1., 0., 1.], "y_red": [1., 0., 0., 1.]})
    score = pd.DataFrame({"unit": ["lvivska"], "t": [t0 + 3 * H1]})
    pi = pd.Series({"lvivska": 0.25})
    got = NB.red_share(common, score, pi, 10.0, pd.Timedelta(days=14), H1)   # rows s <= t - 1 h: first three
    assert got[0] == pytest.approx((1 + 10 * 0.25) / (2 + 10))
    big = common.assign(y_red=[5., 5., 5., 5.])
    assert NB.red_share(big, score, pd.Series({"lvivska": 1.0}), 10.0, pd.Timedelta(days=14), H1)[0] == 1.0


# ---------------- 8 test-once guard (a split INSIDE the training period; never the real test week) ----------------

def guard_split():
    return P.Split("guardtest", ts("2026-09-13 00:00"), (ts("2026-09-13 00:00"), ts("2026-09-27 00:00")),
                   (ts("2026-09-27 00:00"), ts("2026-10-01 00:00")), ts("2026-10-01 00:00"), ts("2026-10-04 00:00"))


def test_test_once_guard(tmp_path):
    out, acc = tmp_path / "out", tmp_path / "access"
    sp = guard_split()
    P.fit(sp, out, access_dir=acc)
    P.score_test(sp, out, access_dir=acc)
    rec = json.loads(P.access_path(sp, acc).read_text())
    assert rec["status"] == "done"
    with pytest.raises(DataQualityError, match="already accessed"):
        P.score_test(sp, out, access_dir=acc)
    with pytest.raises(DataQualityError, match="already accessed"):
        P.fit(sp, out, access_dir=acc)
    # a tampered model fails the pre-registration check (fresh access dir)
    f = out / "model_red_h1.txt"
    f.write_text(f.read_text() + "\n")
    with pytest.raises(DataQualityError, match="differs from the pre-registration"):
        P.score_test(sp, out, access_dir=tmp_path / "access2")
    assert not P.access_path(sp, tmp_path / "access2").exists()   # nothing reserved when verification fails


def test_reservation_is_exclusive(tmp_path):
    P.reserve(guard_split(), "x", tmp_path)
    with pytest.raises(FileExistsError):
        P.reserve(guard_split(), "x", tmp_path)


# ---------------- 9 real datastore smoke ----------------

def test_real_datastore_smoke():
    al, cov, _ = nd.load()
    assert cov.history_start == ts("2026-09-12 17:00:43") and cov.holes == ()
    assert cov.coverage_end >= ts("2026-10-17 19:36:38")
    assert P.first_split().test_end <= cov.coverage_end.floor("h")
    assert set(al["unit"]) == set(regions.units()) and set(al["source"]) == {"api"}
    for typ in nd.TYPES:
        on = F.onsets_by_unit(al, typ)
        assert sum(len(v) for v in on.values()) > 0, typ


# ---------------- harness-review regressions ----------------

def test_overlapping_test_week_is_refused(tmp_path):
    sp = guard_split()
    P.reserve(sp, "x", tmp_path)
    shorter = replace(sp, name="other", test_end=sp.test_end - H1)       # same week, one hour shorter
    assert P.accessed(shorter, tmp_path)
    with pytest.raises(DataQualityError, match="already accessed"):
        P.fit(shorter, tmp_path / "out", access_dir=tmp_path)
    later = replace(sp, val=(sp.val[0], sp.test_end), test_start=sp.test_end, test_end=sp.test_end + 24 * H1)
    assert not P.accessed(later, tmp_path)                                  # disjoint week: allowed


def test_official_model_check_runs_before_reservation(tmp_path, monkeypatch):
    out, acc = tmp_path / "out", tmp_path / "acc"
    sp = guard_split()
    P.fit(sp, out, access_dir=acc)

    def broken(H):
        raise DataQualityError("official model changed")
    monkeypatch.setattr(P, "official_predictor", broken)
    with pytest.raises(DataQualityError, match="official model changed"):
        P.score_test(sp, out, access_dir=acc)
    assert not P.accessed(sp, acc)                                          # the test week is still available


def test_coverage_input_validation():
    later = [(u, "2026-09-20T00:00:00Z", "2026-10-20T00:00:00Z") for u in regions.units() if u != "kyiv_city"]
    gap = [("kyiv_city", "2026-10-15T00:00:00Z", "2026-11-14T00:00:00Z")]
    two = [{"hole_from": "2026-10-12T17:00:00Z", "hole_to": "2026-10-13T00:00:00Z"},
           {"hole_from": "2026-10-13T00:00:00Z", "hole_to": "2026-10-15T00:00:00Z"}]
    cov = nd.coverage(full_log(later + gap), two)                           # adjacent holes cover the gap together
    assert cov.holes == ((ts("2026-10-12 17:00"), ts("2026-10-15 00:00")),)
    with pytest.raises(DataQualityError, match="outside the coverage"):
        nd.coverage(full_log(), [{"hole_from": "2026-09-01T00:00:00Z", "hole_to": "2026-12-01T00:00:00Z"}])
    with pytest.raises(DataQualityError, match="inverted pull window"):
        nd.coverage(full_log([("kyiv_city", "2026-10-20T00:00:00Z", "2026-10-01T00:00:00Z")]), [])
    with pytest.raises(Exception):
        nd.coverage(full_log([("kyiv_city", "2026-09-20 00:00", "2026-10-01T00:00:00Z")]), [])   # no 'Z': raises
