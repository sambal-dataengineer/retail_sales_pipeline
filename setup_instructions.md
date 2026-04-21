# Setup Instructions — Cafe Sales Data Pipeline

This guide explains how to install everything you need and reproduce the
entire pipeline from scratch on a new machine.

---

## Step 1 — Install Python

1. Go to: https://www.python.org/downloads/
2. Download Python 3.10 or higher
3. During installation on Windows, tick the box that says **"Add Python to PATH"**
4. Verify the install worked by opening a terminal and running: python --version

You should see something like: `Python 3.14.2`

---

## Step 2 — Install PostgreSQL

1. Go to: https://www.postgresql.org/download/
2. Download and install PostgreSQL 15 for your operating system
3. During setup, set a password for the default `postgres` user — remember this password
4. pgAdmin 4 is included with the PostgreSQL installer — make sure it is selected

---

## Step 3 — Install Power BI Desktop (Windows only)

1. Go to: https://powerbi.microsoft.com/desktop/
2. Click "Download free" and install from the Microsoft Store
   OR download the standalone .exe installer
3. Power BI Desktop is free. You do not need a paid account to open .pbix files.

---

## Step 4 — Clone this repository

If you have Git installed:

```bash
git clone https://github.com/sambal-dataengineer/retail_sales_pipeline
cd retail_sales_pipeline
```

Or download as a ZIP file from GitHub and extract it.

---

## Step 5 — Set up a Python virtual environment

A virtual environment keeps this project's packages separate from your system Python.

```bash
# Navigate into the project folder
cd retail_sales_pipeline

# Create the virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate

# Your terminal prompt will now show (venv)
```

---

## Step 6 — Install all Python dependencies

```bash
pip install -r requirements.txt
```

This installs pandas, numpy, scikit-learn, xgboost, SQLAlchemy, psycopg2, and all other libraries used in the project.

---

## Step 7 — Set up the PostgreSQL database

Open pgAdmin 4 and:

1. Connect to your local PostgreSQL server (right-click → Connect)
2. Right-click "Databases" → Create → Database → name it `retail_sales`
3. Open the Query Tool on `retail_sales` and run:

```sql
CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold;
```

---

## Step 8 — Configure database credentials

In each Python script, find the `create_engine` line and update it with your credentials:

```python
# Replace with your actual PostgreSQL password
engine = create_engine("postgresql://postgres:YOUR_PASSWORD@localhost:5432/cafe_sales")
```

---

## Step 9 — Run the pipeline

Run these in order:

```bash
# 1. Bronze layer — ingest raw CSV
python scripts/bronze_ingestion.py

# 2. Silver layer — clean and transform
python scripts/silver_transformation.py
```

Then in pgAdmin, run the SQL files inside `sql/gold/` to create the Gold layer tables.

---

## Step 10 — Run the ML notebook

1. Open VS Code or Jupyter Notebook
2. Open `notebooks/ml_pipeline.ipynb`
3. Run all cells from top to bottom
4. Predictions are saved to `gold.sales_predictions` in PostgreSQL

---

## Step 11 — Open the Power BI Dashboard

1. Open Power BI Desktop
2. File → Open → browse to `dashboard/cafe_sales_dashboard.pbix`
3. If prompted, update the data source connection to your local PostgreSQL
4. Click "Refresh" on the Home tab to load your data
