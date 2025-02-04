from common.custom_types import *
from common.map_enums import *


# --------------------------------------------------------------map area--------------------------------------------------------------
# OSM_INPUT_FILE_NAMES: str = ['../osm_files/vys.osm.pbf','../osm_files/jihmor.osm.pbf']
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/vysJihE.osm.pbf'
OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/hv.osm.pbf'
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/brno.osm.pbf'
# extract
OSM_WANT_EXTRACT_AREA: bool = False
# set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None
OSM_OUTPUT_FILE_NAME: None | str = '../osm_files/okresice.osm.pbf'

OUTPUT_PDF_NAME: str = '../pdfs/divocina'
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
# AREA: WantedArea = [(15.771692,49.346707), (15.991242, 49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 14 -
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 13 -
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 12 -
# AREA: WantedArea = [(15.771692,49.346707), (15.991242,49.347326), (15.992636, 49.221204), (15.770450, 49.219111)] # zoom 11 -
# AREA: WantedArea = [(14.5122769,49.9189048), (16.7593887,49.9184627), (16.7593378, 48.8638096), (14.5141625, 48.8825185)] # zoom 10 -
# AREA: WantedArea = [(12.9395476,50.8278038), (17.4318749,50.8064127), (17.4281868,48.7534708), (12.9522022, 48.7996803)] # zoom 9 -
# AREA: WantedArea = [(10.7711036,51.9150971), (19.7678764,51.8786709), (19.7610689, 47.7784321), (10.9928686, 47.9098377)] # zoom 8 -
# AREA: WantedArea = [(1.978792,55.788072), (30.252955,55.874256),(30.177249, 39.428847), (2.704960, 39.183520) ] # zoom 6 -
# AREA: WantedArea = [(15.7644462, 49.2855126), (15.9847172, 49.2897762),(15.9796880, 49.1586191), (15.7701351, 49.1588611) ]  - trebic test

# AREA: WantedArea = [[(15.7396182, 49.3111173), (16.0273871, 49.3028839),
#                     (16.0266146, 49.1439064), (15.6712219, 49.1928600)]]  # trebic
# AREA: WantedArea = ["Česko", "Německo", "Polsko", "Rakousko", "Slovensko"]
# AREA: WantedArea = ["Česko", "Německo", "Slovensko"]
# AREA: WantedArea = ["Česko","Vysočina, Česko", "Jihomoravský kraj, Česko"]
AREA: WantedArea = ["Brno, Česko"]
# AREA: WantedArea = ["Horní Vilémovice, Česko"]
# AREA: WantedArea = ["Okřešice, Česko"]
# AREA: WantedArea = ["Třebíč, Česko"]
# AREA: WantedArea = ["Texas, USA"]
# AREA: WantedArea = ["Vysočina, Česko"]

PAPER_DIMENSIONS: PaperSize | tuple[float | None, float | None] = PaperSize.A4.dimensions
# set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
# PAPER_DIMENSIONS = (1000, None)
# PAPER_DIMENSIONS = (200, 200)
# what side of paper was set (smaller true bigger false) - only if only one side in custom dimension was set to None
GIVEN_SMALLER_PAPER_DIMENSION: bool = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
WANTED_ORIENTATION: MapOrientation = MapOrientation.AUTOMATIC

# FIT_PAPER_SIZE recomended with PERCENTAGE_PADDING 0
EXPAND_AREA_MODE = ExpandArea.FIT_PAPER_SIZE
# polygon or country name - custom area must be bigger than normal
CUSTOM_EXPAND_AREA: WantedArea | None = [[(15.7396182, 49.3111173), (16.0273871, 49.3028839),
                    (16.0266146, 49.1439064), (15.6712219, 49.1928600)]]

# bounds
# COMBINED - one bound around area, SEPARATED - separated bounds around every area in AREA variable
AREA_BOUNDARY = AreaBounds.SEPARATED
EXPAND_AREA_BOUNDS_PLOT = False
AREA_BOUNDARY_LINEWIDTH = 30


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
# OUTER_AREA: WantedArea = "Vysočina, Česko"
OUTER_AREA: WantedArea = "Česko"
# OUTER_AREA: WantedArea = [(15.7396182, 49.3111173), (16.0273871, 49.3028839),
#                     (16.0266146, 49.1439064), (15.6712219, 49.1928600)]

