from enum import Enum

#------------cons--------------

WAYS_RATIO_TO_MAP_SIZE = 0.1
GENERAL_DEFAULT_STYLES = {'color':'#EDEDE0', 'zindex':0, 'linewidth':0 , 'bg_color': '#5d5d5d'}

city_name = "Brno, Czech Republic"


#------------filters--------------

way_filters = {
    'waterway': True,
    # 'highway': ['highway','trunk','primary','secondary'],
    'highway':True,
    'railway': ['rail','tram']
}

way_filters_dont_want ={
    'service':['spur']
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
    'grass': {'color': '#B7DEA6', 'zindex': 1},
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
    'road': {'color': '#FFFFFF', 'zindex': None},
    'footway': {'color': '#8f8364', 'zindex': None},
    'steps': {'color': '#8f8364', 'zindex': None},
    'path': {'color': '#8f8364', 'zindex': None},
    'residential': {'color': '#8f8364', 'zindex': None}
}
railway_styles = {
    'rail': {'color': '#FFFFFF', 'zindex': 1, 'linewidth': 4, 'bg_color': '#5d5d5d'},
    'tram': {'color': '#404040', 'zindex': 1, 'linewidth': 1},
    'tram_stop': {'color': '#404040', 'zindex': 1, 'linewidth': 1},
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
    'highway': (highway_styles, {'color': '#FFFFFF', 'zindex': 2, 'linewidth': 4}),
    'railway': (railway_styles, {'color': '#FFFFFF', 'zindex': 2, 'linewidth': 4, 'bg_color': '#5d5d5d'}),
}

MM_TO_INCH = 25.4
PAPER_SIZES ={
    'A0': (841, 1189),
    'A1': (594, 841),
    'A2': (420, 594),
    'A3': (297, 420),
    'A4': (210, 297),
    'A5': (148, 210),
    'A6': (105, 148)
}

class MapOrientation(Enum):
    AUTOMATIC = 1
    LANDSCAPE = 2
    PORTRAIT = 3