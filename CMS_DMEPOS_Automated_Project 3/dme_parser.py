import pandas as pd
from pathlib import Path
import re


def parse_dme_file(input_csv, output_csv):
    print("=" * 50)
    print("DMEPOS PARSER")
    print("=" * 50)

    input_csv = Path(input_csv)
    output_csv = Path(output_csv)

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    print(f"Input file: {input_csv}")

    # --------------------------------------------------
    # 1. Find the real header row
    # --------------------------------------------------
    preview = pd.read_csv(
        input_csv,
        header=None,
        nrows=20,
        dtype=str,
        encoding="latin1"
    )

    header_row = None

    for i in range(len(preview)):
        first_value = str(preview.iloc[i, 0]).strip().upper()

        if first_value == "HCPCS":
            header_row = i
            break

    if header_row is None:
        raise ValueError("Could not find HCPCS header row.")

    print(f"Header row found at: {header_row + 1}")

    # --------------------------------------------------
    # 2. Read CSV using detected header
    # --------------------------------------------------
    df = pd.read_csv(
        input_csv,
        skiprows=header_row,
        dtype=str,
        encoding="latin1"
    )

    # Remove completely empty rows/columns
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")

    # Clean column names
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    print(f"Rows loaded: {len(df)}")
    print(f"Columns loaded: {len(df.columns)}")

    # --------------------------------------------------
    # 3. Validate important columns
    # --------------------------------------------------
    required_columns = [
        "HCPCS",
        "Mod",
        "Mod2",
        "JURIS",
        "CATG",
        "Ceiling",
        "Floor",
        "Description"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print("Required columns validated successfully.")

    # --------------------------------------------------
    # 4. Detect state price columns
    # --------------------------------------------------
    state_price_pattern = re.compile(
        r"^[A-Z]{2}\s+\((NR|R)\)$"
    )

    state_price_columns = [
        col for col in df.columns
        if state_price_pattern.match(col)
    ]

    if not state_price_columns:
        raise ValueError(
            "No state price columns were detected."
        )

    print(
        f"State price columns detected: "
        f"{len(state_price_columns)}"
    )

    # --------------------------------------------------
    # 5. Clean text values
    # --------------------------------------------------
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Convert pandas NaN strings back to empty values
    df = df.replace(
        ["nan", "NaN", "None"],
        ""
    )

    # --------------------------------------------------
    # 6. Save cleaned file
    # --------------------------------------------------
    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_csv,
        index=False
    )

    print(f"Cleaned file saved: {output_csv}")
    print(f"Unique HCPCS codes: {df['HCPCS'].nunique()}")

    print("=" * 50)
    print("PARSING COMPLETED")
    print("=" * 50)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "state_price_columns": len(state_price_columns),
        "hcpcs_count": df["HCPCS"].nunique(),
        "output_file": str(output_csv)
    }


if __name__ == "__main__":

    # Standalone test using the existing January 2026 file
    input_file = (
        Path("downloads")
        / "dme26"
        / "DMEPOS26_JAN.csv"
    )

    output_file = (
        Path("output")
        / "dmepos_cleaned.csv"
    )

    parse_dme_file(
        input_file,
        output_file
    )