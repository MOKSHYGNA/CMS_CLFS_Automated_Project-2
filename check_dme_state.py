import sqlite3
import pandas as pd

conn = sqlite3.connect("cms_clfs.db")

print("=" * 60)
print("DME STATE PRICING VALIDATION")
print("=" * 60)

# Total records
result = pd.read_sql_query(
    "SELECT COUNT(*) AS total FROM dme_state_pricing",
    conn
)
print("\nTotal records:")
print(result.to_string(index=False))

# Records by year
result = pd.read_sql_query(
    """
    SELECT fee_year, COUNT(*) AS records
    FROM dme_state_pricing
    GROUP BY fee_year
    ORDER BY fee_year
    """,
    conn
)
print("\nRecords by fee year:")
print(result.to_string(index=False))

# Records by year and quarter
result = pd.read_sql_query(
    """
    SELECT fee_year, quarter, COUNT(*) AS records
    FROM dme_state_pricing
    GROUP BY fee_year, quarter
    ORDER BY fee_year, quarter
    """,
    conn
)
print("\nRecords by year and quarter:")
print(result.to_string(index=False))

# State distribution
result = pd.read_sql_query(
    """
    SELECT state, COUNT(*) AS records
    FROM dme_state_pricing
    GROUP BY state
    ORDER BY state
    """,
    conn
)
print("\nState distribution:")
print(result.to_string(index=False))

# Pricing type
result = pd.read_sql_query(
    """
    SELECT pricing_type, COUNT(*) AS records
    FROM dme_state_pricing
    GROUP BY pricing_type
    ORDER BY pricing_type
    """,
    conn
)
print("\nPricing type distribution:")
print(result.to_string(index=False))

# Sample records
result = pd.read_sql_query(
    """
    SELECT
        hcpcs,
        mod,
        mod2,
        state,
        pricing_type,
        allowance,
        fee_year,
        quarter,
        release
    FROM dme_state_pricing
    LIMIT 20
    """,
    conn
)
print("\nSample records:")
print(result.to_string(index=False))

# Missing allowances
result = pd.read_sql_query(
    """
    SELECT COUNT(*) AS missing_allowance
    FROM dme_state_pricing
    WHERE allowance IS NULL
       OR TRIM(allowance) = ''
    """,
    conn
)
print("\nMissing allowance records:")
print(result.to_string(index=False))

conn.close()

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)