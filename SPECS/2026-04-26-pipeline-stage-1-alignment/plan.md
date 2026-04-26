# Implementation Plan: Stage 1 Alignment

## Task Group 1: Environment & Setup
1. Create directory `pipeline/stage_1/`.
2. Review MT book codes in `pipeline/stage_0/tessela_0_raw.db`.

## Task Group 2: Script Development (`pipeline/stage_1/run.py`)
1. **Source Migration:** Copy all `raw_*` tables from `pipeline/stage_0/tessela_0_raw.db` to the new `tessela_1_aligned.db`.
2. **Setup Mapping:** Create `book_mapping` table with codes (GEN, EXO...) and names (Genesis, Exodus...).
3. **View 1: `view_mt_lxx_vul`:** Implement the `verseID`-based join logic.
4. **View 2: `view_mt_qum_sam`:** Implement the Hebrew versification join using the `book_mapping` table.
5. **View 3: `view_master_alignment`:** 
    - Join View 1 and View 2.
    - Integrate `raw_tov_distilled` for potential differences.
6. **Persistence:** The views are permanent parts of the `tessela_1_aligned.db`.

## Task Group 3: Verification
1. Log total row count (should be at least 23,145 + verses unique to LXX/Vulgate).
2. Check for alignment of known Samaritan variants (e.g., Genesis 2:2).
