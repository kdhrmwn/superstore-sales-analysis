-- ===========================================================
-- SUPERSTORE SEASONALITY: BUSINESS QUERIES (SQLite version)
-- Tables: superstore_clean (9,799 order lines), dim_product, dim_customer
-- Open superstore.db in DB Browser for SQLite -> Execute SQL tab.
-- Run ONE query at a time (select it, then press Ctrl/Cmd+Return).
-- ===========================================================

-- Q1. What share of annual revenue does each month carry, and how far is it
--     from an evenly spread year? (Seasonal index: 1.00 = flat.)
WITH monthly AS (
    SELECT CAST(strftime('%m', order_date) AS INTEGER) AS month_no,
           SUM(sales)                                  AS sales,
           COUNT(DISTINCT order_id)                    AS orders,
           COUNT(DISTINCT customer_id)                 AS active_customers
    FROM superstore_clean
    GROUP BY month_no
)
SELECT substr('JanFebMarAprMayJunJulAugSepOctNovDec', (month_no - 1) * 3 + 1, 3) AS month_name,
       ROUND(sales)                                          AS sales,
       orders,
       active_customers,
       ROUND(100.0 * sales / SUM(sales) OVER (), 1)          AS pct_of_year,
       ROUND(sales / (SUM(sales) OVER () / 12.0), 2)         AS seasonal_index,
       CASE WHEN month_no IN (9, 11, 12)  THEN 'Peak'
            WHEN month_no IN (1, 2, 3, 4) THEN 'Dead zone'
            ELSE 'Shoulder' END                              AS season
FROM monthly
ORDER BY month_no;


-- Q2. Is the peak driven by MORE orders or BIGGER orders?
--     (More orders. Median basket is flat all year.)
--     SQLite has no MEDIAN function, so the median is built with ROW_NUMBER.
WITH order_totals AS (
    SELECT order_id,
           CAST(strftime('%m', MIN(order_date)) AS INTEGER) AS month_no,
           SUM(sales)                                       AS order_value
    FROM superstore_clean
    GROUP BY order_id
), ranked AS (
    SELECT CASE WHEN month_no IN (9, 11, 12) THEN 'Peak' ELSE 'Off-peak' END AS season,
           order_value,
           ROW_NUMBER() OVER (PARTITION BY CASE WHEN month_no IN (9, 11, 12) THEN 1 ELSE 0 END
                              ORDER BY order_value) AS rn,
           COUNT(*) OVER (PARTITION BY CASE WHEN month_no IN (9, 11, 12) THEN 1 ELSE 0 END) AS n
    FROM order_totals
)
SELECT season,
       COUNT(*)                                                                AS orders,
       ROUND(AVG(order_value), 2)                                              AS mean_order_value,
       ROUND(AVG(CASE WHEN rn IN ((n + 1) / 2, (n + 2) / 2) THEN order_value END), 2) AS median_order_value
FROM ranked
GROUP BY season
ORDER BY season;


-- Q3. Which category swings hardest across the year?
--     Seasonal index per category-month via a partitioned window.
SELECT category,
       substr('JanFebMarAprMayJunJulAugSepOctNovDec',
              (CAST(strftime('%m', order_date) AS INTEGER) - 1) * 3 + 1, 3) AS month_name,
       ROUND(SUM(sales))                                                     AS sales,
       ROUND(SUM(sales) / (SUM(SUM(sales)) OVER (PARTITION BY category) / 12.0), 2) AS seasonal_index
FROM superstore_clean
GROUP BY category, CAST(strftime('%m', order_date) AS INTEGER)
ORDER BY category, CAST(strftime('%m', order_date) AS INTEGER);


-- Q4. Peak concentration by sub-category: where should inventory phase in?
--     JOIN to the product dimension; HAVING drops the small long tail.
SELECT p.sub_category,
       ROUND(SUM(s.sales))                                              AS total_sales,
       ROUND(100.0 * SUM(CASE WHEN CAST(strftime('%m', s.order_date) AS INTEGER) IN (9, 11, 12)
                              THEN s.sales ELSE 0 END) / SUM(s.sales), 1) AS pct_in_peak,
       RANK() OVER (ORDER BY SUM(s.sales) DESC)                         AS revenue_rank
