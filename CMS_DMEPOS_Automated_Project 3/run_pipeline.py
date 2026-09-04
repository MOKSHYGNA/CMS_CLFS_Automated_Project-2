import zipfile
import shutil
from pathlib import Path
from datetime import datetime

from change_detector import detect_changes, load_manifest, save_manifest

from dme_parser import parse_dme_file
from dme_transformer import transform_dme_file
from dme_database import load_dme_to_database

from dme_rural_zip_parser import parse_rural_zip
from dme_former_cba_fee_parser import parse_former_cba_fee
from dme_former_cba_zip_parser import parse_former_cba_zip
from dme_former_cba_mail_order_parser import parse_former_cba_mail_order

from zip_carrier_locality_downloader import (
    detect_zip_carrier_locality_change,
    load_manifest as load_zip_manifest,
    save_manifest as save_zip_manifest
)

from zip_carrier_locality_parser import parse_zip5
from dme_zip_database import load_zip_carrier_locality


DOWNLOAD_DIR = Path("downloads")
OUTPUT_DIR = Path("output")
DATABASE = OUTPUT_DIR / "cms_dmepos.db"

ZIP_CARRIER_OUTPUT = OUTPUT_DIR / "zip_carrier_locality.csv"


def extract_zip(zip_file, extract_directory):

    print()
    print("-" * 60)
    print("EXTRACTING ZIP FILE")
    print("-" * 60)

    zip_file = Path(zip_file)
    extract_directory = Path(extract_directory)

    if not zip_file.exists():
        raise FileNotFoundError(
            f"ZIP file not found: {zip_file}"
        )

    if extract_directory.exists():
        shutil.rmtree(extract_directory)

    extract_directory.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_directory)

    print(f"Extracted to: {extract_directory}")

    return extract_directory


def find_dme_csv(extract_directory):

    csv_files = list(Path(extract_directory).rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV file found in {extract_directory}"
        )

    for file in csv_files:
        if "DMEPOS" in file.name.upper():
            return file

    return csv_files[0]


def find_supporting_files(extract_directory):

    files = list(Path(extract_directory).rglob("*"))

    rural = None
    cba_fee = None
    cba_zip = None
    mail_order = None

    for file in files:

        if not file.is_file():
            continue

        name = file.name.lower()

        if "rural" in name and file.suffix.lower() == ".csv":
            rural = file

        elif "former cba fee" in name and file.suffix.lower() == ".csv":
            cba_fee = file

        elif "former cba zip" in name and file.suffix.lower() == ".csv":
            cba_zip = file

        elif "mail-order" in name and file.suffix.lower() == ".csv":
            mail_order = file

    return rural, cba_fee, cba_zip, mail_order


def process_supporting_files(extract_directory, release):

    print()
    print("=" * 60)
    print(f"PROCESSING SUPPORTING FILES - {release}")
    print("=" * 60)

    release_output = OUTPUT_DIR / release
    release_output.mkdir(parents=True, exist_ok=True)

    rural, cba_fee, cba_zip, mail_order = find_supporting_files(
        extract_directory
    )

    if rural:
        try:
            parse_rural_zip(
                input_file=rural,
                output_file=release_output / "dme_rural_zip.csv"
            )
        except Exception as e:
            print(f"Rural ZIP parser failed: {e}")

    if cba_fee:
        try:
            parse_former_cba_fee(
                input_file=cba_fee,
                output_file=release_output / "former_cba_fee.csv"
            )
        except Exception as e:
            print(f"Former CBA fee parser failed: {e}")

    if cba_zip:
        try:
            parse_former_cba_zip(
                input_file=cba_zip,
                output_file=release_output / "former_cba_zip.csv"
            )
        except Exception as e:
            print(f"Former CBA ZIP parser failed: {e}")

    if mail_order:
        try:
            parse_former_cba_mail_order(
                input_file=mail_order,
                output_file=release_output / "former_cba_mail_order.csv"
            )
        except Exception as e:
            print(f"Former CBA mail-order parser failed: {e}")


def process_release(release):

    print()
    print("=" * 60)
    print(f"PROCESSING DME RELEASE: {release}")
    print("=" * 60)

    manifest = load_manifest()

    release_info = manifest.get("releases", {}).get(release)

    if not release_info:
        print(f"No manifest information found for {release}")
        return False

    zip_file = release_info.get("local_file")

    if not zip_file:
        print(f"No local ZIP file recorded for {release}")
        return False

    zip_file = Path(zip_file)

    extract_directory = DOWNLOAD_DIR / release / "extracted"

    try:

        extract_zip(
            zip_file,
            extract_directory
        )

        dme_csv = find_dme_csv(extract_directory)

        print()
        print(f"DME CSV found: {dme_csv}")

        cleaned_output = (
            OUTPUT_DIR /
            release /
            "dme_cleaned.csv"
        )

        transformed_output = (
            OUTPUT_DIR /
            release /
            "dme_normalized.csv"
        )

        cleaned_output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print()
        print("PARSING DMEPOS FILE...")

        parse_dme_file(
            input_csv=dme_csv,
            output_csv=cleaned_output
        )

        print()
        print("TRANSFORMING DMEPOS FILE...")

        transform_dme_file(
            input_csv=cleaned_output,
            output_csv=transformed_output
        )

        print()
        print("LOADING DMEPOS INTO DATABASE...")

        load_dme_to_database(
            input_csv=transformed_output,
            database_file=DATABASE
        )

        process_supporting_files(
            extract_directory,
            release
        )

        print()
        print(f"DME RELEASE {release} COMPLETED SUCCESSFULLY")

        return True

    except Exception as e:

        print()
        print(f"DME RELEASE {release} FAILED")
        print(f"Error: {e}")

        return False


