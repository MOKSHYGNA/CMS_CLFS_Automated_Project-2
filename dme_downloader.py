import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import zipfile
import re
import hashlib
import json


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = (
    "https://www.cms.gov/medicare/payment/fee-schedules/"
    "dmepos/dmepos-fee-schedule"
)

DOWNLOAD_DIR = Path("dme_downloads")
TRACKER_FILE = Path("dme_version_tracker.json")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0"
})


# ============================================================
# TRACKER
# ============================================================

def load_tracker():
    if not TRACKER_FILE.exists():
        return {}

    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print(f"[WARNING] Could not read tracker: {error}")
        return {}


def save_tracker(tracker):
    with open(TRACKER_FILE, "w", encoding="utf-8") as file:
        json.dump(tracker, file, indent=4)


# ============================================================
# SHA256
# ============================================================

def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# ============================================================
# FIND DME RELEASES
# ============================================================

def find_dme_release_pages():

    print("\nSearching CMS for DME releases...")

    response = SESSION.get(
        BASE_URL,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    releases = {}

    for link in soup.find_all("a", href=True):

        text = link.get_text(
            " ",
            strip=True
        ).upper()

        href = link["href"]

        # Only 2024, 2025 and 2026
        match = re.search(
            r"\bDME(24|25|26)[-_]?([A-D])\b",
            text
        )

        if not match:
            continue

        year = match.group(1)
        quarter = match.group(2)

        release_name = (
            f"DME{year}-{quarter}"
        )

        page_url = urljoin(
            BASE_URL,
            href
        )

        releases[release_name] = {
            "name": release_name,
            "year": year,
            "quarter": quarter,
            "url": page_url
        }

    releases = list(
        releases.values()
    )

    releases.sort(
        key=lambda item: (
            int(item["year"]),
            item["quarter"]
        )
    )

    print(
        f"Found {len(releases)} DME releases."
    )

    for release in releases:
        print(
            f"  - {release['name']}"
        )

    return releases


# ============================================================
# FIND ZIP
# ============================================================

def find_zip_url(page_url, release_name):

    response = SESSION.get(
        page_url,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link["href"]

        text = link.get_text(
            " ",
            strip=True
        ).upper()

        if (
            ".ZIP" in href.upper()
            or "ZIP" in text
        ):

            zip_url = urljoin(
                page_url,
                href
            )

            print(
                f"ZIP found for {release_name}:"
            )

            print(zip_url)

            return zip_url

    return None


# ============================================================
# CHECK REMOTE ZIP INFORMATION
# ============================================================

def get_remote_metadata(zip_url):

    try:

        response = SESSION.head(
            zip_url,
            timeout=30,
            allow_redirects=True
        )

        if response.status_code >= 400:
            return None

        headers = response.headers

        metadata = {
            "etag": headers.get("ETag"),
            "last_modified": headers.get(
                "Last-Modified"
            ),
            "content_length": headers.get(
                "Content-Length"
            )
        }

        # If CMS returned at least one useful
        # metadata value, return it.
        if any(metadata.values()):
            return metadata

    except Exception as error:

        print(
            "[WARNING] Remote metadata check failed:"
        )

        print(error)

    return None


# ============================================================
# DOWNLOAD ZIP
# ============================================================

def download_zip(
    zip_url,
    release_name,
    tracker
):

    year = release_name[3:5]
    quarter = release_name[-1]

    quarter_number = (
        ord(quarter)
        - ord("A")
        + 1
    )

    release_dir = (
        DOWNLOAD_DIR
        / f"20{year}"
        / f"Q{quarter_number}"
        / release_name
    )

    release_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    zip_path = (
        release_dir
        / f"{release_name}.zip"
    )

    previous_info = tracker.get(
        release_name,
        {}
    )

    remote_metadata = get_remote_metadata(
        zip_url
    )

    # ========================================================
    # EXISTING LOCAL FILE
    # ========================================================

    if zip_path.exists():

        current_hash = calculate_file_hash(
            zip_path
        )

        previous_hash = previous_info.get(
            "sha256"
        )

        previous_metadata = {
            "etag": previous_info.get("etag"),
            "last_modified": previous_info.get(
                "last_modified"
            ),
            "content_length": previous_info.get(
                "content_length"
            )
        }

        # ----------------------------------------------------
        # CASE 1:
        # Remote metadata is available and matches
        # ----------------------------------------------------

        if remote_metadata:

            metadata_match = (
                remote_metadata == previous_metadata
            )

            if (
                metadata_match
                and previous_hash == current_hash
            ):

                print(
                    f"[UNCHANGED] "
                    f"{release_name}"
                )

                return zip_path, False

            # If metadata changed, CMS package may have
            # changed. Download it.
            if not metadata_match:

                print(
                    f"[UPDATED PACKAGE] "
                    f"{release_name}"
                )

            elif previous_hash != current_hash:

                print(
                    f"[LOCAL FILE CHANGED] "
                    f"{release_name}"
                )

        # ----------------------------------------------------
        # CASE 2:
        # No remote metadata available
        # ----------------------------------------------------

        else:

            if (
                previous_hash
                and previous_hash == current_hash
            ):

                print(
                    f"[UNCHANGED - LOCAL HASH] "
                    f"{release_name}"
                )

                return zip_path, False

            print(
                f"[CHECK REQUIRED] "
                f"{release_name}"
            )

    # ========================================================
    # NEW DOWNLOAD / UPDATED DOWNLOAD
    # ========================================================

    else:

        print()
        print(
            f"[NEW RELEASE] "
            f"{release_name}"
        )

    print(
        f"Downloading {release_name}..."
    )

    response = SESSION.get(
        zip_url,
        timeout=120,
        stream=True
    )

    response.raise_for_status()

    with open(
        zip_path,
        "wb"
    ) as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:
                file.write(chunk)

    print(
        f"Downloaded: {zip_path}"
    )

    # Calculate new SHA256
    file_hash = calculate_file_hash(
        zip_path
    )

    # Get metadata again after download
    if remote_metadata is None:

        remote_metadata = get_remote_metadata(
            zip_url
        )

    # Save everything in tracker
    tracker[release_name] = {

        "year": year,

        "quarter": f"Q{quarter_number}",

        "zip_url": zip_url,

        "sha256": file_hash,

        "etag": (
            remote_metadata.get("etag")
            if remote_metadata
            else None
        ),

        "last_modified": (
            remote_metadata.get(
                "last_modified"
            )
            if remote_metadata
            else None
        ),

        "content_length": (
            remote_metadata.get(
                "content_length"
            )
            if remote_metadata
            else None
        ),

        "status": "downloaded"
    }

    save_tracker(tracker)

    print(
        f"SHA256: {file_hash}"
    )

    return zip_path, True


# ============================================================
# EXTRACT ZIP
# ============================================================

def extract_zip(
    zip_path,
    force=False
):

    extract_dir = (
        zip_path.parent
        / "extracted"
    )

    # Existing extraction
    if (
        extract_dir.exists()
        and any(extract_dir.iterdir())
        and not force
    ):

        print(
            f"[UNCHANGED] Already extracted: "
            f"{zip_path.name}"
        )

        return extract_dir

    # Remove old extracted files when package updated
    if extract_dir.exists() and force:

        for item in extract_dir.iterdir():

            if item.is_file():

                item.unlink()

            elif item.is_dir():

                import shutil

                shutil.rmtree(item)

    extract_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        f"Extracting: "
        f"{zip_path.name}"
    )

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_file:

        zip_file.extractall(
            extract_dir
        )

    print(
        f"Extracted to: "
        f"{extract_dir}"
    )

    return extract_dir


# ============================================================
# MAIN DOWNLOAD PROCESS
# ============================================================

def download_dme_releases():

    DOWNLOAD_DIR.mkdir(
        exist_ok=True
    )

    tracker = load_tracker()

    releases = find_dme_release_pages()

    if not releases:

        print(
            "No DME releases found."
        )

        return

    new_count = 0
    unchanged_count = 0
    updated_count = 0

    for release in releases:

        print()
        print("=" * 60)

        print(
            f"Processing "
            f"{release['name']}"
        )

        print("=" * 60)

        zip_url = find_zip_url(
            release["url"],
            release["name"]
        )

        if not zip_url:

            print(
                f"[WARNING] No ZIP found for "
                f"{release['name']}"
            )

            continue

        was_downloaded = False

        # Remember whether this release existed
        # before checking.
        release_existed = (
            release["name"]
            in tracker
        )

        zip_path, downloaded = download_zip(
            zip_url,
            release["name"],
            tracker
        )

        if downloaded:

            if release_existed:

                updated_count += 1

            else:

                new_count += 1

            extract_zip(
                zip_path,
                force=True
            )

        else:

            unchanged_count += 1

            extract_zip(
                zip_path,
                force=False
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 60)
    print("DME DOWNLOAD SUMMARY")
    print("=" * 60)

    print(
        f"New packages:       {new_count}"
    )

    print(
        f"Updated packages:    {updated_count}"
    )

    print(
        f"Unchanged packages:  {unchanged_count}"
    )

    print(
        f"Tracker file:        {TRACKER_FILE}"
    )

    print("=" * 60)

    print(
        "\nDME download process completed."
    )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    download_dme_releases()