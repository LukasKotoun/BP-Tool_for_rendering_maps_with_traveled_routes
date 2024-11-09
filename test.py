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

# # get polygon of city
# import osmnx as ox
# import osmium
# import subprocess

# # Step 1: Get the polygon of the city using osmnx
# polygon_gdf = ox.geocode_to_gdf('Třebíč, Czech Republic')
# # Save the polygon as a GeoJSON file (osmium accepts GeoJSON format)
# polygon_gdf.to_file("polygon.geojson", driver="GeoJSON")

# # # Step 2: Use osmium to extract data inside the polygon from an OSM file
# # # Input OSM file (change this to the path of your OSM file)
# input_osm_file = "czech-republic-latest.osm.pbf"
# output_osm_file = "test.osm.pbf"

# # Osmium extract command to cut the polygon
# command = [
#     "osmium", "extract",
#     "-p", polygon_gdf,  # Polygon file in GeoJSON format
#     "-o", output_osm_file,    # Output file
#     input_osm_file            # Input OSM file
# ]

# # Execute the command
# subprocess.run(command)
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

# # plt.show()
# import geopandas as gpd
# import matplotlib.pyplot as plt
# from shapely.geometry import LineString, Polygon

# # Sample data: create a GeoDataFrame with polygons
# data = {
#     'geometry': [
#         Polygon([(1, 1), (1, 2), (2, 2), (2, 1)]),  # Sample polygon 1
#         Polygon([(2, 2), (2, 3), (3, 3), (3, 2)])   # Sample polygon 2
#     ]
# }
# gdf_polygons = gpd.GeoDataFrame(data)

# # Convert polygons to lines
# def polygon_to_lines(geom):
#     # Start with the exterior
#     lines = [LineString(geom.exterior.coords)]
#     # Add each interior ring (if needed)
#     for interior in geom.interiors:
#         lines.append(LineString(interior.coords))
#     return lines

# # Apply the function to convert polygons to lines
# gdf_lines = gdf_polygons.copy()
# gdf_lines['geometry'] = gdf_lines['geometry'].apply(polygon_to_lines)

# # Flatten the GeoDataFrame to get one line per row
# gdf_lines = gdf_lines.explode(column='geometry', ignore_index=True)

# # Set up the plot
# fig, ax = plt.subplots(figsize=(8, 6))

# # Plot the original polygons
# gdf_polygons.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5, label='Polygons')

# # Plot the converted lines
# gdf_lines.plot(ax=ax, color='red', linewidth=2, label='Lines')

# # Add titles and labels
# ax.set_title('Polygons and Their Converted Lines')
# ax.set_xlabel('X Coordinate')
# ax.set_ylabel('Y Coordinate')
# ax.legend()

# # Set limits for better visibility
# ax.set_xlim(0, 4)
# ax.set_ylim(0, 4)
# plt.grid()
# plt.gca().set_aspect('equal', adjustable='box')  # Maintain aspect ratio
# plt.show()

#@time_measurement_decorator("spliting")
# def split_lines_into_segments(gdf, segment_length):
#     """
#     Split each LineString in a GeoDataFrame into segments of a specified length.

#     Parameters:
#         gdf (GeoDataFrame): GeoDataFrame containing LineString geometries.
#         segment_length (float): Desired length of each segment.

#     Returns:
#         GeoDataFrame: A GeoDataFrame containing the resulting segments.
#     """
#     line_segments = []
#     for idx, row in gdf.iterrows():
#         line = row.geometry  # Get the LineString geometry
#         total_length = line.length

#         # Calculate the number of segments
#         num_segments = int(total_length // segment_length)

#         # Generate equally spaced distances along the line
#         distances = np.linspace(0, total_length, num_segments + 1)
        
#         # Create segments based on calculated distances
#         segments = [line.interpolate(distance) for distance in distances]
#         # Create LineString segments, skipping every second segment
#         for i in range(0, num_segments, 2):

#             segment = LineString([segments[i], segments[i + 1]])
#             segment_attributes = row.drop(labels='geometry').to_dict()
#             segment_attributes['geometry'] = segment
#             line_segments.append(segment_attributes)
#         # Timing end
        

#     # Create a GeoDataFrame from the list of line segments
#     segments_gdf = gpd.GeoDataFrame(line_segments, crs="EPSG:4326")
#     return segments_gdf     


# from shapely.geometry import LineString
# import numpy as np
# import matplotlib.pyplot as plt
# import time


# def split_line_into_segments(line, segment_length):
#     # Calculate total length of the line
#     total_length = line.length
#     # Calculate the number of segments
#     num_segments = int(total_length // segment_length)
#     # Generate equally spaced distances along the line
#     distances = np.linspace(0, total_length, num_segments + 1)
#     time_sd = time.time() 
#     # Create segments based on calculated distances
#     segments = [line.interpolate(distance) for distance in distances]
    
#     # Create LineString segments
#     line_segments = []
#     for i in range(0,num_segments,2):
#         segment = LineString([segments[i], segments[i + 1]])
#         line_segments.append(segment)

#     return line_segments
# time_sd = time.time() 

# # Example usage
# original_line = LineString([(0, 0), (0, 10), (3,6)])  # A vertical line from (0, 0) to (0, 10)
# segment_length = 1 # Length of each segment
# result_segments=split_line_into_segments(original_line, segment_length)
# time_end = time.time()
# print((time_end-time_sd)*1000)
# # Output the resulting segments
# # for segment in result_segments:
# #     print(segment)

# # Plotting
# plt.figure(figsize=(6, 8))
# # Plot the original line
# x_original, y_original = original_line.xy
# plt.plot(x_original, y_original, color='blue', linewidth=2, label='Original Line')

# # Plot the segments
# for segment in result_segments:
#     x_segment, y_segment = segment.xy
#     plt.plot(x_segment, y_segment, color='red', linewidth=1)

# plt.title('Line Segmentation')
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')
# plt.axhline(0, color='black',linewidth=0.5, ls='--')
# plt.axvline(0, color='black',linewidth=0.5, ls='--')
# plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
# plt.legend()
# plt.axis('equal')  # Equal scaling
# plt.savefig(f'test.pdf', format='pdf')
# plt.show()
                
                # for style_key in wanted_feature_styles:
                #     feature_style = features_category_styles.get(style_key)
                #     # assign style of concrete feature or default if is not specified for this feature
                #     assigned_styles[style_key] = feature_style if feature_style is not None else features_category_default_styles.get(style_key, self.general_default_styles[style_key]) 
import timeit
test = set({"asd"})


def my_function():
    # Simulate some work with a delay
    if(not test):
       return True
        
    # for dict_tag_key, unwanted_values in test.items():
    #    return True
    # return False         
execution_time = timeit.timeit(my_function, number=90000000)  # Run the function 100 times
print(f"Execution time for 100 runs: {execution_time:.6f} seconds")
