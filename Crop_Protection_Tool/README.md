# TerraRoute

**NASA-powered crop rotation decision support for farmers.**

[Open the public app](https://farmerjohn.streamlit.app/)

## The problem

Farmers deciding whether to change their crop rotation face rising heat, uneven rain and fields left bare between crops. Weather data exists, but it is rarely turned into a plain answer to "what could I change, and what would it mean for my farm?"

## What TerraRoute does

TerraRoute takes your location and crop history, pulls NASA weather and soil-wetness data for that spot, and shows when your field is dry, frosty, hot or bare. It then compares your current rotation with two alternatives and stress-tests all three under hotter, drier or wetter weather. Everything is calculated from data and your inputs. It does not guess.


## The six steps

1. **Your Farm.** Pick a point on the regional temperature map, use the Ames sample farm or enter coordinates. If your coordinates are in another state, the map switches to that state automatically. Enter your crop history with dates, soil, water access, priorities, equipment and market.
2. **Weather & Water.** Load daily NASA POWER data for your point. The app shows an average-year chart (rain, crop water need, soil wetness), a month-by-month risk calendar (crops, dry, frost, heat, soil wetness) and plain-language takeaways.
3. **Vulnerable periods.** See heat days, rainfall gaps and bare months inside your crop calendar.
4. **Rotation choices.** Compare your current rotation with two alternatives, each with a 12-month crop strip and indicators computed from your dates and NASA climate (months with cover, rain on bare soil, crop families, extra water demand, climate fit).
5. **Hotter, Drier or Wetter.** Replay a historical season or shift temperature and rain. The app recalculates the climate and gives each option's rain on bare soil, dry months and frost months, with a one-line verdict.
6. **Insights.** Ask the report helper questions and download a readable summary or a full technical JSON report.

Alternatives come from two places. Iowa corn/soybean farms get **locally reviewed examples** (cereal rye cover, and a small grain with red clover). Every other farm gets a **general climate screen** that picks a cover crop and a different-family crop from a small table of indicative values. These are labelled "not locally reviewed" and must be verified locally (FAO ECOCROP or extension advice). The screen never proposes a crop with a poor temperature or frost fit, may suggest a drought-tolerant crop from a family already in your rotation (such as sorghum after corn), and shows each option's climate fit (good, fair or poor) on its card.

## NASA data used

| Dataset | Parameters | Used for |
| --- | --- | --- |
| NASA POWER daily point API (community AG) | `T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, `ALLSKY_SFC_SW_DWN`, `GWETTOP`, `GWETROOT` | Heat, frost, rain, evaporative demand (Turc equation from `T2M` and sunlight), soil wetness and stress tests. Fetched live for any coordinates; if the live request fails, the saved Ames record (`data/power_daily_full.csv`, all seven parameters, 2001–2024) is the offline fallback. `scripts/refresh_ames_csv.py` rebuilds it. |
| NASA POWER monthly `T2M` grid by state, 2000–2025 | `T2M` | Regional summer-temperature map. File `data/usa_temperature_2000_2025.xlsx`, obtained from NASA POWER as confirmed by a team member. The exact export settings were not recorded. |
| NASA MODIS/Terra `MOD13Q1.061` via AppEEARS | NDVI | Ames vegetation context, 2024 only. |

Other inputs: US Census state boundaries (map display only) and your own farm inputs. See [SOURCES.md](SOURCES.md) for the full source register.

## How to run

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run map_app.py
```

On Windows use `py` instead of `python3`. On macOS, `Start_Mac.command` also works. Live NASA requests need internet. To deploy on Streamlit Cloud, set the entry point to `map_app.py`.

## Limitations

- TerraRoute does **not** forecast weather or predict yield, profit, erosion, water savings or soil health. It shortlists options for review with a local farmer or agronomist.
- Indicators describe the plan, not guaranteed outcomes. Crop dates give a screening calendar, not growth stages, and a gap in dates is not proof of bare soil.
- NASA soil wetness is modelled, not measured in your field. Weather is at about 50–70 km grid scale, not field scale.
- General climate-screen values are indicative only. The Iowa options assume cover in March, April, October and November.
- The offline fallback covers Ames only; other locations need a live NASA connection.
- The vegetation example covers Ames only. The temperature workbook's export settings were not recorded.
- Stress tests are sensitivity tests on past weather, not predictions.

## Team

Chan Sum Choy Levon, Chan Bun Long, Tjong Jia Hui Kenneth, Jing Song Ooi, Yeung Han Jie.

## AI use

The TerraRoute idea was developed by the team. We brainstormed it against the challenge requirements and aimed to be creative while keeping the tool easy for farmers to use. AI did not contribute to the idea.

AI coding assistants (Claude Code, and ChatGPT/Codex) helped write and refactor Python/Streamlit code, draft interface wording and documentation, and bundle app assets. The optional Ollama assistant gives AI-generated explanations that are not verified advice; the built-in report helper is deterministic Python, not an AI model. No environmental data are AI-generated. Details are in [SOURCES.md](SOURCES.md).

## Project files

`map_app.py` is the app. `data_access.py` fetches NASA data, `climate.py` builds the monthly climatology, `general_options.py`, `crop_catalog.py` and `recommender.py` build the options, and `option_indicators.py` computes the indicators and stress test. `legacy/` holds earlier research scripts and the forecasting notebook, which the app does not use.
