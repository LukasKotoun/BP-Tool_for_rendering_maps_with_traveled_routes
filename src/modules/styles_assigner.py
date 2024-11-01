import warnings
from common.common_helpers import time_measurement_decorator

import pandas as pd
from geopandas import GeoDataFrame

from common.map_enums import StyleKey
from common.custom_types import  FeaturesCategoriesStyles, WantedCategories, FeatureStyles, FeaturesCategoryStyle

class StyleAssigner:
    def __init__(self, categories_styles: FeaturesCategoriesStyles,
                 general_default_styles: FeatureStyles, mandatory_styles: FeatureStyles):  
        self.categories_styles = categories_styles
        self.general_default_styles = general_default_styles
        self.mandatory_styles = mandatory_styles

    def _get_styles_for_map_feature(self, map_feature: pd.DataFrame, available_styles: FeaturesCategoriesStyles,
                              wanted_feature_styles: list[StyleKey]) -> FeatureStyles:
        """Find and return styles for concrete map feature. Assign concrete styles for feature,
        than add mandatory for feature category and then mandatory for all features.

        Args:
            map_feature (pd.DataFrame): Element to find styles for
            available_styles (FeaturesCategoriesStyles): dict with default styles for category of features. All finded styles will be assigned 
            wanted_feature_styles (list[str]): Used only in combination with general styles if map element category is not found in available_styles

        Returns:
            FeatureStyles: Styles assigned to given map element
        """
        assigned_styles: FeatureStyles = {} 
        # find in what features category is osm feature
        for features_category, (features_category_map, features_category_default_styles) in available_styles.items():
            
            # osm data feature is in this features category
            if features_category in map_feature and pd.notna(map_feature[features_category]):
                # get styles for concrete feature in this category of features or get default styles for this category of features
                features_category_styles = features_category_map.get(map_feature[features_category], features_category_default_styles)
                #assignd general styles, add new and overwrite by features_category_default_styles and again get new and overwrite by features_category_styles
                assigned_styles = {**self.mandatory_styles, **features_category_default_styles, **features_category_styles}
                return assigned_styles
        warnings.warn("_get_styles_for_map_feature: some map FeaturesCategory does not have any style in some FeaturesCategoriesStyles")
        # osm data feature is not in any features category avilable in avilable_styles
        # if that occure assign styles from global styles and assign only wanted 
        return {style_key: self.general_default_styles[style_key] for style_key in wanted_feature_styles}
    
    
    def _filter_category_styles(self, wanted_features_categories: WantedCategories,
                                wanted_features_styles: list[StyleKey]) -> FeaturesCategoriesStyles:
        """Create features categories styles, but containng wanted features categories with wanted styles. 
        Reducing size of features categories styles to only currenlty wanted.

        Args:
            wanted_features_categories (WantedCategories): Currently wanted features categories (e.g. landuse: [forest, grass]) to be included in final styles
            wanted_features_styles (list[StyleKey]): Currently wanted styles (e.g. color) to be included in final styles

        Returns:
            FeaturesCategoriesStyles: Dict with only wanted features categories with wanted styles. 
        """
        filtered_features_categories_styles: FeaturesCategoriesStyles = {}
        # iterate through all styles 
        for features_category, (features_category_style, features_category_default_styles) in self.categories_styles.items(): 
            if features_category in wanted_features_categories: 
                # get wanted map features that i want to include style for
                wanted_features: dict[str] = wanted_features_categories[features_category]
                if wanted_features: 
                    # get style for only some features in features category (list is not empty, only some from this category will be plotted)
                    # (if concrete style for some feateru is not defined it will no be added (it only reduce not add))
                    
                    #filter wanted styles (e.g. color) only for wanted features (already filtered from outer loop)
                    features_category_styles_filtered: FeaturesCategoryStyle = {      
                        feature: {style_key: feature_styles[style_key] 
                                  #iterate through only wanted styles
                                  for style_key in wanted_features_styles 
                                    if style_key in feature_styles
                                  } #inner loop 
                        # iterate through only wanted features
                        for feature, feature_styles in features_category_style.items() # outer loop
                            if feature in wanted_features   
                    }
                else:  
                    #get style for all features in features category (list is empty, all features  from this category will be plotted)
                    # (if concrete style for some feateru is not defined it will no be added (it only reduce not add))
                    
                    # filter wanted styles (e.g. color) for all (styled) features
                    features_category_styles_filtered: FeaturesCategoryStyle = {      
                        feature: {style_key: feature_styles[style_key] 
                                  #iterate through only wanted styles
                                    for style_key in wanted_features_styles 
                                        if style_key in feature_styles
                                  } #inner loop 
                        # iterate through all styled features
                        for feature, feature_styles in features_category_style.items() # outer loop
                    }
                   
                #store filtered features category styles with features category default styles
                filtered_features_categories_styles[features_category] = (features_category_styles_filtered,      
                                                            {style_key: features_category_default_styles[style_key] 
                                                                # select only wanted that are avilable in features category default styles
                                                                for style_key in wanted_features_styles 
                                                                    if style_key in features_category_default_styles})
        return filtered_features_categories_styles 

    @time_measurement_decorator("styles assign")
    def assign_styles_to_gdf(self, gdf: GeoDataFrame, wanted_features_categories: WantedCategories,
                            wanted_styles: list[StyleKey]) -> GeoDataFrame:
        """Will assign wanted_styles to all features (rows) in given GeoDataFrame that are in WantedCategories. 
        If they are not in wanted categories it will assign from general styles.

        Args:
            gdf (GeoDataFrame): Features to assign styles to
            wanted_features_categories (WantedCategories): Wanted categories to be styled using styles for that concrete category (else general styles)
            wanted_styles (list[StyleKey]): Styles to by assigned to features 

        Returns:
            GeoDataFrame: Gdf with assigned styles to features
        """
        if(gdf.empty):
            return gdf
        # get only useful styles (all styles inside will be assigned), it makes assigning quicker
        available_styles = self._filter_category_styles(wanted_features_categories, wanted_styles)
        if(not available_styles):
            warnings.warn("assign_styles_to_gdf: avilable styles are empty")

        # get styles to every map feature in gdf
        styles_columns = gdf.apply(lambda map_feature: self._get_styles_for_map_feature(map_feature, available_styles, wanted_styles), axis=1).tolist()
        styles_columns_df = pd.DataFrame(styles_columns)
        # fill missing values 
        # for style_key in wanted_styles:
        #     if style_key not in styles_columns_df:
        #         styles_columns_df[style_key] = self.general_default_styles[style_key]
        #     else:
        #         styles_columns_df[style_key] = styles_columns_df[style_key].fillna(self.general_default_styles[style_key])
        
        #drop columns that will be assigned twice - assign new
        duplicated_columns = [col for col in wanted_styles if col in gdf.columns]
        if (duplicated_columns):
            gdf = gdf.drop(columns=duplicated_columns)
            warnings.warn(f"Reassigning once assigned styles (the new one were used): {', '.join([str(col) for col in duplicated_columns])}")
        
        styled_gdf = gdf.join(styles_columns_df)     

        # convert object columns to pandas category - for memory optimalization
        for style_column in wanted_styles:
            if(style_column in styled_gdf and styled_gdf[style_column].dtype == object):
                styled_gdf[style_column] = styled_gdf[style_column].astype("category")            
        return styled_gdf
