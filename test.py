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

# @time_measurement_decorator("spliting")
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
# import timeit
# test = set({"asd"})


# def my_function():
#     # Simulate some work with a delay
#     if(not test):
#        return True

#     # for dict_tag_key, unwanted_values in test.items():
#     #    return True
#     # return False
# execution_time = timeit.timeit(my_function, number=90000000)  # Run the function 100 times
# print(f"Execution time for 100 runs: {execution_time:.6f} seconds")
# import matplotlib.pyplot as plt
# import matplotlib.patheffects as PathEffects
# import numpy as np

# if 1:
#     plt.figure(1, figsize=(8, 3))
#     ax1 = plt.subplot(131)
#     ax1.imshow([[1, 2], [2, 3]])
#     txt = ax1.annotate("test", (1., 1.), (0., 0),
#                        arrowprops=dict(arrowstyle="->",
#                                        connectionstyle="angle3", lw=2),
#                        size=20, ha="center", path_effects=[PathEffects.withStroke(linewidth=3,
#                                                                                   foreground="w")])
#     txt.arrow_patch.set_path_effects([
#         PathEffects.Stroke(linewidth=25, foreground="w"),
#         PathEffects.Normal()])

#     ax1.grid(True, linestyle="-")

#     pe = [PathEffects.withStroke(linewidth=23,
#                                  foreground="w")]
#     for l in ax1.get_xgridlines() + ax1.get_ygridlines():
#         l.set_path_effects(pe)

#     ax2 = plt.subplot(132)
#     arr = np.arange(25).reshape((5, 5))
#     ax2.imshow(arr)
#     cntr = ax2.contour(arr, colors="k")

#     plt.setp(cntr.collections, path_effects=[
#         PathEffects.withStroke(linewidth=23, foreground="w")])

#     clbls = ax2.clabel(cntr, fmt="%2.0f", use_clabeltext=True)
#     plt.setp(clbls, path_effects=[
#         PathEffects.withStroke(linewidth=12, foreground="w")])

#     # shadow as a path effect
#     ax3 = plt.subplot(133)
#     p1, = ax3.plot([0, 1], [0, 1])
#     leg = ax3.legend([p1], ["Line 1"], fancybox=True, loc=2)
#     leg.legendPatch.set_path_effects([PathEffects.withSimplePatchShadow()])

# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.colors import to_rgba

# def generate_shades_of_color(base_color, min_factor=0, max_factor=1, num_shades=5):
#     """
#     Generate a range of shades from a base color by adjusting the brightness.

#     Parameters:
#     - base_color: The base color in any valid Matplotlib color format (e.g., 'red', '#FF0000', or RGB tuple).
#     - min_factor: The minimum factor for the brightness (0.0 is completely dark, 1.0 is original color).
#     - max_factor: The maximum factor for the brightness (1.0 is the original color, values > 1.0 are brighter).
#     - num_shades: The number of shades to generate in the range.

#     Returns:
#     - A list of colors representing different shades of the base color.
#     """
#     rgba = to_rgba(())
#     colors = []
#     for i in np.linspace(max_factor, min_factor , num_shades):
#         #scale all components of color by factor except alpha
#         shaded_color = tuple([i * c if idx < 3 else c for idx, c in enumerate(rgba)])
#         colors.append(shaded_color)
#     return colors

# # Example usage
# base_color = ''  # Can be any valid color (name, hex, or RGB)
# shades = generate_shades_of_color(base_color, min_factor=0.3, max_factor=0.8, num_shades=1)
# print(shades)
# # Display the generated shades
# fig, ax = plt.subplots(figsize=(8, 1))
# for i, color in enumerate(shades):
#     ax.add_patch(plt.Rectangle((i / len(shades), 0), 1 / len(shades), 1, color=color))

# ax.set_xlim(0, 1)
# ax.set_ylim(0, 1)
# ax.set_axis_off()
# plt.show()

# import matplotlib.pyplot as plt
# from matplotlib.patches import Polygon
# from shapely.geometry import LineString, Polygon

# # Define a line (using Shapely)
# line = LineString([(2, 6), (8, 6)])
# # line = LineString([(2, 2), (8, 2)])

# # Define a polygon (using Shapely)
# polygon = Polygon([(0, 0), (10, 0), (10, 10), (5,6.01), (0, 10)])

# clipped_line = line.intersection(polygon)
# # is_within = line.within(polygon)
# is_within = polygon.contains(line)
# print(is_within)
# # Plotting
# fig, ax = plt.subplots(figsize=(8, 6))

