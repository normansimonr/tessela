import sqlite3
import os

def align_stage_1():
    pipeline_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_db_path = os.path.join(pipeline_root, "stage_0", "tessela_0_raw.db")
    output_db_path = os.path.join(pipeline_root, "stage_1", "tessela_1_aligned.db")
    
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    
    # 1. Source Migration: Copy tables from Stage 0 to Stage 1
    # We use ATTACH DATABASE for efficient cross-db copying
    conn = sqlite3.connect(output_db_path)
    conn.execute(f"ATTACH DATABASE '{input_db_path}' AS stage0;")
    
    tables = [
        "raw_masoretic", "raw_septuagint", "raw_vulgate", 
        "raw_qumran", "raw_samaritan", "raw_tov_distilled"
    ]
    
    for table in tables:
        print(f"Migrating {table}...")
        conn.execute(f"CREATE TABLE {table} AS SELECT * FROM stage0.{table};")
    
    # 2. Setup Book Mapping
    print("Setting up book_mapping table...")
    conn.execute("CREATE TABLE book_mapping (code TEXT, name TEXT);")
    book_data = [
        ("GEN", "Genesis"), ("EXO", "Exodus"), ("LEV", "Leviticus"), ("NUM", "Numbers"), ("DEU", "Deuteronomy"),
        ("JOS", "Joshua"), ("JDG", "Judges"), ("RUT", "Ruth"), ("1SA", "1 Samuel"), ("2SA", "2 Samuel"),
        ("1KI", "1 Kings"), ("2KI", "2 Kings"), ("1CH", "1 Chronicles"), ("2CH", "2 Chronicles"),
        ("EZR", "Ezra"), ("NEH", "Nehemiah"), ("EST", "Esther"), ("JOB", "Job"), ("PSA", "Psalms"),
        ("PRO", "Proverbs"), ("ECC", "Ecclesiastes"), ("SNG", "Song of Solomon"), ("ISA", "Isaiah"),
        ("JER", "Jeremiah"), ("LAM", "Lamentations"), ("EZK", "Ezekiel"), ("DAN", "Daniel"),
        ("HOS", "Hosea"), ("JOL", "Joel"), ("AMO", "Amos"), ("OBA", "Obadiah"), ("JON", "Jonah"),
        ("MIC", "Micah"), ("NAM", "Nahum"), ("HAB", "Habakkuk"), ("ZEP", "Zephaniah"), ("HAG", "Haggai"),
        ("ZEC", "Zechariah"), ("MAL", "Malachi")
    ]
    conn.executemany("INSERT INTO book_mapping VALUES (?, ?);", book_data)
    
    # 3. View 1: MT, LXX, Vulgate (verseID alignment)
    print("Creating view_mt_lxx_vul...")
    conn.execute("""
    CREATE VIEW view_mt_lxx_vul AS
    SELECT 
        m.verseID, m.book, m.chapter, m.startVerse, m.endVerse,
        m.verseText as mt_text,
        m.hebrew_chapter, m.hebrew_startVerse, m.hebrew_endVerse,
        l.verseText as lxx_text,
        v.verseText as vul_text
    FROM raw_masoretic m
    LEFT JOIN raw_septuagint l ON m.verseID = l.verseID
    LEFT JOIN raw_vulgate v ON m.verseID = v.verseID
    
    UNION ALL
    
    SELECT 
        l.verseID, l.book, l.chapter, l.startVerse, l.endVerse,
        NULL as mt_text, NULL, NULL, NULL,
        l.verseText as lxx_text,
        v.verseText as vul_text
    FROM raw_septuagint l
    LEFT JOIN raw_masoretic m ON l.verseID = m.verseID
    LEFT JOIN raw_vulgate v ON l.verseID = v.verseID
    WHERE m.verseID IS NULL;
    """)
    
    # 4. View 2: MT, Qumran, Samaritan (Hebrew versification alignment)
    print("Creating view_mt_qum_sam...")
    conn.execute("""
    CREATE VIEW view_mt_qum_sam AS
    SELECT 
        m.verseID,
        q.text as qumran_text,
        CASE WHEN s.verse IS NOT NULL THEN 1 ELSE 0 END as samaritan_present
    FROM raw_masoretic m
    LEFT JOIN book_mapping bm ON m.book = bm.code
    LEFT JOIN raw_qumran q ON bm.name = q.book_name 
         AND CAST(m.hebrew_chapter AS TEXT) = CAST(q.chapter AS TEXT) 
         AND CAST(m.hebrew_startVerse AS TEXT) = CAST(q.verse AS TEXT)
    LEFT JOIN raw_samaritan s ON bm.name = s.book_name 
         AND CAST(m.hebrew_chapter AS TEXT) = CAST(s.chapter AS TEXT) 
         AND CAST(m.hebrew_startVerse AS TEXT) = CAST(s.verse AS TEXT);
    """)
    
    # 5. View 3: Master Alignment
    print("Creating view_master_alignment...")
    conn.execute("""
    CREATE VIEW view_master_alignment AS
    SELECT 
        v1.*,
        v2.qumran_text,
        v2.samaritan_present,
        t.potential_difference_verse
    FROM view_mt_lxx_vul v1
    LEFT JOIN view_mt_qum_sam v2 ON v1.verseID = v2.verseID
    LEFT JOIN raw_tov_distilled t ON v1.book = t.book 
         AND CAST(v1.hebrew_chapter AS TEXT) = CAST(t.chapter AS TEXT) 
         AND CAST(v1.hebrew_startVerse AS TEXT) = CAST(CAST(t.verse AS REAL) AS INTEGER);
    """)
    
    conn.commit()
    conn.close()
    print(f"Stage 1 Alignment complete. Output: {output_db_path}")

if __name__ == "__main__":
    align_stage_1()
