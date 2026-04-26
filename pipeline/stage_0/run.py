import sqlite3
import pandas as pd
import os

def ingest_stage_0():
    pipeline_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    orig_data_dir = os.path.join(pipeline_root, "original_data")
    stage_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(stage_dir, "tessela_0_raw.db")
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    source_db_path = os.path.join(orig_data_dir, "sqlite", "bible.db")
    
    if os.path.exists(source_db_path):
        source_conn = sqlite3.connect(source_db_path)
        traditions = {
            "raw_masoretic": "engjps_vpl_with_hebrew", # Use the table that has hebrew versification
            "raw_septuagint": "eng_Brenton_vpl",
            "raw_vulgate": "engDRA_vpl",
            "raw_tov_distilled": "tov_distilled"
        }
        for table_name, source_table in traditions.items():
            df = pd.read_sql_query(f"SELECT * FROM {source_table}", source_conn)
            df.to_sql(table_name, conn, index=False)
        source_conn.close()

    qumran_path = os.path.join(orig_data_dir, "raw", "qumran.csv")
    if os.path.exists(qumran_path):
        df_qumran = pd.read_csv(qumran_path)
        df_qumran.to_sql("raw_qumran", conn, index=False)
    
    qk_path = os.path.join(orig_data_dir, "manual_datasets", "qere_ketiv", "qere_ketiv_verses.csv")
    if os.path.exists(qk_path):
        df_qk = pd.read_csv(qk_path)
        df_qk.to_sql("raw_qere_ketiv", conn, index=False)

    samaritan_path = os.path.join(orig_data_dir, "manual_datasets", "samaritan", "samaritan.csv")
    if os.path.exists(samaritan_path):
        df_samaritan = pd.read_csv(samaritan_path)
        df_samaritan.to_sql("raw_samaritan", conn, index=False)

    conn.close()
    print(f"Stage 0 complete. Output: {db_path}")

if __name__ == "__main__":
    ingest_stage_0()