# # Plot the line
# x_line, y_line = line.xy
# ax.plot(x_line, y_line, color='blue', linewidth=2, label='Line')

# # Plot the polygon
# x_poly, y_poly = polygon.exterior.xy
# ax.fill(x_poly, y_poly, color='orange', alpha=0.5, label='Polygon')

# # Add legend and labels
# ax.legend()
# ax.set_title("Line and Polygon Plot")
# ax.set_xlabel("X")
# ax.set_ylabel("Y")
# ax.grid(True)

# # Display the plot
# plt.show()
# ! data asigning
# import geopandas as gpd
# from shapely.geometry import Point

# # Example: Create a GeoDataFrame
# data = {
#     'id': [1, 2, 3, 4],
#     'geometry': [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)],
#     'value': [10, 20, None, 40]  # Some rows have missing values
# }
# gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

# # Print the original GeoDataFrame
# print("Original GeoDataFrame:")
# print(gdf)

# # Filter rows (e.g., where 'id' is greater than 2)
# filtered_rows = gdf['id'] > 2

# # Dictionary with column names and values to assign
# new_values = {
#     'value': 100,  # Assign 100 to the 'value' column
#     'new_column': 'new_value',  # Assign 'new_value' to the 'new_column' column
#     'another_column': 123  # Assign 123 to the 'another_column' column
# }
# gdf.loc[filtered_rows, list(new_values.keys())] = list(new_values.values())
# print("\nUpdated GeoDataFrame:")
# print(gdf)

# filtered_rows = gdf['id'] > 3
# # Assign the dictionary values to the filtered rows
# new_values = {
#     'value': 10,  # Assign 100 to the 'value' column
#     'new_column': 'new_valdue',  # Assign 'new_value' to the 'new_column' column
#     'another_column': None  # Assign 123 to the 'another_column' column
# }
# gdf.loc[filtered_rows, list(new_values.keys())] = list(new_values.values())

# # Print the updated GeoDataFrame
# print("\nUpdated GeoDataFrame:")
# print(gdf)


#! filter creating
# import geopandas as gpd
# import pandas as pd
# from shapely.geometry import Point
# import numpy as np

# # Example: Create a GeoDataFrame
# data = {
#     'id': ["1", "2", "3", "4"],
#     'geometry': [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)],
#     'value': ["10", "20", np.nan, "40"],  # Some rows have missing values
#     'category': ['A', 'B', 'C', 'A']
# }
# gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

# # Print the original GeoDataFrame
# print("Original GeoDataFrame:")
# print(gdf)

# #! can filter only string values
# # Define the list of tuples for filtering
# filter_conditions = [
#     ('value', ''),
#     ('category', 'C'),
#     ('id', '~2'),
#     ('value', '~40')
# ]

# # Function to create a filter based on the list of tuples
# def create_filter(gdf, conditions):
#     """
#     Creates a filter for a GeoDataFrame based on a list of tuples.

#     Parameters:
#         gdf (GeoDataFrame): The GeoDataFrame to filter.
#         conditions (list of tuples): List of (column_name, column_value) tuples.

#     Returns:
#         pd.Series: A boolean mask for filtering the GeoDataFrame.
#     """
#     filter_mask = pd.Series([True] * len(gdf))  # Start with all rows included

#     for column_name, column_value in conditions:
#         if column_value == "":  # Not NA
#             filter_mask &= gdf[column_name].notna()
#         elif column_value.startswith("~"):  # Not equal to value after ~
#             if column_value == "~":  # Column should be NA
#                 filter_mask &= gdf[column_name].isna()
#             else:  # Column should not equal the value after ~
#                 print((gdf[column_name] != column_value[1:]))
#                 filter_mask &= (gdf[column_name] != column_value[1:])
#         else:  # Column should equal the value
#             filter_mask &= (gdf[column_name] == column_value)

#     return filter_mask

# # Apply the filter
# filter_mask = create_filter(gdf, filter_conditions)
# print(filter_mask)
# filtered_gdf = gdf[filter_mask]
# # Print the filtered GeoDataFrame
# print("\nFiltered GeoDataFrame:")
# print(filtered_gdf)
from enum import Enum

#! data testing


class StyleKey(Enum):
    COLOR = 1
    ALPHA = 2
    ZINDEX = 3
    LINEWIDTH = 4
    LINESTYLE = 5
    EDGE_COLOR = 7  # nastavit asi jako text outline width a color
    EDGE_WIDTH_RATIO = 11
    BRIDGE_COLOR = 9
    BRIDGE_WIDTH_RATIO = 12
    BRIDGE_EDGE_COLOR = 10
    FONT_SIZE = 6
    OUTLINE_WIDTH = 8
    ICON = 16
    ICON_COLOR = 13
    ICON_EDGE = 14
    ICON_SIZE = 15
    DEFAULT = 17
    ZOOM = 18
