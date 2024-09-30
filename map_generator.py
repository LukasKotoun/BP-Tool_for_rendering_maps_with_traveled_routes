from config import *
import osmium
import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely import wkt, geometry
from shapely.geometry import LineString, MultiLineString
import numpy as np

import matplotlib.pyplot as plt
import time
from typing import Union, List, Tuple
import subprocess
import tempfile
import sys


def time_measurement_decorator(timer_name):
    def inner(func):
        def wrapper(*args,**kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time= time.time()
            elapsed_time = end_time - start_time
            print(f"{timer_name} time: {elapsed_time*1000:.6f} ms")
            return result
        return wrapper
    return inner




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
        
    
    @time_measurement_decorator("gdf creating")
    def create_gdf(self):
        # todo check if directly creating geo data frame will be better
        
        print(f"AREA polygons: {sys.getsizeof(self.area_geometry)}, tags: {sys.getsizeof(self.area_tags)}")
        print(f"WAY polygons: {sys.getsizeof(self.way_geometry)}, tags: {sys.getsizeof(self.way_tags)}")
        ways_gdf = gpd.GeoDataFrame(pd.DataFrame(self.way_tags).assign(geometry=self.way_geometry), crs="EPSG:4326")
        areas_gdf = gpd.GeoDataFrame(pd.DataFrame(self.area_tags).assign(geometry=self.area_geometry), crs="EPSG:4326")
        print(f"ways: {sys.getsizeof(ways_gdf)},  areas: {sys.getsizeof(areas_gdf)}, combined: {sys.getsizeof(ways_gdf) + sys.getsizeof(areas_gdf)}")
        return ways_gdf, areas_gdf
    
    
    def clear_gdf(self):
        self.way_geometry.clear()
        self.way_tags.clear()
        self.area_geometry.clear()
        self.area_tags.clear()
            

#todo argument parsin - jmena souboru + kombinace flagu podle složitosti zpracování (bud flag na vypnutí extractu nebo podle zadaného vystupního souboru)
class ArgumentParsing:
    def __init__():
        pass
    

class GdfUtils:
    @staticmethod
    def get_total_bounds(*gdfs):
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
        
    @staticmethod
    def get_map_size_gdf(*gdfs): 
        gdf_total_bounds = GdfUtils.get_total_bounds(*gdfs)
        latitude = gdf_total_bounds['east'] - gdf_total_bounds['west']
        longitude = gdf_total_bounds['north'] - gdf_total_bounds['south']
        return max(latitude, longitude)
    
    def get_map_size_bounds(gdf_total_bounds):
        latitude = gdf_total_bounds['east'] - gdf_total_bounds['west']
        longitude = gdf_total_bounds['north'] - gdf_total_bounds['south']
        return max(latitude, longitude)
    @staticmethod
    def sort_gdf_by_column(gdf, column_name, ascending = True):
        if(column_name in gdf):
            return gdf.sort_values(by=column_name, ascending = ascending)
        print("cannot sort - unexisting column name")
        return gdf
    # def expand_line_to_polygon(gdf_to_expand, )

    # @staticmethod
    # def filter_by(filter, gdf):
    #     pass
    #todo def negativ
    # def filter_by(filter, gdf):
    #todo def both - return (pos,neg)
    # def filter_by(filter, gdf):
    
    @staticmethod
    def buffer_gdf_same_distance(gdf, distance, resolution = 16, cap_style = 'round', join_style = 'round'):
        gdf_mercator_projected  = gdf.to_crs("Web Mercator") #! web mercator - 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(distance,resolution = resolution, cap_style= cap_style, join_style = join_style) 
        return gdf_mercator_projected.to_crs(gdf.crs)

    @staticmethod
    @time_measurement_decorator("buffering")
    def buffer_gdf_column_value_distance(gdf, column_key, additional_padding = 0, resolution = 16, cap_style = 'round', join_style = 'round'):
        gdf_mercator_projected  = gdf.to_crs("Web Mercator") #! web mercator - 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected.apply(
            lambda row: row['geometry'].buffer(row[column_key] + additional_padding,resolution = resolution, cap_style= cap_style, join_style = join_style), axis=1
            ) 
        return gdf_mercator_projected.to_crs(gdf.crs)


        
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
    
    def assign_styles_to_gdf(self, gdf, filters_for_gdf_categories, wanted_styles):
        gdf_available_styles = self.filter_category_styles(filters_for_gdf_categories, wanted_styles)
        if(gdf_available_styles):
            styles_columns = gdf.apply(lambda row: self.assign_styles_to_row(row, gdf_available_styles, wanted_styles), axis=1).tolist()
            return gdf.join(pd.DataFrame(styles_columns))
        print("assign_styles_to_gdf: avilable styles are empty")
        return gdf

    def style_striped_railway_background(self, railways_rail_gdf, aditional_styles_to_assign =[]):
        if aditional_styles_to_assign:
            railways_rail_gdf = self.assign_styles_to_gdf(railways_rail_gdf, {'railway': True}, aditional_styles_to_assign)
        return self.gdf_utils.buffer_gdf_column_value_distance(railways_rail_gdf, "linewidth", 0.1)
