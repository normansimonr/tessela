#!/usr/bin/env python3
"""Analyse the STEPBible TAHOT Qere/Ketiv extraction.

Usage:
  scripts/qere_ketiv/qk_analyzer.py [--input PATH] [--lemmas PATH] [--out-dir PATH] [--help]

Inputs:
  OT-QK.tsv — the 17-column, tab-separated TAHOT lines selected by
  qk_extractor.sh (stage 1).
  lemmas.tsv — Strong's tag to pointed lemma, built by stage 1 from TAHOT's
  expanded tags. It supplies the root of each reading. Without it the roots
  are left empty (a warning is logged).

Outputs (in --out-dir, default data/manual_datasets/qere_ketiv):
  different_lexicon_entry.csv — words whose Qere and Ketiv are different
    lexemes: the variants that can change the translation.
  same_lexicon_entry_different_parsing.csv — same lexeme, different
    morphology: a grammatical choice, not a different word.
  stats.csv — the counts behind both files.

Each dataset gives, for both readings, the pointed Hebrew, the
transliteration, the gloss, the lemma (root), the Strong's tags and the
morphology in words; the ketiv's raw TAHOT note is kept as provenance.
Proper names are kept and flagged in the `Proper Name` column.

The five TAHOT columns read (0-based): 0 reference, 1 Hebrew (Qere),
2 transliteration, 3 translation (gloss), 11 expanded tags (qere lemma),
6 Meaning Variants (the Ketiv note), 4 dStrongs (Qere), 5 Grammar (Qere).

The Meaning Variants cell holds the full Ketiv note, e.g.

  K= 'o.ho.Lo/h (אָהֳלֹ/ה\\׃) "tent/ his" (H0168G/H9023\\H9016=HNcbsc/Sp3ms)

from which the transliteration, Hebrew, gloss and tags are parsed. Strong
tags are normalised before comparison: braces, brackets, slashes and
backslashes are removed, and the syntactic waw (H9001, H9002) and he (H9009)
are stripped so that only the lexical core is compared. The same waw is
removed from the grammar; the he is left there, because it cannot be removed
safely.

Proper names (the grammar's `Np`) are kept, not dropped: a name spelled one
way in the ketiv and another in the qere (Izhar/Zohar, for example) is a real
translation decision. They are flagged in the `Proper Name` column so that
they can be reviewed on their own; the proper-name standard is Milestone 10.

This is stage 2 of 3; run scripts/qere-ketiv to run the whole pipeline.
"""

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import morphology
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = REPO_ROOT / "data" / "manual_datasets" / "qere_ketiv"
DEFAULT_INPUT = DEFAULT_DIR / "OT-QK.tsv"
DEFAULT_LEMMAS = DEFAULT_DIR / "lemmas.tsv"

# TAHOT columns to keep (0-based) and the names they take here.
KEPT_COLUMNS = [0, 1, 2, 3, 11, 6, 4, 5]
COLUMN_NAMES = [
    "Coordinates",
    "Qere",
    "Qere Translit",
    "Qere Gloss",
    "Expanded Tags",
    "Ketiv Note",
    "Strongs Q",
    "Parsing Q",
]

OUTPUT_COLUMNS = [
    "book", "chapter", "verse", "word_index",
    "Qere", "Qere Translit", "Qere Gloss", "Qere Root",
    "Qere Strongs", "Qere Parsing",
    "Ketiv", "Ketiv Translit", "Ketiv Gloss", "Ketiv Root",
    "Ketiv Strongs", "Ketiv Parsing",
    "Proper Name", "Ketiv Note",
]

# K= transliteration (Hebrew) "gloss" (dStrongs=grammar)
KETIV_NOTE = re.compile(
    r'^K= (?P<translit>.+?) \((?P<hebrew>[^()]*)\) "(?P<gloss>.*)" \((?P<tags>[^()]*)\)$'
)

# H9xxx are syntactic tags (waw, he, prepositions), not lexical entries.
SYNTACTIC_TAG = re.compile(r"H9\d{3}")
STRONG_TAG = re.compile(r"^H0*(\d+)([A-Z]?)$")
TAG_SEPARATOR = re.compile(r"[\s/\\{}()+]+")


@dataclass(frozen=True)
class Classes:
    """The three word classes of interest, plus the discarded proper nouns."""
    proper_nouns: int
    same_same_parsing: pd.DataFrame
    same_different_parsing: pd.DataFrame
    different_lexicon_entry: pd.DataFrame


def load_qk(path: Path) -> pd.DataFrame:
    """Read the extracted TAHOT lines and keep the columns of interest."""
    raw = pd.read_csv(path, sep="\t", header=None)
    qk = raw.iloc[:, KEPT_COLUMNS].copy()
    qk.columns = COLUMN_NAMES
    return qk


