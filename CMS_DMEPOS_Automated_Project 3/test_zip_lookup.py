import sqlite3

DATABASE = "output/cms_dmepos.db"

conn = sqlite3.connect(DATABASE)

query = """
SELECT
    zip_code,
    mdcr_carrier_id,
    mdcr_fee_schd_id,
    rural_indicator,
    pricing_area_type,
    year_quarter
FROM zip_carrier_locality
WHERE zip_code = ?
"""

result = conn.execute(query, ("99501",)).fetchone()

print("ZIP LOOKUP RESULT")
print("-----------------")
print(result)

conn.close()