def process_zip_carrier_locality():

    print()
    print("=" * 60)
    print("ZIP CODE TO CARRIER LOCALITY")
    print("=" * 60)

    try:

        result = detect_zip_carrier_locality_change()

        status = result.get("status")

        print(f"ZIP locality status: {status}")

        if status == "no_change":

            print("ZIP Carrier Locality file has not changed.")

            return True

        if status != "process":

            print("ZIP Carrier Locality does not require processing.")

            return True

        input_zip = result.get("local_file")
        sha256 = result.get("sha256")
        file_url = result.get("file_url")

        if not input_zip:

            raise FileNotFoundError(
                "ZIP Carrier Locality local file was not returned."
            )

        print()
        print("PARSING ZIP5 CARRIER LOCALITY FILE...")

        parse_zip5(
            input_zip=input_zip,
            output_csv=ZIP_CARRIER_OUTPUT
        )

        print()
        print("LOADING ZIP CARRIER LOCALITY INTO DATABASE...")

        load_zip_carrier_locality(
            input_file=ZIP_CARRIER_OUTPUT,
            database_file=DATABASE
        )

        zip_manifest = load_zip_manifest()

        zip_manifest["file_url"] = file_url
        zip_manifest["local_file"] = str(input_zip)
        zip_manifest["sha256"] = sha256
        zip_manifest["processed"] = True
        zip_manifest["status"] = "processed"
        zip_manifest["processed_at"] = datetime.now().isoformat()
        zip_manifest["output_csv"] = str(ZIP_CARRIER_OUTPUT)

        save_zip_manifest(zip_manifest)

        print()
        print("ZIP CARRIER LOCALITY COMPLETED SUCCESSFULLY")

        return True

    except Exception as e:

        print()
        print("ZIP CARRIER LOCALITY FAILED")
        print(f"Error: {e}")

        try:

            zip_manifest = load_zip_manifest()

            zip_manifest["processed"] = False
            zip_manifest["status"] = "failed"
            zip_manifest["error"] = str(e)
            zip_manifest["failed_at"] = datetime.now().isoformat()

            save_zip_manifest(zip_manifest)

        except Exception:
            pass

        return False


def main():

    print()
    print("=" * 60)
    print("CMS DMEPOS AUTOMATED PIPELINE")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    DATABASE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dme_failed = False

    try:

        print()
        print("CHECKING DMEPOS RELEASES...")

        changes = detect_changes()

        # detect_changes() returns a LIST of releases
        releases_to_process = changes

        if releases_to_process:

            print()
            print(
                f"Releases requiring processing: "
                f"{releases_to_process}"
            )

            for release in releases_to_process:

                success = process_release(release)

                manifest = load_manifest()

                if "releases" in manifest and release in manifest["releases"]:

                    if success:

                        manifest["releases"][release]["processed"] = True
                        manifest["releases"][release]["status"] = "processed"
                        manifest["releases"][release]["processed_at"] = (
                            datetime.now().isoformat()
                        )

                    else:

                        dme_failed = True

                        manifest["releases"][release]["processed"] = False
                        manifest["releases"][release]["status"] = "failed"
                        manifest["releases"][release]["failed_at"] = (
                            datetime.now().isoformat()
                        )

                    save_manifest(manifest)

                elif not success:

                    dme_failed = True

        else:

            print()
            print("No DMEPOS releases require processing.")

    except Exception as e:

        print()
        print("DMEPOS DETECTION FAILED")
        print(f"Error: {e}")

        dme_failed = True

    zip_success = process_zip_carrier_locality()

    print()
    print("=" * 60)
    print("PIPELINE FINISHED")
    print("=" * 60)

    if dme_failed:

        print("DMEPOS STATUS: FAILED")

    else:

        print("DMEPOS STATUS: SUCCESS")

    if zip_success:

        print("ZIP CARRIER LOCALITY STATUS: SUCCESS")

    else:

        print("ZIP CARRIER LOCALITY STATUS: FAILED")

    print()
    print(f"Database: {DATABASE}")
    print()


if __name__ == "__main__":
    main()