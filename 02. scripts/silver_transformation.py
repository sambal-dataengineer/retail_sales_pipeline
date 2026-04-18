import pandas as pd
import numpy as np
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
# CREATE DATABASE ENGINE
# =========================================================
engine = create_engine(
    f"postgresql://{username}:{password}@{host}:{port}/{database}"
)


# =========================================================
# LOAD DATA FROM BRONZE
# =========================================================
print("=" * 60)
print("Loading data from bronze")
print("=" * 60)

query = "SELECT * FROM bronze.raw_retail_sales;"

df = pd.read_sql(query, engine)

print("\nBronze data loaded successfully.")
print(f"shape: {df.shape}")

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 10 rows")
print(df.head(10))

print("\nRaw Data types:")
print(df.dtypes)

print("\nRaw info:")
print(df.info())

print("\nRaw full description:")
print(df.describe(include = 'all'))

print("\nMissing Values before cleaning:")
print(df.isnull().sum())

print("\nDuplicate rows before cleaning:")
print(df.duplicated().sum())

# =========================================================
# CREATE WORKING COPY
# =========================================================
print("\n" + "=" * 60)
print("Creating working copy")
print("=" * 60)

clean_df = df.copy()

print("\nWorking copy created.")
print(f"Working shape: {clean_df.shape}")

# =========================================================
# CREATE DATA QUALITY FLAGS
# =========================================================
# These are used only temporarily during transformation.
# They will be removed before loading to Silver.
print("\n" + "=" * 60)
print("Creating Data Quality Flags")
print("=" * 60)

clean_df['item_missing_flag'] = clean_df['Item'].isna()
clean_df['price_missing_flag'] = clean_df['Price Per Unit'].isna()
clean_df['quantity_missing_flag'] = clean_df['Quantity'].isna()
clean_df['total_missing_flag'] = clean_df['Total Spent'].isna()
clean_df['discount_missing_flag'] = clean_df['Discount Applied'].isna()

print("\nData quality flags created.")
print("\nFlag Summary:")
print(clean_df[
    [
        'item_missing_flag',
        'price_missing_flag',
        'quantity_missing_flag',
        'total_missing_flag',
        'discount_missing_flag'
    ]
].sum())

# =========================================================
# STANDARDIZE TEXT COLUMNS
# =========================================================
print("\n" + "=" * 60)
print("Standardizing Text Columns")
print("=" * 60)

text_columns = [
    'Transaction ID',
    'Customer ID',
    'Category',
    'Item',
    'Payment Method',
    'Location'
]

for col in text_columns:
    clean_df[col] = clean_df[col].astype("string").str.strip()

print("\nText columns standardized.")
print("\nSample values after text standardization")
for col in text_columns:
    print(f"\nColumn: {col}")
    print(clean_df[col].dropna().unique()[:5])

# =========================================================
# CONVERT DATE COLUMN
# =========================================================
print("\n" + "=" * 60)
print("Converting Transaction Date")
print("=" * 60)

clean_df['Transaction Date'] = pd.to_datetime(
    clean_df["Transaction Date"],
    format = 'mixed',
    dayfirst = True,
    errors = 'coerce'
)

print("\nTransaction Date converted to datetime.")
print("\nDate Range after conversion:")
print(clean_df['Transaction Date'].min(), "to", clean_df["Transaction Date"].max())
missing_dates = clean_df["Transaction Date"].isna().sum()

print("\nMissing Transaction Date values after conversion:")
print(missing_dates)

if missing_dates > 0:
    print("\nSample problematic date values:")
    print(df.loc[clean_df["Transaction Date"].isna(), "Transaction Date"].head(10))

# =========================================================
# CONVERT NUMERICAL COLUMNS
# =========================================================
print("\n" + "=" * 60)
print("Converting Numerical Columns")
print("=" * 60)

numerical_columns = [
    'Price Per Unit',
    'Quantity',
    'Total Spent'
]

for col in numerical_columns:
    clean_df[col] = pd.to_numeric(clean_df[col], errors = 'coerce')

print("\nNumerical columns converted.")
print("\nData types after numerical conversion:")
print(clean_df[numerical_columns].dtypes)

print("\nMissing values in numerical columns after conversion:")
print(clean_df[numerical_columns].isnull().sum())

# =========================================================
# CLEAN DISCOUNT APPLIED
# =========================================================
print("\n" + "=" * 60)
print("Converting Discount Applied")
print("=" * 60)

clean_df["Discount Applied"] = clean_df['Discount Applied'].map({
    True: "Yes",
    False: "No",
    "True": "Yes",
    "False": "No"
})

clean_df["Discount Applied"] = clean_df["Discount Applied"].fillna("Not Applicable")

print("\nDiscount Applied Converted.")
print("\nValue counts after conversion:")
print(clean_df["Discount Applied"].value_counts(dropna = False))

