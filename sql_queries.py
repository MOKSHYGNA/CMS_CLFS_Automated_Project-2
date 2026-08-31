import sqlite3


DATABASE_FILE = "cms_clfs.db"
TABLE_NAME = "clfs_data"


def main():

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    print()
    print("=" * 60)
    print("CMS CLFS SQL ANALYSIS")
    print("=" * 60)

    # --------------------------------------------------
    # QUERY 1 - TOTAL RECORDS
    # --------------------------------------------------

    print("\n1. TOTAL RECORDS")

    cursor.execute(
        f"SELECT COUNT(*) FROM {TABLE_NAME}"
    )

    total = cursor.fetchone()[0]

    print(f"Total records: {total}")

    # --------------------------------------------------
    # QUERY 2 - RECORDS BY YEAR
    # --------------------------------------------------

    print("\n2. RECORDS BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            COUNT(*) AS RECORD_COUNT
        FROM {TABLE_NAME}
        GROUP BY YEAR
        ORDER BY YEAR
        """
    )

    for year, count in cursor.fetchall():

        print(
            f"Year: {year} | Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 3 - RECORDS BY DATA TYPE
    # --------------------------------------------------

    print("\n3. RECORDS BY DATA TYPE")

    cursor.execute(
        f"""
        SELECT
            DATA_TYPE,
            COUNT(*) AS RECORD_COUNT
        FROM {TABLE_NAME}
        GROUP BY DATA_TYPE
        ORDER BY RECORD_COUNT DESC
        """
    )

    for data_type, count in cursor.fetchall():

        print(
            f"Data Type: {data_type} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 4 - UNIQUE HCPCS CODES
    # --------------------------------------------------

    print("\n4. UNIQUE HCPCS CODES")

    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT HCPCS)
        FROM {TABLE_NAME}
        WHERE HCPCS IS NOT NULL
        """
    )

    unique_hcpcs = cursor.fetchone()[0]

    print(
        f"Unique HCPCS codes: {unique_hcpcs}"
    )

    # --------------------------------------------------
    # QUERY 5 - AVERAGE CLINICAL RATE BY YEAR
    # --------------------------------------------------

    print("\n5. AVERAGE CLINICAL RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(AVG(RATE), 2) AS AVERAGE_RATE
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'CLINICAL'
          AND RATE IS NOT NULL
        GROUP BY YEAR
        ORDER BY YEAR
        """
    )

    for year, average_rate in cursor.fetchall():

        print(
            f"Year: {year} | "
            f"Average Clinical Rate: {average_rate}"
        )

    # --------------------------------------------------
    # QUERY 6 - AVERAGE PHYSICIAN RATES
    # --------------------------------------------------

    print("\n6. AVERAGE PHYSICIAN RATES")

    cursor.execute(
        f"""
        SELECT
            ROUND(AVG(CAST(NON_FACILITY_RATE AS REAL)), 2),
            ROUND(AVG(CAST(FACILITY_RATE AS REAL)), 2)
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'PHYSICIAN'
        """
    )

    non_facility, facility = cursor.fetchone()

    print(
        f"Average Non-Facility Rate: {non_facility}"
    )

    print(
        f"Average Facility Rate: {facility}"
    )

    # --------------------------------------------------
    # QUERY 7 - TOP 10 HIGHEST UNIQUE HCPCS RATES
    # --------------------------------------------------

    print("\n7. TOP 10 HIGHEST UNIQUE HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            MAX(RATE) AS MAX_RATE,
            MAX(SHORTDESC) AS DESCRIPTION
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'CLINICAL'
          AND RATE IS NOT NULL
        GROUP BY HCPCS
        ORDER BY MAX_RATE DESC
        LIMIT 10
        """
    )

    for hcpcs, rate, description in cursor.fetchall():

        print(
            f"HCPCS: {hcpcs} | "
            f"Rate: {rate} | "
            f"Description: {description}"
        )

    # --------------------------------------------------
    # QUERY 8 - LOWEST UNIQUE HCPCS RATES
    # --------------------------------------------------

    print("\n8. 10 LOWEST UNIQUE HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            MIN(RATE) AS MIN_RATE,
            MIN(SHORTDESC) AS DESCRIPTION
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'CLINICAL'
          AND RATE IS NOT NULL
        GROUP BY HCPCS
        ORDER BY MIN_RATE ASC
        LIMIT 10
        """
    )

    for hcpcs, rate, description in cursor.fetchall():

        print(
            f"HCPCS: {hcpcs} | "
            f"Rate: {rate} | "
            f"Description: {description}"
        )

    # --------------------------------------------------
    # QUERY 9 - RECORDS BY SOURCE FILE
    # --------------------------------------------------

    print("\n9. RECORDS BY SOURCE FILE")

    cursor.execute(
        f"""
        SELECT
            SOURCE_FILE,
            COUNT(*) AS RECORD_COUNT
        FROM {TABLE_NAME}
        GROUP BY SOURCE_FILE
        ORDER BY SOURCE_FILE
        """
    )

    for source, count in cursor.fetchall():

        print(
            f"{source} | Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 10 - HCPCS RATE HISTORY
    # --------------------------------------------------

    print("\n10. HCPCS RATE HISTORY")

    search_code = "0002M"

    print(
        f"Searching for HCPCS: {search_code}"
    )

    cursor.execute(
        f"""
        SELECT
            YEAR,
            HCPCS,
            EFF_DATE,
            RATE,
            SHORTDESC
        FROM {TABLE_NAME}
        WHERE HCPCS = ?
          AND DATA_TYPE = 'CLINICAL'
        GROUP BY
            YEAR,
            HCPCS,
            EFF_DATE,
            RATE,
            SHORTDESC
        ORDER BY YEAR
        """,
        (search_code,)
    )

    rows = cursor.fetchall()

    if rows:

        for row in rows:

            print(
                f"Year: {row[0]} | "
                f"HCPCS: {row[1]} | "
                f"Effective Date: {row[2]} | "
                f"Rate: {row[3]} | "
                f"Description: {row[4]}"
            )

    else:

        print(
            f"No records found for {search_code}"
        )

    # --------------------------------------------------
    # QUERY 11 - MOST FREQUENT HCPCS CODES
    # --------------------------------------------------

    print("\n11. MOST FREQUENT HCPCS CODES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            COUNT(*) AS RECORD_COUNT
        FROM {TABLE_NAME}
        WHERE HCPCS IS NOT NULL
        GROUP BY HCPCS
        ORDER BY RECORD_COUNT DESC
        LIMIT 10
        """
    )

    for hcpcs, count in cursor.fetchall():

        print(
            f"HCPCS: {hcpcs} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 12 - HCPCS AVAILABLE ACROSS ALL YEARS
    # --------------------------------------------------

    print("\n12. HCPCS AVAILABLE ACROSS ALL YEARS")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            COUNT(DISTINCT YEAR) AS YEAR_COUNT
        FROM {TABLE_NAME}
        WHERE DATA_TYPE = 'CLINICAL'
        GROUP BY HCPCS
        HAVING COUNT(DISTINCT YEAR) = 3
        ORDER BY HCPCS
        LIMIT 10
        """
    )

    for hcpcs, year_count in cursor.fetchall():

        print(
            f"HCPCS: {hcpcs} | "
            f"Years represented: {year_count}"
        )

    # --------------------------------------------------
    # QUERY 13 - NUMBER OF SOURCE FILES
    # --------------------------------------------------

    print("\n13. NUMBER OF SOURCE FILES")

    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT SOURCE_FILE)
        FROM {TABLE_NAME}
        """
    )

    source_count = cursor.fetchone()[0]

    print(
        f"Source files represented: {source_count}"
    )

    # --------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------

    connection.close()

    print()
    print("=" * 60)
    print("SQL ANALYSIS COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    main()