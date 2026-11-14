"""Small, explicitly regional reviewed catalogue; no invented global suitability."""
REFERENCES={
 'corn':{'url':'https://crops.extension.iastate.edu/encyclopedia/corn-pollination-effect-high-temperature-and-stress','note':'Water stress around corn pollination matters; confirm actual tasseling/silking in the field.'},
 'soybean':{'url':'https://crops.extension.iastate.edu/cropnews/2012/07/soybean-potential-drought-conditions','note':'Soybean reproductive stages, especially R3–R6, are sensitive to water deficits; confirm actual stage.'},
 'rye':{'url':'https://store.extension.iastate.edu/product/15548.pdf','note':'Iowa recipe discusses cereal rye after corn before soybean. Establishment and termination need local review.'},
 'diversify':{'url':'https://doi.org/10.1371/journal.pone.0047149','note':'An Iowa study evaluated corn/soybean/small grain with red clover under different management systems. Results do not guarantee farm-specific benefits.'},
 'water':{'url':'https://www.nrcs.usda.gov/sites/default/files/2025-04/Cover_Crop_Termination-FS_0.pdf','note':'Living cover uses water; termination timing influences moisture availability.'}}

def options(profile):
    seq=profile['sequence'];names={r['Crop'].lower() for r in profile['crop_history']}
    base={'id':'current','name':'Keep current rotation','sequence':seq,'cover_opportunity':0,'diversity_opportunity':0,'implementation_ease':2,'source':[],'risk':'Existing gaps and residue practices require confirmation.'}
    candidates=[base];gaps=[]
    supported=profile['region']=='IOWA' and {'corn','soybean'}.issubset(names) and profile['crop'] in ['Corn','Soybean']
    if not supported:
        gaps.append('The reviewed catalogue currently supports Iowa corn/soybean examples only. Add sourced local crop options before recommending two alternatives here. Weather analysis still works for other loaded locations.')
        return candidates,gaps
    candidates += [dict(id='cover',name='Corn/soybean with cereal rye cover',sequence=seq+'; rye after corn before soybean',cover_opportunity=2,diversity_opportunity=1,implementation_ease=1,source=['rye','water'],risk='Cover establishment and termination add work and use water while growing.'),
      dict(id='diversified',name='Add a small grain with red clover',sequence='Corn → soybean → small grain + red clover → corn',cover_opportunity=2,diversity_opportunity=2,implementation_ease=0,source=['diversify','water'],risk='Requires a crop outlet/use, equipment and locally suitable calendars; trial management differs from this farm.')]
    return candidates,gaps
