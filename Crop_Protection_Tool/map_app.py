"""Map-led rotation decision support. AI assistance disclosed in SOURCES.md."""
from pathlib import Path
import json
import calendar
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from map_layers import grid_geojson, smooth_overlay
from rotation_rules import review
from journey import environment, vulnerabilities, stress
from exposure import load_daily, history, load_modis
from ollama_chat import installed_models, ask

ROOT=Path(__file__).parent
st.set_page_config(page_title='TerraRoute',page_icon='🌱',layout='wide')
# Palette follows the viewer's active Streamlit theme (light/dark, incl. "use system setting")
# so text always contrasts with its background.
_dark=getattr(getattr(st.context,'theme',None),'type',None)=='dark'
_c=dict(bg='#0f1a14',heading='#8fd4b0',card='#1a2a21',border='#2e4a3a') if _dark else \
   dict(bg='#f4f7f1',heading='#184b38',card='#ffffff',border='#dce7d8')
st.markdown(f'''<style>.stApp{{background:{_c['bg']}}}.block-container{{max-width:1350px;padding-top:1.6rem}}h1,h2,h3{{color:{_c['heading']}}}[data-testid="stMetric"]{{background:{_c['card']};padding:14px;border-radius:12px;border:1px solid {_c['border']}}}.stButton>button{{min-height:45px}}</style>''',unsafe_allow_html=True)
st.title('TerraRoute')
st.caption('NASA-powered crop rotation decision support')
st.write('Explore rotation choices for your crops, soil and priorities — supported by NASA environmental data.')

@st.cache_data
def read_grid():
    p=ROOT/'data/usa_temperature_2000_2025.xlsx'
    r=pd.read_excel(p,header=None,engine='openpyxl')
    r.columns=['state','parameter','year','lat','lon']+list(range(1,13))+['annual']
    r['state']=r.state.replace('STATE',np.nan).ffill().bfill().str.upper().str.strip().replace({'ILLNOIS':'ILLINOIS'})
    for c in range(1,13):r[c]=pd.to_numeric(r[c],errors='coerce').mask(lambda x:x<=-900)
    r['summer_c']=r[[6,7,8]].mean(axis=1)
    keys=['state','lat','lon']
    early=r[r.year.between(2000,2009)].groupby(keys).summer_c.mean().rename('early_c')
    recent=r[r.year.between(2016,2025)].groupby(keys).summer_c.mean().rename('recent_c')
    g=pd.concat([early,recent],axis=1).reset_index()
    g['change_c']=g.recent_c-g.early_c
    g['point_id']=g.state+'_'+g.lat.astype(str)+'_'+g.lon.astype(str)
    return r,g

try:raw,grid=read_grid()
except Exception as e:st.error(f'Could not read the temperature workbook: {e}');st.stop()
st.subheader('1. Understand your farm · choose a location')
st.caption('Map: a smooth color surface visualizes the supplied coarse temperature grid. Interpolation is for display only; calculations and selections use the original sampled values. Monthly T2M/Celsius column meanings are inferred pending original NASA export metadata.')
states=sorted(grid.state.unique());state=st.selectbox('State',states,index=states.index('IOWA'))
g=grid[grid.state==state].copy().reset_index(drop=True)
nearest=int(((g.lat-42.03)**2+(g.lon+93.62)**2).idxmin()) if state=='IOWA' else 0
point_key='grid_choice_'+state
if point_key not in st.session_state:st.session_state[point_key]=nearest
point=st.selectbox('Grid cell (also selectable on the map)',range(len(g)),key=point_key,format_func=lambda i:f'{g.iloc[i].lat:.3f}, {g.iloc[i].lon:.3f}')
color=st.radio('Color the map by',['Recent summer temperature','Change between two periods'],horizontal=True)
field='recent_c' if color=='Recent summer temperature' else 'change_c'
map_key='temperature_cells_'+state+'_'+field
fig=px.choropleth_map(g,geojson=grid_geojson(g),locations='point_id',featureidkey='id',color=field,
    custom_data=['point_id'],color_continuous_scale='YlOrRd' if field=='recent_c' else 'RdBu_r',
    range_color=(-max(abs(g[field].min()),abs(g[field].max())),max(abs(g[field].min()),abs(g[field].max()))) if field=='change_c' else (float(g[field].min()),float(g[field].max())),
    zoom=4 if state in ['ALASKA','TEXAS'] else 5,opacity=.001,
    center={'lat':float(g.lat.mean()),'lon':float(g.lon.mean())},map_style='open-street-map',
    hover_data={'state':True,'lat':':.3f','lon':':.3f','recent_c':':.1f','change_c':':.1f','point_id':False},
    labels={'recent_c':'Jun–Aug mean T2M, 2016–2025 (°C)','change_c':'2016–2025 minus 2000–2009 (°C)'})
