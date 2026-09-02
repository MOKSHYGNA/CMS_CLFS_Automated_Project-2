
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DOWNLOADS_FOLDER = Path("downloads")
OUTPUT_FOLDER = Path("output")

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# STANDARD COLUMN NAMES
# --------------------------------------------------

COLUMNS = [
    "YEAR",
    "HCPCS",
    "MOD",
    "EFF_DATE",
    "INDICATOR",
    "RATE",
    "SHORTDESC",
    "LONGDESC",
    "EXTENDED_LONGDESC"
]


# --------------------------------------------------
# FIND HEADER ROW
# --------------------------------------------------

def find_header_row(csv_file):

    # Read the file as raw text first.
    # This allows us to handle different CMS CSV formats.

    with open(
        csv_file,
        "r",
        encoding="latin1",
        errors="replace"
    ) as file:

        lines = file.readlines()

    for index, line in enumerate(lines):

        upper_line = line.upper()

        if (
            "YEAR" in upper_line
            and "HCPCS" in upper_line
            and "EFF_DATE" in upper_line
            and "RATE" in upper_line
        ):

            return index

    return None


# --------------------------------------------------
# READ CMS CSV
# --------------------------------------------------

def read_cms_csv(csv_file):

    print(f"\nReading: {csv_file}")

    header_row = find_header_row(
        csv_file
    )

    if header_row is None:

        raise ValueError(
            f"Could not find CMS header in {csv_file}"
        )

    print(
        f"[INFO] Header row: {header_row + 1}"
    )

    # --------------------------------------------------
    # Try normal CSV reading
    # --------------------------------------------------

    try:

        df = pd.read_csv(
            csv_file,
            skiprows=header_row,
            encoding="latin1",
            engine="python"
        )

    except Exception as error:

        raise ValueError(
            f"Could not read CSV: {error}"
        )

    # --------------------------------------------------
    # Remove completely empty columns
    # --------------------------------------------------

    df = df.dropna(
        axis=1,
        how="all"
    )

    # --------------------------------------------------
    # Clean column names
    # --------------------------------------------------

    cleaned_columns = []

    for column in df.columns:

        column_name = str(
            column
        ).strip().upper()

        column_name = column_name.replace(
            " ",
            "_"
        )

        cleaned_columns.append(
            column_name
        )

    df.columns = cleaned_columns

    # --------------------------------------------------
    # Normalize EXTENDED LONG DESCRIPTION
    # --------------------------------------------------

    if "EXTENDEDLONGDESC" in df.columns:

        df = df.rename(
            columns={
                "EXTENDEDLONGDESC":
                "EXTENDED_LONGDESC"
            }
        )

    # --------------------------------------------------
    # Handle unexpected column count
    # --------------------------------------------------

    if len(df.columns) > len(COLUMNS):

        # Keep only the expected CMS columns
        df = df.iloc[:, :len(COLUMNS)]

    elif len(df.columns) < len(COLUMNS):

        # Add missing columns
        while len(df.columns) < len(COLUMNS):

            df[
                f"EXTRA_{len(df.columns)}"
            ] = ""

        df = df.iloc[:, :len(COLUMNS)]

    # Assign standard column names

    df.columns = COLUMNS

    # --------------------------------------------------
    # REMOVE EMPTY ROWS
    # --------------------------------------------------

    df = df.dropna(
        how="all"
    )

    # --------------------------------------------------
    # CLEAN TEXT COLUMNS
    # --------------------------------------------------

    text_columns = [
        "HCPCS",
        "MOD",
        "INDICATOR",
        "SHORTDESC",
        "LONGDESC",
        "EXTENDED_LONGDESC"
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------
    # CLEAN YEAR
    # --------------------------------------------------

    df["YEAR"] = pd.to_numeric(
        df["YEAR"],
        errors="coerce"
    )

    # --------------------------------------------------
    # CLEAN EFFECTIVE DATE
    # --------------------------------------------------

    df["EFF_DATE"] = pd.to_numeric(
        df["EFF_DATE"],
        errors="coerce"
    )

    # --------------------------------------------------
    # CLEAN RATE
    # --------------------------------------------------

    df["RATE"] = (
        df["RATE"]
        .fillna("")
        .astype(str)
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.strip()
    )

    df["RATE"] = pd.to_numeric(
        df["RATE"],
        errors="coerce"
    )

    # --------------------------------------------------
    # REMOVE INVALID RECORDS
    # --------------------------------------------------

    df = df[
        df["HCPCS"].str.strip() != ""
    ]

    # Remove rows where HCPCS is literally "HCPCS"

    df = df[
        df["HCPCS"].str.upper() != "HCPCS"
    ]

    print(
        f"[OK] Rows loaded: {len(df)}"
    )

    print(
        f"[OK] Columns: {len(df.columns)}"
    )

    return df


# --------------------------------------------------
# FIND ALL CSV FILES
# --------------------------------------------------
def find_csv_files():

    csv_files = sorted(
        file
        for file in DOWNLOADS_FOLDER.rglob("*.csv")
        if "anesthesia" not in {
            part.lower()
            for part in file.parts
        }
    )

    print(
        f"\n[INFO] CLFS CSV files found: {len(csv_files)}"
    )

    for csv_file in csv_files:
        print(
            f"  - {csv_file}"
        )

    return csv_files

# --------------------------------------------------
# MAIN ETL PIPELINE
# --------------------------------------------------

def main():

    print("\n")
    print("=" * 60)
    print("CMS CLFS ETL PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # EXTRACT
    # --------------------------------------------------

    csv_files = find_csv_files()

    if not csv_files:

        print(
            "[ERROR] No CSV files found."
        )

        return

    # --------------------------------------------------
    # TRANSFORM
    # --------------------------------------------------

    dataframes = []

    for csv_file in csv_files:

        try:

            df = read_cms_csv(
                csv_file
            )

            # Add source file
            df["SOURCE_FILE"] = (
                csv_file.name
            )

            dataframes.append(
                df
            )

        except Exception as error:

            print(
                f"[ERROR] Failed to process "
                f"{csv_file}: {error}"
            )

    # --------------------------------------------------
    # CHECK WHETHER DATA WAS FOUND
    # --------------------------------------------------

    if not dataframes:

        print(
            "[ERROR] No data could be processed."
        )

        return

    # --------------------------------------------------
    # COMBINE ALL DATA
    # --------------------------------------------------

    final_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    # --------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------

    before = len(
        final_df
    )

    final_df = final_df.drop_duplicates()

    after = len(
        final_df
    )

    print(
        f"\n[INFO] Rows before duplicate removal: "
        f"{before}"
    )

    print(
        f"[INFO] Rows after duplicate removal: "
        f"{after}"
    )

    # --------------------------------------------------
    # FINAL COLUMN ORDER
    # --------------------------------------------------

    final_columns = [
        "YEAR",
        "HCPCS",
        "MOD",
        "EFF_DATE",
        "INDICATOR",
        "RATE",
        "SHORTDESC",
        "LONGDESC",
        "EXTENDED_LONGDESC",
        "SOURCE_FILE"
    ]

    final_df = final_df[
        final_columns
    ]

    # --------------------------------------------------
    # LOAD
    # --------------------------------------------------

    output_file = (
        OUTPUT_FOLDER /
        "cms_clfs_combined.csv"
    )

    final_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\n[OK] Clean dataset created:"
    )

    print(
        f"     {output_file}"
    )

    print(
        f"[OK] Total rows: {len(final_df)}"
    )

    print(
        f"[OK] Total columns: {len(final_df.columns)}"
    )

    # --------------------------------------------------
    # SAMPLE DATA
    # --------------------------------------------------

    print("\nSample data:")

    print(
        final_df.head(5).to_string(
            index=False
        )
    )

    print("\n")
    print("=" * 60)
    print("ETL PIPELINE COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# RUN PIPELINE
# --------------------------------------------------

if __name__ == "__main__":
    main()

