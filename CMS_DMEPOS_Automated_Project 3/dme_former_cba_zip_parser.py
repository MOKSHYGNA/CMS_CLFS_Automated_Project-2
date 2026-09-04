import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE = (
    BASE_DIR
    / "downloads"
    / "dme26-c"
    / "extracted"
    / "Former CBA ZIP Code File  - JUL2026.csv"
)

DEFAULT_OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "former_cba_zip.csv"
)


def parse_former_cba_zip(
    input_file=None,
    output_file=None
):

    print("=" * 60)
    print("CMS FORMER CBA ZIP CODE PARSER")
    print("=" * 60)

    input_file = Path(
        input_file or DEFAULT_INPUT_FILE
    )

    output_file = Path(
        output_file or DEFAULT_OUTPUT_FILE
    )

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    print(f"Input file: {input_file}")

    # ---------------------------------------------------------
    # Read raw file
    # ---------------------------------------------------------

    raw = pd.read_csv(
        input_file,
        dtype=str,
        header=None
    )

    print(f"Raw rows: {len(raw)}")
    print(f"Raw columns: {len(raw.columns)}")

    # ---------------------------------------------------------
    # Find actual header
    # ---------------------------------------------------------

    header_row = None

    for index in range(len(raw)):

        first_value = str(
            raw.iloc[index, 0]
        ).strip()

        if first_value == "CBA State":
            header_row = index
            break

    if header_row is None:
        raise ValueError(
            "Could not find the CBA State header row."
        )

    print(
        f"Header row found: {header_row + 1}"
    )

    # ---------------------------------------------------------
    # Create cleaned headers
    # ---------------------------------------------------------

    headers = raw.iloc[
        header_row
    ].tolist()

    cleaned_headers = []

    for i, header in enumerate(headers):

        if pd.isna(header):

            cleaned_headers.append(
                f"UNNAMED_{i}"
            )

        else:

            cleaned_headers.append(
                str(header).strip()
            )

    # ---------------------------------------------------------
    # Data starts after header
    # ---------------------------------------------------------

    df = raw.iloc[
        header_row + 1:
    ].copy()

    df.columns = cleaned_headers

    # Remove completely empty rows
    df = df.dropna(
        how="all"
    )

    # ---------------------------------------------------------
    # Validate required columns
    # ---------------------------------------------------------

    required_columns = [
        "CBA State",
        "CBA ZIP Code",
        "CBA Name Short",
        "CBA Name",
        "Year/Qtr"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # ---------------------------------------------------------
    # Rename fields
    # ---------------------------------------------------------

    df = df.rename(
        columns={
            "CBA State": "CBA_STATE",
            "CBA ZIP Code": "ZIP_CODE",
            "CBA Name Short": "CBA_NAME_SHORT",
            "CBA Name": "CBA_NAME",
            "Year/Qtr": "YEAR_QUARTER"
        }
    )

    # ---------------------------------------------------------
    # Clean values
    # ---------------------------------------------------------

    for column in df.columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # ---------------------------------------------------------
    # Preserve ZIP leading zeros
    # ---------------------------------------------------------

    df["ZIP_CODE"] = (
        df["ZIP_CODE"]
        .str.zfill(5)
    )

    # ---------------------------------------------------------
    # Validate ZIP
    # ---------------------------------------------------------

    invalid_zip = df[
        ~df["ZIP_CODE"].str.match(
            r"^\d{5}$"
        )
    ]

    if len(invalid_zip) > 0:

        print(
            f"Warning: {len(invalid_zip)} "
            f"invalid ZIP codes found."
        )

    # ---------------------------------------------------------
    # Validate Year/Quarter
    # ---------------------------------------------------------

    invalid_yq = df[
        ~df["YEAR_QUARTER"].str.match(
            r"^\d{6}$"
        )
    ]

    if len(invalid_yq) > 0:

        print(
            f"Warning: {len(invalid_yq)} "
            f"invalid YEAR_QUARTER values found."
        )

    # ---------------------------------------------------------
    # Duplicate check
    # ---------------------------------------------------------

    duplicates = df.duplicated().sum()

    print(
        f"Duplicate records: {duplicates}"
    )

    if duplicates > 0:

        df = df.drop_duplicates()

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    print(
        f"Final rows: {len(df)}"
    )

    print(
        f"Unique ZIP codes: "
        f"{df['ZIP_CODE'].nunique()}"
    )

    print(
        f"Unique CBA short names: "
        f"{df['CBA_NAME_SHORT'].nunique()}"
    )

    print(
        f"Unique CBA names: "
        f"{df['CBA_NAME'].nunique()}"
    )

    print(
        f"States represented: "
        f"{df['CBA_STATE'].nunique()}"
    )

    print(
        f"Quarters represented: "
        f"{df['YEAR_QUARTER'].nunique()}"
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nOutput saved: {output_file}"
    )

    print("\nSample records:")

    print(
        df.head(10)
        .to_string(index=False)
    )

    print("=" * 60)
    print("FORMER CBA ZIP PARSING COMPLETED")
    print("=" * 60)

    return output_file


if __name__ == "__main__":
    parse_former_cba_zip()