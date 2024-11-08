import warnings

from shapely import geometry
import geopandas as gpd
import pandas as pd
import osmnx as ox
import pygeoops
from geopy.distance import geodesic

from common.map_enums import WorldSides, StyleKey
from common.custom_types import BoundsDict, DimensionsTuple, Point, WantedArea
from common.common_helpers import time_measurement_decorator

class GdfUtils:

    
    @staticmethod
    def get_area_gdf(area: str | list[Point], epsg: int) -> gpd.GeoDataFrame:
        if isinstance(area, str): 
            if area.endswith('.geojson'): 
                reqired_area_gdf: gpd.GeoDataFrame = gpd.read_file(area) # Get area from geojson file
                if reqired_area_gdf.empty:
                    raise ValueError("Given GeoJSON file is empty.")
                return reqired_area_gdf
            else:
                try: 
                    # need internet connection 
                    reqired_area_gdf: gpd.GeoDataFrame = ox.geocode_to_gdf(area)  # Get from place name
                except:
                    raise ValueError("The requested location has not been found.")
                if(reqired_area_gdf.empty):
                    raise ValueError("The requested location has not been found.")

        elif isinstance(area, list): #get area from coordinates
            try:
                area_polygon = geometry.Polygon(area)
                reqired_area_gdf = GdfUtils.create_gdf_from_polygon(area_polygon, epsg)
            except:
                raise ValueError("Invalid area given by list of cordinates.")
        else: #area cannot be created
            raise ValueError("Invalid area format.")
        return reqired_area_gdf
    
        
    @staticmethod
    @time_measurement_decorator("spojeni")
    def get_whole_area_gdf(whole_area: WantedArea, epsg: int) -> gpd.GeoDataFrame:
        
        if (isinstance(whole_area, str) or (isinstance(whole_area, list) and len(whole_area) == 1)  #normal area
            or (isinstance(whole_area, list) and all(isinstance(item, tuple) and len(item) == 2 for item in whole_area))): 
            if((isinstance(whole_area, list) and len(whole_area) == 1)): # one area in list
                return GdfUtils.get_area_gdf(whole_area[0], epsg)
            else:
                return GdfUtils.get_area_gdf(whole_area, epsg)
        elif (isinstance(whole_area, list)): #area from multiple areas
            areas_gdf_list: list[gpd.GeoDataFrame] = []
            for area in whole_area:
                areas_gdf_list.append(GdfUtils.get_area_gdf(area, epsg))
            return pd.concat(areas_gdf_list, ignore_index=True)
        else: #area cannot be created
            raise ValueError("Invalid area format.")
    
    
    @staticmethod
    def get_bounds_gdf(*gdfs: gpd.GeoDataFrame, epsg: int | None = None) -> BoundsDict:
        west = float('inf')
        south = float('inf')
        east = float('-inf')
        north = float('-inf')
        
        for gdf in gdfs:
            gdf_edit = gdf
            if(epsg is not None):
                gdf_edit = gdf.to_crs(epsg=epsg)    
            bounds: tuple[float] = gdf_edit.total_bounds #[WorldSides.WEST, WorldSides.SOUTH, WorldSides.EAST, WorldSides.NORTH]
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
    def combine_rows_gdf(gdf: gpd.GeoDataFrame, epsg: int) -> gpd.GeoDataFrame:
        if(len(gdf) == 1):
            return gdf.to_crs(epsg=epsg)
        return gpd.GeoDataFrame(geometry=[gdf.to_crs(epsg=epsg).geometry.unary_union], crs=f"EPSG:{epsg}")
    
    @staticmethod
    def get_polygon_bounds(polygon: geometry.polygon) -> BoundsDict:
        bounds: tuple[float] = polygon.bounds #[WorldSides.WEST, WorldSides.SOUTH, WorldSides.EAST, WorldSides.NORTH]
        return {WorldSides.WEST: bounds[0],
               WorldSides.SOUTH: bounds[1],
               WorldSides.EAST: bounds[2],
               WorldSides.NORTH: bounds[3]}
        
    @staticmethod
    def get_dimensions_m(bounds: BoundsDict) -> DimensionsTuple:
        northern = (bounds[WorldSides.NORTH], (bounds[WorldSides.WEST] + bounds[WorldSides.EAST]) / 2) 
        southern = (bounds[WorldSides.SOUTH], (bounds[WorldSides.WEST] + bounds[WorldSides.EAST]) / 2)
        eastern = ((bounds[WorldSides.NORTH] + bounds[WorldSides.SOUTH]) / 2, bounds[WorldSides.EAST])  
        western = ((bounds[WorldSides.NORTH] + bounds[WorldSides.SOUTH]) / 2, bounds[WorldSides.WEST])
        width = geodesic(eastern, western).meters        
        height = geodesic(northern, southern).meters
        return width, height
        
    @staticmethod
    def get_dimensions_m_gdf(gdf: gpd.GeoDataFrame) -> DimensionsTuple:        
        bounds = GdfUtils.get_bounds_gdf(gdf)
        return GdfUtils.get_dimensions_m(bounds)
    
    @staticmethod
    def get_dimensions_m_polygon(polygon: gpd.GeoDataFrame) -> DimensionsTuple:
        bounds = GdfUtils.get_polygon_bounds(polygon)
        return GdfUtils.get_dimensions_m(bounds)
    
    @staticmethod
    def get_dimensions(bounds: BoundsDict) -> DimensionsTuple:
        width = abs(bounds[WorldSides.EAST] - bounds[WorldSides.WEST])  # east - west
        height = abs(bounds[WorldSides.NORTH] - bounds[WorldSides.SOUTH])  # north - south
        return width, height
    
    @staticmethod
    def get_dimensions_gdf(gdf: gpd.GeoDataFrame) -> DimensionsTuple:        
        bounds = GdfUtils.get_bounds_gdf(gdf)
        return GdfUtils.get_dimensions(bounds)
    
    @staticmethod
    def get_dimensions_polygon(polygon: gpd.GeoDataFrame) -> DimensionsTuple:
        bounds = GdfUtils.get_polygon_bounds(polygon)
        return GdfUtils.get_dimensions(bounds)
    
    @staticmethod 
    def create_polygon_from_bounds(area_bounds: BoundsDict) -> geometry.polygon:
        return geometry.Polygon([
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.SOUTH]),  
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.NORTH]),  
            (area_bounds[WorldSides.WEST], area_bounds[WorldSides.NORTH]),  
            (area_bounds[WorldSides.WEST], area_bounds[WorldSides.SOUTH]),  
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.SOUTH])   # Closing the polygon
        ])
    
    @staticmethod 
    def create_gdf_from_bounds(area_bounds: BoundsDict, epsg) -> gpd.GeoDataFrame:
        return GdfUtils.create_gdf_from_polygon(GdfUtils.create_polygon_from_bounds(area_bounds), epsg)
    
    @staticmethod 
    def create_gdf_from_polygon(area_polygon: geometry.polygon, epsg) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(geometry=[area_polygon], crs=f"EPSG:{epsg}")
    

    @staticmethod 
    def create_polygon_from_gdf_bounds(*gdfs: gpd.GeoDataFrame, epsg: int | None = None) -> geometry.polygon:
        bounds = GdfUtils.get_bounds_gdf(*gdfs, epsg=epsg)
        return GdfUtils.create_polygon_from_bounds(bounds)
    
    @staticmethod 
    def create_polygon_from_gdf(*gdfs: gpd.GeoDataFrame, epsg: int | None = None) -> geometry.polygon:
        if(len(gdfs) == 1):
            if(epsg is None):
                return gdfs[0].unary_union
            gdf_edit = gdfs[0].to_crs(epsg=epsg)    
            return gdf_edit.unary_union
        else:
            if(epsg is None):
                combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
            else:
                combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs, epsg = epsg)
            return combined_gdf.unary_union
    
    @staticmethod
    def is_polygon_inside_bounds(area_bounds: BoundsDict, polygon: geometry.polygon) -> bool:
        return GdfUtils.is_polygon_inside_polygon(GdfUtils.create_polygon_from_bounds(area_bounds), polygon)

    @staticmethod
    def is_polygon_inside_polygon(inner: geometry.polygon, outer: geometry.polygon) -> bool:
        return outer.contains(inner)
    
    @staticmethod
    def is_point_inside_polygon(point: geometry.point, polygon: geometry.polygon) -> bool:
        return polygon.contains(point)
    
    @staticmethod
    def is_polygon_inside_polygon_threshold(inner: geometry.polygon, outer: geometry.polygon, threshold: float = 0.95):
        bbox_area = inner.area
        intersection_area = inner.intersection(outer).area
        percentage_inside = intersection_area / bbox_area
        return percentage_inside >= threshold

    @staticmethod
    def sort_gdf_by_column(gdf: gpd.GeoDataFrame, column_name: StyleKey, ascending: bool = True) -> gpd.GeoDataFrame:
        if(gdf.empty):
            return gdf
        if(column_name in gdf):
           return gdf.sort_values(by=column_name, ascending = ascending).reset_index(drop=True)
        warnings.warn("Cannot sort - unexisting column name") 
        return gdf
    
    
    @staticmethod
    def create_condition(gdf: gpd.GeoDataFrame, att_name: str, att_values: list[str] = []) -> pd.Series:
        """Create condition for given gdf, return true for every row that have att_name with att_value (if given,
        if not it check for any value (not nan)).
        If att_name is not in gdf it return condition with all false.

        Args:
            gdf (gpd.GeoDataFrame): Gdf to create condition for.
            att_name (str): Name of atribute to condition (will leave true for rows with value on this att column).
            att_values (list[str], optional): Values of att_name (will leave true for rows with this values in att_name column) Defaults to [].

        Returns:
            pd.Series[bool]: condition for given gdf.
        """
        if (att_values and att_name in gdf):
            return gdf[att_name].isin(att_values)
        elif(att_name in gdf):
            return gdf[att_name].notna()
        return gdf.index < 0 #set all to false
    
    @staticmethod
    def filter_gdf_in(gdf: gpd.GeoDataFrame, att_name: str, att_values: list[str] = []) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        condition = GdfUtils.create_condition(gdf, att_name, att_values)
        return gdf[condition].reset_index(drop=True), gdf[~condition].reset_index(drop=True)
       
    @staticmethod
    def filter_gdf_not_in(gdf: gpd.GeoDataFrame, att_name: str, att_values: list[str] = []) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
            condition = GdfUtils.create_condition(gdf, att_name, att_values)
            return gdf[~condition].reset_index(drop=True), gdf[condition].reset_index(drop=True)
    
    @staticmethod
    def filter_gdf_rows_inside_gdf_area(gdf_rows: gpd.GeoDataFrame, gdf_area: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return gdf_rows[gdf_rows.geometry.within(gdf_area.unary_union)].reset_index(drop=True)

    @staticmethod
    #todo use one filter creation and than add with 'and' all ways that are longer, that will leave false with all that i want...
    @time_measurement_decorator("short ways filter")
    def filter_short_ways(gdf: gpd.GeoDataFrame, epsg: int, min_lenght: float = 2) -> gpd.GeoDataFrame:
        
        gdf_mercator_projected = gdf.to_crs(epsg=epsg) 
        condition: pd.Series[bool]  = gdf_mercator_projected.geometry.length > min_lenght
        filtered_gdf_mercator_projected = gdf_mercator_projected[condition]
        return filtered_gdf_mercator_projected.to_crs(epsg=gdf.crs)

    @staticmethod
    def buffer_gdf_same_distance(gdf: gpd.GeoDataFrame, distance: float, epsg: int, resolution: int = 16,
                                 cap_style: str = 'round', join_style: str = 'round') -> gpd.GeoDataFrame:
        gdf_mercator_projected = gdf.to_crs(epsg=epsg) 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(distance,resolution = resolution, cap_style= cap_style, join_style = join_style) 
        return gdf_mercator_projected.to_crs(epsg=gdf.crs)
    
    @staticmethod
    def buffer_gdf_column_value_distance(gdf: gpd.GeoDataFrame, column_key: str, epsg : int, 
                                         additional_padding: float = 0, resolution: int = 16,
                                         cap_style: str = 'round', join_style: str = 'round') -> gpd.GeoDataFrame:
        gdf_mercator_projected = gdf.to_crs(epsg=epsg) 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected.apply(
            lambda row: row['geometry'].buffer(row[column_key] + additional_padding,resolution = resolution,
                                               cap_style = cap_style, join_style = join_style), axis=1
            ) 
        return gdf_mercator_projected.to_crs(epsg=gdf.crs)
    
    @staticmethod
    def aggregate_close_lines(gdf: gpd.GeoDataFrame, epsg: int, aggreagate_distance: float = 5) -> gpd.GeoDataFrame:
        if(gdf.empty):
            return gdf
        gdf_mercator_projected = gdf.to_crs(epsg=epsg) 
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(aggreagate_distance) 
        
        #https://stackoverflow.com/questions/73566774/group-by-and-combine-intersecting-overlapping-geometries-in-geopandas
        gdf_merged: gpd.GeoDataFrame = gdf_mercator_projected.sjoin(gdf_mercator_projected, how='left', predicate="intersects")
        gdf_merged.columns = gdf_merged.columns.str.replace('_left', '',regex=False).str.replace('_right', '', regex=False)
        gdf_merged = gdf_merged.loc[:, ~gdf_merged.columns.duplicated()]

        gdf_merged_diss: gpd.GeoDataFrame = gdf_merged.dissolve()
        gdf_merged_diss = gdf_merged_diss.reset_index(drop=True).dissolve()
        gdf_merged_diss['geometry'] = pygeoops.centerline(gdf_merged_diss['geometry'], min_branch_length=aggreagate_distance * 10)
        gdf_merged_diss = gdf_merged_diss.explode(column='geometry', ignore_index=True)
        gdf_merged_diss = gdf_merged_diss.to_crs(epsg=gdf.crs)
        return gdf_merged_diss
    
