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

# @time_measurement("spliting")
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
#     'value': [10, 20, None, 40]
# }
# gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

# # Print the original GeoDataFrame
# print("Original GeoDataFrame:")
# print(gdf)

# # Define the styles dictionary with mixed types
# styles = {
#     'width_ratio': 0.4,  # Float
#     'linestyle': (0, (5, 5)),  # Tuple
#     'color': 'red',  # String
#     'priority': 1  # Integer
# }

# # Define the filtered rows (e.g., where 'id' is greater than 2)
# filtered_rows = gdf['id'] > 2

# # Assign styles to the filtered rows
# for key, value in styles.items():
#     if isinstance(value, (str, int, float)):  # Handle strings, integers, and floats
#         gdf.loc[filtered_rows, key] = value
#     elif isinstance(value, tuple):  # Handle tuples
#         gdf.loc[filtered_rows, key] = [value] * filtered_rows.sum()

# # Print the updated GeoDataFrame
# print("\nUpdated GeoDataFrame:")
# print(gdf)

# import numpy as np
# import pandas as pd


# df = pd.DataFrame({'team': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
#                    'points': [18, 22, 19, 14, 14, 11, 20, 28],
#                    'assists': [5, 7, 7, 9, 12, 9, 9, 4]})
# t = (1,(5,4))
# df['points_assists'] = [t]*len(df)


# import geopandas as gpd
# import matplotlib.pyplot as plt
# from shapely.geometry import LineString, Polygon, LinearRing
# import numpy as np

# def determine_side(geom: Polygon, splitter: LineString) -> str:
#     """
#     Given a polygon (geom) that was produced by splitting with a LineString (splitter),
#     determine whether the geom lies to the left or right of the splitter.

#     The method:
#       1. Extracts the first and last point of the splitter (p0 and pN).
#       2. Obtains a representative point from the geom.
#       3. Constructs a LinearRing using [p0, aside_point, pN, p0].
#       4. Uses ring.is_ccw:
#          - If True, the aside point is to the left of the directed splitter.
#          - If False, it is to the right.

#     Parameters:
#       geom: A Polygon from the splitting result.
#       splitter: The LineString that was used to split the original geometry.

#     Returns:
#       A string "left" or "right" indicating on which side of the splitter the geom lies.
#     """
#     # 1. Get the endpoints of the splitter.
#     coords = list(splitter.coords)
#     p0 = coords[0]
#     pN = coords[-1]

#     # 2. Get a representative point from the geometry.
#     # Using representative_point() ensures the point lies within the geom.
#     aside_point = geom.representative_point()

#     # 3. Form a LinearRing using the splitter endpoints and the aside point.
#     # The order of points is important. Here we use [p0, aside_point, pN, p0].
#     ring_coords = [p0, (aside_point.x, aside_point.y), pN, p0]
#     ring = LinearRing(ring_coords)

#     # 4. Determine side based on the ring orientation.
#     # If ring.is_ccw is True, the aside_point is to the left of the directed line.
#     if ring.is_ccw:
#         return "left"
#     else:
#         return "right"

# # =============================================================================
# # Example Usage
# # =============================================================================

# # Define a splitting line (directed from its first to its last coordinate)
# # splitter = LineString([(0, 0), (10, 0)])
# splitter = LineString([(10, 0), (0, 0)])

# # Create two polygons that result from splitting an area by the splitter.
# # In this example, one polygon lies above the splitter and one below.
# poly_above = Polygon([(-1, 1), (11, 1), (11, 5), (-1, 5), (-1, 1)])
# poly_below = Polygon([(-1, -5), (11, -5), (11, -1), (-1, -1), (-1, -5)])

# # Determine on which side each polygon lies relative to the splitter.
# side_above = determine_side(poly_above, splitter)
# side_below = determine_side(poly_below, splitter)

# print("poly_above is on the", side_above, "side of the splitter")
# print("poly_below is on the", side_below, "side of the splitter")

# # =============================================================================
# # Plotting the Result
# # =============================================================================

# # Convert the geometries to GeoDataFrames for plotting.
# gdf_above = gpd.GeoDataFrame(geometry=[poly_above], crs="EPSG:4326")
# gdf_below = gpd.GeoDataFrame(geometry=[poly_below], crs="EPSG:4326")
# gdf_splitter = gpd.GeoDataFrame(geometry=[splitter], crs="EPSG:4326")

