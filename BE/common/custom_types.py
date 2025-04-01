from typing import NamedTuple, Optional
from collections import namedtuple

from common.map_enums import WorldSides, Style, TextPositions, MinPlot, MarkerPosition

BoundsDict = dict[WorldSides, float]
DimensionsTuple = tuple[float, float]
Point = tuple[float, float]


WantedAreas = list[dict[str, bool | int | list[list[float]|Point] | str]]
OptDimensionsTuple = tuple[float | None, float | None]
WantedCategories = dict[str, set[str]]
FeatureStyles = dict[Style, str | int | float]
FeaturesCategoryStyle = dict[str, FeatureStyles]
FeaturesCategoriesStyles = dict[str,
                                tuple[FeaturesCategoryStyle, FeatureStyles]]

FeatureStyleZooms = dict[str, FeatureStyles]
CategoryFilters = list[tuple[str, str]]
FeatureCategoriesStyles = tuple[CategoryFilters, FeatureStyles]


Styles = dict[Style, str | int | float]
StyleZooms = dict[str, Styles]
RowsConditionsAND = dict[str, str | list[str] | tuple[str]]
RowsConditions = list[RowsConditionsAND]
ElementStyles = tuple[RowsConditions | RowsConditionsAND, Styles]
ElementStylesDynamic = tuple[RowsConditions | RowsConditionsAND, Styles, StyleZooms | None]

class TextRow(NamedTuple):
    geometry: Point           
    TEXT_COLOR: str
    TEXT_FONT_SIZE: float
    TEXT_FONTFAMILY: str
    TEXT_STYLE: str
    TEXT_WEIGHT: str
    TEXT_OUTLINE_WIDTH: float
    TEXT_OUTLINE_COLOR: str
    ALPHA: float
    EDGE_ALPHA: float
    TEXT_FONT_PROPERTIES: Optional[any] = None


class MarkerRow(NamedTuple):
    geometry: Point           
    MARKER: any
    COLOR: float
    WIDTH: str
    ALPHA: str
    EDGE_WIDTH: str
    EDGE_COLOR: str
    MARKER_VERTICAL_ALIGN: Optional[str] = 'center'
    MARKER_HORIZONTAL_ALIGN: Optional[str] = 'center'
    MARKER_FONT_PROPERTIES: Optional[any] = None

class MarkerOneAnotationRow(NamedTuple):
    # text and marker
    geometry: Point   
    ALPHA: str
       
    # text
    TEXT_COLOR: str
    TEXT_FONT_SIZE: float
    TEXT_FONTFAMILY: str
    TEXT_STYLE: str
    TEXT_WEIGHT: str
    TEXT_OUTLINE_WIDTH: float
    TEXT_OUTLINE_COLOR: str
    EDGE_ALPHA: float
    MIN_PLOT_REQ: MinPlot
    
    # marker
    MARKER: any
    COLOR: float
    WIDTH: str
    EDGE_WIDTH: str
    EDGE_COLOR: str
    
    # marker optional
    MARKER_VERTICAL_ALIGN: Optional[str] = 'center'
    MARKER_HORIZONTAL_ALIGN: Optional[str] = 'center'
    MARKER_LAYER_POSITION: Optional[MarkerPosition] = MarkerPosition.NORMAL
    MARKER_FONT_PROPERTIES: Optional[any] = None
    
    
    # text optional
    TEXT1_POSITIONS: Optional[list[TextPositions]] = []
    TEXT2_POSITIONS: Optional[list[TextPositions]] = []
    TEXT1: Optional[str] = None
    TEXT2: Optional[str] = None
    TEXT_FONT_PROPERTIES: Optional[any] = None

    
class MarkerTwoAnotationRow(NamedTuple):
    # text and marker
    geometry: Point   
    ALPHA: float   
         
    # text
    TEXT_COLOR: str
    TEXT_FONT_SIZE: float
    TEXT_FONTFAMILY: str
    TEXT_STYLE: str
    TEXT_WEIGHT: str
    TEXT_OUTLINE_WIDTH: float
    TEXT_OUTLINE_COLOR: str
    
    EDGE_ALPHA: float
    MIN_PLOT_REQ: MinPlot
    TEXT1_POSITIONS: list[TextPositions]
    TEXT2_POSITIONS: list[TextPositions]
    TEXT1: str
    TEXT2: str
    
    # marker
    MARKER: any
    COLOR: float
    WIDTH: str
    EDGE_WIDTH: str
    EDGE_COLOR: str
    
    # marker optional
    MARKER_VERTICAL_ALIGN: Optional[str] = 'center'
    MARKER_HORIZONTAL_ALIGN: Optional[str] = 'center'
    MARKER_LAYER_POSITION: Optional[MarkerPosition] = MarkerPosition.NORMAL
    MARKER_FONT_PROPERTIES: Optional[any] = None
    TEXT_FONT_PROPERTIES: Optional[any] = None
