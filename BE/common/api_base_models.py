"""
API models for map generator endpoints.
Author: Lukáš Kotoun, xkotou08
"""
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from common.map_enums import MapOrientation


class ZoomLevelsModel(BaseModel):
    nodes: int
    ways: int
    areas: int
    general: int


class FitPaperSizeModel(BaseModel):
    fit: Optional[bool] = False
    plot: Optional[bool] = False
    width: Optional[float | int] = None


class PaperDimensionsModel(BaseModel):
    width: float | int | None
    height: float | int | None


class MapGeneratorConfigModel(BaseModel):
    map_area: Any
    paper_dimensions: PaperDimensionsModel
    map_preview_area: Optional[Any] = None
    paper_preview_dimensions: Optional[PaperDimensionsModel] = None
    fit_paper_size: FitPaperSizeModel
    osm_files: List[str]
    min_place_population: Optional[int | float] = None
    peaks_filter_sensitivity: Optional[int | float] = None
    map_theme: Optional[str] = ""
    plot_bridges: Optional[bool] = True
    plot_tunnels: Optional[bool] = True
    wanted_categories_and_styles_edit: Any
    styles_zoom_levels: ZoomLevelsModel
    gpxs_groups: Optional[Dict[str, list[str]]] = {}
    gpxs_styles: Optional[Any] = {}


class MapGeneratorPreviewConfigModel(BaseModel):
    osm_files: List[str]
    map_area: Any
    paper_dimensions: PaperDimensionsModel
    map_preview_area: Optional[Any] = None
    paper_preview_dimensions: PaperDimensionsModel
    fit_paper_size: FitPaperSizeModel

    min_place_population: Optional[int | float] = None
    peaks_filter_sensitivity: Optional[int | float] = None
    map_theme: Optional[str] = ""
    plot_bridges: Optional[bool] = True
    plot_tunnels: Optional[bool] = True
    wanted_categories_and_styles_edit: Any
    styles_zoom_levels: ZoomLevelsModel
    gpxs_groups: Optional[Dict[str, list[str]]] = {}
    gpxs_styles: Optional[Any] = {}


class AreaExistenceConfigModel(BaseModel):
    map_area: Any


class PaperDimensionsConfigModel(BaseModel):
    map_area: Any
    paper_dimensions: PaperDimensionsModel
    given_smaller_paper_dimension: Optional[bool] = True
    wanted_orientation: Optional[str] = MapOrientation.AUTOMATIC.value


class ZoomLevelConfigModel(BaseModel):
    map_area: Any
    paper_dimensions: PaperDimensionsModel


class PaperDimensionsZoomLevelConfigModel(BaseModel):
    map_area: Any
    paper_dimensions: PaperDimensionsModel
    given_smaller_paper_dimension: Optional[bool] = True
    wanted_orientation: Optional[str] = MapOrientation.AUTOMATIC.value


class MapBorderConfigModel(BaseModel):
    map_area: Any
    paper_dimensions: PaperDimensionsModel
    fit_paper_size: FitPaperSizeModel


class GeneratorResponseStatusModel(BaseModel):
    token: str | None = None
    status: str = 'failed'  # started|queued|processing|completed|failed
    message: str | None = None


class ZoomLevelResponseModel(BaseModel):
    zoom_level: int


class PaperDimensionResponseModel(BaseModel):
    width: float | int
    height: float | int


class PaperDimensionsZoomLevelResponseModel(BaseModel):
    width: float | int
    height: float | int
    zoom_level: int


class AvailableOsmFilesResponseModel(BaseModel):
    osm_files: List[str]


class AvailableMapThemesResponseModel(BaseModel):
    map_themes: List[str]


class StatusResponseModel(BaseModel):
    status: str


class MessageResponseModel(BaseModel):
    message: str
