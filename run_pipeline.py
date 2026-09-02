import subprocess
import sys


def run_script(script_name):

    print()
    print("=" * 60)
    print(f"RUNNING: {script_name}")
    print("=" * 60)

    try:

        result = subprocess.run(
            [sys.executable, script_name],
            check=False
        )

    except Exception as error:

        print()
        print(f"[ERROR] Could not start {script_name}")
        print(f"Reason: {error}")

        sys.exit(1)

    if result.returncode != 0:

        print()
        print(f"[ERROR] {script_name} failed.")
        print(f"[ERROR] Exit code: {result.returncode}")

        sys.exit(result.returncode)

    print()
    print(f"[OK] {script_name} completed successfully.")


def main():

    print()
    print("=" * 60)
    print("CMS CLFS + DME AUTOMATED PROJECT")
    print("=" * 60)

    print()
    print("Starting complete automated pipeline...")
    print()

    # --------------------------------------------------
    # STEP 1 - DOWNLOAD AND UPDATE CMS CLFS FILES
    # --------------------------------------------------

    run_script("download_files.py")

    # --------------------------------------------------
    # STEP 2 - PROCESS CLINICAL / CLFS DATA
    # --------------------------------------------------

    run_script("etl_pipeline.py")

    # --------------------------------------------------
    # STEP 3 - PROCESS PHYSICIAN DATA
    # --------------------------------------------------

    run_script("physician_parser.py")

    # --------------------------------------------------
    # STEP 4 - COMBINE CLINICAL + PHYSICIAN DATA
    # --------------------------------------------------

    run_script("combine_datasets.py")

    # --------------------------------------------------
    # STEP 5 - LOAD CLFS + PHYSICIAN DATA INTO DATABASE
    # --------------------------------------------------

    run_script("database.py")

    # --------------------------------------------------
    # STEP 6 - DOWNLOAD ANESTHESIA FILES
    # --------------------------------------------------

    run_script("anesthesia_downloader.py")

    # --------------------------------------------------
    # STEP 7 - PARSE ANESTHESIA DATA
    # --------------------------------------------------

    run_script("anesthesia_parser.py")

    # --------------------------------------------------
    # STEP 8 - LOAD ANESTHESIA DATA INTO DATABASE
    # --------------------------------------------------

    run_script("anesthesia_database.py")

    # --------------------------------------------------
    # STEP 9 - DOWNLOAD DME FILES
    # --------------------------------------------------

    run_script("dme_downloader.py")

    # --------------------------------------------------
    # STEP 10 - PARSE DMEPOS DATA
    # --------------------------------------------------

    run_script("dme_parser.py")

    # --------------------------------------------------
    # STEP 11 - CREATE DME DATABASE TABLES
    # --------------------------------------------------

    run_script("dme_database.py")

    # --------------------------------------------------
    # STEP 12 - LOAD MAIN DME DATA
    # --------------------------------------------------

    run_script("dme_loader.py")

    # --------------------------------------------------
    # STEP 13 - LOAD DME STATE PRICING
    # --------------------------------------------------

    run_script("dme_state_loader.py")

    # --------------------------------------------------
    # STEP 14 - LOAD DMEPEN STATE PRICING
    # --------------------------------------------------

    run_script("dme_pen_state_loader.py")

    # --------------------------------------------------
    # STEP 15 - LOAD FORMER CBA PRICING
    # --------------------------------------------------

    run_script("former_cba_pricing_loader.py")

    # --------------------------------------------------
    # STEP 16 - RUN SQL ANALYSIS
    # --------------------------------------------------

    run_script("sql_queries.py")

    # --------------------------------------------------
    # PIPELINE COMPLETED
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("COMPLETE CMS PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 60)

    print()
    print("Generated outputs:")

    print("  - output/cms_clfs_combined.csv")
    print("  - output/cms_physician_combined.csv")
    print("  - output/cms_all_combined.csv")
    print("  - output/anesthesia_3year_clean.csv")
    print("  - output/dme_combined.csv")
    print("  - cms_clfs.db")

    print()
    print("Database tables:")

    print("  - clfs_data")
    print("  - anesthesia_data")
    print("  - dme_fee_schedule")
    print("  - dme_pen_schedule")
    print("  - dme_rural_zip")
    print("  - dme_former_cba_fee")
    print("  - dme_former_cba_zip")
    print("  - dme_mail_order_dts")
    print("  - dme_state_pricing")
    print("  - dme_pen_state_pricing")
    print("  - dme_former_cba_pricing")

    print()
    print("All pipeline stages completed successfully.")


if __name__ == "__main__":
    main()