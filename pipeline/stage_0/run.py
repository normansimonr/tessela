import sqlite3
import pandas as pd
import os

def ingest_stage_0():
    # Paths are relative to the pipeline root or absolute
    pipeline_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orig_data_dir = os.path.join(pipeline_root, "original_data")
    stage_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(stage_dir, "tessela_0_raw.db")
    
    # Remove existing database for idempotency
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    
    # Source: Existing bible.db (snapshot of SQL loads)
    source_db_path = os.path.join(orig_data_dir, "sqlite", "bible.db")
    
    print(f"Ingesting from {source_db_path}...")
    
    if os.path.exists(source_db_path):
        source_conn = sqlite3.connect(source_db_path)
        
        # MT, LXX, Vulgate from the merged snapshot
        traditions = {
            "raw_masoretic": "engjps_vpl",
            "raw_septuagint": "eng_Brenton_vpl",
            "raw_vulgate": "engDRA_vpl",
            "raw_tov_distilled": "tov_distilled"
        }
        
        for table_name, source_table in traditions.items():
            print(f"  -> {table_name}")
            df = pd.read_sql_query(f"SELECT * FROM {source_table}", source_conn)
            df.to_sql(table_name, conn, index=False)
        
        source_conn.close()
    else:
        print(f"Warning: {source_db_path} not found.")

    # Qumran Placeholder from original_data
    print("Ingesting Qumran placeholder...")
    qumran_path = os.path.join(orig_data_dir, "qumran.csv")
    if os.path.exists(qumran_path):
        df_qumran = pd.read_csv(qumran_path)
        df_qumran.to_sql("raw_qumran", conn, index=False)
    
    # Qere-Ketiv from manual_datasets
    qk_path = os.path.join(orig_data_dir, "manual_datasets", "qere_ketiv", "qere_ketiv_verses.csv")
    if os.path.exists(qk_path):
        print("Ingesting Qere-Ketiv...")
        df_qk = pd.read_csv(qk_path)
        df_qk.to_sql("raw_qere_ketiv", conn, index=False)

    # Samaritan Pentateuch from manual_datasets
    samaritan_path = os.path.join(orig_data_dir, "manual_datasets", "samaritan", "samaritan.csv")
    if os.path.exists(samaritan_path):
        print("Ingesting Samaritan Pentateuch...")
        df_samaritan = pd.read_csv(samaritan_path)
        df_samaritan.to_sql("raw_samaritan", conn, index=False)

    conn.close()
    print(f"Stage 0 Ingestion complete. Output: {db_path}")

if __name__ == "__main__":
    ingest_stage_0()
