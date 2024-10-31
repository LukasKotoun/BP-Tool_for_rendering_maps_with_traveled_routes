from common.custom_types import *
from common.map_enums import *


#--------------normal map area--------------
OSM_FILE_NAME: str = '../osm_files/jihmor.osm.pbf' #todo need fix - cut bigger area than needed
OSM_WANT_EXTRACT_AREA: bool = False
OSM_OUTPUT_FILE_NAME: None | str = '../osm_files/jihmor.osm.pbf' # set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None
OUTPUT_PDF_NAME: str = '../pdfs/jihmor'
# AREA: str | list[Point] = [(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)] #island
# AREA: str | list[Point] = [(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)] #afrika
AREA: str | list[Point] = "Jihomoravský kraj, Czech Republic"
PAPER_DIMENSIONS: PaperSize | tuple[float | None, float | None] = PaperSize.A4.dimensions
# PAPER_DIMENSIONS = (1200, None) # set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
# PAPER_DIMENSIONS = (400, None)
# only if only one side in custom dimension was set to None
GIVEN_SMALLER_PAPER_DIMENSION: bool = True # what side of paper was set (smaller true bigger false)

# is False it will plot only given AREA (recomended) if True it will plot whole osm file AREA in center 
TURN_OFF_AREA_CLIPPING = False



# padding from page borders
PERCENTAGE_PADDING = 1 # NOTE: must have same settings as the resulting one when generating for large format printing
PLOT_AREA_BOUNDARY = True
AREA_BOUNDARY_LINEWIDTH = 30
# set how will resulted paper be oriented
# can be set to AUTOMATIC (Recommended), LANDSCAPE, PORTRAIT
WANTED_ORIENTATION: MapOrientation = MapOrientation.AUTOMATIC

#--------------------------------------------------------------preview--------------------------------------------------------------
# NOTE: must have same settings as the resulting one when generating for large format printing
WANT_PREVIEW: bool = False


OUTER_AREA = "Czech Republic" # area for that you are creating smaller preview (bigger than normal area) 

# OUTER_PAPER_DIMENSIONS = PaperSize.A4.dimensions # real paper size 
OUTER_PAPER_DIMENSIONS = (1100, None) # or set own #if one is left none if will be automaticaly calculated by area size


OUTER_GIVEN_SMALLER_PAPER_DIMENSION = True # what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)
# set how will resulted paper be oriented
# can be set to AUTOMATIC (Recommended), LANDSCAPE, PORTRAIT

OUTER_WANTED_ORIENTATION = MapOrientation.AUTOMATIC



#todo here automatic wanted objects setup using map and pdf ratio automatic_filters_creating_factor - own class ()


#------------cons--------------

#there need to be every mentioned style
EPSG_DEGREE_NUMBER = 4326 # world
EPSG_METERS_NUMBER = 5514 # cz and sk - 5514, world 3857, europe 25833 
LINEWIDTH_MULTIPLIER = 1
#--------------filters--------------

#wanted_ways: WantedFeatures
wanted_ways: WantedCategories = {
    'waterway': [],
    # 'highway': ['motorway', 'trunk','primary', 'secondary'],
    'highway': [ 'motorway', 'trunk','primary', 'secondary', 'tertiary','unclassified', 'residential','path', 'footway' ],
    # 'highway':[],
    'railway': ['rail']
}
# UnwantedFeaturesTags
unwanted_ways_tags: UnwantedCategories  ={
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    'railway': {
        'service':['yard'],
        'tunnel': ['building_passage'],
    }
}

wanted_areas: WantedCategories = {
    # # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium','swimming_pool', 'sports_centre'],
    # # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
    'water': [],
    'boundary': ['national_park'] # todo in automatic this should be to turnoff/on

    # 'water': ['river','lake','reservoir'],
}

unwanted_areas_tags: UnwantedCategories ={
    
}

#------------styles--------------
# there must be all somewhere used styles, if not program can crash
GENERAL_DEFAULT_STYLES: FeatureStyles = {StyleKey.COLOR: '#EDEDE0',  StyleKey.ZINDEX: 0,
                                         StyleKey.LINEWIDTH: 1, StyleKey.BGCOLOR: '#5D5D5D', StyleKey.LINESTYLE: '-',
                                         StyleKey.EDGE_COLOR: 'none', StyleKey.ALPHA: 1}

#styles that must be assigned to all features
GENERAL_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1
}
	
highway_styles: FeaturesCategoryStyle = {
    'motorway': {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.LINEWIDTH: 32}, 
    'trunk': {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6, StyleKey.LINEWIDTH: 26},
    'primary': {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5, StyleKey.LINEWIDTH: 22},
    'secondary': {StyleKey.COLOR: '#F7ED60', StyleKey.ZINDEX: 4, StyleKey.LINEWIDTH: 20},
    'tertiary': {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.LINEWIDTH: 16},
    'unclassified': {StyleKey.COLOR: '#FFFFFF'},
    'road': {StyleKey.COLOR: '#FFFFFF'},
    'footway': {StyleKey.COLOR: '#8f8364'},
    'steps': {StyleKey.COLOR: '#8f8364'},
    'path': {StyleKey.COLOR: '#8f8364'},
    'residential': {StyleKey.COLOR: '#8f8364'}
}

railway_styles: FeaturesCategoryStyle = {
    'rail': {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 10, StyleKey.BGCOLOR: '#5d5d5d'},
    'tram': {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4},
    'tram_stop': {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4},
}



WAYS_STYLES: FeaturesCategoriesStyles = {
    'waterway': ({}, {StyleKey.COLOR: '#8FB8DB', StyleKey.LINEWIDTH: 8}),
    'highway': (highway_styles, {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 8}),
    'railway': (railway_styles, {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 8, StyleKey.BGCOLOR: '#5d5d5d'}),
}
#areas

landuse_styles: FeaturesCategoryStyle = {
    'farmland': {StyleKey.COLOR: '#EDEDE0'},
    'forest': {StyleKey.COLOR: '#9FC98D'},
    'meadow': {StyleKey.COLOR: '#B7DEA6'},
    'grass': {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1},
    'residential': {StyleKey.COLOR: '#E2D4AF'},
    'industrial': {StyleKey.COLOR: '#DFDBD1'},
    'basin': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1},
    'salt_pond': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1},
}

leisure_styles: FeaturesCategoryStyle = {
    'swimming_pool': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1},  
    'golf_curse': {StyleKey.COLOR: '#DCE9B9'},    
    'playground': {StyleKey.COLOR: '#DCE9B9'},  
    'pitch': {StyleKey.COLOR: '#DCE9B9', StyleKey.ZINDEX: 1},  
    'sports_centre': {StyleKey.COLOR: '#9FC98D'}, 
    'nature_reserve':{StyleKey.COLOR: 'none', StyleKey.EDGE_COLOR: '#97BB72', StyleKey.LINEWIDTH: 80, StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.6}
}

building_styles: FeaturesCategoryStyle = {
    'house': {StyleKey.COLOR: 'grey', StyleKey.ZINDEX: 1},
}

AREAS_STYLES: FeaturesCategoriesStyles = {
    'building': (building_styles, {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1}),
    'leisure': (leisure_styles, {StyleKey.COLOR: '#EDEDE0', StyleKey.LINEWIDTH: 8}),
    'natural': (landuse_styles, {StyleKey.COLOR: '#B7DEA6'}),
    'landuse': (landuse_styles, {StyleKey.COLOR: '#EDEDE0'}),
    'water': ({}, {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    'boundary':({}, {StyleKey.EDGE_COLOR: '#97BB72', StyleKey.LINEWIDTH: 80, StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.6})
}