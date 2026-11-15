"""Transparent review rules; no predicted yield, soil benefit or suitability score."""
import pandas as pd

def review(profile):
    priorities=profile['priorities']; water=profile['water'];soil=profile['texture'];drain=profile['drainage']
    seq=profile['sequence'];equipment=profile['equipment'];market=profile['market']
    common=[]
    if soil=='Unknown':common.append('Confirm soil texture and available water capacity.')
    if drain=='Unknown':common.append('Confirm drainage and field trafficability.')
    if drain=='Poor':common.append('Review establishment and machinery access under wet conditions.')
    if soil=='Sandy':common.append('Measure soil moisture; rainfall history alone cannot establish stored water.')
    rows=[{'Strategy':'1 · Keep the current sequence','Sequence':seq,'Potential soil role':'Baseline; soil cover depends on existing residue and tillage.',
           'Priority connection':'Baseline for reviewing change and implementation effort.',
           'Review before choosing':'Document current residue cover, bare periods and crop history.',
           'Feasibility':'Baseline — management details need confirmation'},
          {'Strategy':'2 · Retain crops and add a suitable cover','Sequence':seq+' + locally suitable cover crop',
           'Potential soil role':'Potential additional cover and residue between cash crops [ISU cover crops].',
           'Priority connection':'Relevant to soil cover. Water-conservation benefits depend on management.',
           'Review before choosing':'Cover establishment, seed cost, timing, termination and soil moisture. Living cover uses water [NRCS].',
           'Feasibility':'Needs local species and timing review'},
          {'Strategy':'3 · Retain crops and diversify the cycle','Sequence':seq+' → locally suitable small grain/legume → return to intended crop',
           'Potential soil role':'Explore additional cover and a different crop family; local evidence needed for crop-specific benefits.',
           'Priority connection':'Relevant to diversification; changes timing, markets and equipment requirements.',
           'Review before choosing':'Crop/soil suitability, crop-family conflicts, calendar, equipment and a market or forage use.',
           'Feasibility':'Needs local agronomic and market review'}]
    if water in ['Rainfed','Limited irrigation']:
        rows[1]['Review before choosing']+=' Check moisture before establishing/terminating cover; do not assume it saves water.'
    if equipment=='No new equipment':rows[2]['Feasibility']='Equipment constraint — check contractors or alternatives'
    if market=='No confirmed outlet':rows[2]['Feasibility']='Market constraint — no confirmed outlet'
    if 'Limit added work/equipment' in priorities:rows[0]['Priority connection']+=' Relevant to limiting management changes; actual costs are unknown.'
    if 'Improve soil cover' in priorities:rows[1]['Priority connection']+=' Matches stated soil-cover priority.'
    if 'Diversify the sequence' in priorities:rows[2]['Priority connection']+=' Matches stated diversification priority.'
    if profile['crop'] not in ['Corn','Soybean']:common.append('This prototype has no reviewed crop-stage guidance for the chosen crop; obtain local crop information.')
    if profile['crop'].lower() not in seq.lower() and profile['crop']!='Other':
        common.append('Your selected main crop does not appear in the typed sequence; confirm the plan before choosing.')
    triggers=[[],[],[]]
    if soil=='Sandy':
        rows[1]['Review before choosing']+=' Sandy texture reported: check available water capacity and stored moisture before adding a living cover.'
        triggers[1].append('Sandy soil → added moisture check')
    if drain=='Poor':
        for i in [1,2]:
            rows[i]['Review before choosing']+=' Poor drainage reported: check trafficability and crop establishment.'
            triggers[i].append('Poor drainage → establishment and machinery-access check')
    if water in ['Rainfed','Limited irrigation']:
        triggers[1].append(water+' → cover water-use trade-off highlighted')
    if equipment=='No new equipment':
        triggers[2].append('No new equipment → contractor or alternative needed')
    if market=='No confirmed outlet':
        triggers[2].append('No confirmed outlet → added-crop market unresolved')
    if equipment=='No new equipment' and market=='No confirmed outlet':
        rows[2]['Feasibility']='Both equipment and market constraints need resolution'
    for priority,i in [('Improve soil cover',1),('Conserve water',1),('Diversify the sequence',2),('Limit added work/equipment',0)]:
        if priority in priorities:triggers[i].append('Priority: '+priority)
    if 'Conserve water' in priorities:
        rows[1]['Priority connection']+=' Water priority: compare residue benefits with water consumed by living cover; no saving is assumed.'
    crop_pair='corn' in seq.lower() and ('soy' in seq.lower())
    if profile.get('region')=='IOWA' and crop_pair and profile['crop'] in ['Corn','Soybean']:
        rows[1]['Sequence']=seq+'; consider cereal rye after corn before soybean'
        rows[1]['Potential soil role']='Explore additional living cover and residue between cash crops; local establishment and management must be verified.'
        rows[1]['Evidence basis']='[Iowa cover-crop recipe: post corn, going to soybean](https://store.extension.iastate.edu/product/15548.pdf). This supports an option to review, not measured benefits for this farm.'
        rows[2]['Sequence']='Corn → soybean → small grain + red clover → return to corn (example cycle)'
        rows[2]['Evidence basis']='[Davis et al., 2012, PLOS ONE](https://doi.org/10.1371/journal.pone.0047149): an Iowa trial studied this type of diversified rotation under different management. Trial outcomes are not transferred to this farm.'
    else:
        rows[1]['Evidence basis']='[Cover crop water/termination context, NRCS](https://www.nrcs.usda.gov/sites/default/files/2025-04/Cover_Crop_Termination-FS_0.pdf). Specific species and suitability are not validated for this location.'
        rows[2]['Evidence basis']='A generic diversification candidate only; local crop and soil evidence is missing. Do not transfer the Iowa study to this location without review.'
    rows[0]['Evidence basis']='Your reported crop history is the baseline. Regional temperature evidence informs context, not field-level crop performance.'
    if profile['crop']!='Other' and profile['crop'].lower() not in seq.lower():
        proposed=seq+' → '+profile['crop']+' (desired addition; suitability unverified)'
        rows[1]['Sequence']=proposed+' + locally suitable cover crop'
        rows[2]['Sequence']=proposed+' → locally suitable diversification crop'
        for i in [1,2]:
            triggers[i].append('Desired crop '+profile['crop']+' is absent from the reported history; explicitly added as a proposed future step')
            rows[i]['Feasibility']='Desired crop suitability and '+rows[i]['Feasibility'].lower()
    for i,r in enumerate(rows):
        r['Inputs affecting this option']='; '.join(triggers[i]) if triggers[i] else 'No specific input rule triggered; this remains a baseline or locally unverified option.'
    return pd.DataFrame(rows),common