# fig, ax = plt.subplots(figsize=(8, 6))
# gdf_above.plot(ax=ax, color="lightgreen", edgecolor="black", label=f"Above ({side_above})")
# gdf_below.plot(ax=ax, color="lightcoral", edgecolor="black", label=f"Below ({side_below})")
# gdf_splitter.plot(ax=ax, color="blue", linewidth=2, label="Splitter")
# ax.set_title("Determining the Side Relative to the Splitter")
# ax.legend()
# ax.set_axis_off()
# plt.show()


# import geopandas as gpd
# import matplotlib.pyplot as plt
# from shapely.geometry import Polygon, LineString, LinearRing
# from shapely.ops import split
# import numpy as np

# def determine_side(geom: Polygon, splitter: LineString) -> str:
#     """
#     Given a polygon (resulting from a split) and the splitting line,
#     determine whether the polygon lies to the left or right of the splitter.

#     The splitter’s direction is defined from its first coordinate (p0) to its last (pN).
#     We form a LinearRing using [p0, aside_point, pN, p0] and use its orientation:
#       - If ring.is_ccw is True, the aside point is on the left side.
#       - Otherwise, it is on the right.

#     Parameters:
#       geom: The polygon (a Shapely Polygon) to test.
#       splitter: The splitting line (a Shapely LineString).

#     Returns:
#       A string: "left" or "right".
#     """
#     # 1. Get the endpoints of the splitter.
#     coords = list(splitter.coords)
#     p0 = np.array(coords[0])
#     pN = np.array(coords[-1])

#     # 2. Obtain a representative point from the geometry
#     #    (guaranteed to lie within the polygon).
#     aside_point = geom.representative_point()

#     # 3. Form a LinearRing using [p0, aside_point, pN, p0].
#     ring_coords = [tuple(p0), (aside_point.x, aside_point.y), tuple(pN), tuple(p0)]
#     ring = LinearRing(ring_coords)

#     # 4. Check the orientation:
#     #    If ring.is_ccw is True, the aside_point lies to the left of the directed splitter.
#     if ring.is_ccw:
#         return "left"
#     else:
#         return "right"

# # ------------------------------------------------------------------
# # Example: Create a U‑shaped polygon that will be split into three pieces.
# # ------------------------------------------------------------------
# # The U‑shaped polygon is defined by the following coordinates.
# # (Imagine a U shape that goes from (0,0) → (5,0) → (5,4) → (4,4) → (4,2)
# #  → (1,2) → (1,4) → (0,4) → back to (0,0).)
# u_polygon_coords = [(0,0), (5,0), (5,4), (4,4), (4,2), (1,2), (1,4), (0,4), (0,0)]
# u_polygon = Polygon(u_polygon_coords)

# # Define a horizontal splitting line that cuts through the U shape.
# # We choose a line from (-1,3) to (6,3) so that it crosses the U-shape in several points.
# # splitter = LineString([(-1, 3), (6, 3)])
# splitter = LineString([(6, 3),(-1, 3) ])

# # ------------------------------------------------------------------
# # Split the polygon using the splitter.
# # ------------------------------------------------------------------
# split_result = split(u_polygon, splitter)

# # Print how many polygons resulted from the split.
# print("Number of polygons after splitting:", len(split_result.geoms))

# # For each resulting polygon, determine whether it is to the left or right of the splitter.
# for i, poly in enumerate(split_result.geoms):
#     print(poly)
#     side = determine_side(poly, splitter)
#     print(f"Polygon {i} is on the {side} side of the splitter.")

# # ------------------------------------------------------------------
# # Plotting the original polygon, the splitter, and the resulting pieces.
# # ------------------------------------------------------------------
# # Create GeoDataFrames for easier plotting.
# gdf_u = gpd.GeoDataFrame(geometry=[u_polygon], crs="EPSG:4326")
# gdf_split = gpd.GeoDataFrame(geometry=list(split_result.geoms), crs="EPSG:4326")
# gdf_splitter = gpd.GeoDataFrame(geometry=[splitter], crs="EPSG:4326")
# fig, ax = plt.subplots(figsize=(8, 8))

# # Plot the original U-shaped polygon (as an outline).
# gdf_u.boundary.plot(ax=ax, color="black", linestyle="--", label="Original U-Polygon")
# # Plot the split pieces with different colors.
# gdf_split.plot(ax=ax, cmap="Set2", edgecolor="black", alpha=0.7, legend=True)
# # Plot the splitter.
# gdf_splitter.plot(ax=ax, color="red", linewidth=2, label="Splitter")

# ax.set_title("Splitting a U-shaped Polygon into 3 Parts\nand Determining Side Relative to the Splitter")
# ax.set_axis_off()
# plt.legend()
# plt.show()


