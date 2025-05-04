"""
Functions for handling GeoDataFrame realated tasks.
Author: Lukáš Kotoun, xkotou08
"""
import warnings

import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
import numpy as np
import osmnx as ox
from osmium import FileProcessor
from shapely.geometry import Polygon, MultiLineString, Point
from shapely.ops import split
from scipy.spatial import cKDTree

from config import CRS_DISPLAY
from modules.utils import Utils
from modules.geom_utils import GeomUtils
from common.map_enums import WorldSides, Style, MinPlot
from common.custom_types import BoundsDict, DimensionsTuple, WantedAreas, RowsConditions, RowsConditionsAND


class GdfUtils:

    # ------------getting informations------------
    @staticmethod
    def get_area_gdf(area: str | list[Point], fromCrs: str, toCrs: str | None = None) -> GeoDataFrame:
        """Parse area from string or list of coordinates to gdf.
        From string it will use osmnx with nominatim api"""
        if isinstance(area, str):
            try:
                # need internet connection
                reqired_area_gdf: GeoDataFrame = ox.geocode_to_gdf(
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
                    area_polygon, fromCrs)
            except:
                raise ValueError("Invalid area given by list of cordinates.")
        else:  # area cannot be created
            raise ValueError("Invalid area format.")
        if (toCrs is None):
            return reqired_area_gdf
        else:
            return reqired_area_gdf.to_crs(toCrs)

    @staticmethod
    def get_whole_area_gdf(wanted_areas: WantedAreas, key_with_area, fromCrs: str, toCrs: str | None = None) -> GeoDataFrame:
        """Parse all wanted areas to gdf where each row in one area. Row will also have all aditional columns"""
        if (len(wanted_areas) == 1):
            wanted_area = wanted_areas[0].copy()
            if (key_with_area not in wanted_area):
                raise ValueError(
                    "Missing key with area in dict with wanted area.")
            area_gdf = GdfUtils.get_area_gdf(
                wanted_area[key_with_area], fromCrs=fromCrs, toCrs=toCrs)
            wanted_area.pop(key_with_area, None)
            return area_gdf.assign(**wanted_area)
        else:
            areas_gdf_list: list[GeoDataFrame] = []
            for wanted_area in wanted_areas.copy():
                if (key_with_area not in wanted_area):
                    raise ValueError(
                        "Missing key with area in dict with wanted area.")
                area_gdf = GdfUtils.get_area_gdf(
                    wanted_area[key_with_area], fromCrs=fromCrs, toCrs=toCrs)
                wanted_area.pop(key_with_area, None)
                areas_gdf_list.append(area_gdf.assign(**wanted_area))
            return GdfUtils.combine_gdfs(areas_gdf_list)

    @staticmethod
    def get_areas_borders_gdf(gdf, combine_by):
        # Separate rows with category == (0 or None) and nonzero categories.
        gdf[combine_by] = gdf.get(combine_by, 0)
        gdf_zero, gdf_nonzero = GdfUtils.filter_rows(
            gdf, {combine_by: [0, "~"]}, compl=True)
        if not gdf_nonzero.empty:
            gdf_dissolved = gdf_nonzero.dissolve(by=combine_by, as_index=False)
        else:
            gdf_dissolved = gdf_nonzero.copy()

        # Combine the dissolved nonzero rows with the category 0 rows.
        return GdfUtils.combine_gdfs([gdf_dissolved, gdf_zero])

    @staticmethod
    def get_bounds_gdf(*gdfs: GeoDataFrame, toCrs: str | None = None) -> BoundsDict:
        west = float('inf')
        south = float('inf')
        east = float('-inf')
        north = float('-inf')

        for gdf in gdfs:
            gdf_edit = gdf
            if (toCrs is not None):
                gdf_edit = gdf.to_crs(toCrs)
            # [WorldSides.WEST.value, WorldSides.SOUTH.value, WorldSides.EAST.value, WorldSides.NORTH.value]
            bounds: tuple[float] = gdf_edit.total_bounds
            west = min(west, bounds[0])
            south = min(south, bounds[1])
            east = max(east, bounds[2])
            north = max(north, bounds[3])
        return {
            WorldSides.WEST.value: west,
            WorldSides.SOUTH.value: south,
            WorldSides.EAST.value: east,
            WorldSides.NORTH.value: north
        }

    @staticmethod
    def get_dimensions_gdf(gdf: GeoDataFrame) -> DimensionsTuple:
        bounds = GdfUtils.get_bounds_gdf(gdf)
        return Utils.get_dimensions(bounds)

    # ------------creating------------

    @staticmethod
    def create_gdf_from_file_processor(fp: FileProcessor, fromCrs: str, columns=[]) -> GeoDataFrame:
        gdf = GeoDataFrame.from_features(fp)
        if (gdf.empty):
            # create gdf with column geometry
            return GdfUtils.create_empty_gdf(fromCrs)
        else:
            return gdf.set_crs(fromCrs)

    @staticmethod
    def create_empty_gdf(crs: str, columns=["geometry"]) -> GeoDataFrame:
        if ('geometry' not in columns):
            columns.append('geometry')
        if (crs is None):
            return GeoDataFrame(columns=columns)
        return GeoDataFrame(columns=columns, crs=crs)

    @staticmethod
    def create_gdf_from_bounds(area_bounds: BoundsDict, fromCrs: str, toCrs: str | None = None) -> GeoDataFrame:
        return GdfUtils.create_gdf_from_polygon(GeomUtils.create_polygon_from_bounds(area_bounds), fromCrs, toCrs)

    @staticmethod
    def create_gdf_from_polygon(area_polygon: Polygon, fromCrs: str, toCrs: str | None = None) -> GeoDataFrame:
        if (toCrs is None):
            return GeoDataFrame(geometry=[area_polygon], crs=fromCrs)
        else:
            return GeoDataFrame(geometry=[area_polygon], crs=fromCrs).to_crs(toCrs)

    @staticmethod
    def create_polygon_from_gdf(*gdfs: GeoDataFrame, toCrs: str | None = None) -> Polygon:
        if (len(gdfs) == 1):
            if (toCrs is None):
                return gdfs[0].unary_union
            gdf_edit = gdfs[0].to_crs(toCrs)
            return gdf_edit.unary_union
        else:
            if (toCrs is None):
                combined_gdf = GeoDataFrame(
                    pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
            else:
                combined_gdf = GeoDataFrame(
                    pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs).to_crs(toCrs)
            return combined_gdf.unary_union

    @staticmethod
    def create_background_gdf(map_area_gdf: GeoDataFrame, costline_gdf: GeoDataFrame, water_color: str, land_color: str) -> GeoDataFrame:
        """From costline gdf and map area create gdf with rows of that represent water and land areas.

        Water and land is determined by direction of costline. On left side of costline is land and on right side is water.
        Water and land polygons are created by splitting map area with costline.

        Args:
            map_area_gdf (GeoDataFrame): gdf with area that will be displayed on paper
            costline_gdf (GeoDataFrame): gdf with costlines
            water_color (str): color of water
            land_color (str): color of land    
          """
        if (costline_gdf.empty):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_data = []
        required_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
        # Create splitters from costline gdf and split area by them one by one
        splitters = GeomUtils.merge_lines_safe(costline_gdf.geometry)
        splitters = list(splitters.geoms) if isinstance(
            splitters, MultiLineString) else [splitters]
        for splitter in splitters:
            geometry_collection = split(required_area_polygon, splitter)
            # splitter does not split area
            if (len(geometry_collection.geoms) == 1):
                continue
            # iterate throw each created polygon and check if geom is on right or left of splitter
            for geom in geometry_collection.geoms:
                same_orientation = GeomUtils.check_same_orientation(
                    geom, splitter)
                if (same_orientation is None):
                    continue
                color = ""
                if (same_orientation):
                    if (geom.exterior.is_ccw):
                        color = land_color  # polygon is on left side of splitter
                    else:
                        color = water_color  # polygon is on right side of splitter
                else:
                    if (geom.exterior.is_ccw):  # polygon is reversed to splitter
                        color = water_color  # polygon is on left side of splitter
                    else:
                        color = land_color  # polygon is on left side of splitter
                bg_data.append({"geometry": geom, Style.COLOR.value: color})
        # create gdf from data
        if (not bg_data):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_gdf = GeoDataFrame(
            bg_data, geometry="geometry", crs=map_area_gdf.crs)
        return bg_gdf

    # centroid needs to be calc in display cordinates
    @staticmethod
    def create_points_from_polygons_gdf(gdf: GeoDataFrame):
        """Create points from centers of polygons in given gdf."""
        if (gdf.empty):
            return gdf
        original_crs = gdf.crs
        gdf = GdfUtils.change_crs(gdf, CRS_DISPLAY)
        gdf = gdf[gdf.geometry.type.isin(
            ["Polygon", "MultiPolygon"])].reset_index(drop=True)
        gdf["geometry"] = gdf.geometry.centroid
        gdf = GdfUtils.change_crs(gdf, original_crs)
        return gdf

    # ------------editing gdf------------
    @staticmethod
    def remove_columns(gdf: GeoDataFrame, columns: list[str | Style], neg=False) -> GeoDataFrame:
        if (neg):
            gdf.drop(columns=[
                     col for col in gdf.columns if col not in columns], inplace=True, errors='ignore')
        else:
            gdf.drop(columns=columns, inplace=True, errors='ignore')

    @staticmethod  # column and multipliers must be numeric otherwise it will throw error
    def multiply_column_gdf(gdf: GeoDataFrame, column: Style | str, multipliers: list[str | Style] = [], scaling=None, filter: RowsConditions = []):
        """For each row where given column in 'column' variable is not nan, multiply by miltipliers columns and scaling if given.
        Aditonaly muliply only rows where filter is true."""
        if (column not in gdf):
            return
        # multiply rows where column value is not nan
        rows_with_column = GdfUtils.get_rows_filter(gdf, {column: ""})
        if (filter):
            rows_with_column &= GdfUtils.get_rows_filter(gdf, filter)

        if (scaling is not None):
            gdf.loc[rows_with_column,
                    column] = gdf.loc[rows_with_column, column] * scaling

        multipliers = [
            multiplier for multiplier in multipliers if multiplier in gdf.columns]
        # multiply rows where multiplier column exists
        for multiplier in multipliers:
            rows_with_multipler = GdfUtils.get_rows_filter(
                gdf, {multiplier: ""}) & rows_with_column
            gdf.loc[rows_with_multipler,
                    column] *= gdf.loc[rows_with_multipler, multiplier]

    @staticmethod  # column and multipliers must be numeric otherwise it will throw error
    def create_derivated_columns(gdf: GeoDataFrame, new_column: Style | str, base_column: Style | str, multipliers: list[str | Style] = [],
                                 filter: RowsConditions | RowsConditionsAND = [], fill: any = 0, scaling=None):
        """Create new column in gdf that is derived from base column. and multiply it by multipliers and scaling using multiply_column_gdf function.
        Also create derivated column only for rows where filter is true, if given.

        Args:   
            gdf (GeoDataFrame): gdf to create new column in
            new_column (str): column name
            base_column (str): base column name
            multipliers (list[str], optional): Columns in gdf to multipli new columns with. Defaults to [].
            filter (RowsConditions, optional): Filter to filters rows for with to create new column. Defaults to [].
            fill (any, optional): Fill new columns with if base not exists. Defaults to 0.
            scaling (_type_, optional): Multiply new column by value. Defaults to None.
        """
        # create new column with fill if base not exists
        if (base_column not in gdf):
            gdf[new_column] = gdf.get(new_column, fill)
            return

        # multiply rows where column value is not empty
        rows_filter = GdfUtils.get_rows_filter(gdf, filter)
        gdf.loc[rows_filter, new_column] = gdf.loc[rows_filter, base_column]
        if multipliers or scaling is not None:
            GdfUtils.multiply_column_gdf(gdf, new_column, multipliers, scaling)

    @staticmethod
    def change_columns_to_categorical(gdf: GeoDataFrame, columns: list) -> None:
        for column in columns:
            if (column in gdf):
                gdf[column] = gdf[column].astype("category")

    @staticmethod
    def remove_na_columns(gdf: GeoDataFrame) -> None:
        empty_cols = [col for col in gdf.columns if gdf[col].isna().all()]
        GdfUtils.remove_columns(gdf, empty_cols)

    @staticmethod
    def combine_rows_gdf(gdf: GeoDataFrame) -> GeoDataFrame:
        if (len(gdf) == 1):
            return gdf
        return GeoDataFrame(geometry=[gdf.geometry.unary_union], crs=gdf.crs)

    @staticmethod
    def change_columns_to_numeric(gdf: GeoDataFrame, columns: list[str], downcast: str = 'integer') -> None:
        for column in columns:
            if (column in gdf):
                gdf[column] = pd.to_numeric(
                    gdf[column], errors='coerce', downcast=downcast)

    @staticmethod
    def convert_numeric_columns_int(gdf: GeoDataFrame, columns: list[str]) -> None:
        for column in columns:
            if (column in gdf):
                try:
                    gdf[column] = gdf[column].round(0).astype("Int64")
                except:
                    warnings.warn(f"cannot convert column {column} to int")

    @staticmethod
    def fill_nan_values(gdf: GeoDataFrame, columns: list[str], value=0) -> None:
        for column in columns:
            if (column in gdf):
                gdf[column] = gdf[column].fillna(value)
            else:
                gdf[column] = value

    @staticmethod
    def merge_lines_gdf(gdf: GeoDataFrame, columns_ignore: list[str | Style] = []) -> GeoDataFrame:
        """Try to merge lines in GeoDataFrame to one line if they have same values in columns (except columns in columns_ignore).
        From multiple lines that connect to each other, it will create one line.
        To merging geoms is used function merge_lines_safe that uses unary_union and linemerge from shapely.ops.
        It should merge multiple lines that are one line and that should prevents creating artefacts in plot.
        """
        if (gdf.empty):
            return gdf
        columns_ignore = [*columns_ignore, gdf.geometry.name]
        # if dont want remove columns and than...
        columns = [
            col for col in gdf.columns if col not in columns_ignore]
        if (not columns):
            geometry = GeomUtils.merge_lines_safe(gdf.geometry)
            return GeoDataFrame(geometry=[geometry], crs=gdf.crs)

        # merge all lines with same values in 'columns'
        merged = gdf.groupby(columns, dropna=False, observed=True).agg({
            gdf.geometry.name: GeomUtils.merge_lines_safe
        })
        merged_gdf = GeoDataFrame(
            merged, geometry=gdf.geometry.name, crs=gdf.crs).reset_index()
        return merged_gdf

    @staticmethod
    def combine_gdfs(gdfs: list[GeoDataFrame]) -> GeoDataFrame:
        non_empty_gdfs = [gdf for gdf in gdfs if not gdf.empty]
        for gdf in non_empty_gdfs:
            GdfUtils.remove_na_columns(gdf)
        if (not non_empty_gdfs):
            return GdfUtils.create_empty_gdf(gdfs[0].crs)
        if (len(gdfs) == 1):
            return gdfs[0]
        # concat to one gdf
        return pd.concat(non_empty_gdfs, ignore_index=True)

    @staticmethod
    def expand_gdf_area_fitPaperSize(area_gdf: GeoDataFrame, pdf_dim: DimensionsTuple):
        bounds: BoundsDict = GdfUtils.get_bounds_gdf(area_gdf)
        return GdfUtils.create_gdf_from_bounds(Utils.adjust_bounds_to_fill_paper(bounds, pdf_dim), area_gdf.crs, None)

    @staticmethod
    def sort_gdf_by_columns(gdf: GeoDataFrame, column_name: list[Style | str], ascending: bool = True, na_position: str = 'first', stable=False) -> GeoDataFrame:
        if (gdf.empty):
            return gdf
        if (isinstance(column_name, str)):
            column_name = [column_name]
        column_name_exist = [col for col in column_name if col in gdf.columns]
        if (not column_name_exist):
            return gdf
        if (stable):
            gdf.sort_values(by=column_name_exist, ascending=ascending,
                            na_position=na_position, inplace=True, kind="stable", ignore_index=True)
        else:
            gdf.sort_values(by=column_name_exist, ascending=ascending,
                            na_position=na_position, inplace=True, ignore_index=True)

    def change_crs(gdf: GeoDataFrame, toCrs: str) -> GeoDataFrame:
        if (gdf.empty):
            return gdf.set_crs(toCrs)
        return gdf.to_crs(toCrs)

    # ------------Bool operations------------

    # ------------Filtering------------

    @staticmethod
    def get_rows_filter_AND(gdf: GeoDataFrame, conditions: RowsConditionsAND) -> pd.Series:
        """Get pandas Series with True for rows that match all conditions conditions in gdf.
            For non string values can check only equality.
        Args:
            gdf (GeoDataFrame): gdf to filter
            conditions (RowsConditionsAND): conditions to filter gdf. 
            It can have this formats:
            - {column_name: ''} - single condition - not NA
            - {column_name: value} - single condition - equal to value
            - {column_name: '~'} - single condition - NA
            - {column_name: '~value'} - single condition - not equal to value
            - {column_name: [value1, value2]} - multiple values for one column - can have value1 or value2
            - {column_name: ('~value1', '~value2')} - multiple values for one column - cant have value1 and value2 
            can have more conditions in dict where all must be true to mark row as true
            - {column_name: [value1, value2], column_name2: [value3, value4]} - column_name1 must be value1 or value2 and column_name2 must be value3 or value4
        """
        filter_mask = pd.Series(True, index=gdf.index)
        for column_name, column_value in conditions.items():
            if column_name not in gdf.columns:
                # Handle missing columns
                if isinstance(column_value, list):
                    # If any value is a string starting with "~", we skip the column.
                    if any(isinstance(v, str) and v.startswith("~") for v in column_value):
                        continue
                    else:
                        filter_mask &= False
                        break
                elif isinstance(column_value, tuple):
                    # If any value is a string starting without "~", we return false to the column.
                    if all(isinstance(v, str) and v.startswith("~") for v in column_value):
                        continue
                    else:
                        filter_mask &= False
                        break
                elif isinstance(column_value, str) and column_value.startswith("~"):
                    continue
                else:
                    filter_mask &= False
                    break
            else:
                # Column exists in gdf
                if isinstance(column_value, list):
                    # Start with all rows excluded
                    condition_mask = pd.Series(False, index=gdf.index)
                    if not column_value:
                        # If the list is empty, the column should not be NA
                        condition_mask |= gdf[column_name].notna()
                    else:
                        for value in column_value:
                            if isinstance(value, str):
                                if value == "":  # Not NA
                                    condition_mask |= gdf[column_name].notna()
                                elif value == "~":  # Column should be NA
                                    condition_mask |= gdf[column_name].isna()
                                elif value.startswith("~"):
                                    condition_mask |= (
                                        gdf[column_name] != value[1:])
                                else:  # Column should equal the string value
                                    condition_mask |= (
                                        gdf[column_name] == value)
                            else:
                                # for non-string values, just check equality
                                condition_mask |= (gdf[column_name] == value)
                    filter_mask &= condition_mask

                elif isinstance(column_value, tuple):
                    condition_mask = pd.Series(True, index=gdf.index)
                    if not column_value:
                        # If the list is empty, the column should not be NA
                        condition_mask &= gdf[column_name].notna()
                    else:
                        for value in column_value:
                            if isinstance(value, str):
                                if value == "":  # Not NA
                                    condition_mask &= gdf[column_name].notna()
                                elif value == "~":  # Column should be NA
                                    condition_mask &= gdf[column_name].isna()
                                elif value.startswith("~"):
                                    condition_mask &= (
                                        gdf[column_name] != value[1:])
                                else:  # Column should equal the string value
                                    condition_mask &= (
                                        gdf[column_name] == value)
                            else:
                                # for non-string values, just check equality
                                condition_mask &= (gdf[column_name] == value)
                    filter_mask &= condition_mask
                else:
                    if isinstance(column_value, str):
                        if column_value == '':  # Not NA
                            filter_mask &= gdf[column_name].notna()
                        elif column_value.startswith("~"):
                            if column_value == "~":  # Column should be NA
                                filter_mask &= gdf[column_name].isna()
                            else:  # Column should not equal the value after "~"
                                filter_mask &= (
                                    gdf[column_name] != column_value[1:])
                        else:  # Column should equal the string value
                            filter_mask &= (gdf[column_name] == column_value)
                    else:
                        # non-string condition values, just check equality
                        filter_mask &= (gdf[column_name] == column_value)
        return filter_mask

    def get_rows_filter(gdf: GeoDataFrame, conditions: RowsConditions | RowsConditionsAND) -> pd.Series:
        """Create complex filter mask with OR and AND conditions. Where it use get_rows_filter_AND function to create AND conditions.
        Conditions is in format of list [{cond: [val1, val2]}, {..}] where data in each dict area AND condition 
        and between dicts is OR condition."""
        filter_mask = pd.Series(False, index=gdf.index)
        # if is not list
        if isinstance(conditions, dict):
            conditions = [conditions]
        elif conditions is None:
            return filter_mask  # none - none rows
        elif not conditions:
            conditions = [{}]  # empty condition - all rows
        for and_conditions in conditions:
            filter_mask |= GdfUtils.get_rows_filter_AND(gdf, and_conditions)
        return filter_mask

    def filter_rows(gdf: GeoDataFrame, conditions: RowsConditions | RowsConditionsAND,
                    neg: bool = False, compl: bool = False) -> GeoDataFrame:
        """Return create gdf that area filtered using filter mask that is obtained from get_rows_filter function."""
        filter_mask = GdfUtils.get_rows_filter(gdf, conditions)
        return GdfUtils.return_filtered(gdf, filter_mask, neg, compl)

    @staticmethod
    def return_filtered(gdf: GeoDataFrame, filter_mask: pd.Series, neg: bool = False,
                        compl: bool = False):
        if (compl):
            if (neg):
                return gdf[~filter_mask].reset_index(drop=True), gdf[filter_mask].reset_index(drop=True)
            else:
                return gdf[filter_mask].reset_index(drop=True), gdf[~filter_mask].reset_index(drop=True)
        else:
            if (neg):
                return gdf[~filter_mask].reset_index(drop=True)
            else:
                return gdf[filter_mask].reset_index(drop=True)

    @staticmethod
    def filter_areas(gdf: GeoDataFrame, compl: bool = False, neg: bool = False) -> GeoDataFrame | tuple[GeoDataFrame, GeoDataFrame]:
        return GdfUtils.return_filtered(gdf, gdf.geom_type.isin(["Polygon", "MultiPolygon"]), compl=compl, neg=neg)

    @staticmethod
    def filter_nodes_min_req(nodes_gdf: GeoDataFrame) -> GeoDataFrame:
        """Filter minimum requirments for nodes markers and texts"""
        # must have at least one of the columns
        nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [{Style.MARKER.value: ''},
                                                     {Style.TEXT1.value: ''},
                                                     {Style.TEXT2.value: ''}])
        # filter by min plot requirements - data that does not have that minimum will not be plotted
        nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [{Style.MIN_PLOT_REQ.value: MinPlot.MARKER.value, Style.MARKER.value: '', Style.COLOR.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1.value,
                                                         Style.MARKER.value: '', Style.TEXT1.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT2.value,
                                                         Style.MARKER.value: '', Style.TEXT2.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1_TEXT2.value,
                                                         Style.MARKER.value: '', Style.TEXT1.value: '', Style.TEXT2.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.TEXT1.value,
                                                         Style.TEXT1.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.TEXT2.value,
                                                         Style.TEXT2.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.TEXT1_TEXT2.value,
                                                         Style.TEXT1.value: '', Style.TEXT2.value: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1_OR_TEXT2,
                                                         Style.MARKER.value: '', Style.TEXT1: ''},
                                                     {Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1_OR_TEXT2, Style.MARKER.value: '', Style.TEXT2: ''}])
        return nodes_gdf

    @staticmethod
    def get_rows_inside_area(gdf_rows: GeoDataFrame, gdf_area: GeoDataFrame) -> GeoDataFrame:
        return gdf_rows.loc[gpd.sjoin(gdf_rows, gdf_area, predicate="within").index].reset_index(drop=True)

    # -----------Others functions------------

    @staticmethod
    def get_groups_by_columns(gdf: GeoDataFrame, group_cols: list, default_keys: list = [], dropna: bool = False, sort=True):
        """Create from gdf groups by columns in group_cols. if columns does not exits fill it with default values"""
        # get missing columns and replace with default key if missing
        if len(group_cols) != len(default_keys):
            default_keys = [None] * len(group_cols)
        for col, default in zip(group_cols, default_keys):
            if col not in gdf.columns:
                gdf[col] = default
        # observe true - only categories that appear in the actual data
        if (len(group_cols) == 1):
            return gdf.groupby(group_cols[0], dropna=dropna, observed=True, sort=sort)
        return gdf.groupby(group_cols, dropna=dropna, observed=True, sort=sort)

    @staticmethod
    def filter_peaks(nodes_gdf: GeoDataFrame, radius: float):
        """
        Filter only most significant peaks in given radius.

        For each peak in peaks, the function looks for any nearby peak within
        the given radius. If a higher peak exists than peak is not considered significant.

        Parameters:
        - peaks (GeoDataFrame): must have a 'geometry' column (Point) and an 'elevation' column.
        - radius (float): search radius (in units of peaks - e.g. meters) to look for competing peaks.

        Returns:
        - GeoDataFrame: a filtered GeoDataFrame containing only the significat peaks.
        """
        if (nodes_gdf.empty):
            return nodes_gdf
        if (radius <= 0):
            return nodes_gdf
        peaks, rest = GdfUtils.filter_rows(
            nodes_gdf, {'natural': 'peak'}, compl=True)
        peaks = GdfUtils.filter_rows(peaks, {'ele': ''})
        if (peaks.empty):
            return rest
        # extract coordinates and elevations
        coords = np.array([[geom.x, geom.y] for geom in peaks.geometry])
        elevations = peaks['ele'].values

        # Build a spatial tree for efficient neighbor lookup
        tree = cKDTree(coords)

        # Boolean array to mark whether each peak is important
        is_important = pd.Series(index=peaks.index, dtype=bool)
        # For each peak, query neighbors within the specified radius
        for point_i, (coord, elev) in enumerate(zip(coords, elevations)):
            # Find indices of nearby peaks
            nearby_point_i = tree.query_ball_point(coord, r=radius)
            nearby_point_i.remove(point_i)
            # Check for any higher peak
            for nearby_point in nearby_point_i:
                if elevations[nearby_point] > elev:
                    is_important.at[point_i] = False
                    break

        peaks = peaks[is_important]
        return GdfUtils.combine_gdfs([peaks, rest])

    @staticmethod
    def filter_place_by_population(nodes_gdf: GeoDataFrame, place_to_filter: list, min_population: int):
        """FIlter places where populatino exceeds given value."""
        if (nodes_gdf.empty):
            return nodes_gdf
        if (min_population is None or min_population <= 0):
            return nodes_gdf
        places, rest = GdfUtils.filter_rows(
            nodes_gdf, {'place': place_to_filter}, compl=True)
        places = GdfUtils.filter_rows(places, {'population': ''})
        if (places.empty):
            return rest
        places = places[places['population'] >= min_population]
        return GdfUtils.combine_gdfs([places, rest])

    @staticmethod
    def get_common_borders(gdf1: GeoDataFrame, gdf2: GeoDataFrame):
        """ Get common borders (lines) between two gdfs with lines.
        """
        union1 = gdf1.union_all()
        union2 = gdf2.union_all()
        common_border = union1.boundary.intersection(union2.boundary)
        if (not common_border):
            return GdfUtils.create_empty_gdf(gdf1.crs)
        intersection_gdf = gpd.GeoDataFrame(
            {'geometry': [common_border]}, crs=gdf1.crs)
        intersection_gdf = intersection_gdf[
            intersection_gdf.geometry.type.isin(['LineString', 'MultiLineString'])]
        return GdfUtils.merge_lines_gdf(intersection_gdf)
