
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
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, count in cursor.fetchall():

        print(
            f"Year: {year} | Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 3 - UNIQUE HCPCS CODES
    # --------------------------------------------------

    print("\n3. UNIQUE HCPCS CODES")

    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT HCPCS)
        FROM {TABLE_NAME}
        WHERE HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
        """
    )

    unique_hcpcs = cursor.fetchone()[0]

    print(
        f"Unique HCPCS codes: {unique_hcpcs}"
    )

    # --------------------------------------------------
    # QUERY 4 - AVERAGE RATE BY YEAR
    # --------------------------------------------------

    print("\n4. AVERAGE RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(
                AVG(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ) AS AVERAGE_RATE
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, average_rate in cursor.fetchall():

        print(
            f"Year: {year} | "
            f"Average Rate: {average_rate}"
        )

    # --------------------------------------------------
    # QUERY 5 - HIGHEST RATE BY YEAR
    # --------------------------------------------------

    print("\n5. HIGHEST RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(
                MAX(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ) AS MAX_RATE
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, max_rate in cursor.fetchall():

        print(
            f"Year: {year} | "
            f"Highest Rate: {max_rate}"
        )

    # --------------------------------------------------
    # QUERY 6 - LOWEST RATE BY YEAR
    # --------------------------------------------------

    print("\n6. LOWEST RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(
                MIN(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ) AS MIN_RATE
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, min_rate in cursor.fetchall():

        print(
            f"Year: {year} | "
            f"Lowest Rate: {min_rate}"
        )

    # --------------------------------------------------
    # QUERY 7 - TOP 10 HIGHEST HCPCS RATES
    # --------------------------------------------------

    print("\n7. TOP 10 HIGHEST HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            ROUND(
                MAX(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ) AS MAX_RATE,
            MAX(SHORTDESC) AS DESCRIPTION
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        AND HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
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
    # QUERY 8 - 10 LOWEST HCPCS RATES
    # --------------------------------------------------

    print("\n8. 10 LOWEST HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            ROUND(
                MIN(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ) AS MIN_RATE,
            MIN(SHORTDESC) AS DESCRIPTION
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        AND HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
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
            CAST(NULLIF(TRIM(RATE), '') AS REAL) AS RATE,
            SHORTDESC
        FROM {TABLE_NAME}
        WHERE HCPCS = ?
        ORDER BY
            CAST(YEAR AS INTEGER),
            EFF_DATE
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
        AND TRIM(HCPCS) <> ''
        GROUP BY HCPCS
        ORDER BY RECORD_COUNT DESC, HCPCS
        LIMIT 10
        """
    )

    for hcpcs, count in cursor.fetchall():

        print(
            f"HCPCS: {hcpcs} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 12 - HCPCS AVAILABLE ACROSS ALL 9 YEARS
    # --------------------------------------------------

    print("\n12. HCPCS AVAILABLE ACROSS ALL YEARS")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            COUNT(DISTINCT YEAR) AS YEAR_COUNT
        FROM {TABLE_NAME}
        WHERE HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
        GROUP BY HCPCS
        HAVING COUNT(DISTINCT YEAR) = 9
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
        WHERE SOURCE_FILE IS NOT NULL
        AND TRIM(SOURCE_FILE) <> ''
        """
    )

    source_count = cursor.fetchone()[0]

    print(
        f"Source files represented: {source_count}"
    )

    # --------------------------------------------------
    # QUERY 14 - RECORDS BY INDICATOR
    # --------------------------------------------------

    print("\n14. RECORDS BY INDICATOR")

    cursor.execute(
        f"""
        SELECT
            COALESCE(INDICATOR, 'None') AS INDICATOR_VALUE,
            COUNT(*) AS RECORD_COUNT
        FROM {TABLE_NAME}
        GROUP BY INDICATOR
        ORDER BY RECORD_COUNT DESC
        """
    )

    for indicator, count in cursor.fetchall():

        print(
            f"Indicator: {indicator} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # QUERY 15 - OVERALL RATE SUMMARY
    # --------------------------------------------------

    print("\n15. OVERALL RATE SUMMARY")

    cursor.execute(
        f"""
        SELECT
            ROUND(
                MIN(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ),
            ROUND(
                MAX(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            ),
            ROUND(
                AVG(
                    CAST(NULLIF(TRIM(RATE), '') AS REAL)
                ),
                2
            )
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        """
    )

    minimum, maximum, average = cursor.fetchone()

    print(f"Minimum Rate: {minimum}")
    print(f"Maximum Rate: {maximum}")
    print(f"Average Rate: {average}")

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

