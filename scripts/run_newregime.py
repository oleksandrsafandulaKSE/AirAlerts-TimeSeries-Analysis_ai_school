"""M6c-1: new-regime typed onset models (any / yellow / red) on alerts.in.ua history (plans/M6c-1.md). EXPLORATORY.

  python scripts/run_newregime.py --stage fit     # 6 models + baselines + validation; pre-registration; no test label
  python scripts/run_newregime.py --stage test    # the test week, scored ONCE (split-keyed reservation)
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from newregime import pipeline  # noqa: E402

SPLITS = {"first": pipeline.first_split}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["fit", "test"], required=True)
    ap.add_argument("--split", choices=sorted(SPLITS), default="first")
    ap.add_argument("--out", type=Path, default=pipeline.OUT)
    args = ap.parse_args(argv)
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError("Python 3.13 required (requirements.txt)")
    split = SPLITS[args.split]()
    if args.stage == "fit":
        pipeline.fit(split, args.out)
    else:
        pipeline.score_test(split, args.out)


if __name__ == "__main__":
    main()
