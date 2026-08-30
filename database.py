
import sqlite3
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

INPUT_FILE = Path(
    "output/cms_clfs_combined.csv"
)

DATABASE_FILE = Path(
    "cms_clfs.db"
)

TABLE_NAME = "clfs_data"


# --------------------------------------------------
# LOAD CSV INTO SQLITE
# --------------------------------------------------

def load_database():

    print("\n")
    print("=" * 60)
    print("CMS CLFS DATABASE LOADER")
    print("=" * 60)

    # --------------------------------------------------
    # CHECK INPUT FILE
    # --------------------------------------------------

    if not INPUT_FILE.exists():

        print(
            f"[ERROR] Input file not found: {INPUT_FILE}"
        )

        print(
            "Run etl_pipeline.py first."
        )

        return

    print(
        f"\n[INFO] Reading: {INPUT_FILE}"
    )

    # --------------------------------------------------
    # READ CLEAN CSV
    # --------------------------------------------------

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8"
    )

    print(
        f"[OK] Rows loaded from CSV: {len(df)}"
    )

    print(
        f"[OK] Columns: {len(df.columns)}"
    )

    # --------------------------------------------------
    # CREATE SQLITE DATABASE
    # --------------------------------------------------

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    print(
        f"[OK] Connected to database: {DATABASE_FILE}"
    )

    # --------------------------------------------------
    # LOAD DATA INTO TABLE
    # --------------------------------------------------

    df.to_sql(
        TABLE_NAME,
        connection,
        if_exists="replace",
        index=False
    )

    print(
        f"[OK] Table created: {TABLE_NAME}"
    )

    # --------------------------------------------------
    # VERIFY ROW COUNT
    # --------------------------------------------------

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {TABLE_NAME}"
    )

    row_count = cursor.fetchone()[0]

    print(
        f"[OK] Rows in database: {row_count}"
    )

    # --------------------------------------------------
    # SHOW TABLE COLUMNS
    # --------------------------------------------------

    cursor.execute(
        f"PRAGMA table_info({TABLE_NAME})"
    )

    columns = cursor.fetchall()

    print("\nDatabase columns:")

    for column in columns:

        print(
            f"  - {column[1]}"
        )

    # --------------------------------------------------
    # SAMPLE QUERY
    # --------------------------------------------------

    print("\nSample database records:")

    sample_query = f"""
        SELECT
            YEAR,
            HCPCS,
            EFF_DATE,
            RATE,
            SHORTDESC
        FROM {TABLE_NAME}
        LIMIT 5
    """

    sample_df = pd.read_sql_query(
        sample_query,
        connection
    )

    print(
        sample_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------

    connection.close()

    print("\n[OK] Database connection closed.")

    print("\n")
    print("=" * 60)
    print("DATABASE LOAD COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    load_database()

