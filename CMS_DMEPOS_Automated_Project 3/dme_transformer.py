import pandas as pd
from pathlib import Path


def transform_dme_file(input_csv, output_csv):
    print("=" * 50)
    print("DMEPOS TRANSFORMER")
    print("=" * 50)

    input_csv = Path(input_csv)
    output_csv = Path(output_csv)

    if not input_csv.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_csv}"
        )

    print(f"Input file: {input_csv}")

    # --------------------------------------------------
    # 1. Load cleaned CSV
    # --------------------------------------------------
    df = pd.read_csv(
        input_csv,
        dtype=str
    )

    print(f"Input rows: {len(df)}")

    # --------------------------------------------------
    # 2. Identify state price columns
    # --------------------------------------------------
    state_price_columns = [
        col for col in df.columns
        if "(" in col and ")" in col
    ]

    if not state_price_columns:
        raise ValueError(
            "No state price columns found."
        )

    print(
        f"State price columns found: "
        f"{len(state_price_columns)}"
    )

    # --------------------------------------------------
    # 3. Columns that stay unchanged
    # --------------------------------------------------
    id_columns = [
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
        col for col in id_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # --------------------------------------------------
    # 4. Convert wide format → normalized format
    # --------------------------------------------------
    normalized = df.melt(
        id_vars=id_columns,
        value_vars=state_price_columns,
        var_name="STATE_PRICE_TYPE",
        value_name="PRICE"
    )

    # --------------------------------------------------
    # 5. Split STATE and PRICE_TYPE
    #
    # Example:
    # "AL (NR)" → STATE = AL
    #              PRICE_TYPE = NR
    # --------------------------------------------------
    normalized["STATE"] = (
        normalized["STATE_PRICE_TYPE"]
        .str.extract(r"^([A-Z]{2})")
    )

    normalized["PRICE_TYPE"] = (
        normalized["STATE_PRICE_TYPE"]
        .str.extract(r"\((NR|R)\)")
    )

    # --------------------------------------------------
    # 6. Remove temporary column
    # --------------------------------------------------
    normalized = normalized.drop(
        columns=["STATE_PRICE_TYPE"]
    )

    # --------------------------------------------------
    # 7. Clean text fields
    # --------------------------------------------------
    text_columns = [
        "HCPCS",
        "Mod",
        "Mod2",
        "JURIS",
        "CATG",
        "STATE",
        "PRICE_TYPE",
        "Description"
    ]

    for col in text_columns:
        normalized[col] = (
            normalized[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------
    # 8. Convert numeric fields
    # --------------------------------------------------
    normalized["PRICE"] = pd.to_numeric(
        normalized["PRICE"],
        errors="coerce"
    )

    normalized["Ceiling"] = pd.to_numeric(
        normalized["Ceiling"],
        errors="coerce"
    )

    normalized["Floor"] = pd.to_numeric(
        normalized["Floor"],
        errors="coerce"
    )

    # --------------------------------------------------
    # 9. Remove exact duplicates
    # --------------------------------------------------
    before = len(normalized)

    normalized = normalized.drop_duplicates()

    after = len(normalized)

    print(
        f"Duplicates removed: "
        f"{before - after}"
    )

    # --------------------------------------------------
    # 10. Arrange final column order
    # --------------------------------------------------
    final_columns = [
        "HCPCS",
        "Mod",
        "Mod2",
        "JURIS",
        "CATG",
        "Ceiling",
        "Floor",
        "STATE",
        "PRICE_TYPE",
        "PRICE",
        "Description"
    ]

    normalized = normalized[final_columns]

    # --------------------------------------------------
    # 11. Save normalized data
    # --------------------------------------------------
    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    normalized.to_csv(
        output_csv,
        index=False
    )

    # --------------------------------------------------
    # 12. Summary
    # --------------------------------------------------
    print(f"Output rows: {len(normalized)}")
    print(f"Output columns: {len(normalized.columns)}")
    print(
        f"Unique HCPCS: "
        f"{normalized['HCPCS'].nunique()}"
    )
    print(
        f"Unique states: "
        f"{normalized['STATE'].nunique()}"
    )

    print("\nPrice type counts:")
    print(
        normalized["PRICE_TYPE"]
        .value_counts()
        .to_string()
    )

    print(f"\nNormalized file saved: {output_csv}")

    print("=" * 50)
    print("TRANSFORMATION COMPLETED")
    print("=" * 50)

    return {
        "rows": len(normalized),
        "columns": len(normalized.columns),
        "hcpcs_count": normalized["HCPCS"].nunique(),
        "state_count": normalized["STATE"].nunique(),
        "output_file": str(output_csv)
    }


if __name__ == "__main__":

    # Standalone test using the current cleaned file
    input_file = (
        Path("output")
        / "dmepos_cleaned.csv"
    )

    output_file = (
        Path("output")
        / "dmepos_normalized.csv"
    )

    transform_dme_file(
        input_file,
        output_file
    )