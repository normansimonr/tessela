# CTAT and HOTTP references

Where the great textual-criticism handbooks discuss a verse, this dataset says
so: one row per Old Testament verse, with a flag for the *Hebrew Old Testament
Text Project* (HOTTP) and the volume and page of Barthélemy's *Critique
textuelle de l'Ancien Testament* (CTAT).

The two works complement each other almost exactly. CTAT covers the Old
Testament **except the Pentateuch**, in five volumes; the HOTTP report in this
repository is the **Pentateuch** volume. Together they cover the whole Old
Testament: 3,348 verses, 658 from HOTTP and 2,690 from CTAT.

## Sources

**CTAT** — Dominique Barthélemy, *Critique textuelle de l'Ancien Testament*,
Orbis Biblicus et Orientalis 50, 5 volumes. The digitised volumes are published
by the University of Zurich's open repository (ZORA); `urls.csv` lists the five
PDFs the pipeline downloads (about 161 MB). The volumes are copyrighted, so the
PDFs are **not tracked** here — only the page references derived from them.

**HOTTP** — the *Hebrew Old Testament Text Project* preliminary and interim
reports. `HOTTP-PENTATEUCH.txt` is the Pentateuch volume as text, in which each
discussion is anchored to a verse with a BibleBHS link
(`[[@BibleBHS:GEN 1:1]]`).

## Files

| File | Kind | What it is |
|:--|:--|:--|
| `urls.csv` | input | The five CTAT volume PDFs (volume number and URL). |
| `header_coordinates.csv` | input | Per volume, the pixel box that crops the running head (separate boxes for even and odd pages). |
| `HOTTP-PENTATEUCH.txt` | input | The HOTTP Pentateuch report; the references are its BibleBHS links. |
| `ocr_results.csv` | stage 2 output | One row per page: the OCR of the running-head crop (`volume, page, text, pagina`). 4,330 page rows. |
| `ocr_clean.csv` | stage 3 output | The cleaned data: one row per reference (`volume, pagina, book, value`). 2,705 rows. |
| `refs.csv` | stage 4 output | **The dataset**: one row per verse, with the HOTTP flag and the CTAT page. |

## The pipeline

The pipeline was recovered from the translator's earlier repository and adapted
to run here. One command runs it all:

```bash
./scripts/ctat-refs all --pdfs ~/data/ctat-pdfs
```

The stages are described below.

### 1. Download (`scripts/ctat download`)

Reads `urls.csv` and fetches each volume PDF into the cache directory
(`output/ctat/pdfs/` by default, gitignored). Existing files are kept.

### 2. Headers (`scripts/ctat extract`)

Each page of each volume is rendered at **300 dpi** with PyMuPDF, and the strip
that holds the running head is cropped and OCR'd with tesseract. The crop box
depends on the volume and on whether the page is odd or even, because the head
sits on the outer edge of the page; the boxes are the ones in
`header_coordinates.csv`, in pixels at 300 dpi:

| Volume | Even pages (x0–x1) | Odd pages (x0–x1) | y0–y1 |
|--:|:--|:--|:--|
| 1 | 600–1050 | 600–1050 | 0–220 |
| 2 | 570–970 | 650–1140 | 0–163 |
| 3 | 150–730 | 1000–1600 | 0–183 |
| 4 | 600–1150 | 600–1150 | 0–200 |
| 5 | 940–1450 | 940–1450 | 230–480 |

The result is `ocr_results.csv`: the OCR text of every page, with the page
number of the PDF. Pages without a running head (front matter, chapter
openers) OCR to body text and are dropped by the next stage.

The run can be narrowed for a check: `--volumes 4 --pages 100-110`.

### 3. Clean (`scripts/ctat clean`)

The OCR text is not yet a reference. The cleaning stage:

- drops pages whose OCR text repeats an earlier one;
- rewrites the OCR confusions recorded in the correction table in
  `scripts/ctat/pipeline.py` — the French abbreviations and the Latin/numeral
  slips (`I S` / `1$`, `II R` / `WS`, `Ir` / `Jr`, `MI` / `Mal`, ...);
- splits a running head that names several references on `/` (`Jos 15,9/18,15`);
- separates the book from the verse list, removes witness sigla (`13A-C` is
  verse 13) and parentheses (`Ps 12,8(7)` is Psalm 12:8 in the Hebrew
  numbering);
