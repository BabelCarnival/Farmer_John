"""Monthly climatology and Turc reference evapotranspiration from daily NASA POWER data."""
import numpy as np
import pandas as pd

COLUMNS=['month','rain_mm','tmean_c','tmin_lowest_c','frost_year_share','gwetroot','et0_mm','deficit']


def turc_et0(tmean_c,solar_mj):
    """Daily Turc ET0 (mm/day); 0 when T <= 0. NaN if temperature or radiation is missing."""
    t=pd.to_numeric(tmean_c,errors='coerce');rs=pd.to_numeric(solar_mj,errors='coerce')
    et=0.013*t/(t+15)*(23.8856*rs+50)
    return et.where(t>0,0.0).where(t.notna()&rs.notna())


def _col(d,name):return pd.to_numeric(d[name],errors='coerce') if name in d else pd.Series(np.nan,index=d.index)


def monthly_climatology(daily):
    """Return 12 rows (Jan-Dec). Columns that cannot be computed from missing inputs are NaN."""
    d=pd.DataFrame({'date':pd.to_datetime(daily['date'])})
    for c in ['precip_mm','tmean_c','tmin_c','solar_mj','GWETROOT']:d[c]=_col(daily,c).to_numpy()
    d['et0']=turc_et0(d.tmean_c,d.solar_mj);d['year']=d.date.dt.year;d['month']=d.date.dt.month
    d['frost']=(d.tmin_c<0).where(d.tmin_c.notna())
    g=d.groupby(['year','month'])
    ym=pd.DataFrame({'rain':g.precip_mm.sum(min_count=1),'tmean':g.tmean_c.mean(),'tmin':g.tmin_c.min(),
        'frost':g.frost.max(),'wet':g.GWETROOT.mean(),'et0':g.et0.sum(min_count=1)})
    # drop incomplete months (partial first/last month) so sums are not biased low
    n=g.size();days=d.groupby(['year','month']).date.apply(lambda s:s.dt.days_in_month.iloc[0])
    ym=ym[n==days]
    m=ym.groupby('month')
    out=pd.DataFrame({'rain_mm':m.rain.mean(),'tmean_c':m.tmean.mean(),'tmin_lowest_c':m.tmin.min(),
        'frost_year_share':m.frost.mean(),'gwetroot':m.wet.mean(),'et0_mm':m.et0.mean()}).reindex(range(1,13))
    out['deficit']=(out.rain_mm<0.5*out.et0_mm)&(out.et0_mm>20)
    out.index.name='month';return out.reset_index()[COLUMNS]


MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def month_range(months):
    """[11,12,1,2,3,4] -> 'Nov–Apr'; separate runs are joined with commas."""
    ms=sorted(set(months))
    if not ms:return ''
    runs=[];cur=[ms[0]]
    for m in ms[1:]:
        if m==cur[-1]+1:cur.append(m)
        else:runs.append(cur);cur=[m]
    runs.append(cur)
    if len(runs)>1 and runs[0][0]==1 and runs[-1][-1]==12:runs[-1]+=runs.pop(0)
    f=lambda r:MONTHS[r[0]-1] if len(r)==1 else f'{MONTHS[r[0]-1]}–{MONTHS[r[-1]-1]}'
    return ', '.join(f(r) for r in runs)


def heat_days_by_month(daily,threshold=35):
    """Average number of days per year with Tmax >= threshold, for each month (index 1-12)."""
    d=pd.DataFrame({'date':pd.to_datetime(daily['date']),'hot':pd.to_numeric(daily['tmax_c'],errors='coerce')>=threshold})
    d['year']=d.date.dt.year;d['month']=d.date.dt.month
    return d.groupby(['year','month']).hot.sum().groupby('month').mean().reindex(range(1,13))


def crop_by_month(crop_history):
    """Month -> crop name(s) from planting/harvest dates, or 'bare'."""
    out={m:[] for m in range(1,13)}
    for r in crop_history:
        for m in sorted(set(pd.date_range(r['Planting date'],r['Harvest date'],freq='D').month)):
            if r['Crop'] not in out[m]:out[m].append(r['Crop'])
    return {m:' / '.join(v) if v else 'bare' for m,v in out.items()}


def risk_calendar(clim,heat,crop_history):
    """Rows x 12 months of short text labels, plus a parallel level table (0 ok, 1 watch, 2 risk, -1 no data)."""
    c=clim.set_index('month');crops=crop_by_month(crop_history)
    text={k:[] for k in ['Your crops','Dry','Frost','Heat','Soil wetness']};lvl={k:[] for k in text}
    for m in range(1,13):
        text['Your crops'].append(crops[m]);lvl['Your crops'].append(2 if crops[m]=='bare' else 0)
        if pd.isna(c.et0_mm[m]):text['Dry'].append('–');lvl['Dry'].append(-1)
        elif c.deficit[m]:text['Dry'].append('dry');lvl['Dry'].append(2)
        else:text['Dry'].append('ok');lvl['Dry'].append(0)
        fs=c.frost_year_share[m]
        if pd.isna(fs):text['Frost'].append('–');lvl['Frost'].append(-1)
        elif fs>=.5:text['Frost'].append('likely');lvl['Frost'].append(2)
        elif fs>0:text['Frost'].append('possible');lvl['Frost'].append(1)
        else:text['Frost'].append('none');lvl['Frost'].append(0)
        h=heat[m]
        if pd.isna(h):text['Heat'].append('–');lvl['Heat'].append(-1)
        else:text['Heat'].append(f'{h:.1f} d');lvl['Heat'].append(2 if h>=3 else 1 if h>=.5 else 0)
        w=c.gwetroot[m]
        if pd.isna(w):text['Soil wetness'].append('–');lvl['Soil wetness'].append(-1)
        else:text['Soil wetness'].append(f'{w*100:.0f}%');lvl['Soil wetness'].append(2 if w<.35 else 1 if w<.5 else 0)
    cols=MONTHS
    return pd.DataFrame(text,index=cols).T,pd.DataFrame(lvl,index=cols).T


def takeaways(clim,heat,crop_history):
    """Short plain-language findings generated from the numbers."""
    c=clim.set_index('month');crops=crop_by_month(crop_history);out=[]
    bare=[m for m in range(1,13) if crops[m]=='bare']
    if bare:out.append(f"Your field is bare {month_range(bare)}, when {c.rain_mm[bare].sum():.0f} mm of rain falls on uncovered soil.")
    else:out.append('Your crop dates cover every month.')
    dry=[m for m in range(1,13) if c.deficit[m]]
    if c.et0_mm.notna().any():out.append(f"{month_range(dry)} {'is a dry month' if len(dry)==1 else 'are dry months'}: crops need more water than rain brings." if dry else 'No month is short of water in an average year.')
    fr=[m for m in range(1,13) if c.frost_year_share[m]>=.5]
    if c.frost_year_share.notna().any():out.append(f"Frost is likely {month_range(fr)}." if fr else 'Frost is not likely in any month.')
    hot=[m for m in range(1,13) if heat[m]>=.5]
    if heat.notna().any():out.append(f"Very hot days (35 °C or more) mostly come in {month_range(hot)}: about {heat[hot].sum():.0f} a year." if hot else 'Very hot days (35 °C or more) are rare.')
    if c.gwetroot.notna().any():
        m=int(c.gwetroot.idxmin());out.append(f"Soil is driest in {MONTHS[m-1]} ({c.gwetroot[m]*100:.0f}% wet).")
    return out
