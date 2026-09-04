import sqlite3
import pandas as pd

conn = sqlite3.connect("cms_clfs.db")

print("=" * 60)
print("DME OTHER TABLES VALIDATION")
print("=" * 60)

tables = [
    "dme_rural_zip",
    "dme_former_cba_zip",
    "dme_mail_order_dts"
]

for table in tables:

    print("\n" + "-" * 60)
    print(f"TABLE: {table}")
    print("-" * 60)

    result = pd.read_sql_query(
        f"SELECT COUNT(*) AS records FROM {table}",
        conn
    )

    print("\nTotal records:")
    print(result.to_string(index=False))

    result = pd.read_sql_query(
        f"""
        SELECT fee_year, quarter, COUNT(*) AS records
        FROM {table}
        GROUP BY fee_year, quarter
        ORDER BY fee_year, quarter
        """,
        conn
    )

    print("\nRecords by year and quarter:")
    print(result.to_string(index=False))

    result = pd.read_sql_query(
        f"""
        SELECT *
        FROM {table}
        LIMIT 10
        """,
        conn
    )

    print("\nSample records:")
    print(result.to_string(index=False))

conn.close()

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)