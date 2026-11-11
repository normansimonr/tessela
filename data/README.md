# Data directory

This directory holds the raw, intermediate, and manual datasets used by
Tessela. The textual-criticism datasets below were consolidated from an earlier
textual-criticism dataset collection. Their subfolder READMEs are retained and
document the original pipelines; some paths in those READMEs still refer to the
original layout rather than Tessela's `data/` layout (the mapping is given
below).

## Layout

```
data/
├── raw/                          # Raw source data
│   ├── eng-Brenton_vpl/          # Brenton LXX (English, ebible.org)
│   ├── engDRA_vpl/               # Douay–Rheims Vulgate (English)
│   ├── engjps_vpl/               # JPS 1917 (English)
│   └── LXX_Tov/                  # Tov CATSS .par files (42; git-ignored, local only)
├── intermediate_datasets/        # Processed datasets
│   ├── tov.csv                   # Tov word-level alignment (legacy)
│   ├── tov_distilled.csv         # Tov verse-level boolean flag (legacy)
│   └── septuagint/               # Septuagint variant corpus
│       ├── tov_flagged.csv       # One row per LXX variant (12,951)
│       ├── normalisation/        # Semantic normalisations (jps/lxx/missing)
│       └── README.md
├── manual_datasets/              # Hand-compiled / derived textual-criticism data
│   ├── qumran/                   # Dead Sea Scrolls variants + Hebrew readings
│   ├── samaritan/                # Samaritan Pentateuch variants + Hebrew text (33)
│   ├── masoretic_minority/       # Minority readings within MT (1)
│   ├── qere_ketiv/               # Qere/Ketiv dataset (from STEPBible TAHOT)
│   └── ctat/                     # CTAT/HOTTP references + OCR pipeline
├── reference/                    # Reference tables
│   ├── books.yaml                # Book catalog (canonical IDs, order, testament)
│   └── versification/
│       └── leningrad_codex.csv   # Leningrad codex verse text (Hebrew)
└── sqlite/                       # SQLite database (bible.db) and views
```

## Imported datasets

| Dataset | Original source | Tessela location | Rows | Notes |
|---|---|---|---|---|
| Dead Sea Scrolls variants | `textual_criticism/qumran.csv` | `manual_datasets/qumran/qumran.csv` | 125 passages / 199 rows | One row per (passage, scroll) reading: `scroll`, `hebrew_text`, `transcription`; readings from ETCBC/dss 2.0.5 (credited in `qumran/README.md`) |
| Samaritan Pentateuch variants | `textual_criticism/samaritan.csv` | `manual_datasets/samaritan/samaritan.csv` | 33 | `book`, `chapter`, `verse`, `hebrew_text`; SP Hebrew text from STEPBible SP (credited in `samaritan/README.md`) |
| Masoretic minority readings | `textual_criticism/masoretic_minority.csv` | `manual_datasets/masoretic_minority/masoretic_minority.csv` | 1 | In progress |
| Qere/Ketiv | `textual_criticism/qere_ketiv/` | `manual_datasets/qere_ketiv/` | 1,013 words / 837 verses | Richer than the previous Tessela dataset: readings, transliteration, gloss, root, Strong's, morphology, variant type, proper-name flag |
| CTAT/HOTTP references | `textual_criticism/ctat/` | `manual_datasets/ctat/` | 3,348 verses | Adds `refs.csv` (one row per verse with HOTTP flag and CTAT page) and README |
| Septuagint variants (Tov) | `textual_criticism/septuagint/` | `intermediate_datasets/septuagint/` | 12,951 | Greek, retroverted Hebrew, Masoretic, word diff, Brenton, JPS, LXX-only flag, Tov markers |
| Tov CATSS `.par` files | `textual_criticism/septuagint/raw/LXX_Tov/` | `raw/LXX_Tov/` | 42 files | Word-level Hebrew/Greek alignment; **git-ignored** (`*.par`) per the repository's licensing policy, so present locally only |
| Septuagint normalisations | `textual_criticism/septuagint/normalisation/` | `intermediate_datasets/septuagint/normalisation/` | ~25k | Atomic propositions for JPS and LXX |
| Leningrad codex text | `references/standards/versification/leningrad_codex.csv` | `reference/versification/leningrad_codex.csv` | 23,213 | Hebrew verse text (unpointed/pointed) |
| Book catalog | `meta/books.yaml` | `reference/books.yaml` | 66 books | Canonical IDs, order, testament, names |

## Provenance and licensing

