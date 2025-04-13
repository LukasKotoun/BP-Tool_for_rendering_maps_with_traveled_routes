import warnings
import matplotlib.font_manager as fm
from matplotlib.colors import is_color_like
from dotenv import load_dotenv
import datetime
import os
from fastapi.security import OAuth2PasswordBearer

from common.map_enums import Style, MapOrientation, MarkersCodes, BaseConfigKeys, MarkerPosition
load_dotenv()

# --------------------------------------------------------------base server config - for changing by user--------------------------------------------------------------

#!! all files should be prefilted using shell script on folder or osm_filter_invalid_geoms.py on files one by one 
OSM_FILES_FOLDER = './osm_files/'

# folder where to store tmp files used in generating
OSM_TMP_FILE_FOLDER = './tmp/'

# folder where to store final generated files before sending to user
OUTPUT_PDF_FOLDER: str = './pdfs/'

# number of max concurrent tasks
#min is 1
MAX_CONCURRENT_TASKS_NORMAL = 2
MAX_CONCURRENT_TASKS_PREVIEW = 3

# number of tasks in queues
#min is 1 
MAX_QUEUE_SIZE_NORMAL = 10
MAX_QUEUE_SIZE_PREVIEW = 10

# allowed requests from which origins/domains (* is all) - change to frontend url from env
ALLOWED_ORIGINS = os.getenv("FRONTEND_URL", "*").split(",")

# --------------------------------------------------------------advance server config--------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev_key")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
FILE_DOWNLOAD_CHUNK_SIZE  = 1024 * 1024 # 1MB
JWT_EXPIRATION_TIME = datetime.timedelta(days=2)
USER_ASKED_DELAY_SEC = 30
JWT_ALGORITHM = "HS256"

# --------------------------------------------------------------map config--------------------------------------------------------------

PLACES_TO_FILTER_BY_POPULATION = ['city', 'town', 'village']
# --------------------------------------------------------------preview--------------------------------------------------------------

ALLOWED_WANTED_ELEMENTS_STRUCTURE = {
    'nodes': {
        'place': ['city', 'town', 'village', 'suburb', 'neighbourhood', 'locality'],
        'natural': ['peak'],
        'man_made': ['tower'],
        'historic': ['castle'],
    },
    'ways': {
        'highway': ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'residential', 'unclassified', 'service',
                    'pedestrian', 'cycleway', 'raceway', 'steps', 'footway', 'track', 'path'],
        'railway': ['rail', 'light_rail', "monorail", 'miniature', 'subway', 'funicular'],
        'aeroway': ['runway', 'taxiway'],
        'aerialway': ['cable_car', 'gondola', 'chair_lift', 'mixed_lift', 't-bar', 'j-bar', 'platter', 'rope_tow', 'magic_carpet', 'zip_line', 'goods'],
        'barrier': ['city_wall', 'wall', 'cable_barrier'],
        'waterway': ['river', 'canal', 'stream', 'drain', 'ditch'],
        'route': ['ferry'],
    },
    'areas': {
        'landuse': ['farmland', 'forest', 'residential', 'commercial', 'retail', 'industrial', 'allotments', 'meadow',
                    'grass', 'landfill', 'cemetery', 'vineyard', 'orchard', 'garages', 'quarry', 'recreation_ground'],
        'leisure': ['park', 'garden', 'pitch', 'golf_course', 'playground', 'sports_centre', 'swimming_pool'],
        'natural': ['wood', 'water', 'scrub', 'heath', 'grassland', 'beach', 'sand'],
        'amenity': ['motorcycle_parking', 'parking', 'grave_yard', 'school', 'university', 'college', 'kindergarten', 'bus_station', 'hospital', 'clinic', 'place_of_worship'],
        'boundary': ['national_park'],
        'building': True,
        'aeroway': ['aerodrome'],
        'highway': ['pedestrian', 'footway'],

    }
}

NODES_ALSO_FROM_AREA = {
    'man_made': ['tower'],
    'historic': ['castle'],
}
MANDATORY_WAYS = {
    'natural': {'coastline'}
}


