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
# Log current working directory
st.write("📍 Current working directory:", os.getcwd())

# Check if .env file exists
env_path = os.path.join(os.getcwd(), ".env")
st.write("🔍 Looking for .env file at:", env_path)
st.write("✓ .env file exists:" if os.path.exists(env_path) else "✗ .env file NOT found:", os.path.exists(env_path))

# Load environment variables with explicit path
load_dotenv_result = load_dotenv(dotenv_path=env_path, override=True)
st.write("📥 load_dotenv() returned:", load_dotenv_result)

# Try to get the API key
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")
st.write("🔑 MAPBOX_API_KEY loaded:", "Yes ✓" if MAPBOX_API_KEY else "No ✗")
if MAPBOX_API_KEY:
    st.write("🔑 Key preview:", MAPBOX_API_KEY[:15] + "..." if len(MAPBOX_API_KEY) > 15 else MAPBOX_API_KEY)

# Debug: Let's also try reading the file directly
st.write("🔍 Debug - Reading .env file directly:")
try:
    with open(env_path, 'r') as f:
        env_content = f.read()
        st.code(env_content[:100])  # Show first 100 chars
        # Manual parse
        for line in env_content.split('\n'):
            if line.strip().startswith('MAPBOX_API_KEY='):
                manual_key = line.strip().split('=', 1)[1]
                st.write("🔑 Manually parsed key:", manual_key[:15] + "...")
                if not MAPBOX_API_KEY:
                    MAPBOX_API_KEY = manual_key
                    st.warning("⚠️ Using manually parsed key as fallback")
except Exception as e:
    st.error(f"Error reading .env: {e}")

if not MAPBOX_API_KEY:
    st.error(
        "MAPBOX_API_KEY is missing. Add it to your .env file "
        "(e.g., MAPBOX_API_KEY=pk.abc...) and restart Streamlit."
    )
    st.stop()

# Set Mapbox token for PyDeck via environment variable
os.environ["MAPBOX_API_KEY"] = MAPBOX_API_KEY
st.success("✅ Mapbox API key successfully loaded and set!")

# ── load shapefile ────────────────────────────────────────────────────────────
shapefile_path = "wio_lmma_ioc.shp"
st.write("📂 Looking for shapefile:", shapefile_path)

if not os.path.exists(shapefile_path):
    st.error(
        f"Could not find '{shapefile_path}'. Place all shapefile components "
        "(.shp, .shx, .dbf, .prj, etc.) in the same directory as this script."
    )
    st.stop()

st.write("✓ Shapefile found!")
st.write("📊 Loading shapefile...")
gdf = gpd.read_file(shapefile_path)
st.write(f"✓ Loaded {len(gdf)} features from shapefile")

# ensure WGS84 lat/lon
st.write("🌍 Original CRS:", gdf.crs)
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    st.write("🔄 Converting to WGS84 (EPSG:4326)...")
    gdf = gdf.to_crs(epsg=4326)
    st.write("✓ CRS converted!")

geojson = gdf.__geo_interface__

minx, miny, maxx, maxy = gdf.total_bounds
mid_lat = (miny + maxy) / 2
mid_lon = (minx + maxx) / 2
st.write(f"🗺️ Map center: Lat={mid_lat:.4f}, Lon={mid_lon:.4f}")

# ── build Deck.gl map ─────────────────────────────────────────────────────────
st.write("🗺️ Building PyDeck map...")
deck = pdk.Deck(
map_style="mapbox://styles/mapbox/light-v9",
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
st.write("✓ Map created successfully!")

st.write("📺 Rendering map...")
st.pydeck_chart(deck, use_container_width=True)
st.success("✅ Map rendered!")

# ── attribute preview ─────────────────────────────────────────────────────────
st.subheader("Attribute preview")
st.dataframe(gdf.drop(columns="geometry").head())