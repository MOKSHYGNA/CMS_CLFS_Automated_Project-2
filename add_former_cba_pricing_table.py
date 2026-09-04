import sqlite3

DB_FILE = "cms_clfs.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dme_former_cba_pricing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hcpcs TEXT,
        mod TEXT,
        mod2 TEXT,
        mod3 TEXT,
        catg TEXT,
        cba_name TEXT,
        allowance TEXT,
        fee_year INTEGER,
        quarter TEXT,
        release TEXT,
        source_file TEXT
    )
""")

conn.commit()
conn.close()

print("=" * 60)
print("FORMER CBA PRICING TABLE CREATED")
print("=" * 60)
print("Table: dme_former_cba_pricing")