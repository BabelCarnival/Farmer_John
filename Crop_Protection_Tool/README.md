# TerraRoute

A map-led crop-rotation decision-support prototype using NASA environmental data and explicit local farm inputs.

## Run
Open this extracted folder in VS Code. In the terminal:

    python3 -m pip install -r requirements.txt
    python3 -m streamlit run map_app.py

On Windows replace python3 with py. The terminal must point at this folder, or use the full path to map_app.py. Keep the terminal open. Start_Mac.command is also included.

## Farmer journey
1. Choose a regional temperature-map context, then use the bundled Ames point or enter your own coordinates. The state outline clips the display layer; a selected regional grid is not a farm boundary.
2. Enter crop-history rows with real planting and harvest dates, intended crop, soil information, water access, priorities and feasibility constraints.
3. Load NASA POWER weather and optional modeled soil-wetness indices for those coordinates. Live retrieval needs internet, but not a NASA login. Failed retrieval never silently substitutes another site. Requests are cached for one day in the Streamlit process.
4. Inspect growing-month weather, ranked heat/rainfall-gap review periods and possible cover gaps derived from crop dates. Actual critical growth stages and bare soil still need field confirmation. Optional MODIS evidence is available only at the Ames sample point.
5. Compare the baseline with up to two sourced Iowa corn/soybean options. Hard constraints can exclude candidates. Outside that regional catalogue, the tool says evidence is missing instead of generating generic locally unverified recommendations.
6. Inspect the planning-preference chart, test hotter/drier/wetter scenarios against the loaded point's history, review sources and save the decision report.

Optional Ollama chat: install/open Ollama, run ollama pull llama3.2:3b, and refresh. The chat receives current calculated results and curated reference notes; generated answers require review. It is not a retrieval engine over entire source documents or an automatically verified agronomist.

## Data supplied with the project
- data/usa_temperature_2000_2025.xlsx: original state workbook. Its NASA provenance is user-attributed, and January–December/Celsius column meanings remain inferred pending original export metadata. The regional map uses historical T2M, not daily maximum temperature.
- data/power_daily.csv: supplied Ames NASA POWER daily Tmax and corrected precipitation, 2001–2024.
- data/modis_2024.csv: supplied NASA AppEEARS MOD13Q1.061 extract. Only 2024 good-quality records enter the vegetation panel; a December 2023 boundary composite is excluded. The point is unverified as a crop field.
- data/us_states_2024_20m.geojson: generalized Census state boundaries for display clipping.

New NASA point requests retain original metadata and units in downloadable decision reports. GWETTOP/GWETROOT wetness values are modeled indices, not a local soil test or automatically converted volumetric water content. Weather records and remote-sensing pixels have coarser support than a field. No soil map or field-boundary dataset is bundled.

## Comparison method and limits
The small candidate catalogue has explicit regional support. A planning-preference index uses disclosed 0/1/2 attributes for extra-cover opportunity, diversification opportunity and implementation ease, equally weighted across selected supported priorities. It is a heuristic preference aid, not validated crop suitability, yield, profit or soil improvement. Water conservation is marked unscored because data do not quantify it. Hard exclusions happen before scoring.

The sensitivity tests add a temperature offset and multiply rainfall in historical data. They do not forecast next year's weather. Matching crop-season windows give matching weather exposure even when rotations differ. Calendar gaps do not necessarily mean bare soil because residue, unrecorded crops or other cover may remain. Dates are validated, but they do not establish physiology. Local expert review remains necessary.

Earlier prediction notebooks are retained as optional historical research artifacts. Their data cutoffs and forecast-skill limitations remain in the notebooks; they are not TerraRoute's main recommendation engine.

See SOURCES.md for full attribution and TEAM_EDIT_GUIDE.md for the source-code map. AI assistance was used for concept exploration, code and draft text. Review and disclose it under current event rules. No public deployment or GitHub push is included.


## Farmer interface update
The six-step journey is retained. Rotation cards show the crop sequence, potential benefit, trade-off and next check side by side. Technical attributes and detailed tables are collapsed. Shared heat/dry-spell counts are shown once, and the historical scenario hides duplicate columns. Charts summarize daily history monthly for display only; calculations still use daily data.

The public app includes a deterministic report helper with four question buttons and a text box. It reads only the current report and is explicitly labelled separately from AI chat. Local Ollama remains optional and must run beside the Streamlit Python process. Streamlit Cloud cannot reach Ollama on a visitor's Mac via localhost. No hosted AI service is configured. A readable farm summary and the full JSON report are both downloadable.

### Updating an existing deployment
Replace `map_app.py` and add `report_help.py` in the same `Crop_Protection_Tool` directory in your existing repository. Commit and push both files. Keep the Streamlit entry point `Crop_Protection_Tool/map_app.py`. The archive also includes the updated README and sources disclosure.
