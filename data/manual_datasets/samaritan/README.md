# Samaritan Pentateuch variants

The curated list of Samaritan Pentateuch (SP) variant passages, with the SP
Hebrew text of those verses in the same file.

## File

| File | Contents |
|---|---|
| `samaritan.csv` | 33 variant passages (`book`, `chapter`, `verse`) with their SP Hebrew text (`hebrew_text`) |

One row per variant passage; the reference list and its Hebrew text share a
single source of truth.

## Source and credit

The SP Hebrew text in the `hebrew_text` column comes from the **STEPBible SP
version**:

- STEPBible: <https://www.stepbible.org/version.jsp?version=SP>
- The text is distributed as a SWORD module by CrossWire
  (<https://www.crosswire.org/sword/>), module `SP`, version 1.2.
- The module is titled *Samaritan Pentateuch with Morphology, Transliteration,
  Strongs Concordance Numbers and Idiomatic Translation* and was **digitized
  and prepared by Aleksandr Sigalov**.
- Its base text is Benjaminus Kennicott, *Vetus Testamentum Hebraicum cum
  variis lectionibus* (1780), manually compared with August Freiherr von Gall,
  *Der Hebräische Pentateuch der Samaritaner* (Giessen, 1918).
- Distribution licence (from the module configuration): **"Copyrighted; Free
  non-commercial distribution"**. Use for research; do not redistribute
  commercially.

The `hebrew_text` column is the clean, unpointed Hebrew text as read from the
module. The module's raw OSIS markup (Strong's numbers, glosses and
transliteration) can be read with `pysword` if needed, but is not stored here.

## Rebuilding

```bash
python3 scripts/fetch_samaritan_sp.py
```

The script downloads the SP SWORD module from CrossWire (or uses a cached
`--zip`), reads the references in `samaritan.csv`, and updates the
`hebrew_text` column in place. It requires `pysword` (see `requirements.txt`).

## Note on the variant list

`samaritan.csv` was compiled by the translator from an English translation of
the Samaritan Pentateuch: Florentin, Moshe, and Abraham Tal, *The Samaritan
Pentateuch: An English Translation with a Parallel Annotated Hebrew Text*
(Open Book Publishers, 2025), <https://doi.org/10.11647/OBP.0415>. It is a
subjective working list, not a complete apparatus.
