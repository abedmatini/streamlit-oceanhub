# pages/chat.py
import os
import base64
import mimetypes
import random
from io import BytesIO
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Marine Protected Areas Explorer",
    page_icon="🐠",
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
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #007bff;
        text-align: center;
        margin: 1rem 0;
    }
    .chat-container {
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 1rem;
    }
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
</style>
""",
    unsafe_allow_html=True,
)

# Main header
st.markdown(
    """
<div class="main-header">
    <h1>🐠 Marine Protected Areas Explorer</h1>
    <p style="font-size: 1.2rem; margin: 0;">Transform into a marine protector fish and learn about MPAs & LMMAs!</p>
</div>
""",
    unsafe_allow_html=True,
)

# Google GenAI API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Manual fallback if load_dotenv fails
if not GEMINI_API_KEY:
    try:
        env_path = os.path.join(os.getcwd(), ".env")
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    GEMINI_API_KEY = line.strip().split("=", 1)[1]
                    break
    except Exception as e:
        pass

if not GEMINI_API_KEY:
    st.error(
        "❌ GEMINI_API_KEY is missing. Please set it in your .env file and restart Streamlit."
    )
    st.stop()

# Initialize Gemini client for image generation
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini client: {e}")
    st.stop()

# Marine Protected Areas (MPAs) facts
MPA_FACTS = [
    "Marine Protected Areas (MPAs) are designated ocean spaces where human activities are restricted to conserve marine ecosystems and biodiversity.",
    "There are over 15,000 MPAs worldwide, covering approximately 7.5% of the global ocean area as of 2023.",
    "MPAs can increase fish biomass by up to 446% and species richness by 21% compared to unprotected areas.",
    "The Great Barrier Reef Marine Park in Australia is one of the world's largest MPAs, covering 344,400 square kilometers.",
    "MPAs help protect critical habitats like coral reefs, seagrass beds, mangrove forests, and deep-sea ecosystems.",
    "Well-designed MPAs can serve as 'spillover' areas, where fish populations recover and migrate to surrounding fishing areas.",
    "MPAs are essential tools for climate change adaptation, helping marine ecosystems build resilience to warming oceans.",
    "The Papahānaumokuākea Marine National Monument in Hawaii is larger than all US national parks combined.",
]

# Locally Managed Marine Areas (LMMAs) facts
LMMA_FACTS = [
    "Locally Managed Marine Areas (LMMAs) are marine conservation areas managed by local communities rather than governments.",
    "LMMAs empower coastal communities to take ownership of marine resource management and conservation efforts.",
    "Community-based management in LMMAs often leads to better compliance and enforcement than top-down approaches.",
    "LMMAs typically combine traditional ecological knowledge with modern conservation science for effective management.",
    "The LMMA Network spans over 500 sites across 20 countries, protecting over 1.2 million hectares of marine habitat.",
    "LMMAs often include temporary closures, gear restrictions, and size limits to allow fish populations to recover.",
    "Community-managed areas can be more cost-effective than government-managed MPAs, requiring less infrastructure.",
    "LMMAs support sustainable livelihoods by balancing conservation goals with local fishing and tourism needs.",
]

# Marine conservation tourism information
CONSERVATION_TOURISM_INFO = "Marine conservation tourism offers incredible opportunities to visit MPAs and LMMAs worldwide! Many protected areas welcome visitors for eco-tourism activities like snorkeling, diving, and educational tours. These experiences support local conservation efforts while providing sustainable income for coastal communities. Popular destinations include the Great Barrier Reef, Galápagos Marine Reserve, and community-managed areas in the Pacific and Indian Oceans."


def transform_image_to_fish(image_bytes, uploaded_file):
    """Transform uploaded image to cartoon fish using Gemini 2.5 Flash Image"""
    try:
        # Create improved prompt with marine protection elements
        prompt = """Transform the uploaded face (adult or child) into a fun, cartoon-style fish character that represents marine protection and conservation in Marine Protected Areas (MPAs) and Locally Managed Marine Areas (LMMAs).

The transformation should:
- Maintain the person's key facial features while adding colorful fish elements
- Add decorative fins, scales, and a fish tail
- Include subtle references to marine conservation (like small coral, seagrass, or protected area elements)
- Keep the overall look friendly and whimsical

Style reference: Colorful, cartoon animation with playful features that highlights the importance of protecting marine ecosystems through MPAs and LMMAs.

