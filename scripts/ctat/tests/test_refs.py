"""Tests for the CTAT/HOTTP reference assembly (scripts/ctat/refs.py).

The OCR stages are exercised against the PDFs (see the README); these tests
cover the parts that turn the data into refs.csv, and prove that the
checked-in refs.csv is reproduced exactly.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import refs  # noqa: E402

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "manual_datasets" / "ctat"


def test_parse_value_single_verse() -> None:
    assert refs.parse_value("2:4") == [(2, 4)]


def test_parse_value_lists_verses_written_with_a_period() -> None:
    # 'Is 28,1.4' is printed as '28:1:4' by the cleaning stage.
    assert refs.parse_value("28:1:4") == [(28, 1), (28, 4)]


def test_parse_value_ampersand_keeps_the_chapter() -> None:
    assert refs.parse_value("4:5 &9") == [(4, 5), (4, 9)]
    assert refs.parse_value("24:17 & 22") == [(24, 17), (24, 22)]


def test_parse_value_range() -> None:
    assert refs.parse_value("3:1-3") == [(3, 1), (3, 2), (3, 3)]


def test_parse_hottp_reads_the_biblebhs_links(tmp_path: Path) -> None:
    text = (
        "[[@BibleBHS:GEN 1:1]] discussion\n"
        "[[@BibleBHS:GEN 1:1]] repeated\n"
        "[[@BibleBHS:DEU 32:8]]\n"
        "no reference here\n"
    )
    path = tmp_path / "hottp.txt"
    path.write_text(text, encoding="utf-8")

    assert refs.parse_hottp(path) == [refs.Ref("DEU", 32, 8), refs.Ref("GEN", 1, 1)]


def test_consolidate_flags_hottp_and_keeps_the_ctat_page() -> None:
    canon = {"GEN": {(1, 1)}, "JOS": {(2, 4), (3, 11)}}
    hottp = [refs.Ref("GEN", 1, 1)]
    ctat = [
        (refs.Ref("JOS", 2, 4), "1", 148),
        (refs.Ref("JOS", 3, 11), "1", 149),
    ]

    rows = refs.consolidate(hottp, ctat, canon)

    assert rows == [
        {"book": "GEN", "chapter": 1, "verse": 1, "hottp": "yes",
         "ctat_volume": "", "ctat_page": ""},
        {"book": "JOS", "chapter": 2, "verse": 4, "hottp": "no",
         "ctat_volume": "1", "ctat_page": "148"},
        {"book": "JOS", "chapter": 3, "verse": 11, "hottp": "no",
         "ctat_volume": "1", "ctat_page": "149"},
    ]


def test_consolidate_drops_references_outside_the_canon() -> None:
    canon = {"JOS": {(2, 4)}}
    rows = refs.consolidate([], [(refs.Ref("JOS", 2, 99), "1", 1)], canon)
    assert rows == []


def test_checked_in_refs_are_reproduced(tmp_path: Path) -> None:
    if not (DATA_DIR / "refs.csv").is_file():
        pytest.skip("checked-in refs not available")

    out = tmp_path / "refs.csv"
    refs.build(out)

    assert out.read_bytes() == (DATA_DIR / "refs.csv").read_bytes()


def test_every_reference_is_in_the_canon() -> None:
    import csv

    canon = refs.load_canon()
    with (DATA_DIR / "refs.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            assert (int(row["chapter"]), int(row["verse"])) in canon[row["book"]], row
