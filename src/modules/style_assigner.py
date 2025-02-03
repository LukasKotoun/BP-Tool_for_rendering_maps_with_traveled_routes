import warnings
from common.common_helpers import time_measurement

import pandas as pd
import numpy as np
from geopandas import GeoDataFrame
from modules.gdf_utils import GdfUtils
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

from modules.utils import Utils
from common.map_enums import StyleKey, ColorMode
from common.custom_types import FeaturesCategoriesStyles, WantedCategories, FeatureStyles, FeaturesCategoryStyle, ElementStyles

# element or static or map element and gpx...?


class StyleAssigner:
    def __init__(self, categories_styles: FeaturesCategoriesStyles,
                 general_default_styles: FeatureStyles, mandatory_styles: FeatureStyles):
        self.categories_styles = categories_styles
        self.general_default_styles = general_default_styles
        self.mandatory_styles = mandatory_styles

    # def _get_styles_for_map_feature(self, map_feature: pd.DataFrame, available_styles: FeaturesCategoriesStyles
    #                                 ) -> FeatureStyles:
    #     """Find and return styles for concrete map feature. Assign concrete styles for feature,
    #     than add mandatory for feature category and then mandatory for all features.

    #     Args:
    #         map_feature (pd.DataFrame): Element to find styles for
    #         available_styles (FeaturesCategoriesStyles): dict with default styles for category of features. All finded styles will be assigned 

    #     Returns:
    #         FeatureStyles: Styles assigned to given map element
    #     """
    #     assigned_styles: FeatureStyles = {}
    #     # find in what features category is osm feature
    #     for features_category, (features_category_map, features_category_default_styles) in available_styles.items():

    #         # osm data feature is in this features category
    #         if features_category in map_feature and pd.notna(map_feature[features_category]):
    #             # get styles for concrete feature in this category of features or get default styles for this category of features
    #             features_category_styles = features_category_map.get(
    #                 map_feature[features_category], features_category_default_styles)
    #             # assignd general styles, add new and overwrite by features_category_default_styles and again get new and overwrite by features_category_styles
    #             assigned_styles = {**self.mandatory_styles, **
    #                                features_category_default_styles, **features_category_styles}
    #             return assigned_styles
    #     warnings.warn(
    #         "_get_styles_for_map_feature: some map FeaturesCategory does not have any style in FeaturesCategoriesStyles")
    #     # osm data feature is not in any features category avilable in avilable_styles
    #     # todo check mandatory vs general - usage
    #     return self.general_default_styles

    # # def __replace_none_with_na(self, data): # and empty string?
    # #     """
    # #     Recursively replaces all None values in a nested structure with pd.NA.
    # #     Supports nested dictionaries, lists, and tuples.
    # #     """
    # #     if isinstance(data, dict):
    # #         return {key: self.__replace_none_with_na(value) for key, value in data.items()}
    # #     elif isinstance(data, list):
    # #         return [ self.__replace_none_with_na(item) for item in data]
    # #     elif isinstance(data, tuple):
    # #         return tuple( self.__replace_none_with_na(item) for item in data)
    # #     elif data is None:
    # #         return pd.NA
    # #     else:
    # #         return data

    # def _filter_category_styles(self, wanted_features_categories: WantedCategories) -> tuple[FeaturesCategoriesStyles, list[StyleKey]]:
    #     """Create features categories styles, but containng wanted features categories with wanted styles. 
    #     Reducing size of features categories styles to only currently wanted categories and its features.

    #     Args:
    #         wanted_features_categories (WantedCategories): Currently wanted features categories (e.g. landuse: [forest, grass]) to be included in final styles

    #     Returns:
    #         FeaturesCategoriesStyles: Dict with only wanted features categories with wanted styles. 
    #     """
    #     filtered_features_categories_styles: FeaturesCategoriesStyles = {}
    #     used_styles: StyleKey = set()
    #     # iterate through all styles
    #     for features_category, (features_category_style, features_category_default_styles) in self.categories_styles.items():
    #         if features_category in wanted_features_categories:
    #             # get wanted map features that i want to include style for
    #             wanted_features: set[str] = wanted_features_categories[features_category]
    #             if wanted_features:
    #                 # get style for only some features in features category (list is not empty, only some from this category will be plotted)
    #                 # (if concrete style for some feateru is not defined it will no be added (it only reduce not add))

    #                 features_category_styles_filtered: FeaturesCategoryStyle = {
    #                     feature: feature_styles
    #                     for feature, feature_styles in features_category_style.items()
    #                     if feature in wanted_features
    #                 }
    #             else:
    #                 # get style for all features in category #(list is empty, all features from this category will be plotted)
    #                 # (if concrete style for some feateru is not defined it will no be added (it only reduce not add))

    #                 features_category_styles_filtered: FeaturesCategoryStyle = features_category_style
    #             # store filtered features category styles with features category default styles
    #             used_styles.update(features_category_default_styles.keys())
    #             filtered_features_categories_styles[features_category] = (features_category_styles_filtered,
    #                                                                       features_category_default_styles)
    #     return filtered_features_categories_styles, list(used_styles)

    # @time_measurement("styles assign")
    # def assign_styles(self, gdf: GeoDataFrame, wanted_features_categories: WantedCategories,
    #                   dont_categorize: list[str] = []) -> GeoDataFrame:
    #     """Will assign wanted_styles to all features (rows) in given GeoDataFrame that are in WantedCategories. 
    #     If they are not in wanted categories it will assign from general styles.

    #     Args:
    #         gdf (GeoDataFrame): Features to assign styles to
    #         wanted_features_categories (WantedCategories): Wanted categories to be styled using styles for that concrete category (else general styles)
    #         wanted_styles (list[StyleKey]): Styles to by assigned to features 

    #     Returns:
    #         GeoDataFrame: Gdf with assigned styles to features
    #     """

    #     if (gdf.empty):
    #         return gdf
    #     # get only useful styles    (all styles inside will be assigned), it makes assigning quicker
    #     available_styles, new_styles = self._filter_category_styles(
    #         wanted_features_categories)
    #     if (not available_styles):
    #         warnings.warn("assign_styles_to_gdf: avilable styles are empty")
    #     # create list of all used stylekeys in aviailable styles

    #     # get styles to every map feature in gdf
    #     styles_columns = gdf.apply(lambda map_feature: self._get_styles_for_map_feature(
    #         map_feature, available_styles), axis=1).tolist()
    #     styles_columns_df = pd.DataFrame(styles_columns)
    #     # # # fill missing values
    #     # # # for style_key in wanted_styles:
    #     # # #     if style_key not in styles_columns_df:
    #     # # #         styles_columns_df[style_key] = self.general_default_styles[style_key]
    #     # # #     else:
    #     # # #         styles_columns_df[style_key] = styles_columns_df[style_key].fillna(self.general_default_styles[style_key])

    #     # drop columns that will be assigned twice - assign new
    #     duplicated_columns = [
    #         col for col in new_styles if col in gdf.columns]
    #     if (duplicated_columns):
    #         gdf = gdf.drop(columns=duplicated_columns)
    #         warnings.warn(f"Reassigning once assigned styles (the new one were used): {
    #                       ', '.join([str(col) for col in duplicated_columns])}")

    #     styled_gdf = gdf.join(styles_columns_df)

    #     categorical_list = []
    #     # convert object columns to pandas category - for memory optimalization
    #     for style_column in new_styles:
    #         if (style_column in styled_gdf and style_column not in dont_categorize and styled_gdf[style_column].dtype == object):
    #             categorical_list.append(style_column)
    #     GdfUtils.change_columns_to_categorical(styled_gdf, categorical_list)

    #     return styled_gdf

    
    @staticmethod
    @time_measurement("styles assign")
    def assign_styles(gdf: GeoDataFrame, conditons_styles: ElementStyles, dont_categorize: list[str] = [])  -> None:
        new_styles: StyleKey = set()
        # assign styles from most general to most specific by writing to columns in styles
        for conditons, styles in reversed(conditons_styles): # assing from least specific to most specific
            filtered_rows: pd.Series = GdfUtils.create_rows_filter(gdf, conditons)
            for key, value in styles.items():
                if isinstance(value, tuple): 
                    # write tuple to one column cell
                    gdf_tmp = GdfUtils.create_empty_gdf()
                    gdf_tmp['tmp'] = [value]*filtered_rows.sum()
                    gdf.loc[filtered_rows, key] = gdf_tmp['tmp'].values
                else: 
                    gdf.loc[filtered_rows, key] = value
            new_styles.update(styles.keys())
            
            ## gdf.loc[filterd_rows, list(styles.keys())] = list(styles.values())
            
        # convert object columns to pandas category
        categorical_list = []
        for style_column in new_styles:
            if (style_column in gdf and style_column not in dont_categorize and gdf[style_column].dtype == object):
                categorical_list.append(style_column)
        GdfUtils.change_columns_to_categorical(gdf, categorical_list)

    
    @staticmethod
    def create_styles_from_dynamic():
        pass
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
