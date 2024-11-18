from enum import Enum

class StyleKey(Enum):
    COLOR = 1
    ALPHA = 2
    ZINDEX = 3
    LINEWIDTH = 4
    LINESTYLE = 5
    EDGE_COLOR = 7 # nastavit asi jako text outline width a color
    EDGE_WIDTH_RATIO = 11
    BRIDGE_COLOR = 9
    BRIDGE_WIDTH_RATIO = 12
    BRIDGE_EDGE_COLOR = 10
    FONT_SIZE = 6
    OUTLINE_WIDTH = 8
    ICON = 16
    ICON_COLOR = 13
    ICON_EDGE = 14
    ICON_SIZE = 15
    
    
class AreaBounds(Enum):
    NONE = 1
    COMBINED = 2
    SEPARATED = 3
    
class ExpandArea(Enum):
    NONE = 1
    FIT_PAPER_SIZE = 2
    CUSTOM_AREA = 3

class WorldSides(Enum):
    WEST = 'west'
    EAST = 'east'
    NORTH = 'north'
    SOUTH = 'south'
    
class PaperSize(Enum):
    A0 = (841, 1189)
    A1 = (594, 841)
    A2 = (420, 594)
    A3 = (297, 420)
    A4 = (210, 297)
    A5 = (148, 210)
    A6 = (105, 148)
    A7 = (74, 105)
    A8 = (52, 74)
        
    @property
    def dimensions(self) -> tuple[float, float]:
        return self.value  # Returns the dimensions (width, height)
    
class MapOrientation(Enum):
    AUTOMATIC = 1
    LANDSCAPE = 2
    PORTRAIT = 3