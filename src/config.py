import warnings
import matplotlib.font_manager as fm

from common.custom_types import UnwantedTags, WantedArea, WantedCategories
from common.map_enums import Style, ColorMode, PaperSize, MapOrientation, MarkersCodes, MapThemeVariable


# --------------------------------------------------------------map area--------------------------------------------------------------
# OSM_INPUT_FILE_NAMES: str = ['../osm_files/vys.osm.pbf','../osm_files/jihmor.osm.pbf']
# OSM_INPUT_FILE_NAMES: str | list[str] = '../osm_files/vysJihE.osm.pbf'
# OSM_INPUT_FILE_NAMES: str | list[str] = ['../test.osm.pbf']
OSM_INPUT_FILE_NAMES: str | list[str] = ['../osm_files/zoo.osm.pbf']
# OSM_INPUT_FILE_NAMES: str | list[str] = '../trebic.osm.pbf'
# extract - will be always true
OSM_WANT_EXTRACT_AREA: bool = False
# set if want osm file cutting using osmium command line tool (need to be uinstalled), If not set to None
OSM_OUTPUT_FILE_NAME: None | str = '../osm_files/zoo.osm.pbf'

OUTPUT_PDF_NAME: str = '../pdfs/invalid'

# AREA: WantedArea = [(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)] #island
# AREA: WantedArea = [(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)] #afrika
# AREA: WantedArea = [(13.2198495,-8.8130580),(13.2614774,-8.8139062),(13.2616062,-8.8439302),(13.2181329,-8.8424460)] #angola - mesto 5km
# AREA: WantedArea = [(13.2020960,-8.7766815),(13.2020370,-8.8766827),(13.3099288, -8.8775122), (13.3082471,-8.7782667)] # angol- 11.85 - z14 - square
# AREA: WantedArea = [{"area": [(13.0140862,-8.8831442),(13.1660763,-8.8819132),(13.1667146, -9.0826624), (13.0159664,-9.0781028)],
#                      "plot": False, "category": 0, "width": 1}] # angol- ostrovy test
# AREA: WantedArea = [(15.7937669,49.251 1294),(15.7940459,49.1851468),(15.9009507, 49.1847962), (15.9003445,49.2499564)] # tr - 7.8 - z14 - square

# viden zoo - chodnik a ikony - rchod
# AREA: WantedArea = [{'area':[(16.2985736,48.1866714), (16.3121350, 48.1865714), (16.3120706, 48.1803122), (16.2985736, 48.1803981)], "plot":False}] # zoom 10/17

# rakousko - cestičky -rcest
# AREA: WantedArea = [{'area':[(16.0627306,48.0580592), (16.0897244, 48.0580592), (16.0897244, 48.0453939), (16.0626878, 48.0454514)], "plot":False}] # zoom 9/16

# rakousko - cestičky u koní -rkon
# AREA: WantedArea = [{'area': [(15.9759536,48.0569747), (16.0298253, 48.0564572), (16.0299514, 48.0315206), (15.9758781, 48.0318936)], "plot":False}] # zoom 8/15

# rakousko - dalince konce a trunk - rtrunk
# AREA: WantedArea = [{'area': [(16.7637897,48.6661533), (16.5724411, 48.6708094), (16.5820542, 48.7711483), (16.7701950, 48.7706958)], "plot":False}] # zoom 8/15

#rakousko - dalince konce a trunk - rnpark
# AREA: WantedArea = [{'area': [(16.6840794, 47.8736964), (16.9535233, 47.8754153), (16.9468556, 47.7549778), (16.6704806, 47.7522078)], "plot":False}] # zoom 8/15

#rakousko - invalidní oblast - rinvalid
AREA: WantedArea = [{'area': [(16.3351344, 48.2143981), (16.3379578, 48.2144222), (16.3377272, 48.2127386), (16.3351631, 48.2128781)], "plot":False}] # zoom 8/15


# slovensko - aminety grave - skgrave
# AREA: WantedArea = [{'area': [(17.5622753,48.2370358), (17.5805572, 48.2372431), (17.5798706, 48.2319261), (17.5622325, 48.2326694)], "plot":False}] # zoom 8/15

