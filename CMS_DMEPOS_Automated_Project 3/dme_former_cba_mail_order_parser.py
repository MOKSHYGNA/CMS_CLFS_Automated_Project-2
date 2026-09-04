import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE = (
    PROJECT_ROOT
    / "downloads"
    / "dme26-c"
    / "extracted"
    / "Former CBA National Mail-Order DTS Fee Schedule - JUL2026.csv"
)

DEFAULT_OUTPUT_FILE = (
    PROJECT_ROOT
    / "output"
    / "former_cba_mail_order.csv"
)


# ============================================================
# HEADER DETECTION
# ============================================================

def find_header_row(df):
    """
    Find the actual header row by looking for HCPCS
    in the first column.
    """

    for i in range(len(df)):
        first_value = str(df.iloc[i, 0]).strip().upper()

        if first_value == "HCPCS":
            return i

    raise ValueError(
        "Could not find header row containing HCPCS."
    )


# ============================================================
# MAIN PARSER
# ============================================================

def parse_former_cba_mail_order(
    input_file=None,
    output_file=None
):
    """
    Parse Former CBA National Mail-Order DTS Fee Schedule.

    Parameters
    ----------
    input_file : str or Path, optional
        Input CSV path.

    output_file : str or Path, optional
        Output CSV path.

    Returns
    -------
    Path
        Path of normalized output file.
    """

    print("=" * 60)
    print("CMS FORMER CBA NATIONAL MAIL-ORDER PARSER")
    print("=" * 60)

    # --------------------------------------------------------
    # Resolve input/output paths
    # --------------------------------------------------------

    input_file = (
        Path(input_file)
        if input_file
        else DEFAULT_INPUT_FILE
    )

    output_file = (
        Path(output_file)
        if output_file
        else DEFAULT_OUTPUT_FILE
    )

    print(f"Input file: {input_file}")

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{input_file}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Read raw CSV
    # --------------------------------------------------------

    df_raw = pd.read_csv(
        input_file,
        header=None,
        dtype=str,
        encoding="latin1"
    )

    print(f"Raw rows: {len(df_raw)}")
    print(f"Raw columns: {len(df_raw.columns)}")

    # --------------------------------------------------------
    # Find actual header
    # --------------------------------------------------------

    header_row = find_header_row(df_raw)

    print(f"Header row found: {header_row + 1}")

    # --------------------------------------------------------
    # Rebuild dataframe
    # --------------------------------------------------------

    df = df_raw.iloc[header_row:].copy()

    df.columns = df.iloc[0]

    df = df.iloc[1:].reset_index(drop=True)

    # Remove completely empty rows and columns
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")

    # Clean column names
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # Clean values
    for col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .replace({
                "nan": "",
                "NaN": ""
            })
        )

    # --------------------------------------------------------
    # Display structure
    # --------------------------------------------------------

    print("\nColumns:")

    for col in df.columns:
        print(f"  - {col}")

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = ["HCPCS"]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # --------------------------------------------------------
    # Remove rows without HCPCS
    # --------------------------------------------------------

    df = df[
        df["HCPCS"].astype(str).str.strip() != ""
    ].copy()

    # --------------------------------------------------------
    # Determine ID columns
    # --------------------------------------------------------

    id_columns = ["HCPCS"]

    for col in [
        "Mod",
        "Mod2",
        "Mod3",
        "CATG"
    ]:
        if col in df.columns:
            id_columns.append(col)

    # --------------------------------------------------------
    # Determine value columns
    # --------------------------------------------------------

    value_columns = [
        col
        for col in df.columns
        if col not in id_columns
    ]

    if not value_columns:
        raise ValueError(
            "No fee/data columns were found."
        )

    print(
        f"\nFee/data columns found: "
        f"{len(value_columns)}"
    )

    # --------------------------------------------------------
    # Convert wide format to long format
    # --------------------------------------------------------

    normalized = df.melt(
        id_vars=id_columns,
        value_vars=value_columns,
        var_name="MAIL_ORDER_FIELD",
        value_name="FEE_AMOUNT"
    )

    # --------------------------------------------------------
    # Clean fee amount
    # --------------------------------------------------------

    normalized["FEE_AMOUNT"] = (
        normalized["FEE_AMOUNT"]
        .astype(str)
        .str.strip()
        .replace({
            "": None,
            "nan": None,
            "NaN": None,
            "N/A": None,
            "NA": None
        })
    )

    normalized["FEE_AMOUNT"] = pd.to_numeric(
        normalized["FEE_AMOUNT"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove rows without valid fee
    # --------------------------------------------------------

    normalized = normalized[
        normalized["FEE_AMOUNT"].notna()
    ].copy()

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    duplicate_count = normalized.duplicated().sum()

    print(
        f"Duplicate records: "
        f"{duplicate_count}"
    )

    normalized = (
        normalized
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print(
        f"Final rows: "
        f"{len(normalized)}"
    )

    print(
        f"Unique HCPCS: "
        f"{normalized['HCPCS'].nunique()}"
    )

    print(
        f"Unique mail-order fields: "
        f"{normalized['MAIL_ORDER_FIELD'].nunique()}"
    )

    if "CATG" in normalized.columns:
        print(
            f"Categories: "
            f"{normalized['CATG'].nunique()}"
        )

    # --------------------------------------------------------
    # Save normalized output
    # --------------------------------------------------------

    normalized.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nOutput saved: "
        f"{output_file}"
    )

    # --------------------------------------------------------
    # Sample
    # --------------------------------------------------------

    print("\nSample records:")

    print(
        normalized
        .head(10)
        .to_string(index=False)
    )

    print("=" * 60)
    print(
        "FORMER CBA MAIL-ORDER PARSING COMPLETED"
    )
    print("=" * 60)

    return output_file


# ============================================================
# STANDALONE ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parse_former_cba_mail_order()