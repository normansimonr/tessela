#!/usr/bin/env python3
"""Add Dead Sea Scrolls Hebrew readings to the curated Qumran variant list.

Source
------
ETCBC/dss: https://github.com/ETCBC/dss

The CACCHT Dead Sea Scrolls dataset, in Text-Fabric format (version 2.0.5).
Transcriptions are based on Martin Abegg's data; the dataset was prepared by
Jarod Jacobs, Martijn Naaijer and Dirk Roorda. It is licensed under
Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).

The dataset is not vendored in this repository (it is large). Clone it first:

    git clone --depth 1 https://github.com/ETCBC/dss.git /path/to/ETCBC-dss

What it does
------------
1. Loads the `tf/2.0.5` Text-Fabric dataset from the local clone.
2. Reads the tracked reference list (`data/manual_datasets/qumran/qumran.csv`).
3. For each passage, finds the biblical verse in the DSS dataset and writes
   the enriched copy to `data/derived/qumran.csv` (git-ignored), with one row
   per (passage, scroll) reading and:
   - `scroll`: the manuscript (e.g. `4Q9`);
   - `hebrew_text`: the clean consonantal text;
   - `transcription`: the full ETCBC transcription, which preserves editorial
     markers (brackets for reconstruction, `(^ ... ^)` for uncertainty, `#`
     for damaged text, and `׳` for morpheme boundaries).

A passage attested in several scrolls therefore has several rows. A passage
that is not present in the dataset keeps one row with empty `scroll` and text,
so missing evidence remains explicit.

Usage
-----
    python3 scripts/fetch_qumran_dss.py --dss-dir /path/to/ETCBC-dss

Requires `text-fabric` (see requirements.txt).
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "data" / "derived" / "qumran.csv"
TRACKED_CSV = REPO_ROOT / "data" / "manual_datasets" / "qumran" / "qumran.csv"
DEFAULT_VERSION = "2.0.5"

# The curated list uses full English book names; the Text-Fabric dataset uses
# its own book codes.
BOOK_MAP = {
    "Genesis": "Gen",
    "Exodus": "Ex",
    "Leviticus": "Lev",
    "Numbers": "Num",
    "Deuteronomy": "Deut",
    "Joshua": "Josh",
    "Judges": "Judg",
    "1 Samuel": "1Sam",
    "2 Samuel": "2Sam",
    "1 Kings": "1Kgs",
    "2 Kings": "2Kgs",
    "1 Chronicles": "1Chr",
    "2 Chronicles": "2Chr",
    "Isaiah": "Is",
    "Jeremiah": "Jer",
    "Ezekiel": "Ezek",
    "Hosea": "Hos",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obadiah": "Obad",
    "Jonah": "Jonah",
    "Micah": "Mic",
    "Nahum": "Nah",
    "Habakkuk": "Hab",
    "Zephaniah": "Zeph",
    "Haggai": "Hag",
    "Zechariah": "Zech",
    "Malachi": "Mal",
    "Psalms": "Ps",
    "Proverbs": "Prov",
    "Job": "Job",
    "Song of Songs": "Song",
    "Ruth": "Ruth",
    "Lamentations": "Lam",
    "Ecclesiastes": "Eccl",
    "Esther": "Esth",
    "Daniel": "Dan",
    "Ezra": "Ezra",
    "Nehemiah": "Neh",
}


def natural_key(value: str) -> tuple:
    """Sort `1Q1`, `4Q9`, `11Q1` in a human-friendly order."""
    return tuple(
        int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)
    )


def clean_text(text: str) -> str:
    """Remove the morpheme separator and collapse whitespace."""
    return re.sub(r"\s+", " ", text.replace("׳", "")).strip()


def load_dataset(dss_dir: Path, version: str):
    try:
        from tf.app import use
    except ImportError as error:
        raise SystemExit(
            "text-fabric is required: pip install -r requirements.txt"
        ) from error

    location = dss_dir / "tf" / version
    if not location.is_dir():
        raise SystemExit(f"Text-Fabric dataset not found: {location}")

    app = use(f"data:{location}", silent="deep")
    return app.api.F, app.api.L


def collect_groups(F, L) -> dict[tuple[str, str, str, str], list[int]]:
    """Group word nodes by (book, chapter, verse, scroll)."""
    groups: dict[tuple[str, str, str, str], list[int]] = defaultdict(list)
    for word in F.otype.s("word"):
        book = F.book.v(word)
        if not book:
            continue
        chapter = F.chapter.v(word)
        verse = F.verse.v(word)
        if chapter is None or verse is None:
            continue
        scrolls = L.u(word, "scroll")
        if not scrolls:
            continue
        scroll = F.scroll.v(scrolls[0])
        groups[(book, str(chapter), str(verse), scroll)].append(word)
    return groups


def passages(F, L, groups, book: str, chapter: int, verse: int):
    code = BOOK_MAP.get(book)
    if code is None:
        return []
    found = []
    for (group_book, group_chapter, group_verse, scroll), words in groups.items():
        if (group_book, group_chapter, group_verse) != (code, str(chapter), str(verse)):
            continue
        ordered = sorted(words)
        clean = " ".join(
            clean_text(F.glyph.v(word))
            for word in ordered
            if F.glyph.v(word)
        )
        transcription = " ".join(
            re.sub(r"\s+", " ", F.full.v(word)).strip()
            for word in ordered
            if F.full.v(word)
        )
        found.append((scroll, clean, transcription))
    return sorted(found, key=lambda item: natural_key(item[0]))


def update_csv(csv_path: Path, groups, F, L) -> tuple[int, int, list[str]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not {"book", "chapter", "verse"}.issubset(fieldnames):
        raise SystemExit(
            f"{csv_path} must have book, chapter and verse columns; found {fieldnames}"
        )

    reading_fields = ["scroll", "hebrew_text", "transcription"]
    for column in reading_fields:
        if column not in fieldnames:
            fieldnames.append(column)

    # Collapse any existing reading rows back to one base row per passage, so
    # re-running the script is idempotent.
    passages_order: list[tuple[str, int, int]] = []
    base_rows: dict[tuple[str, int, int], dict[str, str]] = {}
    for row in rows:
        key = (row["book"], int(row["chapter"]), int(row["verse"]))
        if key not in base_rows:
            passages_order.append(key)
            base_rows[key] = {
                name: row.get(name, "")
                for name in fieldnames
                if name not in reading_fields
            }

    output: list[dict[str, str]] = []
    missing: list[str] = []
    readings = 0
    for book, chapter, verse in passages_order:
        found = passages(F, L, groups, book, chapter, verse)
        if not found:
            missing.append(f"{book} {chapter}:{verse}")
            base = dict(base_rows[(book, chapter, verse)])
            base["scroll"] = ""
            base["hebrew_text"] = ""
            base["transcription"] = ""
            output.append(base)
            continue
        for scroll, clean, transcription in found:
            base = dict(base_rows[(book, chapter, verse)])
            base["scroll"] = scroll
            base["hebrew_text"] = clean
            base["transcription"] = transcription
            output.append(base)
        readings += len(found)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    return len(output), readings, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dss-dir", type=Path, required=True,
                        help="local clone of https://github.com/ETCBC/dss")
    parser.add_argument("--version", default=DEFAULT_VERSION,
                        help=f"Text-Fabric dataset version (default: {DEFAULT_VERSION})")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV,
                        help="the curated variant list to update in place")
    args = parser.parse_args(argv)

    if not args.csv.exists():
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TRACKED_CSV, args.csv)

    F, L = load_dataset(args.dss_dir, args.version)
    groups = collect_groups(F, L)
    count, readings, missing = update_csv(args.csv, groups, F, L)

    print(f"wrote {count} rows ({readings} readings) to {args.csv}")
    if missing:
        print("passages not found in the dataset (left empty):")
        for item in missing:
            print(f"  {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
