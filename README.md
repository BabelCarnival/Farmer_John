# Smooth-map update
The map now uses an inverse-distance color surface for display. Original grid values still drive every calculation and point selection. Interpolation adds no observations or field-scale precision; distant unsampled edges fade out. Both absolute temperature and temperature-difference layers use the same color limits as their legends. Earlier notes about non-interpolated square cells describe a previous version.

# Live-update interface and shaded temperature map

Farm inputs now update automatically; no Submit or Generate button is required. Press Enter or leave a text box to apply typed edits. Crop, soil, water, priority, equipment, market and calendar inputs immediately refresh the relevant results. Existing history is kept intact when the desired crop differs; alternative sequences flag the crop as a proposed addition requiring suitability review.

The map uses filled grid polygons with continuous color scales, rather than circles. Approximate display cells are 0.5° latitude by 0.625° longitude around sampled centers, consistent with observed coordinate spacing. The workbook lacks original footprint metadata, so these are not authoritative source-cell or field boundaries. No sub-grid interpolation is used. The grid selector works if map tiles cannot load.

# TerraRoute update: six-step farmer journey

1. Understand the farm: location, current sequence, soil, attention/uncovered months, water and priorities.
2. Analyse environmental evidence: regional temperature comparison with explicit daily-rainfall, vegetation and soil-moisture coverage status.
3. Identify vulnerable periods: for Ames, historical heat days, rainfall gaps and rain during assumed uncovered months. Quality-filtered MODIS adds possible low-greenness context, not proof of bare soil.
4. Compare three rotation options: current practice, cover-crop and diversification candidates; specific Iowa corn/soybean examples are source-linked.
5. Stress-test: historical, hotter +2°C, drier −20%, wetter +20%, or custom sensitivity settings. All detailed rainfall/daily tests use the separate Ames series only. Other regions get temperature-only sensitivity and clear missing-data messages.
6. Explain: potential soil roles, water trade-offs, source evidence, constraints, missing information, optional local Ollama chat and CSV downloads.

Run with python3 -m streamlit run map_app.py after installing requirements.txt. These scenarios are not weather forecasts, erosion estimates or crop-yield predictions. Soil moisture is not observed; rainfall is not silently substituted for it. Calendar edits are explicit user assumptions. The original temperature workbook's NASA provenance, Celsius units and inferred month columns still need original metadata confirmation.

# TerraRoute — crop rotation decision support

## Start the map tool on your Mac

Unzip the project, then open this folder in VS Code. Use its terminal:

    python3 -m pip install -r requirements.txt
    python3 -m streamlit run map_app.py

Open the Local URL printed by Streamlit. For a folder-safe launch, run the included Start_Mac.command from Terminal after installing requirements. Keep the terminal open. A browser internet connection is needed for OpenStreetMap background tiles; grid-point selection still works without the tiles.

## Farmer workflow

1. Choose a state and grid point, or click a point on the map. Map colors show historical June–August monthly mean temperature or a difference between two ten-year periods.
2. Enter intended crop, existing rotation, soil texture, drainage, water access, priorities, equipment and market constraints.
3. Compare the current sequence with a cover-crop strategy and a diversification strategy. Inspect constraints and save the comparison CSV.
4. Optionally explore the separate Ames daily-weather and MODIS example. These data are not generalized to other states.
5. Ask questions with a local Ollama model. Open Ollama, run ollama pull llama3.2:3b, then refresh the app. Chat is optional and generated answers need review.

This is one farmer interface. Unknown soil inputs remain unknown. Rule-based notes change with farmer inputs; there is no unvalidated crop-suitability score or numerical soil-benefit estimate. Crop-stage reference guidance is available for corn and soybean only. Other crops require local guidance. Candidate alternatives are locally unverified templates, not prescriptions. The state workbook was attributed to NASA by the user; original export metadata is still needed to verify provenance and the inferred column meanings and Celsius units.

## Data and original files

