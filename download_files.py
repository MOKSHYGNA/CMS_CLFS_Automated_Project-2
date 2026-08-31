import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import re
import hashlib
import csv
import shutil

from change_detector import compare_csv_files


# ============================================================
# CONFIGURATION
# ============================================================

CMS_URL = (
    "https://www.cms.gov/medicare/payment/"
    "fee-schedules/clinical-laboratory-fee-schedule-clfs/files"
)

SUPPORTED_YEARS = {"24", "25", "26"}

SUPPORTED_QUARTERS = {
    "Q1",
    "Q2",
    "Q3",
    "Q4"
}

session = requests.Session()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_download_url(url):
    """
    Convert CMS license/download URLs
    into the actual downloadable file URL.
    """

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    if "file" in query:
        file_path = query["file"][0]

        if file_path.startswith("/"):
            return "https://www.cms.gov" + file_path

    return url


def calculate_file_hash(file_path):
    """
    Calculate SHA-256 hash of a file.
    Used to detect whether a CMS ZIP file changed.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def save_hash(hash_file, file_hash):
    """
    Save SHA-256 hash to disk.
    """

    with open(
        hash_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(file_hash)


def load_hash(hash_file):
    """
    Load previously saved SHA-256 hash.
    """

    if not hash_file.exists():
        return None

    try:

        with open(
            hash_file,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read().strip()

    except Exception:

        return None


def read_csv_records(csv_file):
    """
    Read CSV records and return them as a set.

    Blank rows are ignored.
    """

    records = set()

    try:

        with open(
            csv_file,
            "r",
            encoding="utf-8-sig",
            errors="ignore",
            newline=""
        ) as file:

            reader = csv.reader(file)

            for row in reader:

                if not row:
                    continue

                row_text = "|".join(
                    str(value).strip()
                    for value in row
                )

                records.add(row_text)

    except Exception as error:

        print(
            f"[WARNING] Could not read CSV "
            f"{csv_file}: {error}"
        )

    return records


# ============================================================
# STEP 1: CONNECT TO CMS
# ============================================================

print("\nConnecting to CMS website...")

try:

    response = session.get(
        CMS_URL,
        timeout=60
    )

    response.raise_for_status()

except Exception as error:

    print(
        f"[ERROR] Could not connect to CMS: {error}"
    )

    raise SystemExit(1)


soup = BeautifulSoup(
    response.text,
    "html.parser"
)


# ============================================================
# STEP 2: FIND CLFS FILES
# ============================================================

print("\nScanning CMS page for CLFS files...")

selected_files = []

for link in soup.find_all(
    "a",
    href=True
):

    name = link.get_text(
        strip=True
    ).upper()

    match = re.fullmatch(
        r"(\d{2})CLAB(Q[1-4])(V\d+)?",
        name
    )

    if not match:
        continue

    year = match.group(1)

    if year not in SUPPORTED_YEARS:
        continue

    quarter = match.group(2)

    if quarter not in SUPPORTED_QUARTERS:
        continue

    version = match.group(3) or "V1"

    page_url = urljoin(
        CMS_URL,
        link["href"]
    )

    selected_files.append(
        {
            "name": name,
            "year": year,
            "quarter": quarter,
            "version": version,
            "page_url": page_url
        }
    )


print(
    f"[INFO] Detected "
    f"{len(selected_files)} CMS CLFS files."
)


# ============================================================
# STEP 3: REMOVE DUPLICATE FILES
# ============================================================

unique_files = {}

for file in selected_files:

    key = file["name"]

    unique_files[key] = file


selected_files = list(
    unique_files.values()
)


# ============================================================
# STEP 4: FIND ZIP DOWNLOAD LINKS
# ============================================================

for file in selected_files:

    print(
        f"\nFinding download for "
        f"{file['name']}..."
    )

    try:

        page_response = session.get(
            file["page_url"],
            timeout=60
        )

        page_response.raise_for_status()

    except Exception as error:

        print(
            f"[ERROR] Could not open page "
            f"for {file['name']}: {error}"
        )

        continue


    page_soup = BeautifulSoup(
        page_response.text,
        "html.parser"
    )


    for link in page_soup.find_all(
        "a",
        href=True
    ):

        href = link["href"]

        full_url = urljoin(
            file["page_url"],
            href
        )

        if re.search(
            r"\.zip(?:$|\?)",
            full_url,
            re.IGNORECASE
        ):

            file["download_url"] = (
                get_download_url(full_url)
            )

            break


# ============================================================
# STEP 5: CHECK CMS FILES
# ============================================================

print("\n")
print("=" * 60)
print("CHECKING CMS FILES FOR NEW OR CHANGED DATA")
print("=" * 60)


base_folder = Path("downloads")

files_to_process = []


for file in selected_files:

    year_folder = (
        base_folder /
        f"20{file['year']}"
    )

    quarter_folder = (
        year_folder /
        file["quarter"]
    )

    extract_folder = (
        quarter_folder /
        file["name"]
    )

    zip_path = (
        quarter_folder /
        f"{file['name']}.zip"
    )

    hash_path = (
        quarter_folder /
        f"{file['name']}.sha256"
    )


    # ========================================================
    # CASE 1: FILE DOES NOT EXIST
    # ========================================================

    if not zip_path.exists():

        print(
            f"[NEW FILE] "
            f"{file['name']} not downloaded."
        )

        file["status"] = "NEW"

        files_to_process.append(
            file
        )

        continue


    # ========================================================
    # CASE 2: ZIP EXISTS BUT DATA IS MISSING
    # ========================================================

    if (
        not extract_folder.exists()
        or not any(
            extract_folder.rglob("*.csv")
        )
    ):

        print(
            f"[MISSING DATA] "
            f"{file['name']} needs extraction."
        )

        file["status"] = "NEW"

        files_to_process.append(
            file
        )

        continue


    # ========================================================
    # CASE 3: EXISTING FILE
    # CHECK WHETHER CMS FILE CHANGED
    # ========================================================

    print(
        f"\n[CHECK] Checking for updates: "
        f"{file['name']}"
    )


    if "download_url" not in file:

        print(
            f"[WARNING] No download URL found "
            f"for {file['name']}"
        )

        continue


    quarter_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    temp_zip_path = (
        quarter_folder /
        f"{file['name']}_temp.zip"
    )


    try:

        print(
            "[INFO] Checking CMS file..."
        )


        check_response = session.get(
            file["download_url"],
            stream=True,
            timeout=120
        )

        check_response.raise_for_status()


        with open(
            temp_zip_path,
            "wb"
        ) as output_file:

            for chunk in check_response.iter_content(
                chunk_size=8192
            ):

                if chunk:
                    output_file.write(chunk)


        current_hash = calculate_file_hash(
            temp_zip_path
        )


        previous_hash = load_hash(
            hash_path
        )


        # ====================================================
        # FIRST RUN
        # CREATE BASELINE HASH
        # ====================================================

        if previous_hash is None:

            old_hash = calculate_file_hash(
                zip_path
            )

            save_hash(
                hash_path,
                old_hash
            )

            previous_hash = old_hash


        # ====================================================
        # NO CHANGE
        # ====================================================

        if current_hash == previous_hash:

            print(
                f"[UNCHANGED] "
                f"{file['name']} has no changes."
            )

            temp_zip_path.unlink(
                missing_ok=True
            )

            continue


        # ====================================================
        # CHANGE DETECTED
        # ====================================================

        print(
            f"[CHANGE DETECTED] "
            f"{file['name']} has been updated on CMS."
        )


        print(
            f"[INFO] Old hash: "
            f"{previous_hash}"
        )


        print(
            f"[INFO] New hash: "
            f"{current_hash}"
        )


        file["status"] = "UPDATED"

        file["current_hash"] = current_hash

        file["temp_zip_path"] = (
            temp_zip_path
        )

        files_to_process.append(
            file
        )


    except Exception as error:

        print(
            f"[ERROR] Could not check "
            f"{file['name']}: {error}"
        )

        if temp_zip_path.exists():

            temp_zip_path.unlink()

        continue


# ============================================================
# STEP 6: DOWNLOAD / UPDATE / DETECT CHANGES
# ============================================================

print("\n")
print("=" * 60)
print("STARTING AUTOMATIC DOWNLOAD / UPDATE")
print("=" * 60)


for file in files_to_process:

    if "download_url" not in file:

        print(
            f"[ERROR] No ZIP found for "
            f"{file['name']}"
        )

        continue


    year_folder = (
        base_folder /
        f"20{file['year']}"
    )

    quarter_folder = (
        year_folder /
        file["quarter"]
    )


    quarter_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    zip_path = (
        quarter_folder /
        f"{file['name']}.zip"
    )


    extract_folder = (
        quarter_folder /
        file["name"]
    )


    hash_path = (
        quarter_folder /
        f"{file['name']}.sha256"
    )


    print("\n" + "-" * 60)

    print(
        f"PROCESSING: {file['name']}"
    )

    print(
        f"STATUS: {file.get('status', 'UNKNOWN')}"
    )


    try:

        # ====================================================
        # SAVE OLD CSV BEFORE DELETING OLD DATA
        # ====================================================

        old_csv_files = []

        if extract_folder.exists():

            old_csv_files = list(
                extract_folder.rglob("*.csv")
            )


        old_csv_backup = None


        if (
            file.get("status") == "UPDATED"
            and old_csv_files
        ):

            old_csv_backup = (
                quarter_folder /
                f"{file['name']}_old.csv"
            )


            print(
                "[INFO] Creating backup "
                "of previous CSV..."
            )


            shutil.copy2(
                old_csv_files[0],
                old_csv_backup
            )


            print(
                f"[OK] Old CSV backed up to: "
                f"{old_csv_backup}"
            )


        # ====================================================
        # USE TEMP ZIP IF FILE WAS UPDATED
        # ====================================================

        temp_zip_path = file.get(
            "temp_zip_path"
        )


        if (
            temp_zip_path
            and Path(temp_zip_path).exists()
        ):

            print(
                "[INFO] Using newly downloaded "
                "updated ZIP."
            )


            Path(
                temp_zip_path
            ).replace(
                zip_path
            )


        else:

            # =================================================
            # DOWNLOAD NEW FILE
            # =================================================

            print(
                f"\nDownloading "
                f"{file['name']}..."
            )


            print(
                f"URL: "
                f"{file['download_url']}"
            )


            download_response = session.get(
                file["download_url"],
                stream=True,
                timeout=120
            )


            download_response.raise_for_status()


            with open(
                zip_path,
                "wb"
            ) as output_file:

                for chunk in download_response.iter_content(
                    chunk_size=8192
                ):

                    if chunk:
                        output_file.write(chunk)


            print(
                f"[OK] Downloaded: "
                f"{zip_path}"
            )


        # ====================================================
        # DELETE OLD EXTRACTION
        # ====================================================

        if extract_folder.exists():

            shutil.rmtree(
                extract_folder
            )


        # ====================================================
        # EXTRACT NEW ZIP
        # ====================================================

        extract_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        print(
            f"[INFO] Extracting "
            f"{file['name']}..."
        )


        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_file:

            zip_file.extractall(
                extract_folder
            )


        print(
            f"[OK] Extracted to: "
            f"{extract_folder}"
        )


        # ====================================================
        # FIND NEW CSV FILES
        # ====================================================

        csv_files = list(
            extract_folder.rglob("*.csv")
        )


        if not csv_files:

            print(
                f"[WARNING] No CSV found "
                f"inside {file['name']}"
            )

            continue


        for csv_file in csv_files:

            print(
                f"[OK] CSV found: "
                f"{csv_file}"
            )


        # ====================================================
        # DETECT RECORD CHANGES
        # ====================================================

        if (
            file.get("status") == "UPDATED"
            and old_csv_backup is not None
        ):

            print("\n")

            print(
                "=" * 60
            )

            print(
                "DETECTING RECORD CHANGES"
            )

            print(
                "=" * 60
            )


            try:

                change_report = compare_csv_files(
                    old_csv_backup,
                    csv_files[0]
                )


                print("\n")

                print(
                    "=" * 60
                )

                print(
                    f"RECORD CHANGE REPORT: "
                    f"{file['name']}"
                )

                print(
                    "=" * 60
                )


                print(
                    f"Previous records: "
                    f"{change_report['old_count']}"
                )


                print(
                    f"Current records: "
                    f"{change_report['new_count']}"
                )


                print(
                    f"New records detected: "
                    f"{change_report['new_count_records']}"
                )


                print(
                    f"Removed records: "
                    f"{change_report['removed_count']}"
                )


                print(
                    f"Modified records: "
                    f"{change_report['modified_count']}"
                )


                # ============================================
                # SHOW NEW RECORDS
                # ============================================

                new_records = (
                    change_report.get(
                        "new_records",
                        []
                    )
                )


                if new_records:

                    print(
                        "\n[NEW RECORDS DETECTED]"
                    )


                    for index, record in enumerate(
                        new_records
                    ):

                        if index >= 10:
                            break


                        print(
                            f"  {record}"
                        )


                    if len(new_records) > 10:

                        print(
                            f"  ... and "
                            f"{len(new_records) - 10} "
                            f"more new records."
                        )


                else:

                    print(
                        "\n[INFO] No completely "
                        "new records detected."
                    )


                # ============================================
                # SHOW MODIFIED RECORDS
                # ============================================

                modified_records = (
                    change_report.get(
                        "modified_records",
                        []
                    )
                )


                if modified_records:

                    print(
                        "\n[MODIFIED RECORDS DETECTED]"
                    )


                    for index, record in enumerate(
                        modified_records
                    ):

                        if index >= 10:
                            break


                        print(
                            f"  {record}"
                        )


                    if len(modified_records) > 10:

                        print(
                            f"  ... and "
                            f"{len(modified_records) - 10} "
                            f"more modified records."
                        )


            except Exception as error:

                print(
                    f"[ERROR] Record comparison failed: "
                    f"{error}"
                )


        # ====================================================
        # UPDATE HASH
        # ====================================================

        new_hash = calculate_file_hash(
            zip_path
        )


        save_hash(
            hash_path,
            new_hash
        )


        print(
            "[OK] Hash updated."
        )


        # ====================================================
        # REMOVE OLD CSV BACKUP
        # ====================================================

        if old_csv_backup is not None:

            old_csv_backup.unlink(
                missing_ok=True
            )


    except Exception as error:

        print(
            f"[ERROR] Error processing "
            f"{file['name']}: {error}"
        )


# ============================================================
# FINISH
# ============================================================

print("\n")

print("=" * 60)

print(
    "DOWNLOAD / UPDATE STEP COMPLETED"
)

print("=" * 60)


print(
    "\n[INFO] CMS monitoring completed."
)


print(
    "[INFO] New files and changed files "
    "have been checked."
)


print(
    "[INFO] New, removed and modified "
    "records were detected where applicable."
)


print(
    "[INFO] The remaining ETL pipeline "
    "can now process the data."
)