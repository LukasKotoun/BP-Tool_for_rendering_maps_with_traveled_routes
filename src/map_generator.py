import warnings

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Depends, Response
from multiprocessing.managers import DictProxy
import multiprocessing
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from uuid_extensions import uuid7str

import json
from typing import List, Optional, Any
import time
from config import *
from common.map_enums import ProcessingStatus
from modules.main_generator import calc_preview, get_map_area_gdf, plot_map_borders
from common.api_base_models import *
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.osm_data_parser import OsmDataParser
from modules.style_assigner import StyleManager
from modules.gpx_manager import GpxManager
from modules.received_structure_processor import ReceivedStructureProcessor
from modules.task_manager import TaskManager
from multiprocessing import Lock
import os

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev_key")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

server_app = FastAPI()
server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



task_queue_manager = TaskManager(max_normal_tasks=MAX_CONCURRENT_TASKS_NORMAL,
                                         max_preview_tasks=MAX_CONCURRENT_TASKS_PREVIEW,
                                         gpx_tmp_folder=GPX_TMP_FOLDER, gpx_crs=CRS_DISPLAY)

# endpoints helpers
def decode_task_id_from_JWT(token: str = Depends(oauth2_scheme)):
    payload = Utils.decode_jwt(token, JWT_ALGORITHM, SECRET_KEY)
    task_id = payload.get("task_id")
    if task_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return task_id

# endpoints

@server_app.get("/available_osm_files", response_model=AvailableOsmFilesResponseModel)
def available_osm_files():
    return {"osm_files": OSM_AVAILABLE_FILES.keys()}


@server_app.get("/available_map_themes", response_model=AvailableMapThemesResponseModel)
def available_map_themes():
    return {"map_themes": STYLES.keys()}


@server_app.post("/paper_dimensions", response_model=PaperDimensionResponseModel)
def get_paper_dimensions(config: PaperDimensionsConfigModel):
    try:
        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf = get_map_area_gdf(
            map_area, False)
        paper_dimensions = ReceivedStructureProcessor.convert_paper_dimension(
            config.paper_dimensions, True)
        wanted_orientation = ReceivedStructureProcessor.validate_wanted_orientation(
            config.wanted_orientation, ALLOWED_WANTED_PAPER_ORIENTATIONS)
        given_smaller_paper_dimension = config.given_smaller_paper_dimension
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error in config validation: {e}")

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, paper_dimensions,
                                                        given_smaller_paper_dimension, wanted_orientation)

    return {"width": paper_dimensions_mm[0], "height": paper_dimensions_mm[1]}

@server_app.post("/generate_map_borders")
def generate_map_borders(config: MapBorderConfigModel):
    try:
        paper_dimensions_mm = ReceivedStructureProcessor.convert_paper_dimension(
            config.paper_dimensions, False)
        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
            map_area, True)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error in config validation: {e}")

    if (config.fit_paper_size):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        if (config.fit_paper_size_bounds_plot):
            boundary_map_area_gdf = GdfUtils.combine_gdfs(
                [boundary_map_area_gdf, map_area_gdf.copy()])
    file_id = uuid7str()
    file_path = plot_map_borders(file_id, map_area_gdf, boundary_map_area_gdf, paper_dimensions_mm)
    if(file_path is None or not os.path.isfile(file_path)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error white generating borders")
    
    def iterfile():
        # stream file and delete after completion
        try:
            #https://stackoverflow.com/questions/73550398/how-to-download-a-large-file-using-fastapi
            with open(file_path, 'rb') as f:
                while chunk := f.read(FILE_DOWNLOAD_CHUNK_SIZE):
                    yield chunk
            # delete file after successful streaming
            Utils.remove_file(file_path)
        except Exception as e:
            print(f"Error during file streaming: {str(e)}")

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=map.pdf"}
    )



@server_app.post("/zoom_level", response_model=ZoomLevelResponseModel)
def get_zoom_level(config: ZoomLevelConfigModel):
    try:
        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf = get_map_area_gdf(
            map_area, False)
        paper_dimensions_mm = ReceivedStructureProcessor.convert_paper_dimension(
            config.paper_dimensions, False)
        fit_paper_size = config.fit_paper_size

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error in config validation: {e}")

    expanded_map_area_dimensions = GdfUtils.get_dimensions_gdf(GdfUtils.expand_gdf_area_fitPaperSize(
        map_area_gdf, paper_dimensions_mm))
    map_scaling_factor = Utils.calc_map_scaling_factor(expanded_map_area_dimensions,
                                                       paper_dimensions_mm)
    zoom_level = Utils.get_zoom_level(
        map_scaling_factor, ZOOM_MAPPING, 0.2)
    return {"zoom_level": zoom_level}


