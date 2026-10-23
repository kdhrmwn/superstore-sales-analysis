import pandas as pd, numpy as np
df=pd.read_csv('data/processed/superstore_clean.csv',parse_dates=['order_date','ship_date'])
T=df.Sales.sum()
print(f"TOTAL SALES ${T:,.0f} over {df.ym.nunique()} months")

print("\n=== A. Monthly seasonal profile (4yr pooled) ===")
m=df.groupby('month').agg(sales=('Sales','sum'),orders=('Order ID','nunique'),lines=('Sales','size'))
m['share_%']=(m.sales/T*100).round(1)
m['index']=(m.sales/(T/12)).round(2)
m['med_order']=df.groupby(['month','Order ID']).Sales.sum().groupby('month').median().round(0)
m.index=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
print(m.to_string())
peak=['Sep','Nov','Dec']
print("\nPeak Sep+Nov+Dec share: %.1f%%  (3/12 mo = 25%% if flat) -> %.2fx"%(m.loc[peak,'share_%'].sum(), m.loc[peak,'index'].mean()))
print(f"Feb (trough) vs Nov (crest): ${m.loc['Feb','sales']:,.0f} vs ${m.loc['Nov','sales']:,.0f} = {m.loc['Nov','sales']/m.loc['Feb','sales']:.1f}x")

print("\n=== SANITY CHECK: orders vs basket size ===")
print("peak orders/mo avg: %.0f | offpeak: %.0f"%(m.loc[peak,'orders'].sum()/3, m.drop(peak).orders.sum()/9))
po=df[df.month.isin([9,11,12])].groupby('Order ID').Sales.sum(); oo=df[~df.month.isin([9,11,12])].groupby('Order ID').Sales.sum()
print("median order value peak $%.2f vs offpeak $%.2f"%(po.median(),oo.median()))
from scipy import stats
u=stats.mannwhitneyu(po,oo); print("Mann-Whitney p=%.4f  n_peak=%d n_off=%d"%(u.pvalue,len(po),len(oo)))

print("\n=== B. Season x Category ===")
ct=df.pivot_table(index='Category',columns='season',values='Sales',aggfunc='sum')
ct['peak_share_%']=(ct['Peak (Sep,Nov,Dec)']/(ct.sum(axis=1))*100).round(1)
ct['cat_share_of_total_%']=(df.groupby('Category').Sales.sum()/T*100).round(1)
# monthly index per category
mi=df.pivot_table(index='month',columns='Category',values='Sales',aggfunc='sum')
mi=(mi/mi.sum()*12).round(2)
print(ct.round(0).to_string()); print("\nSeasonal index by month/category (1.0=flat):"); print(mi.to_string())
print("\nSwing (max-min index):",(mi.max()-mi.min()).round(2).to_dict())

print("\n=== C. Sub-category peak concentration (top movers) ===")
sc=df.pivot_table(index='Sub-Category',columns='season',values='Sales',aggfunc='sum').fillna(0)
sc['total']=sc.sum(axis=1); sc['peak_%']=(sc['Peak (Sep,Nov,Dec)']/sc.total*100).round(1)
print(sc.sort_values('total',ascending=False)[['total','peak_%']].round(0).to_string())

print("\n=== D. YoY / trend ===")
y=df.groupby('year').Sales.sum(); print((y.round(0)).to_string()); print("YoY %:",(y.pct_change()*100).round(1).to_dict())
print("CAGR 2015->2018: %.1f%%"%(((y[2018]/y[2015])**(1/3)-1)*100))
# is seasonality stable across years?
sy=df.pivot_table(index='month',columns='year',values='Sales',aggfunc='sum')
syi=(sy/sy.sum()*12).round(2); print("\nSeasonal index by year:"); print(syi.to_string())
print("Sep+Nov+Dec share by year:",((sy.loc[[9,11,12]].sum()/sy.sum())*100).round(1).to_dict())

print("\n=== E. Dead zone Jan-Apr ===")
dz=m.loc[['Jan','Feb','Mar','Apr']]
print("Jan-Apr share %.1f%% of revenue for 33.3%% of the year"%dz['share_%'].sum())
print(f"Gap to flat: ${(T/12*4-dz.sales.sum())/4:,.0f}/yr")
