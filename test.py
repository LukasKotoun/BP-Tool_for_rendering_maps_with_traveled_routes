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


# def ensure_opposite_orientation(polygon):
#     """
#     Ensure that the inner rings (holes) have the opposite orientation to the outer ring.

#     Parameters:
#         polygon (Polygon): The input polygon.

#     Returns:
#         Polygon: A new polygon with corrected inner ring orientations.
#     """
#     # Determine the orientation of the exterior ring
#     is_exterior_ccw = polygon.exterior.is_ccw

#     all_opposite = True
#     # Fix the orientation of each interior ring
#     fixed_interiors = []
#     for interior in list(polygon.interiors):
#         if interior.is_ccw == is_exterior_ccw:  # If the orientation matches the exterior, reverse it
#             all_opposite = False
#             fixed_interiors.append(interior.coords[::-1])
#         else:
#             fixed_interiors.append(interior.coords)

#     if (all_opposite):
#         return polygon
#     return Polygon(polygon.exterior.coords, fixed_interiors)


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

# # # Zobrazení
# import numpy as np
# from enum import Enum

# # plt.show()


# class StyleKey(Enum):
#     # general
#     COLOR = 1
#     ALPHA = 2
#     ZINDEX = 3
#     # lines
#     WIDTH = 4
#     LINESTYLE = 5
#     EDGE_COLOR = 6
#     EDGE_ALPHA = 21
#     EDGE_WIDTH_RATIO = 7
#     EDGE_LINESTYLE = 8
#     #   bridges
#     BRIDGE_COLOR = 9
#     BRIDGE_WIDTH_RATIO = 10
#     BRIDGE_EDGE_COLOR = 11
#     BRIDGE_EDGE_WIDTH_RATIO = 12
#     # points
#     ICON = 13

#     # text
#     TEXT_FONT_SIZE = 14
#     TEXT_OUTLINE_WIDHT_RATIO = 16

#     # calculated - cant be set by user
#     # calculated like TEXT_FONT_SIZE * TEXT_OUTLINE_WIDHT_RATIO
#     TEXT_OUTLINE_WIDTH = 17
#     # calculated like WIDTH + WIDTH * EDGE_WIDTH_RATIO
#     EDGEWIDTH = 18
#     # calculated like
#     BRIDGE_WIDTH = 19
#     # calculated like WIDTH + WIDTH * (BRIDGE_WIDTH_RATIO * EDGE_WIDTH_RATIO) or BRIDGE_WIDTH + BRIDGE_WIDTH * BRIDGE_EDGE_WIDTH_RATIO
#     BRIDGE_EDGE_WIDTH = 20


# class StyleType(Enum):
#     DEFAULT = 1
#     ZOOM = 2


# #! Přiřazení dynamic stylů
# # highway_styles = [
# #     ([('highway', 'motorway')], {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.WIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"}),
# #     ([('highway', 'trunk')], {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6, StyleKey.WIDTH: 26, StyleKey.EDGE_COLOR: "#E19532"}),
# #     ([('highway', 'primary')], {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5, StyleKey.WIDTH: 22, StyleKey.EDGE_COLOR: "#E19532"}),
# #     ([('highway', 'secondary')], {StyleKey.COLOR: '#F7ED60', StyleKey.ZINDEX: 4, StyleKey.WIDTH: 20, StyleKey.EDGE_COLOR: "#c1b42a"}),
# #     ([('highway', 'tertiary')], {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.WIDTH: 16}),
# #     # ([('highway', 'tertiary')], {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.WIDTH: 5}),
# #     ([('highway', 'unclassified')], {StyleKey.COLOR: '#FFFFFF'}),
# #     ([('highway', 'road')], {StyleKey.COLOR: '#FFFFFF'}),
# #     ([('highway', 'footway')], {StyleKey.COLOR: '#FFFFFF', StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
# #     ([('highway', 'steps')], {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None}),
# #     ([('highway', 'path')], {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
# #     ([('highway', 'track')], {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
# #     ([('highway', 'residential')], {StyleKey.COLOR: '#FFFFFF'}),
# # ]

