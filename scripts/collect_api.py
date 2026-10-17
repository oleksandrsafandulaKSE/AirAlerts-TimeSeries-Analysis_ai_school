"""M6a collector CLI (plans/M6a.md).

    python scripts/collect_api.py                                   # one live pull of the 24 units (~48 min)
    python scripts/collect_api.py --seed-from data/raw/alerts_in_ua/2026-10-12T1645Z   # one-off seed, no network
    python scripts/collect_api.py --dry-run                         # live pull into a scratch copy, repo untouched

Token: env ALERTS_IN_UA_TOKEN, else the line `ALERTS_IN_UA_TOKEN=...` of --env-file (default: <repo>/.env).
The token is never printed. Any failed check raises: nothing is written.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import requests  # noqa: E402

from collect import api_collector as C  # noqa: E402

TOKEN_VAR = "ALERTS_IN_UA_TOKEN"


def read_token(env_file):
    token = os.environ.get(TOKEN_VAR, "")
    if token:
        return token
    env_file = Path(env_file)
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[len("export "):]
            key, sep, value = line.partition("=")
            if sep and key.strip() == TOKEN_VAR:
                value = value.strip()
                if value[:1] in ("'", '"'):                       # quoted: take what is inside the quotes
                    value = value[1:].split(value[0], 1)[0]
                else:                                             # unquoted: drop an inline ' # comment'
                    value = value.split(" #", 1)[0].strip()
                return value
    raise C.CollectError(f"{TOKEN_VAR} not set in the environment and not found in {env_file}")


def git_head():
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datastore", default=str(ROOT / "datastore"), help="directory holding alerts_in_ua.csv")
    ap.add_argument("--log", default=str(ROOT / "reports" / "collect" / "pull_log.csv"))
    ap.add_argument("--seed-from", help="saved dump directory (manifest.tsv + uid_<N>.json)")
    ap.add_argument("--dry-run", action="store_true", help="live pull into a scratch copy; write nothing in the repo")
    ap.add_argument("--env-file", default=str(ROOT / ".env"))
    args = ap.parse_args(argv)

    store = Path(args.datastore) / "alerts_in_ua.csv"
    log = Path(args.log)
    commit = git_head()
    if args.seed_from:
        if args.dry_run:
            raise C.CollectError("--seed-from and --dry-run cannot be combined")
        C.seed_from_dump(args.seed_from, store, log, commit)
        return
    token = read_token(args.env_file)
    with requests.Session() as session:
        if args.dry_run:
            with tempfile.TemporaryDirectory() as tmp:
                s2, l2 = Path(tmp) / "alerts_in_ua.csv", Path(tmp) / "pull_log.csv"
                for src, dst in ((store, s2), (log, l2)):
                    if src.exists():
                        shutil.copy2(src, dst)
                C.collect(s2, l2, token, session, C.SystemClock(), commit)
                print("[collect] DRY RUN: nothing written in the repo")
        else:
            C.collect(store, log, token, session, C.SystemClock(), commit)


if __name__ == "__main__":
    main()
