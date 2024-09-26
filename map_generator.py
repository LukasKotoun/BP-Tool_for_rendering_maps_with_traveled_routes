import osmium
import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely import wkt, geometry
import matplotlib.pyplot as plt
import time
from typing import Union, List, Tuple
import subprocess
import tempfile
import sys
from memory_profiler import profile
import gc
import timeit

#------------cons--------------
WAYS_RATIO_TO_MAP_SIZE = 0.1
DEFAULT_MAP_BG_COLOR = '#EDEDE0'


city_name = "Brno, Czech Republic"


#------------settings--------------

way_filters = {
    'waterway': True,
    'highway': ['highway','trunk','primary','secondary'],
    # 'highway':True
}
# allowed_values_way = {}
# for key, values in way_filters.items():
#     for value in values:
#         allowed_values_way[value] = key
area_filters = {
    # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium','swimming_pool', 'sports_centre'],
    'water': True,
    # 'water': ['river','lake','reservoir'],
}
landuse_styles = {
    'farmland': {'color': '#EDEDE0', 'zindex': None},
    'forest': {'color': '#9FC98D', 'zindex': None},
    'meadow': {'color': '#B7DEA6', 'zindex': None},
    'grass': {'color': '#B7DEA6', 'zindex': None},
    'residential': {'color': '#E2D4AF', 'zindex': None},
    'industrial': {'color': '#DFDBD1', 'zindex': None},
    'basin': {'color': '#8FB8DB', 'zindex': 1},
    'salt_pond': {'color': '#8FB8DB', 'zindex': 1},
}

leisure_styles = {
    'swimming_pool': {'color': '#8FB8DB', 'zindex': 2},  
    'golf_curse': {'color': '#DCE9B9', 'zindex': 1},    
    'playground': {'color': '#DCE9B9', 'zindex': 1},  
    'pitch': {'color': '#DCE9B9', 'zindex': 2},  
    'sports_centre': {'color': '#9FC98D', 'zindex': 1},  
}
	
highway_styles = {
    'highway': {'color': '#FDC364', 'zindex': 7}, 
    'trunk': {'color': '#FDC364', 'zindex': 6},
    'primary': {'color': '#FDC364', 'zindex': 5},
    'secondary': {'color': '#F7ED60', 'zindex': 4},
    'tertiary': {'color': '#FFFFFF', 'zindex': 3},
    'unclassified': {'color': '#FFFFFF', 'zindex': None},
    'road': {'color': '#DAD6D2', 'zindex': None},
    'footway': {'color': 'brown', 'zindex': None},
    'steps': {'color': 'purple', 'zindex': None},
    'path': {'color': 'red', 'zindex': None},
    'residential': {'color': 'blue', 'zindex': None}
}

building_styles = {
    'house': {'color': 'grey', 'zindex': 1},
}


# Define attribute mapping with default values
tag_styles = {
    'building': (building_styles, {'color': '#B7DEA6', 'zindex': 1}),
    'water': ({}, {'color': '#8FB8DB', 'zindex': 1}),
    'waterway': ({}, {'color': '#8FB8DB', 'zindex': 1}),
    'leisure': (leisure_styles, {'color': '#EDEDE0', 'zindex': 0}),
    'natural': (landuse_styles, {'color': '#B7DEA6', 'zindex': 0}),
    'landuse': (landuse_styles, {'color': '#EDEDE0', 'zindex': 0}),
    'highway': (highway_styles, {'color': '#FFFFFF', 'zindex': 2})
}

# road_width_mapping = {
#     'primary': 1.5,    # Primary roads
#     'secondary': 1.3,  # Secondary roads
#     'tertiary': 0.7,   # Tertiary roads
#     'residential': 0.5, # Residential roads
#     'service': 0.3     # Smallest for service roads
# }

#------------settings end--------------

