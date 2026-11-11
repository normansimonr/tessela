"""Build, write and validate the Septuagint variant corpus."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOKS = REPO_ROOT / "data" / "reference" / "books.yaml"
CANON = REPO_ROOT / "data" / "reference" / "versification" / "leningrad_codex.csv"

COLUMNS = ["book", "chapter", "verse", "lxx_ref", "jps_ref", "greek",
           "retroverted", "masoretic", "diff", "brenton", "jps", "lxx_only",
           "tov_markers"]


def book_order() -> dict[str, int]:
    books = yaml.safe_load(BOOKS.read_text(encoding="utf-8"))["books"]
    return {book_id: data["order"] for book_id, data in books.items()}


def canonicalise(rows: list[dict[str, str]],
                 canon: dict[str, set[tuple[int, int]]]) -> list[dict[str, str]]:
    """Keep every row on a canonical MT verse.

    Tov's files contain a few running heads that are not verses (a page break
    cuts 'Num 26:45' to 'Num 6:45') and a few Greek pluses with their own
    number (the Song of the Three, the Greek additions to Lamentations and
    Joshua). A row with Greek and no canonical MT verse is kept as LXX-only,
    anchored to the preceding canonical verse of the book; a row without Greek
    is a parsing artefact and is dropped.
    """
    ordered = {book: sorted(refs) for book, refs in canon.items()}
    out = []
    for row in rows:
        book = row["book"]
        reference = (int(row["chapter"]), int(row["verse"]))
        if book in canon and reference in canon[book]:
            out.append(row)
            continue
        if not row["greek"]:
            continue
        previous = [ref for ref in ordered.get(book, []) if ref < reference]
        if not previous:
            continue
        chapter, verse = previous[-1]
        row["chapter"], row["verse"] = str(chapter), str(verse)
        if row["masoretic"]:
            # The left column of a Greek-only verse is a retroversion, not MT.
            if not row["retroverted"]:
                row["retroverted"] = row["masoretic"]
            row["masoretic"] = ""
        row["diff"] = ""
        row["lxx_only"] = "yes"
        out.append(row)
    return out


def unpoint(text: str) -> str:
    """Remove the vowel points and cantillation from Hebrew text."""
    import re
    return re.sub(r"[\u0591-\u05c7\u05be\u05c0\u05c3\u05c6]", "", text)


def fill_masoretic(rows: list[dict[str, str]],
                   canon_text: dict[tuple[str, int, int], str]) -> None:
    """Fill a missing Masoretic text from the Leningrad codex (unpointed)."""
    from .diff import word_diff
    for row in rows:
        if row["lxx_only"] == "yes" or row["masoretic"]:
            continue
        text = canon_text.get((row["book"], int(row["chapter"]), int(row["verse"])))
        if text:
            row["masoretic"] = unpoint(text)
            row["diff"] = word_diff(row["masoretic"], row["retroverted"])


def load_canon_text() -> dict[tuple[str, int, int], str]:
    texts = {}
    with CANON.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            texts[(row["book"], int(row["chapter"]), int(row["verse"]))] = row["text"]
    return texts


def build_dataset(raw_dir: Path, tov_module, align_module) -> list[dict[str, str]]:
    verses = tov_module.read_all(raw_dir / "LXX_Tov")
    brenton = align_module.English(align_module.load_vpl(raw_dir / "eng-Brenton_vpl" / "eng-Brenton_vpl.txt"))
    jps = align_module.English(align_module.load_vpl(raw_dir / "engjps_vpl" / "engjps_vpl.txt"))
    rows = align_module.build(verses, brenton, jps)
    rows = canonicalise(rows, load_canon())
    fill_masoretic(rows, load_canon_text())

    order = book_order()
    rows.sort(key=lambda row: (order.get(row["book"], 999),
                               int(row["chapter"]), int(row["verse"]),
                               row["lxx_ref"]))
    return rows


def write_dataset(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_canon() -> dict[str, set[tuple[int, int]]]:
    canon: dict[str, set[tuple[int, int]]] = {}
    with CANON.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            canon.setdefault(row["book"], set()).add((int(row["chapter"]), int(row["verse"])))
    return canon


def check_dataset(path: Path) -> list[str]:
    """Return a list of problems; an empty list means the dataset is sound."""
    problems: list[str] = []
    canon = load_canon()
    seen: set[tuple[str, str, str, str]] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            problems.append(f"unexpected columns: {reader.fieldnames}")
        for number, row in enumerate(reader, start=2):
            key = (row["book"], row["chapter"], row["verse"], row["lxx_ref"])
            if key in seen:
                problems.append(f"line {number}: duplicate row {key}")
            seen.add(key)
            if row["book"] not in canon:
                problems.append(f"line {number}: unknown book {row['book']}")
                continue
            reference = (int(row["chapter"]), int(row["verse"]))
            if reference not in canon[row["book"]]:
                problems.append(f"line {number}: {row['book']} {row['chapter']}:{row['verse']} is not in the canon")
            if not row["greek"] and not row["masoretic"]:
                problems.append(f"line {number}: no Greek and no Hebrew")
            if row["lxx_only"] == "yes" and row["masoretic"]:
                problems.append(f"line {number}: LXX-only row has a Masoretic text")
            if row["lxx_only"] == "no" and not row["masoretic"]:
                problems.append(f"line {number}: non-LXX-only row has no Masoretic text")
    return problems
