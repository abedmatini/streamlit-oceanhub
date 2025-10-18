# Check Shapefile Data Structure

import geopandas as gpd
import pandas as pd

print("=" * 80)
print("CHECKING BOTH SHAPEFILES")
print("=" * 80)

# ══════════════════════════════════════════════════════════════════════════════
# SHAPEFILE 1: wio_lmma_ioc.shp (EXISTING)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "🔵 " * 40)
print("SHAPEFILE 1: wio_lmma_ioc.shp (LMMAs)")
print("🔵 " * 40)

gdf_lmma = gpd.read_file("wio_lmma_ioc.shp")

print("\n📋 AVAILABLE COLUMNS:")
print("-" * 80)
for i, col in enumerate(gdf_lmma.columns, 1):
    print(f"{i}. {col}")

if 'Country' in gdf_lmma.columns:
    print("\n✅ 'Country' column EXISTS")
    print("\n🌍 COUNTRIES IN DATA:")
    print("-" * 80)
    country_counts = gdf_lmma['Country'].value_counts()
    for country, count in country_counts.items():
        print(f"  {country}: {count} features")
    print(f"\n  Total Countries: {len(country_counts)}")

print(f"\n📍 TOTAL FEATURES: {len(gdf_lmma)}")
print(f"🗺️  CRS: {gdf_lmma.crs}")

# ══════════════════════════════════════════════════════════════════════════════
# SHAPEFILE 2: wio_mpa_ioc.shp (NEW)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "🟢 " * 40)
print("SHAPEFILE 2: wio_mpa_ioc.shp (MPAs - NEW)")
print("🟢 " * 40)

gdf_mpa = gpd.read_file("wio_mpa_ioc.shp")

print("\n📋 AVAILABLE COLUMNS:")
print("-" * 80)
for i, col in enumerate(gdf_mpa.columns, 1):
    print(f"{i}. {col}")

if 'Country' in gdf_mpa.columns:
    print("\n✅ 'Country' column EXISTS")
    print("\n🌍 COUNTRIES IN DATA:")
    print("-" * 80)
    country_counts = gdf_mpa['Country'].value_counts()
    for country, count in country_counts.items():
        print(f"  {country}: {count} features")
    print(f"\n  Total Countries: {len(country_counts)}")
else:
    print("\n❌ 'Country' column NOT FOUND")
    print("\n🔍 Columns that might contain country data:")
    for col in gdf_mpa.columns:
        if any(keyword in col.lower() for keyword in ['country', 'nation', 'state', 'region', 'name']):
            print(f"  - {col}")

print("\n📊 SAMPLE DATA (first 3 rows):")
print("-" * 80)
print(gdf_mpa.drop(columns='geometry').head(3).to_string())

print(f"\n📍 TOTAL FEATURES: {len(gdf_mpa)}")
print(f"🗺️  CRS: {gdf_mpa.crs}")

# ══════════════════════════════════════════════════════════════════════════════
# COMPARISON & MERGE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "🔶 " * 40)
print("COMPARISON & MERGE ANALYSIS")
print("� " * 40)

print(f"\n📊 SUMMARY:")
print("-" * 80)
print(f"  LMMA Features: {len(gdf_lmma)}")
print(f"  MPA Features:  {len(gdf_mpa)}")
print(f"  Combined:      {len(gdf_lmma) + len(gdf_mpa)}")

print(f"\n🗺️  CRS COMPATIBILITY:")
print("-" * 80)
print(f"  LMMA CRS: {gdf_lmma.crs}")
print(f"  MPA CRS:  {gdf_mpa.crs}")
if gdf_lmma.crs == gdf_mpa.crs:
    print("  ✅ CRS MATCH - Can merge directly")
else:
    print("  ⚠️  CRS DIFFERENT - Need to reproject before merge")

print("\n📋 COLUMN COMPARISON:")
print("-" * 80)
lmma_cols = set(gdf_lmma.columns) - {'geometry'}
mpa_cols = set(gdf_mpa.columns) - {'geometry'}
common_cols = lmma_cols & mpa_cols
lmma_only = lmma_cols - mpa_cols
mpa_only = mpa_cols - lmma_cols

print(f"  Common columns: {len(common_cols)}")
if common_cols:
    print(f"    {', '.join(sorted(common_cols))}")
print(f"\n  LMMA-only columns: {len(lmma_only)}")
if lmma_only:
    print(f"    {', '.join(sorted(list(lmma_only)[:5]))}{'...' if len(lmma_only) > 5 else ''}")
print(f"\n  MPA-only columns: {len(mpa_only)}")
if mpa_only:
    print(f"    {', '.join(sorted(list(mpa_only)[:5]))}{'...' if len(mpa_only) > 5 else ''}")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("✅ You can display both shapefiles on the same map!")
print("   - Option 1: Show as separate layers (different colors)")
print("   - Option 2: Merge into one layer")
print("   - Option 3: Add toggle to switch between them")
print("=" * 80)
