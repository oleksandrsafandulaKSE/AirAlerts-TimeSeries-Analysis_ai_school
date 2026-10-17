"""M6a collector (plans/M6a.md §6): offline. HTTP via a fake session, time via a fake clock; no network."""
import csv
import dataclasses
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest
import requests

from collect import api_collector as C
from src import config, data, regions

ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
SECRET = "TEST-SECRET-XYZ"
SEED_FETCH = datetime(2026, 10, 17, 3, 0, 0, tzinfo=UTC)
LIVE_START = datetime(2026, 10, 18, 3, 17, 0, tzinfo=UTC)


def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def rec(i, uid, start, end=None, upd=None, level="raion", kind="air_raid", lvl="yellow", notes=None, raion=None):
    """A complete API record (14 fields, + location_raion if given). `start`/`end`/`upd` are datetimes."""
    unit = regions.unit_from_api_uid(uid)
    r = {"id": i, "location_title": "x", "location_type": level, "started_at": ts(start),
         "finished_at": ts(end) if end else None, "updated_at": ts(upd or end or start), "alert_type": kind,
         "location_oblast": regions.UNITS[unit]["api_oblast_name"], "location_uid": "999", "notes": notes,
         "country": None, "alert_level": lvl, "location_title_en": "x", "location_oblast_uid": 999}
    if raion is not None:
        r["location_raion"] = raion
    return r


def pull(uid, records, fetched):
    return {"uid": uid, "records": records, "fetched_at": C.fmt_ts(fetched)}


def make_dump(tmp_path, fetch=SEED_FETCH, extra=None, name="2026-10-17T0300Z"):
    """Dump in the saved format (manifest 3..31, 404 for UIDs 6/7): one closed alert per unit + extra {uid: [...]}."""
    d = tmp_path / name
    d.mkdir()
    lines = ["uid\thttp\tbytes\tfetched_at_utc"]
    nid = 5000
    for uid in range(3, 32):
        f = fetch.strftime("%Y-%m-%dT%H:%M:%SZ")
        if uid in regions.API_404_UIDS:
            lines.append(f"{uid}\t404\t0\t{f}")
            (d / f"uid_{uid}.json").write_text("")
            continue
        lines.append(f"{uid}\t200\t1\t{f}")
        als = []
        if uid not in regions.EXCLUDED_API_UIDS:
            nid += 1
            als.append(rec(nid, uid, fetch - timedelta(days=2), fetch - timedelta(days=2) + timedelta(minutes=30)))
        if uid == 9:                       # one old end, so the national window check (>= 29 d) is satisfied
            als.append(rec(4999, uid, fetch - timedelta(days=29, hours=13), fetch - timedelta(days=29, hours=12)))
        als += (extra or {}).get(uid, [])
        (d / f"uid_{uid}.json").write_text(json.dumps({"alerts": als, "meta": {}, "disclaimer": ""}))
    (d / "manifest.tsv").write_text("\n".join(lines) + "\n")
    return d


class FakeClock:
    def __init__(self, t):
        self.t, self.sleeps = t, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += timedelta(seconds=s)


class FakeResp:
    def __init__(self, status, payload=None, text=None):
        self.status_code, self._payload, self._text = status, payload, text

    def json(self):
        if self._text is not None:
            return json.loads(self._text)
        return self._payload


class FakeSession:
    """Per-UID scripts of ('ok', duration) | ('status', code, duration) | ('timeout', duration) | ('badjson', d).
    UIDs without a script answer ('ok', 1). 'ok' returns one closed alert finished a day before the call."""

    def __init__(self, clock, scripts=None, ok_duration=1):
        self.clock, self.scripts, self.ok_duration = clock, scripts or {}, ok_duration
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        uid = int(url.split("/regions/")[1].split("/")[0])
        self.calls.append({"uid": uid, "start": self.clock.now(), "url": url, "headers": dict(headers or {})})
        script = self.scripts.get(uid)
        step = script.pop(0) if script else ("ok", self.ok_duration)
        self.clock.t += timedelta(seconds=step[-1])
        if step[0] == "timeout":
            raise requests.Timeout("read timed out")
        if step[0] == "status":
            return FakeResp(step[1])
        if step[0] == "badjson":
            return FakeResp(200, text="{not json")
        t = self.clock.now()
        als = [rec(90000 + uid, uid, t - timedelta(days=1, hours=1), t - timedelta(days=1)),
               rec(95000 + uid, uid, t - timedelta(days=29, hours=13), t - timedelta(days=29, hours=12))]
        return FakeResp(200, {"alerts": als, "meta": {}, "disclaimer": ""})


def seeded(tmp_path, extra=None):
    store, log = tmp_path / "ds" / "alerts_in_ua.csv", tmp_path / "pull_log.csv"
    C.seed_from_dump(make_dump(tmp_path, extra=extra), store, log, "abc123")
    return store, log


