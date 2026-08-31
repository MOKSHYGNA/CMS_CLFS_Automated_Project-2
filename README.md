# CMS CLFS Automated Data Pipeline

## Project Overview

The **CMS CLFS Automated Data Pipeline** is a Python-based data engineering project that automatically downloads CMS (Centers for Medicare & Medicaid Services) healthcare pricing data, processes and cleans the data, combines Clinical Laboratory Fee Schedule (CLFS) data with Physician Fee Schedule data, stores the final dataset in a SQLite database, and performs SQL-based analysis.

The project is designed as an automated end-to-end ETL pipeline.

---

## Project Objective

The main objectives of this project are:

- Automatically download CMS data files.
- Extract and process Clinical Laboratory Fee Schedule (CLFS) data.
- Process Physician Fee Schedule data.
- Clean and standardize the datasets.
- Combine Clinical and Physician datasets into one unified dataset.
- Store the combined data in a SQLite database.
- Perform SQL analysis on the processed data.
- Generate useful statistics such as record counts, average rates, HCPCS rate history, and highest/lowest rates.
- Automate the complete workflow using a single Python script.

---

# Technologies Used

- **Python**
- **Pandas**
- **SQLite**
- **SQL**
- **Requests**
- **BeautifulSoup**
- **Pathlib**
- **Subprocess**
- **CMS public data files**
- **CSV**
- **ZIP files**

---

# Project Structure

```text
CMS_CLFS_Automated_Project 2/
│
├── download_files.py
├── etl_pipeline.py
├── physician_parser.py
├── combine_datasets.py
├── database.py
├── sql_queries.py
├── run_pipeline.py
│
├── cms_clfs.db
│
├── downloads/
│   ├── 2024/
│   ├── 2025/
│   └── 2026/
│
└── output/
    ├── cms_clfs_combined.csv
    ├── cms_physician_combined.csv
    └── cms_all_combined.csv