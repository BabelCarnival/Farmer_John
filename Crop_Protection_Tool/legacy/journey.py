"""TerraRoute evidence and scenario screens. Scenarios are sensitivity tests."""
from pathlib import Path
import calendar,json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import sys;sys.path.insert(0,str(Path(__file__).parent.parent))
from exposure import load_daily,history,load_modis,dry_run,compare
ROOT=Path(__file__).parent.parent

def environment(selected,state,near):
    st.subheader('2. Understand the environmental evidence')
    st.write(f"Selected {state} grid: summer mean temperature {selected.recent_c:.1f}°C in 2016–2025, {selected.change_c:+.1f}°C compared with 2000–2009.")
    st.dataframe(pd.DataFrame([
      {'Signal':'Temperature history','Coverage':'Selected workbook grid, 2000–2025','Status':'Monthly T2M/Celsius interpretation needs original export metadata'},
      {'Signal':'Daily rainfall and heat','Coverage':'Ames sample only, 2001–2024','Status':'Available as separate nearby example' if near else 'Unavailable for this selected region'},
      {'Signal':'Vegetation / NDVI','Coverage':'One Ames MODIS pixel, 2024','Status':'Quality-filtered example available' if near else 'Unavailable for this selected region'},
      {'Signal':'Soil moisture','Coverage':'No satellite soil-moisture product supplied','Status':'Not inferred from rainfall; field information needed'}
    ]),hide_index=True,width='stretch')
    st.caption('Regional data and one mixed vegetation pixel are not field sensors. Local soil inputs remain separate.')

def vulnerabilities(profile,near):
    st.subheader('3. Identify potentially vulnerable periods')
    st.write('Attention months: '+', '.join(calendar.month_abbr[m] for m in profile['sensitive_months']))
    st.write('Assumed uncovered months: '+(', '.join(calendar.month_abbr[m] for m in profile['bare_months']) or 'None entered'))
    if not near:
        st.info('This region has monthly temperature context only. Daily dry spells, water limitations and bare-ground conditions cannot be quantified here from the supplied data. The scenario test below will be temperature-only.')
        return None
    d=load_daily(ROOT/'data/power_daily.csv');h=history(d)
    worst=int(h.loc[h.compound.idxmax(),'year'])
    years=h.year.astype(int).tolist()
    year=st.selectbox('Choose an Ames historical season to inspect',years,index=years.index(worst))
    daily=d[d.date.dt.year==year]
    focus=daily[daily.date.dt.month.isin(profile['sensitive_months'])]
    heat=int((focus.tmax_c>=35).sum());dry=dry_run(focus,1)
    a,b=st.columns(2);a.metric('Days ≥35°C in attention months',heat);b.metric('Longest run with <1 mm/day rain',f'{dry} days')
    st.caption('Screening thresholds, not validated crop injury limits. Irrigation, soil moisture and crop stage can change field outcomes.')
    monthly=daily.groupby(daily.date.dt.month).agg(rain_mm=('precip_mm','sum'),mean_daily_tmax_c=('tmax_c','mean')).reset_index(names='month')
    monthly['attention_month']=monthly.month.isin(profile['sensitive_months']);monthly['assumed_bare_month']=monthly.month.isin(profile['bare_months'])
    st.plotly_chart(px.bar(monthly,x='month',y='rain_mm',color='assumed_bare_month',labels={'month':'Month','rain_mm':'Historical rain (mm)','assumed_bare_month':'Assumed uncovered'},title=f'{year}: rain falling in and outside assumed uncovered months'),width='stretch')
    if profile['water']=='Rainfed':st.write('**Water limitation to review:** rainfall gaps matter for a rainfed field, but stored soil water has not been measured by this tool.')
    if profile['drainage']=='Poor':st.write('**Wet-period limitation to review:** your reported poor drainage raises establishment and machinery-access questions. Rainfall alone does not establish waterlogging.')
    m=load_modis(ROOT/'data/modis_2024.csv');m=m[(m.quality=='Good')&m.ndvi.notna()]
    low=m[m.ndvi<.3]
    with st.expander('Check vegetation and possible low-cover observations'):
        st.plotly_chart(px.line(m,x='date',y='ndvi',markers=True,labels={'date':'2024 composite date','ndvi':'NDVI'}),width='stretch')
        st.write(f'{len(low)} good-quality 2024 observations fall below the illustrative NDVI screen of 0.3. These are possible low-greenness observations, not confirmed bare soil. Snow, seasonality and mixed land cover need review.')
        st.caption('The MODIS point has not been verified as farmland. It does not validate assumed bare months or the selected historical replay year.')
    return {'daily':d,'year':year,'heat_days':heat,'dry_spell_days':dry}

