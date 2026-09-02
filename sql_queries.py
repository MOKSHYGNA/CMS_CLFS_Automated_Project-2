import sqlite3


DATABASE_FILE = "cms_clfs.db"


def run_clfs_analysis(cursor):

    TABLE_NAME = "clfs_data"

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
        SELECT YEAR, COUNT(*) AS RECORD_COUNT
        FROM {TABLE_NAME}
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, count in cursor.fetchall():
        print(f"Year: {year} | Records: {count}")

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

    print(f"Unique HCPCS codes: {cursor.fetchone()[0]}")

    # --------------------------------------------------
    # QUERY 4 - AVERAGE RATE BY YEAR
    # --------------------------------------------------

    print("\n4. AVERAGE RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(
                AVG(CAST(NULLIF(TRIM(RATE), '') AS REAL)),
                2
            )
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, average_rate in cursor.fetchall():
        print(f"Year: {year} | Average Rate: {average_rate}")

    # --------------------------------------------------
    # QUERY 5 - HIGHEST RATE BY YEAR
    # --------------------------------------------------

    print("\n5. HIGHEST RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(
                MAX(CAST(NULLIF(TRIM(RATE), '') AS REAL)),
                2
            )
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, max_rate in cursor.fetchall():
        print(f"Year: {year} | Highest Rate: {max_rate}")

    # --------------------------------------------------
    # QUERY 6 - LOWEST RATE BY YEAR
    # --------------------------------------------------

    print("\n6. LOWEST RATE BY YEAR")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            ROUND(
                MIN(CAST(NULLIF(TRIM(RATE), '') AS REAL)),
                2
            )
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        GROUP BY YEAR
        ORDER BY CAST(YEAR AS INTEGER)
        """
    )

    for year, min_rate in cursor.fetchall():
        print(f"Year: {year} | Lowest Rate: {min_rate}")

    # --------------------------------------------------
    # QUERY 7 - TOP 10 HIGHEST HCPCS RATES
    # --------------------------------------------------

    print("\n7. TOP 10 HIGHEST HCPCS RATES")

    cursor.execute(
        f"""
        SELECT
            HCPCS,
            ROUND(
                MAX(CAST(NULLIF(TRIM(RATE), '') AS REAL)),
                2
            ),
            MAX(SHORTDESC)
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        AND HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
        GROUP BY HCPCS
        ORDER BY 2 DESC
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
                MIN(CAST(NULLIF(TRIM(RATE), '') AS REAL)),
                2
            ),
            MIN(SHORTDESC)
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        AND HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
        GROUP BY HCPCS
        ORDER BY 2 ASC
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
        SELECT SOURCE_FILE, COUNT(*)
        FROM {TABLE_NAME}
        GROUP BY SOURCE_FILE
        ORDER BY SOURCE_FILE
        """
    )

    for source, count in cursor.fetchall():
        print(f"{source} | Records: {count}")

    # --------------------------------------------------
    # QUERY 10 - HCPCS RATE HISTORY
    # --------------------------------------------------

    print("\n10. HCPCS RATE HISTORY")

    search_code = "0002M"

    print(f"Searching for HCPCS: {search_code}")

    cursor.execute(
        f"""
        SELECT
            YEAR,
            HCPCS,
            EFF_DATE,
            CAST(NULLIF(TRIM(RATE), '') AS REAL),
            SHORTDESC
        FROM {TABLE_NAME}
        WHERE HCPCS = ?
        ORDER BY CAST(YEAR AS INTEGER), EFF_DATE
        """,
        (search_code,)
    )

    for row in cursor.fetchall():
        print(
            f"Year: {row[0]} | "
            f"HCPCS: {row[1]} | "
            f"Effective Date: {row[2]} | "
            f"Rate: {row[3]} | "
            f"Description: {row[4]}"
        )

    # --------------------------------------------------
    # QUERY 11 - MOST FREQUENT HCPCS CODES
    # --------------------------------------------------

    print("\n11. MOST FREQUENT HCPCS CODES")

    cursor.execute(
        f"""
        SELECT HCPCS, COUNT(*)
        FROM {TABLE_NAME}
        WHERE HCPCS IS NOT NULL
        AND TRIM(HCPCS) <> ''
        GROUP BY HCPCS
        ORDER BY 2 DESC, HCPCS
        LIMIT 10
        """
    )

    for hcpcs, count in cursor.fetchall():
        print(f"HCPCS: {hcpcs} | Records: {count}")

    # --------------------------------------------------
    # QUERY 12 - HCPCS AVAILABLE ACROSS ALL 9 YEARS
    # --------------------------------------------------

    print("\n12. HCPCS AVAILABLE ACROSS ALL YEARS")

    cursor.execute(
        f"""
        SELECT HCPCS, COUNT(DISTINCT YEAR)
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
        print(f"HCPCS: {hcpcs} | Years represented: {year_count}")

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

    print(f"Source files represented: {cursor.fetchone()[0]}")

    # --------------------------------------------------
    # QUERY 14 - RECORDS BY INDICATOR
    # --------------------------------------------------

    print("\n14. RECORDS BY INDICATOR")

    cursor.execute(
        f"""
        SELECT
            COALESCE(INDICATOR, 'None'),
            COUNT(*)
        FROM {TABLE_NAME}
        GROUP BY INDICATOR
        ORDER BY 2 DESC
        """
    )

    for indicator, count in cursor.fetchall():
        print(f"Indicator: {indicator} | Records: {count}")

    # --------------------------------------------------
    # QUERY 15 - OVERALL RATE SUMMARY
    # --------------------------------------------------

    print("\n15. OVERALL RATE SUMMARY")

    cursor.execute(
        f"""
        SELECT
            ROUND(MIN(CAST(NULLIF(TRIM(RATE), '') AS REAL)), 2),
            ROUND(MAX(CAST(NULLIF(TRIM(RATE), '') AS REAL)), 2),
            ROUND(AVG(CAST(NULLIF(TRIM(RATE), '') AS REAL)), 2)
        FROM {TABLE_NAME}
        WHERE RATE IS NOT NULL
        AND TRIM(RATE) <> ''
        """
    )

    minimum, maximum, average = cursor.fetchone()

    print(f"Minimum Rate: {minimum}")
    print(f"Maximum Rate: {maximum}")
    print(f"Average Rate: {average}")


