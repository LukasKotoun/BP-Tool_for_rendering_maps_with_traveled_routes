from config import *
import osmium
import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely import wkt, geometry
import pygeoops
import matplotlib.pyplot as plt
from matplotlib import patheffects
import time
from typing import Union, List, Tuple
import subprocess
import tempfile
import sys
import os
#!!! todo separate to files

def time_measurement_decorator(timer_name):
    def wrapper(func):
        def inner(*args,**kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time= time.time()
            elapsed_time = end_time - start_time
            print(f"{timer_name} time: {elapsed_time*1000:.6f} ms")
            return result
        return inner
    return wrapper


class OsmDataPreprocessor:
    #, area: Union[str, List[Tuple[float, float]]]
    def __init__(self, osm_input_file: str, osm_output_file : str = None):
        self.osm_input_file = osm_input_file # Can be a string (place name) or a list of coordinates
        self.osm_output_file = osm_output_file
    #todo
    def check_files_validity():
        pass

    def extract_area(self, reqired_area_gdf):
        #todo check file validity - if file exists
        if self.osm_output_file:
            
            temp_geojson_path = self.create_tmp_geojson(reqired_area_gdf)
            command = [
                'osmium', 'extract',
                '-p', temp_geojson_path,
                self.osm_input_file,
                '-o', self.osm_output_file
            ]
            #todo catch if file osm file not exist
            subprocess.run(command, check=True)
            return self.osm_output_file
        else:
            return self.osm_input_file
        
    def create_tmp_geojson(self, reqired_area_gdf):
        #create tmp file for osmium extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson:
            reqired_area_gdf.to_file(temp_geojson.name, driver="GeoJSON")
            return temp_geojson.name
        


class OsmDataParser(osmium.SimpleHandler):
    #todo add filters as arg
    def __init__(self, way_filters, area_filters, unwanted_ways_tags, unwanted_areas_tags,
                 way_additional_columns = [], area_additional_columns = [], reqired_map_area_name = None,
                 get_required_area_from_osm = False):
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
                #todo filtering ... tag z apply_filters + adition tags? - pokud bude kontrola ze nebude víckrát tak není potřeba - performace test 
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
    def create_gdf(self):        
        print(f"AREA polygons: {sys.getsizeof(self.area_geometry)}, tags: {sys.getsizeof(self.area_tags)}")
        print(f"WAY polygons: {sys.getsizeof(self.way_geometry)}, tags: {sys.getsizeof(self.way_tags)}")
        ways_gdf = gpd.GeoDataFrame(pd.DataFrame(self.way_tags).assign(geometry=self.way_geometry), crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        areas_gdf = gpd.GeoDataFrame(pd.DataFrame(self.area_tags).assign(geometry=self.area_geometry), crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        print(f"ways: {sys.getsizeof(ways_gdf)},  areas: {sys.getsizeof(areas_gdf)}, combined: {sys.getsizeof(ways_gdf) + sys.getsizeof(areas_gdf)}")
        return ways_gdf, areas_gdf
    
    def get_required_area_gdf(self):
        return self.reqired_area_polygon
    
    def clear_gdf(self):
        self.way_geometry.clear()
        self.way_tags.clear()
        self.area_geometry.clear()
        self.area_tags.clear()
            

class GdfUtils:
    @staticmethod
    def get_gdf_bounds(*gdfs):
        west = float('inf')
        south = float('inf')
        east = float('-inf')
        north = float('-inf')
        
        for gdf in gdfs:
            bounds = gdf.total_bounds #[WordSides.WEST, WordSides.SOUTH, WordSides.EAST, WordSides.NORTH]
            west = min(west, bounds[0])
            south = min(south, bounds[1])
            east = max(east, bounds[2])
            north = max(north, bounds[3])
            
        return {
            WordSides.WEST: west,
            WordSides.SOUTH: south,
            WordSides.EAST: east,
            WordSides.NORTH: north
            }
    @staticmethod
    def get_area_gdf(area):
        if isinstance(area, str): 
            if area.endswith('.geojson'): 
                reqired_area_gdf = gpd.read_file(area) # Get area from geojson file
                if reqired_area_gdf.empty:
                    raise ValueError("Given GeoJSON file is empty.")
                return area, reqired_area_gdf
            else:
                try:
                    reqired_area_gdf = ox.geocode_to_gdf(area)  # Get from place name
                except:
                    #todo if not found error - exit program
                    #if internet connection error - find in osm file
                    raise ValueError("The requested location has not been found.")
                if(reqired_area_gdf.empty):
                    raise ValueError("The requested location has not been found.")

        elif isinstance(area, list): #get area from coordinates
            #todo try catch...
            area_polygon = geometry.Polygon(area)
            reqired_area_gdf = gpd.GeoDataFrame(geometry=[area_polygon], crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        else: #area cannot be created
            raise ValueError("Invalid area")
        return reqired_area_gdf
    @staticmethod
    def get_polygon_bounds(polygon):
        bounds = polygon.bounds #[WordSides.WEST, WordSides.SOUTH, WordSides.EAST, WordSides.NORTH]
        return {WordSides.WEST: bounds[0],
               WordSides.SOUTH: bounds[1],
               WordSides.EAST: bounds[2],
               WordSides.NORTH: bounds[3]}
    
    @staticmethod
    def get_map_size(bounds):
        width = bounds[WordSides.EAST] - bounds[WordSides.WEST]
        height = bounds[WordSides.NORTH] - bounds[WordSides.SOUTH]
        if width > height:
            return width
        else:
            return height
    @staticmethod
    def get_map_orientation(gdf):
        gdf_meters = gdf.to_crs(epsg=EPSG_METERS_NUMBER)    
        bounds = GdfUtils.get_gdf_bounds(gdf_meters)
        width = bounds[WordSides.EAST] - bounds[WordSides.WEST]
        height = bounds[WordSides.NORTH] - bounds[WordSides.SOUTH]
        if width > height:
            return MapOrientation.LANDSCAPE
        else:
            return MapOrientation.PORTRAIT
        
    @staticmethod
    def get_map_size_from_gdf(*gdfs): 
        bounds = GdfUtils.get_gdf_bounds(*gdfs)
        return GdfUtils.get_map_size(bounds)
 
    @staticmethod
    def sort_gdf_by_column(gdf, column_name, ascending = True):
        if(gdf.empty):
            return gdf
        if(column_name in gdf):
            return gdf.sort_values(by=column_name, ascending = ascending)
        print("cannot sort - unexisting column name") #todo error handling
        return gdf
    
    @staticmethod
    def is_polygon_inside_bounds(area_bounds, polygon):
        polygon_from_bounds = geometry.Polygon([
            (area_bounds[WordSides.EAST], area_bounds[WordSides.SOUTH]),  
            (area_bounds[WordSides.EAST], area_bounds[WordSides.NORTH]),  
            (area_bounds[WordSides.WEST], area_bounds[WordSides.NORTH]),  
            (area_bounds[WordSides.WEST], area_bounds[WordSides.SOUTH]),  
            (area_bounds[WordSides.EAST], area_bounds[WordSides.SOUTH])   # Closing the polygon
        ])
        return polygon_from_bounds.contains(polygon)
    
    # todo to one filter creation
    @staticmethod
    def filter_gdf_in(gdf, att_name, att_values = []):
        if (att_values and att_name in gdf):
            condition = gdf[att_name].isin(att_values)
            return gdf[condition].reset_index(drop=True), gdf[~condition].reset_index(drop=True) 
        elif(att_name in gdf):
            condition = gdf[att_name].notna()
            return gdf[condition].reset_index(drop=True), gdf[~condition].reset_index(drop=True)
        return gpd.GeoDataFrame(geometry=[]), gdf
    
    @staticmethod
    def filter_gdf_not_in(gdf, att_name, att_values = []):
        if(att_values and att_name in gdf):
            condition = gdf[att_name].isin(att_values)
            return gdf[~condition].reset_index(drop=True), gdf[condition].reset_index(drop=True)
        elif(att_name in gdf):
            condition = gdf[att_name].notna()
            return gdf[~condition].reset_index(drop=True), gdf[condition].reset_index(drop=True)
        return gdf, gpd.GeoDataFrame(geometry=[])
    
    #todo use one filter creation and than add with 'and' all ways that are longer, that will leave false with all that i want...
    @staticmethod
    @time_measurement_decorator("short ways filter")
    def filter_short_ways(gdf, min_lenght = 2):
        gdf_mercator_projected  = gdf.to_crs(epsg=EPSG_METERS_NUMBER) 
        condition = gdf_mercator_projected.geometry.length > min_lenght
        filtered_gdf_mercator_projected = gdf_mercator_projected[condition]
        return filtered_gdf_mercator_projected.to_crs(epsg=gdf.crs)
    
    @staticmethod
    def buffer_gdf_same_distance(gdf, distance, resolution = 16, cap_style = 'round', join_style = 'round'):
        gdf_mercator_projected  = gdf.to_crs(epsg=EPSG_METERS_NUMBER) 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(distance,resolution = resolution, cap_style= cap_style, join_style = join_style) 
        return gdf_mercator_projected.to_crs(epsg=gdf.crs)

    @staticmethod
    def buffer_gdf_column_value_distance(gdf, column_key, additional_padding = 0, resolution = 16, cap_style = 'round', join_style = 'round'):
        gdf_mercator_projected  = gdf.to_crs(EPSG_METERS_NUMBER) #! web mercator - 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected.apply(
            lambda row: row['geometry'].buffer(row[column_key] + additional_padding,resolution = resolution, cap_style= cap_style, join_style = join_style), axis=1
            ) 
        return gdf_mercator_projected.to_crs(epsg=gdf.crs)
    
    @staticmethod
    @time_measurement_decorator("aggregating")
    def aggregate_close_lines(gdf, buffer_distance = 5):
        if(gdf.empty):
            return gdf
        gdf_mercator_projected  = gdf.to_crs(epsg=EPSG_METERS_NUMBER) 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(buffer_distance) 
        
        #https://stackoverflow.com/questions/73566774/group-by-and-combine-intersecting-overlapping-geometries-in-geopandas
        gdf_merged = gdf_mercator_projected.sjoin(gdf_mercator_projected, how='left', predicate="intersects")
        gdf_merged.columns = gdf_merged.columns.str.replace('_left', '',regex=False).str.replace('_right', '', regex=False)
        gdf_merged = gdf_merged.loc[:, ~gdf_merged.columns.duplicated()]

        gdf_merged_diss = gdf_merged.dissolve()
        gdf_merged_diss = gdf_merged_diss.reset_index(drop=True).dissolve()
        gdf_merged_diss['geometry'] = pygeoops.centerline(gdf_merged_diss['geometry'], min_branch_length=buffer_distance * 10)
        gdf_merged_diss = gdf_merged_diss.explode(column='geometry', ignore_index=True)
        gdf_merged_diss = gdf_merged_diss.to_crs(epsg=gdf.crs)
        return gdf_merged_diss
    

        
class GeoDataStyler:
    def __init__(self, gdf_utils , categories_styles, general_default_styles):  
        self.gdf_utils = gdf_utils
        self.categories_styles = categories_styles
        self.general_default_styles = general_default_styles
    
    def assign_styles_to_row(self, row, available_styles, wanted_styles):
        assigned_styles = {}
        for category_name, (category_map, category_default_styles) in available_styles.items():
            if category_name in row and pd.notna(row[category_name]):
                category_styles = category_map.get(row[category_name], category_default_styles) #retrieve record for a specific key (e.g. landues) and value (e.g. forest) combination in the map or retrieve the default value for that key.
                for style_key, default_style in category_default_styles.items(): # select individual values from the category styles or use default values if there are none individual in the record
                    category_style = category_styles.get(style_key)
                    assigned_styles[style_key] = category_style if category_style is not None else default_style 
                # one category was found - row can be in one category only 
                return assigned_styles
        # if category_name is not in row or nan in row and all posible categories was tryed return general styles but wanted only   
        return {style_key: self.general_default_styles[style_key] for style_key in wanted_styles  
                                                            if style_key in category_default_styles}
    
    def filter_category_styles(self, wanted_categories,wanted_styles):
        filtered_categories_styles = {}
        for category_name, (category_map, category_default_styles) in self.categories_styles.items():
            if category_name in wanted_categories: #check if category can be in gdf
                category_filter = wanted_categories[category_name]
                if category_filter: #get style for only some items in category
                    filtered_category_styles = {      
                        category_item: {style_key: item_styles[style_key] for style_key in wanted_styles if style_key in item_styles} #filter only wanted styles for item in category (e.g. color)
                        for category_item, item_styles in category_map.items()
                        if category_item in category_filter     #filter wanted items
                    }
                else:  #get style for all items in category
                    filtered_category_styles = {
                        category_item: {style_key: item_styles[style_key] for style_key in wanted_styles if style_key in item_styles} #filter only wanted styles for item in category (e.g. color)
                        for category_item, item_styles in category_map.items()
                    }
                filtered_categories_styles[category_name] = (filtered_category_styles, 
                                                            {style_key: category_default_styles[style_key] for style_key in wanted_styles 
                                                            if style_key in category_default_styles}) #store filterd category with wanted default styles
        return filtered_categories_styles
    
    def assign_styles_to_gdf(self, gdf, wanted_categories, wanted_styles):
        if(gdf.empty):
            return gdf
        gdf_available_styles = self.filter_category_styles(wanted_categories, wanted_styles)
        if(gdf_available_styles):
            styles_columns = gdf.apply(lambda row: self.assign_styles_to_row(row, gdf_available_styles, wanted_styles), axis=1).tolist()
            return gdf.join(pd.DataFrame(styles_columns))
        print("assign_styles_to_gdf: avilable styles are empty")
        return gdf
    
 
    


class Plotter:
    def __init__(self, gdf_utils, geo_data_styler, ways_gdf, areas_gdf, gpxs_gdf,
                 requred_area_gdf, map_bg_color, paper_size_mm):
        self.gdf_utils = gdf_utils
        self.geo_data_styler = geo_data_styler
        self.ways_gdf = ways_gdf
        self.areas_gdf = areas_gdf
        self.gpxs_gdf = gpxs_gdf
        self.reqired_area_gdf = requred_area_gdf 
        self.paper_size_mm = paper_size_mm
        self.init_plot(map_bg_color)
        
        
    def init_plot(self, map_bg_color):
        self.fig, self.ax = plt.subplots(figsize=(self.paper_size_mm[0]/25.4,self.paper_size_mm[1]/25.4)) #convert mm to inch
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # No margins
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color, linewidth=1)
        
        
    def __plot_highways(self,highways_gdf):
        if(highways_gdf.empty or StyleKey.COLOR not in highways_gdf and StyleKey.LINEWIDTH not in highways_gdf):
            return
        
        for line, color, linewidth in zip(highways_gdf.geometry, highways_gdf[StyleKey.COLOR], highways_gdf[StyleKey.LINEWIDTH]):
            x, y = line.xy
            self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle = 'round')
            
    def __plot_waterways(self,waterways_gdf):
        if(waterways_gdf.empty or StyleKey.COLOR not in waterways_gdf and StyleKey.LINEWIDTH not in waterways_gdf):
            return
        waterways_gdf.plot(ax = self.ax,color=waterways_gdf[StyleKey.COLOR], linewidth = waterways_gdf[StyleKey.LINEWIDTH])
        
        # for line, color, linewidth in zip(waterways_gdf.geometry, waterways_gdf[StyleKey.COLOR], waterways_gdf[StyleKey.LINEWIDTH]):
        #     x, y = line.xy
        #     self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle='round')

                    
            
    def __plot_railways(self,railways_gdf, rail_bg_width_offset, tram_second_line_spacing):
        #todo change ploting style
        if(railways_gdf.empty or StyleKey.COLOR not in railways_gdf or StyleKey.LINEWIDTH not in railways_gdf):
            return
        
        tram_gdf, rails_gdf = self.gdf_utils.filter_gdf_in(railways_gdf, 'railway', ['tram'])
        
        # tram_gdf = self.gdf_utils.aggregate_close_lines(tram_gdf,5)
        # rails_gdf = self.gdf_utils.aggregate_close_lines(rails_gdf,5)
        for line, color, linewidth in zip(tram_gdf.geometry, tram_gdf[StyleKey.COLOR], tram_gdf[StyleKey.LINEWIDTH]):
            x, y = line.xy #todo len to config/style
            self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle='round', alpha=0.6,path_effects=[
            patheffects.withTickedStroke(angle=-90, spacing=tram_second_line_spacing, length=0.05),
            patheffects.withTickedStroke(angle=90, spacing=tram_second_line_spacing, length=0.05)])
        
        if(StyleKey.BGCOLOR not in rails_gdf):
            rails_gdf = self.geo_data_styler.assign_styles_to_gdf(rails_gdf, {'railway': []}, [StyleKey.BGCOLOR])
            # rails_gdf = self.geo_data_styler.assign_styles_to_gdf(rails_gdf, {'railway': ['rail']}, [StyleKey.BGCOLOR]) #todo solve double adding
       
        for line, color, bg_color,linewidth in zip(rails_gdf.geometry, rails_gdf[StyleKey.COLOR],rails_gdf[StyleKey.BGCOLOR], rails_gdf[StyleKey.LINEWIDTH]):
            x, y = line.xy
            self.ax.plot(x, y, color=bg_color, linewidth = linewidth + rail_bg_width_offset)
            self.ax.plot(x, y, color=color, linewidth =  linewidth ,linestyle=(0,(5,5)))
    @time_measurement_decorator("wayplot")            
    def plot_ways(self, preview_area_gdf = None):
        #todo count with pdf size
        #todo to func - get width and length
        gdf_mercator_projected  = preview_area_gdf.to_crs(epsg=EPSG_METERS_NUMBER)
        bounds = gdf_mercator_projected.total_bounds
        # bounds = gdf_mercator_projected.total_bounds / 1000
        x_range = bounds[2] - bounds[0]  # east - west
        y_range = bounds[3] - bounds[1]  # north - south
        map_scaling_factor = (x_range + y_range) / 2  # average extent
        paper_scaling_factor = (self.paper_size_mm[0] + self.paper_size_mm[1])
        
        
        
        # LINE_TRANSFORM_CONSTANT = 0.008
        scaling_factor =  paper_scaling_factor / map_scaling_factor
        self.ways_gdf[StyleKey.LINEWIDTH] = self.ways_gdf[StyleKey.LINEWIDTH] * scaling_factor
        
        # bounds = self.reqired_area_gdf.total_bounds
        # x_range = bounds[2] - bounds[0]  # east - west
        # y_range = bounds[3] - bounds[1]  # north - south
        # scaling_factor = (x_range + y_range) / 2  # average extent
        # self.ways_gdf[StyleKey.LINEWIDTH] = self.ways_gdf[StyleKey.LINEWIDTH]  / scaling_factor
        
        
        
        waterways_gdf, rest_gdf = self.gdf_utils.filter_gdf_in(self.ways_gdf, 'waterway')
        self.__plot_waterways(waterways_gdf)
        
        highways_gdf, rest_gdf = self.gdf_utils.filter_gdf_in(rest_gdf, 'highway')
        self.__plot_highways(highways_gdf)
        
        railways_gdf, rest_gdf = self.gdf_utils.filter_gdf_in(rest_gdf, 'railway')
        self.__plot_railways(railways_gdf, 2*scaling_factor,15*scaling_factor)


            
    def plot_areas(self):
        if(StyleKey.COLOR in self.areas_gdf):
            #todo bounds filter
            self.areas_gdf.plot(ax=self.ax, color = self.areas_gdf[StyleKey.COLOR] , alpha=1)
        else:
            pass
    
    def plot_gpxs(self):
        self.gpxs_gdf.plot(ax = self.ax,color="red", linewidth = 0.65)

        
    
    
        #todo to self.reqired
    def clip(self, whole_area_bounds, reqired_area_polygon, clipped_area_color = 'white'):
        #clip
        whole_area_polygon = geometry.Polygon([
            (whole_area_bounds[WordSides.EAST], whole_area_bounds[WordSides.SOUTH]),  
            (whole_area_bounds[WordSides.EAST], whole_area_bounds[WordSides.NORTH]),  
            (whole_area_bounds[WordSides.WEST], whole_area_bounds[WordSides.NORTH]),  
            (whole_area_bounds[WordSides.WEST], whole_area_bounds[WordSides.SOUTH]),  
            (whole_area_bounds[WordSides.EAST], whole_area_bounds[WordSides.SOUTH])   # Closing the polygon
        ])
        clipping_polygon = whole_area_polygon.difference(reqired_area_polygon)
        # clipping_polygon = geometry.MultiPolygon([clipping_polygon])
        clipping_polygon = gpd.GeoDataFrame(geometry=[clipping_polygon], crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        
        clipping_polygon.plot(ax=self.ax, color=clipped_area_color, alpha=1, zorder=3)
        
    
    def plot_map_boundary(self, color = 'black', linewidth = 1):
        self.reqired_area_gdf.boundary.plot(ax=self.ax, color=color, linewidth=linewidth, zorder=3)
        
    #use function to get gdf sizes - same as in ways
    #todo change to names
    def zoom(self, zoom_bounds, zoom_percent_padding = 1):
        zoom_padding = zoom_percent_padding / 100 #convert from percent
        x_buffer = (zoom_bounds[2] - zoom_bounds[0]) * zoom_padding  # 1% of width
        y_buffer = (zoom_bounds[3] - zoom_bounds[1]) * zoom_padding  # 1% of height
        self.ax.set_xlim([zoom_bounds[0] - x_buffer, zoom_bounds[2] + x_buffer])  # Expand x limits
        self.ax.set_ylim([zoom_bounds[1] - y_buffer, zoom_bounds[3] + y_buffer])  # Expand y limits
        
        
    def generate_pdf(self, pdf_name):
        plt.savefig(f'{pdf_name}.pdf', format='pdf', transparent=True)
    
    def show_plot(self):
        plt.show()

#general utils
#return (width, height)
def set_orientation(tuple:Tuple[float,float], wanted_orientation:MapOrientation) -> Tuple[float,float]:
    if(wanted_orientation == MapOrientation.LANDSCAPE):
        return tuple if tuple[0] > tuple[1] else tuple[::-1]
    #portrait
    return tuple if tuple[0] < tuple[1] else tuple[::-1]
#utils
def get_paper_size_mm( map_orientaion,paperSize :PaperSize = PaperSize.A4, wanted_orientation = MapOrientation.AUTOMATIC):
    
    paper_size = paperSize.dimensions
    if(wanted_orientation == MapOrientation.AUTOMATIC):
        return set_orientation(paper_size,map_orientaion)
    elif(wanted_orientation in [MapOrientation.LANDSCAPE, MapOrientation.PORTRAIT]):
        return set_orientation(paper_size,wanted_orientation)
    return paper_size

class GpxProcesser:
    def __init__(self, gpx_folder):
        self.gpx_folder = gpx_folder
        
        #todo add reqired att
    def get_gpxs_gdf(self):
        gpx_list = []
        for file in os.listdir(self.gpx_folder):
            if not file.endswith('.gpx'):
                continue
            gpx_gdf = gpd.read_file(os.path.join(self.gpx_folder,file), layer='tracks', crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
            gpx_gdf['name'] = file
            gpx_list.append(gpx_gdf)
        return gpd.GeoDataFrame(pd.concat(gpx_list, ignore_index=True), crs=f"EPSG:{EPSG_DEGREE_NUMBER}")



@time_measurement_decorator("main")
def main():
    # osm_dir = '/zfs-pool/home/xkotou08/BP/'
    # osm_file = 'cz'
    # place_name = 'Czech Republic'
    osm_dir = './osm_files/'
    osm_file = 'vys'
    place_name = 'Vysočina, Czech Republic'
    
    osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm.pbf')
    # osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm',[(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)]) #island
    # osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm',[(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)]) #afrika
    # osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm.pbf',f'{place_name}',"new osm name")
    get_required_area_from_osm = False #from settings if true dont use reqired_area_gdf, need to send area name for osm cutting
    reqired_area_gdf = GdfUtils.get_area_gdf(place_name)
    preview_area_gdf = GdfUtils.get_area_gdf("Czech Republic")
    

    osm_file_name = osm_data_preprocessor.extract_area(reqired_area_gdf)
    osm_file_parser = OsmDataParser(wanted_ways,wanted_areas,unwanted_ways_tags, unwanted_areas_tags,
                                    reqired_map_area_name=f'{place_name}', get_required_area_from_osm = get_required_area_from_osm)
    @time_measurement_decorator("apply file")
    def t():
        osm_file_parser.apply_file(osm_file_name)
    t()
    
    
    reqired_area_polygon = reqired_area_gdf.unary_union
    ways_gdf, areas_gdf = osm_file_parser.create_gdf()
    osm_file_parser.clear_gdf()
    
    total_gdf_bounds = GdfUtils.get_gdf_bounds(ways_gdf, areas_gdf)
    #check if area is inside osm file
    if(not GdfUtils.is_polygon_inside_bounds(total_gdf_bounds, reqired_area_polygon)):
        #todo error handle class
        print("Selected area map must be inside given osm.pbf file")
        sys.exit()  
    
    
    geo_data_styler = GeoDataStyler(GdfUtils, CATEGORIES_STYLES, GENERAL_DEFAULT_STYLES)
    gpx_processer =  GpxProcesser('./gpxs')
    gpxs_gdf = gpx_processer.get_gpxs_gdf()
    #todo check if gpx go somewhere outside reqired_area
   
        
    # only for some ways categories
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)
    #todo styles for ways and areas separeated
    ways_gdf = geo_data_styler.assign_styles_to_gdf(ways_gdf, wanted_ways, [StyleKey.COLOR, StyleKey.ZINDEX, StyleKey.LINEWIDTH])
    areas_gdf = geo_data_styler.assign_styles_to_gdf(areas_gdf, wanted_areas, [StyleKey.COLOR, StyleKey.ZINDEX])
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    
    map_orientation = GdfUtils.get_map_orientation(reqired_area_gdf)
    #todo check for custom - without paper size
    paper_size_mm = get_paper_size_mm(map_orientation, PAPER_SIZE)
    
    plotter = Plotter(GdfUtils, geo_data_styler, ways_gdf, areas_gdf, gpxs_gdf,
                             reqired_area_gdf,  GENERAL_DEFAULT_STYLES[StyleKey.COLOR], paper_size_mm)
    plotter.plot_areas()
    plotter.plot_ways(reqired_area_gdf)
    plotter.plot_gpxs()
    plotter.clip(total_gdf_bounds, reqired_area_polygon)
    #change to map_orientation
    plotter.zoom(reqired_area_polygon.bounds)
    plotter.plot_map_boundary()
    plotter.generate_pdf(f'./pdfs/{osm_file}a0')
    # plotter.show_plot()
if __name__ == "__main__":
    main()
    
    
    
    
    
