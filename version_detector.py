
import re
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path


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

VERSION_TRACKER_FILE = Path("version_tracker.json")


# ============================================================
# PARSE VERSION
# ============================================================

def parse_version(file_name):

    name = file_name.upper().strip()

    match = re.fullmatch(
        r"(\d{2})CLAB(Q[1-4])(V(\d+))?",
        name
    )

    if not match:
        return None

    year = match.group(1)
    quarter = match.group(2)

    version = (
        int(match.group(4))
        if match.group(4)
        else 1
    )

    return {
        "name": name,
        "year": year,
        "quarter": quarter,
        "version": version
    }


# ============================================================
# FIND LATEST VERSIONS
# ============================================================

def find_latest_versions(file_names):

    latest_versions = {}

    for file_name in file_names:

        parsed = parse_version(file_name)

        if parsed is None:
            continue

        key = (
            parsed["year"],
            parsed["quarter"]
        )

        if key not in latest_versions:

            latest_versions[key] = parsed

        elif (
            parsed["version"]
            >
            latest_versions[key]["version"]
        ):

            latest_versions[key] = parsed

    return latest_versions


# ============================================================
# LOAD VERSION TRACKER
# ============================================================

def load_version_tracker():

    if not VERSION_TRACKER_FILE.exists():
        return {}

    try:

        with open(
            VERSION_TRACKER_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"[WARNING] Could not load version tracker: {error}"
        )

        return {}


# ============================================================
# GET REAL CMS FILE NAMES
# ============================================================

def get_cms_files():

    print("\nConnecting to CMS website...")

    try:

        response = requests.get(
            CMS_URL,
            timeout=60
        )

        response.raise_for_status()

    except Exception as error:

        print(
            f"[ERROR] Could not connect to CMS: {error}"
        )

        return []


    print("Scanning CMS page for CLFS versions...")


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    cms_files = []


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

        quarter = match.group(2)


        if year not in SUPPORTED_YEARS:
            continue


        if quarter not in SUPPORTED_QUARTERS:
            continue


        cms_files.append(name)


    return cms_files


# ============================================================
# CREATE VERSION REPORT
# ============================================================

def create_version_report(
    cms_files,
    stored_versions
):

    latest_versions = find_latest_versions(
        cms_files
    )

    report = []


    for key, cms_file in latest_versions.items():

        year, quarter = key


        stored_version = stored_versions.get(
            f"{year}-{quarter}"
        )


        if stored_version is None:

            status = "NEW"


        elif cms_file["version"] > int(
            stored_version
        ):

            status = "NEW_VERSION"


        elif cms_file["version"] == int(
            stored_version
        ):

            status = "UNCHANGED"


        else:

            status = "OLDER_VERSION"


        report.append(
            {
                "year": year,
                "quarter": quarter,
                "cms_file": cms_file["name"],
                "cms_version": cms_file["version"],
                "stored_version": stored_version,
                "status": status
            }
        )


    return report


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("CMS CLFS VERSION DETECTOR")
    print("=" * 60)


    # --------------------------------------------------------
    # STEP 1: GET REAL CMS FILES
    # --------------------------------------------------------

    cms_files = get_cms_files()


    if not cms_files:

        print(
            "\n[ERROR] No CMS CLFS files found."
        )

        raise SystemExit(1)


    print(
        f"\n[INFO] CMS files detected: "
        f"{len(cms_files)}"
    )


    for file_name in cms_files:

        print(
            f"  [FOUND] {file_name}"
        )


    # --------------------------------------------------------
    # STEP 2: LOAD VERSION TRACKER
    # --------------------------------------------------------

    raw_tracker = load_version_tracker()


    print("\n[INFO] Current tracked versions:")


    for key, version in raw_tracker.items():

        print(
            f"  {key} -> V{version}"
        )


    # --------------------------------------------------------
    # STEP 3: CREATE VERSION REPORT
    # --------------------------------------------------------

    report = create_version_report(
        cms_files,
        raw_tracker
    )


    # --------------------------------------------------------
    # STEP 4: DISPLAY REPORT
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("VERSION REPORT")
    print("=" * 60)


    for item in report:

        stored = item["stored_version"]

        if stored is None:
            stored_text = "NONE"
        else:
            stored_text = f"V{stored}"


        print(
            f"{item['cms_file']} | "
            f"Stored: {stored_text} | "
            f"CMS: V{item['cms_version']} | "
            f"Status: {item['status']}"
        )


    print("\n")
    print("=" * 60)
    print("VERSION DETECTION COMPLETED")
    print("=" * 60)