def stress(profile,selected,state,near,evidence):
    st.subheader('5. Stress-test the three options')
    st.caption('What-if sensitivity analysis. Temperature offsets and rainfall multipliers are applied to historical observations; these are not future climate forecasts.')
    preset=st.selectbox('Scenario',['Historical conditions','Hotter (+2°C)','Drier (−20% rain)','Wetter (+20% rain)','Custom'])
    delta=2. if preset=='Hotter (+2°C)' else 0.
    rain_factor=.8 if preset=='Drier (−20% rain)' else 1.2 if preset=='Wetter (+20% rain)' else 1.
    if preset=='Custom':
        delta=st.slider('Temperature change (°C)',-2.,5.,2.,.5)
        rain_factor=st.slider('Rainfall as % of historical amount',50,150,80,5)/100
    if not near:
        st.info('Rainfall scenarios cannot be evaluated for this region. Only a monthly mean-temperature sensitivity is available; no daily heat/dry-spell counts are inferred.')
        st.metric('Scenario summer mean temperature',f'{selected.recent_c+delta:.1f}°C',f'{delta:+.1f}°C applied')
        return {'scenario':preset,'delta_c':delta,'rain_factor_requested':rain_factor,'coverage':'Selected-grid monthly temperature only; rainfall not evaluated'}
    daily=evidence['daily'];year=evidence['year']
    st.write('Adjust the example calendars below with local knowledge. The diversified option represents one proposed crop phase, not a complete multi-year crop-growth simulation.')
    cover=st.multiselect('Months the proposed cover would protect the soil (assumption)',range(1,13),[3,4,10,11],format_func=lambda n:calendar.month_abbr[n])
    alt_sensitive=st.multiselect('Attention months in the diversified crop phase (assumption)',range(1,13),[5,6,7],format_func=lambda n:calendar.month_abbr[n])
    if not alt_sensitive:
        st.warning('Choose at least one attention month for the diversified phase.');return {}
    plans=[{'name':'Existing rotation','sensitive':profile['sensitive_months'],'bare':profile['bare_months']},
           {'name':'Existing crops + cover','sensitive':profile['sensitive_months'],'bare':[m for m in profile['bare_months'] if m not in cover]},
           {'name':'Diversified crop phase','sensitive':alt_sensitive,'bare':[m for m in profile['bare_months'] if m not in cover]}]
    baseline=compare(daily,plans,year,35.,1.)
    changed=daily.copy();changed['tmax_c']+=delta;changed['precip_mm']*=rain_factor
    result=compare(changed,plans,year,35.,1.)
    output=pd.DataFrame({'Strategy':result.strategy,
        'Historical heat days':baseline.heat_days,'Scenario heat days':result.heat_days,
        'Historical longest dry run (days)':baseline.dry_spell_days,'Scenario longest dry run (days)':result.dry_spell_days,
        'Scenario rain in assumed uncovered months (mm)':result.bare_rain_mm.round(1),
        'Scenario heavy-rain days in assumed uncovered months':result.bare_heavy_days})
    st.dataframe(output,hide_index=True,width='stretch')
    st.write(f'**Scenario applied:** historical {year} weather with {delta:+.1f}°C added to daily maximum temperatures and rainfall multiplied by {rain_factor:.2f}.')
    st.write('**How to read this:** the cover option may reduce assumed uncovered months but does not change the weather. Equal attention windows produce equal heat/dry-spell exposure. A changed window tests timing; it does not prove a crop will perform better.')
    output['replay_year']=year;output['temperature_offset_c']=delta;output['rainfall_multiplier']=rain_factor
    output['profile']=json.dumps(profile);output['calendar_assumptions']=json.dumps(plans)
    st.download_button('Save scenario evidence',output.to_csv(index=False),'TerraRoute_scenario_evidence.csv','text/csv')
    return {'scenario':preset,'delta_c':delta,'rain_factor':rain_factor,'historical_year':year,'calendar_assumptions':plans,'results':output.drop(columns=['profile','calendar_assumptions']).to_dict('records')}