After generating the fish transformation:
1. Show the transformed image
2. Provide exactly ONE interesting fact about Marine Protected Areas (MPAs) or Locally Managed Marine Areas (LMMAs)
3. Include a brief statement about marine conservation tourism opportunities
"""

        # Create proper content structure with inline_data for image
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
                        data=image_bytes, mime_type=uploaded_file.type
                    ),
                ],
            )
        ]

        # Generate content with image and text using Gemini 2.5 Flash Image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=contents,
        )

        # Process the response to extract images and text
        response_text = ""
        response_images = []

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                response_text += part.text
            elif part.inline_data is not None:
                response_images.append(
                    {
                        "data": part.inline_data.data,
                        "mime_type": part.inline_data.mime_type,
                        "caption": "Your Marine Protector Fish Transformation!",
                    }
                )

        # If no AI response text, add our own content
        if not response_text:
            mpa_fact = random.choice(MPA_FACTS)
            lmma_fact = random.choice(LMMA_FACTS)

            response_text = f"""🐠 **Ta-da! You've been transformed into a marine protector fish!**

Here's your amazing fish transformation! You're now part of the global marine conservation effort! 🎨

---

🏛️ **Marine Protected Area (MPA) Fact:**
{mpa_fact}

---

🏘️ **Locally Managed Marine Area (LMMA) Fact:**
{lmma_fact}

---

✈️ **Marine Conservation Tourism:**
{CONSERVATION_TOURISM_INFO}

Feel free to ask me more about MPAs, LMMAs, or marine conservation!"""

        return response_text, response_images, None

    except Exception as e:
        return None, None, f"Error: {str(e)}"


def get_chat_response(prompt):
    """Generate a chat response about MPAs, LMMAs, or marine conservation"""
    try:
        # Create a context-aware prompt
        context_prompt = f"""You are a friendly marine conservation expert who specializes in Marine Protected Areas (MPAs), Locally Managed Marine Areas (LMMAs), and marine conservation.
        
        The user has asked: "{prompt}"
        
        If they're asking about MPAs, provide information about Marine Protected Areas, their benefits, management, and global examples.
        
        If they're asking about LMMAs, share information about Locally Managed Marine Areas, community-based management, and their effectiveness.
        
        If they're asking about marine conservation tourism, provide information about visiting protected areas, eco-tourism opportunities, and sustainable travel.
        
        If they're asking about marine conservation in general, discuss the importance of protecting marine ecosystems, threats to ocean health, and conservation solutions.
        
        Keep your response friendly, informative, and focused on marine conservation. Use emoji occasionally for a fun tone.
        
        Limit your response to 3-4 paragraphs maximum."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[context_prompt],
        )

        return response.candidates[0].content.parts[0].text

    except Exception as e:
        return f"I encountered an error generating a response: {str(e)}\n\nPlease try asking something else about MPAs, LMMAs, or marine conservation."


# Initialize session state for chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

    # Welcome message
    welcome_msg = """👋 Welcome to Marine Protected Areas Explorer!

🐠 **What I can do:**
- Transform your uploaded photo into a fun cartoon fish character
- Share interesting facts about Marine Protected Areas (MPAs) and Locally Managed Marine Areas (LMMAs)
- Tell you about marine conservation tourism opportunities worldwide

📸 **How to get started:**
1. Upload your photo using the file uploader above
2. Your transformation will happen automatically!
3. Get your cartoon fish transformation + marine conservation facts!

Let's explore marine protection together! 🎨✨"""

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": welcome_msg, "images": []}
    )

# Image upload section with improved styling
st.markdown(
    """
<div class="upload-section">
    <h2>📸 Upload Your Photo</h2>
    <p>Choose a clear photo of your face to transform into a marine protector fish!</p>
</div>
""",
    unsafe_allow_html=True,
)

uploaded_image = st.file_uploader(
    "Choose a photo of your face:",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear photo of your face to transform into a cartoon fish character",
    label_visibility="collapsed",
)

