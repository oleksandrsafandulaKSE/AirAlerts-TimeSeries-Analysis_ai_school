"""M12 (plans/M12.md): split and boundaries, input pinning, artefact copy, the date-gated test stage, label maturity per
H with a negative control, the red-share rule fixtures, the replay keyed comparison, and the code-isolation guards."""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from collect import api_collector as ac
from src import baselines as B, evaluate, grid, regions
from src.data import DataQualityError
from newregime import data as nd, frames as F, horizons as HZ, pipeline as P, redshare as RS

ROOT = Path(__file__).resolve().parents[1]
M6C1_FINGERPRINT_AT_MAIN = "5cf10aca6f571d92a55464114b174409d2baf2c72ea2ee0a27567174eabe5008"  # M6c-1 code at main 8f91abe


def ts(s):
    return pd.Timestamp(s, tz="UTC")


# ---------------------------------------------------------------- isolation guards
def test_m6c1_and_official_code_untouched():
    assert P.code_fingerprint() == M6C1_FINGERPRINT_AT_MAIN
    from scripts import run_all
    official = json.loads((ROOT / "reports/official/preregistration.json").read_text())["code_fingerprint"]
    assert run_all.code_fingerprint() == official
    assert P.HORIZONS == (pd.Timedelta(hours=1), pd.Timedelta(hours=3))
    changed = subprocess.run(["git", "diff", "--name-only", "8f91abe", "--", *P.CODE_FILES], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
    assert changed == [], f"M6c-1 code changed: {changed}"


# ---------------------------------------------------------------- split
def test_split_order_gap_and_dates():
    s = HZ.m12_split()
    f = P.first_split()
    assert (s.train, s.val, s.grid_start) == (f.train, f.val, f.grid_start)
    assert (s.gap_end, s.test_start, s.test_end) == (ts("2026-10-18"), ts("2026-10-18"), ts("2026-10-25"))
    with pytest.raises(ValueError):
        HZ.M12Split("bad", s.grid_start, s.train, s.val, ts("2026-10-10"), ts("2026-10-10"), s.test_end)


def alerts_df(rows):
    df = pd.DataFrame([{"source": "api", "alert_id": str(i), "unit": u, "level": "raion", "started_at": ts(a),
                        "finished_at": ts(b) if b else pd.NaT, "alert_level": lv} for i, (u, a, b, lv) in enumerate(rows)])
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)
    return df


@pytest.mark.parametrize("H", [6, 12, 24])
def test_label_window_endpoints_and_purge(H):
    t0 = ts("2026-10-01 00:00")
    a = alerts_df([("kyiv_city", "2026-10-01 00:00", "2026-10-01 00:20", "yellow"),            # onset exactly at t0
                   ("kyiv_city", str(t0 + pd.Timedelta(hours=H) + pd.Timedelta(minutes=0))[:16], None, "yellow")])
    g = grid.build_grid(a, t0 - pd.Timedelta(hours=2), t0 + pd.Timedelta(hours=1), pd.Timedelta(hours=H),
                        unit_list=["kyiv_city"]).set_index("t")
    assert g.loc[t0, "mask"] == 1                       # onset at t: under alert at t, not y(t)
    assert g.loc[t0 - pd.Timedelta(hours=1), "y"] == 1  # covers the onset at t0 in (t - 1 h, t - 1 h + H]
    g2 = grid.build_grid(alerts_df([("kyiv_city", str(t0 + pd.Timedelta(hours=H))[:16], str(t0 + pd.Timedelta(hours=H, minutes=20))[:16],
                                     "yellow")]), t0, t0 + pd.Timedelta(hours=2), pd.Timedelta(hours=H), unit_list=["kyiv_city"]).set_index("t")
    assert g2.loc[t0, "y"] == 1                          # onset exactly at t + H is in y(t)
    assert g2.loc[t0 + pd.Timedelta(hours=1), "y"] == 1 and g2.loc[t0, "mask"] == 0
    # purge: a fit row is kept iff t + H <= cut-off (equality kept)
    fr = pd.DataFrame({"unit": "kyiv_city", "t": pd.date_range(t0, periods=48, freq="h"), "mask": 0, "y": 0.0,
                       "group": "kyiv_city"})
    for c in F.feature_list("any"):
        fr[c] = 1.0
    C = t0 + pd.Timedelta(hours=30)
    el, _ = evaluate.eligibility(fr, t0, C, pd.Timedelta(hours=H), F.feature_list("any"))
    kept = fr[el]
    assert kept["t"].max() + pd.Timedelta(hours=H) == C


