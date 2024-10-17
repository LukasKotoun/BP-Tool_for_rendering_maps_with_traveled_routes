from enum import Enum
from typing import Tuple


#-----------------Enums--------------

class StyleKey(Enum):
    COLOR = 'color'
    ZINDEX = 'zindex'
    LINEWIDTH = 'linewidth'
    BGCOLOR = 'bg_color'
    LINESTYLE = 'linestyle'

class WorldSides(Enum):
    WEST = 'west'
    EAST = 'east'
    NORTH = 'north'
    SOUTH = 'south'
    
# CUSTOM_PAPER_SIZE = (None,100)



class PaperSize(Enum):
    A0 = (841, 1189)
    A1 = (594, 841)
    A2 = (420, 594)
    A3 = (297, 420)
    A4 = (210, 297)
    A5 = (148, 210)
    A6 = (105, 148)
    A7 = (74, 105)
    A8 = (52, 74)
        
    @property
    def dimensions(self) -> Tuple[float, float]:
        return self.value  # Returns the dimensions (width, height)
    
class MapOrientation(Enum):
    AUTOMATIC = 1
    LANDSCAPE = 2
    PORTRAIT = 3

#------------cons--------------

WAYS_RATIO_TO_MAP_SIZE = 0.007
#there need to be every mentioned style
MM_TO_INCH = 25.4
GENERAL_DEFAULT_STYLES = {StyleKey.COLOR:'#EDEDE0',  StyleKey.ZINDEX :0, StyleKey.LINEWIDTH:0 , StyleKey.BGCOLOR: '#5d5d5d', StyleKey.LINESTYLE:'-'}
EPSG_DEGREE_NUMBER = 4326 # world
EPSG_METERS_NUMBER = 5514 # cz and sk - 5514, world 3857, europe 25833 

#--------



OSM_FILE_EXTENSION = '.osm.pbf'
OSM_FILE_NAME = 'olomkraj'
OSM_WANT_EXTRACT_AREA = False
OSM_OUTPUT_FILE_NAME = None # set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None


OUTPUT_PDF_NAME = 'olomkraj'

AREA  = "Olomoucký kraj, Czech Republic"
# PAPER_DIMENSIONS = PaperSize.A4.dimensions
PAPER_DIMENSIONS = (1200, None) # set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
# PAPER_DIMENSIONS = (1500, None)
GIVEN_SMALLER_PAPER_DIMENSION = True # what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)

# set how will resulted paper be oriented
# can be set to AUTOMATIC (Recommended), LANDSCAPE, PORTRAIT
WANTED_ORIENTATION = MapOrientation.AUTOMATIC


# NOTE: must have same settings as the resulting one when generating for large format printing
WANT_PREVIEW = False
PREVIEW_AREA = "Vysočina, Czech Republic" # area that you are previewing (the bigger one) 

# PREVIEW_PAPER_DIMENSIONS= PaperSize.A4.dimensions # real paper size (bigger one)
PREVIEW_PAPER_DIMENSIONS = (1500, None) # or set own #if one is left none if will be automaticaly calculated by area size

PREVIEW_GIVEN_SMALLER_PAPER_DIMENSION = True # what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)
# set how will resulted paper be oriented
# can be set to AUTOMATIC (Recommended), LANDSCAPE, PORTRAIT

PREVIEW_WANTED_ORIENTATION = MapOrientation.AUTOMATIC
#------------filters--------------


wanted_ways = {
    'waterway': [],
    # 'highway': ['motorway', 'trunk','primary', 'secondary'],
    'highway': [ 'motorway', 'trunk','primary', 'secondary','tertiary','unclassified', 'residential','path', 'footway' ],
    # 'highway':[],
    'railway': ['rail']
}

#todo edit for all or for concrete way filter (like rails, railway tram....)
unwanted_ways_tags ={
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    'railway': {
        'service':['yard'],
        'tunnel': ['building_passage'],
    }
}


wanted_areas = {
    # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium','swimming_pool', 'sports_centre'],
    #todo nature reserve to boundaries? 
    # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
    'water': [],
    # 'water': ['river','lake','reservoir'],
}

unwanted_areas_tags ={
    
}

#------------styles--------------

landuse_styles = {
    'farmland': {StyleKey.COLOR: '#EDEDE0'},
    'forest': {StyleKey.COLOR: '#9FC98D'},
    'meadow': {StyleKey.COLOR: '#B7DEA6'},
    'grass': {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1},
    'residential': {StyleKey.COLOR: '#E2D4AF'},
    'industrial': {StyleKey.COLOR: '#DFDBD1'},
    'basin': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1},
    'salt_pond': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1},
}

leisure_styles = {
    'swimming_pool': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 2},  
    'golf_curse': {StyleKey.COLOR: '#DCE9B9', StyleKey.ZINDEX: 1},    
    'playground': {StyleKey.COLOR: '#DCE9B9', StyleKey.ZINDEX: 1},  
    'pitch': {StyleKey.COLOR: '#DCE9B9', StyleKey.ZINDEX: 2},  
    'sports_centre': {StyleKey.COLOR: '#9FC98D', StyleKey.ZINDEX: 1},  
}
	
highway_styles = {
   'motorway': {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.LINEWIDTH: 16}, 
    'trunk': {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6, StyleKey.LINEWIDTH: 13},
    'primary': {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5, StyleKey.LINEWIDTH: 11},
    'secondary': {StyleKey.COLOR: '#F7ED60', StyleKey.ZINDEX: 4, StyleKey.LINEWIDTH: 10},
    'tertiary': {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.LINEWIDTH: 8},
    'unclassified': {StyleKey.COLOR: '#FFFFFF'},
    'road': {StyleKey.COLOR: '#FFFFFF'},
    'footway': {StyleKey.COLOR: '#8f8364'},
    'steps': {StyleKey.COLOR: '#8f8364'},
    'path': {StyleKey.COLOR: '#8f8364'},
    'residential': {StyleKey.COLOR: '#8f8364'}
    # 'footway': {StyleKey.COLOR: 'red'},
    # 'steps': {StyleKey.COLOR: 'blue'},
    # 'path': {StyleKey.COLOR: 'red'},
    # 'residential': {StyleKey.COLOR: 'brown'}
}
railway_styles = {
    'rail': {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 5, StyleKey.BGCOLOR: '#5d5d5d'},
    'tram': {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 2},
    'tram_stop': {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 2},
}



building_styles = {
    'house': {StyleKey.COLOR: 'grey', StyleKey.ZINDEX: 1},
}


# Define attribute mapping with default values

CATEGORIES_STYLES = {
    'building': (building_styles, {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4}),
    'water': ({}, {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4}),
    'waterway': ({}, {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4}),
    'leisure': (leisure_styles, {StyleKey.COLOR: '#EDEDE0', StyleKey.ZINDEX: 0, StyleKey.LINEWIDTH: 4}),
    'natural': (landuse_styles, {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 0, StyleKey.LINEWIDTH: 4}),
    'landuse': (landuse_styles, {StyleKey.COLOR: '#EDEDE0', StyleKey.ZINDEX: 0, StyleKey.LINEWIDTH: 4}),
    'highway': (highway_styles, {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 4}),
    'railway': (railway_styles, {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 4, StyleKey.BGCOLOR: '#5d5d5d'}),
}