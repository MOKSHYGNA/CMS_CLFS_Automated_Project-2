import sqlite3
import pandas as pd
from pathlib import Path
import re


DB_FILE = "cms_clfs.db"
DME_ROOT = Path("dme_downloads")


# ============================================================
# SUPPORTED DME RELEASES
# ============================================================

VALID_RELEASES = {
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


# ============================================================
# DATABASE TABLES
# ============================================================

TABLES = [
    "dme_fee_schedule",
    "dme_pen_schedule",
    "dme_rural_zip",
    "dme_former_cba_fee",
    "dme_former_cba_zip",
    "dme_mail_order_dts"
]


# ============================================================
# GET RELEASE INFORMATION
# ============================================================

def get_release_info(file_path):

    release_name = file_path.parent.parent.name.upper()

    match = re.fullmatch(
        r"DME(24|25|26)-([A-D])",
        release_name
    )

    if not match:
        return None, None, None

    year = int("20" + match.group(1))

    quarter_map = {
        "A": "Q1",
        "B": "Q2",
        "C": "Q3",
        "D": "Q4"
    }

    quarter = quarter_map[match.group(2)]

    return year, quarter, release_name


# ============================================================
# GET ONLY SUPPORTED FILES
# ============================================================

def get_supported_files(pattern):

    files = []

    for file_path in DME_ROOT.rglob(pattern):

        release_name = file_path.parent.parent.name.upper()

        if release_name in VALID_RELEASES:
            files.append(file_path)

    return sorted(files)


# ============================================================
# FIND HEADER ROW
# ============================================================

def find_header_row(file_path, required_column):

    try:

        preview = pd.read_csv(
            file_path,
            header=None,
            dtype=str,
            nrows=30,
            keep_default_na=False
        )

    except Exception:
        return None

    for index, row in preview.iterrows():

        values = (
            row
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        if required_column in values:
            return index

    return None


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(DB_FILE)


# ============================================================
# CLEAR EXISTING DME BASE TABLES
# ============================================================

def clear_tables():

    connection = get_connection()
    cursor = connection.cursor()

    for table in TABLES:

        cursor.execute(
            f"DELETE FROM {table}"
        )

    connection.commit()
    connection.close()

    print()
    print("Existing DME base-table records cleared.")


# ============================================================
# LOAD MAIN DMEPOS
# ============================================================

def load_dme_fee_schedule():

    files = get_supported_files(
        "DMEPOS*.csv"
    )

    print()
    print("=" * 60)
    print("DME FEE SCHEDULE")
    print("=" * 60)

    print(
        f"Found supported DMEPOS files: {len(files)}"
    )

    connection = get_connection()

    total = 0

    for file_path in files:

        try:

            header_row = find_header_row(
                file_path,
                "HCPCS"
            )

            if header_row is None:

                print(
                    f"Header not found: {file_path}"
                )

                continue

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

            if "HCPCS" not in df.columns:
                continue

            df = df[
                df["HCPCS"]
                .astype(str)
                .str.strip()
                != ""
            ]

            year, quarter, release = (
                get_release_info(file_path)
            )

            output = pd.DataFrame()

            output["hcpcs"] = df.get(
                "HCPCS",
                ""
            )

            output["mod"] = df.get(
                "Mod",
                ""
            )

            output["mod2"] = df.get(
                "Mod2",
                ""
            )

            output["juris"] = df.get(
                "JURIS",
                ""
            )

            output["catg"] = df.get(
                "CATG",
                ""
            )

            output["ceiling"] = df.get(
                "Ceiling",
                ""
            )

            output["floor"] = df.get(
                "Floor",
                ""
            )

            output["description"] = df.get(
                "Description",
                ""
            )

            output["fee_year"] = year
            output["quarter"] = quarter
            output["release"] = release
            output["source_file"] = file_path.name

            output.to_sql(
                "dme_fee_schedule",
                connection,
                if_exists="append",
                index=False
            )

            count = len(output)

            total += count

            print(
                f"{release}: {count:,}"
            )

        except Exception as error:

            print()
            print(
                f"ERROR: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    connection.close()

    print()
    print(
        f"Total DME fee schedule records: {total:,}"
    )


# ============================================================
# LOAD DMEPEN
# ============================================================

def load_dme_pen_schedule():

    files = get_supported_files(
        "DMEPEN*.csv"
    )

    print()
    print("=" * 60)
    print("DMEPEN SCHEDULE")
    print("=" * 60)

    print(
        f"Found supported DMEPEN files: {len(files)}"
    )

    connection = get_connection()

    total = 0

    for file_path in files:

        try:

            header_row = find_header_row(
                file_path,
                "HCPCS"
            )

            if header_row is None:
                continue

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

            if "HCPCS" not in df.columns:
                continue

            df = df[
                df["HCPCS"]
                .astype(str)
                .str.strip()
                != ""
            ]

            year, quarter, release = (
                get_release_info(file_path)
            )

            output = pd.DataFrame()

            output["hcpcs"] = df.get(
                "HCPCS",
                ""
            )

            output["mod"] = df.get(
                "Mod",
                ""
            )

            output["mod2"] = df.get(
                "Mod2",
                ""
            )

            output["description"] = df.get(
                "Description",
                ""
            )

            output["fee_year"] = year
            output["quarter"] = quarter
            output["release"] = release
            output["source_file"] = file_path.name

            output.to_sql(
                "dme_pen_schedule",
                connection,
                if_exists="append",
                index=False
            )

            count = len(output)

            total += count

            print(
                f"{release}: {count:,}"
            )

        except Exception as error:

            print(
                f"ERROR: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    connection.close()

    print(
        f"Total DMEPEN records: {total:,}"
    )


# ============================================================
# LOAD RURAL ZIP
# ============================================================

def load_rural_zip():

    files = get_supported_files(
        "*RURAL*.csv"
    )

    print()
    print("=" * 60)
    print("RURAL ZIP")
    print("=" * 60)

    print(
        f"Found supported rural ZIP files: {len(files)}"
    )

    connection = get_connection()

    total = 0

    for file_path in files:

        try:

            df = pd.read_csv(
                file_path,
                dtype=str,
                keep_default_na=False
            )

            if df.empty:
                continue

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            if len(df.columns) < 2:
                continue

            year, quarter, release = (
                get_release_info(file_path)
            )

            output = pd.DataFrame()

            output["state"] = df.iloc[:, 0]
            output["rural_zip_code"] = df.iloc[:, 1]

            output["year_qtr"] = (
                str(year) + quarter
            )

            output["fee_year"] = year
            output["quarter"] = quarter
            output["source_file"] = file_path.name

            output.to_sql(
                "dme_rural_zip",
                connection,
                if_exists="append",
                index=False
            )

            count = len(output)

            total += count

            print(
                f"{release}: {count:,}"
            )

        except Exception as error:

            print(
                f"ERROR: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    connection.close()

    print(
        f"Total rural ZIP records: {total:,}"
    )


# ============================================================
# FIND FORMER CBA FEE FILES
# ============================================================

def find_former_cba_fee_files():

    candidates = get_supported_files(
        "*Former*CBA*.csv"
    )

    selected = {}

    for file_path in candidates:

        filename = file_path.name.upper()

        # Exclude obvious ZIP/supporting files.
        if "ZIP" in filename:
            continue

        # Exclude DTS/mail-order files.
        if "DTS" in filename:
            continue

        try:

            header_row = find_header_row(
                file_path,
                "HCPCS"
            )

            if header_row is None:
                continue

            preview = pd.read_csv(
                file_path,
                header=header_row,
                dtype=str,
                nrows=5,
                keep_default_na=False
            )

            preview.columns = [
                str(column).strip()
                for column in preview.columns
            ]

            columns = {
                str(column).upper().strip()
                for column in preview.columns
            }

            # The fee file must contain HCPCS and pricing
            # columns. Supporting files with only names,
            # ZIP information, etc. are excluded.
            if "HCPCS" not in columns:
                continue

            pricing_columns = {
                "CATG",
                "MOD",
                "MOD2",
                "MOD3"
            }

            if not columns.intersection(
                pricing_columns
            ):
                continue

            year, quarter, release = (
                get_release_info(file_path)
            )

            if release is None:
                continue

            # Prefer the file with the largest number of
            # columns because the actual Former CBA fee
            # schedule contains the pricing structure.
            column_count = len(preview.columns)

            if (
                release not in selected
                or column_count
                > selected[release][1]
            ):

                selected[release] = (
                    file_path,
                    column_count
                )

        except Exception:
            continue

    return [
        selected[release][0]
        for release in sorted(selected)
    ]


# ============================================================
# LOAD FORMER CBA FEE
# ============================================================

def load_former_cba_fee():

    files = find_former_cba_fee_files()

    print()
    print("=" * 60)
    print("FORMER CBA FEE")
    print("=" * 60)

    print(
        f"Selected Former CBA fee files: {len(files)}"
    )

    connection = get_connection()

    total = 0

    for file_path in files:

        try:

            header_row = find_header_row(
                file_path,
                "HCPCS"
            )

            if header_row is None:
                continue

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

            if "HCPCS" not in df.columns:
                continue

            df = df[
                df["HCPCS"]
                .astype(str)
                .str.strip()
                != ""
            ]

            year, quarter, release = (
                get_release_info(file_path)
            )

            output = pd.DataFrame()

            output["hcpcs"] = df.get(
                "HCPCS",
                ""
            )

            output["mod"] = df.get(
                "Mod",
                ""
            )

            output["mod2"] = df.get(
                "Mod2",
                ""
            )

            output["mod3"] = df.get(
                "Mod3",
                ""
            )

            output["catg"] = df.get(
                "CATG",
                ""
            )

            output["description"] = df.get(
                "Description",
                ""
            )

            output["fee_year"] = year
            output["quarter"] = quarter
            output["release"] = release
            output["source_file"] = file_path.name

            output.to_sql(
                "dme_former_cba_fee",
                connection,
                if_exists="append",
                index=False
            )

            count = len(output)

            total += count

            print(
                f"{release}: "
                f"{count:,} "
                f"({file_path.name})"
            )

        except Exception as error:

            print()
            print(
                f"ERROR: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    connection.close()

    print()
    print(
        f"Total Former CBA fee records: "
        f"{total:,}"
    )


# ============================================================
# LOAD FORMER CBA ZIP
# ============================================================

def load_former_cba_zip():

    files = get_supported_files(
        "*CBA*ZIP*.csv"
    )

    print()
    print("=" * 60)
    print("FORMER CBA ZIP")
    print("=" * 60)

    print(
        f"Found supported Former CBA ZIP files: {len(files)}"
    )

    connection = get_connection()

    total = 0

    for file_path in files:

        try:

            df = pd.read_csv(
                file_path,
                dtype=str,
                keep_default_na=False
            )

            if df.empty:
                continue

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            if len(df.columns) < 2:
                continue

            year, quarter, release = (
                get_release_info(file_path)
            )

            output = pd.DataFrame()

            output["cba_state"] = df.iloc[:, 0]
            output["cba_zip_code"] = df.iloc[:, 1]

            if len(df.columns) > 2:
                output["cba_name_short"] = df.iloc[:, 2]
            else:
                output["cba_name_short"] = ""

            if len(df.columns) > 3:
                output["cba_name"] = df.iloc[:, 3]
            else:
                output["cba_name"] = ""

            output["year_qtr"] = (
                str(year) + quarter
            )

            output["fee_year"] = year
            output["quarter"] = quarter
            output["source_file"] = file_path.name

            output.to_sql(
                "dme_former_cba_zip",
                connection,
                if_exists="append",
                index=False
            )

            count = len(output)

            total += count

            print(
                f"{release}: {count:,}"
            )

        except Exception as error:

            print(
                f"ERROR: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    connection.close()

    print(
        f"Total Former CBA ZIP records: {total:,}"
    )


# ============================================================
# LOAD MAIL ORDER DTS
# ============================================================

def load_mail_order_dts():

    files = get_supported_files(
        "*DTS*.csv"
    )

    print()
    print("=" * 60)
    print("MAIL ORDER DTS")
    print("=" * 60)

    print(
        f"Found supported DTS files: {len(files)}"
    )

    connection = get_connection()

    total = 0

    for file_path in files:

        try:

            header_row = find_header_row(
                file_path,
                "HCPCS"
            )

            if header_row is None:
                continue

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

            if "HCPCS" not in df.columns:
                continue

            df = df[
                df["HCPCS"]
                .astype(str)
                .str.strip()
                != ""
            ]

            year, quarter, release = (
                get_release_info(file_path)
            )

            output = pd.DataFrame()

            output["hcpcs"] = df.get(
                "HCPCS",
                ""
            )

            output["mod"] = df.get(
                "Mod",
                ""
            )

            output["mod2"] = df.get(
                "Mod2",
                ""
            )

            output["mod3"] = df.get(
                "Mod3",
                ""
            )

            output["catg"] = df.get(
                "CATG",
                ""
            )

            output["national_mail_order"] = df.get(
                "National Mail Order",
                ""
            )

            output["description"] = df.get(
                "Description",
                ""
            )

            output["fee_year"] = year
            output["quarter"] = quarter
            output["release"] = release
            output["source_file"] = file_path.name

            output.to_sql(
                "dme_mail_order_dts",
                connection,
                if_exists="append",
                index=False
            )

            count = len(output)

            total += count

            print(
                f"{release}: {count:,}"
            )

        except Exception as error:

            print(
                f"ERROR: {file_path}"
            )

            print(
                f"Reason: {error}"
            )

    connection.close()

    print(
        f"Total mail-order DTS records: {total:,}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("DME DATABASE LOADER")
    print("=" * 60)

    clear_tables()

    load_dme_fee_schedule()
    load_dme_pen_schedule()
    load_rural_zip()
    load_former_cba_fee()
    load_former_cba_zip()
    load_mail_order_dts()

    print()
    print("=" * 60)
    print("DME DATABASE LOADING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()