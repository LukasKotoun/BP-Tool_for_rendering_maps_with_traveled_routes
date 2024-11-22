from common.custom_types import *
from common.map_enums import *


# --------------normal map area--------------
# OSM_INPUT_FILE_NAMES: str = ['../osm_files/vys.osm.pbf','../osm_files/jihmor.osm.pbf']
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/vysJihE.osm.pbf'
OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/HV.osm.pbf'
# extract
OSM_WANT_EXTRACT_AREA: bool = False
# set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None
OSM_OUTPUT_FILE_NAME: None | str = '../osm_files/brnoE.osm.pbf'

OUTPUT_PDF_NAME: str = '../pdfs/divočina'
# with fill or false cliping is recomended 0
# padding from page borders NOTE: must have same settings as the resulting one when generating for large format printing
PERCENTAGE_PADDING = 0.5

# AREA: WantedArea = [(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)] #island
# AREA: WantedArea = [(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)] #afrika
AREA: WantedArea = "Česko"
# AREA: WantedArea = ["Vysočina, Česko", "Jihomoravský kraj, Česko"]
# PAPER_DIMENSIONS: PaperSize | tuple[float | None, float | None] = PaperSize.A4.dimensions
# PAPER_DIMENSIONS = (400, None)
# set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
PAPER_DIMENSIONS = (1100, None)
# what side of paper was set (smaller true bigger false) - only if only one side in custom dimension was set to None
GIVEN_SMALLER_PAPER_DIMENSION: bool = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
WANTED_ORIENTATION: MapOrientation = MapOrientation.AUTOMATIC

# FIT_PAPER_SIZE recomended with PERCENTAGE_PADDING 0
EXPAND_AREA_MODE = ExpandArea.NONE
# polygon or country name - custom area must be bigger than normal
CUSTOM_EXPAND_AREA: WantedArea | None = ["Třebíč, Česko"]

# bounds
# COMBINED - one bound around area, SEPARATED - separated bounds around every area in AREA variable
AREA_BOUNDARY = AreaBounds.SEPARATED
EXPAND_AREA_BOUNDS_PLOT = True
AREA_BOUNDARY_LINEWIDTH = 70

# clipping
# if true it will plot only given AREA (recomended) if False it will plot whole osm file with AREA in center
WANT_AREA_CLIPPING = True

# city text
SHOW_CITY_NAMES = True  # in automatic wanted_nodes creation
# The largest urban settlement or settlements within the territory.
CITY_CITY_SIZE_MULTIPLIER = 1
# An important urban centre, between a village and a city in size.
CITY_TOWN_SIZE_MULTIPLIER = 1
# A smaller distinct settlement, smaller than a town with few facilities available with people traveling to nearby towns to access these.
CITY_VILLAGE_SIZE_MULTIPLIER = 1

# peek text ...
# text general
TEXT_WRAP_NAMES_LEN = 15  # len or None if not wrap (15 default)
# if allow is false set threashold (0-1) how much of text must be inside
TEXT_BOUNDS_OVERFLOW_THRESHOLD = 0.97


# --------------------------------------------------------------preview--------------------------------------------------------------
# NOTE: must have same settings as the resulting one when generating for large format printing
WANT_PREVIEW: bool = False
# area for that you are creating smaller preview (bigger than normal area)
OUTER_AREA: WantedArea = "Vysočina, Česko"

OUTER_PAPER_DIMENSIONS = PaperSize.A0.dimensions  # real paper size
# OUTER_PAPER_DIMENSIONS = (300, None) # or set own #if one is left none if will be automaticaly calculated by area size
# what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)
OUTER_GIVEN_SMALLER_PAPER_DIMENSION = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
OUTER_WANTED_ORIENTATION = MapOrientation.AUTOMATIC

# expand
OUTER_EXPAND_AREA_MODE = ExpandArea.FIT_PAPER_SIZE
OUTER_CUSTOM_EXPAND_AREA: WantedArea | None = "Česko"


# todo here automatic wanted objects setup using map and pdf ratio automatic_filters_creating_factor - own class ()


# ------------cons--------------

# world 3857
EPSG_OSM = 4326
EPSG_CALC = 3857  # cz and sk - 5514, , europe 25833
EPSG_DISPLAY = 3857
# todo table with epsg
OBJECT_MULTIPLIER = 1
AREAS_EDGE_WIDTH_MULTIPLIER = 1
WAYS_WIDTH_MULTIPLIER = 1
# --------------filters--------------
# columns that are used for ploting nodes name for city, ele for elevation points
NODES_ADDITIONAL_COLUMNS = ['name']
WAYS_ADDITIONAL_COLUMNS = ['bridge', 'layer']

# wanted_ways: WantedFeatures
wanted_nodes: WantedCategories = {
    # 'place': {'city', 'town', 'village'}
    # 'place': {'town'}
    'place': {'city', 'town'},
    'natural': {'peak'}
}

# UnwantedFeaturesTags
unwanted_nodes_tags: UnwantedTags = {

}

