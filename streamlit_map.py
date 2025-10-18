# streamlit_map.py
import os

from dotenv import load_dotenv
import geopandas as gpd
import streamlit as st
import pydeck as pdk
import google.generativeai as genai

# ── streamlit page setup ──────────────────────────────────────────────────────
st.set_page_config(page_title="WIO LMMA IOC Map with AI Assistant", layout="wide")
st.title("🌊 WIO LMMA IOC Map with AI Assistant")

# ── read API keys from .env ───────────────────────────────────────────────────
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path, override=True)

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Manual fallback if load_dotenv fails
if not MAPBOX_API_KEY:
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('MAPBOX_API_KEY='):
                    MAPBOX_API_KEY = line.strip().split('=', 1)[1]
                if line.strip().startswith('GEMINI_API_KEY='):
                    GEMINI_API_KEY = line.strip().split('=', 1)[1]
    except Exception:
        pass

if not MAPBOX_API_KEY:
    st.error("❌ MAPBOX_API_KEY is missing. Add it to your .env file and restart Streamlit.")
    st.stop()

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY is missing. Add it to your .env file and restart Streamlit.")
    st.stop()

os.environ["MAPBOX_API_KEY"] = MAPBOX_API_KEY

# ── Initialize Gemini AI ──────────────────────────────────────────────────────
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini AI: {e}")
    st.stop()

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

# ── Prepare context about the data for AI ─────────────────────────────────────
# Get summary statistics
total_features = len(gdf)
countries = gdf['Country'].unique().tolist() if 'Country' in gdf.columns else []
country_counts = gdf['Country'].value_counts().to_dict() if 'Country' in gdf.columns else {}

# Get column names and sample data
columns_info = list(gdf.columns)
columns_info.remove('geometry') if 'geometry' in columns_info else None

# Create context string for AI
data_context = f"""
You are an AI assistant helping users understand LMMA (Locally Managed Marine Area) data from the Western Indian Ocean region.

CURRENT DATA LOADED:
- Total LMMA features: {total_features}
- Countries represented: {', '.join(countries)}
- Data coverage: Western Indian Ocean (WIO) region
- Coordinate bounds: Lat({miny:.2f} to {maxy:.2f}), Lon({minx:.2f} to {maxx:.2f})

COUNTRY BREAKDOWN:
{chr(10).join([f"- {country}: {count} LMMAs" for country, count in country_counts.items()])}

DATA ATTRIBUTES:
Available fields: {', '.join(columns_info)}

ABOUT LMMAs:
LMMAs (Locally Managed Marine Areas) are coastal zones where local communities play a key role in managing marine resources. They are important for:
- Sustainable fisheries management
- Marine biodiversity conservation
- Community-based resource governance
- Coastal ecosystem protection

When answering questions:
- Be specific about the data when users ask about numbers, countries, or locations
- Explain marine conservation concepts clearly
- Reference the actual data when relevant
- Be helpful and educational about ocean conservation
"""

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
        # Add welcome message with data info
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"👋 Hello! I'm your AI assistant powered by Google Gemini, and I'm aware of the LMMA data you're viewing.\n\n📊 **Current Data:**\n- **{total_features} LMMA features** loaded\n- **{len(countries)} countries**: {', '.join(countries[:3])}{'...' if len(countries) > 3 else ''}\n- Covering the **Western Indian Ocean** region\n\n💡 **Try asking me:**\n- \"How many LMMAs are in [country name]?\"\n- \"What countries have the most LMMAs?\"\n- \"Explain what an LMMA is\"\n- \"Why are LMMAs important?\""
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
        
        # Generate AI response with Gemini
        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                try:
                    # Show typing indicator
                    message_placeholder.markdown("💭 Thinking...")
                    
                    # Combine context with user prompt
                    full_prompt = f"{data_context}\n\nUser Question: {prompt}"
                    
                    # Generate response from Gemini
                    response = model.generate_content(full_prompt)
                    
                    # Extract text from response
                    if response and response.text:
                        ai_response = response.text
                    else:
                        ai_response = "I apologize, but I couldn't generate a response. Please try again."
                    
                    # Display the response
                    message_placeholder.markdown(ai_response)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}\n\nPlease check your API key or try again."
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Force rerun to update the display
        st.rerun()
    
    # Add helpful info below chat
    st.divider()
    
    # Example prompts
    st.caption("💡 **Example Questions:**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📊 Data stats", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What countries have the most LMMAs?"})
            st.rerun()
        if st.button("🌊 What is LMMA?", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What is an LMMA and why is it important?"})
            st.rerun()
    with col_b:
        if st.button("🗺️ Coverage area", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What geographic area does this data cover?"})
            st.rerun()
        if st.button("🐠 Conservation", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "How do LMMAs help marine conservation?"})
            st.rerun()
    
    st.caption(f"📝 {len(st.session_state.messages)} messages in history")

# ── Debug Info (collapsible) ──────────────────────────────────────────────────
with st.expander("🔧 Debug Information"):
    st.write("**Working Directory:**", os.getcwd())
    st.write("**Shapefile CRS:**", gdf.crs)
    st.write("**Map Center:**", f"Lat: {mid_lat:.4f}, Lon: {mid_lon:.4f}")
    st.write("**Features Count:**", len(gdf))
    st.write("**Mapbox API:**", "✅ Loaded" if MAPBOX_API_KEY else "❌ Missing")
    st.write("**Gemini API:**", "✅ Loaded" if GEMINI_API_KEY else "❌ Missing")
    st.write("**Gemini Model:**", "gemini-2.5-flash")