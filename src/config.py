"""Named run configs (D-017 #3). No dates are hard-coded anywhere else."""
from dataclasses import dataclass, field, replace

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
    recent_window: pd.Timedelta = pd.Timedelta(days=14)   # rolling recent-rate window (D-021)
    shrink_alpha: float = 10.0                            # pseudo-rows toward the unit train rate (M3)
    persistence_bins: tuple = (0, 60, 180, 720, float("inf"))  # minutes_since_last_end, [a, b)
    min_class_per_unit: int = 10                          # within-unit AUC: >= 10 pos and >= 10 neg
    history_start: pd.Timestamp | None = None             # API: start of complete coverage (M4 plan §5.2)
    data_path: str = ""                                   # API dump folder (relative to the repo root)
    low_n_rows: int = 100                                 # M4: groups with fewer eligible rows are flagged low-n
    api_alert_types: tuple | None = None                  # API alert types kept; any other type present -> raise
    data_url: str = ""
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        # forecasts are issued on an hourly grid; the horizon must be a positive whole number of hours
        if self.H <= pd.Timedelta(0) or self.H % pd.Timedelta(hours=1) != pd.Timedelta(0):
            raise ValueError(f"H must be a positive whole number of hours, got {self.H}")

    @property
    def H_label(self):
        return f"{int(self.H / pd.Timedelta(hours=1))}h"


OFFICIAL_URL = ("https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/"
                "main/datasets/official_data_en.csv")


EPOCH = pd.Timestamp("2000-01-01", tz="UTC")  # "minus infinity" for the history-start zone


def mask_gaps(cfg):
    """Missing-data intervals used for masks and features: the approved recording gaps, plus, for a source whose
    coverage starts at `history_start`, the interval [EPOCH, history_start) (M4 plan §5.2). Gap DETECTION
    still checks only `approved_gaps`."""
    extra = ((EPOCH, cfg.history_start),) if cfg.history_start is not None else ()
    return tuple(cfg.approved_gaps) + extra


def gap_label_mask_interval(cfg):
    """Rows masked by the gap: label window touches the gap, or post-gap state is unknowable.
    [g0 - H, g1 + post_gap) -> official: [2026-08-28 23:00, 2026-09-04 00:00) = 145 h (M3 plan §2)."""
    return tuple((g0 - cfg.H, g1 + cfg.post_gap_mask) for g0, g1 in mask_gaps(cfg))


def uncertainty_zones(cfg):
    """Missing-data intervals extended by the post-gap mask: [g0, g1 + post_gap) (M2 plan §4)."""
    return tuple((g0, g1 + cfg.post_gap_mask) for g0, g1 in mask_gaps(cfg))


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


def official_h3():
    """Additional horizon H = 3h (M3b, extra results row; the headline stays H = 1)."""
    return replace(official(), name="official_h3", H=pd.Timedelta(hours=3))


def new_regime():
    """D-015 exploratory window on the alerts.in.ua dump (M4 plan §5.2). `test` is the API scoring range.
    history_start = max over the 24 units' files of (fetched_at - 30 days); coverage_end = earliest fetched_at;
    both are asserted against the manifest by data.load_api."""
    return RunConfig(
        name="new_regime",
        source="api",
        grid_start=_ts("2026-09-13 00:00"),
        grid_end=_ts("2026-10-12 16:00"),
        coverage_end=_ts("2026-10-12 16:45:36"),
        train=(None, None), val=(None, None),
        test=(_ts("2026-09-13 00:00"), _ts("2026-10-12 16:00")),
        history_start=_ts("2026-09-12 17:00:43"),
        data_path="data/raw/alerts_in_ua/2026-10-12T1645Z",
        api_alert_types=("air_raid",),
    )


def new_regime_all_types():
    """Variant pending the human's decision (M4 escalation, reviews/M4-codex-artillery.md): keep every API alert type,
    because the official feed appears to include artillery-shelling alerts (Nikopol evidence). Reported side by side with
    `new_regime`; neither is adopted as the rule until the human decides."""
    return replace(new_regime(), name="new_regime_all_types",
                   api_alert_types=("air_raid", "artillery_shelling", "urban_fights"))


def monthly(as_of):
    raise NotImplementedError("monthly(as_of) is M6 future work (D-016); M1 exception to D-017")


def get_config(name, as_of=None):
    if name == "official":
        return official()
    if name == "official_h3":
        return official_h3()
    if name == "new_regime":
        return new_regime()
    if name == "new_regime_all_types":
        return new_regime_all_types()
    if name == "monthly":
        return monthly(as_of)
    raise ValueError(f"unknown config: {name!r}")
