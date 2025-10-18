# streamlit_map.py
import os
import pandas as pd

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

# ── load shapefiles ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="🔄 Loading LMMA data...")
def load_lmma_data():
    """Load and preprocess LMMA shapefile"""
    gdf = gpd.read_file("wio_lmma_ioc.shp")
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf

@st.cache_data(show_spinner="🔄 Loading MPA data...")
def load_mpa_data():
    """Load and preprocess MPA shapefile"""
    gdf = gpd.read_file("wio_mpa_ioc.shp")
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf

# Check if files exist
lmma_shapefile = "wio_lmma_ioc.shp"
mpa_shapefile = "wio_mpa_ioc.shp"

if not os.path.exists(lmma_shapefile):
    st.error(f"❌ Could not find '{lmma_shapefile}'. Place all shapefile components in the same directory.")
    st.stop()

if not os.path.exists(mpa_shapefile):
    st.error(f"❌ Could not find '{mpa_shapefile}'. Place all shapefile components in the same directory.")
    st.stop()

# Load data with caching (only loads once, then reuses)
with st.spinner("🌊 Loading marine conservation data..."):
    gdf_lmma = load_lmma_data()
    gdf_mpa = load_mpa_data()

# Convert to GeoJSON
geojson_lmma = gdf_lmma.__geo_interface__
geojson_mpa = gdf_mpa.__geo_interface__

# Calculate map center from combined bounds
all_bounds = gpd.GeoDataFrame(pd.concat([gdf_lmma, gdf_mpa], ignore_index=True))
minx, miny, maxx, maxy = all_bounds.total_bounds
mid_lat = (miny + maxy) / 2
mid_lon = (minx + maxx) / 2

# ── Prepare context about the data for AI ─────────────────────────────────────
# Get summary statistics for LMMAs
total_lmma = len(gdf_lmma)
lmma_countries = gdf_lmma['Country'].unique().tolist() if 'Country' in gdf_lmma.columns else []
lmma_country_counts = gdf_lmma['Country'].value_counts().to_dict() if 'Country' in gdf_lmma.columns else {}

# Get summary statistics for MPAs
total_mpa = len(gdf_mpa)
mpa_countries = gdf_mpa['Country'].unique().tolist() if 'Country' in gdf_mpa.columns else []
mpa_country_counts = gdf_mpa['Country'].value_counts().to_dict() if 'Country' in gdf_mpa.columns else {}

# Combined statistics
total_features = total_lmma + total_mpa
all_countries = sorted(set(lmma_countries + mpa_countries))

# Create context string for AI
data_context = f"""
You are an AI assistant helping users understand marine conservation data from the Western Indian Ocean region.

CURRENT DATA LOADED:
- LMMA features (Locally Managed Marine Areas): {total_lmma} - community-based management
- MPA features (Marine Protected Areas): {total_mpa} - government-designated protected areas
- Total features: {total_features}
- Countries represented: {', '.join(all_countries)}
- Data coverage: Western Indian Ocean (WIO) region
- Coordinate bounds: Lat({miny:.2f} to {maxy:.2f}), Lon({minx:.2f} to {maxx:.2f})

LMMA COUNTRY BREAKDOWN:
{chr(10).join([f"- {country}: {count} LMMAs" for country, count in lmma_country_counts.items()])}

MPA COUNTRY BREAKDOWN:
{chr(10).join([f"- {country}: {count} MPAs" for country, count in mpa_country_counts.items()])}

ABOUT LMMAs (Locally Managed Marine Areas):
LMMAs are coastal zones where local communities play a key role in managing marine resources. They are characterized by:
- Community-based resource governance
- Local participation in decision-making
- Sustainable fisheries management
- Traditional and customary practices
- Bottom-up management approach

ABOUT MPAs (Marine Protected Areas):
MPAs are government-designated protected areas focused on conservation. They are characterized by:
- Legal protection status
- Government management and enforcement
- Biodiversity conservation goals
- Often stricter regulations
- Top-down management approach

KEY DIFFERENCES:
- LMMAs: Community-led, local governance, sustainable use focus
- MPAs: Government-led, legal protection, conservation focus
- Both are important for marine ecosystem protection

When answering questions:
- Be specific about LMMA vs MPA when users ask about types
- Explain the differences clearly when asked
- Reference actual data numbers for both types
- Be helpful and educational about marine conservation
- Clarify which management approach (LMMA or MPA) when relevant
"""

# ── create 2-column layout ────────────────────────────────────────────────────
col1, col2 = st.columns([6, 4])  # 60% map, 40% chat

