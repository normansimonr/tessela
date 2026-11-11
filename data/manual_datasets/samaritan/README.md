# Samaritan Pentateuch variants

The curated list of Samaritan Pentateuch (SP) variant passages, with the SP
Hebrew text of those verses in the same file.

## Files

| File | Tracked? | Contents |
|---|---|---|
| `samaritan.csv` | yes | 33 variant passages (`book`, `chapter`, `verse`) |
| `data/derived/samaritan.csv` | no (git-ignored) | The same passages with their SP Hebrew text (`hebrew_text`) |

The reference list is tracked; the Hebrew text is non-commercial and is
generated locally by `make data-samaritan` (or
`python3 scripts/fetch_data.py samaritan`). The derived file is the single
source of truth for the enriched readings, and `src/witnesses.py` prefers it
when it exists. The Bible references and their order come from the tracked
list; only the `hebrew_text` column is added locally.

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
make data-samaritan
# or: python3 scripts/fetch_data.py samaritan
```

This seeds `data/derived/samaritan.csv` from the tracked reference list, then
runs `scripts/fetch_samaritan_sp.py`, which downloads the SP SWORD module from
CrossWire (or uses a cached `--zip`) and adds the `hebrew_text` column. It
requires `pysword` (see `requirements.txt`).

## Note on the variant list

`samaritan.csv` was compiled by the translator from an English translation of
the Samaritan Pentateuch: Florentin, Moshe, and Abraham Tal, *The Samaritan
Pentateuch: An English Translation with a Parallel Annotated Hebrew Text*
(Open Book Publishers, 2025), <https://doi.org/10.11647/OBP.0415>. It is a
subjective working list, not a complete apparatus.
