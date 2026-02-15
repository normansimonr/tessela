#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Reinitialising database

echo "Preparing to remove existing bible.db file";

rm data/sqlite/bible.db -f

echo "Existing bible.db file removed";

# Processing TOV

echo "Processing Tov's raw data files";
#source .venv/bin/activate
#export PYTHONPATH=$PYTHONPATH:$PWD

#pushd src/tov_processor
#python3 convert_lxx_tov_to_csv_unicode.py
#python3 distill_tov.py
#popd

echo "Tov's retroversion successfully distilled";

# Importing TOV (distilled)

echo "Importing distilled Tov's dataset into bible.db";

sqlite3 data/sqlite/bible.db <<'EOF'
.mode csv
.headers on
.import data/intermediate_datasets/tov_distilled.csv tov_distilled
EOF

echo "Distilled Tov's dataset successfully imported into bible.db";

# Loading the raw data

echo "Loading ebible data into bible.db (Brenton, DRA and JPS)";
sqlite3 data/sqlite/bible.db < data/sqlite/eng-Brenton_vpl.sql
echo "-> Brenton successfully loaded";
sqlite3 data/sqlite/bible.db < data/sqlite/engDRA_vpl.sql
echo "-> DRA successfully loaded";
sqlite3 data/sqlite/bible.db < data/sqlite/engjps_vpl.sql
echo "-> JPS successfully loaded";
echo "ebible data successfully loaded into bible.db (Brenton, DRA and JPS)";

# Creating the necessary views

echo "Creating primary bible.db views";
sqlite3 data/sqlite/bible.db < data/sqlite/hebrew_verse_extractor.sql
sqlite3 data/sqlite/bible.db < data/sqlite/vulgate_jps_view.sql
sqlite3 data/sqlite/bible.db < data/sqlite/brenton_jps_view.sql
sqlite3 data/sqlite/bible.db < data/sqlite/merge_brenton_tov.sql
echo "bible.db views successfully created";
