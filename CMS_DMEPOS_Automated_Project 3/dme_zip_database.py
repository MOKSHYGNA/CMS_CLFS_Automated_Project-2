import sqlite3
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_FILE = PROJECT_ROOT / "output" / "zip_carrier_locality.csv"
DATABASE_FILE = PROJECT_ROOT / "output" / "cms_dmepos.db"


def load_zip_carrier_locality(
    input_file=INPUT_FILE,
    database_file=DATABASE_FILE
):
    print("=" * 60)
    print("ZIP CARRIER / LOCALITY DATABASE LOADER")
    print("=" * 60)

    input_file = Path(input_file)
    database_file = Path(database_file)

    if not input_file.exists():
        raise FileNotFoundError(
            f"ZIP carrier/locality CSV not found: {input_file}"
        )

    database_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Input file: {input_file}")
    print(f"Database: {database_file}")

    # ---------------------------------------------------------
    # READ CSV
    # ---------------------------------------------------------
    df = pd.read_csv(
        input_file,
        dtype=str,
        keep_default_na=False
    )

    print(f"Records read: {len(df)}")

    # ---------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # ---------------------------------------------------------
    required_columns = [
        "STATE",
        "ZIP_CODE",
        "MDCR_CARRIER_ID",
        "MDCR_FEE_SCHD_ID",
        "RURAL_INDICATOR",
        "BENE_LAB_CB_LOCALITY",
        "RURAL_INDICATOR2",
        "PLUS4_FLAG",
        "PART_B_PAYMENT_INDICATOR",
        "YEAR_QUARTER",
        "PRICING_AREA_TYPE"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print("Required columns validated successfully.")

    # ---------------------------------------------------------
    # CLEAN VALUES
    # ---------------------------------------------------------
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Keep ZIP and IDs as text so leading zeros are preserved.
    df["ZIP_CODE"] = df["ZIP_CODE"].str.zfill(5)
    df["MDCR_CARRIER_ID"] = df["MDCR_CARRIER_ID"].str.zfill(5)
    df["MDCR_FEE_SCHD_ID"] = df["MDCR_FEE_SCHD_ID"].str.zfill(2)

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------
    before = len(df)

    df = df.drop_duplicates(
        subset=[
            "ZIP_CODE",
            "YEAR_QUARTER"
        ]
    ).copy()

    duplicates_removed = before - len(df)

    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Final records: {len(df)}")

    # ---------------------------------------------------------
    # DATABASE CONNECTION
    # ---------------------------------------------------------
    conn = sqlite3.connect(database_file)

    try:
        # -----------------------------------------------------
        # CREATE TABLE
        # -----------------------------------------------------
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS zip_carrier_locality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            zip_code TEXT NOT NULL,
            mdcr_carrier_id TEXT,
            mdcr_fee_schd_id TEXT,
            rural_indicator TEXT,
            bene_lab_cb_locality TEXT,
            rural_indicator2 TEXT,
            plus4_flag TEXT,
            part_b_payment_indicator TEXT,
            year_quarter TEXT,
            pricing_area_type TEXT,
            UNIQUE(zip_code, year_quarter)
        )
        """

        conn.execute(create_table_sql)

        # -----------------------------------------------------
        # REPLACE CURRENT ZIP MAPPING
        # -----------------------------------------------------
        conn.execute(
            "DELETE FROM zip_carrier_locality"
        )

        # -----------------------------------------------------
        # INSERT DATA
        # -----------------------------------------------------
        insert_sql = """
        INSERT INTO zip_carrier_locality (
            state,
            zip_code,
            mdcr_carrier_id,
            mdcr_fee_schd_id,
            rural_indicator,
            bene_lab_cb_locality,
            rural_indicator2,
            plus4_flag,
            part_b_payment_indicator,
            year_quarter,
            pricing_area_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        records = [
            (
                row["STATE"],
                row["ZIP_CODE"],
                row["MDCR_CARRIER_ID"],
                row["MDCR_FEE_SCHD_ID"],
                row["RURAL_INDICATOR"],
                row["BENE_LAB_CB_LOCALITY"],
                row["RURAL_INDICATOR2"],
                row["PLUS4_FLAG"],
                row["PART_B_PAYMENT_INDICATOR"],
                row["YEAR_QUARTER"],
                row["PRICING_AREA_TYPE"]
            )
            for _, row in df.iterrows()
        ]

        conn.executemany(insert_sql, records)

        # -----------------------------------------------------
        # INDEXES
        # -----------------------------------------------------
        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_zip_carrier_zip
            ON zip_carrier_locality(zip_code)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_zip_carrier_ids
            ON zip_carrier_locality(
                mdcr_carrier_id,
                mdcr_fee_schd_id
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_zip_carrier_year
            ON zip_carrier_locality(year_quarter)
        """)

        conn.commit()

        # -----------------------------------------------------
        # VERIFY
        # -----------------------------------------------------
        count = conn.execute(
            "SELECT COUNT(*) FROM zip_carrier_locality"
        ).fetchone()[0]

        unique_zips = conn.execute(
            "SELECT COUNT(DISTINCT zip_code) "
            "FROM zip_carrier_locality"
        ).fetchone()[0]

        unique_carriers = conn.execute(
            "SELECT COUNT(DISTINCT mdcr_carrier_id) "
            "FROM zip_carrier_locality"
        ).fetchone()[0]

        unique_fee_schedules = conn.execute(
            "SELECT COUNT(DISTINCT mdcr_fee_schd_id) "
            "FROM zip_carrier_locality"
        ).fetchone()[0]

        print()
        print("Database table created successfully.")
        print(f"Records in database: {count}")
        print(f"Unique ZIP codes: {unique_zips}")
        print(f"Unique Carrier IDs: {unique_carriers}")
        print(f"Unique Fee Schedule IDs: {unique_fee_schedules}")

    finally:
        conn.close()

    print("=" * 60)
    print("ZIP DATABASE LOAD COMPLETED")
    print("=" * 60)

    return database_file


if __name__ == "__main__":
    load_zip_carrier_locality()