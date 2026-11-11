"""Tests for the Qere/Ketiv pipeline (scripts/qere_ketiv).

The datasets are derived from the STEPBible TAHOT files, which are far too
large to keep in the repository. The tests therefore prove three things:

* the fragile parts of the TAHOT parsing behave as the datasets assume;
* the roots resolve against the checked-in lemma index; and
* running the analysis on the checked-in extraction (OT-QK.tsv) reproduces
  the checked-in datasets exactly.

The pipeline needs pandas, which is an optional dependency:
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/pytest scripts/qere_ketiv/tests
"""

import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import qk_analyzer  # noqa: E402
import verse_consolidator  # noqa: E402

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "manual_datasets" / "qere_ketiv"

# A real TAHOT Qere/Ketiv line, trimmed to the columns the pipeline reads.
GEN_9_21 = (
    "Gen.9.21#07=Q(K)\tאָהֳלֽ/וֹ\\׃\t'o.ho.L/o\ttent/ his\t"
    "{H0168G}/H9023\\H9016\tHNcmsc/Sp3ms\t"
    "K= 'o.ho.Lo/h (אָהֳלֹ/ה\\׃) \"tent/ his\" (H0168G/H9023\\H9016=HNcbsc/Sp3ms)\t\t"
    "H0168G\t\t\t{H0168G=אֹ֫הֶל=: tent}/H9023=Ps3m=his"
)

# A proper-noun Qere/Ketiv line: the pipeline drops these.
GEN_36_5 = (
    "Gen.36.5#04=Q(K)\tיְע֥וּשׁ\t\tJeish\t{H3274}\tHNpm\t"
    "K= ye'.ish (יְעִישׁ) \"Jeish\" (H3274=HNpm)"
)

# Tags with an escaped space: the old 'last whitespace token' parser lost all
# but the final tag, so the readings were wrongly called different lexemes.
ESCAPED_SPACE_NOTE = (
    "K= se.vi.vo.to/v (סְבִיבֹת/וֹ\\׃\\ \\ס) \"around/ him\" "
    "(H5439G/H9033\\H9016\\ \\H9018=HNcbsc/Sp3bs)"
)

# A note with more than one reading: only the K reading is wanted.
MULTI_READING_NOTE = (
    "B= he/m.fe.ru.tzim (הֵ֣/מפְּרוּצִ֔ים) \"<the>/ [had been] broken down\" "
    "(H9009/{H6555}=HTd/Pp3mp) ¦ K= ha/me.for.va.tzim (הַ/מְפֹרוָצִים) "
    "\"<the>/ [had been] broken down\" (H9009/H6555=HTd/Pp3mp)"
)