@server_app.post("/generate-map-normal", response_model=GeneratorResponseStatusModel)
def generate_map_normal(gpxs: Optional[List[UploadFile]] = File(None),
                        config: str = Form(...)):
    # validate
    try:
        config: MapGeneratorConfigModel = MapGeneratorConfigModel(
            **json.loads(config))
        osm_files = ReceivedStructureProcessor.validate_and_convert_osm_files(
            config.osm_files, OSM_AVAILABLE_FILES)
        ReceivedStructureProcessor.validate_zoom_levels(
            config.styles_zoom_levels.dict(), ZOOM_STYLE_LEVELS_VALIDATION)
        styles_zoom_levels = config.styles_zoom_levels.dict()
        paper_dimensions_mm = ReceivedStructureProcessor.convert_paper_dimension(
            config.paper_dimensions, False)
        ReceivedStructureProcessor.validate_wanted_elements_and_styles(
            config.wanted_categories_and_styles_edit, ALLOWED_WANTED_ELEMENTS_STRUCTURE, FE_EDIT_STYLES_VALIDATION)
        gpxs_styles = ReceivedStructureProcessor.validate_and_convert_gpx_styles(
            config.gpxs_styles, GPX_NORMAL_COLUMNS, GPX_GENERAL_KEYS, GPX_STYLES_VALIDATION, GPX_STYLES_MAPPING)

        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
            map_area, True)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error in config validation: {e}")

    # calc needed values before storing in front - are different for normal and preview
    # ------------get paper dimension (size and orientation)------------
        # calc scaling factor always from expanded are on paper - to get correct sizes of scaled objects
    if (config.fit_paper_size):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        map_scaling_factor = Utils.calc_map_scaling_factor(map_area_dimensions,
                                                           paper_dimensions_mm)
        if (config.fit_paper_size_bounds_plot):
            boundary_map_area_gdf = GdfUtils.combine_gdfs(
                [boundary_map_area_gdf, map_area_gdf.copy()])
    else:
        expanded_map_area_dimensions = GdfUtils.get_dimensions_gdf(GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm))
        map_scaling_factor = Utils.calc_map_scaling_factor(expanded_map_area_dimensions,
                                                           paper_dimensions_mm)

    map_scale = Utils.get_scale(GdfUtils.get_bounds_gdf(
        GdfUtils.change_crs(map_area_gdf, CRS_OSM)), paper_dimensions_mm)

    map_area_gdf = GdfUtils.change_crs(map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)
    peaks_filter_radius = map_scale * 10 * config.peaks_filter_sensitivity

    gpxs_gdf = GpxManager.load_to_gdf_from_memory(
        gpxs, config.gpxs_categories, CRS_DISPLAY)

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
    task_status, task_id = task_queue_manager.add_task(
        map_generator_config, QueueType.NORMAL)
    if(task_id is None or task_status == ProcessingStatus.FAILED.value):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot start task")
        
    access_token = Utils.create_access_token(
        data={"task_id": task_id}, expires_delta=JWT_EXPIRATION_TIME, algorithm=JWT_ALGORITHM, secret_key=SECRET_KEY
    )
    return {"message": "Map is generating", "token": access_token, "status": task_status}


