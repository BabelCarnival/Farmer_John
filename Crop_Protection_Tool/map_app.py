"""Map-led rotation decision support. AI assistance disclosed in SOURCES.md."""
from pathlib import Path
import json
import calendar
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from map_layers import grid_geojson, smooth_overlay
from analysis_v2 import parse_history,annual_exposure,monthly_exposure
from data_access import load_environment
from recommender import recommend
from crop_catalog import REFERENCES
from exposure import compare
from map_layers import polygon_mask
from datetime import date
from exposure import load_daily, history, load_modis
from ollama_chat import installed_models, ask
from report_help import answer_report_question, QUESTIONS

ROOT=Path(__file__).parent
st.set_page_config(page_title='TerraRoute',page_icon='https://i.imgur.com/4NhKhEe.png',layout='wide')
st.markdown('''<style>@keyframes logofade{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}[data-testid="stImage"] img{animation:logofade 1.6s ease-out}.stApp{background:#f4f7f1}.block-container{max-width:1350px;padding-top:4rem}h1,h2,h3{color:#184b38}[data-testid="stMetric"]{background:white;padding:14px;border-radius:12px;border:1px solid #dce7d8}.stButton>button{min-height:45px}</style>''',unsafe_allow_html=True)
st.components.v1.html('''<script>
const P=window.parent,D=P.document;
if(!P.sessionStorage.getItem("tr-intro")&&!D.getElementById("tr-intro")){
    P.sessionStorage.setItem("tr-intro","1");
    const css=D.createElement("style");
    css.textContent="#tr-intro{position:fixed;inset:0;z-index:9999999;background:#f4f7f1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;transition:opacity .7s ease}#tr-intro img{width:min(340px,70vw);animation:trpulse 1.6s ease-in-out infinite}#tr-intro .bar{width:min(220px,50vw);height:4px;border-radius:2px;background:#dce7d8;overflow:hidden}#tr-intro .bar i{display:block;height:100%;width:40%;border-radius:2px;background:#2e9e6b;animation:trslide 1.2s ease-in-out infinite}@keyframes trpulse{0%,100%{opacity:.55;transform:scale(.97)}50%{opacity:1;transform:scale(1)}}@keyframes trslide{0%{transform:translateX(-100%)}100%{transform:translateX(350%)}}";
    D.head.appendChild(css);
    const o=D.createElement("div");o.id="tr-intro";
    o.innerHTML='<img src="https://i.imgur.com/k28tRZs.png"><div class="bar"><i></i></div>';
    D.body.appendChild(o);
    setTimeout(()=>{o.style.opacity="0";setTimeout(()=>o.remove(),800);},2200);
    setTimeout(()=>{const x=D.getElementById("tr-intro");if(x)x.remove();},6000);
}
</script>''',height=0)
st.components.v1.html('''<script>
const P=window.parent,D=P.document;
["tr-rail","tr-rail-style"].forEach(i=>{const o=D.getElementById(i);if(o)o.remove();});
if(P.__trSpy)D.removeEventListener("scroll",P.__trSpy,true);
const items=[["location","1","Your Farm"],["history","2","Crop History"],["weather","3","Weather & Water"],["compare","4","Rotation Choices"],["whatif","5","Hotter, Drier or Wetter"],["insights","6","Download Insights"]];
const st=D.createElement("style");st.id="tr-rail-style";
st.textContent="#location,#history,#weather,#compare,#whatif,#insights{scroll-margin-top:90px}#tr-rail{position:fixed;left:14px;top:50%;transform:translateY(-50%);z-index:999999;background:#fff;border:1px solid #dce7d8;border-radius:24px;padding:10px 8px;width:46px;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column;gap:6px;box-shadow:0 6px 24px rgba(24,75,56,.15);transition:width .25s ease}#tr-rail:hover{width:235px}#tr-rail a{display:flex;align-items:center;gap:12px;height:30px;color:#184b38;text-decoration:none;white-space:nowrap;cursor:pointer}#tr-rail .n{flex:0 0 30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#eef3ea;font:600 13px sans-serif;transition:background .2s}#tr-rail .t{opacity:0;font:500 14px sans-serif;transition:opacity .15s}#tr-rail:hover .t{opacity:1}#tr-rail a:hover .n{background:#d7e8d0}#tr-rail a.active .n{background:#2e9e6b;color:#fff}#tr-rail a.active .t{color:#2e9e6b;font-weight:700}@media(max-width:900px){#tr-rail{display:none}}";
D.head.appendChild(st);
const nav=D.createElement("div");nav.id="tr-rail";
items.forEach(([id,n,label])=>{
  const a=D.createElement("a");a.dataset.id=id;
  const s1=D.createElement("span");s1.className="n";s1.textContent=n;
  const s2=D.createElement("span");s2.className="t";s2.textContent=label;
  a.append(s1,s2);
  a.onclick=e=>{e.preventDefault();const el=D.getElementById(id);if(el)el.scrollIntoView({behavior:"smooth",block:"start"});};
  nav.appendChild(a);
});
D.body.appendChild(nav);
function update(){
  let cur=items[0][0];
  items.forEach(([id])=>{const el=D.getElementById(id);if(el&&el.getBoundingClientRect().top<=170)cur=id;});
  nav.querySelectorAll("a").forEach(a=>a.classList.toggle("active",a.dataset.id===cur));
}
P.__trSpy=update;
D.addEventListener("scroll",update,true);
setTimeout(update,300);
</script>''',height=0)
st.image('https://i.imgur.com/k28tRZs.png', width=400)
st.write('Explore rotation choices for your crops, soil and priorities')

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
st.subheader('1. Your Farm',anchor='location',help='Map: a smooth color surface visualizes the supplied coarse temperature grid. Interpolation is for display only; calculations and selections use the original sampled values. Monthly T2M/Celsius column meanings are inferred pending original NASA export metadata.')
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
boundaries=json.loads((ROOT/'data/us_states_2024_20m.geojson').read_text())
state_feature=next((f for f in boundaries['features'] if f['id']==state),None)
if state_feature is None:
    st.error('No state outline found.');st.stop()
