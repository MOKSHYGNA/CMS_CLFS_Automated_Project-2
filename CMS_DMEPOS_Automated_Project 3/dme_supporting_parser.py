import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

EXTRACTED_DIR = (
    BASE_DIR
    / "downloads"
    / "dme26-c"
    / "extracted"
)

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FILES = {
    "rural_zip": "DME Rural Zip Code Quarter 3 2026.csv",
    "former_cba_fee": "Former CBA Fee Schedule File - JUL2026.csv",
    "former_cba_zip": "Former CBA ZIP Code File  - JUL2026.csv",
    "mail_order": "Former CBA National Mail-Order DTS Fee Schedule - JUL2026.csv",
}


def find_header_row(file_path, required_columns):
    """
    Find the actual header row by looking for the required columns.
    """

    raw = pd.read_csv(
        file_path,
        header=None,
        nrows=30,
        encoding="latin1"
    )

    for index, row in raw.iterrows():
        values = {
            str(value).strip()
            for value in row.tolist()
            if pd.notna(value)
        }

        if all(column in values for column in required_columns):
            return index

    raise ValueError(
        f"Could not find header row in {file_path.name}"
    )


def read_supporting_file(file_name, required_columns):
    """
    Read a CMS supporting file after automatically locating
    its real header row.
    """

    file_path = EXTRACTED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    header_row = find_header_row(
        file_path,
        required_columns
    )

    df = pd.read_csv(
        file_path,
        header=header_row,
        encoding="latin1",
        dtype=str
    )

    df = df.dropna(how="all")
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # Strip whitespace from text values
    for column in df.columns:
        df[column] = (
            df[column]
            .astype(str)
            .replace("nan", "")
            .str.strip()
        )

    print(f"\nFile: {file_name}")
    print(f"Header row: {header_row + 1}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print("Columns:")
    print(list(df.columns))

    return df


def parse_rural_zip():
    df = read_supporting_file(
        FILES["rural_zip"],
        [
            "STATE",
            "DMEPOS RURAL ZIP CODE",
            "YEAR/QTR",
        ],
    )

    output_file = OUTPUT_DIR / "dme_rural_zip.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")

    return df


def parse_former_cba_fee():
    df = read_supporting_file(
        FILES["former_cba_fee"],
        [
            "HCPCS",
            "Mod",
            "CATG",
        ],
    )

    output_file = OUTPUT_DIR / "former_cba_fee_schedule.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")

    return df


def parse_former_cba_zip():
    df = read_supporting_file(
        FILES["former_cba_zip"],
        [
            "CBA State",
            "CBA ZIP Code",
            "CBA Name Short",
            "CBA Name",
            "Year/Qtr",
        ],
    )

    output_file = OUTPUT_DIR / "former_cba_zip.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")

    return df


def parse_mail_order():
    df = read_supporting_file(
        FILES["mail_order"],
        [
            "HCPCS",
            "Mod",
            "Mod2",
            "CATG",
            "National Mail-Order",
            "Description",
        ],
    )

    output_file = OUTPUT_DIR / "former_cba_mail_order.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file}")

    return df


def main():

    print("=" * 70)
    print("DMEPOS SUPPORTING FILE PARSER")
    print("=" * 70)

    print("\nParsing Rural ZIP file...")
    rural_df = parse_rural_zip()

    print("\nParsing Former CBA Fee Schedule...")
    cba_fee_df = parse_former_cba_fee()

    print("\nParsing Former CBA ZIP file...")
    cba_zip_df = parse_former_cba_zip()

    print("\nParsing Former CBA Mail-Order file...")
    mail_order_df = parse_mail_order()

    print("\n" + "=" * 70)
    print("PARSING SUMMARY")
    print("=" * 70)

    print(f"Rural ZIP records: {len(rural_df)}")
    print(f"Former CBA Fee records: {len(cba_fee_df)}")
    print(f"Former CBA ZIP records: {len(cba_zip_df)}")
    print(f"Mail-Order records: {len(mail_order_df)}")

    print("\nSupporting files parsed successfully.")


if __name__ == "__main__":
    main()