import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path(
    "output/anesthesia_3year_clean.csv"
)

DATABASE_FILE = Path(
    "cms_clfs.db"
)

TABLE_NAME = "anesthesia_data"


# ============================================================
# LOAD ANESTHESIA DATA INTO SQLITE
# ============================================================

def load_anesthesia_database():

    print("\n")
    print("=" * 60)
    print("CMS ANESTHESIA DATABASE LOADER")
    print("=" * 60)

    # --------------------------------------------------------
    # CHECK INPUT FILE
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print(
            f"[ERROR] Input file not found: {INPUT_FILE}"
        )

        print(
            "[INFO] Run anesthesia_parser.py first."
        )

        return False

    print(
        f"\n[INFO] Reading: {INPUT_FILE}"
    )

    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            INPUT_FILE,
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
        f"[OK] Columns loaded: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "PRICING_YEAR",
        "EFFECTIVE_FROM",
        "EFFECTIVE_TO",
        "MDCR_CARRIER_ID",
        "MDCR_FEE_SCHD_ID",
        "LOCALITY_NAME",
        "CONV_FACTOR_AMT",
        "NON_QUALIFYING_CONV_FACTOR",
        "QUALIFYING_CONV_FACTOR",
        "SOURCE_FILE"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print(
            "\n[ERROR] Missing required columns:"
        )

        for column in missing_columns:
            print(f" - {column}")

        return False

    print(
        "\n[OK] All required Anesthesia columns found."
    )

    # --------------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------------

    try:

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        print(
            f"[OK] Connected to database: "
            f"{DATABASE_FILE}"
        )

    except Exception as error:

        print(
            f"[ERROR] Could not connect to database: "
            f"{error}"
        )

        return False

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    print(
        f"\n[OK] Records before duplicate removal: "
        f"{before}"
    )

    print(
        f"[OK] Records after duplicate removal: "
        f"{after}"
    )

    # --------------------------------------------------------
    # LOAD INTO SQLITE
    # --------------------------------------------------------

    try:

        df.to_sql(
            TABLE_NAME,
            connection,
            if_exists="replace",
            index=False
        )

        print(
            f"\n[OK] Table created/updated: "
            f"{TABLE_NAME}"
        )

    except Exception as error:

        print(
            f"[ERROR] Could not load Anesthesia data: "
            f"{error}"
        )

        connection.close()

        return False

    # --------------------------------------------------------
    # VERIFY ROW COUNT
    # --------------------------------------------------------

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {TABLE_NAME}"
    )

    database_count = cursor.fetchone()[0]

    print(
        f"[OK] Rows in database: "
        f"{database_count}"
    )

    if database_count == len(df):

        print(
            "[OK] Database row count matches CSV."
        )

    else:

        print(
            "[WARNING] Database row count does not "
            "match CSV."
        )

    # --------------------------------------------------------
    # SHOW DATABASE COLUMNS
    # --------------------------------------------------------

    cursor.execute(
        f"PRAGMA table_info({TABLE_NAME})"
    )

    columns = cursor.fetchall()

    print("\nAnesthesia database columns:")

    for column in columns:

        print(
            f" - {column[1]}"
        )

    # --------------------------------------------------------
    # RECORDS BY YEAR
    # --------------------------------------------------------

    print("\nRecords by pricing year:")

    year_query = f"""
        SELECT
            PRICING_YEAR,
            COUNT(*)
        FROM {TABLE_NAME}
        GROUP BY PRICING_YEAR
        ORDER BY PRICING_YEAR
    """

    for year, count in cursor.execute(year_query):

        print(
            f" - {year}: {count}"
        )

    # --------------------------------------------------------
    # RECORDS BY EFFECTIVE PERIOD
    # --------------------------------------------------------

    print("\nRecords by effective period:")

    date_query = f"""
        SELECT
            EFFECTIVE_FROM,
            EFFECTIVE_TO,
            COUNT(*)
        FROM {TABLE_NAME}
        GROUP BY
            EFFECTIVE_FROM,
            EFFECTIVE_TO
        ORDER BY EFFECTIVE_FROM
    """

    for start, end, count in cursor.execute(date_query):

        print(
            f" - {start} to {end}: {count}"
        )

    # --------------------------------------------------------
    # 2026 CONVERSION FACTORS
    # --------------------------------------------------------

    print("\n2026 Conversion Factor sample:")

    sample_query = f"""
        SELECT
            PRICING_YEAR,
            MDCR_CARRIER_ID,
            MDCR_FEE_SCHD_ID,
            LOCALITY_NAME,
            CONV_FACTOR_AMT,
            NON_QUALIFYING_CONV_FACTOR,
            QUALIFYING_CONV_FACTOR
        FROM {TABLE_NAME}
        WHERE PRICING_YEAR = '2026'
        LIMIT 5
    """

    sample_df = pd.read_sql_query(
        sample_query,
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
            "[INFO] No 2026 records found."
        )

    # --------------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------------

    connection.close()

    print(
        "\n[OK] Database connection closed."
    )

    print("\n")
    print("=" * 60)
    print("ANESTHESIA DATABASE LOAD COMPLETED")
    print("=" * 60)

    return True


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    success = load_anesthesia_database()

    if not success:

        raise SystemExit(1)