def run_dme_analysis(cursor):

    print()
    print("=" * 60)
    print("CMS DME SQL ANALYSIS")
    print("=" * 60)

    # --------------------------------------------------
    # DME QUERY 1 - MAIN DME RECORDS
    # --------------------------------------------------

    print("\n1. TOTAL DMEPOS RECORDS")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_fee_schedule
        """
    )

    print(f"Total DMEPOS records: {cursor.fetchone()[0]}")

    # --------------------------------------------------
    # DME QUERY 2 - RECORDS BY YEAR
    # --------------------------------------------------

    print("\n2. DMEPOS RECORDS BY YEAR")

    cursor.execute(
        """
        SELECT fee_year, COUNT(*)
        FROM dme_fee_schedule
        GROUP BY fee_year
        ORDER BY fee_year
        """
    )

    for year, count in cursor.fetchall():
        print(f"Year: {year} | Records: {count}")

    # --------------------------------------------------
    # DME QUERY 3 - RECORDS BY QUARTER
    # --------------------------------------------------

    print("\n3. DMEPOS RECORDS BY QUARTER")

    cursor.execute(
        """
        SELECT
            fee_year,
            quarter,
            COUNT(*)
        FROM dme_fee_schedule
        GROUP BY fee_year, quarter
        ORDER BY fee_year, quarter
        """
    )

    for year, quarter, count in cursor.fetchall():
        print(
            f"Year: {year} | "
            f"Quarter: {quarter} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # DME QUERY 4 - UNIQUE HCPCS
    # --------------------------------------------------

    print("\n4. UNIQUE DME HCPCS CODES")

    cursor.execute(
        """
        SELECT COUNT(DISTINCT hcpcs)
        FROM dme_fee_schedule
        WHERE hcpcs IS NOT NULL
        AND TRIM(hcpcs) <> ''
        """
    )

    print(f"Unique DME HCPCS codes: {cursor.fetchone()[0]}")

    # --------------------------------------------------
    # DME QUERY 5 - RECORDS BY RELEASE
    # --------------------------------------------------

    print("\n5. RECORDS BY DME RELEASE")

    cursor.execute(
        """
        SELECT
            release,
            COUNT(*)
        FROM dme_fee_schedule
        GROUP BY release
        ORDER BY release
        """
    )

    for release, count in cursor.fetchall():
        print(f"{release} | Records: {count}")

    # --------------------------------------------------
    # DME QUERY 6 - HIGHEST CEILING
    # --------------------------------------------------

    print("\n6. TOP 10 HIGHEST DME CEILING PRICES")

    cursor.execute(
        """
        SELECT
            hcpcs,
            ceiling,
            description
        FROM dme_fee_schedule
        WHERE ceiling IS NOT NULL
        AND TRIM(ceiling) <> ''
        ORDER BY CAST(ceiling AS REAL) DESC
        LIMIT 10
        """
    )

    for hcpcs, ceiling, description in cursor.fetchall():
        print(
            f"HCPCS: {hcpcs} | "
            f"Ceiling: {ceiling} | "
            f"Description: {description}"
        )

    # --------------------------------------------------
    # DME QUERY 7 - LOWEST FLOOR
    # --------------------------------------------------

    print("\n7. LOWEST DME FLOOR PRICES")

    cursor.execute(
        """
        SELECT
            hcpcs,
            floor,
            description
        FROM dme_fee_schedule
        WHERE floor IS NOT NULL
        AND TRIM(floor) <> ''
        ORDER BY CAST(floor AS REAL) ASC
        LIMIT 10
        """
    )

    for hcpcs, floor, description in cursor.fetchall():
        print(
            f"HCPCS: {hcpcs} | "
            f"Floor: {floor} | "
            f"Description: {description}"
        )

    # --------------------------------------------------
    # DME QUERY 8 - STATE PRICING
    # --------------------------------------------------

    print("\n8. DME STATE PRICING SUMMARY")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_state_pricing
        """
    )

    print(
        f"State pricing records: {cursor.fetchone()[0]}"
    )

    # --------------------------------------------------
    # DME QUERY 9 - NR VS R
    # --------------------------------------------------

    print("\n9. NON-RURAL VS RURAL PRICING")

    cursor.execute(
        """
        SELECT
            pricing_type,
            COUNT(*)
        FROM dme_state_pricing
        GROUP BY pricing_type
        ORDER BY pricing_type
        """
    )

    for pricing_type, count in cursor.fetchall():
        print(
            f"Pricing type: {pricing_type} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # DME QUERY 10 - STATE DISTRIBUTION
    # --------------------------------------------------

    print("\n10. STATE PRICING DISTRIBUTION")

    cursor.execute(
        """
        SELECT
            state,
            COUNT(*)
        FROM dme_state_pricing
        GROUP BY state
        ORDER BY state
        """
    )

    for state, count in cursor.fetchall():
        print(f"State: {state} | Records: {count}")

    # --------------------------------------------------
    # DME QUERY 11 - DMEPEN
    # --------------------------------------------------

    print("\n11. DMEPEN SUMMARY")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_pen_schedule
        """
    )

    print(f"DMEPEN records: {cursor.fetchone()[0]}")

    cursor.execute(
        """
        SELECT
            fee_year,
            quarter,
            COUNT(*)
        FROM dme_pen_schedule
        GROUP BY fee_year, quarter
        ORDER BY fee_year, quarter
        """
    )

    for year, quarter, count in cursor.fetchall():
        print(
            f"Year: {year} | "
            f"Quarter: {quarter} | "
            f"Records: {count}"
        )

    # --------------------------------------------------
    # DME QUERY 12 - FORMER CBA
    # --------------------------------------------------

    print("\n12. FORMER CBA PRICING SUMMARY")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_former_cba_pricing
        """
    )

    print(
        f"Former CBA pricing records: {cursor.fetchone()[0]}"
    )

    cursor.execute(
        """
        SELECT COUNT(DISTINCT cba_name)
        FROM dme_former_cba_pricing
        """
    )

    print(
        f"Unique CBA/location values: {cursor.fetchone()[0]}"
    )

    # --------------------------------------------------
    # DME QUERY 13 - RURAL ZIP
    # --------------------------------------------------

    print("\n13. RURAL ZIP SUMMARY")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_rural_zip
        """
    )

    print(
        f"Rural ZIP records: {cursor.fetchone()[0]}"
    )

    # --------------------------------------------------
    # DME QUERY 14 - FORMER CBA ZIP
    # --------------------------------------------------

    print("\n14. FORMER CBA ZIP SUMMARY")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_former_cba_zip
        """
    )

    print(
        f"Former CBA ZIP records: {cursor.fetchone()[0]}"
    )

    # --------------------------------------------------
    # DME QUERY 15 - MAIL ORDER DTS
    # --------------------------------------------------

    print("\n15. NATIONAL MAIL-ORDER DTS")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dme_mail_order_dts
        """
    )

    print(
        f"Mail-order DTS records: {cursor.fetchone()[0]}"
    )

    print()
    print("=" * 60)
    print("DME SQL ANALYSIS COMPLETED")
    print("=" * 60)


def main():

    connection = sqlite3.connect(DATABASE_FILE)

    try:

        cursor = connection.cursor()

        run_clfs_analysis(cursor)

        run_dme_analysis(cursor)

    finally:

        connection.close()

    print()
    print("=" * 60)
    print("SQL ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()