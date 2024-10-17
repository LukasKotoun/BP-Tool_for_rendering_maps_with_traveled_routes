from shapely import geometry
import geopandas as gpd
import osmnx as ox
import pygeoops

from config import * 
from modules.common_helpers import time_measurement_decorator

class GdfUtils:
    @staticmethod
    def get_bounds_gdf(*gdfs):
        west = float('inf')
        south = float('inf')
        east = float('-inf')
        north = float('-inf')
        
        for gdf in gdfs:
            bounds = gdf.total_bounds #[WorldSides.WEST, WorldSides.SOUTH, WorldSides.EAST, WorldSides.NORTH]
            west = min(west, bounds[0])
            south = min(south, bounds[1])
            east = max(east, bounds[2])
            north = max(north, bounds[3])
            
        return {
            WorldSides.WEST: west,
            WorldSides.SOUTH: south,
            WorldSides.EAST: east,
            WorldSides.NORTH: north
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
        bounds = polygon.bounds #[WorldSides.WEST, WorldSides.SOUTH, WorldSides.EAST, WorldSides.NORTH]
        return {WorldSides.WEST: bounds[0],
               WorldSides.SOUTH: bounds[1],
               WorldSides.EAST: bounds[2],
               WorldSides.NORTH: bounds[3]}
    
    @staticmethod
    def get_map_size(bounds):
        width, height = GdfUtils.calc_dimensions(bounds)
        if width > height:
            return width
        else:
            return height
        
    @staticmethod
    def get_map_orientation(gdf):
        gdf_meters = gdf.to_crs(epsg=EPSG_METERS_NUMBER)    
        bounds = GdfUtils.get_bounds_gdf(gdf_meters)
        width, height = GdfUtils.calc_dimensions(bounds)
        if width > height:
            return MapOrientation.LANDSCAPE
        else:
            return MapOrientation.PORTRAIT
        
    @staticmethod
    def get_map_size_from_gdf(*gdfs): 
        bounds = GdfUtils.get_bounds_gdf(*gdfs)
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
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.SOUTH]),  
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.NORTH]),  
            (area_bounds[WorldSides.WEST], area_bounds[WorldSides.NORTH]),  
            (area_bounds[WorldSides.WEST], area_bounds[WorldSides.SOUTH]),  
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.SOUTH])   # Closing the polygon
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
    def calc_dimensions(bounds):
        width = bounds[WorldSides.EAST] - bounds[WorldSides.WEST]  # east - west
        height = bounds[WorldSides.NORTH] - bounds[WorldSides.SOUTH]  # north - south
        return width, height
    
    @staticmethod
    def calc_dimensions_gdf(gdf, epgs = None):
        if(epgs is not None):
            gdf = gdf.to_crs(epsg=epgs)    
        bounds = GdfUtils.get_bounds_gdf(gdf)
        width = bounds[WorldSides.EAST] - bounds[WorldSides.WEST]  # east - west
        height = bounds[WorldSides.NORTH] - bounds[WorldSides.SOUTH]  # north - south
        return width, height
    
    
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
    
