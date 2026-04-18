DROP TABLE IF EXISTS gold.discount_analysis;

CREATE TABLE gold.discount_analysis AS
SELECT
    "Discount Applied" AS discount_applied,
    COUNT(DISTINCT "Transaction ID") AS total_orders,
    SUM("Quantity") AS total_quantity_sold,
    SUM("Total Spent") AS total_revenue,
    AVG("Total Spent") AS avg_order_value
FROM silver.cleaned_retail_sales
GROUP BY "Discount Applied"
ORDER BY total_revenue DESC;