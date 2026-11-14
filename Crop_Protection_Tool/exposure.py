"""Deterministic exposure indicators. AI-assisted code; see SOURCES.md."""
import numpy as np
import pandas as pd


def load_daily(source):
    d = pd.read_csv(source)
    d = d[['date', 'tmax_c', 'precip_mm']].copy()
    d['date'] = pd.to_datetime(d.date, errors='raise')
    for c in ['tmax_c', 'precip_mm']:
        d[c] = pd.to_numeric(d[c], errors='coerce').replace(-999, np.nan)
    if d.date.duplicated().any():
        raise ValueError('Duplicate daily dates. Resolve these before analysis.')
    if (d.precip_mm.dropna() < 0).any():
        raise ValueError('Negative rainfall found. Check missing-value codes.')
    return d.sort_values('date').reset_index(drop=True)


def window(d, months):
    return d[d.date.dt.month.isin(months)]


def dry_run(d, cutoff):
    """Missing values and gaps break runs; never join across missing days."""
    best = current = 0
    previous = None
    for row in d.sort_values('date').itertuples():
        if previous is not None and (row.date - previous).days != 1:
            current = 0
        current = current + 1 if pd.notna(row.precip_mm) and row.precip_mm < cutoff else 0
        best = max(best, current)
        previous = row.date
    return best


def exposure(d, months, heat=35, cutoff=1):
    s = window(d, months)
    valid = s[['tmax_c', 'precip_mm']].notna().all(axis=1)
    return {'heat_days': int((s.tmax_c >= heat).sum()),
            'dry_spell_days': dry_run(s, cutoff),
            'rain_mm': float(s.precip_mm.sum(min_count=1)),
            'valid_days': int(valid.sum())}


def history(d, heat=35, cutoff=1):
    rows = []
    for year, g in d.groupby(d.date.dt.year):
        r = exposure(g, list(range(4, 10)), heat, cutoff)
        expected = len(pd.date_range(f'{year}-04-01', f'{year}-09-30'))
        r.update(year=int(year), coverage=r['valid_days']/expected)
        rows.append(r)
    a = pd.DataFrame(rows)
    # Exclude incomplete seasons from selecting historical extremes.
    a['eligible'] = a.coverage >= .95
    for c, sign in [('heat_days', 1), ('dry_spell_days', 1), ('rain_mm', -1)]:
        vals = a.loc[a.eligible, c]
        sd = vals.std(ddof=0)
        a[c + '_z'] = sign*(a[c]-vals.mean())/(sd if sd > 0 else 1)
    a['compound'] = a[['heat_days_z','dry_spell_days_z','rain_mm_z']].mean(axis=1)
    return a


def compare(d, plans, year, heat, cutoff):
    g = d[d.date.dt.year == year]
    rows = []
    for p in plans:
        r = exposure(g, p['sensitive'], heat, cutoff)
        b = window(g, p['bare'])
        r.update(strategy=p['name'], bare_rain_mm=float(b.precip_mm.sum()),
                 bare_heavy_days=int((b.precip_mm >= 10).sum()))
        rows.append(r)
    return pd.DataFrame(rows)


def load_modis(source):
    d = pd.read_csv(source)
    n = 'MOD13Q1_061__250m_16_days_NDVI'
    q = 'MOD13Q1_061__250m_16_days_pixel_reliability'
    d = d.rename(columns={'Date':'date', n:'ndvi', q:'reliability'})
    d['date'] = pd.to_datetime(d.date)
    # AppEEARS CSV is already scaled (values around 0–1). Do not scale twice.
    d = d[d.date.dt.year == 2024].copy()
    d['quality'] = d.reliability.map({0:'Good',1:'Marginal',2:'Snow/ice',3:'Cloudy',-1:'Fill'}).fillna('Unknown')
    d.loc[~d.ndvi.between(-.2, 1), 'ndvi'] = np.nan
    return d