OUTER_PAPER_DIMENSIONS = PaperSize.A2.dimensions  # real paper size
# or set own #if one is left none if will be automaticaly calculated by area size
# OUTER_PAPER_DIMENSIONS = (1100, None)
# what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)
OUTER_GIVEN_SMALLER_PAPER_DIMENSION = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
OUTER_WANTED_ORIENTATION = MapOrientation.AUTOMATIC

# expand area
OUTER_EXPAND_AREA_MODE = ExpandArea.FIT_PAPER_SIZE
OUTER_CUSTOM_EXPAND_AREA: WantedArea | None = "Česko"
 
# clipping - if used without preview than replaced by fit_paper_size and default should be true
# if true it will plot only given AREA (recomended) if False it will plot whole osm file with AREA in center
WANT_AREA_CLIPPING = False

# --------------------------------------------------------------gpx settings--------------------------------------------------------------


GPX_FOLDER: str = '../gpx/trebic'
ROOT_FILES_COLOR_MODE: ColorMode = ColorMode.DEFAULT
ROOT_FILES_COLOR_OR_PALLET: str = "Set1"
ROOT_FILES_COLOR_DIS_PALLET = True

FOLDER_COLOR_MODE: ColorMode = ColorMode.DEFAULT
FOLDER_COLOR_OR_PALLET: str = "Set1"
FOLDER_COLOR_DIS_PALLET = True

# ? none means that it will not be printed (edge or facecolor (not normal color in ways)), "" will be like that is not in that? - or better to be just removed
# -------------------gpx styles by folder-------------------

# todo styles for gpx will be assigned on fronted and will be sended to backend in format like
# gpx will be recived from FE a turned to gdf and then styled by backend using sent styles
root_files_styles: ElementStyles = [
    ([('fileName', 'Grilovačka.gpx')], {StyleKey.COLOR: "Red"}),
]

folders_styles: ElementStyles = [
    ([('folder', 'pěšky')], {StyleKey.COLOR: "Blue"}),
    ([('folder', 'Kolo testování')], {StyleKey.WIDTH: 40, StyleKey.ALPHA: 0.7}),
    ([('folder', 'Kolo')], {StyleKey.COLOR: "Purple"}),
]


gpxs_styles_default: ElementStyles = [
    ([('fileName', '')], {StyleKey.COLOR: 'Orange', StyleKey.WIDTH: 40, StyleKey.ALPHA: 0.7,  StyleKey.ZINDEX: 0}),
    ([('folder', '')], {StyleKey.COLOR: 'Orange', StyleKey.WIDTH: 40, StyleKey.ALPHA: 0.7,  StyleKey.ZINDEX: 0}),
]

gpxs_mandatory_styles: ElementStyles = [
    ([], {StyleKey.COLOR: 'Green', StyleKey.ALPHA: 1.0, StyleKey.LINESTYLE: "-"})
]

GPXS_STYLES: ElementStyles =[
    *folders_styles, # folder must be first - folder have only some byt file name have all
    *root_files_styles,
    *gpxs_styles_default,
    *gpxs_mandatory_styles
]

# --------------filters for map elements--------------
# columns that are used for ploting nodes name for city, ele for elevation points
NODES_ADDITIONAL_COLUMNS = ['name', 'ele']
WAYS_ADDITIONAL_COLUMNS = ['bridge', 'layer', 'tunnel']
AREA_ADDITIONAL_COLUMNS = []
# wanted_ways: WantedFeatures
wanted_nodes: WantedCategories = {
    # 'place': {'city'},
    # 'place': {'city', 'town'},
    # 'place': {'city', 'town', 'village'},
    # 'place': {'village'},
    'natural': {'peak'}
}


# todo automatic wanted objects setup using map and pdf ratio automatic_filters_creating_factor - own class ()


unwanted_nodes_tags: UnwantedTags = {

}