CRS_OSM = "EPSG:4326"  # WGS84 - World Geodetic System 1984 - unit - degrees
CRS_DISPLAY = "EPSG:3857"  # WGS 84 / Pseudo-Mercator - unit - meters
try:
    font_paths = fm.findSystemFonts(
        fontpaths='./common/fonts/texts', fontext='ttf')
    for font_path in font_paths:
        fm.fontManager.addfont(font_path)
except:
    warnings.warn("Font paths not found")
try:
    FONT_AWESOME_PATH = "./common/fonts/markers/FontAwesome6Free-Solid-900.otf"
    font_awesome_prop = fm.FontProperties(fname=FONT_AWESOME_PATH)
except:
    font_awesome_prop = None
    warnings.warn("Font awesome not found")
try:
    MATERIAL_DESIGN_OUTLINE_PATH = "./common/fonts/markers/MaterialSymbolsRounded-VariableFont_FILL,GRAD,opsz,wght.ttf"
    material_design_prop = fm.FontProperties(
        fname=MATERIAL_DESIGN_OUTLINE_PATH)
except:
    material_design_prop = None
    warnings.warn("Material desing outline not found")

# mapping tuple - new key, new value (function), bool - extract - as new keys are added to dict
MARKERS_UCODE_MAPPING: dict[str, str] = {
    "finish": {Style.FINISH_MARKER.value: MarkersCodes.FA_FINISH_ICON.value, 
                  Style.FINISH_MARKER_FONT_PROPERTIES.value: font_awesome_prop, 
                  Style.FINISH_MARKER_VERTICAL_ALIGN.value: 'bottom',
                  Style.FINISH_MARKER_HORIZONTAL_ALIGN.value: 'left'},
    
    "start": {Style.START_MARKER.value: MarkersCodes.MPL_CIRCLE_MARKER.value, 
                  Style.START_MARKER_FONT_PROPERTIES.value: None,
                  Style.START_MARKER_VERTICAL_ALIGN.value: None,
                  Style.START_MARKER_HORIZONTAL_ALIGN.value: None}
}
# --------------------------------------------------------------API validation config--------------------------------------------------------------

GPX_NORMAL_STYLE_KEYS = ['file_name', 'group']
GPX_GENERAL_STYLE_KEYS = ['general']

ALLOWED_WANTED_PAPER_ORIENTATIONS = [MapOrientation.AUTOMATIC.value, MapOrientation.LANDSCAPE.value, MapOrientation.PORTRAIT.value]
MIN_WIDTH_POINTS = 0.1
MIN_TEXT_WIDTH = 0.1
MM_TO_INCH = 25.4
MATPLOTLIB_POINTS_PER_INCH = 72

FUNC_MM_TO_POINTS_CONVERSION = lambda v: max(v / MM_TO_INCH * MATPLOTLIB_POINTS_PER_INCH, MIN_WIDTH_POINTS)
ALPHA_CLAMP_VALUE = lambda v: min(1, max(v, 0))
ICON_EDGE_RATIO_MAPPING = lambda v: max(v, 0)
EDGE_RATIO_MAPPING = lambda v: max(v + 1, 0)
ZOOM_LEVEL_CLAMP_VALUE = lambda v: min(10, max(v, 1))

# is validated and not mapped
FIT_PAPER_VALIDATION = {"fit": (bool, True), "plot": (bool, True),
                        "width": (int | float, False)}
# requred area settings
REQ_AREA_KEY_WITH_AREA = "area"
REQ_AREA_KEY_WITH_BOOLEAN_PLOT = "plot"
REQ_AREA_KEY_TO_GROUP_BY = "group"

# key, (types, required) - area can be string or list of lists with cordinates x,y (lon, lat)
REQ_AREA_DICT_KEYS = {"area": (str | list, True), "plot": (bool, True), "group": (
    int, False), "width": (int | float, False)}
REQ_AREAS_MAPPING_DICT = {"width": (Style.WIDTH.value, FUNC_MM_TO_POINTS_CONVERSION),
                          "group":("group", lambda v: max(v, 0))}


FE_EDIT_STYLES_VALIDATION = {'width_scale': (float | int, False),
                             "text_scale": (float | int, False)}
