DROP TABLE IF EXISTS gold.monthly_trends;

CREATE TABLE gold.monthly_trends AS
WITH monthly_data AS (
    SELECT
        EXTRACT(YEAR FROM "Transaction Date") AS year,
        EXTRACT(MONTH FROM "Transaction Date") AS month_number,
        TO_CHAR(DATE_TRUNC('month', "Transaction Date"), 'Mon') AS month_name,
        SUM("Total Spent") AS revenue,
        COUNT(DISTINCT "Transaction ID") AS order_count,
        SUM("Quantity") AS quantity_sold,
        COUNT(DISTINCT "Customer ID") AS unique_customers
    FROM silver.cleaned_retail_sales
    GROUP BY
        EXTRACT(YEAR FROM "Transaction Date"),
        EXTRACT(MONTH FROM "Transaction Date"),
        DATE_TRUNC('month', "Transaction Date")
)
SELECT
    year,
    month_number,
    month_name,
    revenue,
    order_count,
    quantity_sold,
    unique_customers,
    LAG(revenue) OVER (ORDER BY year, month_number) AS prev_month_revenue,
    ROUND(
        (
            (
                revenue - LAG(revenue) OVER (ORDER BY year, month_number)
            ) / NULLIF(LAG(revenue) OVER (ORDER BY year, month_number), 0)
        )::numeric * 100,
        2
    ) AS growth_pct
FROM monthly_data
ORDER BY year, month_number;