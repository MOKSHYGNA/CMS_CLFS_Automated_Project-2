import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import zipfile
import re


# ============================================================
# CONFIGURATION
# ============================================================

CMS_URL = "https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule"

BASE_URL = "https://www.cms.gov"

DOWNLOAD_FOLDER = Path("downloads")

DOWNLOAD_FOLDER.mkdir(exist_ok=True)


# ============================================================
# GET CMS PAGE
# ============================================================

def get_cms_page():

    print("\n" + "=" * 70)
    print("ACCESSING CMS DMEPOS PAGE")
    print("=" * 70)

    response = requests.get(CMS_URL)

    response.raise_for_status()

    print("CMS page accessed successfully!")

    return response.text


# ============================================================
# FIND DME RELEASE PAGES
# ============================================================

def find_dme_release_pages(html):

    print("\n" + "=" * 70)
    print("FINDING DME RELEASE PAGES")
    print("=" * 70)

    soup = BeautifulSoup(html, "html.parser")

    release_pages = []

    for link in soup.find_all("a", href=True):

        text = link.get_text(" ", strip=True)
        href = link["href"]

        # Match DME release names such as:
        # DME26-A
        # DME26-B
        # DME26-C
        # DME25-A
        # DME25-B

        if re.match(r"^DME\d{2}", text, re.IGNORECASE):

            full_url = urljoin(BASE_URL, href)

            release_pages.append({
                "name": text,
                "url": full_url
            })

    # Remove duplicate URLs

    unique_pages = {}

    for item in release_pages:

        unique_pages[item["url"]] = item

    release_pages = list(unique_pages.values())

    print(f"Release pages found: {len(release_pages)}")

    for item in release_pages:

        print(f"{item['name']} -> {item['url']}")

    return release_pages


# ============================================================
# FIND ZIP FILE
# ============================================================

def find_zip_link(release):

    print("\n" + "-" * 70)
    print(f"CHECKING RELEASE: {release['name']}")
    print("-" * 70)

    response = requests.get(release["url"])

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):

        href = link["href"]

        full_url = urljoin(BASE_URL, href)

        if "/files/zip/" in full_url.lower():

            print(f"ZIP found: {full_url}")

            return full_url

    print("No ZIP file found.")

    return None


# ============================================================
# CHECK WHETHER FILE ALREADY EXISTS
# ============================================================

def file_already_exists(zip_url):

    file_name = zip_url.split("/")[-1]

    zip_path = DOWNLOAD_FOLDER / file_name

    return zip_path.exists()


# ============================================================
# DOWNLOAD FILE
# ============================================================

def download_file(zip_url, release_name):

    file_name = zip_url.split("/")[-1]

    zip_path = DOWNLOAD_FOLDER / file_name

    print("\n" + "-" * 70)
    print(f"DOWNLOADING: {release_name}")
    print("-" * 70)

    response = requests.get(zip_url, stream=True)

    response.raise_for_status()

    with open(zip_path, "wb") as file:

        for chunk in response.iter_content(chunk_size=8192):

            if chunk:

                file.write(chunk)

    print(f"Downloaded: {zip_path}")

    return zip_path


# ============================================================
# EXTRACT FILE
# ============================================================

def extract_zip(zip_path):

    folder_name = zip_path.stem

    extract_folder = DOWNLOAD_FOLDER / folder_name

    # If already extracted, don't extract again

    if extract_folder.exists():

        print(f"Already extracted: {extract_folder}")

        return extract_folder

    print("\n" + "-" * 70)
    print(f"EXTRACTING: {zip_path.name}")
    print("-" * 70)

    extract_folder.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:

        zip_ref.extractall(extract_folder)

    print(f"Extracted to: {extract_folder}")

    return extract_folder


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("CMS DMEPOS AUTOMATED DOWNLOAD SYSTEM")
    print("=" * 70)

    # STEP 1
    html = get_cms_page()

    # STEP 2
    releases = find_dme_release_pages(html)

    print("\n")
    print("=" * 70)
    print("CHECKING FOR NEW FILES")
    print("=" * 70)

    new_files = 0
    existing_files = 0

    # STEP 3
    for release in releases:

        try:

            zip_url = find_zip_link(release)

            if zip_url is None:

                continue

            # STEP 4
            # Check whether ZIP already exists

            if file_already_exists(zip_url):

                print(
                    f"ALREADY EXISTS: {zip_url.split('/')[-1]}"
                )

                existing_files += 1

                continue

            # STEP 5
            # New file found

            print(
                f"NEW FILE DETECTED: {release['name']}"
            )

            zip_path = download_file(
                zip_url,
                release["name"]
            )

            # STEP 6
            extract_zip(zip_path)

            new_files += 1

        except Exception as e:

            print(
                f"ERROR processing {release['name']}: {e}"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("DOWNLOAD PROCESS COMPLETED")
    print("=" * 70)

    print(f"Existing files : {existing_files}")
    print(f"New files      : {new_files}")

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
    