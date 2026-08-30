
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import re


CMS_URL = "https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs/files"

TARGET_YEARS = {"24", "25", "26"}
TARGET_QUARTERS = {"Q1", "Q2", "Q3"}

session = requests.Session()


def get_download_url(url):
    """
    Convert CMS license/download URLs into the actual ZIP URL.
    """

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    if "file" in query:
        file_path = query["file"][0]

        if file_path.startswith("/"):
            return "https://www.cms.gov" + file_path

    return url


# --------------------------------------------------
# STEP 1: Get CMS main page
# --------------------------------------------------

print("\nConnecting to CMS website...")

response = session.get(CMS_URL)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")


# --------------------------------------------------
# STEP 2: Find required CLAB pages
# --------------------------------------------------

selected_files = []

for link in soup.find_all("a", href=True):

    name = link.get_text(strip=True).upper()

    match = re.fullmatch(
        r"(\d{2})CLAB(Q[1-3])(V\d+)?",
        name
    )

    if match:

        year = match.group(1)
        quarter = match.group(2)
        version = match.group(3) or "V1"

        if year in TARGET_YEARS and quarter in TARGET_QUARTERS:

            page_url = urljoin(
                CMS_URL,
                link["href"]
            )

            selected_files.append({
                "name": name,
                "year": year,
                "quarter": quarter,
                "version": version,
                "page_url": page_url
            })


# --------------------------------------------------
# STEP 3: Find ZIP links
# --------------------------------------------------

for file in selected_files:

    print(f"\nFinding download for {file['name']}...")

    page_response = session.get(file["page_url"])
    page_response.raise_for_status()

    page_soup = BeautifulSoup(
        page_response.text,
        "html.parser"
    )

    for link in page_soup.find_all("a", href=True):

        href = link["href"]

        full_url = urljoin(
            file["page_url"],
            href
        )

        if re.search(
            r"\.zip",
            full_url,
            re.IGNORECASE
        ):

            file["download_url"] = get_download_url(full_url)

            break


# --------------------------------------------------
# STEP 4: Download files
# --------------------------------------------------

print("\n")
print("=" * 60)
print("STARTING AUTOMATIC DOWNLOAD")
print("=" * 60)


base_folder = Path("downloads")


for file in selected_files:

    if "download_url" not in file:

        print(
            f"[ERROR] No ZIP found for {file['name']}"
        )

        continue


    year_folder = base_folder / f"20{file['year']}"

    quarter_folder = year_folder / file["quarter"]

    quarter_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    zip_path = quarter_folder / f"{file['name']}.zip"


    print(f"\nDownloading {file['name']}...")
    print(f"URL: {file['download_url']}")


    try:

        # --------------------------------------------------
        # Download ZIP
        # --------------------------------------------------

        download_response = session.get(
            file["download_url"],
            stream=True
        )

        download_response.raise_for_status()


        with open(zip_path, "wb") as output_file:

            for chunk in download_response.iter_content(
                chunk_size=8192
            ):

                if chunk:
                    output_file.write(chunk)


        print(f"[OK] Downloaded: {zip_path}")


        # --------------------------------------------------
        # STEP 5: Extract ZIP file
        # --------------------------------------------------

        extract_folder = (
            quarter_folder / file["name"]
        )


        extract_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        print(
            f"[INFO] Extracting {file['name']}..."
        )


        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_file:

            zip_file.extractall(
                extract_folder
            )


        print(
            f"[OK] Extracted to: {extract_folder}"
        )


        # --------------------------------------------------
        # Find CSV files
        # --------------------------------------------------

        csv_files = list(
            extract_folder.rglob("*.csv")
        )


        if csv_files:

            for csv_file in csv_files:

                print(
                    f"[OK] CSV found: {csv_file}"
                )

        else:

            print(
                f"[WARNING] No CSV found inside {file['name']}"
            )


    except Exception as error:

        print(
            f"[ERROR] Error processing "
            f"{file['name']}: {error}"
        )


# --------------------------------------------------
# FINISH
# --------------------------------------------------

print("\n")
print("=" * 60)
print("DOWNLOAD STEP COMPLETED")
print("=" * 60)

