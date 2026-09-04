import zipfile
import shutil
from pathlib import Path

from zip_carrier_locality_parser import parse_zip5
from dme_zip_database import load_zip_carrier_locality

PROJECT_ROOT = Path(__file__).resolve().parent

ZIP_DIR = PROJECT_ROOT / "downloads" / "zip_carrier_locality"
EXTRACT_DIR = ZIP_DIR / "extracted"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_CSV = OUTPUT_DIR / "zip_carrier_locality.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ZIP_DIR.mkdir(parents=True, exist_ok=True)


def find_input_zip():
    zip_files = list(ZIP_DIR.glob("*.zip"))

    if not zip_files:
        raise FileNotFoundError(
            f"No ZIP file found in: {ZIP_DIR}"
        )

    return zip_files[0]


def extract_zip(zip_file):
    print()
    print("=" * 60)
    print("EXTRACTING ZIP CARRIER / LOCALITY FILE")
    print("=" * 60)

    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    print(f"ZIP file: {zip_file}")
    print(f"Extracted to: {EXTRACT_DIR}")

    print()
    print("Extracted files:")

    for file in EXTRACT_DIR.rglob("*"):
        if file.is_file():
            print(f"  - {file.name}")


def find_zip5_file():
    candidates = list(EXTRACT_DIR.rglob("ZIP5_OCT*.txt"))

    if not candidates:
        raise FileNotFoundError(
            "ZIP5_OCT*.txt was not found in the extracted ZIP."
        )

    selected_file = candidates[0]

    print()
    print(f"ZIP5 input file found: {selected_file}")

    return selected_file


def main():

    input_zip = find_input_zip()

    print()
    print(f"Input ZIP: {input_zip}")

    extract_zip(input_zip)

    input_file = find_zip5_file()

    print()
    print("=" * 60)
    print("PARSING ZIP CARRIER / LOCALITY FILE")
    print("=" * 60)

    parse_zip5(
        input_zip=input_zip,
        output_csv=OUTPUT_CSV
    )

    print()
    print("=" * 60)
    print("LOADING ZIP CARRIER / LOCALITY INTO DATABASE")
    print("=" * 60)

    load_zip_carrier_locality(
        input_file=OUTPUT_CSV
    )

    print()
    print("=" * 60)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(f"CSV: {OUTPUT_CSV}")
    print("Database: output/cms_dmepos.db")


if __name__ == "__main__":
    main()


