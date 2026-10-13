"""M7 extra inputs, all known at t (plans/M7.md §2.1, §3). Reads src/ read-only; never changes the headline pipeline.

Block A (labels, s <= t - H; human-approved exception): unit shrunk recent rates over 14 d and 30 d, national 14-d rate.
Offset input: r(t) = the unit's 14-d shrunk rate with the CAUSAL expanding prior q(t).
Block B (onset events up to t): national onsets (t-1h, t] and (t-3h, t]; frontline onsets (t-3h, t]; neighbours' onsets
(t-1h, t]; minutes since the last national onset.
Block C (onset events up to t): onset in [t-25h, t-23h] (UTC, "same time yesterday"); onsets whose Kyiv hour is within
+-1 of t's Kyiv hour (mod 24) over (t-7d, t].
Gap rule (D-023): any window touching an uncertainty zone -> NaN; time-since -> NaN if the last event is before the zone end.
"""
import numpy as np
import pandas as pd

from src import regions
from src.data import DataQualityError
from src.grid import check_units, unit_intervals

ALPHA = 10.0
CLIP = 1e-4
BLOCK_A = ["rate_14d", "rate_30d", "national_rate_14d"]
BLOCK_B = ["national_onsets_1h", "national_onsets_3h", "frontline_onsets_3h", "neighbour_onsets_1h",
           "minutes_since_national_onset"]
BLOCK_C = ["onset_same_time_yesterday", "onsets_same_kyiv_hour_7d"]
BLOCKS = {"A": BLOCK_A, "B": BLOCK_B, "C": BLOCK_C}
HOUR = np.timedelta64(1, "h")


def _naive(s):
    return pd.DatetimeIndex(s).tz_convert("UTC").tz_localize(None).to_numpy("datetime64[ns]")


def _zone_nan(t, w, zones):
    """(t - w, t] intersects any zone [u0, u1)."""
    bad = np.zeros(len(t), dtype=bool)
    for u0, u1 in zones:
        bad |= (t >= u0) & (t - w < u1)
    return bad


def _zones_naive(zones):
    return [(np.datetime64(pd.Timestamp(a).tz_convert("UTC").tz_localize(None), "ns"),
             np.datetime64(pd.Timestamp(b).tz_convert("UTC").tz_localize(None), "ns")) for a, b in zones]


def label_rates(g, H, zones=()):
    """Block A + offset rate from the grid's binary labels. g: complete hourly grid (unit, t, mask, y) sorted by unit, t.
    k = sum(y), n = count(y) over ELIGIBLE rows (mask == 0, y known) with s in the window and s <= t - H."""
    if H <= pd.Timedelta(0) or H % pd.Timedelta(hours=1) != pd.Timedelta(0):
        raise DataQualityError(f"H must be a positive whole number of hours, got {H}")
    h = int(H / pd.Timedelta(hours=1))
    units = list(dict.fromkeys(g["unit"]))
    t_all = _naive(g.loc[g["unit"] == units[0], "t"])
    T = len(t_all)
    if T > 1 and not np.all(np.diff(t_all) == HOUR):          # windows are row offsets: the grid must be gap-free hourly
        raise DataQualityError("label_rates needs a complete hourly grid (missing hours found)")
    if not all((g["unit"] == u).sum() == T for u in units):
        raise ValueError("grid must be complete and hourly for every unit")
    E = np.zeros((len(units), T))
    Y = np.zeros((len(units), T))
    for j, u in enumerate(units):
        gu = g[g["unit"] == u]
        if not np.array_equal(_naive(gu["t"]), t_all):
            raise ValueError("units must share one sorted hourly time index")
        e = ((gu["mask"].to_numpy() == 0) & gu["y"].notna().to_numpy()).astype(float)
        E[j], Y[j] = e, np.nan_to_num(gu["y"].to_numpy(float)) * e
    CE = np.concatenate([np.zeros((len(units), 1)), np.cumsum(E, axis=1)], axis=1)
    CY = np.concatenate([np.zeros((len(units), 1)), np.cumsum(Y, axis=1)], axis=1)
    idx = np.arange(T)
    last = idx - h                                   # last allowed history index (s <= t - H)
    lc = np.clip(last + 1, 0, T)
    k_exp, n_exp = CY[:, lc], CE[:, lc]               # expanding, per unit
    nk, nn = k_exp.sum(axis=0), n_exp.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        q_nat = np.where(nn > 0, nk / nn, np.nan)
        q = np.where(n_exp > 0, k_exp / n_exp, q_nat[None, :])

    def window(hours):
        first = idx - hours                           # window [t - W, t - H] -> indices first .. last
        ok = first >= 0
        a, b = np.clip(first, 0, T), np.clip(last + 1, 0, T)
        k, n = CY[:, b] - CY[:, a], CE[:, b] - CE[:, a]
        return k, n, ok

    zn = _zones_naive(zones)
    out = {}
    for name, hours in (("rate_14d", 14 * 24), ("rate_30d", 30 * 24)):
        k, n, ok = window(hours)
        r = (k + ALPHA * q) / (n + ALPHA)
        r[:, ~ok] = np.nan
        r[:, _zone_nan(t_all, np.timedelta64(hours, "h"), zn)] = np.nan
        out[name] = r
    k, n, ok = window(14 * 24)
    with np.errstate(invalid="ignore", divide="ignore"):
        nat = np.where(n.sum(axis=0) > 0, k.sum(axis=0) / n.sum(axis=0), np.nan)
    nat[~ok] = np.nan
    nat[_zone_nan(t_all, np.timedelta64(14 * 24, "h"), zn)] = np.nan
    rows = []
    for j, u in enumerate(units):
        rows.append(pd.DataFrame({"unit": u, "t": g.loc[g["unit"] == u, "t"].to_numpy(),
                                  "rate_14d": out["rate_14d"][j], "rate_30d": out["rate_30d"][j],
                                  "national_rate_14d": nat, "prior_q": q[j]}))
    df = pd.concat(rows, ignore_index=True)
    df["offset_rate"] = df["rate_14d"]
    return df


