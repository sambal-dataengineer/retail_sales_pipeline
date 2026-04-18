-- Check schema
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'silver';

-- Check table exists
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'silver'
  AND table_name = 'cleaned_retail_sales';

-- Check row count
SELECT COUNT(*) AS row_count
FROM silver.cleaned_retail_sales;

-- Preview rows
SELECT *
FROM silver.cleaned_retail_sales
LIMIT 10;

-- Check columns and types
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'silver'
  AND table_name = 'cleaned_retail_sales'
ORDER BY ordinal_position;

-- Check nulls
SELECT
    COUNT(*) FILTER (WHERE "Transaction ID" IS NULL) AS transaction_id_nulls,
    COUNT(*) FILTER (WHERE "Customer ID" IS NULL) AS customer_id_nulls,
    COUNT(*) FILTER (WHERE "Category" IS NULL) AS category_nulls,
    COUNT(*) FILTER (WHERE "Item" IS NULL) AS item_nulls,
    COUNT(*) FILTER (WHERE "Price Per Unit" IS NULL) AS price_nulls,
    COUNT(*) FILTER (WHERE "Quantity" IS NULL) AS quantity_nulls,
    COUNT(*) FILTER (WHERE "Total Spent" IS NULL) AS total_spent_nulls,
    COUNT(*) FILTER (WHERE "Payment Method" IS NULL) AS payment_method_nulls,
    COUNT(*) FILTER (WHERE "Location" IS NULL) AS location_nulls,
    COUNT(*) FILTER (WHERE "Transaction Date" IS NULL) AS transaction_date_nulls,
    COUNT(*) FILTER (WHERE "Discount Applied" IS NULL) AS discount_applied_nulls
FROM silver.cleaned_retail_sales;

-- Check transaction id uniqueness
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT "Transaction ID") AS unique_transaction_ids
FROM silver.cleaned_retail_sales;

-- Validate total spent = price * quantity
SELECT COUNT(*) AS mismatch_count
FROM silver.cleaned_retail_sales
WHERE ROUND(("Price Per Unit" * "Quantity")::numeric, 2) <> ROUND("Total Spent"::numeric, 2);