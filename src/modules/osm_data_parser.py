import sys
import warnings

import osmium
from shapely import wkt
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

from common.common_helpers import time_measurement_decorator

class OsmDataParser(osmium.SimpleHandler):
    
    def __init__(self, wanted_nodes, wanted_ways, wanted_areas, unwanted_nodes_tags, unwanted_ways_tags, unwanted_areas_tags,
                 node_additional_columns = {}, way_additional_columns = {}, area_additional_columns = {}):
        super().__init__()
        #init for storing loaded elements
        self.nodes_tags = []
        self.nodes_geometry = []
        self.ways_tags = []
        self.ways_geometry = []
        self.areas_tags = []
        self.areas_geometry = []
        
        self.wanted_nodes = wanted_nodes
        self.wanted_ways = wanted_ways
        self.wanted_areas = wanted_areas
        self.unwanted_nodes_tags = unwanted_nodes_tags
        self.unwanted_ways_tags = unwanted_ways_tags
        self.unwanted_areas_tags = unwanted_areas_tags
        
        # merge always wanted columns (map objects) with additions wanted info columns
        self.nodes_columns = set(wanted_nodes.keys() | node_additional_columns)
        self.way_columns = set(wanted_ways.keys() | way_additional_columns)
        self.area_columns = set(wanted_areas.keys() | area_additional_columns)
        # Create WKT Factory for geometry conversion
        # self.geom_factory =   
        #extract function from libraries - quicker than extracting every time 
        self.geom_factory_linestring = osmium.geom.WKTFactory().create_linestring
        self.geom_factory_polygon = osmium.geom.WKTFactory().create_multipolygon
        self.geom_factory_point = osmium.geom.WKTFactory().create_point
        self.wkt_loads_func = wkt.loads
    @staticmethod
    def _apply_filters_not_allowed(not_allowed_tags, tags, curr_tag_key_inside = None):
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
        if(not not_allowed_tags):
            return True
        for dict_tag_key, unwanted_values in not_allowed_tags.items():
            #not directly inside any tag and curr tag is not in tags => skip
            if(curr_tag_key_inside is None and dict_tag_key not in tags): continue
            
            # Checking if map feature meets the defined conditions
            if(isinstance(unwanted_values, dict)):
                # The unwanted values are more nested => need to go down further
                next_tag_key_inside = None
                if(dict_tag_key in tags): # dict_tag_key is tag_key (column name) in tags
                    next_tag_key_inside = dict_tag_key
               
                else:  # tag_key_value after tag_key
                    # check if the value inside the current key matches the dict tag key - map feature meet this condition
                    curr_tag_key_value = tags.get(curr_tag_key_inside)
                    if(curr_tag_key_value != dict_tag_key): 
                        continue # map feature does not meet this conditon for going to this next recursion level => skip
                
                # map feature meet this condition go to next recursion level
                return_value = OsmDataParser._apply_filters_not_allowed(unwanted_values, tags, next_tag_key_inside)
                if(return_value): continue # unwanted value not found in this branch try to find in some other tag (can't have a single one)
                return False # one unwanted was found, tags are not valid
            
            # map feature meets the defined conditions 
            # Check map feature for illegal values in dict_tag_key columns
            dict_key_value = tags.get(dict_tag_key)
            if(dict_key_value is not None):
                # list of unwanted values is empty ban all values, else check for specific value
                if not unwanted_values or dict_key_value in unwanted_values:
                    return False      
        # does not conntain unwanted tags  
        return True  
          
    @staticmethod
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
            feature = tags.get(features_category)
            if feature is not None:
                # features_values is empty list => get all from features_category else check if feature is wanted
                if not wanted_features_values or feature in wanted_features_values: 
                    return True      
        # map feature is not in wanted features        
        return False
    
    
    def node(self, node):
        if OsmDataParser._apply_filters(self.wanted_nodes, node.tags):
            try:
                # convert osmium node to wkt str format and than to shapely point geometry
                shapely_geometry = self.wkt_loads_func(self.geom_factory_point(node)) 
                filtered_tags = {tag_key: tag_value for tag_key, tag_value in node.tags if tag_key in self.nodes_columns}
                self.nodes_geometry.append(shapely_geometry)
                self.nodes_tags.append(filtered_tags)
            except RuntimeError as e:
                warnings.warn(f"Invalid node geometry: {e}")
                return
            except Exception as e:
                warnings.warn(f"Error in node function - osm file processing: {e}")
                return
            

    def way(self, way):
        if OsmDataParser._apply_filters(self.wanted_ways, way.tags) and OsmDataParser._apply_filters_not_allowed(self.unwanted_ways_tags, way.tags):
            try:
                # convert osmium way to wkt str format and than to shapely linestring geometry
                shapely_geometry = self.wkt_loads_func(self.geom_factory_linestring(way)) 
                filtered_tags = {tag_key: tag_value for tag_key, tag_value in way.tags if tag_key in self.way_columns}
                self.ways_geometry.append(shapely_geometry)
                self.ways_tags.append(filtered_tags)
            except RuntimeError as e:
                warnings.warn(f"Invalid way geometry: {e}")
                return
            except Exception as e:
                warnings.warn(f"Error in way function - osm file processing: {e}")
                return
            
    def area(self, area):
        if OsmDataParser._apply_filters(self.wanted_areas, area.tags) and OsmDataParser._apply_filters_not_allowed(self.unwanted_areas_tags, area.tags):
            try:
                shapely_geometry = self.wkt_loads_func(self.geom_factory_polygon(area)) #convert osmium area to wkt str format and than to shapely polygon/multipolygon geometry 
                filtered_tags = {tag_key: tag_value for tag_key, tag_value in area.tags if tag_key in self.area_columns}
                self.areas_geometry.append(shapely_geometry)
                self.areas_tags.append(filtered_tags)
            except RuntimeError as e:
                warnings.warn(f"Invalid area geometry: {e}")
                return
            except Exception as e:
                warnings.warn(f"Error in area function - osm file processing: {e}")
                return
            
    @time_measurement_decorator("gdf creating")
    def create_gdf(self, epsg_number):
        nodes_gdf = gpd.GeoDataFrame(pd.DataFrame(self.nodes_tags).assign(geometry=self.nodes_geometry), crs=f"EPSG:{epsg_number}")
        ways_gdf = gpd.GeoDataFrame(pd.DataFrame(self.ways_tags).assign(geometry=self.ways_geometry), crs=f"EPSG:{epsg_number}")
        areas_gdf = gpd.GeoDataFrame(pd.DataFrame(self.areas_tags).assign(geometry=self.areas_geometry), crs=f"EPSG:{epsg_number}")

        for column, _ in self.wanted_nodes.items():
            if(column in nodes_gdf):
                nodes_gdf[column] = nodes_gdf[column].astype("category")
            
        for column, _ in self.wanted_ways.items():
            if(column in ways_gdf):
                ways_gdf[column] = ways_gdf[column].astype("category")
                
        for column, _ in self.wanted_areas.items():
            if(column in areas_gdf):
                areas_gdf[column] = areas_gdf[column].astype("category")
        # print(nodes_gdf.memory_usage(deep=True))
        # print(ways_gdf.memory_usage(deep=True))
        # print(areas_gdf.memory_usage(deep=True))
        print(f"nodes:{nodes_gdf.memory_usage(deep=True).sum()},  ways: {ways_gdf.memory_usage(deep=True).sum()},  areas: {areas_gdf.memory_usage(deep=True).sum()},combined: {nodes_gdf.memory_usage(deep=True).sum() + ways_gdf.memory_usage(deep=True).sum() + areas_gdf.memory_usage(deep=True).sum()}")
            
        return nodes_gdf, ways_gdf, areas_gdf
    
    def get_required_area_gdf(self):
        return self.reqired_area_polygon
    
    def clear_gdf(self):
        self.nodes_geometry.clear()
        self.nodes_tags.clear()
        self.ways_geometry.clear()
        self.ways_tags.clear()
        self.areas_geometry.clear()
        self.areas_tags.clear()