def offset_logit(rate):
    r = np.asarray(rate, float)
    if np.isnan(r).any() or (r < 0).any() or (r > 1).any():
        raise DataQualityError("offset rate must be a probability in [0, 1]")
    r = np.clip(r, CLIP, 1 - CLIP)
    return np.log(r / (1 - r))


def event_features(alerts, g, cap=pd.Timedelta(hours=24), zones=(), neighbours=None):
    """Blocks B and C from D-023 merged onsets (events known at t)."""
    neighbours = regions.NEIGHBOURS if neighbours is None else neighbours
    check_units(alerts, list(dict.fromkeys(g["unit"])))      # no alert may be silently ignored
    ivs = unit_intervals(alerts, cap)
    empty = np.array([], dtype="datetime64[ns]")
    on = {u: ivs.get(u, (empty, empty, empty))[2] for u in dict.fromkeys(g["unit"])}
    nat = np.sort(np.concatenate([on[u] for u in on]))
    front_units = [u for u in on if regions.UNITS.get(u, {}).get("group") == "frontline"]
    front = np.sort(np.concatenate([on[u] for u in front_units])) if front_units else empty
    zn = _zones_naive(zones)

    def count(arr, t, w):
        return (np.searchsorted(arr, t, side="right") - np.searchsorted(arr, t - w, side="right")).astype(float)

    parts = []
    for u in on:
        gu = g[g["unit"] == u]
        t = _naive(gu["t"])
        f = {"unit": u, "t": gu["t"].to_numpy()}
        f["national_onsets_1h"] = count(nat, t, HOUR)
        f["national_onsets_3h"] = count(nat, t, 3 * HOUR)
        f["frontline_onsets_3h"] = count(front, t, 3 * HOUR)
        nb = [on[v] for v in neighbours.get(u, ()) if v in on]
        nb_arr = np.sort(np.concatenate(nb)) if nb else empty
        f["neighbour_onsets_1h"] = count(nb_arr, t, HOUR)
        li = np.searchsorted(nat, t, side="right") - 1
        last = np.where(li >= 0, nat[np.clip(li, 0, None)] if len(nat) else t, np.datetime64("NaT", "ns"))
        mins = (t - last) / np.timedelta64(1, "m")
        mins[li < 0] = np.nan
        # same time yesterday (UTC): any onset in [t - 25h, t - 23h]
        lo = np.searchsorted(on[u], t - 25 * HOUR, side="left")
        hi = np.searchsorted(on[u], t - 23 * HOUR, side="right")
        f["onset_same_time_yesterday"] = (hi - lo > 0).astype(float)
        # onsets whose Kyiv hour is within +-1 of t's Kyiv hour, over (t - 7d, t]
        ou = on[u]
        oh = pd.DatetimeIndex(ou).tz_localize("UTC").tz_convert("Europe/Kyiv").hour.to_numpy() if len(ou) else np.array([], int)
        th = pd.DatetimeIndex(gu["t"]).tz_convert("Europe/Kyiv").hour.to_numpy()
        same = np.zeros(len(t))
        for hr in range(24):
            arr = ou[oh == hr]
            if not len(arr):
                continue
            c = count(arr, t, np.timedelta64(7 * 24, "h"))
            near = (np.abs(((th - hr) + 12) % 24 - 12) <= 1)
            same += np.where(near, c, 0.0)
        f["onsets_same_kyiv_hour_7d"] = same
        for name, w in (("national_onsets_1h", HOUR), ("national_onsets_3h", 3 * HOUR), ("frontline_onsets_3h", 3 * HOUR),
                        ("neighbour_onsets_1h", HOUR), ("onset_same_time_yesterday", 25 * HOUR),
                        ("onsets_same_kyiv_hour_7d", np.timedelta64(7 * 24, "h"))):
            f[name][_zone_nan(t, w, zn)] = np.nan
        for u0, u1 in zn:  # time-since: unknown if the last national onset could lie inside the zone
            mins[(t >= u0) & ~(last >= u1)] = np.nan
        f["minutes_since_national_onset"] = mins
        parts.append(pd.DataFrame(f))
    return pd.concat(parts, ignore_index=True)


def compute_plus(alerts, g, H, cap=pd.Timedelta(hours=24), zones=(), neighbours=None):
    """All M7 inputs for every grid row: unit, t, BLOCK_A + BLOCK_B + BLOCK_C, prior_q, offset_rate.
    National and frontline counts are only meaningful on the full unit set, so all 24 units are required here."""
    if neighbours is None and set(g["unit"]) != set(regions.units()):
        raise DataQualityError("compute_plus needs the grid of all 24 units (national counts would be wrong)")
    lr = label_rates(g.sort_values(["unit", "t"]), H, zones)
    ev = event_features(alerts, g.sort_values(["unit", "t"]), cap, zones, neighbours)
    out = lr.merge(ev, on=["unit", "t"], how="inner", validate="one_to_one")
    if len(out) != len(g):
        raise ValueError("M7 features do not cover every grid row")
    return out