#    
    
class MapPlotter:
    def __init__(self, gdf_utils, geo_data_styler, ways_gdf, areas_gdf, reqired_map_area, general_default_styles):
        self.gdf_utils = gdf_utils
        self.geo_data_styler = geo_data_styler
        self.ways_gdf = ways_gdf
        self.areas_gdf = areas_gdf
        self.reqired_map_area = reqired_map_area
        self.reqired_map_area_gdf = gpd.GeoDataFrame(geometry=[self.reqired_map_area], crs="EPSG:4326")

        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        self.reqired_map_area_gdf.plot(ax=self.ax, color=general_default_styles['color'], linewidth=1)
    
    def plot_ways(self):
        
        # map_longest_side_lenght = get_map_size(gdf_total_bounds)
        mapsize = self.gdf_utils.get_map_size_gdf(self.reqired_map_area_gdf)
        # self.ways_gdf = split_lines_into_segments(self.ways_gdf,mapsize/150)
       
        
        self.ways_gdf = self.gdf_utils.buffer_gdf_column_value_distance(self.ways_gdf,'linewidth', resolution=8)
        condition = self.ways_gdf['railway'].isin(['rail', 'tram'])
        rails = self.ways_gdf[condition].reset_index()
        self.ways_gdf = self.ways_gdf[~condition].reset_index()
        self.ways_gdf.plot(ax=self.ax, color=self.ways_gdf['color'], alpha=1,edgecolor='None', antialiased=True,pickradius=0, snap = False)
        
        
        #highway
        #waterway - nic
        #railways
        
        # areas_gdf = self.geo_data_styler.assign_styles_to_gdf(rails, area_filters, ['colors'])
        # print(areas_gdf)

        # rails_bg = self.geo_data_styler.style_striped_railway_background(rails,['bg_color'])
        # rails_bg.plot(ax=self.ax, color=rails_bg['bg_color'], alpha=1)
        rails.plot(ax=self.ax, color=rails['color'], linestyle=(0, (5, 5)) , alpha=1, hatch ="xxxx")
        
        
        #prevest na polygon, přes polygon nakreslit čáru se stylem - -
        #potrebuji vyfiltrovat, nechat polygon i linestring 
        
        
        # plot with linewidth
        

        # plot ways outlines
        # ways_gdf.plot(ax=ax, color='none', edgecolor='black', linewidth=0.1, zorder=2)
        # Plot polygon edges (buffered geometries)

        # Overlay filled polygons (if you want to visualize the filled area as well)
        # ways_gdf.plot(ax=ax, color='lightgreen', alpha=0.5, edgecolor='black', linewidth = 0.1)
        # edge_ways.plot(ax=ax, color="gray", alpha=0.8)

        # condition = ways_gdf['highway'].notnull()
        # filtered_gdf = ways_gdf[condition]
        # remaining_gdf = ways_gdf[~condition]
    def plot_areas(self):
        self.areas_gdf.plot(ax=self.ax, color=self.areas_gdf['color'], alpha=1)
        pass
   
    def clip(self, whole_area_bounds, clipped_area_color = 'white'):
        #clip
        whole_area_polygon = geometry.Polygon([
            (whole_area_bounds['east'], whole_area_bounds['south']),  
            (whole_area_bounds['east'], whole_area_bounds['north']),  
            (whole_area_bounds['west'], whole_area_bounds['north']),  
            (whole_area_bounds['west'], whole_area_bounds['south']),  
            (whole_area_bounds['east'], whole_area_bounds['south'])   # Closing the polygon
        ])

        clipping_polygon = whole_area_polygon.difference(self.reqired_map_area)
        # if isinstance(clipping_polygon, geometry.Polygon):
        clipping_polygon = geometry.MultiPolygon([clipping_polygon])
        clipping_polygon = gpd.GeoDataFrame(geometry=[clipping_polygon], crs="EPSG:4326")
        
        clipping_polygon.plot(ax=self.ax, color=clipped_area_color, alpha=1, zorder=3)
        
    
    def plot_map_boundary(self):
        self.reqired_map_area_gdf.boundary.plot(ax=self.ax, color='black', linewidth=1, zorder=3)

    
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
        

