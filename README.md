@"
# CMS CLFS Automated Data Pipeline

## Project Overview

The **CMS CLFS Automated Data Pipeline** is a Python-based end-to-end ETL and data automation project for processing healthcare pricing data published by the **Centers for Medicare & Medicaid Services (CMS)**.

The pipeline automatically:

- Checks CMS for new or updated CLFS files
- Detects file versions
- Tracks previously processed versions
- Detects record-level changes
- Downloads and extracts CMS files
- Processes Clinical Laboratory Fee Schedule (CLFS) data
- Processes Physician Fee Schedule data
- Processes Anesthesia Conversion Factor data
- Cleans and standardizes the datasets
- Combines datasets into a unified dataset
- Stores the processed data in SQLite
- Performs SQL-based analysis
- Runs the complete workflow through a single pipeline

---

## Project Objective

The primary objective is to automate the collection, processing, validation, storage, and analysis of CMS healthcare pricing data.

The project reduces manual work by automatically identifying whether CMS has published a new file or version and processing the updated data through the ETL pipeline.

---

# Pipeline Architecture

```text
                    CMS Website
                         |
                         v
              Version Detection
                         |
                         v
              Version Tracker
                         |
              +----------+----------+
              |                     |
         UNCHANGED             NEW VERSION
              |                     |
              |                     v
              |              Download File
              |                     |
              +----------+----------+
                         |
                         v
                 Change Detection
                         |
              +----------+----------+
              |          |          |
            Added     Modified    Removed
              |          |          |
              +----------+----------+
                         |
                         v
                    ETL Process
                         |
          +--------------+--------------+
          |              |              |
        CLFS         Physician      Anesthesia
          |              |              |
          +--------------+--------------+
                         |
                         v
                 Dataset Combination
                         |
                         v
                  SQLite Database
                         |
                         v
                    SQL Analysis