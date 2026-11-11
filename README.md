# ⚠️ Work in Progress (WIP)

> **This project is under active development.** The codebase, data model, and
> pipeline are being refactored to align with the expanded mission in
> `SPECS/MISSION.md`. APIs, scripts, and database schemas may change without
> notice. See `SPECS/ROADMAP.md` for the current delivery plan.

# Tessela — Biblical Text Normalizer & Textual Criticism Research Assistant

Tessela is a research and decision-support system for the textual criticism of
the Hebrew Bible. It helps a translator or researcher evaluate a large body of
textual evidence efficiently, transparently, and consistently.

Its purpose is to automate a substantial part of the work involved in
identifying, organizing, comparing, and evaluating textually significant
variants — while keeping scholarly judgment, uncertainty, and traceability at
the centre of the process.

## Overview

Tessela brings together readings from the Masoretic Text and other ancient
witnesses (Qere/Ketiv, Samaritan Pentateuch, Dead Sea Scrolls, Septuagint,
Vulgate, Peshitta), relevant scholarly discussion (Barthélemy's CTAT and
open-access papers), explicit hypotheses about the development of the text, and
structured AI-assisted analysis. It helps the researcher understand what the
evidence may indicate, why competing explanations are plausible, and how
strongly each conclusion is supported.

Tessela is a **research assistant, not an autonomous textual critic**. It must
not conceal uncertainty, manufacture evidence, or present an AI-generated
reconstruction as an attested reading.

## Current state

The project is in an early stage. What exists today:

- **Data ingestion**: Masoretic Text (JPS 1917 English), Septuagint (Brenton
  English + Tov's Hebrew retroversions), Vulgate (Douay–Rheims English),
  Qere/Ketiv extraction from STEP-Bible TAHOT, CTAT OCR pipeline.
- **Semantic normalization**: Gemini-based decomposition of verses into atomic
  propositions.
- **Semantic comparison**: verse-by-verse comparison of normalized propositions
  (MT vs. LXX).
- **SQLite database** (`data/sqlite/bible.db`): English translations with
  alignment views.
- **Manual datasets**: Qere/Ketiv analysis, Samaritan Pentateuch verse list,
  CTAT OCR results.

See `SPECS/ROADMAP.md` for what is planned and `SPECS/MISSION.md` for the full
vision.

## Architecture

The project follows a **pipeline-driven** architecture (see `SPECS/TECH.md`).
Each stage takes a SQLite database from the previous stage and produces a new
one:

```
Stage 0: Ingestion    → tessela_0_raw.db
Stage 1: Alignment    → tessela_1_aligned.db
Stage 2: Normalization → tessela_2_normalised.db
Stage 3: Comparison   → tessela_3_compared.db
Stage 4: Scholarly    → tessela_4_sourced.db
Stage 5: Hypotheses   → tessela_5_hypotheses.db
Stage 6: Adversarial  → tessela_6_assessed.db
Stage 7: Dossiers     → research dossiers (Markdown/PDF)
```

> **Note:** The pipeline is currently being refactored. The existing scripts
> operate on CSV files and a single `bible.db`. Stage-gated SQLite outputs are
> planned but not yet implemented.

## Project structure

```
tessela/
├── data/                  # Input/raw/intermediate datasets
│   ├── raw/               # Raw source files (ebible.org SQL, Tov's data)
│   ├── intermediate_datasets/  # Processed datasets (tov_distilled.csv, etc.)
│   ├── manual_datasets/   # Qere/Ketiv, Samaritan, CTAT OCR
│   └── sqlite/            # SQLite database (bible.db) and SQL views
├── output/                # Normalized CSV output (generated)
├── comparisons/           # Comparison CSV output (generated)
├── prompts/               # AI prompt templates
│   ├── normalization_prompt.txt
│   └── comparison_prompt.txt
├── src/                   # Python source code
│   ├── data_loader.py
│   ├── normalization_service.py
│   ├── utils.py
│   └── tov_processor/     # Tov LXX retroversion processing
├── scripts/               # Executable pipeline scripts
│   ├── run_normalization.py
│   └── run_comparison.py
├── SPECS/                 # Mission, tech spec, roadmap, feature specs
├── run.sh                 # Run normalization pipeline
├── compare.sh             # Run comparison pipeline
├── prepare_database.sh    # Build bible.db from raw data
└── requirements.txt       # Python dependencies
```

## Prerequisites

- Python 3.11+
- A Google AI API key with access to the Gemini model.
- `sqlite3` (for database preparation)

## Setup

1. **Create a Python virtual environment:**

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## How to run

### Normalization

1. Place source CSV files (`masoretic.csv`, `vulgate.csv`, `septuagint.csv`)
   into the `data/` directory. The files must have the following columns:
   - **masoretic.csv / vulgate.csv**: `book_name`, `chapter`, `verse`, `text`
   - **septuagint.csv**: `book_name`, `chapter`, `verse`, `potential_difference_verse`, `text`

2. Set your Google AI API key:

   ```bash
   export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
   ```

3. Run:

   ```bash
   ./run.sh
   ```

   Normalized files (`masoretic_normalised.csv`, etc.) are saved in `output/`.

### Comparison

```bash
./compare.sh
```

Compares normalized JPS vs. LXX verses and saves results in `comparisons/`.

### Database preparation

```bash
./prepare_database.sh
```

Builds `data/sqlite/bible.db` from raw ebible.org data and Tov's distilled
dataset, creating alignment views.

## Data sources

- **LXX**: Tov's CATSS project (https://ccat.sas.upenn.edu/rak/catss.html) and
  Brenton's Septuagint (Vaticanus)
- **Masoretic text**: JPS 1917
- **Vulgate**: Douay–Rheims Bible
- **Qere-Ketiv**: TAHOT dataset from STEP-Bible
  (https://github.com/STEPBible/STEPBible-Data)
- **CTAT**: Dominique Barthélemy's *Critique Textuelle de l'Ancien Testament*
  (OCR pipeline in `data/manual_datasets/ctat/`)
- **Samaritan Pentateuch**: curated variant list (`data/manual_datasets/samaritan/`)

## Constitution

The project's constitution (mission, tech spec, roadmap) lives in `SPECS/`:

- `SPECS/MISSION.md` — mission and vision
- `SPECS/TECH.md` — technical specification
- `SPECS/ROADMAP.md` — delivery roadmap

## License

See `LICENSE`.