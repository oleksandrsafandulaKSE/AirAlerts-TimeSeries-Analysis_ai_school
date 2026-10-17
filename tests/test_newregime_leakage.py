"""M6c-1 leakage audit (ts-leakage-audit skill; plans/M6c-1.md §8 tests 11–15) on the REAL datastore, with per-type
negative controls."""
import numpy as np
import pandas as pd
import pytest

from src import baselines as B, config, grid, regions
from newregime import blend, data as nd, frames as F, pipeline as P
from newregime import baselines as NB

ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
H1 = pd.Timedelta(hours=1)
SPLIT = P.first_split()
# one in each split, right after the 7-d NaN window ends, a Kyiv midnight (21:00 UTC in EEST)
TIMES = [ts("2026-09-18 05:00"), ts("2026-09-20 18:00"), ts("2026-09-28 21:00"), ts("2026-10-07 13:00"),
         ts("2026-10-15 03:00")]


@pytest.fixture(scope="module")
def full():
    al, cov, _ = nd.load()
    return al, cov, config.uncertainty_zones(F.run_config(SPLIT, cov, H1))


def cut_at(t):
    """The datastore as it would be reconstructed at t (starts after t dropped, ends after t hidden)."""
    return nd.load(reconstruct_at=t)[0]


def mismatches(fn, al_full, zones, typ, cols=None):
    full = fn(al_full, pd.DatetimeIndex(TIMES), zones, typ).set_index(["unit", "t"])
    cols = [c for c in full.columns if c not in ("type",)] if cols is None else cols
    bad = []
    for t in TIMES:
        cut = fn(cut_at(t), pd.DatetimeIndex([t]), zones, typ).set_index(["unit", "t"])
        for u in regions.units():
            for c in cols:
                x, y = full.loc[(u, t), c], cut.loc[(u, t), c]
                if not ((pd.isna(x) and pd.isna(y)) or x == y):
                    bad.append((str(t), u, c, x, y))
    return bad


def leaky(alerts, times, zones, typ):
    """NEGATIVE CONTROL: (a) type-T onsets in (t, t + 1 h] (future); (b) final duration of the current type-T alert
    (an end not yet known at t)."""
    a = nd.typed(alerts, typ)
    on = F.onsets_by_unit(alerts, typ)
    rows = []
    for t in times:
        tn = np.datetime64(t.tz_localize(None), "ns")
        for u in regions.units():
            o = on.get(u, np.array([], dtype="datetime64[ns]"))
            g = a[(a.unit == u) & (a.started_at <= t) & ~(a.finished_at <= t)]
            dur = ((g.finished_at - g.started_at).dt.total_seconds() / 60).max() if len(g) else -1.0
            rows.append({"unit": u, "t": t, "onsets_next_1h": int(((o > tn) & (o <= tn + np.timedelta64(H1))).sum()),
                         "current_alert_final_minutes": dur})
    return pd.DataFrame(rows)


@pytest.mark.parametrize("typ", nd.TYPES)
def test_truncation_invariance_real_datastore(full, typ):
    al, _, zones = full
    bad = mismatches(F.typed_features, al, zones, typ)
    assert bad == [], f"{typ}: features look into the future: {bad[:5]}"
    if typ != "any":
        assert F.OTHER_COL in F.typed_features(al, pd.DatetimeIndex(TIMES[:1]), zones, typ).columns


@pytest.mark.parametrize("typ", nd.TYPES)
def test_negative_control_is_caught(full, typ):
    al, _, zones = full
    bad = mismatches(leaky, al, zones, typ)
    cols = {b[2] for b in bad}
    assert cols == {"onsets_next_1h", "current_alert_final_minutes"}, f"{typ}: negative control not caught: {cols}"


# ---------------- 13 causality of rolling quantities (synthetic) ----------------

def history(n_hours=60, unit="lvivska", seed=0):
    rng = np.random.default_rng(seed)
    t = ts("2026-10-04 00:00") + pd.to_timedelta(np.arange(n_hours), unit="h")
    return pd.DataFrame({"unit": unit, "t": t, "mask": 0, "y": rng.integers(0, 2, n_hours).astype(float),
                         "p_m": rng.uniform(0, 1, n_hours), "p_b": rng.uniform(0, 1, n_hours)})


def onsets_for(h):
    """One onset inside (s, s + 1 h] for every positive row."""
    pos = h.loc[h["y"] == 1, "t"] + pd.Timedelta(minutes=30)
    return {"lvivska": pos.dt.tz_localize(None).to_numpy("datetime64[ns]")}


@pytest.mark.parametrize("H", [H1, pd.Timedelta(hours=3)])
def test_rolling_quantities_are_causal(H):
    h = history()
    t = ts("2026-10-05 12:00")
    score = pd.DataFrame({"unit": ["lvivska"], "t": [t]})
    pu = pd.Series({"lvivska": 0.3})
    common = h.rename(columns={"y": "y_any"}).assign(y_red=h["y"] * (np.arange(len(h)) % 2))
    pi = pd.Series({"lvivska": 0.4})

    def quantities(hh, cc):
        rr = B.recent_rate(hh, score, pu, 10.0, pd.Timedelta(days=14), H)[0]
        sh = NB.red_share(cc, score, pi, 10.0, pd.Timedelta(days=14), H)[0]
        w = blend.weights([t], hh, onsets_for(hh), H, ts("2026-10-04 00:00"))
        return rr, sh, w["w"].iloc[0], w["w_star"].iloc[0]

    base = quantities(h, common)
    fut = h["t"] > t - H                                      # labels not known at t
    h2, c2 = h.copy(), common.copy()
    h2.loc[fut, "y"] = 1 - h2.loc[fut, "y"]
    c2.loc[fut, ["y_any", "y_red"]] = 1 - c2.loc[fut, ["y_any", "y_red"]]
    assert quantities(h2, c2) == base
    past = h.index[h["t"] == t - H - 2 * H1][0]                # a known label inside every window: must matter
    h3, c3 = h.copy(), common.copy()
    h3.loc[past, "y"] = 1 - h3.loc[past, "y"]
    c3.loc[past, "y_red"] = 1 - c3.loc[past, "y_red"]
    q3 = quantities(h3, c3)
    assert q3[0] != base[0] and q3[1] != base[1] and q3[3] != base[3]


# ---------------- 14, 15 fitted components and label isolation ----------------

@pytest.fixture(scope="module")
def ctx_full():
    return P.prepare(SPLIT)


def test_label_isolation(ctx_full):
    for H in ctx_full.cfgs:
        iso = P._all_frames_isolated(ctx_full, H)
        for typ, f in iso.items():
            assert f.loc[f["t"] + pd.Timedelta(hours=H) > SPLIT.test_start, "y"].isna().all()
            assert f.loc[f["t"] + pd.Timedelta(hours=H) <= SPLIT.test_start, "y"].notna().any()


def test_fit_ignores_test_week(ctx_full):
    """Data reconstructed at the test start (test-week alerts removed, later ends hidden) gives byte-identical models,
    calibrators and baseline tables: no test outcome can reach what drives w(t) and the model on the test week."""
    ctx_cut = P.prepare(SPLIT, reconstruct_at=SPLIT.test_start)
    assert ctx_cut.alerts["started_at"].max() <= SPLIT.test_start < ctx_full.alerts["started_at"].max()
    a, b = P.fit_artifacts(ctx_full), P.fit_artifacts(ctx_cut)
    for k in a:
        assert a[k]["model_str"] == b[k]["model_str"], k
        assert a[k]["cal"] == b[k]["cal"], k
        assert a[k]["tables"] == b[k]["tables"], k