# # highway_styles_D = [
# #     ([('highway', 'motorway')], {StyleType.DEFAULT: {StyleKey.COLOR: '#8cd25f',
# #      StyleKey.ZINDEX: 7, StyleKey.WIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"}, StyleType.ZOOM: {}}),
# #     ([('highway', 'trunk')], {StyleType.DEFAULT: {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6,
# #      StyleKey.WIDTH: 26, StyleKey.EDGE_COLOR: "#E19532"}, StyleType.ZOOM: {"1-2": {StyleKey.EDGE_COLOR: 'asd'}, "2-8": {StyleKey.EDGE_COLOR: 'red'}, "7-14": {StyleKey.COLOR: 'blue'}}}),
# #     ([('highway', 'residential')],  {
# #      StyleType.DEFAULT: {StyleKey.EDGE_COLOR: "#E19532"}}),

# # ]


# # def convert_dynamic_to_normal(dynamic_styles, zoom_level):
# #     def check_range(range_str, zoom_level):
# #         lower_str, upper_str = range_str.split("-")
# #         lower, upper = int(lower_str), int(upper_str)
# #         if (lower > upper):
# #             lower, upper = upper, lower
# #         return lower <= zoom_level <= upper

# #     normal_styles = []
# #     for filter, styles in dynamic_styles:
# #         style_default = {}
# #         styles_filter = {}
# #         for style_type, style_values in styles.items():
# #             if style_type == StyleType.DEFAULT:
# #                 style_default = style_values
# #             elif style_type == StyleType.ZOOM:
# #                 for zoom_range, zoom_style_values in style_values.items():
# #                     if (check_range(zoom_range, zoom_level)):
# #                         styles_filter = {**zoom_style_values, **styles_filter}
# #             else:  # if styletype is not assigned
# #                 style_default = styles
# #                 break
# #         styles = {**style_default, **styles_filter}
# #         normal_styles.append((filter, styles))
# #     return normal_styles


# #     # Example Usage:
# # dict1 = {"a": 1, "b": 2, "c": 3}
# # dict2 = {"a": 2, "d": 4, "r": 5}
# # dict3 = {"a": 3, "b": 6}

# # dicts = [dict1, dict2, dict3]  # Priority: dict1 > dict2 > dict3
# # result = convert_dynamic_to_normal(highway_styles_D, 7)

# # print(result)


# def map_continuous_to_discrete(value):
#     # middle 
#     mapping = {
#         19: 0.7832305,
#         18: 0.3925486,
#         17: 0.1967345,
#         16: 0.0981350,
#         15: 0.0490022,
#         14: 0.0245145,
#         13: 0.0122572,
#         12: 0.0061528,
#         11: 0.0030862,
#         10: 0.0015295,
#         9:  0.0007648,
#         8:  0.0003824,
#         7:  0.0001920,
#         6:  0.0000958
#     }

#     # Sort by descending continuous values
#     levels = sorted(mapping.items(), key=lambda x: -x[1])
#     for i in range(len(levels) - 1):
#         higher_level, higher_value = levels[i]
#         lower_level, lower_value = levels[i + 1]

#         # Compute the threshold at 1/4 from lower to higher value
#         threshold = lower_value + (higher_value - lower_value) * 0.25

#         if value >= threshold:
#             return higher_level

#     return levels[-1][0]  # Assign lowest level if below the lowest threshold


# # Example usage
# test_values = [5, 0.3, 0.2, 0.1, 0.025, 0.0005, 0.0001,0.00000005]
# mapped_values = [map_continuous_to_discrete(v) for v in test_values]
# print(mapped_values)  # Output: [18, 16, 14, 9, 6]

# def parse_range(range_str):
#     lower_str, upper_str = range_str.split("-")
#     lower, upper = int(lower_str), int(upper_str)
#     return lower, upper

# # Example usage
# range_str = "3-7"
# lower, upper = parse_range(range_str)

# number_to_check = 4
# if lower <= number_to_check <= upper:
#     print(f"{number_to_check} is between {lower} and {upper}.")
# else:
#     print(f"{number_to_check} is not between {lower} and {upper}.")

# ! filter performance tests
# import numpy as np
# from enum import Enum

# # plt.show()


