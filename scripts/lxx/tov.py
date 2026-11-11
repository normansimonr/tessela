"""Read Emmanuel Tov's CATSS parallel files (.par) into verse records.

The .par format pairs the Masoretic Hebrew of a verse with the Septuagint
Greek, word by word, and marks every place where the two do not correspond.
This module turns that format into clean verse text: the Masoretic Hebrew, the
Hebrew retroversion (Tov's reconstruction of the Vorlage behind the Greek), the
Greek, and the editorial flags.

The transliteration tables and the list of known malformed lines come from the
translator's earlier Tessela scripts; the parsing here is new, so that markers
are kept as structured flags rather than being flattened into the text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

# Book code in the .par header -> Tessela book ID. The Greek Daniel and Esther
# keep their own codes because they are separate textual traditions.
PAR_BOOKS = {
    "Gen": "GEN", "Exod": "EXO", "Lev": "LEV", "Num": "NUM", "Deut": "DEU",
    "JoshB": "JOS", "JudgB": "JDG", "Ruth": "RUT",
    "1Sam/K": "1SA", "2Sam/K": "2SA", "1/3Kgs": "1KI", "2/4Kgs": "2KI",
    "1Chr": "1CH", "2Chr": "2CH",
    "Esth": "ESG", "Ezr": "EZR", "Neh": "NEH", "Ps": "PSA", "Prov": "PRO",
    "Qoh": "ECC", "Song": "SNG", "Job": "JOB", "Hos": "HOS", "Mic": "MIC",
    "Amos": "AMO", "Joel": "JOL", "Jonah": "JON", "Obad": "OBA", "Nah": "NAM",
    "Hab": "HAB", "Zeph": "ZEP", "Hag": "HAG", "Zech": "ZEC", "Mal": "MAL",
    "Isa": "ISA", "Jer": "JER", "Lam": "LAM", "Ezek": "EZK",
    "Dan": "DAG",
}

FILES = {
    "GEN": "01.Genesis.par", "EXO": "02.Exodus.par", "LEV": "03.Lev.par",
    "NUM": "04.Num.par", "DEU": "05.Deut.par", "JOS": "06.JoshB.par",
    "JDG": "08.JudgesB.par", "RUT": "10.Ruth.par", "1SA": "11.1Sam.par",
    "2SA": "12.2Sam.par", "1KI": "13.1Kings.par", "2KI": "14.2Kings.par",
    "1CH": "15.1Chron.par", "2CH": "16.2Chron.par", "ESG": "18.Esther.par",
    "EZR": "18.Ezra.par", "NEH": "19.Neh.par", "PSA": "20.Psalms.par",
    "PRO": "23.Prov.par", "ECC": "24.Qoh.par", "SNG": "25.Cant.par",
    "JOB": "26.Job.par", "HOS": "28.Hosea.par", "MIC": "29.Micah.par",
    "AMO": "30.Amos.par", "JOL": "31.Joel.par", "JON": "32.Jonah.par",
    "OBA": "33.Obadiah.par", "NAM": "34.Nahum.par", "HAB": "35.Hab.par",
    "ZEP": "36.Zeph.par", "HAG": "37.Haggai.par", "ZEC": "38.Zech.par",
    "MAL": "39.Malachi.par", "ISA": "40.Isaiah.par", "JER": "41.Jer.par",
    "LAM": "43.Lam.par", "EZK": "44.Ezekiel.par", "DAG": "45.DanielOG.par",
}

# The markers that make a verse a candidate for a different Hebrew Vorlage.
# This is the translator's original definition (Tessela's convert script):
# explicit minuses and pluses, long minuses/pluses, a secondary LXX reading,
# a Hebrew variant, a difference in numbers, an incomplete retroversion, and
# the consonant-interchange markers. Any retroversion also counts.
DIFFERENCE_MARKERS = {
    "---", "--+", "---{x}", "--+{x}", "''", "{v}", "G", "=+", "=r", ".",
    ".rd", ".m", ".z", ".s", ".j", ".w",
}

# The editorial markers we understand. Order matters: longer first.
MARKERS = [
    "--+{x}", "---{x}", "=%vap", "=%vpa", "=%p+", "=p%-", "=%p-", "=%p",
    "=p%", "=%", "=@...a", "{..~}", "{..d}", "{..r}", "{..p}", "~~~", "..a",
    "=;", "=+", "=@", "=:", "=v", "=r", "=?", "--+", "---", "''", "...",
    "{*}", "{**}", "{#}", "{g}", "{v}", "{d}", "{p}", "{!}", "{s}", "{t}",
    "*z", "**", "*",
]

# Malformed lines in the distributed .par files: a tab is missing, so two
# columns are glued into one. Each entry is (broken text, repaired text).
FIXES = [
    ("W/)T H/GRG$Y ^ =W/)T W/H/)MRY KAI\\ TO\\N AMORRAI=ON",
     "W/)T H/GRG$Y ^ =W/)T W/H/)MRY \tKAI\\ TO\\N AMORRAI=ON"),
    ("W/H/KHNYM =W/H/)BNYM .m .kb # KAI\\ OI( LI/QOI ",
     "W/H/KHNYM =W/)BNYM .m .kb \tKAI\\ OI( LI/QOI "),
    ("W/YC+YRW =;W/YC+YDW .rd <9.12 E)PESITI/SANTO {d} KAI\\ H(TOIMA/SANTO ",
     "W/YC+YRW =;W/YC+YDW .rd <9.12 \tE)PESITI/SANTO {d} KAI\\ H(TOIMA/SANTO "),
    ("--+ '' =;L/GBWLWT/YHM <19.49> E)N TOI=S O(RI/OIS AU)TW=N ",
     "--+ '' =;L/GBWLWT/YHM <19.49> \t E)N TOI=S O(RI/OIS AU)TW=N "),
    ("E)N TH=| BASILEI/A| \nAU)TOU=", "E)N TH=| BASILEI/A| AU)TOU="),
    ("E)NNAKO/SIOI PENTH/KONTA \nE(/C", "E)NNAKO/SIOI PENTH/KONTA E(/C"),
    ("TOU= E)PONOMA/SAI TO\\ O)/NOMA/ \nMOU", "TOU= E)PONOMA/SAI TO\\ O)/NOMA/ MOU"),
    ("[96.7]\n\nPSL", "[96.7]\nPSL"),
    ("[11.2]\n\nPSW", "[11.2]\nPSW"),
    ("[47.14]\n\nPSGW", "[47.14]\nPSGW"),
    ("[71.16]\n\nPST", "[71.16]\nPST"),
    ("[37c]\n\n--+", "[37c]\n--+"),
    ("--=", "--+"),
    ("^^^                                    *", "~~~"),
    ("^^^", "~~~"),
    ("''=", "'' ="),
    (";=L/PNY", "=;L/PNY"),
    (";=YHWH", "=;YHWH"),
    (":=NX$", "=:NX$"),
    (":=H/(MWNY", "=:H/(MWNY"),
    (":=W/K/ZHB", "=;W/K/ZHB"),
    ("{...?AU)TOU=} MDBR =v\tLALOU=NTOS", "MDBR =v\t{...?AU)TOU=} LALOU=NTOS"),
    ("W/MR$Y(=?W/B/R$(Y .mb\tKAI\\ E)N A(MARTI/AIS",
     "W/MR$Y( = ?W/B/R$(Y .mb\tKAI\\ E)N A(MARTI/AIS"),
    ("{...K/}{...)$R}\tO(\\N TRO/PON O(/TAN", "{...K/} {...)$R}\tO(\\N TRO/PON O(/TAN"),
    ("{...W/}{...)L}\tKAI\\ MH\\", "{...W/} {...)L}\tKAI\\ MH\\"),
]

HEADER = re.compile(r"^(\S+) (\d+)(?::(\d+))?$")
BRACKETS = re.compile(r"\[\[(\d+(?:\.\d+)?[a-z]?)\]\]|\[(\d+)(?:\.(\d+))?([a-z]?)\]")
CROSS_REF = re.compile(r"<([^>]*)>")
HEBREW_LETTERS = set(")BGDHWZX+YKLMNSPCQR#$&T")
GREEK_LETTERS = set("ABGDEZHQIKLMNCOPRSJTU FXYW".replace(" ", ""))


def load_json(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


HEBREW = load_json("hebrew_equivalences.json")
GREEK = load_json("greek_equivalences.json")
FINAL = {"כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ"}


@dataclass
class Word:
    """One Hebrew/Greek pair in a verse."""
    mt: str = ""
    retro: str = ""
    greek: str = ""
    lxx_refs: list[tuple[int, int, str]] = field(default_factory=list)
    mt_refs: list[tuple[int, int]] = field(default_factory=list)
    markers: set[str] = field(default_factory=set)
    aramaic: bool = False


@dataclass
class Verse:
    book: str
    chapter: int
    verse: int
    words: list[Word] = field(default_factory=list)

    @property
    def mt(self) -> str:
        return " ".join(w.mt for w in self.words if w.mt)

    @property
    def greek(self) -> str:
        return " ".join(w.greek for w in self.words if w.greek)

    @property
    def retroverted(self) -> str:
        """The Hebrew Vorlage: retroverted words plus unchanged MT words.

        A word that Tov marks as absent from the LXX (a minus) is omitted; a
        word the Greek adds is the retroverted word.
        """
        out = []
        for w in self.words:
            if w.retro:
                out.append(w.retro)
            elif w.mt and not ({"---", "---{x}"} & w.markers):
                out.append(w.mt)
        return " ".join(out)

    @property
    def markers(self) -> set[str]:
        found: set[str] = set()
        for w in self.words:
            found |= w.markers
        return found

    @property
    def potential_difference(self) -> bool:
        if any(w.retro for w in self.words):
            return True
        return bool(self.markers & DIFFERENCE_MARKERS)

    @property
    def lxx_refs(self) -> list[tuple[int, int, str]]:
        refs = []
        for w in self.words:
            for ref in w.lxx_refs:
                if ref not in refs:
                    refs.append(ref)
        return refs


# Markers that are written as tokens or prefixes. Longest first so that
# '--+ {x}' is consumed before '--+'. A retroversion prefix is stripped by
# RETRO_PREFIX; the bare '.' is a marker only when it stands alone.
MARKER_PATTERN = re.compile(
    r"---\s*\{x\}|--\+\s*\{x\}|--\+|---|''|"
    r"\{[^}]*\}|\[\[?[^\]]*\]\]?|<[^>]*>|"
    r"\.\S*|(?<!\S)\.(?!\S)|(?<!\S)G(?!\S)|"
    r"~~~|\^+|,,a|\*+|\?"
)
RETRO_PREFIX = re.compile(
    r"^(?:(?:=@\.\.\.a|=%vap|=%vpa|=%p\+|=p%-|=%p-|=%p|=p%|=%|=@|=;|=:|=v|=r|=\+|=|=\?)\s*)+"
)


def strip_marker(token: str) -> tuple[str, set[str]]:
    """Remove the editorial markers from a token, returning it and the markers."""
    found = {match.group(0).strip() for match in MARKER_PATTERN.finditer(token)}
    token = MARKER_PATTERN.sub(" ", token)
    token = re.sub(r"\{[^}]*\}?", " ", token)  # unbalanced {..?..} markers
    token = token.replace("<sp>", " ").replace("^", " ")
    return " ".join(token.split()), found


def split_hebrew(field: str) -> tuple[str, str, set[str]]:
    """Split a Hebrew field into (MT word, retroverted word, markers).

    A retroversion is written after '='; the '=' may be prefixed with a marker
    such as '=;' (context-based retroversion) or '=: ' (proper noun).
    """
    field = field.strip()
    if "=" not in field:
        mt_raw, retro_raw = field, ""
    else:
        before, _, after = field.partition("=")
        mt_raw, retro_raw = before, "=" + after

    retro_raw = RETRO_PREFIX.sub("", retro_raw)
    mt, mt_markers = strip_marker(mt_raw)
    retro, retro_markers = strip_marker(retro_raw)
    extra = {marker for marker in ("=+", "=r") if marker in field}
    # A marker-only left side ('--+') is a plus, not a Hebrew word.
    if mt in {"--+", "---", "''"}:
        mt = ""
    return mt, retro, mt_markers | retro_markers | extra


def split_greek(field: str, mt_chapter: int, verse_no: int) -> tuple[str, list, list[tuple[int, int]], set[str]]:
    lxx_refs = []
    mt_refs = []
    for match in BRACKETS.finditer(field):
        double, chapter, number, suffix = match.groups()
        if double:
            if "." in double:
                ch, v = double.split(".")
                mt_refs.append((int(ch), int(v)))
            continue
        if chapter is None:
            continue
        if number:
            lxx_refs.append((int(chapter), int(number), suffix or ""))
        else:
            lxx_refs.append((mt_chapter, int(chapter), suffix or ""))
    text, markers = strip_marker(field)
    markers = {m for m in markers if not m.startswith(("[", "<"))}
    return text, lxx_refs, mt_refs, markers


def hebrew_unicode(word: str) -> str:
    word = word.replace("/", "").replace("\u200e", "")
    word = "".join(HEBREW.get(char, char) for char in word).replace("\u200e", "")
    if word and word[-1] in FINAL:
        word = word[:-1] + FINAL[word[-1]]
    return word


def greek_unicode(word: str) -> str:
    for char in ")(|/\\=+*":
        word = word.replace(char, "")
    word = word.replace("#3", "Ñ")
    word = "".join(GREEK.get(char, char) for char in word)
    if word.endswith("σ"):
        word = word[:-1] + "ς"
    return word


def parse_file(path: Path) -> list[Verse]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    for old, new in FIXES:
        raw = raw.replace(old, new)
    raw = raw.replace("--=", "--+").replace("^^^", "~~~")

    verses: list[Verse] = []
    for paragraph in re.split(r"\n\s*\n", raw.strip()):
        lines = [line for line in paragraph.split("\n") if line.strip()]
        if not lines:
            continue
        header = HEADER.match(lines[0].strip())
        if not header:
            continue
        book = PAR_BOOKS.get(header.group(1))
        if book is None:
            continue
        number = int(header.group(2))
        second = header.group(3)
        if second is None:
            if book == "OBA":
                chapter, verse_no = 1, number
            else:
                # A running head that fell on a page break: the words continue
                # the previous verse.
                chapter, verse_no = (verses[-1].chapter, verses[-1].verse) if verses else (number, 1)
        else:
            chapter, verse_no = number, int(second)
        verse = Verse(book, chapter, verse_no)
        for line in lines[1:]:
            if "\t" not in line:
                continue
            hebrew, greek = line.split("\t", 1)
            aramaic = ",,a" in hebrew or ",,a" in greek
            hebrew = hebrew.replace(",,a", " ")
            greek = greek.replace(",,a", " ")

            mt, retro, h_markers = split_hebrew(hebrew)
            greek_text, lxx_refs, mt_refs, g_markers = split_greek(greek, verse.chapter, verse.verse)

            word = Word(
                mt=hebrew_unicode(mt),
                retro=hebrew_unicode(retro),
                greek=greek_unicode(greek_text),
                lxx_refs=lxx_refs,
                mt_refs=mt_refs,
                markers=h_markers | g_markers,
                aramaic=aramaic,
            )
            # A Greek minus (---) means the MT word has no counterpart.
            if "---" in g_markers:
                word.markers.add("---")
            verse.words.append(word)
        verses.append(verse)
    return verses


def read_all(raw_dir: Path) -> list[Verse]:
    """Read every book, merging repeated verse headers into one verse."""
    merged: dict[tuple[str, int, int], Verse] = {}
    order: list[tuple[str, int, int]] = []
    for filename in FILES.values():
        path = raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(path)
        for verse in parse_file(path):
            key = (verse.book, verse.chapter, verse.verse)
            if key not in merged:
                merged[key] = verse
                order.append(key)
            else:
                merged[key].words.extend(verse.words)
    return [merged[key] for key in order]