state_geometry=state_feature['geometry']
fig.update_layout(map_layers=[
    smooth_overlay(g,field,vmin,vmax,'YlOrRd' if field=='recent_c' else 'RdBu_r',clip_geometry=state_geometry),
    {'sourcetype':'geojson','source':state_feature,'type':'line','color':'#304a3e','line':{'width':1.4},'below':'traces'}
])
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
st.caption('Smooth shading is an inverse-distance visualization between sampled points, not additional observations or field-scale precision. Click the map or use the grid selector for an original value. Color is clipped to the selected Census state outline; distant unsampled areas stay transparent. Background tiles require internet.')
a,b,c=st.columns(3)
a.metric('Selected point',f'{selected.lat:.2f}, {selected.lon:.2f}')
b.metric('Recent summer mean temperature',f'{selected.recent_c:.1f}°C')
c.metric('Difference between periods',f'{selected.change_c:+.1f}°C')
st.caption('Historical comparison, not a forecast or an attribution of cause. Summer means June–August.')
site=raw[(raw.state==state)&raw.lat.eq(selected.lat)&raw.lon.eq(selected.lon)].sort_values('year')
with st.expander('See this point’s temperature history'):
    st.plotly_chart(px.line(site,x='year',y='summer_c',markers=True,labels={'summer_c':'Jun–Aug mean T2M (°C)','year':'Year'}),width='stretch')

st.subheader('2. Crop History',anchor='history')
mode=st.radio('Detailed evidence location',['Sample farm (Ames, Iowa)','My coordinates'],index=0 if state=='IOWA' else 1,key='location_mode_'+state,horizontal=True)
if mode=='Sample farm (Ames, Iowa)':
    latitude,longitude=42.03,-93.62
    st.caption('Detailed evidence below describes 42.03, −93.62, not every point on the regional map.')
else:
    a,b=st.columns(2)
    latitude=a.number_input('Farm latitude',-90.,90.,float(selected.lat),format='%.4f')
    longitude=b.number_input('Farm longitude',-180.,180.,float(selected.lon),format='%.4f')