def write_qk(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "OT-QK.tsv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_parse_coordinates_splits_book_chapter_verse_and_word() -> None:
    qk = pd.DataFrame({"Coordinates": ["Gen.9.21#07=Q(K)"],
                       "Expanded Tags": [""]})
    parsed = qk_analyzer.parse_coordinates(qk)
    assert parsed.loc[0, "book"] == "Gen"
    assert parsed.loc[0, "chapter"] == 9
    assert parsed.loc[0, "verse"] == "21"
    assert parsed.loc[0, "word_index"] == 7
    assert "Coordinates" not in parsed.columns


def test_parse_coordinates_ignores_parenthetical_hebrew_reference() -> None:
    qk = pd.DataFrame({"Coordinates": ["Psa.51.1(51.3)#02=Q(K)"],
                       "Expanded Tags": [""]})
    parsed = qk_analyzer.parse_coordinates(qk)
    assert parsed.loc[0, "book"] == "Psa"
    assert parsed.loc[0, "chapter"] == 51
    assert parsed.loc[0, "verse"] == "1"


def test_split_ketiv_parses_hebrew_transliteration_gloss_and_tags() -> None:
    qk = pd.DataFrame({"Ketiv Note": [
        "K= 'o.ho.Lo/h (אָהֳלֹ/ה\\׃) \"tent/ his\" (H0168G/H9023\\H9016=HNcbsc/Sp3ms)"
    ]})
    split = qk_analyzer.split_ketiv(qk)
    assert split.loc[0, "Ketiv"] == "אָהֳלֹ/ה\\׃"
    assert split.loc[0, "Ketiv Translit"] == "'o.ho.Lo/h"
    assert split.loc[0, "Ketiv Gloss"] == "tent/ his"
    assert split.loc[0, "Strongs K"] == "H0168G/H9023\\H9016"
    assert split.loc[0, "Parsing K"] == "HNcbsc/Sp3ms"


def test_split_ketiv_keeps_tags_containing_an_escaped_space() -> None:
    split = qk_analyzer.split_ketiv(pd.DataFrame({"Ketiv Note": [ESCAPED_SPACE_NOTE]}))
    assert split.loc[0, "Strongs K"] == "H5439G/H9033\\H9016\\ \\H9018"


def test_split_ketiv_takes_the_ketiv_from_a_multi_reading_note() -> None:
    split = qk_analyzer.split_ketiv(
        pd.DataFrame({"Ketiv Note": [MULTI_READING_NOTE]})
    )
    assert split.loc[0, "Ketiv"] == "הַ/מְפֹרוָצִים"
    assert split.loc[0, "Parsing K"] == "HTd/Pp3mp"


def test_split_ketiv_fails_loudly_on_an_unparsable_note() -> None:
    with pytest.raises(ValueError, match="unparsable Ketiv note"):
        qk_analyzer.split_ketiv(pd.DataFrame({"Ketiv Note": ["not a note"]}))


def test_normalise_strips_waw_and_he_but_keeps_the_lexical_core() -> None:
    qk = pd.DataFrame({
        "Strongs Q": ["{H9002/H0168G}"],
        "Parsing Q": ["HNcmsc/Sp3ms"],
        "Strongs K": ["(H9009\\H0430G"],
        "Parsing K": ["HNcmpa"],
    })
    normalised = qk_analyzer.normalise(qk)

    assert normalised.loc[0, "Strongs Q"].strip() == "H0168G"
    assert normalised.loc[0, "Strongs K"].strip() == "H0430G"
    assert normalised.loc[0, "Parsing Q"] == "HNcmsc Sp3ms"


def test_resolve_root_skips_syntax_tags_and_tries_the_base_tag() -> None:
    lemmas = {"H0168G": "אֹ֫הֶל", "H0430G": "אֱלֹהִים"}
    assert qk_analyzer.resolve_root("H9003 H0168G", lemmas) == "אֹ֫הֶל"
    assert qk_analyzer.resolve_root("H0430", lemmas) == "אֱלֹהִים"
    assert qk_analyzer.resolve_root("H9999", lemmas) == ""
    assert qk_analyzer.resolve_root(float("nan"), lemmas) == ""


def test_proper_names_are_kept_and_flagged(tmp_path: Path) -> None:
    qk_path = write_qk(tmp_path, GEN_9_21, GEN_36_5)
    lemmas_path = tmp_path / "lemmas.tsv"
    lemmas_path.write_text("H0168G\tאֹ֫הֶל\nH3274\tיְעוּשׁ\n", encoding="utf-8")

    stats = qk_analyzer.analyse(qk_path, tmp_path, lemmas_path)

    assert stats.loc[0, "Words with QK"] == 2
    assert stats.loc[0, "Words with a proper name"] == 1
    assert stats.loc[0, "Words with same lexicon entry and same parsing"] == 1
    assert stats.loc[0, "Words with same lexicon entry but different parsing"] == 1
    assert stats.loc[0, "Words with different lexicon entry"] == 0

    different = pd.read_csv(tmp_path / "different_lexicon_entry.csv")
    same_different = pd.read_csv(
        tmp_path / "same_lexicon_entry_different_parsing.csv"
    )
    assert different.empty
    assert list(same_different.columns) == qk_analyzer.OUTPUT_COLUMNS
    assert len(same_different) == 1
    assert same_different.loc[0, "Qere Root"] == "אֹ֫הֶל"
    assert same_different.loc[0, "Qere Parsing"] == (
        "common noun, masculine, singular, construct + pronominal suffix, "
        "3rd person, masculine, singular"
    )
    assert same_different.loc[0, "Proper Name"] == "no"


def test_analysis_reproduces_the_checked_in_datasets(tmp_path: Path) -> None:
    if not (DATA_DIR / "OT-QK.tsv").is_file():
        pytest.skip("checked-in extraction not available")

    qk_analyzer.analyse(DATA_DIR / "OT-QK.tsv", tmp_path, DATA_DIR / "lemmas.tsv")

    for name in (
        "different_lexicon_entry.csv",
        "same_lexicon_entry_different_parsing.csv",
        "stats.csv",
    ):
        assert (tmp_path / name).read_bytes() == (DATA_DIR / name).read_bytes(), name


def test_consolidator_collapses_both_kinds_and_keeps_every_reading(
    tmp_path: Path,
) -> None:
    same = pd.DataFrame([
        {"book": "Gen", "chapter": 1, "verse": 1, "word_index": 1, "Proper Name": "no"}
    ])
    different = pd.DataFrame([
        {"book": "Gen", "chapter": 1, "verse": 1, "word_index": 2, "Proper Name": "yes"},
        {"book": "Gen", "chapter": 2, "verse": 1, "word_index": 1, "Proper Name": "no"},
    ])
    for frame in (same, different):
        for column in verse_consolidator.DETAIL_COLUMNS:
            frame[column] = f"{column}-{frame['word_index'].iloc[0]}"
    same.to_csv(tmp_path / "same_lexicon_entry_different_parsing.csv", index=False)
    different.to_csv(tmp_path / "different_lexicon_entry.csv", index=False)

    consolidated = verse_consolidator.consolidate(tmp_path, tmp_path)

    types = {
        (row.book, row.chapter, row.verse): row.type
        for row in consolidated.itertuples()
    }
    assert types == {("Gen", 1, 1): "kK", ("Gen", 2, 1): "K"}

    gen_1_1 = consolidated[
        (consolidated["chapter"] == 1) & (consolidated["verse"] == 1)
    ].iloc[0]
    assert gen_1_1["Qere"] == "Qere-1 | Qere-2"
    assert gen_1_1["Variant Type"] == "different word and different grammar"
    assert gen_1_1["Proper Name"] == "yes"

    gen_2_1 = consolidated[consolidated["chapter"] == 2].iloc[0]
    assert gen_2_1["Variant Type"] == "different word"

    written = pd.read_csv(tmp_path / "qere_ketiv_verses.csv")
    assert list(written.columns) == verse_consolidator.OUTPUT_COLUMNS
