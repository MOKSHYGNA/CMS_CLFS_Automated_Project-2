import json
import hashlib
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import re


# ============================================================
# CONFIGURATION
# ============================================================

CMS_MAIN_URL = (
    "https://www.cms.gov/medicare/payment/fee-schedules/"
    "dmepos/dmepos-fee-schedule"
)

OUTPUT_DIR = Path("output")
DOWNLOAD_DIR = Path("downloads")
MANIFEST_FILE = OUTPUT_DIR / "dme_release_manifest.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ============================================================
# DIRECTORY SETUP
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MANIFEST FUNCTIONS
# ============================================================

def load_manifest():
    """
    Load the release tracking manifest.

    The manifest keeps track of:
    - release name
    - CMS release URL
    - ZIP URL
    - local downloaded file
    - SHA-256 hash
    - processed status
    - processing timestamps
    """

    if not MANIFEST_FILE.exists():
        return {}

    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        print("WARNING: Manifest could not be read.")
        print("Starting with an empty manifest.")
        return {}


def save_manifest(manifest):
    """
    Save the manifest to disk.
    """

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)


# ============================================================
# SHA-256
# ============================================================

def calculate_sha256(file_path):
    """
    Calculate SHA-256 hash for a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================
# DOWNLOAD
# ============================================================

def download_file(url, destination):
    """
    Download a file from CMS.
    """

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading:")
    print(url)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=120
    )

    response.raise_for_status()

    with open(destination, "wb") as f:
        f.write(response.content)

    print(f"Downloaded: {destination}")

    return destination


# ============================================================
# CMS RELEASE DISCOVERY
# ============================================================

def get_cms_releases():
    """
    Find current-year DMEPOS releases from the CMS page.

    Example:
        DME26-A
        DME26-B
        DME26-C
    """

    print("Checking CMS DMEPOS page...")

    response = requests.get(
        CMS_MAIN_URL,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    current_year = datetime.now().year % 100

    release_pattern = re.compile(
        rf"DME{current_year:02d}-[A-Z]+",
        re.IGNORECASE
    )

    releases = {}

    for link in soup.find_all("a", href=True):

        text = link.get_text(" ", strip=True)
        href = link["href"]

        match = release_pattern.search(text)

        if not match:
            continue

        release_name = match.group(0).upper()

        if href.startswith("/"):
            release_url = "https://www.cms.gov" + href
        elif href.startswith("http"):
            release_url = href
        else:
            continue

        releases[release_name] = release_url

    print(f"Total CMS releases found: {len(soup.find_all('a', href=True))}")
    print(f"Current year releases found: {len(releases)}")

    return dict(sorted(releases.items()))


# ============================================================
# FIND ZIP FILE
# ============================================================

def get_zip_url(release_url):
    """
    Open the individual CMS release page and find its ZIP file.
    """

    response = requests.get(
        release_url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):

        href = link["href"]

        if ".zip" not in href.lower():
            continue

        if href.startswith("/"):
            return "https://www.cms.gov" + href

        if href.startswith("http"):
            return href

    return None


# ============================================================
# CHANGE DETECTION
# ============================================================

def detect_changes():
    """
    Detect new, changed, or unprocessed CMS DMEPOS releases.

    Logic:

        New release
            -> process

        Existing release + processed = False
            -> process

        Existing release + processed = True + same SHA
            -> skip

        Existing release + processed = True + different SHA
            -> reprocess

        Existing release + processed = True + local file missing
            -> download and process
    """

    manifest = load_manifest()

    print()
    print("=" * 60)
    print("CHANGE DETECTION")
    print("=" * 60)

    releases = get_cms_releases()

    changes = []

    for release_name, release_url in releases.items():

        print()
        print("----------------------------------------")
        print(f"Release: {release_name}")
        print("----------------------------------------")

        zip_url = get_zip_url(release_url)

        if not zip_url:

            print("ERROR: ZIP file not found.")
            continue

        print(f"ZIP URL: {zip_url}")

        # ----------------------------------------------------
        # Local ZIP location
        # ----------------------------------------------------

        release_directory = DOWNLOAD_DIR / release_name.lower()

        release_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        zip_filename = Path(zip_url).name

        local_file = release_directory / zip_filename

        # ----------------------------------------------------
        # Existing manifest record
        # ----------------------------------------------------

        existing = manifest.get(release_name)

        # ====================================================
        # CASE 1: NEW RELEASE
        # ====================================================

        if existing is None:

            print("NEW RELEASE DETECTED.")

            try:

                download_file(
                    zip_url,
                    local_file
                )

                file_hash = calculate_sha256(local_file)

                manifest[release_name] = {
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": file_hash,
                    "status": "downloaded",
                    "processed": False,
                    "detected_at": datetime.now().isoformat()
                }

                changes.append({
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": file_hash
                })

                print("STATUS: NEW")
                print("Action: PROCESS")

            except Exception as e:

                print(f"ERROR downloading {release_name}: {e}")

                manifest[release_name] = {
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": None,
                    "status": "download_failed",
                    "processed": False,
                    "error": str(e),
                    "detected_at": datetime.now().isoformat()
                }

            continue

        # ====================================================
        # CASE 2: RELEASE EXISTS BUT WAS NOT PROCESSED
        # ====================================================

        processed = existing.get("processed", False)

        if not processed:

            print("Release is already tracked.")
            print("BUT it has not been successfully processed.")

            # -----------------------------------------------
            # Local file exists
            # -----------------------------------------------

            if local_file.exists():

                print("Local ZIP exists.")
                print("Action: PROCESS EXISTING FILE.")

                file_hash = calculate_sha256(local_file)

                # Update hash in case it was missing
                existing["sha256"] = file_hash
                existing["local_file"] = str(local_file)
                existing["status"] = "downloaded"

                changes.append({
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": file_hash
                })

                continue

            # -----------------------------------------------
            # Local file missing
            # -----------------------------------------------

            print("Local ZIP is missing.")
            print("Downloading again...")

            try:

                download_file(
                    zip_url,
                    local_file
                )

                file_hash = calculate_sha256(local_file)

                existing["release_url"] = release_url
                existing["file_url"] = zip_url
                existing["local_file"] = str(local_file)
                existing["sha256"] = file_hash
                existing["status"] = "downloaded"

                changes.append({
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": file_hash
                })

            except Exception as e:

                print(f"ERROR downloading {release_name}: {e}")

                existing["status"] = "download_failed"
                existing["processed"] = False
                existing["error"] = str(e)

            continue

        # ====================================================
        # CASE 3: PROCESSED RELEASE
        # ====================================================

        print("Release already processed.")

        # -----------------------------------------------
        # Local file missing
        # -----------------------------------------------

        if not local_file.exists():

            print("Local ZIP is missing.")
            print("Action: DOWNLOAD AND PROCESS.")

            try:

                download_file(
                    zip_url,
                    local_file
                )

                file_hash = calculate_sha256(local_file)

                existing["release_url"] = release_url
                existing["file_url"] = zip_url
                existing["local_file"] = str(local_file)
                existing["sha256"] = file_hash
                existing["processed"] = False
                existing["status"] = "downloaded"

                changes.append({
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": file_hash
                })

                print("STATUS: FILE REDOWNLOADED")
                print("Action: PROCESS")

            except Exception as e:

                print(f"ERROR downloading {release_name}: {e}")

                existing["status"] = "download_failed"
                existing["error"] = str(e)

            continue

        # -----------------------------------------------
        # Compare SHA-256
        # -----------------------------------------------

        print("Calculating SHA-256...")

        current_hash = calculate_sha256(local_file)

        previous_hash = existing.get("sha256")

        print(f"Previous SHA-256: {previous_hash}")
        print(f"Current SHA-256:  {current_hash}")

        # ====================================================
        # CASE 3A: SAME FILE
        # ====================================================

        if previous_hash == current_hash:

            print("STATUS: NO CHANGE")
            print("File is identical to the processed version.")

            existing["release_url"] = release_url
            existing["file_url"] = zip_url
            existing["local_file"] = str(local_file)

        # ====================================================
        # CASE 3B: FILE CHANGED
        # ====================================================

        else:

            print("STATUS: CHANGE DETECTED")
            print("SHA-256 hash is different.")
            print("Action: REPROCESS.")

            try:

                download_file(
                    zip_url,
                    local_file
                )

                new_hash = calculate_sha256(local_file)

                existing["release_url"] = release_url
                existing["file_url"] = zip_url
                existing["local_file"] = str(local_file)
                existing["sha256"] = new_hash
                existing["processed"] = False
                existing["status"] = "changed"
                existing["detected_at"] = datetime.now().isoformat()

                changes.append({
                    "release": release_name,
                    "release_url": release_url,
                    "file_url": zip_url,
                    "local_file": str(local_file),
                    "sha256": new_hash
                })

            except Exception as e:

                print(f"ERROR downloading changed release: {e}")

                existing["status"] = "download_failed"
                existing["processed"] = False
                existing["error"] = str(e)

    # ========================================================
    # SAVE MANIFEST
    # ========================================================

    save_manifest(manifest)

    print()
    print("=" * 60)

    if changes:

        print(
            f"Releases requiring processing: {len(changes)}"
        )

        for item in changes:
            print(f"  - {item['release']}")

    else:

        print("No new, changed, or unprocessed releases found.")
        print("Database is already up to date.")

    print("=" * 60)

    return changes


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    changes = detect_changes()

    print()
    print("CHANGE DETECTION COMPLETED.")
    print(f"Releases requiring processing: {len(changes)}")