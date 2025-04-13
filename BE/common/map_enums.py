from enum import Enum
from typing import Literal

class ProcessingStatus(Enum):
    FAILED = "failed"
    STARTING = "starting"
    IN_QUEUE = "in_queue"
    EXTRACTING = "extracting"
    LOADING = "loading"
    FILTERING = "filtering"
    STYLING = "styling"
    PREPARING_FOR_PLOTTING = "preparing_for_plotting"
    AREAS_PLOTTING = "areas_plotting"
    WAYS_PLOTTING = "ways_plotting"
    NODES_PLOTTING = "nodes_plotting"
    GPXS_PLOTTING = "gpxs_plotting"
    FILE_SAVING = "file_saving"
    COMPLETED = "completed"

class SharedDictKeys(Enum):
    FILES = "files"
    STATUS = "status"
    PROCESS_RUNNING = "process_running"
    PID = "pid"
    IS_PREVIEW = "is_preview"
    USER_CHECK_INFO = "user_check_info"
    
class TaskQueueKeys(Enum):
    CONFIG = "config"
    QUEUE_TYPE = "queue_type"
    TASK_ID = "task_id"

class QueueType(Enum):
    NORMAL = "normal"
    PREVIEW = "preview"

class GpxColumns(Enum):
    FILE_NAME = "file_name"
    GROUP = "group"

class LineCupStyles(Enum):
    ROUND = "round"
    BUTT = "butt"
    PROJECTING = "projecting"

class MarkersCodes(Enum):
    FA_TOWER_OBSERVATION = "\ue586"
    #gpx
    FA_FINISH_ICON = '\uf11e'
    
    MU_CASTLE = "\ueaad"
    MPL_TRIANGLE = '^'
    #gpx
    MPL_CIRCLE_MARKER = 'o'

    
class MapConfigKeys(Enum):
    MAP_AREA = "map_area" 
    MAP_AREA_BOUNDARY = "map_area_boundary"
    MAP_OUTER_AREA = "map_outer_area"
    PEAKS_FILTER_RADIUS = "peaks_filter_radius" # 0 is for no filter
    MIN_PLACE_POPULATION = "min_place_population" # 0 is for no filter
    MAP_SCALING_FACTOR = "map_scaling_factor"
    PLOT_BRIDGES = "plot_bridges"
    PLOT_TUNNELS = "plot_tunnels"
    OSM_FILES = "osm_files" # checked
    PAPER_DIMENSION_MM = "paper_dimension_mm"
    WANTED_CATEGORIES_AND_STYLE_EDIT = "wanted_categires_and_style_edit" # 'nodes', 'nodes_from_area, 'ways', 'areas'
    UNWANTED_CATEGORIES = "unwanted_categories" # 'nodes', 'ways', 'areas'
    STYLES_ZOOM_LEVELS = "styles_zoom_levels" # 'nodes', 'ways', 'areas', 'general'
    MAP_THEME = "map_theme"
    GPXS = "gpxs"
    GPXS_STYLES = "gpxs_styles"
    PEAKS_FILTER_SENSITIVITY = "peaks_filter_sensitivity" # 0 is for no filter
    
    
class MinPlot(Enum):  # minimum parts that node must have. If not whole node object is removed
    MARKER_TEXT1_TEXT2 = "MARKER_TEXT1_TEXT2"
    MARKER_TEXT1_OR_TEXT2 = "MARKER_TEXT1_OR_TEXT2"
    MARKER_TEXT1 = "MARKER_TEXT1"
    MARKER_TEXT2 = "MARKER_TEXT2"
    MARKER = "MARKER"
    TEXT1 = "TEXT1"
    TEXT2 = "TEXT2"
    TEXT1_TEXT2 = "TEXT1_TEXT2"

class BaseConfigKeys(Enum):
    ADDITIONAL_COLUMNS = 'ADDITIONAL_COLUMNS'
    NUMERIC_COLUMNS = 'NUMERIC_COLUMNS'
    ROUND_COLUMNS = 'ROUND_COLUMNS'
    DERIVATE_COLUMNS = 'DERIVATE_COLUMNS'
    DONT_CATEGORIZE = 'DONT_CATEGORIZE'

