import warnings
from common.common_helpers import time_measurement

import pandas as pd
import numpy as np
from geopandas import GeoDataFrame
from modules.gdf_utils import GdfUtils
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

from modules.utils import Utils
from common.map_enums import StyleKey, ColorMode, StyleType
from common.custom_types import FeaturesCategoriesStyles, WantedCategories, FeatureStyles, FeaturesCategoryStyle, ElementStyles

# element or static or map element and gpx...?


class StyleAssigner:
    def __init__(self):
        pass
    
    @staticmethod
    def convert_dynamic_to_normal(dynamic_styles, zoom_level):
        def check_range(range_str, zoom_level):
            lower_str, upper_str = range_str.split("-")
            lower, upper = int(lower_str), int(upper_str)
            if (lower > upper):
                lower, upper = upper, lower
            return lower <= zoom_level <= upper

        normal_styles = []
        for filter, styles_default, *zoom_styles in dynamic_styles:
            zoom_styles = zoom_styles[0] if zoom_styles else {} # convert list to dict
            styles_filter = {}
            for zoom_range, zoom_style_values in zoom_styles.items():
                if (check_range(zoom_range, zoom_level)):
                    styles_filter = {**zoom_style_values, **styles_filter}
            styles = {**styles_default, **styles_filter}
            normal_styles.append((filter, styles))
        return normal_styles

    
    @staticmethod
    @time_measurement("styles assign")
    def assign_styles(gdf: GeoDataFrame, conditons_styles: ElementStyles, dont_categorize: list[str] = [])  -> None:
        if(gdf.empty):
            return
        new_styles: StyleKey = set()
        # assign styles from most general to most specific by writing to columns in styles
        for conditons, styles in reversed(conditons_styles): # assing from least specific to most specific
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


    # todo move to FE
    @staticmethod
    def generate_shades_of_color(base_color, num_shades, min_factor=0.3, max_factor=0.7) -> list[tuple[float, float, float, float]]:
        """
        Generate a range of shades from a base color by adjusting the brightness.

        Parameters:
        - base_color: The base color in any valid Matplotlib color format (e.g., 'red', '#FF0000', or RGB tuple).
        - min_factor: The minimum factor for the brightness (0.0 is completely dark, 1.0 is original color).
        - max_factor: The maximum factor for the brightness (1.0 is the original color, values > 1.0 are brighter).
        - num_shades: The number of shades to generate in the range.

        Returns:
        - A list of colors representing different shades of the base color. 
        """
        rgba = to_rgba(base_color)
        if (num_shades == 1):
            return [rgba]

        colors = []
        for i in np.linspace(max_factor, min_factor, num_shades):
            # scale all components of color by factor except alpha
            shaded_color = tuple(
                [i * c if idx < 3 else c for idx, c in enumerate(rgba)])
            colors.append(shaded_color)
        return colors

    # todo move to FE
    # call this function on 2 modes only, on mode where want to use one static color it is not necessary - color will be in default styles or mandatory styles (should be created based on UI)
    @staticmethod
    def assign_dynamic_colors(keys: list[str], existing_styles: FeaturesCategoryStyle, mode: ColorMode,
                              color_or_pallet: str, dis_pallet=False, max_color_count: int = None, colors_used: int = None) -> int:
        """Extend existing_styles with keys that are not in existing_styles and are in keys.

            keys - dict with all keys that are needed in resulting dict as keys
            existing_styles - dict with styles already explicit written for gpxs
            mode - wheter to add colors from PALETTE or one color shades
            color_or_pallet - name of pallet or color to shade use
            max_color_count - number of colors that will be used from continues pallet or shades (for linear assigment)
            colors_used - used number of colors from pallet
        """
        # if not given (different styling for root and folders), calculate how many colors are missing
        if (max_color_count is None):
            max_color_count = Utils.count_missing_values(
                keys, existing_styles, StyleKey.COLOR)
        if (colors_used is None):
            colors_used = 0

        if (mode == ColorMode.PALETTE):
            try:
                # pallet = color_or_pallet
                cmap = plt.get_cmap(color_or_pallet)
            except ValueError:
                warnings.warn(
                    f"Palette '{color_or_pallet}' does not exist. Using 'tab10' instead.")
                cmap = plt.get_cmap("tab10")
                dis_pallet = True

            if (dis_pallet):
                for key in keys:
                    if key not in existing_styles:
                        existing_styles[key] = {
                            StyleKey.COLOR: cmap(colors_used)}
                        colors_used += 1
                    elif (StyleKey.COLOR not in existing_styles[key].keys()):
                        existing_styles[key].update(
                            {StyleKey.COLOR: cmap(colors_used)})
                        colors_used += 1
            # continues
            else:
                norm = plt.Normalize(vmin=0,
                                     vmax=max_color_count)
                for key in keys:
                    if key not in existing_styles:
                        existing_styles[key] = {
                            StyleKey.COLOR: cmap(norm(colors_used))}
                        colors_used += 1
                    elif (StyleKey.COLOR not in existing_styles[key].keys()):
                        existing_styles[key].update(
                            {StyleKey.COLOR: cmap(norm(colors_used))})
                        colors_used += 1
                        
        elif (mode == ColorMode.SHADE):
            # color = color_or_pallet
            colors = StyleAssigner.generate_shades_of_color(
                color_or_pallet, max_color_count, 0.2, 0.8) #? maybe add min and max factor as parameter
            for key in keys:
                if key not in existing_styles:
                    existing_styles[key] = {
                        StyleKey.COLOR: colors[colors_used]}
                    colors_used += 1
                elif (StyleKey.COLOR not in existing_styles[key].keys()):
                    existing_styles[key].update(
                        {StyleKey.COLOR: colors[colors_used]})
                    colors_used += 1
        else:
            warnings.warn(
                "assign_dynamic_colors: mode is not supported, no colors were assigned")
            return 0

        return colors_used
