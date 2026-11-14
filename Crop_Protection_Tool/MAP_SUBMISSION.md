# TerraRoute — submission draft

Review this text against the final deployed app before submitting. Add the team's actual repository and demo links.

## Project name

TerraRoute

## High-level project summary

TerraRoute is a crop-rotation decision-support prototype that helps farmers explore how changes to a crop sequence could fit their soil conditions, priorities and practical constraints. It connects NASA environmental evidence to a six-step journey: understand the farm, analyse conditions, identify vulnerable periods, compare rotation options, stress-test historical scenarios and explain the results.

Farmers compare their current approach with supported cover-crop and diversification alternatives. Plain-language cards show potential roles, trade-offs, supporting references and next checks. The aim is to make rotation planning easier to discuss and review locally, without treating regional weather data as proof of field-level suitability or future benefits.

## Why it matters

Rotation changes involve more than selecting another crop. Farmers need to consider soil cover, water demand, crop timing, machinery and a market or forage use. TerraRoute brings those considerations together with environmental evidence so users can see where a promising option also creates a practical constraint or an unanswered question.

## Detailed project description

1. **Understand the farm:** collect location, dated crop history, intended crop, local soil information, water access, farmer priorities and implementation constraints.
2. **Analyse environmental conditions:** display regional historical temperature context and bundled or live NASA POWER daily weather. Request optional modeled soil-wetness indices. Show a separate quality-filtered Ames vegetation example.
3. **Identify vulnerable periods:** derive growing-month and potential cover-gap windows from entered crop dates; screen historical heat days and rainfall gaps for review. These windows do not establish actual crop stages or bare soil.
4. **Compare rotations:** retain the current sequence as a baseline and offer up to two reviewed Iowa corn/soybean alternatives: cereal rye after corn before soybean, and a longer cycle with a small grain and red clover. Explain exclusions where equipment, crop outlets, cover-management capacity or regional evidence are limiting.
5. **Stress-test:** apply transparent hotter, drier, wetter or custom changes to a historical weather season. Show common crop-season weather exposure once and compare rainfall during assumed uncovered months. The tool does not simulate rotation-induced changes to weather or soil water balance.
6. **Explain:** show evidence, practical trade-offs, uncertainties and next checks. Provide a built-in report helper, optional local Ollama AI explanations and downloadable text/JSON reports.

The application uses Python, Streamlit, pandas, NumPy, Plotly and the libraries listed in `requirements.txt`. A small rule-based crop catalogue and transparent exposure calculations support the workflow; it does not contain a trained crop-response model.

## NASA data and resources used

- **NASA POWER daily weather:** bundled `T2M_MAX` and `PRECTOTCORR`, 8,766 daily records for 2001–2024 at 42.03°N, 93.62°W near Ames, Iowa. Live point retrieval can request the selected coordinates and optional `GWETTOP` / `GWETROOT` modeled soil wetness, subject to availability.
- **NASA MODIS/Terra MOD13Q1.061:** NDVI and pixel reliability extracted through NASA AppEEARS, Ames sample, 2024. Good-quality observations enter the vegetation panel.
- **Supplied temperature workbook:** used for regional historical map context. Its NASA origin is user-attributed; original export metadata and inferred monthly schema/units must be confirmed before a definitive provenance claim.

GPM/IMERG and Landsat imagery are not used by the current main app. Full source details are in `SOURCES.md`.

## Other data and references

US Census generalized state boundaries clip the map display. Farmer-entered soil, crop and management information supplies local context. Iowa State Extension guidance, an Iowa rotation study and NRCS cover-crop guidance support the reviewed examples and water-use cautions. No verified farm boundary, local soil-survey dataset or measured soil-health outcomes are bundled.

## What is implemented and what remains limited

The app implements mapping, structured inputs, point weather retrieval, historical screening, conditional rotation comparisons, scenario perturbations, explanations and report downloads. The reviewed alternative catalogue is limited to Iowa corn/soybean systems. Other locations can use loaded weather evidence but do not receive invented regional alternatives.

Historical what-if scenarios are not future weather forecasts. Equal growing-month windows produce equal heat and rainfall-gap counts. Living cover uses water, and actual establishment is unverified. Weather grids and a vegetation pixel cannot establish crop suitability, irrigation requirements, yield, profit, erosion reduction or soil-health gains. Modeled wetness is not a field soil test.

## Links

- Public app: https://farmerjohn.streamlit.app/
- Code repository: add the team's final public GitHub URL.
- Demo: add a publicly accessible seven-slide presentation or video of 30 seconds or less, following the supplied submission instructions.

Check that each link works without a password, permission request or registration. Confirm the public app has received the latest committed changes.

## Use of SI / AI assistance

ChatGPT/Codex assisted with concept exploration, Python code, interface wording and documentation. Optional question answering uses a locally installed Ollama model. The public report helper uses deterministic responses from current report fields and is not an AI model. Environmental observations are supplied or retrieved NASA data; crop-calendar and scenario settings are planning assumptions. The team must accurately disclose its actual use of AI and review all content against the event's current rules.

## 30-second demo narration

TerraRoute helps farmers explore crop rotations with NASA data. Enter crop history, soil conditions and priorities. Inspect weather exposure and possible cover gaps, then compare the current rotation with supported alternatives. Replay a difficult season under hotter, drier or wetter conditions. Clear explanations show the evidence, trade-offs and missing information, helping farmers decide what to investigate locally before changing their rotation.

## Seven-slide demo outline

1. TerraRoute and the farmer's rotation-planning question.
2. Why soil, water, timing and practical constraints belong in one decision.
3. NASA POWER and MODIS evidence, plus farmer inputs and their coverage limits.
4. Enter an Iowa corn/soybean example and inspect vulnerable periods.
5. Compare three options; change a constraint and explain an exclusion.
6. Run a historical what-if scenario; show assumptions and uncertainty.
7. Outcome, limitations, source attribution and public project links.

## Deployment entry point

Use `Crop_Protection_Tool/map_app.py` when the project folder sits inside the repository, or `map_app.py` when its contents are at the repository root. The older `app.py` instruction does not apply to the current TerraRoute app.
