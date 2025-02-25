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
from modules.geom_utils import GeomUtils
from common.map_enums import WorldSides, Style, MinParts
from common.custom_types import BoundsDict, DimensionsTuple, WantedAreas, RowsConditions, RowsConditionsAND, WantedArea
from common.common_helpers import time_measurement


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
                    "The requested location has not been found.") # todo should be validated on FE
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
    @time_measurement("spojeni")
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
        # Separate rows with category == 0 and nonzero categories.
        gdf_zero, gdf_nonzero = GdfUtils.filter_rows(
            gdf, {combine_by: 0}, compl=True)
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
                same_orientation = GeomUtils.check_same_orientation(geom, splitter)
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
        if (bg_data == []):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_gdf = GeoDataFrame(
            bg_data, geometry="geometry", crs=map_area_gdf.crs)
        return bg_gdf

    # ------------editing gdf------------
    @staticmethod
    def remove_columns(gdf: GeoDataFrame, columns: list[str | Style], neg = False) -> GeoDataFrame:
        if(neg):
            gdf.drop(columns=[col for col in gdf.columns if col not in columns], inplace=True, errors='ignore')
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
    def combine_rows_gdf(gdf: GeoDataFrame, toCrs: int) -> GeoDataFrame:
        if (len(gdf) == 1):
            return gdf.to_crs(toCrs)
        return GeoDataFrame(geometry=[gdf.to_crs(toCrs).geometry.unary_union], crs=toCrs)


    @staticmethod
    def change_columns_to_numeric(gdf: GeoDataFrame, columns: list[str]) -> None:
        for column in columns:
            if (column in gdf):
                gdf[column] = pd.to_numeric(gdf[column], errors='coerce')

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
        columns_ignore = [*columns_ignore, gdf.geometry.name]
        # if dont want remove columns and than...
        columns = [
            col for col in gdf.columns if col not in columns_ignore]
        # merge all lines with same values in 'columns'
        merged = gdf.groupby(columns, dropna=False, observed=True).agg({
            gdf.geometry.name: GeomUtils.merge_lines_safe
        })
        merged_gdf = GeoDataFrame(
            merged, geometry=gdf.geometry.name, crs=gdf.crs).reset_index()
        return merged_gdf

    @staticmethod
    def combine_gdfs(gdfs: list[GeoDataFrame]) -> GeoDataFrame:
        if (len(gdfs) == 1):
            return gdfs[0]
        return pd.concat(gdfs, ignore_index=True)  # concat to one gdf

    @staticmethod
    def expand_gdf_area_fitPaperSize(area_gdf: GeoDataFrame, pdf_dim: DimensionsTuple):
        bounds: BoundsDict = GdfUtils.get_bounds_gdf(area_gdf)
        return GdfUtils.create_gdf_from_bounds(Utils.adjust_bounds_to_fill_paper(bounds, pdf_dim), area_gdf.crs, None)

    @staticmethod
    def sort_gdf_by_column(gdf: GeoDataFrame, column_name: Style, ascending: bool = True, na_position: str = 'first') -> GeoDataFrame:
        if (gdf.empty):
            return gdf
        if (column_name in gdf):
            return gdf.sort_values(by=column_name, ascending=ascending, na_position=na_position, kind="mergesort").reset_index(drop=True)
        warnings.warn("Cannot sort - unexisting column name")
        return gdf

    def change_crs(gdf: GeoDataFrame, toCrs: str) -> GeoDataFrame:
        if (gdf.empty):
            return gdf.set_crs(toCrs)
        return gdf.to_crs(toCrs)

    @staticmethod  # does not work if area is inside of another area - use or not use - by gap
    @time_measurement("inacurrate")
    def remove_common_boundary_inaccuracy(boundary_gdf: GeoDataFrame) -> None:
        """Remove common boundary inaccuracy in given GeoDataFrame 
        by shifting the common border of the one area to the neigbour area.

        Args:
            boundary_gdf (GeoDataFrame): Gdf with boundaries.
        """
        # # by shifting area...
        # boundary_gdf['area'] = boundary_gdf.geometry.area
        # boundary_gdf = boundary_gdf.sort_values(by='area', ascending=True)
        # # from smallest to biggest area
        # for i, area1 in boundary_gdf.iterrows():
        #     for j, area2 in boundary_gdf.iterrows():
        #         if i >= j:
        #             continue
        #         # find the shared border
        #         common_border = area1.geometry.intersection(area2.geometry)
        #         if not common_border.is_empty:
        #             # shift area2's border to the area1's border
        #             adjusted_area2 = area2.geometry.difference(common_border)
        #             precise_area2 = adjusted_area2.union(common_border)

        # boundary_gdf.loc[j, "geometry"] = adjusted_area2

        # work by creating from 2 seperated areas row with combined area and one row with original area
        # # remove small gaps between areas - does not work always but better then above??
        boundary_gdf[boundary_gdf.geometry.name] = boundary_gdf["geometry"].buffer(0)
        for i, row in boundary_gdf.iterrows():
            # find areas that share a boundary with row
            neighbors = boundary_gdf[boundary_gdf.geometry.touches(
                row.geometry)]
            for _, neighbor in neighbors.iterrows():
                # merge the border of the current area and neighbor
                merged_border = row.geometry.union(neighbor.geometry)
                boundary_gdf.at[i, boundary_gdf.geometry.name] = merged_border
        return boundary_gdf
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
                                          Style.EDGEWIDTH.name: '', Style.EDGE_COLOR.name: '', Style.ALPHA.name: ''})

    @staticmethod
    def filter_invalid_nodes_min_req(nodes_gdf: GeoDataFrame) -> GeoDataFrame:
        nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [{Style.MIN_REQ_POINT.name: MinParts.MARKER.name, Style.MARKER.name: '', Style.COLOR.name: ''},
                                                     {Style.MIN_REQ_POINT.name: MinParts.MARKER_TEXT1.name,
                                                         Style.MARKER.name: '', Style.TEXT1.name: ''},
                                                     {Style.MIN_REQ_POINT.name: MinParts.MARKER_TEXT2.name,
                                                         Style.MARKER.name: '', Style.TEXT2.name: ''},
                                                     {Style.MIN_REQ_POINT.name: MinParts.MARKER_TEXT1_TEXT2.name,
                                                         Style.MARKER.name: '', Style.TEXT1.name: '', Style.TEXT2.name: ''},
                                                     {Style.MIN_REQ_POINT.name: MinParts.TEXT1.name,
                                                         Style.TEXT1.name: ''},
                                                     {Style.MIN_REQ_POINT.name: MinParts.TEXT2.name,
                                                         Style.TEXT2.name: ''},
                                                     {Style.MIN_REQ_POINT.name: MinParts.TEXT1_TEXT2.name, Style.TEXT1.name: '', Style.TEXT2.name: ''}])
        nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [{Style.MARKER.name: ''},
                                                     {Style.TEXT1.name: ''},
                                                     {Style.TEXT2.name: ''}])

        return nodes_gdf

    @staticmethod
    def get_rows_inside_area(gdf_rows: GeoDataFrame, gdf_area: GeoDataFrame) -> GeoDataFrame:
        return gdf_rows.loc[gpd.sjoin(gdf_rows, gdf_area, predicate="within").index]

    # -----------Others functions------------

    @staticmethod
    def get_groups_by_columns(gdf, group_cols, default_keys=None, dropna=False):
        # get missing columns and replace with default key if missing
        # todo make quicker - refactor
        if len(group_cols) != len(default_keys):
            default_keys = [None] * len(group_cols)
        for col, default in zip(group_cols, default_keys):
            if col not in gdf.columns:
                gdf[col] = default

        if (len(group_cols) == 1):
            return gdf.groupby(group_cols[0], dropna=dropna, observed=False)
        return gdf.groupby(group_cols, dropna=dropna, observed=False)



