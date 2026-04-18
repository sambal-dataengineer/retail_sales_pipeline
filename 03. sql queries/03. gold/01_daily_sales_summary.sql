DROP TABLE IF EXISTS gold.daily_sales_summary;

CREATE TABLE gold.daily_sales_summary AS
SELECT
    DATE("Transaction Date") AS date,
    SUM("Total Spent") AS total_revenue,
    COUNT(DISTINCT "Transaction ID") AS total_orders,
    AVG("Total Spent") AS avg_order_value,
    SUM("Quantity") AS total_quantity_sold,
    COUNT(DISTINCT "Customer ID") AS unique_customers
FROM silver.cleaned_retail_sales
GROUP BY DATE("Transaction Date")
ORDER BY date;