def snapshot(*paths):
    return [p.read_bytes() if p.exists() else None for p in paths]


# ---------------- 1. seed ----------------

def test_seed_rows_units_types_open_and_log(tmp_path):
    extra = {31: [rec(1, 31, SEED_FETCH - timedelta(days=3), kind="artillery_shelling", lvl="red"),
                  rec(2, 31, SEED_FETCH - timedelta(days=3), kind="urban_fights"),
                  rec(3, 31, SEED_FETCH - timedelta(days=40))],                          # open, started long ago
             14: [rec(4, 14, SEED_FETCH - timedelta(days=1), SEED_FETCH - timedelta(hours=20), level="hromada",
                      raion="Бучанський район")]}
    store, log = seeded(tmp_path, extra)
    rows = C.read_datastore(store)
    assert len(rows) == 25 + 4
    by_id = {r["id"]: r for r in rows}
    assert by_id[1]["unit"] == "kyiv_city" and by_id[4]["unit"] == "kyivska"     # by requested UID, not 999
    assert by_id[1]["alert_type"] == "artillery_shelling" and by_id[2]["alert_type"] == "urban_fights"
    assert by_id[3]["finished_at"] is None
    assert by_id[4]["location_raion"] == "Бучанський район" and "location_raion" not in by_id[1]
    assert {r["fetched_at"] for r in rows} == {"2026-10-17T03:00:00Z"}
    assert {r["pull_id"] for r in rows} == {"seed-2026-10-17T0300Z"}
    lg = C.read_log(log)
    assert len(lg) == 24 and {int(r["uid"]) for r in lg} == set(C.unit_uids())
    assert all(r["git_commit"] == "abc123" and r["nominal_window_from"] == "2026-09-17T03:00:00Z" for r in lg)
    # seeded rows are unknown before the dump's fetch time (OBSERVED view)
    assert C.as_known_at(rows, SEED_FETCH - timedelta(seconds=1)) == []
    assert len(C.as_known_at(rows, SEED_FETCH)) == 25 + 4


def test_seed_refused_into_non_empty_datastore(tmp_path):
    store, log = seeded(tmp_path)
    with pytest.raises(C.CollectError, match="seed refused"):
        C.seed_from_dump(make_dump(tmp_path, name="other"), store, log, "abc")


# ---------------- 2. merge + known-at-t ----------------

def naive_latest(rows, t):
    """NEGATIVE CONTROL: latest updated_at regardless of fetched_at (future knowledge leaks in)."""
    return [r2 for r in C._latest_per_id(rows) if (r2 := C._hide_future(r, t)) is not None]


def test_merge_versions_and_known_at_with_negative_control(tmp_path):
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    d = datetime(2026, 10, 20, tzinfo=UTC)
    open_v = rec(7, 31, d + timedelta(hours=8), upd=d + timedelta(hours=8, seconds=1))
    closed_v = rec(7, 31, d + timedelta(hours=8), d + timedelta(hours=10), upd=d + timedelta(hours=10, seconds=2))
    corrected = rec(7, 31, d + timedelta(hours=7, minutes=50), d + timedelta(hours=10),
                    upd=d + timedelta(days=1, hours=12))
    C.apply_pulls(store, log, [pull(31, [open_v], d + timedelta(hours=9))], "p1", "c")
    assert C.apply_pulls(store, log, [pull(31, [open_v], d + timedelta(hours=11))], "p1b", "c").new_rows == []   # 0 rows
    assert len(C.apply_pulls(store, log, [pull(31, [closed_v], d + timedelta(days=1, hours=3, minutes=17))],
                             "p2", "c").new_rows) == 1
    C.apply_pulls(store, log, [pull(31, [corrected], d + timedelta(days=2, hours=3, minutes=17))], "p3", "c")
    rows = C.read_datastore(store)
    assert len(rows) == 3
    full = C.as_known_at(rows)
    assert len(full) == 1 and full[0]["started_at"] == corrected["started_at"]

    t1 = d + timedelta(hours=12)
    k1 = C.as_known_at(rows, t1)
    assert k1[0]["finished_at"] is None and k1[0]["started_at"] == open_v["started_at"]
    t2 = d + timedelta(days=1, hours=4)
    k2 = C.as_known_at(rows, t2)
    assert k2[0]["finished_at"] == closed_v["finished_at"] and k2[0]["started_at"] == open_v["started_at"]
    # the naive selector leaks the later correction and the end into t1 -> must fail the same assertions
    n1 = naive_latest(rows, t1)
    assert not (n1[0]["finished_at"] is None and n1[0]["started_at"] == open_v["started_at"])


