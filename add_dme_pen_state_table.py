import sqlite3

DB_FILE = "cms_clfs.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dme_pen_state_pricing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hcpcs TEXT,
        mod TEXT,
        mod2 TEXT,
        state TEXT,
        pricing_type TEXT,
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
print("DMEPEN STATE PRICING TABLE CREATED")
print("=" * 60)
print("Table: dme_pen_state_pricing")