print("\nData type of Discount Applied:\n",clean_df["Discount Applied"].dtype)

# =========================================================
# RECONSTRUCT PRICE PER UNIT
# =========================================================
print("\n" + "=" * 60)
print("Reconstructing Missing Price Per Unit")
print("=" * 60)

price_missing_before = clean_df["Price Per Unit"].isna().sum()

price_fill_mask = (
    clean_df["Price Per Unit"].isna()
    & clean_df["Total Spent"].notna()
    & clean_df["Quantity"].notna()
    & (clean_df["Quantity"] != 0)
)

reconstructed_price_count = price_fill_mask.sum()

clean_df.loc[price_fill_mask, "Price Per Unit"] = (
    clean_df.loc[price_fill_mask, "Total Spent"]
    / clean_df.loc[price_fill_mask, "Quantity"]
).round(2)

price_missing_after = clean_df['Price Per Unit'].isna().sum()

print(f"\nPrice Per Unit missing before: {price_missing_before}")
print(f"Rows reconstructed: {reconstructed_price_count}")
print(f"Price Per Unit missing after: {price_missing_after}")

# =========================================================
# RECONSTRUCT QUANTITY
# =========================================================
print("\n" + "=" * 60)
print("Reconstructing Missing Quantity")
print("=" * 60)

quantity_missing_before = clean_df["Quantity"].isna().sum()

quantity_fill_mask = (
    clean_df["Quantity"].isna()
    & clean_df["Total Spent"].notna()
    & clean_df["Price Per Unit"].notna()
    & (clean_df["Price Per Unit"] != 0)
)

candidate_quantity = (
    clean_df.loc[quantity_fill_mask, "Total Spent"]
    / clean_df.loc[quantity_fill_mask, "Price Per Unit"]
)

valid_quantity_mask = np.isclose(candidate_quantity % 1, 0)
valid_quantity_index = candidate_quantity[valid_quantity_mask].index

clean_df.loc[valid_quantity_index, "Quantity"] = (
    candidate_quantity[valid_quantity_mask].round()
)

quantity_missing_after = clean_df["Quantity"].isna().sum()

print(f"\nQuantity missing before: {quantity_missing_before}")
print(f"Rows eligible for calculation: {quantity_fill_mask.sum()}")
print(f"Rows safely reconstructed: {len(valid_quantity_index)}")
print(f"Quantity missing after: {quantity_missing_after}")

# =========================================================
# RECONSTRUCT TOTAL SPENT
# =========================================================
print("\n" + "=" * 60)
print("Reconstructing Missing Total Spent")
print("=" * 60)

total_missing_before = clean_df["Total Spent"].isna().sum()

total_fill_mask = (
    clean_df["Total Spent"].isna()
    & clean_df["Price Per Unit"].notna()
    & clean_df["Quantity"].notna()
)

reconstructed_total_count = total_fill_mask.sum()

clean_df.loc[total_fill_mask, "Total Spent"] = (
    clean_df.loc[total_fill_mask, "Price Per Unit"]
    * clean_df.loc[total_fill_mask, "Quantity"]
).round(2)

total_missing_after = clean_df["Total Spent"].isna().sum()

print(f"\nTotal Spent missing before: {total_missing_before}")
print(f"Rows reconstructed: {reconstructed_total_count}")
print(f"Total Spent missing after: {total_missing_after}")

# =========================================================
# RECONSTRUCT ITEM USING CATEGORY + PRICE PER UNIT 
# =========================================================
print("\n" + "=" * 60)
print("Reconstructing Missing Item Values")
print("=" * 60)

item_missing_before = clean_df["Item"].isna().sum()

item_lookup_df = (
    clean_df.dropna(subset = ["Category", "Price Per Unit", "Item"])
    .drop_duplicates(subset = ["Category", "Price Per Unit"])
    [["Category", "Price Per Unit", "Item"]]
)

item_lookup = {}
for _, row in item_lookup_df.iterrows():
    key = (row["Category"], round(float(row["Price Per Unit"]), 2))
    value = row["Item"]
    item_lookup[key] = value

item_fill_mask = (
    clean_df["Item"].isna()
    & clean_df["Category"].notna()
    & clean_df["Price Per Unit"].notna()
)

clean_df.loc[item_fill_mask, "Item"] = clean_df.loc[item_fill_mask].apply(
    lambda row: item_lookup.get(
        (row["Category"], round(float(row["Price Per Unit"]), 2))
    ),
    axis = 1
)

item_missing_after = clean_df["Item"].isna().sum()

print(f"\nItem missing before: {item_missing_before}")
print(f"Rows eligible for reconstruction: {item_fill_mask.sum()}")
print(f"Item missing after: {item_missing_after}")

