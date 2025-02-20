from common.custom_types import *
from common.map_enums import *


# --------------------------------------------------------------map area--------------------------------------------------------------
# OSM_INPUT_FILE_NAMES: str = ['../osm_files/vys.osm.pbf','../osm_files/jihmor.osm.pbf']
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/vysJihE.osm.pbf'
OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/jihmor.osm.pbf'
# OSM_INPUT_FILE_NAMES: str | list[str] = '../trebic.osm.pbf'
# extract
OSM_WANT_EXTRACT_AREA: bool = False
# set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None
OSM_OUTPUT_FILE_NAME: None | str = '../osm_files/T.osm.pbf'

OUTPUT_PDF_NAME: str = '../pdfs/divocina1'
# with fill or false cliping is recomended 0
# padding from page borders NOTE: must have same settings as the resulting one when generating for large format printing
PERCENTAGE_PADDING = 0

# AREA: WantedArea = [(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)] #island
# AREA: WantedArea = [(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)] #afrika
# AREA: WantedArea = [(13.2198495,-8.8130580),(13.2614774,-8.8139062),(13.2616062,-8.8439302),(13.2181329,-8.8424460)] #angola - mesto 5km
# AREA: WantedArea = [(13.2020960,-8.7766815),(13.2020370,-8.8766827),(13.3099288, -8.8775122), (13.3082471,-8.7782667)] # angol- 11.85 - z14 - square
# AREA: WantedArea = [(13.0140862,-8.8831442),(13.1660763,-8.8819132),(13.1667146, -9.0826624), (13.0159664,-9.0781028)] # angol- ostrovy test
# AREA: WantedArea = [(15.7937669,49.2511294),(15.7940459,49.1851468),(15.9009507, 49.1847962), (15.9003445,49.2499564)] # tr - 7.8 - z14 - square

# zoom testing
# AREA: WantedArea = [(15.8149639,48.6439769), (15.8183625,48.6439700), (15.8183439, 48.6423997), (15.8149561, 48.6424158)] # zoom 19  - 0.7832305054706878
# AREA: WantedArea = [(15.8131475,48.6445003), (15.8199369,48.6445106), (15.8199317, 48.6413736), (15.8131403, 48.6413914)] # zoom 18  - 0.39254868520064207
# AREA: WantedArea = [(15.8096936,48.6459956), (15.8232333,48.6460311), (15.8232550, 48.6397219), (15.8097686, 48.6397503)] # zoom 17 - 0.19673458447026707
# AREA: WantedArea = [(15.8036264,48.6490436), (15.8307706,48.6489869), (15.8307706, 48.6363825), (15.8035836, 48.6365244)] # zoom 16 - 0.0981350054744773
# AREA: WantedArea = [(15.8408317, 48.6556897), (15.7863853, 48.6557486), (15.7865139, 48.6306536), (15.8407161, 48.6304267)] # zoom 15 - 0.049002255315964124
# AREA: WantedArea = [(15.7568897,48.6700053), (15.8648558, 48.6704314), (15.8651992, 48.6197892), (15.7563658, 48.6202431)] # zoom 14 - 0.024514500087610937 
# AREA: WantedArea = [(15.7034756,48.6941575), (15.9206889,48.6941186), (15.9198775, 48.5926164), (15.7030222, 48.5936264)] # zoom 13 - 0.012257255675006467
# AREA: WantedArea = [(15.5986414,48.7535425), (16.0311167,48.7533311), (16.0307733, 48.5528361), (15.5975000, 48.5544269)] # zoom 12 - 0.0061528912374338475
# AREA: WantedArea = [(15.3856592,48.8443469), (16.2499850,48.8453725), (16.2499850, 48.4415864), (15.3854983, 48.4465967)] # zoom 11 - 0.0030862202898378687
# AREA: WantedArea = [(14.8355758,49.0061161), (16.5771717,49.0046311), (16.5799181, 48.2009656), (14.8385853, 48.2055419)] # zoom 10 - 0.001529514243755352
# AREA: WantedArea = [(14.0269703,49.4851617), (17.5151294,49.4833772), (17.5096361,47.8731517), (14.0297167, 47.8786783)] # zoom 9 - 0.000764872334474359
# AREA: WantedArea = [(12.4551956,50.4569714), (19.4047778,50.4934189), (19.3992847, 47.2727942), (12.4284594, 47.3100528)] # zoom 8 - 0.0003824361562733402
# AREA: WantedArea = [(7.4931519,51.7666714), (21.3850633,51.7483686),(21.3740772, 45.3686397), (7.4983447, 45.3454797) ] # zoom 7 - 0.0001920539454228724
# AREA: WantedArea = [(0.3733594, 54.1375764), (27.5538867, 54.1118236),(27.5538867, 40.9478483), (0.3294142, 41.1136006)]  # zoom 6 - 0.000095


