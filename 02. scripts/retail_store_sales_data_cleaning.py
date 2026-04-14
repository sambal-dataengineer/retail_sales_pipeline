import pandas as pd
import numpy as np

# =========================================================
# FILE PATHS
# =========================================================

file_path = r"C:\Users\samba\OneDrive\Desktop\Data_Engineer\retail_store_sales_pipeline_project\01. data/retail_store_sales.csv"

# =========================================================
# LOAD RAW DATA
# =========================================================

print("=" * 60)
print("Loading Raw Data")
print("=" * 60)

df = pd.read_csv(file_path)

print("\nRaw dataset loaded successfully.")
print(f"Raw shape: {df.shape}")

print("\nFirst 10 rows:")
print(df.head(10))

print("\nRaw Data types:")
print(df.dtypes)

print("\nRaw info:")
print(df.info())

print("\nRaw full desciption:")
print(df.describe(include = 'all'))

print("\nMissing Values before cleaning:")
print(df.isnull().sum())

print("\nDuplicate rows before cleaning:")
print(df.duplicated().sum())

# =========================================================
# MAKE A WORKING COPY
# =========================================================

print("\n" + "=" * 60)
print("Creating Working Copy")
print("=" * 60)

clean_df = df.copy()

print("\nWorking copy created.")
print(f"Working shape: {clean_df.shape}")

# =========================================================
# CREATE DATA QUALITY FLAGS
# =========================================================
# These flags preserve the original missingness information.
# Even if we later fill a value, we still know that the raw file had an issue.

print("\n" + "=" * 60)
print("Creating Data Quality Flags")
print("=" * 60)

clean_df['item_missing_flag'] = clean_df['Item'].isna()
clean_df['price_missing_flag'] = clean_df['Price Per Unit'].isna()
clean_df['quantity_missing_flag'] = clean_df['Quantity'].isna()
clean_df['total_missing_flag'] = clean_df['Total Spent'].isna()
clean_df['discount_missing_flag'] = clean_df['Discount Applied'].isna()

print("\nData quality flags added.")
print("\nFlag summary:")
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
# We strip extra spaces from text columns.

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
print("\nSample values after text standardizstion")
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
    clean_df['Transaction Date'],
    format = 'mixed',
    dayfirst = True,
    errors = 'coerce'
)

print("\nTransaction Date converted to datetime.")
print("\ Date range after conversion:")
print(clean_df['Transaction Date'].min(), "to", clean_df['Transaction Date'].max())

missing_dates = clean_df["Transaction Date"].isna().sum()

print("\nMissing Transaction Date values after conversion:")
print(clean_df['Transaction Date'].isna().sum())

if missing_dates > 0:
    print("\nSample problematic date values:")
    print(df.loc[clean_df["Transaction Date"].isna(), "Transaction Date"].head(10))

# =========================================================
# CONVERT NUMERICAL COLUMNS
# =========================================================
print("\n" + "=" * 60)
print("Converting Numerical Columns")
print("=" * 60)

numeric_columns = [
    'Price Per Unit', 
    'Quantity', 
    'Total Spent'
]

for col in numeric_columns:
    clean_df[col] = pd.to_numeric(
        clean_df[col],
        errors = 'coerce'
)

print("\nNumerical columns created.")
print("\nData types after numerical conversion:")
print(clean_df[numeric_columns].dtypes)

print("\nMissing values in numerical columns after conversion:")
print(clean_df[numeric_columns].isnull().sum())

# =========================================================
# CONVERT DISCOUNT APPLIED TO NULLABLE BOOLEAN
# =========================================================

print("\n" + "=" * 60)
print("Converting Discount Applied")
print("=" * 60)

clean_df["Discount Applied"] = clean_df["Discount Applied"].map({
    True: "Yes",
    False: "No",
    "True": "Yes",
    "Fales": "No"
})

clean_df["Discount Applied"] = clean_df["Discount Applied"].fillna("Not Applicable")

print("\nDiscount Applied converted.")
print("\nValue counts after conversion:")
print(clean_df["Discount Applied"].value_counts(dropna = False))

