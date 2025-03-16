import warnings

import multiprocessing
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional

from config import *
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
import os
from multiprocessing import Lock
import shutil


shared_tasks = multiprocessing.Manager().dict()
shared_tasks_lock = Lock()

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


@server_app.post("/generate_map", response_model=GeneratorResponseStatusModel)
def normal_map_endpoint(gpxs: Optional[List[UploadFile]] = File(None),
                        config: str = Form(...)):
    try:
        # todo validate unwanted categories
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
        gpxs_styles = ReceivedStructureProcessor.validate_gpx_styles(config.gpxs_styles, [
            'categories', 'names'], ['general'], GPX_STYLES_VALIDATION, GPX_STYLES_MAPPING)

        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
            map_area, True)
    except Exception as e:
        return {"message": f"Error in data validation: {e}", "status": "failed"}

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

    # todo check for front and by that convert to gdf from memory or store as tmp files
    # and by that also use config.gpxs_categories
    gpx_manager = GpxManager(GPX_FOLDER, CRS_DISPLAY)
    gpxs_gdf = gpx_manager.get_gpxs_gdf()

    # check how it will be recived from FE and change or remap
    map_generator_config = {
        # from fe checked and changed to gdf
        MapConfigKeys.MAP_AREA.value: map_area_gdf,
        # gdf or list of (path_name, category|None)
        MapConfigKeys.GPXS.value: gpxs_gdf,
        # MapConfigKeys.GPXS_CATEGORIES.value: [],
        MapConfigKeys.MAP_OUTER_AREA.value: None,
        MapConfigKeys.MAP_AREA_BOUNDARY.value: boundary_map_area_gdf,
        MapConfigKeys.MAP_SCALING_FACTOR.value: map_scaling_factor,
        MapConfigKeys.PAPER_DIMENSION_MM.value: paper_dimensions_mm,
        MapConfigKeys.OSM_FILES.value: osm_files,
        MapConfigKeys.PEAKS_FILTER_RADIUS.value: peaks_filter_radius,

        # from FE - checked
        MapConfigKeys.MIN_PLACE_POPULATION.value: config.min_place_population,
        MapConfigKeys.MAP_THEME.value: config.map_theme,
        MapConfigKeys.PLOT_BRIDGES.value: config.plot_bridges,
        MapConfigKeys.PLOT_TUNNELS.value: config.plot_tunnels,
        MapConfigKeys.WANTED_CATEGORIES_AND_STYLES_CHANGES.value: config.wanted_categories_and_styles_edit,
        MapConfigKeys.UNWANTED_CATEGORIES.value: config.unwanted_categories,
        MapConfigKeys.STYLES_ZOOM_LEVELS.value: styles_zoom_levels,
        MapConfigKeys.GPXS_STYLES.value: gpxs_styles,
    }
    task_id = uuid.uuid4()

    process = multiprocessing.Process(
        target=generate_map, args=(map_generator_config, task_id, shared_tasks, shared_tasks_lock, False))
    
    with shared_tasks_lock:
        process.start()
        shared_tasks[task_id] = {
            "status": "starting",
            "pid": process.pid,
            "files": [],
            "process_running": False
        }
    return {"message": "Map is generating", "status": "in progress"}


