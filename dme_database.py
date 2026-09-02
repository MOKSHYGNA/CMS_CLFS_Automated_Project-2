import sqlite3
from pathlib import Path


DB_FILE = Path("cms_clfs.db")


def create_dme_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # 1. MAIN DMEPOS FEE SCHEDULE
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_fee_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            mod TEXT,
            mod2 TEXT,
            juris TEXT,
            catg TEXT,
            ceiling TEXT,
            floor TEXT,
            description TEXT,
            fee_year INTEGER,
            quarter TEXT,
            release TEXT,
            source_file TEXT
        )
    """)

    # ---------------------------------------------------------
    # 2. DMEPEN - PARENTERAL / ENTERAL NUTRITION
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_pen_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            mod TEXT,
            mod2 TEXT,
            description TEXT,
            fee_year INTEGER,
            quarter TEXT,
            release TEXT,
            source_file TEXT
        )
    """)

    # ---------------------------------------------------------
    # 3. RURAL ZIP CODE
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_rural_zip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            rural_zip_code TEXT,
            year_qtr TEXT,
            fee_year INTEGER,
            quarter TEXT,
            source_file TEXT
        )
    """)

    # ---------------------------------------------------------
    # 4. FORMER CBA FEE SCHEDULE
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_former_cba_fee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            mod TEXT,
            mod2 TEXT,
            mod3 TEXT,
            catg TEXT,
            description TEXT,
            fee_year INTEGER,
            quarter TEXT,
            release TEXT,
            source_file TEXT
        )
    """)

    # ---------------------------------------------------------
    # 5. FORMER CBA ZIP CODE
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_former_cba_zip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cba_state TEXT,
            cba_zip_code TEXT,
            cba_name_short TEXT,
            cba_name TEXT,
            year_qtr TEXT,
            fee_year INTEGER,
            quarter TEXT,
            source_file TEXT
        )
    """)

    # ---------------------------------------------------------
    # 6. FORMER CBA NATIONAL MAIL-ORDER DTS
    # ---------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dme_mail_order_dts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcpcs TEXT,
            mod TEXT,
            mod2 TEXT,
            mod3 TEXT,
            catg TEXT,
            national_mail_order TEXT,
            description TEXT,
            fee_year INTEGER,
            quarter TEXT,
            release TEXT,
            source_file TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("=" * 60)
    print("DME DATABASE TABLES CREATED")
    print("=" * 60)
    print("1. dme_fee_schedule")
    print("2. dme_pen_schedule")
    print("3. dme_rural_zip")
    print("4. dme_former_cba_fee")
    print("5. dme_former_cba_zip")
    print("6. dme_mail_order_dts")
    print("=" * 60)


if __name__ == "__main__":
    create_dme_tables()
    