class MapThemeVariable(Enum):
    WATER_COLOR = "WATER_COLOR"
    LAND_COLOR = "LAND_COLOR"
    AREAS_WITH_WAYS_FILTER = "AREAS_WITH_WAYS_FILTER"
    WAYS_WITHOUT_CROSSING_FILTER = "WAYS_WITHOUT_CROSSING_FILTER"
    GPXS_STYLES_SCALE = "GPXS_STYLES_SCALE"
    NODES_STYLES_SCALE = "NODES_STYLES_SCALE"
    WAYS_STYLES_SCALE = "WAYS_STYLES_SCALE"
    AREAS_STYLES_SCALE = "AREAS_STYLES_SCALE"
    TEXT_BB_EXPAND_PERCENT = "TEXT_BB_EXPAND_PERCENT"
    MARKER_BB_EXPAND_PERCENT = "MARKER_BB_EXPAND_PERCENT"
    TEXT_WRAP_NAMES_LENGTH = "TEXT_WRAP_NAMES_LENGTH"
    TEXT_BOUNDS_OVERFLOW_THRESHOLD = "TEXT_BOUNDS_OVERFLOW_THRESHOLD"

class TextPositions(Enum):  
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TOP_LEFT = "TOP_LEFT"
    TOP_RIGHT = "TOP_RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    
class MarkerPosition(Enum):
    ABOVE_ALL = "ABOVE_ALL"
    ABOVE_NORMAL = "ABOVE_NORMAL"
    NORMAL = "NORMAL"
    UNDER_TEXT_OVERLAP = "UNDER_TEXT_OVERLAP" # can be under text but also can be above/under normal markers, depends on the zindex (but will overlap)
    

