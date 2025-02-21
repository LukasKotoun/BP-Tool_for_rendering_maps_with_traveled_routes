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
    COLOR = 1
    ALPHA = 2
    ZINDEX = 3
    WIDTH = 4
    EDGE_COLOR = 6
    EDGE_ALPHA = 21
    EDGE_WIDTH_RATIO = 7
    WIDTH_SCALE = 30
    FE_WIDTH_SCALE = 31
    # lines
    LINESTYLE = 5
    LINE_CUP = 35
    EDGE_LINESTYLE = 8
    PLOT_ON_BRIDGE = 33
    EDGE_CUP = 34
    # bridges
    BRIDGE_COLOR = 9
    BRIDGE_WIDTH_RATIO = 10
    BRIDGE_EDGE_COLOR = 11
    BRIDGE_EDGE_WIDTH_RATIO = 12
    # markers
    ICON = 13
    MARKER_CHECK_OVERLAP = 88
    # gpx
    START_ICON = 54
    START_ICON_WIDHT = 59
    FINISH_ICON = 55
    FINISH_ICON_WIDHT = 56
    START_ICON_EDGE_RATIO = 57
    FINISH_ICON_EDGE_RATIO = 58
    # ? maybe add START_ICON_WIDHT, START_ICON_EDGE_RATIO, FINISH_ICON_WIDHT, FINISH_ICON_EDGE_RATIO, -> START_ICON_EDGE_WIDTH, FINISH_ICON_EDGE_WIDTH calculated

    # texts
    TEXT_FONT_SIZE = 14
    TEXT_FONT_SIZE_SCALE = 32
    FE_TEXT_FONT_SIZE_SCALE = 32
    TEXT_OUTLINE_WIDTH_RATIO = 16
    TEXT_COLOR = 74
    TEXT_OUTLINE_COLOR = 85
    TEXT_FONTFAMILY = 59
    TEXT_STYLE = 60
    TEXT_WEIGHT = 45
    TEXT1 = 61
    TEXT2 = 62
    TEXT1_POSITIONS = 68
    TEXT2_POSITIONS = 65
    TEXT1_WRAP_LEN = 99
    TEXT2_WRAP_LEN = 100
    # nodes 
    MIN_REQ_POINT = 63

    # calculated/derivated - cant be set by user
    # calculated like TEXT_FONT_SIZE * TEXT_OUTLINE_WIDTH_RATIO
    TEXT_OUTLINE_WIDTH = 17
    # calculated like WIDTH * (1 + EDGE_WIDTH_RATIO)
    EDGEWIDTH = 18
    # calculated like WIDTH * (1 + BRIDGE_WIDTH_RATIO)
    BRIDGE_WIDTH = 19
    # calculated like BRIDGE_WIDTH * (1 + BRIDGE_EDGE_WIDTH_RATIO)
    BRIDGE_EDGE_WIDTH = 20
    # calculated like start START_ICON_WIDHT * START_ICON_EDGE_RATIO
    START_ICON_EDGE_WIDTH = 60
    # calculated like FINISH_ICON_WIDHT * FINISH_ICON_EDGE_RATIO
    FINISH_ICON_EDGE_WIDTH = 61

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
