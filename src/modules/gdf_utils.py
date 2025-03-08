import warnings

import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pd
import osmnx as ox
import numpy as np
from shapely.geometry import Polygon, GeometryCollection, MultiLineString, LineString, Point
from osmium import FileProcessor
from shapely.ops import split

from modules.utils import Utils
from config import CRS_DISPLAY
from modules.geom_utils import GeomUtils
from common.map_enums import WorldSides, Style, MinPlot
from common.custom_types import BoundsDict, DimensionsTuple, WantedAreas, RowsConditions, RowsConditionsAND, WantedArea
from common.common_helpers import time_measurement


import numpy as np
from scipy.spatial import cKDTree


class GdfUtils:
    # ------------getting informations------------
    @staticmethod
    def get_area_gdf(area: str | list[Point], fromCrs: str, toCrs: str | None = None) -> GeoDataFrame:
        if isinstance(area, str):
            try:
                # need internet connection
                reqired_area_gdf: GeoDataFrame = ox.geocode_to_gdf(
                    area)  # Get from place name
            except:
                raise ValueError(
                    "The requested location has not been found.")  # todo should be validated on FE
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
    def map_gdf_column_names(gdf, mapping_dict):
        """Replace GeoDataFrame column names with enums if in mapping, otherwise keep them unchanged."""
        gdf.columns = [mapping_dict.get(col, col) for col in gdf.columns]
        return gdf

    @staticmethod
    def columns_to_upper(gdf, to_upper):
        """Change GeoDataFrame column names to upper case."""
        gdf.columns = [col.upper() if col in to_upper else col for col in gdf.columns]
        return gdf

    @staticmethod
    def get_whole_area_gdf(wanted_areas: WantedAreas, key_with_area, fromCrs: str, toCrs: str | None = None) -> GeoDataFrame:
        if (len(wanted_areas) == 1):
            wanted_area = wanted_areas[0]
            if (key_with_area not in wanted_area):
                raise ValueError(
                    "Missing key with area in dict with wanted area.")
            area_gdf = GdfUtils.get_area_gdf(
                wanted_area[key_with_area], fromCrs=fromCrs, toCrs=toCrs)
            wanted_area.pop(key_with_area, None)
            return area_gdf.assign(**wanted_area)
        else:
            areas_gdf_list: list[GeoDataFrame] = []
            for wanted_area in wanted_areas:
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
        gdf_zero, gdf_nonzero = GdfUtils.filter_rows(
            gdf, {combine_by: [0, "~"]}, compl=True)
        if not gdf_nonzero.empty:
            gdf_dissolved = gdf_nonzero.dissolve(by='category', as_index=False)
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
            # [WorldSides.WEST.name, WorldSides.SOUTH.name, WorldSides.EAST.name, WorldSides.NORTH.name]
            bounds: tuple[float] = gdf_edit.total_bounds
            west = min(west, bounds[0])
            south = min(south, bounds[1])
            east = max(east, bounds[2])
            north = max(north, bounds[3])
        return {
            WorldSides.WEST.name: west,
            WorldSides.SOUTH.name: south,
            WorldSides.EAST.name: east,
            WorldSides.NORTH.name: north
        }

    @staticmethod
    def get_dimensions_gdf(gdf: GeoDataFrame) -> DimensionsTuple:
        bounds = GdfUtils.get_bounds_gdf(gdf)
        return Utils.get_dimensions(bounds)

    # ------------creating------------

    @staticmethod
    def create_gdf_from_geometry_and_attributes(geometry: list, tags: list[dict], fromCrs: str) -> GeoDataFrame:
        return GeoDataFrame(pd.DataFrame(tags).assign(
            geometry=geometry), crs=fromCrs)

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
        if (costline_gdf.empty):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_data = []
        required_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
        # split one by one
        splitters = GeomUtils.merge_lines_safe(costline_gdf.geometry)
        splitters = list(splitters.geoms) if isinstance(
            splitters, MultiLineString) else [splitters]
        for splitter in splitters:
            geometry_collection = split(required_area_polygon, splitter)
            # splitter does not split area
            if (len(geometry_collection.geoms) == 1):
                continue
            # check if geom is on right or left of splitter
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
                bg_data.append({"geometry": geom, Style.COLOR.name: color})
        # create gdf from data
        if (not bg_data):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_gdf = GeoDataFrame(
            bg_data, geometry="geometry", crs=map_area_gdf.crs)
        return bg_gdf

    # centroid needs to be calc in display cordinates 
    @staticmethod
    def create_points_from_polygons_gdf(gdf: GeoDataFrame):
        if(gdf.empty):
            return gdf
        original_crs = gdf.crs
        gdf = GdfUtils.change_crs(gdf, CRS_DISPLAY)
        gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])].reset_index(drop=True)
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
    def multiply_column_gdf(gdf, column: Style | str, multipliers: list[str | Style] = [], scaling=None, filter: RowsConditions = []):
        if (column not in gdf):
            return
        # multiply rows where column value is not empty
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
    def create_derivated_columns(gdf, new_column: Style | str, base_column: Style | str, multipliers: list[str | Style] = [],
                                 filter: RowsConditions | RowsConditionsAND = [], fill: any = 0, scaling=None):
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

    @time_measurement("mergeLines")
    @staticmethod
    def merge_lines_gdf(gdf: GeoDataFrame, columns_ignore: list[str | Style] = []) -> GeoDataFrame:
        """Merge lines in GeoDataFrame to one line if they have same values in columns (except columns in columns_ignore).
        If want_bridges is True, merge all lines with same values in columns. If False, merge all lines with same values but ignore bridges.
        To merging geoms is used function merge_lines_safe that uses unary_union and linemerge from shapely.ops.
        It should merge multiple lines that are one line and that should prevents creating artifacts in plot.

        Args:
            gdf (GeoDataFrame): _description_
            want_bridges (bool): _description_
            columns_ignore (list[str  |  Style], optional): _description_. Defaults to [].

        Returns:
            GeoDataFrame: _description_
        """
        if(gdf.empty):
            return gdf
        columns_ignore = [*columns_ignore, gdf.geometry.name]
        # if dont want remove columns and than...
        columns = [
            col for col in gdf.columns if col not in columns_ignore]
        if(not columns):
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
        if(not non_empty_gdfs):
            return GdfUtils.create_empty_gdf(gdfs[0].crs)
        if (len(gdfs) == 1):
            return gdfs[0]
        return pd.concat(non_empty_gdfs, ignore_index=True)  # concat to one gdf

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

    @staticmethod
    def are_gdf_geometry_inside_geometry(gdf: GeoDataFrame, polygon: GeometryCollection) -> bool:
        return gdf[gdf.geometry.name].within(polygon).all()
        # todo check speed and try using sjoin

    # ------------Filtering------------

    @staticmethod
    def get_rows_filter_AND(gdf: GeoDataFrame, conditions: RowsConditionsAND) -> pd.Series:
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
        filter_mask = pd.Series(False, index=gdf.index)
        # if is not list
        if isinstance(conditions, dict):
            conditions = [conditions]
        elif conditions is None:
            return filter_mask # none - none rows
        elif not conditions:
            conditions = [{}]  # empty condition - all rows
        for and_conditions in conditions:
            filter_mask |= GdfUtils.get_rows_filter_AND(gdf, and_conditions)
        return filter_mask

    def filter_rows(gdf: GeoDataFrame, conditions: RowsConditions | RowsConditionsAND,
                    neg: bool = False, compl: bool = False) -> GeoDataFrame:
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

    # todo move somewhere else - to plotter
    @staticmethod
    def filter_invalid_texts(gdf):
        return GdfUtils.filter_rows(gdf, {Style.TEXT_FONT_SIZE.name: '', Style.TEXT_OUTLINE_WIDTH.name: '', Style.TEXT_COLOR.name: '',
                                          Style.TEXT_OUTLINE_COLOR.name: '', Style.TEXT_FONTFAMILY.name: '', Style.TEXT_WEIGHT.name: '',
                                          Style.TEXT_STYLE.name: '', Style.ALPHA.name: '', Style.EDGE_ALPHA.name: ''})

    @staticmethod
    def filter_invalid_markers(gdf):
        return GdfUtils.filter_rows(gdf, {Style.MARKER.name: '', Style.COLOR.name: '', Style.WIDTH.name: '',
                                          Style.EDGE_WIDTH.name: '', Style.EDGE_COLOR.name: '', Style.ALPHA.name: ''})
    # to some utils or main
    @staticmethod
    def filter_areas(gdf: GeoDataFrame, compl: bool = False, neg: bool = False) -> GeoDataFrame | tuple[GeoDataFrame, GeoDataFrame]:
        return GdfUtils.return_filtered(gdf, gdf.geom_type.isin(["Polygon", "MultiPolygon"]), compl=compl, neg=neg)
      


    @staticmethod
    @time_measurement("filter")
    def check_filter_nodes_min_req(nodes_gdf: GeoDataFrame) -> GeoDataFrame:
        nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [{Style.MARKER.name: ''},
                                                     {Style.TEXT1.name: ''},
                                                     {Style.TEXT2.name: ''}])
        
        nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [{Style.MIN_PLOT_REQ.name: MinPlot.MARKER.name, Style.MARKER.name: '', Style.COLOR.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                                                         Style.MARKER.name: '', Style.TEXT1.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT2.name,
                                                         Style.MARKER.name: '', Style.TEXT2.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1_TEXT2.name,
                                                         Style.MARKER.name: '', Style.TEXT1.name: '', Style.TEXT2.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.TEXT1.name,
                                                         Style.TEXT1.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.TEXT2.name,
                                                         Style.TEXT2.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.TEXT1_TEXT2.name,
                                                         Style.TEXT1.name: '', Style.TEXT2.name: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1_OR_TEXT2,
                                                         Style.MARKER.name: '', Style.TEXT1: ''},
                                                     {Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1_OR_TEXT2, Style.MARKER.name: '', Style.TEXT2: ''}])
        return nodes_gdf

    @staticmethod
    def get_rows_inside_area(gdf_rows: GeoDataFrame, gdf_area: GeoDataFrame) -> GeoDataFrame:
        return gdf_rows.loc[gpd.sjoin(gdf_rows, gdf_area, predicate="within").index].reset_index(drop=True)

    # -----------Others functions------------

    @staticmethod
    def get_groups_by_columns(gdf: GeoDataFrame, group_cols: list, default_keys: list = [], dropna: bool = False, sort=True):
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
    @time_measurement("prominence")
    def filter_peaks_by_prominence(nodes_gdf: GeoDataFrame, radius: float, min_prominence: float, ele_prominence_max_diff_ratio: float | None = None):
        """
        Filters peaks based on a simplified prominence criterion.

        For each peak in peaks, the function looks for any nearby peak within
        the given radius. If a higher peak exists and the elevation difference is less 
        than min_prominence, then the peak is considered less “prominent” and is filtered out.

        Parameters:
        - peaks (GeoDataFrame): must have a 'geometry' column (Point) and an 'elevation' column.
        - radius (float): search radius (in units of peaks) to look for competing peaks.
        - min_prominence (float): minimum required elevation difference for a peak to be considered prominent.

        Returns:
        - GeoDataFrame: a filtered GeoDataFrame containing only the peaks meeting the prominence threshold.
        """
        if(nodes_gdf.empty):
            return nodes_gdf
        if(radius <= 0 or min_prominence <= 0):
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

        # Boolean array to mark whether each peak is prominent
        prominence = pd.Series(index=peaks.index, dtype=float)
        is_prominent = pd.Series(index=peaks.index, dtype=bool)
        # For each peak, query neighbors within the specified radius
        for point_i, (coord, elev) in enumerate(zip(coords, elevations)):
            # Find indices of nearby peaks - make bigger until there are some peaks
            nearby_point_i = tree.query_ball_point(coord, r=radius)
            nearby_point_i.remove(point_i)

            # Check for any higher peak with a small elevation gap
            prominence.at[point_i] = elevations[point_i]
            for nearby_point in nearby_point_i:
                if elevations[nearby_point] > elev:
                    curr_peak_prominence = elevations[nearby_point] - elev
                    prominence.at[point_i] = curr_peak_prominence
                    if (curr_peak_prominence) < min_prominence:
                        is_prominent.at[point_i] = False
                        break

        peaks['prominence'] = prominence
        if(ele_prominence_max_diff_ratio is not None and ele_prominence_max_diff_ratio > 0):
            peaks = peaks[is_prominent & ~(peaks['prominence'] > peaks['ele'] * ele_prominence_max_diff_ratio)]
        else:
            peaks = peaks[is_prominent]
        return GdfUtils.combine_gdfs([peaks, rest])
    
    @staticmethod
    def filter_place_by_population(nodes_gdf: GeoDataFrame, place_to_filter: list, min_population: int):
        if(nodes_gdf.empty):
            return nodes_gdf
        if(min_population is None or min_population <= 0):
            return nodes_gdf
        places, rest = GdfUtils.filter_rows(
            nodes_gdf, {'place': place_to_filter}, compl=True)
        places = GdfUtils.filter_rows(places, {'population': ''})
        places = places[places['population'] >= min_population]
        return GdfUtils.combine_gdfs([places, rest])

    @staticmethod
    def get_common_borders(gdf1: GeoDataFrame, gdf2: GeoDataFrame):
        union1 = gdf1.union_all()  
        union2 = gdf2.union_all()
        common_border = union1.boundary.intersection(union2.boundary)
        if(not common_border):
            return GdfUtils.create_empty_gdf(gdf1.crs)
        intersection_gdf = gpd.GeoDataFrame({'geometry': [common_border]}, crs=gdf1.crs)
        intersection_gdf = intersection_gdf[
        intersection_gdf.geometry.type.isin(['LineString', 'MultiLineString'])]
        return GdfUtils.merge_lines_gdf(intersection_gdf)

