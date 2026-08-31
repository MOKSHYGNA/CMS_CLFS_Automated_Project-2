import csv
from pathlib import Path


# ============================================================
# CMS CSV CHANGE DETECTOR
# ============================================================

def find_header_row(csv_file):
    """
    Find the actual header row in a CMS CSV file.

    CMS files can contain information rows before
    the actual column header.
    """

    with open(
        csv_file,
        "r",
        encoding="utf-8-sig",
        errors="ignore",
        newline=""
    ) as file:

        reader = csv.reader(file)

        for index, row in enumerate(reader):

            if not row:
                continue

            cleaned = [
                str(value).strip().upper()
                for value in row
            ]

            # CMS CLFS files normally contain HCPCS
            # as one of the column names.
            if "HCPCS" in cleaned:

                return index

    return 0


# ============================================================
# READ CMS CSV
# ============================================================

def read_csv_data(csv_file):
    """
    Read a CMS CSV file and return:

        headers
        records

    Metadata rows before the header are ignored.
    """

    csv_file = Path(csv_file)

    header_row = find_header_row(
        csv_file
    )

    rows = []

    with open(
        csv_file,
        "r",
        encoding="utf-8-sig",
        errors="ignore",
        newline=""
    ) as file:

        reader = csv.reader(file)

        for _ in range(header_row):
            next(reader, None)

        headers = next(
            reader,
            []
        )

        headers = [
            str(header).strip()
            for header in headers
        ]

        for row in reader:

            if not row:
                continue

            # Ignore completely empty rows
            if not any(
                str(value).strip()
                for value in row
            ):
                continue

            # Make row length equal to header length
            if len(row) < len(headers):

                row = row + (
                    [""] *
                    (len(headers) - len(row))
                )

            elif len(row) > len(headers):

                row = row[:len(headers)]

            record = {}

            for index, header in enumerate(
                headers
            ):

                record[header] = (
                    str(row[index]).strip()
                )

            rows.append(record)

    return headers, rows


# ============================================================
# NORMALIZE VALUE
# ============================================================

def normalize_value(value):
    """
    Normalize values before comparison.

    This prevents insignificant formatting
    differences from being treated as changes.
    """

    if value is None:
        return ""

    value = str(value).strip()

    return value


# ============================================================
# CREATE RECORD KEY
# ============================================================

def create_record_key(record, headers):
    """
    Create a stable identifier for a CMS CLFS record.

    HCPCS + MOD + EFF_DATE identifies a clinical
    laboratory fee schedule record.

    If those fields are unavailable, all fields
    are used as a fallback.
    """

    hcpcs = normalize_value(
        record.get("HCPCS", "")
    )

    mod = normalize_value(
        record.get("MOD", "")
    )

    eff_date = normalize_value(
        record.get("EFF_DATE", "")
    )

    # Primary CMS CLFS record identity
    if hcpcs:

        return (
            hcpcs,
            mod,
            eff_date
        )

    # Fallback if HCPCS is unavailable
    return tuple(
        normalize_value(
            record.get(header, "")
        )
        for header in headers
    )


# ============================================================
# CONVERT RECORD TO COMPARISON VALUE
# ============================================================

def record_values(record, headers):
    """
    Convert a record into a tuple containing
    all its values.

    This is used to determine whether an existing
    record was modified.
    """

    return tuple(
        normalize_value(
            record.get(header, "")
        )
        for header in headers
    )


# ============================================================
# COMPARE CSV FILES
# ============================================================

def compare_csv_files(old_csv, new_csv):
    """
    Compare an old CMS CSV with a new CMS CSV.

    Detects:

        1. New records
        2. Removed records
        3. Modified records

    Returns a dictionary used by download_files.py.
    """

    old_csv = Path(old_csv)
    new_csv = Path(new_csv)

    print(
        f"[INFO] Comparing:"
    )

    print(
        f"       OLD: {old_csv}"
    )

    print(
        f"       NEW: {new_csv}"
    )


    # ========================================================
    # CHECK FILES
    # ========================================================

    if not old_csv.exists():

        raise FileNotFoundError(
            f"Old CSV not found: {old_csv}"
        )

    if not new_csv.exists():

        raise FileNotFoundError(
            f"New CSV not found: {new_csv}"
        )


    # ========================================================
    # READ OLD FILE
    # ========================================================

    old_headers, old_records = (
        read_csv_data(old_csv)
    )


    # ========================================================
    # READ NEW FILE
    # ========================================================

    new_headers, new_records = (
        read_csv_data(new_csv)
    )


    print(
        f"[INFO] Old CSV records: "
        f"{len(old_records)}"
    )

    print(
        f"[INFO] New CSV records: "
        f"{len(new_records)}"
    )


    # ========================================================
    # CREATE OLD RECORD DICTIONARY
    # ========================================================

    old_record_dict = {}

    for record in old_records:

        key = create_record_key(
            record,
            old_headers
        )

        old_record_dict[key] = record


    # ========================================================
    # CREATE NEW RECORD DICTIONARY
    # ========================================================

    new_record_dict = {}

    for record in new_records:

        key = create_record_key(
            record,
            new_headers
        )

        new_record_dict[key] = record


    # ========================================================
    # FIND NEW RECORDS
    # ========================================================

    new_records_found = []

    for key, new_record in (
        new_record_dict.items()
    ):

        if key not in old_record_dict:

            new_records_found.append(
                new_record
            )


    # ========================================================
    # FIND REMOVED RECORDS
    # ========================================================

    removed_records = []

    for key, old_record in (
        old_record_dict.items()
    ):

        if key not in new_record_dict:

            removed_records.append(
                old_record
            )


    # ========================================================
    # FIND MODIFIED RECORDS
    # ========================================================

    modified_records = []

    # Only compare records that exist
    # in both versions.

    common_keys = (
        set(old_record_dict.keys())
        &
        set(new_record_dict.keys())
    )


    for key in common_keys:

        old_record = old_record_dict[key]

        new_record = new_record_dict[key]


        old_values = record_values(
            old_record,
            old_headers
        )


        new_values = record_values(
            new_record,
            new_headers
        )


        if old_values != new_values:

            modified_records.append(
                {
                    "key": key,
                    "old": old_record,
                    "new": new_record
                }
            )


    # ========================================================
    # PRINT SUMMARY
    # ========================================================

    print(
        "\n[CHANGE DETECTOR]"
    )

    print(
        f"Old records      : "
        f"{len(old_records)}"
    )

    print(
        f"New records      : "
        f"{len(new_records)}"
    )

    print(
        f"Newly added      : "
        f"{len(new_records_found)}"
    )

    print(
        f"Removed          : "
        f"{len(removed_records)}"
    )

    print(
        f"Modified         : "
        f"{len(modified_records)}"
    )


    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {

        "old_count":
            len(old_records),

        "new_count":
            len(new_records),

        "new_count_records":
            len(new_records_found),

        "removed_count":
            len(removed_records),

        "modified_count":
            len(modified_records),

        "new_records":
            new_records_found,

        "removed_records":
            removed_records,

        "modified_records":
            modified_records
    }