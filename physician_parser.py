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


def find_physician_zip(project_folder, file_type):
    """
    Search the Project 2 folder and all subfolders
    for the required Physician ZIP file.
    """

    project_folder = Path(project_folder)

    if file_type == "QP":
        possible_names = [
            "PFREV26C_QP.zip",
            "pfrev26c_qp.zip"
        ]
    else:
        possible_names = [
            "PFREV26C_nonQP.zip",
            "pfrev26c_nonqp.zip"
        ]

    # Search all folders inside Project 2
    for file_path in project_folder.rglob("*.zip"):

        if file_path.name.lower() in [
            name.lower() for name in possible_names
        ]:
            return file_path

    return None


def read_physician_zip(zip_path, file_type):
    """
    Read the TXT file from a Physician ZIP file.
    """

    zip_path = Path(zip_path)

    with ZipFile(zip_path, "r") as zip_ref:

        txt_files = [
            name
            for name in zip_ref.namelist()
            if name.lower().endswith(".txt")
        ]

        if not txt_files:
            raise FileNotFoundError(
                f"No TXT file found inside {zip_path.name}"
            )

        txt_file = txt_files[0]

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

    df = pd.DataFrame(
        rows,
        columns=COLUMNS
    )

    df["FILE_TYPE"] = file_type
    df["SOURCE_FILE"] = zip_path.name

    return df


if __name__ == "__main__":

    # ---------------------------------------------------------
    # PROJECT 2 FOLDER
    # ---------------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parent

    print("\n==============================================")
    print("CMS PHYSICIAN DATA PROCESSING")
    print("==============================================")

    print("\nProject folder:")
    print(PROJECT_ROOT)

    # ---------------------------------------------------------
    # FIND QP ZIP
    # ---------------------------------------------------------

    print("\nSearching for Physician QP ZIP...")

    qp_zip = find_physician_zip(
        PROJECT_ROOT,
        "QP"
    )

    if qp_zip is None:

        print("\n[ERROR] Physician QP ZIP file was not found.")

        print("\nExpected file:")
        print("PFREV26C_QP.zip")

        print("\nThe program searched inside:")
        print(PROJECT_ROOT)

        raise FileNotFoundError(
            "PFREV26C_QP.zip was not found inside the Project 2 folder."
        )

    print("[OK] QP ZIP found:")
    print(qp_zip)

    # ---------------------------------------------------------
    # FIND NON-QP ZIP
    # ---------------------------------------------------------

    print("\nSearching for Physician nonQP ZIP...")

    nonqp_zip = find_physician_zip(
        PROJECT_ROOT,
        "nonQP"
    )

    if nonqp_zip is None:

        print("\n[ERROR] Physician nonQP ZIP file was not found.")

        print("\nExpected file:")
        print("PFREV26C_nonQP.zip")

        print("\nThe program searched inside:")
        print(PROJECT_ROOT)

        raise FileNotFoundError(
            "PFREV26C_nonQP.zip was not found inside the Project 2 folder."
        )

    print("[OK] nonQP ZIP found:")
    print(nonqp_zip)

    # ---------------------------------------------------------
    # READ QP DATA
    # ---------------------------------------------------------

    print("\nReading QP Physician data...")

    qp_df = read_physician_zip(
        qp_zip,
        "QP"
    )

    print("[OK] QP data loaded.")
    print("QP rows:", len(qp_df))

    # ---------------------------------------------------------
    # READ NON-QP DATA
    # ---------------------------------------------------------

    print("\nReading nonQP Physician data...")

    nonqp_df = read_physician_zip(
        nonqp_zip,
        "nonQP"
    )

    print("[OK] nonQP data loaded.")
    print("nonQP rows:", len(nonqp_df))

    # ---------------------------------------------------------
    # COMBINE DATA
    # ---------------------------------------------------------

    physician_df = pd.concat(
        [
            qp_df,
            nonqp_df
        ],
        ignore_index=True
    )

    print("\n==============================================")
    print("PHYSICIAN DATA LOADED SUCCESSFULLY")
    print("==============================================")

    print("\nTotal rows:")
    print(len(physician_df))

    print("\nTotal columns:")
    print(len(physician_df.columns))

    print("\nColumns:")
    print(physician_df.columns.tolist())

    # ---------------------------------------------------------
    # FIRST 5 ROWS
    # ---------------------------------------------------------

    print("\nFirst 5 rows:")
    print(
        physician_df.head()
    )

    # ---------------------------------------------------------
    # DATA TYPES
    # ---------------------------------------------------------

    print("\nData types:")
    print(
        physician_df.dtypes
    )

    # ---------------------------------------------------------
    # FILE TYPE COUNTS
    # ---------------------------------------------------------

    print("\nFILE_TYPE counts:")
    print(
        physician_df["FILE_TYPE"].value_counts()
    )

    # ---------------------------------------------------------
    # STATUS CODE COUNTS
    # ---------------------------------------------------------

    print("\nStatus Code counts:")
    print(
        physician_df["STATUS_CODE"].value_counts()
    )

    # ---------------------------------------------------------
    # SAMPLE PHYSICIAN RECORDS
    # ---------------------------------------------------------

    print("\nSample Physician records:")

    sample_columns = [
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

    print(
        physician_df[
            sample_columns
        ].head(10).to_string(index=False)
    )

    # ---------------------------------------------------------
    # CREATE OUTPUT FOLDER
    # ---------------------------------------------------------

    output_dir = PROJECT_ROOT / "output"

    output_dir.mkdir(
        exist_ok=True
    )

    # ---------------------------------------------------------
    # SAVE CSV
    # ---------------------------------------------------------

    output_file = (
        output_dir /
        "cms_physician_combined.csv"
    )

    physician_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print("\n==============================================")
    print("PHYSICIAN OUTPUT CREATED")
    print("==============================================")

    print("\n[OK] Physician dataset created:")
    print(output_file)

    print("\nRows saved:")
    print(len(physician_df))

    print("\n==============================================")
    print("PHYSICIAN PROCESS COMPLETED")
    print("==============================================")