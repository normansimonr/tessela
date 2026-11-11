#!/usr/bin/env python3
"""Consolidate the Qere/Ketiv word datasets to one row per verse.

Usage:
  scripts/qere_ketiv/verse_consolidator.py [--in-dir PATH] [--out-dir PATH] [--help]

Inputs (in --in-dir, default data/manual_datasets/qere_ketiv):
  same_lexicon_entry_different_parsing.csv — stage 2
  different_lexicon_entry.csv — stage 2

Output (in --out-dir, default data/manual_datasets/qere_ketiv):
  qere_ketiv_verses.csv with the columns book, chapter, verse, type and the
  readings themselves, where type records which kinds of variant the verse
  contains:
    K  — a different lexeme (meaning)
    k  — the same lexeme with a different parsing (grammar)
    kK — both in the same verse
  `Variant Type` says the same in words: 'different word', 'different grammar'
  or 'different word and different grammar'.

A word-by-word list is right for study, but the translation works verse by
verse, so this stage collapses the two datasets to the verse level. A verse
with more than one variant keeps every reading, joined with ' | ' in the
original word order (the values within a reading are de-duplicated), and is
flagged when any of its variants is a proper name.

This is stage 3 of 3; run scripts/qere-ketiv to run the whole pipeline.
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = REPO_ROOT / "data" / "manual_datasets" / "qere_ketiv"

KEY = ["book", "chapter", "verse"]
DETAIL_COLUMNS = [
    "Qere", "Qere Translit", "Qere Gloss", "Qere Root",
    "Qere Strongs", "Qere Parsing",
    "Ketiv", "Ketiv Translit", "Ketiv Gloss", "Ketiv Root",
    "Ketiv Strongs", "Ketiv Parsing",
]
OUTPUT_COLUMNS = KEY + ["type", "Variant Type"] + DETAIL_COLUMNS + ["Proper Name"]

# Plain-language name for each combination of letters in `type`.
VARIANT_TYPES = {
    "K": "different word",
    "k": "different grammar",
    "kK": "different word and different grammar",
}


def join_readings(values: pd.Series) -> str:
    """Join the readings of a verse with ' | ', dropping exact repeats."""
    readings: list[str] = []
    for value in values:
        if pd.isna(value) or value == "":
            continue
        if value not in readings:
            readings.append(str(value))
    return " | ".join(readings)


def consolidate(in_dir: Path, out_dir: Path) -> pd.DataFrame:
    """Merge both word datasets and collapse them to one row per verse."""
    same_entry = pd.read_csv(in_dir / "same_lexicon_entry_different_parsing.csv")
    same_entry["type"] = "k"

    different_entry = pd.read_csv(in_dir / "different_lexicon_entry.csv")
    different_entry["type"] = "K"

    df = pd.concat([same_entry, different_entry])

    # One letter per kind of variant, in the k then K order.
    types = (df.drop_duplicates(subset=KEY + ["type"])
               .groupby(KEY, sort=True)["type"]
               .apply(lambda letters: "".join(letters))
               .reset_index())

    readings = (df.groupby(KEY, sort=True)[DETAIL_COLUMNS]
                  .agg(join_readings)
                  .reset_index())

    proper_names = (df.groupby(KEY, sort=True)["Proper Name"]
                      .apply(lambda values: "yes" if (values == "yes").any() else "no")
                      .reset_index())

    verses = (types.merge(readings, on=KEY)
                   .merge(proper_names, on=KEY))
    verses["Variant Type"] = verses["type"].map(VARIANT_TYPES)
    verses = verses[OUTPUT_COLUMNS]

    out_dir.mkdir(parents=True, exist_ok=True)
    verses.to_csv(out_dir / "qere_ketiv_verses.csv", index=False)

    logging.info("verses with a Qere/Ketiv variant: %d", len(verses))
    for kind, count in verses["type"].value_counts().sort_index().items():
        logging.info("  type %s: %d", kind, count)
    return verses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Consolidate the Qere/Ketiv word datasets to one row per verse"
    )
    parser.add_argument("--in-dir", type=Path, default=DEFAULT_DIR,
                        help="directory holding the stage 2 datasets")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_DIR,
                        help="directory for qere_ketiv_verses.csv")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    for name in ("same_lexicon_entry_different_parsing.csv",
                 "different_lexicon_entry.csv"):
        if not (args.in_dir / name).is_file():
            logging.error("input not found: %s", args.in_dir / name)
            return 1

    consolidate(args.in_dir, args.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
