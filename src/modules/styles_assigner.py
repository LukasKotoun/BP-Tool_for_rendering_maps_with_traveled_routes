import warnings

import pandas as pd
from geopandas import GeoDataFrame

from common.map_enums import StyleKey
from common.custom_types import  CategoriesStyles, WantedCategories, ItemStyles, CategoryStyle

class StyleAssigner:
    def __init__(self, categories_styles: CategoriesStyles,
                 general_default_styles: dict[StyleKey, str | int | float]):  
        self.categories_styles = categories_styles
        self.general_default_styles = general_default_styles
    
    def _get_styles_for_map_element(self, map_feature: pd.DataFrame, available_styles: CategoriesStyles,
                              wanted_feature_styles: list[str]) -> ItemStyles:
        """Find and return styles for concrete map element.

        Args:
            map_feature (pd.DataFrame): Element to find styles for
            available_styles (CategoriesStyles): Dict where to find styles for that element - all finded styles will be assigned 
            wanted_feature_styles (list[str]): Used only in combination with general styles if map element category is not found in available_styles

        Returns:
            ItemStyles: Styles assigned to given map element
        """
        assigned_styles: ItemStyles = {} 
        # find in what features category is osm element
        for features_category, (features_category_map, features_category_default_styles) in available_styles.items():
            
            # osm data element is in this features category
            if features_category in map_feature and pd.notna(map_feature[features_category]):
                # get styles for concrete feature in this category of features or get default styles for this category of features
                features_category_styles = features_category_map.get(map_feature[features_category], features_category_default_styles) 
                
                # iterate through all available styles for this features category (will be already filtered to contains only wanted)
                for style_key, default_style in features_category_default_styles.items():
                    feature_style = features_category_styles.get(style_key)
                    # assign style of concrete feature or default if is not specified for this feature
                    assigned_styles[style_key] = feature_style if feature_style is not None else default_style 
                    
                # map_feature category was found (map_feature can be in one category only) and styles are assigned 
                return assigned_styles
        
        warnings.warn("_get_styles_for_map_element: osm data element is not in any features category avilable in avilable_styles")
        # osm data element is not in any features category avilable in avilable_styles (should not occur) 
        # if that occure assign styles from global styles and assign only wanted 
        return {style_key: self.general_default_styles[style_key] for style_key in wanted_feature_styles  
                                                            if style_key in features_category_default_styles}
    
    
    def _filter_category_styles(self, wanted_features_categories: WantedCategories,
                                wanted_features_styles: list[StyleKey]) -> CategoriesStyles:
        """Create features categories styles, but containng wanted features categories with wanted styles. 
        Reducing size of features categories styles to only currenlty wanted.

        Args:
            wanted_features_categories (WantedCategories): Currently wanted features categories (e.g. landuse: [forest, grass]) to be included in final styles
            wanted_features_styles (list[StyleKey]): Currently wanted styles (e.g. color) to be included in final styles

        Returns:
            CategoriesStyles: Dict with only wanted features categories with wanted styles. 
        """
        filtered_features_categories_styles: CategoriesStyles = {}
        # iterate through all styles 
        for features_category, (features_category_style, features_category_default_styles) in self.categories_styles.items(): 
            if features_category in wanted_features_categories: 
                # get wanted map features that i want to include style for
                wanted_features: list[str] = wanted_features_categories[features_category]
                if wanted_features: 
                    # get style for only some features in features category (list is not empty, only some from this category will be plotted)
                    # (if concrete style for some feateru is not defined it will no be added (it only reduce not add))
                    
                    #filter wanted styles (e.g. color) only for wanted features (already filtered from outer loop)
                    features_category_styles_filtered: CategoryStyle = {      
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
                    features_category_styles_filtered: CategoryStyle = {      
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
        gdf_available_styles = self._filter_category_styles(wanted_features_categories, wanted_styles)
        if(gdf_available_styles):
            # get styles to every map feature in gdf
            styles_columns = gdf.apply(lambda map_feature: self._get_styles_for_map_element(map_feature, gdf_available_styles, wanted_styles), axis=1).tolist()
            styled_gdf = gdf.join(pd.DataFrame(styles_columns))     
            # convert object columns to pandas category - for memory optimalization
            for style_column in wanted_styles:
                if(style_column in styled_gdf and styled_gdf[style_column].dtype == object):
                    styled_gdf[style_column] = styled_gdf[style_column].astype("category")            
            return styled_gdf
        warnings.warn("assign_styles_to_gdf: avilable styles are empty")
        return gdf