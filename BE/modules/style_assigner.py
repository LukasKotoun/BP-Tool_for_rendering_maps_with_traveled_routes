"""
Assigning styles to GeoDataFrame based on conditions.
Author: Lukáš Kotoun, xkotou08
"""
import warnings

import pandas as pd
from geopandas import GeoDataFrame
from modules.gdf_utils import GdfUtils

from common.map_enums import Style
from common.custom_types import ElementStyles


class StyleManager:
    def __init__(self):
        pass

    @staticmethod
    def __check_range(range_str, zoom_level):
        # check if - is in string if not take it as single value
        try:
            if "-" not in range_str:
                return int(range_str) == zoom_level

            lower_str, upper_str = range_str.split("-")
            lower, upper = int(lower_str), int(upper_str)
            if (lower > upper):
                lower, upper = upper, lower
            return lower <= zoom_level <= upper
        except ValueError:
            warnings.warn(
                f"zoom_range ({range_str}) is not int but {type(range_str)}")
            return False

    @staticmethod
    def convert_variables_from_dynamic(variable, zoom_level) -> ElementStyles:
        if (not isinstance(variable, dict)):
            return variable
        zoom_variable = variable
        for zoom_range, zoom_value in variable.items():
            if (StyleManager.__check_range(zoom_range, zoom_level)):
                return zoom_value
        return zoom_variable

    @staticmethod
    def convert_from_dynamic(dynamic_styles, zoom_level) -> ElementStyles:
        normal_styles = []
        for filter, styles_default, *zoom_styles in dynamic_styles:
            # convert list to dict
            zoom_styles = zoom_styles[0] if zoom_styles else {}
            styles_filter = {}
            if (not isinstance(zoom_styles, dict)):
                warnings.warn(
                    f"zoom_styles ({zoom_styles})is not dict but {type(zoom_styles)}")
                continue
            for zoom_range, zoom_style_values in zoom_styles.items():
                if (StyleManager.__check_range(zoom_range, zoom_level)):
                    styles_filter = {**zoom_style_values, **styles_filter}
            styles = {**styles_default, **styles_filter}
            normal_styles.append((filter, styles))
        return normal_styles

    @staticmethod
    def assign_styles(gdf: GeoDataFrame, conditons_styles: ElementStyles, dont_categorize: list[str] = []) -> None:
        """
        Assign styles to gdf rows based on conditions in styles using pandas filtres."""
        if (gdf.empty):
            return
        new_styles: Style = set()
        # assign styles from most general to most specific by writing to columns in styles
        # assing from least specific to most specific
        for conditons, styles in reversed(conditons_styles):
            filtered_rows: pd.Series = GdfUtils.get_rows_filter(gdf, conditons)
            for key, value in styles.items():
                if isinstance(value, tuple) or isinstance(value, list):
                    # write whole tuple to one column cell. Dont need to match index to filtered_rows, it will be assinged by value
                    tmp = pd.Series([value] * filtered_rows.sum())
                    gdf.loc[filtered_rows, key] = tmp.values
                else:
                    gdf.loc[filtered_rows, key] = value
            new_styles.update(styles.keys())

        # convert object columns to pandas category
        categorical_list = []
        for style_column in new_styles:
            if (style_column in gdf and style_column not in dont_categorize and gdf[style_column].dtype == object):
                categorical_list.append(style_column)
        GdfUtils.change_columns_to_categorical(gdf, categorical_list)

    @staticmethod
    def scale_styles(all_styles: ElementStyles, styles_to_scale: list[str], map_scaling_factor: float):
        styles_to_scale = set(styles_to_scale)
        if (not styles_to_scale):
            return
        for filter, styles_dict in all_styles:
            for key in styles_dict.keys() & styles_to_scale:
                styles_dict[key] *= map_scaling_factor
