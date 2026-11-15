# TerraRoute: final-day improvement plan

_Written Sun 15 Nov 2026, 13:45 SGT, after testing https://farmerjohn.streamlit.app and the `main` branch (commit f5b1872)._
**Submission deadline: tonight 23:59. Target: features frozen by 18:00, project submitted by 21:00.**

This file is the brief for Claude in VS Code. Each task below has a goal, what to change, and how to check it's done. Do them **in order**, one at a time, and commit after each.

---

## Test results (what works today)

| Step | Works | Problem |
|---|---|---|
| 1 Your Farm | Map, state/grid select, crop-history table with dates | The map uses a temperature workbook whose NASA source is **unconfirmed**. |
| 2/3 Weather & Water | **Live NASA POWER fetch works for any coordinates** (tested: 9,131 rows in about 20 s). Soil wetness (GWETTOP/GWETROOT) loads. | The soil-wetness chart is 25 years of daily lines, impossible to read. No water-balance view (rain vs evaporative demand). No frost signal. The rainfall-gap chart legend says "True/False". |
| 3 Vulnerable periods | Bare-month gaps come from crop dates. The worst historical season is auto-selected. | Results are spread over several charts. There's no single "risk calendar" a farmer can read in 5 seconds. |
| 4 Rotation choices | Three cards for **Iowa corn/soybean only** | **Any other location or crop gets only 1 option ("Keep current").** That fails the brief ("compare at least three"). There's no visual comparison. |
| 5 Hotter/Drier/Wetter | Works with loaded data | Heat days and dry runs are identical for all options, so the only difference shown is rain in uncovered months. |
| 6 Insights | Summary download, JSON report, report helper | Fine. |

**Rule risks, fix first:**
1. **The header logo and intro splash show the NASA "meatball" logo** ("TerraRoute × NASA", `https://i.imgur.com/k28tRZs.png`). The Space Apps rules forbid NASA logos and branding in project materials. **This must be removed.**
2. The README and SOURCES.md say AI was used for "concept exploration" / "idea exploration". The rules say AI must not be used to come up with the solution idea. The team must state **truthfully** what AI was used for. If the idea was the team's, say so and list only what AI actually did (code, text, etc.).
3. Images are hot-linked from imgur. If imgur rate-limits during judging, the logo disappears. Bundle images in the repo.

---

## Task 1: Remove NASA branding and bundle images (P0, ~20 min)
- Create `Crop_Protection_Tool/assets/`. Save a **TerraRoute-only** logo there (no NASA logo or name styled as a logo). If you only have the combined image, crop out the NASA part or use a text title.
- In `map_app.py`, replace every `https://i.imgur.com/...` URL (the page icon, `st.image`, the intro splash `<img>`, the chat-bubble background) with the local files. Use `st.image(str(ROOT/'assets/logo.png'))`, `page_icon=str(ROOT/'assets/icon.png')`. For HTML/CSS, embed as base64 data URIs.
- Keep plain-text mentions like "uses NASA POWER data". Those are fine.
- **Done when:** grepping the repo finds no `imgur` and no NASA logo image, and the page shows the TerraRoute logo.

## Task 2: Honest provenance and AI wording (P0, ~15 min, needs a human decision)
- Ask Ken where `data/usa_temperature_2000_2025.xlsx` came from. If it was downloaded from NASA POWER, write the exact source (API or Data Access Viewer, parameter T2M, dates) in README.md and SOURCES.md and remove "unconfirmed". If nobody knows, relabel the map in the app as "Supplied regional temperature grid (source being confirmed)" and don't list it as NASA data on the form.
- Rewrite the "AI assistance" sections in `README.md` and `Crop_Protection_Tool/SOURCES.md` so they accurately describe what AI did. Don't claim AI generated the idea unless that's true, and don't hide AI use either.

## Task 3: Better NASA data fetch (P1, ~30 min)
In `data_access.py`, extend the NASA POWER request (still the daily point API, community AG) to also fetch `T2M`, `T2M_MIN` and `ALLSKY_SFC_SW_DWN`, alongside the existing `T2M_MAX`, `PRECTOTCORR`, `GWETTOP`, `GWETROOT`. The API allows several parameters per call; split into two calls if it complains. Rename to friendly columns: `tmean_c`, `tmin_c`, `solar_mj`. Add the same columns to the Ames CSV fallback path as NaN, so the app never crashes when they're missing.
- Add a helper in a new file `climate.py`:
  - `monthly_climatology(daily)`: returns 12 rows (Jan–Dec) with the mean over all years of monthly rain (mm), mean temperature, the lowest Tmin, the share of years with frost (Tmin < 0 °C), mean GWETROOT, and **ET0** (mm/month).
  - ET0 (reference evapotranspiration) by the **Turc** equation, per day: if T > 0: `ET0 = 0.013 * T/(T+15) * (23.8856*Rs + 50)`, with T = tmean_c and Rs = solar_mj (MJ/m²/day). Otherwise 0. Sum per month, then average across years.
  - `deficit` flag: rain < 0.5 × ET0 and ET0 > 20 mm.
- **Done when:** loading Ames and loading a custom coordinate both give a 12-row climatology table without errors.

## Task 4: "Your farm at a glance" risk calendar (P1, ~45 min)
Replace the noisy daily soil-wetness line chart in Step 3 with:
1. **One combined monthly chart** (Plotly): bars = average monthly rain, line = ET0 (evaporative demand), second axis = root-zone soil wetness (%). Title it "Average year at your farm (NASA POWER, <start>–<end>)". Caption in plain words: "When the bars sit below the line, crops rely on stored soil water or irrigation."
2. **A 12-month risk calendar** (a small coloured table or heatmap with one column per month). Rows:
   - *Your crops* (crop name in growing months, "bare" in gap months, from `parse_history`)
   - *Dry* (deficit months)
   - *Frost* ("likely" if frost in ≥50% of years, "possible" if any year)
   - *Heat* (days ≥ 35 °C per year, averaged)
   - *Soil wetness* (GWETROOT %)
