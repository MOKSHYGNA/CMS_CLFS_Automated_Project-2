
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
    # QUERY 3 - UNIQUE HCPCS CODES
    # --------------------------------------------------

    print("\n3. UNIQUE HCPCS CODES")

    cursor.execute(
        f"""
        SELECT COUNT(DISTINCT HCPCS)
        FROM {TABLE_NAME}
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
            ROUND(AVG(RATE), 2) AS AVERAGE_RATE
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        GROUP BY YEAR
        ORDER BY YEAR
        """
    )

    for year, average_rate in cursor.fetchall():

        print(
            f"Year: {year} | "
            f"Average Rate: {average_rate}"
        )

    # --------------------------------------------------
    # QUERY 5 - HIGHEST UNIQUE HCPCS RATES
    # --------------------------------------------------

    print("\n5. TOP 10 HIGHEST UNIQUE HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            MAX(RATE) AS MAX_RATE,
            MAX(SHORTDESC) AS DESCRIPTION
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
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
    # QUERY 6 - LOWEST UNIQUE HCPCS RATES
    # --------------------------------------------------

    print("\n6. 10 LOWEST UNIQUE HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            MIN(RATE) AS MIN_RATE,
            MIN(SHORTDESC) AS DESCRIPTION
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
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
    # QUERY 7 - RECORDS BY SOURCE FILE
    # --------------------------------------------------

    print("\n7. RECORDS BY SOURCE FILE")

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
    # QUERY 8 - HCPCS RATE HISTORY
    # --------------------------------------------------

    print("\n8. HCPCS RATE HISTORY")

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
        GROUP BY YEAR, HCPCS, EFF_DATE, RATE, SHORTDESC
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
    # QUERY 9 - NUMBER OF SOURCE FILES
    # --------------------------------------------------

    print("\n9. NUMBER OF SOURCE FILES")

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