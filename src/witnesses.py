"""Read and compare Masoretic, Samaritan, and Dead Sea Scrolls readings.

The data is the curated, checked-in snapshot under ``data/``:

* MT: ``data/reference/versification/leningrad_codex.csv``
* SP: ``data/manual_datasets/samaritan/samaritan.csv``
* DSS: ``data/manual_datasets/qumran/qumran.csv``

The comparison is consonantal: vowel points, cantillation, maqaf and
punctuation are removed before diffing. DSS editorial markers are preserved in
the source CSV's ``transcription`` column but the ``hebrew_text`` column used
here is the clean consonantal text.
"""

from __future__ import annotations

import csv
import difflib
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MT_CSV = DATA / "reference" / "versification" / "leningrad_codex.csv"
SP_CSV = DATA / "manual_datasets" / "samaritan" / "samaritan.csv"
DSS_CSV = DATA / "manual_datasets" / "qumran" / "qumran.csv"
BOOKS_YAML = DATA / "reference" / "books.yaml"

_POINTS = re.compile(r"[\u0591-\u05C7\u05BE\u05C0\u05C3\u05C6]")
_REFERENCE = re.compile(r"^\s*([1-3]?\s*[A-Za-z][A-Za-z ]*?)\s+(\d+)\s*:\s*(\d+)\s*$")


@dataclass(frozen=True)
class Reading:
    """A single witness reading for a verse."""

    witness: str
    detail: str
    text: str


def normalise(text: str) -> str:
    """Return a consonantal form suitable for comparison."""
    text = text.replace("\u05be", " ")
    text = _POINTS.sub("", text)
    text = text.replace("\u05f3", "").replace("\u05c3", " ")
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def _book_index() -> dict[str, str]:
    books = yaml.safe_load(BOOKS_YAML.read_text(encoding="utf-8"))["books"]
    index: dict[str, str] = {}
    for book_id, data in books.items():
        # Accept the canonical ID (e.g. DEU), the full name (Deuteronomy) and
        # the short name (1 Samuel).
        index[book_id.casefold()] = book_id
        names = data["names"]["en-gb"]
        for key in ("long", "short", "shortest"):
            name = names.get(key)
            if name:
                index[name.casefold()] = book_id
    return index


@lru_cache(maxsize=1)
def _id_to_name() -> dict[str, str]:
    books = yaml.safe_load(BOOKS_YAML.read_text(encoding="utf-8"))["books"]
    return {book_id: data["names"]["en-gb"]["short"] for book_id, data in books.items()}


def parse_reference(reference: str) -> tuple[str, int, int]:
    """Parse a reference such as ``DEU 32:8`` or ``1 Samuel 1:11``."""
    match = _REFERENCE.match(reference)
    if not match:
        raise ValueError(
            f"Unrecognised reference: {reference!r} (expected e.g. 'DEU 32:8')"
        )
    book_name, chapter, verse = match.groups()
    book_id = _book_index().get(" ".join(book_name.split()).casefold())
    if book_id is None:
        raise ValueError(f"Unknown book: {book_name!r}")
    return book_id, int(chapter), int(verse)


def load_mt(book_id: str, chapter: int, verse: int) -> Reading | None:
    with MT_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if (
                row["book"] == book_id
                and int(row["chapter"]) == chapter
                and int(row["verse"]) == verse
            ):
                return Reading("MT", "Leningrad Codex", normalise(row["text"]))
    return None


def load_sp(book_id: str, chapter: int, verse: int) -> Reading | None:
    name = _id_to_name().get(book_id)
    with SP_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if (
                row["book"] == name
                and int(row["chapter"]) == chapter
                and int(row["verse"]) == verse
            ):
                return Reading("SP", "Samaritan Pentateuch", normalise(row["hebrew_text"]))
    return None


def _natural_key(value: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def load_dss(book_id: str, chapter: int, verse: int) -> list[Reading]:
    name = _id_to_name().get(book_id)
    readings: list[Reading] = []
    with DSS_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if (
                row["book"] == name
                and int(row["chapter"]) == chapter
                and int(row["verse"]) == verse
                and row["hebrew_text"].strip()
            ):
                readings.append(
                    Reading("DSS", row["scroll"], normalise(row["hebrew_text"]))
                )
    return sorted(readings, key=lambda reading: _natural_key(reading.detail))


def readings(reference: str) -> tuple[str, list[Reading]]:
    """Return the witness readings for a reference, MT first."""
    book_id, chapter, verse = parse_reference(reference)
    result: list[Reading] = []
    mt = load_mt(book_id, chapter, verse)
    if mt is not None:
        result.append(mt)
    sp = load_sp(book_id, chapter, verse)
    if sp is not None:
        result.append(sp)
    result.extend(load_dss(book_id, chapter, verse))
    return book_id, result


def diff_segments(base: str, other: str) -> list[tuple[str, str]]:
    """Return the non-whitespace substitutions between two normalised texts."""
    matcher = difflib.SequenceMatcher(None, base, other)
    changes: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        left, right = base[i1:i2], other[j1:j2]
        if not left.strip() and not right.strip():
            continue
        changes.append((left, right))
    return changes