# wanted_ways: WantedFeatures
wanted_ways: WantedCategories = {
    'waterway': set({}),
    # 'highway': ['motorway', 'trunk','primary', 'secondary'],
    'highway': {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'},
    # 'highway':[],
    'railway': {'rail'}
}

# UnwantedFeaturesTags
unwanted_ways_tags: UnwantedTags = {
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    'railway': {
        'service': ['yard'],
        'tunnel': ['building_passage'],
    }
    # {'railway':""}:{'service':['yard'],'tunnel': ['building_passage']}
}

wanted_areas: WantedCategories = {
    # # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
    'landuse': {'forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'},
    'leisure': {'park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
    # # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
    'water': set({}),
    # todo in automatic this should be to turnoff/on
    'boundary': {'national_park'}
    # todo add natural - water
    # 'water': ['river','lake','reservoir'],
}


unwanted_areas_tags: UnwantedTags = {
}

# ------------styles--------------
# there must be all somewhere used styles, if not program can crash
GENERAL_DEFAULT_STYLES: FeatureStyles = {StyleKey.COLOR: '#EDEDE0',  StyleKey.ZINDEX: 0,
                                         StyleKey.LINEWIDTH: 1, StyleKey.LINESTYLE: '-',
                                         StyleKey.ALPHA: 1}

# styles that must be assigned to all area features
AREA_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0
}
# styles that must be assigned to all way features
WAY_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0, StyleKey.LINEWIDTH: 1, StyleKey.LINESTYLE: '-',
    StyleKey.EDGE_WIDTH_RATIO: 0.3, StyleKey.BRIDGE_WIDTH_RATIO: 0, StyleKey.BRIDGE_COLOR: "#FFFFFF",
    StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D"
}
# styles that must be assigned to all node features
NODES_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#000000', StyleKey.FONT_SIZE: 50, StyleKey.EDGE_COLOR: '#FFFFFF',
    StyleKey.OUTLINE_WIDTH: 5,
}
# ? appka asi taky tímhle stylem? pokud bude chtít vlastní nastavení styl (např pro šířku) - (nemá automatické nastavování - to má pouze které výběr....)

# nodes
place_styles: FeaturesCategoryStyle = {  # todo OUTLINE_WIDTH to edge size ratio
    'city': {StyleKey.FONT_SIZE: 2500 * CITY_CITY_SIZE_MULTIPLIER, StyleKey.OUTLINE_WIDTH: 270 * CITY_CITY_SIZE_MULTIPLIER},
    'town': {StyleKey.FONT_SIZE: 1000 * CITY_TOWN_SIZE_MULTIPLIER, StyleKey.OUTLINE_WIDTH: 100 * CITY_TOWN_SIZE_MULTIPLIER},
    'village': {StyleKey.FONT_SIZE: 300 * CITY_VILLAGE_SIZE_MULTIPLIER, StyleKey.OUTLINE_WIDTH: 50 * CITY_VILLAGE_SIZE_MULTIPLIER}
}
natural_styles_nodes: FeaturesCategoryStyle = {
    'peak': {StyleKey.ICON: "^", StyleKey.ICON_COLOR: "#7f3016", StyleKey.ICON_EDGE: 20}
}

NODES_STYLES: FeaturesCategoriesStyles = {
    # color is color of text, EDGE_COLOR is outline color
    'place': (place_styles, {StyleKey.COLOR: '#000000', StyleKey.EDGE_COLOR: '#FFFFFF'}),
    'natural': (natural_styles_nodes, {StyleKey.COLOR: '#000000', StyleKey.EDGE_COLOR: '#FFFFFF', StyleKey.ICON_SIZE: 300, StyleKey.ICON_COLOR: "red"}),
}

# ways
highway_styles: FeaturesCategoryStyle = {
    'motorway': {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.LINEWIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"},
    'trunk': {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6, StyleKey.LINEWIDTH: 26, StyleKey.EDGE_COLOR: "#E19532"},
    'primary': {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5, StyleKey.LINEWIDTH: 22, StyleKey.EDGE_COLOR: "#E19532"},
    'secondary': {StyleKey.COLOR: '#F7ED60', StyleKey.ZINDEX: 4, StyleKey.LINEWIDTH: 20, StyleKey.EDGE_COLOR: "#c1b42a"},
    'tertiary': {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.LINEWIDTH: 16},
    'unclassified': {StyleKey.COLOR: '#FFFFFF'},
    'road': {StyleKey.COLOR: '#FFFFFF'},
    'footway': {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.BRIDGE_COLOR: "#FFFFFF"},
    'steps': {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--"},
    'path': {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.BRIDGE_COLOR: "#FFFFFF"},
    'residential': {StyleKey.COLOR: '#FFFFFF'}
}
railway_styles: FeaturesCategoryStyle = {
    'rail': {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 10,
             StyleKey.BRIDGE_EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_COLOR: "#FFFFFF",
             StyleKey.EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_WIDTH_RATIO: 1.7, StyleKey.LINESTYLE: (2.5, (5, 5))},
    'tram': {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 10, StyleKey.LINEWIDTH: 4, StyleKey.ALPHA: 0.6},
    'tram_stop': {StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 4},
}


WAYS_STYLES: FeaturesCategoriesStyles = {
    'waterway': ({}, {StyleKey.COLOR: '#8FB8DB', StyleKey.LINEWIDTH: 8, StyleKey.ZINDEX: 0}),
    'highway': (highway_styles, {StyleKey.COLOR: '#FFFFFF',
                                 StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D",
                                 StyleKey.ZINDEX: 1, StyleKey.LINEWIDTH: 8, StyleKey.EDGE_COLOR: "#B0A78D"}),
    'railway': (railway_styles, {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.LINEWIDTH: 8}),
}
# areas

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
    'nature_reserve': {StyleKey.COLOR: 'none', StyleKey.EDGE_COLOR: '#97BB72', StyleKey.LINEWIDTH: 80,
                       StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.85, StyleKey.LINESTYLE: '-'}
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
    'boundary': ({}, {StyleKey.EDGE_COLOR: '#97BB72', StyleKey.LINEWIDTH: 80, StyleKey.LINESTYLE: '-', StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.85})
}
