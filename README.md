# CMS Healthcare Pricing Automated Data Pipeline

## Project Overview

The **CMS Healthcare Pricing Automated Data Pipeline** is a Python-based end-to-end ETL and data automation project for collecting, processing, validating, storing, and analyzing healthcare pricing data published by the **Centers for Medicare & Medicaid Services (CMS)**.

The project automates multiple CMS pricing datasets:

* Clinical Laboratory Fee Schedule (CLFS)
* Physician Fee Schedule
* Anesthesia Conversion Factors
* Durable Medical Equipment (DME/DMEPOS)

The pipeline automatically detects new releases, downloads CMS packages, extracts the files, parses different file formats, transforms the data into structured tables, stores the results in SQLite, and performs SQL-based analysis.

---

# Project Objectives

The main objectives are:

1. Automate CMS file downloading.
2. Detect new quarterly releases and updated versions.
3. Track previously processed releases.
4. Detect changes in existing records.
5. Parse different CMS file formats automatically.
6. Clean and standardize healthcare pricing data.
7. Store data in structured SQLite tables.
8. Maintain separate table structures for different pricing datasets.
9. Perform SQL analysis and validation.
10. Execute the complete workflow using one pipeline command.

---

# Data Sources

The project processes the following CMS datasets:

| Dataset    | Purpose                                  |
| ---------- | ---------------------------------------- |
| CLFS       | Clinical Laboratory Fee Schedule pricing |
| Physician  | Physician Fee Schedule data              |
| Anesthesia | Anesthesia conversion factor data        |
| DME/DMEPOS | Durable Medical Equipment pricing        |

---

# Pipeline Architecture

```text
                         CMS Website
                              |
                              v
                    Release / Version Detection
                              |
                              v
                       Version Tracking
                              |
                +-------------+-------------+
                |                           |
           UNCHANGED                  NEW / UPDATED
                |                           |
                |                           v
                |                    Download Package
                |                           |
                +-------------+-------------+
                              |
                              v
                         File Extraction
                              |
                              v
                         File Parsing
                              |
              +---------------+---------------+
              |               |               |
             CLFS         Physician       Anesthesia
              |               |               |
              +---------------+---------------+
                              |
                              |
                              v
                             DME
                              |
             +----------------+----------------+
             |                |                |
        DMEPOS Pricing   State Pricing   CBA Pricing
             |                |                |
             +----------------+----------------+
                              |
                              v
                       Data Transformation
                              |
                              v
                         SQLite Database
                              |
                              v
                         SQL Analysis
```

---

# 1. CLFS Processing

The CLFS pipeline automatically:

* Checks CMS for available CLFS releases.
* Identifies year and quarter.
* Detects file versions such as `25CLABQ3V2`.
* Tracks previously processed versions.
* Downloads ZIP packages.
* Extracts CSV files.
* Parses CLFS data.
* Cleans and standardizes columns.
* Detects record-level changes.
* Loads the data into SQLite.
* Performs SQL analysis.

### CLFS Version Detection

The version detector identifies:

```text
24CLABQ1
24CLABQ2
25CLABQ3V2
26CLABQ3
```

The release is interpreted as:

```text
Year + Quarter + Version
```

For example:

```text
25CLABQ3V2
```

means:

```text
Year    = 2025
Quarter = Q3
Version = V2
```

If the version is not explicitly present, the system treats it as the initial version.

---

# 2. Record-Level Change Detection

The project also detects changes between old and new records.

For CLFS, records are compared using:

```text
HCPCS
MOD
EFF_DATE
```

The system can identify:

```text
NEW RECORD
MODIFIED RECORD
REMOVED RECORD
```

This allows the pipeline to determine not only that a file changed, but also **which records changed**.

---

# 3. Physician Fee Schedule

The Physician Fee Schedule data is parsed and cleaned automatically.

The processed dataset contains:

* Procedure information
* Pricing information
* Status information
* File type
* Additional physician pricing attributes

The Physician data is combined with the Clinical dataset where required by the project design.

Current processed Physician dataset:

```text
Rows: 3,270
Columns: 18
```

---

# 4. Clinical + Physician Combined Dataset

Clinical Laboratory Fee Schedule and Physician Fee Schedule data are combined into a unified dataset.

Output:

```text
output/cms_all_combined.csv
```

Current combined dataset:

```text
Rows: 61,259
Columns: 25
```

---

# 5. Anesthesia Processing

The Anesthesia pipeline downloads and processes CMS anesthesia conversion factor files.

The process includes:

1. Downloading CMS files.
2. Extracting Excel workbooks.
3. Identifying the required workbook.
4. Parsing locality-adjusted conversion factors.
5. Cleaning the records.
6. Loading the data into SQLite.

Output:

```text
output/anesthesia_3year_clean.csv
```

Current processed data:

```text
Years: 2024–2026
Rows: 436
```

---

# 6. DME/DMEPOS Processing