# ---------------------------------------------------------------- real data (pinned) fixtures
@pytest.fixture(scope="module")
def pinned():
    pr = json.loads((ROOT / "reports/m12/preregistration.json").read_text())
    return pr, HZ.load_pinned(pd.Timestamp(pr["acquisition_cutoff"]))


@pytest.fixture(scope="module")
def ctx(pinned):
    pr, (alerts, cov, stats, R, _) = pinned
    s = HZ.m12_split()
    return HZ.build_ctx(s, alerts, cov, stats, min(s.test_start, R), items=[("any", 6), ("any", 12), ("any", 24)])


def test_fit_rows_respect_cutoffs(ctx):
    s = HZ.m12_split()
    for H in HZ.NEW_H:
        fr = ctx.frames[("any", H)]
        h = pd.Timedelta(hours=H)
        for a, b in (s.train, s.val):
            el, _ = evaluate.eligibility(fr, a, b, h, F.feature_list("any"))
            assert (fr[el]["t"] + h <= b).all() and len(fr[el])
        assert fr["t"].max() + h <= s.test_start                   # no row whose label reaches the reserved week


def truncate(al, t):
    a = al[al["started_at"] <= t].copy()
    a.loc[a["finished_at"] > t, "finished_at"] = pd.NaT
    return a


@pytest.mark.parametrize("H", [6, 12, 24])
def test_recent_rate_uses_only_labels_known_at_t_and_negative_control(ctx, H):
    """Truncating the raw data at t leaves the D-025 recent rate at t unchanged; a window that ends AT t (reads labels of
    rows s in (t - H, t]) changes at the pinned t."""
    cfg = ctx.cfgs[H]
    h = pd.Timedelta(hours=H)
    t = ts("2026-10-08 12:00")
    full = ctx.frames[("any", H)]
    cut_alerts = truncate(ctx.alerts, t)
    cut = F.build_frame(cut_alerts, cfg, "any")
    row = full[(full["t"] == t)].head(24)
    p_unit = pd.Series(json.loads((ROOT / f"reports/m12/baseline_fit_any_h{H}.json").read_text())["p_unit"])
    a = B.recent_rate(full, row, p_unit, 10.0, cfg.recent_window, h)
    b = B.recent_rate(cut, row, p_unit, 10.0, cfg.recent_window, h)
    assert np.array_equal(a, b)
    leaky = lambda fr: B.recent_rate(fr, row, p_unit, 10.0, cfg.recent_window, pd.Timedelta(0))  # noqa: E731
    assert not np.array_equal(leaky(full), leaky(cut))


@pytest.mark.parametrize("H", [6, 24])
def test_features_truncation_invariant(ctx, H):
    cfg = ctx.cfgs[H]
    for t in (ts("2026-10-05 07:00"), ts("2026-10-10 18:00"), ts("2026-10-17 00:00")):
        times = pd.DatetimeIndex([t])
        zones = HZ.config_mod.uncertainty_zones(cfg)
        a = F.typed_features(ctx.alerts, times, zones, "any").set_index("unit").sort_index()
        b = F.typed_features(truncate(ctx.alerts, t), times, zones, "any").set_index("unit").sort_index()
        pd.testing.assert_frame_equal(a, b, check_dtype=False)


# ---------------------------------------------------------------- pinning
def _copy_inputs(tmp):
    d = Path(tmp)
    for f in (nd.DATASTORE, nd.PULL_LOG, nd.HOLES):
        shutil.copy(f, d / f.name)
    return P.Paths(store=d / nd.DATASTORE.name, log=d / nd.PULL_LOG.name, holes=d / nd.HOLES.name)


