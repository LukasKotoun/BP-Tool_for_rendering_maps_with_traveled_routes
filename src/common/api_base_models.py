from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, UploadFile


class ZoomLevelsModel(BaseModel):
    nodes: int
    ways: int
    areas: int
    general: int

class MapGeneratorConfigModel(BaseModel):
    map_area: Any
    paper_dimensions: list[float|int, float|int]
    map_preview_area: Optional[Any] = None
    paper_preview_dimensions: Optional[list[float|int, float|int]] = None
    fit_paper_size: Optional[bool] = False
    fit_paper_size_bounds_plot: Optional[bool] = False
    osm_files: List[str]
    min_place_population: Optional[int|float] = None
    peaks_filter_sensitivity: Optional[int|float] = None
    map_theme: Optional[str] = ""
    plot_bridges: Optional[bool] = True
    plot_tunnels: Optional[bool] = True
    wanted_categories_and_styles_edit: Any
    styles_zoom_levels: ZoomLevelsModel
    gpxs_categories: Optional[Dict[str, str]] = {}
    gpxs_styles: Optional[Any] = []


class ZoomLevelModel(BaseModel):
    map_area: Any
    paper_dimensions: list[float|int, float|int]
    map_preview_area: Optional[Any] = None
    paper_preview_dimensions: Optional[list[float|int, float|int]] = None
    fit_paper_size: Optional[bool] = False
    fit_paper_size_bounds_plot: Optional[bool] = False
    osm_files: List[str]
    min_place_population: Optional[int|float] = None
    peaks_filter_sensitivity: Optional[int|float] = None
    map_theme: Optional[str] = ""
    plot_bridges: Optional[bool] = True
    plot_tunnels: Optional[bool] = True
    wanted_categories_and_styles_edit: Any
    styles_zoom_levels: ZoomLevelsModel
    gpxs_categories: Optional[Dict[str, str]] = {}
    gpxs_styles: Optional[Any] = []

# class ZoomLevelModel(BaseModel):
#     map_area: Any
#     paper_dimensions: list[float|int, float|int]
#     map_preview_area: Optional[Any] = None
#     paper_preview_dimensions: Optional[list[float|int, float|int]] = None
#     fit_paper_size: Optional[bool] = False
#     fit_paper_size_bounds_plot: Optional[bool] = False
#     osm_files: List[str]
#     min_place_population: Optional[int|float] = None
#     peaks_filter_sensitivity: Optional[int|float] = None
#     map_theme: Optional[str] = ""
#     plot_bridges: Optional[bool] = True
#     plot_tunnels: Optional[bool] = True
#     wanted_categories_and_styles_edit: Any
#     unwanted_categories: Any
#     styles_zoom_levels: ZoomLevelsModel
#     gpxs_categories: Optional[Dict[str, str]] = {}
#     gpxs_styles: Optional[Any] = []
    

class GeneratorResponseStatusModel(BaseModel):
    task_id: str | None = None
    status: str = 'failed'  # started|queued|processing|completed|failed
    message: str | None = None