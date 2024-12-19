from common.custom_types import *
from common.map_enums import *


# --------------------------------------------------------------map area--------------------------------------------------------------
# OSM_INPUT_FILE_NAMES: str = ['../osm_files/vys.osm.pbf','../osm_files/jihmor.osm.pbf']
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/vysJihE.osm.pbf'
OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/trebic.osm.pbf'
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/brno.osm.pbf'
# extract
OSM_WANT_EXTRACT_AREA: bool = False
# set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None
OSM_OUTPUT_FILE_NAME: None | str = '../osm_files/hv.osm.pbf'

OUTPUT_PDF_NAME: str = '../pdfs/divočina2'
# with fill or false cliping is recomended 0
# padding from page borders NOTE: must have same settings as the resulting one when generating for large format printing
PERCENTAGE_PADDING = 0

# AREA: WantedArea = [(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)] #island
# AREA: WantedArea = [(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)] #afrika
# AREA: WantedArea = "Horní vilémovice, Česko"
# AREA: WantedArea = "Česko"
# AREA: WantedArea = [(15.8784350,49.2926919), (15.8852585,49.2925274), (15.8845263, 49.2894905), (15.8769732, 49.2896681)] # zoom 18 (inf - 0.13* 1 
# AREA: WantedArea = [(15.86797,49.30036), (15.89574,49.30038), (15.89571, 49.28466), (15.86797, 49.28444)] # zoom 17 - 0.13-0.1 * 1.5
# AREA: WantedArea = [(15.86797,49.30036), (15.89574,49.30038), (15.89571, 49.28466), (15.86797, 49.28444)] # zoom 16 - 0.1-0.06 * 2
# AREA: WantedArea = [(15.85353,49.30649), (15.90876,49.30660), (15.90846, 49.27511), (15.85331, 49.27455)] # zoom 15 - 
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 14 - 
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 13 - 
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 12 - 
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 11 - 
AREA: WantedArea = [(14.5122769,49.9189048), (16.7593887,49.9184627), (16.7593378, 48.8638096), (14.5141625, 48.8825185)] # zoom 10 - 
# AREA: WantedArea = [(12.9395476,50.8278038), (17.4318749,50.8064127), (17.4281868,48.7534708), (12.9522022, 48.7996803)] # zoom 9 - 
# AREA: WantedArea = [(10.7711036,51.9150971), (19.7678764,51.8786709), (19.7610689, 47.7784321), (10.9928686, 47.9098377)] # zoom 8 - 
# AREA: WantedArea = [(1.978792,55.788072), (30.252955,55.874256),(30.177249, 39.428847), (2.704960, 39.183520) ] # zoom 6 - 


# AREA: WantedArea = [(15.7396182, 49.3111173), (16.0273871, 49.3028839),
#                     (16.0266146, 49.1439064), (15.6712219, 49.1928600)]  # trebic
# AREA: WantedArea = ["Česko", "Německo", "Polsko", "Rakousko", "Slovensko"]
PAPER_DIMENSIONS: PaperSize | tuple[float |
                              None, float | None] = PaperSize.A4.dimensions
# PAPER_DIMENSIONS = (400, None)
# set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
# PAPER_DIMENSIONS = (3000, None)
# what side of paper was set (smaller true bigger false) - only if only one side in custom dimension was set to None
GIVEN_SMALLER_PAPER_DIMENSION: bool = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
WANTED_ORIENTATION: MapOrientation = MapOrientation.AUTOMATIC

# FIT_PAPER_SIZE recomended with PERCENTAGE_PADDING 0
EXPAND_AREA_MODE = ExpandArea.FIT_PAPER_SIZE
# polygon or country name - custom area must be bigger than normal
CUSTOM_EXPAND_AREA: WantedArea | None = [(12.9395476,50.8278038), (17.4318749,50.8064127), (17.4281868,48.7534708), (12.9522022, 48.7996803)]

# bounds
# COMBINED - one bound around area, SEPARATED - separated bounds around every area in AREA variable
AREA_BOUNDARY = AreaBounds.NONE
EXPAND_AREA_BOUNDS_PLOT = False
AREA_BOUNDARY_LINEWIDTH = 70

# clipping
# if true it will plot only given AREA (recomended) if False it will plot whole osm file with AREA in center
WANT_AREA_CLIPPING = True

