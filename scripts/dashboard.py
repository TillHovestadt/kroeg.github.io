from pathlib import Path

import geopandas as gpd
import geoviews as gv
import holoviews as hv
import panel as pn
import hvplot.pandas  # noqa: F401
import pandas as pd
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap

pn.extension("bokeh")
gv.extension("bokeh")

# -----------------------------
# USER SETTINGS
# -----------------------------

SCRIPT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = SCRIPT_DIR.parent

POLYGON_FILE = PROJECT_ROOT / "data" / "synthetic_data.gpkg"

POSTCODE_COL = "postcode"
GROUP_COL = "stedelijkheid"            # your 4-value grouping variable

# Friendly labels -> base variable names
LABELS = {
    "All Third Places": "third_places_total_ranked",
    "All Third Places except Medical Places": "third_places_non_medical_total_ranked",
    "All Third Places except Medical and Retail Places": "third_places_non_medical_non_retail_total_ranked",
    "Medical Places only": "third_places_medical_ranked",
    "Food and Beverage only": "third_places_food_beverage_ranked",
    "Retail Places only": "third_places_retail_ranked",
    "Community Places only": "third_places_community_ranked",
    "Cultural Places only": "third_places_cultural_ranked",
    "Sport and Leisure only": "third_places_sport_leisure_ranked",
}


GROUP_PALETTE = {
    # adjust if your grouping variable values are 1..4 or names
    "0": "#4C78A8",
    "1": "#4C78A8",
    "2": "#F58518",
    "3": "#54A24B",
    "4": "#B279A2",
    "5": "#B279A2",
}

INPUT_CRS = "EPSG:28992"
DISPLAY_PROJ = ccrs.GOOGLE_MERCATOR

# -----------------------------
# DATA
# -----------------------------
gdf = gpd.read_file(POLYGON_FILE).reset_index(drop=True)

gdf["geometry"] = gdf["geometry"].simplify(tolerance=50, preserve_topology=True)

if gdf.crs is None:
    gdf = gdf.set_crs(INPUT_CRS)
elif str(gdf.crs) != INPUT_CRS:
    gdf = gdf.to_crs(INPUT_CRS)

# normalize postcode to string, preserve leading zeros if present
gdf[POSTCODE_COL] = gdf[POSTCODE_COL].astype(str).str.strip()

group_values = [str(x) for x in pd.unique(gdf[GROUP_COL].dropna())]
mode_options = ["universal", "bygroup"] + [f"only_group_{g}" for g in group_values]

# -----------------------------
# WIDGETS
# -----------------------------
label_select = pn.widgets.Select(
    name="Indicator",
    options=list(LABELS.keys()),
    value=list(LABELS.keys())[0],
)

mode_select = pn.widgets.Select(
    name="Construction",
    options=mode_options,
    value="universal",
)

postcode_input = pn.widgets.TextInput(
    name="Search postcode",
    placeholder="Type postcode and press enter",
)

info = pn.pane.Markdown("")

# -----------------------------
# HELPERS
# -----------------------------
def nice_gradient(base_color: str):
    return LinearSegmentedColormap.from_list(
        "grad",
        ["#ffffff", base_color],
    )

def polygon_layer(
    data: gpd.GeoDataFrame,
    value_col: str,
    base_color: str,
    hover_cols=None,
    colorbar=False,
    title=None,
):
    if data.empty:
        return hv.Text(0, 0, "No data to display")

    cmap = nice_gradient(base_color)

    # no tiles here; we add one tile layer once in the final overlay
    return data.hvplot.polygons(
        c=value_col,
        geo=True,
        crs=ccrs.epsg(28992),
        projection=DISPLAY_PROJ,
        cmap=cmap,
        clim=(float(data[value_col].min()), float(data[value_col].max())),
        colorbar=colorbar,
        hover_cols=hover_cols or [POSTCODE_COL],
        line_color="white",
        line_width=0.15,
        frame_width=1100,
        frame_height=750,
        title=title,
    )

def highlight_layer(data: gpd.GeoDataFrame):
    if data.empty:
        return None

    return data.hvplot.polygons(
        geo=True,
        crs=ccrs.epsg(28992),
        projection=DISPLAY_PROJ,
        color=None,
        fill_alpha=0,
        line_color="red",
        line_width=3,
        hover_cols=[],
        frame_width=1100,
        frame_height=750,
    )

def build_map(label, mode, postcode):
    stem = LABELS[label]
    universal_col = stem
    bygroup_col = f"{stem}_by_urbanisation"

    df = gdf.copy()

    # normalize postcode input
    q = (postcode or "").strip()

    # base highlight subset
    if q:
        hit = df[df[POSTCODE_COL] == q]
    else:
        hit = df.iloc[0:0]

    # -------------------------
    # UNIVERSAL
    # -------------------------
    if mode == "universal":
        sub = df.dropna(subset=[universal_col]).copy()

        base = polygon_layer(
            sub,
            universal_col,
            base_color="#4C78A8",
            hover_cols=[POSTCODE_COL, GROUP_COL, universal_col],
            colorbar=True,
            title=f"{label} — universal",
        )

        if q and not hit.empty:
            base = base * highlight_layer(hit)

        if q and hit.empty:
            info.object = f"**No postcode found:** `{q}`"
        elif q:
            info.object = f"**Highlighted postcode:** `{q}`"
        else:
            info.object = ""

        return base

    # -------------------------
    # BYGROUP / ONLY ONE GROUP
    # -------------------------
    if mode == "bygroup":
        plot_df = df.dropna(subset=[GROUP_COL, bygroup_col]).copy()
        groups_to_show = group_values
        title = f"{label} — by group"

    elif mode.startswith("only_group_"):
        chosen_group = mode.replace("only_group_", "")
        plot_df = df[(df[GROUP_COL].astype(str) == chosen_group)].dropna(
            subset=[GROUP_COL, bygroup_col]
        ).copy()
        groups_to_show = [chosen_group]
        title = f"{label} — only group {chosen_group}"

    else:
        raise ValueError(f"Unknown mode: {mode}")

    overlays = []
    for grp in groups_to_show:
        sub = plot_df[plot_df[GROUP_COL].astype(str) == str(grp)].copy()
        if sub.empty:
            continue

        base_color = GROUP_PALETTE.get(str(grp), "#4C78A8")
        overlays.append(
            polygon_layer(
                sub,
                bygroup_col,
                base_color=base_color,
                hover_cols=[POSTCODE_COL, GROUP_COL, bygroup_col],
                colorbar=False,
                title=title if not overlays else None,
            )
        )

    base = hv.Overlay(overlays) if overlays else hv.Text(0, 0, "No data to display")

    if q and not hit.empty:
        base = base * highlight_layer(hit)

    if q and hit.empty:
        info.object = f"**No postcode found:** `{q}`"
    elif q:
        info.object = f"**Highlighted postcode:** `{q}`"
    else:
        info.object = ""

    return base

# reactive view
@pn.depends(label_select, mode_select, postcode_input)
def view(label, mode, postcode):
    return build_map(label, mode, postcode)

template = pn.template.FastGridTemplate(

    title="Postcode dashboard",

)

controls = pn.Card(
    label_select,
    mode_select,
    postcode_input,
    info,
    title="Controls",
    collapsed=False,
)

template.sidebar.append(controls)
template.main.append(view)
template.servable()

'''
template = pn.template.FastListTemplate(
    title="Third Places Dashboar",
    sidebar=[
        pn.pane.Markdown("## Controls"),
        label_select,
        mode_select,
        #postcode_input,
        info,
    ],
    main=[view],
)
'''

template.servable()