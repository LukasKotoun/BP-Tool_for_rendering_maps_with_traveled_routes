from config import *
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
import timeit




class OsmDataParser(osmium.SimpleHandler):
    #todo add filters as arg
    def __init__(self, way_filters, area_filters, way_additional_columns = [], area_additional_columns = []):
        super().__init__()
        self.way_tags = []
        self.way_geometry = []
        self.area_tags = []
        self.area_geometry = []
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
        if self.apply_filters(self.way_filters, way.tags):
            shapely_geometry = self.wkt_loads_func(self.geom_factory_linestring(way)) #convert osmium way to wkt str format and than to shapely linestring geometry
            filtered_tags = {tag_key: tag_value for tag_key, tag_value in way.tags if tag_key in self.way_columns}
            self.way_geometry.append(shapely_geometry)
            self.way_tags.append(filtered_tags)
        
    
    def area(self, area):
        if self.apply_filters(self.area_filters, area.tags):
            shapely_geometry = self.wkt_loads_func(self.geom_factory_polygon(area)) #convert osmium area to wkt str format and than to shapely polygon/multipolygon geometry 
            filtered_tags = {tag_key: tag_value for tag_key, tag_value in area.tags if tag_key in self.area_columns}
            self.area_geometry.append(shapely_geometry)
            self.area_tags.append(filtered_tags)
        
    
    
    def create_gdf(self):
        # todo check if directly creating geo data frame will be better
        start_time = time.time()  # Record start time
        
        print(f"AREA polygons: {sys.getsizeof(self.area_geometry)}, tags: {sys.getsizeof(self.area_tags)}")
        print(f"WAY polygons: {sys.getsizeof(self.way_geometry)}, tags: {sys.getsizeof(self.way_tags)}")
        ways_gdf = gpd.GeoDataFrame(pd.DataFrame(self.way_tags).assign(geometry=self.way_geometry), crs="EPSG:4326")
        areas_gdf = gpd.GeoDataFrame(pd.DataFrame(self.area_tags).assign(geometry=self.area_geometry), crs="EPSG:4326")
        print(f"ways: {sys.getsizeof(ways_gdf)},  areas: {sys.getsizeof(areas_gdf)}, combined: {sys.getsizeof(ways_gdf) + sys.getsizeof(areas_gdf)}")
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print(f"Elapsed time gdf: {elapsed_time * 1000:.5f} ms")
        
        return ways_gdf, areas_gdf
    
    
    def clear_gdf(self):
       pass
        #self.polygons2.clear()
        #self.tags2.clear()
        
        
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


#categories in format 'category_item':{'style_key':'style_value'}
def filter_category_styles(categories_styles, wanted_styles, wanted_categories):
    filtered_categories_styles = {}
    for category_name, (category_map, category_default_styles) in categories_styles.items():
        if category_name in wanted_categories: #check if category can be in gdf
            category_filter = wanted_categories[category_name]
            if isinstance(category_filter, list): #get style for only some items in category
                filtered_category_styles = {      
                    category_item: {style_key: item_styles[style_key] for style_key in wanted_styles if style_key in item_styles} #filter only wanted styles for item in category (e.g. color)
                    for category_item, item_styles in category_map.items()
                    if category_item in category_filter     #filter wanted items
                }
            elif category_filter is True:  #get style for all items in category
                filtered_category_styles = {
                    category_item: {style_key: item_styles[style_key] for style_key in wanted_styles if style_key in item_styles} #filter only wanted styles for item in category (e.g. color)
                    for category_item, item_styles in category_map.items()
                }
            filtered_categories_styles[category_name] = (filtered_category_styles, 
                                                        {style_key: category_default_styles[style_key] for style_key in wanted_styles 
                                                        if style_key in category_default_styles}) #store filterd category with wanted default styles
    return filtered_categories_styles

def get_total_bounds(gdfs = []):
    west = float('inf')
    south = float('inf')
    east = float('-inf')
    north = float('-inf')
    
    for gdf in gdfs:
        bounds = gdf.total_bounds #['west', 'north', 'east', 'south']
        west = min(west, bounds[0])
        south = min(south, bounds[1])
        east = max(east, bounds[2])
        north = max(north, bounds[3])
        
    return {
        'west': west,
        'south': south,
        'east': east,
        'north': north
        }


def assign_styles(row, categories_styles):
    assigned_styles = {}
    for category_name, (category_map, category_default_styles) in categories_styles.items():
        if category_name in row and pd.notna(row[category_name]):
            category_styles = category_map.get(row[category_name], category_default_styles) #retrieve record for a specific key (e.g. landues) and value (e.g. forest) combination in the map or retrieve the default value for that key.
            for style_key, default_style in category_default_styles.items(): # select individual values from the category styles or use default values if there are none individual in the record
                category_style = category_styles.get(style_key)
                assigned_styles[style_key] = category_style if category_style is not None else default_style
            return assigned_styles
    return GENERAL_DEFAULT_STYLES

start_time_whole = time.time()  # Record start time



