# streamlit_map.py
import os

from dotenv import load_dotenv
import geopandas as gpd
import streamlit as st
import pydeck as pdk

# ── streamlit page setup ──────────────────────────────────────────────────────
st.set_page_config(page_title="WIO LMMA IOC Map with AI Assistant", layout="wide")
st.title("🌊 WIO LMMA IOC Map with AI Assistant")

# ── read Mapbox token from .env ───────────────────────────────────────────────
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path, override=True)

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

# Manual fallback if load_dotenv fails
if not MAPBOX_API_KEY:
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('MAPBOX_API_KEY='):
                    MAPBOX_API_KEY = line.strip().split('=', 1)[1]
                    break
    except Exception:
        pass

if not MAPBOX_API_KEY:
    st.error("❌ MAPBOX_API_KEY is missing. Add it to your .env file and restart Streamlit.")
    st.stop()

os.environ["MAPBOX_API_KEY"] = MAPBOX_API_KEY

# ── load shapefile ────────────────────────────────────────────────────────────
shapefile_path = "wio_lmma_ioc.shp"

if not os.path.exists(shapefile_path):
    st.error(f"❌ Could not find '{shapefile_path}'. Place all shapefile components in the same directory.")
    st.stop()

gdf = gpd.read_file(shapefile_path)

# ensure WGS84 lat/lon
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

geojson = gdf.__geo_interface__

minx, miny, maxx, maxy = gdf.total_bounds
mid_lat = (miny + maxy) / 2
mid_lon = (minx + maxx) / 2

# ── create 2-column layout ────────────────────────────────────────────────────
col1, col2 = st.columns([6, 4])  # 60% map, 40% chat

# ── LEFT COLUMN: Map ──────────────────────────────────────────────────────────
with col1:
    st.subheader("🗺️ Interactive Map")
    
    # Build Deck.gl map
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
    
    st.pydeck_chart(deck, use_container_width=True)
    
    # Attribute preview
    with st.expander("📊 View Data Attributes"):
        st.dataframe(gdf.drop(columns="geometry").head(10))

# ── RIGHT COLUMN: Chat ────────────────────────────────────────────────────────
with col2:
    st.subheader("💬 AI Chat Assistant")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"� Hello! I'm your AI assistant. I can help you understand the LMMA data.\n\n📊 Currently loaded: **{len(gdf)} LMMA features**\n\nAsk me anything!"
        })
    
    # Display chat messages in a container
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input at the bottom
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Generate echo response (temporary - will be replaced with Gemini in Step 3)
        response = f"🔄 **Echo Bot Response:**\n\nYou said: _{prompt}_\n\n✨ This is a test response. Real AI coming in Step 3!"
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)
        
        # Force rerun to update the display
        st.rerun()
    
    # Add helpful info below chat
    st.divider()
    st.caption("💡 **Tips:**")
    st.caption("• Try asking about the map data")
    st.caption("• Real AI responses coming in Step 3")
    st.caption(f"• {len(st.session_state.messages)} messages in history")

# ── Debug Info (collapsible) ──────────────────────────────────────────────────
with st.expander("🔧 Debug Information"):
    st.write("**Working Directory:**", os.getcwd())
    st.write("**Shapefile CRS:**", gdf.crs)
    st.write("**Map Center:**", f"Lat: {mid_lat:.4f}, Lon: {mid_lon:.4f}")
    st.write("**Features Count:**", len(gdf))
    st.write("**API Key Status:**", "✅ Loaded" if MAPBOX_API_KEY else "❌ Missing")