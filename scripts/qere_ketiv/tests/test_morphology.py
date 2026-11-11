"""Tests for the morphology decoder (scripts/qere_ketiv/morphology.py).

The codes are the OpenScriptures scheme with the STEPBible adaptations
documented at <https://tinyurl.com/HebMorph>. The last test proves that every
grammar cell in the checked-in extraction decodes, so a source change that
introduces a new code fails loudly instead of producing nonsense.
"""

import csv
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import morphology  # noqa: E402

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "manual_datasets" / "qere_ketiv"


def test_noun() -> None:
    assert morphology.describe("HNcmsa") == (
        "common noun, masculine, singular, absolute"
    )


def test_noun_with_pronominal_suffix() -> None:
    assert morphology.describe("HC/Ncmsc/Sp3ms") == (
        "conjunction + common noun, masculine, singular, construct "
        "+ pronominal suffix, 3rd person, masculine, singular"
    )


def test_verb_finite() -> None:
    assert morphology.describe("HVqw3ms") == (
        "verb, qal, sequential imperfect, 3rd person, masculine, singular"
    )


def test_verb_participle() -> None:
    assert morphology.describe("HVqrmpa") == (
        "verb, qal, active participle, masculine, plural, absolute"
    )


def test_verb_infinitive_and_cohortative() -> None:
    assert morphology.describe("HVqcc") == "verb, qal, infinitive construct"
    assert morphology.describe("HVqc1cs") == (
        "verb, qal, cohortative, 1st person, common gender, singular"
    )


def test_consecutive_conjunction() -> None:
    assert morphology.describe("Hc/Vqw3ms").startswith(
        "consecutive conjunction + verb, qal, sequential imperfect"
    )


def test_preposition_with_definite_article() -> None:
    assert morphology.describe("HRd/Ncfpc") == (
        "preposition with definite article "
        "+ common noun, feminine, plural, construct"
    )


def test_proper_names_and_aramaic() -> None:
    assert morphology.describe("HNpm") == "proper name, masculine"
    assert morphology.describe("HNpl") == "proper name, location"
    assert morphology.describe("ANgmpd/Ta") == (
        "gentilic noun, masculine, plural, determined + Aramaic article"
    )
    assert morphology.describe("AVqp3ms") == (
        "verb, peal, perfect, 3rd person, masculine, singular"
    )


def test_empty_grammar_describes_nothing() -> None:
    assert morphology.describe("") == ""
    assert morphology.describe(float("nan")) == ""


def test_unknown_code_fails_loudly() -> None:
    with pytest.raises(morphology.MorphologyError):
        morphology.describe("HQz9")


def test_every_checked_in_grammar_cell_decodes() -> None:
    data = DATA_DIR / "OT-QK.tsv"
    if not data.is_file():
        pytest.skip("checked-in extraction not available")

    note = re.compile(r'^K= .+? \([^()]*\) ".*" \(([^()]*)\)$')
    grammars: set[str] = set()
    with data.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            grammars.add(row[5])
            match = note.match(row[6].split(" ¦ ")[-1])
            if match:
                tags = match.group(1)
                grammars.add(tags.split("=", 1)[1] if "=" in tags else "")

    undecodable = []
    for grammar in grammars:
        try:
            morphology.describe(grammar)
        except morphology.MorphologyError as error:
            undecodable.append(str(error))

    assert not undecodable, undecodable
