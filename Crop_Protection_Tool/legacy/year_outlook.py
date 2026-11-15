"""Twelve-month statistical climate outlook; not a numerical weather forecast."""
from pathlib import Path
import calendar
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

HERE=Path(__file__).parent.parent
LABELS={'tmax_mean_c':'Monthly mean of daily maximum temperature (°C)',
        'rain_mm':'Monthly rainfall total (mm)',
        'hot_days':'Monthly days ≥35°C',
        'max_dry_run':'Longest within-month run <1 mm/day (days)'}

def longest(a):
    best=run=0
    for v in a:
        run=run+1 if v else 0;best=max(best,run)
    return best

def load_monthly(path=None):
    d=pd.read_csv(path or HERE/'data/power_daily.csv',parse_dates=['date']).set_index('date').sort_index()
    if d.index.duplicated().any():raise ValueError('Duplicate dates')
    d=d.reindex(pd.date_range(d.index.min(),d.index.max(),freq='D')).replace(-999,np.nan)
    rows=[]
    for period,g in d.groupby(d.index.to_period('M')):
        if len(g)!=period.days_in_month or g[['tmax_c','precip_mm']].isna().any().any():continue
        rows.append({'date':period.to_timestamp(),'tmax_mean_c':g.tmax_c.mean(),'rain_mm':g.precip_mm.sum(),
                     'hot_days':int((g.tmax_c>=35).sum()),'max_dry_run':longest(g.precip_mm.to_numpy()<1)})
    m=pd.DataFrame(rows).set_index('date')
    if len(m)<120:raise ValueError('At least ten years of complete monthly records are required.')
    return m

def design(index):
    # Calendar-only regressors: no future observed weather enters a forecast.
    t=(index.year-2000)+(index.month-1)/12
    months=np.eye(12)[index.month-1]
    return np.column_stack([months,t/10])

def forecast(train,index,target,model):
    y=train[target]
    seasonal=y.groupby(train.index.month).mean()
    base=np.array([seasonal.loc[m] for m in index.month])
    if model=='Seasonal average':p=base
    else:
        reg=Ridge(alpha=10.).fit(design(train.index),y)
        p=reg.predict(design(index))
    if target!='tmax_mean_c':p=np.maximum(p,0)
    if target in ['hot_days','max_dry_run']:p=np.minimum(p,index.days_in_month)
    return p

def run(path=None):
    m=load_monthly(path)
    # Validation chooses whether a modest linear trend improves seasonal climatology.
    # Test years are later and never used for this selection or interval width.
    val_years=[2017,2018,2019,2020];test_years=[2021,2022,2023,2024]
    validation=[];test=[];rows=[];out=[]
    for target in LABELS:
        by_model={}
        for name in ['Seasonal average','Season + trend']:
            residuals=[]
            for year in val_years:
                train=m[m.index.year<year];truth=m[m.index.year==year]
                if len(truth)!=12:continue
                p=forecast(train,truth.index,target,name)
                residuals.extend(abs(truth[target].to_numpy()-p))
                validation.extend([{'target':target,'model':name,'date':date,'observed':obs,'prediction':pred}
                    for date,obs,pred in zip(truth.index,truth[target],p)])
            by_model[name]=np.mean(residuals)
        selected=min(by_model,key=by_model.get)
        v=pd.DataFrame(validation);v=v[(v.target==target)&(v.model==selected)]
        residual=np.abs(v.observed-v.prediction)
        # Empirical pooled validation residual band, not a guaranteed forecast interval.
        width=float(np.quantile(residual,.90,method='higher'))
        errors=[];base_errors=[];covers=[]
        for year in test_years:
            train=m[m.index.year<year];truth=m[m.index.year==year]
            if len(truth)!=12:continue
            p=forecast(train,truth.index,target,selected)
            b=forecast(train,truth.index,target,'Seasonal average')
            errors.extend(abs(truth[target].to_numpy()-p));base_errors.extend(abs(truth[target].to_numpy()-b))
            covers.extend(abs(truth[target].to_numpy()-p)<=width)
            for lead,(date,obs,pred,bpred) in enumerate(zip(truth.index,truth[target],p,b),1):
                test.append({'target':target,'origin':f'{year-1}-12-31','lead_month':lead,'date':date,'observed':obs,'prediction':pred,'baseline':bpred,'absolute_error':abs(obs-pred)})
        mae=float(np.mean(errors));baseline=float(np.mean(base_errors));skill=1-mae/baseline if baseline else 0
        rows.append({'target':target,'selected_model':selected,'test_MAE':mae,'baseline_MAE':baseline,
                     'skill_vs_baseline':skill,'test_band_coverage':float(np.mean(covers)),
                     'test_months':len(errors),'validation_band_halfwidth':width,
                     'interpretation':'Added skill observed on test years' if skill>0 else 'No added skill over seasonal baseline'})
        start=m.index.max()+pd.offsets.MonthBegin(1)
        future=pd.date_range(start,periods=12,freq='MS')
        p=forecast(m,future,target,selected)
        for lead,(date,pred) in enumerate(zip(future,p),1):
            lo=pred-width;hi=pred+width
            if target!='tmax_mean_c':lo=max(0,lo)
            if target in ['hot_days','max_dry_run']:hi=min(hi,date.days_in_month)
            out.append({'target':target,'date':date,'lead_month':lead,'prediction':pred,'lower_band':lo,'upper_band':hi,
                        'model':selected,'test_skill_vs_baseline':skill,
                        'status':'Statistical outlook; empirical band, not a live weather forecast'})
    return m,pd.DataFrame(rows),pd.DataFrame(out),pd.DataFrame(test),pd.DataFrame(validation)

if __name__=='__main__':
    p=HERE/'outputs';p.mkdir(exist_ok=True)
    m,s,f,t,v=run()
    s.to_csv(p/'performance.csv',index=False);f.to_csv(p/'next_12_months.csv',index=False)
    t.to_csv(p/'heldout_predictions.csv',index=False);v.to_csv(p/'validation_predictions.csv',index=False)
    t.groupby(['target','lead_month']).absolute_error.mean().to_csv(p/'error_by_lead_month.csv')
    print(s.to_string(index=False));print('Outlook:',f.date.min(),f.date.max())
