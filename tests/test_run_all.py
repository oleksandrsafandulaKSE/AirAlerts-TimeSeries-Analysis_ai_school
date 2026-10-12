import dataclasses
import json

import pytest

from scripts import run_all
from src import config, data, regions

HEADER = "oblast,raion,hromada,level,started_at,finished_at,source\n"


def fixture(tmp_path, dup=False):
    rows = []
    for d in range(1, 29):
        for i, v in enumerate(regions.UNITS.values()):
            rows.append(f"{v['official_name']},,,oblast,2024-02-{d:02d} {i % 24:02d}:10:00+00:00,"
                        f"2024-02-{d:02d} {i % 24:02d}:40:00+00:00,official\n")
    if dup:
        rows.append(rows[0])
    p = tmp_path / "f.csv"
    p.write_text(HEADER + "".join(rows))
    return p, len(rows)


def cfg(n_raw, n_dup):
    import pandas as pd
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    return dataclasses.replace(config.official(), grid_start=ts("2024-02-02"), grid_end=ts("2024-02-27"),
                               coverage_end=ts("2024-02-28"), approved_gaps=(),
                               test=(ts("2024-02-20"), ts("2024-02-27")),
                               expected_raw_rows=n_raw, expected_duplicate_rows=n_dup)


def test_run_writes_meta(tmp_path, monkeypatch):
    p, n = fixture(tmp_path)
    monkeypatch.setattr(run_all.grid, "check_base_rate", lambda g, before: 0.0)
    out = tmp_path / "out"
    run_all.run_pipeline(cfg(n, 0), p, out)
    meta = json.loads((out / "run_meta.json").read_text())
    for k in ["config", "dates", "data_sha256", "row_counts", "git_commit", "python", "packages", "features"]:
        assert k in meta
    assert (out / "m1_checks.json").exists() and (out / "base_rate_by_quarter.csv").exists()
    assert (out / "m2_checks.json").exists()
    assert meta["features"] == run_all.features.FEATURES and "active_at_t" not in meta["features"]


@pytest.mark.parametrize("argv,exc", [(["--config", "new_regime"], NotImplementedError),
                                      (["--config", "official", "--as-of", "2026-10-01"], ValueError),
                                      (["--config", "nope"], ValueError)])
def test_main_rejects_before_reading_data(argv, exc, tmp_path):
    with pytest.raises(exc):
        run_all.main(argv + ["--data-path", str(tmp_path / "missing.csv"), "--out-dir", str(tmp_path / "o")])
    assert not (tmp_path / "o").exists()


def test_failed_check_writes_nothing(tmp_path):
    p, n = fixture(tmp_path, dup=True)
    out = tmp_path / "out"
    with pytest.raises(data.DataQualityError):
        run_all.run_pipeline(cfg(n, 0), p, out)
    assert not out.exists()
