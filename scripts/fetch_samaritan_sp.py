#!/usr/bin/env python3
"""Add the Samaritan Pentateuch Hebrew text to the curated variant list.

Source
------
STEPBible SP version: https://www.stepbible.org/version.jsp?version=SP

The SP text is a SWORD module distributed by CrossWire
(https://www.crosswire.org/sword/). The module is titled
"Samaritan Pentateuch with Morphology, Transliteration, Strongs Concordance
Numbers and Idiomatic Translation" and was digitized and prepared by
Aleksandr Sigalov. Its base text is Kennicott's *Vetus Testamentum Hebraicum
cum variis lectionibus* (1780), manually compared with von Gall's *Der
Hebräische Pentateuch der Samaritaner* (1918).

Distribution licence (from the module configuration): "Copyrighted; Free
non-commercial distribution". This script is a research aid; do not use the
data commercially.

What it does
------------
1. Downloads the SP SWORD module (`SP.zip`) from CrossWire (or uses a cached
   copy with `--zip`).
2. Reads the tracked reference list (`data/manual_datasets/samaritan/samaritan.csv`)
   and writes the enriched copy to `data/derived/samaritan.csv` (git-ignored).
3. Adds/updates the `hebrew_text` column, so the reference list and its Hebrew
   text share one source of truth.

Usage
-----
    python3 scripts/fetch_samaritan_sp.py [--zip PATH] [--csv PATH]

Requires `pysword` and `requests` (see requirements.txt).
"""

from __future__ import annotations

import argparse
import csv
import io
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "data" / "derived" / "samaritan.csv"
TRACKED_CSV = REPO_ROOT / "data" / "manual_datasets" / "samaritan" / "samaritan.csv"
SP_URL = "https://www.crosswire.org/ftpmirror/pub/sword/packages/rawzip/SP.zip"

# The curated list uses full English book names; the SWORD module uses OSIS IDs.
BOOK_CODES = {
    "Genesis": "gen",
    "Exodus": "exod",
    "Leviticus": "lev",
    "Numbers": "num",
    "Deuteronomy": "deut",
}


def download_module(destination: Path) -> Path:
    """Download SP.zip and return the extracted module data directory."""
    import requests

    print(f"downloading {SP_URL}")
    response = requests.get(SP_URL, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(destination)

    module_dir = destination / "modules" / "texts" / "ztext" / "sp"
    if not module_dir.is_dir():
        raise SystemExit(f"SP module data directory not found: {module_dir}")
    return module_dir


def add_hebrew_text(csv_path: Path, module_dir: Path) -> int:
    try:
        from pysword.bible import SwordBible
    except ImportError as error:
        raise SystemExit(
            "pysword is required: pip install -r requirements.txt"
        ) from error

    bible = SwordBible(str(module_dir), versification="mt")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not {"book", "chapter", "verse"}.issubset(fieldnames):
        raise SystemExit(
            f"{csv_path} must have book, chapter and verse columns; found {fieldnames}"
        )
    if "hebrew_text" not in fieldnames:
        fieldnames.append("hebrew_text")

    missing: list[str] = []
    for row in rows:
        book = row["book"]
        chapter = int(row["chapter"])
        verse = int(row["verse"])
        code = BOOK_CODES.get(book)
        if code is None:
            missing.append(f"{book} {chapter}:{verse} (unknown book)")
            continue
        try:
            text = bible.get(
                books=[code], chapters=[chapter], verses=[verse], clean=True
            ).strip()
        except Exception as error:  # noqa: BLE001 - report and continue
            missing.append(f"{book} {chapter}:{verse} ({error})")
            continue
        if not text:
            missing.append(f"{book} {chapter}:{verse} (empty)")
            continue
        row["hebrew_text"] = text

    if missing:
        raise SystemExit(
            "could not read these verses from the SP module:\n  " + "\n  ".join(missing)
        )

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zip", type=Path, help="use a cached SP.zip instead of downloading")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV,
                        help="the curated variant list to update in place")
    args = parser.parse_args(argv)

    if not args.csv.exists():
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TRACKED_CSV, args.csv)

    with tempfile.TemporaryDirectory(prefix="sp-") as temporary:
        temp = Path(temporary)
        if args.zip:
            with zipfile.ZipFile(args.zip) as archive:
                archive.extractall(temp)
            module_dir = temp / "modules" / "texts" / "ztext" / "sp"
        else:
            module_dir = download_module(temp)

        count = add_hebrew_text(args.csv, module_dir)

    print(f"updated {count} verses in {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
