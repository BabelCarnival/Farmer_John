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
- U.S. state temperature workbook: not used for the Ames daily weather analysis. It is used by the app only for the regional temperature map (see the workbook section below).
- GPM downloader scripts: access instructions only, not rainfall observations.
- Landsat and GPM daily were explored but are not integrated. Do not list them as model inputs in the submission.

## Software and SI disclosure

Python; pandas; NumPy; Plotly; Streamlit. Dependencies are listed in requirements.txt.
AI did not contribute to the project idea, which was developed by the team (Chan Sum Choy Levon, Chan Bun Long, Tjong Jia Hui Kenneth, Jing Song Ooi, Yeung Han Jie). AI coding assistants (Claude Code, ChatGPT/Codex) were used for code, interface copy, documentation and asset bundling. No AI-generated environmental observations are used. Default crop-calendar assumptions are explicitly labeled.

The question assistant uses a user-installed local Ollama model through /api/tags and /api/chat at localhost:11434. It receives annual POWER summaries, current calendars and exposure results. Answers are generated, not validated agronomic findings. Model files and inference are provided by the user’s Ollama installation. API reference: https://docs.ollama.com/api/chat .

# Prediction-tool additions

The twelve-month outlook uses only the POWER daily CSV as predictive input. The MODIS CSV is displayed for 2024 context only. The Washington GPM monthly rainfall and downloader scripts remain excluded. This describes the earlier forecasting notebook, now in legacy/, which is not part of the app. Ollama is not part of that notebook release.

Additional crop-protection references consulted:
- Iowa State University: Soybean Growth Stages. https://crops.extension.iastate.edu/encyclopedia/soybean-growth-stages
- Iowa State University: Soybean Potential in Drought Conditions. https://crops.extension.iastate.edu/cropnews/2012/07/soybean-potential-drought-conditions
- Iowa State University: Managing Soils Under Dry Conditions. https://crops.extension.iastate.edu/encyclopedia/managing-soils-under-dry-conditions
- USDA NRCS: Cover Crop Termination. https://www.nrcs.usda.gov/sites/default/files/2025-04/Cover_Crop_Termination-FS_0.pdf

These support qualitative guidance; they do not validate assumed calendars or predicted benefits. scikit-learn provides Ridge regression and MAE evaluation; matplotlib supplies charts. The models, splits and uncertainty method are project design choices, not NASA algorithms. No trained crop-response model or official seasonal forecast is integrated.

