import pandas as pd
from pathlib import Path


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

CLINICAL_FILE = Path(
    "output/cms_clfs_combined.csv"
)

PHYSICIAN_FILE = Path(
    "output/cms_physician_combined.csv"
)

OUTPUT_FILE = Path(
    "output/cms_all_combined.csv"
)


# --------------------------------------------------
# COMBINE DATASETS
# --------------------------------------------------

def combine_datasets():

    print("\n")
    print("=" * 60)
    print("CMS CLINICAL + PHYSICIAN DATA COMBINER")
    print("=" * 60)

    # --------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------

    if not CLINICAL_FILE.exists():
        print(f"[ERROR] Clinical file not found: {CLINICAL_FILE}")
        return

    if not PHYSICIAN_FILE.exists():
        print(f"[ERROR] Physician file not found: {PHYSICIAN_FILE}")
        return

    # --------------------------------------------------
    # READ FILES
    # --------------------------------------------------

    print(f"\n[INFO] Reading Clinical data:")
    print(f"       {CLINICAL_FILE}")

    clinical_df = pd.read_csv(
        CLINICAL_FILE,
        dtype=str
    )

    print(f"[OK] Clinical rows: {len(clinical_df)}")
    print(f"[OK] Clinical columns: {len(clinical_df.columns)}")

    print(f"\n[INFO] Reading Physician data:")
    print(f"       {PHYSICIAN_FILE}")

    physician_df = pd.read_csv(
        PHYSICIAN_FILE,
        dtype=str
    )

    print(f"[OK] Physician rows: {len(physician_df)}")
    print(f"[OK] Physician columns: {len(physician_df.columns)}")

    # --------------------------------------------------
    # ADD DATA TYPE
    # --------------------------------------------------

    clinical_df["DATA_TYPE"] = "CLINICAL"

    physician_df["DATA_TYPE"] = "PHYSICIAN"

    # --------------------------------------------------
    # CREATE COMMON COLUMNS
    # --------------------------------------------------

    all_columns = sorted(
        set(clinical_df.columns)
        .union(set(physician_df.columns))
    )

    clinical_df = clinical_df.reindex(
        columns=all_columns
    )

    physician_df = physician_df.reindex(
        columns=all_columns
    )

    # --------------------------------------------------
    # COMBINE
    # --------------------------------------------------

    combined_df = pd.concat(
        [
            clinical_df,
            physician_df
        ],
        ignore_index=True
    )

    print(
        f"\n[INFO] Combined rows: {len(combined_df)}"
    )

    print(
        f"[INFO] Combined columns: {len(combined_df.columns)}"
    )

    # --------------------------------------------------
    # REMOVE EXACT DUPLICATES
    # --------------------------------------------------

    before = len(combined_df)

    combined_df = combined_df.drop_duplicates()

    after = len(combined_df)

    print(
        f"[INFO] Rows before duplicate removal: {before}"
    )

    print(
        f"[INFO] Rows after duplicate removal: {after}"
    )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    combined_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print("\n[OK] Combined dataset created:")
    print(f"     {OUTPUT_FILE}")

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print("\nData type summary:")

    print(
        combined_df["DATA_TYPE"].value_counts()
    )

    print("\nFinal columns:")

    for column in combined_df.columns:
        print(f"  - {column}")

    print("\n")
    print("=" * 60)
    print("COMBINATION COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    combine_datasets()