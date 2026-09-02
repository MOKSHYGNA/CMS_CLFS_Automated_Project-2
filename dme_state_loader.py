import sqlite3
import pandas as pd
import re
from pathlib import Path


DB_FILE = Path("cms_clfs.db")
DME_ROOT = Path("dme_downloads")


# ============================================================
# CREATE TABLE
# ============================================================

def create_dme_state_table(conn):

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_state_pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            mod TEXT,
            mod2 TEXT,
            state TEXT,
            pricing_type TEXT,
            allowance TEXT,
            fee_year INTEGER,
            quarter TEXT,
            release TEXT,
            source_file TEXT
        )
    """)

    conn.commit()


# ============================================================
# FIND HEADER ROW
# ============================================================

def find_header_row(file_path):

    preview = pd.read_csv(
        file_path,
        header=None,
        dtype=str,
        nrows=30
    )

    for index, row in preview.iterrows():

        values = (
            row
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        if "HCPCS" in values:
            return index

    return None


# ============================================================
# GET RELEASE INFORMATION
# ============================================================

def get_release_info(file_path):

    release_name = file_path.parent.parent.name
    release_upper = release_name.upper()

    year = None
    quarter = None

    match = re.fullmatch(
        r"DME(24|25|26)-([A-D])",
        release_upper
    )

    if match:

        year = int(
            "20" + match.group(1)
        )

        quarter_map = {
            "A": "Q1",
            "B": "Q2",
            "C": "Q3",
            "D": "Q4"
        }

        quarter = quarter_map[
            match.group(2)
        ]

    return year, quarter, release_name


# ============================================================
# GET ONLY DME 2024-2026 FILES
# ============================================================

def get_dme_files():

    valid_releases = {
        "DME24-A",
        "DME24-B",
        "DME24-C",
        "DME24-D",
        "DME25-A",
        "DME25-B",
        "DME25-C",
        "DME25-D",
        "DME26-A",
        "DME26-B",
        "DME26-C"
    }

    files = []

    for file_path in DME_ROOT.rglob("DMEPOS*.csv"):

        release_name = file_path.parent.parent.name.upper()

        if release_name in valid_releases:

            files.append(file_path)

    return sorted(files)


# ============================================================
# LOAD STATE PRICING
# ============================================================

def load_dme_state_pricing():

    print()
    print("=" * 60)
    print("DME STATE PRICING LOADER")
    print("=" * 60)

    csv_files = get_dme_files()

    print(
        f"Found DMEPOS CSV files: {len(csv_files)}"
    )

    if not csv_files:

        print(
            "No DME 2024-2026 CSV files found."
        )

        return

    conn = sqlite3.connect(DB_FILE)

    # Create table automatically if it does not exist.
    create_dme_state_table(conn)

    cursor = conn.cursor()

    # Clear previous data so the loader is rerunnable.
    cursor.execute(
        "DELETE FROM dme_state_pricing"
    )

    conn.commit()

    total_records = 0

    # ========================================================
    # PROCESS FILES
    # ========================================================

    for file_path in csv_files:

        print()
        print(
            f"Processing: {file_path}"
        )

        try:

            # ------------------------------------------------
            # Find header
            # ------------------------------------------------

            header_row = find_header_row(
                file_path
            )

            if header_row is None:

                print(
                    "[WARNING] HCPCS header not found."
                )

                continue

            print(
                f"Header row found at: {header_row}"
            )

            # ------------------------------------------------
            # Read CSV
            # ------------------------------------------------

            df = pd.read_csv(
                file_path,
                header=header_row,
                dtype=str,
                keep_default_na=False
            )

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            # ------------------------------------------------
            # Release information
            # ------------------------------------------------

            year, quarter, release = (
                get_release_info(file_path)
            )

            # ------------------------------------------------
            # Find state pricing columns
            # ------------------------------------------------

            state_columns = []

            state_pattern = re.compile(
                r"^([A-Z]{2})\s*\((NR|R)\)$",
                re.IGNORECASE
            )

            for column in df.columns:

                match = state_pattern.match(
                    str(column).strip()
                )

                if match:

                    state = (
                        match.group(1)
                        .upper()
                    )

                    pricing_type = (
                        match.group(2)
                        .upper()
                    )

                    state_columns.append(
                        (
                            column,
                            state,
                            pricing_type
                        )
                    )

            if not state_columns:

                print(
                    "[WARNING] "
                    "No state pricing columns found."
                )

                continue

            print(
                f"State pricing columns found: "
                f"{len(state_columns)}"
            )

            # ------------------------------------------------
            # Process records
            # ------------------------------------------------

            rows_to_insert = []

            for _, row in df.iterrows():

                hcpcs = str(
                    row.get(
                        "HCPCS",
                        ""
                    )
                ).strip()

                if not hcpcs:
                    continue

                if hcpcs.upper() == "NAN":
                    continue

                mod = str(
                    row.get(
                        "Mod",
                        ""
                    )
                ).strip()

                mod2 = str(
                    row.get(
                        "Mod2",
                        ""
                    )
                ).strip()

                for (
                    column,
                    state,
                    pricing_type
                ) in state_columns:

                    allowance = str(
                        row.get(
                            column,
                            ""
                        )
                    ).strip()

                    if not allowance:
                        continue

                    rows_to_insert.append(
                        (
                            hcpcs,
                            mod,
                            mod2,
                            state,
                            pricing_type,
                            allowance,
                            year,
                            quarter,
                            release,
                            file_path.name
                        )
                    )

            # ------------------------------------------------
            # Insert records
            # ------------------------------------------------

            cursor.executemany(
                """
                INSERT INTO dme_state_pricing (
                    hcpcs,
                    mod,
                    mod2,
                    state,
                    pricing_type,
                    allowance,
                    fee_year,
                    quarter,
                    release,
                    source_file
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows_to_insert
            )

            conn.commit()

            record_count = len(
                rows_to_insert
            )

            total_records += record_count

            print(
                f"Records loaded: {record_count}"
            )

        except Exception as error:

            print(
                f"[ERROR] Processing: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    conn.close()

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("DME STATE PRICING SUMMARY")
    print("=" * 60)

    print(
        f"Total records loaded: {total_records}"
    )

    print(
        "Table: dme_state_pricing"
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    load_dme_state_pricing()