import pandas as pd

class StyleAssigner:
    def __init__(self, gdf_utils , categories_styles, general_default_styles):  
        self.gdf_utils = gdf_utils
        self.categories_styles = categories_styles
        self.general_default_styles = general_default_styles
    
    def _assign_styles_to_row(self, row, available_styles, wanted_styles):
        assigned_styles = {}
        for category_name, (category_map, category_default_styles) in available_styles.items():
            if category_name in row and pd.notna(row[category_name]):
                category_styles = category_map.get(row[category_name], category_default_styles) #retrieve record for a specific key (e.g. landues) and value (e.g. forest) combination in the map or retrieve the default value for that key.
                for style_key, default_style in category_default_styles.items(): # select individual values from the category styles or use default values if there are none individual in the record
                    category_style = category_styles.get(style_key)
                    assigned_styles[style_key] = category_style if category_style is not None else default_style 
                # one category was found - row can be in one category only 
                return assigned_styles
        # if category_name is not in row or nan in row and all posible categories was tryed return general styles but wanted only   
        return {style_key: self.general_default_styles[style_key] for style_key in wanted_styles  
                                                            if style_key in category_default_styles}
    
    def _filter_category_styles(self, wanted_categories,wanted_styles):
        filtered_categories_styles = {}
        for category_name, (category_map, category_default_styles) in self.categories_styles.items():
            if category_name in wanted_categories: #check if category can be in gdf
                category_filter = wanted_categories[category_name]
                if category_filter: #get style for only some items in category
                    filtered_category_styles = {      
                        category_item: {style_key: item_styles[style_key] for style_key in wanted_styles if style_key in item_styles} #filter only wanted styles for item in category (e.g. color)
                        for category_item, item_styles in category_map.items()
                        if category_item in category_filter     #filter wanted items
                    }
                else:  #get style for all items in category
                    filtered_category_styles = {
                        category_item: {style_key: item_styles[style_key] for style_key in wanted_styles if style_key in item_styles} #filter only wanted styles for item in category (e.g. color)
                        for category_item, item_styles in category_map.items()
                    }
                filtered_categories_styles[category_name] = (filtered_category_styles, 
                                                            {style_key: category_default_styles[style_key] for style_key in wanted_styles 
                                                            if style_key in category_default_styles}) #store filterd category with wanted default styles
        return filtered_categories_styles
    
    def assign_styles_to_gdf(self, gdf, wanted_categories, wanted_styles):
        if(gdf.empty):
            return gdf
        gdf_available_styles = self._filter_category_styles(wanted_categories, wanted_styles)
        if(gdf_available_styles):
            styles_columns = gdf.apply(lambda row: self._assign_styles_to_row(row, gdf_available_styles, wanted_styles), axis=1).tolist()
            return gdf.join(pd.DataFrame(styles_columns))
        print("assign_styles_to_gdf: avilable styles are empty")
        return gdf