def test_pinning_appends_allowed_edits_refused(tmp_path):
    paths = _copy_inputs(tmp_path)
    A = HZ.last_pull(paths)
    h0 = HZ.prefix_hashes(*HZ.pinned_inputs(A, paths))
    lines = paths.store.read_text().splitlines()
    head, last = lines[0].split(","), lines[-1].split(",")
    i = head.index("fetched_at")
    later = list(last)
    later[i] = "2026-12-01T00:00:00Z"                                    # a version fetched after A
    paths.store.write_text("\n".join(lines + [",".join(later)]) + "\n")
    assert HZ.prefix_hashes(*HZ.pinned_inputs(A, paths)) == h0
    edited = list(last)
    j = head.index("finished_at") if last[head.index("finished_at")] else head.index("notes")
    edited[j] = "2026-10-18T00:00:00Z" if j == head.index("finished_at") else "edited"
    paths.store.write_text("\n".join(lines[:-1] + [",".join(edited)]) + "\n")
    assert HZ.prefix_hashes(*HZ.pinned_inputs(A, paths))["datastore"] != h0["datastore"]
    paths.store.write_text("\n".join(lines[:-1]) + "\n")                 # deletion
    assert HZ.prefix_hashes(*HZ.pinned_inputs(A, paths))["datastore"] != h0["datastore"]


def test_reconstruction_time_from_filtered_coverage(tmp_path):
    """The plan's case: the last pull (A) is later than the coverage of the filtered inputs, because coverage is the
    MIN over units of their latest pull. R must come from the filtered coverage, not from A."""
    paths = _copy_inputs(tmp_path)
    log = ac.read_log(paths.log)
    A = sorted(nd._ts(r["fetched_at"]) for r in log)[-30]               # an earlier acquisition cut-off
    _, cov, _, R, _ = HZ.load_pinned(A, paths)
    assert R == cov.coverage_end.floor("h") and cov.coverage_end <= A
    assert R < A.floor("h") or cov.coverage_end.floor("h") == A.floor("h")
    with pytest.raises(DataQualityError, match="after coverage_end"):   # the unfiltered last hour would break the guard
        nd.load(paths.store, paths.log, paths.holes, reconstruct_at=cov.coverage_end + pd.Timedelta(days=30))


def test_pinning_detects_pull_log_and_holes_edits(tmp_path):
    paths = _copy_inputs(tmp_path)
    A = HZ.last_pull(paths)
    h0 = HZ.prefix_hashes(*HZ.pinned_inputs(A, paths))
    lines = paths.log.read_text().splitlines()
    f = lines[1].split(",")
    f[ac.LOG_COLUMNS.index("n_records")] = str(int(f[ac.LOG_COLUMNS.index("n_records")]) + 1)
    paths.log.write_text("\n".join([lines[0], ",".join(f)] + lines[2:]) + "\n")
    assert HZ.prefix_hashes(*HZ.pinned_inputs(A, paths))["pull_log"] != h0["pull_log"]
    hl = paths.holes.read_text().splitlines()
    paths.holes.write_text("\n".join(hl + ["x,3,khmelnytska,2026-10-01T00:00:00Z,2026-10-01T01:00:00Z,abc"]) + "\n")
    assert HZ.prefix_hashes(*HZ.pinned_inputs(A, paths))["coverage_holes"] != h0["coverage_holes"]


def test_artifact_copy_refuses_a_changed_byte(tmp_path):
    for f in HZ.M6C1.iterdir():
        if f.is_file():
            shutil.copy(f, tmp_path / f.name)
    HZ.m6c1_artifacts(tmp_path)
    p = tmp_path / "model_any_h1.txt"
    p.write_text(p.read_text() + " ")
    with pytest.raises(DataQualityError, match="differs from the M6c-1 pre-registration"):
        HZ.m6c1_artifacts(tmp_path)


