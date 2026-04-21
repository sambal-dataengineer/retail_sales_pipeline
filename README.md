# 🛒 Retail Sales Data Pipeline

> An end-to-end data engineering project — from raw messy CSV to a multi-layer PostgreSQL pipeline, 5-page Power BI dashboard, and machine learning revenue forecasting.

---

## 🏅 Badges

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Project Overview

This project builds a complete data engineering pipeline for a retail business. Starting from a single dirty CSV file, the data is ingested, cleaned, transformed, and loaded into a multi-layer PostgreSQL warehouse (Bronze → Silver → Gold). A 5-page Power BI dashboard provides business intelligence insights across categories, time, payments, locations, and customers — while a machine learning layer forecasts future sales revenue using three regression models.

This is **Project 2** in my data engineering portfolio, a step up from Project 1 (Cafe Sales Pipeline), introducing a wider dataset, 9 Gold tables, a 5-page dashboard, and an improved ML pipeline.

---

## 🏗️ Pipeline Architecture

```text
Raw CSV Files
     │
     ▼
Bronze Layer
(raw ingestion into PostgreSQL)
     │
     ▼
Silver Layer
(cleaning and transformation using pandas)
     │
     ▼
Gold Layer
(9 analytics-ready aggregation tables in PostgreSQL)
     │
     ├──────────────► Power BI Dashboard (5 pages)
     │
     └──────────────► Machine Learning Models
                             │
                             ▼
                    Future Revenue Predictions
```

---

## 🛠️ Tech Stack

| Category         | Tools / Libraries             |
| ---------------- | ----------------------------- |
| Language         | Python 3.10+                  |
| Data Processing  | pandas, numpy                 |
| Machine Learning | scikit-learn, xgboost, joblib |
| Database ORM     | SQLAlchemy, psycopg2-binary   |
| Visualisation    | matplotlib, seaborn           |
| Database         | PostgreSQL (pgAdmin)          |
| BI Dashboard     | Power BI Desktop              |
| Notebook         | Jupyter Notebook / VS Code    |
| Version Control  | Git + GitHub                  |

---

## 📁 Project Structure

```
retail_sales_pipeline/
│
├── data/
│   ├── retail_store_sales.csv             # Original raw dataset
|   ├── Test data.csv                      # Testing data
│   └── cleaned_retail_sales.csv           # Cleaned version (post-Silver layer)
│
├── scripts/
│   ├── bronze_ingestion.py                 # Loads raw CSV → PostgreSQL Bronze
|   ├── inspection.ipynb                    # Standalone Jupyter notebook that inspects the dataset
|   ├── retail_store_sales_data_cleaning.py # Standalone dataset cleaning script
│   └── silver_transformation.py            # Cleans Bronze → Silver layer
│
├── sql/
│   ├── bronze/                            # SQL for Bronze layer setup
│   ├── silver/                            # SQL for Silver layer setup
│   └── gold/                              # SQL for all 9 Gold layer tables
│
├── dashboard/
│   └── retail_sales_dashboard.pbix        # Power BI dashboard file
│
├── notebooks/
│   └── ml_pipeline.ipynb                  # ML model training and evaluation
│
├── models/
│   ├── retail_sales_model.joblib          # Saved best model
│   ├── retail_scaler.joblib               # Saved StandardScaler
│   └── feature_list.txt                   # Features used in training
│
├── outputs/
│   └── model_comparison.csv               # MAE / RMSE / R² for all 3 models
│
├── screenshots/
│   ├── page1_overview.png
│   ├── page2_category_product.png
│   ├── page3_time_trends.png
│   ├── page4_payment_location.png
│   └── page5_customer_insights.png
│
├── README.md                              # ← You are here
├── requirements.txt                       # Python dependencies
├── .gitignore                             # Files excluded from Git
├── setup_instructions.txt                # How to reproduce this project
├── project_summary.txt                   # Plain-text project summary
└── LICENSE                               # MIT License
```

---

## 🔄 Pipeline Layers — Detailed

