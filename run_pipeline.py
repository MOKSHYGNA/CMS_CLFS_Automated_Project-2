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
    print("CMS CLFS AUTOMATED PROJECT")
    print("=" * 60)

    print()
    print("Starting complete automated pipeline...")
    print()

    # --------------------------------------------------
    # STEP 1 - DOWNLOAD AND EXTRACT CMS FILES
    # --------------------------------------------------

    run_script("download_files.py")

    # --------------------------------------------------
    # STEP 2 - PROCESS CLINICAL DATA
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
    # STEP 5 - LOAD DATA INTO SQLITE DATABASE
    # --------------------------------------------------

    run_script("database.py")

    # --------------------------------------------------
    # STEP 6 - RUN SQL ANALYSIS
    # --------------------------------------------------

    run_script("sql_queries.py")

    # --------------------------------------------------
    # PIPELINE COMPLETED
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 60)

    print()
    print("Generated outputs:")
    print("  - output/cms_clfs_combined.csv")
    print("  - output/cms_physician_combined.csv")
    print("  - output/cms_all_combined.csv")
    print("  - cms_clfs.db")

    print()
    print("All pipeline stages completed successfully.")


if __name__ == "__main__":
    main()