# slovensko - cesty/tunel - pathtunel -skprimlink
# AREA: WantedArea = [{'area': [(17.0829244,48.1368075), (17.11670941, 48.1362819), (17.1167183,48.1188031), (17.0824389, 48.1203419)], "plot":False}] # zoom 8/15

# slovensko - cesty/tunel - pathtunel -skseclink
# AREA: WantedArea = [{'area': [(17.0684572,48.1268372), (17.1043628, 48.1272075), (17.1034186,48.1060056), (17.0688289, 48.1074958)], "plot":False}] # zoom 8/15

# slovensko - cesty/tunel - pathtunel -skptunl
# AREA: WantedArea = [{'area': [(16.9703950,48.2047167), ( 17.0168581, 48.2045317), (17.0169011, 48.1791842), (16.9623128, 48.1794417)], "plot":False}] # zoom 8/15

# slovensko - cyklotrasa asfalt/non asfalt- pathtunel u koní -skptunl

# slovensko - lanovky - sklan
# AREA: WantedArea = [{'area': [(18.9836906,49.2351414), (19.1019653, 49.2350294), (19.1017936, 49.1852375), (18.9838622, 49.1870325)], "plot":False}] # zoom

# slovensko - letiste - sklet
# AREA: WantedArea = [{'area': [(17.1374492,48.1955133), (17.2557239, 48.1951700), (17.2557239, 48.1444531), (17.1377925, 48.1452547)], "plot":False}] # zoom

# slovensko - bratislava centrum  - skbr
# AREA: WantedArea = [{'area': [(17.0797297, 48.1649183), (17.1410558, 48.1642600), (17.1413133, 48.1383769), (17.0762106, 48.1384056)], "plot": False}]  # zoom

# slovensko - voj prostor  - skvoj
# AREA: WantedArea = [{'area': [(17.0325058,48.6691606), (17.6252633, 48.6856314), (17.6225169, 48.1661969), (17.0031625, 48.1808503)], "plot":False}] # zoom

# slovensko - bratislava nakup a landuse others  - sknak
# AREA: WantedArea = [{'area': [(16.9756656,48.1968728), (16.9761267, 48.2213817), (17.0408431, 48.2214961), (17.0408431, 48.1953561)], "plot":False}] # zoom

# slovensko - bratislava area way  - skareaway
# AREA: WantedArea = [{'area': [(17.1848258,48.1529047), (17.2031475, 48.1531017), (17.2038558, 48.1396642), (17.1842006, 48.1394925)], "plot":False}] # zoom

# slovensko - potok, reka, kanal, silnice 1,2,3 a dalnice, zelecnice, residental,
# service, footway
# industrial zona - skways
# AREA: WantedArea = [{'area': [(16.8529242,48.4770300), (17.2031475, 48.4733883), (17.1986503, 48.3386914), (16.8525808, 48.3382350)], "plot":False}] # zoom


# nemecko - funicular tunnel a railway tunnel - gefun
# AREA: WantedArea = [{'area': [(8.6807722,49.4195719), (8.7399353, 49.4195644), (8.7400211, 49.3951311), (8.6807550, 49.3952708)], "plot":False}] # zoom


# rozhledna - baliny
#AREA: WantedArea = [{"area": "Baliny, Česko", "plot": True, "category": 0, "width": None}]


# zricenina - rokstejn - Brtnice
# AREA: WantedArea = [{"area": "Brtnice, Česko", "plot": True, "category": 0, "width": None}]


