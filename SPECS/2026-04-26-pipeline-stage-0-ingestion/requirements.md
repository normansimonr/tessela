# Requirements: Stage 0 Ingestion

## Goal
Consolidate all raw textual sources into a single SQLite database snapshot to serve as the immutable entry point for the Tessela pipeline.

## Scope
- Ingest Masoretic (JPS), Septuagint (Tov/Brenton), Vulgate (Douay-Rheims), and a placeholder for Qumran data.
- Maintain the original column names and structures from the raw CSV files.

## Decisions
- **Source Data:** MT, LXX, and Vulgate are pulled from existing CSVs in `data/`.
- **Qumran Placeholder:** A new CSV `data/raw/qumran.csv` will be created with columns `book_name`, `chapter`, `verse`, `text`.
- **Output:** The result must be a single file `data/pipeline_stages/tessela_0_raw.db`.
- **Execution:** A standalone Python script `src/pipeline/stage_0_ingestion.py`.

## Context
By mirroring the raw schemas in Stage 0, we ensure that any later changes to how we "align" or "normalize" the data can be re-run without worrying about the initial data loading logic.
