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
