import sys

import osmium
from shapely import wkt
import pandas as pd
import geopandas as gpd

from modules.common_helpers import time_measurement_decorator

class OsmDataParser(osmium.SimpleHandler):
    
    def __init__(self, way_filters, area_filters, unwanted_ways_tags, unwanted_areas_tags,
                 way_additional_columns = [], area_additional_columns = [], 
                 reqired_map_area_name = None, get_required_area_from_osm = False):
        super().__init__()
        self.way_tags = []
        self.way_geometry = []
        self.area_tags = []
        self.area_geometry = []
        self.way_filters = way_filters
        self.area_filters = area_filters
        self.unwanted_ways_tags = unwanted_ways_tags
        self.unwanted_areas_tags = unwanted_areas_tags
        # merge always wanted columns (map objects) with additions wanted info columns
        self.way_columns = way_filters.keys() | way_additional_columns
        self.area_columns = area_filters.keys() | area_additional_columns
        #area searching
        self.reqired_area_polygon = None
        self.get_required_area_from_osm = get_required_area_from_osm
        self.reqired_map_area_name = reqired_map_area_name
        
        self.geom_factory = osmium.geom.WKTFactory()  # Create WKT Factory for geometry conversion
        #extract function from libraries - quicker than extracting every time 
        self.geom_factory_linestring = self.geom_factory.create_linestring
        self.geom_factory_polygon = self.geom_factory.create_multipolygon
        self.wkt_loads_func = wkt.loads

    @staticmethod
    def filter_not_allowed_tags(not_allowed_tags, tags, curr_tag_key=None):  
        for dict_tag_key, unwanted_values in not_allowed_tags.items():
            if(curr_tag_key is None and dict_tag_key not in tags): continue
            if(isinstance(unwanted_values, dict)):
                next_tag_key = None
                if(dict_tag_key in tags): # two tag_keys after each other
                    next_tag_key = dict_tag_key
                elif (curr_tag_key is not None): # tag_key_value after tag_key
                    curr_tag_key_value = tags.get(curr_tag_key)
                    if(curr_tag_key_value != dict_tag_key): #key values are not coresponding (dict key value and key value in tags) => dont go in next level of immersion 
                        continue
                    
                return_value = OsmDataParser.filter_not_allowed_tags(unwanted_values, tags, next_tag_key)
                if(return_value): continue # try to find some unwanted tag
                return False
            # unwanted_values is list
            #sub_tag is unwanted tag and value is value of that tag in tags
            dict_key_value = tags.get(dict_tag_key)
            if(dict_key_value is not None):
                #list of unwanted tag values is empty (filter all with any on that tag) or value is in list 
                if not unwanted_values or dict_key_value in unwanted_values:
                    return False        
        return True  
            
    @staticmethod
    def apply_filters(allowed_tags, tags):
        for tag_key, allowed_values in allowed_tags.items():
            key_value = tags.get(tag_key)
            if key_value is not None:
                if not allowed_values or key_value in allowed_values: 
                    return True                     
        return False
    
    def way(self, way):
        if OsmDataParser.apply_filters(self.way_filters, way.tags) and OsmDataParser.filter_not_allowed_tags(self.unwanted_ways_tags, way.tags):
            try:
                shapely_geometry = self.wkt_loads_func(self.geom_factory_linestring(way)) #convert osmium way to wkt str format and than to shapely linestring geometry
                #! možná přidání které chci tagy pokud obsahuje ještě další tagy?, nebo udělat prostě 3 urovně měst
                filtered_tags = {tag_key: tag_value for tag_key, tag_value in way.tags if tag_key in self.way_columns}
                self.way_geometry.append(shapely_geometry)
                self.way_tags.append(filtered_tags)
            except RuntimeError as e:
                print(f"Invalid way geometry: {e}")
                return
            except Exception as e:
                print(f"Error in way function - osm file processing: {e}")
                return
            
    def area(self, area):
        if (self.get_required_area_from_osm): #find area name in osm file
            if('name' in area.tags and area.tags['name'] == self.reqired_map_area_name):
                self.reqired_area_polygon = self.geom_factory_polygon(area)
        if OsmDataParser.apply_filters(self.area_filters, area.tags) and OsmDataParser.filter_not_allowed_tags(self.unwanted_areas_tags, area.tags):
            try:
                shapely_geometry = self.wkt_loads_func(self.geom_factory_polygon(area)) #convert osmium area to wkt str format and than to shapely polygon/multipolygon geometry 
                filtered_tags = {tag_key: tag_value for tag_key, tag_value in area.tags if tag_key in self.area_columns}
                self.area_geometry.append(shapely_geometry)
                self.area_tags.append(filtered_tags)
            except RuntimeError as e:
                print(f"Invalid area geometry: {e}")
                return
            except Exception as e:
                print(f"Error in area function - osm file processing: {e}")
                return
            
    @time_measurement_decorator("gdf creating")
    def create_gdf(self, epgs_number):
        print(f"AREA polygons: {sys.getsizeof(self.area_geometry)}, tags: {sys.getsizeof(self.area_tags)}")
        print(f"WAY polygons: {sys.getsizeof(self.way_geometry)}, tags: {sys.getsizeof(self.way_tags)}")
        ways_gdf = gpd.GeoDataFrame(pd.DataFrame(self.way_tags).assign(geometry=self.way_geometry), crs=f"EPSG:{epgs_number}")
        areas_gdf = gpd.GeoDataFrame(pd.DataFrame(self.area_tags).assign(geometry=self.area_geometry), crs=f"EPSG:{epgs_number}")
        print(f"ways: {sys.getsizeof(ways_gdf)},  areas: {sys.getsizeof(areas_gdf)}, combined: {sys.getsizeof(ways_gdf) + sys.getsizeof(areas_gdf)}")
        return ways_gdf, areas_gdf
    
    def get_required_area_gdf(self):
        return self.reqired_area_polygon
    
    def clear_gdf(self):
        self.way_geometry.clear()
        self.way_tags.clear()
        self.area_geometry.clear()
        self.area_tags.clear()