def test_known_at_hides_future_end_and_drops_future_start():
    t = datetime(2026, 10, 20, 12, tzinfo=UTC)
    base = {"requested_uid": 31, "unit": "kyiv_city", "fetched_at": "2026-10-20T11:00:00Z", "pull_id": "p"}
    end_row = {**rec(1, 31, t - timedelta(hours=1), t + timedelta(seconds=1)), **base}
    at_t = {**rec(2, 31, t - timedelta(hours=1), t), **base}
    start_row = {**rec(3, 31, t + timedelta(seconds=1)), **base}
    for view in (C.as_known_at, C.as_reconstructed_at):
        got = {r["id"]: r for r in view([end_row, at_t, start_row], t)}
        assert got[1]["finished_at"] is None                      # step (3): end after t hidden
        assert got[2]["finished_at"] == at_t["finished_at"]       # boundary: end exactly at t kept
        assert 3 not in got                                       # step (4): start after t dropped
        later = {r["id"]: r for r in view([end_row, at_t, start_row], t + timedelta(seconds=1))}
        assert later[1]["finished_at"] == end_row["finished_at"] and 3 in later


# ---------------- 3. append-only guard ----------------

def test_append_only_guard_and_negative_control(tmp_path, monkeypatch):
    with pytest.raises(C.CollectError, match="append-only"):
        C.check_append_only(b"h\nrow1\n", b"h\nrowX\nrow2\n", "x")
    store, log = seeded(tmp_path)
    before = snapshot(store, log)
    real = C.render_csv

    def rewriting_render(columns, rows):                 # a buggy writer that rewrites the first old row
        rows = [list(r) for r in rows]
        if columns == C.COLUMNS and rows:
            rows[0][C.COLUMNS.index("alert_level")] = "red" if rows[0][14] != "red" else "yellow"
        return real(columns, rows)

    monkeypatch.setattr(C, "render_csv", rewriting_render)
    t = SEED_FETCH + timedelta(days=1)
    with pytest.raises(C.CollectError, match="append-only"):
        C.apply_pulls(store, log, [pull(31, [rec(77, 31, t - timedelta(hours=2), t - timedelta(hours=1))], t)],
                      "p", "c")
    assert snapshot(store, log) == before


# ---------------- 4. conflicts ----------------

def test_same_key_different_content_and_id_under_two_uids(tmp_path):
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    t = datetime(2026, 10, 20, 12, tzinfo=UTC)
    a = rec(1, 31, t - timedelta(hours=2), t - timedelta(hours=1))
    C.apply_pulls(store, log, [pull(31, [a], t), pull(14, [], t)], "p1", "c")
    changed = {**a, "alert_level": "red"}
    with pytest.raises(C.CollectError, match="same key, different content"):
        C.apply_pulls(store, log, [pull(31, [changed], t + timedelta(hours=1))], "p2", "c")
    with pytest.raises(C.CollectError, match="under two UIDs"):
        C.apply_pulls(store, log, [pull(31, [], t + timedelta(hours=1)),
                                   pull(14, [rec(1, 14, t - timedelta(hours=2), t - timedelta(hours=1))],
                                        t + timedelta(hours=1))], "p3", "c")


# ---------------- 5. HTTP failures ----------------

@pytest.mark.parametrize("script,match", [
    ([("status", 403, 1)], "403: likely geo-block.*self-hosted"),
    ([("status", 401, 1)], "401, token rejected"),
    ([("status", 404, 1)], "HTTP 404"),
    ([("status", 500, 1)] * 3, "retry budget exhausted"),
    ([("badjson", 1)], "invalid JSON"),
])
def test_http_failures_raise_and_write_nothing(tmp_path, script, match):
    store, log = seeded(tmp_path)
    before = snapshot(store, log)
    clock = FakeClock(LIVE_START)
    with pytest.raises(C.CollectError, match=match):
        C.collect(store, log, SECRET, FakeSession(clock, {9: list(script)}), clock, "c")
    assert snapshot(store, log) == before


def test_exhausted_429_prints_one_line_per_attempt(tmp_path, capsys):
    store, log = seeded(tmp_path)
    before = snapshot(store, log)
    clock = FakeClock(LIVE_START)
    with pytest.raises(C.CollectError, match="retry budget exhausted"):
        C.collect(store, log, SECRET, FakeSession(clock, {3: [("status", 429, 1)] * 3}), clock, "c")
    lines = [l for l in capsys.readouterr().out.splitlines() if "uid  3 attempt" in l]
    assert len(lines) == 3 and all("HTTP 429" in l for l in lines)
    assert "retry in 120 s" in lines[0] and "budget exhausted" in lines[2]
    assert snapshot(store, log) == before


# ---------------- 6. rate and budget ----------------

def test_spacing_and_successful_run_writes_log(tmp_path):
    store, log = seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    session = FakeSession(clock, {3: [("status", 429, 1)]})
    C.collect(store, log, SECRET, session, clock, "c")
    starts = [c["start"] for c in session.calls]
    assert len(starts) == 25
    assert all((b - a).total_seconds() >= 120 for a, b in zip(starts, starts[1:]))
    assert 120 in clock.sleeps
    lg = C.read_log(log)
    new = [r for r in lg if not r["pull_id"].startswith("seed")]
    assert len(new) == 24 and {r["pull_id"] for r in new} == {"2026-10-18T0317Z"}
    r3 = next(r for r in new if r["uid"] == "3")
    assert (r3["n_retries_429"], r3["n_retries_other"]) == ("1", "0")


