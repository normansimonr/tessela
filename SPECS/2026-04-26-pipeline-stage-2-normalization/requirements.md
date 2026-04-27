# Requirements: Stage 2 Normalization

## Goal
Integrate pre-computed semantic normalizations (decomposed into atomic propositions) from existing CSV files into the aligned database. Validate all matches for accuracy, document inconsistencies, and prepare the data for downstream variant detection.

## Scope
- Merge three normalised CSV files into the aligned database:
  - `masoretic_normalised.csv` (23,147 rows)
  - `septuagint_normalised.csv` (15,072 rows)
  - `vulgate_normalised.csv` (23,507 rows)
- Thoroughly validate verse matching across different coordinate systems
- Generate comprehensive reports on data quality and coverage

## Key Decisions
- **Data Source:** Use existing normalised CSV files (from prior Gemini run) instead of calling the API
- **Coordinate Matching:**
  - Map CSV coordinates `(book_name, chapter, verse)` → Database `verseID`
  - Use `book_mapping` table to convert book names to codes
  - Handle special cases: decimal verse numbers (LXX), compound verses
- **Validation Strategy:**
  - **LXX Priority:** Cross-check normalised verses against Tov distilled data to identify coordinate system errors
  - **Vulgate Priority:** Line-by-line base text comparison (100% match required)
  - Generate mismatch reports with exact coordinates
- **Storage:**
  - Output database: `pipeline/stage_2/tessela_2_normalised.db` (copy of stage_1 DB with new columns)
  - Add 5 columns to all raw tables: `mt_norm`, `lxx_norm`, `vulgate_norm`, `qumran_norm`, `samaritan_norm`
  - Results stored as JSON strings (array of propositions)
  - Unmatched verses left as NULL

## Context
This stage is a critical data quality checkpoint. Unlike a fresh normalization run, we are integrating pre-computed results and must verify that the matching process is accurate, especially given the known issues with Tov coordinates and Vulgate source mismatches. The comprehensive reports generated here will inform whether to re-normalize missing verses or accept the current coverage.
