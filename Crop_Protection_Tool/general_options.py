"""General climate-screened rotation options for farms the reviewed catalogue does not cover.

The crop table below holds GENERAL SCREENING VALUES (indicative only). They are not locally
reviewed: verify locally with FAO ECOCROP / extension advice before acting.
"""
import numpy as np
from climate import MONTHS, month_range, crop_by_month

NOTE='General screening values, verify locally with FAO ECOCROP / extension advice.'
BADGE='General climate screen (not locally reviewed)'

# key: (name, family, type, months needed, (tmin, tmax) monthly-mean °C, frost tolerant, drought tolerant)
CROPS={
 'rye':('Cereal rye cover','grass','cover',3,(3,20),'yes','yes'),
 'oats':('Oats cover/forage','grass','cover',3,(8,22),'partly','no'),
 'vetch':('Hairy vetch cover (legume)','legume','cover',4,(5,22),'yes','partly'),
 'sunnhemp':('Sunn hemp cover (legume)','legume','cover',3,(22,35),'no','yes'),
 'cowpea':('Cowpea','legume','cash',3,(22,35),'no','yes'),
 'chickpea':('Chickpea','legume','cash',4,(15,28),'partly','yes'),
 'sorghum':('Sorghum','grass','cash',4,(22,35),'no','yes'),
 'mustard':('Mustard','brassica','cash',4,(10,25),'partly','partly'),
}
FAMILY={'corn':'grass','wheat':'grass','rice':'grass','sorghum':'grass','oats':'grass','rye':'grass',
        'soybean':'legume','red clover':'legume'}
LOCAL=['Check local seed supply and a market or use for the crop.','Needs establishment and termination work; verify with a local agronomist.']


def _runs(months):
    """Runs of consecutive months (wrapping Dec->Jan), longest first."""
    s=set(months)
    if not s or len(s)==12:return [sorted(s)] if s else []
    start=[m for m in s if (m-2)%12+1 not in s];runs=[]
    for m in start:
        r=[m]
        while r[-1]%12+1 in s:r.append(r[-1]%12+1)
        runs.append(r)
    return sorted(runs,key=len,reverse=True)


def _active(c,months,key):
    """Months the crop is actually growing. Frost-tolerant cover crops (rye, vetch) are dormant,
    not killed, in months with a mean temperature below 0 °C, so those months are skipped."""
    v=CROPS[key]
    if v[2]=='cover' and v[5]=='yes':return [m for m in months if c.tmean_c[m]>=0]
    return list(months)


def _fit(c,months,key):
    """Return (score, detail) for crop `key` over `months`, or (None, reason) if it fails."""
    name,family,typ,need,(lo,hi),frost,drought=CROPS[key]
    dormant=[m for m in months if m not in _active(c,months,key)];months=_active(c,months,key)
    if CROPS[key][2]=='cover' and CROPS[key][5]=='yes' and len(months)<2:return None,'fewer than 2 months above 0 °C to grow in'
    t=[c.tmean_c[m] for m in months];fr=[c.frost_year_share[m] for m in months]
    pen=float(np.mean([max(0,lo-x,x-hi) for x in t]))
    worst=max(fr);dry=[m for m in months if c.deficit[m]]
    if frost=='no' and worst>=.25:return None,f'frost in {worst*100:.0f}% of years'
    if frost=='partly' and worst>=.75:return None,f'frost in {worst*100:.0f}% of years'
    if pen>6:return None,f'mean {np.mean(t):.1f} °C is far outside its {lo}–{hi} °C range'
    bonus=0.
    if dry:bonus={'yes':1.5,'partly':.5,'no':-1.}[drought]
    score=-pen+bonus
    detail=(f"{month_range(months)}"+(f" (dormant in {month_range(dormant)}, below 0 °C)" if dormant else "")+f": monthly mean {min(t):.0f} to {max(t):.0f} °C (it prefers {lo}–{hi} °C), "
            f"frost in up to {worst*100:.0f}% of years"+(f", dry in {month_range(dry)}" if dry else ", no dry months")+
            f"; rain {sum(c.rain_mm[m] for m in months):.0f} mm vs {sum(c.et0_mm[m] for m in months):.0f} mm crop water need")
    return score,detail


def fit_label(c,months,key):
    """Temperature/frost fit of crop `key` over `months`: 'good', 'fair' or 'poor' (c = clim indexed by month)."""
    name,family,typ,need,(lo,hi),frost,drought=CROPS[key]
    months=_active(c,months,key)
    if typ=='cover' and frost=='yes' and len(months)<2:return 'poor'
    t=[c.tmean_c[m] for m in months];fr=max(c.frost_year_share[m] for m in months)
    if (frost=='no' and fr>=.25) or (frost=='partly' and fr>=.75):return 'poor'
    pen=float(np.mean([max(0,lo-x,x-hi) for x in t]))
    return 'good' if pen<=1 else 'fair' if pen<=3 else 'poor'


