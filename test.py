# import requests

# def get_bounding_box(city_name):
#     url = f'https://nominatim.openstreetmap.org/search'
#     params = {
#         'q': city_name,
#         'format': 'json',
#         'addressdetails': 1,
#         'limit': 1
#     }
#     response = requests.get(url, params=params)
#     print(response)
#     # data = response.json()
#     # if data:
#     #     # Extract bounding box from the response
#     #     bbox = data[0].get('boundingbox')
#     #     if bbox:
#     #         return tuple(map(float, bbox))
#     return None

# # Get bounding box for Třebíč
# bounding_box = get_bounding_box('Třebíč, Czech Republic')
# if bounding_box:
#     print(f'Bounding Box: {bounding_box}')
# else:
#     print('Bounding box not found.')
# import osmium
# import geopandas as gpd
# from shapely.geometry import shape
# import matplotlib.pyplot as plt

# class AreaHandler(osmium.SimpleHandler):
#     def __init__(self):
#         super(AreaHandler, self).__init__()
#         self.geofactory = osmium.geom.WKBFactory()
#         self.geometries = []

#     def area(self, a):
#         geometry = self.geofactory.create_multipolygon(a)
#         if geometry:
#             shapely_geom = shape(geometry)
#             self.geometries.append(shapely_geom)

# # Apply handler to an OSM file
# handler = AreaHandler()
# handler.apply_file("output_trebic.osm.pbf")

# # Convert to GeoDataFrame
# gdf = gpd.GeoDataFrame(geometry=handler.geometries)

# # Plot
# gdf.plot()
# plt.title("Geometries from OSM")
# plt.show()

# get polygon of city
import osmnx as ox
import osmium
import subprocess

# Step 1: Get the polygon of the city using osmnx
polygon_gdf = ox.geocode_to_gdf('Třebíč, Czech Republic')
# Save the polygon as a GeoJSON file (osmium accepts GeoJSON format)
polygon_gdf.to_file("polygon.geojson", driver="GeoJSON")

# # Step 2: Use osmium to extract data inside the polygon from an OSM file
# # Input OSM file (change this to the path of your OSM file)
input_osm_file = "czech-republic-latest.osm.pbf"
output_osm_file = "test.osm.pbf"

# Osmium extract command to cut the polygon
command = [
    "osmium", "extract",
    "-p", polygon_gdf,  # Polygon file in GeoJSON format
    "-o", output_osm_file,    # Output file
    input_osm_file            # Input OSM file
]

# Execute the command
subprocess.run(command)
# import time
# import osmnx as ox
# import geopandas as gpd
# import subprocess
# from shapely.geometry import Polygon
# city_name = "Třebíč, Czech Republic"
# polygon_gdf = ox.geocode_to_gdf(city_name)

# start_time = time.time()  # Record start time
       

# # Load the extracted OSM data (using GeoPandas)
# osm_gdf = gpd.read_file("trebic.osm.pbf")

# # Clip the geometries to the exact boundary of the polygon
# clipped_gdf = gpd.clip(osm_gdf, polygon_gdf)

# # Step 4: Save the clipped data to a new GeoJSON file
# clipped_gdf.to_file("clipped_output.geojson", driver="GeoJSON")

# end_time = time.time()  # Record end time
# elapsed_time = end_time - start_time  # Calculate elapsed time
# print(f"Elapsed time gdf: {elapsed_time * 1000:.5f} ms")

# import osmnx as ox
# import geopandas as gpd
# import subprocess
# from shapely.geometry import Polygon

# # Step 1: Get the polygon of the city using osmnx
# city_name = "Třebíč, Czech Republic"
# polygon_gdf = ox.geocode_to_gdf(city_name)

# # Save the polygon as a GeoJSON file (osmium accepts GeoJSON format)
# polygon_gdf.to_file("polygon.geojson", driver="GeoJSON")

# # Step 2: Use osmium to extract data inside the polygon from an OSM file
# # Input OSM file (change this to the path of your OSM file)
# input_osm_file = "czech-republic-latest.osm.pbf"
# output_osm_file = "trebic.osm.pbf"

# # Osmium extract command to cut the polygon
# command = [
#     "osmium", "extract",
#     "-p", "polygon.geojson",  # Polygon file in GeoJSON format
#     "-o", output_osm_file,    # Output file
#     input_osm_file            # Input OSM file
# ]

# # Execute the command
# subprocess.run(command)

# # # Step 3: Post-process to clip the geometries exactly to the polygon

# # # Load the extracted OSM data (using GeoPandas)
# # osm_gdf = gpd.read_file(output_osm_file)

# # # Clip the geometries to the exact boundary of the polygon

# # # Step 4: Save the clipped data to a new GeoJSON file
# # clipped_gdf.to_file("clipped_output.geojson", driver="GeoJSON")




# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.patches import Polygon, PathPatch
# from matplotlib.path import Path

# # Define your polygons as numpy arrays
# num1 = np.array([[1, 1], [1, 4], [4, 4], [4, 1]])  # Boundary polygon
# num2 = np.array([[2, 2], [2, 5], [5, 5], [5, 2]])  # Object polygon

# # Create a figure and axis
# fig, ax = plt.subplots()

# # Plot the boundary polygon (num1) with transparency
# poly1 = Polygon(num1, closed=True, facecolor='none', edgecolor='black', linewidth=2, alpha=0.5)
# ax.add_patch(poly1)

# # Create a PathPatch for num2
# path_num2 = Path(num2, closed=True)
# patch_num2 = PathPatch(path_num2, facecolor='blue', edgecolor='blue', alpha=1)

# # Set the clipping path to num1
# patch_num2.set_clip_path(poly1)

# # Add the clipped patch for num2
# ax.add_patch(patch_num2)

# # Set the limits and aspect
# ax.set_xlim(0, 6)
# ax.set_ylim(0, 6)
# ax.set_aspect('equal', adjustable='box')

# # Set the background color to white
# fig.patch.set_facecolor('white')

# # Show the plot
# plt.show()



# import matplotlib.pyplot as plt
# from shapely.geometry import Polygon

# # Define your boundary polygon (polygon1)
# boundary_coords = [(1, 1), (5, 1), (5, 5), (1, 5)]
# polygon1 = Polygon(boundary_coords)

# # Define some red polygons
# red_polygons_coords = [
#     [(2, 2), (3, 2), (3, 3), (2, 3)],  # Inside
#     [(4, 4), (6, 4), (6, 6), (4, 6)],  # Outside
#     [(0, 0), (1, 0), (1, 1), (0, 1)],  # Outside
# ]

# # Create Shapely polygons for red polygons
# red_polygons = [Polygon(coords) for coords in red_polygons_coords]

# # Create a figure and axis
# fig, ax = plt.subplots()

# # Fill the entire plot with white
# ax.set_xlim(0, 7)
# ax.set_ylim(0, 7)
# ax.set_facecolor('white')

# # Create a larger polygon for the entire area
# outer_polygon = Polygon([(0, 0), (7, 0), (7, 7), (0, 7)])
# mask_area = outer_polygon.difference(polygon1)

# if not mask_area.is_empty:
#     x, y = mask_area.exterior.xy
#     ax.fill(x, y, color='white')

# # Overlay the red polygons that intersect with polygon1
# for red_poly in red_polygons:
#     if polygon1.intersects(red_poly):
#         intersection = polygon1.intersection(red_poly)
#         # Check if the intersection is a Polygon
#         if intersection.is_empty:
#             continue
#         if intersection.geom_type == 'Polygon':
#             x, y = intersection.exterior.xy
#             ax.fill(x, y, color='red', alpha=0.5)  # Red with transparency
#         elif intersection.geom_type == 'MultiPolygon':
#             for poly in intersection:
#                 x, y = poly.exterior.xy
#                 ax.fill(x, y, color='red', alpha=0.5)  # Red with transparency

# # Set aspect ratio
# ax.set_aspect('equal')

# plt.show()
# import geopandas as gpd
# from shapely.geometry import Polygon, MultiPolygon
# import matplotlib.pyplot as plt

# # Create the big polygon (whole area)
# big_polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

# # Create the smaller polygon (hole)
# small_polygon = Polygon([(0.3, 0.3), (0.7, 0.3), (0.7, 0.7), (0.3, 0.7)])
# small_polygon2 = Polygon([(0.4, 0.4), (0.6, 0.4), (0.8, 0.9), (0.4, 0.6)])

# # Create the difference (resulting in a MultiPolygon)
# result_polygon = big_polygon.difference(small_polygon)

# # Ensure the result is a MultiPolygon
# if isinstance(result_polygon, Polygon):
#     result_polygon = MultiPolygon([result_polygon])

# # Create a GeoDataFrame
# gdf = gpd.GeoDataFrame(geometry=[result_polygon])
# gdf2 = gpd.GeoDataFrame(geometry=[small_polygon2])

# # Plot the MultiPolygon
# fig, ax = plt.subplots()
# gdf2.plot(ax=ax,color="blue")
# gdf.boundary.plot(ax=ax, color='blue')  # Only plot the boundary
# gdf.fillna(0).plot(ax=ax, color='white', alpha=1)  # Fill the outer polygon
# # Set limits to zoom in on the hole area
# ax.set_xlim(0.2, 0.8)  # Adjust these values for zooming
# ax.set_ylim(0.2, 0.8)  # Adjust these values for zooming
# ax.set_aspect('equal')

# plt.show()