wanted_ways: WantedCategories = {
    'waterway': set({}),
    'highway': ['motorway', 'trunk','primary', 'secondary', 'tertiary'],
    # 'highway': ['motorway', 'trunk','primary', 'secondary'],
    # 'highway': {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'},
    # 'highway':[],
    'railway': {'rail'}
}

unwanted_ways_tags: UnwantedTags = {
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    'railway': {
        'service': ['yard', 'spur'], # spur, siding
        'tunnel': ['building_passage'],
    },
    'waterway': ['stream']

    
    # {'railway':""}:{'service':['yard'],'tunnel': ['building_passage']}
}


wanted_areas: WantedCategories = {
        # # 'landuse': ['forest', 'residential', 'farmland', 'meadow', 'grass'],
        'landuse': {'forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'},
        'leisure': {'park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
        # 'leisure': {'park', 'pitch', 'garden', 'golf_course', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
        'natural': {'wood', 'water', 'scrub', 'heath'},
        # # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
        'water': set({}),
        'boundary': {'national_park'},
        'building':{'house','residential'}
        # 'water': ['river','lake','reservoir'],
}
unwanted_areas_tags: UnwantedTags = {
}

# todo change to ElementStylesDynamic and create function to convert from it to this - same filter but dict is created from this and specific zooms
# ------------styles--------------
GENERAL_DEFAULT_STYLES: FeatureStyles = {StyleKey.COLOR: '#EDEDE0',  StyleKey.ZINDEX: 0,
                                        StyleKey.WIDTH: 1, StyleKey.LINESTYLE: '-',
                                          StyleKey.ALPHA: 1, StyleKey.EDGE_COLOR: None, StyleKey.EDGE_LINESTYLE: '-'}
# -------------------nodes-------------------
# styles that must be assigned to all node features
nodes_mandatory_styles: ElementStyles = [
    ([], {
        StyleKey.COLOR: '#000000', StyleKey.TEXT_FONT_SIZE: 50, 
        StyleKey.EDGE_COLOR: '#FFFFFF', StyleKey.TEXT_OUTLINE_WIDTH: 5
    })
]

place_styles: ElementStyles = [
    ([('place', 'city')], {
        StyleKey.TEXT_FONT_SIZE: 2500 * CITY_CITY_SIZE_MULTIPLIER, 
        StyleKey.TEXT_OUTLINE_WIDTH: 270 * CITY_CITY_SIZE_MULTIPLIER
    }),
    ([('place', 'town')], {
        StyleKey.TEXT_FONT_SIZE: 1500 * CITY_TOWN_SIZE_MULTIPLIER, 
        StyleKey.TEXT_OUTLINE_WIDTH: 170 * CITY_TOWN_SIZE_MULTIPLIER
    }),
    # ([('place', 'village')], {
    #     StyleKey.TEXT_FONT_SIZE: 15 * CITY_VILLAGE_SIZE_MULTIPLIER, 
    #     StyleKey.TEXT_OUTLINE_WIDTH: 0 * CITY_VILLAGE_SIZE_MULTIPLIER
    # }),
    ([('place', 'village')], {
        StyleKey.TEXT_FONT_SIZE: 550 * CITY_VILLAGE_SIZE_MULTIPLIER, 
        StyleKey.TEXT_OUTLINE_WIDTH: 110 * CITY_VILLAGE_SIZE_MULTIPLIER
    }),
]
# !!! icon from svg
# # # from svgpath2mpl import parse_path
# # # finis = parse_path("M 100,10 L 40,198 L 190,78 L 10,78 L 160,198 z")
# # # finis = parse_path("M 0,0 L 0,100 L 100,100 L 100,0 z")
# # # def center_path(p):
# # #     p.vertices -= p.vertices.mean(axis=0)
# # #     return p

# # # test = {
# # #     "d": 112,
# # #     "marker": center_path(parse_path("M 100,10 L 40,198 L 190,78 L 10,78 L 160,198 z"))
# # # }
natural_styles_nodes: ElementStyles = [
    ([('natural', 'peak')], {
        StyleKey.ICON: "^", StyleKey.COLOR: "#7f3016", 
        StyleKey.EDGEWIDTH: 0.2, StyleKey.TEXT_OUTLINE_WIDTH: 50, 
        StyleKey.TEXT_FONT_SIZE: 400, StyleKey.WIDTH: 3.6
    }),
]


nodes_styles_default: ElementStyles = [
    ([('place', '')], {
        StyleKey.COLOR: '#000000', StyleKey.EDGE_COLOR: '#FFFFFF'
    }),
    ([('natural', '')], {
    }),
    # ([('natural', '')], {
    #     StyleKey.COLOR: "red", StyleKey.EDGE_COLOR: '#FFFFFF', 
    #     StyleKey.WIDTH: 300**2
    # }),
]

NODES_STYLES: ElementStyles = [
    *natural_styles_nodes,
    *place_styles,
    *nodes_styles_default,
    *nodes_mandatory_styles
]

# -------------------ways-------------------
# styles that must be assigned to all way features
ways_mandatory_styles: ElementStyles = [
    ([], {
        StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0, StyleKey.WIDTH: 1, StyleKey.LINESTYLE: '-',
        StyleKey.EDGE_WIDTH_RATIO: 0.3, StyleKey.BRIDGE_WIDTH_RATIO: 0, StyleKey.BRIDGE_EDGE_WIDTH_RATIO: 0.3, 
        StyleKey.BRIDGE_COLOR: "#FFFFFF", StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D", 
        StyleKey.EDGE_COLOR: None, StyleKey.EDGE_LINESTYLE: '-'
    })
]

# # highway_styles_tunnels: FeaturesCategoryStyle = {
# #     'motorway': {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.WIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"..},
# # }

highway_styles: ElementStyles = [
    ([('highway', 'motorway')], {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.WIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"}),
    ([('highway', 'trunk')], {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6, StyleKey.WIDTH: 26, StyleKey.EDGE_COLOR: "#E19532"}),
    ([('highway', 'primary')], {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5, StyleKey.WIDTH: 22, StyleKey.EDGE_COLOR: "#E19532"}),
    ([('highway', 'secondary')], {StyleKey.COLOR: '#F7ED60', StyleKey.ZINDEX: 4, StyleKey.WIDTH: 20, StyleKey.EDGE_COLOR: "#c1b42a"}),
    ([('highway', 'tertiary')], {StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 3, StyleKey.WIDTH: 16}),
    ([('highway', 'unclassified')], {StyleKey.COLOR: '#FFFFFF'}),
    ([('highway', 'road')], {StyleKey.COLOR: '#FFFFFF'}),
    ([('highway', 'footway')], {StyleKey.COLOR: '#FFFFFF', StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
    ([('highway', 'steps')], {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None}),
    ([('highway', 'path')], {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
    ([('highway', 'track')], {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--", StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
    ([('highway', 'residential')], {StyleKey.COLOR: '#FFFFFF'}),
]

railway_styles: ElementStyles = [
    ([('railway', 'rail')], {
        StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 1, StyleKey.WIDTH: 10,
        StyleKey.BRIDGE_EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_COLOR: "#FFFFFF",
        StyleKey.EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_WIDTH_RATIO: 1.7, 
        StyleKey.BRIDGE_EDGE_WIDTH_RATIO: 0.4,  # todo control after function to calculating width
        StyleKey.LINESTYLE: (0, (5, 5))
    }),
    ([('railway', 'tram')], {
        StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 10, StyleKey.WIDTH: 4, 
        StyleKey.ALPHA: 0.6
    }),
    ([('railway', 'tram_stop')], {
        StyleKey.COLOR: '#404040', StyleKey.ZINDEX: 1, StyleKey.WIDTH: 4
    })
]


ways_styles_default: ElementStyles = [

    ([('highway', '')], {
        StyleKey.COLOR: '#FFFFFF', StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D",
        StyleKey.ZINDEX: 1, StyleKey.WIDTH: 8, StyleKey.EDGE_COLOR: "#B0A78D"
    }),
    ([('railway', '')], {
        StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 2, StyleKey.WIDTH: 8
    }),
    ([('waterway', '')], {
        StyleKey.COLOR: '#8FB8DB', StyleKey.WIDTH: 8, 
        StyleKey.ZINDEX: 0, StyleKey.EDGE_COLOR: None
    }),
]


WAYS_STYLES: ElementStyles = [
    *highway_styles,
    *railway_styles,
    *ways_styles_default,
    *ways_mandatory_styles
]

# -------------------areas-------------------
# styles that must be assigned to all area features
area_mandatory_styles: ElementStyles = [
    ([], {
        StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0
    })
]
landuse_styles: ElementStyles = [
    ([('landuse', 'farmland')], {StyleKey.COLOR: '#EDEDE0'}),
    ([('landuse', 'forest')], {StyleKey.COLOR: '#9FC98D'}),
    ([('landuse', 'meadow')], {StyleKey.COLOR: '#B7DEA6'}),
    ([('landuse', 'grass')], {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1}),
    ([('landuse', 'residential')], {StyleKey.COLOR: '#E2D4AF'}),
    ([('landuse', 'industrial')], {StyleKey.COLOR: '#DFDBD1'}),
    ([('landuse', 'basin')], {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    ([('landuse', 'salt_pond')], {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
]

# todo ....

leisure_styles: ElementStyles = [
    ([('leisure', 'swimming_pool')], {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    ([('leisure', 'golf_course')], {StyleKey.COLOR: '#DCE9B9'}),
    ([('leisure', 'playground')], {StyleKey.COLOR: '#DCE9B9'}),
    ([('leisure', 'pitch')], {StyleKey.COLOR: '#DCE9B9', StyleKey.ZINDEX: 1}),
    ([('leisure', 'sports_centre')], {StyleKey.COLOR: '#9FC98D'}),
    ([('leisure', 'nature_reserve')], {StyleKey.COLOR: None, StyleKey.EDGE_COLOR: '#97BB72', 
                                       StyleKey.WIDTH: 80, StyleKey.ZINDEX: 1, 
                                       StyleKey.ALPHA: 0.85, StyleKey.EDGE_LINESTYLE: '-'})
]

building_styles: ElementStyles = [
    ([('building', 'house')], {StyleKey.COLOR: 'grey', StyleKey.ZINDEX: 1}),
    ([('building', 'residential')], {StyleKey.COLOR: 'grey', StyleKey.ZINDEX: 1}),
]

natural_styles: ElementStyles = [
    ([('natural', 'wood')], {StyleKey.COLOR: '#9FC98D'}),
    ([('natural', 'water')], {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    ([('natural', 'scrub')], {StyleKey.COLOR: '#B7DEA6'}),
    ([('natural', 'heath')], {StyleKey.COLOR: '#B7DEA6'}),
]

area_styles_default: ElementStyles = [
    ([('building', '')], {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1}),
    ([('landuse', '')],  {StyleKey.COLOR: '#EDEDE0'}),
    ([('water', '')], {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    ([('leisure', '')], {StyleKey.COLOR: '#EDEDE0', StyleKey.WIDTH: 8}),
    ([('natural', '')], {StyleKey.COLOR: '#B7DEA6'}),
    ([('boundary', '')], {
        StyleKey.COLOR: None, StyleKey.EDGE_COLOR: '#97BB72',
        StyleKey.WIDTH: 80, StyleKey.EDGE_LINESTYLE: '-',
        StyleKey.ZINDEX: 1, StyleKey.ALPHA: 0.85
    })
]

AREAS_STYLES: ElementStyles = [
    *natural_styles, 
    *building_styles,
    *landuse_styles,
    *leisure_styles,
    *area_styles_default,
    *area_mandatory_styles
]

STYLES: dict[str, ElementStyles]   = {
    'nodes': NODES_STYLES,
    'ways': WAYS_STYLES,
    'areas': AREAS_STYLES
}

# ------------constants--------------

# world 3857
EPSG_OSM = 4326
# mercato to all ploting and calc paper and map scaling factor of elements and special funcion for map scale
# map scaling factor of elements should be in same as map will be displayed to maintain same scale
# EPSG_CALC = 25833  
EPSG_CALC = 3857  # europe 25833 - calculating map scale and scaling factor
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