# --------------------------------------------------------------names settings--------------------------------------------------------------
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

# expand area
OUTER_EXPAND_AREA_MODE = ExpandArea.FIT_PAPER_SIZE
OUTER_CUSTOM_EXPAND_AREA: WantedArea | None = "Česko"

# --------------------------------------------------------------gpx settings--------------------------------------------------------------


GPX_FOLDER: str = './pdfs'
ROOT_FILES_COLOR_MODE: ColorMode = ColorMode.PALETTE
ROOT_FILES_COLOR_OR_PALLET: str = "Set1"
ROOT_FILES_COLOR_DIS_PALLET = True

FOLDER_COLOR_MODE: ColorMode = ColorMode.PALETTE
FOLDER_COLOR_OR_PALLET: str = "Set1"
FOLDER_COLOR_DIS_PALLET = True

# ? none means that it will not be printed (edge or facecolor (not normal color in ways)), "" will be like that is not in that? - or better to be just removed
# -------------------gpx styles by folder-------------------


root_files_styles: FeaturesCategoryStyle = {
    "Grilovačka.gpx": {StyleKey.COLOR: "Red"},
}
folders_styles: FeaturesCategoryStyle = {
    # 'pěšky': {StyleKey.COLOR: "Blue"},
    'Kolo testování': { StyleKey.LINEWIDTH: 200,StyleKey.ALPHA: 0.7},
    # 'Kolo': {StyleKey.COLOR: "Purple"}
}

GPXS_STYLES: FeaturesCategoriesStyles = {
    # for files in root by fileName
    'fileName': (root_files_styles, {StyleKey.COLOR: 'Orange', StyleKey.LINEWIDTH: 200, StyleKey.ALPHA: 0.7,  StyleKey.ZINDEX: 0}),
    # for files in subfolders folder
    'folder': (folders_styles, {StyleKey.COLOR: 'Orange', StyleKey.LINEWIDTH: 200, StyleKey.ALPHA: 0.7,  StyleKey.ZINDEX: 0}),
}

# styles that must be assigned to all gpxs
GPXS_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: 'Green', StyleKey.ALPHA: 1.0, StyleKey.LINESTYLE: "-"
}


# --------------filters for map elements--------------
# columns that are used for ploting nodes name for city, ele for elevation points
NODES_ADDITIONAL_COLUMNS = ['name', 'ele']
WAYS_ADDITIONAL_COLUMNS = ['bridge', 'layer']
# wanted_ways: WantedFeatures
wanted_nodes: WantedCategories = {
    # 'place': {'city', 'town', 'village'}
    # 'place': {'town'}
    # 'place': {'city', 'town', 'village'},
    # 'natural': {'peak'}
}


# todo automatic wanted objects setup using map and pdf ratio automatic_filters_creating_factor - own class ()



unwanted_nodes_tags: UnwantedTags = {

}

wanted_ways: WantedCategories = {
    'waterway': set({}),
    # 'highway': ['motorway', 'trunk','primary', 'secondary'],
    'highway': {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'},
    # 'highway':[],
    'railway': {'rail'}
}

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
    'natural': {'wood', 'water', 'scrub', 'heath'},
    # # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
    'water': set({}),
    # todo in automatic this should be to turnoff/on
    'boundary': {'national_park'},
    'building':{'house','residential'}
    # 'water': ['river','lake','reservoir'],
}
unwanted_areas_tags: UnwantedTags = {
}

# ------------styles--------------
# there must be all somewhere used styles, if not program can crash todo
GENERAL_DEFAULT_STYLES: FeatureStyles = {StyleKey.COLOR: '#EDEDE0',  StyleKey.ZINDEX: 0,
                                         StyleKey.LINEWIDTH: 1, StyleKey.LINESTYLE: '-',
                                         StyleKey.ALPHA: 1, StyleKey.EDGE_COLOR: None}

# ? appka asi taky tímhle stylem? pokud bude chtít vlastní nastavení styl (např pro šířku) - (nemá automatické nastavování - to má pouze které výběr....)

# -------------------nodes-------------------
# styles that must be assigned to all node features
NODES_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#000000', StyleKey.FONT_SIZE: 50, StyleKey.EDGE_COLOR: '#FFFFFF',
    StyleKey.OUTLINE_WIDTH: 5,
}

