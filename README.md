# Superstore Sales Seasonality Analysis

**Goal** : Identify when revenue starts coming in, which categories contribute most to revenue fluctuations, and how to address the four month dead zone.

**Headline** : Three months (Sep, Nov, Dec) generate **43% of annual revenue** , mainly due to higher order volumes rather than larger purchases. While Jan to Apr generates only **21.5% of annual revenue**, despite covering one third of the year, leaving approximately **$67K a year** on the table.

![Monthly revenue](visuals/01_monthly_revenue.png)

---

## Three key findings

**1. Revenue is heavily concentrated in three months, and this pattern has remained consistent for four years.**

Sep, Nov, Dec contribute to **43.0% of annual revenue** (95% CI: 39.7–46.2%), significantly higher than the 25.0% expected if revenue were evenly distributed throughout the year. Nov alone generates **$350K**, nearly **5.9× February's $59K**. The trends appears every year, although the peak share has fallen from 47.5% in 2015 to 39.8% in 2018.

**2. Peak revenue is driven by more customers, not higher spending per order.**

During a typical peak month, **703 orders** were placed across four years, compared to **312 orders during off peak months**, showing a **2.3× increase**. Sep also records **454 active customers** compared to just  **145 active customers in February**. However, the median order value remains **$150.07 during peak vs $152.93 during off peak**, with no statistically significant difference (Mann Whitney U test, p = 0.67, n = 2,110 / 2,812). The average lines per order are also similar (1.98 vs 2.00). This indicates that revenue increases mainly because more customers are purchasing, rather than because each customer is spending more.

![Traffic vs basket](visuals/03_traffic_vs_basket.png)

**3. Furniture is the most seasonal category and the one worth phasing.**

Furniture swings from a **0.26 index in Feb to 2.00 in Dec** , a 1.74 point difference, compared to 1.37 for Office Supplies. Chairs (48% of annual revenue during peak) and Bookcases (50%) show the greatest seasonal concentration. Meanwhile, Copiers (28%) and Supplies (26%) perform relatively better during slower months, making them valuable categories for maintaining sales during the dead zone.

![Season x Category](visuals/02_season_x_category.png)

---

## Bonus finding: Revenue has two seasonal peaks, but the dip between them is closing.

Revenue follows two main peaks: **Sep (13.3% of the year)** and **Nov to Dec (29.7%)**, separated by an October dip 34% below September.
However, the dip is closing. In 2015 to 2016, October was 51–61% below September, compared to only 10–14% lower in 2017 to 2018, so the year is turning into one long season. However, the exact reason for this remains unclear because the dataset does not include customers' reasons for purchasing.

![Two peaks](visuals/05_two_peaks.png)
![Peaks merging](visuals/06_peaks_merging.png)

---

## Recommendations

| # | Action | Supporting Findings | Expected Impact |
|---|---|---|---|
| 1 | **Launch a Feb to Mar reactivation campaign** targeting the **383 customers** who buy during the peak but never return during Feb or Mar. Focus on increasing the number of orders. | Finding 2: Peak revenue is driven by more customers, not higher spending per order. | Recovering half the Jan to Apr gap could generate approximately **$33K/yr**, closing the full gap could add **$67K/yr**. |
| 2 | **Adjust Furniture inventory based on seasonal demand.** Increase stock ahead of Nov to Dec by **2.00x a normal month** and hold 0.26x inventory during Feb instead of purchasing equal amounts every month. | Finding 3: Furniture's seasonal index 0.26 in Feb to 2.00 in Dec | Reduces excess inventory and tied up capital during Q1 while lowering the risk of stock shortages for Chairs and Bookcases during peak months. |
| 3 | **Lead the Q1 offer with Copiers and Supplies** Prioritize these products during slower months because they show more stable demand outside the main sales season. | Finding 3: Copiers and Supplies have relatively low peak season revenue shares of 28% and 26%, respectively. | Helps generate revenue during the dead zone by focusing on products that already perform better during this period. |
| 4 | **Maintain Oct's revenue growth.** Identify opportunities to support October sales. | Oct's seasonal index increased from 0.79 in 2015 to 1.29 in 2018, reducing dependence during peak months. | Supports a more balanced revenue distribution throughout the year and may help extend the period of strong sales. |

**Measurement plan:** track `Order Count` and `Active Customers` for Jan to Apr against the 2018 baseline
| Month | 2018 Orders | 2018 Active Customers |
|---|---|---|
| Jan | 67 | 66|
| Feb | 52 | 52 |
| Mar | 117 | 114 |
| Apr | 115 | 108 |

The main goal is to increase customer participation and order frequency during slower months. **Average Order Value should not be tracked**, since the analysis found no significant seasonal difference in spending per order.

![Peak erosion](visuals/04_peak_erosion.png)

---

## Caveats and assumptions

**What the Data Shows:** The analysis is based on **9,799 order lines** collected between **Jan 3, 2015, and Dec 30, 2018**. Revenue trends, order counts, customer activity, and category performance are calculated directly from this dataset.

**What Findings Suggest:** The Sep and Nov to Dec revenue peaks may be influenced by different purchasing behaviors. However, this cannot be confirmed because the dataset does not record customers' reasons for purchasing.

