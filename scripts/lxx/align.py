"""Align Tov's verses with Brenton (the LXX in English) and the JPS (the MT).

Three versification systems meet here:

* Tov's .par files use the Masoretic (Hebrew) numbering.
* Brenton follows the Greek (Septuagint) numbering, which differs in Psalms,
  Jeremiah, Daniel, Esther and a few other places.
* The JPS follows the English numbering, which differs from the Hebrew where a
  Psalm title is unnumbered, where a chapter division falls elsewhere, etc.

Tov's Greek column carries the LXX verse number in square brackets whenever it
differs from the Hebrew (e.g. MT Jer 27:2 is marked [34.2]); the JPS text
carries the Hebrew number in parentheses (e.g. '(3-2)'). Both are used here,
so the alignment is derived from the sources themselves rather than guessed.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from . import tov
from .diff import word_diff

REF = re.compile(r"^(\w+) (\d+):(\d+)$")
JPS_ANNOTATION = re.compile(r"\((\d+)-(\d+)\)")
VPL_LINE = re.compile(r"^(\w+) (\d+):(\d+)([a-z]?) (.*)$")


@dataclass(frozen=True)
class LxxRef:
    book: str
    chapter: int
    verse: int
    suffix: str = ""

    def __str__(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}{self.suffix}"


def load_vpl(path: Path) -> dict[tuple[str, int, int, str], str]:
    """Read an ebible verse-per-line file into (book, chapter, verse, suffix)."""
    verses: dict[tuple[str, int, int, str], str] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            match = VPL_LINE.match(line.rstrip("\n"))
            if not match:
                continue
            book, chapter, verse, suffix, text = match.groups()
            verses[(book, int(chapter), int(verse), suffix)] = text
    return verses


class English:
    """Look up a verse in an English translation, joining LXX sub-verses."""

    def __init__(self, verses: dict[tuple[str, int, int, str], str]):
        self.verses = verses
        self.by_verse: dict[tuple[str, int, int], list[tuple[str, str]]] = defaultdict(list)
        for (book, chapter, verse, suffix), text in verses.items():
            self.by_verse[(book, chapter, verse)].append((suffix, text))
        for key in self.by_verse:
            self.by_verse[key].sort(key=lambda item: (item[0] != "", item[0]))

    def get(self, book: str, chapter: int, verse: int, suffix: str = "") -> str:
        if suffix:
            text = self.verses.get((book, chapter, verse, suffix))
            if text is not None:
                return text
        parts = [text for _, text in self.by_verse.get((book, chapter, verse), [])]
        return " ".join(parts)


def jps_mapping(jps: English) -> dict[tuple[str, int, int], tuple[str, int, int]]:
    """MT reference -> JPS reference, from the '(chapter-verse)' annotations."""
    mapping: dict[tuple[str, int, int], tuple[str, int, int]] = {}
    for (book, chapter, verse), entries in jps.by_verse.items():
        text = " ".join(text for _, text in entries)
        annotations = JPS_ANNOTATION.findall(text)
        if annotations:
            for hc, hv in annotations:
                mapping.setdefault((book, int(hc), int(hv)), (book, chapter, verse))
        else:
            mapping.setdefault((book, chapter, verse), (book, chapter, verse))
    return mapping


def jps_text(jps: English, ref: tuple[str, int, int] | None) -> str:
    if ref is None:
        return ""
    book, chapter, verse = ref
    text = jps.get(book, chapter, verse)
    # The printed JPS carries '(3-2)' markers for the Hebrew numbering; they are
    # useful for the mapping but are not part of the translation.
    return JPS_ANNOTATION.sub("", text).strip()


# Book codes differ between the three sources. Tov uses the Masoretic names
# (with DAG/ESG for the Greek Daniel and Esther); the JPS uses similar codes;
# Brenton uses its own (DNG for the Greek Daniel, SOL for the Song).
BOOK_ID_OVERRIDES = {"EZK": "EZE", "JOL": "JOE", "NAM": "NAH", "SNG": "SON",
              "DAG": "DAN", "ESG": "EST"}
BRENTON_BOOK = {"EZK": "EZE", "JOL": "JOE", "NAM": "NAH",
                "DAG": "DNG", "SNG": "SOL", "ESG": "ESG"}
JPS_BOOK = {"EZK": "EZE", "JOL": "JOE", "NAM": "NAH",
            "DAG": "DAN", "ESG": "EST", "SNG": "SOL"}


def brenton_book(book: str) -> str:
    return BRENTON_BOOK.get(book, book)


def jps_book(book: str) -> str:
    return JPS_BOOK.get(book, book)


def verse_refs(verse: tov.Verse) -> tuple[LxxRef, dict[LxxRef, str]]:
    """Return the verse's primary LXX reference and the Greek text of each ref.

    A word with a bracket belongs to the referenced LXX verse; a word without
    one belongs to the verse's own coordinate. When the verse has no Greek at
    its own coordinate, the most frequent bracket is the primary reference.
    The other references carry plus material: the Song of the Three, the Greek
    Esther additions, and the like.
    """
    mt = (verse.chapter, verse.verse)
    counts: Counter[tuple[int, int, str]] = Counter()
    word_refs: list[list[LxxRef]] = []
    for word in verse.words:
        explicit = [LxxRef(brenton_book(verse.book), c, v, s) for c, v, s in word.lxx_refs]
        refs = explicit or [LxxRef(brenton_book(verse.book), mt[0], mt[1])]
        word_refs.append(refs)
        # A bracketed reference counts even without Greek text (a minus verse
        # still has Tov's LXX number); an untagged word counts only if it has
        # Greek, so that transposition markers do not pull the verse back to
        # its own coordinate.
        if explicit or word.greek:
            for ref in dict.fromkeys(refs):
                counts[(ref.chapter, ref.verse, ref.suffix)] += 1

    has_text = any(word.greek for word in verse.words)
    primary = LxxRef(brenton_book(verse.book), mt[0], mt[1])
    if not has_text:
        # A verse absent from the LXX (a minus): only a bracket, if Tov gives
        # one, identifies the LXX place; otherwise there is no LXX verse.
        if counts:
            chapter, number, suffix = counts.most_common(1)[0][0]
            primary = LxxRef(brenton_book(verse.book), chapter, number, suffix)
        else:
            primary = None
    elif (primary.chapter, primary.verse, primary.suffix) not in counts:
        if counts:
            chapter, number, suffix = counts.most_common(1)[0][0]
            primary = LxxRef(brenton_book(verse.book), chapter, number, suffix)

    texts: dict[LxxRef, list[str]] = defaultdict(list)
    for word, refs in zip(verse.words, word_refs):
        if not word.greek:
            continue
        target = refs[0]
        if LxxRef(brenton_book(verse.book), mt[0], mt[1]) in refs:
            target = LxxRef(brenton_book(verse.book), mt[0], mt[1])
        texts[target].append(word.greek)
    return primary, {ref: " ".join(words) for ref, words in texts.items()}


def build(verses: list[tov.Verse], brenton: English, jps: English) -> list[dict[str, str]]:
    """Build the final table: one row per Tov-flagged verse, plus LXX-only rows."""
    jps_map = jps_mapping(jps)

    # Every primary reference claims its Greek text; references left over are
    # Greek-only material (no Hebrew verse behind them).
    parsed = []
    claimed: set[LxxRef] = set()
    for verse in verses:
        primary, texts = verse_refs(verse)
        claimed.add(primary)
        if verse.potential_difference:
            parsed.append((verse, primary, texts))

    rows: list[dict[str, str]] = []
    for verse, primary, texts in parsed:
        greek = texts.get(primary, "") if primary else ""
        jbook = jps_book(verse.book)
        jps_ref = jps_map.get((jbook, verse.chapter, verse.verse))
        if verse.book == "DAG":
            jps_ref = jps_map.get(("DAN", verse.chapter, verse.verse))
        elif verse.book == "ESG" and not verse.mt:
            jps_ref = None
        row = {
            "book": BOOK_ID_OVERRIDES.get(verse.book, verse.book),
            "chapter": str(verse.chapter),
            "verse": str(verse.verse),
            "lxx_ref": str(primary) if primary else "",
            "jps_ref": str(LxxRef(*jps_ref)) if jps_ref else "",
            "greek": greek,
            "retroverted": verse.retroverted,
            "masoretic": verse.mt,
            "diff": word_diff(verse.mt, verse.retroverted),
            "brenton": brenton.get(primary.book, primary.chapter, primary.verse, primary.suffix) if primary else "",
            "jps": jps_text(jps, jps_ref),
            "lxx_only": "no" if (verse.mt or jps_ref) else "yes",
            "tov_markers": " ".join(sorted(verse.markers)),
        }
        rows.append(row)

        for ref, text in texts.items():
            if ref == primary or ref in claimed:
                continue
            rows.append({
                "book": BOOK_ID_OVERRIDES.get(verse.book, verse.book),
                "chapter": str(verse.chapter),
                "verse": str(verse.verse),
                "lxx_ref": str(ref),
                "jps_ref": "",
                "greek": text,
                "retroverted": "",
                "masoretic": "",
                "diff": "",
                "brenton": brenton.get(ref.book, ref.chapter, ref.verse, ref.suffix),
                "jps": "",
                "lxx_only": "yes",
                "tov_markers": "",
            })
    return rows
