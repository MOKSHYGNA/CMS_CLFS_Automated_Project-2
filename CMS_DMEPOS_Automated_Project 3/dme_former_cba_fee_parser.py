import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE = (
    BASE_DIR
    / "downloads"
    / "dme26-c"
    / "extracted"
    / "Former CBA Fee schedule File - JUL2026.csv"
)

DEFAULT_OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "former_cba_fee_schedule.csv"
)


def parse_former_cba_fee(
    input_file=None,
    output_file=None
):

    print("=" * 60)
    print("CMS FORMER CBA FEE SCHEDULE PARSER")
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

        if first_value == "HCPCS":
            header_row = index
            break

    if header_row is None:
        raise ValueError(
            "Could not find the HCPCS header row."
        )

    print(
        f"Header row found: {header_row + 1}"
    )

    # ---------------------------------------------------------
    # Create headers
    # ---------------------------------------------------------

    headers = raw.iloc[header_row].tolist()

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
    # Data after header
    # ---------------------------------------------------------

    df = raw.iloc[
        header_row + 1:
    ].copy()

    df.columns = cleaned_headers

    df = df.dropna(
        how="all"
    )

    df = df.dropna(
        axis=1,
        how="all"
    )

    # ---------------------------------------------------------
    # Required columns
    # ---------------------------------------------------------

    base_columns = [
        "HCPCS",
        "Mod",
        "Mod2",
        "Mod3",
        "CATG"
    ]

    missing = [
        col
        for col in base_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing expected columns: {missing}"
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
    # Find CBA locality columns
    # ---------------------------------------------------------

    start_index = (
        df.columns.get_loc("CATG") + 1
    )

    locality_columns = list(
        df.columns[start_index:]
    )

    locality_columns = [
        col
        for col in locality_columns
        if not col.startswith("UNNAMED_")
        and col.strip() != ""
    ]

    print(
        f"CBA locality columns found: "
        f"{len(locality_columns)}"
    )

    if not locality_columns:
        raise ValueError(
            "No CBA locality columns found."
        )

    # ---------------------------------------------------------
    # Convert wide → normalized
    # ---------------------------------------------------------

    normalized = df[
        base_columns + locality_columns
    ].melt(
        id_vars=base_columns,
        value_vars=locality_columns,
        var_name="CBA_LOCALITY",
        value_name="FEE_AMOUNT"
    )

    # ---------------------------------------------------------
    # Clean fee
    # ---------------------------------------------------------

    normalized["FEE_AMOUNT"] = (
        normalized["FEE_AMOUNT"]
        .astype(str)
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.strip()
    )

    normalized["FEE_AMOUNT"] = pd.to_numeric(
        normalized["FEE_AMOUNT"],
        errors="coerce"
    )

    normalized = normalized[
        normalized["FEE_AMOUNT"].notna()
    ].copy()

    # ---------------------------------------------------------
    # Duplicate check
    # ---------------------------------------------------------

    duplicates = normalized.duplicated().sum()

    print(
        f"Duplicate records: {duplicates}"
    )

    if duplicates > 0:
        normalized = (
            normalized
            .drop_duplicates()
        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    print(
        f"Final normalized records: "
        f"{len(normalized)}"
    )

    print(
        f"Unique HCPCS codes: "
        f"{normalized['HCPCS'].nunique()}"
    )

    print(
        f"Unique CBA localities: "
        f"{normalized['CBA_LOCALITY'].nunique()}"
    )

    print(
        f"Unique categories: "
        f"{normalized['CATG'].nunique()}"
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    normalized.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nOutput saved: {output_file}"
    )

    print("\nSample records:")

    print(
        normalized.head(10)
        .to_string(index=False)
    )

    print("=" * 60)
    print("FORMER CBA FEE PARSING COMPLETED")
    print("=" * 60)

    return output_file


if __name__ == "__main__":
    parse_former_cba_fee()