from shapely.geometry import mapping
from shapely.geometry import Polygon, LineString
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import ListedColormap

from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, LineString, MultiLineString
from shapely.ops import split, linemerge
polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]).reverse()
# splitters = [LineString([(2,1), (1,1), (1,4)]), LineString([(2, 5), (5, 7), (7, 7)]), LineString([(1,4), (4, 3), (2, 5)]), LineString([(1.1,4), (4, 3), (2, 5), (1.1,4)])]

# splitters = LineString([(2, 1), (2, 5), (4, 3), (2, 1)])
# splitters = splitters.reverse()
# splitters = LineString([(-1,5), (2, 1), (2, 5), (4, 3), (2.1, 1), (8, 3), (8, 2), (11, 5)])
splitters = [LineString([(-1, 5), (2, 1), (2, 5), (4, 3), (2.1, 1), (8, 3), (8, 2), (11, 5)]).reverse(),  # down is watter
             LineString([(7, 7), (8, 8), (9, 7), (7, 7)]
                        ),  # inside is watter
             LineString([(1, 7), (2, 8), (1, 9), (1, 7)])]  # inside is land

# splitters = splitters.reverse()
# if(not isinstance(splitters, LineString)):


splitters = linemerge(splitters) if isinstance(
    splitters, list) else linemerge([splitters])

print(splitters)


def ensure_opposite_orientation(polygon):
    """
    Ensure that the inner rings (holes) have the opposite orientation to the outer ring.

    Parameters:
        polygon (Polygon): The input polygon.

    Returns:
        Polygon: A new polygon with corrected inner ring orientations.
    """
    # Determine the orientation of the exterior ring
    is_exterior_ccw = polygon.exterior.is_ccw

    all_opposite = True
    # Fix the orientation of each interior ring
    fixed_interiors = []
    for interior in list(polygon.interiors):
        if interior.is_ccw == is_exterior_ccw:  # If the orientation matches the exterior, reverse it
            all_opposite = False
            fixed_interiors.append(interior.coords[::-1])
        else:
            fixed_interiors.append(interior.coords)

    if (all_opposite):
        return polygon
    return Polygon(polygon.exterior.coords, fixed_interiors)


# Create a GeoDataFrame for each geometry
polygon_gdf = gpd.GeoDataFrame(geometry=[polygon])
line_gdf = gpd.GeoDataFrame(geometry=[splitters])

# Plot
fig, ax = plt.subplots(figsize=(10, 10))

data = []
line_gdf.plot(ax=ax, color='red', linewidth=2)
splitters = list(splitters.geoms) if isinstance(
    splitters, MultiLineString) else [splitters]

for splitter in splitters:
    geometry_collection = split(polygon, splitter)
    if (len(geometry_collection.geoms) == 1):
        continue
    # check if geom is on right or left of splitter
    for geom in geometry_collection.geoms:
        print(geom)
        # if (len(geom.interiors) > 0):
        #     geom = ensure_opposite_orientation(geom)

        # získání intersection podle orinetace geomu 
        geomInter = geom.intersection(splitter)
        geomInter = linemerge(geomInter) if isinstance(
            geomInter, MultiLineString) else geomInter  # todo to function

        # získání intersection podle orinetace spliteru
        lineinter = splitter.intersection(geom)
        lineinter = linemerge(lineinter) if isinstance(
            lineinter, MultiLineString) else lineinter

        line_coords = list(geomInter.coords)
        line_coords2 = list(lineinter.coords)
        # check if orientation are same
        color = ""
        if (line_coords == line_coords2):
            if (geom.exterior.is_ccw):
                color = '#EDEDE0'  # polygon is on left side of splitter
            else:
                color = 'blue'  # polygon is on right side of splitter
        else:
            if (geom.exterior.is_ccw):  # polygon is reversed to splitter
                color = 'blue'  # polygon is on left side of splitter
            else:
                color = '#EDEDE0'  # polygon is on left side of splitter
        data.append({"geometry": geom, "color": color})

        # check if polygon is on righ or left side of splitter
        print("-------------------------------------------------")


gdf = gpd.GeoDataFrame(data, geometry="geometry")
gdf['area'] = gdf.area
# order gdf by area
gdf = gdf.sort_values(by='area', ascending=False)
print(gdf)
gdf.plot(ax=ax, color=gdf["color"])
# Customize plot
ax.set_title('Polygon and Line Plot')
plt.show()