# class StyleKey(Enum):
#     # general
#     COLOR = 1
#     ALPHA = 2
#     ZINDEX = 3
#     # lines
#     WIDTH = 'width'
#     LINESTYLE = 5
#     EDGE_COLOR = 6
#     EDGE_ALPHA = 21
#     EDGE_WIDTH_RATIO = 7
#     EDGE_LINESTYLE = 8
#     #   bridges
#     BRIDGE_COLOR = 9
#     BRIDGE_WIDTH_RATIO = 10
#     BRIDGE_EDGE_COLOR = 11
#     BRIDGE_EDGE_WIDTH_RATIO = 12
#     # points
#     ICON = 13

#     # text
#     TEXT_FONT_SIZE = 14
#     TEXT_OUTLINE_WIDHT_RATIO = 16

#     # calculated - cant be set by user
#     # calculated like TEXT_FONT_SIZE * TEXT_OUTLINE_WIDHT_RATIO
#     TEXT_OUTLINE_WIDTH = 17
#     # calculated like WIDTH + WIDTH * EDGE_WIDTH_RATIO
#     EDGEWIDTH = 18
#     # calculated like
#     BRIDGE_WIDTH = 19
#     # calculated like WIDTH + WIDTH * (BRIDGE_WIDTH_RATIO * EDGE_WIDTH_RATIO) or BRIDGE_WIDTH + BRIDGE_WIDTH * BRIDGE_EDGE_WIDTH_RATIO
#     BRIDGE_EDGE_WIDTH = 20

# import time
# import numpy as np
# import pandas as pd
# import geopandas as gpd
# def create_rows_filter_OR(gdf: gpd.GeoDataFrame, conditions) -> pd.Series:

#         # todo craete function that will suport also OR - using this as AND and new function as for every call of this function use OR and remove all other filters, can also replace
#         # todo all suported conditons - name, nan ~, nonan '', [list of or values with individual ~] - [list with '' and '~' will return all rows]
#         # filter_mask = pd.Series([True] * len(gdf))
#         filter_mask = pd.Series(True, index=gdf.index)

#         for column_name, column_value in conditions:
#             if column_name not in gdf.columns:
#                 # handle missing columns
#                 if (isinstance(column_value, list)):
#                     # If any value in the list start with "~", the columns can be skipped
#                     if any(str(v).startswith("~") for v in column_value):
#                         continue
#                     else:
#                         # If none of the values start with "~", the column must exists
#                         filter_mask &= False
#                         break
#                 # not equal to value after ~ or NA
#                 elif column_value.startswith("~"):
#                     continue
#                 # column should equal the value or should not be NA (but column doesn't exist)
#                 else:
#                     filter_mask &= False
#                     break

#             else:
#                 if isinstance(column_value, list):
#                     # start with all rows excluded
#                     condition_mask = pd.Series([False] * len(gdf))
#                     if not column_value:
#                         # If the list is empty, the column should not be NA
#                         condition_mask |= gdf[column_name].notna()
#                     else:
#                         for value in column_value:
#                             if value == "":  # Not NA
#                                 condition_mask |= gdf[column_name].notna()
#                             elif value == "~":  # Column should be NA
#                                 condition_mask |= gdf[column_name].isna()
#                             # Not equal to value after ~
#                             elif value.startswith("~"):
#                                 condition_mask |= (
#                                     gdf[column_name] != value[1:])
#                             else:  # Column equal the value
#                                 condition_mask |= (gdf[column_name] == value)
#                         filter_mask &= condition_mask

#                 else:
#                     if column_value == '':  # Not NA
#                         filter_mask &= gdf[column_name].notna()
#                     elif column_value.startswith("~"):
#                         if column_value == "~":  # column should be NA
#                             filter_mask &= gdf[column_name].isna()
#                         else:  # column should not equal the value after ~
#                             filter_mask &= (
#                                 gdf[column_name] != column_value[1:])
#                     else:  # column should equal the value
#                         filter_mask &= (gdf[column_name] == column_value)
#         return filter_mask
# import numexpr

# def f(gdf, fil):

#     return gdf.eval(fil)
    