@server_app.post("/generate_map_preview", response_model=GeneratorResponseStatusModel)
def preview_map_endpoint(gpxs: Optional[List[UploadFile]] = File(None),
                         config: str = Form(...)):
    try:
        # data validation
        # todo validate unwanted categories
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

        gpxs_styles = ReceivedStructureProcessor.validate_gpx_styles(config.gpxs_styles, [
            'categories', 'names'], ['general'], GPX_STYLES_VALIDATION, GPX_STYLES_MAPPING)
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
        return {"message": f"Error in data validation: {e}", "status": "failed"}
    # area - big area with all settings
    # preview_area - area to display

    # data preparation and preview calculation
    (map_scaling_factor, preview_map_area_gdf, map_area_gdf,
     map_scale) = calc_preview(map_area_gdf, paper_dimensions_mm, config.fit_paper_size, preview_map_area_gdf, preview_paper_dimensions_mm)

    preview_map_area_gdf = GdfUtils.change_crs(
        preview_map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)

    peaks_filter_radius = map_scale * 10 * config.peaks_filter_sensitivity

    # todo check for front and by that convert to gdf from memory or store as tmp files
    gpx_manager = GpxManager(GPX_FOLDER, CRS_DISPLAY)
    gpxs_gdf = gpx_manager.get_gpxs_gdf()

    # config for map generator
    map_generator_config = {
        MapConfigKeys.MAP_AREA.value: preview_map_area_gdf,
        MapConfigKeys.MAP_AREA_BOUNDARY.value: boundary_map_area_gdf,
        MapConfigKeys.MAP_OUTER_AREA.value: map_area_gdf,
        MapConfigKeys.MAP_SCALING_FACTOR.value: map_scaling_factor,
        MapConfigKeys.PAPER_DIMENSION_MM.value: preview_paper_dimensions_mm,
        MapConfigKeys.OSM_FILES.value: osm_files,
        MapConfigKeys.PEAKS_FILTER_RADIUS.value: peaks_filter_radius,
        MapConfigKeys.MIN_PLACE_POPULATION.value: config.min_place_population,
        MapConfigKeys.MAP_THEME.value: config.map_theme,
        MapConfigKeys.PLOT_BRIDGES.value: config.plot_bridges,
        MapConfigKeys.PLOT_TUNNELS.value: config.plot_tunnels,
        MapConfigKeys.WANTED_CATEGORIES_AND_STYLES_CHANGES.value: config.wanted_categories_and_styles_edit,
        MapConfigKeys.UNWANTED_CATEGORIES.value: config.unwanted_categories,
        MapConfigKeys.STYLES_ZOOM_LEVELS.value: styles_zoom_levels,
        MapConfigKeys.GPXS_STYLES.value: gpxs_styles,
        MapConfigKeys.GPXS.value: gpxs_gdf,

    }
    task_id: uuid.UUID = uuid.uuid4()
    process = multiprocessing.Process(
        target=generate_map, args=(map_generator_config, task_id, shared_tasks, shared_tasks_lock, False))
    with shared_tasks_lock:
        process.start()
        shared_tasks[task_id] = {
            "status": "in_progress",
            "files": [],
            "pid": process.pid,
            "process_running": False
        }

    return {"message": "Map preview is generating", "status": "in progress"}

@server_app.get("/tasks")
def get_task_status():
    """
    Get the status of a specific task.
    """
    print(shared_tasks)
    return{ "tasks": shared_tasks}

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
    # with shared_tasks_lock:
    #     task = shared_tasks.get(task_id)
    #     if not task:
    #         print(f"Task {task_id} not found.")
    #         return

    #     pid = task.get("pid")
    #     process_running = task.get("process_running", False)
    #     files = task.get("files", [])

    #     # Kill the process if it's running
    #     if process_running and pid:
    #         try:
    #             os.kill(pid, signal.SIGTERM)  # Send terminate signal
    #             print(f"Terminated process {pid} for task {task_id}")
    #         except ProcessLookupError:
    #             print(f"Process {pid} not found, may have already exited.")
    #         except PermissionError:
    #             print(f"Permission denied when trying to kill process {pid}")

    #     # Remove temporary files
    #     for file_path in files:
    #         if os.path.exists(file_path):
    #             try:
    #                 os.remove(file_path)
    #                 print(f"Removed file: {file_path}")
    #             except Exception as e:
    #                 print(f"Error removing file {file_path}: {e}")

    #     # Update task status
    #     task["process_running"] = False
    #     task["files"] = []
    #     shared_tasks[task_id] = task
    #     print(f"Cleanup completed for task {task_id}")