- turns the comma into the chapter/verse separator, giving `ocr_clean.csv` with
  one row per reference (`volume, pagina, book, value`).

The correction table is deliberately literal: each entry records an OCR error
seen in these volumes.

### 4. References (`scripts/ctat-refs refs`)

`scripts/ctat/refs.py` reads the cleaned CTAT rows and the HOTTP text and
combines them:

- CTAT values are expanded into verses: `2:4` is one verse; `28:1:4` and
  `4:5 &9` list verses (the running heads use `.` and `&` for lists, not
  ranges); `3:1-3` is a range;
- the HOTTP references are the `[[@BibleBHS:…]]` links in the text;
- every reference is checked against the Hebrew versification canon in
  `data/reference/versification/leningrad_codex.csv`, and the eight OCR
  slips that name a verse the canon does not have are dropped (the run logs
  them: `2SA 21:64`, `2CH 28:28`, `JER 17:30`, `17:48`, `27:38`, `48:54`,
  `LAM 1:144`, `EZE 47:94`);
- the two sources are merged, the books sorted in canonical order, and
  `refs.csv` is written.

## `refs.csv`

One row per verse:

| Column | Description |
|:--|:--|
| `book` | Canonical book ID, as in `data/reference/books.yaml` (e.g. `GEN`, `JOS`, `PSA`) |
| `chapter`, `verse` | the verse, in Hebrew versification |
| `hottp` | `yes` when the HOTTP report discusses the verse |
| `ctat_volume` | the CTAT volume, `1`–`5` (empty when the verse is HOTTP only) |
| `ctat_page` | the page of that volume's PDF on which the reference appears; several pages are comma-separated |

`ctat_page` is the **page of the PDF**, as produced by the pipeline, not the
volume's printed page number. The CTAT abbreviations map to the canonical IDs as
follows (the French forms): `1S`/`2S` → `1SA`/`2SA`, `1R`/`2R` → `1KI`/`2KI`,
`Esd` → `EZR`, `Is` → `ISA`, `Jr` → `JER`, `Ez` → `EZE`, `Dn` → `DAN`,
`Os` → `HOS`, `Jl`/`JI` → `JOE`, `Ab` → `OBA`, `Jon` → `JON`, `Mi` → `MIC`,
`Na` → `NAH`, `Ha` → `HAB`, `So` → `ZEP` (Sophonie), `Ag` → `HAG`,
`Za` → `ZEC`, `Mal` → `MAL`, `Ps` → `PSA`, `Jb` → `JOB`, `Pr` → `PRO`,
`Qo` → `ECC`, `Ct` → `SON` (Cantique); the rest are self-evident.

## Rebuilding

The OCR stages need the optional `ctat` dependency group and the system
`tesseract` binary:

```bash
.venv/bin/pip install -e '.[ctat]'
```

The five PDFs are 161 MB, and a full OCR run of 5,335 pages takes roughly
30–45 minutes on a laptop:

```bash
./scripts/ctat-refs all --pdfs ~/data/ctat-pdfs
```

To rebuild only the dataset from the tracked OCR snapshot (seconds):

```bash
./scripts/ctat-refs refs
```

## Verification

- The cleaning stage reproduces the tracked `ocr_clean.csv` **byte for byte**
  from the tracked `ocr_results.csv`.
- A fresh OCR of sampled pages matches the tracked snapshot exactly — volumes
  2, 4 and 5, pages 100–102 (`Is 1,17`, `Ps 12,8(7)`, `Jb 11,10`, …) — and
  volumes 1 and 3, pages 100–102 are front matter, which is why the snapshot
  has no rows for them.
- `refs.csv` rebuilds byte-identically, and every row is checked against the
  canon by the test suite.

## Caveats

- OCR is imperfect. The cleaning rules fix the errors that were seen; a header
  the OCR mangled beyond recognition is lost (a few dozen of the 2,705 rows).
- A verse discussed on several pages keeps every page, comma-separated.
- CTAT discusses verses, not every verse: 2,690 of the Old Testament's verses
  have a discussion. The absence of a row means no discussion was found, not
  that the text is certain.
- The PDFs are not tracked (copyright and size); `urls.csv` is the permanent
  pointer to them.

## Tests

```bash
.venv/bin/pytest scripts/ctat/tests
```
