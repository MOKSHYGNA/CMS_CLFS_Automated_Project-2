import zipfile
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

INPUT_ZIP = BASE_DIR / "output" / "zip_carrier_locality.zip"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_CSV = OUTPUT_DIR / "zip_carrier_locality.csv"


def find_zip5_file(zip_file):
    """
    Find the ZIP5 data file inside the CMS ZIP package.
    """

    names = zip_file.namelist()

    zip5_files = [
        name for name in names
        if Path(name).name.upper().startswith("ZIP5_")
        and Path(name).suffix.lower() == ".txt"
    ]

    if not zip5_files:
        raise FileNotFoundError(
            "Could not find ZIP5_*.txt inside the CMS ZIP package."
        )

    if len(zip5_files) > 1:
        print("Multiple ZIP5 files found:")
        for name in zip5_files:
            print(f"  {name}")

    return zip5_files[0]


def parse_zip5(input_zip, output_csv):
    print("=" * 60)
    print("CMS ZIP5 CARRIER / LOCALITY PARSER")
    print("=" * 60)

    input_zip = Path(input_zip)
    output_csv = Path(output_csv)

    if not input_zip.exists():
        raise FileNotFoundError(
            f"Input ZIP not found: {input_zip}"
        )

    print(f"Input ZIP: {input_zip}")

    with zipfile.ZipFile(input_zip, "r") as z:

        zip5_file = find_zip5_file(z)

        print(f"ZIP5 file found: {zip5_file}")

        raw_data = z.read(zip5_file).decode(
            "latin1"
        )

    lines = raw_data.splitlines()

    print(f"Raw ZIP5 records: {len(lines)}")

    records = []

    for line_number, line in enumerate(lines, start=1):

        # Ignore completely blank lines
        if not line.strip():
            continue

        # CMS ZIP5 layout requires at least 80 positions
        if len(line) < 80:
            print(
                f"Warning: line {line_number} has only "
                f"{len(line)} characters. Skipping."
            )
            continue

        record = {
            "STATE": line[0:2].strip(),
            "ZIP_CODE": line[2:7].strip(),
            "MDCR_CARRIER_ID": line[7:12].strip(),
            "MDCR_FEE_SCHD_ID": line[12:14].strip(),
            "RURAL_INDICATOR": line[14:15].strip(),
            "BENE_LAB_CB_LOCALITY": line[15:17].strip(),
            "RURAL_INDICATOR2": line[17:18].strip(),
            "PLUS4_FLAG": line[20:21].strip(),
            "PART_B_PAYMENT_INDICATOR": line[22:23].strip(),
            "YEAR_QUARTER": line[75:80].strip(),
        }

        records.append(record)

    df = pd.DataFrame(records)

    print(f"Parsed records: {len(df)}")

    if df.empty:
        raise ValueError("No ZIP5 records were parsed.")

    # Validate important fields
    required_columns = [
        "STATE",
        "ZIP_CODE",
        "MDCR_CARRIER_ID",
        "MDCR_FEE_SCHD_ID",
        "RURAL_INDICATOR",
        "YEAR_QUARTER",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print("Required fields validated successfully.")

    # Preserve leading zeros
    df["ZIP_CODE"] = df["ZIP_CODE"].astype(str).str.zfill(5)

    df["MDCR_CARRIER_ID"] = (
        df["MDCR_CARRIER_ID"]
        .astype(str)
        .str.zfill(5)
    )

    df["MDCR_FEE_SCHD_ID"] = (
        df["MDCR_FEE_SCHD_ID"]
        .astype(str)
        .str.zfill(2)
    )

    # Convert blank rural indicator to URBAN
    df["PRICING_AREA_TYPE"] = df[
        "RURAL_INDICATOR"
    ].map(
        {
            "": "URBAN",
            "R": "RURAL",
            "B": "SUPER_RURAL",
        }
    )

    # Detect unexpected rural indicators
    unexpected = sorted(
        set(df["RURAL_INDICATOR"])
        - {"", "R", "B"}
    )

    if unexpected:
        print(
            f"Warning: unexpected rural indicators: {unexpected}"
        )

    # Duplicate check
    duplicate_count = df.duplicated().sum()

    print(f"Duplicate records: {duplicate_count}")

    # Remove exact duplicates if any
    if duplicate_count > 0:
        df = df.drop_duplicates()

    # Statistics
    print(f"Unique ZIP codes: {df['ZIP_CODE'].nunique()}")
    print(
        f"Unique Carrier IDs: "
        f"{df['MDCR_CARRIER_ID'].nunique()}"
    )
    print(
        f"Unique Fee Schedule IDs: "
        f"{df['MDCR_FEE_SCHD_ID'].nunique()}"
    )

    print(
        f"Rural records: "
        f"{(df['RURAL_INDICATOR'] == 'R').sum()}"
    )

    print(
        f"Super rural records: "
        f"{(df['RURAL_INDICATOR'] == 'B').sum()}"
    )

    print(
        f"Urban records: "
        f"{(df['RURAL_INDICATOR'] == '').sum()}"
    )

    # Save
    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_csv,
        index=False
    )

    print(f"\nOutput saved: {output_csv}")

    print("\nSample records:")
    print(
        df[
            [
                "STATE",
                "ZIP_CODE",
                "MDCR_CARRIER_ID",
                "MDCR_FEE_SCHD_ID",
                "RURAL_INDICATOR",
                "PRICING_AREA_TYPE",
                "YEAR_QUARTER",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("=" * 60)
    print("ZIP5 PARSING COMPLETED")
    print("=" * 60)

    return {
        "records": len(df),
        "unique_zip_codes": df["ZIP_CODE"].nunique(),
        "unique_carriers": df["MDCR_CARRIER_ID"].nunique(),
        "unique_fee_schedule_ids": df[
            "MDCR_FEE_SCHD_ID"
        ].nunique(),
        "output_file": str(output_csv),
    }


if __name__ == "__main__":

    parse_zip5(
        INPUT_ZIP,
        OUTPUT_CSV
    )
    