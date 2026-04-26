import sqlite3
import pandas as pd
import os
import glob

def ingest_stage_0():
    db_path = "data/pipeline_stages/tessela_0_raw.db"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Remove existing database to ensure a fresh start (idempotency)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    
    # Sources configuration
    # We'll use the existing bible.db as a source for the 'raw' tables we already have there,
    # as they were loaded from the SQL files in data/sqlite/
    source_db_path = "data/sqlite/bible.db"
    
    print(f"Ingesting from {source_db_path} and other raw files...")
    
    if os.path.exists(source_db_path):
        source_conn = sqlite3.connect(source_db_path)
        
        # MT: engjps_vpl
        print("Ingesting MT (engjps_vpl)...")
        df_mt = pd.read_sql_query("SELECT * FROM engjps_vpl", source_conn)
        df_mt.to_sql("raw_masoretic", conn, index=False)
        
        # LXX: eng_Brenton_vpl
        print("Ingesting LXX (eng_Brenton_vpl)...")
        df_lxx = pd.read_sql_query("SELECT * FROM eng_Brenton_vpl", source_conn)
        df_lxx.to_sql("raw_septuagint", conn, index=False)
        
        # Vulgate: engDRA_vpl
        print("Ingesting Vulgate (engDRA_vpl)...")
        df_vulgate = pd.read_sql_query("SELECT * FROM engDRA_vpl", source_conn)
        df_vulgate.to_sql("raw_vulgate", conn, index=False)
        
        # TOV Distilled (Extra context for LXX differences)
        print("Ingesting TOV Distilled...")
        df_tov = pd.read_sql_query("SELECT * FROM tov_distilled", source_conn)
        df_tov.to_sql("raw_tov_distilled", conn, index=False)
        
        source_conn.close()
    else:
        print(f"Warning: {source_db_path} not found. Skipping SQL ingestion.")

    # Qumran Placeholder
    print("Ingesting Qumran placeholder...")
    qumran_path = "data/raw/qumran.csv"
    if os.path.exists(qumran_path):
        df_qumran = pd.read_csv(qumran_path)
        df_qumran.to_sql("raw_qumran", conn, index=False, if_exists='replace')
    
    # Qere-Ketiv
    qk_path = "data/manual_datasets/qere_ketiv/qere_ketiv_verses.csv"
    if os.path.exists(qk_path):
        print("Ingesting Qere-Ketiv...")
        df_qk = pd.read_csv(qk_path)
        df_qk.to_sql("raw_qere_ketiv", conn, index=False)

    conn.close()
    print(f"Stage 0 Ingestion complete. Database created at {db_path}")

if __name__ == "__main__":
    ingest_stage_0()
