"""Constraint filtering and disclosed planning-preference index, not crop suitability."""
import pandas as pd
from crop_catalog import options

def recommend(profile):
    candidates,gaps=options(profile);eligible=[];blocked=[]
    weights={'cover_opportunity':int('Improve soil cover' in profile['priorities']),
             'diversity_opportunity':int('Diversify the sequence' in profile['priorities']),
             'implementation_ease':int('Limit added work/equipment' in profile['priorities'])}
    for c in candidates:
        reasons=[]
        if c['id']=='cover' and profile['cover_feasible']=='No':reasons.append('No cover-establishment/termination capacity')
        if c['id']=='diversified':
            if profile['equipment']=='No new equipment':reasons.append('No new equipment/contractor capacity')
            if profile['market']=='No confirmed outlet':reasons.append('No confirmed market or forage use')
        if reasons:blocked.append({'option':c['name'],'reason':'; '.join(reasons)});continue
        c['score']=round(100*sum(c[k]*w for k,w in weights.items())/(2*sum(weights.values())),1) if sum(weights.values()) else None
        c['priority_note']='Water conservation cannot be scored from these observations alone.' if 'Conserve water' in profile['priorities'] else ''
        c['soil_note']=''
        if profile['texture']=='Sandy':c['soil_note']+='Confirm available water capacity and measured soil moisture. '
        if profile['drainage']=='Poor':c['soil_note']+='Review wet-soil establishment and trafficability. '
        if profile['texture']=='Unknown' or profile['drainage']=='Unknown':c['soil_note']+='Local soil information is incomplete. '
        if c['id']!='current' and profile['water'] in ['Rainfed','Limited irrigation']:c['soil_note']+='Review water consumed by living cover before assuming a saving.'
        eligible.append(c)
    eligible.sort(key=lambda c:(c['id']!='current',-(c['score'] or 0)))
    return eligible,blocked,gaps,weights