FROM superstore_clean s
JOIN dim_product p ON p.product_id = s.product_id
GROUP BY p.sub_category
HAVING SUM(s.sales) > 50000
ORDER BY pct_in_peak DESC;


-- Q5. Is the business becoming LESS peak-dependent over time?
--     LAG gives the year-over-year move in peak share.
WITH by_year AS (
    SELECT CAST(strftime('%Y', order_date) AS INTEGER) AS yr,
           SUM(sales)                                  AS total_sales,
           SUM(CASE WHEN CAST(strftime('%m', order_date) AS INTEGER) IN (9, 11, 12)
                    THEN sales ELSE 0 END)             AS peak_sales
    FROM superstore_clean
    GROUP BY yr
), shares AS (
    SELECT yr, total_sales, ROUND(100.0 * peak_sales / total_sales, 1) AS peak_share_pct
    FROM by_year
)
SELECT yr,
       ROUND(total_sales)                                       AS total_sales,
       peak_share_pct,
       ROUND(peak_share_pct - LAG(peak_share_pct) OVER (ORDER BY yr), 1) AS peak_share_change_pp,
       ROUND(100.0 * (total_sales - LAG(total_sales) OVER (ORDER BY yr))
             / LAG(total_sales) OVER (ORDER BY yr), 1)          AS yoy_growth_pct,
       ROUND(SUM(total_sales) OVER (ORDER BY yr))               AS running_total
FROM shares
ORDER BY yr;


-- Q6. Does the seasonal shape differ by customer segment? (JOIN to customer dimension)
SELECT c.segment,
       COUNT(DISTINCT s.customer_id) AS customers,
       ROUND(SUM(s.sales))           AS total_sales,
       ROUND(100.0 * SUM(CASE WHEN CAST(strftime('%m', s.order_date) AS INTEGER) IN (9, 11, 12)
                              THEN s.sales ELSE 0 END) / SUM(s.sales), 1) AS pct_in_peak,
       ROUND(100.0 * SUM(CASE WHEN CAST(strftime('%m', s.order_date) AS INTEGER) IN (1, 2, 3, 4)
                              THEN s.sales ELSE 0 END) / SUM(s.sales), 1) AS pct_in_dead_zone
FROM superstore_clean s
JOIN dim_customer c ON c.customer_id = s.customer_id
GROUP BY c.segment
ORDER BY pct_in_peak DESC;


-- Q7. Sanity check on Q1: does a single outlier line carry any month?
--     A subquery finds the largest line in each month against the month total.
SELECT month_no,
       ROUND(month_sales)                       AS month_sales,
       ROUND(max_line)                          AS largest_single_line,
       ROUND(100.0 * max_line / month_sales, 1) AS pct_from_one_line
FROM (SELECT CAST(strftime('%m', order_date) AS INTEGER) AS month_no,
             SUM(sales) AS month_sales, MAX(sales) AS max_line
      FROM superstore_clean
      GROUP BY month_no) m
ORDER BY pct_from_one_line DESC;


-- Q8. Reusable view for BI tools.
CREATE VIEW IF NOT EXISTS v_monthly_seasonality AS
SELECT strftime('%Y-%m-01', order_date)                   AS month_start,
       CAST(strftime('%Y', order_date) AS INTEGER)        AS yr,
       CAST(strftime('%m', order_date) AS INTEGER)        AS month_no,
       CASE WHEN CAST(strftime('%m', order_date) AS INTEGER) IN (9, 11, 12)
            THEN 'Peak' ELSE 'Off-peak' END               AS season,
       category,
       SUM(sales)                                         AS sales,
       COUNT(DISTINCT order_id)                           AS orders,
       COUNT(DISTINCT customer_id)                        AS active_customers
FROM superstore_clean
GROUP BY 1, 2, 3, 4, 5;

-- Check the view works:
SELECT * FROM v_monthly_seasonality ORDER BY month_start, category LIMIT 10;