# Check if this is a new upload
if uploaded_image and uploaded_image not in st.session_state.get(
    "processed_images", []
):
    # Add to processed images to prevent reprocessing
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = []
    st.session_state.processed_images.append(uploaded_image)

    # Read the uploaded image
    image_bytes = uploaded_image.read()

    # Add user message
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": "🎨 Transform me into a marine protector fish!",
            "images": [{"data": image_bytes, "caption": "My Photo"}],
        }
    )

    # Transform image automatically
    with st.spinner("🐠 Transforming you into a marine protector fish..."):
        response_text, response_images, error = transform_image_to_fish(
            image_bytes, uploaded_image
        )

        if response_text and response_images:
            # Add assistant response with AI-generated content
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": response_text,
                    "images": response_images,
                }
            )

        elif error:
            error_msg = f"❌ Oops! Something went wrong with the transformation: {error}\n\nPlease try uploading a different photo or try again later."
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": error_msg, "images": []}
            )
        else:
            # Fallback response if no content generated
            mpa_fact = random.choice(MPA_FACTS)
            lmma_fact = random.choice(LMMA_FACTS)

            fallback_response = f"""🐠 **We had some trouble with the transformation, but here's some marine conservation info!**

---

🏛️ **Marine Protected Area (MPA) Fact:**
{mpa_fact}

---

🏘️ **Locally Managed Marine Area (LMMA) Fact:**
{lmma_fact}

---

✈️ **Marine Conservation Tourism:**
{CONSERVATION_TOURISM_INFO}

Feel free to ask me more about MPAs, LMMAs, or marine conservation!"""

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": fallback_response,
                    "images": [],
                }
            )

    st.rerun()

elif uploaded_image:
    # Show the uploaded image preview
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(uploaded_image, caption="Your Original Photo", width=300)
    with col2:
        st.success("✅ Photo uploaded! Check the chat below for your transformation!")

# Chat interface with improved styling
st.markdown(
    """
<div class="chat-container">
    <h2>💬 Chat about MPAs, LMMAs & Marine Conservation</h2>
</div>
""",
    unsafe_allow_html=True,
)

# Display chat messages
chat_container = st.container(height=500)
with chat_container:
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display images if any
            if "images" in message and message["images"]:
                cols = st.columns(min(len(message["images"]), 2))
                for idx, img_data in enumerate(message["images"]):
                    with cols[idx % 2]:
                        if isinstance(img_data["data"], bytes):
                            st.image(
                                img_data["data"],
                                caption=img_data.get("caption", "Image"),
                            )
                        else:
                            st.image(
                                img_data["data"],
                                caption=img_data.get("caption", "Image"),
                            )

# Chat input
if prompt := st.chat_input("Ask me about MPAs, LMMAs, or marine conservation..."):
    # Add user message
    st.session_state.chat_messages.append(
        {"role": "user", "content": prompt, "images": []}
    )

    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Generate response using Gemini
    with st.spinner("Thinking..."):
        response = get_chat_response(prompt)

    # Display assistant response
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(response)

            # Add to session state
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": response, "images": []}
            )

    st.rerun()

# Action buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.processed_images = []
        st.rerun()

# Add information about marine protection
with st.expander("ℹ️ About Marine Protected Areas & LMMAs", expanded=False):
    st.markdown(
        """
        ## 🌊 Marine Protected Areas (MPAs) & Locally Managed Marine Areas (LMMAs)
        
        **Marine Protected Areas (MPAs)** are designated ocean spaces where human activities are restricted to conserve marine ecosystems and biodiversity. They can increase fish biomass by up to 446% and species richness by 21% compared to unprotected areas.
        
        **Locally Managed Marine Areas (LMMAs)** are marine conservation areas managed by local communities rather than governments. The LMMA Network spans over 500 sites across 20 countries, protecting over 1.2 million hectares of marine habitat.
        
        ### Key Benefits:
        
        - **Biodiversity Protection**: Safeguard critical habitats like coral reefs, seagrass beds, and mangrove forests
        - **Fish Population Recovery**: Allow marine species to reproduce and grow without fishing pressure
        - **Climate Resilience**: Help marine ecosystems adapt to warming oceans and acidification
        - **Sustainable Livelihoods**: Support eco-tourism and sustainable fishing practices
        
        ### How You Can Help:
        
        - Support marine conservation organizations working on MPA establishment
        - Choose sustainable seafood and eco-tourism options
        - Spread awareness about the importance of marine protection
        - Participate in citizen science programs monitoring marine health
        """
    )

# Clean footer for demo
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🐠 <strong>Marine Protected Areas Explorer</strong> | Supporting Global Marine Conservation</p>
    </div>
    """,
    unsafe_allow_html=True,
)
