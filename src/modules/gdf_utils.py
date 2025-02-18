import warnings

from shapely import geometry
from shapely.geometry import Polygon, GeometryCollection, MultiLineString, LineString
import geopandas as gpd
import pandas as pd
import osmnx as ox
import pygeoops

from modules.utils import Utils
from osmium import FileProcessor
from common.map_enums import WorldSides, StyleKey
from common.custom_types import BoundsDict, DimensionsTuple, Point, WantedArea, RowsConditions, RowsConditionsAND
from common.common_helpers import time_measurement

from shapely.ops import unary_union, split, linemerge

# todo remove unused and refactor


class GdfUtils:

    # ------------getting informations------------
    @staticmethod
    def get_area_gdf(area: str | list[Point], fromCrs: str, toCrs: str | None = None) -> gpd.GeoDataFrame:
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
    @time_measurement("spojeni")
    def get_whole_area_gdf(whole_area: WantedArea, fromCrs: str, toCrs: str | None = None) -> gpd.GeoDataFrame:
        if (isinstance(whole_area, str) or (isinstance(whole_area, list) and len(whole_area) == 1)  # normal area
                or (isinstance(whole_area, list) and all(isinstance(item, tuple) and len(item) == 2 for item in whole_area))):
            if ((isinstance(whole_area, list) and len(whole_area) == 1)):  # one area in list
                return GdfUtils.get_area_gdf(whole_area[0], fromCrs, toCrs)
            else:
                return GdfUtils.get_area_gdf(whole_area, fromCrs, toCrs)
        elif (isinstance(whole_area, list)):  # area from multiple areas
            areas_gdf_list: list[gpd.GeoDataFrame] = []
            for area in whole_area:
                areas_gdf_list.append(GdfUtils.get_area_gdf(
                    area, fromCrs, toCrs))  # store areas to list of areas
            return GdfUtils.combine_gdfs(areas_gdf_list)
        else:  # area cannot be created
            raise ValueError("Invalid area format.")

    @staticmethod
    def get_bounds_gdf(*gdfs: gpd.GeoDataFrame, toCrs: str | None = None) -> BoundsDict:
        west = float('inf')
        south = float('inf')
        east = float('-inf')
        north = float('-inf')

        for gdf in gdfs:
            gdf_edit = gdf
            if (toCrs is not None):
                gdf_edit = gdf.to_crs(toCrs)
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
    def create_gdf_from_geometry_and_attributes(geometry: list, tags: list[dict], fromCrs: str) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(pd.DataFrame(tags).assign(
            geometry=geometry), crs=fromCrs)

    @staticmethod
    def create_gdf_from_file_processor(fp: FileProcessor, fromCrs: str, columns=[]) -> gpd.GeoDataFrame:
        gdf = gpd.GeoDataFrame.from_features(fp)
        if (gdf.empty):
            # create gdf with column geometry
            return GdfUtils.create_empty_gdf(fromCrs)
        else:
            return gdf.set_crs(fromCrs)

    @staticmethod
    def create_empty_gdf(crs: str, columns=["geometry"]) -> gpd.GeoDataFrame:
        if (crs is None):
            return gpd.GeoDataFrame(columns=columns)
        return gpd.GeoDataFrame(columns=columns, crs=crs)

    @staticmethod
    def create_gdf_from_bounds(area_bounds: BoundsDict, fromCrs: str, toCrs: str | None = None) -> gpd.GeoDataFrame:
        return GdfUtils.create_gdf_from_polygon(GdfUtils.create_polygon_from_bounds(area_bounds), fromCrs, toCrs)

    @staticmethod
    def create_gdf_from_polygon(area_polygon: Polygon, fromCrs: str, toCrs: str | None = None) -> gpd.GeoDataFrame:
        if (toCrs is None):
            return gpd.GeoDataFrame(geometry=[area_polygon], crs=fromCrs)
        else:
            return gpd.GeoDataFrame(geometry=[area_polygon], crs=fromCrs).to_crs(toCrs)

    @staticmethod
    def create_polygon_from_gdf_bounds(*gdfs: gpd.GeoDataFrame, toCrs: str | None = None) -> Polygon:
        bounds = GdfUtils.get_bounds_gdf(*gdfs, toCrs=toCrs)
        return GdfUtils.create_polygon_from_bounds(bounds)

    @staticmethod
    def create_polygon_from_gdf(*gdfs: gpd.GeoDataFrame, toCrs: str | None = None) -> Polygon:
        if (len(gdfs) == 1):
            if (toCrs is None):
                return gdfs[0].unary_union
            gdf_edit = gdfs[0].to_crs(toCrs)
            return gdf_edit.unary_union
        else:
            if (toCrs is None):
                combined_gdf = gpd.GeoDataFrame(
                    pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
            else:
                combined_gdf = gpd.GeoDataFrame(
                    pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs).to_crs(toCrs)
            return combined_gdf.unary_union

    @staticmethod
    def create_bg_gdf(map_area_gdf: gpd.GeoDataFrame, costline_gdf: gpd.GeoDataFrame, water_color: str, land_color: str) -> gpd.GeoDataFrame:
        def check_same_orientation(geom, splitter):
            # get intersetion by orientation of geom
            geom_orientation_inter = geom.intersection(splitter)
            geom_orientation_inter = GdfUtils.merge_lines_safe(
                geom_orientation_inter)

            # get intersetion by orientation of splitter
            split_orientation_inter = splitter.intersection(geom)
            split_orientation_inter = GdfUtils.merge_lines_safe(
                split_orientation_inter)
            if (not geom_orientation_inter.equals(split_orientation_inter)):
                return None

            # if both are linestring can compare
            if (isinstance(geom_orientation_inter, LineString) and isinstance(split_orientation_inter, LineString)):
                return list(geom_orientation_inter.coords) == list(split_orientation_inter.coords)

            # check if there is mulitlinestring or create empty list for FOR loop
            if isinstance(geom_orientation_inter, MultiLineString):
                geom_lines = list(geom_orientation_inter.geoms)
            else:
                geom_lines = [geom_orientation_inter]

            if isinstance(split_orientation_inter, MultiLineString):
                split_lines = list(split_orientation_inter.geoms)
            else:
                split_lines = [split_orientation_inter]

            # if some is multilinestring find components that are equal and check if it is equal by direction
            for g_line in geom_lines:
                for s_line in split_lines:
                    if g_line.equals(s_line):  # Check if they are the same
                        # check if they are same by orientation
                        return list(g_line.coords) == list(s_line.coords)

            return None

        if (costline_gdf.empty):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_data = []
        required_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
        # split one by one
        # splitters = linemerge(costline_gdf.geometry.unary_union)
        splitters = GdfUtils.merge_lines_safe(costline_gdf.geometry)
        splitters = list(splitters.geoms) if isinstance(
            splitters, MultiLineString) else [splitters]
        for splitter in splitters:
            geometry_collection = split(required_area_polygon, splitter)
            # splitter does not split area
            if (len(geometry_collection.geoms) == 1):
                continue
            # check if geom is on right or left of splitter
            for geom in geometry_collection.geoms:
                same_orientation = check_same_orientation(geom, splitter)
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
                bg_data.append({"geometry": geom, StyleKey.COLOR: color})
        # create gdf from data
        if (bg_data == []):
            return GdfUtils.create_empty_gdf(map_area_gdf.crs)
        bg_gdf = gpd.GeoDataFrame(
            bg_data, geometry="geometry", crs=map_area_gdf.crs)
        return bg_gdf

    # ------------editing gdf------------
    @staticmethod
    def change_bridges_and_tunnels(gdf, want_bridges: bool, want_tunnels: bool):
        gdf['layer'] = gdf.get('layer', 0)
        gdf.loc[GdfUtils.get_rows_filter(
            gdf, {'tunnel': '~', 'bridge': '~'}), 'layer'] = 0
        if (not want_bridges and not want_tunnels):
            gdf['layer'] = 0
            gdf.drop(columns=['bridge', 'tunnel'],
                     inplace=True, errors='ignore')

        if (not want_bridges):
            if ('layer' in gdf):
                # set layer to 0 in bridges - as normal ways
                gdf.loc[GdfUtils.get_rows_filter(
                    gdf, {'bridge': ''}), 'layer'] = 0
            gdf.drop(columns=['bridge'], inplace=True, errors='ignore')

        if (not want_tunnels):
            if ('layer' in gdf):
                # set layer to 0 in tunnels - as normal ways
                gdf.loc[GdfUtils.get_rows_filter(
                    gdf, {'tunnel': ''}), 'layer'] = 0
            gdf.drop(columns=['tunnel'], inplace=True, errors='ignore')
        return

    @staticmethod  # column and multipliers must be numeric otherwise it will throw error
    def multiply_column_gdf(gdf, column: StyleKey | str, multipliers: list[str | StyleKey] = [], scaling=None, filter: RowsConditions = []):
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
    def create_derivated_columns(gdf, new_column: StyleKey | str, base_column: StyleKey | str, multipliers: list[str | StyleKey] = [], filter: RowsConditions | RowsConditionsAND = [], scaling=None):
        # create new column with 0 if base not exists
        if (base_column not in gdf):
            gdf[new_column] = gdf.get(new_column, 0)
            return
        # multiply rows where column value is not empty
        rows_filter = GdfUtils.get_rows_filter(gdf, filter)
        gdf.loc[rows_filter, new_column] = gdf.loc[rows_filter, base_column]
        GdfUtils.multiply_column_gdf(gdf, new_column, multipliers, scaling)

    @staticmethod
    def change_columns_to_categorical(gdf: gpd.GeoDataFrame, columns: list) -> None:
        for column in columns:
            if (column in gdf):
                gdf[column] = gdf[column].astype("category")

    @staticmethod
    def combine_rows_gdf(gdf: gpd.GeoDataFrame, toCrs: int) -> gpd.GeoDataFrame:
        if (len(gdf) == 1):
            return gdf.to_crs(toCrs)
        return gpd.GeoDataFrame(geometry=[gdf.to_crs(toCrs).geometry.unary_union], crs=toCrs)

    # todo to normal utils
    @staticmethod
    def merge_lines_safe(geoms):
        unioned = unary_union(geoms)
        if unioned.is_empty:
            return unioned
        if unioned.geom_type == "LineString":
            return unioned
        if unioned.geom_type == "MultiLineString":
            try:
                return linemerge(unioned)
            except Exception as e:
                print(f"linemerge failed on MultiLineString: {e}")
                return unioned
        if unioned.geom_type == "GeometryCollection":
            lines = [geom for geom in unioned if geom.geom_type in [
                "LineString", "MultiLineString"]]
            if not lines:
                return unioned
            elif len(lines) == 1:
                return lines[0]
            else:
                # merge the extracted line geometries from geometry collection
                try:
                    return linemerge(MultiLineString(lines))
                except Exception as e:
                    print(f"linemerge failed on extracted lines: {e}")
                    return MultiLineString(lines)
        return unioned

    @staticmethod
    def change_columns_to_numeric(gdf: gpd.GeoDataFrame, columns: list[str]) -> None:
        for column in columns:
            if (column in gdf):
                gdf[column] = pd.to_numeric(gdf[column], errors='coerce')

    @time_measurement("mergeLines")
    @staticmethod
    def merge_lines_gdf(gdf: gpd.GeoDataFrame, columns_ignore: list[str | StyleKey] = []) -> gpd.GeoDataFrame:
        """Merge lines in GeoDataFrame to one line if they have same values in columns (except columns in columns_ignore).
        If want_bridges is True, merge all lines with same values in columns. If False, merge all lines with same values but ignore bridges.
        To merging geoms is used function merge_lines_safe that uses unary_union and linemerge from shapely.ops.
        It should merge multiple lines that are one line and that should prevents creating artifacts in plot.

        Args:
            gdf (gpd.GeoDataFrame): _description_
            want_bridges (bool): _description_
            columns_ignore (list[str  |  StyleKey], optional): _description_. Defaults to [].

        Returns:
            gpd.GeoDataFrame: _description_
        """
        columns_ignore = [*columns_ignore, 'geometry']
        # if dont want remove columns and than...
        columns = [
            col for col in gdf.columns if col not in columns_ignore]
        # merge all lines with same values in 'columns'
        merged = gdf.groupby(columns, dropna=False, observed=True).agg({
            'geometry': GdfUtils.merge_lines_safe
        })
        merged_gdf = gpd.GeoDataFrame(
            merged, geometry='geometry', crs=gdf.crs).reset_index()
        return merged_gdf

    @staticmethod
    def combine_gdfs(gdfs: list[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
        if (len(gdfs) == 1):
            return gdfs[0]
        return pd.concat(gdfs, ignore_index=True)  # concat to one gdf

    @staticmethod
    def expand_area_fitPaperSize(area_gdf: gpd.GeoDataFrame, pdf_dim: DimensionsTuple):
        bounds: BoundsDict = GdfUtils.get_bounds_gdf(area_gdf)
        return GdfUtils.create_gdf_from_bounds(Utils.adjust_bounds_to_fill_paper(bounds, pdf_dim), area_gdf.crs, None)

    @staticmethod
    def sort_gdf_by_column(gdf: gpd.GeoDataFrame, column_name: StyleKey, ascending: bool = True, na_position: str = 'first') -> gpd.GeoDataFrame:
        if (gdf.empty):
            return gdf
        if (column_name in gdf):
            return gdf.sort_values(by=column_name, ascending=ascending, na_position=na_position, kind="mergesort").reset_index(drop=True)
        warnings.warn("Cannot sort - unexisting column name")
        return gdf

    def change_crs(gdf: gpd.GeoDataFrame, toCrs: str) -> gpd.GeoDataFrame:
        if (gdf.empty):
            return gdf.set_crs(toCrs)
        return gdf.to_crs(toCrs)

    @staticmethod  # does not work if area is inside of another area - use or not use - by gap
    @time_measurement("inacurrate")
    def remove_common_boundary_inaccuracy(boundary_gdf: gpd.GeoDataFrame) -> None:
        """Remove common boundary inaccuracy in given GeoDataFrame 
        by shifting the common border of the one area to the neigbour area.

        Args:
            boundary_gdf (gpd.GeoDataFrame): Gdf with boundaries.
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
        boundary_gdf["geometry"] = boundary_gdf["geometry"].buffer(0)
        for i, row in boundary_gdf.iterrows():
            # find areas that share a boundary with row
            neighbors = boundary_gdf[boundary_gdf.geometry.touches(
                row.geometry)]
            for _, neighbor in neighbors.iterrows():
                # merge the border of the current area and neighbor
                merged_border = row.geometry.union(neighbor.geometry)
                boundary_gdf.at[i, 'geometry'] = merged_border

    # ------------Bool operations------------
    @staticmethod
    def is_geometry_inside_bounds(area_bounds: BoundsDict, polygon: GeometryCollection) -> bool:
        return GdfUtils.is_geometry_inside_geometry(GdfUtils.create_polygon_from_bounds(area_bounds), polygon)

    @staticmethod
    def are_gdf_geometry_inside_geometry(gdf: gpd.GeoDataFrame, polygon: GeometryCollection) -> bool:
        return gdf['geometry'].within(polygon).all()

    @staticmethod
    def is_geometry_inside_geometry(inner: GeometryCollection, outer: GeometryCollection) -> bool:
        return outer.contains(inner)

    @staticmethod
    def is_geometry_inside_geometry_threshold(inner: GeometryCollection, outer: GeometryCollection, threshold: float = 0.95) -> bool:
        bbox_area: float = inner.area
        intersection_area: float = inner.intersection(outer).area
        percentage_inside: float = intersection_area / bbox_area
        return percentage_inside >= threshold

    # ------------Filtering------------

    def get_rows_filter_AND(gdf: gpd.GeoDataFrame, conditions: RowsConditionsAND) -> pd.Series:
        filter_mask = pd.Series(True, index=gdf.index)
        for column_name, column_value in conditions.items():
            if column_name not in gdf.columns:
                # handle missing columns
                if (isinstance(column_value, list)):
                    # If any value in the list start with "~", the columns can be skipped
                    if any(str(v).startswith("~") for v in column_value):
                        continue
                    else:
                        # If none of the values start with "~", the column must exists
                        filter_mask &= False
                        break
                # not equal to value after ~ or NA
                elif column_value.startswith("~"):
                    continue
                # column should equal the value or should not be NA (but column doesn't exist)
                else:
                    filter_mask &= False
                    break

            else:
                if isinstance(column_value, list):
                    # start with all rows excluded
                    condition_mask = pd.Series(False, index=gdf.index)

                    if not column_value:
                        # If the list is empty, the column should not be NA
                        condition_mask |= gdf[column_name].notna()
                    else:
                        for value in column_value:
                            if value == "":  # Not NA
                                condition_mask |= gdf[column_name].notna()
                            elif value == "~":  # Column should be NA
                                condition_mask |= gdf[column_name].isna()
                            # Not equal to value after ~
                            elif value.startswith("~"):
                                condition_mask |= (
                                    gdf[column_name] != value[1:])
                            else:  # Column equal the value
                                condition_mask |= (gdf[column_name] == value)
                        filter_mask &= condition_mask

                else:
                    if column_value == '':  # Not NA
                        filter_mask &= gdf[column_name].notna()
                    elif column_value.startswith("~"):
                        if column_value == "~":  # column should be NA
                            filter_mask &= gdf[column_name].isna()
                        else:  # column should not equal the value after ~
                            filter_mask &= (
                                gdf[column_name] != column_value[1:])
                    else:  # column should equal the value
                        filter_mask &= (gdf[column_name] == column_value)
        return filter_mask

    def get_rows_filter(gdf: gpd.GeoDataFrame, conditions: RowsConditions | RowsConditionsAND) -> pd.Series:
        filter_mask = pd.Series(False, index=gdf.index)
        # if is not list
        if isinstance(conditions, dict):
            conditions = [conditions]
        elif not conditions:
            conditions = [{}]  # empty condition - all rows

        for and_conditions in conditions:
            filter_mask |= GdfUtils.get_rows_filter_AND(gdf, and_conditions)
        return filter_mask

    def filter_rows(gdf: gpd.GeoDataFrame, conditions: RowsConditions | RowsConditionsAND,
                    neg: bool = False, compl: bool = False) -> gpd.GeoDataFrame:
        filter_mask = GdfUtils.get_rows_filter(gdf, conditions)
        return GdfUtils.return_filtered(gdf, filter_mask, neg, compl)

    @staticmethod
    def return_filtered(gdf: gpd.GeoDataFrame, filter_mask: pd.Series, neg: bool = False,
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
    def get_rows_inside_area(gdf_rows: gpd.GeoDataFrame, gdf_area: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return gdf_rows[gdf_rows.geometry.within(gdf_area.unary_union)].reset_index(drop=True)

    @staticmethod
    # todo use one filter creation and than add with 'and' all ways that are longer, that will leave false with all that i want...
    @time_measurement("short ways filter")
    def filter_short_ways(gdf: gpd.GeoDataFrame, toCrs: str, min_lenght: float = 2) -> gpd.GeoDataFrame:

        gdf_mercator_projected = gdf.to_crs(toCrs)
        condition: pd.Series[bool] = gdf_mercator_projected.geometry.length > min_lenght
        filtered_gdf_mercator_projected = gdf_mercator_projected[condition]
        return filtered_gdf_mercator_projected.to_crs(gdf.crs)

    # ------------Others functions------------

    @staticmethod
    def buffer_gdf_same_distance(gdf: gpd.GeoDataFrame, distance: float, toCrs: str, resolution: int = 16,
                                 cap_style: str = 'round', join_style: str = 'round') -> gpd.GeoDataFrame:
        gdf_mercator_projected = gdf.to_crs(toCrs)
        gdf_mercator_projected['geometry'] = gdf_mercator_projected['geometry'].buffer(
            distance, resolution=resolution, cap_style=cap_style, join_style=join_style)
        return gdf_mercator_projected.to_crs(toCrs)

    @staticmethod
    def buffer_gdf_column_value_distance(gdf: gpd.GeoDataFrame, column_key: str, toCrs: str,
                                         additional_padding: float = 0, resolution: int = 16,
                                         cap_style: str = 'round', join_style: str = 'round') -> gpd.GeoDataFrame:
        gdf_mercator_projected = gdf.to_crs(toCrs)
        gdf_mercator_projected['geometry'] = gdf_mercator_projected.apply(
            lambda row: row['geometry'].buffer(row[column_key] + additional_padding, resolution=resolution,
                                               cap_style=cap_style, join_style=join_style), axis=1
        )
        return gdf_mercator_projected.to_crs(gdf.crs)

    @staticmethod
    def aggregate_close_lines(gdf: gpd.GeoDataFrame, toCrs: str, aggreagate_distance: float = 5) -> gpd.GeoDataFrame:
        if (gdf.empty):
            return gdf
        gdf_mercator_projected = gdf.to_crs(toCrs)
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
        # gdf_merged_diss = gdf_merged_diss.to_crs(gdf.crs.epsg)
        return gdf_merged_diss


    @staticmethod
    def get_groups_by_columns(df, group_cols, dropna=True, default_key=None):
     
        missing = [col for col in group_cols if col not in df.columns]
        if missing:
            if default_key is None:
                # Default key is np.nan for a single column, or a tuple of np.nan for multiple columns.
                default_key = pd.NA if len(group_cols) == 1 else tuple(pd.NA for _ in group_cols)
            return [(default_key, df)]
        else:
            return df.groupby(group_cols, dropna=dropna)