# ---------------------------------------------------------------- test stage gate
def test_test_ready_gate():
    split = HZ.m12_split()
    with pytest.raises(DataQualityError, match="test week not complete"):
        HZ.test_ready(split, nd.Coverage(ts("2026-09-12"), ts("2026-10-24 23:59"), ()))
    HZ.test_ready(split, nd.Coverage(ts("2026-09-12"), ts("2026-10-25 00:30"), ()))      # passes once data reaches 10-25


def _m12_copy(tmp):
    """A copy of reports/m12 so a test never writes into the real output directory."""
    d = Path(tmp) / "m12"
    shutil.copytree(ROOT / "reports" / "m12", d)
    return d


class _Stop(Exception):
    pass


def _never(*a, **k):
    raise AssertionError("reached a step that must not run in a test")


def test_test_stage_gate_runs_before_reserve_and_writes_nothing(tmp_path, monkeypatch):
    """Never lets score_test past its gate: test_ready is forced to fail, reserve and build_ctx must not be reached,
    and the output copy is unchanged — whatever the real coverage is on the day pytest runs (review F1)."""
    out = _m12_copy(tmp_path)
    before = sorted(p.name for p in out.iterdir())
    monkeypatch.setattr(P, "reserve", _never)
    monkeypatch.setattr(HZ, "build_ctx", _never)
    monkeypatch.setattr(HZ, "test_ready", lambda split, cov: (_ for _ in ()).throw(_Stop()))
    with pytest.raises(_Stop):
        HZ.score_test(out_dir=out, access_dir=tmp_path / "access")
    assert sorted(p.name for p in out.iterdir()) == before and not (tmp_path / "access").exists()


def test_test_stage_refuses_an_overlapping_reservation(tmp_path, monkeypatch):
    out = _m12_copy(tmp_path)
    access = tmp_path / "access"
    access.mkdir()
    (access / "test_2026-10-20T0000Z_2026-10-21T0000Z.json").write_text("{}")
    monkeypatch.setattr(P, "reserve", _never)
    monkeypatch.setattr(HZ, "build_ctx", _never)
    monkeypatch.setattr(HZ, "test_ready", lambda split, cov: None)
    with pytest.raises(DataQualityError, match="overlapping test reservation"):
        HZ.score_test(out_dir=out, access_dir=access)


def test_test_stage_refuses_changed_pinned_inputs(tmp_path, monkeypatch):
    out = _m12_copy(tmp_path)
    paths = _copy_inputs(tmp_path)
    lines = paths.log.read_text().splitlines()
    paths.log.write_text("\n".join(lines[:1] + lines[2:]) + "\n")       # a pinned pull-log row deleted
    monkeypatch.setattr(P, "reserve", _never)
    with pytest.raises(DataQualityError, match="pinned input row"):
        HZ.score_test(out_dir=out, paths=paths, access_dir=tmp_path / "access")


def test_fit_refuses_after_the_week_was_accessed(tmp_path):
    (tmp_path / "test_2026-10-18T0000Z_2026-10-25T0000Z.json").write_text("{}")
    with pytest.raises(DataQualityError, match="already accessed"):
        HZ.fit(out_dir=tmp_path / "out", access_dir=tmp_path)


# ---------------------------------------------------------------- red share
def cov_of(hs="2026-09-01 00:00", ce="2026-10-30 00:00", holes=()):
    return nd.Coverage(ts(hs), ts(ce), tuple((ts(a), ts(b)) for a, b in holes))


