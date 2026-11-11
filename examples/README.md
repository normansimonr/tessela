# Example dossiers

The full dossiers include Samaritan and Dead Sea Scrolls readings. Those
datasets are non-commercial and are **not tracked** (see
[`DATA_LICENSES.md`](../DATA_LICENSES.md)), so the rendered dossiers are
generated into the git-ignored `data/derived/examples/` rather than committed.

```bash
make data       # fetch the non-commercial datasets into data/derived/
make examples   # render DEU 32:8, GEN 2:2 and DEU 27:4
```

Or render one directly:

```bash
./scripts/tessela dossier "DEU 32:8"
./scripts/tessela dossier "GEN 2:2" --format text
./scripts/tessela dossier "DEU 27:4" --out /tmp/deu-27-4.md
```

The README shows a short terminal excerpt; the full Markdown dossiers add the
readings by witness, the normalised differences, and provenance.