The complete uploaded state-temperature workbook is under data/usa_temperature_2000_2025.xlsx. POWER and MODIS are data/power_daily.csv and data/modis_2024.csv. State labels are cleaned, including ILLNOIS → ILLINOIS; missing state labels are filled by block. The first data row was labeled STATE; it is assigned to the following Washington block, preserving its observations. Selected points are within the supplied state labels, which have not been independently spatially validated.

The map is historical evidence, not the year-ahead forecast. Keep all forecast limitations with any notebook results. The earlier notebook and model are retained as optional research artifacts below.

---

# Rotation decision-support notebook update

The notebook now directly loads the supplied 2000–2025 state-temperature Excel workbook. Keep the data/ folder alongside the Python files. It includes local soil and farmer-priority inputs and a three-strategy rotation decision table. Unknown local information is visibly marked, not fabricated. The Excel columns and Celsius interpretation are provisional until original NASA metadata is provided.

# Crop Protection Outlook — 12-month prediction notebook

This is a statistical seasonal outlook, not a live weather forecast or a crop-yield model. It supports the question: how might the crops a farmer wants to grow overlap with expected weather exposure, and what protection strategies need local review?

## Start in VS Code
Open this extracted folder. In its terminal run:

    python3 -m pip install -r requirements.txt

Open Crop_Protection_Outlook.ipynb, choose that Python environment as the kernel, and Run All. Edit crop, sensitive months and irrigation access in the farmer-input cell. The first cell finds this folder, including when the notebook starts from its parent.

Or run without a notebook:

    python3 year_outlook.py

Results are written to outputs/. No Ollama, NASA login or API key is needed.

## The time horizon
The tool forecasts all twelve months following the last COMPLETE month in the supplied file. The bundled file ends December 2024, so the included outlook is January–December 2025. This is future relative to the file, but not future relative to today's date. Replace data/power_daily.csv with updated NASA POWER data to move the forecast window forward. This release does not fetch recent observations or incorporate official seasonal forecasts.

## What is predicted
Monthly mean maximum air temperature, monthly rainfall total, expected monthly counts of days at least 35°C, and expected longest within-month dry run (less than 1 mm/day). Fractional day outputs are statistical estimates. Counts and dry-run predictions use simple statistical models, not event probabilities. Do not interpret them as exact future dates or a plant damage forecast.

Models: calendar-month historical average and regularized season-plus-linear-trend regression. A small candidate set is deliberate given just 24 annual cycles at one location. Validation: four rolling December origins forecasting 2017–2020. Model selection uses validation MAE. Test: four rolling December origins forecasting 2021–2024, without test-based selection. Each test origin trains only on earlier observations. Error is reported at each lead month, with just four test cases per lead. No guarantee of one-year forecast accuracy is made.

Forecast bands use the 90th percentile of absolute validation residuals pooled across lead months, not calibrated probabilities for every horizon. Test band coverage is shown. Temporal dependence and limited examples constrain reliability. If no added test skill is found, the notebook says so. It does not hide weak results or claim performance gains.

## Protection comparisons
The farmer keeps their intended crop. Compare current practice, a winter-cover strategy, and small-grain/legume diversification as discussion scenarios. These options have practical constraints and potential soil-cover benefits based on the cited extension guidance. The tool does not predict numerical risk reduction, yield improvement, profit, nitrogen credit or soil-health improvement from adopting them. The same weather affects each option. Sensitive months are farmer/adviser inputs rather than automatically inferred crop stages.

MODIS 2024 observations support a separate quality-filtered vegetation panel, not prediction: a single year cannot train a long-term vegetation model. The sample coordinate is not verified as cropland; confirm a real parcel before a farm-specific claim.

## SI disclosure
AI assisted with concept exploration, code, calculations and explanatory drafts. Environmental observations are the supplied NASA data. Review outputs and disclose assistance under the applicable competition rules. See SOURCES.md for attribution.

## Generate and update comparisons
Farm inputs update automatically. Results identify the entered conditions that triggered review notes. Changing the map point refreshes the selected environmental context. Strategy types remain three fixed planning categories; the tool does not claim NASA data selects suitable crops.