## Newly integrated user-supplied workbook
Original file: 2000-2025 USA Temp by State (50 States)(1).xlsx; packaged unchanged as data/usa_temperature_2000_2025.xlsx. Source: NASA POWER (https://power.larc.nasa.gov/), as confirmed by the team member who obtained it. The specific POWER product (API vs Data Access Viewer), community and temporal resolution were not recorded. All 65,338 rows contain T2M, with years 2000–2025 and coordinate pairs. The headerless monthly columns are interpreted as January–December plus annual mean; Celsius is assumed (the POWER default for T2M); the file carries no units. State labels are forward-filled; initial STATE label is replaced with the next Washington block label; ILLNOIS is normalized to ILLINOIS. A nearest grid point within a chosen state block is used. These are grid-point observations, not a state-wide average. This monthly T2M series trains a separate temperature model and must not be merged as if equivalent to daily maximum temperature. Predictions do not quantify soil-health improvements.

Soil properties, water access, local crop stages, market and equipment constraints are user inputs. No soil dataset is supplied, inferred or fabricated. Rotation comparison remains conditional on those inputs.

## Interactive-map tool
The map directly reads the supplied state-temperature workbook, averages June–August monthly T2M for 2000–2009 and 2016–2025, and shows their difference per grid point. These are historical comparisons, not predictions or causal attribution. Missing local soil and management inputs are explicitly unknown. The decision-support rules are in rotation_rules.py and generate review notes and feasibility flags, not measured rotation effects or a suitability ranking. Detailed POWER and MODIS evidence is displayed only as a separate Ames demonstration when the selected workbook point is within approximately 30 km.

The optional Ollama chat receives the selected grid context, farmer inputs and decision table; it is locally generated text, not verified agronomic advice. Plotly provides the interactive map, and OpenStreetMap provides the basemap: https://www.openstreetmap.org/copyright . No soil map, statewide vegetation product, yield dataset, official forecast or verified farm boundary has been added.

## TerraRoute strategy and scenario additions
- Iowa State University Extension, Iowa Cover Crop Recipe: Post Corn, Going to Soybean — Use Cereal Rye. https://store.extension.iastate.edu/product/15548.pdf . Used to identify a source-supported cover-crop option for the Iowa corn/soybean example, conditional on local establishment and termination review.
- Davis, A.S., Hill, J.D., Chase, C.A., Johanns, A.M., and Liebman, M. (2012). Increasing Cropping System Diversity Balances Productivity, Profitability and Environmental Health. PLOS ONE 7(10), e47149. https://doi.org/10.1371/journal.pone.0047149 . Used to identify an Iowa diversification example; it does not validate benefits for an arbitrary field, and the trial management differed between systems.

Scenario method: temperature offsets add to observed daily Tmax; rainfall multipliers scale historical daily precipitation. The same external weather is applied to all calendar options. Heat days count Tmax ≥35°C in entered attention months; dry runs count consecutive daily precipitation <1 mm, with gaps breaking runs. Rain in assumed bare months and ≥10 mm rain-day counts are exposure measures, not erosion. NDVI <0.3 is an illustrative low-greenness screen after good-quality filtering; it does not establish bare soil, drought or crop identity. The source sample point is unverified as cropland. No satellite soil-moisture series is supplied.

## Shaded map display and live inputs
The temperature layer now uses continuously colored polygon cells centered on the sampled coordinates. 0.5° latitude × 0.625° longitude is an approximate display footprint based on observed coordinate spacing; exact grid metadata was not recorded with the export, so footprints are unconfirmed. The cells are neither farm boundaries nor interpolated fine-scale weather. Farm widgets now update results immediately; typed edits commit on Enter or loss of focus. A mismatch between main crop and history is retained and explicitly flagged, with desired crops shown as proposed additions in alternatives.

## Smooth map visualization update
The map's color surface is now inverse-distance interpolation of at most four nearest sampled points, rendered as an image layer in map coordinates. Display distances use observed coarse grid spacing. The overlay fades out beyond nearby sample support. This surface is visual only and never feeds environmental analysis, crop options or forecasts. Original discrete values remain the basis of selection, metrics and exported results. Legend limits match the raster normalization.

## State outline layer
U.S. Census Bureau, 2024 Cartographic Boundary Files, State and Equivalent Entities, 1:20,000,000. Download: https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip . Reference: https://www.census.gov/geographies/mapping-files/2024/geo/carto-boundary-file.html . Accessed November 14, 2026. Converted from the generalized Census shapefile to data/us_states_2024_20m.geojson for map display. Boundaries clip display opacity and add an outline; they do not turn the temperature samples into state-wide or field-scale observations. Geometries are generalized cartographic outlines, not survey boundaries.

## Current implementation update: live point data and conditional recommendations
The latest map_app.py can retrieve daily T2M_MAX and PRECTOTCORR for user coordinates through the NASA POWER Daily API, and separately request GWETTOP and GWETROOT. NASA metadata and returned units are retained; fill/missing observations are preserved as missing and missing dates are reindexed. Optional wetness retrieval may fail independently of core weather. POWER wetness documentation: https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/ . The live service was checked at Ames for January 1–7, 2024, returning core weather and both wetness variables. This check is not an assurance of service availability for every request.

New data_access.py handles retrieval, analysis_v2.py derives calendar/weather screens, crop_catalog.py holds the small reviewed regional catalogue, and recommender.py applies constraints and explicit heuristic preference weights. The catalogue supports Iowa corn/soybean examples and does not establish global suitability. Outside it, general_options.py applies a general climate screen (see the section at the end of this file). Reference URLs in crop_catalog.py are the extension/NRCS and Davis et al. sources already listed above. Their short paraphrased notes are passed to Ollama with computed results; full documents are not retrieved automatically. Original NASA observations are not generated by a language model.


## Farmer interface and report helper update
No new environmental datasets were added by this interface update. Daily NASA observations still drive calculations. Long weather-history plots now aggregate to monthly means of daily maximum temperature and monthly rain totals for readability; the underlying daily data are downloadable. The report helper is deterministic Python text selection from current report fields, not an AI model, forecast or new scientific source. Optional Ollama explanations remain AI-generated. AI coding assistants were used to develop this interface and helper code. Technical comparison attributes and assumptions remain available in collapsed sections and the JSON report.


## Step 4 plain-language comparison
The large 0–100 preference chart has been removed. Cards now explain how each option relates to the selected priorities. A comparison of cover, diversity, work and water trade-offs was shown as a table; it has since been replaced by data-computed indicators (see the section at the end of this file). Excluded options have explicit reasons. Internal catalogue weights only order alternatives and remain disclosed in the method and technical report; they are not probabilities, NASA-derived benefits or suitability scores. No environmental datasets or scientific claims were added.


## Current implementation update (final submission build)

**Extra NASA POWER variables.** data_access.py now also requests T2M (daily mean), T2M_MIN and ALLSKY_SFC_SW_DWN (solar radiation, MJ/m²/day) in a second request, with the same community (AG) and daily point API as before. They become tmean_c, tmin_c and solar_mj. If this request fails, the app shows a warning and continues without them. The bundled Ames CSV has none of these, so they are NaN in the fallback and the frost, evaporative-demand and stress-test features show "data not loaded" instead of values. The full live parameter list is T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, GWETTOP and GWETROOT.

**Monthly climatology (climate.py).** For each calendar month, the mean over all complete years of monthly rain, mean temperature, the lowest daily minimum, the share of years with frost (Tmin < 0 °C), mean root-zone soil wetness (GWETROOT) and reference evapotranspiration (ET0). Partial months are left out. ET0 uses the Turc equation per day: if T > 0 °C, ET0 = 0.013 × T/(T+15) × (23.8856 × Rs + 50), with T = daily mean temperature and Rs = solar radiation in MJ/m²/day; otherwise 0. Daily values are summed per month and averaged across years. A month is flagged as a water deficit when rain is below half of ET0 and ET0 exceeds 20 mm. Turc ET0 is a simple estimate, not a measured or full-energy-balance value.

**Farm at a glance (Step 3).** A monthly chart (rain, ET0, soil wetness), a 12-month risk calendar and plain-language takeaways are generated from the climatology and the entered crop dates. Heat shows the average days per year with Tmax ≥ 35 °C. Colour cut-offs in the calendar are screening choices made by the team: heat watch at 0.5 or more days and risk at 3 or more days per year; soil wetness watch below 50% and risk below 35%; frost likely when frost occurs in at least half of years. Daily soil-wetness lines remain available under "Daily detail".

**General climate-screened options (general_options.py).** Where the reviewed Iowa catalogue does not apply, the app proposes two alternatives from a small table of crop groups (cereal rye, oats, hairy vetch, sunn hemp, cowpea, chickpea, sorghum, mustard). The table holds GENERAL SCREENING VALUES: indicative growing-month counts, monthly-mean temperature ranges, and frost and drought tolerance. These values were written by the team as rough guides, are not locally reviewed and are not taken from a cited dataset. They must be verified locally, for example with FAO ECOCROP or extension advice. The cover option picks the best temperature and frost fit for the longest run of bare months; the diversify option picks a crop from a different family that suits the main growing months. Each option's reason quotes the NASA climate numbers used. These are climate-fit screens, not yield or profit predictions.

**Option indicators (option_indicators.py).** For each option: months with living cover, rain on bare soil (sum of average monthly rain over bare months), crops and crop families in the cycle, extra water demand (months where a new living crop grows while rain is under half of ET0: none = 0, some = 1–2, high = 3 or more) and climate fit (good, fair or poor from the temperature and frost screen). All are computed from the entered crop dates, the option calendar and the NASA climatology. The reviewed Iowa options carry no stored calendar, so cover is assumed in March, April, October and November, as in Step 5. The indicators describe the plan and are not guaranteed outcomes.

**Option stress test (Step 5).** For the chosen scenario the daily record is shifted (temperature offset added to daily mean, minimum and maximum temperature; rainfall multiplied by the factor), the climatology and ET0 are recomputed, and each option reports rain on bare soil, dry months while crops grow, frost-likely months for the new crop (frost in at least half of years), plus a one-line verdict. This is a sensitivity test on past weather, not a forecast and not a crop or soil-water simulation.

**Branding and images.** The app uses a text "TerraRoute" title in the open-licence Caveat font, bundled in assets/ with the sprout icon. No NASA logo is used. Plain-text mentions of NASA data sources remain.

**Repository organisation.** Earlier research scripts and the forecasting notebook (journey.py, rotation_rules.py, state_temperature.py, year_outlook.py, Crop_Protection_Outlook.ipynb) are in legacy/ and are not imported by the app.

**Offline fallback and caching (latest build).** data/power_daily_full.csv holds the full NASA POWER daily record for the Ames sample farm (42.03, -93.62; 2001-01-01 to 2024-12-31; T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, GWETTOP, GWETROOT), saved by scripts/refresh_ames_csv.py through the same data_access.load_environment() the live app uses. It is used only if the live request fails. The older data/power_daily.csv (T2M_MAX and PRECTOTCORR only) is kept. Live results are cached with a version number so results saved by earlier app versions are ignored, and any missing optional column is added as empty rather than breaking the app.

**General-option rules (update).** The general climate screen never proposes a crop whose temperature and frost fit is "poor" for its window. For the diversify option, a crop from a family already in the rotation is allowed only if it is a different crop and drought-tolerant; new families score higher. The fit label (good, fair, poor) is shown on each general card. It is a screen against indicative table values, not a yield prediction.

**State follows coordinates.** When typed farm coordinates fall inside another state's outline (U.S. Census boundaries already listed above), the app switches the state selector to that state and moves the grid cell to the nearest sampled point. Coordinates outside every state keep the existing warning.