# AREA: WantedArea = [[(15.7396182, 49.3111173), (16.0273871, 49.3028839),
#                     (16.0266146, 49.1439064), (15.6712219, 49.1928600)]]  # trebic
# AREA: WantedArea = ["Česko","Vysočina, Česko", "Jihomoravský kraj, Česko"]
# AREA: WantedArea = ["Brno, Česko"]
# AREA: WantedArea = ["Jihomoravský kraj, Česko", "Kraj Vysočina, Česko"]
# AREA: WantedArea = ["Kraj Vysočina, Česko"]
AREA: WantedArea = ["Jihomoravský kraj, Česko"]
# AREA: WantedArea = ["Česko"]
# AREA: WantedArea = ["Okřešice, Česko"]
# AREA: WantedArea = ["Třebíč, Česko"]
# AREA: WantedArea = ["Okres Třebíč, Česko", "Třebíč, Česko", "Okres Jihlava, Česko"]
# AREA: WantedArea = ["Texas, USA"]

PAPER_DIMENSIONS: PaperSize | tuple[float | None, float | None] = PaperSize.A4.dimensions
# PAPER_DIMENSIONS: PaperSize | tuple[float | None, float | None] = PaperSize.A4.dimensions
# set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
# PAPER_DIMENSIONS = (1100, None)

# what side of paper was set (smaller true bigger false) - only if only one side in custom dimension was set to None
GIVEN_SMALLER_PAPER_DIMENSION: bool = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
WANTED_ORIENTATION: MapOrientation = MapOrientation.AUTOMATIC

# FIT_PAPER_SIZE recomended with PERCENTAGE_PADDING 0
FIT_PAPER_SIZE = False

# bounds
# COMBINED - one bound around area, SEPARATED - separated bounds around every area in AREA variable
AREA_BOUNDARY = AreaBounds.SEPARATED
EXPAND_AREA_BOUNDS_PLOT = False
AREA_BOUNDARY_LINEWIDTH = 3

# text general
TEXT_WRAP_NAMES_LEN = 15  # len or None if not wrap (15 default)
# if allow is false set threashold (0-1) how much of text must be inside
TEXT_BOUNDS_OVERFLOW_THRESHOLD = 0.97

# plot as bridge (True)  or normal way (False)
PLOT_BRIDGES = True
# plot as tunnel (True) or normal way (False) - if false and in dont want tags -> will not be plotted at all
PLOT_TUNNELS = True

# --------------------------------------------------------------preview--------------------------------------------------------------
# NOTE: must have same settings as the resulting one when generating for large format printing
WANT_PREVIEW: bool = False
# OUTER_AREA: WantedArea = [(15.7034756,48.6941575), (15.9206889,48.6941186), (15.9198775, 48.5926164), (15.7030222, 48.5936264)] # zoom 13 - 0.012257255675006467

# area for that you are creating smaller preview (bigger than normal area)
OUTER_AREA: WantedArea = "Vysočina, Česko"
# OUTER_AREA: WantedArea = "Česko"
# OUTER_AREA: WantedArea = [(15.7396182, 49.3111173), (16.0273871, 49.3028839),
#                     (16.0266146, 49.1439064), (15.6712219, 49.1928600)]

# OUTER_PAPER_DIMENSIONS = PaperSize.A4.dimensions  # real paper size
# or set own #if one is left none if will be automaticaly calculated by area size
OUTER_PAPER_DIMENSIONS = (1100, None)
# what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)
OUTER_GIVEN_SMALLER_PAPER_DIMENSION = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
OUTER_WANTED_ORIENTATION = MapOrientation.AUTOMATIC

# expand area
OUTER_FIT_PAPER_SIZE = False
 