place_styles: FeaturesCategoryStyle = {  # todo OUTLINE_WIDTH to edge size ratio
    'city': {StyleKey.FONT_SIZE: 2500 * CITY_CITY_SIZE_MULTIPLIER, StyleKey.OUTLINE_WIDTH: 270 * CITY_CITY_SIZE_MULTIPLIER},
    'town': {StyleKey.FONT_SIZE: 1500 * CITY_TOWN_SIZE_MULTIPLIER, StyleKey.OUTLINE_WIDTH: 170 * CITY_TOWN_SIZE_MULTIPLIER},
    'village': {StyleKey.FONT_SIZE: 500 * CITY_VILLAGE_SIZE_MULTIPLIER, StyleKey.OUTLINE_WIDTH: 100 * CITY_VILLAGE_SIZE_MULTIPLIER}
}

natural_styles_nodes: FeaturesCategoryStyle = {
    # ? textOutlineWitdh
    'peak': {StyleKey.ICON: "^", StyleKey.ICON_COLOR: "#7f3016", StyleKey.ICON_EDGE: 20, StyleKey.OUTLINE_WIDTH: 50, StyleKey.FONT_SIZE: 400}
}

NODES_STYLES: FeaturesCategoriesStyles = {
    # color is color of text, EDGE_COLOR is outline color
    'place': (place_styles, {StyleKey.COLOR: '#000000', StyleKey.EDGE_COLOR: '#FFFFFF'}),
    'natural': (natural_styles_nodes, {StyleKey.COLOR: '#000000', StyleKey.EDGE_COLOR: '#FFFFFF', StyleKey.ICON_SIZE: 300**2, StyleKey.ICON_COLOR: "red"}),
}

# -------------------ways-------------------
# styles that must be assigned to all way features
WAY_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0, StyleKey.LINEWIDTH: 1, StyleKey.LINESTYLE: '-',
    StyleKey.EDGE_WIDTH_RATIO: 0.3, StyleKey.BRIDGE_WIDTH_RATIO: 0, StyleKey.BRIDGE_COLOR: "#FFFFFF",
    StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D"
}

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

# -------------------areas-------------------
# styles that must be assigned to all area features
AREA_MANDATORY_STYLES: FeatureStyles = {
    StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0
}
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
    'nature_reserve': {StyleKey.COLOR: None, StyleKey.EDGE_COLOR: '#97BB72', StyleKey.LINEWIDTH: 80,
                       StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.85, StyleKey.LINESTYLE: '-'}
}

building_styles: FeaturesCategoryStyle = {
    'house': {StyleKey.COLOR: 'grey', StyleKey.ZINDEX: 1},
    'residential': {StyleKey.COLOR: 'grey', StyleKey.ZINDEX: 1},
}

natural_styles: FeaturesCategoryStyle = {
    'wood': {StyleKey.COLOR: '#9FC98D'},
    'water': {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1},
    'scrub': {StyleKey.COLOR: '#B7DEA6'},
    'heath': {StyleKey.COLOR: '#B7DEA6'},
}

AREAS_STYLES: FeaturesCategoriesStyles = {
    'building': (building_styles, {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1}),
    'landuse': (landuse_styles, {StyleKey.COLOR: '#EDEDE0'}),
    'water': ({}, {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    'leisure': (leisure_styles, {StyleKey.COLOR: '#EDEDE0', StyleKey.LINEWIDTH: 8}),
    'natural': (natural_styles, {StyleKey.COLOR: '#B7DEA6'}),
    'boundary': ({}, {StyleKey.EDGE_COLOR: '#97BB72', StyleKey.LINEWIDTH: 80, StyleKey.LINESTYLE: '-', StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.85})
}


# ------------constants--------------

# world 3857
EPSG_OSM = 4326
EPSG_CALC = 3857  # cz and sk - 5514, , europe 25833
EPSG_DISPLAY = 3857
# todo table with epsg
OBJECT_MULTIPLIER = 1
AREAS_EDGE_WIDTH_MULTIPLIER = 1
WAYS_WIDTH_MULTIPLIER = 1

# set wanted categories to all gpxs with folder ->
# switching/workaround from styling map elements by category to styling GPX routes by folder
GPX_FOLDERS_CATEGORIES: WantedCategories = {
    'folder': set({}),
}
GPX_ROOT_FILES_CATEGORIES: WantedCategories = {
    'fileName': set({}),
}