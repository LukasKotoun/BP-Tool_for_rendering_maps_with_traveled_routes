from enum import Enum

class StyleKey(Enum):
    COLOR = 1
    EDGE_COLOR = 2
    ZINDEX = 3
    LINEWIDTH = 4
    BGCOLOR = 5
    LINESTYLE = 6
    ALPHA = 7

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