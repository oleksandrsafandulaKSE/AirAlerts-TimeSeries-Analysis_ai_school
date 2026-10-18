"""M12 §C (plans/M12.md): "if an alert starts, will it be red?" — the 7-day red-share rule, evaluated as the hourly
forecast the page would have shown just before each "any" onset. EXPLORATORY, API data (air-raid only, D-040/D-045).

Event: an "any" onset = the start of a merged air-raid interval (D-020 cap). Colour: red iff a red air-raid alert of that
unit starts at that instant (simultaneous red + yellow -> red); a red that starts inside a running interval is an
escalation, not an onset. For onset o: tau = floor_hour(o) if o is after the hour start, else o - 1 h, so o is in
(tau, tau + 1 h]. Rule = R / N over the unit's onsets with start in (tau - 7 d, tau]; comparator = the national share
over the same window. Every window is anchored at the same tau."""
import numpy as np
import pandas as pd

from src import evaluate, regions
from src.data import DataQualityError
from newregime import data as nd, frames as F

WINDOW = pd.Timedelta(days=7)
HOUR = pd.Timedelta(hours=1)


def coloured_onsets(alerts):
    """-> DataFrame unit, o (UTC aware), red (0/1) for every "any" onset."""
    on = F.onsets_by_unit(alerts, "any")
    red = nd.typed(alerts, "red")
    red_starts = {u: set(g["started_at"].dt.tz_convert("UTC").dt.tz_localize(None).to_numpy("datetime64[ns]").tolist())
                  for u, g in red.groupby("unit")}
    rows = []
    for u, arr in on.items():
        rs = red_starts.get(u, set())
        for o in arr:
            rows.append({"unit": u, "o": pd.Timestamp(o).tz_localize("UTC"), "red": int(o.tolist() in rs)})
    df = pd.DataFrame(rows, columns=["unit", "o", "red"])
    return df.sort_values(["o", "unit"]).reset_index(drop=True)


def forecast_time(o):
    f = o.floor("h")
    return f if o > f else o - HOUR


def covered(a, b, cov):
    """(a, b] inside [history_start, coverage_end] and touching no recorded hole."""
    if a < cov.history_start or b > cov.coverage_end:
        return False
    return not any(h0 < b and a < h1 for h0, h1 in cov.holes)


def evaluate_rule(alerts, cov, end, min_class=10, low_n_rows=100):
    """Rows: onsets with tau >= history_start + 7 d and o < end. -> (scored, counts, table, reasons)."""
    ons = coloured_onsets(alerts)
    counts = {"onsets": 0, "excluded_window_before_history": 0, "excluded_coverage": 0, "no_prediction_n0": 0, "scored": 0}
    by_unit = {u: g.reset_index(drop=True) for u, g in ons.groupby("unit")}
    rows = []
    for r in ons[ons["o"] < end].itertuples():
        counts["onsets"] += 1
        tau = forecast_time(r.o)
        lo = tau - WINDOW
        if lo < cov.history_start:
            counts["excluded_window_before_history"] += 1
            continue
        if not covered(lo, tau, cov):
            counts["excluded_coverage"] += 1
            continue
        g = by_unit[r.unit]
        w = g[(g["o"] > lo) & (g["o"] <= tau)]
        if not len(w):
            counts["no_prediction_n0"] += 1
            continue
        nat = ons[(ons["o"] > lo) & (ons["o"] <= tau)]
        if not len(nat):
            raise DataQualityError(f"national window empty although the unit has onsets ({r.unit} {tau})")
        rows.append({"unit": r.unit, "o": r.o, "tau": tau, "y": r.red, "R": int(w["red"].sum()), "N": len(w),
                     "rule": float(w["red"].mean()), "national": float(nat["red"].mean()),
                     "group": regions.group_of(r.unit)})
    sc = pd.DataFrame(rows)
    counts["scored"] = len(sc)
    if not len(sc):
        raise DataQualityError("no scorable onsets for the red-share check")
    table, reasons = evaluate.metric_table(sc, ["rule", "national"], "national", min_class)
    table = evaluate.low_n_flags(table, low_n_rows).rename(columns={"baseline": "predictor",
                                                                    "brier_skill_vs_recent": "brier_skill_vs_national"})
    citl = evaluate.calibration_in_the_large(sc, ["rule", "national"])
    table = table.merge(citl.rename(columns={"predictor": "predictor"})[["predictor", "group", "mean_pred", "mean_obs",
                                                                          "pred_minus_obs"]],
                        on=["predictor", "group"], how="left")
    return sc, counts, table, reasons
