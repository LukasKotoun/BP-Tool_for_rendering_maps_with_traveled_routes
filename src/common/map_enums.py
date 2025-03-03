from enum import Enum
from typing import Literal
class ColorMode(Enum):
    DEFAULT = "DEFAULT"
    SINGLE = "SINGLE"
    SHADE = "SHADE"
    PALETTE = "PALETTE"

class LineCupStyles(Enum):
    ROUND = "round"
    BUTT = "butt"
    PROJECTING = "projecting"

class MarkersCodes(Enum):
    TEST = "\u2713"

class MinPlot(Enum):  # minimum parts that node must have. If not whole node object is removed
    MARKER_TEXT1_TEXT2 = "MARKER_TEXT1_TEXT2"
    MARKER_TEXT1_OR_TEXT2 = "MARKER_TEXT1_OR_TEXT2"
    MARKER_TEXT1 = "MARKER_TEXT1"
    MARKER_TEXT2 = "MARKER_TEXT2"
    MARKER = "MARKER"
    TEXT1 = "TEXT1"
    TEXT2 = "TEXT2"
    TEXT1_TEXT2 = "TEXT1_TEXT2"

class MinLoad(Enum):  # minimum parts that node must have. If not whole node object is removed
    TEXT1 = "TEXT1"
    TEXT2 = "TEXT2"
    TEXT1_TEXT2 = "TEXT1_TEXT2"
    TEXT1_OR_TEXT2 = "TEXT1_OR_TEXT2"
    NONE = "NONE"

class TextPositions(Enum):  
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    
class MarkerAbove(Enum):
    ALL = "ALL"
    NORMAL = "NORMAL"
    NONE = "NONE"

class Style(Enum):
    # general
    COLOR = "COLOR"
    ALPHA = "ALPHA"
    ZINDEX = "ZINDEX"
    WIDTH = "WIDTH"
    EDGE_COLOR = "EDGE_COLOR"
    EDGE_ALPHA = "EDGE_ALPHA"
    EDGE_WIDTH_RATIO = "EDGE_WIDTH_RATIO"

    # lines
    LINESTYLE = "LINESTYLE"
    LINE_CAPSTYLE = "LINE_CAPSTYLE"
    EDGE_CAPSTYLE = "EDGE_CAPSTYLE"
    EDGE_LINESTYLE = "EDGE_LINESTYLE"
    PLOT_ON_BRIDGE = "PLOT_ON_BRIDGE"
    
    # bridges
    BRIDGE_COLOR = "BRIDGE_COLOR"
    BRIDGE_WIDTH_RATIO = "BRIDGE_WIDTH_RATIO"
    BRIDGE_EDGE_COLOR = "BRIDGE_EDGE_COLOR"
    BRIDGE_EDGE_WIDTH_RATIO = "BRIDGE_EDGE_WIDTH_RATIO"
    BRIDGE_LINESTYLE = "BRIDGE_LINESTYLE"
    BRIDGE_EDGE_LINESTYLE = "BRIDGE_EDGE_LINESTYLE"
    
    # markers 
    MARKER = "MARKER"
    MARKER_ABOVE_OTHERS = "MARKER_ABOVE_OTHERS"
    MARKER_FONT_PROPERTIES = "MARKER_FONT_PROPERTIES"
    MARKER_VERTICAL_ALIGN = "MARKER_VERTICAL_ALIGN"
    MARKER_HORIZONTAL_ALIGN = "MARKER_HORIZONTAL_ALIGN"
    # gpx - for 2 markers in gpx - used for mapping - same but only with prefix 
        #start
    START_MARKER = "START_MARKER"
    START_MARKER_WIDHT = "START_MARKER_WIDHT"
    START_MARKER_EDGE_RATIO = "START_MARKER_EDGE_RATIO"
    START_MARKER_COLOR = "START_MARKER_COLOR"
    START_MARKER_EDGE_COLOR = "START_MARKER_EDGE_COLOR"
    START_MARKER_ALPHA = "START_MARKER_ALPHA"
    START_MARKER_FONT_PROPERTIES = "START_MARKER_FONT_PROPERTIES"
    START_MARKER_VERTICAL_ALIGN = "START_MARKER_VERTICAL_ALIGN"
    START_MARKER_HORIZONTAL_ALIGN = "START_MARKER_HORIZONTAL_ALIGN"
    
        #finish
    FINISH_MARKER = "FINISH_MARKER"
    FINISH_MARKER_WIDHT = "FINISH_MARKER_WIDHT"
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
    
    TEXT1 = "TEXT1"
    TEXT2 = "TEXT2"
    # nodes annotation requirements
    TEXT1_POSITIONS = "TEXT1_POSITIONS"
    TEXT2_POSITIONS = "TEXT2_POSITIONS"
    
    # nodes annotation requirements for ploting 
    MIN_PLOT_REQ = "MIN_PLOT_REQ"
    # nodes min annotation requirements in loading
    MIN_LOAD_REQ = "MIN_LOAD_REQ"

    #scales
    FE_WIDTH_SCALE = "FE_WIDTH_SCALE" # lines and icons
    TEXT_FONT_SIZE_SCALE = "TEXT_FONT_SIZE_SCALE"
    FE_TEXT_FONT_SIZE_SCALE = "FE_TEXT_FONT_SIZE_SCALE" # text
    
    # calculated/derivated - cant be set by user
    # calculated like TEXT_FONT_SIZE * TEXT_OUTLINE_WIDTH_RATIO
    TEXT_OUTLINE_WIDTH = "TEXT_OUTLINE_WIDTH"
    # calculated like WIDTH * (1 + EDGE_WIDTH_RATIO)
    EDGE_WIDTH = "EDGE_WIDTH"
    # calculated like WIDTH * (1 + BRIDGE_WIDTH_RATIO)
    BRIDGE_WIDTH = "BRIDGE_WIDTH"
    # calculated like BRIDGE_WIDTH * (1 + BRIDGE_EDGE_WIDTH_RATIO)
    BRIDGE_EDGE_WIDTH = "BRIDGE_EDGE_WIDTH"
    # calculated like start START_MARKER_WIDHT * START_MARKER_EDGE_RATIO
    START_MARKER_EDGE_WIDTH = "START_MARKER_EDGE_WIDTH"
    # calculated like FINISH_MARKER_WIDHT * FINISH_MARKER_EDGE_RATIO
    FINISH_MARKER_EDGE_WIDTH = "FINISH_MARKER_EDGE_WIDTH"


class WorldSides(Enum):
    WEST = 'WEST'
    EAST = 'EAST'
    NORTH = 'NORTH'
    SOUTH = 'SOUTH'


class PaperSize(Enum):
    A0: tuple[Literal[841], Literal[1189]] = (841, 1189)
    A1: tuple[Literal[594], Literal[841]] = (594, 841)
    A2: tuple[Literal[420], Literal[594]] = (420, 594)
    A3: tuple[Literal[297], Literal[420]] = (297, 420)
    A4: tuple[Literal[210], Literal[297]] = (210, 297)
    A5: tuple[Literal[148], Literal[210]] = (148, 210)
    A6: tuple[Literal[105], Literal[148]] = (105, 148)
    A7: tuple[Literal[74], Literal[105]] = (74, 105)
    A8: tuple[Literal[52], Literal[74]] = (52, 74)

    @property
    def dimensions(self) -> tuple[float, float]:
        return self.value  # Returns the dimensions (width, height)


class MapOrientation(Enum):
    AUTOMATIC = "AUTOMATIC"
    LANDSCAPE = "LANDSCAPE"
    PORTRAIT = "PORTRAIT"