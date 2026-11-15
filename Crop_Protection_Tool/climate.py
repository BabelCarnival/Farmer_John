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
