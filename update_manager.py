import subprocess
import sys
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPTS = {
    "download": "download_files.py",
    "etl": "etl_pipeline.py",
    "database": "database.py"
}


# ============================================================
# RUN PYTHON SCRIPT
# ============================================================

def run_script(script_name):

    print("\n")
    print("=" * 60)
    print(f"RUNNING: {script_name}")
    print("=" * 60)

    try:

        result = subprocess.run(
            [sys.executable, script_name],
            check=True
        )

        print(
            f"[OK] {script_name} completed successfully."
        )

        return True

    except subprocess.CalledProcessError as error:

        print(
            f"[ERROR] {script_name} failed."
        )

        print(
            f"[ERROR] Return code: {error.returncode}"
        )

        return False

    except Exception as error:

        print(
            f"[ERROR] Could not run {script_name}: {error}"
        )

        return False


# ============================================================
# MAIN UPDATE PROCESS
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("CMS CLFS AUTOMATIC UPDATE MANAGER")
    print("=" * 60)

    # ========================================================
    # STEP 1: CHECK CMS FILES
    # ========================================================

    print("\n[STEP 1] Checking CMS files and versions...")

    download_success = run_script(
        SCRIPTS["download"]
    )

    if not download_success:

        print(
            "\n[ERROR] CMS download/update process failed."
        )

        return

    # ========================================================
    # STEP 2: RUN ETL
    # ========================================================

    print("\n[STEP 2] Running ETL pipeline...")

    etl_success = run_script(
        SCRIPTS["etl"]
    )

    if not etl_success:

        print(
            "\n[ERROR] ETL pipeline failed."
        )

        return

    # ========================================================
    # STEP 3: LOAD DATABASE
    # ========================================================

    print("\n[STEP 3] Updating SQLite database...")

    database_success = run_script(
        SCRIPTS["database"]
    )

    if not database_success:

        print(
            "\n[ERROR] Database update failed."
        )

        return

    # ========================================================
    # FINISH
    # ========================================================

    print("\n")
    print("=" * 60)
    print("CMS CLFS AUTOMATIC UPDATE COMPLETED")
    print("=" * 60)

    print(
        "\n[OK] CMS files checked."
    )

    print(
        "[OK] Version and hash changes checked."
    )

    print(
        "[OK] ETL pipeline completed."
    )

    print(
        "[OK] SQLite database updated."
    )

    print(
        "\n[INFO] Final CSV:"
    )

    print(
        "       output/cms_clfs_combined.csv"
    )

    print(
        "\n[INFO] Database:"
    )

    print(
        "       cms_clfs.db"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()