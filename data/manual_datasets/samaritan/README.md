# Samaritan Pentateuch variants

The curated list of Samaritan Pentateuch (SP) variant passages, together with
the SP Hebrew text of those verses.

## Files

| File | Contents |
|---|---|
| `samaritan.csv` | 33 variant passages (references only) |
| `samaritan_hebrew.csv` | The SP Hebrew text for those 33 verses |

## Source and credit

The SP Hebrew text in `samaritan_hebrew.csv` comes from the **STEPBible SP
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
module. The `osis` column preserves the raw OSIS markup (Strong's numbers,
glosses and transliteration) for provenance and auditability.

## Rebuilding

```bash
python3 scripts/fetch_samaritan_sp.py
```

The script downloads the SP SWORD module from CrossWire (or uses a cached
`--zip`), reads the references in `samaritan.csv`, and rewrites
`samaritan_hebrew.csv`. It requires `pysword` (see `requirements.txt`).

## Note on the variant list

`samaritan.csv` was compiled by the translator from an English translation of
the Samaritan Pentateuch: Florentin, Moshe, and Abraham Tal, *The Samaritan
Pentateuch: An English Translation with a Parallel Annotated Hebrew Text*
(Open Book Publishers, 2025), <https://doi.org/10.11647/OBP.0415>. It is a
subjective working list, not a complete apparatus.