@time_measurement_decorator("main")
def main():
    osm_dir = './osm_files/'
    # place_osm = 'vys'
    place_osm = 'brno'
    # place_name = 'Vysočina, Czech Republic'
    place_name = 'Brno, Czech Republic'
    osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{place_osm}.osm.pbf',f'{place_name}')

    osm_file_name, reqired_map_area = osm_data_preprocessor.extract_area()
    osm_file_parser = OsmDataParser(way_filters,area_filters)
    osm_file_parser.apply_file(osm_file_name)
    ways_gdf, areas_gdf = osm_file_parser.create_gdf()
    osm_file_parser.clear_gdf()

    geo_data_styler = GeoDataStyler(GdfUtils, CATEGORIES_STYLES, GENERAL_DEFAULT_STYLES)

    #set default common styles
    ways_gdf = geo_data_styler.assign_styles_to_gdf(ways_gdf, way_filters, ['color', 'zindex', 'linewidth'])
    areas_gdf = geo_data_styler.assign_styles_to_gdf(areas_gdf, area_filters, ['color', 'zindex'])
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf,'zindex')
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf,'zindex')


    #!edges
    # gdf_projected = ways_gdf.to_crs("Web Mercator") # web mercator
    # # gdf_projected['geometry'] = gdf_projected['geometry'].buffer(4) 
    # gdf_projected['geometry'] = gdf_projected.apply(
    #     lambda row: row['geometry'].buffer(0.0000000001), axis=1
    # )
    # edge_ways = gdf_projected.to_crs(ways_gdf.crs)


    map_plotter = MapPlotter(GdfUtils, geo_data_styler, ways_gdf, areas_gdf, reqired_map_area, GENERAL_DEFAULT_STYLES)
    map_plotter.plot_areas()
    map_plotter.plot_ways()

    total_gdf_bounds = GdfUtils.get_total_bounds(ways_gdf,areas_gdf)
    map_plotter.clip(total_gdf_bounds)
    #GdfUtils.get_total_bounds_polygon(reqired_map_area)
    map_plotter.zoom(reqired_map_area.bounds)
    map_plotter.plot_map_boundary()
    map_plotter.generate_pdf(f'./pdfs/{place_osm}')
    map_plotter.show_plot()

if __name__ == "__main__":
    main()
    
    
    
    
    
