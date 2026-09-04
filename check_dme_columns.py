import sqlite3

conn = sqlite3.connect("cms_clfs.db")
cursor = conn.cursor()

tables = [
    "dme_fee_schedule",
    "dme_pen_schedule",
    "dme_rural_zip",
    "dme_former_cba_fee",
    "dme_former_cba_zip",
    "dme_mail_order_dts"
]

for table in tables:
    print("\n" + "=" * 60)
    print(f"TABLE: {table}")
    print("=" * 60)

    columns = cursor.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    for column in columns:
        print(f"{column[1]:25} {column[2]}")

conn.close()