# # Define a polygon
# polygon = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)])
# # Define a splitting line
# splitter = LineString([(2, -1), (2, 5), (2, 3), (2, -1)])

# # t = split(polygon, splitter) # ! test jestli split nevrací to vlevo ccw a v pravo normálně
# # print(t)
# from shapely.geometry import Polygon

# # Create a polygon with counter-clockwise orientation (CCW)
# polygon_ccw = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

# # Create a polygon with clockwise orientation (CW)
# polygon_cw = Polygon([(0, 0), (1, 0), (0, 1), (1, 1)])

# # Check if the polygons are CCW
# print(f"Is polygon_ccw CCW? {polygon_ccw.exterior.is_ccw}")
# print(f"Is polygon_cw CCW? {polygon_cw.exterior.is_ccw}")
# print(f"Is polygon_cw CCW? {polygon.exterior.is_ccw}")
# print(f"Is polygon_cw CCW? {polygon.reverse().exterior.is_ccw}")
# rew = t.geoms[0].intersection(splitter)
# same = t.geoms[1].intersection(splitter)
# rewPol = t.geoms[0]
# samePol = t.geoms[1]
# print(rewPol)
# print(same)

# def test(l1,l2): #! stejná orientaec kde l2 je splitter a l1 le linestring co je intersection s polygonem
#     line = l2.intersection(l1)
#     if line.is_empty or not hasattr(line, "coords"):
#         return False  # Handle empty or non-LineString cases
#     return True if line.coords[0] == l1.coords[0] and line.coords[-1] == l1.coords[-1] else False
# if(not (test(rewPol.intersection(splitter),splitter))):
#   rewPol2 = rewPol.reverse()
#   print(rewPol2)
# if(not (test(samePol.intersection(splitter),splitter))):
#   samePol2 = samePol.reverse()

# # print(samePol.equals(samePol2))
# print(rewPol.equals(rewPol2))
# # Extract first and last intersection points

# # Print results


# ! měřítko
# import matplotlib.pyplot as plt
# import numpy as np

# # === PARAMETRY MAPY ===
# scale = 25000  # Měřítko mapy (např. 1:25000 → 1 cm = 250 m)
# paper_width_cm = 21  # Šířka mapového výřezu na papíře (např. A4 na šířku = 21 cm)
# min_ratio = 0.08  # Minimální délka čáry jako % šířky mapy (8 %)
# max_ratio = 0.10  # Maximální délka čáry jako % šířky mapy (10 %)

# # === VÝPOČET OPTIMÁLNÍHO MĚŘÍTKA ===
# min_scale_length_cm = paper_width_cm * min_ratio  # Převod na cm
# max_scale_length_cm = paper_width_cm * max_ratio  # Převod na cm

# # Převod na reálnou vzdálenost (v metrech)
# min_real_length_m = min_scale_length_cm * scale / 100  # Převod na metry
# max_real_length_m = max_scale_length_cm * scale / 100  # Převod na metry

# # Zvolíme "hezkou" hodnotu měřítka (100m, 200m, 500m, 1km, 2km, 5km…)
# scale_values_m = [100, 200, 500, 1000, 2000, 5000, 10000, 20000]
# chosen_length_m = max([s for s in scale_values_m if min_real_length_m <= s <= max_real_length_m], default=1000)

# # Spočítáme odpovídající délku čáry na papíře v cm
# scale_length_cm = (chosen_length_m * 100) / scale

# # === VYKRESLENÍ MĚŘÍTKA ===
# fig, ax = plt.subplots(figsize=(paper_width_cm / 2.54, 2), dpi=300)

# # Nakreslíme černý pruh
# ax.plot([0, scale_length_cm], [0, 0], color="black", lw=8, solid_capstyle="butt")

# # Popisky na začátku a na konci
# ax.text(0, 0.5, "0", ha="center", va="bottom", fontsize=10, fontweight="bold",
#         bbox=dict(facecolor='white', edgecolor='none'))

# # Pokud je měřítko v km, zobrazíme v km, jinak v metrech
# if chosen_length_m >= 1000:
#     text_label = f"{chosen_length_m // 1000} km"
# else:
#     text_label = f"{chosen_length_m} m"

# ax.text(scale_length_cm, 0.5, text_label, ha="center", va="bottom", fontsize=10, fontweight="bold",
#         bbox=dict(facecolor='white', edgecolor='none'))

# # Skrytí os
# ax.set_xticks([])
# ax.set_yticks([])
# ax.set_frame_on(False)

# # Zobrazení
# plt.show()
