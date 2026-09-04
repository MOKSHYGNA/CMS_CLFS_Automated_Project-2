import sqlite3

conn = sqlite3.connect("cms_clfs.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dme_state_pricing (
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
print("DME STATE PRICING TABLE CREATED")
print("=" * 60)
print("Table: dme_state_pricing")