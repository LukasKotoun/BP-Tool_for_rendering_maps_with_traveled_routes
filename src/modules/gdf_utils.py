import warnings

from shapely import geometry
from shapely.geometry.polygon import Polygon
import geopandas as gpd
import pandas as pd
import osmnx as ox
import pygeoops

from modules.utils import Utils
from geopy.distance import geodesic

from common.map_enums import WorldSides, StyleKey
from common.custom_types import BoundsDict, DimensionsTuple, Point, WantedArea
from common.common_helpers import time_measurement_decorator


class GdfUtils:

    # ------------getting informations------------
    @staticmethod
    def get_area_gdf(area: str | list[Point], fromEpsg: int, toEpsg: int | None = None) -> gpd.GeoDataFrame:
        if isinstance(area, str):
            if area.endswith('.geojson'):
                reqired_area_gdf: gpd.GeoDataFrame = gpd.read_file(
                    area)  # Get area from geojson file
                if reqired_area_gdf.empty:
                    raise ValueError("Given GeoJSON file is empty.")
                return reqired_area_gdf
            else:
                try:
                    # need internet connection
                    reqired_area_gdf: gpd.GeoDataFrame = ox.geocode_to_gdf(
                        area)  # Get from place name
                except:
                    raise ValueError(
                        "The requested location has not been found.")
                if (reqired_area_gdf.empty):
                    raise ValueError(
                        "The requested location has not been found.")

        elif isinstance(area, list):  # get area from coordinates
            try:
                area_polygon = Polygon(area)
                reqired_area_gdf = GdfUtils.create_gdf_from_polygon(
                    area_polygon, fromEpsg)  # todo change
            except:
                raise ValueError("Invalid area given by list of cordinates.")
        else:  # area cannot be created
            raise ValueError("Invalid area format.")
        if (toEpsg is None):
            return reqired_area_gdf
        else:
            return reqired_area_gdf.to_crs(epsg=toEpsg)

    @staticmethod
    @time_measurement_decorator("spojeni")
    def get_whole_area_gdf(whole_area: WantedArea, fromEpsg: int, toEpsg: int | None = None) -> gpd.GeoDataFrame:
        if (isinstance(whole_area, str) or (isinstance(whole_area, list) and len(whole_area) == 1)  # normal area
                or (isinstance(whole_area, list) and all(isinstance(item, tuple) and len(item) == 2 for item in whole_area))):
            if ((isinstance(whole_area, list) and len(whole_area) == 1)):  # one area in list
                return GdfUtils.get_area_gdf(whole_area[0], fromEpsg, toEpsg)
            else:
                return GdfUtils.get_area_gdf(whole_area, fromEpsg, toEpsg)
        elif (isinstance(whole_area, list)):  # area from multiple areas
            areas_gdf_list: list[gpd.GeoDataFrame] = []
            for area in whole_area:
                areas_gdf_list.append(GdfUtils.get_area_gdf(
                    area, fromEpsg, toEpsg))  # store areas to list of areas
            return GdfUtils.combine_gdfs(areas_gdf_list)
        else:  # area cannot be created
            raise ValueError("Invalid area format.")

    @staticmethod
    def get_bounds_gdf(*gdfs: gpd.GeoDataFrame, toEpsg: int | None = None) -> BoundsDict:
        west = float('inf')
        south = float('inf')
        east = float('-inf')
        north = float('-inf')

        for gdf in gdfs:
            gdf_edit = gdf
            if (toEpsg is not None):
                gdf_edit = gdf.to_crs(epsg=toEpsg)
            # [WorldSides.WEST, WorldSides.SOUTH, WorldSides.EAST, WorldSides.NORTH]
            bounds: tuple[float] = gdf_edit.total_bounds
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
    def get_polygon_bounds(polygon: Polygon) -> BoundsDict:
        # [WorldSides.WEST, WorldSides.SOUTH, WorldSides.EAST, WorldSides.NORTH]
        bounds: tuple[float] = polygon.bounds
        return {WorldSides.WEST: bounds[0],
                WorldSides.SOUTH: bounds[1],
                WorldSides.EAST: bounds[2],
                WorldSides.NORTH: bounds[3]}

    @staticmethod
    def get_dimensions_m(bounds: BoundsDict) -> DimensionsTuple:
        northern = (bounds[WorldSides.NORTH],
                    (bounds[WorldSides.WEST] + bounds[WorldSides.EAST]) / 2)
        southern = (bounds[WorldSides.SOUTH],
                    (bounds[WorldSides.WEST] + bounds[WorldSides.EAST]) / 2)
        eastern = ((bounds[WorldSides.NORTH] +
                   bounds[WorldSides.SOUTH]) / 2, bounds[WorldSides.EAST])
        western = ((bounds[WorldSides.NORTH] +
                   bounds[WorldSides.SOUTH]) / 2, bounds[WorldSides.WEST])
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
    def get_dimensions_gdf(gdf: gpd.GeoDataFrame) -> DimensionsTuple:
        bounds = GdfUtils.get_bounds_gdf(gdf)
        return Utils.get_dimensions(bounds)

    @staticmethod
    def get_dimensions_polygon(polygon: gpd.GeoDataFrame) -> DimensionsTuple:
        bounds = GdfUtils.get_polygon_bounds(polygon)
        return Utils.get_dimensions(bounds)

    # ------------creating------------
    @staticmethod
    def create_polygon_from_bounds(area_bounds: BoundsDict) -> Polygon:
        return Polygon([
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.SOUTH]),
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.NORTH]),
            (area_bounds[WorldSides.WEST], area_bounds[WorldSides.NORTH]),
            (area_bounds[WorldSides.WEST], area_bounds[WorldSides.SOUTH]),
            # Closing the polygon
            (area_bounds[WorldSides.EAST], area_bounds[WorldSides.SOUTH])
        ])

    @staticmethod
    def create_gdf_from_bounds(area_bounds: BoundsDict, fromEpsg: int, toEpsg: int | None = None) -> gpd.GeoDataFrame:
        return GdfUtils.create_gdf_from_polygon(GdfUtils.create_polygon_from_bounds(area_bounds), fromEpsg, toEpsg)

    @staticmethod
    def create_gdf_from_polygon(area_polygon: Polygon, fromEpsg: int, toEpsg: int | None = None) -> gpd.GeoDataFrame:
        if (toEpsg is None):
            return gpd.GeoDataFrame(geometry=[area_polygon], crs=f"EPSG:{fromEpsg}")
        else:
            return gpd.GeoDataFrame(geometry=[area_polygon], crs=f"EPSG:{fromEpsg}").to_crs(epsg=toEpsg)

    @staticmethod
    def create_polygon_from_gdf_bounds(*gdfs: gpd.GeoDataFrame, toEpsg: int | None = None) -> Polygon:
        bounds = GdfUtils.get_bounds_gdf(*gdfs, toEpsg=toEpsg)
        return GdfUtils.create_polygon_from_bounds(bounds)

    @staticmethod
    def create_polygon_from_gdf(*gdfs: gpd.GeoDataFrame, toEpsg: int | None = None) -> Polygon:
        if (len(gdfs) == 1):
            if (toEpsg is None):
                return gdfs[0].unary_union
            gdf_edit = gdfs[0].to_crs(epsg=toEpsg)
            return gdf_edit.unary_union
        else:
            if (toEpsg is None):
                combined_gdf = gpd.GeoDataFrame(
                    pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
            else:
                combined_gdf = gpd.GeoDataFrame(
                    pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs).to_crs(epsg=toEpsg)
            return combined_gdf.unary_union

    # ------------editing gdf------------
    @staticmethod
    def combine_rows_gdf(gdf: gpd.GeoDataFrame, toEpsg: int) -> gpd.GeoDataFrame:
        if (len(gdf) == 1):
            return gdf.to_crs(epsg=toEpsg)
        return gpd.GeoDataFrame(geometry=[gdf.to_crs(epsg=toEpsg).geometry.unary_union], crs=f"EPSG:{toEpsg}")

    @staticmethod
    def combine_gdfs(gdfs: list[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
        if (len(gdfs) == 1):
            return gdfs
        return pd.concat(gdfs, ignore_index=True)  # concat to one gdf

    @staticmethod
    def expand_area(area_gdf: gpd.GeoDataFrame | None, fromEpsg: int, toEpsg: int | None = None, pdf_dim: DimensionsTuple | None = None, custom_area: WantedArea | None = None):
        if (custom_area is not None):  # custom expand area to one row in gdf
            return GdfUtils.combine_rows_gdf(GdfUtils.get_whole_area_gdf(custom_area, fromEpsg, toEpsg), toEpsg)
        else:  # fit paper - expand by area bounds to rectangle
            bounds: BoundsDict = GdfUtils.get_bounds_gdf(area_gdf)
            return GdfUtils.create_gdf_from_bounds(Utils.adjust_bounds_to_fill_paper(bounds, pdf_dim), fromEpsg, toEpsg)

    @staticmethod
    def sort_gdf_by_column(gdf: gpd.GeoDataFrame, column_name: StyleKey, ascending: bool = True, na_position: str = 'first') -> gpd.GeoDataFrame:
        if (gdf.empty):
            return gdf
        if (column_name in gdf):
            return gdf.sort_values(by=column_name, ascending=ascending, na_position=na_position, kind="mergesort").reset_index(drop=True)
        warnings.warn("Cannot sort - unexisting column name")
        return gdf

    # ------------Bool operations------------
    @staticmethod
    def is_polygon_inside_bounds(area_bounds: BoundsDict, polygon: Polygon) -> bool:
        return GdfUtils.is_polygon_inside_polygon(GdfUtils.create_polygon_from_bounds(area_bounds), polygon)

    @staticmethod
    def is_polygon_inside_polygon(inner: Polygon, outer: Polygon) -> bool:
        return outer.contains(inner)

    @staticmethod
    def is_point_inside_polygon(point: geometry.point.Point, polygon: Polygon) -> bool:
        return polygon.contains(point)

    @staticmethod
    def is_polygon_inside_polygon_threshold(inner: Polygon, outer: Polygon, threshold: float = 0.95) -> bool:
        bbox_area: float = inner.area
        intersection_area: float = inner.intersection(outer).area
        percentage_inside: float = intersection_area / bbox_area
        return percentage_inside >= threshold

    # ------------Filtering------------
    @staticmethod
    def create_condition(gdf: gpd.GeoDataFrame, att_name: str, att_values: list[str] = []) -> pd.Series:
        """Create condition for given gdf, return true for every row that have att_name with att_value (if given,
        if not it check for any value (not NA)).
        If att_name is not in gdf it return condition with all false.

        Args:
            gdf (gpd.GeoDataFrame): Gdf to create condition for.
            att_name (str): Name of atribute to condition (will leave true for rows with value on this att column).
            att_values (list[str], optional): Values of att_name (will leave true for rows with this values in att_name column) Defaults to [].

        Returns:
            pd.Series[bool]: condition for given gdf.
        """

    @staticmethod
    def filter_gdf_column_values(gdf: gpd.GeoDataFrame, col_name: str,
                                 col_values: list = [], neg: bool = False,
                                 compl: bool = False) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame] | gpd.GeoDataFrame:
        if (col_values and col_name in gdf):
            condition = gdf[col_name].isin(col_values)
        elif (col_name in gdf):
            condition = gdf[col_name].notna()
        else:
            if (col_values and any(pd.isna(value) for value in col_values)):
                # match missin column as NA
                condition = gdf.index >= 0
            else:
                # cant have NA and have missing column
                condition = gdf.index < 0
                
        if (compl):
            if (neg):
                return gdf[~condition].reset_index(drop=True), gdf[condition].reset_index(drop=True)
            else:
                return gdf[condition].reset_index(drop=True), gdf[~condition].reset_index(drop=True)
        else:
            if (neg):
                return gdf[~condition].reset_index(drop=True)
            else:
                return gdf[condition].reset_index(drop=True)

    @staticmethod
    @time_measurement_decorator("filter")
    def filter_gdf_columns_values_AND(gdf: gpd.GeoDataFrame, col_names: list[str],
                                      col_values: list = [], neg: bool = False,
                                      compl: bool = False) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame] | gpd.GeoDataFrame:
        """Return gdf with rows that have in every column specified in 'col_names' any of 'col_values'.
        If neg is used return gdf with rows that dont have any of values specified in 'col_values' in any of 'col_names'.

        Example of usage:
                Want all rows that have '-' or pd.NA in columns 1 and 2
                    filter_gdf_columns_values_AND(gdf, [1, 2], ['-', pd.NA])
                Want all rows that dont have '-' or pd.NA in columns 1 and 2
                    filter_gdf_columns_values_AND(gdf, [1, 2], ['-', pd.NA], True)
                Want all rows that have some value in columns 1 and 2
                    filter_gdf_columns_values_AND(gdf, [1, 2], [])
                Want all rows that dont have some value (have pd.NA) in columns 1 and 2
                    filter_gdf_columns_values_AND(gdf, [1, 2], [], True)
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame where to check.
            col_names (list[str]): List of columns to check.
            col_values (list, optional): List of values to check for in columns. Defaults to [].
            neg (bool, optional): If is set to true returned gdfs will be swapped (AND first and than OR). Defaults to False.

        Returns:
            tuple[gpd.GeoDataFrame, gpd.GeoDataFrame] | gpd.GeoDataFrame: Filtered frames one with conditions and optionaly compl gdf.
        """
        existing_columns: list[str] = [
            col for col in col_names if col in gdf.columns]

        # None of values in col_values can be in any of column in each row
        if (neg):
            # All of col_names are in gdf
            if (set(existing_columns) == set(col_names)):
                if (col_values):
                    # ~(some column have some value from col_values) == no column has any value from col_values
                    condition = ~gdf[existing_columns].isin(
                        col_values).any(axis=1)
                else:
                    # col values are not specified - values must have NA
                    condition = gdf[existing_columns].isna().all(axis=1)

            # None of col_names is in gdf
            elif (not existing_columns):
                if (col_values and any(pd.isna(value) for value in col_values)):
                    # cant have NA
                    condition = gdf.index < 0
                else:
                    # can have na - match missing columns (all) as NA
                    condition = gdf.index >= 0

            # Some of col_names are in gdf
            else:
                if (col_values and any(pd.isna(value) for value in col_values)):
                    # cant have NA and have missing columns
                    condition = gdf.index < 0
                else:
                    if (col_values):
                        # can have NA
                        condition = ~gdf[existing_columns].isin(
                            col_values).any(axis=1)
                    else:
                        # Must have NA
                        condition = gdf[existing_columns].isna().all(axis=1)
                    # match missing columns as NA and check rest

        # Some value from col_values must be in every column in each row
        else:
            # All of col_names are in gdf
            if (set(existing_columns) == set(col_names)):
                if (col_values):
                    condition = gdf[existing_columns].isin(
                        col_values).all(axis=1)
                else:
                    # col values are not specified - values cant have NA
                    condition = gdf[existing_columns].notna().all(axis=1)

            # None of col_names is in gdf
            elif (not existing_columns):
                if (col_values and any(pd.isna(value) for value in col_values)):
                    # match missing columns (all) as NA
                    condition = gdf.index >= 0
                else:
                    # cant have NA - non specified or not containing NA
                    condition = gdf.index < 0

            # Some of col_names are in gdf
            else:
                if (col_values and any(pd.isna(value) for value in col_values)):
                    # match missing columns as NA and check rest
                    condition = gdf[existing_columns].isin(
                        col_values).all(axis=1)
                else:
                    # cant have NA and have missing columns
                    condition = gdf.index < 0

        if (compl):
            return gdf[condition].reset_index(drop=True), gdf[~condition].reset_index(drop=True)
        else:
            return gdf[condition].reset_index(drop=True)

    @staticmethod
    def filter_gdf_rows_inside_gdf_area(gdf_rows: gpd.GeoDataFrame, gdf_area: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return gdf_rows[gdf_rows.geometry.within(gdf_area.unary_union)].reset_index(drop=True)

    @staticmethod
    # todo use one filter creation and than add with 'and' all ways that are longer, that will leave false with all that i want...
    @time_measurement_decorator("short ways filter")
    def filter_short_ways(gdf: gpd.GeoDataFrame, toEpsg: int, min_lenght: float = 2) -> gpd.GeoDataFrame:

        gdf_mercator_projected = gdf.to_crs(epsg=toEpsg)
        condition: pd.Series[bool] = gdf_mercator_projected.geometry.length > min_lenght
        filtered_gdf_mercator_projected = gdf_mercator_projected[condition]
        return filtered_gdf_mercator_projected.to_crs(epsg=gdf.crs)

    # ------------Others functions------------
    @staticmethod
    def buffer_gdf_same_distance(gdf: gpd.GeoDataFrame, distance: float, toEpsg: int, resolution: int = 16,
                                 cap_style: str = 'round', join_style: str = 'round') -> gpd.GeoDataFrame:
        gdf_mercator_projected = gdf.to_crs(epsg=toEpsg)
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(
            distance, resolution=resolution, cap_style=cap_style, join_style=join_style)
        return gdf_mercator_projected.to_crs(epsg=gdf.crs)

    @staticmethod
    def buffer_gdf_column_value_distance(gdf: gpd.GeoDataFrame, column_key: str, toEpsg: int,
                                         additional_padding: float = 0, resolution: int = 16,
                                         cap_style: str = 'round', join_style: str = 'round') -> gpd.GeoDataFrame:
        gdf_mercator_projected = gdf.to_crs(epsg=toEpsg)
        gdf_mercator_projected['geometry'] = gdf_mercator_projected.apply(
            lambda row: row['geometry'].buffer(row[column_key] + additional_padding, resolution=resolution,
                                               cap_style=cap_style, join_style=join_style), axis=1
        )
        return gdf_mercator_projected.to_crs(epsg=gdf.crs)

    @staticmethod
    def aggregate_close_lines(gdf: gpd.GeoDataFrame, toEpsg: int, aggreagate_distance: float = 5) -> gpd.GeoDataFrame:
        if (gdf.empty):
            return gdf
        gdf_mercator_projected = gdf.to_crs(epsg=toEpsg)
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(
            aggreagate_distance)

        # https://stackoverflow.com/questions/73566774/group-by-and-combine-intersecting-overlapping-geometries-in-geopandas
        gdf_merged: gpd.GeoDataFrame = gdf_mercator_projected.sjoin(
            gdf_mercator_projected, how='left', predicate="intersects")
        gdf_merged.columns = gdf_merged.columns.str.replace(
            '_left', '', regex=False).str.replace('_right', '', regex=False)
        gdf_merged = gdf_merged.loc[:, ~gdf_merged.columns.duplicated()]

        gdf_merged_diss: gpd.GeoDataFrame = gdf_merged.dissolve()
        gdf_merged_diss = gdf_merged_diss.reset_index(drop=True).dissolve()
        gdf_merged_diss['geometry'] = pygeoops.centerline(
            gdf_merged_diss['geometry'], min_branch_length=aggreagate_distance * 10)
        gdf_merged_diss = gdf_merged_diss.explode(
            column='geometry', ignore_index=True)
        gdf_merged_diss = gdf_merged_diss.to_crs(epsg=gdf.crs)
        return gdf_merged_diss
