# Validation: Stage 1 Alignment

## Success Criteria
- [ ] **Database Created:** `pipeline/stage_1/tessela_1_aligned.db` exists.
- [ ] **Table Integrity:** Table `aligned_verses` contains columns for all five traditions.
- [ ] **MT Integrity:** All verses from `raw_masoretic` are present in `aligned_verses`.
- [ ] **Alignment Accuracy (Samaritan):** Genesis 2:2 shows the Samaritan Pentateuch record aligned with the MT record.
- [ ] **Alignment Accuracy (LXX):** Verses marked in `tov_distilled` correctly show `potential_difference_verse = True`.
- [ ] **Versification:** Cases where JPS and LXX verse numbers differ (but semantic content matches) are correctly aligned via `verseID`.

## Verification Command
```bash
sqlite3 pipeline/stage_1/tessela_1_aligned.db "SELECT * FROM aligned_verses WHERE book_code='GEN' AND hebrew_chapter=2 AND hebrew_verse=2;"
```