# =========================================================
# DROP UNUSABLE ROWS
# =========================================================
print("\n" + "=" * 60)
print("Dropping Unsuable Rows")
print("=" * 60)

print("\nRemaining missing values after all reconstructions:")
print(clean_df[["Price Per Unit", "Quantity", "Total Spent"]].isna().sum())

rows_before_drop = len(clean_df)

drop_mask = (
    clean_df["Price Per Unit"].isna()
    | clean_df["Quantity"].isna()
    | clean_df["Total Spent"].isna()
    | clean_df["Transaction Date"].isna()
)

rows_to_drop = drop_mask.sum()

clean_df = clean_df.loc[~drop_mask].copy()

rows_after_drop = len(clean_df)

print(f"\nRows before dopping unsuable rows: {rows_before_drop}")
print(f"Rows dropped: {rows_to_drop}")
print(f"Rows after dropping unusable rows: {rows_after_drop}")

# =========================================================
# FINALIZE QUANTITY TYPE
# =========================================================
print("\n" + "=" * 60)
print("Finalizing Quantity Type")
print("=" * 60)

clean_df["Quantity"] = clean_df["Quantity"].round().astype("Int64")

print("\nQuantity converted to integer.")
print(clean_df["Quantity"].dtype)

print("\nQuantity summary:")
print(clean_df["Quantity"].describe())

# =========================================================
# VALIDATE TOTAL SPENT
# =========================================================
print("\n" + "=" * 60)
print("Validating Total Spent")
print("=" * 60)

validation_mask = clean_df[
    ["Price Per Unit", "Quantity", "Total Spent"]
].notna().all(axis = 1)

mismatch_count = (
    ~np.isclose(
        clean_df.loc[validation_mask, "Price Per Unit"] * clean_df.loc[validation_mask, "Quantity"],
        clean_df.loc[validation_mask, "Total Spent"]
    )
).sum()

print(f"\nRows checked for total validation: {validation_mask.sum()}")
print(f"Total mismatch count: {mismatch_count}")

# =========================================================
# REMOVE FLAG COLUMNS BEFORE LOADING TO SILVER
# =========================================================
print("\n" + "=" * 60)
print("Removing Flag Columns")
print("=" * 60)

flag_columns = [
    "item_missing_flag",
    "price_missing_flag",
    "quantity_missing_flag",
    "total_missing_flag",
    "discount_missing_flag"
]

clean_df.drop(columns = flag_columns, inplace = True)

print("\nFlag columns removed.")
print("Remaining columns:")
print(clean_df.columns.tolist())

# =========================================================
# FINAL BEFORE VS AFTER SUMMARY
# =========================================================
print("\n" + "=" * 60)
print("Before Vs After Summary")
print("=" * 60)

print("\nBefore cleaning")
print(f"Shape: {df.shape}")
print("\nMissing Values:")
print(df.isnull().sum())
print("\nData types:")
print(df.dtypes)

print("\n" + "-" * 60)

print("\nAfter cleaning")
print(f"Shape: {clean_df.shape}")
print("\nMissing Values:")
print(clean_df.isnull().sum())
print("\nData types:")
print(clean_df.dtypes)

# =========================================================
# FINAL INFO + DESCRIBE
# =========================================================
print("\n" + "=" * 60)
print("Final Cleaned Data Preview")
print("=" * 60)

print("\nFirst 10 cleaned rows:")
print(clean_df.head(10))

print("\nCleaned info:")
print(clean_df.info())

print("\nCleaned description:")
print(clean_df.describe(include = 'all'))

print("\nUnique values count per column after cleaning:")
for col in clean_df.columns:
    print(f"{col}: \t{clean_df[col].nunique(dropna = True)} unique values")

# =========================================================
# CREATE SILVER SCHEMA
# =========================================================
print("\n" + "=" * 60)
print("Creating Silver Schema")
print("=" * 60)

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
    conn.commit()

print("\nSilver schema ready.")

# =========================================================
# LOAD CLEAN DATA INTO SILVER
# =========================================================
print("\n" + "=" * 60)
print("Loading Data Into Silver.cleaned_retail_sales")
print("=" * 60)

clean_df.to_sql(
    name = "cleaned_retail_sales",
    con = engine,
    schema = "silver",
    if_exists = "replace",
    index = False
)

print("\nCleaned data loaded successfully into silver.cleaned_retail_sales")

# =========================================================
# VERIFY SILVER LOAD
# =========================================================
print("\n" + "=" * 60)
print("Verifying Silver Load")
print("=" * 60)

verification_query = """
SELECT COUNT(*) AS row_count
FROM silver.cleaned_retail_sales
"""

verification_df = pd.read_sql(verification_query, engine)

print("\nSilver table row count:")
print(verification_df)

print("\nSilver transformation completed successfully")