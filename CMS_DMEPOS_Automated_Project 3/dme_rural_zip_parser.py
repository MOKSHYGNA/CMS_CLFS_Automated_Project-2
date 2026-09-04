import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE = (
    BASE_DIR
    / "downloads"
    / "dme26-c"
    / "extracted"
    / "DME Rural Zip Code Quarter 3 2026.csv"
)

DEFAULT_OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "dme_rural_zip.csv"
)


def parse_rural_zip(
    input_file=None,
    output_file=None
):

    print("=" * 60)
    print("CMS DMEPOS RURAL ZIP PARSER")
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

    df = pd.read_csv(
        input_file,
        dtype=str
    )

    print(f"Raw rows: {len(df)}")
    print(f"Raw columns: {list(df.columns)}")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    required_columns = [
        "STATE",
        "DMEPOS RURAL ZIP CODE",
        "YEAR/QTR"
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

    df = df.rename(
        columns={
            "DMEPOS RURAL ZIP CODE": "ZIP_CODE",
            "YEAR/QTR": "YEAR_QUARTER"
        }
    )

    for column in df.columns:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["ZIP_CODE"] = (
        df["ZIP_CODE"]
        .str.zfill(5)
    )

    invalid_zip = df[
        ~df["ZIP_CODE"].str.match(r"^\d{5}$")
    ]

    if len(invalid_zip) > 0:
        print(
            f"Warning: {len(invalid_zip)} invalid ZIP codes found."
        )

    invalid_yq = df[
        ~df["YEAR_QUARTER"].str.match(r"^\d{6}$")
    ]

    if len(invalid_yq) > 0:
        print(
            f"Warning: {len(invalid_yq)} invalid YEAR_QUARTER values found."
        )

    duplicates = df.duplicated().sum()

    print(f"Duplicate records: {duplicates}")

    if duplicates > 0:
        df = df.drop_duplicates()

    df["DME_RURAL_FLAG"] = "Y"

    print(f"Final rows: {len(df)}")
    print(
        f"Unique ZIP codes: {df['ZIP_CODE'].nunique()}"
    )
    print(
        f"States represented: {df['STATE'].nunique()}"
    )
    print(
        f"Quarters represented: "
        f"{df['YEAR_QUARTER'].nunique()}"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False
    )

    print(f"\nOutput saved: {output_file}")

    print("\nSample records:")
    print(
        df.head(10).to_string(index=False)
    )

    print("=" * 60)
    print("RURAL ZIP PARSING COMPLETED")
    print("=" * 60)

    return output_file


if __name__ == "__main__":
    parse_rural_zip()