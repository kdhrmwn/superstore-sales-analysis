import pandas as pd, numpy as np
df = pd.read_csv('data/raw/train.csv')
print("SHAPE", df.shape)
print("\n--- dtypes / missing / cardinality ---")
rep = pd.DataFrame({
 'dtype': df.dtypes.astype(str),
 'missing': df.isna().sum(),
 'miss_pct': (df.isna().mean()*100).round(2),
 'nunique': df.nunique(),
 'example': [df[c].dropna().iloc[0] if df[c].notna().any() else None for c in df.columns]
})
print(rep.to_string())
d = pd.to_datetime(df['Order Date'], format='%d/%m/%Y', errors='coerce')
print("\nOrder Date parse fails:", d.isna().sum(), "| range:", d.min(), "->", d.max())
s = pd.to_datetime(df['Ship Date'], format='%d/%m/%Y', errors='coerce')
print("Ship Date parse fails:", s.isna().sum(), "| range:", s.min(), "->", s.max())
print("ship before order:", (s<d).sum())
print("\nRow ID unique:", df['Row ID'].is_unique)
print("Full dup rows:", df.duplicated().sum())
print("Dup ignoring Row ID:", df.drop(columns=['Row ID']).duplicated().sum())
print("Orders:", df['Order ID'].nunique(), "Customers:", df['Customer ID'].nunique(), "Products:", df['Product ID'].nunique())
print("\nSales: ", df['Sales'].describe().to_string())
print("Sales <=0:", (df['Sales']<=0).sum())
print("\nSegment:", df['Segment'].value_counts().to_dict())
print("Region:", df['Region'].value_counts().to_dict())
print("Category:", df['Category'].value_counts().to_dict())
print("ShipMode:", df['Ship Mode'].value_counts().to_dict())
print("Country:", df['Country'].value_counts().to_dict())
print("States:", df['State'].nunique(), "Cities:", df['City'].nunique())
# integrity checks
print("\nProductID -> multiple names:", (df.groupby('Product ID')['Product Name'].nunique()>1).sum())
print("ProductID -> multiple subcat:", (df.groupby('Product ID')['Sub-Category'].nunique()>1).sum())
print("CustID -> multiple names:", (df.groupby('Customer ID')['Customer Name'].nunique()>1).sum())
print("CustID -> multiple segments:", (df.groupby('Customer ID')['Segment'].nunique()>1).sum())
print("OrderID -> multiple dates:", (df.groupby('Order ID')['Order Date'].nunique()>1).sum())
print("OrderID -> multiple customers:", (df.groupby('Order ID')['Customer ID'].nunique()>1).sum())
print("City -> multiple states:", (df.groupby('City')['State'].nunique()>1).sum())
# month coverage
m = d.dt.to_period('M')
print("\nMonths covered:", m.nunique(), "of", (d.max().to_period('M')-d.min().to_period('M')).n+1)
print(m.value_counts().sort_index().head(3).to_string())
print("orders per year:", d.dt.year.value_counts().sort_index().to_dict())
