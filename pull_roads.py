
import osmnx as ox
import geopandas as gpd
from shapely import force_2d

PLACE   = "Detroit, Michigan, USA"
OUTFILE = "data/detroit_roads_osm.geojson"

print(f"Downloading road network for: {PLACE}")

# Geocode separately to avoid internal geometry-collection issue in graph_from_place
place_gdf    = ox.geocode_to_gdf(PLACE)
detroit_poly = force_2d(place_gdf.geometry.iloc[0])   # strip Z before passing in

G = ox.graph_from_polygon(detroit_poly, network_type="drive", simplify=True)

# Convert graph edges to GeoDataFrame
nodes, edges = ox.graph_to_gdfs(G)

# Keep useful columns
keep = ["name", "highway", "lanes", "maxspeed", "oneway", "length", "geometry"]
roads = edges[[c for c in keep if c in edges.columns]].reset_index(drop=True)

# Flatten list-valued cells (osmnx sometimes returns lists for name/highway)
for col in ["name", "highway", "maxspeed", "lanes"]:
    if col in roads.columns:
        roads[col] = roads[col].apply(
            lambda v: v[0] if isinstance(v, list) else v
        )

# Fix 1: drop Z coordinates (mixed 2D/3D breaks shapely ufuncs on export)
roads["geometry"] = roads["geometry"].apply(force_2d)

# Fix 2: explode MultiLineStrings -> LineStrings for uniform geometry type
roads = roads.explode(index_parts=False).reset_index(drop=True)

print(f"  Edges : {len(roads):,}")
print(f"  CRS   : {roads.crs}")
print(f"  Types : {roads.geom_type.value_counts().to_dict()}")

roads.to_file(OUTFILE, driver="GeoJSON")
print(f"\nSaved -> {OUTFILE}")
