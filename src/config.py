"""Named run configs (D-017 #3). No dates are hard-coded anywhere else."""
from dataclasses import dataclass, field

import pandas as pd


def _ts(s):
    return pd.Timestamp(s, tz="UTC")


@dataclass(frozen=True)
class RunConfig:
    name: str
    source: str
    grid_start: pd.Timestamp
    grid_end: pd.Timestamp            # exclusive
    coverage_end: pd.Timestamp        # last moment the source is known to be recording
    train: tuple                      # half-open [start, end) (D-021)
    val: tuple
    test: tuple
    H: pd.Timedelta = pd.Timedelta(hours=1)
    target_levels: str = "any"
    standing_cap: pd.Timedelta = pd.Timedelta(hours=24)
    approved_gaps: tuple = ()          # tuple of (start, end), half-open
    post_gap_mask: pd.Timedelta = pd.Timedelta(hours=24)
    expected_raw_rows: int | None = None
    expected_duplicate_rows: int | None = None
    gap_min_hours: int = 24
    data_url: str = ""
    extra: dict = field(default_factory=dict)


OFFICIAL_URL = ("https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/"
                "main/datasets/official_data_en.csv")


def uncertainty_zones(cfg):
    """Approved gaps extended by the post-gap mask: [g0, g1 + post_gap) (M2 plan §4)."""
    return tuple((g0, g1 + cfg.post_gap_mask) for g0, g1 in cfg.approved_gaps)


def official():
    return RunConfig(
        name="official",
        source="official",
        grid_start=_ts("2022-03-23 00:00"),
        grid_end=_ts("2026-09-07 00:00"),
        coverage_end=_ts("2026-09-07 05:28"),
        train=(_ts("2022-03-23 00:00"), _ts("2026-06-29 00:00")),
        val=(_ts("2026-06-29 00:00"), _ts("2026-07-27 00:00")),
        test=(_ts("2026-07-27 00:00"), _ts("2026-09-07 00:00")),
        approved_gaps=((_ts("2026-08-29 00:00"), _ts("2026-09-03 00:00")),),
        expected_raw_rows=299_275,
        expected_duplicate_rows=113_845,
        data_url=OFFICIAL_URL,
    )


def new_regime():
    # D-015 exploratory window; the API loader arrives in M4.
    return RunConfig(
        name="new_regime",
        source="api",
        grid_start=_ts("2026-09-13 00:00"),
        grid_end=_ts("2026-10-12 00:00"),
        coverage_end=_ts("2026-10-12 16:45"),
        train=(None, None), val=(None, None),
        test=(_ts("2026-09-13 00:00"), _ts("2026-10-12 00:00")),
    )


def monthly(as_of):
    raise NotImplementedError("monthly(as_of) is M6 future work (D-016); M1 exception to D-017")


def get_config(name, as_of=None):
    if name == "official":
        return official()
    if name == "new_regime":
        return new_regime()
    if name == "monthly":
        return monthly(as_of)
    raise ValueError(f"unknown config: {name!r}")
