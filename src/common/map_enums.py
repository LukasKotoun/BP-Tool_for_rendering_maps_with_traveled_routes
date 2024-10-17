from enum import Enum

class StyleKey(Enum):
    COLOR = 'color'
    ZINDEX = 'zindex'
    LINEWIDTH = 'linewidth'
    BGCOLOR = 'bg_color'
    LINESTYLE = 'linestyle'

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