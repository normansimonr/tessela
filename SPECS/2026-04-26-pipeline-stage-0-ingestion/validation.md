# Validation: Stage 0 Ingestion

## Success Criteria
- [ ] **File Presence:** `data/pipeline_stages/tessela_0_raw.db` exists.
- [ ] **Table Integrity:** Tables `raw_masoretic`, `raw_septuagint`, `raw_vulgate`, and `raw_qumran` exist in the database.
- [ ] **Schema Fidelity:** Column names in `raw_masoretic` match those in `data/masoretic.csv`.
- [ ] **Record Count:** `SELECT COUNT(*) FROM raw_masoretic` matches the number of lines (minus header) in `data/masoretic.csv`.
- [ ] **Qumran Placeholder:** `raw_qumran` exists even if it is empty (or has only dummy data).

## Verification Command
```bash
sqlite3 data/pipeline_stages/tessela_0_raw.db .tables
sqlite3 data/pipeline_stages/tessela_0_raw.db "SELECT count(*) FROM raw_masoretic;"
```