inside_state=bool(polygon_mask(np.array([longitude]),np.array([latitude]),state_geometry)[0])
if not inside_state:st.warning('These coordinates lie outside the selected state outline. Regional crop options will not be transferred to them. Daily NASA point data can still be loaded.')
crop=st.selectbox('Main crop you intend to grow',['Corn','Soybean','Wheat','Rice','Sorghum','Other'])
st.caption('Enter real crop dates. These sample dates are illustrative until you replace them. Weather risk windows will be calculated from these dates; actual physiological stages still require field confirmation.')
default_history=pd.DataFrame({'Crop':['Corn','Soybean'],'Planting date':[date(2023,5,1),date(2024,5,1)],'Harvest date':[date(2023,10,1),date(2024,10,1)]})
edited=st.data_editor(default_history,num_rows='dynamic',hide_index=True,width='stretch',key='crop_history_editor',column_config={'Crop':st.column_config.SelectboxColumn(options=['Corn','Soybean','Wheat','Rice','Sorghum','Oats','Red clover','Other'],required=True),'Planting date':st.column_config.DateColumn(required=True),'Harvest date':st.column_config.DateColumn(required=True)})
try:crop_history,growing_months,gap_months=parse_history(edited)
except ValueError as e:st.warning(str(e));st.stop()
sequence=' → '.join(r['Crop'] for r in crop_history)
a,b=st.columns(2)
with a:
    texture=st.selectbox('Soil texture',['Unknown','Sandy','Loamy','Clayey'])
    drainage=st.selectbox('Drainage',['Unknown','Well drained','Moderate','Poor'])
    soil_source=st.text_input('Local soil source',placeholder='Soil test or local soil map, including date')
    water=st.selectbox('Water access',['Rainfed','Limited irrigation','Irrigated','Unknown'])
with b:
    priorities=st.multiselect('Priorities',['Improve soil cover','Conserve water','Diversify the sequence','Limit added work/equipment'],default=['Improve soil cover','Conserve water'])
    equipment=st.selectbox('Equipment/contractor capacity',['Unknown','No new equipment','Additional equipment/contractor possible'])
    market=st.selectbox('Added-crop market or forage outlet',['Unknown','No confirmed outlet','Confirmed market or forage use'])
    cover_feasible=st.selectbox('Can establish and terminate a cover crop?',['Unknown','Yes','No'])
profile=dict(crop=crop,sequence=sequence,crop_history=crop_history,region=state if inside_state else 'Unverified',texture=texture,drainage=drainage,soil_source=soil_source or 'Not supplied',water=water,priorities=priorities,equipment=equipment,market=market,cover_feasible=cover_feasible,sensitive_months=growing_months,bare_months=gap_months,latitude=latitude,longitude=longitude)
st.caption('Results update on input changes. Crop dates identify growing-month coverage, not confirmed crop stages or bare soil; retained residues and unrecorded cover can protect calendar gaps.')

st.subheader('3. Weather & Water',anchor='weather')
@st.cache_data(ttl=86400,show_spinner=False)
def fetch_point(lat,lon,start,end):return load_environment(lat,lon,start,end,True)
near_ames=abs(latitude-42.03)<.001 and abs(longitude+93.62)<.001
bundle=None
if mode=='Sample farm (Ames, Iowa)':
    try:bundle=fetch_point(42.03,-93.62,'2001-01-01','2024-12-31')
    except Exception:
        bundle={'daily':load_daily(ROOT/'data/power_daily.csv'),'metadata':{'source':'Supplied NASA POWER daily CSV','requested_coordinates':[42.03,-93.62],'units':{'tmax_c':'°C','precip_mm':'mm/day'},'period':'2001–2024'},'warnings':[]}
