# TerraRoute — submission draft

Review this text against the final deployed app before submitting. Add the team's actual repository and demo links.

## Project name

TerraRoute

## High-level project summary

TerraRoute is a crop-rotation decision-support prototype that helps farmers explore how changes to a crop sequence could fit their soil conditions, priorities and practical constraints. It connects NASA environmental evidence to a six-step journey: understand the farm, analyse conditions, identify vulnerable periods, compare rotation options, stress-test historical scenarios and explain the results.

For any location, TerraRoute turns NASA POWER data into a plain "farm at a glance": a month-by-month risk calendar (crops, dry months, frost, heat, soil wetness) and a few short takeaways. Farmers then compare their current rotation with two alternatives, each with a 12-month crop strip and indicators computed from their own crop dates and NASA climate. Plain-language cards show trade-offs, supporting references and next checks. The aim is to make rotation planning easier to discuss and review locally, without treating regional weather data as proof of field-level suitability or future benefits.

## Why it matters

Rotation changes involve more than selecting another crop. Farmers need to consider soil cover, water demand, crop timing, machinery and a market or forage use. TerraRoute brings those considerations together with environmental evidence so users can see where a promising option also creates a practical constraint or an unanswered question.

## Detailed project description

1. **Understand the farm:** collect location (typed coordinates in another state move the map to that state automatically), dated crop history, intended crop, local soil information, water access, farmer priorities and implementation constraints.
2. **Analyse environmental conditions:** display regional historical temperature context and bundled or live NASA POWER daily weather for any coordinates, including modeled root-zone soil wetness. Build an average-year chart (rain, crop water need from the Turc evapotranspiration estimate, soil wetness), a month-by-month risk calendar and plain-language takeaways. Show a separate quality-filtered Ames vegetation example.
3. **Identify vulnerable periods:** derive growing-month and potential cover-gap windows from entered crop dates; screen historical heat days and rainfall gaps for review. These windows do not establish actual crop stages or bare soil.
4. **Compare rotations:** retain the current sequence as a baseline and offer two alternatives. Iowa corn/soybean farms get locally reviewed examples (cereal rye after corn before soybean, and a longer cycle with a small grain and red clover). Every other location gets a general climate screen that picks a cover crop for the longest bare window and a crop that suits the growing season (never a poor climate fit; a drought-tolerant crop from a family already in the rotation is allowed), each showing its climate fit, labelled "not locally reviewed" and quoting the NASA numbers behind each choice. Indicators (months with living cover, rain on bare soil, crop families, extra water demand, climate fit) and a 12-month crop strip per option are calculated from the data. Explain exclusions where equipment, crop outlets or cover-management capacity are limiting.
5. **Stress-test:** apply transparent hotter, drier, wetter or custom changes to the NASA record, recompute the climate (temperature shift, rain factor, evaporative demand), and report for each option the rain on bare soil, dry months while crops grow and frost-likely months for the new crop, with a one-line verdict. The tool does not simulate rotation-induced changes to weather or a full soil water balance.
6. **Explain:** show evidence, practical trade-offs, uncertainties and next checks. Provide a built-in report helper, optional local Ollama AI explanations and downloadable text/JSON reports.

The application uses Python, Streamlit, pandas, NumPy, Plotly and the libraries listed in `requirements.txt`. A small rule-based crop catalogue and transparent exposure calculations support the workflow; it does not contain a trained crop-response model.

## NASA data and resources used