def test_budget_exhaustion_per_uid_and_per_run(tmp_path):
    store, log = seeded(tmp_path)
    before = snapshot(store, log)
    clock = FakeClock(LIVE_START)
    # 7 retryable failures spread over 4 UIDs (<= 2 each): the 7th raises
    scripts = {u: [("timeout", 30)] * 2 for u in (3, 4, 5, 8)}
    with pytest.raises(C.CollectError, match="retry budget exhausted"):
        C.collect(store, log, SECRET, FakeSession(clock, scripts), clock, "c")
    assert snapshot(store, log) == before


def test_worst_successful_schedule_within_64_minutes(tmp_path):
    store, log = seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    scripts = {u: [("timeout", 30)] * 2 for u in (3, 4, 5)}          # 6 retryable failures, <= 2 per UID
    C.collect(store, log, SECRET, FakeSession(clock, scripts, ok_duration=30), clock, "c")
    assert (clock.now() - LIVE_START) <= timedelta(minutes=64)
    assert len([r for r in C.read_log(log) if r["n_retries_other"] == "2"]) == 3


# ---------------- 7. token ----------------

def test_token_never_leaks(tmp_path, capsys):
    store, log = seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    session = FakeSession(clock)
    C.collect(store, log, SECRET, session, clock, "c")
    assert session.calls[0]["headers"]["Authorization"] == f"Bearer {SECRET}"      # it is sent ...
    assert all(SECRET not in c["url"] for c in session.calls)                       # ... only in the header
    clock2 = FakeClock(LIVE_START + timedelta(days=1))
    with pytest.raises(C.CollectError) as e:
        C.collect(store, log, SECRET, FakeSession(clock2, {3: [("status", 403, 1)]}), clock2, "c")
    out = capsys.readouterr()
    assert SECRET not in out.out + out.err + str(e.value)
    assert SECRET.encode() not in store.read_bytes() + log.read_bytes()


def test_missing_token_raises_before_any_request(tmp_path):
    store, log = seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    session = FakeSession(clock)
    with pytest.raises(C.CollectError, match="missing or empty"):
        C.collect(store, log, "", session, clock, "c")
    assert session.calls == []


def test_cli_reads_token_from_env_file(tmp_path, monkeypatch):
    from scripts import collect_api
    monkeypatch.delenv("ALERTS_IN_UA_TOKEN", raising=False)
    f = tmp_path / ".env"
    f.write_text(f"OTHER=1\nALERTS_IN_UA_TOKEN='{SECRET}'\n")
    assert collect_api.read_token(f) == SECRET
    with pytest.raises(C.CollectError, match="not found"):
        collect_api.read_token(tmp_path / "missing.env")


# ---------------- 8. schema + encoding ----------------

T0 = datetime(2026, 10, 20, 12, tzinfo=UTC)


def good():
    return rec(1, 31, T0 - timedelta(hours=2), T0 - timedelta(hours=1))


@pytest.mark.parametrize("mutate,match", [
    (lambda r: r.update(extra_field=1), "schema change"),
    (lambda r: r.pop("country"), "schema change"),
    (lambda r: r.update(alert_level="green"), "alert_level"),
    (lambda r: r.update(started_at="2026-10-20 10:00:00"), "ending in 'Z'"),
    (lambda r: r.update(started_at="2026-13-40T10:00:00.000Z"), "invalid date"),
    (lambda r: r.update(id="1"), "expected int"),
    (lambda r: r.update(location_raion=None), "is null"),
    (lambda r: r.update(location_oblast="Київська область"), "location_oblast"),
    (lambda r: r.update(finished_at=ts(T0 - timedelta(hours=3))), "finished_at < started_at"),
])
def test_schema_violations_raise(mutate, match):
    r = good()
    mutate(r)
    with pytest.raises(C.CollectError, match=match):
        C.validate_pull(31, {"alerts": [r]}, T0)


def test_window_check_and_new_alert_type_kept():
    old = rec(2, 31, T0 - timedelta(days=32), T0 - timedelta(days=31))
    with pytest.raises(C.CollectError, match="older than fetched_at - 30 d"):
        C.validate_pull(31, {"alerts": [old]}, T0)
    new_type = {**good(), "alert_type": "chemical"}
    assert C.validate_pull(31, {"alerts": [new_type]}, T0) == [new_type]
    with pytest.raises(C.CollectError, match="no 'alerts' list"):
        C.validate_pull(31, {"data": []}, T0)


@pytest.mark.parametrize("value,cell", [(None, ""), ("", "\\e"), ("\\e", "\\\\e"), ("\\x", "\\\\x"), ("plain", "plain"),
                                        (7, "7")])
