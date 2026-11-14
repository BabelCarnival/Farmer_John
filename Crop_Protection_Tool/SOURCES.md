# Source register

## Environmental data actually used

1. NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
   - User-supplied nasa_power_daily.csv, packaged as data/power_daily.csv.
   - Point: latitude 42.03, longitude -93.62; daily UTC; January 1, 2001–December 31, 2024.
   - Variables: T2M_MAX (daily maximum air temperature at 2 m, °C); PRECTOTCORR (corrected precipitation, mm/day).
   - Original response supplied in the conversation identifies MERRA2 and POWER as sources. These meteorological values are gridded estimates rather than a field gauge or pure satellite-only observations.
   - Used for heat-day counts, rainfall sums, longest dry runs and historical scenario selection.
   - CSV has 8,766 records and no missing cells. Preserve original request metadata when publishing.

2. NASA MODIS/Terra MOD13Q1 Version 6.1, Vegetation Indices 16-Day Global 250 m.
   - Dataset DOI: https://doi.org/10.5067/MODIS/MOD13Q1.061
   - Dataset description: https://modis.gsfc.nasa.gov/data/dataprod/mod13.php
   - Access tool: NASA AppEEARS, https://appeears.earthdatacloud.nasa.gov/
   - User-supplied Ames-MODIS-2024-MOD13Q1-061-results.csv, packaged as data/modis_2024.csv.
   - Requested point: 42.03, -93.62; requested dates January 1–December 31, 2024.
   - Layers used: _250m_16_days_NDVI and _250m_16_days_pixel_reliability. VI_Quality supplied and retained in raw data.
   - The supplied file has 24 rows including one December 2023 boundary composite. The app restricts to 2024.
   - AppEEARS NDVI values are already scaled; the app does not apply the scale again.
   - Default analysis keeps reliability 0 (good); reliability 1 (marginal) can be enabled. Cloud, snow/ice and fill observations are excluded from the trajectory.
   - Used as a separate 2024 vegetation panel, not as proof of crop identity, bare ground or historical rotation effects.
   - Suggested citation: Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA LP DAAC. DOI above. Accessed by project team November 14, 2026.

## Local agricultural context consulted

3. Iowa State University Extension: Corn pollination: effect of high temperature and stress.
   https://crops.extension.iastate.edu/encyclopedia/corn-pollination-effect-high-temperature-and-stress
   - Supports treating growth-stage timing as important when examining weather exposure. It does not validate this app's month windows or alert thresholds.

4. Iowa State University Extension: Planning for Successful Cover Crops.
   https://crops.extension.iastate.edu/post/planning-successful-cover-crops
   - Context for cover-crop establishment windows and the need for local planning.

5. Iowa State University Extension: Start Planning for 2026 Cover Crop Termination.
   https://crops.extension.iastate.edu/post/start-planning-2026-cover-crop-termination
   - Context for termination trade-offs. The prototype does not issue herbicide or termination prescriptions.

## Challenge reference

6. Field Shift: Adapting Farms with NASA Data.
   https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/
   - Challenge objectives and the user's supplied project-submission screenshots.

## Model assumptions and boundaries

- Default corn/soybean, winter-cover and small-grain/legume strategy labels are illustrative comparisons.
- Sensitive months and bare months are user assumptions, not inferred calendars and not validated by the local context references above.
- Temperature and rainfall thresholds are user-controlled screening settings.
- Bare-month rainfall is an exposure proxy; it is not measured erosion, runoff or soil-health improvement.
- No soil samples, confirmed field boundary, water-holding-capacity data, crop yield observations or market records are included.
- The POWER and MODIS products have different spatial and temporal support. They are displayed separately rather than resampled into falsely precise field data.

## Files inspected but not used in the model

- GPM_3IMERGM_07 monthly precipitation CSV supplied for Washington: excluded because the area and temporal support do not match Ames daily analysis. Its units must be checked before any future use.
- U.S. state temperature workbook: excluded; it is not required for the Ames daily weather analysis.
- GPM downloader scripts: access instructions only, not rainfall observations.
- Landsat and GPM daily were explored but are not integrated. Do not list them as model inputs in the submission.

## Software and SI disclosure

Python; pandas; NumPy; Plotly; Streamlit. Dependencies are listed in requirements.txt.
AI assistance was used for idea exploration, code, interface copy and submission drafting. The team should review, edit and accurately disclose that assistance under the current competition rules. No AI-generated environmental observations are used. Default crop-calendar assumptions are explicitly labeled.

The question assistant uses a user-installed local Ollama model through /api/tags and /api/chat at localhost:11434. It receives annual POWER summaries, current calendars and exposure results. Answers are generated, not validated agronomic findings. Model files and inference are provided by the user’s Ollama installation. API reference: https://docs.ollama.com/api/chat .

# Prediction-tool additions

The twelve-month outlook uses only the POWER daily CSV as predictive input. The MODIS CSV is displayed for 2024 context only. The Washington GPM monthly rainfall, state temperature workbook and downloader scripts remain excluded. Ollama is not part of this notebook release.

