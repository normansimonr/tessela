"""Tests for the versification alignment and the word diff."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lxx import (
    align,  # noqa: E402
    diff,  # noqa: E402
    tov,  # noqa: E402
)


def test_jps_annotations_map_hebrew_to_english() -> None:
    english = align.English({
        ("PSA", 3, 1, ""): "(3-1) A Psalm of David. (3-2) LORD, how many are mine adversaries!",
        ("PSA", 3, 2, ""): "(3-3) Many there are that say of my soul.",
        ("GEN", 1, 1, ""): "In the beginning God created.",
    })
    mapping = align.jps_mapping(english)

    assert mapping[("PSA", 3, 2)] == ("PSA", 3, 1)
    assert mapping[("PSA", 3, 3)] == ("PSA", 3, 2)
    assert mapping[("GEN", 1, 1)] == ("GEN", 1, 1)


def test_brenton_subverses_are_joined() -> None:
    english = align.English({
        ("ESG", 1, 1, ""): "In the second year.",
        ("ESG", 1, 1, "b"): "A Jew dwelling in Susa.",
    })
    assert english.get("ESG", 1, 1) == "In the second year. A Jew dwelling in Susa."
    assert english.get("ESG", 1, 1, "b") == "A Jew dwelling in Susa."


def test_verse_refs_reads_the_lxx_bracket() -> None:
    verse = tov.Verse("PSA", 10, 1)
    verse.words.append(tov.Word(mt="למה", greek="ινα τι", lxx_refs=[(9, 22, "")]))
    primary, texts = align.verse_refs(verse)

    assert str(primary) == "PSA 9:22"
    assert texts[primary] == "ινα τι"


def test_verse_refs_keeps_a_minus_verse_without_greek() -> None:
    verse = tov.Verse("JER", 27, 1)
    verse.words.append(tov.Word(mt="בראשית", greek="", lxx_refs=[(34, 1, "")]))
    primary, _ = align.verse_refs(verse)

    assert str(primary) == "JER 34:1"


def test_word_diff_marks_the_changes() -> None:
    assert diff.word_diff("א ב ג", "א ב ד") == "א ב [-ג-]{+ד+}"
    assert diff.word_diff("א ב", "א ב ג") == "א ב {+ג+}"
    assert diff.word_diff("א ב ג", "א ב") == "א ב [-ג-]"