# # Create a sample GeoDataFrame with 1,000,000 rows
# # n = 1000
# # n = 60_000_000

# # n = 2000000
# # n = 3000000
# # n = 20_000_000
# n = 500_000
# # n = 100_000_000
# # Define possible values for the 'landuse' column, including some missing values (None)
# landuse_options = ['forest', 'test', pd.NA, 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
# data = {
#     StyleKey.WIDTH.value: np.random.choice(landuse_options, n),
#     'area':  np.random.choice(landuse_options, n),
#     "asd": np.random.choice(landuse_options, n),
#     "dddd": np.random.choice(landuse_options, n),
#     "sdsd": np.random.choice(landuse_options, n),
#     "sdsd2": np.random.choice(landuse_options, n),
#     "sdsd3": np.random.choice(landuse_options, n)
# }
# gdf = gpd.GeoDataFrame(data)
# query = f"{StyleKey.WIDTH} == 'test' and area == 1000"

# # # # Number of iterations for timing
# filOne = [f"{StyleKey.WIDTH} == 'test' and area == 1000", f"{StyleKey.WIDTH}.isna()", f"{StyleKey.WIDTH} == 'forest'"]
# filOne = [f"{StyleKey.WIDTH.value}.notna() and asd.notna() and dddd.notna()"]

# result_query = None
# start_time = time.time()
# for t in filOne:
#     result_query = f(gdf,t)
# query_time = (time.time() - start_time)

# filtwo = [[(StyleKey.WIDTH.value, ['forest', 'test','a', 'c', 'i'])], [('asd',[
# 'test','asdd', 'ddd','dded'])], [('dddd', ['test'])], [('sdsd', ['test'])], [('sdsd2', ['test'])], [('sdsd3', ['test'])]]
# start_time: float = time.time()
# for t in filtwo:
#     result_bool =  create_rows_filter_OR(gdf, t)

#     # result_bool = gdf[gdf['landuse'].notna()]
# bool_time = (time.time() - start_time)
# # print("Time using .query() (Python engine): {:.6f} ms".format(query_time*1000))
# print("Time using boolean indexing: {:.6f} ms".format(bool_time*1000))


#! load performance tests - does not work - does not handle realations
# from shapely import geometry
# from shapely.geometry import Polygon, GeometryCollection, MultiLineString, LineString
# import geopandas as gpd
# import pandas as pd
# import osmnx as ox
# import pygeoops



# from shapely.ops import unary_union, split, linemerge

# from pyrosm import OSM
# import geopandas as gpd
# import time
# import matplotlib.pyplot as plt
#  # todo to normal utils
# def merge_lines_safe(geoms):
#     unioned = unary_union(geoms)
#     if unioned.is_empty:
#         return unioned
#     if unioned.geom_type == "LineString":
#         return unioned
#     if unioned.geom_type == "MultiLineString":
#         try:
#             return linemerge(unioned)
#         except Exception as e:
#             print(f"linemerge failed on MultiLineString: {e}")
#             return unioned
#     if unioned.geom_type == "GeometryCollection":
#         lines = [geom for geom in unioned if geom.geom_type in [
#             "LineString", "MultiLineString"]]
#         if not lines:
#             return unioned
#         elif len(lines) == 1:
#             return lines[0]
#         else:
#             # merge the extracted line geometries from geometry collection
#             try:
#                 return linemerge(MultiLineString(lines))
#             except Exception as e:
#                 print(f"linemerge failed on extracted lines: {e}")
#                 return MultiLineString(lines)
#     return unioned


# def merge_lines_gdf(gdf: gpd.GeoDataFrame, columns_ignore: list[str ] = []) -> gpd.GeoDataFrame:
#     """Merge lines in GeoDataFrame to one line if they have same values in columns (except columns in columns_ignore).
#     If want_bridges is True, merge all lines with same values in columns. If False, merge all lines with same values but ignore bridges.
#     To merging geoms is used function merge_lines_safe that uses unary_union and linemerge from shapely.ops.
#     It should merge multiple lines that are one line and that should prevents creating artifacts in plot.

#     Args:
#         gdf (gpd.GeoDataFrame): _description_
#         want_bridges (bool): _description_
#         columns_ignore (list[str  |  StyleKey], optional): _description_. Defaults to [].

