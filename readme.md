# 🌊 WIO Marine Conservation Map with AI Assistant

An interactive web application for visualizing and exploring marine conservation areas in the Western Indian Ocean (WIO) region, featuring AI-powered chat assistance and location checking capabilities.

---

## 📊 What Does This Project Do?

This Streamlit application (`streamlit_map.py`) provides:

### **🗺️ Interactive Map Visualization**

- Displays **421 Locally Managed Marine Areas (LMMAs)** in blue
- Displays **78 Marine Protected Areas (MPAs)** in green
- Covers 6 countries: Madagascar, Mauritius, Comoros, Seychelles, France, Tanzania
- Interactive tooltips with zone information
- Dual-layer visualization using Mapbox and PyDeck

### **📍 Location Checker**

- Check if any coordinates fall within a protected zone
- Quick test buttons for common locations
- Manual coordinate input (latitude/longitude)
- Visual red pin marker on the map
- Detailed results showing zone name, type, country, and establishment year
- Spatial analysis using GeoPandas and Shapely

### **🤖 AI Chat Assistant**

- Powered by Google Gemini AI (gemini-2.5-flash)
- Context-aware responses about marine conservation data
- Knows about LMMAs vs MPAs differences
- Can answer questions about checked locations
- Provides educational information about marine conservation
- Example question buttons for quick queries

### **⚡ Performance Features**

- Cached data loading for fast subsequent loads
- Optimized shapefile processing
- Responsive two-column layout (60% map, 40% chat)
- Data preview tabs for both LMMA and MPA datasets

---

## 🚀 First Time Setup

### **Prerequisites**

