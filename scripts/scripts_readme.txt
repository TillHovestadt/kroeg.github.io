# Scripts for the KROEG Index

###################
### What's here ###
###################

This folder holds the notebooks that turn the index data into the maps shown on the website.
There are three notebooks. The first two are the live pipeline; the third is a development
version kept for reference.

	1_add_polygons_to_data.ipynb   (file: add_polygons_to_data.ipynb)
		Attaches map shapes to the index data.
		1. Loads the index table from data/indexed_data.csv.
		2. Loads the PC4 area polygons from data/pc4_polygons.geojson.
		3. Merges the two on the postcode (PC4) field.
		4. Saves the combined geo-table as data/KROEG_index.gpkg (and a copy as
		   data/KROEG_index.csv). This .gpkg is the input for the next script.

	2_panel_mapping.ipynb          (file: panel_mapping.ipynb)
		Generates every map HTML file used by the dashboard.
		1. Loads data/KROEG_index.gpkg and sets the CRS to EPSG:28992 (Dutch RD New).
		2. Defines a blue-to-orange colour scale and two drawing functions: one for a
		   national map, one filtered to a single urbanisation level.
		3. Saves one national map per sector to     plots/<sector>.html
		   and one map per sector per level 1-5 to   plots/<sector>_by_urbanisation_<level>.html
		   Each file is a self-contained interactive map (saved with INLINE resources).
		These 55 files are what the dashboard loads into its iframe.

	(dev) create_maps.ipynb
		An earlier/alternative mapping notebook used during development. It works from
		synthetic data (data/synthetic_data.gpkg) and writes to site/maps/. Not part of
		the live build, but kept as a reference for the mapping approach.


#################
### To re-run ###
#################

Run add_polygons_to_data.ipynb first, then panel_mapping.ipynb. After the maps in plots/ are
updated, rebuild the website with 'quarto render' from the repository root.


############################
### Packages (Python) ###
############################

These notebooks use: pandas, geopandas, panel, hvplot/holoviews, bokeh, cartopy, matplotlib,
numpy, shapely. See requirements.txt in the repository root.
