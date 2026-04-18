import pandas as pd
from sqlalchemy import create_engine, text

# =========================================================
# DATABASE CONFIGURATION
# =========================================================
username = "postgres"
password = "root"
host = "localhost"
port = "5432"
database = "retail_sales_project"

# =========================================================
# FILE PATH
# =========================================================
file_path = r"C:\Users\samba\OneDrive\Desktop\Data_Engineer\retail_store_sales_pipeline_project\01. data/retail_store_sales.csv"

# =========================================================
# CREATE DATABASE ENGINE
# =========================================================
engine = create_engine(
    f"postgresql://{username}:{password}@{host}:{port}/{database}"
)

# =========================================================
# LOAD RAW CSV
# =========================================================
print("=" * 60)
print("Loading raw CSV")
print("=" * 60)

df = pd.read_csv(file_path)

print("\nRaw file loaded successfully.")
print(f"shapes: {df.shape}")
print("\nColumns:")
print(df.columns.tolist())

# =========================================================
# CREATE BRONZE SCHEMA IF NOT EXISTS
# =========================================================
print("=" * 60)
print("Creating Bronze Schema")
print("=" * 60)
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze;"))
    conn.commit()

print("\nBronze schema ready.")

# =========================================================
# LOAD RAW DATA INTO BRONZE TABLE
# =========================================================
print("=" * 60)
print("Loading Data into bronze.raw_retail_sales")
print("=" * 60)

df.to_sql(
    name = "raw_retail_sales",
    con = engine,
    schema = "bronze",
    if_exists = "replace",
    index = False
)

print("\nRaw data loaded successfully into bronze.raw_retail_sales.")

# =========================================================
# VERIFICATION
# =========================================================
print("\n" + "=" * 60)
print("Verifying Bronze load")
print("=" * 60)

verification_query = """
SELECT COUNT(*) AS row_count
FROM bronze.raw_retail_sales;
"""

verification_df = pd.read_sql(verification_query, engine)
print("\nBronze table row count:")
print(verification_df)

print("\nBronze Ingestion complete successfully.")
