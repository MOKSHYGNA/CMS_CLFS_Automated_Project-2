import csv
import io
import urllib.request
from zipfile import ZipFile
from pathlib import Path

import pandas as pd


# ============================================================
# PHYSICIAN DATA COLUMNS
# ============================================================

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


# ============================================================
# CMS PHYSICIAN FILE
# ============================================================

CMS_URL = (
    "https://www.cms.gov/files/zip/"
    "pfrev26c-posted-06-30-2026.zip"
)


# ============================================================
# PROJECT LOCATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DOWNLOAD_DIR = PROJECT_ROOT / "downloads"

OUTPUT_DIR = PROJECT_ROOT / "output"

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DOWNLOAD CMS FILE
# ============================================================

def download_physician_file():
    """
    Download the official PFREV26C Physician file
    directly from CMS.
    """

    zip_path = DOWNLOAD_DIR / "pfrev26c-posted-06-30-2026.zip"

    print("\n==============================================")
    print("DOWNLOADING CMS PHYSICIAN FILE")
    print("==============================================")

    print("\nCMS source:")
    print(CMS_URL)

    print("\nDownloading...")

    try:

        request = urllib.request.Request(
            CMS_URL,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            data = response.read()

        with open(
            zip_path,
            "wb"
        ) as file:

            file.write(data)

        print("\n[OK] CMS Physician file downloaded.")

        print("Saved to:")
        print(zip_path)

        print("File size:")
        print(
            round(
                len(data) / (1024 * 1024),
                2
            ),
            "MB"
        )

        return zip_path

    except Exception as e:

        print("\n[ERROR] Could not download Physician file.")

        print("Error:")
        print(e)

        raise


# ============================================================
# FIND PHYSICIAN FILE INSIDE CMS ZIP
# ============================================================

def find_file_inside_zip(
    zip_path,
    keywords
):
    """
    Search inside the CMS ZIP file for a file whose
    name contains all requested keywords.
    """

    with ZipFile(
        zip_path,
        "r"
    ) as outer_zip:

        names = outer_zip.namelist()

        for name in names:

            lower_name = name.lower()

            if all(
                keyword.lower() in lower_name
                for keyword in keywords
            ):

                return name

    return None


# ============================================================
# EXTRACT NESTED ZIP
# ============================================================

def extract_nested_zip(
    outer_zip_path,
    nested_zip_name,
    output_path
):
    """
    Extract a ZIP file stored inside another ZIP file.
    """

    with ZipFile(
        outer_zip_path,
        "r"
    ) as outer_zip:

        nested_data = outer_zip.read(
            nested_zip_name
        )

    with open(
        output_path,
        "wb"
    ) as file:

        file.write(nested_data)

    return output_path


# ============================================================
# LOCATE QP AND NON-QP FILES
# ============================================================

def locate_physician_files(
    downloaded_zip
):
    """
    Locate QP and nonQP Physician files inside
    the CMS PFREV26C download.

    The CMS download can contain nested ZIP files,
    so this function handles both ZIP and TXT layouts.
    """

    print("\n==============================================")
    print("LOCATING PHYSICIAN QP / NON-QP FILES")
    print("==============================================")

    with ZipFile(
        downloaded_zip,
        "r"
    ) as outer_zip:

        names = outer_zip.namelist()

        print("\nFiles found inside CMS download:")

        for name in names:
            print(" -", name)

        # ----------------------------------------------------
        # Search for QP ZIP
        # ----------------------------------------------------

        qp_zip_name = None

        for name in names:

            lower_name = name.lower()

            if (
                "qp" in lower_name
                and "nonqp" not in lower_name
                and lower_name.endswith(".zip")
            ):
                qp_zip_name = name
                break

        # ----------------------------------------------------
        # Search for NON-QP ZIP
        # ----------------------------------------------------

        nonqp_zip_name = None

        for name in names:

            lower_name = name.lower()

            if (
                "nonqp" in lower_name
                and lower_name.endswith(".zip")
            ):
                nonqp_zip_name = name
                break

        # ----------------------------------------------------
        # Search for QP TXT
        # ----------------------------------------------------

        qp_txt_name = None

        for name in names:

            lower_name = name.lower()

            if (
                "qp" in lower_name
                and "nonqp" not in lower_name
                and lower_name.endswith(".txt")
            ):
                qp_txt_name = name
                break

        # ----------------------------------------------------
        # Search for NON-QP TXT
        # ----------------------------------------------------

        nonqp_txt_name = None

        for name in names:

            lower_name = name.lower()

            if (
                "nonqp" in lower_name
                and lower_name.endswith(".txt")
            ):
                nonqp_txt_name = name
                break

    # --------------------------------------------------------
    # QP ZIP FOUND
    # --------------------------------------------------------

    if qp_zip_name:

        qp_output = DOWNLOAD_DIR / "PFREV26C_QP.zip"

        extract_nested_zip(
            downloaded_zip,
            qp_zip_name,
            qp_output
        )

        print("\n[OK] QP ZIP found:")
        print(qp_output)

    elif qp_txt_name:

        qp_output = DOWNLOAD_DIR / "PFREV26C_QP.txt"

        with ZipFile(
            downloaded_zip,
            "r"
        ) as zip_ref:

            data = zip_ref.read(
                qp_txt_name
            )

        with open(
            qp_output,
            "wb"
        ) as file:

            file.write(data)

        print("\n[OK] QP TXT found:")
        print(qp_output)

    else:

        qp_output = None

        print("\n[WARNING] QP file was not found.")

    # --------------------------------------------------------
    # NON-QP ZIP FOUND
    # --------------------------------------------------------

    if nonqp_zip_name:

        nonqp_output = (
            DOWNLOAD_DIR /
            "PFREV26C_nonQP.zip"
        )

        extract_nested_zip(
            downloaded_zip,
            nonqp_zip_name,
            nonqp_output
        )

        print("\n[OK] nonQP ZIP found:")
        print(nonqp_output)

    elif nonqp_txt_name:

        nonqp_output = (
            DOWNLOAD_DIR /
            "PFREV26C_nonQP.txt"
        )

        with ZipFile(
            downloaded_zip,
            "r"
        ) as zip_ref:

            data = zip_ref.read(
                nonqp_txt_name
            )

        with open(
            nonqp_output,
            "wb"
        ) as file:

            file.write(data)

        print("\n[OK] nonQP TXT found:")
        print(nonqp_output)

    else:

        nonqp_output = None

        print("\n[WARNING] nonQP file was not found.")

    return qp_output, nonqp_output


# ============================================================
# READ PHYSICIAN ZIP
# ============================================================

def read_physician_zip(
    zip_path,
    file_type
):
    """
    Read the TXT file from a Physician ZIP file.
    """

    zip_path = Path(zip_path)

    print(
        f"\nReading {file_type} Physician data..."
    )

    with ZipFile(
        zip_path,
        "r"
    ) as zip_ref:

        txt_files = [
            name
            for name in zip_ref.namelist()
            if name.lower().endswith(".txt")
        ]

        if not txt_files:

            raise FileNotFoundError(
                f"No TXT file found inside "
                f"{zip_path.name}"
            )

        txt_file = txt_files[0]

        print(
            f"Reading TXT file: {txt_file}"
        )

        with zip_ref.open(
            txt_file
        ) as file:

            text_file = io.TextIOWrapper(
                file,
                encoding="utf-8",
                errors="replace"
            )

            rows = []

            for row in csv.reader(
                text_file
            ):

                if len(row) != len(COLUMNS):

                    continue

                rows.append(row)

    df = pd.DataFrame(
        rows,
        columns=COLUMNS
    )

    df["FILE_TYPE"] = file_type

    df["SOURCE_FILE"] = zip_path.name

    print(
        f"[OK] {file_type} rows loaded:",
        len(df)
    )

    return df


# ============================================================
# READ PHYSICIAN TXT
# ============================================================

def read_physician_txt(
    txt_path,
    file_type
):
    """
    Read a Physician TXT file directly.
    """

    txt_path = Path(txt_path)

    print(
        f"\nReading {file_type} Physician TXT..."
    )

    rows = []

    with open(
        txt_path,
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as file:

        for row in csv.reader(file):

            if len(row) != len(COLUMNS):

                continue

            rows.append(row)

    df = pd.DataFrame(
        rows,
        columns=COLUMNS
    )

    df["FILE_TYPE"] = file_type

    df["SOURCE_FILE"] = txt_path.name

    print(
        f"[OK] {file_type} rows loaded:",
        len(df)
    )

    return df


# ============================================================
# READ ANY PHYSICIAN FILE
# ============================================================

def read_physician_file(
    file_path,
    file_type
):
    """
    Read either a ZIP or TXT Physician file.
    """

    file_path = Path(file_path)

    if file_path.suffix.lower() == ".zip":

        return read_physician_zip(
            file_path,
            file_type
        )

    if file_path.suffix.lower() == ".txt":

        return read_physician_txt(
            file_path,
            file_type
        )

    raise ValueError(
        f"Unsupported Physician file type: "
        f"{file_path}"
    )


# ============================================================
# MAIN PROCESS
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("==============================================")
    print("CMS PHYSICIAN AUTOMATION")
    print("==============================================")

    print("\nProject folder:")
    print(PROJECT_ROOT)

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    downloaded_zip = download_physician_file()

    # --------------------------------------------------------
    # LOCATE QP / NON-QP
    # --------------------------------------------------------

    qp_file, nonqp_file = locate_physician_files(
        downloaded_zip
    )

    # --------------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------------

    if qp_file is None:

        raise FileNotFoundError(
            "CMS QP Physician file could not be located."
        )

    if nonqp_file is None:

        raise FileNotFoundError(
            "CMS nonQP Physician file could not be located."
        )

    # --------------------------------------------------------
    # READ QP
    # --------------------------------------------------------

    qp_df = read_physician_file(
        qp_file,
        "QP"
    )

    # --------------------------------------------------------
    # READ NON-QP
    # --------------------------------------------------------

    nonqp_df = read_physician_file(
        nonqp_file,
        "nonQP"
    )

    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    physician_df = pd.concat(
        [
            qp_df,
            nonqp_df
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # SUCCESS INFORMATION
    # --------------------------------------------------------

    print("\n==============================================")
    print("PHYSICIAN DATA LOADED SUCCESSFULLY")
    print("==============================================")

    print("\nQP rows:")
    print(len(qp_df))

    print("\nnonQP rows:")
    print(len(nonqp_df))

    print("\nTotal rows:")
    print(len(physician_df))

    print("\nTotal columns:")
    print(len(physician_df.columns))

    # --------------------------------------------------------
    # FILE TYPE COUNTS
    # --------------------------------------------------------

    print("\nFILE_TYPE counts:")

    print(
        physician_df[
            "FILE_TYPE"
        ].value_counts()
    )

    # --------------------------------------------------------
    # STATUS CODE COUNTS
    # --------------------------------------------------------

    print("\nStatus Code counts:")

    print(
        physician_df[
            "STATUS_CODE"
        ].value_counts()
    )

    # --------------------------------------------------------
    # SAMPLE RECORDS
    # --------------------------------------------------------

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
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # SAVE OUTPUT
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR /
        "cms_physician_combined.csv"
    )

    physician_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    print("\n==============================================")
    print("PHYSICIAN OUTPUT CREATED")
    print("==============================================")

    print("\n[OK] Physician dataset created:")

    print(output_file)

    print("\nRows saved:")
    print(len(physician_df))

    print("\n==============================================")
    print("PHYSICIAN AUTOMATION COMPLETED")
    print("==============================================")