# ── LEFT COLUMN: Map ──────────────────────────────────────────────────────────
with col1:
    st.subheader("🗺️ Interactive Map")
    
    # Add legend
    st.markdown("""
    **Legend:**  
    🔵 **Blue** = LMMAs (Locally Managed Marine Areas) - {0} features  
    🟢 **Green** = MPAs (Marine Protected Areas) - {1} features
    """.format(total_lmma, total_mpa))
    
    # Build Deck.gl map with two layers
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_lon,
            zoom=5,
            pitch=0,
        ),
        layers=[
            # LMMA Layer (Blue)
            pdk.Layer(
                "GeoJsonLayer",
                data=geojson_lmma,
                stroked=True,
                filled=True,
                opacity=0.6,
                get_fill_color=[82, 170, 225, 120],  # Ocean Blue
                get_line_color=[12, 60, 90],
                line_width_min_pixels=1,
                pickable=True,
            ),
            # MPA Layer (Green)
            pdk.Layer(
                "GeoJsonLayer",
                data=geojson_mpa,
                stroked=True,
                filled=True,
                opacity=0.6,
                get_fill_color=[46, 204, 113, 120],  # Emerald Green
                get_line_color=[22, 160, 133],
                line_width_min_pixels=1,
                pickable=True,
            ),
        ],
        tooltip={"text": "LMMA: {Name of LM}\nMPA: {NAME}\nCountry: {Country}"},
    )
    
    st.pydeck_chart(deck, use_container_width=True)
    
    # Data preview tabs
    tab1, tab2 = st.tabs(["📊 LMMA Data", "📊 MPA Data"])
    
    with tab1:
        st.caption(f"Showing {min(10, len(gdf_lmma))} of {len(gdf_lmma)} LMMA features")
        st.dataframe(gdf_lmma.drop(columns="geometry").head(10), use_container_width=True)
    
    with tab2:
        st.caption(f"Showing {min(10, len(gdf_mpa))} of {len(gdf_mpa)} MPA features")
        st.dataframe(gdf_mpa.drop(columns="geometry").head(10), use_container_width=True)

# ── RIGHT COLUMN: Chat ────────────────────────────────────────────────────────
with col2:
    st.subheader("💬 AI Chat Assistant")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message with data info
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"👋 Hello! I'm your AI assistant powered by Google Gemini, and I'm aware of the marine conservation data you're viewing.\n\n📊 **Current Data:**\n- **{total_lmma} LMMAs** (Locally Managed Marine Areas)\n- **{total_mpa} MPAs** (Marine Protected Areas)\n- **{len(all_countries)} countries**: {', '.join(all_countries[:4])}{'...' if len(all_countries) > 4 else ''}\n- Covering the **Western Indian Ocean** region\n\n💡 **Try asking me:**\n- \"What's the difference between LMMA and MPA?\"\n- \"How many MPAs are in Seychelles?\"\n- \"Compare Madagascar's LMMAs and MPAs\"\n- \"Why are both types important?\""
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
        if st.button("📊 Compare data", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Compare LMMAs and MPAs in the data"})
            st.rerun()
        if st.button("🌊 LMMA vs MPA?", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What's the difference between LMMA and MPA?"})
            st.rerun()
    with col_b:
        if st.button("🇸🇨 Seychelles MPAs", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Tell me about Seychelles' MPAs"})
            st.rerun()
        if st.button("🐠 Conservation", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Why are both LMMAs and MPAs important?"})
            st.rerun()
    
    st.caption(f"📝 {len(st.session_state.messages)} messages in history")

# ── Debug Info (collapsible) ──────────────────────────────────────────────────
with st.expander("🔧 Debug Information"):
    st.write("**Working Directory:**", os.getcwd())
    st.write("**LMMA CRS:**", gdf_lmma.crs)
    st.write("**MPA CRS:**", gdf_mpa.crs)
    st.write("**Map Center:**", f"Lat: {mid_lat:.4f}, Lon: {mid_lon:.4f}")
    st.write("**LMMA Features:**", len(gdf_lmma))
    st.write("**MPA Features:**", len(gdf_mpa))
    st.write("**Total Features:**", total_features)
    st.write("**Mapbox API:**", "✅ Loaded" if MAPBOX_API_KEY else "❌ Missing")
    st.write("**Gemini API:**", "✅ Loaded" if GEMINI_API_KEY else "❌ Missing")
    st.write("**Gemini Model:**", "gemini-2.5-flash")