FE_EDIT_STYLES_MAPPING = {"width_scale": (Style.FE_WIDTH_SCALE.value, lambda v: max(v, 0)),
                          "text_scale": (Style.FE_TEXT_FONT_SIZE_SCALE.value, lambda v: max(v, 0))}


ZOOM_STYLE_LEVELS_VALIDATION = {"nodes": (int, True), "ways": (
    int, True), "areas": (int, True), "general": (int, True)}

ZOOM_STYLE_LEVELS_MAPPING = {"nodes": ("nodes", ZOOM_LEVEL_CLAMP_VALUE ), "ways": (
    "ways", ZOOM_LEVEL_CLAMP_VALUE), "areas": ("areas", ZOOM_LEVEL_CLAMP_VALUE), "general": ("general", ZOOM_LEVEL_CLAMP_VALUE)}


GPX_STYLES_VALIDATION = {
    "color": (str, False, lambda v: is_color_like(v)),
    "width": (int | float, False),
    "alpha": (float|int, False),
    "zindex": (int, False),
    "linestyle": (str, False, lambda v: v in ['-', '--', '- -']),
    "line_capstyle": (str, False, lambda v: v in ['round', 'butt', 'projecting']),
    "edge_alpha": (float|int, False),
    "edge_color": (str, False, lambda v: is_color_like(v)),
    "edge_width_ratio": (float|int, False),
    "edge_linestyle": (str, False, lambda v: v in ['-', '--', '- -']),
    "edge_capstyle": (str, False, lambda v: v in ['round', 'butt', 'projecting']),
    "gpx_above_text": (bool, False),
    "start_marker": (str, False, lambda v: v in MARKERS_UCODE_MAPPING.keys()),
    "start_marker_width": (int|float, False),
    "start_marker_edge_ratio": (int|float, False),
    "start_marker_color": (str, False, lambda v: is_color_like(v)),
    "start_marker_edge_color": (str, False, lambda v: is_color_like(v)),
    "start_marker_alpha": (int|float, False),
    "finish_marker": (str, False, lambda v: v in MARKERS_UCODE_MAPPING.keys()),
    "finish_marker_width": (int|float, False, None),
    "finish_marker_edge_ratio": (int|float, False),
    "finish_marker_color": (str, False, lambda v: is_color_like(v)),
    "finish_marker_edge_color": (str, False, lambda v: is_color_like(v)),
    "finish_marker_alpha": (int|float, False),
    "marker_layer_position": (str, False, lambda v: v in ['above_text', 'under_text']),
}

GPX_STYLES_MAPPING = {
    'color': (Style.COLOR.value, None),
    "width": (Style.WIDTH.value, FUNC_MM_TO_POINTS_CONVERSION),
    "alpha": (Style.ALPHA.value, ALPHA_CLAMP_VALUE),
    "zindex": (Style.ZINDEX.value, None),
    "linestyle": (Style.LINESTYLE.value, lambda v: (0, (5, 5)) if v == '- -' else v),
    "line_capstyle": (Style.LINE_CAPSTYLE.value, None),
    "edge_alpha": (Style.EDGE_ALPHA.value, ALPHA_CLAMP_VALUE),
    "edge_color": (Style.EDGE_COLOR.value, None),
    "edge_width_ratio": (Style.EDGE_WIDTH_RATIO.value, EDGE_RATIO_MAPPING),
    "edge_linestyle": (Style.EDGE_LINESTYLE.value, lambda v: (0, (5, 5)) if v == '- -' else v),
    "edge_capstyle": (Style.EDGE_CAPSTYLE.value, None),
    "gpx_above_text": (Style.GPX_ABOVE_TEXT.value, None),
    "start_marker": (None, lambda v: MARKERS_UCODE_MAPPING[v] if v is not None else {}, True),
    "start_marker_width": (Style.START_MARKER_WIDTH.value, FUNC_MM_TO_POINTS_CONVERSION),
    "start_marker_edge_ratio": (Style.START_MARKER_EDGE_RATIO.value, ICON_EDGE_RATIO_MAPPING),
    "start_marker_color": (Style.START_MARKER_COLOR.value, None),
    "start_marker_edge_color": (Style.START_MARKER_EDGE_COLOR.value, None),
    "start_marker_alpha": (Style.START_MARKER_ALPHA.value, ALPHA_CLAMP_VALUE),
    "finish_marker": (None, lambda v: MARKERS_UCODE_MAPPING[v] if v is not None else {}, True),
    "finish_marker_width": (Style.FINISH_MARKER_WIDTH.value, FUNC_MM_TO_POINTS_CONVERSION),
    "finish_marker_edge_ratio": (Style.FINISH_MARKER_EDGE_RATIO.value, ICON_EDGE_RATIO_MAPPING),
    "finish_marker_color": (Style.FINISH_MARKER_COLOR.value, None),
    "finish_marker_edge_color": (Style.FINISH_MARKER_EDGE_COLOR.value, None),
    "finish_marker_alpha": (Style.FINISH_MARKER_ALPHA.value, ALPHA_CLAMP_VALUE),
    "marker_layer_position": (Style.MARKER_LAYER_POSITION.value, lambda v: MarkerPosition.UNDER_TEXT_OVERLAP.value if v == 'under_text' else MarkerPosition.ABOVE_ALL.value),
}