- **Dead Sea Scrolls / Samaritan / Masoretic minority lists** were compiled
  manually by the translator from published English translations:
  - Samaritan: Florentin & Tal, *The Samaritan Pentateuch: An English
    Translation with a Parallel Annotated Hebrew Text* (Open Book Publishers,
    2025), <https://doi.org/10.11647/OBP.0415>.
  - Qumran: Abegg, Flint & Ulrich, *The Dead Sea Scrolls Bible* (HarperOne,
    1999).
  - These are **working lists**; the selection is subjective and not a complete
    critical apparatus.
- **Dead Sea Scrolls Hebrew readings** (the `scroll`, `hebrew_text` and
  `transcription` columns of `qumran/qumran.csv`) come from the **CACCHT Dead
  Sea Scrolls dataset** (<https://github.com/ETCBC/dss>), Text-Fabric version
  2.0.5, based on Martin Abegg's data and prepared by Jarod Jacobs, Martijn
  Naaijer and Dirk Roorda. Licence: **CC BY-NC 4.0**. See
  `manual_datasets/qumran/README.md`.
- **Samaritan Pentateuch Hebrew text** (the `hebrew_text` column of
  `samaritan/samaritan.csv`) is from the **STEPBible SP version**
  (<https://www.stepbible.org/version.jsp?version=SP>), a SWORD module
  distributed by CrossWire (<https://www.crosswire.org/sword/>), digitized and
  prepared by **Aleksandr Sigalov** from Kennicott (1780) and von Gall (1918).
  Licence: "Copyrighted; Free non-commercial distribution". See
  `manual_datasets/samaritan/README.md`.
- **Qere/Ketiv** is derived from STEPBible's *Translators Amalgamated Hebrew OT*
  (TAHOT), CC BY 4.0. The four raw TAHOT files are not tracked here (STEPBible
  asks that they be distributed from its own repository); only the derived
  datasets are tracked.
- **CTAT/HOTTP** references are derived from Dominique Barthélemy's *Critique
  textuelle de l'Ancien Testament* (OBO 50) and the *Hebrew Old Testament Text
  Project* reports. The copyrighted CTAT PDFs are not tracked; only page
  references are.
- **Septuagint**: Tov's CATSS `.par` files are present locally in
  `raw/LXX_Tov/` but are **not tracked** (`.gitignore` excludes `*.par` because
  they are not in the public domain); Brenton and JPS English texts are public
  domain (ebible.org).
- **Leningrad codex** verse text is used for versification/alignment reference.

See each subfolder's `README.md` for the detailed pipeline and caveats.

## Notes on paths

The imported subfolder READMEs describe the original layout:

| Original path | Tessela path |
|---|---|
| `textual_criticism/qumran.csv` | `data/manual_datasets/qumran/qumran.csv` |
| `textual_criticism/samaritan.csv` | `data/manual_datasets/samaritan/samaritan.csv` |
| `textual_criticism/masoretic_minority.csv` | `data/manual_datasets/masoretic_minority/masoretic_minority.csv` |
| `textual_criticism/qere_ketiv/` | `data/manual_datasets/qere_ketiv/` |
| `textual_criticism/ctat/` | `data/manual_datasets/ctat/` |
| `textual_criticism/septuagint/` | `data/intermediate_datasets/septuagint/` |
| `references/standards/versification/` | `data/reference/versification/` |
| `data/reference/books.yaml` | `data/reference/books.yaml` |

The generator scripts were imported and adapted to Tessela's
`data/` layout:

| Script | Rebuilds | Inputs |
|---|---|---|
| `scripts/qere-ketiv` | `manual_datasets/qere_ketiv/` | STEPBible TAHOT files (not tracked) |
| `scripts/ctat-refs` | `manual_datasets/ctat/refs.csv` (and OCR stages) | `urls.csv`, `header_coordinates.csv`, `HOTTP-PENTATEUCH.txt` |
| `scripts/lxx-refs` | `intermediate_datasets/septuagint/tov_flagged.csv` and normalisations | `raw/LXX_Tov/*.par`, `raw/eng-*/…txt`, `reference/versification/leningrad_codex.csv` |

The underlying modules live in `scripts/lxx/`, `scripts/ctat/` and
`scripts/qere_ketiv/`; each has tests. Verified against the imported snapshots:

- `./scripts/lxx-refs build --out /tmp/tov_flagged.csv` reproduces
  `tov_flagged.csv` byte-for-byte.
- `./scripts/ctat-refs refs --out /tmp/refs.csv` reproduces `refs.csv`.
- The Qere/Ketiv analyser reproduces the four checked-in CSVs from
  `OT-QK.tsv` + `lemmas.tsv` (covered by `scripts/qere_ketiv/tests`).

The previous Tessela Qere/Ketiv scripts (`qk_analyzer.py`,
`verse_consolidator.py`, `qk_extractor.sh`) were moved to
`manual_datasets/qere_ketiv/legacy/` so they cannot overwrite the richer
enriched dataset.
