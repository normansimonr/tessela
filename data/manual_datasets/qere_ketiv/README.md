# Qere/Ketiv variants

Where the Masoretic text writes one thing and reads another, this dataset says
where it happens, what the two readings are, and whether the difference matters
for translation.

The Hebrew Bible is written with consonants only; the scribes who added the
vowels also left marginal notes. **Ketiv** (*what is written*) is the
consonantal text in the line; **qere** (*what is read*) is the reading the
tradition says to pronounce instead. Translators normally follow the qere and
record the ketiv as a variant, so every qere/ketiv pair is a place where the
translation could go one way or the other.

## Source

All of the data comes from **STEPBible**: the *Translators Amalgamated Hebrew
OT* (TAHOT), which follows the Leningrad Codex and is published under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The four source files
are:

```
TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
TAHOT Jos-Est - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
TAHOT Job-Sng - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
TAHOT Isa-Mal - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
```

They are published at
<https://github.com/STEPBible/STEPBible-Data/tree/master/Translators%20Amalgamated%20OT%2BNT>
and are **not tracked here**: they weigh about 68 MB in total, and STEPBible
asks that the data be distributed from its own repository rather than copied
about. Only the derived datasets below are tracked.

The extraction was first written by the translator in an earlier repository and
imported here on 2026-10-20.

## Files

| File | Kind | What it is |
|:--|:--|:--|
| `OT-QK.tsv` | stage 1 output | The 1,013 TAHOT lines that carry a plain qere/ketiv variant, verbatim apart from trimmed trailing padding (17 tab-separated columns). |
| `lemmas.tsv` | stage 1 output | 11,415 rows mapping a Strong's tag to its pointed lemma (`H0168G` → `אֹ֫הֶל`), harvested from TAHOT's expanded tags. It supplies the roots. |
| `extracted/Gen-Deu.tsv`, `Jos-Est.tsv`, `Job-Sng.tsv`, `Isa-Mal.tsv` | stage 1 intermediates | The same lines, one file per TAHOT source file, kept so the concatenation can be checked. |
| `different_lexicon_entry.csv` | stage 2 output | 438 words whose qere and ketiv are **different lexemes**. |
| `same_lexicon_entry_different_parsing.csv` | stage 2 output | 496 words that are the **same lexeme** but parsed differently. |
| `stats.csv` | stage 2 output | The counts behind the two files above. |
| `qere_ketiv_verses.csv` | stage 3 output | 837 verses, one row each, saying what kind of variant the verse has and giving the readings themselves. |

## What the pipeline does

One command runs the three stages:

```bash
./scripts/qere-ketiv <tahot-dir>
```

The code lives in `scripts/qere_ketiv/`; the stages are described below.

### 1. Extract (`qk_extractor.sh`)

TAHOT marks each word with its text type. A word whose qere replaces a plain
ketiv is labelled `=Q(K)` in the reference column, for example
`Gen.9.21#07=Q(K)`. The extractor greps those lines out of the four source
files, writes one file per source file, and concatenates them into `OT-QK.tsv`.

TAHOT pads some lines with trailing tabs, which carry no data. The extractor
trims that padding and normalises line endings to LF, so the output is stable
and passes the repository's whitespace guardrails. Nothing else is altered.

In the same pass it collects the lemmas. TAHOT's expanded tags spell out every
ordinary word, `{H0168G=אֹ֫הֶל=: tent...}`, so the extractor harvests each
`tag=lemma` pair into `lemmas.tsv`, sorted by tag and de-duplicated.

Only the **plain** `=Q(K)` form is selected. TAHOT also labels composite
variants such as `=Q(K+B)` (two variants at once) and the other text types
(`L` the Leningrad text, `R` restored text, `X` text reconstructed from the
Septuagint); none of those are in this dataset.

### 2. Analyse (`qk_analyzer.py`)

The TAHOT lines are 17 tab-separated columns; eight are read:

| Column | TAHOT field | Used as |
|--:|:--|:--|
| 1 | `Ref: Eng (+Heb)#Heb.words` | book, chapter, verse and word index |
| 2 | `Hebrew` | the pointed **qere** |
| 3 | `Transliteration` | the qere's transliteration |
| 4 | `Translation` | the qere's gloss |
| 5 | `dStrongs` | the qere's Strong's tags |
| 6 | `Grammar` | the qere's morphology |
| 7 | `Meaning Variants` | the full note, which carries the **ketiv** |
| 12 | `Expanded Strong tags` | the qere's lemma (harvested in stage 1) |

