# CMS DMEPOS Automated Pipeline

## Project Overview

This project automates the process of downloading, detecting changes, parsing, transforming, and loading **CMS DMEPOS (Durable Medical Equipment, Prosthetics, Orthotics, and Supplies) Fee Schedule** data into a database.

The pipeline also processes the **CMS ZIP Code to Carrier Locality** file, which maps ZIP codes to Medicare Carrier IDs and Fee Schedule IDs.

The main goal is to ensure that when CMS publishes a new or modified quarterly file, the system can automatically identify the change and process only the required data.

---

## Key Features

* Automatic detection of CMS DMEPOS quarterly releases
* Automatic download of CMS ZIP files
* SHA-256 based file change detection
* Prevention of duplicate processing
* DMEPOS CSV parsing and validation
* Transformation of state-level pricing data
* Rural ZIP Code processing
* Former CBA fee schedule processing
* Former CBA ZIP Code processing
* Former CBA National Mail-Order processing
* ZIP Code to Carrier Locality processing
* SQLite database loading
* Manifest-based processing history
* End-to-end automated pipeline

---

## Technologies Used

* **Python**
* **Pandas**
* **Requests**
* **BeautifulSoup**
* **SQLite**
* **SHA-256**
* **CSV**
* **ZIP files**
* **PowerShell**
* **Git / GitHub**

---

## Project Architecture

```text
CMS Website
     |
     v
Change Detection
     |
     +----------------------+
     |                      |
     v                      v
DMEPOS Releases       ZIP Carrier Locality
     |                      |
     v                      v
Download ZIP            Download ZIP
     |                      |
     v                      v
Extract Files           Parse ZIP5
     |                      |
     v                      v
Parse DMEPOS            Validate Data
     |
     v
Transform Data
     |
     v
Process Supporting Files
     |
     v
Load into SQLite Database
     |
     +----------------------+
                |
                v
        cms_dmepos.db
```

---

## Change Detection Logic

The project uses **SHA-256 hashing** to determine whether a CMS file has changed.

The process is:

1. Check the CMS website for available releases.
2. Identify current-year DMEPOS releases.
3. Download the required ZIP file.
4. Calculate the SHA-256 hash of the downloaded file.
5. Compare the current hash with the previously stored hash.
6. If the hash is unchanged, processing is skipped.
7. If the file is new or changed, the pipeline processes it.
8. After successful processing, the manifest is updated with the new hash.

This prevents unnecessary reprocessing of files that have already been processed.

---

## DMEPOS Processing

The main DMEPOS file is processed through the following stages:

### 1. Download

The system identifies the current CMS DMEPOS release and downloads the corresponding ZIP file.

### 2. Parse

The DMEPOS file is read and validated.

Important fields include:

* HCPCS
* Modifier
* Modifier 2
* Jurisdiction
* Category
* Ceiling
* Floor
* Description
* State-level pricing

### 3. Transform

The state pricing columns are converted from a wide format into a normalized structure.

For example:

```text
AL (NR)
AL (R)
AK (NR)
AK (R)
```

are transformed into separate fields such as:

```text
STATE
PRICE_TYPE
PRICE
```

### 4. Database Loading

The normalized DMEPOS records are loaded into the SQLite database.

---

## Supporting Files

The pipeline also processes supporting CMS files:

### DME Rural ZIP Code

Identifies rural ZIP codes used in DME pricing.

### Former CBA Fee Schedule

Processes former Competitive Bidding Area fee information.

### Former CBA ZIP Code

Maps ZIP codes to former CBA areas.

### Former CBA National Mail-Order

Processes national mail-order fee schedule information.

---

## ZIP Code to Carrier Locality

The pipeline separately monitors the CMS **ZIP Code to Carrier Locality** file.

The file is parsed from the ZIP5 fixed-width format.

Important fields include:

* State
* ZIP Code
* Medicare Carrier ID
* Medicare Fee Schedule ID
* Rural Indicator
* Beneficiary Laboratory CB Locality
* Year / Quarter

Example:

```text
ZIP Code: 99501
Carrier ID: 02102
Fee Schedule ID: 01
State: AK
```

The processed locality data is stored in the SQLite database.

---

## Database

The main database is:

```text
output/cms_dmepos.db
```

The database contains DMEPOS pricing information and ZIP Code to Carrier Locality mapping.

The pipeline verifies the loaded record counts after database insertion.

---

## Manifest Tracking

The project uses JSON manifests to maintain processing history.

The manifest stores information such as:

* Release
* File URL
* Local file
* SHA-256 hash
* Processing status
* Processing timestamp
* Output file

This allows the pipeline to determine whether a file is:

* New
* Changed
* Already processed
* Unchanged
* Failed

---

## Main Scripts

| Script                                | Purpose                                 |
| ------------------------------------- | --------------------------------------- |
| `run_pipeline.py`                     | Main end-to-end automation              |
| `change_detector.py`                  | Detects new/changed DMEPOS releases     |
| `download_dme_files.py`               | Downloads DMEPOS release ZIP files      |
| `dme_parser.py`                       | Parses and validates DMEPOS files       |
| `dme_transformer.py`                  | Normalizes state-level pricing          |
| `dme_database.py`                     | Loads DMEPOS data into SQLite           |
| `dme_rural_zip_parser.py`             | Processes rural ZIP data                |
| `dme_former_cba_fee_parser.py`        | Processes former CBA fee data           |
| `dme_former_cba_zip_parser.py`        | Processes former CBA ZIP data           |
| `dme_former_cba_mail_order_parser.py` | Processes former CBA mail-order data    |
| `zip_carrier_locality_downloader.py`  | Detects/downloads locality file changes |
| `zip_carrier_locality_parser.py`      | Parses ZIP5 carrier locality data       |
| `dme_zip_database.py`                 | Loads locality data into SQLite         |

---

## End-to-End Execution

Run the complete pipeline using:

```powershell
python run_pipeline.py
```

The pipeline checks both:

1. DMEPOS releases
2. ZIP Code to Carrier Locality file

If no changes are detected, previously processed files are skipped.

---

## Validation

The pipeline was successfully tested with the current CMS releases:

* DME26-A
* DME26-B
* DME26-C

The ZIP Code to Carrier Locality file was also successfully processed.

Final successful execution:

```text
============================================================
PIPELINE FINISHED
============================================================
DMEPOS STATUS: SUCCESS
ZIP CARRIER LOCALITY STATUS: SUCCESS

Database: output\cms_dmepos.db
```

The ZIP5 locality processing successfully loaded:

```text
42,957 records
55 unique Carrier IDs
47 unique Fee Schedule IDs
0 duplicate records
```

---

## Future Updates

When CMS publishes a new quarterly DMEPOS release, the pipeline can detect it automatically.

For example:

```text
New CMS Release
      |
      v
Download
      |
      v
Calculate SHA-256
      |
      v
Compare with Manifest
      |
      +---- Same ----> Skip Processing
      |
      +---- Different -> Process
                           |
                           v
                       Parse
                           |
                           v
                       Transform
                           |
                           v
                       Database
                           |
                           v
                       Update Manifest
```

This makes the project suitable for recurring quarterly CMS fee schedule updates.

---

## Project Outcome

The project provides an automated ETL workflow for CMS DMEPOS data:

**Extract → Detect Changes → Parse → Transform → Validate → Load → Track**

The system reduces manual processing and ensures that new CMS files can be detected and processed without reloading unchanged data.
