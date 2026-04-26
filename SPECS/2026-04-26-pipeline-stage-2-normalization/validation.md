# Validation: Stage 2 Normalization

## Success Criteria
- [ ] **Database Setup:** `pipeline/stage_2/tessela_2_normalised.db` exists with the 5 new columns.
- [ ] **API Logic:** The script correctly chooses between Standard and Batch API based on request size.
- [ ] **Data Quality:** The `*_norm` columns contain valid JSON arrays of strings.
- [ ] **Targeting:** Flags for tradition, book, and chapter work as expected.
- [ ] **Idempotency:** Re-running the script does not re-process already normalized verses unless a "force" flag is used.

## Verification Commands
```bash
# Example: Normalize Genesis 1 MT
python3 pipeline/stage_2/run.py --tradition mt --book GEN --chapter 1

# Check the output
sqlite3 pipeline/stage_2/tessela_2_normalised.db "SELECT mt_norm FROM view_master_alignment WHERE book='GEN' AND chapter='1' LIMIT 1;"
```
