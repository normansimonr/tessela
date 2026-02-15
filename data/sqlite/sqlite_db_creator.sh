rm bible.db

# Loading the raw data

sqlite3 bible.db < eng-Brenton_vpl.sql
sqlite3 bible.db < engDRA_vpl.sql
sqlite3 bible.db < engjps_vpl.sql 

# Creating the necessary views

sqlite3 bible.db < hebrew_verse_extractor.sql
sqlite3 bible.db < vulgate_jps_view.sql
sqlite3 bible.db < brenton_jps_view.sql