3. Three to five **plain-language takeaways** above it, generated from the numbers. Example: "Your field is bare Nov–Apr, when 263 mm of rain falls on uncovered soil." "Jul–Aug are water-deficit months." "Frost is likely Nov–Mar."
- Move the old daily charts into an expander called "Daily detail".
- Fix the rainfall-gap chart legend: "True/False" → "Inside crop season" / "Outside crop season".

## Task 5: Three rotation options for ANY location (P1, biggest gap, ~90 min)
Today `crop_catalog.options()` returns only "Keep current" outside Iowa corn/soybean. Keep the reviewed Iowa options exactly as they are, and **add a general climate-screened fallback** so every farm gets current + two alternatives:
- Create `general_options.py` with a small, clearly labelled table of crop groups (indicative values; mark them in the code and the UI as "general screening values, verify locally with FAO ECOCROP / extension advice"):

  | key | name | family | type | months | temp range °C (monthly mean) | frost tolerant | drought tolerant |
  |---|---|---|---|---|---|---|---|
  | rye | Cereal rye cover | grass | cover | 3–6 | 3–20 | yes | yes |
  | oats | Oats cover/forage | grass | cover | 3 | 8–22 | partly | no |
  | vetch | Hairy vetch cover (legume) | legume | cover | 4–5 | 5–22 | yes | partly |
  | sunnhemp | Sunn hemp cover (legume) | legume | cover | 3 | 22–35 | no | yes |
  | cowpea | Cowpea | legume | cash | 3 | 22–35 | no | yes |
  | chickpea | Chickpea | legume | cash | 4 | 15–28 | partly | yes |
  | sorghum | Sorghum | grass | cash | 4 | 22–35 | no | yes |
  | mustard | Mustard | brassica | cash | 4 | 10–25 | partly | partly |

- Logic:
  1. **"Cover the bare window"**: take the longest run of gap months from `parse_history`. Pick the cover crop whose temperature range best fits the climatology means in those months (from Task 3) and isn't killed by frost there. Sequence: current crops + that cover in the gap months.
  2. **"Diversify / water-wise"**: pick the cash legume or drought-tolerant crop that best fits the temperature in the main growing months and is a **different family** from the current crops. Sequence: current → that crop → back to current.
  3. Each option carries: why it was chosen (the numbers used), the fit result, and the risks: "needs local market", "needs establishment and termination", "verify with local agronomist".
- In `recommender.py`, use these when the reviewed catalogue doesn't apply, and keep the existing equipment, market and cover-feasibility exclusions. Label general options with a badge: "General climate screen (not locally reviewed)". Keep the Iowa cards labelled "Locally reviewed example".
- **Done when:** choosing e.g. California or Texas, or custom coordinates outside Iowa, after loading NASA data shows **3 cards**, each with a reason that quotes the NASA numbers.

## Task 6: Visual comparison of the 3 options (P1, ~45 min)
Below the cards, replace the text-only "practical differences" table with **indicator bars** computed from data, not opinion:
- *Months with living cover* (count per year)
- *Rain on bare soil* (mm/yr in uncovered months, from the climatology). Lower is better for erosion.
- *Crop families in the cycle* (count). More breaks pest cycles.
- *Extra water demand* (rough: does the option add a living crop in deficit months? none / some / high)
- *Climate fit* of the new crop (from Task 5's temperature fit: good / fair / poor)

Show these as a Plotly grouped bar chart or a coloured table with an arrow ▲▼ vs the current rotation. Add a caption: "Indicators describe the plan, not guaranteed outcomes."
Also add a **12-month crop strip** under each card (months coloured by crop, grey for bare).

## Task 7: Make Step 5 show differences between options (P2, ~30 min)
In the stress test, also report for each option, under the scenario: **rain falling on bare soil**, **number of deficit months during living cover** (cover uses water) and **frost months during the new crop**. Recompute the climatology with the offsets (T + Δ, rain × factor, and ET0 recomputed). Add a one-line verdict per scenario: "Under hotter & drier, Option B keeps the most months covered but adds water demand in Jul–Aug."

## Task 8: Clean-up and polish (P2, ~30 min)
- Delete `.DS_Store` and add it to `.gitignore`. Move unused legacy files (`journey.py`, `rotation_rules.py`, `state_temperature.py`, `year_outlook.py`, the notebook) into `Crop_Protection_Tool/legacy/`, but only if `map_app.py` doesn't import them. Check with grep first.
- Add a 3-line "How to use" box under the logo: 1) pick your farm, 2) enter crops and priorities, 3) compare options and download.
- Make sure the app has no `st.stop()` dead-ends that hide Steps 4–6 without a clear message.
- Rewrite the root `README.md`: problem → what TerraRoute does → screenshot → 6 steps → NASA data used (exact parameters) → how to run → limitations → team → AI use (accurate).

## Final checks (human, by 20:30)
- Open https://farmerjohn.streamlit.app in an **incognito** window. Test Ames, plus one non-Iowa location with "My coordinates" → Load. No red errors.
- Check on a phone.
- Take screenshots for the demo slides.
- Submission form: summary, details, NASA data list (POWER daily: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, GWETTOP, GWETROOT; MODIS MOD13Q1 NDVI via AppEEARS), AI-use answer, demo link (public, no login).