else:
    a,b=st.columns(2)
    start=a.date_input('Weather start date',date(2001,1,1),key='weather_start')
    end=b.date_input('Weather end date',date(2025,12,31),max_value=date.today(),key='weather_end')
    query_key=json.dumps([latitude,longitude,str(start),str(end)])
    if st.button('Load NASA weather and soil wetness',type='primary'):
        try:
            with st.spinner('Requesting this point from NASA POWER…'):
                loaded=fetch_point(latitude,longitude,str(start),str(end))
            st.session_state.point_data=loaded;st.session_state.point_key=query_key
        except Exception as e:st.error('NASA data could not be loaded. No other location was substituted. '+str(e))
    if st.session_state.get('point_key')==query_key:bundle=st.session_state.point_data
    else:st.info('Click Load NASA weather and soil wetness for these coordinates/dates. Rotation constraints below can still be reviewed before loading.')
daily=bundle['daily'] if bundle else None
if bundle:
    st.success(f"Loaded {len(daily):,} daily rows for {latitude:.4f}, {longitude:.4f}. Missing observations remain missing.")
    for warning in bundle['warnings']:st.warning(warning)
    wet=[c for c in ['GWETTOP','GWETROOT'] if c in daily and daily[c].notna().any()]
    if wet:
        st.plotly_chart(px.line(daily,x='date',y=wet,render_mode='svg',title='NASA modeled soil-wetness indices (not field moisture measurements)'),width='stretch')
        st.caption('Use units in the downloaded NASA metadata. Wetness fractions are not automatically equivalent to volumetric water content.')
    with st.expander('Data provenance, units and missing values'):
        st.json(bundle['metadata']);st.write(daily.isna().sum().to_dict())
        st.download_button('Download normalized NASA point data',daily.to_csv(index=False),'NASA_point_daily.csv','text/csv')
    with st.expander('Explore the weather history'):
        monthly=daily.set_index('date').resample('MS').agg(tmax_c=('tmax_c','mean'),precip_mm=('precip_mm',lambda x:x.sum(min_count=1))).reset_index()
        st.plotly_chart(px.line(monthly,x='date',y='tmax_c',render_mode='svg',labels={'tmax_c':'Monthly mean of daily maximum temperature (°C)','date':'Date'}),width='stretch')
        st.plotly_chart(px.bar(monthly,x='date',y='precip_mm',labels={'precip_mm':'Monthly precipitation total (mm)','date':'Date'}),width='stretch')
        st.caption('Monthly summaries make long records readable. All stress-test calculations still use daily observations; missing daily values are not filled.')

st.subheader('Periods Needing Closer Attention')
st.write('Growing months from entered dates: '+', '.join(calendar.month_abbr[m] for m in growing_months))
st.write('Calendar gaps to verify for soil cover: '+(', '.join(calendar.month_abbr[m] for m in gap_months) or 'None identified'))
st.caption('The growing-month union is a screening approximation across the entered crop history. It does not infer phenology, yield response or exposed soil from dates alone.')
year=None;window_table=None
if daily is not None:
    annual=annual_exposure(daily,growing_months);eligible=annual[annual.coverage>=.95]
    if eligible.empty:st.warning('No seasons have at least 95% valid daily coverage inside the entered growing months.')
    else:
        default=int(eligible.loc[eligible['index'].idxmax(),'year']);years=eligible.year.astype(int).tolist()
        year=st.selectbox('Historical season (default: highest combined exposure)',years,index=years.index(default))
        sample=daily[daily.date.dt.year==year]
        window_table=monthly_exposure(sample,growing_months)
        focus=window_table[window_table['Within entered crop season']].copy()
        focus['screen_rank']=focus['Heat days ≥35°C'].rank(pct=True)+focus['Longest rainfall gap (days)'].rank(pct=True)
        top=focus.nlargest(min(3,len(focus)),'screen_rank')
        st.write('Weather periods to inspect first: '+', '.join(calendar.month_abbr[int(m)] for m in top.Month))
        st.caption('Ranked within this replay year by heat-day and rainfall-gap exposure during the entered growing season. These are not automatically critical physiological stages. 35°C and <1 mm/day are screening settings, not crop-damage thresholds.')
        st.plotly_chart(px.bar(window_table,x='Month',y='Longest rainfall gap (days)',color='Within entered crop season',labels={'Month':'Month','Within entered crop season':'Inside your crop calendar'}),width='stretch')
        with st.expander('See monthly heat and rainfall values'):
            st.dataframe(window_table.round(1),hide_index=True,width='stretch')
