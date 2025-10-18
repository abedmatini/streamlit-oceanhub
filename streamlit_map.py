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
st.title("🌊 Where is my MPA?")

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
    # Simplify only valid geometries for performance
    gdf.loc[gdf.geometry.is_valid, 'geometry'] = gdf.loc[gdf.geometry.is_valid, 'geometry'].simplify(
        tolerance=0.002, preserve_topology=True
    )
    return gdf

@st.cache_data(show_spinner="🔄 Loading MPA data...")
def load_mpa_data():
    """Load and preprocess MPA shapefile"""
    gdf = gpd.read_file("wio_mpa_ioc.shp")
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    # Simplify only valid geometries for performance
    gdf.loc[gdf.geometry.is_valid, 'geometry'] = gdf.loc[gdf.geometry.is_valid, 'geometry'].simplify(
        tolerance=0.002, preserve_topology=True
    )
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

# ─────────────────────────────────────────────────────────────────────────────
# 🚀 PERFORMANCE OPTIMIZATION: Cache GeoJSON conversion
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def convert_to_geojson(_gdf, cache_key):
    """Convert GeoDataFrame to GeoJSON format (cached for performance)
    
    Note: _gdf has underscore prefix to tell Streamlit not to hash it
    cache_key is used to differentiate between different GeoDataFrames
    """
    return _gdf.__geo_interface__

@st.cache_data
def calculate_map_center(_gdf_lmma, _gdf_mpa):
    """Calculate map center from combined bounds (cached for performance)
    
    Note: _gdf parameters have underscore prefix (not hashable)
    Returns: (mid_lat, mid_lon, minx, miny, maxx, maxy)
    """
    all_bounds = gpd.GeoDataFrame(pd.concat([_gdf_lmma, _gdf_mpa], ignore_index=True))
    minx, miny, maxx, maxy = all_bounds.total_bounds
    mid_lat = (miny + maxy) / 2
    mid_lon = (minx + maxx) / 2
    return mid_lat, mid_lon, minx, miny, maxx, maxy

# Load data with caching (only loads once, then reuses)
with st.spinner("🌊 Loading marine conservation data..."):
    gdf_lmma = load_lmma_data()
    gdf_mpa = load_mpa_data()

# Convert to GeoJSON (cached - only converts once per dataset!)
geojson_lmma = convert_to_geojson(gdf_lmma, "lmma")
geojson_mpa = convert_to_geojson(gdf_mpa, "mpa")

# Calculate map center from combined bounds (cached!)
mid_lat, mid_lon, minx, miny, maxx, maxy = calculate_map_center(gdf_lmma, gdf_mpa)

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

# ── SIDEBAR: Location Checker ─────────────────────────────────────────────────
st.sidebar.header("📍 Check Your Location")
st.sidebar.markdown("Enter coordinates to check if you're in a protected zone")

# Initialize session state for coordinates
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = -15.5
if 'user_lon' not in st.session_state:
    st.session_state.user_lon = 49.5

# Example location buttons
st.sidebar.markdown("**🎯 Quick Test Locations:**")
col_btn1, col_btn2, col_btn3 = st.sidebar.columns(3)

if col_btn1.button("🏝️ Madagascar", help="Test LMMA location"):
    st.session_state.user_lat = -15.5
    st.session_state.user_lon = 49.5
    
if col_btn2.button("🏖️ Seychelles", help="Test MPA location"):
    st.session_state.user_lat = -4.6
    st.session_state.user_lon = 55.5
    
if col_btn3.button("🌊 Ocean", help="Test open ocean"):
    st.session_state.user_lat = -10.0
    st.session_state.user_lon = 60.0

st.sidebar.markdown("**Or enter manually:**")

# Input fields for coordinates
user_lat = st.sidebar.number_input(
    "Latitude",
    min_value=-90.0,
    max_value=90.0,
    value=st.session_state.user_lat,
    step=0.1,
    format="%.4f",
    help="Enter latitude between -90 and 90",
    key="lat_input"
)

user_lon = st.sidebar.number_input(
    "Longitude",
    min_value=-180.0,
    max_value=180.0,
    value=st.session_state.user_lon,
    step=0.1,
    format="%.4f",
    help="Enter longitude between -180 and 180",
    key="lon_input"
)

# Update session state
st.session_state.user_lat = user_lat
st.session_state.user_lon = user_lon

# Check location button
check_button = st.sidebar.button("🔍 Check Location", use_container_width=True, type="primary")

# STEP 2: Spatial logic function
def check_location(lat, lon, gdf_lmma, gdf_mpa):
    """
    Check if coordinates fall within any LMMA or MPA
    
    Args:
        lat: Latitude
        lon: Longitude
        gdf_lmma: GeoDataFrame of LMMAs
        gdf_mpa: GeoDataFrame of MPAs
    
    Returns:
        dict with 'type', 'name', 'country', 'data' or None
    """
    from shapely.geometry import Point
    
    point = Point(lon, lat)  # Shapely uses (lon, lat) order
    
    # Check LMMAs first
    lmma_match = gdf_lmma[gdf_lmma.geometry.contains(point)]
    if not lmma_match.empty:
        row = lmma_match.iloc[0]
        return {
            'type': 'LMMA',
            'name': row['Name of LM'],
            'country': row['Country'],
            'year': row.get('Year Start', 'N/A'),
            'area': row.get('Areas, Siz', 'N/A'),
            'data': row
        }
    
    # Check MPAs
    mpa_match = gdf_mpa[gdf_mpa.geometry.contains(point)]
    if not mpa_match.empty:
        row = mpa_match.iloc[0]
        return {
            'type': 'MPA',
            'name': row['NAME'],
            'country': row['Country'],
            'year': row.get('Year_estab', 'N/A'),
            'category': row.get('IUCN_Categ', 'N/A'),
            'data': row
        }
    
    return None