def test_cell_encoding_round_trip(value, cell):
    assert C.encode_cell(value) == cell
    field = "id" if isinstance(value, int) else "notes"
    assert C.decode_cell(cell, field) == value


def test_encoding_through_file_and_corrupt_cell(tmp_path):
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    variants = [None, "", "\\e", "\\x", 'quote " and, comma\nnewline']
    recs = [{**rec(10 + i, 31, T0 - timedelta(hours=2), T0 - timedelta(hours=1)), "notes": v}
            for i, v in enumerate(variants)]
    recs.append(rec(20, 31, T0 - timedelta(hours=2), level="hromada", raion="R"))          # open + raion
    C.apply_pulls(store, log, [pull(31, recs, T0)], "p1", "c")
    rows = {r["id"]: r for r in C.read_datastore(store)}
    assert [rows[10 + i]["notes"] for i in range(len(variants))] == variants
    assert rows[20]["finished_at"] is None and rows[20]["location_raion"] == "R"
    assert "location_raion" not in rows[10]
    assert C.apply_pulls(store, log, [pull(31, recs, T0 + timedelta(hours=1))], "p2", "c").new_rows == []   # reload == fetch
    txt = store.read_text().replace("\\\\x", "\\x", 1)                                            # corrupt a cell
    store.write_text(txt)
    with pytest.raises(C.CollectError, match="corrupt cell"):
        C.read_datastore(store)


def test_real_datastore_empty_notes_witness():
    """The 3 real records with notes == "" (ids 266250, 262685, 262686) survive seed -> write -> reload, and a
    re-merge of the same records adds 0 rows (canonical types after reload)."""
    store = ROOT / "datastore" / "alerts_in_ua.csv"
    assert store.exists(), "datastore/alerts_in_ua.csv is missing: run the seed (plans/M6a.md §7)"
    rows = C.read_datastore(store)
    wit = [r for r in rows if r["id"] in (266250, 262685, 262686)]
    assert len(wit) == 3 and all(r["notes"] == "" for r in wit)
    recs = [{k: v for k, v in r.items() if k != "_file_uid"} for r in C.to_api_records(wit)]
    uids = sorted({r["requested_uid"] for r in wit})
    assert uids == [14, 15]
    pulls = [pull(u, [x for x, r in zip(recs, wit) if r["requested_uid"] == u], T0) for u in uids]
    new, _ = C.merge(rows, pulls, "p")
    assert new == []


# ---------------- 9. coverage holes + crash recovery ----------------

def test_coverage_holes_are_recorded_and_collection_continues(tmp_path):
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    holes = C.default_holes_path(log)
    t = datetime(2026, 10, 20, tzinfo=UTC)
    C.apply_pulls(store, log, [pull(31, [], t), pull(14, [], t)], "p0", "c")
    assert holes.read_text() == ",".join(C.HOLES_COLUMNS) + "\n"                          # header-only, always written
    C.apply_pulls(store, log, [pull(31, [], t + timedelta(days=1)), pull(14, [], t)], "p1", "c")
    # window_from = day 0.5: later than p0 (day 0) but not than the LATEST previous pull p1 (day 1) -> no hole
    # (records a hole if find_holes used the earliest previous fetched_at instead of the latest)
    assert C.apply_pulls(store, log, [pull(31, [], t + timedelta(days=30, hours=12))], "p_half", "c").holes == []
    # exactly 30 days after the previous pull: window_from == previous fetched_at -> no hole
    assert C.apply_pulls(store, log, [pull(14, [], t + timedelta(days=30))], "p30", "c").holes == []
    # 31 days after uid 31's last pull: the data IS written, one hole row with exact open-interval ends
    a = rec(9, 31, t + timedelta(days=61, hours=-2), t + timedelta(days=61, hours=-1))
    res = C.apply_pulls(store, log, [pull(31, [a], t + timedelta(days=61, hours=12))], "p_gap", "c")
    assert len(res.new_rows) == 1 and 9 in {r["id"] for r in C.read_datastore(store)}
    hr = list(csv.DictReader(open(holes)))
    assert hr == [{"pull_id": "p_gap", "uid": "31", "unit": "kyiv_city", "hole_from": "2026-11-19T12:00:00Z",
                   "hole_to": "2026-11-20T12:00:00Z", "git_commit": "c"}]
    # next day: no new hole row
    assert C.apply_pulls(store, log, [pull(31, [], t + timedelta(days=62, hours=12))], "p_next", "c").holes == []
    assert len(list(csv.DictReader(open(holes)))) == 1
    # endpoints: covered at both ends of the OPEN hole, not just inside
    lg = C.read_log(log)
    a_, b_ = C.parse_ts("2026-11-19T12:00:00Z"), C.parse_ts("2026-11-20T12:00:00Z")
    assert C.covered(lg, hr, 31, a_) and C.covered(lg, hr, 31, b_)
    assert not C.covered(lg, hr, 31, a_ + timedelta(seconds=1)) and not C.covered(lg, hr, 31, b_ - timedelta(seconds=1))


