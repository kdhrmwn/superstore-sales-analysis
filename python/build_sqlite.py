# Builds superstore.db (SQLite) from the cleaned CSV so the SQL queries can be run in DB Browser for SQLite.
# Run from the repository root:  python python/build_sqlite.py
import sqlite3, pandas as pd, os
df = pd.read_csv('data/processed/superstore_clean.csv', parse_dates=['order_date'])
fact = pd.DataFrame({
    'order_id': df['Order ID'], 'order_date': df.order_date.dt.strftime('%Y-%m-%d'),
    'customer_id': df['Customer ID'], 'product_id': df['Product ID'], 'segment': df.Segment,
    'category': df.Category, 'sub_category': df['Sub-Category'], 'region': df.Region,
    'state': df.State, 'sales': df.Sales})
dim_product = df[['Product ID','Category','Sub-Category']].drop_duplicates('Product ID')
dim_product.columns = ['product_id','category','sub_category']
dim_customer = df[['Customer ID','Customer Name','Segment']].drop_duplicates('Customer ID')
dim_customer.columns = ['customer_id','customer_name','segment']
if os.path.exists('superstore.db'): os.remove('superstore.db')
con = sqlite3.connect('superstore.db')
fact.to_sql('superstore_clean', con, index=False)
dim_product.to_sql('dim_product', con, index=False)
dim_customer.to_sql('dim_customer', con, index=False)
con.commit(); con.close()
print('superstore.db built:', len(fact), 'rows')