### Layer 1 — Bronze (Raw Ingestion)

**Script:** `scripts/bronze_ingestion.py`
**Output table:** `bronze.raw_retail_sales`

Loads the raw CSV file (`retail_store_sales.csv`) into PostgreSQL as-is. No cleaning is performed — the Bronze layer preserves the original data in its messy state, acting as a historical record. Uses `pandas` to read the CSV and `SQLAlchemy` + `psycopg2` to write to PostgreSQL.

---

### Layer 2 — Silver (Cleaning & Transformation)

**Script:** `scripts/silver_transformation.py`
**Input table:** `bronze.raw_retail_sales`
**Output table:** `silver.cleaned_retail_sales`

Pulls raw data from Bronze and applies a structured, multi-step cleaning pipeline using `pandas` and `numpy`:

**1. Profiling & Quality Flags**
Before any changes, the raw data is profiled (shape, dtypes, missing values, duplicates, full describe). Temporary boolean flag columns are created to track which rows had missing values in `Item`, `Price Per Unit`, `Quantity`, `Total Spent`, and `Discount Applied` — used for auditability during transformation, then dropped before loading.

**2. Text Standardisation**
All string columns (`Transaction ID`, `Customer ID`, `Category`, `Item`, `Payment Method`, `Location`) are cast to the `string` dtype and stripped of leading/trailing whitespace.

**3. Date Conversion**
`Transaction Date` is parsed using `pd.to_datetime()` with `format='mixed'` and `dayfirst=True` to handle inconsistent date formats. Unparseable dates are coerced to `NaT`.

**4. Numerical Type Conversion**
`Price Per Unit`, `Quantity`, and `Total Spent` are converted to numeric using `pd.to_numeric(..., errors='coerce')`, which turns any non-numeric strings into `NaN`.

**5. Discount Applied Cleaning**
Boolean values (`True`/`False`) and their string equivalents are mapped to `"Yes"` / `"No"`. Remaining nulls (where discount was not recorded) are filled with `"Not Applicable"`.

**6. Smart Numerical Reconstruction**
Missing values across the three core numeric columns are recovered using the mathematical relationship `Total Spent = Price Per Unit × Quantity`:

- Missing `Price Per Unit` → calculated from `Total Spent / Quantity`
- Missing `Quantity` → calculated from `Total Spent / Price Per Unit`, only accepted if the result is a whole number (using `np.isclose` to check divisibility)
- Missing `Total Spent` → calculated from `Price Per Unit × Quantity`

**7. Item Reconstruction**
Missing `Item` names are recovered using a lookup built from existing clean rows, matching on `(Category, Price Per Unit)` pairs — restoring item names wherever the combination is unambiguous.

**8. Dropping Unusable Rows**
Rows where `Price Per Unit`, `Quantity`, `Total Spent`, or `Transaction Date` remain null after all reconstruction attempts are dropped. These are rows where recovery is not possible without introducing assumptions.

**9. Type Finalisation & Validation**
`Quantity` is rounded and cast to `Int64`. A final validation pass uses `np.isclose()` to check that `Price Per Unit × Quantity ≈ Total Spent` across all rows, flagging any remaining mismatches.

**10. Load to Silver**
Flag columns are dropped, the cleaned DataFrame is loaded into `silver.cleaned_retail_sales` using `to_sql(..., if_exists='replace')`, and the row count is verified with a post-load query.

---

### Layer 3 — Gold (Analytics-Ready Tables)

**SQL files:** `sql/gold/`
**Input:** `silver.cleaned_retail_sales`
**Output:** 9 Gold aggregation tables

Transforms cleaned Silver data into purpose-built analytical tables. Each table is designed to answer specific business questions and power specific dashboard visuals or ML features. All tables are built using `CREATE TABLE AS SELECT` and can be refreshed by re-running the SQL files in order via `run_all_gold.sql`.

---

### Layer 4 — Power BI Dashboard

**File:** `dashboard/retail_sales_dashboard.pbix`
**Connected to:** PostgreSQL Gold schema