def crash_on(path, monkeypatch):
    """Make os.replace raise when renaming onto `path` (simulates a crash before that rename)."""
    real = C.os.replace

    def fake(src, dst):
        if Path(dst) == Path(path):
            raise OSError("simulated crash")
        return real(src, dst)

    monkeypatch.setattr(C.os, "replace", fake)
    return real


def test_crash_before_log_rename_is_detected_and_repair_restarts(tmp_path, monkeypatch):
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    t = datetime(2026, 10, 20, 12, tzinfo=UTC)
    C.apply_pulls(store, log, [pull(31, [], t)], "p0", "c")
    holes = C.default_holes_path(log)
    before = {p: p.read_bytes() for p in (store, holes)}
    real = crash_on(log, monkeypatch)
    with pytest.raises(OSError):
        C.apply_pulls(store, log, [pull(31, [rec(5, 31, t - timedelta(hours=2), t - timedelta(hours=1))],
                                        t + timedelta(hours=1))], "p1", "c")
    monkeypatch.setattr(C.os, "replace", real)
    with pytest.raises(C.CollectError, match="incomplete previous run.*restore BOTH"):
        C.apply_pulls(store, log, [pull(31, [], t + timedelta(hours=2))], "p2", "c")
    for p, b in before.items():                     # the repair: both files back to the last committed state
        p.write_bytes(b)
    assert C.apply_pulls(store, log, [pull(31, [], t + timedelta(hours=2))], "p2", "c").holes == []


def test_first_hole_crash_with_zero_new_rows_repair_restarts(tmp_path, monkeypatch):
    store, log = seeded(tmp_path)
    holes = C.default_holes_path(log)
    assert holes.exists()                            # the seed writes the header-only holes file
    before = {p: p.read_bytes() for p in (store, holes)}
    late = SEED_FETCH + timedelta(days=31)
    pulls = [pull(u, [], late) for u in C.unit_uids()]
    real = crash_on(log, monkeypatch)
    with pytest.raises(OSError):
        C.apply_pulls(store, log, pulls, "p_gap", "c")
    monkeypatch.setattr(C.os, "replace", real)
    assert holes.read_bytes() != before[holes]       # an orphan hole row was renamed in
    with pytest.raises(C.CollectError, match="incomplete previous run"):
        C.apply_pulls(store, log, pulls, "p_gap2", "c")
    for p, b in before.items():
        p.write_bytes(b)
    res = C.apply_pulls(store, log, pulls, "p_gap2", "c")
    assert len(res.holes) == 24 and res.new_rows == []


# ---------------- 10. compatibility with src.data.api_alerts ----------------

def test_datastore_loads_like_the_dump_through_src_data(tmp_path):
    fetch = datetime(2026, 10, 26, 12, tzinfo=UTC)
    dst = [rec(1, 31, datetime(2026, 10, 25, 0, 59, 59, tzinfo=UTC), datetime(2026, 10, 25, 1, 0, 0, tzinfo=UTC)),
           rec(2, 31, fetch - timedelta(days=3))]                                        # open, > 24 h old
    kyivska = [rec(3, 14, fetch - timedelta(days=1), fetch - timedelta(hours=23), level="hromada", raion="R")]
    dump = make_dump(tmp_path, fetch=fetch, extra={31: dst, 14: kyivska}, name="2026-10-26T1200Z")
    store, log = tmp_path / "s.csv", tmp_path / "l.csv"
    C.seed_from_dump(dump, store, log, "c")
    rows = C.read_datastore(store)
    by_id = {r["id"]: r for r in rows}
    assert by_id[1]["started_at"] == "2026-10-25T00:59:59.000Z" and by_id[1]["finished_at"] == "2026-10-25T01:00:00.000Z"
    assert by_id[1]["unit"] == "kyiv_city" and by_id[3]["unit"] == "kyivska" and by_id[2]["finished_at"] is None

    cfg = dataclasses.replace(config.new_regime_all_types(), history_start=pd.Timestamp(fetch) - pd.Timedelta(days=30),
                              coverage_end=pd.Timestamp(fetch))
    records, manifest = data.read_api_dump(dump)
    expected = data.api_alerts(records, manifest, cfg)
    got = data.api_alerts(C.to_api_records(C.as_known_at(rows)), manifest, cfg)
    pd.testing.assert_frame_equal(got, expected)


# ---------------- review fixes (reviewer + harness) ----------------