class StyleType(Enum):
    DEFAULT = 17
    ZOOM = 18

# highway_styles = {
#     [('highway', 'motorway')]: {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.LINEWIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"},
#     [('highway', 'trunk')]: {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6, StyleKey.LINEWIDTH: 26, StyleKey.EDGE_COLOR: "#E19532"},
#     [('highway', 'primary')]: {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5, StyleKey.LINEWIDTH: 22, StyleKey.EDGE_COLOR: "#E19532"},
#     [('highway', 'secondary')]: {StyleKey.COLOR: '#F7ED60', StyleKey.ZINDEX: 4, StyleKey.LINEWIDTH: 20, StyleKey.EDGE_COLOR: "#c1b42a"},
#     [('highway', 'tertiary')]: {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.LINEWIDTH: 16},
#     [('highway', 'unclassified')]: {StyleKey.COLOR: '#FFFFFF'},
#     [('highway', 'road')]: {StyleKey.COLOR: '#FFFFFF'},
#     [('highway', 'footway')]: {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF"},
#     [('highway', 'steps')]: {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None},
#     [('highway', 'path')]: {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF"},
#     [('highway', 'residential')]: {StyleKey.COLOR: '#FFFFFF'}
# }

# railway_styles = {
#     [('railway', 'rail')]: { StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 10,
#             StyleKey.BRIDGE_EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_COLOR: "#FFFFFF",
#             StyleKey.EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_WIDTH_RATIO: 1.7, StyleKey.LINESTYLE: (0, (5, 5))},
#     [('railway', 'tram')]: {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 10, StyleKey.LINEWIDTH: 4, StyleKey.ALPHA: 0.6},
#     [('railway', 'tram_stop')]: {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4},
# }

    # **highway_styles,
    # **railway_styles,


FeatureStyles = dict[StyleKey, str | int | float]
FeatureStyleZooms = dict[str, FeatureStyles]
FeatureStyleDynamics = dict[StyleType, FeatureStyles | FeatureStyleZooms]
CategoryFilters = list[tuple([str, str])]
FeatureCategoriesStyles = tuple[CategoryFilters, FeatureStyles]
FeatureCategoriesStylesDynamic = tuple[CategoryFilters, FeatureStyleDynamics]



# StyleDict = Dict[str, Dict[str, Any]]  # e.g., StyleKey.DEFAULT, StyleKey.ZOOM
# StyleEntry = Tuple[List[Tuple[str, str]] , StyleDict]  # List of tuples for categories, and a dict for styles


WAYS_STYLES  = [
    ([('waterway', '')], {StyleType.DEFAULT: {StyleKey.COLOR: '#8FB8DB', StyleKey.LINEWIDTH: 8, StyleKey.ZINDEX: 0},
                          StyleType.ZOOM: {'4-5': {StyleKey.LINEWIDTH: 4}, '6-7': {StyleKey.LINEWIDTH: 6}, '8-9': {StyleKey.LINEWIDTH: 8}}}),
    ([('highway', '')], {StyleType.DEFAULT: {StyleKey.COLOR: '#FFFFFF',
                         StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D",
                         StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 8, StyleKey.EDGE_COLOR: "#B0A78D"}, 
                         StyleType.ZOOM: {'4-5': {StyleKey.LINEWIDTH: 4}, '6-7': {StyleKey.LINEWIDTH: 6}, '8-9': {StyleKey.LINEWIDTH: 8}}}),
    ([('railway', '')], {StyleType.DEFAULT:{StyleKey.COLOR: '#FFFFFF',
     StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 8}, StyleType.ZOOM:{'4-5': {StyleKey.LINEWIDTH: 4}, '6-7': {StyleKey.LINEWIDTH: 6}, '8-9': {StyleKey.LINEWIDTH: 8}}}),
]


WAYS_STYLES: FeatureCategoriesStyles  = [
    ([('waterway', '')], {StyleKey.COLOR: '#8FB8DB', StyleKey.LINEWIDTH: 8, StyleKey.ZINDEX: 0}),
    ([('highway', '')], {StyleKey.COLOR: '#FFFFFF', StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D",
                         StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 8, StyleKey.EDGE_COLOR: "#B0A78D"}),
    ([('railway', '')], {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 8}),
]


print(WAYS_STYLES)
