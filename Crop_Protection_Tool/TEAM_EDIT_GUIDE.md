# Current TerraRoute code map

The following upgrades are implemented in the current source. Older journey.py and rotation_rules.py remain as legacy reference and are no longer imported by map_app.py.

1. Farm inputs — map_app.py plus analysis_v2.parse_history(): structured editable crop/date rows, intended crop, local soil, water and priorities; validates dates and derives growing-month coverage and calendar gaps. Actual physiology and confirmed bare soil still need field input.
2. Environmental evidence — data_access.load_environment(): NASA POWER daily point requests by coordinates/dates, explicit core units, missing-date preservation, optional GWETTOP/GWETROOT retrieval and complete response metadata. map_app.py caches requests by parameters and never silently substitutes Ames. MODIS remains Ames-only; no unprovided vegetation series is fabricated. Workbook source: NASA POWER, confirmed by Ken (Tjong Jia Hui Kenneth); exact export settings were not recorded.
3. Vulnerability — analysis_v2.annual_exposure()/monthly_exposure() plus map_app.py: computes historical weather-exposure screens within entered crop months and ranks periods to inspect; automatically derives possible cover gaps from calendar coverage. A low-NDVI observation does not prove bare soil.
4. Rotations — crop_catalog.options() and recommender.recommend(): a small reviewed Iowa corn/soybean catalogue, hard exclusions for stated establishment/equipment/market constraints, baseline plus up to two supported options, and an explicit heuristic planning-preference matrix. The tool intentionally shows fewer options outside catalogue support or under hard constraints.
5. Stress — map_app.py uses exposure.compare() with the loaded location series and eligible options. All options receive the same perturbation; assumed cover changes calendar gaps, not weather. No crop-response or water-balance model is claimed.
6. Explanation — short map_app.py cards with evidence expanders; ollama_chat.ask() receives calculated context plus curated source notes. Generated text and numeric claims are not automatically verified.

## Map appearance
map_layers.smooth_overlay() performs display-only inverse-distance interpolation, masks alpha using polygon_mask() and the selected Census state geometry, and retains the original sample values for calculations. map_app.py adds the state outline. Source polygons are bundled in data/us_states_2024_20m.geojson.

## Files to review when merging into the shared repository
Changed: map_app.py, ollama_chat.py, requirements.txt, README.md, SOURCES.md, MAP_SUBMISSION.md.
New: data_access.py, analysis_v2.py, crop_catalog.py, recommender.py.
Keep the existing data/ folder, exposure.py, and map_layers.py. Preserve teammates' edits by reviewing differences before merging. Nothing here automatically pushes to GitHub or deploys a public site.
