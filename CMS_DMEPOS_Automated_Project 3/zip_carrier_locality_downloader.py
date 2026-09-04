import hashlib
import json
import re
import requests
from pathlib import Path
from urllib.parse import urljoin


CMS_FEE_SCHEDULE_URL = "https://www.cms.gov/medicare/payment/fee-schedules"

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads" / "zip_carrier_locality"
MANIFEST_FILE = OUTPUT_DIR / "zip_carrier_locality_manifest.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_manifest():
    if not MANIFEST_FILE.exists():
        return {}

    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)


def find_zip_url():
    print("Checking CMS Fee Schedules page...")

    response = requests.get(
        CMS_FEE_SCHEDULE_URL,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    html = response.text

    print(f"CMS page downloaded successfully: {len(html)} characters")

    matches = re.findall(
        r'href=["\']([^"\']+\.zip)["\']',
        html,
        flags=re.IGNORECASE
    )

    candidate_urls = []

    for href in matches:
        url = urljoin(CMS_FEE_SCHEDULE_URL, href)
        url_lower = url.lower()

        if (
            "zip-code-carrier-locality" in url_lower
            or "carrier-locality" in url_lower
        ):
            if url not in candidate_urls:
                candidate_urls.append(url)

    if not candidate_urls:
        raise RuntimeError(
            "Could not find the Zip Code to Carrier Locality ZIP file on CMS."
        )

    print(f"Found ZIP URL: {candidate_urls[0]}")

    return candidate_urls[0]


def download_file(url, destination):
    print("Downloading ZIP file...")
    print(f"URL: {url}")

    response = requests.get(
        url,
        headers=HEADERS,
        stream=True,
        timeout=120
    )

    response.raise_for_status()

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    print(f"Downloaded: {destination}")

    return destination


def detect_zip_carrier_locality_change():
    manifest = load_manifest()

    zip_url = find_zip_url()

    file_name = Path(zip_url.split("?")[0]).name

    if not file_name.lower().endswith(".zip"):
        file_name = "zip_carrier_locality.zip"

    local_file = DOWNLOAD_DIR / file_name

    previous_hash = manifest.get("sha256")
    previous_url = manifest.get("file_url")
    previous_processed = manifest.get("processed", False)

    # ---------------------------------------------------------
    # Case 1: Local file exists
    # ---------------------------------------------------------

    if local_file.exists():

        current_hash = calculate_sha256(local_file)

        print(f"Local file found: {local_file}")
        print(f"Current SHA-256: {current_hash}")

        if (
            previous_url == zip_url
            and previous_hash == current_hash
            and previous_processed is True
        ):
            print("No change detected.")
            print("ZIP Carrier Locality file was already processed.")

            return {
                "status": "no_change",
                "file_url": zip_url,
                "local_file": str(local_file),
                "sha256": current_hash
            }

        if previous_processed is not True:
            print("File exists but has not been processed.")
            print("Status: process")

            return {
                "status": "process",
                "file_url": zip_url,
                "local_file": str(local_file),
                "sha256": current_hash
            }

        if previous_hash != current_hash:
            print("File content has changed.")
            print("Status: process")

            return {
                "status": "process",
                "file_url": zip_url,
                "local_file": str(local_file),
                "sha256": current_hash
            }

        if previous_url != zip_url:
            print("CMS file URL has changed.")
            print("Status: process")

            return {
                "status": "process",
                "file_url": zip_url,
                "local_file": str(local_file),
                "sha256": current_hash
            }

    # ---------------------------------------------------------
    # Case 2: File does not exist
    # ---------------------------------------------------------

    print("No processed local file found.")

    download_file(zip_url, local_file)

    current_hash = calculate_sha256(local_file)

    print(f"SHA-256: {current_hash}")
    print("Status: process")

    return {
        "status": "process",
        "file_url": zip_url,
        "local_file": str(local_file),
        "sha256": current_hash
    }


if __name__ == "__main__":

    try:
        result = detect_zip_carrier_locality_change()

        print()
        print("==============================================")
        print("ZIP CARRIER LOCALITY DETECTION RESULT")
        print("==============================================")
        print(f"Status    : {result['status']}")
        print(f"File URL  : {result['file_url']}")
        print(f"Local File: {result['local_file']}")
        print(f"SHA-256   : {result['sha256']}")
        print("==============================================")

    except Exception as error:

        print()
        print("==============================================")
        print("ERROR")
        print("==============================================")
        print(error)
        print("==============================================")