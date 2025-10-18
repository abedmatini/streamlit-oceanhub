#import geopandas as gpd
#import matplotlib.pyplot as plt
#from matplotlib.patches import FancyArrow

#gdf = gpd.read_file(gpd.datasets.get_path("./wio_lmma_ioc.shp"))

# map.py
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow

# --- load the shapefile ------------------------------------------------------
shapefile_path = "wio_lmma_ioc.shp"  # or "./wio_lmma_ioc.shp"

if not os.path.exists(shapefile_path):
 raise FileNotFoundError(
     f"Couldn't find '{shapefile_path}' in {os.getcwd()}. "
     "Make sure the .shp and its companion files (.shx, .dbf, etc.) "
     "are in the same directory as this script."
 )

gdf = gpd.read_file(shapefile_path)

print("Loaded GeoDataFrame:")
print(gdf.head())
print(gdf.crs)

# --- plot --------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))
gdf.plot(
 ax=ax,
 color="#6baed6",
 edgecolor="#08306b",
 linewidth=0.5,
)

# Add an arrow from the lower-left to the upper-right of the dataset’s bounds.
minx, miny, maxx, maxy = gdf.total_bounds
dx = maxx - minx
dy = maxy - miny
arrow = FancyArrow(
 x=minx + 0.05 * dx,
 y=miny + 0.05 * dy,
 dx=0.3 * dx,
 dy=0.3 * dy,
 width=0.02 * dx,
 length_includes_head=True,
 head_width=0.05 * dx,
 head_length=0.08 * dy,
 color="crimson",
 alpha=0.6,
)
ax.add_patch(arrow)

ax.set_title("WIO LMMA IOC Shapefile", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_aspect("equal")
ax.grid(True, linestyle=":", alpha=0.3)

plt.tight_layout()
plt.show()