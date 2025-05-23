"""
Functions for handling map realated tasks.
Author: Lukáš Kotoun, xkotou08
"""
import os
import glob
import warnings
import math
import jwt
import rtree
import textwrap
import pandas as pd
from fastapi import HTTPException, status
import datetime
from shapely import geometry
from shapely.geometry import Point
from matplotlib.transforms import Bbox

from modules.geom_utils import GeomUtils
from common.custom_types import DimensionsTuple, OptDimensionsTuple, BoundsDict
from common.map_enums import MapOrientation, WorldSides


class Utils:
    @staticmethod
    def set_orientation(tuple: DimensionsTuple, wanted_orientation: MapOrientation) -> DimensionsTuple:
        if (wanted_orientation == MapOrientation.LANDSCAPE.value):
            return tuple if tuple[0] > tuple[1] else tuple[::-1]
        # portrait
        return tuple if tuple[0] < tuple[1] else tuple[::-1]

    @staticmethod
    def resolve_paper_dimensions(map_dimensions: DimensionsTuple, map_orientaion: MapOrientation,
                                 paper_dimensions: OptDimensionsTuple, given_paper_smaller_side=True):
        """Calulate missing paper dimension based on map dimensions and wanted paper orientation."""
        if (given_paper_smaller_side):
            # given paper size is smaller get map smaller side (coresponding size)
            # if map orientation is landscape smaller size is height
            coresponding_map_side: float = map_dimensions[
                1] if map_orientaion == MapOrientation.LANDSCAPE.value else map_dimensions[0]
        else:
            # given paper size is bigger get map bigger side (coresponding size)
            # if map orientation is landscape bigger size is width
            coresponding_map_side: float = map_dimensions[
                0] if map_orientaion == MapOrientation.LANDSCAPE.value else map_dimensions[1]

        other_map_side: float = map_dimensions[1] if math.isclose(
            coresponding_map_side, map_dimensions[0]) else map_dimensions[0]

        if (paper_dimensions[0] is not None):
            given_paper_side: float = paper_dimensions[0]
        else:
            given_paper_side: float = paper_dimensions[1]
        side_ratio: float = coresponding_map_side/given_paper_side
        resolved_pdf_side: float = other_map_side/side_ratio
        return (int(given_paper_side), int(resolved_pdf_side))

    @staticmethod
    def adjust_paper_dimensions(map_dimensions: DimensionsTuple,
                                paper_dimensions: OptDimensionsTuple,
                                given_smaller_paper_side: bool = True,
                                wanted_orientation=MapOrientation.AUTOMATIC.value) -> DimensionsTuple:
        """Edit paper dimensions based on map dimensions and wanted orientation.
            If one of the paper dimensions is None it will be calculated based on map dimensions and wanted orientation."""

        if (wanted_orientation == MapOrientation.AUTOMATIC.value):
            if map_dimensions[0] >= map_dimensions[1]:
                map_orientaion: MapOrientation = MapOrientation.LANDSCAPE.value
            else:
                map_orientaion: MapOrientation = MapOrientation.PORTRAIT.value
        else:
            map_orientaion: MapOrientation = wanted_orientation

        if (paper_dimensions.count(None) == 1):
            paper_dimensions = Utils.resolve_paper_dimensions(
                map_dimensions, map_orientaion, paper_dimensions, given_smaller_paper_side)
        elif (paper_dimensions.count(None) > 1):
            raise ValueError("Only one paper dimension can be None")

        # flip resolved orientation
        if (wanted_orientation == MapOrientation.AUTOMATIC.value):
            paper_dimensions = Utils.set_orientation(
                paper_dimensions, map_orientaion)
        else:
            paper_dimensions = Utils.set_orientation(
                paper_dimensions, wanted_orientation)

        return paper_dimensions

    @staticmethod
    def calc_ratios(area1: DimensionsTuple, area2: DimensionsTuple) -> DimensionsTuple:
        # calculate the ratio area1 to area2
        width_ratio = area1[0] / area2[0]
        height_ratio = area1[1] / area2[1]
        return width_ratio, height_ratio

    @staticmethod
    def get_dimensions(bounds: BoundsDict) -> DimensionsTuple:
        width = abs(bounds[WorldSides.EAST.value] -
                    bounds[WorldSides.WEST.value])  # east - west
        height = abs(bounds[WorldSides.NORTH.value] -
                     bounds[WorldSides.SOUTH.value])  # north - south
        return width, height

    @staticmethod
    def calc_bounds_to_fill_paper_with_ratio(center_point: Point, pdf_dim: DimensionsTuple,
                                             bigger_area_dim: DimensionsTuple, bigger_pdf_dim: DimensionsTuple) -> BoundsDict:
        """Calculate bounds of area to fill paper with ratio (bigger area/bigger pdf dimensions) for area preview.

            Calc bounds that will have center in center_point and will fill whole paper.
            Function will first calculated new dimensions that will match bigger pdf ratios and one side will fill pdf side.
            This dimensions will be adjusted by function adjust_bounds_to_fill_paper to fill whole paper by expanding the remaining side to fill pdf paper.

        Args:
            center_point (Point): center points of final bounds (best in mercator projection)
            pdf_dim (DimensionsTuple): currect pdf dim that will be created
            bigger_area_dim (DimensionsTuple): area that will be used to calculate ratio (best in mercator projection)
            bigger_pdf_dim (DimensionsTuple): pdf that will be used to calculate ratio

        Returns:
            BoundsDict: Bounds that will fill whole paper
        """
        pdf_to_area_ratio_bigger = Utils.calc_ratios(
            bigger_area_dim, bigger_pdf_dim)
        # Calc from eqation (must have same aspects) -> bigger_area_dim (in M) / bigger_pdf_dim ==  area_dim(M) /pdf_dim
        #  bigger_area_dim (in M)/ bigger_pdf_dim ==  area_dim(M) /pdf_dim => areaDim(M) == bigger_area_dim (in M)/bigger_pdf_dim*pdf_dim =>
        #  => areaDim(M) == pdf_to_area_ratio_bigger * pdf_dim
        new_width = pdf_dim[0] * pdf_to_area_ratio_bigger[0]
        new_height = pdf_dim[1] * pdf_to_area_ratio_bigger[1]

        return Utils.adjust_bounds_to_fill_paper({
            WorldSides.WEST.value: center_point.x - (new_width / 2),
            WorldSides.EAST.value: center_point.x + (new_width / 2),
            WorldSides.SOUTH.value: center_point.y - (new_height / 2),
            WorldSides.NORTH.value: center_point.y + (new_height / 2)
        }, pdf_dim)

    @staticmethod
    def adjust_bounds_to_fill_paper(area_bounds: BoundsDict, pdf_dim: DimensionsTuple) -> BoundsDict:
        """Adjust one side of bounds (that dont will that dimension of paper) to fill whole paper.

            Function will adjust one side of bounds to fill whole paper by expanding the remaining side to fill pdf paper.
            It will calculate aspect ratio of bounds and paper and than adjust the side that is shorter than paper side.
        Args:
            area_bounds (BoundsDict): Bounds where one bound will fill one paper dimension (best in mercator projection)
            pdf_dim (DimensionsTuple): Paper dimension to fill

        Returns:
            BoundsDict: Bounds that will fill whole paper
        """
        width, height = Utils.get_dimensions(area_bounds)
        # width / height
        paper_aspect_ratio = pdf_dim[0] / pdf_dim[1]
        current_aspect_ratio = width / height

        if current_aspect_ratio < paper_aspect_ratio:
            # Current aspect have shorther (smaller) width to height ratio than paper => adjust width
            # Expand width
            # w/h == pw/ph => w = h * (pw/ph)
            new_width = height * paper_aspect_ratio
            width_diff = (new_width - width) / 2
            area_bounds[WorldSides.WEST.value] -= width_diff
            area_bounds[WorldSides.EAST.value] += width_diff
        else:
            # Current aspect have longer (bigger) width to height ratio than paper => adjust height
            # Expand height
            # w/h == pw/ph => h = w / (pw/ph)
            new_height = width / paper_aspect_ratio
            height_diff = (new_height - height) / 2
            area_bounds[WorldSides.SOUTH.value] -= height_diff
            area_bounds[WorldSides.NORTH.value] += height_diff

        return area_bounds

    @staticmethod
    def calc_map_scaling_factor(map_dimensions_m, paper_dimensions_mm):

        map_scaling_factor = (map_dimensions_m[0] + map_dimensions_m[1])
        paper_scaling_factor = (
            paper_dimensions_mm[0] + paper_dimensions_mm[1])
        return (paper_scaling_factor / map_scaling_factor)

    @staticmethod
    def get_scale(map_bounds: BoundsDict, paper_dimensions_mm: DimensionsTuple) -> int:
        """
        Calculate the scale for the map based on the map bounds and the paper dimensions.
        In unit of 1:scale, where 1 is mm on paper and scale is m irl. 
        For example scale 95 means 1mm on paper is 95m in real life.
        If paper have 200mm the map will have 

        Returns:
            int: Scale as 1cm on paper is 'scale number' m in real life
        """
        # Use middle longitude for vertical distance
        midx = (map_bounds[WorldSides.NORTH.value] +
                map_bounds[WorldSides.SOUTH.value]) / 2

        height = GeomUtils.get_distance((map_bounds[WorldSides.NORTH.value], map_bounds[WorldSides.WEST.value]), (
            map_bounds[WorldSides.SOUTH.value], map_bounds[WorldSides.WEST.value]))
        width = GeomUtils.get_distance(
            (midx, map_bounds[WorldSides.WEST.value]), (midx, map_bounds[WorldSides.EAST.value]))
        # Calculate the scale for width and height
        scale_width = width / paper_dimensions_mm[0]
        scale_height = height / paper_dimensions_mm[1]

        # Use the larger scale to ensure the entire area fits on the paper
        scale = max(scale_width, scale_height)

        return scale

    @staticmethod
    def get_zoom_level(value, mapping, threshold_above_lower=0.25):
        zooms = sorted(mapping.items(), key=lambda x: -x[1])
        for i in range(len(zooms) - 1):
            higher_level, higher_value = zooms[i]
            lower_level, lower_value = zooms[i + 1]

            # Compute the threshold at threshold_above_lower from lower to higher value
            # so if is between to values it should be higher zoom
            threshold = lower_value + \
                ((higher_value - lower_value) * threshold_above_lower)

            if value >= threshold:
                return higher_level

        return zooms[-1][0]  # lowest level

    @staticmethod
    def wrap_text(text: str, width: int, replace_whitespace: bool = False):
        if (text is None):
            return None
        if (width == 0 or width is None):
            return text
        width = int(width)
        text = str(text)
        return textwrap.fill(text, width, replace_whitespace=False)

    @staticmethod
    def expand_bbox(bbox: Bbox, percent_expand: int = 0) -> Bbox:
        if (percent_expand == 0):
            return bbox
        width = bbox.x1 - bbox.x0
        height = bbox.y1 - bbox.y0
        expand_x = (width * percent_expand) / 100
        expand_y = (height * percent_expand) / 100
        expanded_bbox = Bbox.from_extents(bbox.x0 - expand_x, bbox.y0 - expand_y,
                                          bbox.x1 + expand_x, bbox.y1 + expand_y)
        return expanded_bbox

    @staticmethod
    def expand_bounds_dict(bounds: BoundsDict, percent_expand: int = 0) -> Bbox:
        if (percent_expand == 0):
            return bounds
        width = bounds[WorldSides.EAST.value] - bounds[WorldSides.WEST.value]
        height = bounds[WorldSides.NORTH.value] - \
            bounds[WorldSides.SOUTH.value]
        expand_x = (width * percent_expand) / 100
        expand_y = (height * percent_expand) / 100
        return {
            WorldSides.WEST.value: bounds[WorldSides.WEST.value] - expand_x,
            WorldSides.EAST.value: bounds[WorldSides.EAST.value] + expand_x,
            WorldSides.SOUTH.value: bounds[WorldSides.SOUTH.value] - expand_y,
            WorldSides.NORTH.value: bounds[WorldSides.NORTH.value] + expand_y
        }

    @staticmethod
    def get_name_tuple_value(row, column_name: str, default_value: any = None):
        value = getattr(row, column_name, None)
        if pd.isna(value):
            return default_value
        return value

    @staticmethod
    def is_bbox_valid(bbox: Bbox):
        return bbox is not None and bbox.x0 < bbox.x1 and bbox.y0 < bbox.y1

    @staticmethod
    def check_bbox_position(bbox_to_overlap: Bbox, bbox_to_overflow: Bbox, bbox_index: rtree.index.Index | None,
                            text_bounds_overflow_threshold, reqired_area_polygon) -> bool:
        if (bbox_index is not None):
            try:
                matches = list(bbox_index.intersection(
                    bbox_to_overlap.extents))
                for match in matches:
                    if (match is not None):
                        return False
            except Exception as e:
                print(e)
                return False

        # check overlap with other bbox
        if math.isclose(text_bounds_overflow_threshold, 0):
            return True

        # check if bbox is inside required area
        bbox_polygon = geometry.box(
            bbox_to_overflow.x0, bbox_to_overflow.y0, bbox_to_overflow.x1, bbox_to_overflow.y1)
        return GeomUtils.is_geometry_inside_geometry_threshold(bbox_polygon, reqired_area_polygon, text_bounds_overflow_threshold)

    @staticmethod
    def cumulative_zoom_size_multiplier(data, key):
        """Returns a dictionary where each key maps to {key: cumulative value, ...extra dict...}.

        Each multiplier in data can be:
        - A number, or
        - A tuple: (number, extra_dict), where extra_dict is merged into the output.
        """
        cumulative = None
        result = {}
        for dict_key, multiplier in data.items():
            if isinstance(multiplier, tuple):
                # Unpack the tuple into the numerical multiplier and extra dictionary.
                multiplier_value, extra_dict = multiplier
            else:
                multiplier_value = multiplier
                extra_dict = {}

            if cumulative is None:
                cumulative = multiplier_value
            else:
                cumulative *= multiplier_value

            result[dict_key] = {key: cumulative, **extra_dict}

        return result

    @staticmethod
    def ensure_dir_exists(dir_path: str):
        if (dir_path is None):
            return ""
        if (dir_path[-1] != '/'):
            dir_path += '/'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return dir_path

    @staticmethod
    def remove_file(file_path: str):
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            warnings.warn(f"Error cleaning up file {file_path}: {str(e)}")

    @staticmethod
    def remove_files(files_list: list[str]):
        """Delete files in list"""
        for file_path in files_list:
            Utils.remove_file(file_path)

    @staticmethod
    def create_task_access_token(data: dict, expires_delta: datetime.timedelta, algorithm: str, secret_key: str):
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt

    @staticmethod
    def decode_jwt(token, algorithm: str, secret_key: str):
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    @staticmethod
    def create_osm_files_mapping(folder: str) -> dict[str, str]:
        """From filder with osm files create dict with key as file name without extension  and value as file path"""
        folder = Utils.ensure_dir_exists(folder)

        osm_files_dict = {}
        # Search for all .osm and .osm.pbf files in the specified folder
        osm_pattern = os.path.join(folder, "*.osm")
        osm_pbf_pattern = os.path.join(folder, "*.osm.pbf")
        osm_files = glob.glob(osm_pbf_pattern) + glob.glob(osm_pattern)

        for file_path in osm_files:
            file_name = os.path.basename(file_path).split('.')[0]
            counter = 1
            while file_name in osm_files_dict:
                # If the file name already exists, append a counter to make it unique
                file_name = f"{file_name}_{counter}"
                counter += 1
            osm_files_dict[file_name] = file_path

        return osm_files_dict