def test_redshare_fixtures():
    rows = [("kyiv_city", "2026-10-01 10:30", "2026-10-01 11:00", "red"),
            ("kyiv_city", "2026-10-01 10:30", "2026-10-01 11:10", "yellow"),       # simultaneous -> red onset
            ("kyiv_city", "2026-10-02 08:00", "2026-10-02 09:00", "yellow"),
            ("kyiv_city", "2026-10-02 08:20", "2026-10-02 08:40", "red"),           # escalation: not an onset
            ("kyiv_city", "2026-10-03 12:00", "2026-10-03 12:30", "yellow"),        # on the hour: tau = 11:00
            ("kyivska", "2026-10-03 11:30", "2026-10-03 12:30", "red")]
    al = alerts_df(rows)
    ons = RS.coloured_onsets(al)
    kc = ons[ons.unit == "kyiv_city"]
    assert list(kc["red"]) == [1, 0, 0] and len(kc) == 3
    assert RS.forecast_time(ts("2026-10-03 12:00")) == ts("2026-10-03 11:00")
    assert RS.forecast_time(ts("2026-10-03 11:30")) == ts("2026-10-03 11:00")
    sc, counts, table, _ = RS.evaluate_rule(al, cov_of(), ts("2026-10-20"), min_class=1, low_n_rows=1)
    r = sc[(sc.unit == "kyiv_city") & (sc.o == ts("2026-10-03 12:00"))].iloc[0]
    assert (r.R, r.N) == (1, 2)                                                    # strictly before tau, own unit
    assert r.national == pytest.approx(1 / 2)          # national (tau - 7 d, tau]: kyiv_city red + yellow (kyivska after tau)
    assert counts["no_prediction_n0"] == 2                                         # first onsets of each unit
    k = sc[sc.unit == "kyivska"]
    assert k.empty                                                                 # Kyivska has one onset only -> N = 0


def test_redshare_coverage_hole_excludes_and_window_anchor():
    rows = [("kyiv_city", f"2026-10-0{d} 10:30", f"2026-10-0{d} 11:00", "yellow") for d in range(1, 6)]
    al = alerts_df(rows)
    _, full, _, _ = RS.evaluate_rule(al, cov_of(), ts("2026-10-20"), min_class=1, low_n_rows=1)
    # a hole [09-25 00:00, 06:00) touches only the window of onset 1 ((09-24 10:00, 10-01 10:00]); onsets 2-5 score
    sc, holed, _, _ = RS.evaluate_rule(al, cov_of(holes=[("2026-09-25 00:00", "2026-09-25 06:00")]), ts("2026-10-20"),
                                       min_class=1, low_n_rows=1)
    assert full["excluded_coverage"] == 0 and full["no_prediction_n0"] == 1 and full["scored"] == 4
    assert holed["excluded_coverage"] == 1 and holed["no_prediction_n0"] == 0 and holed["scored"] == 4
    # every window starts before the history start -> nothing scorable -> raise (no silent empty table)
    with pytest.raises(DataQualityError, match="no scorable onsets"):
        RS.evaluate_rule(al, cov_of(hs="2026-09-29 00:00"), ts("2026-10-20"), min_class=1, low_n_rows=1)


# ---------------------------------------------------------------- replay
@pytest.fixture(scope="module")
def replay_ctx(tmp_path_factory):
    paths = HZ.pinned_m6c1_paths(tmp_path_factory.mktemp("m6c1"))
    ctx = P.prepare(P.first_split(), paths)
    arts, _ = HZ.m6c1_artifacts()
    return ctx, arts


def test_replay_matches_an_independent_score_range_per_row(replay_ctx):
    ctx, arts = replay_ctx
    rep = pd.read_csv(ROOT / "reports/m12/replay_m6c1_any.csv", parse_dates=["t"])
    assert HZ.compare_replay(rep, ctx, arts)
    assert set(rep["status"]) >= {"scored", "under_alert"}                      # under-alert hours are in the file
    w = pd.read_csv(HZ.M6C1 / "blend_weights.csv", parse_dates=["t"])
    w = w[(w.split == "test") & (w.type == "any")]
    for H in (1, 3):
        r = rep[(rep.H == H) & (rep.status == "scored")]
        assert np.array_equal(r["w"].to_numpy(), r["t"].map(w[w.H == H].set_index("t")["w"]).to_numpy())
    swapped = rep.copy()
    i, j = swapped.index[(swapped.H == 1) & (swapped.status == "scored")][:2]
    swapped.loc[[i, j], "p_model"] = swapped.loc[[j, i], "p_model"].to_numpy()
    with pytest.raises(DataQualityError, match="p_model differs"):
        HZ.compare_replay(swapped, ctx, arts)