# zoom testing
# AREA: WantedArea = [{'area':[(15.8096936,48.6459956), (15.8232333, 48.6460311), (15.8232550, 48.6397219), (15.8097686, 48.6397503)], "plot": False}] # zoom 10/17 - 0.19673458447026707
# AREA: WantedArea = [{'area':[(15.8036264,48.6490436), (15.8307706, 48.6489869), (15.8307706, 48.6363825), (15.8035836, 48.6365244)], "plot": False}] # zoom 9/16 - 0.0981350054744773
# AREA: WantedArea = [{'area':[(15.8408317, 48.6556897), (15.7863853, 48.6557486), (15.7865139, 48.6306536), (15.8407161, 48.6304267)], "plot": False}] # zoom 8/15 - 0.049002255315964124
# AREA: WantedArea = [{'area':[(15.7568897,48.6700053), (15.8648558, 48.6704314), (15.8651992, 48.6197892), (15.7563658, 48.6202431)], "plot": False}] # zoom 7/14 - 0.024514500087610937
# AREA: WantedArea = [{'area':[(15.7034756,48.6941575), (15.9206889, 48.6941186), (15.9198775, 48.5926164), (15.7030222, 48.5936264)], "plot": False}] # zoom 6/13 - 0.012257255675006467
# AREA: WantedArea = [{'area':[(15.5986414,48.7535425), (16.0311167, 48.7533311), (16.0307733, 48.5528361), (15.5975000, 48.5544269)], "plot": False}] # zoom 5/12 - 0.0061528912374338475
# AREA: WantedArea = [{'area':[(15.3856592,48.8443469), (16.2499850, 48.8453725), (16.2499850, 48.4415864), (15.3854983, 48.4465967)], "plot": False}] # zoom 4/11 - 0.0030862202898378687
# AREA: WantedArea = [{'area':[(14.8355758,49.0061161), (16.5771717,49.0046311), (16.5799181, 48.2009656), (14.8385853, 48.2055419)], "plot": False}] # zoom 3/10 - 0.001529514243755352
# AREA: WantedArea = [{'area':[(14.0269703,49.4851617), (17.5151294,49.4833772), (17.5096361,47.8731517), (14.0297167, 47.8786783], "plot": False}] # zoom 2/9 - 0.000764872334474359
# AREA: WantedArea = [{'area':[(12.4551956,50.4569714), (19.4047778,50.4934189), (19.3992847, 47.2727942), (12.4284594, 47.3100528)], "plot": False}] # zoom 1/8 - 0.0003824361562733402



# AREA: WantedArea = [{"area": "Slovensko", "plot": False}]
# AREA: WantedArea = [{"area": "Brno, Česko", "plot": True, "category": 5, "width": None}]
# AREA: WantedArea = [{"area": "Baliny, Česko", "plot": True, "category": 0, "width": None}]
# AREA: WantedArea =[{"area": "Jihomoravský kraj, Česko", "plot": True, "category": 2, "width": 1},
#                     {"area": "Praha, Česko", "plot": True, "category": 1, "width": 1},
#                     {"area": "Trebic, Česko", "plot": True, "category": 1, "width": 1}]
# AREA: WantedArea = [{"area": "Jihomoravský kraj, Česko", "plot": True, "category": 2, "width": 1},
#                     {"area": "Kraj Vysočina, Česko", "plot": True, "category": 1, "width": 1},
#                      {"area": "Pardubický kraj, Česko", "plot": True, "category": 2, "width": 1},
#                       {"area": "Jihočeský kraj, Česko", "plot": True, "category": 1, "width": 1}]

# AREA: WantedArea = [{"area": "Třebíč, Česko", "plot": False, "category": 1, "width": 1},
#                     {"area": "Trnava, Vysočina, Česko", "plot": False, "category": 1, "width": 1},
#                     {"area": "Horní Vilémovice, Česko", "plot": False, "category": 1, "width": 1}]
# AREA: WantedArea = [{"area": "Jaroměřice nad rokytnou, Česko", "plot": True, "category": 0, "width": 1}]
# AREA: WantedArea = [{"area": "Jihomoravský kraj, Česko", "plot": True, "category": 1, "width": 1},
#                     {"area": "Kraj Vysočina, Česko", "plot": True, "category": 1, "width": 1},
#                     {"area": "Třebíč, Česko", "plot": False, "category": 0, "width": 1}]
# AREA: WantedArea = [{"area": "Německo", "plot": True, "category": 1, "width": 1},
# {"area": "Lucembursko", "plot": True, "category": 2, "width": 1}]

# AREA: WantedArea = ["Kraj Vysočina, Česko"]
# AREA: WantedArea = ["Jihomoravský kraj, Česko"]
# AREA: WantedArea = ["Česko"]
# AREA: WantedArea = ["Okřešice, Česko"]
# AREA: WantedArea = ["Třebíč, Česko"]
# AREA: WantedArea = ["Okres Třebíč, Česko", "Třebíč, Česko", "Okres Jihlava, Česko"]
# AREA: WantedArea = ["Texas, USA"]

