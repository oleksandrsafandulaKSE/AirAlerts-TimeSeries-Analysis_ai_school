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


# ---------------- alerts.in.ua API dump (M4 plan §5.1; D-007, D-015, D-027) ----------------

def read_api_dump(dump_dir):
    """Raw records + manifest from a saved dump (no network). Every record keeps the UID of the file it came from
    (the requested region), which is the ONLY unit key (location_oblast_uid holds raion ids)."""
    import csv
    import json
    dump_dir = Path(dump_dir)
    with open(dump_dir / "manifest.tsv") as fh:
        manifest = [{"uid": int(r["uid"]), "http": int(r["http"]),
                     "fetched_at": pd.Timestamp(r["fetched_at_utc"]).tz_convert("UTC")}
                    for r in csv.DictReader(fh, delimiter="\t")]
    uids = {m["uid"] for m in manifest}
    if uids != set(range(3, 32)):
        raise DataQualityError(f"manifest UIDs {sorted(uids)} != 3..31")
    not_found = {m["uid"] for m in manifest if m["http"] == 404}
    if not_found != regions.API_404_UIDS or any(m["http"] not in (200, 404) for m in manifest):
        raise DataQualityError(f"unexpected HTTP statuses: 404 for {sorted(not_found)}")
    records = []
    for m in manifest:
        if m["http"] != 200:
            continue
        payload = json.loads((dump_dir / f"uid_{m['uid']}.json").read_text())
        for a in payload["alerts"]:
            records.append({**a, "_file_uid": m["uid"]})
    return records, manifest


def api_alerts(records, manifest, cfg, stats=None, require_all_units=True):
    """Raw API records -> shared alert format. Dedup by id keeping the latest updated_at; open alerts are KEPT
    (finished_at = NaT = end unknown; the D-020 cap handles them, D-027). Checks raise."""
    stats = {} if stats is None else stats
    raw = pd.DataFrame(records)
    stats["records_raw"] = len(raw)
    excl = raw["_file_uid"].isin(regions.EXCLUDED_API_UIDS)
    stats["excluded_uid_records"] = {int(k): int(v) for k, v in raw.loc[excl, "_file_uid"].value_counts().items()}
    raw = raw.loc[~excl].copy()
    raw["unit"] = raw["_file_uid"].map(regions.unit_from_api_uid)  # unknown UID -> KeyError
    for u, g in raw.groupby("unit"):  # file identity: exactly one oblast, the one its UID maps to
        names = set(g["location_oblast"])
        if names != {regions.UNITS[u]["api_oblast_name"]}:
            raise DataQualityError(f"{u}: file names oblast(s) {names}, expected {regions.UNITS[u]['api_oblast_name']!r}")
    # alert types: the config must name the kept types explicitly; an unlisted type present raises (M4 plan §5.1)
    stats["alert_types"] = raw["alert_type"].value_counts().to_dict()
    kept_types = cfg.api_alert_types
    if kept_types is None:
        raise DataQualityError(f"api_alert_types not set in config; types present: {stats['alert_types']}")
    unknown = set(raw["alert_type"]) - set(kept_types) - {"air_raid", "artillery_shelling", "urban_fights"}
    if unknown:
        raise DataQualityError(f"unexpected alert types {sorted(unknown)}")
    stats["alert_types_dropped"] = raw.loc[~raw["alert_type"].isin(kept_types), "alert_type"].value_counts().to_dict()
    raw = raw.loc[raw["alert_type"].isin(kept_types)].copy()
    for col in ("started_at", "updated_at"):
        if not raw[col].str.endswith("Z").all():
            raise DataQualityError(f"{col}: timestamps without a 'Z' (UTC) suffix")
    fin = raw["finished_at"].dropna()
    if not fin.str.endswith("Z").all():
        raise DataQualityError("finished_at: timestamps without a 'Z' (UTC) suffix")
    raw["_updated"] = pd.to_datetime(raw["updated_at"], utc=True, format="ISO8601")  # sort as times, not text
    two_units = raw.groupby("id")["unit"].nunique()
    if (two_units > 1).any():
        raise DataQualityError(f"alert ids present under two units: {two_units[two_units > 1].index[:5].tolist()}")
    raw = raw.sort_values(["id", "_updated"], kind="stable")
    n0 = len(raw)
    raw = raw.drop_duplicates("id", keep="last")
    stats["duplicate_ids_dropped"] = n0 - len(raw)
    started = pd.to_datetime(raw["started_at"], utc=True, format="ISO8601")
    finished = pd.to_datetime(raw["finished_at"], utc=True, format="ISO8601")
    if (finished < started).any():
        raise DataQualityError(f"{int((finished < started).sum())} API alerts with finished_at < started_at")
    out = pd.DataFrame({
        "source": "api", "alert_id": raw["id"].astype(str).to_numpy(), "unit": raw["unit"].to_numpy(),
        "level": raw["location_type"].to_numpy(), "started_at": started.to_numpy(),
        "finished_at": finished.to_numpy(), "alert_level": raw["alert_level"].to_numpy(),
    })[SHARED_COLUMNS]
    out["started_at"] = pd.to_datetime(out["started_at"], utc=True)
    out["finished_at"] = pd.to_datetime(out["finished_at"], utc=True)
    if not set(out["alert_level"]) <= {"yellow", "red"}:
        raise DataQualityError(f"unexpected alert_level values {sorted(set(out['alert_level']))}")
    if require_all_units and set(out["unit"]) != set(regions.units()):
        raise DataQualityError(f"API unit set mismatch: missing {set(regions.units()) - set(out['unit'])}")
    is_open = out["finished_at"].isna()
    stats["open_alerts"] = int(is_open.sum())
    stats["open_by_unit"] = out.loc[is_open, "unit"].value_counts().to_dict()
    if cfg.history_start is not None:
        stats["open_started_in_window"] = int((is_open & (out["started_at"] >= cfg.history_start)
                                               & (out["started_at"] < cfg.grid_end)).sum())
    stats["alerts"] = len(out)
    return out.sort_values(["unit", "started_at", "alert_id"], ignore_index=True)


