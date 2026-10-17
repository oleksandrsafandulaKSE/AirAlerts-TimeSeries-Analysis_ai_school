"""Datastore -> shared alert format via the EVENT-TIME RECONSTRUCTION (plans/M6a.md §4.2); coverage and holes from the
pull log (plans/M6c-1.md §3); typed alert subsets (§4). Checks raise."""
import csv
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from collect import api_collector as ac
from src import data, regions

ROOT = Path(__file__).resolve().parents[1]
DATASTORE = ROOT / "datastore" / "alerts_in_ua.csv"
PULL_LOG = ROOT / "reports" / "collect" / "pull_log.csv"
HOLES = ROOT / "reports" / "collect" / "coverage_holes.csv"
ALERT_TYPES = ("air_raid",)          # same as the M4 `new_regime` config; artillery is a pending human question
TYPES = ("any", "yellow", "red")
OTHER = {"yellow": "red", "red": "yellow"}


def _ts(s):
    """Strict ISO-8601 UTC with 'Z' (collect.parse_ts raises otherwise)."""
    return pd.Timestamp(ac.parse_ts(s)).tz_convert("UTC")


def _merge(intervals):
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


@dataclass(frozen=True)
class Coverage:
    history_start: pd.Timestamp       # max over units of the unit's earliest nominal_window_from
    coverage_end: pd.Timestamp        # min over units of the unit's latest fetched_at
    holes: tuple                      # ((hole_from, hole_to), ...) national missing-data intervals, half-open


def read_holes(path):
    path = Path(path)
    if not path.exists():
        raise data.DataQualityError(f"{path} missing (M6a always writes at least its header)")
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames != ac.HOLES_COLUMNS:
            raise data.DataQualityError(f"{path}: header {rd.fieldnames} != {ac.HOLES_COLUMNS}")
        return list(rd)


def coverage(log_rows, hole_rows):
    """Per unit: closed pull windows [nominal_window_from, fetched_at]. Every unit must have a pull, and the union of
    its windows must cover [history_start, coverage_end] apart from recorded holes (raise otherwise)."""
    units = regions.units()
    win = {u: [] for u in units}
    for r in log_rows:
        if r["unit"] not in win:
            raise data.DataQualityError(f"pull log names unknown unit {r['unit']!r}")
        a, b = _ts(r["nominal_window_from"]), _ts(r["fetched_at"])
        if not a < b:
            raise data.DataQualityError(f"{r['unit']}: inverted pull window [{a}, {b}]")
        win[r["unit"]].append((a, b))
    missing = [u for u in units if not win[u]]
    if missing:
        raise data.DataQualityError(f"units without any pull: {missing}")
    hs = max(min(a for a, _ in w) for w in win.values())
    ce = min(max(b for _, b in w) for w in win.values())
    if not hs < ce:
        raise data.DataQualityError(f"no common coverage: history_start {hs} >= coverage_end {ce}")
    holes = sorted((_ts(h["hole_from"]), _ts(h["hole_to"])) for h in hole_rows)
    for h0, h1 in holes:
        if not (h0 < h1 and hs <= h0 and h1 <= ce):
            raise data.DataQualityError(f"hole ({h0}, {h1}) is inverted or outside the coverage [{hs}, {ce}]")
    merged = _merge(holes)   # adjacent / overlapping holes cover a gap together
    for u, w in win.items():  # walk the windows; any uncovered stretch inside [hs, ce] must lie inside a hole
        reach = hs
        for a, b in sorted(w):
            if a > reach and reach < ce:
                gap = (reach, min(a, ce))
                if not any(h0 <= gap[0] and gap[1] <= h1 for h0, h1 in merged):
                    raise data.DataQualityError(f"{u}: unrecorded coverage gap {gap}")
            reach = max(reach, b)
        if reach < ce:
            raise data.DataQualityError(f"{u}: windows end at {reach} before coverage_end {ce}")
    return Coverage(hs, ce, tuple(merged))


def load(store_path=DATASTORE, log_path=PULL_LOG, holes_path=HOLES, reconstruct_at=None, stats=None):
    """-> (alerts in the shared format, Coverage, stats). Reconstruction time = coverage_end unless given (tests use an
    earlier time to prove that later events cannot reach a fit)."""
    stats = {} if stats is None else stats
    cov = coverage(ac.read_log(log_path), read_holes(holes_path))
    at = cov.coverage_end if reconstruct_at is None else reconstruct_at
    if at > cov.coverage_end:
        raise data.DataQualityError(f"reconstruction time {at} after coverage_end {cov.coverage_end}")
    rows = ac.read_datastore(store_path)
    rec = ac.as_reconstructed_at(rows, at.to_pydatetime())
    stats.update(datastore_rows=len(rows), distinct_ids=len({r["id"] for r in rows}), reconstructed_records=len(rec),
                 reconstruct_at=str(at))
    cfg = SimpleNamespace(api_alert_types=ALERT_TYPES, history_start=cov.history_start, grid_end=at)
    alerts = data.api_alerts(ac.to_api_records(rec), None, cfg, stats)
    if set(alerts["source"]) != {"api"}:
        raise data.DataQualityError("non-API rows in an API-only run (never mix sources)")
    print(f"[nr-data] datastore rows {len(rows):,} ({stats['distinct_ids']:,} ids) -> event-time reconstruction at "
          f"{at}: {len(rec):,} records -> {len(alerts):,} air-raid alerts (open {stats['open_alerts']}), "
          f"starts {alerts.started_at.min()} -> {alerts.started_at.max()}")
    print(f"[nr-data] alert types present {stats['alert_types']}, dropped {stats['alert_types_dropped']}; "
          f"by level {alerts['alert_level'].value_counts().to_dict()}")
    print(f"[nr-data] coverage: history_start {cov.history_start}, coverage_end {cov.coverage_end}, holes {cov.holes}")
    return alerts, cov, stats


def typed(alerts, typ):
    """ANY = all air-raid alerts (yellow ∪ red); YELLOW / RED = that alert_level. Units stay in the shared format."""
    if typ == "any":
        return alerts
    if typ in OTHER:
        return alerts[alerts["alert_level"] == typ]
    raise ValueError(f"unknown type {typ!r}")