- Python 3.8 or higher
- Git (optional, for cloning)
- Mapbox API key ([Get free key](https://account.mapbox.com/access-tokens/))
- Google Gemini API key ([Get free key](https://aistudio.google.com/app/apikey))

---

### **Step 1: Clone or Download the Project**

```bash
# Option A: Clone with Git
git clone https://github.com/abedmatini/streamlit-oceanhub.git
cd streamlit-oceanhub

# Option B: Download ZIP and extract
# Then navigate to the folder
cd streamlit-oceanhub
```

---

### **Step 2: Create Virtual Environment**

#### **On Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### **On macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### **Step 3: Install Dependencies**

#### **Option A: Using requirements.txt (Recommended) ⭐**

```bash
pip install -r requirements.txt
```

This will automatically install all required packages with correct versions.

#### **Option B: Manual Installation**

```bash
pip install python-dotenv geopandas streamlit pydeck google-generativeai
```

**Required packages:**

- `streamlit` - Web application framework
- `pydeck` - Map visualization library
- `geopandas` - Geospatial data processing
- `python-dotenv` - Environment variable management
- `google-generativeai` - Google Gemini AI SDK
- `pandas` - Data manipulation (comes with geopandas)
- `shapely` - Geometric operations (comes with geopandas)

#### **Verify Installation:**

```bash
pip list
```

You should see all the packages listed above.

---

### **Step 4: Set Up API Keys**

Create a `.env` file in the project root directory:

```bash
# On Windows
notepad .env

# On macOS/Linux
nano .env
```

Add your API keys to the `.env` file:

```env
MAPBOX_API_KEY=your_mapbox_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

**How to get API keys:**

1. **Mapbox API Key:**

   - Visit: https://account.mapbox.com/access-tokens/
   - Sign up or log in
   - Create a new token (default public token works)
   - Copy and paste into `.env`

2. **Google Gemini API Key:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Select "Create API key in new project"
   - Copy and paste into `.env`

**Important:** Never commit your `.env` file to Git! (It's already in `.gitignore`)

---

### **Step 5: Verify Required Data Files**

Make sure these shapefile components are in your project directory:

**LMMA Shapefile:**

- `wio_lmma_ioc.shp`
- `wio_lmma_ioc.shx`
- `wio_lmma_ioc.dbf`
- `wio_lmma_ioc.prj`
- `wio_lmma_ioc.cpg`

**MPA Shapefile:**

- `wio_mpa_ioc.shp`
- `wio_mpa_ioc.shx`
- `wio_mpa_ioc.dbf`
- `wio_mpa_ioc.prj`
- `wio_mpa_ioc.cpg`

---

### **Step 6: Run the Application**

```bash
streamlit run streamlit_map.py
```

The app will automatically open in your default browser at: `http://localhost:8501`

---

## 🎯 How to Use

### **Exploring the Map**

1. View the interactive map with blue (LMMA) and green (MPA) zones
2. Hover over zones to see tooltips
3. Use mouse to pan and zoom
4. Check the legend for feature counts

### **Checking a Location**

1. Look at the sidebar on the left
2. Click a quick test button (Madagascar, Seychelles, or Ocean)
3. OR enter coordinates manually
4. Click "🔍 Check Location"
5. View results and see the red pin on the map

### **Chatting with AI**

1. Scroll to the chat panel on the right
2. Type a question or click an example button
3. Ask about:
   - Differences between LMMA and MPA
   - Country-specific data
   - The location you just checked
   - Marine conservation topics

---

## 📂 Project Structure

```
streamlit-oceanhub/
├── streamlit_map.py          # Main application (519 lines)
├── requirements.txt           # Python dependencies
├── .env                       # API keys (DO NOT COMMIT)
├── readme.md                  # This file
├── wio_lmma_ioc.*            # LMMA shapefile components
├── wio_mpa_ioc.*             # MPA shapefile components
├── check_data.py              # Data analysis utility
├── .gitignore                 # Git ignore rules
└── Documentation/
    ├── PROJECT_PLAN.md
    ├── PIN_DROP_FEATURE_PLAN.md
    ├── FINAL_TESTING_GUIDE.md
    ├── PROJECT_STATUS_FINAL.md
    └── ... (15+ documentation files)
```

---

## 🛠️ Troubleshooting

### **"Module not found" errors:**

```bash
pip install --upgrade pip
pip install python-dotenv geopandas streamlit pydeck google-generativeai
```

### **API key errors:**

- Check that `.env` file exists in the project root
- Verify API keys are correct (no extra spaces or quotes)
- Ensure `.env` format: `KEY=value` (no quotes needed)

### **Map doesn't load:**

- Verify Mapbox API key is valid
- Check internet connection
- Try refreshing the browser

### **AI doesn't respond:**

- Verify Gemini API key is valid
- Check API quota (15 requests/minute on free tier)
- Try refreshing the page

### **Shapefile errors:**

- Ensure all shapefile components (.shp, .shx, .dbf, .prj) are present
- Verify files are in the same directory as `streamlit_map.py`

---

## 🎓 Technical Details

### **Technologies Used:**

- **Frontend:** Streamlit (Python web framework)
- **Mapping:** PyDeck (Deck.gl) + Mapbox
- **Geospatial:** GeoPandas + Shapely
- **AI:** Google Gemini 2.5 Flash
- **Data Format:** Shapefiles (ESRI format)

### **Data Processing:**

- Shapefiles loaded with GeoPandas
- CRS transformation to EPSG:4326 (WGS84)
- Cached with `@st.cache_data` for performance
- Spatial queries using `geometry.contains()`

### **Architecture:**

- Two-column layout (60/40 split)
- Session state for coordinate persistence
- Real-time AI context updates
- Dynamic map layer composition

---

## 📊 Data Sources

- **LMMAs:** 421 locally managed marine areas
- **MPAs:** 78 marine protected areas
- **Region:** Western Indian Ocean (WIO)
- **Countries:** Madagascar, Mauritius, Comoros, Seychelles, France, Tanzania
- **Coordinate System:** EPSG:4326 (WGS84)

---

## 🤝 Contributing

This project was developed for a hackathon. Feel free to:

- Report issues
- Suggest features
- Submit pull requests
- Fork and modify for your needs

---

## 📄 License

[Add your license information here]

---

## 👥 Authors

- [Add author information here]

---

## 🙏 Acknowledgments

- Google Gemini AI for chat capabilities
- Mapbox for map visualization
- Marine conservation organizations for data

---

## 📞 Support

For questions or issues:

- Open a GitHub issue
- Check documentation files in the project
- Review the FINAL_TESTING_GUIDE.md for testing help

---

## 🎉 Quick Start Summary

```bash
# 1. Navigate to project
cd streamlit-oceanhub

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies (RECOMMENDED)
pip install -r requirements.txt

# 5. Create .env file with your API keys
# MAPBOX_API_KEY=your_mapbox_key_here
# GEMINI_API_KEY=your_gemini_key_here

# 6. Run the app
streamlit run streamlit_map.py
```

**🚀 That's it! Your app should now be running at http://localhost:8501**

---

**Happy Mapping! 🌊🗺️🤖**
