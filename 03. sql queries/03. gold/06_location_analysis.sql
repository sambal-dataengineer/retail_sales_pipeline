DROP TABLE IF EXISTS gold.location_analysis;

CREATE TABLE gold.location_analysis AS
SELECT
    "Location" AS location,
    COUNT(DISTINCT "Transaction ID") AS total_orders,
    SUM("Quantity") AS total_quantity_sold,
    SUM("Total Spent") AS total_revenue,
    AVG("Total Spent") AS avg_order_value,
    COUNT(DISTINCT "Customer ID") AS unique_customers
FROM silver.cleaned_retail_sales
GROUP BY "Location"
ORDER BY total_revenue DESC;