# CMS CLFS Automated Project

## Overview

This project is an automated ETL pipeline for downloading, processing, storing, and analyzing CMS Clinical Laboratory Fee Schedule (CLFS) data.

The project automatically collects CLFS data for multiple quarters from 2024 to 2026, processes the downloaded CSV files, combines the data into a clean dataset, stores the data in a SQLite database, and performs SQL-based analysis.

## Project Workflow

The project follows this workflow:

CMS Website
    ↓
Download CLFS ZIP Files
    ↓
Extract CSV Files
    ↓
Clean and Combine Data
    ↓
Create Combined CSV Dataset
    ↓
Load Data into SQLite Database
    ↓
Run SQL Analysis

## Project Structure

```text
CMS_CLFS_Automated_Project 2/
│
├── download_files.py
├── etl_pipeline.py
├── database.py
├── sql_queries.py
├── run_pipeline.py
├── .gitignore
├── README.md
│
├── downloads/
│   ├── 2024/
│   ├── 2025/
│   └── 2026/
│
├── output/
│   └── cms_clfs_combined.csv
│
└── cms_clfs.db