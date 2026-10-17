# Mamaearth Returns & Growth Intelligence Pipeline

An end-to-end data analytics capstone project that investigates order
returns, revenue reconciliation, customer/product performance, and
monthly revenue trends using SQL, Python/Pandas, visualizations, and a
GenAI-powered business narrative.

## Project Overview

The project is designed around three connected layers:

1.  **SQL relational layer (MySQL)** --- creates the `Mamaearth_Returns` database, defines customer/product/order tables and foreign keys, stages raw order data for type conversion, and answers business questions with joins, aggregates, filters, ranking, and conditional logic.
2.  **Python/Pandas analysis layer** --- cleans the raw data, removes
    duplicate orders, handles missing values, detects quantity outliers,
    evaluates return-rate hypotheses, and generates charts.
3.  **GenAI insight narrator** --- uses verified findings to write a
    Situation--Complication--Resolution (SCR) narrative for business
    stakeholders. The implementation uses CrewAI with Gemini and
    includes a deterministic offline fallback.

The source CSV files are kept unchanged. Cleaning is performed in the
analysis code.

## Business Questions

-   What are the raw order count, revenue, and average order value?
-   How many orders have missing ratings?
-   Which customers have no orders?
-   Which cities have a return rate above 20%?
-   Which customers generate the highest spend?
-   How do order counts and revenue vary by product category?
-   Does Cash on Delivery (COD) have a higher return rate than Card or
    UPI?
-   Does the COD return risk vary by city tier?
-   Are discounts meaningfully associated with returns?
-   How do unusually large quantity orders affect the monthly revenue
    trend?
-   What actions should operations and finance teams consider based on
    the verified findings?

## Key Findings

The analysis is intended to reproduce the following figures from the
supplied capstone dataset:

  Metric                                                                        Result
  --------------------------------------------------- --------------------------------
  Raw orders                                                                       180
  Orders after duplicate removal                                                   175
  Raw revenue                                                               ₹99,860.20
  Cleaned revenue                                                           ₹97,358.30
  Revenue difference due to duplicate orders                                 ₹2,501.90
  COD return rate                                                                44.4%
  Card return rate                                                               14.7%
  UPI return rate                                                                18.9%
  Highest-risk segment                                  COD customers in Tier-2 cities
  Return rate for COD + Tier-2                                                   54.5%
  True peak month after excluding quantity outliers                         March 2026
  Corrected March revenue                                                   ₹20,318.90

The raw January revenue appears unusually high because two
large-quantity orders fall in January. After flagging those orders as
quantity outliers and excluding them for the corrected time-series view,
March is the actual peak month. The outlier orders are flagged for
analysis rather than deleted from the cleaned order dataset.

## Repository Structure

Organize the GitHub repository in the following structure. Keep the
source CSV files in `data/` and commit the SQL, Python, JSON, chart, and
README files used for the project.

``` text
mamaearth-returns-growth-intelligence/
├── README.md
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    ├── generate_narrative.py
    └── sample_output.txt
```

If your current solution is still in a Google Colab notebook, you can
also commit the notebook (for example, `mamaearth.ipynb`) and then split
the code into the files above to match the required submission
structure. Make sure the file paths in the scripts match the repository
structure.

## Tech Stack

-   Python
-   Pandas and NumPy
-   Matplotlib and Seaborn
-   MySQL / SQL
-   Google GenAI SDK
-   CrewAI
-   JSON for structured findings
-   Google Colab for notebook-based development

## Setup

### 1. Clone the repository

``` bash
git clone <your-github-repository-url>
cd mamaearth-returns-growth-intelligence
```

### 2. Create and activate a virtual environment (optional but recommended)

``` bash
python -m venv .venv
```

Windows:

``` bash
.venv\Scripts\activate
```

macOS/Linux:

``` bash
source .venv/bin/activate
```

### 3. Install Python dependencies

``` bash
pip install pandas numpy matplotlib seaborn google-genai crewai
```

Use a compatible Python version and the package versions that work with
your code. If you run the notebook in Google Colab, install any missing
packages in a notebook cell instead.

## Execution Order

Run the layers in this order so each stage can be checked independently.

### Part 1 --- SQL database design, data loading, and reporting

The SQL code is written for **MySQL** (it uses `CREATE DATABASE`, `USE`,
`STR_TO_DATE`, and `CAST(... AS UNSIGNED)`). It is not directly compatible
with the SQLite CLI commands shown in many generic tutorials, so use a
MySQL client such as MySQL Workbench or the MySQL command-line client.

#### Database schema

- **`customers`** — one row per customer, with `customer_id` as the
  primary key, name, city, city tier, signup date, and acquisition source.