@server_app.post("/generate-map-preview", response_model=GeneratorResponseStatusModel)
def generate_preview_map(gpxs: Optional[List[UploadFile]] = File(None),
                         config: str = Form(...)):
    # Validate
    try:
        config: MapGeneratorPreviewConfigModel = MapGeneratorPreviewConfigModel(
            **json.loads(config))
        osm_files = ReceivedStructureProcessor.validate_and_convert_osm_files(
            config.osm_files, OSM_AVAILABLE_FILES)

        ReceivedStructureProcessor.validate_zoom_levels(
            config.styles_zoom_levels.dict(), ZOOM_STYLE_LEVELS_VALIDATION)
        styles_zoom_levels = config.styles_zoom_levels.dict()

        paper_dimensions_mm = ReceivedStructureProcessor.convert_paper_dimension(
            config.paper_dimensions, False)
        preview_paper_dimensions_mm = ReceivedStructureProcessor.convert_paper_dimension(
            config.paper_preview_dimensions, False)
        ReceivedStructureProcessor.validate_wanted_elements_and_styles(
            config.wanted_categories_and_styles_edit, ALLOWED_WANTED_ELEMENTS_STRUCTURE, FE_EDIT_STYLES_VALIDATION)

        gpxs_styles = ReceivedStructureProcessor.validate_and_convert_gpx_styles(
            config.gpxs_styles, GPX_NORMAL_COLUMNS, GPX_GENERAL_KEYS, GPX_STYLES_VALIDATION, GPX_STYLES_MAPPING)

        map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            config.map_area, REQ_AREA_DICT_KEYS, key_with_area="area")
        map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
            map_area, True)
        if (config.map_preview_area is None):
            map_preview_area_gdf = map_area_gdf.copy()
        else:
            map_preview_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
                config.map_preview_area, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")
            map_preview_area_gdf = get_map_area_gdf(
                map_preview_area, False)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error in config validation: {e}")
    # area - big area with all settings
    # preview_area - area to display
    # calc needed values before storing in front - are different for normal and preview
    (map_scaling_factor, map_preview_area_gdf, map_area_gdf,
     map_scale) = calc_preview(map_area_gdf, paper_dimensions_mm, config.fit_paper_size, map_preview_area_gdf, preview_paper_dimensions_mm)

    map_preview_area_gdf = GdfUtils.change_crs(
        map_preview_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)

    peaks_filter_radius = map_scale * 10 * config.peaks_filter_sensitivity

    gpxs_gdf = GpxManager.load_to_gdf_from_memory(
        gpxs, config.gpxs_categories, CRS_DISPLAY)

    # config for map generator
    map_generator_config = {
        MapConfigKeys.OSM_FILES.value: osm_files,
        MapConfigKeys.MAP_AREA.value: map_preview_area_gdf,
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
    task_status, task_id = task_queue_manager.add_task(
        map_generator_config, QueueType.PREVIEW)
    
    if(task_id is None or task_status == ProcessingStatus.FAILED.value):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot start task")
        
    access_token = Utils.create_access_token(
        data={"task_id": task_id}, expires_delta=JWT_EXPIRATION_TIME, algorithm=JWT_ALGORITHM, secret_key=SECRET_KEY
    )

    return {"message": "Map preview is generating", "token": access_token, "status": task_status}

@server_app.get("/task_status", response_model=StatusResponseModel)
def get_task_status(task_id: str = Depends(decode_task_id_from_JWT)):
    """
    Get the status of a specific task from id in token.
    """
    task_info = task_queue_manager.get_task_info(task_id)
    if (task_info is not None):
        return {"status": task_info[SharedDictKeys.STATUS.value]}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@server_app.delete("/terminate_task", response_model=MessageResponseModel)
def terminate_task(task_id: str = Depends(decode_task_id_from_JWT)):
    """
    Terminate task from id in token.
    """
    terminated = task_queue_manager.delete_task(task_id)
    if (terminated):
        return {"message": "Task terminated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot terminate task - task not found")
   
@server_app.get("/download_map")
def get_map_file(task_id: str = Depends(decode_task_id_from_JWT)):
    task_info = task_queue_manager.get_task_info(task_id)
    if (task_info is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if (task_info[SharedDictKeys.STATUS.value] != ProcessingStatus.COMPLETED.value):
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY, detail="Task not completed yet")
    file_path = None
    for file in task_info[SharedDictKeys.FILES.value]:
        if file.endswith(".pdf"):
            file_path = file
            break
    if(file_path is None or not os.path.isfile(file_path)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    def iterfile():
        # stream file and delete after completion
        try:
            #https://stackoverflow.com/questions/73550398/how-to-download-a-large-file-using-fastapi
            with open(file_path, 'rb') as f:
                while chunk := f.read(FILE_DOWNLOAD_CHUNK_SIZE):
                    yield chunk
            # delete file after successful streaming
            delete_status = task_queue_manager.delete_task(task_id)
            if(not delete_status):
                warnings.warn("Error: cannot remove task")
        except Exception as e:
            print(f"Error during file streaming: {str(e)}")

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=map.pdf"}
    )



@server_app.on_event("shutdown")
def shutdown_cleanup():
    """
    Cleanup any running processes and tmp files on server shutdown.
    """
    print("Shutting down server...")
    task_queue_manager.delete_all_tasks()