place_name = 'trebic'
#todo argument parsin - jmena souboru + kombinace flagu podle složitosti zpracování (bud flag na vypnutí extractu nebo podle zadaného vystupního souboru)
# osm_data_preprocessor = OsmDataPreprocessor('trebic.osm.pbf','Třebíč, Czech Republic')
osm_data_preprocessor = OsmDataPreprocessor(f'{place_name}.osm.pbf','Třebíč, Czech Republic')

osm_file_name, reqired_map_area = osm_data_preprocessor.extract_area()
reqired_map_area_gdf = gpd.GeoDataFrame(geometry=[reqired_map_area], crs="EPSG:4326")
osm_file_parser = OsmDataParser(way_filters,area_filters)

osm_file_parser.apply_file(osm_file_name)
#todo 2 dif functions
ways_gdf, areas_gdf = osm_file_parser.create_gdf()
#todo add clearing

#todo data process class 
def assign_styles_to_gdf(gdf, categories_styles, style_keys, filters):
    styles = filter_category_styles(categories_styles, style_keys, filters)
    styles_columns = gdf.apply(lambda row: assign_styles(row, styles), axis=1).tolist()
    gdf = gdf.join(pd.DataFrame(styles_columns))
    return gdf

ways_gdf = assign_styles_to_gdf(ways_gdf, categories_styles, ['color', 'zindex'], way_filters)
areas_gdf = assign_styles_to_gdf(areas_gdf, categories_styles, ['color', 'zindex'], area_filters)

#remove unwanted spaces between lines in corners - by converting to polygon and expanding 
gdf_projected = ways_gdf.to_crs("Web Mercator") # web mercator
gdf_projected['geometry'] = gdf_projected['geometry'].buffer(4) 
ways_gdf = gdf_projected.to_crs(ways_gdf.crs)

#!filering for diferent ways ploting
# Define the condition for filtering
# condition = ways_gdf['highway'].notnull()
# filtered_gdf = ways_gdf[condition]
# remaining_gdf = ways_gdf[~condition]

def sort_gdf_by(gdf, column_name):
    if column_name in gdf.columns:
        return gdf.sort_values(by=column_name)
    
    
ways_gdf = sort_gdf_by(ways_gdf, 'zindex')
areas_gdf = sort_gdf_by(areas_gdf, 'zindex')


# todo to map plot class
def get_map_size(gdf_total_bounds):
    latitude = gdf_total_bounds['east'] - gdf_total_bounds['west']
    longitude = gdf_total_bounds['north'] - gdf_total_bounds['south']
    return max(latitude, longitude)
start_time = time.time()

#map bounds
# gdf_total_bounds = dict(zip(['west', 'north', 'east', 'south'], gdf.total_bounds))
#! change total bounds ploting

# gdf_total_bounds = dict(zip(['west', 'north', 'east', 'south'], reqired_map_area_gdf.total_bounds))
gdf_total_bounds = get_total_bounds([ways_gdf,areas_gdf])
map_longest_side_lenght = get_map_size(gdf_total_bounds)
end_time = time.time()

# Measure time taken
time_taken = end_time - start_time
print(f"Time taken for filtering: {time_taken:.6f} seconds")

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

fig, ax = plt.subplots(figsize=(10, 10))
ax.axis('off')
reqired_map_area_gdf.plot(ax=ax, color=GENERAL_DEFAULT_STYLES['color'], linewidth=1)



#plot all
areas_gdf.plot(ax=ax, color=areas_gdf['color'], alpha=1)
ways_gdf.plot(ax=ax, color=ways_gdf['color'], alpha=1)

# plot with linewidth
#ways_gdf.plot(ax=ax, facecolor=ways_gdf['color'], edgecolor=ways_gdf['color'], linewidth= WAYS_RATIO_TO_MAP_SIZE/map_longest_side_lenght)

# plot ways outlines
# ways_gdf.plot(ax=ax, color='none', edgecolor='black', linewidth=0.1, zorder=2)


#clip
clipping_polygon.plot(ax=ax, color='white', alpha=1, zorder=3)  # Fill the outer polygon
reqired_map_area_gdf.boundary.plot(ax=ax, color='black', linewidth=1, zorder=3)

#zoom
hole_bounds = reqired_map_area.bounds  # Get the bounds of the hole polygon
x_buffer = (hole_bounds[2] - hole_bounds[0]) * 0.01  # 1% of width
y_buffer = (hole_bounds[3] - hole_bounds[1]) * 0.01  # 1% of height
ax.set_xlim([hole_bounds[0] - x_buffer, hole_bounds[2] + x_buffer])  # Expand x limits
ax.set_ylim([hole_bounds[1] - y_buffer, hole_bounds[3] + y_buffer])  # Expand y limits


pdf_filename = f'{place_name}.pdf'
plt.savefig(pdf_filename, format='pdf')


end_time_whole = time.time()
duration = end_time_whole - start_time_whole
print("Time whole taken:", duration*10000, "ms")

plt.show()