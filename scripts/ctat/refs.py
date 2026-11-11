"""Build the CTAT/HOTTP reference dataset.

Two sources of Old Testament textual-criticism references are combined:

* **CTAT** — Dominique Barthélemy's *Critique textuelle de l'Ancien
  Testament*. The verses cited in the running heads of the five volumes,
  recovered by OCR (see pipeline.py). Each reference carries the volume and
  the page of the PDF on which it appears.
* **HOTTP** — the *Hebrew Old Testament Text Project* preliminary and interim
  reports, whose Pentateuch volume is in HOTTP-PENTATEUCH.txt. The references
  are the BibleBHS links in that text.

The output is one row per verse, with the HOTTP flag and the CTAT page.
"""

from __future__ import annotations

import csv
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "manual_datasets" / "ctat"
BOOKS_YAML = REPO_ROOT / "data" / "reference" / "books.yaml"
CANON = REPO_ROOT / "data" / "reference" / "versification" / "leningrad_codex.csv"

# The French abbreviations used in the CTAT running heads, plus the OCR slips
# that survive the cleaning stage. Mapped to the canonical book IDs.
CTAT_BOOKS = {
    "1Ch": "1CH", "2Ch": "2CH", "1S": "1SA", "2S": "2SA", "1R": "1KI",
    "2R": "2KI", "Jos": "JOS", "Jg": "JDG", "Rt": "RUT", "Esd": "EZR",
    "Néh": "NEH", "Neh": "NEH", "Est": "EST", "Is": "ISA", "Jr": "JER",
    "Lm": "LAM", "Ez": "EZE", "Dn": "DAN", "Os": "HOS", "Jl": "JOE",
    "JI": "JOE", "Am": "AMO", "Ab": "OBA", "Jon": "JON", "Mi": "MIC",
    "Na": "NAH", "Ha": "HAB", "So": "ZEP", "Ag": "HAG", "Za": "ZEC",
    "Mal": "MAL", "Ps": "PSA", "Jb": "JOB", "Pr": "PRO", "Qo": "ECC",
    "Ct": "SON",
}

BHS_REFERENCE = re.compile(r"\[\[@BibleBHS:([A-Z]{3}) (\d+):(\d+)\]\]")


@dataclass(frozen=True, order=True)
class Ref:
    book: str
    chapter: int
    verse: int


def book_order() -> dict[str, int]:
    """Canonical order of the books."""
    books = yaml.safe_load(BOOKS_YAML.read_text(encoding="utf-8"))["books"]
    return {book_id: data["order"] for book_id, data in books.items()}


def load_canon() -> dict[str, set[tuple[int, int]]]:
    """The Hebrew versification canon: book -> {(chapter, verse)}."""
    canon: dict[str, set[tuple[int, int]]] = defaultdict(set)
    with CANON.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            canon[row["book"]].add((int(row["chapter"]), int(row["verse"])))
    return canon


def parse_hottp(path: Path) -> list[Ref]:
    """Read the BibleBHS references out of the HOTTP text."""
    text = path.read_text(encoding="utf-8")
    refs = [Ref(book, int(chapter), int(verse))
            for book, chapter, verse in BHS_REFERENCE.findall(text)]
    logging.info("HOTTP: %d references (%d unique)", len(refs), len(set(refs)))
    return sorted(set(refs))


def parse_value(value: str) -> list[tuple[int, int]]:
    """Turn a cleaned CTAT value into (chapter, verse) pairs.

    The values are already cleaned: 'C:V', 'C:V1:V2' (verses listed with '.'
    in the running head), 'C:V &V2' (verses listed with '&'), and ranges
    'C:V-V2'. A chapter carries over across an '&' group.
    """
    value = value.replace(" ", "")
    pairs: list[tuple[int, int]] = []
    chapter: int | None = None

    for group in value.split("&"):
        parts = [part for part in group.split(":") if part]
        if not parts:
            continue
        if len(parts) == 1:
            if chapter is None:
                continue
            verse_parts = parts
        else:
            chapter = int(parts[0])
            verse_parts = parts[1:]

        for part in verse_parts:
            span = re.fullmatch(r"(\d+)[-–](\d+)", part)
            if span:
                pairs.extend((chapter, verse) for verse in
                             range(int(span.group(1)), int(span.group(2)) + 1))
            elif part.isdigit():
                pairs.append((chapter, int(part)))
    return pairs


def read_ctat(path: Path) -> tuple[list[tuple[Ref, str, int]], list[dict[str, str]]]:
    """Read the cleaned CTAT data into (ref, volume, page) triples."""
    entries: list[tuple[Ref, str, int]] = []
    rejected: list[dict[str, str]] = []

    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            book = CTAT_BOOKS.get(row["book"])
            if book is None:
                rejected.append(row)
                continue
            pairs = parse_value(row["value"])
            if not pairs:
                rejected.append(row)
                continue
            for chapter, verse in pairs:
                entries.append((Ref(book, chapter, verse), row["volume"], int(row["pagina"])))

    logging.info("CTAT: %d references from %d rows", len(entries),
                 len(entries) + len(rejected))
    if rejected:
        logging.warning("CTAT: %d rows could not be read: %s", len(rejected),
                        [f"{r['book']} {r['value']}" for r in rejected[:5]])
    return entries, rejected


def consolidate(hottp: list[Ref], ctat: list[tuple[Ref, str, int]],
                canon: dict[str, set[tuple[int, int]]]) -> list[dict[str, object]]:
    """Merge both sources into one row per verse, dropping impossible refs."""
    hottp_set = set(hottp)
    pages: dict[Ref, set[tuple[str, int]]] = defaultdict(set)
    invalid: list[Ref] = []

    for ref, volume, page in ctat:
        if (ref.chapter, ref.verse) not in canon.get(ref.book, set()):
            invalid.append(ref)
            continue
        pages[ref].add((volume, page))

    for ref in hottp:
        if (ref.chapter, ref.verse) not in canon.get(ref.book, set()):
            invalid.append(ref)

    if invalid:
        logging.warning("dropped %d references outside the canon: %s",
                        len(invalid), [f"{r.book} {r.chapter}:{r.verse}" for r in invalid[:10]])

    order = book_order()
    rows = []
    for ref in sorted(set(pages) | hottp_set,
                      key=lambda r: (order.get(r.book, 999), r.chapter, r.verse)):
        if (ref.chapter, ref.verse) not in canon.get(ref.book, set()):
            continue
        locations = sorted(pages.get(ref, set()))
        rows.append({
            "book": ref.book,
            "chapter": ref.chapter,
            "verse": ref.verse,
            "hottp": "yes" if ref in hottp_set else "no",
            "ctat_volume": ",".join(sorted({volume for volume, _ in locations}, key=int)),
            "ctat_page": ",".join(str(page) for _, page in locations),
        })
    return rows


def build(out_path: Path,
          hottp_path: Path = DATA_DIR / "HOTTP-PENTATEUCH.txt",
          ctat_path: Path = DATA_DIR / "ocr_clean.csv") -> list[dict[str, object]]:
    """Build refs.csv from the HOTTP text and the cleaned CTAT data."""
    canon = load_canon()
    rows = consolidate(parse_hottp(hottp_path), read_ctat(ctat_path)[0], canon)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["book", "chapter", "verse", "hottp",
                                                    "ctat_volume", "ctat_page"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    logging.info("wrote %d verses to %s (%d with HOTTP, %d with CTAT)",
                 len(rows), out_path,
                 sum(1 for row in rows if row["hottp"] == "yes"),
                 sum(1 for row in rows if row["ctat_page"]))
    return rows
