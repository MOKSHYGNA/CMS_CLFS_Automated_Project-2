import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import re
import zipfile


# ============================================================
# CONFIGURATION
# ============================================================

CMS_URL = "https://www.cms.gov/anesthesiologists-information-center"

DOWNLOAD_DIR = Path("downloads/anesthesia")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mentor requirement: same table format for 3 years
REQUIRED_YEARS = [2024, 2025, 2026]


# ============================================================
# FIND ANESTHESIA FILES
# ============================================================

def find_anesthesia_files():

    print("\n" + "=" * 60)
    print("CMS ANESTHESIA FILE DETECTOR")
    print("=" * 60)

    try:

        response = requests.get(
            CMS_URL,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

    except Exception as error:

        print(
            f"[ERROR] Could not access CMS: {error}"
        )

        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    files = []

    for link in soup.find_all("a", href=True):

        link_text = link.get_text(
            " ",
            strip=True
        )

        href = link["href"]

        if "Anesthesia Conversion Factors" not in link_text:
            continue

        if not href.lower().endswith(".zip"):
            continue

        year_match = re.search(
            r"(20\d{2})",
            link_text
        )

        if not year_match:
            continue

        year = int(
            year_match.group(1)
        )

        full_url = urljoin(
            CMS_URL,
            href
        )

        files.append(
            {
                "year": year,
                "name": link_text,
                "url": full_url
            }
        )

    return files


# ============================================================
# SELECT REQUIRED THREE YEARS
# ============================================================

def select_required_files(files):

    selected_files = []

    print("\nRequired Anesthesia years:")

    for year in REQUIRED_YEARS:

        matching_files = [
            file
            for file in files
            if file["year"] == year
        ]

        if matching_files:

            selected = matching_files[0]

            selected_files.append(
                selected
            )

            print(
                f"[OK] {year}: "
                f"{selected['name']}"
            )

        else:

            print(
                f"[WARNING] {year}: "
                f"No file found on CMS page."
            )

    return selected_files


# ============================================================
# DOWNLOAD ZIP
# ============================================================

def download_file(file_info):

    year = file_info["year"]

    output_file = (
        DOWNLOAD_DIR /
        f"anesthesia_{year}.zip"
    )

    # Avoid downloading the same file repeatedly
    if output_file.exists():

        print(
            f"\n[SKIP] {year} already downloaded:"
        )

        print(
            f"       {output_file}"
        )

        return output_file

    print(
        f"\nDownloading {year}:"
    )

    print(
        file_info["name"]
    )

    try:

        response = requests.get(
            file_info["url"],
            timeout=60,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        output_file.write_bytes(
            response.content
        )

        print(
            f"[OK] Downloaded: "
            f"{output_file}"
        )

        return output_file

    except Exception as error:

        print(
            f"[ERROR] Download failed for "
            f"{year}: {error}"
        )

        return None


# ============================================================
# EXTRACT ZIP
# ============================================================

def extract_zip(zip_file):

    extract_dir = (
        DOWNLOAD_DIR /
        zip_file.stem
    )

    # If already extracted, don't extract again
    if extract_dir.exists():

        print(
            f"[SKIP] Already extracted:"
            f" {extract_dir}"
        )

        return extract_dir

    extract_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        with zipfile.ZipFile(
            zip_file,
            "r"
        ) as zip_ref:

            zip_ref.extractall(
                extract_dir
            )

        print(
            f"[OK] Extracted to: "
            f"{extract_dir}"
        )

        print("\nExtracted files:")

        for file in extract_dir.rglob("*"):

            if file.is_file():

                print(
                    f" - {file}"
                )

        return extract_dir

    except Exception as error:

        print(
            f"[ERROR] Extraction failed: "
            f"{error}"
        )

        return None


# ============================================================
# MAIN
# ============================================================

def main():

    files = find_anesthesia_files()

    if not files:

        print(
            "[ERROR] No Anesthesia files found."
        )

        return False

    selected_files = select_required_files(
        files
    )

    if not selected_files:

        print(
            "[ERROR] None of the required "
            "Anesthesia files were found."
        )

        return False

    print("\n" + "=" * 60)
    print("DOWNLOADING REQUIRED ANESTHESIA FILES")
    print("=" * 60)

    for file_info in selected_files:

        zip_file = download_file(
            file_info
        )

        if zip_file is None:
            continue

        extract_zip(
            zip_file
        )

    print("\n" + "=" * 60)
    print("ANESTHESIA DOWNLOAD COMPLETED")
    print("=" * 60)

    return True


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    success = main()

    if not success:

        raise SystemExit(1)