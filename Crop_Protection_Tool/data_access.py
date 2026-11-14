"""NASA point access with source/units retained; no silent location fallback."""
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import requests

URL='https://power.larc.nasa.gov/api/temporal/daily/point'

def _request(latitude,longitude,start,end,parameters):
    if not -90<=latitude<=90 or not -180<=longitude<=180:raise ValueError('Coordinates outside valid ranges')
    r=requests.get(URL,params={'latitude':latitude,'longitude':longitude,'start':pd.Timestamp(start).strftime('%Y%m%d'),'end':pd.Timestamp(end).strftime('%Y%m%d'),'parameters':','.join(parameters),'community':'AG','format':'JSON','time-standard':'UTC'},timeout=90)
    r.raise_for_status();j=r.json()
    feature=j if 'properties' in j else (j.get('features') or [{}])[0]
    p=feature.get('properties',{}).get('parameter')
    if not p:raise ValueError('NASA POWER returned no daily values: '+str(j.get('messages',j))[:500])
    f=pd.DataFrame(p);f.index=pd.to_datetime(f.index,format='%Y%m%d');f.index.name='date'
    fill=j.get('header',{}).get('fill_value',-999)
    f=f.apply(pd.to_numeric,errors='coerce').replace(fill,np.nan)
    return f,{'request_url':r.url,'requested_coordinates':[latitude,longitude],'response_coordinates':feature.get('geometry',{}).get('coordinates'),'header':j.get('header',{}),'parameter_metadata':j.get('parameters',{}),'accessed_utc':datetime.now(timezone.utc).isoformat()}

def load_environment(latitude,longitude,start,end,include_wetness=True):
    start,end=pd.Timestamp(start),pd.Timestamp(end)
    if start>end:raise ValueError('Start date must precede end date')
    f,meta=_request(latitude,longitude,start,end,['T2M_MAX','PRECTOTCORR'])
    for name,acceptable in [('T2M_MAX',['C','degC','°C']),('PRECTOTCORR',['mm/day','mm/d'])]:
        units=meta['parameter_metadata'].get(name,{}).get('units')
        if units not in acceptable:raise ValueError(f'Unrecognized {name} units: {units}. Check NASA metadata before analysis.')
    f=f.rename(columns={'T2M_MAX':'tmax_c','PRECTOTCORR':'precip_mm'})
    warnings=[]
    if include_wetness:
        try:
            w,wm=_request(latitude,longitude,start,end,['GWETTOP','GWETROOT'])
            f=f.join(w,how='outer');meta['soil_wetness']=wm
        except Exception as e:warnings.append('Soil wetness unavailable: '+str(e))
    # Reindexing preserves unknown observations; missing rainfall is never zero-filled.
    f=f.reindex(pd.date_range(start,end,freq='D'));f.index.name='date'
    if (f.precip_mm.dropna()<0).any():raise ValueError('Negative precipitation encountered')
    return {'daily':f.reset_index(),'metadata':meta,'warnings':warnings}
