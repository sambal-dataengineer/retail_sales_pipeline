DROP TABLE IF EXISTS gold.payment_analysis;

CREATE TABLE gold.payment_analysis AS
SELECT
    "Payment Method" AS payment_method,
    COUNT(DISTINCT "Transaction ID") AS total_transactions,
    SUM("Total Spent") AS total_revenue,
    AVG("Total Spent") AS avg_transaction_value,
    SUM("Quantity") AS total_quantity_sold
FROM silver.cleaned_retail_sales
GROUP BY "Payment Method"
ORDER BY total_revenue DESC;