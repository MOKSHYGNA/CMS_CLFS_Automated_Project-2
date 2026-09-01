
import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "output/cms_all_combined.csv"
)

DATABASE_FILE = Path(
    "cms_clfs.db"
)

TABLE_NAME = "clfs_data"


# ============================================================
# LOAD CSV INTO SQLITE
# ============================================================

def load_database():

    print("\n")
    print("=" * 60)
    print("CMS CLFS DATABASE LOADER")
    print("=" * 60)

    # ========================================================
    # CHECK INPUT FILE
    # ========================================================

    if not INPUT_FILE.exists():

        print(
            f"[ERROR] Input file not found: {INPUT_FILE}"
        )

        print(
            "[INFO] Run physician_parser.py and "
            "combine_datasets.py first."
        )

        return False

    print(
        f"\n[INFO] Reading: {INPUT_FILE}"
    )

    # ========================================================
    # READ CSV
    # ========================================================

    try:

        df = pd.read_csv(
            INPUT_FILE,
            encoding="utf-8",
            dtype=str
        )

    except Exception as error:

        print(
            f"[ERROR] Could not read CSV: {error}"
        )

        return False

    print(
        f"[OK] Rows loaded from CSV: {len(df)}"
    )

    print(
        f"[OK] Columns: {len(df.columns)}"
    )

    # ========================================================
    # CHECK DATA_TYPE
    # ========================================================

    if "DATA_TYPE" in df.columns:

        print("\n[OK] DATA_TYPE column found.")

        print("\nData type summary:")

        print(
            df["DATA_TYPE"].value_counts()
        )

    else:

        print(
            "\n[WARNING] DATA_TYPE column not found."
        )

    # ========================================================
    # CONNECT TO SQLITE DATABASE
    # ========================================================

    try:

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        print(
            f"\n[OK] Connected to database: "
            f"{DATABASE_FILE}"
        )

    except Exception as error:

        print(
            f"[ERROR] Could not connect to database: "
            f"{error}"
        )

        return False

    # ========================================================
    # LOAD DATA INTO SQLITE
    # ========================================================

    try:

        df.to_sql(
            TABLE_NAME,
            connection,
            if_exists="replace",
            index=False
        )

        print(
            f"[OK] Table created/updated: "
            f"{TABLE_NAME}"
        )

    except Exception as error:

        print(
            f"[ERROR] Could not load data into database: "
            f"{error}"
        )

        connection.close()

        return False

    # ========================================================
    # VERIFY ROW COUNT
    # ========================================================

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {TABLE_NAME}"
    )

    row_count = cursor.fetchone()[0]

    print(
        f"[OK] Rows in database: {row_count}"
    )

    # ========================================================
    # SHOW DATABASE COLUMNS
    # ========================================================

    cursor.execute(
        f"PRAGMA table_info({TABLE_NAME})"
    )

    columns = cursor.fetchall()

    print("\nDatabase columns:")

    for column in columns:

        print(
            f"  - {column[1]}"
        )

    # ========================================================
    # VERIFY DATA TYPES IN DATABASE
    # ========================================================

    if "DATA_TYPE" in df.columns:

        cursor.execute(
            f"""
            SELECT
                DATA_TYPE,
                COUNT(*)
            FROM {TABLE_NAME}
            GROUP BY DATA_TYPE
            """
        )

        print("\nDatabase data type summary:")

        for data_type, count in cursor.fetchall():

            print(
                f"  - {data_type}: {count}"
            )

    # ========================================================
    # SAMPLE CLINICAL RECORDS
    # ========================================================

    print("\nSample clinical records:")

    clinical_query = f"""
        SELECT
            YEAR,
            HCPCS,
            MOD,
            EFF_DATE,
            INDICATOR,
            RATE,
            SHORTDESC,
            DATA_TYPE
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'CLINICAL'
        LIMIT 5
    """

    try:

        sample_df = pd.read_sql_query(
            clinical_query,
            connection
        )

        if not sample_df.empty:

            print(
                sample_df.to_string(
                    index=False
                )
            )

        else:

            print(
                "[INFO] No clinical records found."
            )

    except Exception as error:

        print(
            f"[WARNING] Clinical sample query failed: "
            f"{error}"
        )

    # ========================================================
    # SAMPLE PHYSICIAN RECORDS
    # ========================================================

    print("\nSample physician records:")

    physician_query = f"""
        SELECT
            YEAR,
            HCPCS,
            MOD,
            NON_FACILITY_RATE,
            FACILITY_RATE,
            PCTC_INDICATOR,
            STATUS_CODE,
            FILE_TYPE,
            DATA_TYPE
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'PHYSICIAN'
        LIMIT 5
    """

    try:

        sample_physician_df = pd.read_sql_query(
            physician_query,
            connection
        )

        if not sample_physician_df.empty:

            print(
                sample_physician_df.to_string(
                    index=False
                )
            )

        else:

            print(
                "[INFO] No physician records found."
            )

    except Exception as error:

        print(
            f"[WARNING] Physician sample query failed: "
            f"{error}"
        )

    # ========================================================
    # CLOSE DATABASE
    # ========================================================

    connection.close()

    print(
        "\n[OK] Database connection closed."
    )

    print("\n")
    print("=" * 60)
    print("DATABASE LOAD COMPLETED")
    print("=" * 60)

    return True


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    success = load_database()

    if not success:

        raise SystemExit(1)