#     Returns:
#         gpd.GeoDataFrame: _description_
#     """
#     columns_ignore = [*columns_ignore, 'geometry']
#         # if dont want remove columns and than...
#     columns = [
#         col for col in gdf.columns if col not in columns_ignore]
#     # merge all lines with same values in 'columns'
#     merged = gdf.groupby(columns, dropna=False, observed=True).agg({
#         'geometry': merge_lines_safe
#     })
#     merged_gdf = gpd.GeoDataFrame(
#         merged, geometry='geometry', crs=gdf.crs).reset_index()
#     return merged_gdf
# # Load OSM file

# # Define custom filter (e.g., extract only parks and forests)

# wanted_nodes1 = {
#     # 'place': {'city'},
#     # # 'place': {'city', 'town'},
#     # # 'place': {'city', 'town', 'village'},
#     'place': ['village'],
#     'natural': ['peak']
# }
# wanted_ways1 = {
#     # 'waterway': set({}),
#     # 'highway': ['motorway', 'trunk','primary', 'secondary', 'tertiary'],
#     # 'highway': ['motorway', 'trunk', 'primary'],
#     'highway': ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'],
#     # 'highway':set({}),
#     # 'railway': {'rail', 'tram'},
#     'railway': ['rail'],
#     'natural': ['coastline']
# }

# wanted_areas1 = {
#         # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
#         'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
#         'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium', 'swimming_pool', 'sports_centre'],
#         'natural': ['wood', 'water', 'scrub', 'heath'],
#         'boundary': ['national_park'],
#         'building': ['house','residential'],
#         'water': ['river','lake','reservoir'],
# }

# # Define additional tags to include in the output
# extra_tags_n = ["place", "natural", "name", 'ele']
# extra_tags_w = ['highway', 'railway', 'natural', 'bridge', 'layer', 'tunnel']
# extra_tags_a =  ["landuse", "leisure", "natural", "water", "boundary", "building"]
# # osm_keys_to_keep_n = ["place", "natural"]
# # osm_keys_to_keep_w = ["highway", "railway", "natural"]
# # osm_keys_to_keep_a = ["landuse", "leisure", "natural", "water", "boundary", "building"]

# # Measure time
# start_time = time.time()
# osm = OSM("./osm_files/brno.osm.pbf")

# # Get data with filter and additional tags
# nodes_gdf = osm.get_data_by_custom_criteria(wanted_nodes1, filter_type="keep", tags_as_columns=extra_tags_n)
# nodes_gdf = nodes_gdf[nodes_gdf.geom_type.isin(["Point"])]
# ways_gdf = osm.get_data_by_custom_criteria(wanted_ways1, filter_type="keep", tags_as_columns=extra_tags_w, keep_nodes=False)
# ways_gdf = ways_gdf[ways_gdf.geom_type.isin(["LineString", "MultiLineString"])]
# areas_gdf = osm.get_data_by_custom_criteria(wanted_areas1, filter_type="keep", tags_as_columns=extra_tags_a, keep_nodes=False)

