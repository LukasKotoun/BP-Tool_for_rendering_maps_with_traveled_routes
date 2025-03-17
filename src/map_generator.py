import warnings

import multiprocessing
from uuid_extensions import uuid7str
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional
import time
from config import *
from common.map_enums import ProcessingStatus
from modules.main_generator import generate_map, calc_preview, get_map_area_gdf
from common.api_base_models import MapGeneratorConfigModel, GeneratorResponseStatusModel
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.osm_data_parser import OsmDataParser
from modules.style_assigner import StyleManager
from modules.plotter import Plotter
from modules.gpx_manager import GpxManager
from modules.received_structure_processor import ReceivedStructureProcessor
from modules.task_queue_manager import MapTaskQueueManager
from multiprocessing import Lock

shared_tasks = multiprocessing.Manager().dict()
shared_tasks_lock = Lock()

task_queue_manager = MapTaskQueueManager(max_normal_tasks=MAX_CONCURRENT_TASKS_NORMAL,
                                         max_preview_tasks=MAX_CONCURRENT_TASKS_PREVIEW,
                                         gpx_tmp_folder=GPX_TMP_FOLDER, gpx_crs=CRS_DISPLAY)

server_app = FastAPI()
server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


def paper_dimensions_endpoint(area: WantedArea, paper_dimensions, wanted_orientation, given_smaller_paper_dimension):
    map_area_gdf = GdfUtils.get_whole_area_gdf(
        area, 'area', CRS_OSM, CRS_DISPLAY)
    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, paper_dimensions,
                                                        given_smaller_paper_dimension, wanted_orientation)

    return paper_dimensions_mm


def zoom_level_endpoint(area: WantedArea, paper_dimensions_mm, wanted_orientation, fit_paper_size, given_smaller_paper_dimension):
    map_area_gdf = GdfUtils.get_whole_area_gdf(
        area, 'area', CRS_OSM, CRS_DISPLAY)
    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, paper_dimensions_mm,
                                                        given_smaller_paper_dimension, wanted_orientation)

    if (fit_paper_size):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

    map_scaling_factor = Utils.calc_map_scaling_factor(map_area_dimensions,
                                                       paper_dimensions_mm)

    zoom_level = Utils.get_zoom_level(
        map_scaling_factor, ZOOM_MAPPING, 0.3)
    return zoom_level


