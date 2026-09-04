import sqlite3

DB_FILE = "cms_clfs.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("TABLES:")
tables = cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name LIKE 'dme_%'
    ORDER BY name
""").fetchall()

for table in tables:
    print(table[0])

print("\nCOUNTS:")

table_names = [
    "dme_fee_schedule",
    "dme_pen_schedule",
    "dme_rural_zip",
    "dme_former_cba_fee",
    "dme_former_cba_zip",
    "dme_mail_order_dts"
]

for table in table_names:
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count}")

conn.close()