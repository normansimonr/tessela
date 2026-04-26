# Requirements: Stage 1 Alignment

## Goal
Resolve versification differences across MT, LXX, Vulgate, Qumran, and Samaritan into a single unified master table.

## Scope
- Use the Masoretic Text (MT/JPS 1917) as the base versification system.
- Replicate the alignment logic found in the original `bible.db` views (`brenton_jps_master`, `vulgate_jps_master`, `brenton_jps_tov_master`).
- Align Qumran and Samaritan data to the MT using Hebrew versification mapping.

## Decisions
- **Join Keys (LXX/Vulgate):** Use `verseID` (e.g., `GN1_1`) to align JPS with Brenton and Vulgate, as established in the original SQL views.
- **Join Keys (Qumran/Samaritan):** Aligned via Hebrew versification columns (`hebrew_chapter`, `hebrew_startVerse`).
- **Book Mapping:** Implement mapping from long book names (e.g., "Genesis") to MT codes (e.g., "GEN") for Samaritan and Qumran ingestion.
- **Output:** A single SQLite database `pipeline/stage_1/tessela_1_aligned.db` containing the `aligned_verses` table.

## Context
The alignment is the backbone of the comparative analysis. By normalizing all traditions to the MT base, we can identify translationally significant variants in a structured way.