class OsmDataParser(osmium.SimpleHandler):
    #todo add filters as arg
    def __init__(self, way_filters, area_filters, way_additional_columns = [], area_additional_columns = []):
        super().__init__()
        self.tags = []
        self.polygons = []
        self.way_filters = way_filters
        self.area_filters = area_filters
        # merge always wanted columns (map objects) with additions wanted info columns
        self.way_columns = way_filters.keys() | way_additional_columns
        self.area_columns = area_filters.keys() | area_additional_columns
        
        self.geom_factory = osmium.geom.WKTFactory()  # Create WKT Factory for geometry conversion
        #extract function from libraries - quicker than extracting every time 
        self.geom_factory_linestring = self.geom_factory.create_linestring
        self.geom_factory_polygon = self.geom_factory.create_multipolygon
        self.wkt_loads_func = wkt.loads
        

    def apply_filters(self, allowed_tags, tags):
        for key, allowed_values in allowed_tags.items():
            tag_value = tags.get(key)
            if tag_value is not None:
                if allowed_values is True or tag_value in allowed_values: 
                    return True
        return False
        
    def way(self, way):
        # todo filter - bud rozdelit na area a way a nebo pro vsechny
        if self.apply_filters(self.way_filters, way.tags):
            wkt_geom = self.geom_factory_linestring(way) 
            shapely_geom = self.wkt_loads_func(wkt_geom)  
            self.polygons.append(shapely_geom)
            filtered_tags = {tag_key: tag_value for tag_key, tag_value in way.tags if tag_key in self.way_columns}
            self.tags.append(filtered_tags)
        
    
    
    def area(self, area):
        if self.apply_filters(self.area_filters, area.tags):
            wkt_geom = self.geom_factory_polygon(area) 
            shapely_geom = self.wkt_loads_func (wkt_geom) 
            filtered_tags = {tag_key: tag_value for tag_key, tag_value in area.tags if tag_key in self.area_columns}
            self.tags.append(filtered_tags)
            self.polygons.append(shapely_geom)
        
    
    
    def create_gdf(self):
        # todo check if directly creating geo data frame will be better
        # start_time = time.time()  # Record start time
        
        print(f"polygons: {sys.getsizeof(self.polygons)}, tags: {sys.getsizeof(self.tags)}")
        gdf =  gpd.GeoDataFrame(pd.DataFrame(self.tags).assign(geometry=self.polygons), crs="EPSG:4326")

        # gdf2 = gpd.GeoDataFrame(pd.DataFrame(self.tags2).assign(geometry=self.polygons2), crs="EPSG:4326")
        print(f"gdf: {sys.getsizeof(gdf)}")
        # print(f"polygons: {sys.getsizeof(self.polygons)}, tags: {sys.getsizeof(self.tags)}")
        # end_time = time.time()  # Record end time
        # elapsed_time = end_time - start_time  # Calculate elapsed time
        # print(f"Elapsed time gdf: {elapsed_time * 1000:.5f} ms")
        
        return gdf
    
    
    def clear_gdf(self):
        self.polygons.clear()
        self.tags.clear()
        # self.polygons2.clear()
        # self.tags2.clear()
        
        
class OsmDataPreprocessor:
    def __init__(self, osm_input_file: str, area: Union[str, List[Tuple[float, float]]], osm_output_file : str = None):
        self.osm_input_file = osm_input_file # Can be a string (place name) or a list of coordinates
        self.area = area  # Can be a string (place name) or a list of coordinates
        self.osm_output_file = osm_output_file
    
    def check_files_validity():
        pass
    
    def extract_area(self):
        #todo check file validity - if file exists
        if self.osm_output_file:
            temp_geojson_path, reqired_map_area = self.create_geojson(True)
            command = [
                'osmium', 'extract',
                '-p', temp_geojson_path,
                self.osm_input_file,
                '-o', self.osm_output_file
            ]
            #todo catch if file osm file exist
            subprocess.run(command, check=True)
            return self.osm_output_file, reqired_map_area
        else:
            temp_geojson_path, reqired_map_area = self.create_geojson(False)
            return self.osm_input_file, reqired_map_area 
        
                
    def create_geojson(self, want_geojson):
        if isinstance(self.area, str): 
            if self.area.endswith('.geojson'): 
                polygon_gdf = gpd.read_file(self.area) # Get area from geojson file
                if polygon_gdf.empty:
                    raise ValueError("Given GeoJSON file is empty.")
                polygon = polygon_gdf.unary_union
                return self.area, polygon
            else:
                polygon_gdf = ox.geocode_to_gdf(self.area)  # Get from place name
                if polygon_gdf.empty:
                    raise ValueError("The requested location has not been found.")
                
        elif isinstance(self.area, list): #get area from coordinates
            polygon = geometry.Polygon(self.area)
            polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
        else: #area cannot be created
            raise ValueError("Invalid area")
        
        polygon = polygon_gdf.unary_union
        if(want_geojson):
        #create tmp file for osmium extraction
            with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson:
                polygon_gdf.to_file(temp_geojson.name, driver="GeoJSON")
                return temp_geojson.name, polygon
        return None, polygon


