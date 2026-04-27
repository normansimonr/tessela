# Implementation Plan: Stage 2 Normalization

## Task Group 1: Environment & Setup
1. Create directory `pipeline/stage_2/`.
2. Copy `tessela_1_aligned.db` → `tessela_2_normalised.db`.
3. Add normalization columns to all raw tables:
   - `mt_norm`, `lxx_norm`, `vulgate_norm`, `qumran_norm`, `samaritan_norm`
   - All columns: TEXT, default NULL

## Task Group 2: Coordinate Mapping & Validation
1. Create `pipeline/stage_2/merge.py` script with:
   - `normalize_book_name(csv_name)` function to convert CSV book names to DB codes
   - CSV verse coordinate parser (handle decimal verse numbers like "10.0")
   - Matching engine: map CSV `(book_name, chapter, verse)` → Database `verseID`
   
2. For each tradition (MT, LXX, Vulgate):
   - Load CSV into memory
   - For each CSV row:
     - Resolve book code via `book_mapping`
     - Find matching `verseID` in database
     - Store match result: (csv_coords, verseID, match_status)
   - Track unmatched entries and text mismatches

3. Build three mapping tables (CSV):
   - `mt_mapping.csv`: (csv_book_name, csv_chapter, csv_verse, verseID, match_status, text_match)
   - `lxx_mapping.csv`: (csv_book_name, csv_chapter, csv_verse, verseID, match_status, text_match)
   - `vulgate_mapping.csv`: (csv_book_name, csv_chapter, csv_verse, verseID, match_status, text_match)

## Task Group 3: Consistency Reporting
1. Generate `MERGE_REPORT.md` containing:

   **a) Coverage Summary:**
   - For each tradition: total verses in CSV, total matched to DB, match rate
   - For each tradition: total verses in DB, how many have normalisations
   
   **b) LXX Tov Analysis:**
   - Cross-check normalized LXX verses against `raw_tov_distilled` table
   - Count: verses marked "potential_difference_verse" in Tov vs. verses that were actually normalized
   - Identify anomalies (e.g., normalized verses that aren't in Tov, Tov verses not normalized)
   - Document suspected Tov coordinate misalignment issues
   
   **c) Vulgate Text Validation:**
   - For each normalized Vulgate verse:
     - Compare CSV text with existing `raw_vulgate.verseText`
     - Flag any text mismatches with side-by-side comparison
   - Generate: `vulgate_text_mismatches.csv` with details
   
   **d) Mismatch Details:**
   - Verses in CSV but not found in DB (by tradition)
   - Verses in DB without a match in CSV (coverage gaps)
   - Verses with coordinate ambiguities (e.g., compound verses)

2. Output detailed debugging CSVs:
   - `*_unmatched.csv`: CSV entries without DB match
   - `*_gaps.csv`: DB verses without CSV normalisation
   - `*_text_mismatches.csv`: Coordinate matches but text differs

## Task Group 4: Database Population
1. For each matched CSV entry:
   - Insert the normalisation JSON into the appropriate `*_norm` column
   - Update the correct `verseID` row in the matching raw table
   
2. Verify:
   - All inserted JSON arrays parse correctly
   - No overwrite conflicts (no duplicate matches)
   - NULL handling for unmatched verses

## Task Group 5: Final Validation
1. Create validation queries:
   - Count non-NULL entries in each `*_norm` column
   - Verify JSON structure (all are valid arrays of strings)
   - Spot-check 10 random entries from each tradition
2. Generate `VALIDATION_SUMMARY.md` with:
   - Success/failure counts
   - Data quality metrics
   - Recommendations for next steps
