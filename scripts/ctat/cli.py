"""scripts/ctat-refs — rebuild the CTAT/HOTTP reference dataset.

Usage:
  scripts/ctat-refs <command> [options] [--help]

Commands:
  download   fetch the five CTAT volume PDFs from the URLs in urls.csv
  extract    render the PDFs, crop the running heads and OCR them
  clean      turn the OCR page texts into one row per CTAT verse
  refs       combine the cleaned CTAT data and the HOTTP text into refs.csv
  all        download -> extract -> clean -> refs (a full rebuild)

Options:
  --pdfs DIR    where the volume PDFs are cached (default: output/ctat/pdfs)
  --in PATH     clean: the OCR results to read (default: the tracked snapshot)
  --out PATH    output file (defaults: cache for extract, the data folder otherwise)
  --volumes     extract: comma-separated volume numbers (e.g. 1,2)
  --pages       extract: 1-based page range, e.g. 148-152
  --help        show this help

Inputs live in data/manual_datasets/ctat/: urls.csv, header_coordinates.csv,
HOTTP-PENTATEUCH.txt, ocr_results.csv (OCR snapshot) and ocr_clean.csv.

The OCR stages need the optional `ctat` dependency group:
  .venv/bin/pip install -r requirements.txt
The `refs` command only needs pandas.
"""

import argparse
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ctat import pipeline, refs  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "manual_datasets" / "ctat"
CACHE_DIR = REPO_ROOT / "output" / "ctat"


def parse_pages(value: str) -> range:
    start, _, end = value.partition("-")
    return range(int(start), int(end or start) + 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ctat-refs", add_help=False,
                                     description="Rebuild the CTAT/HOTTP reference dataset")
    parser.add_argument("command", nargs="?",
                        choices=["download", "extract", "clean", "refs", "all"])
    parser.add_argument("--pdfs", type=Path, default=CACHE_DIR / "pdfs")
    parser.add_argument("--in", dest="source", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--volumes")
    parser.add_argument("--pages")
    parser.add_argument("--help", "-h", action="store_true")
    args = parser.parse_args(argv)

    if args.help:
        print(__doc__)
        return 0
    if not args.command:
        print(__doc__)
        return 1

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    full_rebuild = args.command == "all"
    cached_ocr = CACHE_DIR / "ocr_results.csv"

    if args.command in ("download", "all"):
        pipeline.download(DATA_DIR / "urls.csv", args.pdfs)

    if args.command in ("extract", "all"):
        pipeline.extract(
            args.pdfs,
            args.out or cached_ocr,
            volumes=args.volumes.split(",") if args.volumes else None,
            pages=parse_pages(args.pages) if args.pages else None,
        )

    if args.command in ("clean", "all"):
        source = args.source or (cached_ocr if full_rebuild else DATA_DIR / "ocr_results.csv")
        pipeline.clean(source, args.out or DATA_DIR / "ocr_clean.csv")

    if args.command in ("refs", "all"):
        refs.build(args.out or DATA_DIR / "refs.csv")

    return 0


if __name__ == "__main__":
    sys.exit(main())