def general_options(profile,clim):
    """Return (alternatives, notes). `clim` is monthly_climatology() output. Never raises on missing data."""
    c=clim.set_index('month')
    if c.tmean_c.isna().any() or c.frost_year_share.isna().any() or c.et0_mm.isna().any():
        return [],['Climate-screened options need NASA temperature and sunlight data. Load them in Step 3 to see two alternatives here.']
    crops=crop_by_month(profile['crop_history'])
    gap=[m for m in range(1,13) if crops[m]=='bare'];grow=[m for m in range(1,13) if crops[m]!='bare']
    names={r['Crop'].lower() for r in profile['crop_history']}
    fams={FAMILY.get(n) for n in names}-{None}
    seq=profile['sequence'];out=[];notes=[NOTE]

    # 1. cover the longest bare window
    best=None
    runs=_runs(gap)
    if runs:
        window=runs[0][:6]
        for k,v in CROPS.items():
            if v[2]!='cover' or len(window)<v[3] or k in names:continue
            s,d=_fit(c,window,k)
            if s is not None and fit_label(c,window,k)!='poor' and (best is None or s>best[0]):best=(s,k,d,window)
    if best:
        _,k,d,w=best;nm=CROPS[k][0];legume=CROPS[k][1]=='legume'
        out.append(dict(id='general_cover',general=True,badge=BADGE,name=f'Add {nm.lower()} in the bare months',
            sequence=f'{seq}; {nm.lower()} in {month_range(w)}',cover_opportunity=2,diversity_opportunity=2 if legume else 1,
            implementation_ease=1,source=[],risk='Cover establishment and termination add work and use water while growing.',
            reason=f'Your field is bare in {month_range(runs[0])}. NASA POWER climate for {d}.',
            fit={'crop':k,'months':w,'detail':d,'label':fit_label(c,w,k)},risks=LOCAL,
            ui=dict(what=f'Plant {nm.lower()} in {month_range(w)}; confirm establishment and termination locally.',
                before='Check seed, sowing access, soil moisture and termination timing.',
                cover='Cover in the bare months',div='Adds a legume' if legume else 'Adds a cover grass',work='Sow and terminate the cover',
                note_div=f'Adds {nm.lower()} between crops.',note_work='Adds sowing and termination tasks.')))
    elif runs:
        notes.append('No cover crop in the general table fits your bare months (too cold, too short or too frost-prone).')
    else:notes.append('Your crop dates leave no bare months, so no cover-crop window was found.')

    # 2. diversify / water-wise crop in the main growing window
    cands=[]
    gw=_runs(grow)
    for k,v in CROPS.items():
        if v[2]!='cash' or k in names:continue
        new_family=v[1] not in fams
        # a family already in the rotation is allowed only for a drought-tolerant crop (e.g. sorghum after corn)
        if not new_family and v[6]!='yes':continue
        if new_family and not (v[1]=='legume' or v[6]!='no'):continue
        if not gw:continue
        L=gw[0];best_w=None
        for i in range(len(L)-v[3]+1) if len(L)>=v[3] else []:
            w=L[i:i+v[3]];s,d=_fit(c,w,k)
            if s is None or fit_label(c,w,k)=='poor':continue  # never propose a poor climate fit
            if best_w is None or s>best_w[0]:best_w=(s,d,w)
        if best_w:cands.append((best_w[0]+(1. if new_family else 0)+(.5 if v[1]=='legume' else 0),k,best_w[1],best_w[2]))
    cands.sort(reverse=True)
    need=2-len(out)
    for s,k,d,w in cands[:need]:
        nm=CROPS[k][0];fam=CROPS[k][1]
        out.append(dict(id='general_diversified' if not any(o['id']=='general_diversified' for o in out) else 'general_diversified2',
            general=True,badge=BADGE,name=f'Add {nm.lower()} to the rotation',
            sequence=f'{seq} → {nm} → {seq}',cover_opportunity=1,diversity_opportunity=2,implementation_ease=0,source=[],
            risk='Needs a local market or use, suitable calendar and possibly new equipment.',
            reason=(f'A different crop family ({fam}) that suits your growing season. ' if fam not in fams else f'A different crop from a family already in your rotation ({fam}), chosen because it tolerates dry conditions. ')+f'NASA POWER climate for {d}.',
            fit={'crop':k,'months':w,'detail':d,'label':fit_label(c,w,k)},risks=LOCAL,
            ui=dict(what=f'Add {nm.lower()} for one season; confirm a local crop calendar and outlet.',
                before='Confirm machinery, crop timing and a market or forage use.',
                cover='Another crop in the cycle',div=f'{nm} ({fam}) added',work='More crop operations; check machinery',
                note_div=f'Adds {nm.lower()} ({fam}) to the cycle.',note_work='Needs more crop operations and equipment or a contractor.')))
    if len(out)<2:notes.append('Fewer than two general options fit your climate and crop history.')
    return out,notes
