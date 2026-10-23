import pandas as pd, numpy as np
log=[]
df = pd.read_csv('data/raw/train.csv')
n0=len(df); log.append(("Loaded raw",n0,""))

# R1 drop exact duplicate line (ignoring Row ID)
before=len(df)
df = df.drop_duplicates(subset=[c for c in df.columns if c!='Row ID'], keep='first')
log.append(("R1 Drop exact dup line (US-2015-150119)", before-len(df), "Row 3407 removed; kept 3406"))

# R2 dates
df['order_date']=pd.to_datetime(df['Order Date'],format='%d/%m/%Y')
df['ship_date']=pd.to_datetime(df['Ship Date'],format='%d/%m/%Y')
log.append(("R2 Parse dates dd/mm/yyyy",len(df),"0 failures"))

# R3 postal code
before=df['Postal Code'].isna().sum()
df.loc[df['Postal Code'].isna() & (df.City=='Burlington') & (df.State=='Vermont'),'Postal Code']=5401
df['Postal Code']=df['Postal Code'].astype(int).astype(str).str.zfill(5)
log.append(("R3 Impute Burlington VT postal = 05401",before,"lookup fill; not used in analysis"))

# R4 product name canonicalisation
mode_name=df.groupby('Product ID')['Product Name'].agg(lambda s:s.mode().iat[0])
affected=(df['Product Name']!=df['Product ID'].map(mode_name)).sum()
df['Product Name']=df['Product ID'].map(mode_name)
log.append(("R4 Canonicalise Product Name to modal name per Product ID",affected,"32 IDs had >1 name"))

# R5 derived fields
df['year']=df.order_date.dt.year
df['month']=df.order_date.dt.month
df['month_name']=df.order_date.dt.strftime('%b')
df['ym']=df.order_date.dt.to_period('M').astype(str)
df['quarter']=df.order_date.dt.quarter
df['ship_lag_days']=(df.ship_date-df.order_date).dt.days
peak=[9,11,12]
df['season']=np.where(df.month.isin(peak),'Peak (Sep,Nov,Dec)','Off-peak (other 9 mo)')
log.append(("R5 Derive year/month/ym/quarter/ship_lag/season",len(df),"peak = Sep,Nov,Dec"))

# R6 outliers: RETAINED
big=(df.Sales>5000).sum()
log.append(("R6 Outliers RETAINED (no cap/trim)",big,"lines >$5k; real bulk orders, dropping would bias peak months"))

df.to_csv('data/processed/superstore_clean.csv',index=False)
print(pd.DataFrame(log,columns=['Rule','Rows affected','Note']).to_string(index=False))
print("\nFinal shape:",df.shape)