- **NASA POWER daily weather (live point API, community AG):** `T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, `ALLSKY_SFC_SW_DWN`, `GWETTOP` and `GWETROOT` for any coordinates, subject to availability. Used for heat, frost, rain, evaporative demand and soil wetness. If the live request fails, a saved offline record for 42.03°N, 93.62°W near Ames, Iowa (all seven parameters, 8,766 daily records, 2001–2024, `data/power_daily_full.csv`) keeps the Ames sample working.
- **NASA MODIS/Terra MOD13Q1.061:** NDVI and pixel reliability extracted through NASA AppEEARS, Ames sample, 2024. Good-quality observations enter the vegetation panel.
- **Supplied temperature workbook:** used for regional historical map context. Source: NASA POWER (https://power.larc.nasa.gov/), as confirmed by the team member who downloaded it. The exact POWER product and export settings were not recorded; monthly columns and Celsius units are inferred.

GPM/IMERG and Landsat imagery are not used by the current main app. Full source details are in `SOURCES.md`.

## Other data and references

US Census generalized state boundaries clip the map display. Farmer-entered soil, crop and management information supplies local context. Iowa State Extension guidance, an Iowa rotation study and NRCS cover-crop guidance support the reviewed examples and water-use cautions. The general-screen crop table holds indicative values written by the team; they are not locally reviewed and must be verified (for example with FAO ECOCROP or extension advice). No verified farm boundary, local soil-survey dataset or measured soil-health outcomes are bundled.

## What is implemented and what remains limited

The app implements mapping, structured inputs, point weather retrieval for any location, a risk calendar, historical screening, rotation comparisons with data-computed indicators, scenario stress tests per option, explanations and report downloads. The locally reviewed alternatives cover Iowa corn/soybean systems only; elsewhere the options come from a general climate screen of indicative values that is clearly labelled and not locally reviewed.

Historical what-if scenarios are not future weather forecasts. Indicators describe the plan, not guaranteed outcomes. NASA weather is gridded (roughly 50–70 km), not field-scale. Living cover uses water, and actual establishment is unverified. Weather grids and a vegetation pixel cannot establish crop suitability, irrigation requirements, yield, profit, erosion reduction or soil-health gains. Modeled wetness is not a field soil test.

## Links

- Public app: https://farmerjohn.streamlit.app/
- Code repository: add the team's final public GitHub URL.
- Demo: add a publicly accessible seven-slide presentation or video of 30 seconds or less, following the supplied submission instructions.

Check that each link works without a password, permission request or registration. Confirm the public app has received the latest committed changes.

## Use of SI / AI assistance

**Idea and team.** The TerraRoute idea was developed by the team (Chan Sum Choy Levon, Chan Bun Long, Tjong Jia Hui Kenneth, Jing Song Ooi, Yeung Han Jie). We brainstormed it against the challenge requirements and aimed to be creative while keeping the tool easy for farmers to use. AI did not contribute to the idea.

**AI tools used.** AI coding assistants (Claude Code, and ChatGPT/Codex) helped write and refactor Python/Streamlit code, draft interface wording and documentation, and bundle app assets. The optional Ollama assistant produces AI-generated explanations that are not verified agronomic advice; the built-in report helper is deterministic Python, not an AI model. No environmental data are AI-generated: observations come from NASA POWER and MODIS.

Optional question answering uses a locally installed Ollama model. Crop-calendar and scenario settings are planning assumptions.

## 30-second demo narration

TerraRoute turns NASA data into a plain farm risk calendar for any location. Enter your crops and priorities, see dry, frost and heat months at a glance, then compare your rotation with two alternatives on indicators calculated from the data. Stress-test them under hotter or drier weather and get a one-line verdict. Clear evidence and limits help farmers decide what to check locally.

## Seven-slide demo outline

1. TerraRoute and the farmer's rotation-planning question.
2. Why soil, water, timing and practical constraints belong in one decision.
3. NASA POWER (seven parameters, live for any location with an offline Ames fallback) and MODIS evidence, plus farmer inputs and their coverage limits.
4. Load a farm anywhere (Iowa, then California); show the risk calendar and takeaways.
5. Compare three options with crop strips and indicators; show a general climate-screened option and its NASA-based reason.
6. Run a hotter and drier stress test; show the verdict, assumptions and uncertainty.
7. Outcome, limitations, source attribution and public project links.

## Deployment entry point

Use `Crop_Protection_Tool/map_app.py` when the project folder sits inside the repository, or `map_app.py` when its contents are at the repository root. The older `app.py` instruction does not apply to the current TerraRoute app.