def test_national_window_check_catches_a_shrunken_window(tmp_path):
    store, log = seeded(tmp_path)
    before = snapshot(store, log)

    class ShortWindow(FakeSession):              # the API suddenly returns only the last ~7 days
        def get(self, url, headers=None, timeout=None):
            r = super().get(url, headers, timeout)
            if r.status_code == 200:
                t = self.clock.now()
                r._payload["alerts"] = [a for a in r._payload["alerts"] if C.parse_ts(a["finished_at"]) > t - timedelta(days=7)]
            return r

    clock = FakeClock(LIVE_START)
    with pytest.raises(C.CollectError, match="shorter than 29 days"):
        C.collect(store, log, SECRET, ShortWindow(clock), clock, "c")
    assert snapshot(store, log) == before


def test_missing_store_next_to_real_log_and_empty_log_raise(tmp_path):
    store, log = seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    with pytest.raises(C.CollectError, match="not in the datastore"):
        C.collect(tmp_path / "typo" / "alerts_in_ua.csv", log, SECRET, FakeSession(clock), clock, "c")
    with pytest.raises(C.CollectError, match="seed the datastore first"):
        C.collect(tmp_path / "e" / "s.csv", tmp_path / "e" / "l.csv", SECRET, FakeSession(clock), clock, "c")


def test_pull_id_collision_fails_before_any_request(tmp_path):
    store, log = seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    C.collect(store, log, SECRET, FakeSession(clock), clock, "c")
    clock2 = FakeClock(LIVE_START + timedelta(seconds=30))            # same minute -> same pull_id
    s2 = FakeSession(clock2)
    with pytest.raises(C.CollectError, match="already in the log"):
        C.collect(store, log, SECRET, s2, clock2, "c")
    assert s2.calls == []


def test_naive_datetime_and_empty_seed_name_raise(tmp_path, monkeypatch):
    with pytest.raises(C.CollectError, match="naive"):
        C.fmt_ts(datetime(2026, 1, 1))
    assert C.fmt_ts(datetime(2026, 1, 1, 0, 0, 0, 1, tzinfo=UTC)) == "2026-01-01T00:00:01Z"   # rounded UP
    monkeypatch.chdir("/")
    with pytest.raises(C.CollectError, match="cannot derive a pull_id"):
        C.seed_from_dump(".", tmp_path / "s.csv", tmp_path / "l.csv", "c")


@pytest.mark.parametrize("line", [f"ALERTS_IN_UA_TOKEN={SECRET}", f"export ALERTS_IN_UA_TOKEN={SECRET}",
                                  f"ALERTS_IN_UA_TOKEN={SECRET} # main token", f'ALERTS_IN_UA_TOKEN="{SECRET}" # c'])
def test_cli_env_file_styles(tmp_path, monkeypatch, line):
    from scripts import collect_api
    monkeypatch.delenv("ALERTS_IN_UA_TOKEN", raising=False)
    f = tmp_path / ".env"
    f.write_text(f"# comment\n{line}\n")
    assert collect_api.read_token(f) == SECRET


# ---------------- exit codes: CLI and the workflow, executed offline ----------------

def run_cli(tmp_path, monkeypatch, clock, session):
    from scripts import collect_api
    monkeypatch.setenv("ALERTS_IN_UA_TOKEN", SECRET)
    monkeypatch.setattr(collect_api, "git_head", lambda: "c")
    monkeypatch.setattr(collect_api.C, "SystemClock", lambda: clock)

    class Ctx:
        def __enter__(self):
            return session

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(collect_api.requests, "Session", Ctx)
    return collect_api.main(["--datastore", str(tmp_path / "ds"), "--log", str(tmp_path / "pull_log.csv"),
                             "--holes", str(tmp_path / "coverage_holes.csv")])


def test_cli_exit_codes(tmp_path, monkeypatch):
    seeded(tmp_path)
    clock = FakeClock(LIVE_START)
    assert run_cli(tmp_path, monkeypatch, clock, FakeSession(clock)) == 0
    clock = FakeClock(LIVE_START + timedelta(days=31))
    assert run_cli(tmp_path, monkeypatch, clock, FakeSession(clock)) == 3
    assert len(list(csv.DictReader(open(tmp_path / "coverage_holes.csv")))) == 24
    before = snapshot(tmp_path / "ds" / "alerts_in_ua.csv", tmp_path / "pull_log.csv", tmp_path / "coverage_holes.csv")
    clock = FakeClock(LIVE_START + timedelta(days=32))
    with pytest.raises(C.CollectError):
        run_cli(tmp_path, monkeypatch, clock, FakeSession(clock, {3: [("status", 404, 1)]}))
    assert snapshot(tmp_path / "ds" / "alerts_in_ua.csv", tmp_path / "pull_log.csv",
                    tmp_path / "coverage_holes.csv") == before


