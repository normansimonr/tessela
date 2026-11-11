"""Tests for the witness loading and comparison helpers."""

import pytest

from src.witnesses import diff_segments, normalise, parse_reference, readings


def test_normalise_removes_points_maqaf_and_punctuation() -> None:
    assert normalise("בְּרֵאשִׁ֖ית בָּרָ֣א") == "בראשית ברא"
    assert normalise("מִכָּל־מְלַאכְתּ֖וֹ׃") == "מכל מלאכתו"


def test_normalise_keeps_consonants() -> None:
    assert normalise("ישראל") == "ישראל"


def test_parse_reference_accepts_ids_and_names() -> None:
    assert parse_reference("DEU 32:8") == ("DEU", 32, 8)
    assert parse_reference("Genesis 2:2") == ("GEN", 2, 2)
    assert parse_reference("1 Samuel 1:11") == ("1SA", 1, 11)


def test_parse_reference_rejects_unknown_book() -> None:
    with pytest.raises(ValueError, match="Unknown book"):
        parse_reference("Nope 1:1")


def test_parse_reference_rejects_malformed_reference() -> None:
    with pytest.raises(ValueError, match="Unrecognised reference"):
        parse_reference("DEU 32")


def test_diff_segments_finds_a_substitution() -> None:
    assert diff_segments("השביעי", "הששי") == [("השביעי", "הששי")]


def test_diff_segments_ignores_word_division_only() -> None:
    assert diff_segments("ויען יוסף", "ו יען יוסף") == []


def test_diff_segments_reports_additions_and_omissions() -> None:
    assert diff_segments("אלהים יענה", "אלהים לא יענה") == [("יענה", "לא יענה")]
    assert diff_segments("עמים למספר בני ישראל", "עמים") == [
        ("עמים למספר בני ישראל", "עמים")
    ]


def test_readings_includes_the_masoretic_text() -> None:
    book_id, items = readings("DEU 32:8")
    assert book_id == "DEU"
    mt = next(reading for reading in items if reading.witness == "MT")
    assert "ישראל" in mt.text
