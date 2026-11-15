# TerraRoute

**NASA-powered crop rotation decision support.**

TerraRoute helps farmers explore crop-rotation changes using NASA environmental data, their crop history, local soil information and practical priorities. Its six-step journey connects an interactive map to weather exposure, rotation trade-offs and historical stress tests.

[Open the public app](https://farmerjohn.streamlit.app/)

## The farmer journey

1. **Understand the farm.** Choose a regional map context, then use the Ames demonstration or enter farm coordinates. Enter crop history and dates, soil information, water access, priorities, equipment capacity and a crop outlet.
2. **Analyse environmental conditions.** Use bundled Ames weather or request daily NASA POWER temperature, precipitation and optional modeled soil-wetness indices for the chosen coordinates. A separate vegetation example is available at Ames.
3. **Identify vulnerable periods.** Review heat days, rainfall gaps and possible soil-cover gaps inside the entered crop calendar. These are screening flags to verify locally.
4. **Compare rotation strategies.** Compare the current sequence with up to two reviewed alternatives. Cards explain changes, priority trade-offs and next checks; a compact table compares cover, diversity, work and water. Excluded options have reasons.
5. **Stress-test the options.** Replay a historical season under unchanged, hotter, drier, wetter or custom conditions. Inspect weather exposure and rainfall during assumed uncovered months.
6. **Explain and save.** Review evidence and uncertainty, ask the report helper questions, and download a readable farm summary or full technical JSON report. Optional local Ollama provides AI explanations.

The reviewed alternative catalogue currently covers **Iowa corn/soybean systems**: cereal rye after corn before soybean, and a longer cycle involving a small grain and red clover. Constraints or missing local evidence can leave fewer than three options. The app does not invent alternatives for unsupported regions.

## Run locally

Extract the project and open the `Crop_Protection_Tool` folder in VS Code. In its terminal, run each command separately.

**macOS / Linux**

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run map_app.py
```

**Windows**

```powershell
py -m pip install -r requirements.txt
py -m streamlit run map_app.py
```

Keep the terminal open and open the local URL Streamlit displays. On macOS, `Start_Mac.command` is also included. If a command reports a missing file, check that the terminal is inside the extracted project folder.

## Data and sources

| Input | Used for | Coverage and limits |
| --- | --- | --- |
| NASA POWER daily `T2M_MAX`, `PRECTOTCORR` | Heat and rainfall exposure | Bundled 8,766 daily records, 2001–2024, at 42.03°N, 93.62°W near Ames, Iowa; `data/power_daily.csv`. |
| Live NASA POWER point requests | Location-specific daily weather; optional `GWETTOP` / `GWETROOT` | Requires internet. Availability, units and metadata are retained in the report. Failed requests do not substitute Ames. |
| NASA MODIS/Terra `MOD13Q1.061`, via AppEEARS | Quality-filtered NDVI vegetation context | Ames sample, 2024 only; `data/modis_2024.csv`. A boundary composite from 2023 is excluded. |
| Supplied temperature workbook | Regional summer-temperature map and historical comparison | `data/usa_temperature_2000_2025.xlsx`. Monthly 2-m air temperature (T2M) by grid point, 2000–2025, obtained from NASA POWER (https://power.larc.nasa.gov/) as confirmed by the team member who downloaded it. The exact POWER product and export settings were not recorded; monthly columns and Celsius units are inferred from the file. |
| US Census state boundaries | Clip smooth map shading to state outlines | Generalized 2024 boundaries; display only, not field boundaries. |
| Farmer inputs and cited agricultural references | Crop calendars, soil context, constraints and rotation examples | Soil and management information is entered by the user. No local soil-survey dataset is bundled. |

See [SOURCES.md](SOURCES.md) for the source register and disclosures. GPM/IMERG and Landsat imagery are **not used by the current main app**.

## How to interpret the results

- **Map:** Smooth shading interpolates the supplied coarse grid for display only. Calculations use original sampled values. A state outline or selected grid point is not a verified farm parcel.
- **Weather:** Long history charts use monthly summaries for readability; stress-test calculations use daily data. Missing observations remain missing. Eligible replay seasons require at least 95% valid coverage inside the entered growing months.
- **Crop timing:** Planting/harvest dates define a growing-month screening window. They do not identify physiological stages. Calendar gaps are not proof of bare soil: residues or unrecorded cover can remain.
- **Rotation comparison:** Rules screen practical constraints. Internal 0–2 catalogue attributes, equally weighted across supported selected priorities, only order alternatives. They are not a suitability model, success probability or NASA-measured benefit. Water savings are not scored.
- **Stress tests:** Temperature offsets and rainfall multipliers perturb a historical season. Shared crop calendars produce matching heat and rainfall-gap counts across options. Cover assumptions change uncovered-month accounting only.
- **Soil and vegetation:** Modeled wetness indices are not a field soil test or automatically equivalent to volumetric water content. NDVI does not establish crop identity, bare soil or the cause of stress. The Ames vegetation pixel is not transferred to other locations.

**TerraRoute does not forecast next year's weather or predict crop yield, profit, erosion, water savings or soil-health gains.** Use it to shortlist questions and options for local farmer/agronomist review.

## Questions and optional AI

The built-in **report helper** works without an AI service. Four question buttons and a text box explain current rotation options, stress tests, information gaps and sources using deterministic Python responses. Unsupported questions are identified rather than answered with invented facts.

For open-ended AI explanations, run Ollama on the **same computer as the Streamlit Python process**:

```bash
ollama pull llama3.2:3b
```

Start Ollama, run TerraRoute locally and check the connection in the app. The model receives the current report and curated reference notes; its answers are not automatically verified. On Streamlit Cloud, `localhost` refers to the hosted server, so it cannot reach Ollama on a visitor's Mac. No hosted AI service or credentials are included.

## Deploy and update

Commit the app files, `requirements.txt` and required `data/` contents to GitHub. For a repository containing the outer project folder, set the Streamlit entry point to:

```text
Crop_Protection_Tool/map_app.py
```

If the project contents are at the repository root, use `map_app.py`. Do not use the old `app.py` entry point. After local edits, commit and push to the branch connected to your deployment; then check the published app. Replacing a folder on your computer alone does not publish it.

Do not commit credentials, machine-specific caches or private farm information. The archive provided here does not itself push changes to GitHub or update the public app.

## Project files

| File | Role |
| --- | --- |
| `map_app.py` | Streamlit interface and six-step journey |
| `map_layers.py` | Grid selection, smooth map surface and state clipping |
| `data_access.py` | Live NASA POWER retrieval and metadata |
| `analysis_v2.py`, `exposure.py` | Crop calendars, weather screening and scenario calculations |
| `crop_catalog.py`, `recommender.py` | Reviewed examples, constraints and planning attributes |
| `report_help.py` | Built-in report-question helper |
| `ollama_chat.py` | Optional local AI client |
| `MAP_SUBMISSION.md` | Submission text to review against the final deployment |

Earlier forecasting notebooks, scripts and outputs remain as research artifacts. They are not the main app's recommendation engine or evidence of validated year-ahead forecast skill.

## AI assistance

**Idea and team.** The TerraRoute idea was developed by the team (Chan Sum Choy Levon, Chan Bun Long, Tjong Jia Hui Kenneth, Jing Song Ooi, Yeung Han Jie). We brainstormed it against the challenge requirements and aimed to be creative while keeping the tool easy for farmers to use. AI did not contribute to the idea.

**AI tools used.** AI coding assistants (Claude Code, and ChatGPT/Codex) helped write and refactor Python/Streamlit code, draft interface wording and documentation, and bundle app assets. The optional Ollama assistant produces AI-generated explanations that are not verified agronomic advice; the built-in report helper is deterministic Python, not an AI model. No environmental data are AI-generated: observations come from NASA POWER and MODIS.
