import pandas as pd
from pathlib import Path
import re


# ============================================================
# CONFIGURATION
# ============================================================

ANESTHESIA_DIR = Path("downloads/anesthesia")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "anesthesia_3year_clean.csv"


# ============================================================
# FIND EXCEL FILES
# ============================================================

def find_excel_files():

    files = [
        file
        for file in ANESTHESIA_DIR.rglob("*.xlsx")
        if "__MACOSX" not in str(file)
        and not file.name.startswith("~$")
    ]

    print(f"\n[OK] Anesthesia Excel files found: {len(files)}")

    for file in files:
        print(f" - {file}")

    return files


# ============================================================
# DETECT YEAR
# ============================================================

def detect_year(file_path):

    match = re.search(
        r"(20\d{2})",
        file_path.name
    )

    if match:
        return int(match.group(1))

    return None


# ============================================================
# DETECT HEADER ROW
# ============================================================

def detect_header_row(file_path):

    preview = pd.read_excel(
        file_path,
        sheet_name="Locality Adjusted CFs",
        header=None
    )

    required = {
        "Contractor",
        "Locality",
        "Locality Name"
    }

    for index, row in preview.iterrows():

        values = {
            str(value).strip()
            for value in row.dropna()
        }

        if required.issubset(values):

            return index

    return None


# ============================================================
# DETECT EFFECTIVE DATES
# ============================================================

def detect_effective_dates(file_path):

    filename = file_path.name

    # 2024 Jan 1 - March 8
    if re.search(
        r"Jan 1-March 8",
        filename,
        re.IGNORECASE
    ):

        return (
            "2024-01-01",
            "2024-03-08"
        )

    # 2024 March 9 - December 31
    if re.search(
        r"March 9-December 31",
        filename,
        re.IGNORECASE
    ):

        return (
            "2024-03-09",
            "2024-12-31"
        )

    # 2025
    if "2025" in filename:

        return (
            "2025-01-01",
            "2025-12-31"
        )

    # 2026
    if "2026" in filename:

        return (
            "2026-01-01",
            "2026-12-31"
        )

    return (
        None,
        None
    )


# ============================================================
# FIND CONVERSION FACTOR COLUMNS
# ============================================================

def find_conversion_columns(columns):

    national_cf = None
    non_qualifying_cf = None
    qualifying_cf = None

    for column in columns:

        column_text = str(column).strip()

        # 2024 / 2025
        if (
            "National Anes CF" in column_text
            and "Non-Qualifying" not in column_text
            and "Qualifying" not in column_text
        ):

            national_cf = column

        # 2026
        if (
            "Non-Qualifying APM National Anes CF"
            in column_text
        ):

            non_qualifying_cf = column

        if (
            "Qualifying APM National Anes CF"
            in column_text
        ):

            qualifying_cf = column

    return (
        national_cf,
        non_qualifying_cf,
        qualifying_cf
    )


# ============================================================
# PARSE ONE FILE
# ============================================================

