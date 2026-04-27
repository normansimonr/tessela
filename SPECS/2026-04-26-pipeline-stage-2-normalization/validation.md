# Validation: Stage 2 Normalization

## Success Criteria
- [ ] **Database Setup:** `pipeline/stage_2/tessela_2_normalised.db` exists with 5 new normalization columns in all raw tables
- [ ] **Coordinate Mapping:** Mapping CSVs generated showing match status for all entries
- [ ] **Coverage Stats:** All three mapping CSVs show >90% match rate (or document why lower)
- [ ] **LXX Analysis:** `MERGE_REPORT.md` includes Tov cross-check with anomaly analysis
- [ ] **Vulgate Validation:** All Vulgate base texts match (or mismatches are fully documented)
- [ ] **Database Population:** Normalisations correctly inserted; all JSON validates
- [ ] **No Data Loss:** All matched normalizations present in final DB with correct format

## Verification Commands

### 1. Check Database Setup
```bash
sqlite3 pipeline/stage_2/tessela_2_normalised.db ".schema raw_masoretic" | grep norm
```

### 2. Check Mapping Coverage
```bash
# Should show high match rates for each tradition
head -20 pipeline/stage_2/mt_mapping.csv
head -20 pipeline/stage_2/lxx_mapping.csv
head -20 pipeline/stage_2/vulgate_mapping.csv
```

### 3. Check Populated Normalisations
```bash
# Count non-NULL entries in each column
sqlite3 pipeline/stage_2/tessela_2_normalised.db << 'SQL'
SELECT
  'mt_norm' as column_name, COUNT(*) as non_null_count FROM raw_masoretic WHERE mt_norm IS NOT NULL
UNION ALL
SELECT 'lxx_norm', COUNT(*) FROM raw_septuagint WHERE lxx_norm IS NOT NULL
UNION ALL
SELECT 'vulgate_norm', COUNT(*) FROM raw_vulgate WHERE vulgate_norm IS NOT NULL;
SQL
```

### 4. Spot-Check JSON Validity
```bash
# Sample a normalisation and verify it's valid JSON
sqlite3 pipeline/stage_2/tessela_2_normalised.db \
  "SELECT mt_norm FROM raw_masoretic WHERE mt_norm IS NOT NULL LIMIT 1;"
# Should output valid JSON array like: ["prop1", "prop2", ...]
```

### 5. Read Quality Reports
```bash
cat pipeline/stage_2/MERGE_REPORT.md
cat pipeline/stage_2/VALIDATION_SUMMARY.md
```

### 6. LXX Tov Alignment Check
```bash
# Examine identified anomalies
head -50 pipeline/stage_2/lxx_tov_analysis.csv
```

### 7. Vulgate Text Mismatches
```bash
# If any mismatches found, review them
cat pipeline/stage_2/vulgate_text_mismatches.csv
```

## Acceptance Criteria
- ✅ Mapping coverage: MT ≥95%, Vulgate ≥95%, LXX ≥75% (lower due to known Tov issues)
- ✅ All populated JSON is valid (parseable as array of strings)
- ✅ MERGE_REPORT identifies and documents all anomalies
- ✅ Vulgate text validation shows results (matches or documented mismatches)
- ✅ Database queries confirm correct column population
