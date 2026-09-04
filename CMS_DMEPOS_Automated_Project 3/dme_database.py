import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime


def load_dme_to_database(
    input_csv,
    db_path,
    release_name,
    sha256=None
):
    print("=" * 50)
    print("DMEPOS DATABASE LOADER")
    print("=" * 50)

    input_csv = Path(input_csv)
    db_path = Path(db_path)

    if not input_csv.exists():
        raise FileNotFoundError(
            f"Normalized CSV not found: {input_csv}"
        )

    print(f"Input file: {input_csv}")
    print(f"Release: {release_name}")

    # --------------------------------------------------
    # 1. Load normalized data
    # --------------------------------------------------
    df = pd.read_csv(
        input_csv,
        dtype=str
    )

    print(f"Records loaded: {len(df)}")

    # --------------------------------------------------
    # 2. Add release and hash
    # --------------------------------------------------
    df["RELEASE"] = release_name
    df["SHA256"] = sha256

    # --------------------------------------------------
    # 3. Convert numeric columns
    # --------------------------------------------------
    for column in ["Ceiling", "Floor", "PRICE"]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------
    # 4. Rename columns
    # --------------------------------------------------
    rename_map = {
        "HCPCS": "hcpcs",
        "Mod": "modifier",
        "Mod2": "modifier_2",
        "JURIS": "jurisdiction",
        "CATG": "category",
        "Ceiling": "ceiling",
        "Floor": "floor",
        "STATE": "state",
        "PRICE_TYPE": "price_type",
        "PRICE": "price",
        "Description": "description",
        "RELEASE": "release",
        "SHA256": "sha256"
    }

    df = df.rename(columns=rename_map)

    # --------------------------------------------------
    # 5. Create database folder
    # --------------------------------------------------
    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # 6. Connect to database
    # --------------------------------------------------
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --------------------------------------------------
    # 7. Release tracking table
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_releases (
            release TEXT PRIMARY KEY,
            records INTEGER,
            sha256 TEXT,
            loaded_at TEXT
        )
    """)

    # --------------------------------------------------
    # 8. Main fee schedule table
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dmepos_fee_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            modifier TEXT,
            modifier_2 TEXT,
            jurisdiction TEXT,
            category TEXT,
            ceiling REAL,
            floor REAL,
            state TEXT,
            price_type TEXT,
            price REAL,
            description TEXT,
            release TEXT,
            sha256 TEXT
        )
    """)

    conn.commit()

    # --------------------------------------------------
    # 9. Check existing release
    # --------------------------------------------------
    cursor.execute(
        """
        SELECT sha256
        FROM dme_releases
        WHERE release = ?
        """,
        (release_name,)
    )

    existing = cursor.fetchone()

    # --------------------------------------------------
    # 10. NEW RELEASE
    # --------------------------------------------------
    if existing is None:

        print(f"New release detected: {release_name}")

        df.to_sql(
            "dmepos_fee_schedule",
            conn,
            if_exists="append",
            index=False
        )

        cursor.execute(
            """
            INSERT INTO dme_releases
            (release, records, sha256, loaded_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                release_name,
                len(df),
                sha256,
                datetime.now().isoformat()
            )
        )

        conn.commit()

        print(
            f"Release records inserted: {len(df)}"
        )

    # --------------------------------------------------
    # 11. EXISTING RELEASE
    # --------------------------------------------------
    else:

        old_sha256 = existing[0]

        # Same hash = no change
        if sha256 and old_sha256 == sha256:

            print(
                f"Release {release_name} already exists "
                "with the same file hash."
            )

            print("Skipping duplicate load.")

            conn.close()

            return "already_loaded"

        # --------------------------------------------------
        # 12. CHANGED RELEASE
        # --------------------------------------------------
        print(
            f"Release {release_name} has changed."
        )

        print("Replacing old records...")

        # Delete old records
        cursor.execute(
            """
            DELETE FROM dmepos_fee_schedule
            WHERE release = ?
            """,
            (release_name,)
        )

        # Insert updated records
        df.to_sql(
            "dmepos_fee_schedule",
            conn,
            if_exists="append",
            index=False
        )

        # Update release information
        cursor.execute(
            """
            UPDATE dme_releases
            SET records = ?,
                sha256 = ?,
                loaded_at = ?
            WHERE release = ?
            """,
            (
                len(df),
                sha256,
                datetime.now().isoformat(),
                release_name
            )
        )

        conn.commit()

        print(
            f"Old records replaced with "
            f"{len(df)} new records."
        )

    # --------------------------------------------------
    # 13. Summary
    # --------------------------------------------------
    cursor.execute(
        "SELECT COUNT(*) FROM dmepos_fee_schedule"
    )

    total_records = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM dme_releases"
    )

    total_releases = cursor.fetchone()[0]

    print(f"Total database records: {total_records}")
    print(f"Total releases stored: {total_releases}")

    conn.close()

    print("=" * 50)
    print("DATABASE LOAD COMPLETED")
    print("=" * 50)

    return "loaded"


# ======================================================
# STANDALONE TEST
# ======================================================

if __name__ == "__main__":

    INPUT_FILE = "output\\dmepos_normalized.csv"
    DATABASE = "output\\cms_dmepos.db"
    RELEASE = "DME26-A"

    load_dme_to_database(
        INPUT_FILE,
        DATABASE,
        RELEASE
    )