PAPER_DIMENSIONS: PaperSize | tuple[float |
                                    None, float | None] = PaperSize.A4.dimensions
# PAPER_DIMENSIONS: PaperSize | tuple[float | None, float | None] = PaperSize.A4.dimensions
# set own dimensions. If one is left as 'None' it will be automaticaly calculated using area size
# PAPER_DIMENSIONS = (1100, None)

# what side of paper was set (smaller true bigger false) - only if only one side in custom dimension was set to None
GIVEN_SMALLER_PAPER_DIMENSION: bool = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
WANTED_ORIENTATION: MapOrientation = MapOrientation.AUTOMATIC

FIT_PAPER_SIZE = True
FIT_PAPER_SIZE_BOUNDS_PLOT = False


# text general
TEXT_WRAP_NAMES_LEN = 15  # len or 0/None if not wrap (15 default)
# if allow is false set threashold (0-1) how much of text must be inside
TEXT_BOUNDS_OVERFLOW_THRESHOLD = 0.97

map_theme = 'mapycz'
# plot as bridge (True)  or normal way (False)
PLOT_BRIDGES = False
# plot as tunnel (True) or normal way (False) - if false and in dont want tags -> will not be plotted at all
PLOT_TUNNELS = True
PEAKS_FILTER_SENSITIVITY: float | None = 2.5
ELE_PROMINENCE_MAX_DIFF_RATIO = 3

# from fe by zoom or from be map styles by zoom
MIN_POPULATION: int | None = 300
PLACES_TO_FILTER_BY_POPULATION = ['city', 'town', 'village']
# --------------------------------------------------------------preview--------------------------------------------------------------
# NOTE: must have same settings as the resulting one when generating for large format printing
WANT_PREVIEW: bool = True
# OUTER_AREA: WantedArea = [(15.7034756,48.6941575), (15.9206889,48.6941186), (15.9198775, 48.5926164), (15.7030222, 48.5936264)] # zoom 13 - 0.012257255675006467

# area for that you are creating smaller preview (bigger than normal area)
# OUTER_AREA: WantedArea =  "Vysočina, Česko"

OUTER_AREA: WantedArea =  [{"area": "Česko", "plot": True, "category": 2, "width": 1}]
# OUTER_AREA: WantedArea =  [{"area": "Česko", "plot": True, "category": 2, "width": 1},
#                            {"area": "Slovensko", "plot": True, "category": 2, "width": 1}]
# OUTER_AREA: WantedArea = [{"area": "Jihomoravský kraj, Česko", "plot": True, "category": 2, "width": 1},
                        #   {"area": "Praha, Česko", "plot": True, "category": 1, "width": 1}]
# OUTER_AREA: WantedArea = "Česko"
# OUTER_AREA: WantedArea = [(15.7396182, 49.3111173), (16.0273871, 49.3028839),
#                     (16.0266146, 49.1439064), (15.6712219, 49.1928600)]

# OUTER_PAPER_DIMENSIONS = PaperSize.A0.dimensions  # real paper size
# or set own #if one is left none if will be automaticaly calculated by area size
OUTER_PAPER_DIMENSIONS = (50000, None)
# what side of paper was set (smaller true bigger false)(only if only one side in custom dimension was set)
OUTER_GIVEN_SMALLER_PAPER_DIMENSION = True
# set how will resulted paper be oriented, AUTOMATIC is Recommended
OUTER_WANTED_ORIENTATION = MapOrientation.AUTOMATIC

# expand area
OUTER_FIT_PAPER_SIZE = False

# wanted_ways: WantedFeatures # where they vanish - already not on map - for mapycz styles
wanted_nodes: WantedCategories = {
     'place': {'city', 
               'town', # zoom 1
            #    'village',# zoom 3
            #    'suburb', # zoom 5
            #    'neighbourhood', # zoom 7
            #    'locality'
               }, # zoom 7
     
    'natural': {'peak'}, # zoom 1
    # 'man_made': {'tower'}, # zoom 7
    # 'historic': {'castle'}, # zoom 7
}

wanted_nodes_from_area: WantedCategories = {
    # 'man_made': {'tower'}, # zoom 7
    # 'historic': {'castle'}, # zoom 7
}



