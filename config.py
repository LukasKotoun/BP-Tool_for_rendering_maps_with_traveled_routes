#------------cons--------------

WAYS_RATIO_TO_MAP_SIZE = 0.1
GENERAL_DEFAULT_STYLES = {'color':'#EDEDE0', 'zindex':0}

city_name = "Brno, Czech Republic"


#------------filters--------------

way_filters = {
    'waterway': True,
    # 'highway': ['highway','trunk','primary','secondary'],
    'highway':True
}

area_filters = {
    # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium','swimming_pool', 'sports_centre'],
    'water': True,
    # 'water': ['river','lake','reservoir'],
}


#------------styles--------------


landuse_styles = {
    'farmland': {'color': '#EDEDE0', 'zindex': None},
    'forest': {'color': '#9FC98D', 'zindex': None},
    'meadow': {'color': '#B7DEA6', 'zindex': None},
    'grass': {'color': '#B7DEA6', 'zindex': None},
    'residential': {'color': '#E2D4AF', 'zindex': None},
    'industrial': {'color': '#DFDBD1', 'zindex': None},
    'basin': {'color': '#8FB8DB', 'zindex': 1},
    'salt_pond': {'color': '#8FB8DB', 'zindex': 1},
}

leisure_styles = {
    'swimming_pool': {'color': '#8FB8DB', 'zindex': 2},  
    'golf_curse': {'color': '#DCE9B9', 'zindex': 1},    
    'playground': {'color': '#DCE9B9', 'zindex': 1},  
    'pitch': {'color': '#DCE9B9', 'zindex': 2},  
    'sports_centre': {'color': '#9FC98D', 'zindex': 1},  
}
	
highway_styles = {
    'highway': {'color': '#FDC364', 'zindex': 7, 'linewidth': 15}, 
    'trunk': {'color': '#FDC364', 'zindex': 6, 'linewidth': 12},
    'primary': {'color': '#FDC364', 'zindex': 5, 'linewidth': 9},
    'secondary': {'color': '#F7ED60', 'zindex': 4, 'linewidth': 7},
    'tertiary': {'color': '#FFFFFF', 'zindex': 3, 'linewidth': 6},
    'unclassified': {'color': '#FFFFFF', 'zindex': None},
    'road': {'color': '#DAD6D2', 'zindex': None},
    'footway': {'color': 'brown', 'zindex': None},
    'steps': {'color': 'purple', 'zindex': None},
    'path': {'color': 'red', 'zindex': None},
    'residential': {'color': 'blue', 'zindex': None}
}

building_styles = {
    'house': {'color': 'grey', 'zindex': 1},
}


# Define attribute mapping with default values

CATEGORIES_STYLES = {
    'building': (building_styles, {'color': '#B7DEA6', 'zindex': 1, 'linewidth': 4}),
    'water': ({}, {'color': '#8FB8DB', 'zindex': 1, 'linewidth': 4}),
    'waterway': ({}, {'color': '#8FB8DB', 'zindex': 1, 'linewidth': 4}),
    'leisure': (leisure_styles, {'color': '#EDEDE0', 'zindex': 0, 'linewidth': 4}),
    'natural': (landuse_styles, {'color': '#B7DEA6', 'zindex': 0, 'linewidth': 4}),
    'landuse': (landuse_styles, {'color': '#EDEDE0', 'zindex': 0, 'linewidth': 4}),
    'highway': (highway_styles, {'color': '#FFFFFF', 'zindex': 2, 'linewidth': 4})
}


# road_width_mapping = {
#     'primary': 1.5,    # Primary roads
#     'secondary': 1.3,  # Secondary roads
#     'tertiary': 0.7,   # Tertiary roads
#     'residential': 0.5, # Residential roads
#     'service': 0.3     # Smallest for service roads
# }