# --------------------------------------------------------------styles and loading data config--------------------------------------------------------------

BASE_OSM_CONFIG = {
    'nodes': {
        BaseConfigKeys.ADDITIONAL_COLUMNS: ['name', 'ele', 'population', 'tower:type', 'capital'],
        BaseConfigKeys.NUMERIC_COLUMNS: ['ele', 'population'],
        BaseConfigKeys.ROUND_COLUMNS: ['ele'],
        BaseConfigKeys.DERIVATE_COLUMNS: [
            ({'place': ''}, Style.TEXT1.value, 'name', None),
            ({'man_made': 'tower'}, Style.TEXT1.value, 'name', None),
            ({'natural': 'peak'}, Style.TEXT1.value, 'name', None),
            ({'historic': 'castle'}, Style.TEXT1.value, 'name', None),
            ({'natural': 'peak'}, Style.TEXT2.value, 'ele', None),
        ],
        BaseConfigKeys.DONT_CATEGORIZE: [
            Style.TEXT1_POSITIONS.value, Style.TEXT2_POSITIONS.value, Style.TEXT_FONTFAMILY.value
        ],
    },

    'ways': {
        BaseConfigKeys.ADDITIONAL_COLUMNS: ['name', 'layer', 'bridge', 'tunnel', 'historic',
                                            'surface', 'tracktype', 'service', 'intermittent', 'covered'],
        BaseConfigKeys.NUMERIC_COLUMNS: [],
        BaseConfigKeys.ROUND_COLUMNS: [],

        BaseConfigKeys.DERIVATE_COLUMNS: [],
        BaseConfigKeys.DONT_CATEGORIZE: [],
    },

    'areas': {
        BaseConfigKeys.ADDITIONAL_COLUMNS: ['area', 'place'],
        BaseConfigKeys.NUMERIC_COLUMNS: [],
        BaseConfigKeys.ROUND_COLUMNS: [],

        BaseConfigKeys.DERIVATE_COLUMNS: [],
        BaseConfigKeys.DONT_CATEGORIZE: [],
    }
}

# where to switch to more detailed zoom level
ZOOM_LEVEL_THRESHOLD = 0.1
# zoom level: scaling value
ZOOM_MAPPING: dict[int, float] = {
    10: 0.1967345,
    9: 0.0981350,
    8: 0.0490022,
    7: 0.0245145,
    6: 0.0122572,
    5: 0.0061528,
    4: 0.0030862,
    3: 0.0015295,
    2: 0.0007648,
    1: 0.0003824,
}

# fmt: off
from styles.mapycz_style import MAPYCZ_STYLE, MAPYCZ_BASE_OSM_CONFIG

STYLES = {
    "mapycz": (MAPYCZ_STYLE, MAPYCZ_BASE_OSM_CONFIG),
}
DEFAULT_STYLE = (MAPYCZ_STYLE, MAPYCZ_BASE_OSM_CONFIG)

