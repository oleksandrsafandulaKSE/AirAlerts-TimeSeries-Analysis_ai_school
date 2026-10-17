"""M9 §A (exact-duration pins, option A: outside the fingerprinted code) and §E3 (onset collapse across Dec 2025)."""
from pathlib import Path

import pandas as pd
import pytest

from extras import data_quality as dq
from src import config, data
from tests.test_data import HEADER, base_rows, cfg_for, row, write

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "official_data_en.csv"
CFG = config.official()


# ---------------- §A synthetic ----------------

def open_row(oblast, start, level="hromada", raion="R", hromada="H"):
    return f"{oblast},{raion},{hromada},{level},{start}+00:00,,official\n"


def test_exact_counts_after_dedup_and_exclusion(tmp_path):
    extra = [
        row("Kyiv City", "2024-02-01 10:00:00", "2024-02-01 11:00:00", "hromada", "R", "H"),   # exact 1h
        row("Kyiv City", "2024-02-01 10:00:00", "2024-02-01 11:00:00", "hromada", "R", "H"),   # exact dup -> once
        row("Luhanska oblast", "2024-03-01 10:00:00", "2024-03-01 11:00:00"),                   # excluded
        row("Sumska oblast", "2024-04-01 10:00:00", "2024-04-01 10:59:59", "raion", "R"),       # 3599 s
        row("Sumska oblast", "2024-04-02 10:00:00", "2024-04-02 11:00:01", "raion", "R"),       # 3601 s
        row("Sumska oblast", "2024-04-03 10:00:00", "2024-04-03 10:30:00", "raion", "R"),       # 1800 s
        open_row("Sumska oblast", "2024-04-04 10:00:00"),                                       # open: never counted
    ]
    a = data.load_official(write(tmp_path, base_rows() + extra), cfg_for(24 + len(extra), 1))
    # base_rows() are 24 exact-1h oblast rows (one per unit)
    assert dq.exact_duration_counts(a, 3600) == {"total": 25, "by_level": {"oblast": 24, "hromada": 1}}
    assert dq.exact_duration_counts(a, 1800) == {"total": 1, "by_level": {"raion": 1}}
    assert dq.exact_duration_counts(a, 7) == {"total": 0, "by_level": {}}
    ok = {3600: {"total": 25, "by_level": {"oblast": 24, "hromada": 1}}}
    assert dq.check_exact_durations(a, ok) == ok
    with pytest.raises(data.DataQualityError, match="fabricated_1h_ends"):
        dq.check_exact_durations(a, {3600: {"total": 26, "by_level": {"oblast": 24, "hromada": 2}}})
    with pytest.raises(data.DataQualityError):  # same total, wrong per-level split
        dq.check_exact_durations(a, {3600: {"total": 25, "by_level": {"oblast": 25}}})


# ---------------- §E3 synthetic ----------------

def shared(rows):
    df = pd.DataFrame([{"source": "t", "alert_id": str(i), "unit": u, "level": lvl,
                        "started_at": pd.Timestamp(s), "finished_at": pd.Timestamp(e),
                        "alert_level": ""} for i, (u, lvl, s, e) in enumerate(rows)])
    return df


def reform_fixture():
    rows = []
    for u in ("A", "B"):
        for k in range(12):  # before the reform: oblast-level alerts
            s = pd.Timestamp("2025-09-03", tz="UTC") + pd.Timedelta(days=7 * k)
            rows.append((u, "oblast", s, s + pd.Timedelta(hours=1)))
        for k in range(12):  # after: raion / hromada alerts only
            s = pd.Timestamp("2026-01-03", tz="UTC") + pd.Timedelta(days=7 * k)
            rows.append((u, "raion" if k % 2 else "hromada", s, s + pd.Timedelta(hours=1)))
    rows.append(("A", "hromada", pd.Timestamp("2026-02-01 05:00", tz="UTC"),
                 pd.Timestamp("2026-03-15 05:00", tz="UTC")))  # standing > 24h: D-020 cap applies
    return shared(rows)


def test_collapse_check_passes_all_levels_and_fails_oblast_only():
    a = reform_fixture()
    r = dq.check_onset_collapse(a, CFG.standing_cap, unit_list=["A", "B"])
    assert r.set_index("unit").loc["A", "late_onsets"] == 13 and r.set_index("unit").loc["B", "late_onsets"] == 12
    with pytest.raises(data.DataQualityError, match="collapse"):
        dq.check_onset_collapse(a[a.level == "oblast"], CFG.standing_cap, unit_list=["A", "B"])


def test_collapse_check_raises_on_too_few_early_onsets():
    a = reform_fixture()
    a = a[~((a.unit == "B") & (a.started_at < pd.Timestamp("2025-12-01", tz="UTC"))
            & (a.started_at >= pd.Timestamp("2025-09-25", tz="UTC")))]
    with pytest.raises(data.DataQualityError, match="< 10 onsets"):
        dq.check_onset_collapse(a, CFG.standing_cap, unit_list=["A", "B"])


# ---------------- real data (fails, like tests/test_leakage.py, when the file is absent) ----------------

@pytest.fixture(scope="module")
def real():
    if not DATA.exists():
        pytest.fail(f"{DATA} missing: run scripts/run_all.py --config official once to download it")
    return data.load_official(DATA, CFG)


def test_real_exact_duration_pins(real):
    got = dq.check_exact_durations(real)
    assert got[3600] == {"total": 255, "by_level": {"hromada": 109, "raion": 87, "oblast": 59}}
    assert got[1800]["total"] == 38


def test_real_no_onset_collapse_across_admin_reform(real):
    r = dq.check_onset_collapse(real, CFG.standing_cap)
    assert len(r) == 24 and (r.early_onsets >= dq.COLLAPSE_MIN_EARLY).all()
    print(r.sort_values("ratio").to_string(index=False))