A 5-page interactive business intelligence dashboard:

| Page | Title                        | Key Visuals                                             |
| ---- | ---------------------------- | ------------------------------------------------------- |
| 1    | Executive Overview           | KPI cards, total revenue, transactions, AOV             |
| 2    | Category & Product Analysis  | Revenue by category, top products bar chart             |
| 3    | Time Trends & Growth         | Monthly revenue line chart, MoM growth %                |
| 4    | Payment, Location & Discount | Payment method split, location revenue, discount impact |
| 5    | Customer Insights            | Spend distribution, top customers, purchase frequency   |

---

### Layer 5 — Machine Learning

**Notebook:** `notebooks/ml_pipeline.ipynb`
**Input:** `gold.ml_features`
**Output:** Saved model files + `outputs/model_comparison.csv`

Three regression models were trained to predict daily sales revenue:

- **Linear Regression** — baseline model
- **Random Forest Regressor** — ensemble tree model
- **XGBoost Regressor** — gradient boosting model

Features used: daily order count, daily quantity sold, average order value, average price per unit, unique customers, unique items sold, unique categories sold, online/in-store order ratios, discount ratios, date components (year, month, day, day_of_week), weekend flag, lag features (lag_1, lag_7), and 7-day rolling average.

The best-performing model was saved as `retail_sales_model.joblib` along with the fitted scaler (`retail_scaler.joblib`) for consistent inference on new data.

---

## 🥇 Gold Layer Tables

| Table                      | Description                     | Key Columns                                                                                                                                                                                                                                                                                                                                            |
| -------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `gold.daily_sales_summary` | Daily business summary          | date, total_revenue, total_orders, avg_order_value, total_quantity_sold, unique_customers                                                                                                                                                                                                                                                              |
| `gold.product_performance` | Product-level KPIs              | item, category, total_quantity_sold, total_revenue, avg_unit_price, transaction_count, unique_customers                                                                                                                                                                                                                                                |
| `gold.monthly_trends`      | Month-over-month analysis       | year, month_number, month_name, revenue, order_count, quantity_sold, unique_customers, prev_month_revenue, growth_pct                                                                                                                                                                                                                                  |
| `gold.payment_analysis`    | Payment method breakdown        | payment_method, total_transactions, total_revenue, avg_transaction_value, total_quantity_sold                                                                                                                                                                                                                                                          |
| `gold.category_analysis`   | Revenue and orders by category  | category, total_orders, total_quantity_sold, total_revenue, avg_order_value, unique_items                                                                                                                                                                                                                                                              |
| `gold.location_analysis`   | Revenue by store location       | location, total_orders, total_quantity_sold, total_revenue, avg_order_value, unique_customers                                                                                                                                                                                                                                                          |
| `gold.discount_analysis`   | Impact of discounts on sales    | discount_applied, total_orders, total_quantity_sold, total_revenue, avg_order_value                                                                                                                                                                                                                                                                    |
| `gold.customer_analysis`   | Customer-level aggregation      | customer_id, total_orders, total_quantity_sold, total_revenue, avg_order_value, first_purchase_date, last_purchase_date                                                                                                                                                                                                                                |
| `gold.ml_features`         | Feature-engineered table for ML | date, daily_revenue, daily_order_count, daily_quantity_sold, avg_order_value, avg_price_per_unit, unique_customers, unique_items_sold, unique_categories_sold, online_order_ratio, instore_order_ratio, discount_yes_ratio, discount_no_ratio, discount_not_applicable_ratio, year, month, day, day_of_week, weekend_flag, lag_1, lag_7, rolling_avg_7 |

---

## 📸 Dashboard Preview

### Page 1 — Executive Overview

![Executive Overview](screenshots/Page1_Executive_Overview.png)

### Page 2 — Category & Product Analysis

![Category & Product Analysis](screenshots/Page2_Product_&_Category.png)

### Page 3 — Time Trends & Growth

