import pandas as pd
import pytest

from src import config


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def test_official_dates_d021():
    c = config.official()
    assert c.train == (ts("2022-03-23"), ts("2026-06-29"))  # D-021 amended (M2 decision 1)
    assert c.grid_start == c.train[0]
    assert c.val == (ts("2026-06-29"), ts("2026-07-27"))
    assert c.test == (ts("2026-07-27"), ts("2026-09-07"))
    assert c.train[1] == c.val[0] and c.val[1] == c.test[0]
    assert c.grid_end == c.test[1]
    assert c.coverage_end == ts("2026-09-07 05:28")
    assert c.approved_gaps == ((ts("2026-08-29"), ts("2026-09-03")),)
    assert c.H == pd.Timedelta(hours=1) and c.target_levels == "any"
    for x in (*c.train, *c.val, *c.test, c.grid_start, c.grid_end):
        assert str(x.tz) == "UTC"


def test_unknown_and_monthly():
    with pytest.raises(ValueError):
        config.get_config("nope")
    with pytest.raises(NotImplementedError):
        config.get_config("monthly", "2026-11-01")


@pytest.mark.parametrize("bad", [pd.Timedelta(0), pd.Timedelta(hours=-1), pd.Timedelta(minutes=90)])
def test_horizon_must_be_positive_whole_hours(bad):
    import dataclasses
    with pytest.raises(ValueError):
        dataclasses.replace(config.official(), H=bad)


def test_official_h3():
    import dataclasses
    o, h3 = config.official(), config.get_config("official_h3")
    assert h3.H == pd.Timedelta(hours=3) and o.H == pd.Timedelta(hours=1) and h3.name == "official_h3"
    same = {f.name for f in dataclasses.fields(o)} - {"name", "H"}
    assert all(getattr(o, k) == getattr(h3, k) for k in same)
    assert config.gap_label_mask_interval(h3) == ((ts("2026-08-28 21:00"), ts("2026-09-04 00:00")),)
    assert (o.H_label, h3.H_label) == ("1h", "3h")
