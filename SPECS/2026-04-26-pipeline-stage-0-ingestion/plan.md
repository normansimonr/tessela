# Implementation Plan: Stage 0 Ingestion

## Task Group 1: Environment Setup
1. Create directory `data/pipeline_stages/` if it doesn't exist.
2. Ensure `data/raw/` exists (it should, based on repo tree).
3. Create `data/raw/qumran.csv` with headers: `book_name,chapter,verse,text`.

## Task Group 2: Ingestion Script Development
1. Create `src/pipeline/stage_0_ingestion.py`.
2. Implement SQLite connection management.
3. Create functions to:
    - Load `data/masoretic.csv` into table `raw_masoretic`.
    - Load `data/septuagint.csv` into table `raw_septuagint`.
    - Load `data/vulgate.csv` into table `raw_vulgate`.
    - Load `data/raw/qumran.csv` into table `raw_qumran`.
4. Ensure the script is idempotent (deletes existing `tessela_0_raw.db` or overwrites tables).

## Task Group 3: Execution & Logging
1. Run the script.
2. Log the number of records imported for each tradition.
