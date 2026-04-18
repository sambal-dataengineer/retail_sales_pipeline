SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'bronze';

SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'bronze'
  AND table_name = 'raw_retail_sales';

SELECT COUNT(*) AS row_count
FROM bronze.raw_retail_sales;

SELECT *
FROM bronze.raw_retail_sales
LIMIT 10;

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'bronze'
	AND table_name = 'raw_retail_sales'
ORDER BY ordinal_position;

SELECT
	COUNT(*) FILTER (WHERE "Transaction ID" IS NULL) AS transaction_id_nulls,
	COUNT(*) FILTER (WHERE "Customer ID" IS NULL) AS customer_id_nulls,
	COUNT(*) FILTER (WHERE "Category" IS NULL) AS category_nulls,
	COUNT(*) FILTER (WHERE "Item" IS NULL) AS item_nulls,
	COUNT(*) FILTER (WHERE "Price Per Unit" IS NULL) AS price_nulls,
	COUNT(*) FILTER (WHERE "Quantity" IS NULL) AS quantity_nulls,
	COUNT(*) FILTER (WHERE "Total Spent" IS NULL) AS total_spent_nulls,
	COUNT(*) FILTER (WHERE "Payment Method" IS NULL) AS payment_nulls,
	COUNT(*) FILTER (WHERE "Location" IS NULL) AS location_nulls,
	COUNT(*) FILTER (WHERE "Transaction Date" IS NULL) AS transaction_date_nulls,
	COUNT(*) FILTER (WHERE "Discount Applied" IS NULL) AS discount_applied_nulls
FROM bronze.raw_retail_sales;