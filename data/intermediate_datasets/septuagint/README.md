# Septuagint variants (Tov / CATSS)

> **Data is fetched locally.** `tov_flagged.csv` and `normalisation/` are not
> tracked: they are derived from Tov's CATSS data and are written to
> `data/derived/septuagint/` by `make data-septuagint` (see
> [`DATA_LICENSES.md`](../../DATA_LICENSES.md)). The paths in this README are
> relative to that derived folder unless stated otherwise.

The verses where the Septuagint probably reflects a Hebrew Vorlage different
from the Masoretic Text, with the evidence side by side: Tov's Greek, his
retroverted Hebrew, the Masoretic text, a word-level diff, Brenton's English
and the JPS.

The list is not a complete apparatus. It follows Emmanuel Tov's CATSS parallel
files: a verse is included only where Tov's word alignment marks a difference
that may go back to the Hebrew, so the first filter is already scholarly
judgement, not a mechanical comparison.

## Sources

| Source | File | What it provides |
|:--|:--|:--|
| Tov, CATSS | `raw/LXX_Tov/*.par` (42 files) | The Hebrew/Greek word alignment, the editorial markers and the LXX verse numbers. |
| Brenton | `raw/eng-Brenton_vpl.txt` | The Septuagint in English (ebible.org, public domain). |
| JPS 1917 | `raw/engjps_vpl.txt` | The Masoretic Text in English (ebible.org, public domain). |
| Leningrad codex | `data/reference/versification/leningrad_codex.csv` | The Hebrew text, used to fill the one verse where Tov's Hebrew column is empty. |

The CATSS `.par` files are Tov's data; they are included here so that the build
is reproducible. The folder has 42 files: the 39 used by the build plus the
alternate Joshua (Alexandrinus), Judges (Alexandrinus) and Daniel (Theodotion)
files, kept for completeness but not read. The two English translations are
public domain.

## The versification problem

Four numbering systems meet in this corpus, and they do not agree:

- **Tov** uses the Masoretic (Hebrew) numbering. I checked every book against
  the Leningrad canon: Tov's 23,212 verse coordinates match it exactly.
- **Brenton** follows the Greek numbering. Psalm 9 absorbs Masoretic Psalms
  9–10; Jeremiah 27 is Greek Jeremiah 34; the Greek Daniel has the Song of the
  Three inside chapter 3.
- **The JPS** follows the English numbering, which differs from the Hebrew
  wherever a Psalm title is unnumbered or a chapter division falls elsewhere.