def _apply_filters_not_allowed(not_allowed_tags, tags, curr_tag_key_inside: str | None = None):
    """Checking for unwanted tag values in tags. Recursively going through 
nested dictionaries and checks if the map feature that has these tags meets the defined condition (e.g. it is a tram track). 
It then checks that the map feature does not contain any illegal values (e.g. tram track must not lead inside a building)

The not_allowed_tags structure that will ensure that tram tracks doesn't have tunnel column with building_passage as value will look like this:
    {
    'railway': { # will ensure that map feature is railway category
        'tram': { # will ensure that map feature is tram track
            'tunnel': ['building_passage'] # and will set that tunnel column of map feature will not have building_passage value
            }
        }   
    }
    Args:
        not_allowed_tags (dict[str, dict[any]]|dict[str, list[str]]): Nested dictionary
        tags (_type_): Tags of concrete map feature (area, way, node)
        curr_tag_key_inside (str, optional): The key to this dict is that the function is nested within (e.g., railway)
        but cannot be a value that is inside a column in a osm data (e.g. tram, forrest...) only name of column in osm data

    Returns:
        bool: True if doesn't contain any not allowed tags otherwise false 
    """
    if (not not_allowed_tags):
        return True
    for dict_tag_key, unwanted_values in not_allowed_tags.items():
        # not directly inside any tag and curr tag is not in tags => skip
        if (curr_tag_key_inside is None and dict_tag_key not in tags):
            continue

        # Checking if map feature meets the defined conditions
        if (isinstance(unwanted_values, dict)):
            # The unwanted values are more nested => need to go down further
            next_tag_key_inside: str | None = None
            if (dict_tag_key in tags):  # dict_tag_key is tag_key (column name) in tags
                next_tag_key_inside = dict_tag_key

            else:  # tag_key_value after tag_key
                # check if the value inside the current key matches the dict tag key - map feature meet this condition
                curr_tag_key_value = tags.get(curr_tag_key_inside)
                if (curr_tag_key_value != dict_tag_key):
                    continue  # map feature does not meet this conditon for going to this next recursion level => skip

            # map feature meet this condition go to next recursion level
            return_value = _apply_filters_not_allowed(
                unwanted_values, tags, next_tag_key_inside)
            if (return_value):
                # unwanted value not found in this branch try to find in some other tag (can't have a single one)
                continue
            return False  # one unwanted was found, tags are not valid

        # map feature meets the defined conditions
        # Check map feature for illegal values in dict_tag_key columns
        dict_key_value = tags.get(dict_tag_key)
        if (dict_key_value is not None):
            # list of unwanted values is empty ban all values, else check for specific value in list
            if not unwanted_values or dict_key_value in unwanted_values:
                return False
    # does not conntain unwanted tags
    return True

def _apply_filters(wanted_features, tags):
    """ Checking for wanted features by checking values in tags. Going through wanted_tags and check if map feature is some of wanted map feature.

    Map feature is represented as key (feature category) with value (concrete feature) (e.g. key=landuse and value=forest).  

    Args:
        wanted_features (dict[str, list[str]]): dict with feature category and list of allowed features for this category
        tags (_type_): tags of concrete map feature (area, way, node)

    Returns:
        bool: If find one return true else false
    """
    for features_category, wanted_features_values in wanted_features.items():
        # check if map feature is feature from this features category
        feature: str | None = tags.get(features_category)
        if feature is not None:
            # features_values is empty list => get all from features_category else check if feature is wanted
            if not wanted_features_values or feature in wanted_features_values:
                return True
    # map feature is not in wanted features
    return False
# map feature is not in wanted features
# pokud je pole prázdné nic nepřidávat do tagFilter, pokud je tag filter prázný ani se nezobrazí 
# key filter se zobrazí vždy, tagy budou spojený
    return False

unwanted_nodes_tags = {

}

unwanted_ways_tags = {
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    # 'railway': {
    #     'service': ['yard', 'spur','crossover', 'siding'], # spur, siding
    #     # 'tunnel': ['building_passage'],
    #     # 'tunnel': [],
    # },
    # 'waterway': ['stream']

    
    # {'railway':""}:{'service':['yard'],'tunnel': ['building_passage']}
}

unwanted_areas_tags = {
}

wanted_ways = {
    # 'waterway': set({}),
    # 'highway': ['motorway', 'trunk','primary', 'secondary', 'tertiary'],
    # 'highway': ['motorway', 'trunk', 'primary'],
    # 'highway': {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'},
    # 'highway': {'tertiary'},
    'highway': set({}),
    'railway': {'rail', 'tram'},

    # 'railway': {'rail'},
    'natural': {'coastline'}
}



