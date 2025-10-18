# pages/order_a_boat.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
from datetime import datetime, timedelta
import random
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = None
if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.warning(f"⚠️ Gemini API not available: {e}")


def generate_captain_response(
    captain_name, user_message, mpa_name, depth_zone, trip_date
):
    """Generate a realistic captain response using Gemini AI with system instructions"""
    if not gemini_client:
        # Fallback responses if Gemini is not available
        return "All good! Looking forward to showing you around the MPA! 🌊"

    try:
        # System instructions define the captain's role and behavior
        system_instruction = f"""You are {captain_name}, a friendly Malagasy boat captain working at {mpa_name}.

Your personality:
- Warm, enthusiastic, and genuinely excited about showing tourists the marine life
- You use casual, conversational language like "Ahoy!", "Fantastic!", or local Malagasy phrases
- You love your local waters and know them well
- Keep responses SHORT - just 1-2 sentences maximum
- Be natural and varied - don't use the same phrases repeatedly

Context for this conversation:
- The tourist booked a {depth_zone} trip on {trip_date}
- Location: {mpa_name}

IMPORTANT: Respond directly as the captain. Don't explain what you would say, just say it naturally."""

        # User's actual message
        user_prompt = user_message

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                types.Content(
                    role="user", parts=[types.Part.from_text(text=user_prompt)]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=1.2,  # Higher for more creativity and variation
                top_p=0.95,
                top_k=64,
                system_instruction=system_instruction,  # Use system instruction properly
            ),
        )

        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                if hasattr(candidate.content, "parts") and candidate.content.parts:
                    response_text = candidate.content.parts[0].text.strip()
                    # Remove any meta-commentary like "Response 1:", "Here's what I'd say:", etc.
                    if "Response" in response_text and ":" in response_text:
                        # Extract just the actual response after any meta text
                        lines = response_text.split("\n")
                        for line in lines:
                            if (
                                line.strip()
                                and not line.startswith("Response")
                                and ":" not in line[:20]
                            ):
                                return line.strip().strip('"')
                    return response_text

        return "All good! I'm so excited to have you visit our beautiful MPA! 🌊"

    except Exception as e:
        return f"All good! Can't wait to show you the amazing marine life at {mpa_name}! 🐠"


