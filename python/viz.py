import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
df=pd.read_csv('data/processed/superstore_clean.csv'); T=df.Sales.sum()
MN=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
PEAK='#0072B2'; GREY='#BBBBBB'; ORANGE='#D55E00'; GREEN='#009E73'

# --- Chart 1: monthly revenue, peak highlighted
m=df.groupby('month').Sales.sum()/1000
fig,ax=plt.subplots(figsize=(9,4.4))
cols=[PEAK if i in (9,11,12) else GREY for i in m.index]
ax.bar(MN,m.values,color=cols)
for i,v in enumerate(m.values): ax.text(i,v+6,f'{v/m.sum()*100:.1f}%',ha='center',fontsize=8.5,color='#333')
ax.axhline(m.sum()/12,ls='--',lw=1,color=ORANGE)
ax.text(5.5,m.sum()/12+11,'flat-year avg $188K',color=ORANGE,fontsize=8.5,ha='center')
ax.set_title('Sep, Nov and Dec generate 43% of annual revenue — Feb generates 2.6%',fontweight='bold',fontsize=12.5,loc='left')
ax.set_ylabel('Revenue, $000 (2015–2018 pooled)'); ax.set_ylim(0,400)
ax.annotate('Nov peak = 5.9× the Feb trough',xy=(1,64),xytext=(1.6,290),fontsize=9.5,
            arrowprops=dict(arrowstyle='->',color='#555',connectionstyle='arc3,rad=0.3'))
plt.tight_layout(); plt.savefig('visuals/01_monthly_revenue.png'); plt.close()

# --- Chart 2: season x category seasonal index heatmap
mi=df.pivot_table(index='month',columns='Category',values='Sales',aggfunc='sum')
mi=(mi/mi.sum()*12)
fig,ax=plt.subplots(figsize=(6.4,5.6))
im=ax.imshow(mi.values,cmap='RdBu_r',vmin=0.2,vmax=2.0,aspect='auto')
ax.set_xticks(range(3)); ax.set_xticklabels(mi.columns,fontsize=9.5)
ax.set_yticks(range(12)); ax.set_yticklabels(MN,fontsize=9)
for i in range(12):
    for j in range(3):
        v=mi.values[i,j]
        ax.text(j,i,f'{v:.2f}',ha='center',va='center',fontsize=9,
                color='white' if (v>1.55 or v<0.5) else '#222',
                fontweight='bold' if v>1.5 else 'normal')
ax.set_title('Furniture swings hardest: 2.00 in Dec vs 0.26 in Feb\nSeasonal index, 1.00 = flat year',fontweight='bold',fontsize=11.5,loc='left')
plt.colorbar(im,ax=ax,shrink=0.6,label='index')
plt.tight_layout(); plt.savefig('visuals/02_season_x_category.png'); plt.close()

# --- Chart 3: traffic vs basket
o=df.groupby(['Order ID','month']).Sales.sum().reset_index()
cnt=o.groupby('month').size(); med=o.groupby('month').Sales.median()
fig,axs=plt.subplots(1,2,figsize=(10,4.1))
c=[PEAK if i in (9,11,12) else GREY for i in cnt.index]
axs[0].bar(MN,cnt.values,color=c); axs[0].set_title('Orders per month: 2.3× higher in peak',fontsize=11,fontweight='bold',loc='left')
axs[0].set_ylabel('Orders (4-yr total)')
axs[1].bar(MN,med.values,color=c); axs[1].axhline(med.median(),ls='--',lw=1,color=ORANGE)
axs[1].set_title('Median order value: flat all year (p = 0.67)',fontsize=11,fontweight='bold',loc='left')
axs[1].set_ylabel('Median order value, $'); axs[1].set_ylim(0,220)
fig.suptitle('The peak is a traffic event, not a bigger-basket event',fontsize=13,fontweight='bold',x=0.01,ha='left')
plt.tight_layout(rect=[0,0,1,0.94]); plt.savefig('visuals/03_traffic_vs_basket.png'); plt.close()

# --- Chart 4: peak concentration eroding
sy=df.pivot_table(index='month',columns='year',values='Sales',aggfunc='sum')
sh=(sy.loc[[9,11,12]].sum()/sy.sum()*100)
fig,ax=plt.subplots(figsize=(6.6,3.8))
ax.plot(sh.index,sh.values,marker='o',color=ORANGE,lw=2.2)
for x,v in sh.items(): ax.text(x,v+0.9,f'{v:.1f}%',ha='center',fontsize=9.5)
ax.set_ylim(35,52); ax.set_ylabel('Peak share of annual revenue')
ax.set_xticks(sh.index)
ax.set_title('Peak dependence is falling: 47.5% → 39.8% as Oct and Jan grow',fontweight='bold',fontsize=11.5,loc='left')
plt.tight_layout(); plt.savefig('visuals/04_peak_erosion.png'); plt.close()
print("done")
