import warnings

import pandas as pd
from geopandas import GeoDataFrame
from modules.gdf_utils import GdfUtils

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.colors import to_rgba

from modules.utils import Utils
from common.map_enums import Style, ColorMode
from common.custom_types import FeaturesCategoriesStyles, WantedCategories, FeatureStyles, FeaturesCategoryStyle, ElementStyles

# element or static or map element and gpx...?

# todo to styleManager
class StyleAssigner:
    def __init__(self):
        pass
    
    @staticmethod
    def convert_from_dynamic(dynamic_styles, zoom_level) -> ElementStyles:
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
            if(not isinstance(zoom_styles, dict)):
                warnings.warn(f"zoom_styles ({zoom_styles})is not dict but {type(zoom_styles)}")
                continue
            for zoom_range, zoom_style_values in zoom_styles.items():
                if (check_range(zoom_range, zoom_level)):
                    styles_filter = {**zoom_style_values, **styles_filter}
            styles = {**styles_default, **styles_filter}
            normal_styles.append((filter, styles))
        return normal_styles

    
    @staticmethod
    def assign_styles(gdf: GeoDataFrame, conditons_styles: ElementStyles, dont_categorize: list[str] = [])  -> None:
        if(gdf.empty):
            return
        new_styles: Style = set()
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
    @staticmethod
    def scale_styles(all_styles: ElementStyles, styles_to_scale: list[str], map_scaling_factor: float):
        styles_to_scale = set(styles_to_scale)
        for filter, styles_dict in all_styles:
            for key in styles_dict.keys() & styles_to_scale:
                styles_dict[key] *= map_scaling_factor
