# Data licences

The **source code** in this repository is released under the MIT License (see
[`LICENSE`](LICENSE)). The **datasets** are separate works with their own
terms. This file records them so that the code licence is not mistaken for a
data licence.

| Dataset | Files | Source | Licence / terms |
|---|---|---|---|
| Masoretic Text (Leningrad Codex) | `data/reference/versification/leningrad_codex.csv` | Leningrad Codex, via the ETCBC/SOFER ecosystem | Public-domain text; the digital transcription is a factual representation of a public-domain manuscript |
| Samaritan Pentateuch | `data/derived/samaritan.csv` (git-ignored; the tracked `samaritan.csv` is references only) | STEPBible SP version, a SWORD module distributed by CrossWire; digitized and prepared by Aleksandr Sigalov from Kennicott (1780) and von Gall (1918) | **“Copyrighted; Free non-commercial distribution”** (module configuration). Research use only; commercial use requires permission |
| Dead Sea Scrolls | `data/derived/qumran.csv` (git-ignored; the tracked `qumran.csv` is references only) | CACCHT Dead Sea Scrolls dataset, <https://github.com/ETCBC/dss>, v2.0.5; based on Martin Abegg’s data; prepared by Jarod Jacobs, Martijn Naaijer and Dirk Roorda | **CC BY-NC 4.0** (Attribution-NonCommercial 4.0 International) |
| Qere/Ketiv | `data/manual_datasets/qere_ketiv/` | STEPBible *Translators Amalgamated Hebrew OT* (TAHOT), <https://github.com/STEPBible/STEPBible-Data> | **CC BY 4.0** (Attribution 4.0 International). The raw TAHOT files are not tracked; only derived datasets are |
| Septuagint (Tov/CATSS) | `data/derived/septuagint/` (git-ignored); `data/raw/LXX_Tov/` (git-ignored) | Tov’s CATSS project, <https://ccat.sas.upenn.edu/rak/catss.html>; Brenton and JPS English texts from ebible.org | The CATSS `.par` files are **not tracked** (`*.par` is git-ignored); derived tables are research data. Brenton (LXX) and JPS (MT) English texts are public domain |
| Vulgate | `data/sqlite/engDRA_vpl.sql`, `data/raw/engDRA_vpl/` | Douay–Rheims Bible, ebible.org | Public domain |
| CTAT / HOTTP references | `data/manual_datasets/ctat/` | Dominique Barthélemy, *Critique textuelle de l’Ancien Testament* (OBO 50); *Hebrew Old Testament Text Project* reports | **Page references only**; the copyrighted CTAT PDFs are not tracked. The HOTTP text is included for research; verify reuse terms with the publisher before redistribution |
| Book catalog | `data/reference/books.yaml` | Project metadata (book names, canonical order, testament) | Factual metadata; no creative text from a single copyrighted source |

## Notes

- **Non-commercial datasets are not tracked.** The Samaritan Pentateuch and
  Dead Sea Scrolls datasets are non-commercial, so only their reference lists
  are committed; the readings are fetched locally into `data/derived/` by
  `make data` and are git-ignored. If you intend to use this repository (or its
  data) commercially, obtain permission from CrossWire/STEPBible and the
  ETCBC/dss rights holders first, or replace those datasets with sources whose
  terms permit your use.
- **Attribution.** When reusing the data, retain the citations above. In
  particular, cite the ETCBC/dss dataset and its authors, and the STEPBible SP
  module and Aleksandr Sigalov’s transcription.
- **Code vs. data.** The MIT licence applies to the code in `src/`, `scripts/`,
  and the configuration files. It does not grant rights to the datasets.
- **Tov’s CATSS files.** The `.par` files are deliberately excluded from Git
  (`.gitignore` contains `*.par`) because they are not in the public domain.