# STEP 3: Display results
if check_button:
    with st.spinner("🔍 Checking location..."):
        result = check_location(user_lat, user_lon, gdf_lmma, gdf_mpa)
        
        if result:
            st.sidebar.success("✅ Location Found!")
            st.sidebar.markdown(f"""
            **📍 You are in:**  
            **{result['name']}**
            
            🏷️ **Type:** {result['type']} {'(Locally Managed Marine Area)' if result['type'] == 'LMMA' else '(Marine Protected Area)'}  
            🌍 **Country:** {result['country']}  
            📅 **Established:** {result.get('year', 'N/A')}  
            📏 **Details:** {result.get('area', result.get('category', 'N/A'))}  
            📊 **Coordinates:** {user_lat:.4f}, {user_lon:.4f}
            """)
            
            # Store in session state for AI context AND pin display
            st.session_state.last_checked_location = result
            st.session_state.show_pin = True  # Flag to show pin
            
        else:
            st.sidebar.warning("❌ Not in any protected zone")
            st.sidebar.markdown(f"""
            The coordinates **{user_lat:.4f}, {user_lon:.4f}** are not within any registered LMMA or MPA in our database.
            
            This could be:
            - Open ocean
            - Unprotected coastal area
            - Outside the Western Indian Ocean region
            """)
            st.session_state.last_checked_location = None
            st.session_state.show_pin = True  # Still show pin for not-found locations

st.sidebar.divider()

# ── create 2-column layout ────────────────────────────────────────────────────
col1, col2 = st.columns([6, 4])  # 60% map, 40% chat

# ── LEFT COLUMN: Map ──────────────────────────────────────────────────────────
with col1:
    st.subheader("🗺️ Interactive Map")
    
    # Add legend
    legend_text = """
    **Legend:**  
    🔵 **Blue** = LMMAs (Locally Managed Marine Areas) - {0} features  
    🟢 **Green** = MPAs (Marine Protected Areas) - {1} features
    """.format(total_lmma, total_mpa)
    
    # Add pin to legend if location was checked
    if 'show_pin' in st.session_state and st.session_state.show_pin:
        legend_text += "\n🔴 **Red Pin** = Your checked location ({:.4f}, {:.4f})".format(
            st.session_state.user_lat, st.session_state.user_lon
        )
    
    st.markdown(legend_text)
    
    # STEP 4: Prepare map layers
    map_layers = [
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
    ]
    
    # STEP 4: Add red pin to map when location is checked
    if 'show_pin' in st.session_state and st.session_state.show_pin:
        if 'user_lat' in st.session_state and 'user_lon' in st.session_state:
            pin_lat = st.session_state.user_lat
            pin_lon = st.session_state.user_lon
            
            pin_layer = pdk.Layer(
                "ScatterplotLayer",
                data=[{
                    "position": [pin_lon, pin_lat],
                    "name": "📍 Your Checked Location"
                }],
                get_position="position",
                get_fill_color=[255, 0, 0, 220],  # Bright Red
                get_line_color=[150, 0, 0],  # Dark red border
                get_radius=10000,  # 10km radius for better visibility
                radius_min_pixels=10,  # Minimum 10 pixels
                radius_max_pixels=30,  # Maximum 30 pixels
                line_width_min_pixels=2,
                pickable=True,
                auto_highlight=True,
            )
            map_layers.append(pin_layer)
    
    # Build Deck.gl map with all layers
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_lon,
            zoom=4,
            pitch=0,
        ),
        layers=map_layers,
        tooltip={"text": "LMMA: {Name of LM}\nMPA: {NAME}\nCountry: {Country}\nLocation: {name}"},
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
            "content": f"👋 Hello! I'm your AI assistant powered by Google Gemini, and I'm aware of the marine conservation data you're viewing.\n\n📊 **Current Data:**\n- **{total_lmma} LMMAs** (Locally Managed Marine Areas)\n- **{total_mpa} MPAs** (Marine Protected Areas)\n- **{len(all_countries)} countries**: {', '.join(all_countries[:4])}{'...' if len(all_countries) > 4 else ''}\n- Covering the **Western Indian Ocean** region\n\n� **New Feature:** Check if any coordinates are in a protected zone using the sidebar!\n\n�💡 **Try asking me:**\n- \"What's the difference between LMMA and MPA?\"\n- \"How many MPAs are in Seychelles?\"\n- \"Tell me about the location I just checked\"\n- \"Why are both types important?\""
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
                    
                    # STEP 5: Add location checker context to AI
                    location_context = ""
                    if 'last_checked_location' in st.session_state and st.session_state.last_checked_location:
                        loc = st.session_state.last_checked_location
                        location_context = f"""

RECENT LOCATION CHECK:
The user just checked coordinates ({st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f}) and found:
- Location: {loc['name']}
- Type: {loc['type']} ({'Locally Managed Marine Area' if loc['type'] == 'LMMA' else 'Marine Protected Area'})
- Country: {loc['country']}
- Established: {loc.get('year', 'N/A')}
- Additional Info: {loc.get('area', loc.get('category', 'N/A'))}

The user can see a red pin on the map at this location. Be aware of this context when answering questions.
"""
                    elif 'last_checked_location' in st.session_state and st.session_state.last_checked_location is None:
                        location_context = f"""

RECENT LOCATION CHECK:
The user checked coordinates ({st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f}) but it was NOT in any protected zone (LMMA or MPA). This is likely open ocean or an unprotected area.
"""
                    
                    # Combine all context with user prompt
                    full_prompt = f"{data_context}{location_context}\n\nUser Question: {prompt}"
                    
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