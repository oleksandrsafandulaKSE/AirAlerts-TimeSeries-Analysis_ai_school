import dataclasses

import pandas as pd
import pytest

from src import config, data, regions

HEADER = "oblast,raion,hromada,level,started_at,finished_at,source\n"


def row(oblast, start, end, level="oblast", raion="", hromada=""):
    return f"{oblast},{raion},{hromada},{level},{start}+00:00,{end}+00:00,official\n"


def base_rows():
    # one row per canonical unit so the 24-unit check passes
    return [row(v["official_name"], "2024-01-01 10:00:00", "2024-01-01 11:00:00")
            for v in regions.UNITS.values()]


def cfg_for(raw, dups):
    return dataclasses.replace(config.official(), expected_raw_rows=raw, expected_duplicate_rows=dups)


def write(tmp_path, rows):
    p = tmp_path / "f.csv"
    p.write_text(HEADER + "".join(rows))
    return p


def test_dedup_exclude_and_shared_format(tmp_path):
    extra = [
        row("Kyiv City", "2024-02-01 10:00:00", "2024-02-01 10:30:00"),
        row("Kyiv City", "2024-02-01 10:00:00", "2024-02-01 10:30:00"),       # exact dup
        row("Kyiv City", "2024-02-01 10:00:00", "2024-02-01 10:31:00"),       # differs -> kept
        row("Kyivska oblast", "2024-03-01 10:00:00", "2024-03-01 10:30:00", "hromada", "Buchanskyi", "X"),
        row("Kyivska oblast", "2024-03-01 10:00:00", "2024-03-01 10:30:00", "hromada", "Buchanskyi", "X"),  # dup
        row("Luhanska oblast", "2024-01-01 00:00:00", "2024-01-02 00:00:00"),
    ]
    p = write(tmp_path, base_rows() + extra)
    stats = {}
    a = data.load_official(p, cfg_for(30, 2), stats)
    assert stats["duplicate_rows"] == 2 and stats["excluded_rows"] == 1
    assert len(a) == 24 + 3
    assert list(a.columns) == data.SHARED_COLUMNS
    assert (a.source == "official").all() and (a.alert_level == "").all()
    assert str(a.started_at.dt.tz) == "UTC"
    assert set(a.unit) == set(regions.units())
    assert (a.unit == "kyiv_city").sum() == 3 and (a.unit == "kyivska").sum() == 2
    assert regions.group_of("kyiv_city") == "kyiv_city" and regions.group_of("kyivska") == "rear"
    c = data.alert_counts(a)
    assert c["exactly_30min_total"] == 2
    assert c["exactly_30min_by_level"] == {"oblast": 1, "hromada": 1}


def test_unknown_name_raises(tmp_path):
    p = write(tmp_path, base_rows() + [row("Atlantis oblast", "2024-01-01 00:00:00", "2024-01-01 01:00:00")])
    with pytest.raises(KeyError):
        data.load_official(p, cfg_for(25, 0))


def test_23_units_raises(tmp_path):
    p = write(tmp_path, base_rows()[1:])
    with pytest.raises(data.DataQualityError):
        data.load_official(p, cfg_for(23, 0))


def test_count_mismatches_raise(tmp_path):
    p = write(tmp_path, base_rows())
    with pytest.raises(data.DataQualityError):
        data.load_official(p, cfg_for(25, 0))
    with pytest.raises(data.DataQualityError):
        data.load_official(p, cfg_for(24, 1))


def test_end_before_start_raises(tmp_path):
    p = write(tmp_path, base_rows() + [row("Kyiv City", "2024-05-01 10:00:00", "2024-05-01 09:00:00")])
    with pytest.raises(data.DataQualityError):
        data.load_official(p, cfg_for(25, 0))


def test_naive_timestamp_raises(tmp_path):
    naive = "Kyiv City,,,oblast,2024-05-01 10:00:00,2024-05-01 11:00:00+00:00,official\n"
    p = write(tmp_path, base_rows() + [naive])
    with pytest.raises(data.DataQualityError):
        data.load_official(p, cfg_for(25, 0))


def test_over_24h_counter(tmp_path):
    p = write(tmp_path, base_rows() + [row("Sumska oblast", "2024-05-01 00:00:00", "2024-05-03 00:00:00"),
                                       row("Sumska oblast", "2024-06-01 00:00:00", "2024-06-02 00:00:00")])
    a = data.load_official(p, cfg_for(26, 0))
    c = data.alert_counts(a)
    assert c["over_24h_total"] == 1 and c["over_24h_by_unit"] == {"sumska": 1}  # exactly 24h is not > 24h
