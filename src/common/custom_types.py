from common.map_enums import WorldSides, Style, TextPositions, MinParts
from typing import NamedTuple, Optional
from collections import namedtuple

BoundsDict = dict[WorldSides, float]
DimensionsTuple = tuple[float, float]
Point = tuple[float, float]
WantedArea = str | list[Point] | list[str | list[Point]]


WantedAreas = list[dict[str, bool | int | list[list[float]|Point] | str]]
OptDimensionsTuple = tuple[float | None, float | None]
WantedCategories = dict[str, set[str]]
UnwantedTags = dict[str, any]
FeatureStyles = dict[Style, str | int | float]
FeaturesCategoryStyle = dict[str, FeatureStyles]
FeaturesCategoriesStyles = dict[str,
                                tuple[FeaturesCategoryStyle, FeatureStyles]]

FeatureStyleZooms = dict[str, FeatureStyles]
CategoryFilters = list[tuple[str, str]]
FeatureCategoriesStyles = tuple[CategoryFilters, FeatureStyles]


Styles = dict[Style, str | int | float]
StyleZooms = dict[str, Styles]
RowsConditionsAND = dict[str, str | list[str]]
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

class MarkerRow(NamedTuple):
    geometry: Point           
    MARKER: any
    COLOR: float
    WIDTH: str
    ALPHA: str
    EDGEWIDTH: str
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
    MIN_REQ_POINT: MinParts
    
    # marker
    MARKER: any
    COLOR: float
    WIDTH: str
    EDGEWIDTH: str
    EDGE_COLOR: str
    
    # marker optional
    MARKER_VERTICAL_ALIGN: Optional[str] = 'center'
    MARKER_HORIZONTAL_ALIGN: Optional[str] = 'center'
    MARKER_CHECK_OVERLAP: Optional[bool] = True
    MARKER_FONT_PROPERTIES: Optional[any] = None
    
    # text optional
    TEXT1_POSITIONS: Optional[list[TextPositions]] = []
    TEXT2_POSITIONS: Optional[list[TextPositions]] = []
    TEXT1: Optional[str] = None
    TEXT2: Optional[str] = None
    
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
    MIN_REQ_POINT: MinParts
    TEXT1_POSITIONS: list[TextPositions]
    TEXT2_POSITIONS: list[TextPositions]
    TEXT1: str
    TEXT2: str
    
    # marker
    MARKER: any
    COLOR: float
    WIDTH: str
    EDGEWIDTH: str
    EDGE_COLOR: str
    
    # marker optional
    MARKER_VERTICAL_ALIGN: Optional[str] = 'center'
    MARKER_HORIZONTAL_ALIGN: Optional[str] = 'center'
    MARKER_CHECK_OVERLAP: Optional[bool] = True
    MARKER_FONT_PROPERTIES: Optional[any] = None