class Style(Enum):
    # general
    COLOR = "COLOR"
    ALPHA = "ALPHA"
    ZINDEX = "ZINDEX"
    WIDTH = "WIDTH"
    EDGE_COLOR = "EDGE_COLOR"
    EDGE_ALPHA = "EDGE_ALPHA"
    EDGE_WIDTH_RATIO = "EDGE_WIDTH_RATIO"
    EDGE_WIDTH_DASHED_CONNECT_RATIO = "EDGE_WIDTH_DASHED_CONNECT_RATIO"
    # lines
    LINESTYLE = "LINESTYLE"
    LINE_CAPSTYLE = "LINE_CAPSTYLE"
    EDGE_CAPSTYLE = "EDGE_CAPSTYLE"
    EDGE_LINESTYLE = "EDGE_LINESTYLE"
    PLOT_ON_BRIDGE = "PLOT_ON_BRIDGE"
    PLOT_WITHOUT_CROSSING = "PLOT_WITHOUT_CROSSING"
    
    # bridges
    BRIDGE_COLOR = "BRIDGE_COLOR"
    BRIDGE_WIDTH_RATIO = "BRIDGE_WIDTH_RATIO"
    BRIDGE_EDGE_COLOR = "BRIDGE_EDGE_COLOR"
    BRIDGE_EDGE_WIDTH_RATIO = "BRIDGE_EDGE_WIDTH_RATIO"
    BRIDGE_LINESTYLE = "BRIDGE_LINESTYLE"
    BRIDGE_EDGE_LINESTYLE = "BRIDGE_EDGE_LINESTYLE"
    
    # markers
    MARKER = "MARKER"
    MARKER_LAYER_POSITION = "MARKER_LAYER_POSITION"
    MARKER_FONT_PROPERTIES = "MARKER_FONT_PROPERTIES"
    MARKER_VERTICAL_ALIGN = "MARKER_VERTICAL_ALIGN"
    MARKER_HORIZONTAL_ALIGN = "MARKER_HORIZONTAL_ALIGN"
    
    # gpx - for 2 markers in gpx - used for mapping - same but only with prefix 
    GPX_ABOVE_TEXT = "GPX_ABOVE_TEXT"
        #start
    START_MARKER = "START_MARKER"
    START_MARKER_WIDTH = "START_MARKER_WIDTH"
    START_MARKER_EDGE_RATIO = "START_MARKER_EDGE_RATIO"
    START_MARKER_COLOR = "START_MARKER_COLOR"
    START_MARKER_EDGE_COLOR = "START_MARKER_EDGE_COLOR"
    START_MARKER_ALPHA = "START_MARKER_ALPHA"
    START_MARKER_FONT_PROPERTIES = "START_MARKER_FONT_PROPERTIES"
    START_MARKER_VERTICAL_ALIGN = "START_MARKER_VERTICAL_ALIGN"
    START_MARKER_HORIZONTAL_ALIGN = "START_MARKER_HORIZONTAL_ALIGN"
    
        #finish
    FINISH_MARKER = "FINISH_MARKER"
    FINISH_MARKER_WIDTH = "FINISH_MARKER_WIDTH"
    FINISH_MARKER_EDGE_RATIO = "FINISH_MARKER_EDGE_RATIO"
    FINISH_MARKER_COLOR = "FINISH_MARKER_COLOR"
    FINISH_MARKER_EDGE_COLOR = "FINISH_MARKER_EDGE_COLOR"
    FINISH_MARKER_ALPHA = "FINISH_MARKER_ALPHA"
    FINISH_MARKER_FONT_PROPERTIES = "FINISH_MARKER_FONT_PROPERTIES"
    FINISH_MARKER_VERTICAL_ALIGN = "FINISH_MARKER_VERTICAL_ALIGN"
    FINISH_MARKER_HORIZONTAL_ALIGN = "FINISH_MARKER_HORIZONTAL_ALIGN"
    
    # texts
    TEXT_FONT_SIZE = "TEXT_FONT_SIZE"
    TEXT_OUTLINE_WIDTH_RATIO = "TEXT_OUTLINE_WIDTH_RATIO"
    TEXT_COLOR = "TEXT_COLOR"
    TEXT_OUTLINE_COLOR = "TEXT_OUTLINE_COLOR"
    TEXT_FONTFAMILY = "TEXT_FONTFAMILY"
    TEXT_STYLE = "TEXT_STYLE"
    TEXT_WEIGHT = "TEXT_WEIGHT"
    TEXT_WRAP_LEN = "TEXT_WRAP_LEN"
    TEXT_FONT_PROPERTIES = "TEXT_FONT_PROPERTIES"
    TEXT1 = "TEXT1"
    TEXT2 = "TEXT2"
    # nodes annotation requirements
    TEXT1_POSITIONS = "TEXT1_POSITIONS"
    TEXT2_POSITIONS = "TEXT2_POSITIONS"
    
    # nodes annotation requirements for ploting 
    MIN_PLOT_REQ = "MIN_PLOT_REQ"
    # nodes min annotation requirements in loading

    #scales
    FE_WIDTH_SCALE = "FE_WIDTH_SCALE" # lines and icons
    FE_TEXT_FONT_SIZE_SCALE = "FE_TEXT_FONT_SIZE_SCALE" # text
    
    # calculated/derivated - cant be set by user
    # calculated like TEXT_FONT_SIZE * TEXT_OUTLINE_WIDTH_RATIO
    TEXT_OUTLINE_WIDTH = "TEXT_OUTLINE_WIDTH"
    # calculated like WIDTH * (EDGE_WIDTH_RATIO)
    EDGE_WIDTH = "EDGE_WIDTH"
    # calculated like WIDTH * (EDGE_WIDTH_DASHED_CONNECT_RATIO)
    EDGE_WIDTH_DASHED_CONNECT = "EDGE_WIDTH_DASHED_CONNECT"
    # calculated like WIDTH * (BRIDGE_WIDTH_RATIO)
    BRIDGE_WIDTH = "BRIDGE_WIDTH"
    # calculated like BRIDGE_WIDTH * (BRIDGE_EDGE_WIDTH_RATIO)
    BRIDGE_EDGE_WIDTH = "BRIDGE_EDGE_WIDTH"
    # calculated like start Style.START_MARKER_WIDTH * START_MARKER_EDGE_RATIO
    START_MARKER_EDGE_WIDTH = "START_MARKER_EDGE_WIDTH"
    # calculated like Style.FINISH_MARKER_WIDTH * FINISH_MARKER_EDGE_RATIO
    FINISH_MARKER_EDGE_WIDTH = "FINISH_MARKER_EDGE_WIDTH"


class WorldSides(Enum):
    WEST = 'WEST'
    EAST = 'EAST'
    NORTH = 'NORTH'
    SOUTH = 'SOUTH'

class MapOrientation(Enum):
    AUTOMATIC = "automatic"
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"