# todo automatic wanted objects setup using map and pdf ratio automatic_filters_creating_factor - own class ()


unwanted_nodes_tags: UnwantedTags = {

}

wanted_ways: WantedCategories = {
    # all
    # ways connected with links
    'highway': {
        'motorway', # zoom none
                 'trunk', # zoom none
                 'primary', # zoom none
                  'secondary', # zoom 2
                #  'tertiary', # zoom 3
                  'motorway_link',# zoom none - smaller only
                  'trunk_link',# zoom none - smaller only
                  'primary_link',# zoom none - smaller only
                  'secondary_link',# zoom 3
                #   'tertiary_link',# zoom 5
                #   'residential',# zoom 5 - same size as unclassified
                #   'unclassified',# zoom 5 - same size as residential
                #    'service',# zoom - 6
                  'pedestrian',# zoom 5 - same as residental 
                #    'cycleway',# zoom 6
                  'raceway',# zoom 3
                #   'steps', # zoom 6
                 #   'footway',# zoom 6
                #    'track', # zoom 6 (5)
                #    'path'
                },# zoom 6 (5)
    
    'railway': {'rail', # service - service smaller 6, 3 normal
                'light_rail', #- service smaller 6, 3 normal
                "monorail", #- service smaller 6, 3 normal
                'miniature',  #- service smaller 6, 3 normal
                # 'subway', # zoom 6
                'funicular', # zoom 4
                'tram'
                },# zoom 8
    'aeroway': {'runway',# zoom 3
                'taxiway'},# zoom 3
    
    'aerialway': {'cable_car',# zoom 4
                  'gondola',# zoom 4
                  'chair_lift',# zoom 4
                  'mixed_lift',# zoom 4
                  't-bar', # zoom 5 a ostatní
                  'j-bar', 
                  'platter',
                  'rope_tow',
                  'magic_carpet',
                  'zip_line',
                  'goods'
                  },
    
    # 'barrier': {'city_wall', # zoom 8
    #             'wall',  # zoom 8
    #             'cable_barrier'}, # zoom 8
    
    'waterway': {'river', # zoom never
                  'canal',  # zoom 4
                #   'stream', # zoom 4
                #   'drain', # zoom 6
                #   'ditch'
                 }, # zoom 6
    'route': {'ferry'}, # none


    'natural': {'coastline'},




    # 'highway': ['primary'],
    #    'highway': ['motorway', 'trunk','primary', 'secondary', 'tertiary'],
    # # 'highway': ['motorway', 'trunk', 'primary'],
    # 'highway': {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'path', 'footway'},
    # # # 'highway': {'tertiary'},
    # 'railway': {'rail', 'tram'},
    # 'natural': {'coastline'},
}


unwanted_ways_tags: UnwantedTags = {
    # 'highway':['coridor','via_ferrata','crossing','traffic_island','proposed','construction' ],
    'railway': {
        'service': ['yard', 'spur','crossover', 'siding'], # spur, siding
        # 'tunnel': ['building_passage'],
        # 'tunnel': [],
    },
    # 'waterway': ['stream']


    # {'railway':""}:{'service':['yard'],'tunnel': ['building_passage']}
}

wanted_areas: WantedCategories = {
    # all areas - osm can have more tags? how to do it
    'landuse': {'farmland', 'forest', 'residential', 'commercial', 'retail', 'industrial', 'allotments', 'retail',
                'meadow', 'grass', 'landfill', 'cemetery', 'vineyard', 'orchard', 'garages',
                'quarry', 'recreation_ground'},  # zoom never
    'leisure': {'park', 'pitch', 'garden', 'golf_course',
               'playground', 'stadium', 'swimming_pool', 'sports_centre'}, # zoom 2
    # # all water (except pools) is in natural
    'natural': {'wood', 'water', 'scrub', 'heath', 'grassland',
                'bay', 'beach', 'sand'}, # zoom never
    # občanské vybavení
    # parking zoom 6
    'amenity': {'motorcycle_parking', 'parking', 'grave_yard', 'school', 'university', 'college', 'kindergarten'
                'bus_station', 'hospital', 'clinic', 'place_of_worship'}, # zoom 2
    'boundary' : {'national_park'}, # zoom 1
    'building': set({}),  # zoom 2
    'aeroway': {'aerodrome'}, # zoom 5
    'highway': {'pedestrian', 'footway'}, # zoom 6
}