def parse_file(file_path):

    print("\n" + "-" * 60)
    print(f"Processing: {file_path.name}")
    print("-" * 60)

    # --------------------------------------------------------
    # Detect year
    # --------------------------------------------------------

    year = detect_year(file_path)

    if year is None:

        print(
            "[WARNING] Could not detect year."
        )

        return None

    print(
        f"[OK] Pricing year: {year}"
    )

    # --------------------------------------------------------
    # Detect header
    # --------------------------------------------------------

    header_row = detect_header_row(
        file_path
    )

    if header_row is None:

        print(
            "[ERROR] Could not detect header row."
        )

        return None

    print(
        f"[OK] Header row: {header_row + 1}"
    )

    # --------------------------------------------------------
    # Read Excel
    # --------------------------------------------------------

    try:

        df = pd.read_excel(
            file_path,
            sheet_name="Locality Adjusted CFs",
            header=header_row
        )

    except Exception as error:

        print(
            f"[ERROR] Could not read file: {error}"
        )

        return None

    # --------------------------------------------------------
    # Remove empty rows and columns
    # --------------------------------------------------------

    df = df.dropna(
        how="all"
    ).copy()

    df = df.dropna(
        axis=1,
        how="all"
    )

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Detect conversion factor columns
    # --------------------------------------------------------

    (
        national_cf,
        non_qualifying_cf,
        qualifying_cf
    ) = find_conversion_columns(
        df.columns
    )

    # --------------------------------------------------------
    # Build standardized dataset
    # --------------------------------------------------------

    # IMPORTANT:
    # Use the same index as df so scalar values correctly
    # populate every row.

    result = pd.DataFrame(
        index=df.index
    )

    # --------------------------------------------------------
    # Pricing year
    # --------------------------------------------------------

    result["PRICING_YEAR"] = year

    # --------------------------------------------------------
    # Effective dates
    # --------------------------------------------------------

    effective_from, effective_to = (
        detect_effective_dates(file_path)
    )

    result["EFFECTIVE_FROM"] = effective_from
    result["EFFECTIVE_TO"] = effective_to

    # --------------------------------------------------------
    # Contractor
    # --------------------------------------------------------

    result["MDCR_CARRIER_ID"] = (
        df["Contractor"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Locality
    # --------------------------------------------------------

    result["MDCR_FEE_SCHD_ID"] = (
        df["Locality"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Locality name
    # --------------------------------------------------------

    result["LOCALITY_NAME"] = (
        df["Locality Name"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Standard conversion factor
    # --------------------------------------------------------

    if national_cf is not None:

        result["CONV_FACTOR_AMT"] = (
            pd.to_numeric(
                df[national_cf],
                errors="coerce"
            )
        )

    else:

        result["CONV_FACTOR_AMT"] = pd.NA

    # --------------------------------------------------------
    # Non-Qualifying APM conversion factor
    # --------------------------------------------------------

    if non_qualifying_cf is not None:

        result["NON_QUALIFYING_CONV_FACTOR"] = (
            pd.to_numeric(
                df[non_qualifying_cf],
                errors="coerce"
            )
        )

    else:

        result["NON_QUALIFYING_CONV_FACTOR"] = pd.NA

    # --------------------------------------------------------
    # Qualifying APM conversion factor
    # --------------------------------------------------------

    if qualifying_cf is not None:

        result["QUALIFYING_CONV_FACTOR"] = (
            pd.to_numeric(
                df[qualifying_cf],
                errors="coerce"
            )
        )

    else:

        result["QUALIFYING_CONV_FACTOR"] = pd.NA

    # --------------------------------------------------------
    # Source file
    # --------------------------------------------------------

    result["SOURCE_FILE"] = file_path.name

    # --------------------------------------------------------
    # Remove invalid records
    # --------------------------------------------------------

    result = result[
        result["MDCR_CARRIER_ID"].notna()
    ].copy()

    result = result[
        result["MDCR_CARRIER_ID"] != "nan"
    ].copy()

    print(
        f"[OK] Records parsed: {len(result)}"
    )

    return result


# ============================================================
# PARSE ALL FILES
# ============================================================

def parse_all_files():

    files = find_excel_files()

    if not files:

        print(
            "[ERROR] No Anesthesia Excel files found."
        )

        return None

    datasets = []

    for file_path in files:

        df = parse_file(
            file_path
        )

        if df is not None:

            datasets.append(
                df
            )

    if not datasets:

        print(
            "[ERROR] No files could be parsed."
        )

        return None

    # --------------------------------------------------------
    # Combine all years/files
    # --------------------------------------------------------

    combined = pd.concat(
        datasets,
        ignore_index=True
    )

    return combined


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_output(df):

    try:

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            f"\n[OK] Output saved: "
            f"{OUTPUT_FILE}"
        )

        return True

    except Exception as error:

        print(
            f"[ERROR] Could not save output: {error}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("CMS ANESTHESIA 3-YEAR PARSER")
    print("=" * 60)

    # --------------------------------------------------------
    # Parse all files
    # --------------------------------------------------------

    df = parse_all_files()

    if df is None:

        return False

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PARSER SUMMARY")
    print("=" * 60)

    print(
        f"Total records: {len(df)}"
    )

    # --------------------------------------------------------
    # Records by year
    # --------------------------------------------------------

    print("\nRecords by pricing year:")

    print(
        df["PRICING_YEAR"]
        .value_counts()
        .sort_index()
    )

    # --------------------------------------------------------
    # Records by source file
    # --------------------------------------------------------

    print("\nRecords by source file:")

    print(
        df["SOURCE_FILE"]
        .value_counts()
    )

    # --------------------------------------------------------
    # Sample
    # --------------------------------------------------------

    print("\nSample records:")

    print(
        df.head(10).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    if not save_output(df):

        return False

    print("\n")
    print("=" * 60)
    print("ANESTHESIA 3-YEAR PARSING COMPLETED")
    print("=" * 60)

    return True


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    success = main()

    if not success:

        raise SystemExit(1)