@server_app.post("/generate-map-normal", response_model=GeneratorResponseStatusModel)
def generate_map_normal(gpxs: Optional[List[UploadFile]] = File(None),
                        config: str = Form(...)):
    # validate
    try:
        # todo validate gpx names and files names
        config: MapGeneratorConfigModel = MapGeneratorConfigModel(
            **json.loads(config))
        osm_files = ReceivedStructureProcessor.validate_and_convert_osm_files(
            config.osm_files, OSM_AVAILABLE_FILES)
        ReceivedStructureProcessor.validate_zoom_levels(
            config.styles_zoom_levels.dict(), ZOOM_STYLE_LEVELS_VALIDATION)
        styles_zoom_levels = config.styles_zoom_levels.dict()
        paper_dimensions_mm = ReceivedStructureProcessor.validate_and_convert_paper_dimension(
            config.paper_dimensions)
        ReceivedStructureProcessor.validate_wanted_elements_and_styles(
            config.wanted_categories_and_styles_edit, ALLOWED_WANTED_ELEMENTS_STRUCTURE, FE_EDIT_STYLES_VALIDATION)
        gpxs_styles = ReceivedStructureProcessor.validate_and_convert_gpx_styles(
            config.gpxs_styles, GPX_NORMAL_COLUMNS, GPX_GENERAL_KEYS, GPX_STYLES_VALIDATION, GPX_STYLES_MAPPING)

        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
            map_area, True)
    except Exception as e:
        return {"message": f"Error in data validation: {e}", "status": ProcessingStatus.FAILED.value}

    # calc needed values before storing in front - are different for normal and preview
    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    if (config.fit_paper_size):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

        if (config.fit_paper_size_bounds_plot):
            boundary_map_area_gdf = GdfUtils.combine_gdfs(
                [boundary_map_area_gdf, map_area_gdf.copy()])

    map_scaling_factor = Utils.calc_map_scaling_factor(map_area_dimensions,
                                                       paper_dimensions_mm)
    map_scale = Utils.get_scale(GdfUtils.get_bounds_gdf(
        GdfUtils.change_crs(map_area_gdf, CRS_OSM)), paper_dimensions_mm)

    map_area_gdf = GdfUtils.change_crs(map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)
    peaks_filter_radius = map_scale * 10 * config.peaks_filter_sensitivity

    gpxs_gdf = GpxManager.load_to_gdf_from_memory(gpxs, config.gpxs_categories, CRS_DISPLAY)

    map_generator_config = {
        MapConfigKeys.OSM_FILES.value: osm_files,
        MapConfigKeys.MAP_AREA.value: map_area_gdf,
        MapConfigKeys.GPXS.value: gpxs_gdf,
        MapConfigKeys.MAP_OUTER_AREA.value: None,
        MapConfigKeys.MAP_AREA_BOUNDARY.value: boundary_map_area_gdf,
        MapConfigKeys.MAP_SCALING_FACTOR.value: map_scaling_factor,
        MapConfigKeys.PAPER_DIMENSION_MM.value: paper_dimensions_mm,
        MapConfigKeys.PEAKS_FILTER_RADIUS.value: peaks_filter_radius,
        MapConfigKeys.MIN_PLACE_POPULATION.value: config.min_place_population,
        MapConfigKeys.MAP_THEME.value: config.map_theme,
        MapConfigKeys.PLOT_BRIDGES.value: config.plot_bridges,
        MapConfigKeys.PLOT_TUNNELS.value: config.plot_tunnels,
        MapConfigKeys.WANTED_CATEGORIES_AND_STYLES_CHANGES.value: config.wanted_categories_and_styles_edit,
        MapConfigKeys.STYLES_ZOOM_LEVELS.value: styles_zoom_levels,
        MapConfigKeys.GPXS_STYLES.value: gpxs_styles,
    }
    task_id: str = uuid7str()

    status = task_queue_manager.add_task(
        map_generator_config, task_id, shared_tasks, shared_tasks_lock, QueueType.NORMAL)
    
    return {"message": "Map is generating", "task_id": task_id, "status": status}


