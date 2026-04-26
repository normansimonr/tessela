# Implementation Plan: Stage 1 Alignment

## Task Group 1: Environment & Setup
1. Create directory `pipeline/stage_1/`.
2. Review MT book codes in `pipeline/stage_0/tessela_0_raw.db`.

## Task Group 2: Script Development (`pipeline/stage_1/run.py`)
1. **Source Loading:** Read all tables from `pipeline/stage_0/tessela_0_raw.db`.
2. **Book Mapping Utility:** Create a mapping between Samaritan/Qumran `book_name` and MT `book_code`.
3. **Core Alignment (MT-LXX-Vulgate):**
    - Perform a `FULL OUTER JOIN` (emulated via `UNION` of `LEFT JOINs` as per original SQL) between JPS, Brenton, and Vulgate using `verseID`.
    - Ensure `hebrew_chapter` and `hebrew_startVerse` are preserved for all rows.
4. **Secondary Alignment (Qumran-Samaritan):**
    - Join `raw_qumran` to the master set using `book_code`, `hebrew_chapter`, and `hebrew_startVerse`.
    - Join `raw_samaritan` to the master set using `book_code`, `hebrew_chapter`, and `hebrew_startVerse`.
5. **Context Enrichment:**
    - Join `raw_tov_distilled` to add `potential_difference_verse`.
6. **Persistence:** Write the final dataframe to `pipeline/stage_1/tessela_1_aligned.db`.

## Task Group 3: Verification
1. Log total row count (should be at least 23,145 + verses unique to LXX/Vulgate).
2. Check for alignment of known Samaritan variants (e.g., Genesis 2:2).
