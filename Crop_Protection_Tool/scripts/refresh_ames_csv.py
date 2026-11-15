"""Download the full NASA POWER daily record for the Ames sample farm and save it as the offline fallback.

Run from anywhere:  python3 Crop_Protection_Tool/scripts/refresh_ames_csv.py
"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from data_access import load_environment

out=ROOT/'data/power_daily_full.csv'
b=load_environment(42.03,-93.62,'2001-01-01','2024-12-31')
for w in b['warnings']:print('WARNING:',w)
d=b['daily']
d.to_csv(out,index=False)
print(f'Saved {len(d):,} rows to {out}\nColumns: {list(d.columns)}\nMissing per column: {d.isna().sum().to_dict()}')