def parse_coordinates(qk: pd.DataFrame) -> pd.DataFrame:
    """Turn 'Gen.9.21#07=Q(K)' into book, chapter, verse and word index."""
    reference = qk["Coordinates"].str.replace("=Q(K)", "", regex=False)
    book_and_verse = reference.str.split("#").str[0]
    book_and_verse = book_and_verse.str.replace(r"\([^)]*\)", "", regex=True)

    qk["book"] = book_and_verse.str.split(".", regex=False).str[0]
    qk["chapter"] = book_and_verse.str.split(".", regex=False).str[1].astype(int)
    qk["verse"] = book_and_verse.str.split(".", regex=False).str[2]
    qk["word_index"] = reference.str.split("#").str[1].astype(int)
    return qk.drop(columns=["Coordinates", "Expanded Tags"])


def split_ketiv(qk: pd.DataFrame) -> pd.DataFrame:
    """Parse the Ketiv transliteration, Hebrew, gloss and tags from its note.

    A note occasionally carries more than one reading, separated by ' ¦ '
    (e.g. 'B= ... ¦ K= ...'); the last segment is the K reading this pipeline
    works with.
    """
    note = qk["Ketiv Note"].str.split(" ¦ ", regex=False).str[-1]
    match = note.str.extract(KETIV_NOTE)

    missing = match["hebrew"].isna()
    if missing.any():
        raise ValueError(
            "unparsable Ketiv note(s) at row(s): "
            + ", ".join(str(i) for i in match.index[missing][:10])
        )

    qk["Ketiv"] = match["hebrew"]
    qk["Ketiv Translit"] = match["translit"]
    qk["Ketiv Gloss"] = match["gloss"]
    qk["Strongs K"] = match["tags"].str.split("=", regex=False).str[0]
    qk["Parsing K"] = match["tags"].str.split("=", regex=False).str[1]
    return qk


def clean_strongs_q(series: pd.Series) -> pd.Series:
    return (series.str.replace("{", "", regex=False)
                  .str.replace("}", "", regex=False)
                  .str.replace("/", " ", regex=False)
                  .str.replace("\\", " ", regex=False))


def clean_strongs_k(series: pd.Series) -> pd.Series:
    return (series.str.replace("(", "", regex=False)
                  .str.replace("/", " ", regex=False)
                  .str.replace("\\", " ", regex=False))


def clean_parsing_q(series: pd.Series) -> pd.Series:
    return (series.str.replace("{", "", regex=False)
                  .str.replace("}", "", regex=False)
                  .str.replace("/", " ", regex=False)
                  .str.replace("\\", " ", regex=False))


def clean_parsing_k(series: pd.Series) -> pd.Series:
    return (series.str.replace(")", "", regex=False)
                  .str.replace("/", " ", regex=False)
                  .str.replace("\\", " ", regex=False))


def normalise(qk: pd.DataFrame) -> pd.DataFrame:
    """Strip the syntax tags so that Qere and Ketiv can be compared."""
    qk["Strongs K"] = clean_strongs_k(qk["Strongs K"])
    qk["Parsing K"] = clean_parsing_k(qk["Parsing K"])
    qk["Strongs Q"] = clean_strongs_q(qk["Strongs Q"])
    qk["Parsing Q"] = clean_parsing_q(qk["Parsing Q"])

    # Remember the syntactic waw (H9001, H9002) and he (H9009), which mark
    # conjunction and the definite article rather than a lexical difference.
    for column in ("Strongs K", "Strongs Q"):
        qk[column] = (qk[column].str.replace("H9001", "", regex=False)
                                .str.replace("H9002", "", regex=False)
                                .str.strip())
    for column in ("Parsing K", "Parsing Q"):
        qk[column] = (qk[column].str.replace("Hc", "", regex=False)
                                .str.replace("HC", "", regex=False)
                                .str.strip())
    for column in ("Strongs K", "Strongs Q"):
        qk[column] = qk[column].str.replace("H9009", "", regex=False).str.strip()
    return qk


def load_lemmas(path: Path | None) -> dict[str, str]:
    """Read the Strong's tag to lemma index built by stage 1."""
    if path is None or not path.is_file():
        logging.warning("lemma index not found (%s): roots will be empty", path)
        return {}

    lemmas: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            tag, _, lemma = line.rstrip("\n").partition("\t")
            if tag:
                lemmas.setdefault(tag, lemma)
    logging.info("loaded %d lemmas from %s", len(lemmas), path)
    return lemmas


def _lookup_root(tag: str, lemmas: dict[str, str]) -> str | None:
    """Find a tag's lemma, tolerating missing or differing letter suffixes."""
    if tag in lemmas:
        return lemmas[tag]

    match = STRONG_TAG.match(tag)
    if not match:
        return None
    number = f"H{int(match.group(1)):04d}"

    if match.group(2):
        candidates = [number + match.group(2), number]
    else:
        candidates = [number] + [
            number + letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ]
    for candidate in candidates:
        if candidate in lemmas:
            return lemmas[candidate]
    return None


def resolve_root(strongs: str, lemmas: dict[str, str]) -> str:
    """Return the pointed lemma(s) of a space-separated dStrongs cell."""
    if not isinstance(strongs, str):
        return ""

    roots: list[str] = []
    for tag in TAG_SEPARATOR.split(strongs or ""):
        if not tag or SYNTACTIC_TAG.fullmatch(tag):
            continue
        root = _lookup_root(tag, lemmas)
        if root and root not in roots:
            roots.append(root)
    return " ".join(roots)