@server_app.post("/generate-map-preview", response_model=GeneratorResponseStatusModel)
def preview_map_endpoint(gpxs: Optional[List[UploadFile]] = File(None),
                         config: str = Form(...)):
    # Validate 
    try:
        # todo validate gpx names and files
        config: MapGeneratorConfigModel = MapGeneratorConfigModel(
            **json.loads(config))
        osm_files = ReceivedStructureProcessor.validate_and_convert_osm_files(
            config.osm_files, OSM_AVAILABLE_FILES)
        
        ReceivedStructureProcessor.validate_zoom_levels(
            config.styles_zoom_levels.dict(), ZOOM_STYLE_LEVELS_VALIDATION)
        styles_zoom_levels = config.styles_zoom_levels.dict()
        
        paper_dimensions_mm = ReceivedStructureProcessor.validate_and_convert_paper_dimension(
            config.paper_dimensions)
        preview_paper_dimensions_mm = paper_dimensions_mm = ReceivedStructureProcessor.validate_and_convert_paper_dimension(
            config.paper_preview_dimensions)
        ReceivedStructureProcessor.validate_wanted_elements_and_styles(
            config.wanted_categories_and_styles_edit, ALLOWED_WANTED_ELEMENTS_STRUCTURE, FE_EDIT_STYLES_VALIDATION)

        gpxs_styles = ReceivedStructureProcessor.validate_and_convert_gpx_styles(
            config.gpxs_styles, GPX_NORMAL_COLUMNS, GPX_GENERAL_KEYS, GPX_STYLES_VALIDATION, GPX_STYLES_MAPPING)
        
        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
            map_area, True)
        if (config.map_preview_area is None):
            preview_map_area_gdf = map_area_gdf.copy()
        else:
            preview_map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
                config.map_preview_area, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")
            preview_map_area_gdf = get_map_area_gdf(
                preview_map_area, False)

    except Exception as e:
        return {"message": f"Error in data validation: {e}", "status": ProcessingStatus.FAILED.value}
    # area - big area with all settings
    # preview_area - area to display
    # calc needed values before storing in front - are different for normal and preview
    (map_scaling_factor, preview_map_area_gdf, map_area_gdf,
     map_scale) = calc_preview(map_area_gdf, paper_dimensions_mm, config.fit_paper_size, preview_map_area_gdf, preview_paper_dimensions_mm)

    preview_map_area_gdf = GdfUtils.change_crs(
        preview_map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)

    peaks_filter_radius = map_scale * 10 * config.peaks_filter_sensitivity

    gpxs_gdf = GpxManager.load_to_gdf_from_memory(gpxs, config.gpxs_categories, CRS_DISPLAY)

    # config for map generator
    map_generator_config = {
        MapConfigKeys.OSM_FILES.value: osm_files,
        MapConfigKeys.MAP_AREA.value: preview_map_area_gdf,
        MapConfigKeys.MAP_AREA_BOUNDARY.value: boundary_map_area_gdf,
        MapConfigKeys.MAP_OUTER_AREA.value: map_area_gdf,
        MapConfigKeys.MAP_SCALING_FACTOR.value: map_scaling_factor,
        MapConfigKeys.PAPER_DIMENSION_MM.value: preview_paper_dimensions_mm,
        MapConfigKeys.PEAKS_FILTER_RADIUS.value: peaks_filter_radius,
        MapConfigKeys.MIN_PLACE_POPULATION.value: config.min_place_population,
        MapConfigKeys.MAP_THEME.value: config.map_theme,
        MapConfigKeys.PLOT_BRIDGES.value: config.plot_bridges,
        MapConfigKeys.PLOT_TUNNELS.value: config.plot_tunnels,
        MapConfigKeys.WANTED_CATEGORIES_AND_STYLES_CHANGES.value: config.wanted_categories_and_styles_edit,
        MapConfigKeys.STYLES_ZOOM_LEVELS.value: styles_zoom_levels,
        MapConfigKeys.GPXS_STYLES.value: gpxs_styles,
        MapConfigKeys.GPXS.value: gpxs_gdf,
    }
    task_id: str = uuid7str()
    status = task_queue_manager.add_task(
        map_generator_config, task_id, shared_tasks, shared_tasks_lock, QueueType.PREVIEW)

    return {"message": "Map preview is generating", "task_id": task_id, "status": status}


@server_app.get("/tasks")
def get_task_status():
    """
    Get the status of a specific task.
    """
    print(shared_tasks)
    return {"tasks": shared_tasks}

# @server_app.get("/tasks/{job_id}")
# def get_task_status(job_id: str):
#     """
#     Get the status of a specific task.
#     """
#     print(shared_tasks)

# @server_app.get("/stop_task/{job_id}")
# def get_task_status(job_id: str):
#     """
#     Get the status of a specific task.
#     """
#     if job_id in tasks:
#         return {"job_id": job_id, "status": tasks[job_id]}
#     else:
#         return {"error": "Job not found"}


# @server_app.get("/get_map/{job_id}")
# def get_task_status(job_id: str):
#     # find in shared_tasks or folder
#     pass


@server_app.on_event("shutdown")
def shutdown_cleanup():
    """
    Cleanup any running processes and tmp files on server shutdown.
    """
    print("Shutting down server...")
    task_queue_manager.clear_queue(shared_tasks, shared_tasks_lock)
    for task_id in shared_tasks.keys():
        try:
            print(f"Terminating task {task_id}, {shared_tasks[task_id]}")
            task_queue_manager.terminate_task(task_id, shared_tasks, shared_tasks_lock)
            print(f"Terminated {task_id}")
            with shared_tasks_lock:
                shared_tasks.pop(task_id)
        except Exception as e:
            print(f"Error terminating task {task_id}: {e}")
            
