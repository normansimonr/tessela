"""Tests for the CATSS .par reader."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lxx import tov  # noqa: E402

FIXTURE = """\
Gen 1:1
B/R)$YT\tE)N A)RXH=|
BR)\tE)POI/HSEN
)LHYM\tO( QEO/S

Ps 10:1
L/MH\tI(/NA TI/ [9.22]
YHWH\tKU/RIE [9.22]
MQWM =?MQWH\tSUNAGWGH\\N

Gen 1:2
)T\t---
H/$MYM\tTO\\N OU)RANO\\N
--+\tKAI\\ TH\\N GH=N
"""


def parse(tmp_path: Path):
    path = tmp_path / "01.Genesis.par"
    path.write_text(FIXTURE, encoding="utf-8")
    return {(verse.book, verse.chapter, verse.verse): verse for verse in tov.parse_file(path)}


def test_verse_text_is_converted_to_unicode(tmp_path: Path) -> None:
    verse = parse(tmp_path)[("GEN", 1, 1)]
    assert verse.mt == "בראשית ברא אלהים"
    assert verse.greek == "εν αρχη εποιησεν ο θεος"


def test_retroversion_and_lxx_reference(tmp_path: Path) -> None:
    verse = parse(tmp_path)[("PSA", 10, 1)]
    assert verse.lxx_refs == [(9, 22, "")]
    assert verse.words[2].retro == "מקוה"


def test_minus_and_plus_are_flags(tmp_path: Path) -> None:
    verse = parse(tmp_path)[("GEN", 1, 2)]
    assert "---" in verse.markers
    assert "--+" in verse.markers
    assert verse.potential_difference
    assert "את" in verse.mt
    # The Hebrew word marked as absent from the LXX is not in the Vorlage.
    assert "את" not in verse.retroverted


def test_verse_without_differences_is_not_flagged(tmp_path: Path) -> None:
    assert not parse(tmp_path)[("GEN", 1, 1)].potential_difference