wanted_areas = {
        'landuse': {'forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'},
   
        'leisure': {'park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
        # 'leisure': {'park', 'pitch', 'garden', 'golf_course', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
        'natural': {'wood', 'water', 'scrub', 'heath'},
        # # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
        # 'water': set({}),
        'boundary': {'national_park'},
        'building': {'house','residential'},
        'water': ['river','lake','reservoir'],
}

import osmium
import time
import geopandas
import osmium.filter
import osmium.osm

wanted_nodes = {
    # 'place': {'city'},
    # # 'place': {'city', 'town'},
    # # # 'place': {'city', 'town', 'village'},
    # 'place': {'village'},
    # 'natural': {'peak'}
}

file = './osm_files/vysJihE.osm.pbf'

#! merged
# startM = time.time()

# class Filter():
#     def node(self, node):
#         return not (_apply_filters(wanted_nodes, node.tags) and _apply_filters_not_allowed(unwanted_nodes_tags, node.tags))
          
#     def way(self, way):
#         return not (_apply_filters(wanted_ways, way.tags) and _apply_filters_not_allowed(unwanted_ways_tags, way.tags))
        
#     def area(self, area):
#         return not (_apply_filters(wanted_areas, area.tags) and _apply_filters_not_allowed(unwanted_areas_tags, area.tags))
    

# fp: osmium.FileProcessor = osmium.FileProcessor(file)\
#          .with_locations().with_areas()\
#             .with_filter(osmium.filter.EmptyTagFilter())\
#             .with_filter(osmium.filter.KeyFilter("boundary", "water", "building", "landuse", 'leisure', "natural", "highway", "railway", "natural"))\
#             .with_filter(Filter())\
#             .with_filter(osmium.filter.GeoInterfaceFilter(tags=['place']))

# gdf = geopandas.GeoDataFrame.from_features(fp)
# nodes1 = gdf[gdf.geom_type.isin(["Point"])]
# ways1 = gdf[gdf.geom_type.isin(["LineString", "MultiLineString"])]
# areas1 = gdf[gdf.geom_type.isin(["Polygon", "MultiPolygon"])]

# endM = time.time()







#! splited
class Nodes():
    def node(self, node):
        return not (_apply_filters(wanted_nodes, node.tags) and _apply_filters_not_allowed(unwanted_nodes_tags, node.tags))
    
class Ways():
    def way(self, way):
        return not (_apply_filters(wanted_ways, way.tags) and _apply_filters_not_allowed(unwanted_ways_tags, way.tags))
        
class Areas():
    def area(self, area):
        return not (_apply_filters(wanted_areas, area.tags) and _apply_filters_not_allowed(unwanted_areas_tags, area.tags))
    
startS = time.time()

fpnode: osmium.FileProcessor = osmium.FileProcessor('./osm_files/brno.osm.pbf')\
         .with_locations()\
            .with_filter(osmium.filter.EmptyTagFilter())\
            .with_filter(osmium.filter.EntityFilter(osmium.osm.NODE))\
            .with_filter(osmium.filter.KeyFilter(""))\
            .with_filter(Nodes())\
            .with_filter(osmium.filter.GeoInterfaceFilter(tags=['place']))

fpway: osmium.FileProcessor = osmium.FileProcessor('./osm_files/brno.osm.pbf')\
         .with_locations()\
            .with_filter(osmium.filter.EmptyTagFilter())\
            .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
            .with_filter(osmium.filter.KeyFilter("highway", 'railway', 'natural'))\
            .with_filter(Ways())\
            .with_filter(osmium.filter.GeoInterfaceFilter(tags=['place']))


fparea: osmium.FileProcessor = osmium.FileProcessor('./osm_files/brno.osm.pbf')\
         .with_areas()\
            .with_filter(osmium.filter.EmptyTagFilter())\
            .with_filter(osmium.filter.EntityFilter(osmium.osm.AREA))\
            .with_filter(osmium.filter.KeyFilter("boundary", "water", "building", "landuse", 'leisure', "natural"))\
            .with_filter(Areas())\
            .with_filter(osmium.filter.GeoInterfaceFilter(tags=['place']))

nodes2 = geopandas.GeoDataFrame.from_features(fpnode)
ways2 = geopandas.GeoDataFrame.from_features(fpway)
areas2 = geopandas.GeoDataFrame.from_features(fparea)

endS = time.time()
# print(len(nodes1))
# print(len(ways1))
# print(len(areas1))
print(len(nodes2))
print(len(ways2))
print(len(areas2))
# print(f"time merged: {(endM-startM)*1000} ms")
print(f"time splited: {(endS-startS)*1000} ms")