def add_roots(qk: pd.DataFrame, lemmas: dict[str, str]) -> pd.DataFrame:
    """Add the Qere and Ketiv root columns from the lemma index."""
    qk["Qere Root"] = qk["Strongs Q"].apply(lambda value: resolve_root(value, lemmas))
    qk["Ketiv Root"] = qk["Strongs K"].apply(lambda value: resolve_root(value, lemmas))

    unresolved = int((qk["Ketiv Root"] == "").sum() + (qk["Qere Root"] == "").sum())
    if unresolved:
        logging.info("roots left empty for %d reading(s): no lemma in TAHOT", unresolved)
    return qk


def is_proper_name(parsing: str) -> bool:
    """True when the grammar marks the word as a proper name (Np)."""
    if not isinstance(parsing, str):
        return False
    for segment in re.split(r"[\\/\s]+", parsing or ""):
        if len(segment) > 1 and segment[0] in "HA" and segment[1] in "NVAPRTCDS":
            segment = segment[1:]
        if segment.startswith("Np"):
            return True
    return False


def add_reading_columns(qk: pd.DataFrame) -> pd.DataFrame:
    """Turn the morphology codes into words and flag proper names."""
    qk["Qere Parsing"] = qk["Parsing Q"].apply(morphology.describe)
    qk["Ketiv Parsing"] = qk["Parsing K"].apply(morphology.describe)
    qk["Proper Name"] = qk["Parsing Q"].apply(
        lambda code: "yes" if is_proper_name(code) else "no"
    )
    qk = qk.rename(columns={"Strongs Q": "Qere Strongs", "Strongs K": "Ketiv Strongs"})
    return qk


def classify(qk: pd.DataFrame) -> Classes:
    """Split the words into the classes that matter here."""
    different_lexicon_entry = qk[
        qk["Qere Strongs"] != qk["Ketiv Strongs"]
    ]
    same_lexicon_entry = qk[
        qk["Qere Strongs"] == qk["Ketiv Strongs"]
    ]
    same_lexicon_entry_different_parsing = same_lexicon_entry[
        same_lexicon_entry["Qere Parsing"] != same_lexicon_entry["Ketiv Parsing"]
    ]
    same_lexicon_entry_same_parsing = same_lexicon_entry[
        same_lexicon_entry["Qere Parsing"] == same_lexicon_entry["Ketiv Parsing"]
    ]
    return Classes(
        proper_nouns=int((qk["Proper Name"] == "yes").sum()),
        same_same_parsing=same_lexicon_entry_same_parsing,
        same_different_parsing=same_lexicon_entry_different_parsing,
        different_lexicon_entry=different_lexicon_entry,
    )


def analyse(
    input_path: Path,
    out_dir: Path,
    lemmas_path: Path | None = None,
) -> pd.DataFrame:
    """Run the analysis and write the two datasets and the statistics."""
    qk = load_qk(input_path)
    qk = parse_coordinates(qk)
    qk = split_ketiv(qk)
    qk = normalise(qk)
    qk = add_roots(qk, load_lemmas(lemmas_path))
    qk = add_reading_columns(qk)

    classes = classify(qk)

    out_dir.mkdir(parents=True, exist_ok=True)
    classes.different_lexicon_entry[OUTPUT_COLUMNS].to_csv(
        out_dir / "different_lexicon_entry.csv", index=False
    )
    classes.same_different_parsing[OUTPUT_COLUMNS].to_csv(
        out_dir / "same_lexicon_entry_different_parsing.csv", index=False
    )

    stats = pd.DataFrame([
        len(qk),
        classes.proper_nouns,
        len(classes.same_same_parsing),
        len(classes.same_different_parsing),
        len(classes.different_lexicon_entry),
    ]).T
    stats.columns = [
        "Words with QK",
        "Words with a proper name",
        "Words with same lexicon entry and same parsing",
        "Words with same lexicon entry but different parsing",
        "Words with different lexicon entry",
    ]
    stats.to_csv(out_dir / "stats.csv", index=False)

    logging.info("words with Qere/Ketiv: %d", len(qk))
    logging.info("words with a proper name (kept, flagged): %d", classes.proper_nouns)
    logging.info("same lexeme, same parsing (discarded): %d",
                 len(classes.same_same_parsing))
    logging.info("same lexeme, different parsing: %d",
                 len(classes.same_different_parsing))
    logging.info("different lexeme: %d", len(classes.different_lexicon_entry))
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyse the STEPBible TAHOT Qere/Ketiv extraction"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help="OT-QK.tsv produced by qk_extractor.sh")
    parser.add_argument("--lemmas", type=Path, default=DEFAULT_LEMMAS,
                        help="lemmas.tsv produced by qk_extractor.sh")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_DIR,
                        help="directory for the two datasets and stats.csv")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.input.is_file():
        logging.error("input not found: %s", args.input)
        return 1

    try:
        stats = analyse(args.input, args.out_dir, args.lemmas)
    except ValueError as error:
        logging.error(str(error))
        return 1

    print(stats.T.to_string(header=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
