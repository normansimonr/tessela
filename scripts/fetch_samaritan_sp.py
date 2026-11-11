#!/usr/bin/env python3
"""Fetch the Samaritan Pentateuch Hebrew text for the curated variant verses.

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
2. Reads `data/manual_datasets/samaritan/samaritan.csv` (the curated list of
   variant verses).
3. Writes `data/manual_datasets/samaritan/samaritan_hebrew.csv` with:
   `book`, `chapter`, `verse`, `hebrew_text` (clean, unpointed Hebrew) and
   `osis` (the raw OSIS markup: Strong's numbers, glosses, transliteration).

Usage
-----
    python3 scripts/fetch_samaritan_sp.py [--zip PATH] [--out PATH]

Requires `pysword` and `requests` (see requirements.txt).
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSES = REPO_ROOT / "data" / "manual_datasets" / "samaritan" / "samaritan.csv"
DEFAULT_OUT = REPO_ROOT / "data" / "manual_datasets" / "samaritan" / "samaritan_hebrew.csv"
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
    payload = response.content

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        archive.extractall(destination)

    module_dir = destination / "modules" / "texts" / "ztext" / "sp"
    if not module_dir.is_dir():
        raise SystemExit(f"SP module data directory not found: {module_dir}")
    return module_dir


def extract_verses(verses_path: Path, module_dir: Path) -> list[dict[str, str]]:
    try:
        from pysword.bible import SwordBible
    except ImportError as error:
        raise SystemExit(
            "pysword is required: pip install -r requirements.txt"
        ) from error

    bible = SwordBible(str(module_dir), versification="mt")

    rows = list(csv.DictReader(verses_path.open(newline="", encoding="utf-8")))
    if not rows:
        raise SystemExit(f"no verses found in {verses_path}")

    result: list[dict[str, str]] = []
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
            osis = bible.get(
                books=[code], chapters=[chapter], verses=[verse], clean=False
            ).strip()
        except Exception as error:  # noqa: BLE001 - report and continue
            missing.append(f"{book} {chapter}:{verse} ({error})")
            continue
        if not text:
            missing.append(f"{book} {chapter}:{verse} (empty)")
            continue
        result.append(
            {
                "book": book,
                "chapter": str(chapter),
                "verse": str(verse),
                "hebrew_text": text,
                "osis": osis,
            }
        )

    if missing:
        raise SystemExit(
            "could not read these verses from the SP module:\n  " + "\n  ".join(missing)
        )
    return result


def write_csv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["book", "chapter", "verse", "hebrew_text", "osis"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zip", type=Path, help="use a cached SP.zip instead of downloading")
    parser.add_argument("--verses", type=Path, default=DEFAULT_VERSES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="sp-") as temporary:
        temp = Path(temporary)
        if args.zip:
            with zipfile.ZipFile(args.zip) as archive:
                archive.extractall(temp)
            module_dir = temp / "modules" / "texts" / "ztext" / "sp"
        else:
            module_dir = download_module(temp)

        rows = extract_verses(args.verses, module_dir)
        write_csv(rows, args.out)

    print(f"wrote {len(rows)} verses to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
