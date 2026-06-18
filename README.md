# Third Places Index — Static Quarto + Panel Dashboard

A static Quarto + Panel dashboard that visualizes a **Third Places Index** for the Netherlands. The site is built for GitHub Pages: maps are pre-rendered as standalone Plotly HTML files, and a small JavaScript dropdown swaps between them, so no Python server is needed once the site is built.

## About the data

A "third place" is a place outside home and work where people spend time — cafés, shops, community centers, sports clubs, and the like. This index ranks every PC4 area (a 4-digit Dutch postal code area) by how many third places it has, relative to all other PC4 areas, using company data from FirmBackbone.

The index is a percentile-style score from 0 to 100. A score of 30 means 70% of PC4 areas have *more* third places of that type, and 30% have fewer.

Third places are split into six categories:

| Code | Category |
|---|---|
| a | Food and beverage establishments |
| b | Retail and services |
| c | Community spaces (noncommercial) |
| d | Cultural venues |
| e | Sport and leisure venues |
| f | Medical services |

Three aggregate scores are also provided: a **total** across all six categories, a **non-medical total** (a–e), and a **non-medical, non-retail total** (a, c, d, e).

### Columns

| Column | Description |
|---|---|
| `PC4` | 4-digit postal code area |
| `Stedelijkheid` | Urbanisation level of the area, based on address density (levels below) |
| `geometry` | Polygon geometry of the PC4 area, used to draw the map |

Every ranking measure comes in two versions: a national `_ranked` column (ranked against all PC4 areas) and a `_ranked_by_urbanisation` column (ranked only against PC4 areas in the same urbanisation class). The measures are:

| Ranking column (national version shown) | Measures |
|---|---|
| `third_places_total_ranked` | All third places |
| `third_places_non_medical_total_ranked` | Non-medical third places (a–e) |
| `third_places_medical_ranked` | Medical services (f) |
| `third_places_food_beverage_ranked` | Food and beverage establishments (a) |
| `third_places_retail_ranked` | Retail and services (b) |
| `third_places_community_ranked` | Community spaces (c) |
| `third_places_cultural_ranked` | Cultural venues (d) |
| `third_places_sport_leisure_ranked` | Sport and leisure venues (e) |
| `third_places_non_medical_non_retail_total_ranked` | Non-medical, non-retail third places (a, c, d, e) |

Each row above also exists with a `_by_urbanisation` suffix (e.g. `third_places_total_ranked_by_urbanisation`).

**Stedelijkheid (urbanisation) levels:**

| Level | Description | Address density |
|---|---|---|
| 1 | Extremely urbanised | 2,500+ per km² |
| 2 | Strongly urbanised | 1,500–2,500 per km² |
| 3 | Moderately urbanised | 1,000–1,500 per km² |
| 4 | Hardly urbanised | 500–1,000 per km² |
| 5 | Not urbanised | Fewer than 500 per km² |

## Data pipeline available only inside SANE

The maps used by the dashboard are produced by four notebooks, run in order:

1. **`1_data_processing_sbi_codes.ipynb`** — Loads 2024 KVK (Dutch business registry) data and a codebook mapping each SBI code (industry classification) to a third-place category, then counts, per PC4 area, how many businesses fall into each category.
2. **`2_kvk_cbs_linking.ipynb`** — Loads CBS open geospatial PC4 data, keeps the `geometry`, `PC4`, and `Stedelijkheid` columns, merges it with the category counts from step 1 on `PC4`, and saves the result as a `.gpkg` file.
3. **`3_index_ranking.ipynb`** — Loads that `.gpkg` file and, for every third-place column, ranks PC4 areas by count and rescales the ranks to run from 0 to 100, then repeats the same ranking within each urbanisation category. The raw counts are dropped afterward, leaving only the ranking columns described above, and the result is saved as the final `.gpkg`.
4. **`4_visualization.ipynb`** — Loads the final `.gpkg`, checks that it loaded correctly and that the coordinate reference system is set as expected, builds an example map with matplotlib and geopandas, and then plots a color-coded map for every index. These are the maps that get exported into `plots/` for the dashboard below. A future iteration may add Folium for additional plotting, pending approval of `offline_Folium` for use in SANE.

## Dashboard

This project is set up for GitHub Pages.

### File naming convention

Put your pre-rendered panel.holoviz map HTML files into `plots/` using this pattern:

```text
<group_level>__<indicator>.html
```

Examples:

```text
plots/district__poverty.html
plots/region__income.html
plots/country__deprivation.html
```

For this project, that would mean one file per ranking column from the table above, e.g. `plots/pc4__third_places_total_ranked.html` or `plots/pc4_by_urbanisation__third_places_food_beverage_ranked.html`.

### Build

Run:

```bash
python scripts/panel_mapping.ipynb
quarto render
```

That script will:

1. scan `plots/` and create `plot_manifest.json`
2. export the static Panel dashboard to `_build/panel-dashboard.html`
3. render the Quarto site to `docs/`
4. copy the Panel export and plot HTML files into `docs/`

### Publish to GitHub Pages

In your repository settings, set GitHub Pages to serve from the `docs/` folder on the branch you push.

## Notes

- The Panel dashboard is static because it only swaps between pre-rendered HTML files.
- The dropdown behavior is implemented in JavaScript, so it works on GitHub Pages without a Python server.
- The final dataset contains only the ranking columns described above, not the underlying counts of third places.