The DME pipeline automates CMS Durable Medical Equipment pricing data.

The pipeline currently processes:

```text
DME24-A
DME24-B
DME24-C
DME24-D

DME25-A
DME25-B
DME25-C
DME25-D

DME26-A
DME26-B
DME26-C
```

This covers the available DME releases from **2024 through 2026 Q3**.

The DME downloader automatically:

* Finds available CMS DME releases.
* Identifies release names.
* Finds the corresponding ZIP package.
* Downloads new packages.
* Detects updated packages.
* Avoids downloading unchanged packages.
* Extracts the packages automatically.
* Maintains a DME release tracker.

---

# 7. DME Version / Update Detection

DME releases are tracked using:

```text
dme_version_tracker.json
```

The system stores information such as:

```text
Release
Year
Quarter
ZIP URL
SHA-256 hash
ETag
Last-Modified
Content-Length
Status
```

Before downloading a package, the system checks the remote CMS metadata and the locally stored information.

### If nothing changed

```text
[UNCHANGED]
```

The package is not downloaded again.

### If CMS publishes a new release

```text
[NEW]
```

The package is downloaded and processed.

### If CMS updates an existing package

```text
[UPDATED]
```

The new package is downloaded, extracted, and processed again.

This prevents unnecessary downloads while still detecting CMS updates.

---

# 8. DME Main Pricing Data

The main DMEPOS files contain information such as:

```text
HCPCS
MOD
MOD2
JURIS
CATG
Ceiling
Floor
State Pricing
```

The DME parser automatically detects the header row and converts the CMS file into structured records.

Current DME main dataset:

```text
Files processed: 11
Rows: 38,437
Columns: 118
```

Output:

```text
output/dme_combined.csv
```

---

# 9. DME State-Level Pricing

DME files contain state-specific pricing columns.

Examples include:

```text
AL (NR)
AL (R)
AK (NR)
AK (R)
...
```

The state pricing loader automatically detects these columns and converts the wide CMS structure into a normalized database table.

Table:

```text
dme_state_pricing
```

Current records:

```text
4,074,322
```

This represents:

```text
38,437 DME records × 106 state pricing columns
= 4,074,322 records
```

The table stores:

```text
HCPCS
MOD
MOD2
STATE
PRICING_TYPE
ALLOWANCE
FEE_YEAR
QUARTER
RELEASE
SOURCE_FILE
```

---

# 10. DMEPEN State Pricing

The project also processes DMEPEN files containing state-level pricing.

Table:

```text
dme_pen_state_pricing
```

Current records:

```text
26,394
```

The same automated state-column detection approach is used.

---

# 11. Former CBA Pricing

Former Competitive Bidding Area pricing is processed separately.

The loader automatically:

* Identifies Former CBA pricing files.
* Detects the pricing columns.
* Extracts CBA names.
* Converts the wide structure into normalized records.
* Loads the records into SQLite.

Table:

```text
dme_former_cba_pricing
```

Current records:

```text
880,360
```

---

# 12. DME Additional Data

The DME process also handles:

### DMEPEN

```text
dme_pen_schedule
```

### Rural ZIP Codes

```text
dme_rural_zip
```

### Former CBA Fee Schedule

```text
dme_former_cba_fee
```

### Former CBA ZIP Codes

```text
dme_former_cba_zip
```

### National Mail Order DTS

```text
dme_mail_order_dts
```

---

# 13. SQLite Database

The project uses SQLite for structured storage.

Database:

```text
cms_clfs.db
```

### Main tables

```text
clfs_data
anesthesia_data

dme_fee_schedule
dme_pen_schedule
dme_rural_zip
dme_former_cba_fee
dme_former_cba_zip
dme_mail_order_dts

dme_state_pricing
dme_pen_state_pricing
dme_former_cba_pricing
```

The Clinical and Physician data are also represented through the combined processing workflow.

---

# 14. SQL Analysis

The project contains SQL queries for validating and analyzing the processed datasets.

### CLFS analysis includes

* Records by year
* Average rates
* Highest rates
* Lowest rates
* Top HCPCS codes
* Source file distribution
* Indicator distribution

### DME analysis includes

* Total DMEPOS records
* Records by year
* Records by quarter
* Unique HCPCS codes
* Records by release
* Highest ceiling prices
* Lowest floor prices
* State pricing totals
* Rural vs non-rural pricing
* State distribution
* DMEPEN summary
* Former CBA summary
* Rural ZIP summary
* Former CBA ZIP summary
* Mail-order DTS summary

---

# 15. Complete Automated Pipeline

The complete project can be executed using:

```bash
python run_pipeline.py
```

The pipeline executes:

```text
1. download_files.py
2. etl_pipeline.py
3. physician_parser.py
4. combine_datasets.py
5. database.py

6. anesthesia_downloader.py
7. anesthesia_parser.py
8. anesthesia_database.py

9. dme_downloader.py
10. dme_parser.py
11. dme_database.py
12. dme_loader.py
13. dme_state_loader.py
14. dme_pen_state_loader.py
15. former_cba_pricing_loader.py

16. sql_queries.py
```