- **`products`** — one row per product, with `product_id` as the primary
  key, product name, category, and price.
- **`orders`** — order-level records with order date, quantity, discount,
  payment method, rating, and return flag. `customer_id` and `product_id`
  are foreign keys to the customer and product tables.
- **`orders_staging`** — a temporary/raw-import layer in which order
  values are stored as text so blank values and date/number conversions
  can be handled while loading into `orders`.

#### SQL queries and skills demonstrated

| Query / analysis | What it demonstrates |
|---|---|
| Table row counts and `SELECT *` checks | Basic data validation after loading |
| `STR_TO_DATE`, `CAST`, `NULLIF`, `UPPER` during staging-to-orders insert | Date/number conversion, blank-to-`NULL` handling, and payment-method standardization |
| Order count, total revenue, and average order value | `COUNT`, `SUM`, `AVG`, joins between orders and products, and discount-adjusted revenue |
| Rated vs. unrated orders | Difference between `COUNT(*)` and `COUNT(rating)` |
| Customers with no orders | `LEFT JOIN`, `GROUP BY`, and `HAVING COUNT(...) = 0` |
| City return rate above 20% | Three-table relationships where needed, aggregation, `HAVING`, calculated metrics, and descending sort |
| Top five customers by spend | Multi-table `JOIN`, `COALESCE` for missing discounts, `ROUND`, `GROUP BY`, and `ORDER BY` with `LIMIT` |
| Revenue by product category | Three-table joins and category-level aggregation |
| Customer names beginning with “A” | `LIKE` pattern matching |
| Distinct acquisition sources | `DISTINCT` |
| Customer loyalty tier counts | `CASE` expressions and grouping by a derived label (`Gold` for Tier 1, otherwise `Silver`) |

These queries support business questions about sales performance, order
quality, customer activity, product-category revenue, city-level return
risk, and customer spending. The code provided does not include result
outputs for every query, so the README describes the analyses rather than
inventing additional SQL result figures.

#### How to run the SQL

1. Open MySQL Workbench or connect using the MySQL CLI.
2. Run the database and table creation statements.
3. Import the source data into `customers`, `products`, and
   `orders_staging` (the supplied snippet defines the staging table but
   does not include the complete import commands).
4. Run the staging-to-`orders` insert after checking the column names and
   data types.
5. Run the reporting queries and verify their outputs.

**Before running the supplied SQL, fix/check these details:**

- In the staging insert, `STR_TO_DATE(orde r_date, '%Y-%m-%d')` contains
  a typo. It should reference the actual staging column, likely
  `order_date`.
- Ensure the date format passed to `STR_TO_DATE` matches the values in
  the source file. If dates are stored as `DD-MM-YYYY`, use the matching
  format string (for example, `'%d-%m-%Y'`) instead of `'%Y-%m-%d'`.
- `NULLIF(discount_pct, '')` and `NULLIF(rating, '')` produce `NULL` for
  blank values. In the order-total query, a missing `discount_pct` can
  make the arithmetic expression `NULL`; use `COALESCE(o.discount_pct,
  0)` there if the intended business rule is to treat a missing discount
  as zero.
- The final `CASE` query groups Tier 1 as `Gold` and every other tier as
  `Silver`; it does not actually run an `ALTER TABLE` or `UPDATE`, despite
  the original comment mentioning those operations.
- Use `DROP TABLE IF EXISTS` carefully: it deletes the existing table
  before recreating it. Do not run it against a database whose data you
  need to preserve.

For a clean repository, split the SQL into files such as
`sql/schema.sql` (database and table definitions), `sql/load_data.sql`
(staging/import and conversion), and `sql/reports.sql` (business queries).
The code shared so far is a single SQL script/snippet; those separate files
are a suggested organization, not confirmed existing files.

### Part 2 --- Python data cleaning, EDA, and charts

Run the cleaning and analysis script first:

``` bash
python analysis/clean_and_eda.py
```

Then generate the visualizations:

``` bash
python analysis/visualize.py
```

The analysis should:

-   Load the original CSV files.
-   Standardize payment methods to `COD`, `CARD`, and `UPI`.
-   Detect and remove the five duplicate orders using the natural key,
    not `order_id`.
-   Fill missing discounts with `0` and missing ratings with the median.
-   Merge orders with product and customer details.
-   Reconcile cleaned revenue against raw revenue.
-   Flag quantity outliers using the IQR method without deleting them
    from the cleaned dataset.
-   Compare return rates by payment method and by payment method/city
    tier.
-   Calculate and label pairwise correlations.
-   Compare monthly revenue with and without the flagged quantity
    outliers.
-   Save `return_rate_by_payment.png` and `monthly_revenue_trend.png`
    under `visualizations/`.
