"""Describe the TAHOT morphology codes in words.

TAHOT's Grammar field uses the OpenScriptures Hebrew morphology codes, with
the STEPBible adaptations documented at <https://tinyurl.com/HebMorph>

  H  language: Hebrew        A  language: Aramaic
  N  noun                   V  verb
  A  adjective              P  pronoun
  R  preposition            T  particle
  C  conjunction            D  adverb
  S  suffix

A word's morphemes are separated by '/' (and '\\' for punctuation); the
language prefix appears only on the first one. This module turns a code such
as 'HC/Ncmsc/Sp3ms' into 'conjunction + noun, common, masculine, singular,
construct + pronominal suffix, 3rd person, masculine, singular'.

The decoder is strict: an unknown code raises MorphologyError, so a change in
the source data is noticed rather than silently rendered as gibberish.
"""

from __future__ import annotations

import re

LANGUAGES = {"H": "Hebrew", "A": "Aramaic"}

# The first letters that can follow a language prefix.
WORD_TYPES = set("NVAPRTCDS")

NOUN_TYPES = {
    "c": "common",
    "g": "gentilic",
    "t": "title",
    "n": "numerical",
}
PROPER_NAME_TYPES = {
    "m": "masculine",
    "f": "feminine",
    "l": "location",
    "t": "title",
    "d": "deity, demon, angel or monster",
}
ADJECTIVE_TYPES = {
    "a": "adjective",
    "c": "cardinal number",
    "o": "ordinal number",
    "g": "gentilic adjective",
}
PRONOUN_TYPES = {
    "p": "personal pronoun",
    "d": "demonstrative pronoun",
    "f": "indefinite pronoun",
    "i": "interrogative pronoun",
    "r": "relative pronoun",
}
PARTICLE_TYPES = {
    "a": "affirmation particle",
    "c": "consequence particle",
    "d": "definite article",
    "e": "exhortation particle",
    "i": "interrogative particle",
    "j": "interjection",
    "m": "demonstrative particle",
    "n": "negative particle",
    "o": "object marker",
    "r": "relative particle",
}
SUFFIX_TYPES = {
    "p": "pronominal suffix",
    "d": "directional he",
    "h": "paragogic he",
    "n": "paragogic nun",
}
GENDERS = {
    "m": "masculine",
    "f": "feminine",
    "b": "both genders",
    "c": "common gender",
    "u": "unspecified gender",
}
NUMBERS = {"s": "singular", "d": "dual", "p": "plural"}
STATES = {"a": "absolute", "c": "construct", "d": "determined"}

HEBREW_STEMS = {
    "q": "qal", "N": "niphal", "p": "piel", "P": "pual", "h": "hiphil",
    "H": "hophal", "t": "hithpael", "o": "polel", "O": "polal",
    "r": "hithpolel", "m": "poel", "M": "poal", "k": "palel", "K": "pulal",
    "Q": "qal passive", "l": "pilpel", "L": "polpal", "f": "hithpalpel",
    "D": "nithpael", "j": "pealal", "i": "pilel", "u": "hothpaal",
    "c": "tiphil", "v": "hishtaphel", "w": "nithpalel", "y": "nithpoel",
    "z": "hithpoel",
}
ARAMAIC_STEMS = {
    "q": "peal", "Q": "peil", "u": "hithpeel", "p": "pael", "P": "ithpaal",
    "M": "hithpaal", "a": "aphel", "h": "haphel", "s": "saphel",
    "e": "shaphel", "H": "hophal", "i": "ithpeel", "t": "hishtaphel",
    "v": "ishtaphel", "w": "hithaphel", "o": "polel", "z": "ithpoel",
    "r": "hithpolel", "f": "hithpalpel", "b": "hephal", "c": "tiphel",
    "m": "poel", "l": "palpel", "L": "ithpalpel", "O": "ithpolel",
    "G": "ittaphal",
}
FINITE_FORMS = {
    "p": "perfect",
    "q": "sequential perfect",
    "i": "imperfect",
    "w": "sequential imperfect",
    "u": "conjunctive imperfect",
    "j": "jussive",
    "c": "cohortative",
    "v": "imperative",
}
PARTICIPLES = {"r": "active participle", "s": "passive participle"}
INFINITIVES = {"a": "infinitive absolute", "c": "infinitive construct"}

PERSON = re.compile(r"^[123]")


class MorphologyError(ValueError):
    """Raised when a morphology code cannot be described."""


def _feature(table: dict[str, str], letter: str, what: str, code: str) -> str:
    try:
        return table[letter]
    except KeyError:
        raise MorphologyError(f"unknown {what} '{letter}' in code '{code}'") from None


def _person_gender_number(rest: str, code: str) -> list[str]:
    """Read person, gender and number (in that order) from the tail."""
    if len(rest) < 3 or not PERSON.match(rest):
        raise MorphologyError(f"incomplete person/gender/number in code '{code}'")
    return [
        f"{rest[0]}{'st' if rest[0] == '1' else 'nd' if rest[0] == '2' else 'rd'} person",
        _feature(GENDERS, rest[1], "gender", code),
        _feature(NUMBERS, rest[2], "number", code),
    ]