if near_ames:
    with st.expander('Ames 2024 vegetation evidence'):
        m=load_modis(ROOT/'data/modis_2024.csv');m=m[(m.quality=='Good')&m.ndvi.notna()]
        st.plotly_chart(px.line(m,x='date',y='ndvi',markers=True),width='stretch')
        low=m[m.ndvi<.3];st.write(f'{len(low)} good-quality observations below illustrative NDVI 0.3. Candidate low-greenness periods need field validation; cloud filtering does not establish bare soil or crop identity.')
else:st.caption('Vegetation data have not been supplied for these coordinates. The Ames pixel is not substituted.')

st.subheader('4. Rotation Choices',anchor='compare')
options,blocked,gaps,weights=recommend(profile)
st.write('Compare what changes on your farm, then use Step 5 to check weather exposure.')
for msg in gaps:st.info(msg)
if blocked:
    with st.expander(f'Why {len(blocked)} option(s) were left out',expanded=True):
        for item in blocked:st.write('**'+item['option']+'** — '+item['reason'])
if len(options)<3:st.caption(f'{len(options)} option(s) available with your current inputs. Options needing unsupported local evidence or conflicting with your constraints are left out.')

def priority_explanation(candidate):
    notes=[]
    current=candidate['id']=='current'
    if 'Improve soil cover' in priorities:
        notes.append('Keeps existing cover practices; check gaps and residues.' if current else 'Adds an opportunity for living cover; establishment must be confirmed.')
    if 'Diversify the sequence' in priorities:
        notes.append('Keeps your current crop mix.' if current else 'Adds rye between cash crops.' if candidate['id']=='cover' else 'Adds a small grain and red clover to the cycle.')
    if 'Limit added work/equipment' in priorities:
        notes.append('No crop-system change proposed.' if current else 'Adds sowing and termination tasks.' if candidate['id']=='cover' else 'Needs more crop operations and equipment or a contractor.')
    if 'Conserve water' in priorities:
        notes.append('Water savings have not been established.' if current else 'Living cover uses water; review moisture and termination timing.')
    return notes or ['Select a priority in Step 1 to see the relevant trade-offs.']

shared_notes=[]
for c in options:
    for text in [c['priority_note'],c['soil_note']]:
        if text and text not in shared_notes:shared_notes.append(text)
for offset in range(0,len(options),3):
    for column,c in zip(st.columns(min(3,len(options)-offset)),options[offset:offset+3]):
        with column,st.container(border=True):
            st.caption('YOUR CURRENT APPROACH' if c['id']=='current' else 'ALTERNATIVE TO EXPLORE')
            st.markdown('### '+c['name'])
            st.write('**Crop sequence**')
            st.write(c['sequence'])
            st.write('**What changes**')
            st.write('Keep your current crop system as the comparison point.' if c['id']=='current' else 'Plant cereal rye after corn, before soybean; confirm establishment and termination locally.' if c['id']=='cover' else 'Extend the cycle with a small grain and red clover; confirm a local crop calendar and outlet.')
            st.write('**For your priorities**')
            for note in priority_explanation(c):st.write('• '+note)
            st.write('**Main trade-off:** '+c['risk'])
            st.write('**Before trying it:** '+('Confirm current residue cover and uncovered months.' if c['id']=='current' else 'Check seed, sowing access, soil moisture and termination timing.' if c['id']=='cover' else 'Confirm machinery, crop timing and a market or forage use.'))
            with st.expander('Supporting evidence'):
                for key in c['source']:st.markdown('['+REFERENCES[key]['note']+']('+REFERENCES[key]['url']+')')
                if not c['source']:st.write('Your entered crop history; no change assumed.')

