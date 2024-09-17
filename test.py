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
import matplotlib.pyplot as plt

# Define the city name
city_name = "Czech Republic"

# Get the boundary polygon of the city
city_boundary = ox.geocode_to_gdf(city_name)

# Plot the boundary
city_boundary.plot(edgecolor='k', facecolor='none')
plt.show()