# Page configuration
st.set_page_config(
    page_title="Book a Boat - MPA Explorer",
    page_icon="🚤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .captain-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .captain-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .depth-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.1rem;
    }
    .shore-badge { background: #e3f2fd; color: #1976d2; }
    .snorkeling-badge { background: #e8f5e8; color: #388e3c; }
    .deep-badge { background: #fff3e0; color: #f57c00; }
    .stButton > button {
        background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,123,255,0.3);
    }
    .payment-split {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .chat-message {
        background: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-message {
        background: #007bff;
        color: white;
        margin-left: auto;
    }
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 0.5rem 1rem;
        background: #e3f2fd;
        border-radius: 15px;
        max-width: 100px;
        margin: 0.5rem 0;
    }
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background: #007bff;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.5;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "selected_mpa" not in st.session_state:
    st.session_state.selected_mpa = None
if "group_size" not in st.session_state:
    st.session_state.group_size = 1
if "depth_preference" not in st.session_state:
    st.session_state.depth_preference = None
if "filtered_captains" not in st.session_state:
    st.session_state.filtered_captains = []
if "selected_captain" not in st.session_state:
    st.session_state.selected_captain = None
if "booking_details" not in st.session_state:
    st.session_state.booking_details = {}
if "payment_processed" not in st.session_state:
    st.session_state.payment_processed = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "depth_choice" not in st.session_state:
    st.session_state.depth_choice = None
if "trip_date" not in st.session_state:
    st.session_state.trip_date = None
if "trip_time" not in st.session_state:
    st.session_state.trip_time = None
if "duration" not in st.session_state:
    st.session_state.duration = None

# Main header
st.markdown(
    """
<div class="main-header">
    <h1>🚤 Book a Boat - MPA Explorer</h1>
    <p style="font-size: 1.2rem; margin: 0;">Connect with accredited boat captains for marine adventures in Madagascar's protected areas</p>
</div>
""",
    unsafe_allow_html=True,
)


# Progress Bar - Don't auto-update step, let manual navigation control it
# Only validate that user can't skip ahead without prerequisites

# Define steps
steps = [
    {"name": "🏝️ Select MPA", "description": "Choose your destination"},
    {"name": "📋 Trip Details", "description": "Group size & depth preference"},
    {"name": "👨‍✈️ Choose Captain", "description": "Select your boat captain"},
    {"name": "📅 Booking Details", "description": "Date, time & duration"},
    {"name": "💳 Payment", "description": "Complete your booking"},
    {"name": "🎉 Confirmation", "description": "Chat with your captain"},
]

# Progress bar
progress = st.session_state.current_step / len(steps)
st.progress(progress)

# Step indicators
cols = st.columns(len(steps))
for i, step in enumerate(steps):
    with cols[i]:
        if i + 1 <= st.session_state.current_step:
            st.markdown(f"✅ **{step['name']}**")
            st.caption(step["description"])
        else:
            st.markdown(f"⏳ {step['name']}")
            st.caption(step["description"])

st.markdown("---")

# Sample MPA data (in a real app, this would come from the shapefile)
MADAGASCAR_MPAS = [
    {
        "name": "Nosy Be Marine Park",
        "type": "Marine Protected Area",
        "nearest_npa": "Nosy Be",
        "description": "Coral reefs and diverse marine life around Nosy Be island",
        "depth_zones": ["shore", "snorkeling", "deep"],
        "coordinates": [-13.4, 48.3],
        "area": "32,000 hectares",
    },
    {
        "name": "Toliara Reef System",
        "type": "Locally Managed Marine Area",
        "nearest_npa": "Toliara",
        "description": "Community-managed coral reef system with traditional fishing zones",
        "depth_zones": ["shore", "snorkeling"],
        "coordinates": [-23.35, 43.67],
        "area": "15,000 hectares",
    },
    {
        "name": "Sainte Marie Marine Reserve",
        "type": "Marine Protected Area",
        "nearest_npa": "Sainte Marie",
        "description": "Whale watching sanctuary and pristine coral reefs",
        "depth_zones": ["shore", "snorkeling", "deep"],
        "coordinates": [-16.83, 49.83],
        "area": "25,000 hectares",
    },
    {
        "name": "Fort Dauphin Bay",
        "type": "Locally Managed Marine Area",
        "nearest_npa": "Fort Dauphin",
        "description": "Traditional fishing grounds with community conservation efforts",
        "depth_zones": ["shore", "snorkeling"],
        "coordinates": [-25.03, 46.98],
        "area": "8,500 hectares",
    },
]

# Sample captain data
CAPTAINS_DATA = [
    {
        "name": "Captain Jean-Baptiste",
        "photo": "👨‍✈️",
        "vessel_name": "Ocean Explorer",
        "vessel_capacity": 8,
        "depth_zones": ["shore", "snorkeling", "deep"],
        "vessel_type": "Motorboat",
        "equipment": ["Snorkel gear", "Life jackets", "GPS", "Radio", "First aid"],
        "price_per_person": {"shore": 20, "snorkeling": 35, "deep": 50},
        "certifications": ["Dive master", "First aid certified"],
        "rating": 4.8,
        "mpa": "Nosy Be Marine Park",
    },
    {
        "name": "Captain Marie",
        "photo": "👩‍✈️",
        "vessel_name": "Coral Dream",
        "vessel_capacity": 6,
        "depth_zones": ["shore", "snorkeling"],
        "vessel_type": "Motorboat",
        "equipment": ["Snorkel gear", "Life jackets", "Shade covers"],
        "price_per_person": {"shore": 18, "snorkeling": 30, "deep": None},
        "certifications": ["First aid certified"],
        "rating": 4.6,
        "mpa": "Toliara Reef System",
    },
    {
        "name": "Captain Pierre",
        "photo": "👨‍✈️",
        "vessel_name": "Whale Watcher",
        "vessel_capacity": 12,
        "depth_zones": ["shore", "snorkeling", "deep"],
        "vessel_type": "Large Motorboat",
        "equipment": [
            "Snorkel gear",
            "Life jackets",
            "GPS",
            "Radio",
            "Dive equipment",
            "Emergency equipment",
        ],
        "price_per_person": {"shore": 25, "snorkeling": 40, "deep": 60},
        "certifications": ["Dive master", "Emergency response", "Whale watching guide"],
        "rating": 4.9,
        "mpa": "Sainte Marie Marine Reserve",
    },
    {
        "name": "Captain Fatima",
        "photo": "👩‍✈️",
        "vessel_name": "Traditional Pirogue",
        "vessel_capacity": 4,
        "depth_zones": ["shore"],
        "vessel_type": "Traditional Pirogue",
        "equipment": ["Life jackets", "Shade covers", "Traditional fishing gear"],
        "price_per_person": {"shore": 15, "snorkeling": None, "deep": None},
        "certifications": ["Traditional fishing guide"],
        "rating": 4.7,
        "mpa": "Fort Dauphin Bay",
    },
]

# Step 1: MPA Selection Section
if st.session_state.current_step == 1:
    st.markdown(
        """
<div class="section-header">
    <h2>🏝️ Select Your Marine Protected Area</h2>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        mpa_options = {f"{mpa['name']} ({mpa['type']})": mpa for mpa in MADAGASCAR_MPAS}
        selected_mpa_key = st.selectbox(
            "Choose your MPA destination:",
            options=list(mpa_options.keys()),
            help="Select the Marine Protected Area where you want to book your boat trip",
        )

        if selected_mpa_key:
            st.session_state.selected_mpa = mpa_options[selected_mpa_key]

            # Display MPA details
            mpa = st.session_state.selected_mpa
            st.markdown(f"**📍 {mpa['name']}**")
            st.markdown(f"**Type:** {mpa['type']}")
            st.markdown(f"**Nearest Town:** {mpa['nearest_npa']}")
            st.markdown(f"**Area:** {mpa['area']}")
            st.markdown(f"**Description:** {mpa['description']}")

            # Show available depth zones
            depth_icons = {"shore": "🏖️", "snorkeling": "🤿", "deep": "🌊"}
            available_zones = [
                f"{depth_icons[zone]} {zone.title()}" for zone in mpa["depth_zones"]
            ]
            st.markdown(f"**Available Activities:** {', '.join(available_zones)}")

    with col2:
        if st.session_state.selected_mpa:
            # Simple map visualization
            mpa = st.session_state.selected_mpa
            lat, lon = mpa["coordinates"]

            # Create a simple map with the MPA location
            view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=10)

            # Add a marker for the MPA
            marker_layer = pdk.Layer(
                "ScatterplotLayer",
                data=[{"coordinates": [lon, lat]}],
                get_position="coordinates",
                get_color="[255, 0, 0, 200]",
                get_radius=1000,
                pickable=True,
            )

            st.pydeck_chart(
                pdk.Deck(
                    layers=[marker_layer],
                    initial_view_state=view_state,
                    map_style="mapbox://styles/mapbox/light-v9",
                )
            )

    # Navigation button for Step 1
    if st.session_state.selected_mpa:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(
                "➡️ Continue to Trip Details",
                key="next_step1",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.current_step = 2
                st.rerun()

# Step 2: Trip Requirements Section
elif st.session_state.current_step == 2:
    # Validate that user has selected an MPA
    if not st.session_state.selected_mpa:
        st.error("❌ Please select an MPA first.")
        st.session_state.current_step = 1
        st.rerun()

    st.markdown(
        """
<div class="section-header">
    <h2>📋 Trip Requirements</h2>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**👥 Group Size**")
        group_size = st.number_input(
            "Number of people in your group:",
            min_value=1,
            max_value=12,
            value=st.session_state.group_size,
            help="Maximum group size varies by captain and vessel type",
        )
        st.session_state.group_size = group_size

        if group_size > 8:
            st.warning(
                "⚠️ Groups larger than 8 people may have limited captain options for deep water trips"
            )

    with col2:
        st.markdown("**🌊 Water Depth Preference**")
        depth_options = {
            "🏖️ Shore": {
                "value": "shore",
                "description": "Shallow water, beach activities, wadeable depths (0-2m)",
                "activities": "Beach activities, shallow water exploration",
                "wildlife": "Small fish, crabs, shallow coral",
                "swimming": "Basic swimming skills",
            },
            "🤿 Snorkeling": {
                "value": "snorkeling",
                "description": "Moderate depth, reef exploration (2-10m)",
                "activities": "Snorkeling, reef exploration",
                "wildlife": "Colorful fish, coral reefs, sea turtles",
                "swimming": "Good swimming skills recommended",
            },
            "🌊 Deep Water": {
                "value": "deep",
                "description": "Offshore, diving, pelagic wildlife (10m+)",
                "activities": "Diving, whale watching, pelagic fishing",
                "wildlife": "Large fish, whales, dolphins, sharks",
                "swimming": "Strong swimming skills required",
            },
        }

        depth_choice = st.radio(
            "Choose your preferred water depth:",
            options=list(depth_options.keys()),
            help="Select based on your group's swimming ability and interests",
        )

        st.session_state.depth_preference = depth_options[depth_choice]["value"]
        st.session_state.depth_choice = depth_choice

        # Show details for selected depth
        selected_depth_info = depth_options[depth_choice]
        st.markdown(f"**Activities:** {selected_depth_info['activities']}")
        st.markdown(f"**Wildlife:** {selected_depth_info['wildlife']}")
        st.markdown(f"**Swimming:** {selected_depth_info['swimming']}")

    # Navigation buttons for Step 2
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(
            "⬅️ Back to MPA Selection", key="back_step2", use_container_width=True
        ):
            st.session_state.current_step = 1
            st.rerun()
    with col3:
        if st.session_state.depth_preference:
            if st.button(
                "➡️ Find Captains",
                key="next_step2",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.current_step = 3
                st.rerun()

# Step 3: Captain Matching Section
elif st.session_state.current_step == 3:
    # Validate prerequisites
    if not st.session_state.selected_mpa:
        st.error("❌ Please select an MPA first.")
        st.session_state.current_step = 1
        st.rerun()
    elif not st.session_state.depth_preference:
        st.error("❌ Please select your depth preference first.")
        st.session_state.current_step = 2
        st.rerun()

    st.markdown(
        """
<div class="section-header">
            <h2>👨‍✈️ Available Captains</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter captains based on requirements
    available_captains = []
    for captain in CAPTAINS_DATA:
        # Check if captain operates in selected MPA
        if captain["mpa"] == st.session_state.selected_mpa["name"]:
            # Check if captain can handle group size
            if captain["vessel_capacity"] >= st.session_state.group_size:
                # Check if captain offers selected depth zone
                if st.session_state.depth_preference in captain["depth_zones"]:
                    available_captains.append(captain)

    st.session_state.filtered_captains = available_captains

    if available_captains:
        st.success(
            f"✅ Found {len(available_captains)} captain(s) for {st.session_state.group_size} people going to {st.session_state.depth_choice}"
        )

        # Display captain cards
        for i, captain in enumerate(available_captains):
            with st.container():
                st.markdown(f'<div class="captain-card">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    st.markdown(f"### {captain['photo']}")
                    st.markdown(f"**{captain['name']}**")
                    st.markdown(f"⭐ {captain['rating']}/5")

                with col2:
                    st.markdown(f"**Vessel:** {captain['vessel_name']}")
                    st.markdown(f"**Type:** {captain['vessel_type']}")
                    st.markdown(f"**Capacity:** {captain['vessel_capacity']} people")

                    # Show depth certifications
                    depth_badges = []
                    for zone in captain["depth_zones"]:
                        if zone == "shore":
                            depth_badges.append(
                                '<span class="depth-badge shore-badge">🏖️ Shore ✓</span>'
                            )
                        elif zone == "snorkeling":
                            depth_badges.append(
                                '<span class="depth-badge snorkeling-badge">🤿 Snorkeling ✓</span>'
                            )
                        elif zone == "deep":
                            depth_badges.append(
                                '<span class="depth-badge deep-badge">🌊 Deep Water ✓</span>'
                            )

                    st.markdown(
                        f"**Certifications:** {' '.join(depth_badges)}",
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"**Equipment:** {', '.join(captain['equipment'])}")

                with col3:
                    price = captain["price_per_person"][
                        st.session_state.depth_preference
                    ]
                    st.markdown(f"**Price:** ${price}/person")
                    st.markdown(f"**Total:** ${price * st.session_state.group_size}")

                    if st.button(f"Select Captain", key=f"captain_{i}"):
                        st.session_state.selected_captain = captain
                        st.success(f"✅ Selected {captain['name']}!")

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(
            f"❌ No captains available for {st.session_state.group_size} people wanting {st.session_state.depth_choice} access in {st.session_state.selected_mpa['name']}"
        )

    # Navigation buttons for Step 3
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(
            "⬅️ Back to Trip Details", key="back_step3", use_container_width=True
        ):
            st.session_state.current_step = 2
            st.rerun()
    with col3:
        if st.session_state.selected_captain:
            if st.button(
                "➡️ Continue to Booking",
                key="next_step3",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.current_step = 4
                st.rerun()

# Step 4: Booking Details Section
elif st.session_state.current_step == 4:
    # Validate prerequisites
    if not st.session_state.selected_captain:
        st.error("❌ Please select a captain first.")
        st.session_state.current_step = 3
        st.rerun()

    st.markdown(
        """
<div class="section-header">
            <h2>📅 Booking Details</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Date picker
        min_date = datetime.now().date()
        max_date = min_date + timedelta(days=30)
        trip_date = st.date_input(
            "Select trip date:",
            min_value=min_date,
            max_value=max_date,
            value=min_date + timedelta(days=1),
        )
        st.session_state.trip_date = trip_date

    with col2:
        # Time selector
        trip_time = st.time_input(
            "Select departure time:", value=datetime.strptime("09:00", "%H:%M").time()
        )
        st.session_state.trip_time = trip_time

    with col3:
        # Duration selector based on depth preference
        duration_options = {
            "shore": [2, 3, 4],
            "snorkeling": [3, 4, 6],
            "deep": [4, 6, 8],
        }

        duration = st.selectbox(
            "Trip duration (hours):",
            options=duration_options[st.session_state.depth_preference],
            help="Duration varies by depth zone - deeper trips require more time",
        )
        st.session_state.duration = duration

    # Special requests
    special_requests = st.text_area(
        "Special requests or notes:",
        placeholder="Any dietary restrictions, equipment needs, or special considerations...",
        height=100,
    )

    # Calculate total price
    captain = st.session_state.selected_captain
    base_price = captain["price_per_person"][st.session_state.depth_preference]
    duration_multiplier = {2: 1.0, 3: 1.2, 4: 1.4, 6: 1.6, 8: 1.8}.get(
        st.session_state.duration, 1.0
    )
    total_price = base_price * st.session_state.group_size * duration_multiplier

    st.markdown(
        f"**💰 Total Price:** ${total_price:.2f} ({st.session_state.group_size} people × ${base_price} × {duration_multiplier:.1f}x duration)"
    )

    # Navigation buttons for Step 4
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Captains", key="back_step4", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    with col3:
        if st.button(
            "💳 Proceed to Payment",
            key="next_step4",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.current_step = 5
            st.rerun()

# Step 5: Mock Payment Section
elif st.session_state.current_step == 5:
    # Validate prerequisites
    if not st.session_state.selected_captain:
        st.error("❌ Please select a captain first.")
        st.session_state.current_step = 3
        st.rerun()

    st.markdown(
        """
<div class="section-header">
            <h2>💳 Payment (Demo)</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    captain = st.session_state.selected_captain
    base_price = captain["price_per_person"][st.session_state.depth_preference]
    duration_multiplier = {2: 1.0, 3: 1.2, 4: 1.4, 6: 1.6, 8: 1.8}.get(
        st.session_state.duration, 1.0
    )
    total_price = base_price * st.session_state.group_size * duration_multiplier

    # Payment breakdown using Streamlit components
    st.subheader("💰 Payment Breakdown")

    st.write(f"**Group Size:** {st.session_state.group_size} people")
    st.write(f"**Depth Zone:** {st.session_state.depth_choice}")
    st.write(f"**Total Amount:** ${total_price:.2f}")

    st.markdown("---")

    # Payment split visualization
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👨‍✈️ Captain Payment")
        st.markdown(
            f"<h2 style='text-align: center; color: #007bff;'>${total_price * 0.5:.2f}</h2>",
            unsafe_allow_html=True,
        )
        st.caption(f"50% to {captain['name']}")

    with col2:
        st.markdown("### 🌊 Conservation Tip")
        st.markdown(
            f"<h2 style='text-align: center; color: #28a745;'>${total_price * 0.5:.2f}</h2>",
            unsafe_allow_html=True,
        )
        st.caption("50% to MPA conservation")

    st.markdown("---")

    # Mock payment form
    st.markdown("**🔒 Payment Information (Demo Only)**")
    st.caption("This is a demo - no real payment will be processed")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.text_input(
            "Card Number:",
            value="4532 1234 5678 9010",
            disabled=True,
            key="card_number",
        )
        st.text_input("Expiry Date:", value="12/25", disabled=True, key="expiry_date")

    with col2:
        st.text_input("CVV:", value="123", disabled=True, key="cvv")
        st.text_input(
            "Cardholder Name:", value="John Doe", disabled=True, key="cardholder_name"
        )

    if st.button("🚀 Process Payment", key="process_payment", type="primary"):
        with st.spinner("Processing payment..."):
            import time

            time.sleep(2)  # Simulate processing time

        st.session_state.payment_processed = True
        st.success("✅ Payment processed successfully!")
        st.balloons()

        # Auto-advance to confirmation step
        st.session_state.current_step = 6
        st.rerun()

    # Navigation buttons for Step 5
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Back to Booking", key="back_step5", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()

# Step 6: Confirmation & Chat Section
elif st.session_state.current_step == 6:
    # Validate prerequisites
    if not st.session_state.payment_processed:
        st.error("❌ Please complete payment first.")
        st.session_state.current_step = 5
        st.rerun()

    st.markdown(
        """
<div class="section-header">
            <h2>🎉 Booking Confirmed!</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    captain = st.session_state.selected_captain
    mpa = st.session_state.selected_mpa

    # Booking summary
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"**✅ Captain:** {captain['name']}")
        st.markdown(f"**🚤 Vessel:** {captain['vessel_name']}")
        st.markdown(f"**👥 Group Size:** {st.session_state.group_size} people")
        st.markdown(f"**🌊 Depth Zone:** {st.session_state.depth_choice}")
        st.markdown(f"**📅 Date:** {st.session_state.trip_date}")
        st.markdown(f"**⏰ Time:** {st.session_state.trip_time}")
        st.markdown(f"**⏱️ Duration:** {st.session_state.duration} hours")

    with col2:
        # Meeting point based on depth
        meeting_points = {
            "shore": "🏖️ Beach access point",
            "snorkeling": "🚤 Harbor dock",
            "deep": "⚓ Dive dock",
        }

        st.markdown(
            f"**📍 Meeting Point:** {meeting_points[st.session_state.depth_preference]}"
        )

        # Required items based on depth
        required_items = {
            "shore": ["Sunscreen", "Hat", "Water bottle", "Towel"],
            "snorkeling": ["Sunscreen", "Hat", "Water bottle", "Towel", "Swimwear"],
            "deep": [
                "Sunscreen",
                "Hat",
                "Water bottle",
                "Towel",
                "Swimwear",
                "Motion sickness medication",
            ],
        }

        st.markdown(
            f"**🎒 Required Items:** {', '.join(required_items[st.session_state.depth_preference])}"
        )

        # Safety equipment
        st.markdown(f"**🛡️ Safety Equipment:** {', '.join(captain['equipment'])}")

    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Communicate with Your Captain")

    # Initialize chat messages if not exists or validate existing messages
    if not st.session_state.chat_messages:
        # Generate initial welcome message from captain using Gemini
        initial_message = generate_captain_response(
            captain_name=captain["name"],
            user_message=f"I just booked a {st.session_state.depth_choice} trip",
            mpa_name=mpa["name"],
            depth_zone=st.session_state.depth_choice,
            trip_date=st.session_state.trip_date,
        )

        st.session_state.chat_messages = [
            {
                "role": "captain",
                "content": f"👨‍✈️ {captain['name']}: {initial_message}",
                "timestamp": datetime.now().strftime("%H:%M"),
            }
        ]
    else:
        # Validate and fix any messages missing timestamp
        for msg in st.session_state.chat_messages:
            if "timestamp" not in msg:
                msg["timestamp"] = datetime.now().strftime("%H:%M")
            if "content" not in msg:
                msg["content"] = ""
            if "role" not in msg:
                msg["role"] = "captain"

    # Display chat messages
    chat_container = st.container(height=300)
    with chat_container:
        for message in st.session_state.chat_messages:
            # Get timestamp with fallback
            timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))
            content = message.get("content", "")

            if message.get("role") == "captain":
                st.markdown(
                    f'<div class="chat-message">{content} <small>({timestamp})</small></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-message user-message">{content} <small>({timestamp})</small></div>',
                    unsafe_allow_html=True,
                )

    # Chat input
    quick_messages = {
        "shore": [
            "We're running 5 minutes late",
            "Can we bring snacks?",
            "What's the water temperature?",
        ],
        "snorkeling": [
            "Do you have extra snorkel gear?",
            "Are there any jellyfish today?",
            "Can we see sea turtles?",
        ],
        "deep": [
            "Is the weather still good?",
            "Do you have motion sickness pills?",
            "What wildlife might we see?",
        ],
    }

    col1, col2 = st.columns([2, 1])

    with col1:
        user_message = st.text_input(
            "Type your message:", placeholder="Ask your captain anything..."
        )

    with col2:
        if st.button("Send Message", key="send_message"):
            if user_message:
                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content": user_message,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )

                # Generate captain response using Gemini with typing delay
                with st.spinner("💬 Captain is typing..."):
                    import time

                    response = generate_captain_response(
                        captain_name=captain["name"],
                        user_message=user_message,
                        mpa_name=mpa["name"],
                        depth_zone=st.session_state.depth_choice,
                        trip_date=st.session_state.trip_date,
                    )
                    # Add realistic typing delay
                    time.sleep(3)

                st.session_state.chat_messages.append(
                    {
                        "role": "captain",
                        "content": f"👨‍✈️ {captain['name']}: {response}",
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )

                st.rerun()

    # Quick message buttons
    st.markdown("**Quick Messages:**")
    quick_cols = st.columns(len(quick_messages[st.session_state.depth_preference]))
    for i, msg in enumerate(quick_messages[st.session_state.depth_preference]):
        with quick_cols[i]:
            if st.button(msg, key=f"quick_{i}"):
                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content": msg,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )

                # Generate captain response using Gemini with typing delay
                with st.spinner("💬 Captain is typing..."):
                    import time

                    response = generate_captain_response(
                        captain_name=captain["name"],
                        user_message=msg,
                        mpa_name=mpa["name"],
                        depth_zone=st.session_state.depth_choice,
                        trip_date=st.session_state.trip_date,
                    )
                    # Add realistic typing delay
                    time.sleep(3)

                st.session_state.chat_messages.append(
                    {
                        "role": "captain",
                        "content": f"👨‍✈️ {captain['name']}: {response}",
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )

                st.rerun()

    # Start Over button for Step 6
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            # Just clear chat messages
            st.session_state.chat_messages = []
            st.rerun()
    with col2:
        if st.button(
            "🔄 Start New Booking", type="secondary", use_container_width=True
        ):
            # Reset all session state
            st.session_state.selected_mpa = None
            st.session_state.group_size = 1
            st.session_state.depth_preference = None
            st.session_state.filtered_captains = []
            st.session_state.selected_captain = None
            st.session_state.booking_details = {}
            st.session_state.payment_processed = False
            st.session_state.chat_messages = []
            st.session_state.current_step = 1
            st.session_state.depth_choice = None
            st.session_state.trip_date = None
            st.session_state.trip_time = None
            st.session_state.duration = None
            st.rerun()

# Fallback: If user is on an invalid step, redirect to step 1
else:
    st.warning("⚠️ Please start from the beginning to book your boat trip.")
    if st.button("🏝️ Start Booking Process", key="start_booking", type="primary"):
        st.session_state.current_step = 1
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚤 <strong>MPA Boat Booking</strong> | Supporting Marine Conservation in Madagascar</p>
        <p style="font-size: 0.9rem;">This is a demonstration of how technology could connect tourists with accredited boat captains while supporting conservation efforts.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
