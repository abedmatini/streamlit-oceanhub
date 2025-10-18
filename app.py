import streamlit as st
import pydeck as pdk

# Rectangle coordinates (bounding box)
rectangle = pdk.Layer(
    "PolygonLayer",
    [
        {
            "polygon": [
                [18.41, -33.93],  # SW corner
                [18.41, -33.91],  # NW corner
                [18.44, -33.91],  # NE corner
                [18.44, -33.93],  # SE corner
                [18.41, -33.93],  # Close polygon
            ]
        }
    ],
    get_polygon="polygon",
    get_fill_color=[255, 0, 0, 80],  # Red with transparency
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(latitude=-33.92, longitude=18.42, zoom=12)
st.pydeck_chart(pdk.Deck(layers=[rectangle], initial_view_state=view_state))