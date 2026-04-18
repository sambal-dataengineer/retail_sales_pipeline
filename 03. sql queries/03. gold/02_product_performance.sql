DROP TABLE IF EXISTS gold.product_performance;

CREATE TABLE gold.product_performance AS
SELECT
    "Item" AS item,
    "Category" AS category,
    SUM("Quantity") AS total_quantity_sold,
    SUM("Total Spent") AS total_revenue,
    AVG("Price Per Unit") AS avg_unit_price,
    COUNT(DISTINCT "Transaction ID") AS transaction_count,
    COUNT(DISTINCT "Customer ID") AS unique_customers
FROM silver.cleaned_retail_sales
GROUP BY "Item", "Category"
ORDER BY total_revenue DESC;