fig.update_traces(marker_line_width=0)
vmin,vmax=(float(g[field].min()),float(g[field].max()))
if field=='change_c':vmin,vmax=-max(abs(vmin),abs(vmax)),max(abs(vmin),abs(vmax))
fig.update_layout(map_layers=[smooth_overlay(g,field,vmin,vmax,'YlOrRd' if field=='recent_c' else 'RdBu_r')])
fig.update_layout(height=460,margin=dict(l=0,r=0,t=0,b=0))
def choose_cell():
    event=st.session_state.get(map_key,{})
    points=event.get('selection',{}).get('points',[])
    if points:
        p=points[-1];custom=p.get('customdata',[])
        pid=custom[0] if custom else p.get('location')
        matches=g.index[g.point_id==pid].tolist()
        if matches:st.session_state[point_key]=int(matches[0])
st.plotly_chart(fig,width='stretch',key=map_key,on_select=choose_cell,selection_mode='points')
selected=g.iloc[st.session_state[point_key]]
st.caption('Smooth shading is an inverse-distance visualization between sampled points, not additional observations or field-scale precision. Click the map or use the grid selector for an original value. Unsampled edges fade out. Background tiles require internet.')
a,b,c=st.columns(3)
a.metric('Selected point',f'{selected.lat:.2f}, {selected.lon:.2f}')
b.metric('Recent summer mean temperature',f'{selected.recent_c:.1f}°C')
c.metric('Difference between periods',f'{selected.change_c:+.1f}°C')
st.caption('Historical comparison, not a forecast or an attribution of cause. Summer means June–August.')
site=raw[(raw.state==state)&raw.lat.eq(selected.lat)&raw.lon.eq(selected.lon)].sort_values('year')
with st.expander('See this point’s temperature history'):
    st.plotly_chart(px.line(site,x='year',y='summer_c',markers=True,labels={'summer_c':'Jun–Aug mean T2M (°C)','year':'Year'}),width='stretch')

st.subheader('Farm history, soil and priorities')
left,right=st.columns(2)
with left:
    crop=st.selectbox('Main crop you want to keep',['Corn','Soybean','Wheat','Rice','Sorghum','Other'])
    sequence=st.text_input('Your current crop sequence','Corn → soybean')
    texture=st.selectbox('Soil texture',['Unknown','Sandy','Loamy','Clayey'])
    drainage=st.selectbox('Drainage',['Unknown','Well drained','Moderate','Poor'])
    soil_source=st.text_input('Soil information source (optional)',placeholder='For example: a soil test or local soil survey')
    sensitive_months=st.multiselect('Crop months needing closer attention (local assumption)',range(1,13),[6,7,8],format_func=lambda n:calendar.month_abbr[n])
    bare_months=st.multiselect('Expected uncovered months (local assumption)',range(1,13),[1,2,3,4,10,11,12],format_func=lambda n:calendar.month_abbr[n])
with right:
    water=st.selectbox('Water access',['Rainfed','Limited irrigation','Irrigated','Unknown'])
    priorities=st.multiselect('What matters most to you?',['Improve soil cover','Conserve water','Diversify the sequence','Limit added work/equipment'],default=['Improve soil cover','Conserve water'])
    equipment=st.selectbox('Equipment constraints',['Unknown','No new equipment','Additional equipment/contractor possible'])
    market=st.selectbox('Outlet for an added crop',['Unknown','No confirmed outlet','Confirmed market or forage use'])
if not sequence.strip() or not sensitive_months:
    st.warning('Enter your current crop sequence and at least one attention month to see the comparison.');st.stop()
profile=dict(crop=crop,sequence=sequence.strip(),texture=texture,drainage=drainage,soil_source=soil_source or 'Not supplied',water=water,priorities=priorities,equipment=equipment,market=market,region=state,sensitive_months=sensitive_months,bare_months=bare_months)
st.caption('Results below update automatically. For typed text, press Enter or click outside the box to apply your edit.')
st.write('**Inputs used:** '+profile['crop']+'; '+profile['texture']+' soil; '+profile['drainage']+' drainage; '+profile['water']+'. Priorities: '+(', '.join(profile['priorities']) or 'None selected'))
st.write(f'**Selected temperature evidence:** {state}, {selected.lat:.3f}, {selected.lon:.3f}: June–August mean {selected.recent_c:.1f}°C in 2016–2025; difference {selected.change_c:+.1f}°C from 2000–2009. This regional trend does not establish crop suitability or select cover species.')
near_ames=state=='IOWA' and np.hypot((selected.lat-42.03)*111,(selected.lon+93.62)*82)<30
environment(selected,state,near_ames)
evidence=vulnerabilities(profile,near_ames)
report,gaps=review(profile)
st.caption('Soil and management inputs are supplied by you, not inferred from the temperature map. No local soil dataset is bundled.')

