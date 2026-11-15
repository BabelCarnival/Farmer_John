"""Monthly T2M from the supplied NASA POWER workbook; schema assumptions explicit."""
from pathlib import Path
import numpy as np
import pandas as pd
from year_outlook import forecast

HERE=Path(__file__).parent.parent

def load_workbook(state='IOWA',latitude=42.03,longitude=-93.62):
    # header=None matters: the first row contains a valid data record.
    raw=pd.read_excel(HERE/'data/usa_temperature_2000_2025.xlsx',header=None,engine='openpyxl')
    if raw.shape[1]!=18:raise ValueError('Expected state, parameter, year, lat, lon, 12 months, annual.')
    raw.columns=['state','parameter','year','lat','lon']+list(range(1,13))+['annual']
    raw['state']=raw.state.replace('STATE',np.nan).ffill().bfill().str.upper().str.strip().replace({'ILLNOIS':'ILLINOIS'})
    selected=raw[raw.state.eq(state.upper())&raw.parameter.eq('T2M')].copy()
    if selected.empty:raise ValueError('State not found. Available: '+', '.join(sorted(raw.state.unique())))
    points=selected[['lat','lon']].drop_duplicates().copy()
    # Approximate local distance for selecting a representative grid point.
    points['distance']=((points.lat-latitude)**2+((points.lon-longitude)*np.cos(np.radians(latitude)))**2)
    nearest=points.loc[points.distance.idxmin()]
    g=selected[selected.lat.eq(nearest.lat)&selected.lon.eq(nearest.lon)].copy()
    if g.year.duplicated().any():raise ValueError('Duplicate years at selected grid point')
    records=[]
    for _,r in g.iterrows():
        for month in range(1,13):
            value=pd.to_numeric(r[month],errors='coerce')
            if pd.isna(value) or value<=-900:continue
            records.append({'date':pd.Timestamp(int(r.year),month,1),'t2m_mean_c':float(value)})
    monthly=pd.DataFrame(records).set_index('date').sort_index()
    info={'state':state.upper(),'selected_lat':float(nearest.lat),'selected_lon':float(nearest.lon),
          'source':'NASA POWER monthly T2M, 2000–2025 USA Temp by State workbook (source confirmed by team; export settings not recorded)',
          'schema':'Columns 6–17 interpreted as January–December monthly mean T2M; Celsius assumed. Exact export settings not recorded.',
          'meaning':'Representative grid point within the state label; not a state-wide average and not daily maximum temperature.'}
    return monthly,info

def run_state(state='IOWA',latitude=42.03,longitude=-93.62):
    m,info=load_workbook(state,latitude,longitude)
    return run_signed(m,info)

def temperature_forecast(m,index,target,name):
    return forecast(m.rename(columns={target:'tmax_mean_c'}),index,'tmax_mean_c',name)

def run_signed(m,info):
    target='t2m_mean_c';scores={};res={}
    for name in ['Seasonal average','Season + trend']:
        es=[]
        for year in range(2017,2021):
            t=m[m.index.year==year];p=temperature_forecast(m[m.index.year<year],t.index,target,name)
            es.extend(abs(t[target].to_numpy()-p))
        scores[name]=np.mean(es);res[name]=es
    name=min(scores,key=scores.get);width=float(np.quantile(res[name],.9,method='higher'))
    rows=[]
    for year in range(2021,2026):
        t=m[m.index.year==year]
        if len(t)!=12:continue
        train=m[m.index.year<year];p=temperature_forecast(train,t.index,target,name);b=temperature_forecast(train,t.index,target,'Seasonal average')
        rows.extend([{'date':date,'lead_month':i+1,'observed':obs,'prediction':pred,'baseline':bp}
                     for i,(date,obs,pred,bp) in enumerate(zip(t.index,t[target],p,b))])
    test=pd.DataFrame(rows);mae=float(abs(test.observed-test.prediction).mean());base=float(abs(test.observed-test.baseline).mean())
    future=pd.date_range(m.index.max()+pd.offsets.MonthBegin(1),periods=12,freq='MS');p=temperature_forecast(m,future,target,name)
    out=pd.DataFrame({'date':future,'predicted_monthly_mean_t2m_c':p,'lower_band':p-width,'upper_band':p+width})
    info.update(model=name,test_MAE_c=mae,baseline_MAE_c=base,skill_vs_baseline=1-mae/base,test_months=len(test))
    return m,out,test,info
