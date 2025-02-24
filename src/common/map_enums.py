from enum import Enum
from typing import Literal


class ColorMode(Enum):
    DEFAULT = 1
    SINGLE = 2
    SHADE = 3
    PALETTE = 4


class BboxCheckSettings(Enum):
    NONE = 1
    TEXT = 2
    MARKER = 3
    ALL = 4

# what part of point with text can be removed without removing whole object (marker and texts)
# na začátku jeden velký filtr tohoto v jednom gdf, a nechat jen ty co sedí: např {removable_part: RemovablePart.NOTHING, ikona, text1, }
# mohl bych dát jeden dict do settings který by prošel data nastavil správně sloupce - tedy text1 a text2 by vlastně zkopíroval vždy podle filtru
# [({filter}, nový sloupce, původní sloupce)
# [({filter}, text1, name) - pro všechny nodes
# [({filter}, text2, ele) - pro některé
# a pak filtr podle removable_part nebo přejmenovat minimum


class MinParts(Enum):  # minimum parts that must node have. If not whole node object is removed
    MARKER_TEXT1_TEXT2 = 1
    MARKER_TEXT1 = 6
    MARKER_TEXT2 = 7
    MARKER = 2
    TEXT1 = 3
    TEXT2 = 4
    TEXT1_TEXT2 = 5

class TextPositions(Enum):  # minimum parts that must node have. If not whole node object is removed
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4


class StyleKey(Enum):
    # general
    COLOR = "COLOR"
    ALPHA = "ALPHA"
    ZINDEX = "ZINDEX"
    WIDTH = "WIDTH"
    EDGE_COLOR = "EDGE_COLOR"
    EDGE_ALPHA = "EDGE_ALPHA"
    EDGE_WIDTH_RATIO = "EDGE_WIDTH_RATIO"
    WIDTH_SCALE = "WIDTH_SCALE"
    FE_WIDTH_SCALE = "FE_WIDTH_SCALE"
    # lines
    LINESTYLE = "LINESTYLE"
    LINE_CUP = "LINE_CUP"
    EDGE_LINESTYLE = "EDGE_LINESTYLE"
    PLOT_ON_BRIDGE = "PLOT_ON_BRIDGE"
    EDGE_CUP = "EDGE_CUP"
    # bridges
    BRIDGE_COLOR = "BRIDGE_COLOR"
    BRIDGE_WIDTH_RATIO = "BRIDGE_WIDTH_RATIO"
    BRIDGE_EDGE_COLOR = "BRIDGE_EDGE_COLOR"
    BRIDGE_EDGE_WIDTH_RATIO = "BRIDGE_EDGE_WIDTH_RATIO"
    # markers
    ICON = "ICON"
    MARKER_CHECK_OVERLAP = "MARKER_CHECK_OVERLAP"
    
    # gpx
    START_ICON = "START_ICON"
    START_ICON_WIDHT = "START_ICON_WIDHT"
    START_ICON_EDGE_RATIO = "START_ICON_EDGE_RATIO"
    START_ICON_COLOR = "START_ICON_COLOR"
    START_ICON_EDGE_COLOR = "START_ICON_EDGE_COLOR"
    START_ICON_ALPHA = "START_ICON_ALPHA"
    FINISH_ICON = "FINISH_ICON"
    FINISH_ICON_WIDHT = "FINISH_ICON_WIDHT"
    FINISH_ICON_EDGE_RATIO = "FINISH_ICON_EDGE_RATIO"
    FINISH_ICON_COLOR = "FINISH_ICON_COLOR"
    FINISH_ICON_EDGE_COLOR = "FINISH_ICON_EDGE_COLOR"
    FINISH_ICON_ALPHA = "FINISH_ICON_ALPHA"
    
    # texts
    TEXT_FONT_SIZE = "TEXT_FONT_SIZE"
    TEXT_FONT_SIZE_SCALE = "TEXT_FONT_SIZE_SCALE"
    FE_TEXT_FONT_SIZE_SCALE = "FE_TEXT_FONT_SIZE_SCALE"
    TEXT_OUTLINE_WIDTH_RATIO = "TEXT_OUTLINE_WIDTH_RATIO"
    TEXT_COLOR = "TEXT_COLOR"
    TEXT_OUTLINE_COLOR = "TEXT_OUTLINE_COLOR"
    TEXT_FONTFAMILY = "TEXT_FONTFAMILY"
    TEXT_STYLE = "TEXT_STYLE"
    TEXT_WEIGHT = "TEXT_WEIGHT"
    TEXT1 = "TEXT1"
    TEXT2 = "TEXT2"
    TEXT1_POSITIONS = "TEXT1_POSITIONS"
    TEXT2_POSITIONS = "TEXT2_POSITIONS"
    TEXT1_WRAP_LEN = "TEXT1_WRAP_LEN"
    TEXT2_WRAP_LEN = "TEXT2_WRAP_LEN"
    # nodes 
    MIN_REQ_POINT = "MIN_REQ_POINT"

    # calculated/derivated - cant be set by user
    # calculated like TEXT_FONT_SIZE * TEXT_OUTLINE_WIDTH_RATIO
    TEXT_OUTLINE_WIDTH = "TEXT_OUTLINE_WIDTH"
    # calculated like WIDTH * (1 + EDGE_WIDTH_RATIO)
    EDGEWIDTH = "EDGEWIDTH"
    # calculated like WIDTH * (1 + BRIDGE_WIDTH_RATIO)
    BRIDGE_WIDTH = "BRIDGE_WIDTH"
    # calculated like BRIDGE_WIDTH * (1 + BRIDGE_EDGE_WIDTH_RATIO)
    BRIDGE_EDGE_WIDTH = "BRIDGE_EDGE_WIDTH"
    # calculated like start START_ICON_WIDHT * START_ICON_EDGE_RATIO
    START_ICON_EDGEWIDTH = "START_ICON_EDGEWIDTH"
    # calculated like FINISH_ICON_WIDHT * FINISH_ICON_EDGE_RATIO
    FINISH_ICON_EDGEWIDTH = "FINISH_ICON_EDGEWIDTH"


class StyleType(Enum):
    DEFAULT = 1
    ZOOM = 2


class AreaBounds(Enum):
    NONE = 1
    COMBINED = 2
    SEPARATED = 3


class WorldSides(Enum):
    WEST = 'west'
    EAST = 'east'
    NORTH = 'north'
    SOUTH = 'south'


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
    AUTOMATIC = 1
    LANDSCAPE = 2
    PORTRAIT = 3
