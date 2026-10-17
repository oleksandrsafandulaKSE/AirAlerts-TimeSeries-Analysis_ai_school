"""alerts.in.ua history collector (plans/M6a.md): fetch -> validate -> append-only merge -> pull log.

One CSV row = one record VERSION, key (id, updated_at). Knowledge time of a version = `fetched_at` of the pull that
first saw it. Every check raises (D-017 #6); a failed run writes nothing. Exception (D-039 proposed): a coverage hole is
recorded in reports/collect/coverage_holes.csv and collection continues. The token is only ever put in a request
header: it never appears in URLs, prints, exception messages or files.
"""
import csv
import io
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from src import regions
from src.data import DataQualityError

API_BASE = "https://api.alerts.in.ua"
HISTORY_PATH = "/v1/regions/{uid}/alerts/month_ago.json"

SPACING_S = 120            # min gap between consecutive request STARTS (1 history request / 2 min, D-037 proposed)
RETRY_WAIT_S = 120         # wait after a retryable failure
HTTP_TIMEOUT_S = 30
MAX_RETRIES_PER_UID = 2
MAX_RETRIES_PER_RUN = 6
WINDOW = timedelta(days=30)
WINDOW_SLACK = timedelta(hours=1)
MIN_WINDOW = timedelta(days=29)    # national check: some unit must return an end this old (catches a shrunken window)

# the 14 fields every API record has, plus `location_raion` on hromada rows only
API_FIELDS = ("id", "location_title", "location_type", "started_at", "finished_at", "updated_at", "alert_type",
              "location_oblast", "location_uid", "notes", "country", "alert_level", "location_title_en",
              "location_oblast_uid")
OPTIONAL_FIELDS = ("location_raion",)
INT_FIELDS = {"id", "location_oblast_uid"}
NULLABLE_FIELDS = {"finished_at", "notes", "country"}
TIME_FIELDS = ("started_at", "updated_at", "finished_at")
ALERT_LEVELS = {"yellow", "red"}

COLUMNS = ["id", "updated_at", "requested_uid", "unit", "fetched_at", "pull_id", "location_type", "location_uid",
           "location_oblast", "location_oblast_uid", "location_raion", "location_title", "location_title_en",
           "alert_type", "alert_level", "started_at", "finished_at", "notes", "country"]
META_COLUMNS = ("requested_uid", "unit", "fetched_at", "pull_id")
API_COLUMNS = [c for c in COLUMNS if c not in META_COLUMNS]
HOLES_COLUMNS = ["pull_id", "uid", "unit", "hole_from", "hole_to", "git_commit"]
LOG_COLUMNS = ["pull_id", "uid", "unit", "http", "fetched_at", "nominal_window_from", "n_records", "n_new_rows",
               "n_open", "n_retries_429", "n_retries_other", "git_commit"]

_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$")
_EMPTY_STRING_CELL = "\\e"


class CollectError(DataQualityError):
    pass


def unit_uids():
    """The 24 forecast-unit UIDs, ascending (excluded and 404 UIDs are never requested)."""
    return sorted(v["api_uid"] for v in regions.UNITS.values())


# ---------------- time helpers ----------------

def parse_ts(s, what="timestamp"):
    """Strict ISO-8601 UTC ('...Z') -> aware datetime. Raises on anything else (e.g. month 13)."""
    if not isinstance(s, str) or not _TS_RE.match(s):
        raise CollectError(f"{what}: not an ISO-8601 UTC timestamp ending in 'Z': {s!r}")
    try:
        return datetime.fromisoformat(s[:-1] + "+00:00")
    except ValueError:
        raise CollectError(f"{what}: invalid date/time {s!r}") from None


def fmt_ts(dt):
    """Aware datetime -> 'YYYY-MM-DDTHH:MM:SSZ', rounded UP to the second (a knowledge time is never too early)."""
    if dt.tzinfo is None:
        raise CollectError("naive datetime: an aware UTC time is required")
    dt = dt.astimezone(timezone.utc)
    if dt.microsecond:
        dt = dt.replace(microsecond=0) + timedelta(seconds=1)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class SystemClock:
    def now(self):
        return datetime.now(timezone.utc)

    def sleep(self, seconds):
        import time
        time.sleep(seconds)


