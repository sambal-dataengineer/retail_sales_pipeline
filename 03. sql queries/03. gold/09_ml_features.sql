DROP TABLE IF EXISTS gold.ml_features;

CREATE TABLE gold.ml_features AS
WITH daily_base AS (
    SELECT
        DATE("Transaction Date") AS date,
        SUM("Total Spent") AS daily_revenue,
        COUNT(DISTINCT "Transaction ID") AS daily_order_count,
        SUM("Quantity") AS daily_quantity_sold,
        AVG("Total Spent") AS avg_order_value,
        AVG("Price Per Unit") AS avg_price_per_unit,
        COUNT(DISTINCT "Customer ID") AS unique_customers,
        COUNT(DISTINCT "Item") AS unique_items_sold,
        COUNT(DISTINCT "Category") AS unique_categories_sold,
        SUM(CASE WHEN "Location" = 'Online' THEN 1 ELSE 0 END)::float
            / NULLIF(COUNT(*), 0) AS online_order_ratio,
        SUM(CASE WHEN "Location" = 'In-store' THEN 1 ELSE 0 END)::float
            / NULLIF(COUNT(*), 0) AS instore_order_ratio,
        SUM(CASE WHEN "Discount Applied" = 'Yes' THEN 1 ELSE 0 END)::float
            / NULLIF(COUNT(*), 0) AS discount_yes_ratio,
        SUM(CASE WHEN "Discount Applied" = 'No' THEN 1 ELSE 0 END)::float
            / NULLIF(COUNT(*), 0) AS discount_no_ratio,
        SUM(CASE WHEN "Discount Applied" = 'Not Applicable' THEN 1 ELSE 0 END)::float
            / NULLIF(COUNT(*), 0) AS discount_not_applicable_ratio
    FROM silver.cleaned_retail_sales
    GROUP BY DATE("Transaction Date")
)
SELECT
    date,
    daily_revenue,
    daily_order_count,
    daily_quantity_sold,
    avg_order_value,
    avg_price_per_unit,
    unique_customers,
    unique_items_sold,
    unique_categories_sold,
    online_order_ratio,
    instore_order_ratio,
    discount_yes_ratio,
    discount_no_ratio,
    discount_not_applicable_ratio,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    EXTRACT(DOW FROM date) AS day_of_week,
    CASE
        WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN 1
        ELSE 0
    END AS weekend_flag,
    LAG(daily_revenue, 1) OVER (ORDER BY date) AS lag_1,
    LAG(daily_revenue, 7) OVER (ORDER BY date) AS lag_7,
    ROUND(
        AVG(daily_revenue) OVER (
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::numeric,
        2
    ) AS rolling_avg_7
FROM daily_base
ORDER BY date;