st.markdown('#### The practical differences')
comparison=[]
for c in options:
    kind=c['id']
    comparison.append({'Option':c['name'],
        'Soil cover': 'Existing practices' if kind=='current' else 'Cover between cash crops' if kind=='cover' else 'Longer cycle with additional cover',
        'Crop diversity': 'Your current mix' if kind=='current' else 'Rye added between crops' if kind=='cover' else 'Small grain and clover added',
        'Extra work': 'No system change proposed' if kind=='current' else 'Sow and terminate rye' if kind=='cover' else 'More crop operations; check machinery',
        'Water': 'Not calculated' if kind=='current' else 'Living cover uses water; timing matters'})
st.table(pd.DataFrame(comparison).set_index('Option'))
st.caption('These describe the proposed management changes. They are not measured benefits or a percentage chance of success. NASA weather exposure is checked separately in Step 5.')
with st.expander('Local checks and comparison method'):
    for note in shared_notes:st.write(note)
    st.write('Alternatives are screened using your stated equipment, crop-outlet and cover-management constraints. Unknown answers still need confirmation. The reviewed alternative catalogue currently covers Iowa corn/soybean systems only.')
    st.write('For ordering alternatives, selected cover, diversity and work priorities have equal weights on catalogue attributes coded 0–2. This is a planning heuristic, not validated agronomic suitability. Water savings are not scored. The internal values remain in the technical report for transparency; they are not shown as a farmer recommendation percentage.')

st.subheader('5. Hotter, Drier or Wetter',anchor='whatif')
scenario_result=None;scenario_settings=None
if daily is not None and year is not None:
    scenario=st.selectbox('What-if scenario',['Historical','Hotter +2°C','Drier −20%','Wetter +20%','Custom'])
    delta=2. if scenario=='Hotter +2°C' else 0.;factor=.8 if scenario=='Drier −20%' else 1.2 if scenario=='Wetter +20%' else 1.
    if scenario=='Custom':
        delta=st.slider('Temperature offset (°C)',-2.,5.,2.,.5);factor=st.slider('Rainfall percentage',50,150,80,5)/100
    cover_months=st.multiselect('Assumed cover months for alternative options (confirm locally)',range(1,13),[3,4,10,11],format_func=lambda m:calendar.month_abbr[m])
    plans=[{'name':c['name'],'sensitive':growing_months,'bare':gap_months if c['id']=='current' else [m for m in gap_months if m not in cover_months]} for c in options]
    scenario_settings={'historical_year':int(year),'temperature_offset_c':delta,'rainfall_multiplier':factor,'assumed_cover_months':cover_months,'calendar_plans':plans}
    base=compare(daily,plans,year,35,1);altered=daily.copy();altered['tmax_c']+=delta;altered['precip_mm']*=factor
    result=compare(altered,plans,year,35,1)
    scenario_result=pd.DataFrame({'Strategy':result.strategy,'Baseline heat days':base.heat_days,'Scenario heat days':result.heat_days,'Baseline dry run (days)':base.dry_spell_days,'Scenario dry run (days)':result.dry_spell_days,'Baseline rain in calendar gaps (mm)':base.bare_rain_mm,'Scenario rain in assumed uncovered months (mm)':result.bare_rain_mm})
    a,b=st.columns(2)
    a.metric('Hot days inside your crop calendar',f'{int(result.heat_days.iloc[0])} days',None if scenario=='Historical' else f'{int(result.heat_days.iloc[0]-base.heat_days.iloc[0]):+d} days vs historical')
    b.metric('Longest rainfall gap inside your crop calendar',f'{int(result.dry_spell_days.iloc[0])} days',None if scenario=='Historical' else f'{int(result.dry_spell_days.iloc[0]-base.dry_spell_days.iloc[0]):+d} days vs historical')
    st.caption(f'Replaying {year}. Hot day: maximum temperature ≥35°C. Rainfall gap: consecutive days below 1 mm. The crop calendar is shared across these options, so these weather counts are shown once.')
    cover_chart=pd.DataFrame({'Strategy':result.strategy,'Rain during assumed uncovered months (mm)':result.bare_rain_mm})
    st.plotly_chart(px.bar(cover_chart,x='Strategy',y='Rain during assumed uncovered months (mm)',color_discrete_sequence=['#287554']),width='stretch')
    st.caption('This chart shows rainfall coinciding with your assumed uncovered months. Lower values reflect the calendar assumption only; they do not measure reduced erosion, water savings or cover-crop success. Cover months have not been inferred from NASA data.')
    if scenario=='Historical':st.info('Historical replay: no weather change is applied. Select Hotter, Drier or Wetter to compare a changed scenario.')
    with st.expander('Compare the detailed numbers'):
        shown=scenario_result if scenario!='Historical' else scenario_result[['Strategy','Baseline heat days','Baseline dry run (days)','Baseline rain in calendar gaps (mm)']]
        st.dataframe(shown.round(1),hide_index=True,width='stretch')
        st.caption('Each option receives the same weather. This is a sensitivity test, not a future weather forecast or a simulation of crop physiology and soil water balance.')
