"""Derived calendar gaps and selected-location weather analysis."""
import calendar
import pandas as pd
from exposure import exposure,dry_run

def parse_history(table):
    rows=[];months=set()
    for _,r in table.iterrows():
        if pd.isna(r.get('Crop')):continue
        plant=pd.to_datetime(r.get('Planting date'),errors='coerce');harvest=pd.to_datetime(r.get('Harvest date'),errors='coerce')
        if pd.isna(plant) or pd.isna(harvest) or plant>=harvest:raise ValueError('Every crop needs valid planting and harvest dates, with planting before harvest.')
        if (harvest-plant).days>730:raise ValueError('Crop dates span more than two years; check this calendar.')
        m=set(pd.date_range(plant,harvest,freq='D').month);months.update(m)
        rows.append({'Crop':str(r['Crop']),'Planting date':str(plant.date()),'Harvest date':str(harvest.date())})
    if not rows:raise ValueError('Enter at least one crop-history row.')
    return rows,sorted(months),sorted(set(range(1,13))-months)

def annual_exposure(d,months):
    rows=[]
    for year,g in d.groupby(d.date.dt.year):
        r=exposure(g,months,35,1)
        expected=sum(calendar.monthrange(int(year),m)[1] for m in months)
        r.update(year=int(year),coverage=r['valid_days']/expected)
        rows.append(r)
    out=pd.DataFrame(rows)
    good=out.coverage>=.95
    out['index']=0.
    for col,sign in [('heat_days',1),('dry_spell_days',1),('rain_mm',-1)]:
        v=out.loc[good,col];sd=v.std(ddof=0)
        out['index']+=sign*(out[col]-v.mean())/(sd if pd.notna(sd) and sd>0 else 1)
    return out

def monthly_exposure(d,months):
    rows=[]
    for month,g in d.groupby(d.date.dt.month):
        rows.append({'Month':int(month),'Heat days ≥35°C':int((g.tmax_c>=35).sum()),'Longest rainfall gap (days)':dry_run(g,1),
                     'Rainfall (mm)':float(g.precip_mm.sum()),'Within entered crop season':month in months})
    return pd.DataFrame(rows)
