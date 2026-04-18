-- Check all gold tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'gold'
ORDER BY table_name;

-- Preview each table
SELECT * FROM gold.daily_sales_summary LIMIT 10;
SELECT * FROM gold.product_performance LIMIT 10;
SELECT * FROM gold.monthly_trends LIMIT 10;
SELECT * FROM gold.payment_analysis LIMIT 10;
SELECT * FROM gold.category_analysis LIMIT 10;
SELECT * FROM gold.location_analysis LIMIT 10;
SELECT * FROM gold.discount_analysis LIMIT 10;
SELECT * FROM gold.customer_analysis LIMIT 10;
SELECT * FROM gold.ml_features LIMIT 10;

-- Row counts
SELECT 'daily_sales_summary' AS table_name, COUNT(*) AS row_count FROM gold.daily_sales_summary
UNION ALL
SELECT 'product_performance', COUNT(*) FROM gold.product_performance
UNION ALL
SELECT 'monthly_trends', COUNT(*) FROM gold.monthly_trends
UNION ALL
SELECT 'payment_analysis', COUNT(*) FROM gold.payment_analysis
UNION ALL
SELECT 'category_analysis', COUNT(*) FROM gold.category_analysis
UNION ALL
SELECT 'location_analysis', COUNT(*) FROM gold.location_analysis
UNION ALL
SELECT 'discount_analysis', COUNT(*) FROM gold.discount_analysis
UNION ALL
SELECT 'customer_analysis', COUNT(*) FROM gold.customer_analysis
UNION ALL
SELECT 'ml_features', COUNT(*) FROM gold.ml_features;