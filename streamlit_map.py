# streamlit_map.py
import os

from dotenv import load_dotenv
import geopandas as gpd
import streamlit as st
import pydeck as pdk

# ── streamlit page setup ──────────────────────────────────────────────────────
st.set_page_config(page_title="WIO LMMA IOC Map", layout="wide")
st.title("WIO LMMA IOC Map")

# ── read Mapbox token from .env ───────────────────────────────────────────────
load_dotenv()
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

if not MAPBOX_API_KEY:
st.error(
    "MAPBOX_API_KEY is missing. Add it to your .env file "
    "(e.g., MAPBOX_API_KEY=pk.abc...) and restart Streamlit."
)
st.stop()

# ── load shapefile ────────────────────────────────────────────────────────────
shapefile_path = "wio_lmma_ioc.shp"

if not os.path.exists(shapefile_path):
st.error(
    f"Could not find '{shapefile_path}'. Place all shapefile components "
    "(.shp, .shx, .dbf, .prj, etc.) in the same directory as this script."
)
st.stop()

gdf = gpd.read_file(shapefile_path)

# ensure WGS84 lat/lon
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
gdf = gdf.to_crs(epsg=4326)

geojson = gdf.__geo_interface__

minx, miny, maxx, maxy = gdf.total_bounds
mid_lat = (miny + maxy) / 2
mid_lon = (minx + maxx) / 2

# ── build Deck.gl map ─────────────────────────────────────────────────────────
deck = pdk.Deck(
map_style="mapbox://styles/mapbox/light-v9",
mapbox_key=MAPBOX_API_KEY,
initial_view_state=pdk.ViewState(
    latitude=mid_lat,
    longitude=mid_lon,
    zoom=5,
    pitch=0,
),
layers=[
    pdk.Layer(
        "GeoJsonLayer",
        data=geojson,
        stroked=True,
        filled=True,
        opacity=0.6,
        get_fill_color=[82, 170, 225, 120],
        get_line_color=[12, 60, 90],
        line_width_min_pixels=1,
        pickable=True,
    )
],
tooltip={"text": "{Name of LM}\nCountry: {Country}"},
)

st.pydeck_chart(deck)

# ── attribute preview ─────────────────────────────────────────────────────────
st.subheader("Attribute preview")
st.dataframe(gdf.drop(columns="geometry").head())