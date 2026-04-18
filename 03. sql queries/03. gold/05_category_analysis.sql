DROP TABLE IF EXISTS gold.category_analysis;

CREATE TABLE gold.category_analysis AS
SELECT
    "Category" AS category,
    COUNT(DISTINCT "Transaction ID") AS total_orders,
    SUM("Quantity") AS total_quantity_sold,
    SUM("Total Spent") AS total_revenue,
    AVG("Total Spent") AS avg_order_value,
    COUNT(DISTINCT "Item") AS unique_items
FROM silver.cleaned_retail_sales
GROUP BY "Category"
ORDER BY total_revenue DESC;