- **The Masoretic text** is Tov's own coordinate system, so `book, chapter,
  verse` in this dataset is always the Hebrew verse.

The alignment is not guessed. Each source states the correspondence itself:

- Tov's Greek column carries the LXX verse number in square brackets whenever
  it differs from the Hebrew: Masoretic `Jer 27:2` is marked `[34.2]`,
  `Ps 10:1` is marked `[9.22]`, `Dan 3:24` is marked `[91]`.
- The JPS text carries the Hebrew number in parentheses: Psalm 3:2 is printed
  `(3-2)`, Genesis 31:55 is `(32-1)`. These annotations give the Hebrew → JPS
  map directly.

Where Tov gives no bracket, the LXX verse is the same coordinate. Where the
Greek has no verse at all (a minus), the row has no LXX reference and no
Brenton text; the Masoretic text and the diff still show what the Greek lacks.

### Book codes

The same book has three codes. The dataset uses the canonical book ID in `book`, and the
source code in `lxx_ref` and `jps_ref`:

| Tessela | Tov | Brenton | JPS |
|:--|:--|:--|:--|
| EZE | EZK | EZE | EZE |
| JOE | JOL | JOE | JOE |
| NAH | NAM | NAH | NAH |
| SON | SNG | SOL | SOL |
| DAN | DAG (Old Greek) | DNG | DAN |
| EST | ESG (Greek Esther) | ESG | EST |

### The Greek additions

The Greek Daniel and Esther contain material with no Masoretic counterpart: the
Song of the Three (Greek Daniel 3:24–90), Susanna, Bel, and the additions to
Esther. These are kept as **LXX-only** rows (`lxx_only = yes`): the Greek and
Brenton columns are filled, the Hebrew and JPS columns are empty, and the
`book/chapter/verse` anchor is the Masoretic verse after which the addition
stands (Daniel 3:23 for the Song). The same treatment is given to the smaller
Greek pluses in Lamentations and Joshua.

## The pipeline

One entry point, `scripts/lxx-refs`:

```bash
./scripts/lxx-refs build     # raw .par files -> tov_flagged.csv
./scripts/lxx-refs check     # canon, duplicates, empty rows
./scripts/lxx-refs missing   # write normalisation/missing.csv
./scripts/lxx-refs normalise # reuse/extend the semantic normalisations
```

`build` runs four stages (the code is in `scripts/lxx/`):

1. **Read** (`tov.py`). The `.par` paragraphs become verse records: the
   Masoretic words, the retroverted words (the text after `=`), the Greek, the
   LXX brackets and the editorial markers, all converted to Unicode. The
   distributed files contain a few malformed lines (a missing tab, a broken
   line); the fixes are a literal table in `tov.py`, each with its verse.
2. **Flag.** A verse is a candidate when it contains any of Tov's difference
   markers — `---` (minus in the LXX), `--+` (plus), `''` (long minus/plus),
   `{v}`, `G`, `=+`, `=r`, or one of the consonant-interchange markers — or any
   retroversion. This is the translator's original definition, applied more
   faithfully than the earlier script: the old code missed every retroversion
   written with `=;`, so this build finds more genuine variants (12,784 Masoretic
   verses instead of 11,928).
3. **Align** (`align.py`). The LXX bracket and the JPS annotation are read as
   described above. The English texts are looked up in the two ebible files;
   Brenton's sub-verses (Esther 1:1b–s) are joined to their base verse.
4. **Canonicalise** (`dataset.py`). Tov's files contain a few running heads that
   are not verses (a page break cuts `Num 26:45` to `Num 6:45`) and a few Greek
   pluses with their own number. A row with Greek and no canonical Hebrew verse
   is kept as LXX-only, anchored to the preceding canonical verse; a row without
   Greek is a parsing artefact and is dropped. A missing Masoretic text is
   filled from the Leningrad codex (unpointed, so it can be compared with Tov's
   unpointed Hebrew).

## `tov_flagged.csv`

One row per verse:

| Column | Description |
|:--|:--|
| `book`, `chapter`, `verse` | The Masoretic verse, canonical IDs (`data/reference/books.yaml`). |
| `lxx_ref` | The Septuagint verse in Brenton's numbering, e.g. `JER 34:2`, `PSA 9:22`, `DNG 3:91`; empty for a minus. |
| `jps_ref` | The JPS verse, e.g. `PSA 3:1` for Masoretic Psalm 3:2; empty for an LXX-only row. |
| `greek` | Tov's Greek text of the verse (Unicode, editorial markers removed). |
| `retroverted` | Tov's reconstruction of the Hebrew Vorlage behind the Greek. Unchanged Masoretic words are kept; words the Greek lacks are omitted; words the Greek adds are included. |
| `masoretic` | The Masoretic Hebrew of the verse. |
| `diff` | Word-level diff of `masoretic` against `retroverted`: `[-MT only-]` and `{+Vorlage only+}`; a replacement is `[-old-]{+new+}`. Empty for an LXX-only row. |
| `brenton` | Brenton's English of the Septuagint verse. |
| `jps` | The JPS English of the Masoretic verse, without the `(3-2)` annotations. |
| `lxx_only` | `yes` for Greek material with no Masoretic counterpart. |
| `tov_markers` | The editorial markers found in the verse, for auditing a row whose retroversion is empty. |

### Size

- **12,951 rows**: 12,784 Masoretic verses and 167 LXX-only rows.
- 12,685 rows have Greek, 12,619 have Brenton, 12,777 have the JPS.
- 12,520 have a retroversion; 431 are flagged by a marker without a
  reconstructed text (the `tov_markers` column says which).

## Normalisation

The semantic normalisation (the expensive LLM step) is data, not part of
`build`. Two tables hold it, keyed by the English verse:

- `normalisation/jps.csv` — 11,969 of the 12,770 JPS verses in the dataset
  (93.7%), reused from the earlier Tessela run.
- `normalisation/lxx.csv` — 10,591 of the 12,551 Brenton verses (84.4%),
  re-anchored by matching the old text to the correct Brenton verse.

Each row is `ref, text, propositions`, where `propositions` is the JSON array of
atomic statements. The normalisation is reused only when the text is unchanged;
`./scripts/lxx-refs normalise` reports what is missing and, with
`--provider gemini`, normalises the gaps (it needs `google-generativeai` and
`GOOGLE_API_KEY`, and never runs unless asked).

### What remains to normalise

`normalisation/missing.csv` is the worklist. It is regenerated by
`./scripts/lxx-refs missing` and committed, so the gap is visible and does not
drift:

| Column | Description |
|:--|:--|
| `translation` | `jps` or `lxx`. |
| `ref` | The English verse to normalise (e.g. `PSA 3:1`, `JER 34:2`). |
| `text` | The exact English text the normalisation must cover. |
| `serves` | The Masoretic verse(s) in `tov_flagged.csv` that use this English verse; one JPS verse can serve several (Psalm titles). |
| `lxx_only` | `yes` when every verse it serves is an LXX-only addition. |

There are **2,761 rows**: 801 JPS and 1,960 Brenton. A trial run can be limited
with `./scripts/lxx-refs normalise --provider gemini --only lxx --limit 20`.

## The alignment gaps

The CATSS brackets cover almost every verse, but not all. The visible effect is
**71 rows with Greek but no Brenton verse** (of the 332 rows with no Brenton at
all, 261 are genuine LXX minuses and are correct). The 71 break down as follows.

**Fixable from STEPBible's TVTMS** (20 rows). The TVTMS file (`Versification/
TVTMS …`, CC BY 4.0) states the correspondence in its Ancient Versions column,
for example `Hebrew=115:12 • Greek=113:20` and `Hebrew=28:69 • Greek=29:1`:

| Group | Rows | Mapping |
|:--|--:|:--|
| Psalms | 9 | `10:16→9:37`, `18:40→17:40`, `27:13→26:13`, `107:31→106:31`, `115:12→113:20`, `115:16→113:24`, `115:17→113:25`, `115:18→113:26`, `136:23→135:23` |
| Nehemiah | 5 | `3:34→4:2`, `3:35→4:3`, `3:37→4:5`, `4:6→4:12`, `7:68→7:69` |
| Jeremiah | 3 | `29:26`, `44:23`, `46:10` (same coordinates) |
| Exodus | 2 | `38:31→39:9`, `39:40→39:19` |
| Deuteronomy | 1 | `28:69→29:1` |

**Not fixable from a verse crosswalk** (51 rows):

| Group | Rows | Why |
|:--|--:|:--|
| Proverbs 30–31 | 28 | Brenton's verse-per-line file has an empty `PRO 30:1` and only the acrostic at `31:10–31`; the LXX Words of Agur are not in that English source at all. |
| 1 Kings 3, 6, 9 | 8 | The LXX 3 Kingdoms moves the material (TVTMS records it as a LongVerse mapping, not a simple shift). |
| Daniel 3:67–70 | 4 | Brenton's VPL jumps from 3:66 to 3:71. |
| Jeremiah 23:7–8 | 2 | Tov's bracket says `[41]`, but Brenton has the material at `23:40a` / `23:40b`. |
| Ezekiel 11:11–12 | 2 | No simple Brenton counterpart. |
| Singles | 7 | Exodus 35:17, Joshua 24:33, 2 Samuel 23:31, 2 Chronicles 27:8, Nehemiah 12:41, Job 35:3, Lamentations 1:22 (the Greek adds 1:23). |

The variant itself is never lost: `greek`, `retroverted`, `masoretic` and
`diff` come from Tov's own word alignment. Only `brenton` — and therefore the
future semantic comparison — is affected. The options are:

1. **TVTMS fallback.** Commit the STEPBible file and parse the Ancient Versions
   column; apply it only when the CATSS bracket yields no Brenton verse, so
   Tov's explicit mapping always wins. This fixes the 20 rows above and gives a
   second source for future bracket gaps.
2. **A small curated override table** for Jeremiah 23:7–8 (→ 23:40a/40b) and
   1 Kings 9 (→ 10:22), reviewed line by line.
3. **Another English Septuagint** (e.g. NETS) for Proverbs 30, Daniel 3:67–70
   and the Greek pluses that Brenton does not translate — a licensing and
   sourcing decision, not a mapping one.
4. **A `lxx_ref_source` column** (`bracket`, `same-coordinate`, `tvtms`,
   `none`) so the confidence of every `lxx_ref` is visible in the dataset.

## Esther

The Greek Esther is a separate textual tradition, not a verse-for-verse
translation of the Masoretic text. The Tov parallel aligns it with the Hebrew at
the base-verse level, and the alignment is sound: **all 167 Tov verses match the
Leningrad Esther at the same coordinate with a character similarity of at least
0.95** (after removing points and spaces). The 155 Esther rows in the dataset
carry 154 JPS texts; the only one without is the LXX-only addition `ESG 1:1s`.

The Greek additions are mostly inside the base verse's Greek/Brenton text — the
whole prologue (`1:1a–s`) sits in `ESG 1:1`, compared with Masoretic Esther 1:1.
That is a legitimate "the Greek has a long addition here" row; one addition is
split out as its own LXX-only row.

The weak point is the **anchor of the additions**, not the JPS alignment. To make
the additions explicit:

- split the Greek Esther sub-verses into LXX-only rows with the standard
  Addition A–F labels (the prologue, `3:13a–g`, `4:17a–z`, `5:1a–f`,
  `8:12a–x`, `10:3a–k`); or
- keep them inside the base verse (the current form) and rely on `lxx_only`.

A dedicated Greek Esther ↔ Masoretic crosswalk would refine only those anchors;
the base text does not need it.

## The semantic comparison

**It is not included.** Tessela compared the JPS and LXX propositions with
Gemini, but that comparison was tied to the old, broken alignment — the JPS and
LXX texts in it are often not the same verse. It is not imported. The plan is to
redo the comparison with Jev, on the aligned pairs in this dataset.

## Rebuilding

The build needs only the standard library:

```bash
./scripts/lxx-refs build
./scripts/lxx-refs check
./scripts/lxx-refs missing
```

## Verification

- `pytest scripts/lxx/tests` — 14 tests: the `.par` reader, the JPS mapping,
  the LXX bracket, the word diff, the normalisation reuse, the canon check and
  a byte-for-byte rebuild of `tov_flagged.csv`.
- Every row is checked against the Leningrad canon; a duplicate or an empty
  row fails `check`.
- Spot checks that the three systems really meet:
  - Masoretic `Jer 27:2` → LXX `JER 34:2` (Brenton: "Make to thyself bonds and
    yokes"); JPS: "Make thee bands and bars".
  - Masoretic `Ps 10:1` → LXX `PSA 9:22`.
  - Masoretic `Dan 3:24` → LXX `DNG 3:91`; the Song of the Three is DNG
    3:24–90, marked LXX-only.
  - Masoretic `1Chr 1:6` — Dodanim in the MT, Riphath in the LXX, the
    retroversion `וריפת` and the diff show the change.

## Caveats

- 332 rows have no Brenton text: 261 are genuine LXX minuses and are correct;
  the other 71 are the alignment gaps above.
- 174 rows have no JPS text; almost all are LXX-only additions. The
  parenthetical Hebrew numbers in the JPS are the source of the map, and they
  do not cover every verse of every book.
- The Masoretic text is Tov's unpointed Hebrew; the single filled verse
  (Lamentations 1:1) is the Leningrad text with the points removed, so the diff
  compares like with like.
- The normalisations inherited from Tessela are partial (801 JPS and 1,960
  Brenton verses are still missing) and were produced by an earlier model. They
  are a starting point to save tokens, not an authority.

## Tests

```bash
.venv/bin/pytest scripts/lxx/tests
```