def workflow_steps():
    """Minimal parser for .github/workflows/collect_api.yml steps (name / id / if / shell / run block)."""
    text = (ROOT / ".github" / "workflows" / "collect_api.yml").read_text()
    body = text.split("\n    steps:\n", 1)[1]
    steps = []
    for chunk in body.split("\n      - ")[1:]:
        lines = chunk.splitlines()
        st = {"name": lines[0].split("name:", 1)[1].strip()}
        k = 1
        while k < len(lines):
            line = lines[k]
            stripped = line.strip()
            if stripped.startswith(("id:", "if:", "shell:")):
                key, val = stripped.split(":", 1)
                st[key] = val.strip()
            elif stripped == "run: |":
                block = []
                k += 1
                while k < len(lines) and (lines[k].startswith("          ") or not lines[k].strip()):
                    block.append(lines[k][10:])
                    k += 1
                st["run"] = "\n".join(block).strip() + "\n"
                continue
            elif stripped.startswith("run:"):
                st["run"] = stripped.split(":", 1)[1].strip() + "\n"
            k += 1
        steps.append(st)
    return steps


def condition(expr, code):
    py = expr.replace("steps.collect.outputs.code", repr(code)).replace("||", " or ").replace("&&", " and ")
    return eval(py, {"__builtins__": {}})          # only == / != on string literals


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


@pytest.mark.parametrize("code", ["0", "3", "1"])
def test_workflow_routing_executed_against_a_bare_origin(tmp_path, code):
    origin, work = tmp_path / "origin.git", tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    git(tmp_path, "init", "-q", "-b", "main", str(work))
    for rel, txt in (("datastore/alerts_in_ua.csv", "h\n"), ("reports/collect/pull_log.csv", "pull_id\np0,1\n"),
                     ("reports/collect/coverage_holes.csv", "pull_id\n")):
        (work / rel).parent.mkdir(parents=True, exist_ok=True)
        (work / rel).write_text(txt)
    git(work, "-c", "user.name=t", "-c", "user.email=t@t", "add", ".")
    git(work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
    git(work, "remote", "add", "origin", str(origin))
    git(work, "push", "-q", "origin", "main")
    # stub collector: 0 -> new rows; 3 -> new rows + a hole row; 1 -> writes nothing
    stub = tmp_path / "bin"
    stub.mkdir()
    (stub / "python").write_text(f"""#!/bin/bash
if [ "{code}" != "1" ]; then echo "x" >> datastore/alerts_in_ua.csv; echo "p1,2" >> reports/collect/pull_log.csv; fi
if [ "{code}" = "3" ]; then echo "p1,hole" >> reports/collect/coverage_holes.csv; fi
exit {code}
""")
    (stub / "python").chmod(0o755)
    env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "GITHUB_OUTPUT": str(tmp_path / "out.txt")}
    steps = workflow_steps()
    names = [s["name"] for s in steps]
    start = names.index("Pull alerts.in.ua history (24 units, 1 request / 2 min)")
    events, outputs, job_ok = [], {}, True
    for st in steps[start:]:
        cond = st.get("if")
        run_it = job_ok and (cond is None or condition(cond, outputs.get("code", "")))
        if not run_it:
            continue
        script = st["run"].replace("${{ steps.collect.outputs.code }}", outputs.get("code", ""))
        shell = ["bash", "--noprofile", "--norc"] if st.get("shell") == "bash {0}" else \
            ["bash", "--noprofile", "--norc", "-eo", "pipefail"]
        r = subprocess.run(shell + ["-c", script], cwd=work, env=env, capture_output=True, text=True)
        events.append((st["name"], r.returncode))
        if st.get("id") == "collect":
            outputs = dict(l.split("=", 1) for l in (tmp_path / "out.txt").read_text().split())
        if r.returncode != 0:
            job_ok = False
    pushed = git(tmp_path, "--git-dir", str(origin), "log", "--format=%s", "main").splitlines()
    if code == "0":
        assert job_ok and len(pushed) == 2
        files = git(tmp_path, "--git-dir", str(origin), "show", "--name-only", "--format=", "main").split()
        assert files == ["datastore/alerts_in_ua.csv", "reports/collect/pull_log.csv"]
    elif code == "3":
        assert not job_ok and len(pushed) == 2
        files = git(tmp_path, "--git-dir", str(origin), "show", "--name-only", "--format=", "main").split()
        assert "reports/collect/coverage_holes.csv" in files
        assert [e[0] for e in events][-2:] == ["Commit the new rows", "Fail the run on a coverage hole or a failed pull"]
        assert events[-2][1] == 0 and events[-1][1] != 0          # published BEFORE the run fails
    else:
        assert not job_ok and len(pushed) == 1                       # nothing published
        assert "Commit the new rows" not in [e[0] for e in events]


def test_deleted_holes_file_raises(tmp_path):
    store, log = seeded(tmp_path)
    C.default_holes_path(log).unlink()
    clock = FakeClock(LIVE_START)
    with pytest.raises(C.CollectError, match="coverage_holes.csv is missing"):
        C.collect(store, log, SECRET, FakeSession(clock), clock, "c")
    with pytest.raises(C.CollectError, match="coverage_holes.csv is missing"):
        C.apply_pulls(store, log, [pull(31, [], LIVE_START)], "p", "c")
