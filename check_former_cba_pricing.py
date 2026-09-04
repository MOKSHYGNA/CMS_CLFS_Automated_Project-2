import sqlite3
import pandas as pd

conn = sqlite3.connect("cms_clfs.db")

print("=" * 60)
print("FORMER CBA PRICING VALIDATION")
print("=" * 60)

# 1. Total records
result = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM dme_former_cba_pricing",
    conn
)

print("\nTotal records:")
print(result.to_string(index=False))

# 2. Records by year
result = pd.read_sql_query(
    """
    SELECT fee_year, COUNT(*) AS records
    FROM dme_former_cba_pricing
    GROUP BY fee_year
    ORDER BY fee_year
    """,
    conn
)

print("\nRecords by fee year:")
print(result.to_string(index=False))

# 3. Records by year and quarter
result = pd.read_sql_query(
    """
    SELECT fee_year, quarter, COUNT(*) AS records
    FROM dme_former_cba_pricing
    GROUP BY fee_year, quarter
    ORDER BY fee_year, quarter
    """,
    conn
)

print("\nRecords by year and quarter:")
print(result.to_string(index=False))

# 4. CBA/location distribution
result = pd.read_sql_query(
    """
    SELECT cba_name, COUNT(*) AS records
    FROM dme_former_cba_pricing
    GROUP BY cba_name
    ORDER BY cba_name
    LIMIT 20
    """,
    conn
)

print("\nFirst 20 CBA/location values:")
print(result.to_string(index=False))

# 5. Sample records
result = pd.read_sql_query(
    """
    SELECT
        hcpcs,
        mod,
        mod2,
        mod3,
        catg,
        cba_name,
        allowance,
        fee_year,
        quarter,
        release
    FROM dme_former_cba_pricing
    LIMIT 20
    """,
    conn
)

print("\nSample records:")
print(result.to_string(index=False))

# 6. Missing allowances
result = pd.read_sql_query(
    """
    SELECT COUNT(*) AS missing_allowance
    FROM dme_former_cba_pricing
    WHERE allowance IS NULL
       OR TRIM(allowance) = ''
    """,
    conn
)

print("\nMissing allowance records:")
print(result.to_string(index=False))

# 7. Unique CBA/location count
result = pd.read_sql_query(
    """
    SELECT COUNT(DISTINCT cba_name) AS unique_cba_locations
    FROM dme_former_cba_pricing
    """,
    conn
)

print("\nUnique CBA/location values:")
print(result.to_string(index=False))

conn.close()

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)