Additional crop-protection references consulted:
- Iowa State University: Soybean Growth Stages. https://crops.extension.iastate.edu/encyclopedia/soybean-growth-stages
- Iowa State University: Soybean Potential in Drought Conditions. https://crops.extension.iastate.edu/cropnews/2012/07/soybean-potential-drought-conditions
- Iowa State University: Managing Soils Under Dry Conditions. https://crops.extension.iastate.edu/encyclopedia/managing-soils-under-dry-conditions
- USDA NRCS: Cover Crop Termination. https://www.nrcs.usda.gov/sites/default/files/2025-04/Cover_Crop_Termination-FS_0.pdf

These support qualitative guidance; they do not validate assumed calendars or predicted benefits. scikit-learn provides Ridge regression and MAE evaluation; matplotlib supplies charts. The models, splits and uncertainty method are project design choices, not NASA algorithms. No trained crop-response model or official seasonal forecast is integrated.

## Newly integrated user-supplied workbook
Original file: 2000-2025 USA Temp by State (50 States)(1).xlsx; packaged unchanged as data/usa_temperature_2000_2025.xlsx. User attributes the file to NASA. Original NASA export metadata/URL has not been supplied, so this attribution is not independently verified. All 65,338 rows contain T2M, with years 2000–2025 and coordinate pairs. The headerless monthly columns are interpreted as January–December plus annual mean; Celsius is an explicit assumption pending source confirmation. State labels are forward-filled; initial STATE label is replaced with the next Washington block label; ILLNOIS is normalized to ILLINOIS. A nearest grid point within a chosen state block is used. These are grid-point observations, not a state-wide average. This monthly T2M series trains a separate temperature model and must not be merged as if equivalent to daily maximum temperature. Predictions do not quantify soil-health improvements.

Soil properties, water access, local crop stages, market and equipment constraints are user inputs. No soil dataset is supplied, inferred or fabricated. Rotation comparison remains conditional on those inputs.

## Interactive-map tool
The map directly reads the supplied state-temperature workbook, averages June–August monthly T2M for 2000–2009 and 2016–2025, and shows their difference per grid point. These are historical comparisons, not predictions or causal attribution. Missing local soil and management inputs are explicitly unknown. The decision-support rules are in rotation_rules.py and generate review notes and feasibility flags, not measured rotation effects or a suitability ranking. Detailed POWER and MODIS evidence is displayed only as a separate Ames demonstration when the selected workbook point is within approximately 30 km.

The optional Ollama chat receives the selected grid context, farmer inputs and decision table; it is locally generated text, not verified agronomic advice. Plotly provides the interactive map, and OpenStreetMap provides the basemap: https://www.openstreetmap.org/copyright . No soil map, statewide vegetation product, yield dataset, official forecast or verified farm boundary has been added.

## TerraRoute strategy and scenario additions
- Iowa State University Extension, Iowa Cover Crop Recipe: Post Corn, Going to Soybean — Use Cereal Rye. https://store.extension.iastate.edu/product/15548.pdf . Used to identify a source-supported cover-crop option for the Iowa corn/soybean example, conditional on local establishment and termination review.
- Davis, A.S., Hill, J.D., Chase, C.A., Johanns, A.M., and Liebman, M. (2012). Increasing Cropping System Diversity Balances Productivity, Profitability and Environmental Health. PLOS ONE 7(10), e47149. https://doi.org/10.1371/journal.pone.0047149 . Used to identify an Iowa diversification example; it does not validate benefits for an arbitrary field, and the trial management differed between systems.

Scenario method: temperature offsets add to observed daily Tmax; rainfall multipliers scale historical daily precipitation. The same external weather is applied to all calendar options. Heat days count Tmax ≥35°C in entered attention months; dry runs count consecutive daily precipitation <1 mm, with gaps breaking runs. Rain in assumed bare months and ≥10 mm rain-day counts are exposure measures, not erosion. NDVI <0.3 is an illustrative low-greenness screen after good-quality filtering; it does not establish bare soil, drought or crop identity. The source sample point is unverified as cropland. No satellite soil-moisture series is supplied.

## Shaded map display and live inputs
The temperature layer now uses continuously colored polygon cells centered on the sampled coordinates. 0.5° latitude × 0.625° longitude is an approximate display footprint based on observed coordinate spacing; original NASA grid metadata is needed to confirm footprints. The cells are neither farm boundaries nor interpolated fine-scale weather. Farm widgets now update results immediately; typed edits commit on Enter or loss of focus. A mismatch between main crop and history is retained and explicitly flagged, with desired crops shown as proposed additions in alternatives.

## Smooth map visualization update
The map's color surface is now inverse-distance interpolation of at most four nearest sampled points, rendered as an image layer in map coordinates. Display distances use observed coarse grid spacing. The overlay fades out beyond nearby sample support. This surface is visual only and never feeds environmental analysis, crop options or forecasts. Original discrete values remain the basis of selection, metrics and exported results. Legend limits match the raster normalization.