else:st.info('Load location-specific daily weather to run scenarios. There is no silent temperature-only substitute for missing rainfall.')

st.subheader('6. Download Insights',anchor='insights')
st.write('Use this comparison to shortlist a rotation for local review. Before trying it, check soil moisture, crop timing, cover establishment, equipment and a crop outlet.')
if crop.lower() in REFERENCES:st.markdown('['+REFERENCES[crop.lower()]['note']+']('+REFERENCES[crop.lower()]['url']+')')
export={'farm_inputs':profile,'data_metadata':bundle['metadata'] if bundle else None,'options':options,'excluded':blocked,'missing_evidence':gaps,'preference_weights':weights,'scenario_settings':scenario_settings,'scenario_results':scenario_result.to_dict('records') if scenario_result is not None else None}
summary=['TerraRoute — farm decision summary',f'Location: {latitude:.4f}, {longitude:.4f}',f'Crop history: {sequence}',f'Intended crop: {crop}',f'Priorities: {", ".join(priorities) or "None selected"}',f'Soil: {texture}; drainage: {drainage}; source: {soil_source or "Not supplied"}',f'Water access: {water}','',answer_report_question(QUESTIONS[0],export),'',answer_report_question(QUESTIONS[1],export),'',answer_report_question(QUESTIONS[2],export),'',answer_report_question(QUESTIONS[3],export)]
st.download_button('Download my farm summary', '\n\n'.join(summary),'TerraRoute_farm_summary.txt','text/plain')
with st.expander('Download the full data report'):
    st.download_button('Download technical report (JSON)',json.dumps(export,default=str,indent=2),'TerraRoute_decision_report.json','application/json')
st.markdown('### Ask about your comparison')
st.caption('Use the chat bubble at the bottom left of the page to ask questions about your results.')
@st.cache_data(ttl=30,show_spinner=False)
def available_models():
    try:return installed_models()
    except Exception:return []
models=available_models()
model=None
with st.expander('Optional: connect Ollama for open-ended AI questions'):
    st.write('Ollama must run on the same computer as the Streamlit Python process. On the public Streamlit site, localhost belongs to the hosted server; it cannot reach Ollama on your Mac.')
    st.code('ollama pull llama3.2:3b')
    st.write('For local AI chat, start Ollama and run this app locally. Public AI chat requires a separately configured hosted service; no hosted AI credentials are bundled.')
    if models:model=st.selectbox('Connected Ollama model',models)
    if st.button('Check Ollama connection again'):
        available_models.clear();st.rerun()
if not models:st.info('Report helper is ready. It answers the common questions using your current results. Open-ended AI chat is not connected on this server.')
else:st.caption('Ollama AI is connected. Check its explanations against the supporting data.')
context=json.dumps({**export,'reference_notes':REFERENCES,'limits':'Planning preference index is not validated suitability. Soil wetness is modeled and not a field soil test. Never substitute Ames for another coordinate.'},default=str)
if 'map_chat' not in st.session_state:st.session_state.map_chat=[]
if 'chat_seq' not in st.session_state:st.session_state.chat_seq=0

def ask_chat(question=None):
    text=(question or st.session_state.get('chat_text','')).strip()
    if text:st.session_state.chat_pending=text

