# Qumran (Dead Sea Scrolls) variants

The curated list of Dead Sea Scrolls (DSS) variant passages, with the Hebrew
readings of the scrolls that attest each passage.

## File

| File | Contents |
|---|---|
| `qumran.csv` | One row per (passage, scroll) reading: `book`, `chapter`, `verse`, `scroll`, `hebrew_text`, `transcription` |

The list contains **125 distinct passages**; because a passage may be attested
in more than one scroll, the file has **199 rows** (195 readings plus 4
passages that are not present in the source dataset). To recover the passage
list, use `SELECT DISTINCT book, chapter, verse`.

- `scroll` — the manuscript siglum as used by the dataset (e.g. `4Q9`,
  `1Qisaa`).
- `hebrew_text` — the clean consonantal text (editorial brackets and markers
  removed; the ETCBC word division is preserved).
- `transcription` — the full ETCBC transcription, which preserves editorial
  markers: `[ ]` for reconstructed text, `(^ ... ^)` for uncertain readings,
  `#` for damaged text, and `׳` for morpheme boundaries.

## Source and credit

The Hebrew readings come from the **CACCHT Dead Sea Scrolls dataset**:

- Repository: <https://github.com/ETCBC/dss> (Text-Fabric format, version
  2.0.5).
- The transcriptions are based on **Martin Abegg's** data and were prepared by
  **Jarod Jacobs, Martijn Naaijer and Dirk Roorda** as part of the CACCHT
  project.
- Licence: **Creative Commons Attribution-NonCommercial 4.0 International
  (CC BY-NC 4.0)**. Use for research; do not use commercially.
- The dataset is **not vendored** in this repository (it is large). To rebuild
  the CSV, clone it first:

  ```bash
  git clone --depth 1 https://github.com/ETCBC/dss.git /path/to/ETCBC-dss
  python3 scripts/fetch_qumran_dss.py --dss-dir /path/to/ETCBC-dss
  ```

  The script requires `text-fabric` (see `requirements.txt`).

## Missing passages

The following curated passages are **not present** in the ETCBC/dss 2.0.5
dataset, so their `scroll`, `hebrew_text` and `transcription` fields are empty:

- Exodus 22:5
- Habakkuk 1:17
- Psalms 91:2
- Psalms 91:4

Their absence means the dataset does not contain a transcribed reading for
those verses; it is not a claim that no DSS evidence exists.

## Note on the variant list

`qumran.csv` was compiled by the translator from an English translation of the
Dead Sea Scrolls: Abegg, Martin, Peter Flint, and Eugene Ulrich, *The Dead Sea
Scrolls Bible: The Oldest Known Bible Translated for the First Time into
English* (HarperOne, 1999). It is a subjective working list, not a complete
critical apparatus.