print("\nDtype of Discount Applied:")
print(clean_df["Discount Applied"].dtype)

# =========================================================
# RECONSTRUCT PRICE PER UNIT
# =========================================================
# If Price Per Unit is missing, but Total Spent and Quantity exist,
# then we can safely compute:
# Price Per Unit = Total Spent / Quantity

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

price_missing_after = clean_df["Price Per Unit"].isna().sum()

print(f"\nPrice Per Unit missing before: {price_missing_before}")
print(f"Rows reconstructed: {reconstructed_price_count}")
print(f"Price Per Unit missing after: {price_missing_after}")

# =========================================================
# RECONSTRUCT Quantity
# =========================================================
# If Quantity is missing, but Total Spent and Price Per Unit exist,
# then we can safely compute:
# Quantity = Total Spent / Price Per Unit

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

valid_quantity_index = np.isclose(candidate_quantity % 1, 0)

valid_quantity_index = candidate_quantity[valid_quantity_index].index

clean_df.loc[valid_quantity_index, "Quantity"] = (
    candidate_quantity[valid_quantity_index].round()
)

quantity_missing_after = clean_df["Quantity"].isna().sum()

print(f"\nQuantity missing before: {quantity_missing_before}")
print(f"Rows eligible for calculation: {quantity_fill_mask.sum()}")
print(f"Rows safely reconstructed: {len(valid_quantity_index)}")
print(f"Quantity missing after: {quantity_missing_after}")

# =========================================================
# RECONSTRUCT Total Spent
# =========================================================
# If Total Spent is missing, but Quantity and Price Per Unit exist,
# then we can safely compute:
# Total Spent = Price Per Unit * Quantity

print("\n" + "=" * 60)
print("RECONSTRUCTING MISSING TOTAL SPENT")
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
# We discovered from inspection that within this dataset,
# Category + Price Per Unit uniquely identifies Item.

print("\n" + "=" * 60)
print("Reconstructing Missing Item Values")
print("=" * 60)

item_missing_before = clean_df["Item"].isna().sum()

item_lookup_df = (
    clean_df.dropna(subset = ["Category", "Price Per Unit", "Item"])
    .drop_duplicates(subset = ["Category", "Price Per Unit"])
    [["Category", "Price Per Unit", "Item"]]
)

item_lookup = {
    (row["Category"], round(float(row["Price Per Unit"]), 2)): row["Item"]
    for _, row in item_lookup_df.iterrows()
}

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
# Rows missing Quantity or Total Spent cannot support revenue analysis,
# sales aggregation, or ML target generation.
# Also drop rows with invalid Transaction Date if any appear.

print("\n" + "=" * 60)
print("Dropping Unusable Rows")
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

print(f"\nRows before dropping unusable rows: {rows_before_drop}")
print(f"Rows dropped: {rows_to_drop}")
print(f"Rows after dropping unusable rows: {rows_after_drop}")

# =========================================================
# FINALIZE QUANTITY TYPE
# =========================================================
# Quantity is logically an integer count of units sold.

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
# Validate:
# Total Spent == Price Per Unit * Quantity

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
print(f"Total mismatches found: {mismatch_count}")

# =========================================================
# FINAL BEFORE VS AFTER SUMMARY
# =========================================================

print("\n" + "=" * 60)
print("Before Vs After Summary")
print("=" * 60)

print("\nBefore cleaning")
print(f"Shape: {df.shape}")
print("\nMissing values:")
print(df.isnull().sum())
print("\nData types:")
print(df.dtypes)

print("\n" + "-" * 60)

print("\nAfter cleaning")
print(f"Shape: {clean_df.shape}")
print("\nMissing values:")
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
# EXPORT CLEANED CSV
# =========================================================

print("\n" + "=" * 60)
print("Before Vs After Summary")
print("=" * 60)

cleaned_file_path = r"C:\Users\samba\OneDrive\Desktop\Data_Engineer\retail_store_sales_pipeline_project\01. data/cleaned_retail_store_sales.csv"
clean_df.to_csv(cleaned_file_path, index = False)

print(f"\nCleaned file saved successfully to: {cleaned_file_path}")
print("\nData cleaning completed successfully")