def assign_attributes(row, tag_styles):
    assigned_styles = {}
    for tag_key, (tag_map, default_values) in tag_styles.items():
        if tag_key in row and pd.notna(row[tag_key]):
            tag_styles = tag_map.get(row[tag_key], default_values) #retrieve record for a specific key (e.g. landues) and value (e.g. forest) combination in the map or retrieve the default value for that key.
            for style_key, default_style in default_values.items(): # select individual values from the record or default values if there are none in the record
                tag_style = tag_styles.get(style_key)
                assigned_styles[style_key] = tag_style if tag_style is not None else default_style
            return assigned_styles
    return {'color':DEFAULT_MAP_BG_COLOR,'zindex': 0 }


# if isinstance(row, pd.Series):
place_name = 'brno'
#todo argument parsin - jmena souboru + kombinace flagu podle složitosti zpracování (bud flag na vypnutí extractu nebo podle zadaného vystupního souboru)
# osm_data_preprocessor = OsmDataPreprocessor('trebic.osm.pbf','Třebíč, Czech Republic')
osm_data_preprocessor = OsmDataPreprocessor(f'{place_name}.osm.pbf','Brno, Czech Republic')

osm_file_name, reqired_map_area = osm_data_preprocessor.extract_area()
osm_file_parser = OsmDataParser(way_filters,area_filters)

osm_file_parser.apply_file(osm_file_name)
gdf = osm_file_parser.create_gdf()

start_time = time.time()  # Record start time
attributes = gdf.apply(lambda row: assign_attributes(row, tag_styles), axis=1).tolist()
end_time = time.time()
duration = end_time - start_time
print("Time taken:", duration*10000, "ms")

gdf = gdf.join(pd.DataFrame(attributes))


#!for roads only
gdf_projected = gdf.to_crs("Web Mercator") # web mercator
gdf_projected['geometry'] = gdf_projected['geometry'].buffer(4) 
gdf = gdf_projected.to_crs(gdf.crs)
if 'zindex' in gdf.columns:
    gdf = gdf.sort_values(by='zindex')

# todo to map plot class
def get_map_size(gdf_total_bounds):
    latitude = gdf_total_bounds['east'] - gdf_total_bounds['west']
    longitude = gdf_total_bounds['north'] - gdf_total_bounds['south']
    return max(latitude, longitude)

#map bounds
gdf_total_bounds = dict(zip(['west', 'north', 'east', 'south'], gdf.total_bounds))

map_longest_side_lenght = get_map_size(gdf_total_bounds)
#get cliping polygon


# clipping_area_mask = polygon_gdf.unary_union
 
clipping_helper_polygon = geometry.Polygon([
    (gdf_total_bounds['east'], gdf_total_bounds['south']),  # Bottom-left corner
    (gdf_total_bounds['east'], gdf_total_bounds['north']),  # Top-left corner
    (gdf_total_bounds['west'], gdf_total_bounds['north']),  # Top-right corner
    (gdf_total_bounds['west'], gdf_total_bounds['south']),  # Bottom-right corner
    (gdf_total_bounds['east'], gdf_total_bounds['south'])   # Closing the polygon (back to bottom-left)
])
clipping_polygon = clipping_helper_polygon.difference(reqired_map_area)
if isinstance(clipping_polygon, geometry.Polygon):
    clipping_polygon = geometry.MultiPolygon([clipping_polygon])
clipping_polygon = gpd.GeoDataFrame(geometry=[clipping_polygon], crs="EPSG:4326")
reqired_map_area_gdf = gpd.GeoDataFrame(geometry=[reqired_map_area], crs="EPSG:4326")

fig, ax = plt.subplots(figsize=(10, 10))
ax.axis('off')
reqired_map_area_gdf.plot(ax=ax, color=DEFAULT_MAP_BG_COLOR, linewidth=1)

#plot all
gdf.plot(ax=ax, color=gdf['color'],linewidth = WAYS_RATIO_TO_MAP_SIZE/map_longest_side_lenght, alpha=1)

#clip
clipping_polygon.plot(ax=ax, color='white', alpha=1)  # Fill the outer polygon
reqired_map_area_gdf.boundary.plot(ax=ax, color='black', linewidth=1)

# #zoom
hole_bounds = reqired_map_area.bounds  # Get the bounds of the hole polygon
x_buffer = (hole_bounds[2] - hole_bounds[0]) * 0.01  # 1% of width
y_buffer = (hole_bounds[3] - hole_bounds[1]) * 0.01  # 1% of height
ax.set_xlim([hole_bounds[0] - x_buffer, hole_bounds[2] + x_buffer])  # Expand x limits
ax.set_ylim([hole_bounds[1] - y_buffer, hole_bounds[3] + y_buffer])  # Expand y limits


pdf_filename = f'{place_name}.pdf'
plt.savefig(pdf_filename, format='pdf')


plt.show()