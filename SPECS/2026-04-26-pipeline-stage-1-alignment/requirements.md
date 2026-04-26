# Requirements: Stage 1 Alignment

## Goal
Resolve versification differences across MT, LXX, Vulgate, Qumran, and Samaritan into a single unified master table.

## Scope
- Use the Masoretic Text (MT/JPS 1917) as the base versification system.
- Replicate the alignment logic found in the original `bible.db` views (`brenton_jps_master`, `vulgate_jps_master`, `brenton_jps_tov_master`).
- Align Qumran and Samaritan data to the MT using Hebrew versification mapping.

## Decisions
- **Implementation Method:** Use SQLite **Views** instead of in-memory Python joins to ensure transparency and ease of debugging.
- **Views to Implement:**
    1. `view_mt_lxx_vul`: Aligns JPS, Brenton, and Vulgate via `verseID`.
    2. `view_mt_qum_sam`: Aligns JPS, Qumran, and Samaritan via Hebrew versification.
    3. `view_master_alignment`: Consolidates the above views + TOV data into the final master set.
- **Book Mapping:** A dedicated `book_mapping` table will be created in the database to handle SQL joins between long names and MT codes.
- **Output:** `pipeline/stage_1/tessela_1_aligned.db`.

## Context
The alignment is the backbone of the comparative analysis. By normalizing all traditions to the MT base, we can identify translationally significant variants in a structured way.
