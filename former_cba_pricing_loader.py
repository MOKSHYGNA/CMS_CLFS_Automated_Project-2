import sqlite3
import pandas as pd
import re
from pathlib import Path


DB_FILE = Path("cms_clfs.db")
DME_ROOT = Path("dme_downloads")


# ============================================================
# CREATE TABLE
# ============================================================

def create_former_cba_pricing_table(conn):

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_former_cba_pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            mod TEXT,
            mod2 TEXT,
            mod3 TEXT,
            catg TEXT,
            cba_name TEXT,
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

        # Different Former CBA files may use
        # slightly different wording.
        if (
            "HCPCS" in values
            or "HCPCS CODE" in values
            or "HCPCS CD" in values
        ):
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
# GET FORMER CBA FILES
# ============================================================

def get_former_cba_files():

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

    for file_path in DME_ROOT.rglob("*.csv"):

        filename = file_path.name.upper()

        # Only Former CBA Fee Schedule files.
        if "FORMER CBA FEE" not in filename:
            continue

        release_name = (
            file_path.parent.parent.name.upper()
        )

        if release_name in valid_releases:

            files.append(file_path)

    return sorted(files)


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(df, possible_names):

    normalized_columns = {
        re.sub(
            r"[^A-Z0-9]",
            "",
            str(column).upper()
        ): column
        for column in df.columns
    }

    for name in possible_names:

        normalized_name = re.sub(
            r"[^A-Z0-9]",
            "",
            name.upper()
        )

        if normalized_name in normalized_columns:

            return normalized_columns[
                normalized_name
            ]

    return None


# ============================================================
# LOAD FORMER CBA PRICING
# ============================================================

def load_former_cba_pricing():

    print()
    print("=" * 60)
    print("FORMER CBA PRICING LOADER")
    print("=" * 60)

    csv_files = get_former_cba_files()

    print(
        f"Found Former CBA Fee CSV files: "
        f"{len(csv_files)}"
    )

    if not csv_files:

        print(
            "No Former CBA Fee Schedule files found."
        )

        return

    conn = sqlite3.connect(DB_FILE)

    # Automatically create the table.
    create_former_cba_pricing_table(conn)

    cursor = conn.cursor()

    # Clear old data so the loader can be rerun.
    cursor.execute(
        "DELETE FROM dme_former_cba_pricing"
    )

    conn.commit()

    total_records = 0

    # ========================================================
    # PROCESS EACH FILE
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
                    "[WARNING] Header not found."
                )

                continue

            print(
                f"Header row found at: "
                f"{header_row}"
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
            # Identify columns
            # ------------------------------------------------

            hcpcs_column = find_column(
                df,
                [
                    "HCPCS",
                    "HCPCS CODE",
                    "HCPCS CD",
                    "PROCEDURE CODE",
                    "PROCEDURE CD"
                ]
            )

            mod_column = find_column(
                df,
                [
                    "MOD",
                    "MODIFIER",
                    "MODIFIER 1",
                    "MOD CD1"
                ]
            )

            mod2_column = find_column(
                df,
                [
                    "MOD2",
                    "MODIFIER 2",
                    "MODIFIER2",
                    "MOD CD2"
                ]
            )

            mod3_column = find_column(
                df,
                [
                    "MOD3",
                    "MODIFIER 3",
                    "MODIFIER3",
                    "MOD CD3"
                ]
            )

            catg_column = find_column(
                df,
                [
                    "CATG",
                    "CATEGORY",
                    "CAT"
                ]
            )

            # ------------------------------------------------
            # Check HCPCS
            # ------------------------------------------------

            if hcpcs_column is None:

                print(
                    "[WARNING] "
                    "HCPCS column not found."
                )

                continue

            # ------------------------------------------------
            # Find CBA pricing columns
            # ------------------------------------------------

            # Former CBA files contain multiple CBA/location
            # allowance columns. We identify them as columns
            # that are not the normal descriptive columns.

            excluded_columns = {
                column
                for column in [
                    hcpcs_column,
                    mod_column,
                    mod2_column,
                    mod3_column,
                    catg_column
                ]
                if column is not None
            }

            # Common descriptive columns that should not
            # be treated as pricing columns.
            descriptive_words = [
                "DESCRIPTION",
                "LONGDESC",
                "SHORTDESC",
                "EFFECTIVE",
                "DATE",
                "YEAR",
                "QUARTER",
                "CBA"
            ]

            pricing_columns = []

            for column in df.columns:

                if column in excluded_columns:
                    continue

                column_upper = str(
                    column
                ).upper()

                if any(
                    word in column_upper
                    for word in descriptive_words
                ):
                    continue

                pricing_columns.append(
                    column
                )

            if not pricing_columns:

                print(
                    "[WARNING] "
                    "No CBA pricing columns found."
                )

                continue

            print(
                f"CBA pricing columns found: "
                f"{len(pricing_columns)}"
            )

            # ------------------------------------------------
            # Release information
            # ------------------------------------------------

            year, quarter, release = (
                get_release_info(file_path)
            )

            # ------------------------------------------------
            # Prepare records
            # ------------------------------------------------

            rows_to_insert = []

            for _, row in df.iterrows():

                hcpcs = str(
                    row.get(
                        hcpcs_column,
                        ""
                    )
                ).strip()

                if not hcpcs:
                    continue

                if hcpcs.upper() == "NAN":
                    continue

                mod = ""

                if mod_column is not None:

                    mod = str(
                        row.get(
                            mod_column,
                            ""
                        )
                    ).strip()

                mod2 = ""

                if mod2_column is not None:

                    mod2 = str(
                        row.get(
                            mod2_column,
                            ""
                        )
                    ).strip()

                mod3 = ""

                if mod3_column is not None:

                    mod3 = str(
                        row.get(
                            mod3_column,
                            ""
                        )
                    ).strip()

                catg = ""

                if catg_column is not None:

                    catg = str(
                        row.get(
                            catg_column,
                            ""
                        )
                    ).strip()

                # ------------------------------------------------
                # Each CBA pricing column becomes one record.
                # ------------------------------------------------

                for pricing_column in pricing_columns:

                    allowance = str(
                        row.get(
                            pricing_column,
                            ""
                        )
                    ).strip()

                    if not allowance:
                        continue

                    # Column name represents the CBA location.
                    cba_name = str(
                        pricing_column
                    ).strip()

                    rows_to_insert.append(
                        (
                            hcpcs,
                            mod,
                            mod2,
                            mod3,
                            catg,
                            cba_name,
                            allowance,
                            year,
                            quarter,
                            release,
                            file_path.name
                        )
                    )

            # ------------------------------------------------
            # Insert
            # ------------------------------------------------

            cursor.executemany(
                """
                INSERT INTO dme_former_cba_pricing (
                    hcpcs,
                    mod,
                    mod2,
                    mod3,
                    catg,
                    cba_name,
                    allowance,
                    fee_year,
                    quarter,
                    release,
                    source_file
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows_to_insert
            )

            conn.commit()

            record_count = len(
                rows_to_insert
            )

            total_records += record_count

            print(
                f"Records loaded: "
                f"{record_count}"
            )

        except Exception as error:

            print(
                f"[ERROR] Processing: "
                f"{file_path}"
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
    print("FORMER CBA PRICING SUMMARY")
    print("=" * 60)

    print(
        f"Total records loaded: "
        f"{total_records}"
    )

    print(
        "Table: dme_former_cba_pricing"
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    load_former_cba_pricing()