# Charts 05 and 06: the two seasonal waves (Sep, Nov-Dec) and the closing October dip.
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
df=pd.read_csv('data/processed/superstore_clean.csv')
MN=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
GREY='#BBBBBB'; B1='#0072B2'; B2='#CC79A7'

m=df.groupby('month').Sales.sum()/1000; T=m.sum()
col=[B1 if i==9 else B2 if i in (11,12) else GREY for i in m.index]
fig,ax=plt.subplots(figsize=(9.4,4.7))
ax.bar(MN,m.values,color=col)
for i,v in enumerate(m.values): ax.text(i,v+7,f'{v/T*100:.1f}%',ha='center',fontsize=8.5,color='#333')
ax.text(6.6,372,'Wave 1: September\n13.3% of year',fontsize=9.5,color=B1,fontweight='bold',ha='center')
ax.annotate('',xy=(7.85,318),xytext=(7.35,355),arrowprops=dict(arrowstyle='->',color=B1))
ax.text(10.5,398,'Wave 2: Nov–Dec, 29.7% of year',fontsize=9.5,color=B2,fontweight='bold',ha='center')
ax.text(9,120,'–34%\nvs Sep',fontsize=9,color='white',fontweight='bold',ha='center')
ax.set_ylim(0,430); ax.set_ylabel('Revenue, $000 (2015–2018 pooled)')
ax.set_title('Revenue peaks twice: September, then Nov–Dec, with an October dip between',fontweight='bold',fontsize=12,loc='left')
plt.tight_layout(); plt.savefig('visuals/05_two_peaks.png'); plt.close()

sy=df.pivot_table(index='month',columns='year',values='Sales',aggfunc='sum'); idx=sy/sy.sum()*12
fig,ax=plt.subplots(figsize=(8,4.4))
pal={2015:'#999999',2016:'#BBBBBB',2017:'#56B4E9',2018:B1}
for y in idx.columns:
    ax.plot(range(8,13),idx.loc[8:12,y].values,marker='o',lw=2.6 if y>=2017 else 1.6,color=pal[y],label=str(y),alpha=1 if y>=2017 else .8)
ax.set_xticks(range(8,13)); ax.set_xticklabels(['Aug','Sep','Oct','Nov','Dec'])
ax.set_ylabel('Seasonal index (1.00 = flat)')
ax.text(10.08,0.62,'2015–16: Oct\n51–61% below Sep',fontsize=8.5,color='#666',ha='left')
ax.annotate('2017–18: Oct only\n10–14% below Sep',xy=(10,1.24),xytext=(10.25,0.98),fontsize=8.5,color=B1,fontweight='bold',arrowprops=dict(arrowstyle='->',color=B1))
ax.legend(frameon=False,loc='upper left',fontsize=9,ncol=4); ax.set_ylim(0.5,2.3)
ax.set_title('The two peaks are merging: the October dip has nearly closed',fontweight='bold',fontsize=12,loc='left')
plt.tight_layout(); plt.savefig('visuals/06_peaks_merging.png'); plt.close()