st.subheader('4. Compare three rotation strategies')
st.write('Keep your intended crop in the sequence and compare options. These are candidates for local review, not a suitability ranking or predicted soil-health gains.')
for _,r in report.iterrows():
    with st.container(border=True):
        st.markdown('### '+r.Strategy)
        st.write('**Sequence:** '+r.Sequence)
        a,b=st.columns(2)
        a.write('**Potential soil role:** '+r['Potential soil role'])
        a.write('**Connection to your priorities:** '+r['Priority connection'])
        b.write('**Check first:** '+r['Review before choosing'])
        b.write('**Feasibility:** '+r.Feasibility)
        st.write('**Why this advice changed:** '+r['Inputs affecting this option'])
        st.markdown('**Evidence:** '+r['Evidence basis'])
if gaps:
    st.warning('Before choosing: '+' '.join(gaps))
if crop=='Corn':st.info('Crop characteristic: pollination is sensitive to water stress. Confirm tasseling/silking in the field; monthly temperatures do not identify the actual crop stage. Source: Iowa State Extension corn pollination guide.')
elif crop=='Soybean':st.info('Crop characteristic: reproductive stages, especially R3–R6, deserve attention under water deficits. Confirm actual stage locally. Source: Iowa State Extension soybean drought guidance.')
export=report.copy();export['selected_state']=state;export['lat']=selected.lat;export['lon']=selected.lon
export['farm_inputs']=json.dumps(profile);export['data_limit']='Regional temperature context only; no field-level suitability/benefit model.'
st.download_button('Save my rotation comparison',export.to_csv(index=False),'my_rotation_options.csv','text/csv')

scenario_context=stress(profile,selected,state,near_ames,evidence)
ames_context={k:v for k,v in (evidence or {}).items() if k!='daily'}

st.subheader('6. Explain the results and ask questions')
st.write('Every option shows its potential soil role, disadvantages, evidence and missing information. Soil-health benefits are not measured or predicted by this prototype.')
with st.expander('Connect local Ollama chat'):
    st.write('Open Ollama on this computer. Install a model with the command below, then refresh the page. Chat uses local inference.')
    st.code('ollama pull llama3.2:3b')
try:models=installed_models()
except Exception:models=[]
model=st.selectbox('Local model',models) if models else None
if not models:st.caption('Chat is not connected. The map and rotation comparison work without Ollama.')
context=json.dumps({'selected_region':state,'selected_grid':[selected.lat,selected.lon],
    'summer_mean_T2M_2016_2025':selected.recent_c,'historical_difference_c':selected.change_c,
    'farm_inputs':profile,'rotation_review':report.to_dict('records'),'Ames_separate_example':ames_context,'scenario_stress_test':scenario_context,
    'limitations':'No predicted benefits, local soil database, yield model or suitability ranking. State workbook monthly units/schema inferred; user attributes it to NASA.'},default=str)
if st.session_state.get('map_context')!=context:
    st.session_state.map_chat=[];st.session_state.map_context=context
for q,a in st.session_state.map_chat:
    with st.chat_message('user'):st.write(q)
    with st.chat_message('assistant'):st.write(a)
q=st.chat_input('Ask about the evidence or a rotation trade-off',disabled=not models)
if q:
    try:
        with st.chat_message('user'):st.write(q)
        with st.spinner('Reading your comparison…'):a=ask(model,q,context,st.session_state.map_chat)
        st.session_state.map_chat.append((q,a))
        with st.chat_message('assistant'):st.write(a)
    except Exception as e:st.error('Could not contact the local model. Check Ollama and try again.');st.caption(str(e))
with st.expander('Sources, methods and limits'):
    st.markdown((ROOT/'SOURCES.md').read_text())
    st.download_button('Download sources',(ROOT/'SOURCES.md').read_text(),'SOURCES.md','text/markdown')
st.caption('Independent prototype. AI assistance used in development. NASA data does not by itself establish agronomic suitability. Local expert review is needed.')