**Key Assumptions:** The recommendations assume that seasonal patterns will remain similar in 2019. Although the trends have appeared consistently over four years, the share of revenue generated during peak months has been declining by approximately 2.6 percentage points annually, suggesting that purchasing patterns are gradually changing.


**Data limitations:**
- **Missing business metrics:** The dataset does not include Quantity, Discount, Profit, or Cost. Therefore, the analysis cannot determine profitability, discount effects, or whether revenue changes result from price or quantity.
- **Limited geographical coverage:** Alaska and Hawaii are excluded. The dataset only represents one retailer rather than the entire market.
- **Technology outliers in March:** The Technology index of 1.41 is mainly influenced by two unusually large transactions: a **$22,638 Machines order in 2015** and a **$14,000 Copiers order in 2018**. This should not be treated as a reliable seasonal trend.
- **Large transactions retained:** All outliers were included in the analysis, including **19 order lines exceeding $5,000**, to avoid understating revenue during peak periods.
- **Revenue recognition timing:** Sales are recorded using order dates rather than shipping dates. Using shipping dates would shift approximately **$25,756 (8.0% of Dec revenue)** into Jan. The `[Sales by Ship Date]`  measure can be used to examine this difference.
---

## Transformation changelog

| Rule | Rows affected | Note |
|---|---|---|
| Initial Data | 9,800 | Original number of records before cleaning. |
| R1 — Remove Duplicates | 1 | Removed row 3407 (Order ID: US-2015-150119), which was identical to row 3406 across all 17 fields. |
| R2 — Parse Dates as (dd/mm/yyyy) | 9,799 | 0 parse failures, confirmed by day values >12 |
| R3 — Fill Missing Postal Codes | 11 | Filled missing postal codes for Burlington, Vermont, with 05401. These values were not used in the analysis. |
| R4 — Standardize Product Names | 125 | Standardized product names using the most common name for each Product ID. A total of 32 Product IDs had inconsistent names, while their sub categories remained consistent. |
| R5 — Create Additional Fields | 9,799 | Created Year, Month, Year-Month, Quarter, Shipping Delay (Days), and Season fields. Sep, Nov, and Dec were classified as peak months. |
| R6 — Retain Outliers | 19 | Kept all transactions exceeding $5,000 to preserve actual sales values and avoid understating peak revenue. |

After cleaning, the dataset contains 9,799 records, with total sales of $2,261,255.

Only one exact duplicate was removed. All other records, including unusually large transactions, were retained to maintain the accuracy of the revenue analysis.

No records were removed without documentation, ensuring that the data preparation process remains transparent and traceable.

---

## Repo contents

```
README.md                          ← findings first
data/raw/train.csv                 ← original public Superstore data
data/processed/superstore_clean.csv ← cleaned, 9,799 rows
requirements.txt
superstore.db                      ← SQLite database (open in DB Browser for SQLite)
sql/business_queries.sql           ← 8 commented queries (CTEs, window functions, JOINs, subquery, view); tested in SQLite
python/profile.py                  ← data profiling
python/clean.py                    ← cleaning + changelog
python/analyze.py                  ← seasonality analysis + significance tests
python/build_sqlite.py             ← builds superstore.db for the SQL queries
python/viz.py                      ← charts 01-04
python/viz_two_peaks.py            ← charts 05-06 (two seasonal waves)
python/model.py                    ← builds the Power BI star schema
visuals/                           ← 6 PNGs, embedded in this README
tableau/                           ← flat CSVs used by the Tableau dashboard
dashboard/                         ← dashboard link and screenshot
powerbi/README_build_spec.md       ← Power BI build instructions (optional; dashboard built in Tableau Public)
powerbi/DAX_measures.txt           ← Power BI DAX measures (not tested in Power BI)
powerbi/data/                      ← fact_sales + 5 dimensions, 0 orphan rows
```

## Reproduction

```bash
# run every command from the repository root
pip install -r requirements.txt
python python/profile.py    # profile raw
python python/clean.py      # -> data/processed/superstore_clean.csv + changelog
python python/analyze.py    # all headline numbers
python python/viz.py        # -> visuals/01-04
python python/viz_two_peaks.py  # -> visuals/05-06
python python/model.py      # -> powerbi/data/*.csv
```

## Data dictionary — `fact_sales.csv`

| Column | Type | Description |
|---|---|---|
| LineKey | int | Unique line ID (from Row ID) |
| OrderID | text | Order identifier; 4,922 distinct |
| OrderDateKey | int | YYYYMMDD → `dim_date[DateKey]` (active) |
| ShipDateKey | int | YYYYMMDD → `dim_date[DateKey]` (inactive) |
| CustomerKey | text | → `dim_customer`; 793 distinct |
| ProductKey | text | → `dim_product`; 1,861 distinct |
| GeoKey | text | `State\|City\|PostalCode` → `dim_geography` |
| ShipModeKey | text | → `dim_shipmode`; 4 values |
| Sales | float | Line revenue, USD. Min $0.44, median $54.48, max $22,638.48 |
| ShipLagDays | int | Ship date − order date; 0–7 days |
