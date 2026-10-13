"""API dump loader (M4 plan §5.1, D-027) on small JSON fixtures; no network."""
import dataclasses
import json

import pandas as pd
import pytest

from src import config, data, grid, regions

FETCH = pd.Timestamp("2026-10-12 16:45:00", tz="UTC")


def alert(i, uid, start, end, level="raion", kind="air_raid", lvl="yellow", upd=None, name=None):
    unit = None if uid in regions.EXCLUDED_API_UIDS else regions.unit_from_api_uid(uid)
    return {"id": i, "location_type": level, "started_at": start, "finished_at": end,
            "updated_at": upd or (end or start), "alert_type": kind, "alert_level": lvl,
            "location_oblast": name or (regions.UNITS[unit]["api_oblast_name"] if unit else "Луганська область"),
            "location_uid": "999", "location_oblast_uid": 999}


def make_dump(tmp_path, extra=None, drop_uid=None, override=None):
    """One closed yellow alert per unit + optional extra alerts {uid: [alerts]}."""
    d = tmp_path / "dump"
    d.mkdir()
    rows = ["uid\thttp\tbytes\tfetched_at_utc"]
    nid = 1000
    for uid in range(3, 32):
        if uid in regions.API_404_UIDS:
            rows.append(f"{uid}\t404\t0\t{FETCH.strftime('%Y-%m-%dT%H:%M:%SZ')}")
            (d / f"uid_{uid}.json").write_text("")
            continue
        rows.append(f"{uid}\t200\t1\t{FETCH.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        als = []
        if uid not in regions.EXCLUDED_API_UIDS and uid != drop_uid:
            nid += 1
            als.append(alert(nid, uid, "2026-09-20T10:00:00.000Z", "2026-09-20T10:30:00.000Z"))
        if uid in regions.EXCLUDED_API_UIDS and uid != 30:
            nid += 1
            als.append(alert(nid, uid, "2022-04-04T16:45:39.000Z", None, level="oblast", lvl="red"))
        als += (extra or {}).get(uid, [])
        if override and uid in override:
            als = override[uid]
        (d / f"uid_{uid}.json").write_text(json.dumps({"alerts": als, "meta": {}, "disclaimer": ""}))
    (d / "manifest.tsv").write_text("\n".join(rows) + "\n")
    return d


def cfg():
    return dataclasses.replace(config.new_regime(), history_start=FETCH - pd.Timedelta(days=30), coverage_end=FETCH)


def test_happy_path_open_kept_dedup_excluded(tmp_path):
    extra = {31: [alert(1, 31, "2026-10-01T08:00:00.000Z", None, upd="2026-10-01T08:00:01.000Z"),       # open
                  alert(2, 31, "2026-10-02T08:00:00.000Z", "2026-10-02T08:20:00.000Z", upd="2026-10-02T08:20:00Z"),
                  alert(2, 31, "2026-10-02T08:00:00.000Z", "2026-10-02T09:00:00.000Z", upd="2026-10-02T09:00:00Z"),
                  alert(3, 31, "2026-10-03T08:00:00.000Z", "2026-10-03T08:20:00.000Z", kind="artillery_shelling")]}
    stats = {}
    a = data.load_api(make_dump(tmp_path, extra), cfg(), stats)
    assert list(a.columns) == data.SHARED_COLUMNS and (a.source == "api").all()
    assert set(a.unit) == set(regions.units()) and len(a) == 24 + 2
    assert stats["excluded_uid_records"] == {16: 1, 29: 1}
    assert stats["alert_types_dropped"] == {"artillery_shelling": 1}
    assert stats["duplicate_ids_dropped"] == 1
    kc = a[a.unit == "kyiv_city"].set_index("alert_id")
    assert pd.isna(kc.loc["1", "finished_at"])                                     # open alert KEPT (D-027)
    assert kc.loc["2", "finished_at"] == pd.Timestamp("2026-10-02 09:00", tz="UTC")  # latest updated_at wins
    assert str(a.started_at.dt.tz) == "UTC" and set(a.alert_level) == {"yellow"}
    assert stats["open_alerts"] == 1


def test_open_alert_masks_24h_and_is_onset(tmp_path):
    extra = {31: [alert(1, 31, "2026-10-01T08:10:00.000Z", None)]}
    a = data.load_api(make_dump(tmp_path, extra), cfg())
    g = grid.build_grid(a[a.unit == "kyiv_city"], pd.Timestamp("2026-10-01 07:00", tz="UTC"),
                        pd.Timestamp("2026-10-02 10:00", tz="UTC"), pd.Timedelta(hours=1), unit_list=["kyiv_city"])
    g = g.set_index("t")
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    assert g.loc[ts("2026-10-01 08:00"), "y"] == 1                      # its start is an onset
    assert g.loc[ts("2026-10-02 08:00"), "active_at_t"] == 1            # still inside [s, s + 24h)
    assert g.loc[ts("2026-10-02 09:00"), "active_at_t"] == 0            # s + 24h = 08:10 -> 09:00 is past the cap


def test_identity_swap_raises(tmp_path):
    kyivska_name = regions.UNITS["kyivska"]["api_oblast_name"]
    bad = {31: [alert(5, 31, "2026-09-20T10:00:00.000Z", "2026-09-20T10:30:00.000Z", name=kyivska_name)]}
    with pytest.raises(data.DataQualityError):
        data.load_api(make_dump(tmp_path, override=bad), cfg())


def test_missing_z_and_missing_unit_and_manifest(tmp_path):
    bad = {31: [alert(5, 31, "2026-09-20T10:00:00", "2026-09-20T10:30:00.000Z")]}
    with pytest.raises(data.DataQualityError):
        data.load_api(make_dump(tmp_path, override=bad), cfg())
    (tmp_path / "b").mkdir()
    with pytest.raises(data.DataQualityError):                          # 23 units
        data.load_api(make_dump(tmp_path / "b", drop_uid=31), cfg())
    (tmp_path / "c").mkdir()
    d = make_dump(tmp_path / "c")
    m = (d / "manifest.tsv").read_text().replace("\n7\t404", "\n7\t200")
    (d / "manifest.tsv").write_text(m)
    (d / "uid_7.json").write_text(json.dumps({"alerts": []}))
    with pytest.raises(data.DataQualityError):                          # 404 set differs
        data.load_api(d, cfg())
    with pytest.raises(KeyError):
        regions.unit_from_api_uid(99)


def test_coverage_check(tmp_path):
    d = make_dump(tmp_path)
    with pytest.raises(data.DataQualityError):
        data.load_api(d, config.new_regime())                           # fixture fetch time != real config
    _, manifest = data.read_api_dump(d)
    assert data.check_api_coverage(manifest, cfg()) == (FETCH - pd.Timedelta(days=30), FETCH)


def test_truncate_records():
    recs = [{"started_at": "2026-10-01T08:00:00Z", "finished_at": "2026-10-01T09:00:00Z"},
            {"started_at": "2026-10-01T10:00:00Z", "finished_at": None}]
    t = pd.Timestamp("2026-10-01 08:30", tz="UTC")
    out = data.truncate_api_records(recs, t)
    assert len(out) == 1 and out[0]["finished_at"] is None and recs[0]["finished_at"] is not None


def test_bounded_gap_detection():
    ts = lambda s: pd.Timestamp(s, tz="UTC")  # noqa: E731
    rows = [{"unit": "kyiv_city", "started_at": ts("2024-05-20 09:31")}]          # old open alert, outside the range
    rows += [{"unit": "kyiv_city", "started_at": ts("2026-09-13 00:10") + pd.Timedelta(hours=h)} for h in range(0, 72, 3)]
    a = pd.DataFrame(rows)
    assert grid.detect_gaps(a, 24, ts("2026-09-13 00:00"), ts("2026-09-16 00:00")) == []
    assert len(grid.detect_gaps(a, 24)) == 1                                      # unbounded: sees the 2024->2026 silence


def test_dedup_sorts_times_not_text(tmp_path):
    extra = {31: [alert(7, 31, "2026-10-02T08:00:00.000Z", "2026-10-02T08:20:00.000Z", upd="2026-10-02T09:00:00Z"),
                  alert(7, 31, "2026-10-02T08:00:00.000Z", "2026-10-02T08:40:00.000Z", upd="2026-10-02T09:00:00.500Z")]}
    a = data.load_api(make_dump(tmp_path, extra), cfg())
    assert a.set_index("alert_id").loc["7", "finished_at"] == pd.Timestamp("2026-10-02 08:40", tz="UTC")


def test_same_id_under_two_units_raises(tmp_path):
    extra = {31: [alert(9, 31, "2026-10-02T08:00:00.000Z", "2026-10-02T08:20:00.000Z")],
             14: [alert(9, 14, "2026-10-02T08:00:00.000Z", "2026-10-02T08:20:00.000Z")]}
    with pytest.raises(data.DataQualityError):
        data.load_api(make_dump(tmp_path, extra), cfg())


def test_alert_type_choice_is_explicit(tmp_path):
    extra = {31: [alert(3, 31, "2026-10-03T08:00:00.000Z", "2026-10-03T08:20:00.000Z", kind="artillery_shelling")]}
    d = make_dump(tmp_path, extra)
    a_all = data.load_api(d, dataclasses.replace(cfg(), api_alert_types=("air_raid", "artillery_shelling", "urban_fights")))
    assert "3" in set(a_all.alert_id)
    with pytest.raises(data.DataQualityError):
        data.load_api(d, dataclasses.replace(cfg(), api_alert_types=None))
    (tmp_path / "x").mkdir()
    bad = {31: [alert(4, 31, "2026-10-03T08:00:00.000Z", "2026-10-03T08:20:00.000Z", kind="chemical")]}
    with pytest.raises(data.DataQualityError):
        data.load_api(make_dump(tmp_path / "x", bad), cfg())
