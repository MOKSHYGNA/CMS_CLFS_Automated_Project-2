
import subprocess
import sys


def run_script(script_name):

    print()
    print("=" * 60)
    print(f"RUNNING: {script_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_name]
    )

    if result.returncode != 0:

        print()
        print(f"[ERROR] {script_name} failed.")

        sys.exit(result.returncode)

    print()
    print(f"[OK] {script_name} completed successfully.")


def main():

    print()
    print("=" * 60)
    print("CMS CLFS AUTOMATED PROJECT")
    print("=" * 60)

    # Step 1 - Download and extract CMS files
    run_script("download_files.py")

    # Step 2 - Transform and combine CSV files
    run_script("etl_pipeline.py")

    # Step 3 - Load cleaned data into SQLite
    run_script("database.py")

    # Step 4 - Run SQL analysis
    run_script("sql_queries.py")

    print()
    print("=" * 60)
    print("COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 60)

    print()
    print("Generated outputs:")
    print("  - output/cms_clfs_combined.csv")
    print("  - cms_clfs.db")


if __name__ == "__main__":
    main()

