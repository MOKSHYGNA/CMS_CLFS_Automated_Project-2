import sqlite3
import re

DB_FILE = "cms_clfs.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("=" * 60)
print("CLEANING MAIL-ORDER DTS TABLE")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM dme_mail_order_dts")
before = cursor.fetchone()[0]

print(f"\nRecords before cleanup: {before}")

# Get all records
cursor.execute("""
    SELECT id, hcpcs
    FROM dme_mail_order_dts
""")

rows = cursor.fetchall()

deleted = 0

for row_id, hcpcs in rows:

    hcpcs = str(hcpcs).strip() if hcpcs is not None else ""

    # Valid HCPCS codes are normally 5 characters:
    # one letter followed by four digits
    if not re.fullmatch(r"[A-Z][0-9]{4}", hcpcs.upper()):
        cursor.execute(
            "DELETE FROM dme_mail_order_dts WHERE id = ?",
            (row_id,)
        )
        deleted += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM dme_mail_order_dts")
after = cursor.fetchone()[0]

print(f"Records after cleanup : {after}")
print(f"Invalid records removed: {deleted}")

conn.close()

print("\n" + "=" * 60)
print("MAIL-ORDER DTS CLEANUP COMPLETE")
print("=" * 60)