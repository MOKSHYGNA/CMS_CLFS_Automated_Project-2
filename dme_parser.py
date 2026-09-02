import pandas as pd
from pathlib import Path
import re


DME_ROOT = Path("dme_downloads")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# ALLOWED DME RELEASES
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
# GET ONLY SUPPORTED DME FILES
# ============================================================

def get_dme_files():

    files = []

    for file_path in DME_ROOT.rglob("DMEPOS*.csv"):

        release_name = (
            file_path.parent.parent.name.upper()
        )

        if release_name in VALID_RELEASES:

            files.append(file_path)

    return sorted(files)


# ============================================================
# CLEAN DME DATA
# ============================================================

def clean_dme_data(df):

    # Remove completely empty columns.
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Clean column names.
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Remove completely empty rows.
    df = df.dropna(
        how="all"
    )

    # Keep only real HCPCS records.
    if "HCPCS" in df.columns:

        df["HCPCS"] = (
            df["HCPCS"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df = df[
            (df["HCPCS"] != "") &
            (df["HCPCS"].str.upper() != "NAN")
        ]

    # Convert blank values to NULL.
    df = df.replace(
        ["", "nan", "NaN", "None"],
        pd.NA
    )

    return df


# ============================================================
# PARSE ONE DME FILE
# ============================================================

def parse_dme_file(file_path):

    print()
    print(
        f"Processing: {file_path}"
    )

    header_row = find_header_row(
        file_path
    )

    if header_row is None:

        print(
            "ERROR: HCPCS header not found."
        )

        return None

    print(
        f"Header row found at: {header_row}"
    )

    df = pd.read_csv(
        file_path,
        header=header_row,
        dtype=str,
        keep_default_na=False
    )

    df = clean_dme_data(df)

    year, quarter, release = (
        get_release_info(file_path)
    )

    df["FEE_YEAR"] = year
    df["QUARTER"] = quarter
    df["RELEASE"] = release
    df["SOURCE_FILE"] = file_path.name

    return df


# ============================================================
# PARSE ALL DME FILES
# ============================================================

def parse_all_dme_files():

    print()
    print("=" * 60)
    print("DME PARSER")
    print("=" * 60)

    files = get_dme_files()

    print(
        f"Found DMEPOS CSV files: {len(files)}"
    )

    if not files:

        print(
            "No supported DMEPOS CSV files found."
        )

        return None

    all_data = []

    # --------------------------------------------------------
    # Process each supported release
    # --------------------------------------------------------

    for file_path in files:

        try:

            df = parse_dme_file(
                file_path
            )

            if (
                df is not None
                and not df.empty
            ):

                print(
                    f"Records loaded: "
                    f"{len(df)}"
                )

                all_data.append(df)

        except Exception as error:

            print(
                f"ERROR processing: "
                f"{file_path}"
            )

            print(
                f"Reason: {error}"
            )

    # --------------------------------------------------------
    # Check results
    # --------------------------------------------------------

    if not all_data:

        print(
            "No DME records were parsed."
        )

        return None

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    combined = pd.concat(
        all_data,
        ignore_index=True,
        sort=False
    )

    before = len(
        combined
    )

    combined = combined.drop_duplicates()

    after = len(
        combined
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("DME PARSING SUMMARY")
    print("=" * 60)

    print(
        f"Rows before duplicate removal: "
        f"{before}"
    )

    print(
        f"Rows after duplicate removal : "
        f"{after}"
    )

    print(
        f"Columns                      : "
        f"{len(combined.columns)}"
    )

    print()
    print("Release summary:")

    release_summary = (
        combined
        .groupby(
            [
                "FEE_YEAR",
                "QUARTER",
                "RELEASE"
            ]
        )
        .size()
        .reset_index(
            name="RECORDS"
        )
    )

    print(
        release_summary.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Sample records
    # --------------------------------------------------------

    print()
    print("Sample records:")

    sample_columns = [
        "HCPCS",
        "Mod",
        "Mod2",
        "JURIS",
        "CATG",
        "Ceiling",
        "Floor",
        "Description",
        "FEE_YEAR",
        "QUARTER",
        "RELEASE"
    ]

    sample_columns = [
        column
        for column in sample_columns
        if column in combined.columns
    ]

    print(
        combined[
            sample_columns
        ].head(10).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR /
        "dme_combined.csv"
    )

    combined.to_csv(
        output_file,
        index=False
    )

    print()
    print("Output created:")
    print(output_file)

    return combined


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    parse_all_dme_files()