-   Write the computed findings to `narrator/findings.json` so the
    narrative layer uses the analysis output rather than manually
    re-entered numbers.

**Important:** The source notebook currently uses filenames such as
`orders.csv`, `products.csv`, and `customers.csv` in the working
directory. If you move the code into `analysis/clean_and_eda.py`, update
the paths to `data/orders.csv`, `data/products.csv`, and
`data/customers.csv` (or use paths resolved relative to the project
root).

### Part 3 --- GenAI-powered SCR narrative

The narrator should read `narrator/findings.json`, generate the
narrative, and save the output to `narrator/sample_output.txt` for
review and reproducibility.

#### Option A: Use Gemini through CrewAI

Create a free Gemini API key through Google AI Studio, then set it as an
environment variable. Do not commit the API key to GitHub.

Windows PowerShell:

``` powershell
$env:GEMINI_API_KEY="your-api-key"
python narrator/generate_narrative.py
```

macOS/Linux:

``` bash
export GEMINI_API_KEY="your-api-key"
python narrator/generate_narrative.py
```

If using Google Colab Secrets, store the key in Colab Secrets (for
example, `GEMINI_API_KEY`) and load it into the environment:

``` python
import os
from google.colab import userdata

os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")
```

If your secret is stored under a different name, use that exact name
inside `userdata.get(...)`. The environment variable used by the
application should consistently be `GEMINI_API_KEY`.

The online generation function should use deterministic settings for
factual reporting (`temperature=0.0`), an explicit output-token limit, a
request timeout, and exception handling.

#### Option B: Run without an API key

The offline fallback should run when `GEMINI_API_KEY` is missing or when
the Gemini/CrewAI call fails. It should create the same three SCR
sections using a deterministic template built from `findings.json`,
without a network request.

``` bash
python narrator/generate_narrative.py
```

No API key should be required for this fallback. Confirm that the
returned narrative includes the required verified figures and that the
program returns a structured success/error result instead of exposing an
unhandled exception.

## Validation Checklist

Before submitting the repository, confirm the following:

-   [ ] The three CSV files are committed unchanged in `data/`.
-   [ ] SQL scripts can be rerun and reproduce the expected row counts
    and report results.
-   [ ] `orders.shape` prints `(180, 9)` before cleaning.
-   [ ] Payment-method normalization produces `CARD: 70`, `UPI: 55`, and
    `COD: 55`.
-   [ ] Exactly five duplicates are removed: `O0176`--`O0180`; the
    cleaned shape is `(175, 9)`.
-   [ ] Missing `discount_pct` values are filled with `0`; missing
    ratings are filled with the median (`3.0`).
-   [ ] Cleaned revenue is ₹97,358.30 and the duplicate reconciliation
    difference is ₹2,501.90.
-   [ ] The quantity outliers are flagged as `O0011` (25 units) and
    `O0098` (30 units).
-   [ ] COD, Card, and UPI return rates are 44.4%, 14.7%, and 18.9%.
-   [ ] COD + Tier-2 cities are identified as the highest-risk segment
    at 54.5%.
-   [ ] All six pairwise correlations are labeled using the required
    correlation-strength bands.
-   [ ] The outlier-corrected revenue series identifies March 2026 as
    the peak at ₹20,318.90.
-   [ ] Both charts are regenerated by `analysis/visualize.py`.
-   [ ] `narrator/findings.json` is generated from computed analysis
    values.
-   [ ] The online and offline narrative paths are tested.
-   [ ] The numeric checker passes for cleaned revenue, COD return rate,
    COD + Tier-2 return rate, duplicate delta, and March peak revenue.
-   [ ] `narrator/sample_output.txt` contains a tested narrative sample.
-   [ ] No API key, token, or other secret is committed to the
    repository.

## Business Recommendations

Based on the calculated results, the narrative can recommend
prioritizing COD return controls in Tier-2 cities, investigating reasons
behind COD returns, preventing duplicate order submissions, and using
outlier-corrected monthly revenue for planning. These are analytical
recommendations to investigate, not proof of the underlying causes of
returns.

## Notes

-   This project uses a supplied capstone dataset for analysis and
    learning; the figures describe that dataset, not necessarily
    Mamaearth's real operational performance.
-   Keep raw CSVs unchanged and perform data cleaning in code.
-   Do not manually hardcode findings in place of computing them from
    the data.
-   Ensure the README commands match the final files and folder paths in
    the published repository.

## Author

**SURAJ GUPTA**\
Data Analytics \| SQL \| Python \| Pandas \| Data Visualization \| GenAI

------------------------------------------------------------------------

If you found this project useful, feel free to star the repository.
#