---

# 16. Current Pipeline Validation

The complete pipeline has been successfully executed.

The latest run completed with:

```text
COMPLETE CMS PIPELINE FINISHED SUCCESSFULLY
```

DME processing results:

```text
DMEPOS                 38,437
DME State Pricing   4,074,322
DMEPEN State Pricing   26,394
Former CBA Pricing    880,360
Rural ZIP             175,145
Former CBA ZIP        177,364
Mail Order DTS             121
```

DME releases processed:

```text
11
```

```text
DME24-A
DME24-B
DME24-C
DME24-D
DME25-A
DME25-B
DME25-C
DME25-D
DME26-A
DME26-B
DME26-C
```

The DME downloader also confirmed that all currently tracked packages were unchanged during the latest run:

```text
New packages:       0
Updated packages:   0
Unchanged packages: 11
```

---

# 17. Project Structure

Important Python modules include:

```text
CMS_CLFS_Automated_Project 2/
│
├── download_files.py
├── etl_pipeline.py
├── version_detector.py
├── change_detector.py
├── update_manager.py
│
├── physician_parser.py
├── combine_datasets.py
│
├── anesthesia_downloader.py
├── anesthesia_parser.py
├── anesthesia_database.py
│
├── dme_downloader.py
├── dme_parser.py
├── dme_database.py
├── dme_loader.py
├── dme_state_loader.py
├── dme_pen_state_loader.py
├── former_cba_pricing_loader.py
│
├── database.py
├── sql_queries.py
├── run_pipeline.py
│
├── version_tracker.json
├── dme_version_tracker.json
├── cms_clfs.db
│
├── output/
└── downloads/
```

---

# 18. Technologies Used

* Python
* Pandas
* Requests
* BeautifulSoup
* SQLite
* SQL
* Regular Expressions
* ZIP file processing
* SHA-256 hashing
* Excel/CSV processing
* Git/GitHub

---

# 19. Key Automation Logic

The most important part of the project is the **release detection and update logic**.

The system does not simply download files every time.

Instead, it:

```text
CMS Website
     ↓
Find available releases
     ↓
Identify release / quarter / version
     ↓
Find package URL
     ↓
Check stored tracker
     ↓
Compare metadata / hash
     ↓
       ┌───────────────┐
       │               │
   Unchanged       New/Updated
       │               │
       ↓               ↓
   Skip download   Download
                       ↓
                   Extract
                       ↓
                    Parse
                       ↓
                    Load DB
```

This allows the system to automatically handle future CMS releases without manually changing the code for every quarter.

---

# 20. Future Release Handling

When CMS publishes a future DME release such as:

```text
DME26-D
```

or a later quarterly release, the downloader searches the CMS page dynamically and identifies the release.

The system then:

1. Detects the new release.
2. Finds the ZIP package.
3. Downloads it.
4. Extracts it.
5. Identifies the DMEPOS files.
6. Parses the data.
7. Loads the database tables.
8. Runs SQL validation.

The same principle is used for detecting updated packages.

---

# 21. Outputs

The project generates:

```text
output/cms_clfs_combined.csv
output/cms_physician_combined.csv
output/cms_all_combined.csv
output/anesthesia_3year_clean.csv
output/dme_combined.csv
```

Database:

```text
cms_clfs.db
```

Trackers:

```text
version_tracker.json
dme_version_tracker.json
```

---

# 22. Running the Project

Open PowerShell in the project directory:

```powershell
cd "C:\Users\user\Desktop\CMS_CLFS_Automated_Project 2"
```

Run the complete pipeline:

```powershell
python run_pipeline.py
```

To run individual modules:

```powershell
python dme_downloader.py
python dme_parser.py
python dme_loader.py
python dme_state_loader.py
python dme_pen_state_loader.py
python former_cba_pricing_loader.py
python sql_queries.py
```

---

# 23. Data Quality Approach

The project performs several validation steps:

* Header detection
* Column normalization
* Duplicate checking
* Release filtering
* Version tracking
* File hash comparison
* Record-level change detection
* Row-count validation
* SQL aggregation checks
* Database loading validation

This ensures that CMS source files are transformed into reliable structured pricing data.

---

# 24. Summary

This project provides an automated CMS healthcare pricing data pipeline covering:

```text
CLFS
  +
Physician
  +
Anesthesia
  +
DME/DMEPOS
```

The pipeline automates the complete workflow:

```text
Download
   ↓
Detect Release
   ↓
Detect Version / Update
   ↓
Extract
   ↓
Parse
   ↓
Clean
   ↓
Transform
   ↓
Validate
   ↓
Load into SQLite
   ↓
SQL Analysis
```

The main goal is to minimize manual processing and make the system capable of handling new CMS releases and updated files through automated detection and processing.
