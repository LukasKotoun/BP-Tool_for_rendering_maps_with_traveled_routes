from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, UploadFile


class WantedCategoryFilterModel(BaseModel):
    nodes: dict[str, dict[str, int]]
    ways: dict[str, dict[str, int]]
    areas: dict[str, dict[str, int]]
    nodes_from_area: dict[str, dict[str, int]]

class UnwantedCategoryFilterModel(BaseModel):
    nodes: dict[str, Any]
    ways: dict[str, Any]
    areas: dict[str, Any]

class ZoomLevelsModel(BaseModel):
    nodes: int
    ways: int
    areas: int
    general: int

class MapGeneratorConfigModel(BaseModel):
    map_area: Any
    paper_dimension_mm: list[float, float]
    map_preview_area: Optional[Any] = None
    paper_preview_dimension_mm: Optional[list[float, float]] = None
    fit_paper_size: Optional[bool] = False
    fit_paper_size_bounds_plot: Optional[bool] = False
    osm_files: List[str]
    min_place_population: Optional[int] = None
    peaks_filter_sensitivity: Optional[int] = 0
    map_theme: Optional[str] = ""
    plot_bridges: Optional[bool] = True
    plot_tunnels: Optional[bool] = True
    wanted_categories: WantedCategoryFilterModel
    unwanted_categories: UnwantedCategoryFilterModel
    styles_zoom_levels: ZoomLevelsModel = None
    gpxs_categories: Optional[Dict[str, str]] = {}
    gpxs_styles: Optional[Any] = []

    
class GeneratorResponseStatusModel(BaseModel):
    job_id: UUID4
    status: str  # started|queued|processing|completed|failed
    status_percent: int
    result_url: str | None = None