![Time Trends & Growth](screenshots/Page3_Time_Trends.png)

### Page 4 — Payment, Location & Discount Insights

![Payment, Location & Discount Insights](screenshots/Page4_Payment_Location_&_Discount.png)

### Page 5 — Customer Insights

![Customer Insights](screenshots/Page5_Customer_Analysis.png)

---

## 🤖 Machine Learning Results

Three regression models were trained to predict **daily sales revenue** using features from `gold.ml_features`.

| Model                | MAE   | RMSE  | R² Score |
| -------------------- | ----- | ----- | -------- |
| Linear Regression    | 62.34 | 88.05 | -1.006   |
| Random Forest        | 20.22 | 34.95 | 0.9606   |
| **XGBoost** _(Best)_ | 16.47 | 26.94 | 0.9963   |

> 📝 Fill in your actual values from `outputs/model_comparison.csv` after running the notebook.

**Best Model:** XGBoost Regressor
**Saved to:** `models/retail_sales_model.joblib`

---

## 🚀 How to Run This Project

### Prerequisites

Before you begin, make sure you have these installed:

- Python 3.10+ → [python.org](https://www.python.org/downloads/)
- PostgreSQL → [postgresql.org](https://www.postgresql.org/download/)
- pgAdmin 4 → [pgadmin.org](https://www.pgadmin.org/download/)
- Power BI Desktop (Windows only) → [Microsoft Store](https://powerbi.microsoft.com/desktop/)
- Git → [git-scm.com](https://git-scm.com/)

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/sambal-dataengineer/retail_sales_pipeline.git
cd retail_sales_pipeline
```

### Step 2 — Set up a Python virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### Step 3 — Install all Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up PostgreSQL

1. Open pgAdmin and connect to your local PostgreSQL server
2. Create a new database called `retail_sales_project`
3. Create three schemas: `bronze`, `silver`, `gold`

```sql
CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold;
```

4. Update the connection string in each Python script to match your credentials:

```python
engine = create_engine("postgresql://postgres:YOUR_PASSWORD@localhost:5432/retail_sales_project")
```

### Step 5 — Run the pipeline in order

```bash
# Layer 1: Ingest raw CSV into Bronze
python scripts/bronze_ingestion.py

# Layer 2: Clean data into Silver
python scripts/silver_transformation.py
```

### Step 6 — Run Gold layer SQL

Open pgAdmin, connect to `retail_sales_project`, and run the SQL files in `sql/gold/` in order — or run them all at once using:

```bash
psql -U postgres -d retail_sales_project -f sql/gold/run_all_gold.sql
```

### Step 7 — Run the ML notebook

Open and run `notebooks/ml_pipeline.ipynb` cell by cell in Jupyter or VS Code.

### Step 8 — Open the dashboard

1. Open `dashboard/retail_sales_dashboard.pbix` in Power BI Desktop
2. Update the data source to point to your local PostgreSQL instance
3. Refresh the data

---

## 🔮 Future Improvements

1. **Apache Airflow** — Schedule and orchestrate the pipeline with DAGs instead of running scripts manually
2. **Docker** — Containerise the entire stack (PostgreSQL + Python environment) for one-command setup
3. **Streamlit App** — Build an interactive web app for ML predictions, accessible without Power BI
4. **dbt (data build tool)** — Replace raw SQL Gold layer with dbt models for testing, documentation, and version control
5. **CI/CD Pipeline** — Add GitHub Actions to run data quality checks automatically on every push

---

## 👤 Author

**Sambal Agarwal**
Aspiring Data Engineer | Data Engineering • Analytics • Machine Learning

- 🔗 GitHub: [github.com/sambal-dataengineer](https://github.com/sambal-dataengineer)
- 💼 LinkedIn: [linkedin.com/in/sambal-agarwal-843a43339](https://www.linkedin.com/in/sambal-agarwal-843a43339/)
- 📧 Email: sambalagarwal@gmail.com

> 🚀 Open to internships and entry-level roles in Data Engineering / Analytics

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