The reference is split on `#` into a verse and a word number, and the verse
into book, chapter and verse. A Hebrew alternative in brackets — `Job.41.12(41.4)#01`
— is dropped, so the coordinates always use the English numbering.

The ketiv is taken from the end of the `Meaning Variants` note, which is fully
structured:

```
K= 'o.ho.Lo/h (אָהֳלֹ/ה\׃) "tent/ his" (H0168G/H9023\H9016=HNcbsc/Sp3ms)
   └ translit ┘ └ Hebrew ┘  └ gloss ┘  └── dStrongs ──┘ └─ grammar ─┘
```

Two quirks are handled: a note may carry more than one reading (`B= … ¦ K= …`),
in which case the last one is the K reading; and the tag cell may contain an
escaped space (`\ \`), so the whole parenthetical tag group is taken rather
than the last whitespace-separated token.

Before the qere and the ketiv are compared, both sides are normalised:

- the markup (`{}`, `()`, `/`, `\`) is removed from the tags;
- the syntactic **waw** (H9001, H9002) and **he** (H9009) come off the
  Strong's tags, so that *and* and *the* do not register as lexical
  differences. The waw also comes off the grammar; the he is left there,
  because it cannot be removed safely;
- the language prefix (`H` Hebrew, `A` Aramaic) is ignored, because it is not
  morphology: a pair whose codes differ only by it (`Npm` / `HNpm`) is the
  same reading, not a parsing difference. Fifteen pairs are of this kind.

The **root** of each reading is the pointed lemma of its lexical tags, looked up
in `lemmas.tsv`; syntactic H9xxx tags are ignored, and a missing letter suffix
is tolerated. It is the dictionary form of the word, not its triliteral root.
A rare Strong's number that occurs in TAHOT only as a ketiv has no lemma to
harvest, so its root is left empty (37 qere and 86 ketiv readings of the 927).

Proper names are **kept, not dropped**: a name spelled one way in the ketiv and
another in the qere is a real translation decision, and it belongs to the
proper-name standard of Milestone 10. They are flagged in the `Proper Name`
column so they can be reviewed on their own. 98 of the 1,013 words are names —
masculine and feminine personal names, place names and titles, in Hebrew and
Aramaic (`Npm`, `Npf`, `Npl`, `Npt`, `ANp…`).

The **morphology** is described in words rather than left as a code, by
`scripts/qere_ketiv/morphology.py`, which follows the OpenScriptures scheme and
the STEPBible adaptations documented at <https://tinyurl.com/HebMorph>. For
example:

| Code | In words |
|:--|:--|
| `HNcmsa` | common noun, masculine, singular, absolute |
| `HNpm` | proper name, masculine |
| `HVqw3ms` | verb, qal, sequential imperfect, 3rd person, masculine, singular |
| `HVqrmpa` | verb, qal, active participle, masculine, plural, absolute |
| `HVqcc` | verb, qal, infinitive construct |
| `HC/Ncmsc/Sp3ms` | conjunction + common noun, masculine, singular, construct + pronominal suffix, 3rd person, masculine, singular |

The decoder is strict: a code it does not know raises an error naming the code,
so a change in the source data is noticed rather than silently rendered as
nonsense.

The remaining words fall into three classes:

| Class | Words | Meaning |
|:--|--:|:--|
| Different lexicon entry | 438 | The qere and the ketiv are different words. These can change the translation. |
| Same lexeme, different parsing | 496 | The same word read with a different morphology. A grammatical choice. |
| Same lexeme, same parsing | 79 | No difference worth recording; discarded. |

The first two are written out as CSV; the third is only counted, in `stats.csv`.

### 3. Consolidate (`verse_consolidator.py`)

A translation is made verse by verse, so the word-level datasets are collapsed
to one row per verse. Each verse gets a `type`:

| `type` | `Variant Type` | Meaning | Verses |
|:--|:--|:--|--:|
| `K` | different word | contains a different-lexeme variant | 383 |
| `k` | different grammar | contains only same-lexeme (parsing) variants | 425 |
| `kK` | different word and different grammar | contains both kinds | 29 |

`Variant Type` says the same thing in words, so the file reads without having
to remember the letters.

A verse with more than one variant keeps every reading: the values within one
column are joined with ` | `, in word order, with exact repeats removed.

## Reading the data

The two word-level CSVs share these columns:

| Column | Description |
|:--|:--|
| `book` | TAHOT's book code (see below) |
| `chapter`, `verse` | English (NRSV) chapter and verse |
| `word_index` | the word number in the verse, as TAHOT numbers the words of the Hebrew ketiv text |
| `Qere` | the pointed Hebrew of the qere, with `/` and `\` marking affixes and punctuation |
| `Qere Translit` | the qere's transliteration |
| `Qere Gloss` | the qere's gloss, in the context of this verse |
| `Qere Root` | the pointed lemma of the qere's lexical tags |
| `Qere Strongs` | the qere's normalised dStrongs |
| `Qere Parsing` | the qere's morphology, in words |
| `Ketiv` … `Ketiv Parsing` | the same six fields for the ketiv |
| `Proper Name` | `yes` when the reading is a proper name |
| `Ketiv Note` | the raw TAHOT note, kept as provenance |

`qere_ketiv_verses.csv` has `book`, `chapter`, `verse`, `type`,
`Variant Type` (the same in words) and the reading columns as above (`Qere` to
`Ketiv Parsing`), plus `Proper Name` (`yes` when any variant in the verse is a
name), without `word_index` and `Ketiv Note`. When a verse has several
variants, each column holds the values joined with ` | `.

**Book codes.** Uppercasing TAHOT's code gives the canonical book ID
(`Gen` → `GEN`, `1Ch` → `1CH`), with four exceptions:

| TAHOT | Tessela | Book |
|:--|:--|:--|
| `Ezk` | `EZE` | Ezekiel |
| `Jol` | `JOE` | Joel |
| `Nam` | `NAH` | Nahum |
| `Sng` | `SON` | Song of Songs |

**Versification.** The coordinates follow the English numbering of the source,
not the Hebrew numbering that `data/reference/versification/` (and
`scripts/check-verses`) use for the Old Testament. A verse must be mapped
before it is compared with the translation content.

## Rebuilding the datasets

The pipeline needs Python 3 and pandas, which is an optional dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[qere-ketiv]'
```

Then, with the four TAHOT files in one directory:

```bash
./scripts/qere-ketiv ~/data/tahot
```

Options: `--out DIR` writes somewhere other than `data/manual_datasets/qere_ketiv`,
and `--python PATH` selects an interpreter other than `.venv/bin/python`.
The script fails with a clear message if a TAHOT file is missing or pandas
cannot be imported.

A run should end with:

```
words with Qere/Ketiv: 1013
words with a proper name (kept, flagged): 98
same lexeme, same parsing (discarded): 79
same lexeme, different parsing: 496
different lexeme: 438
verses with a Qere/Ketiv variant: 837
  type K: 383
  type k: 425
  type kK: 29
```

The pipeline is deterministic: the same TAHOT files give byte-identical
datasets. The checked-in files were regenerated on 2026-10-20 from the
STEPBible files with these SHA-256 hashes:

```
e9b8546ee48fe0bfc57c3b70f5f40e98d96580e803526d19026224e31753368b  TAHOT Gen-Deu
f3ded203d2a74d6368932c97ae550d1d0754b271af491dc0dedf36fe3ba0bcc5  TAHOT Isa-Mal
bb508af3af07822fca84cc43a0eba79eb70eecf672aabc0245b8d8cecf329d96  TAHOT Job-Sng
195fee1dc3653bab33701f170734eb894ed647c10cd08cc61749375fe8b73775  TAHOT Jos-Est
```

## Caveats

- The datasets record **readings and tags**, not translation decisions. They
  are a working list for the translator, not a critical apparatus.
- The root is the pointed lemma, not the triliteral root, and it is empty where
  TAHOT has no lemma for that Strong's number.
- The morphology follows the OpenScriptures scheme as STEPBible adapts it. A
  code the decoder does not know stops the pipeline with an error naming the
  code; it is never guessed. The raw codes remain in `OT-QK.tsv` (and in
  `Ketiv Note`) if a specialist needs them.
- Composite variants (`=Q(K+B)`) and the restored/Septuagint text types are
  outside this dataset.
- Nothing consumes these files yet: they are not wired into the render, the
  content validator or the pre-commit checkers.

## Tests

`scripts/qere_ketiv/tests/` proves the fragile parts of the TAHOT parsing, the
root lookup, the morphology decoder and the verse consolidation, and that the
analysis of the checked-in `OT-QK.tsv` reproduces the checked-in datasets
exactly. One test proves that every grammar cell in the checked-in extraction
decodes to words:

```bash
.venv/bin/pytest scripts/qere_ketiv/tests
```

That needs the `dev` extra as well:
`.venv/bin/pip install -e '.[qere-ketiv,dev]'`.
