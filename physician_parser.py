import csv
from io import TextIOWrapper
from zipfile import ZipFile
from pathlib import Path
import pandas as pd


COLUMNS = [
    "YEAR",
    "CARRIER",
    "LOCALITY",
    "HCPCS",
    "MOD",
    "NON_FACILITY_RATE",
    "FACILITY_RATE",
    "FILLER_1",
    "PCTC_INDICATOR",
    "STATUS_CODE",
    "MULTIPLE_SURGERY_INDICATOR",
    "THERAPY_REDUCTION_NON_FACILITY",
    "THERAPY_REDUCTION_FACILITY",
    "OPPS_INDICATOR",
    "OPPS_NON_FACILITY_RATE",
    "OPPS_FACILITY_RATE"
]


def read_physician_zip(zip_path, file_type):
    """
    Read PFREV26C.txt from a Physician ZIP file.
    """

    with ZipFile(zip_path, "r") as zip_ref:

        txt_file = next(
            name for name in zip_ref.namelist()
            if name.lower().endswith(".txt")
        )

        with zip_ref.open(txt_file) as file:

            text_file = TextIOWrapper(
                file,
                encoding="utf-8",
                errors="replace"
            )

            rows = []

            for row in csv.reader(text_file):

                if len(row) != len(COLUMNS):
                    continue

                rows.append(row)

    df = pd.DataFrame(rows, columns=COLUMNS)

    df["FILE_TYPE"] = file_type
    df["SOURCE_FILE"] = Path(zip_path).name

    return df


if __name__ == "__main__":

    base_path = Path.home() / "Documents" / "pfrev26c"

    qp_zip = base_path / "PFREV26C_QP.zip"
    nonqp_zip = base_path / "PFREV26C_nonQP.zip"

    qp_df = read_physician_zip(qp_zip, "QP")
    nonqp_df = read_physician_zip(nonqp_zip, "nonQP")

    physician_df = pd.concat(
        [qp_df, nonqp_df],
        ignore_index=True
    )

    print("\nPhysician data loaded successfully!")

    print("Rows:", len(physician_df))
    print("Columns:", len(physician_df.columns))

    print("\nColumns:")
    print(physician_df.columns.tolist())

    print("\nFirst 5 rows:")
    print(physician_df.head())
    print("\nData types:")
print(physician_df.dtypes)

print("\nFILE_TYPE counts:")
print(physician_df["FILE_TYPE"].value_counts())

print("\nStatus Code counts:")
print(physician_df["STATUS_CODE"].value_counts())

print("\nSample Physician records:")
print(
    physician_df[
        [
            "YEAR",
            "CARRIER",
            "LOCALITY",
            "HCPCS",
            "MOD",
            "NON_FACILITY_RATE",
            "FACILITY_RATE",
            "PCTC_INDICATOR",
            "STATUS_CODE",
            "FILE_TYPE"
        ]
    ].head(10).to_string(index=False)
)
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "cms_physician_combined.csv"

physician_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

print(f"\n[OK] Physician dataset created:")
print(f"     {output_file}")