# Integration Plan: Adding MPA Data to the Map

## 📊 Data Summary

### Shapefile 1: LMMA (Locally Managed Marine Areas)

- **File**: `wio_lmma_ioc.shp`
- **Features**: 421
- **Countries**: Madagascar (412), Mauritius (7), Comoros (2)
- **CRS**: EPSG:4326 (WGS84)
- **Key Column**: `Name of LM`

### Shapefile 2: MPA (Marine Protected Areas) - NEW!

- **File**: `wio_mpa_ioc.shp`
- **Features**: 78
- **Countries**: Seychelles (25), Madagascar (22), Mauritius (18), France (9), Comoros (4)
- **CRS**: World_Mercator (ESRI:54004) ⚠️ **DIFFERENT**
- **Key Column**: `NAME`

### Combined Statistics

- **Total Features**: 499 (421 LMMAs + 78 MPAs)
- **Total Countries**: 6 (added Seychelles + France)
- **CRS Issue**: Need to reproject MPA to EPSG:4326

---

## 🎯 Implementation Options

### **Option 1: Two Separate Layers** ⭐ RECOMMENDED

**Best for**: Distinguishing between LMMA and MPA types

**Map Display**:

- 🔵 Blue layer: LMMAs (existing)
- 🟢 Green layer: MPAs (new)
- Both visible at once
- Different tooltips for each

**Chat Context**:

- AI knows about both types
- Can answer: "How many LMMAs vs MPAs?"
- Type-specific queries

**Pros**:

- ✅ Clear visual distinction
- ✅ Easy to understand different types
- ✅ Can filter/toggle layers
- ✅ Preserve original data structure

**Cons**:

- Need to load 2 shapefiles
- Slightly more code

---

### **Option 2: Merged Single Layer**

**Best for**: Simpler unified view

**Map Display**:

- Single layer with type indicator
- Color by type: LMMA vs MPA
- Unified tooltip

**Chat Context**:

- Total combined features
- Can filter by type in queries

**Pros**:

- ✅ Simpler code
- ✅ Single data structure
- ✅ Easy country totals

**Cons**:

- Need to merge different column structures
- Lose some unique attributes
- More data preprocessing

---

### **Option 3: Toggleable Layers**

**Best for**: User choice and exploration

**Map Display**:

- Checkbox to show/hide each layer
- Switch between datasets
- Compare coverage

**Chat Context**:

- AI aware of active layer(s)
- Context changes based on selection

**Pros**:

- ✅ Maximum flexibility
- ✅ User control
- ✅ Less visual clutter

**Cons**:

- Most complex to implement
- Need UI for controls

---

## 🚀 Recommended Implementation: **Option 1**

### Why Option 1?

1. **Scientific accuracy**: LMMAs and MPAs are different management approaches
2. **Visual clarity**: Colors help users distinguish types
3. **Educational value**: Users learn the difference
4. **Minimal changes**: Builds on existing code
5. **Flexible**: Can add Option 3 later

---

## 📝 Implementation Steps

### Step 1: Load Both Shapefiles

```python
gdf_lmma = gpd.read_file("wio_lmma_ioc.shp")
gdf_mpa = gpd.read_file("wio_mpa_ioc.shp")

# Reproject MPA to match LMMA CRS
gdf_mpa = gdf_mpa.to_crs(epsg=4326)
```

### Step 2: Create Two Map Layers

```python
# Blue layer for LMMAs
lmma_layer = pdk.Layer(
    "GeoJsonLayer",
    data=geojson_lmma,
    get_fill_color=[82, 170, 225, 120],  # Blue
    ...
)

# Green layer for MPAs
mpa_layer = pdk.Layer(
    "GeoJsonLayer",
    data=geojson_mpa,
    get_fill_color=[46, 204, 113, 120],  # Green
    ...
)

# Add both to deck
layers=[lmma_layer, mpa_layer]
```

### Step 3: Update AI Context

```python
data_context = f"""
CURRENT DATA LOADED:
- LMMA features: {len(gdf_lmma)} (community-managed)
- MPA features: {len(gdf_mpa)} (protected areas)
- Total features: {len(gdf_lmma) + len(gdf_mpa)}

LMMA COUNTRIES:
- Madagascar: 412, Mauritius: 7, Comoros: 2

MPA COUNTRIES:
- Seychelles: 25, Madagascar: 22, Mauritius: 18, France: 9, Comoros: 4

DEFINITIONS:
- LMMAs: Locally Managed Marine Areas (community-based)
- MPAs: Marine Protected Areas (government-designated)
"""
```

### Step 4: Update Welcome Message

```python
f"📊 **Current Data:**
- **{len(gdf_lmma)} LMMAs** (community-managed)
- **{len(gdf_mpa)} MPAs** (protected areas)
- **{total_countries} countries** represented
- Covering the **Western Indian Ocean** region"
```

### Step 5: Add Legend

```python
st.markdown("""
🔵 **Blue**: LMMAs (Locally Managed Marine Areas)
🟢 **Green**: MPAs (Marine Protected Areas)
""")
```

---

## 🎨 Color Scheme

- 🔵 **LMMAs**: RGB(82, 170, 225) - Ocean Blue
- 🟢 **MPAs**: RGB(46, 204, 113) - Emerald Green

Both with transparency (alpha 120) to show overlap

---

## 💬 AI Chat Enhancements

### New Questions Users Can Ask:

- "What's the difference between LMMA and MPA?"
- "How many MPAs are in Seychelles?"
- "Which has more features, LMMAs or MPAs?"
- "What countries have both LMMAs and MPAs?"
- "Compare Madagascar's LMMAs and MPAs"

### AI Context Updates:

```
ABOUT LMMAs:
- Community-based management
- Local participation in governance
- Sustainable fisheries focus

ABOUT MPAs:
- Government-designated protected areas
- Often stricter regulations
- Biodiversity conservation focus
```

---

## ✅ Expected Benefits

1. **More Complete Data**: 421 → 499 features (+18%)
2. **More Countries**: 3 → 6 countries (added Seychelles, France, and more coverage)
3. **Better Context**: Users see full protection landscape
4. **Educational**: Learn differences between management types
5. **Richer Analysis**: Compare approaches, coverage, effectiveness

---

## 🔄 Future Enhancements

After implementing Option 1, we can add:

1. **Layer Toggles**: Checkbox to show/hide each type
2. **Statistics Panel**: Compare LMMA vs MPA metrics
3. **Filtering**: Show only one country's data
4. **Click Details**: Pop-up with full feature info
5. **Export**: Download filtered data

---

## 📁 Files to Modify

1. ✅ `streamlit_map.py` - Main application
2. ✅ Update AI context
3. ✅ Add second layer
4. ✅ Update welcome message

---

Ready to implement Option 1? Say "Yes, implement Option 1" and I'll add the code!