new_reply=False
with st.container(key='chatbubble'):
    with st.popover('\u200b'):
        pending=st.session_state.pop('chat_pending',None)
        if pending:
            with st.spinner('Reading your current report…'):
                if model:
                    try:reply=ask(model,pending,context,st.session_state.map_chat)
                    except Exception:reply=answer_report_question(pending,export)
                else:reply=answer_report_question(pending,export)
            st.session_state.map_chat.append((pending,reply))
            st.session_state.chat_seq+=1
            new_reply=True
        if st.session_state.map_chat:
            box=st.container(height=330)
            for question,reply in st.session_state.map_chat:
                with box.chat_message('user'):st.write(question)
                with box.chat_message('assistant'):st.write(reply)
        else:
            st.caption('Ask about your options, weather test, missing data or sources.')
            for question in QUESTIONS:
                st.button(question,key='quick_'+question,on_click=ask_chat,args=(question,),use_container_width=True)
        with st.form('chat_form',clear_on_submit=True):
            st.text_input('Message',key='chat_text',placeholder='Type your question…',label_visibility='collapsed')
            st.form_submit_button('Send',on_click=ask_chat,use_container_width=True)
    if new_reply:
        st.markdown(f'<span class="chatbadge" id="cb{st.session_state.chat_seq}">1</span>',unsafe_allow_html=True)
st.components.v1.html('''<script>
const P=window.parent,D=P.document;
const old=D.getElementById("chat-style");if(old)old.remove();
const css=D.createElement("style");css.id="chat-style";
css.textContent=`.st-key-chatbubble{position:fixed!important;left:14px;bottom:28px;width:54px;height:54px;z-index:999998}
.st-key-chatbubble [data-testid="stPopover"]{width:54px}
.st-key-chatbubble [data-testid="stPopover"]>button,.st-key-chatbubble [data-testid="stPopoverButton"]{width:54px;height:54px;min-height:54px;padding:0;border-radius:50%;background:#fff url(https://i.imgur.com/4NhKhEe.png) center/68% no-repeat!important;border:2px solid #2e9e6b!important;font-size:0!important;box-shadow:0 6px 20px rgba(24,75,56,.3);transition:transform .15s ease}
.st-key-chatbubble [data-testid="stPopover"]>button *{font-size:0!important;color:transparent!important}
.st-key-chatbubble [data-testid="stPopover"]>button:hover,.st-key-chatbubble [data-testid="stPopoverButton"]:hover{transform:scale(1.12)}
.st-key-chatbubble [data-testid="stPopover"]>button svg,.st-key-chatbubble [data-testid="stPopoverButton"] svg,.st-key-chatbubble [data-testid="stIconMaterial"]{display:none}
.chatbadge{position:fixed;left:52px;bottom:66px;min-width:20px;height:20px;padding:0 5px;box-sizing:border-box;border-radius:10px;background:#e53935;color:#fff;font:700 12px/20px sans-serif;text-align:center;z-index:999999;pointer-events:none}
[data-testid="stPopoverBody"]{width:360px;max-width:92vw;max-height:80vh;border-radius:18px}`;
D.head.appendChild(css);
if(P.__chatTimer)clearInterval(P.__chatTimer);
P.__chatTimer=setInterval(()=>{
  const body=D.querySelector('[data-testid="stPopoverBody"]');
  const open=body&&body.getBoundingClientRect().width>0;
  if(open){
    const b=D.querySelector(".chatbadge");if(b)b.style.display="none";
    body.querySelectorAll("div").forEach(d=>{
      if(d.scrollHeight>d.clientHeight+5&&/(auto|scroll)/.test(P.getComputedStyle(d).overflowY)&&d.__h!==d.scrollHeight){d.__h=d.scrollHeight;d.scrollTop=d.scrollHeight;}
    });
  }
},300);
</script>''',height=0)
with st.expander('Full sources and methods'):st.markdown((ROOT/'SOURCES.md').read_text())
st.caption('TerraRoute prototype. NASA environmental observations support local decisions; local crop/soil validation remains necessary. AI assistance disclosed in SOURCES.md.')
