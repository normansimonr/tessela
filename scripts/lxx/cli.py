"""scripts/lxx-refs — build the Septuagint variant corpus from Tov's CATSS data.

Usage:
  scripts/lxx-refs <command> [options] [--help]

Commands:
  build      convert the raw .par files, align the versions and write
             data/derived/septuagint/tov_flagged.csv
  normalise  reuse the committed normalisations and (optionally) normalise the
             missing verses with Gemini; writes normalisation/{jps,lxx}.csv
  missing    write the list of verses still to normalise
             (normalisation/missing.csv)
  check      validate the generated dataset (canon, references, counts)
  all        build + check

Options:
  --out PATH        build/check: the dataset file
  --normalise DIR   normalise/missing: the normalisation folder
  --provider NAME   normalise: 'none' (default) or 'gemini'
  --only NAME       normalise: 'jps', 'lxx' or 'both' (default)
  --limit N         normalise: stop after N missing verses (a trial run)
  --help            show this help

The raw data lives in data/raw/: the 42 CATSS .par files (in LXX_Tov/) and the two
ebible translations (Brenton and JPS, in their per-version folders). Nothing is downloaded
and Gemini is never called unless --provider gemini is given.
"""

import argparse
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lxx import align, tov  # noqa: E402
from lxx.dataset import build_dataset, check_dataset, write_dataset  # noqa: E402
from lxx.normalise import normalise, write_missing  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "derived" / "septuagint"
RAW = REPO_ROOT / "data" / "raw"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lxx-refs", add_help=False,
                                     description="Build the Septuagint variant corpus")
    parser.add_argument("command", nargs="?",
                        choices=["build", "normalise", "missing", "check", "all"])
    parser.add_argument("--out", type=Path, default=DATA_DIR / "tov_flagged.csv")
    parser.add_argument("--normalise", type=Path, default=DATA_DIR / "normalisation")
    parser.add_argument("--provider", default="none", choices=["none", "gemini"])
    parser.add_argument("--only", default="both", choices=["jps", "lxx", "both"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--help", "-h", action="store_true")
    args = parser.parse_args(argv)

    if args.help:
        print(__doc__)
        return 0
    if not args.command:
        print(__doc__)
        return 1

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.command in ("build", "all"):
        rows = build_dataset(RAW, tov, align)
        write_dataset(rows, args.out)
        logging.info("wrote %d rows to %s", len(rows), args.out)

    if args.command == "normalise":
        normalise(args.out, args.normalise, provider=args.provider,
                  only=args.only, limit=args.limit)

    if args.command == "missing":
        write_missing(args.out, args.normalise)

    if args.command in ("check", "all"):
        problems = check_dataset(args.out)
        if problems:
            for problem in problems:
                logging.error(problem)
            return 1
        logging.info("dataset checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