# ---------------- cell encoding (reversible; plans/M6a.md §4.1) ----------------

def encode_cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        raise CollectError("boolean values are not part of the schema")
    if isinstance(value, int):
        return str(value)
    if value == "":
        return _EMPTY_STRING_CELL
    if value.startswith("\\"):
        return "\\" + value
    return value


def decode_cell(cell, field):
    if cell == "":
        return None
    if cell == _EMPTY_STRING_CELL:
        value = ""
    elif cell.startswith("\\\\"):
        value = cell[1:]
    elif cell.startswith("\\"):
        raise CollectError(f"corrupt cell in column {field!r}: unknown escape {cell[:4]!r}")
    else:
        value = cell
    if field in INT_FIELDS or field == "requested_uid":
        if not re.fullmatch(r"-?\d+", value):
            raise CollectError(f"column {field!r}: not an integer: {value!r}")
        return int(value)
    return value


# ---------------- CSV files ----------------

def render_csv(columns, rows):
    """rows = lists of cell strings -> bytes (header + rows), one deterministic format."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    w.writerow(columns)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def read_cells(path, columns):
    """-> (raw bytes, list of cell lists). A missing or empty file = no rows. Header must match exactly."""
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return b"", []
    raw = path.read_bytes()
    reader = csv.reader(io.StringIO(raw.decode("utf-8"), newline=""))
    header = next(reader)
    if header != columns:
        raise CollectError(f"{path.name}: header {header} != expected {columns}")
    rows = list(reader)
    for i, r in enumerate(rows):
        if len(r) != len(columns):
            raise CollectError(f"{path.name}: row {i + 2} has {len(r)} cells, expected {len(columns)}")
    return raw, rows


def check_append_only(old_bytes, new_bytes, name):
    """The existing file must be an exact byte prefix of the new one (old rows never rewritten)."""
    if not new_bytes.startswith(old_bytes):
        raise CollectError(f"{name}: append-only guard failed (an existing row would change)")


def _write_tmp(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    return tmp


def write_all(store_path, store_bytes, holes_path, holes_bytes, log_path, log_bytes):
    """All files to temp files first, then renames in the order CSV, holes, log (the log last; plans/M6a.md §4.4)."""
    t1 = _write_tmp(store_path, store_bytes)
    t2 = _write_tmp(holes_path, holes_bytes)
    t3 = _write_tmp(log_path, log_bytes)
    os.replace(t1, store_path)
    os.replace(t2, holes_path)
    os.replace(t3, log_path)


def decode_row(cells):
    row = {}
    for c, cell in zip(COLUMNS, cells):
        v = decode_cell(cell, c)
        if c == "location_raion" and v is None:
            continue                                   # absent raion
        row[c] = v
    return row


def encode_row(row):
    return [encode_cell(row.get(c)) for c in COLUMNS]


def read_datastore(path):
    """Decoded rows (canonical types: ints, None for null, '' for the empty string, raion key absent if absent)."""
    _, cells = read_cells(path, COLUMNS)
    return [decode_row(r) for r in cells]


def read_log(path):
    _, cells = read_cells(path, LOG_COLUMNS)
    return [dict(zip(LOG_COLUMNS, r)) for r in cells]


# ---------------- validation (plans/M6a.md §4.3) ----------------

def validate_record(rec, uid):
    if not isinstance(rec, dict):
        raise CollectError(f"uid {uid}: a record is not an object")
    keys = set(rec)
    if keys - set(OPTIONAL_FIELDS) != set(API_FIELDS) or not keys <= set(API_FIELDS) | set(OPTIONAL_FIELDS):
        extra = sorted(keys - set(API_FIELDS) - set(OPTIONAL_FIELDS))
        missing = sorted(set(API_FIELDS) - keys)
        raise CollectError(f"uid {uid}: schema change (extra fields {extra}, missing fields {missing})")
    for f, v in rec.items():
        if isinstance(v, bool):
            raise CollectError(f"uid {uid}: field {f!r} has a boolean value")
        if f in INT_FIELDS:
            if not isinstance(v, int):
                raise CollectError(f"uid {uid}: field {f!r} is {type(v).__name__}, expected int")
        elif v is None:
            if f not in NULLABLE_FIELDS:
                raise CollectError(f"uid {uid} id {rec.get('id')}: field {f!r} is null")
        elif not isinstance(v, str):
            raise CollectError(f"uid {uid}: field {f!r} is {type(v).__name__}, expected str")
    unit = regions.unit_from_api_uid(uid)
    if rec["location_oblast"] != regions.UNITS[unit]["api_oblast_name"]:
        raise CollectError(f"uid {uid} id {rec['id']}: location_oblast {rec['location_oblast']!r} != "
                           f"{regions.UNITS[unit]['api_oblast_name']!r}")
    started = parse_ts(rec["started_at"], f"uid {uid} id {rec['id']} started_at")
    parse_ts(rec["updated_at"], f"uid {uid} id {rec['id']} updated_at")
    if rec["finished_at"] is not None:
        finished = parse_ts(rec["finished_at"], f"uid {uid} id {rec['id']} finished_at")
        if finished < started:
            raise CollectError(f"uid {uid} id {rec['id']}: finished_at < started_at")
    if rec["alert_level"] not in ALERT_LEVELS:
        raise CollectError(f"uid {uid} id {rec['id']}: unexpected alert_level {rec['alert_level']!r}")


def validate_pull(uid, payload, fetched_at):
    """-> list of validated records. `fetched_at` = aware datetime of the response."""
    if not isinstance(payload, dict) or not isinstance(payload.get("alerts"), list):
        raise CollectError(f"uid {uid}: response has no 'alerts' list")
    records = payload["alerts"]
    for rec in records:
        validate_record(rec, uid)
    closed = [parse_ts(r["finished_at"]) for r in records if r["finished_at"] is not None]
    if closed and min(closed) < fetched_at - WINDOW - WINDOW_SLACK:
        raise CollectError(f"uid {uid}: earliest finished_at {fmt_ts(min(closed))} is older than fetched_at - 30 d - 1 h "
                           f"({fmt_ts(fetched_at - WINDOW - WINDOW_SLACK)}); the API window is not what the coverage "
                           f"rule assumes")
    return records


def check_national_window(pulls):
    """The other direction of the window check: if the API window had SHRUNK, coverage would be claimed for days it
    never returned. Quiet units can lack old ends, so the check is national: the earliest `finished_at` over all
    units must be <= earliest fetched_at - 29 d. pulls = [{uid, records, fetched_at (str)}]."""
    closed = [parse_ts(r["finished_at"]) for p in pulls for r in p["records"] if r["finished_at"] is not None]
    first_fetch = min(parse_ts(p["fetched_at"]) for p in pulls)
    if not closed or min(closed) > first_fetch - MIN_WINDOW:
        got = fmt_ts(min(closed)) if closed else "none"
        raise CollectError(f"API window looks shorter than 29 days: earliest finished_at over all units {got} > "
                           f"{fmt_ts(first_fetch - MIN_WINDOW)}; the coverage rule would claim days never returned")


# ---------------- fetch (plans/M6a.md §3) ----------------

def fetch_all(token, session, clock, uids=None):
    """-> list of {uid, records, fetched_at, n_retries_429, n_retries_other}. Raises on any failure (nothing kept)."""
    if not token:
        raise CollectError("ALERTS_IN_UA_TOKEN is missing or empty")
    headers = {"Authorization": f"Bearer {token}"}
    uids = unit_uids() if uids is None else uids
    out, last_start, run_retries = [], None, 0
    for uid in uids:
        path = HISTORY_PATH.format(uid=uid)
        attempt, n429, nother = 0, 0, 0
        while True:
            attempt += 1
            if last_start is not None:
                gap = (clock.now() - last_start).total_seconds()
                if gap < SPACING_S:
                    clock.sleep(SPACING_S - gap)
            last_start = clock.now()
            try:
                resp = session.get(API_BASE + path, headers=headers, timeout=HTTP_TIMEOUT_S)
                status, label = resp.status_code, f"HTTP {resp.status_code}"
            except (requests.Timeout, requests.ConnectionError) as e:
                resp, status, label = None, None, type(e).__name__
            except requests.RequestException as e:
                raise CollectError(f"uid {uid} {path}: request failed ({type(e).__name__})") from None
            if status == 200:
                try:
                    payload = resp.json()
                except ValueError:
                    raise CollectError(f"uid {uid} {path}: invalid JSON") from None
                fetched_at = clock.now()
                print(f"[collect] uid {uid:>2} attempt {attempt}: {label}")
                break
            retryable = status is None or status == 429 or 500 <= status < 600
            if not retryable:
                print(f"[collect] uid {uid:>2} attempt {attempt}: {label} (not retryable)")
                if status == 401:
                    raise CollectError(f"uid {uid} {path}: 401, token rejected")
                if status == 403:
                    raise CollectError(f"uid {uid} {path}: 403: likely geo-block of the runner; "
                                       f"see self-hosted fallback (plans/M6a.md §5)")
                raise CollectError(f"uid {uid} {path}: HTTP {status}")
            if status == 429:
                n429 += 1
            else:
                nother += 1
            run_retries += 1
            if attempt > MAX_RETRIES_PER_UID or run_retries > MAX_RETRIES_PER_RUN:
                print(f"[collect] uid {uid:>2} attempt {attempt}: {label} -> retry budget exhausted "
                      f"(uid {attempt - 1}/{MAX_RETRIES_PER_UID}, run {run_retries - 1}/{MAX_RETRIES_PER_RUN})")
                raise CollectError(f"uid {uid} {path}: retry budget exhausted after {label}")
            print(f"[collect] uid {uid:>2} attempt {attempt}: {label} -> retry in {RETRY_WAIT_S} s")
            clock.sleep(RETRY_WAIT_S)
        out.append({"uid": uid, "payload": payload, "fetched_at": fetched_at,
                    "n_retries_429": n429, "n_retries_other": nother})
    return out


# ---------------- merge + log (plans/M6a.md §4.2, §4.4) ----------------

def _row_from_record(rec, uid, fetched_at_s, pull_id):
    row = {c: rec[c] for c in API_FIELDS}
    if "location_raion" in rec:
        row["location_raion"] = rec["location_raion"]
    row.update(requested_uid=uid, unit=regions.unit_from_api_uid(uid), fetched_at=fetched_at_s, pull_id=pull_id)
    return row


def _api_content(row):
    return tuple(row.get(c) for c in API_COLUMNS) + ("location_raion" in row,)


def merge(existing, pulls, pull_id):
    """existing = decoded rows; pulls = [{uid, records, fetched_at (str)}]. -> (new rows sorted, per-uid stats)."""
    by_key = {(r["id"], r["updated_at"]): r for r in existing}
    uid_of_id = {r["id"]: r["requested_uid"] for r in existing}
    new, stats = [], {}
    for p in pulls:
        uid, n_new = p["uid"], 0
        for rec in p["records"]:
            prev_uid = uid_of_id.setdefault(rec["id"], uid)
            if prev_uid != uid:
                raise CollectError(f"alert id {rec['id']} under two UIDs ({prev_uid}, {uid})")
            row = _row_from_record(rec, uid, p["fetched_at"], pull_id)
            key = (rec["id"], rec["updated_at"])
            if key in by_key:
                if _api_content(by_key[key]) != _api_content(row):
                    raise CollectError(f"id {rec['id']} updated_at {rec['updated_at']}: same key, different content")
                continue
            by_key[key] = row
            new.append(row)
            n_new += 1
        stats[uid] = {"n_records": len(p["records"]), "n_new_rows": n_new,
                      "n_open": sum(r["finished_at"] is None for r in p["records"])}
    new.sort(key=lambda r: (r["requested_uid"], r["id"], parse_ts(r["updated_at"])))
    return new, stats


def check_consistency(store_rows, log_rows, hole_rows=()):
    """Every pull_id in the CSV and in the holes file must be in the log (the log is renamed last, so a crash between
    the renames leaves it out)."""
    missing = sorted(({r["pull_id"] for r in store_rows} | {r["pull_id"] for r in hole_rows})
                     - {r["pull_id"] for r in log_rows})
    if missing:
        raise CollectError(f"incomplete previous run: pull_id(s) {missing} are in the datastore or the holes file but "
                           f"not in the pull log. Repair: restore BOTH files to their last committed state (git checkout "
                           f"-- datastore/alerts_in_ua.csv reports/collect/coverage_holes.csv; that run was never "
                           f"committed), then re-run.")


def check_holes_file_present(holes_path, log_rows):
    """A missing holes file is only valid before the first write (empty log); otherwise recorded holes would vanish."""
    if log_rows and not Path(holes_path).exists():
        raise CollectError(f"{holes_path} is missing but the pull log has rows: recorded coverage holes would be lost. "
                           f"Restore it (git checkout -- reports/collect/coverage_holes.csv)")


def check_store_matches_log(store_rows, log_rows, live):
    """The other direction: every log pull that added rows must have them in the store (catches a wrong or missing
    datastore path next to a real log). A live pull needs a seeded/collected history (non-empty log)."""
    have = {r["pull_id"] for r in store_rows}
    lost = sorted({r["pull_id"] for r in log_rows if int(r["n_new_rows"]) > 0} - have)
    if lost:
        raise CollectError(f"pull log lists pull(s) {lost} with new rows that are not in the datastore: wrong "
                           f"--datastore path or a lost file")
    if live and not log_rows:
        raise CollectError("empty pull log: seed the datastore first (scripts/collect_api.py --seed-from DUMP)")


def find_holes(log_rows, fetched_at_by_uid):
    """HOLE = new nominal window start later than the unit's LATEST previous fetched_at. Under D-039 (proposed; the
    human, 2026-10-17) a hole does not stop collection: it is returned as (uid, hole_from, hole_to), an OPEN
    interval, and recorded. A unit missing from a non-empty log still raises (coverage unknown)."""
    if not log_rows:
        return []
    prev = {}
    for r in log_rows:
        t = parse_ts(r["fetched_at"])
        prev[int(r["uid"])] = max(prev.get(int(r["uid"]), t), t)
    holes = []
    for uid, fetched_at in sorted(fetched_at_by_uid.items()):
        if uid not in prev:
            raise CollectError(f"uid {uid} has no previous pull in the log: coverage unknown")
        window_from = fetched_at - WINDOW
        if window_from > prev[uid]:
            holes.append((uid, prev[uid], window_from))
    return holes


def covered(log_rows, hole_rows, uid, t):
    """Raw EVENT coverage of unit `uid` at time t: inside some closed pull window [nominal_window_from, fetched_at]
    and not inside a recorded OPEN hole (hole_from, hole_to). Not a modelling-eligibility rule (plans/M6a.md §4.4)."""
    in_window = any(parse_ts(r["nominal_window_from"]) <= t <= parse_ts(r["fetched_at"])
                    for r in log_rows if int(r["uid"]) == uid)
    in_hole = any(parse_ts(h["hole_from"]) < t < parse_ts(h["hole_to"]) for h in hole_rows if int(h["uid"]) == uid)
    return in_window and not in_hole


def _log_row(pull_id, uid, fetched_at_s, st, n429, nother, git_commit):
    window_from = fmt_ts(parse_ts(fetched_at_s) - WINDOW)
    return [pull_id, str(uid), regions.unit_from_api_uid(uid), "200", fetched_at_s, window_from,
            str(st["n_records"]), str(st["n_new_rows"]), str(st["n_open"]), str(n429), str(nother), git_commit]


def _print_summary(pulls, stats, new_rows):
    from collections import Counter
    starts_all = []
    for p in pulls:
        uid, recs = p["uid"], p["records"]
        st = stats[uid]
        if not recs:
            print(f"[collect] uid {uid:>2} {regions.unit_from_api_uid(uid):<17} EMPTY (0 records)")
            continue
        starts = sorted(r["started_at"] for r in recs)
        fins = [r["finished_at"] for r in recs if r["finished_at"] is not None]
        starts_all += [starts[0], starts[-1]]
        print(f"[collect] uid {uid:>2} {regions.unit_from_api_uid(uid):<17} records {st['n_records']:>5}  "
              f"new {st['n_new_rows']:>5}  dup {st['n_records'] - st['n_new_rows']:>5}  open {st['n_open']:>3}  "
              f"started {starts[0]} -> {starts[-1]}  min finished {min(fins) if fins else '-'}")
    types = Counter((r["alert_type"], r["alert_level"]) for p in pulls for r in p["records"])
    print(f"[collect] types x levels (this pull): {dict(sorted(types.items()))}")
    if starts_all:
        print(f"[collect] pull started_at range {min(starts_all)} -> {max(starts_all)}; new rows {len(new_rows)}")


class PullResult:
    def __init__(self, new_rows, holes):
        self.new_rows, self.holes = new_rows, holes


def default_holes_path(log_path):
    return Path(log_path).with_name("coverage_holes.csv")


def apply_pulls(store_path, log_path, pulls, pull_id, git_commit, retries=None, holes_path=None):
    """Validated pulls -> find holes, merge, guard, write the CSV, the holes file and the log. -> PullResult."""
    holes_path = default_holes_path(log_path) if holes_path is None else Path(holes_path)
    old_store, store_cells = read_cells(store_path, COLUMNS)
    old_holes, hole_cells = read_cells(holes_path, HOLES_COLUMNS)
    old_log, log_cells = read_cells(log_path, LOG_COLUMNS)
    store_rows = [decode_row(r) for r in store_cells]
    hole_rows = [dict(zip(HOLES_COLUMNS, r)) for r in hole_cells]
    log_rows = [dict(zip(LOG_COLUMNS, r)) for r in log_cells]
    check_holes_file_present(holes_path, log_rows)
    check_consistency(store_rows, log_rows, hole_rows)
    check_store_matches_log(store_rows, log_rows, live=False)
    if pull_id in {r["pull_id"] for r in log_rows}:
        raise CollectError(f"pull_id {pull_id} is already in the log")
    holes = find_holes(log_rows, {p["uid"]: parse_ts(p["fetched_at"]) for p in pulls})
    new_rows, stats = merge(store_rows, pulls, pull_id)
    store_bytes = render_csv(COLUMNS, store_cells + [encode_row(r) for r in new_rows])
    retries = retries or {}
    log_bytes = render_csv(LOG_COLUMNS, log_cells + [
        _log_row(pull_id, p["uid"], p["fetched_at"], stats[p["uid"]], *retries.get(p["uid"], (0, 0)), git_commit)
        for p in pulls])
    holes_bytes = render_csv(HOLES_COLUMNS, hole_cells + [
        [pull_id, str(uid), regions.unit_from_api_uid(uid), fmt_ts(a), fmt_ts(b), git_commit] for uid, a, b in holes])
    check_append_only(old_store, store_bytes, Path(store_path).name)
    check_append_only(old_holes, holes_bytes, holes_path.name)
    check_append_only(old_log, log_bytes, Path(log_path).name)
    _print_summary(pulls, stats, new_rows)
    write_all(store_path, store_bytes, holes_path, holes_bytes, log_path, log_bytes)
    print(f"[collect] pull {pull_id}: {len(new_rows)} new rows -> {store_path} "
          f"({len(store_cells) + len(new_rows)} rows); log +{len(pulls)} rows")
    for uid, a, b in holes:
        print(f"[collect] COVERAGE HOLE recorded: uid {uid} ({regions.unit_from_api_uid(uid)}) "
              f"({fmt_ts(a)}, {fmt_ts(b)}) -> {holes_path}; collection continues (D-039 proposed)")
    return PullResult(new_rows, holes)


def collect(store_path, log_path, token, session, clock, git_commit, holes_path=None):
    """One live pull of the 24 units -> PullResult. Raises on any failure; then nothing is written. A coverage hole
    does not raise: it is recorded and reported in PullResult.holes (the CLI then exits 3)."""
    holes_path = default_holes_path(log_path) if holes_path is None else Path(holes_path)
    _, store_cells = read_cells(store_path, COLUMNS)
    _, hole_cells = read_cells(holes_path, HOLES_COLUMNS)
    _, log_cells = read_cells(log_path, LOG_COLUMNS)
    log_rows = [dict(zip(LOG_COLUMNS, r)) for r in log_cells]
    store_rows = [decode_row(r) for r in store_cells]
    check_holes_file_present(holes_path, log_rows)
    check_consistency(store_rows, log_rows, [dict(zip(HOLES_COLUMNS, r)) for r in hole_cells])
    check_store_matches_log(store_rows, log_rows, live=True)
    start = clock.now()
    pull_id = start.strftime("%Y-%m-%dT%H%MZ")
    if pull_id in {r["pull_id"] for r in log_rows}:                     # fail fast, before a ~48 min fetch
        raise CollectError(f"pull_id {pull_id} is already in the log")
    fetched = fetch_all(token, session, clock)
    pulls, retries = [], {}
    for f in fetched:
        records = validate_pull(f["uid"], f["payload"], f["fetched_at"])
        pulls.append({"uid": f["uid"], "records": records, "fetched_at": fmt_ts(f["fetched_at"])})
        retries[f["uid"]] = (f["n_retries_429"], f["n_retries_other"])
    check_national_window(pulls)
    return apply_pulls(store_path, log_path, pulls, pull_id, git_commit, retries, holes_path)


def seed_from_dump(dump_dir, store_path, log_path, git_commit, holes_path=None):
    """One-off seed from a saved dump (manifest.tsv + uid_<N>.json). No network. Only into an empty datastore."""
    dump_dir = Path(dump_dir).resolve()
    if not dump_dir.name:
        raise CollectError(f"seed: cannot derive a pull_id from the dump path {dump_dir}")
    if read_cells(store_path, COLUMNS)[1] or read_cells(log_path, LOG_COLUMNS)[1]:
        raise CollectError("seed refused: the datastore or the pull log already has rows")
    with open(dump_dir / "manifest.tsv") as fh:
        manifest = {int(r["uid"]): r for r in csv.DictReader(fh, delimiter="\t")}
    pulls = []
    for uid in unit_uids():
        m = manifest.get(uid)
        if m is None or int(m["http"]) != 200:
            raise CollectError(f"seed: uid {uid} missing or not HTTP 200 in the manifest")
        fetched_at = parse_ts(m["fetched_at_utc"], f"manifest uid {uid} fetched_at_utc")
        payload = json.loads((dump_dir / f"uid_{uid}.json").read_text())
        records = validate_pull(uid, payload, fetched_at)
        pulls.append({"uid": uid, "records": records, "fetched_at": fmt_ts(fetched_at)})
    check_national_window(pulls)
    return apply_pulls(store_path, log_path, pulls, f"seed-{dump_dir.name}", git_commit, holes_path=holes_path)


# ---------------- views for consumers (plans/M6a.md §4.2) ----------------

def _hide_future(row, t):
    """Truncation at t as in src.data.truncate_api_records: future start -> drop; end after t -> unknown."""
    if parse_ts(row["started_at"]) > t:
        return None
    if row["finished_at"] is not None and parse_ts(row["finished_at"]) > t:
        row = {**row, "finished_at": None}
    return row


def _latest_per_id(rows):
    best = {}
    for r in rows:
        u = parse_ts(r["updated_at"])
        if r["id"] not in best or u > best[r["id"]][0]:
            best[r["id"]] = (u, r)
    return [best[k][1] for k in sorted(best)]


def as_known_at(rows, t=None):
    """OBSERVED view: what this collector had seen at t. (1) fetched_at <= t, (2) latest updated_at per id (D-027),
    (3) end after t hidden, (4) start after t dropped. t=None -> D-027 full-history view (no truncation)."""
    if t is None:
        return _latest_per_id(rows)
    seen = [r for r in rows if parse_ts(r["fetched_at"]) <= t]
    return [r2 for r in _latest_per_id(seen) if (r2 := _hide_future(r, t)) is not None]


def as_reconstructed_at(rows, t):
    """EVENT-TIME RECONSTRUCTION: the D-027 full-history view truncated by event timestamps, the way the official
    dataset is used. Retrospective: it is NOT what was observed at t (later corrections are included)."""
    return [r2 for r in _latest_per_id(rows) if (r2 := _hide_future(r, t)) is not None]


def to_api_records(rows):
    """Decoded rows -> raw-API-shaped records with `_file_uid` = requested UID, as `src.data.api_alerts` takes them."""
    out = []
    for r in rows:
        rec = {c: r[c] for c in API_FIELDS}
        if "location_raion" in r:
            rec["location_raion"] = r["location_raion"]
        rec["_file_uid"] = r["requested_uid"]
        out.append(rec)
    return out