# ------------constants--------------
# world 3857
CRS_OSM = "EPSG:4326"
# mercato to all ploting and calc paper and map scaling factor of elements and special funcion for map scale
# map scaling factor of elements should be in same as map will be displayed to maintain same scale
CRS_CALC = "EPSG:3857"  # europe 25833 - calculating map scale and scaling factor
CRS_DISPLAY = "EPSG:3857"

OBJECT_MULTIPLIER = 1
AREAS_EDGE_WIDTH_MULTIPLIER = 1
WAYS_WIDTH_MULTIPLIER = 1

# --------------------------------------------------------------gpx settings--------------------------------------------------------------

# zooms: scaling values for center of each zoom level 
ZOOM_MAPPING: dict[int, float] = {
    19: 0.7832305,
    18: 0.3925486,
    17: 0.1967345,
    16: 0.0981350,
    15: 0.0490022,
    14: 0.0245145,
    13: 0.0122572,
    12: 0.0061528,
    11: 0.0030862,
    10: 0.0015295,
    9:  0.0007648,
    8:  0.0003824,
    7:  0.0001920,
    6:  0.0000958
}

# this will come from FE:

GPX_FOLDER: str = '../gpxs/trebic2'
ROOT_FILES_COLOR_MODE: ColorMode = ColorMode.DEFAULT
ROOT_FILES_COLOR_OR_PALLET: str = "Set1"
ROOT_FILES_COLOR_DIS_PALLET = True

FOLDER_COLOR_MODE: ColorMode = ColorMode.DEFAULT
FOLDER_COLOR_OR_PALLET: str = "Set1"
FOLDER_COLOR_DIS_PALLET = True


# -------------------gpx styles by folder-------------------

# todo styles for gpx will be assigned on fronted and will be sended to backend in format like
# gpx will be recived from FE a turned to gdf and then styled by backend using sent styles

# --------------filters for map elements--------------
# columns that are used for ploting nodes name for city, ele for elevation points
NODES_ADDITIONAL_COLUMNS = ['name', 'ele']
WAYS_ADDITIONAL_COLUMNS = ['bridge', 'layer', 'tunnel']
AREA_ADDITIONAL_COLUMNS = []

NODES_NAMES_FROM_COLUMNS = [
    ({'place': ''}, StyleKey.TEXT1 , 'name'),
    ({'natural': 'peak'}, StyleKey.TEXT1, 'name'),
    ({'natural': 'peak'}, StyleKey.TEXT2, 'ele')]

NODES_DONT_CATEGORIZE = [StyleKey.TEXT1_POSITIONS, StyleKey.TEXT2_POSITIONS]

# wanted_ways: WantedFeatures
wanted_nodes: WantedCategories = {
    # 'place': {'city'},
    # # 'place': {'city', 'town'},
    'place': {'city', 'town', 'village'},
    # 'place': {'village'},
    'natural': {'peak'}
}


# todo automatic wanted objects setup using map and pdf ratio automatic_filters_creating_factor - own class ()


unwanted_nodes_tags: UnwantedTags = {

}

wanted_ways: WantedCategories = {
    # 'waterway': set({}),
    # 'highway': ['motorway', 'trunk','primary', 'secondary', 'tertiary'],
    # 'highway': ['motorway', 'trunk', 'primary'],
    # 'highway': {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'},
    # 'highway': {'tertiary'},
    # 'highway':set({}),
    # 'railway': {'rail', 'tram'},

    # # 'railway': {'rail'},
    # 'natural': {'coastline'}
}

unwanted_ways_tags: UnwantedTags = {
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    # 'railway': {
    #     'service': ['yard', 'spur','crossover', 'siding'], # spur, siding
    #     # 'tunnel': ['building_passage'],
    #     # 'tunnel': [],
    # },
    # 'waterway': ['stream']

    
    # {'railway':""}:{'service':['yard'],'tunnel': ['building_passage']}
}

wanted_areas: WantedCategories = {
        # 'landuse': {'forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'},
   
        # 'leisure': {'park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
        # # 'leisure': {'park', 'pitch', 'garden', 'golf_course', 'playground', 'stadium', 'swimming_pool', 'sports_centre'},
        # 'natural': {'wood', 'water', 'scrub', 'heath'},
        # # # 'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve'],
        # # 'water': set({}),
        # 'boundary': {'national_park'},
        # 'building': {'house','residential'},
        # 'water': ['river','lake','reservoir'],
}

unwanted_areas_tags: UnwantedTags = {
}