unwanted_areas_tags: UnwantedTags = {
}


# load
# ------------constants--------------
# world 3857
CRS_OSM = "EPSG:4326"
# mercato to all ploting and calc paper and map scaling factor of elements and special funcion for map scale
# map scaling factor of elements should be in same as map will be displayed to maintain same scale
CRS_CALC = "EPSG:3857"  # europe 25833 - calculating map scale and scaling factor
CRS_DISPLAY = "EPSG:3857"

# key, (types, required)
REQ_AREA_DICT_KEYS = {"area": (str | list, True), "plot": (bool, True), "category": (
    int | type(None), False), "width": (int | float | type(None), False)}
REQ_AREAS_MAPPING_DICT = {"width": Style.WIDTH.name}
try:
    FONT_AWESOME_PATH = "./common/fonts/FontAwesome6Free-Solid-900.otf"
    font_awesome_prop = fm.FontProperties(fname=FONT_AWESOME_PATH)
except:
    font_awesome_prop = None
    warnings.warn("Font awesome not found")
try:
    MATERIAL_DESIGN_OUTLINE_PATH = "./common/fonts/MaterialSymbolsRounded-VariableFont_FILL,GRAD,opsz,wght.ttf"
    material_design_prop = fm.FontProperties(fname=MATERIAL_DESIGN_OUTLINE_PATH)
except:
    material_design_prop = None
    warnings.warn("Material desing outline not found")


# --------------------------------------------------------------gpx settings--------------------------------------------------------------

# zooms: scaling values for center of each zoom level
# zoom level: scaling value
ZOOM_MAPPING: dict[int, float] = {
    10: 0.1967345,  # 17
    9: 0.0981350,  # 16
    8: 0.0490022,  # 15
    7: 0.0245145,  # 14
    6: 0.0122572,  # 13
    5: 0.0061528,  # 12
    4: 0.0030862,  # 11
    3: 0.0015295,  # 10
    2:  0.0007648,  # 9
    1:  0.0003824,  # 8
}


# markercode, font_prop, horizontalalignment, verticalalignment by icon
MARKERS_UCODE_MAPPING: dict[str, str] = {
    "FA_start": (MarkersCodes.TEST.value, font_awesome_prop),
    "MD_start": (MarkersCodes.TEST.value, material_design_prop),
    "start": MarkersCodes.TEST.value,
    # if not test in matplotlib markers or set valid from fe here
}

# this will come from FE:

GPX_FOLDER: str = '../gpxs/brno'
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
# only for columns in osm file
NODES_ADDITIONAL_COLUMNS = ['name', 'ele', 'population', 'tower:type', 'capital']
NODES_NUMERIC_COLUMNS = ['ele', 'population']
NODES_ROUND_COLUMNS = ['ele']



WAYS_ADDITIONAL_COLUMNS = ['bridge', 'layer', 'tunnel', 'historic', 
                           'surface', 'tracktype', 'service', 'intermittent', 'covered']
WAYS_NUMERIC_COLUMNS = []
WAYS_ROUND_COLUMNS = []

AREA_ADDITIONAL_COLUMNS = ['area', 'type', 'place']
AREA_NUMERIC_COLUMNS = []
AREA_ROUND_COLUMNS = []

DERIVATE_COLUMNS_NODES = [
    
    ({'place': ''}, Style.TEXT1.name, 'name', None),
    # try to set with filter in derivated columns
    ({'man_made': 'tower'}, Style.TEXT1.name, 'name', None),
    ({'natural': 'peak'}, Style.TEXT1.name, 'name', None),
    ({'historic': 'castle'}, Style.TEXT1.name, 'name', None),
    ({'natural': 'peak'}, Style.TEXT2.name, 'ele', None),
    
]

DERIVATE_COLUMNS_WAYS = []
DERIVATE_COLUMNS_AREAS = []

NODES_DONT_CATEGORIZE = [
    Style.TEXT1_POSITIONS.name, Style.TEXT2_POSITIONS.name]
WAYS_DONT_CATEGORIZE = []
AREAS_DONT_CATEGORIZE = []
