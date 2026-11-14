"""Display sampled grid values as approximate cells, without interpolation."""
def grid_geojson(frame):
    features=[]
    for row in frame.itertuples():
        west=max(-180.,float(row.lon)-.3125);east=min(180.,float(row.lon)+.3125)
        south=max(-90.,float(row.lat)-.25);north=min(90.,float(row.lat)+.25)
        features.append({'type':'Feature','id':row.point_id,'properties':{'point_id':row.point_id},
            'geometry':{'type':'Polygon','coordinates':[[[west,south],[east,south],[east,north],[west,north],[west,south]]]}})
    return {'type':'FeatureCollection','features':features}


def smooth_overlay(frame,field,vmin,vmax,palette='YlOrRd'):
    """IDW display raster only. Returns an image layer; never an analysis input."""
    import base64,io
    import numpy as np
    from scipy.spatial import cKDTree
    from matplotlib import colormaps
    from PIL import Image
    valid=frame.dropna(subset=['lat','lon',field])
    west=max(-180,float(valid.lon.min())-.3125);east=min(180,float(valid.lon.max())+.3125)
    south=max(-85,float(valid.lat.min())-.25);north=min(85,float(valid.lat.max())+.25)
    # Uniform Web-Mercator y avoids unequal visual spacing toward high latitudes.
    xs=np.linspace(west,east,550)
    merc=lambda lat:np.log(np.tan(np.pi/4+np.radians(lat)/2))
    ys=np.degrees(2*np.arctan(np.exp(np.linspace(merc(north),merc(south),450)))-np.pi/2)
    xx,yy=np.meshgrid(xs,ys)
    # Distances expressed in source-grid steps, not invented field-scale precision.
    tree=cKDTree(np.column_stack([valid.lon.to_numpy()/.625,valid.lat.to_numpy()/.5]))
    distance,index=tree.query(np.column_stack([xx.ravel()/.625,yy.ravel()/.5]),k=min(4,len(valid)))
    if distance.ndim==1:distance=distance[:,None];index=index[:,None]
    weights=1/np.maximum(distance,1e-6)**2
    vals=(valid[field].to_numpy()[index]*weights).sum(axis=1)/weights.sum(axis=1)
    rgba=colormaps[palette](np.clip((vals-vmin)/max(vmax-vmin,1e-9),0,1))
    # Do not paint distant unsampled areas. Alpha fades near the support boundary.
    rgba[:,3]=.83*np.clip((.85-distance[:,0])/.2,0,1)
    pixels=(rgba.reshape(len(ys),len(xs),4)*255).astype('uint8')
    b=io.BytesIO();Image.fromarray(pixels).save(b,format='PNG')
    return {'sourcetype':'image','source':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode(),
            'coordinates':[[west,north],[east,north],[east,south],[west,south]],'below':'traces','opacity':1}
