# Textual criticism datasets

The translation is made from the Masoretic Text. Where another textual witness
carries a different reading that could change how a verse is translated, the
passage is recorded here so that the translator can weigh the evidence. The
variant lists (`samaritan.csv`, `qumran.csv`, `masoretic_minority.csv`) record
**verse references**, and two of them also carry the witness's Hebrew text:
`samaritan.csv` has the Samaritan Pentateuch text in `hebrew_text` (see
[`samaritan/README.md`](samaritan/README.md)), and `qumran.csv` has the Dead Sea
Scrolls readings, one row per (passage, scroll), in `scroll`, `hebrew_text` and
`transcription` (see [`qumran/README.md`](qumran/README.md)).

These three datasets are hand-maintained — nothing generates them and nothing
checks them yet. They are the translator's working list, which Milestone 4 of the
roadmap ([`SPECS/ROADMAP.md`](../SPECS/ROADMAP.md)) will build on when the Old
Testament variants are brought into the content.

## Datasets

| File | Witness | Entries |
|:--|:--|--:|
| `samaritan.csv` | Samaritan Pentateuch (Genesis–Deuteronomy), with SP Hebrew text | 33 |
| `qumran.csv` | Qumran — the Dead Sea Scrolls, with Hebrew readings | 125 passages / 199 rows |
| `masoretic_minority.csv` | Minority readings within the Masoretic tradition itself | 1 (in progress) |

### How the datasets were made

All three datasets were compiled **manually by the translator**. The Samaritan
and Qumran lists were made by reading published English translations of the two
witnesses:

- **Samaritan Pentateuch** — Florentin, Moshe, and Abraham Tal. *The Samaritan
  Pentateuch: An English Translation with a Parallel Annotated Hebrew Text.*
  1st edn. Vol. 30. Semitic Languages and Cultures. Open Book Publishers, 2025.
  <https://doi.org/10.11647/OBP.0415>.
- **Qumran** — Abegg, Martin, Peter Flint, and Eugene Ulrich. *The Dead Sea
  Scrolls Bible: The Oldest Known Bible Translated for the First Time into
  English.* HarperOne, 1999.

For each witness the translator recorded the reference of every variant that
seemed likely to be of translational interest. The selection is **subjective**:
it is a working list for the translator, not a complete critical apparatus, and
a passage absent from these files is not thereby free of variants.

`masoretic_minority.csv` was also compiled manually by the translator, from
Abegg et al., *The Dead Sea Scrolls Bible* — the same translation listed above
for Qumran. It records minority readings within the Masoretic tradition itself
and is still in its infancy — one entry so far.

## Qere/Ketiv variants

The [`qere_ketiv/`](qere_ketiv/README.md) subfolder holds a fourth dataset, of a
different kind: the passages where the Masoretic text's *ketiv* (what is
written) differs from its *qere* (what is read), sorted by whether the
difference is lexical or merely grammatical. It is not hand-compiled — it is
derived mechanically from STEPBible's Translators Amalgamated Hebrew OT (TAHOT,
CC BY 4.0) by `scripts/qere-ketiv`. The subfolder's README documents the
pipeline, the files and how to rebuild them.

## CTAT and HOTTP references

The [`ctat/`](ctat/README.md) subfolder records **where the textual criticism
is discussed**, rather than the readings themselves: the verses treated in
Barthélemy's *Critique textuelle de l'Ancien Testament* (with the volume and
page) and in the *Hebrew Old Testament Text Project* reports. Its `refs.csv`
has one row per verse — 3,348 in all, covering the whole Old Testament, since
CTAT treats everything but the Pentateuch and HOTTP treats the Pentateuch. The
data is recovered from the volume PDFs by `scripts/ctat-refs`; the subfolder's
README explains the OCR pipeline and how to rebuild it.

## Septuagint variants

The [`septuagint/`](septuagint/README.md) subfolder holds the verses where the
Septuagint probably reflects a Hebrew Vorlage different from the Masoretic Text,
following Emmanuel Tov's CATSS word alignment. Its `tov_flagged.csv` has one row
per verse — 12,951 in all, 167 of them Greek-only additions — with Tov's Greek,
his reconstructed Hebrew, the Masoretic text, a word-level diff, Brenton's
English and the JPS. The three numbering systems are bridged from the sources
themselves: Tov's `[34.2]` brackets give the LXX verse, the JPS `(3-2)`
annotations give the Hebrew verse. The subfolder's README explains the pipeline,
the normalisation tables and the known alignment gaps.

## Schema

The three hand-maintained files share the same shape: one row per variant passage.

| Column | Type | Description |
|:--|:--|:--|
| `book` | string | Full English book name, as in `data/reference/books.yaml` (e.g. `Genesis`, `1 Samuel`, `Psalms`) |
| `chapter` | integer | Chapter number |
| `verse` | integer | Verse number |

The files are UTF-8 with LF line endings, a header row and quoted book names
(`"Genesis",41,16`). Entries are grouped by book and, within each book, kept in
chapter and verse order; add new entries accordingly.
