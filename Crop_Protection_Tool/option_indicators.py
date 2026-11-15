"""Plan indicators for rotation options. Every number is computed from the entered crop dates,
the option's calendar and the NASA POWER monthly climatology; none are opinions or predictions."""
import numpy as np
import pandas as pd
from climate import MONTHS, crop_by_month
from general_options import CROPS, FAMILY, fit_label

# Reviewed Iowa options have no stored calendar: same cover months as the Step 5 default (an assumption).
IOWA_COVER_MONTHS=[3,4,10,11]
IOWA={'cover':dict(label='Cereal rye',species=['rye'],families=['grass'],fit_key='rye'),
      'diversified':dict(label='Small grain + clover',species=['small grain','red clover'],families=['grass','legume'],fit_key=None)}
PALETTE=['#e0b43c','#6fa8dc','#c27ba0','#93c47d','#e69138','#8e7cc3','#76a5af','#cc4125']


def option_calendar(c,crop_history):
    """month -> crop label ('bare' if none). Also returns the months this option adds a living crop in."""
    cal=crop_by_month(crop_history);added=[]
    if c['id']=='current':return cal,added
    if c.get('general'):
        k=c['fit']['crop'];label=CROPS[k][0].split(' (')[0];months=c['fit']['months']
        if CROPS[k][2]=='cover':months=[m for m in months if cal[m]=='bare']
    else:
        info=IOWA.get(c['id']);label=info['label'] if info else None
        months=[m for m in IOWA_COVER_MONTHS if cal[m]=='bare'] if info else []
    for m in months:cal[m]=label;added.append(m)
    return cal,added


def _crop_names(crop_history,c):
    names={r['Crop'].lower() for r in crop_history}
    fams={FAMILY.get(n,n) for n in names}
    if c['id']=='current':return names,fams
    if c.get('general'):
        k=c['fit']['crop'];names|={k};fams.add(CROPS[k][1])
    elif c['id'] in IOWA:names|=set(IOWA[c['id']]['species']);fams|=set(IOWA[c['id']]['families'])
    return names,fams


def indicators(options,crop_history,clim):
    """Return a DataFrame, one row per option. `clim` may be None (weather not loaded)."""
    c=clim.set_index('month') if clim is not None else None
    rows=[]
    for o in options:
        cal,added=option_calendar(o,crop_history);bare=[m for m in range(1,13) if cal[m]=='bare']
        names,fams=_crop_names(crop_history,o)
        r={'Option':o['name'],'Months with living cover':12-len(bare),'Crops in the cycle':len(names),'Crop families in the cycle':len(fams),
           'Rain on bare soil (mm/yr)':np.nan,'Extra water demand':'unknown','Climate fit of the new crop':'–' if o['id']=='current' else 'not screened'}
        if c is not None:
            r['Rain on bare soil (mm/yr)']=float(c.rain_mm[bare].sum()) if bare else 0.
            if c.deficit.notna().all() and c.et0_mm.notna().any():
                n=sum(bool(c.deficit[m]) for m in added)
                r['Extra water demand']='none' if n==0 else 'some' if n<=2 else 'high'
            if o.get('general'):r['Climate fit of the new crop']=o['fit']['label']
            elif o['id'] in IOWA and IOWA[o['id']]['fit_key'] and not c.tmean_c.isna().any():
                r['Climate fit of the new crop']=fit_label(c,[m for m in IOWA_COVER_MONTHS if cal[m]!='bare' and m in added] or IOWA_COVER_MONTHS,IOWA[o['id']]['fit_key'])
        rows.append(r)
    return pd.DataFrame(rows)


def colour_map(options,crop_history):
    labels=[]
    for o in options:
        for v in option_calendar(o,crop_history)[0].values():
            if v!='bare' and v not in labels:labels.append(v)
    return {l:PALETTE[i%len(PALETTE)] for i,l in enumerate(labels)}|{'bare':'#d9d9d9'}


def strip_html(cal,colours):
    cells=''.join(f'<div title="{MONTHS[m-1]}: {cal[m]}" style="flex:1;background:{colours[cal[m]]};color:#333;font:11px sans-serif;text-align:center;padding:6px 0">{MONTHS[m-1][0]}</div>' for m in range(1,13))
    used=[]
    for m in range(1,13):
        if cal[m] not in used:used.append(cal[m])
    legend=' '.join(f'<span style="font:12px sans-serif;margin-right:8px"><span style="display:inline-block;width:10px;height:10px;background:{colours[u]};margin-right:3px"></span>{u}</span>' for u in used)
    return f'<div style="display:flex;border-radius:6px;overflow:hidden;margin:4px 0">{cells}</div><div>{legend}</div>'
