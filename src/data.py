"""Load sources into the one shared alert format (D-017 #2). Data checks RAISE (D-017 #6)."""
import hashlib
from pathlib import Path

import pandas as pd
import requests

from src import regions

SHARED_COLUMNS = ["source", "alert_id", "unit", "level", "started_at", "finished_at", "alert_level"]
OFFICIAL_COLUMNS = ["oblast", "raion", "hromada", "level", "started_at", "finished_at", "source"]


class DataQualityError(RuntimeError):
    pass


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download_official(cfg, cache_dir="data"):
    """Re-use the cached copy if present, else download once."""
    path = Path(cache_dir) / "official_data_en.csv"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(cfg.data_url, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
    print(f"[data] official file: {path} sha256={file_sha256(path)[:12]}")
    return path


def load_official(path, cfg, stats=None):
    """Raw strings -> dedup on raw strings -> exclude -> map -> parse UTC -> checks -> shared format."""
    stats = {} if stats is None else stats
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    if list(raw.columns) != OFFICIAL_COLUMNS:
        raise DataQualityError(f"unexpected columns {list(raw.columns)}")
    n_raw = len(raw)
    print(f"[data] raw rows: {n_raw:,}")
    if cfg.expected_raw_rows is not None and n_raw != cfg.expected_raw_rows:
        raise DataQualityError(f"raw rows {n_raw} != expected {cfg.expected_raw_rows}")

    dedup = raw.drop_duplicates()
    n_dup = n_raw - len(dedup)
    print(f"[data] exact duplicate rows dropped (raw strings): {n_dup:,} -> {len(dedup):,} rows")
    if cfg.expected_duplicate_rows is not None and n_dup != cfg.expected_duplicate_rows:
        raise DataQualityError(f"duplicates {n_dup} != expected {cfg.expected_duplicate_rows}")
    if dedup.duplicated().sum() != 0:
        raise DataQualityError("duplicates remain after dedup")

    excl = dedup["oblast"].isin(regions.EXCLUDED)
    print(f"[data] excluded-unit rows dropped: {int(excl.sum())} "
          f"({dedup.loc[excl, 'oblast'].value_counts().to_dict()})")
    kept = dedup.loc[~excl]
    unit = kept["oblast"].map(regions.unit_from_official)  # unknown name -> KeyError
    if set(unit) != set(regions.units()):
        raise DataQualityError(f"unit set mismatch: missing={set(regions.units()) - set(unit)}")

    if (kept["started_at"] == "").any():
        raise DataQualityError("empty started_at")
    offset = r"(?:\+00:00|Z)$"
    for col in ("started_at", "finished_at"):
        vals = kept[col][kept[col] != ""]
        if not vals.str.contains(offset).all():
            raise DataQualityError(f"{col}: timestamps without an explicit UTC offset, e.g. "
                                   f"{vals[~vals.str.contains(offset)].iloc[0]!r}")
    started = pd.to_datetime(kept["started_at"], utc=True, format="ISO8601")
    finished = pd.to_datetime(kept["finished_at"].replace("", None), utc=True, format="ISO8601")
    if (finished < started).any():
        raise DataQualityError(f"{int((finished < started).sum())} rows with finished_at < started_at")

    alert_id = kept.apply(lambda r: hashlib.sha1("\x1f".join(r.values).encode()).hexdigest(), axis=1)
    out = pd.DataFrame({
        "source": "official",
        "alert_id": alert_id.values,
        "unit": unit.values,
        "level": kept["level"].values,
        "started_at": started.values,
        "finished_at": finished.values,
        "alert_level": "",
    })[SHARED_COLUMNS]
    out["started_at"] = pd.to_datetime(out["started_at"], utc=True)
    out["finished_at"] = pd.to_datetime(out["finished_at"], utc=True)
    if out["alert_id"].duplicated().any():
        raise DataQualityError("alert_id collision")
    stats.update(raw_rows=n_raw, duplicate_rows=n_dup, dedup_rows=len(dedup),
                 excluded_rows=int(excl.sum()), final_rows=len(out))
    print(f"[data] shared format: {out.shape}, {out.started_at.min()} -> {out.started_at.max()}")
    return out.sort_values(["unit", "started_at"], ignore_index=True)


def alert_counts(alerts):
    """Printed-only diagnostics (D-010, D-020). finished_at here never feeds a rule."""
    dur = alerts["finished_at"] - alerts["started_at"]
    return {
        "missing_finished_at": int(alerts["finished_at"].isna().sum()),
        "zero_duration": int((dur == pd.Timedelta(0)).sum()),
        "exactly_30min_total": int((dur == pd.Timedelta(minutes=30)).sum()),
        "exactly_30min_by_level": alerts.loc[dur == pd.Timedelta(minutes=30), "level"].value_counts().to_dict(),
        "over_24h_by_unit": alerts.loc[dur > pd.Timedelta(hours=24), "unit"].value_counts().to_dict(),
        "over_24h_total": int((dur > pd.Timedelta(hours=24)).sum()),
        "rows_by_level": alerts["level"].value_counts().to_dict(),
        "rows_by_unit": alerts["unit"].value_counts().to_dict(),
    }
