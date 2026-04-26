import sqlite3
import pandas as pd
import os

def align_stage_1():
    pipeline_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_db_path = os.path.join(pipeline_root, "stage_0", "tessela_0_raw.db")
    output_db_path = os.path.join(pipeline_root, "stage_1", "tessela_1_aligned.db")
    
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    
    conn_in = sqlite3.connect(input_db_path)
    conn_out = sqlite3.connect(output_db_path)
    
    print("Loading raw tables...")
    df_mt = pd.read_sql_query("SELECT * FROM raw_masoretic", conn_in)
    df_lxx = pd.read_sql_query("SELECT * FROM raw_septuagint", conn_in)
    df_vul = pd.read_sql_query("SELECT * FROM raw_vulgate", conn_in)
    
    try: df_sam = pd.read_sql_query("SELECT * FROM raw_samaritan", conn_in)
    except: df_sam = pd.DataFrame(columns=['book_name', 'chapter', 'verse'])
        
    try: df_qum = pd.read_sql_query("SELECT * FROM raw_qumran", conn_in)
    except: df_qum = pd.DataFrame(columns=['book_name', 'chapter', 'verse', 'text'])

    try: df_tov = pd.read_sql_query("SELECT * FROM raw_tov_distilled", conn_in)
    except: df_tov = pd.DataFrame(columns=['book', 'chapter', 'verse', 'potential_difference_verse'])
    
    print("Aligning MT, LXX, and Vulgate via verseID...")
    
    df_mt = df_mt.rename(columns={'verseText': 'mt_text'})
    df_lxx = df_lxx.rename(columns={'verseText': 'lxx_text'})
    df_vul = df_vul.rename(columns={'verseText': 'vulgate_text'})
    
    # Outer join MT, LXX, Vulgate
    master = pd.merge(df_mt, df_lxx[['verseID', 'lxx_text']], on='verseID', how='outer')
    master = pd.merge(master, df_vul[['verseID', 'vulgate_text']], on='verseID', how='outer')
    
    book_map = {
        "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
        "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA", "2 Samuel": "2SA",
        "1 Kings": "1KI", "2 Kings": "2KI", "1 Chronicles": "1CH", "2 Chronicles": "2CH",
        "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA",
        "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song of Solomon": "SNG", "Isaiah": "ISA",
        "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
        "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
        "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG",
        "Zechariah": "ZEC", "Malachi": "MAL"
    }
    
    print("Aligning Samaritan and Qumran via Hebrew versification...")
    
    master['hebrew_chapter'] = master['hebrew_chapter'].fillna('').astype(str)
    master['hebrew_startVerse'] = master['hebrew_startVerse'].fillna('').astype(str)
    
    if not df_sam.empty:
        df_sam['book_code'] = df_sam['book_name'].map(book_map)
        df_sam['chapter'] = df_sam['chapter'].astype(str)
        df_sam['verse'] = df_sam['verse'].astype(str)
        
        # Merge Samaritan
        master = pd.merge(
            master, 
            df_sam[['book_code', 'chapter', 'verse']].assign(samaritan_present=1),
            left_on=['book', 'hebrew_chapter', 'hebrew_startVerse'],
            right_on=['book_code', 'chapter', 'verse'],
            how='left',
            suffixes=('', '_sam')
        )
        # Drop join keys if they exist in the new columns
        for col in ['book_code', 'chapter_sam', 'verse_sam']:
            if col in master.columns: master = master.drop(columns=[col])
    else:
        master['samaritan_present'] = 0

    if not df_qum.empty:
        df_qum['book_code'] = df_qum['book_name'].map(book_map)
        df_qum['chapter'] = df_qum['chapter'].astype(str)
        df_qum['verse'] = df_qum['verse'].astype(str)
        
        # Merge Qumran
        master = pd.merge(
            master, 
            df_qum[['book_code', 'chapter', 'verse', 'text']].rename(columns={'text': 'qumran_text'}),
            left_on=['book', 'hebrew_chapter', 'hebrew_startVerse'],
            right_on=['book_code', 'chapter', 'verse'],
            how='left',
            suffixes=('', '_qum')
        )
        for col in ['book_code', 'chapter_qum', 'verse_qum']:
            if col in master.columns: master = master.drop(columns=[col])
    else:
        master['qumran_text'] = None
    
    print("Integrating TOV differences...")
    if not df_tov.empty:
        df_tov['chapter'] = df_tov['chapter'].astype(str)
        df_tov['verse'] = df_tov['verse'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x != '' else "")
        
        master = pd.merge(
            master,
            df_tov[['book', 'chapter', 'verse', 'potential_difference_verse']],
            left_on=['book', 'hebrew_chapter', 'hebrew_startVerse'],
            right_on=['book', 'chapter', 'verse'],
            how='left',
            suffixes=('', '_tov')
        )
        for col in ['book_tov', 'chapter_tov', 'verse_tov']:
            if col in master.columns: master = master.drop(columns=[col])
    else:
        master['potential_difference_verse'] = None
    
    master.to_sql("aligned_verses", conn_out, index=False)
    
    conn_in.close()
    conn_out.close()
    print(f"Stage 1 Alignment complete. Output: {output_db_path}")
    print(f"Total aligned rows: {len(master)}")

if __name__ == "__main__":
    align_stage_1()
