DROP TABLE IF EXISTS gold.customer_analysis;

CREATE TABLE gold.customer_analysis AS
SELECT
    "Customer ID" AS customer_id,
    COUNT(DISTINCT "Transaction ID") AS total_orders,
    SUM("Quantity") AS total_quantity_sold,
    SUM("Total Spent") AS total_revenue,
    AVG("Total Spent") AS avg_order_value,
    MIN(DATE("Transaction Date")) AS first_purchase_date,
    MAX(DATE("Transaction Date")) AS last_purchase_date
FROM silver.cleaned_retail_sales
GROUP BY "Customer ID"
ORDER BY total_revenue DESC;