# 📍 Pin Drop Feature - Implementation Plan

## 🎯 Goal

Add a simple location checker that lets users input coordinates and check if they're inside any LMMA or MPA zone.

---

## 📋 Implementation Steps

### **Step 1: Add Location Checker UI** ✅

- Add sidebar section with title "📍 Check Your Location"
- Add number inputs for Latitude and Longitude
- Add "Check Location" button
- Add placeholder for results display

**Expected Outcome:**

- Sidebar shows input fields
- Button appears but doesn't do anything yet

**Testing:**

- Can type coordinates
- Button is clickable

---

### **Step 2: Implement Spatial Logic** ✅

- Create function to check if point intersects LMMA polygons
- Create function to check if point intersects MPA polygons
- Handle the spatial intersection using GeoPandas `.contains()`
- Return matched features (if any)

**Expected Outcome:**

- Function returns matching LMMA/MPA or None
- Logic works with test coordinates

**Testing:**

- Test with known LMMA coordinates
- Test with known MPA coordinates
- Test with ocean coordinates (no match)

---

### **Step 3: Display Results** ✅

- Format results nicely with emojis
- Show zone name, type, and country
- Handle "not in any zone" case
- Store result in session state

**Expected Outcome:**

- Nice formatted display
- Clear yes/no answer
- Details about the zone

**Testing:**

- Check result displays correctly
- Verify all information shown
- Test both match and no-match cases

---

### **Step 4: Add Pin to Map** ✅

- Create new PyDeck layer for user pin
- Use ScatterplotLayer for the pin marker
- Make it red and prominent
- Only show when user has checked a location

**Expected Outcome:**

- Red pin appears at checked coordinates
- Pin is visible on top of other layers
- Pin disappears on new check or page refresh

**Testing:**

- Pin appears at correct location
- Pin is visible and stands out
- Multiple checks update pin position

---

### **Step 5: AI Integration** ✅

- Update AI context with checked location info
- AI can reference the location in conversation
- Add to system prompt

**Expected Outcome:**

- AI knows about checked location
- Can answer questions about it
- Provides context-aware responses

**Testing:**

- Check location, then ask AI about it
- Verify AI references the correct zone

---

## 🧪 Test Cases

### Test Case 1: Known LMMA Location

**Input:**

- Lat: -12.5
- Lon: 49.3
  **Expected:** Should find Madagascar LMMA

### Test Case 2: Known MPA Location

**Input:**

- Lat: -4.6
- Lon: 55.5
  **Expected:** Should find Seychelles MPA

### Test Case 3: Open Ocean

**Input:**

- Lat: -10.0
- Lon: 60.0
  **Expected:** Not in any protected zone

### Test Case 4: Invalid Coordinates

**Input:**

- Lat: 95.0 (invalid)
- Lon: 200.0 (invalid)
  **Expected:** Handle gracefully with error message

---

## 📦 Dependencies Needed

✅ **All already installed:**

- `geopandas` - for spatial operations
- `shapely` - for Point geometry (comes with geopandas)
- `streamlit` - for UI
- `pydeck` - for map pin layer

❌ **No new packages needed!**

---

## 🎨 UI Design

```
┌─────────────────────────────────────┐
│ SIDEBAR                             │
├─────────────────────────────────────┤
│ 📍 Check Your Location              │
│                                     │
│ Latitude:  [   -15.5   ]           │
│ Longitude: [    49.5   ]           │
│                                     │
│        [🔍 Check Location]          │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Results:                        │ │
│ │ ✅ You are in:                  │ │
│ │    Nosy Tanikely MPA            │ │
│ │ 🏷️ Type: Marine Protected Area  │ │
│ │ 🌍 Country: Madagascar          │ │
│ │ 📍 Coordinates: -15.5, 49.5     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ MAP (shows red pin at location)    │
│        📍 ← Red pin here            │
└─────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Core Function:

```python
from shapely.geometry import Point

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
    point = Point(lon, lat)  # Shapely uses (lon, lat)

    # Check LMMAs
    lmma_match = gdf_lmma[gdf_lmma.geometry.contains(point)]
    if not lmma_match.empty:
        return {
            'type': 'LMMA',
            'name': lmma_match.iloc[0]['Name of LM'],
            'country': lmma_match.iloc[0]['Country'],
            'data': lmma_match.iloc[0]
        }

    # Check MPAs
    mpa_match = gdf_mpa[gdf_mpa.geometry.contains(point)]
    if not mpa_match.empty:
        return {
            'type': 'MPA',
            'name': mpa_match.iloc[0]['NAME'],
            'country': mpa_match.iloc[0]['Country'],
            'data': mpa_match.iloc[0]
        }

    return None
```

### Pin Layer:

```python
pdk.Layer(
    "ScatterplotLayer",
    data=[{"lat": lat, "lon": lon}],
    get_position='[lon, lat]',
    get_fill_color=[255, 0, 0, 200],  # Red
    get_radius=5000,  # 5km radius
    pickable=True,
)
```

---

## ✅ Success Criteria

1. ✅ User can input coordinates
2. ✅ Button triggers location check
3. ✅ Results display correctly for LMMA
4. ✅ Results display correctly for MPA
5. ✅ Results display correctly for "not found"
6. ✅ Red pin appears on map
7. ✅ Pin is at correct coordinates
8. ✅ AI knows about checked location
9. ✅ No errors or crashes
10. ✅ Works on first try (hackathon-ready!)

---

## 🚀 Estimated Time

- Step 1 (UI): 5 minutes
- Step 2 (Logic): 5 minutes
- Step 3 (Display): 5 minutes
- Step 4 (Pin): 5 minutes
- Step 5 (AI): 3 minutes
- **Total: ~25 minutes**

---

## 📝 Notes

- Keep it simple - hackathon prototype
- Focus on "just works"
- Nice-to-have: Example coordinates buttons
- Future: Add geolocation API
- Future: Click on map to drop pin

---

**Status:** 📋 READY TO START
**Next:** Implement Step 1
