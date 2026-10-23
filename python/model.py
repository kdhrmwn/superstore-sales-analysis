import pandas as pd, numpy as np
df=pd.read_csv('data/processed/superstore_clean.csv',parse_dates=['order_date','ship_date'])

# dim_date  (2015-01-01 .. 2019-01-05 to cover ship dates)
dates=pd.DataFrame({'Date':pd.date_range('2015-01-01','2019-01-05')})
dates['DateKey']=dates.Date.dt.strftime('%Y%m%d').astype(int)
dates['Year']=dates.Date.dt.year; dates['Quarter']='Q'+dates.Date.dt.quarter.astype(str)
dates['MonthNo']=dates.Date.dt.month; dates['MonthName']=dates.Date.dt.strftime('%b')
dates['YearMonth']=dates.Date.dt.strftime('%Y-%m')
dates['MonthSort']=dates.Year*100+dates.MonthNo
dates['Season']=np.where(dates.MonthNo.isin([9,11,12]),'Peak','Off-peak')
dates['PeakWave']=np.select([dates.MonthNo==9,dates.MonthNo.isin([11,12]),dates.MonthNo==10],['Wave 1 (Sep)','Wave 2 (Nov-Dec)','Oct dip'],'Base')
dates['DeadZone']=np.where(dates.MonthNo.isin([1,2,3,4]),'Jan-Apr dead zone','Rest of year')
dates['DayName']=dates.Date.dt.strftime('%a')
dates.to_csv('powerbi/data/dim_date.csv',index=False)

dim_cust=df[['Customer ID','Customer Name','Segment']].drop_duplicates().rename(columns={'Customer ID':'CustomerKey','Customer Name':'CustomerName'})
dim_cust.to_csv('powerbi/data/dim_customer.csv',index=False)

dim_prod=df[['Product ID','Product Name','Category','Sub-Category']].drop_duplicates(subset='Product ID').rename(columns={'Product ID':'ProductKey','Product Name':'ProductName','Sub-Category':'SubCategory'})
dim_prod.to_csv('powerbi/data/dim_product.csv',index=False)

geo=df[['Postal Code','City','State','Region','Country']].drop_duplicates()
geo['GeoKey']=geo['State'].astype(str)+'|'+geo['City'].astype(str)+'|'+geo['Postal Code'].astype(str)
geo=geo.drop_duplicates('GeoKey').rename(columns={'Postal Code':'PostalCode'})
geo.to_csv('powerbi/data/dim_geography.csv',index=False)

dim_ship=pd.DataFrame({'ShipModeKey':sorted(df['Ship Mode'].unique())})
dim_ship['SpeedRank']=dim_ship.ShipModeKey.map({'Same Day':1,'First Class':2,'Second Class':3,'Standard Class':4})
dim_ship.to_csv('powerbi/data/dim_shipmode.csv',index=False)

f=df.copy()
f['GeoKey']=f['State'].astype(str)+'|'+f['City'].astype(str)+'|'+f['Postal Code'].astype(str)
fact=f[['Row ID','Order ID','order_date','ship_date','Customer ID','Product ID','GeoKey','Ship Mode','Sales','ship_lag_days']].rename(
 columns={'Row ID':'LineKey','Order ID':'OrderID','Customer ID':'CustomerKey','Product ID':'ProductKey','Ship Mode':'ShipModeKey','ship_lag_days':'ShipLagDays'})
fact['OrderDateKey']=fact.order_date.dt.strftime('%Y%m%d').astype(int)
fact['ShipDateKey']=fact.ship_date.dt.strftime('%Y%m%d').astype(int)
fact=fact.drop(columns=['order_date','ship_date'])
fact.to_csv('powerbi/data/fact_sales.csv',index=False)

for n,t in [('fact_sales',fact),('dim_date',dates),('dim_customer',dim_cust),('dim_product',dim_prod),('dim_geography',geo),('dim_shipmode',dim_ship)]:
    print(f"{n:16s} {t.shape[0]:>6,} rows x {t.shape[1]} cols")
# referential integrity
print("\nOrphan checks (should all be 0):")
print(" product:",(~fact.ProductKey.isin(dim_prod.ProductKey)).sum())
print(" customer:",(~fact.CustomerKey.isin(dim_cust.CustomerKey)).sum())
print(" geo:",(~fact.GeoKey.isin(geo.GeoKey)).sum())
print(" date:",(~fact.OrderDateKey.isin(dates.DateKey)).sum(),(~fact.ShipDateKey.isin(dates.DateKey)).sum())
print("\nFact sales total reconciles to clean.csv:",round(fact.Sales.sum(),2)==round(df.Sales.sum(),2))