def check_api_coverage(manifest, cfg):
    """history_start = max over the 24 units' files of (fetched_at - 30 days); coverage_end = earliest fetched_at
    of those files (M4 plan §5.2). Both must equal the config values."""
    unit_files = [m for m in manifest if m["http"] == 200 and m["uid"] not in regions.EXCLUDED_API_UIDS]
    hs = max(m["fetched_at"] for m in unit_files) - pd.Timedelta(days=30)
    ce = min(m["fetched_at"] for m in unit_files)
    if hs != cfg.history_start or ce != cfg.coverage_end:
        raise DataQualityError(f"API coverage differs from config: history_start {hs} vs {cfg.history_start}, "
                               f"coverage_end {ce} vs {cfg.coverage_end}")
    return hs, ce


def load_api(dump_dir, cfg, stats=None):
    records, manifest = read_api_dump(dump_dir)
    check_api_coverage(manifest, cfg)
    out = api_alerts(records, manifest, cfg, stats)
    print(f"[data] API: {stats.get('records_raw') if stats else ''} raw records -> {len(out):,} alerts "
          f"(open {int(out.finished_at.isna().sum())}), {out.started_at.min()} -> {out.started_at.max()}")
    return out


def truncate_api_records(records, t):
    """The dump as known at t: drop alerts starting after t; hide ends after t (leakage audit)."""
    out = []
    for r in records:
        s = pd.Timestamp(r["started_at"])
        if s > t:
            continue
        r2 = dict(r)
        if r2["finished_at"] is not None and pd.Timestamp(r2["finished_at"]) > t:
            r2["finished_at"] = None
        out.append(r2)
    return out