def _gender_number_state(rest: str, code: str, state: bool = True) -> list[str]:
    if len(rest) < (3 if state else 2):
        raise MorphologyError(f"incomplete gender/number/state in code '{code}'")
    features = [
        _feature(GENDERS, rest[0], "gender", code),
        _feature(NUMBERS, rest[1], "number", code),
    ]
    if state:
        features.append(_feature(STATES, rest[2], "state", code))
    return features


def _noun(rest: str, code: str) -> str:
    if not rest:
        raise MorphologyError(f"incomplete noun code '{code}'")
    noun_type = rest[0]
    if noun_type == "p":
        subtype = rest[1] if len(rest) > 1 else ""
        return "proper name, " + _feature(PROPER_NAME_TYPES, subtype, "proper-name type", code)
    described = _feature(NOUN_TYPES, noun_type, "noun type", code)
    features = _gender_number_state(rest[1:], code)
    return ", ".join([f"{described} noun", *features])


def _adjective(rest: str, code: str) -> str:
    if not rest:
        raise MorphologyError(f"incomplete adjective code '{code}'")
    described = _feature(ADJECTIVE_TYPES, rest[0], "adjective type", code)
    features = _gender_number_state(rest[1:], code)
    return ", ".join([described, *features])


def _verb(rest: str, code: str, language: str | None) -> str:
    if len(rest) < 2:
        raise MorphologyError(f"incomplete verb code '{code}'")
    stems = ARAMAIC_STEMS if language == "Aramaic" else HEBREW_STEMS
    stem = _feature(stems, rest[0], "verb stem", code)
    form = rest[1]
    tail = rest[2:]

    if form in PARTICIPLES:
        features = _gender_number_state(tail, code)
        return ", ".join(["verb", stem, PARTICIPLES[form], *features])
    if form in INFINITIVES:
        # An infinitive carries only a state; a cohortative carries person.
        if form == "c" and tail and PERSON.match(tail):
            features = _person_gender_number(tail, code)
            return ", ".join(["verb", stem, "cohortative", *features])
        if tail:
            _feature(STATES, tail[0], "state", code)
        return ", ".join(["verb", stem, INFINITIVES[form]])

    features = _person_gender_number(tail, code)
    return ", ".join(["verb", stem, _feature(FINITE_FORMS, form, "verb form", code), *features])


def _pronoun(rest: str, code: str) -> str:
    if not rest:
        raise MorphologyError(f"incomplete pronoun code '{code}'")
    described = _feature(PRONOUN_TYPES, rest[0], "pronoun type", code)
    tail = rest[1:]
    if not tail:
        return described
    return ", ".join([described, *_person_gender_number(tail, code)])


def _preposition(rest: str, code: str) -> str:
    if rest == "d":
        return "preposition with definite article"
    if rest:
        raise MorphologyError(f"unknown preposition type '{rest}' in code '{code}'")
    return "preposition"


def _particle(rest: str, code: str, language: str | None) -> str:
    if not rest:
        return "particle"
    if rest == "a" and language == "Aramaic":
        return "Aramaic article"
    return _feature(PARTICLE_TYPES, rest[0], "particle type", code)


def _suffix(rest: str, code: str) -> str:
    if not rest:
        raise MorphologyError(f"incomplete suffix code '{code}'")
    described = _feature(SUFFIX_TYPES, rest[0], "suffix type", code)
    tail = rest[1:]
    if not tail:
        return described
    return ", ".join([described, *_person_gender_number(tail, code)])


def describe_segment(segment: str, language: str | None = None) -> str:
    """Describe one morpheme of a morphology code."""
    code = segment
    if len(segment) > 1 and segment[0] in LANGUAGES and segment[1] in WORD_TYPES:
        language = LANGUAGES[segment[0]]
        segment = segment[1:]

    if not segment:
        raise MorphologyError(f"empty morphology code '{code}'")

    # 'Hc' / 'Ac' is the conjunction that introduces a consecutive verb.
    if segment in ("Hc", "Ac"):
        return "consecutive conjunction"

    kind, rest = segment[0], segment[1:]
    if kind == "N":
        return _noun(rest, code)
    if kind == "A":
        return _adjective(rest, code)
    if kind == "V":
        return _verb(rest, code, language)
    if kind == "P":
        return _pronoun(rest, code)
    if kind == "R":
        return _preposition(rest, code)
    if kind == "T":
        return _particle(rest, code, language)
    if kind == "C" and not rest:
        return "conjunction"
    if kind == "D" and not rest:
        return "adverb"
    if kind == "S":
        return _suffix(rest, code)
    raise MorphologyError(f"unknown morphology code '{code}'")


def describe(grammar: str) -> str:
    """Describe a whole Grammar cell in words.

    Morphemes are separated by '/', '\\' or whitespace; empty morphemes (as in
    'HR//D') are ignored. An empty cell gives an empty string.
    """
    if not isinstance(grammar, str) or not grammar.strip():
        return ""

    parts = [part for part in re.split(r"[\\/\s]+", grammar) if part]
    language = None
    described: list[str] = []
    for part in parts:
        described.append(describe_segment(part, language))
        if len(part) > 1 and part[0] in LANGUAGES and part[1] in WORD_TYPES:
            language = LANGUAGES[part[0]]
    return " + ".join(described)
