"""Rolling Brier-optimal blend weight (plans/M6-definition.md "Blend"; plans/M6c-1.md §6).

p_blend(t) = w(t) p_model(t) + (1 - w(t)) p_recent(t);  w(t) = n / (n + N0) * clip(w*, 0, 1);
w* = sum (p_b - y)(p_b - p_m) / sum (p_m - p_b)^2 over the window rows W(t): eligible rows s of all units with
s in [t - 28 d, t - H] and s >= the model's fit cut-off (no in-sample predictions); n = distinct type-T onset events
(unit, o) with o in (s, s + H] for some positive s in W(t). Before the cut-off, w = 0."""
import numpy as np
import pandas as pd

N0 = 50.0
WINDOW = pd.Timedelta(days=28)


def w_star(y, p_m, p_b):
    y, p_m, p_b = (np.asarray(x, float) for x in (y, p_m, p_b))
    den = float(np.sum((p_m - p_b) ** 2))
    return 0.0 if den == 0.0 else float(np.sum((p_b - y) * (p_b - p_m)) / den)


def _onset_events(rows, onsets, H):
    """For each positive window row: the (unit, onset) events in (s, s + H]. -> DataFrame (row, event)."""
    h = np.timedelta64(H)
    out_row, out_ev = [], []
    units, starts = rows["unit"].to_numpy(), rows["_s"].to_numpy()
    for i in np.flatnonzero(rows["y"].to_numpy() == 1):
        u, s = units[i], starts[i]
        on = onsets.get(u, np.array([], dtype="datetime64[ns]"))
        lo, hi = np.searchsorted(on, s, side="right"), np.searchsorted(on, s + h, side="right")
        if hi == lo:
            raise ValueError(f"positive row {u} {s} has no onset in (s, s+H]")
        for o in on[lo:hi]:
            out_row.append(i)
            out_ev.append(f"{u}|{o}")
    return pd.DataFrame({"row": out_row, "event": out_ev})


def weights(times, rows, onsets, H, cutoff, window=WINDOW, n0=N0):
    """w(t) for each forecast time t. rows: DataFrame unit, t, y, p_m, p_b (eligible rows with known labels only;
    rows with an unknown label are dropped here). -> DataFrame t, w, w_star, n, rows_used."""
    r = rows[rows["y"].notna()].reset_index(drop=True).copy()
    r["_s"] = r["t"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]")
    ev = _onset_events(r, onsets, H)
    s = r["_s"].to_numpy()
    c = np.datetime64(cutoff.tz_convert("UTC").tz_localize(None), "ns")
    out = []
    for t in pd.DatetimeIndex(times):
        tn = np.datetime64(t.tz_convert("UTC").tz_localize(None), "ns")
        if tn < c:
            out.append({"t": t, "w": 0.0, "w_star": np.nan, "n": 0, "rows_used": 0})
            continue
        lo = max(tn - np.timedelta64(window), c)
        m = (s >= lo) & (s <= tn - np.timedelta64(H))
        idx = np.flatnonzero(m)
        n = int(ev.loc[ev["row"].isin(idx), "event"].nunique()) if len(idx) else 0
        ws = w_star(r["y"].to_numpy()[m], r["p_m"].to_numpy()[m], r["p_b"].to_numpy()[m]) if len(idx) else 0.0
        out.append({"t": t, "w": n / (n + n0) * min(max(ws, 0.0), 1.0), "w_star": ws, "n": n, "rows_used": len(idx)})
    return pd.DataFrame(out)


def apply(score, w_table):
    """Blend on the score rows (unit, t, model, recent_rate) with w(t)."""
    w = score["t"].map(w_table.set_index("t")["w"])
    if w.isna().any():
        raise ValueError("score rows without a blend weight")
    return (w * score["model"] + (1 - w) * score["recent_rate"]).to_numpy(float), w.to_numpy(float)
