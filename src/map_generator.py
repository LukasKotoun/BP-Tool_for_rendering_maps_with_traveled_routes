import warnings

import multiprocessing
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional

from config import *
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
import shutil

from common.common_helpers import time_measurement

server_app = FastAPI()
server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
def process_bridges_and_tunnels(gdf, want_bridges: bool, want_tunnels: bool):
    GdfUtils.change_columns_to_numeric(gdf, ['layer'])
    GdfUtils.fill_nan_values(gdf, ['layer'], 0)
    gdf['layer'] = gdf.get('layer', 0)

    # set layer to 0 if there is no bridge or tunnel
    gdf.loc[GdfUtils.get_rows_filter(
        gdf, {'tunnel': '~', 'bridge': '~'}), 'layer'] = 0
    if (not want_bridges and not want_tunnels):
        gdf['layer'] = 0
        GdfUtils.remove_columns(gdf, ['bridge', 'tunnel'])
    elif (not want_bridges):
        if ('layer' in gdf):
            # set layer to 0 in bridges - as normal ways
            gdf.loc[GdfUtils.get_rows_filter(
                gdf, {'bridge': ''}), 'layer'] = 0
        GdfUtils.remove_columns(gdf, ['bridge'])
    elif (not want_tunnels):
        if ('layer' in gdf):
            # set layer to 0 in tunnels - as normal ways
            gdf.loc[GdfUtils.get_rows_filter(
                gdf, {'tunnel': ''}), 'layer'] = 0
        GdfUtils.remove_columns(gdf, ['tunnel'])
    return


def gdfs_convert_loaded_columns(gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf, config):
    GdfUtils.change_columns_to_numeric(
        nodes_gdf, config['nodes'][BaseConfigKeys.NUMERIC_COLUMNS])
    GdfUtils.convert_numeric_columns_int(
        nodes_gdf, config['nodes'][BaseConfigKeys.ROUND_COLUMNS])

    GdfUtils.change_columns_to_numeric(
        ways_gdf, config['ways'][BaseConfigKeys.NUMERIC_COLUMNS])
    GdfUtils.convert_numeric_columns_int(
        ways_gdf, config['ways'][BaseConfigKeys.ROUND_COLUMNS])

    GdfUtils.change_columns_to_numeric(
        areas_gdf, config['areas'][BaseConfigKeys.NUMERIC_COLUMNS])
    GdfUtils.convert_numeric_columns_int(
        areas_gdf, config['areas'][BaseConfigKeys.ROUND_COLUMNS])


def gdfs_prepare_styled_columns(gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf, map_scaling_factor, config):

    GdfUtils.create_derivated_columns(gpxs_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
                                      Style.EDGE_WIDTH_RATIO.value])
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.START_MARKER_EDGE_WIDTH.value, Style.START_MARKER_WIDTH.value, [
                                      Style.START_MARKER_EDGE_RATIO.value])
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.FINISH_MARKER_EDGE_WIDTH.value, Style.FINISH_MARKER_WIDTH.value, [
                                      Style.FINISH_MARKER_EDGE_RATIO.value])

    GdfUtils.remove_columns(gpxs_gdf, [Style.START_MARKER_EDGE_RATIO.value, Style.FINISH_MARKER_EDGE_RATIO.value,
                                       Style.EDGE_WIDTH_RATIO.value])

    # ----nodes----
    # set base width - scale by muplitpliers and object scaling factor
    GdfUtils.fill_nan_values(nodes_gdf, [Style.ZINDEX.value], 0)

    GdfUtils.multiply_column_gdf(nodes_gdf, Style.WIDTH.value, [
        Style.FE_WIDTH_SCALE.value], None)
    GdfUtils.multiply_column_gdf(nodes_gdf, Style.TEXT_FONT_SIZE.value, [
                                 Style.FE_TEXT_FONT_SIZE_SCALE.value], None)
    # text outline
    GdfUtils.create_derivated_columns(nodes_gdf, Style.TEXT_OUTLINE_WIDTH.value, Style.TEXT_FONT_SIZE.value, [
                                      Style.TEXT_OUTLINE_WIDTH_RATIO.value])

    # edge - MARKER size and ways width
    GdfUtils.create_derivated_columns(nodes_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
                                      # ?? maybe remove ...
                                      Style.EDGE_WIDTH_RATIO.value])
    old_column_remove = []
    for filter, new_column, old_column, fill in config['nodes'][BaseConfigKeys.DERIVATE_COLUMNS]:
        GdfUtils.create_derivated_columns(
            nodes_gdf, new_column, old_column, filter=filter, fill=fill)
        old_column_remove.append(old_column)

    GdfUtils.remove_columns(nodes_gdf, [Style.FE_WIDTH_SCALE.value, Style.FE_TEXT_FONT_SIZE_SCALE.value,
                                        Style.EDGE_WIDTH_RATIO.value, Style.TEXT_OUTLINE_WIDTH_RATIO.value, *old_column_remove])

    # ----ways----
    GdfUtils.fill_nan_values(ways_gdf, [Style.ZINDEX.value], 0)

    GdfUtils.multiply_column_gdf(ways_gdf, Style.WIDTH.value, [
        # if i will be creationg function with continues width scaling than multiply only by FEwidthscale
        Style.FE_WIDTH_SCALE.value])

    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
        Style.EDGE_WIDTH_RATIO.value])
    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGE_WIDTH_DASHED_CONNECT.value, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value, [
        Style.WIDTH.value])
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_WIDTH.value, Style.WIDTH.value, [     # calc bridge size only for bridges
                                      Style.BRIDGE_WIDTH_RATIO.value], {'bridge': ''})
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_EDGE_WIDTH.value, Style.BRIDGE_WIDTH.value, [
                                      Style.BRIDGE_EDGE_WIDTH_RATIO.value], {'bridge': ''})

    old_column_remove = []
    for filter, new_column, old_column, fill in config['ways'][BaseConfigKeys.DERIVATE_COLUMNS]:
        GdfUtils.create_derivated_columns(
            ways_gdf, new_column, old_column, filter=filter, fill=fill)
        old_column_remove.append(old_column)
    GdfUtils.remove_columns(ways_gdf, [Style.FE_WIDTH_SCALE.value, Style.EDGE_WIDTH_RATIO.value, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value,
                                       Style.BRIDGE_WIDTH_RATIO.value, Style.BRIDGE_EDGE_WIDTH_RATIO.value, *old_column_remove])

    # ----areas----
    GdfUtils.fill_nan_values(areas_gdf, [Style.ZINDEX.value], 0)

    GdfUtils.multiply_column_gdf(areas_gdf, Style.WIDTH.value, [
        Style.FE_WIDTH_SCALE.value])

    GdfUtils.create_derivated_columns(areas_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
                                      Style.EDGE_WIDTH_RATIO.value])
    old_column_remove = []
    for filter, new_column, old_column, fill in config['areas'][BaseConfigKeys.DERIVATE_COLUMNS]:
        GdfUtils.create_derivated_columns(
            areas_gdf, new_column, old_column, filter=filter, fill=fill)
        old_column_remove.append(old_column)

    GdfUtils.remove_columns(areas_gdf, [Style.FE_WIDTH_SCALE.value,
                                        Style.EDGE_WIDTH_RATIO.value, *old_column_remove])


def calc_preview(map_area_gdf, paper_dimensions_mm, fit_paper_size, preview_map_area_gdf, preview_paper_dimensions_mm):

    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

    if (fit_paper_size):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(
            map_area_gdf)
    map_scaling_factor = Utils.calc_map_scaling_factor(
        map_area_dimensions, paper_dimensions_mm)
    # calc bounds so area_zoom_preview will be 1 and will fill whole paper
    paper_fill_bounds = Utils.calc_bounds_to_fill_paper_with_ratio(preview_map_area_gdf.union_all().centroid,
                                                                   preview_paper_dimensions_mm, map_area_dimensions,
                                                                   paper_dimensions_mm)
    preview_map_area_gdf = GdfUtils.create_gdf_from_bounds(
        paper_fill_bounds, CRS_DISPLAY)
    # always from bigger area for correct elevation - and also send to FE při zjištování zoom levelu
    map_scale = Utils.get_scale(GdfUtils.get_bounds_gdf(
        GdfUtils.change_crs(map_area_gdf, CRS_OSM)), paper_dimensions_mm)

    return map_scaling_factor, preview_map_area_gdf, map_area_gdf, map_scale


def paper_dimensions_endpoint(area: WantedArea, paper_dimensions, wanted_orientation, given_smaller_paper_dimension):
    # todo validate area - maybe send area as list of coords directly
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


def generate_map(config: dict[MapConfigKeys, any]) -> None:
    remove_osm_after_load = True
    map_area_gdf = config[MapConfigKeys.MAP_AREA.value]
    try:
        osm_data_preprocessor = OsmDataPreprocessor(
            OSM_INPUT_FILE_NAMES, OSM_TMP_FILE_FOLDER, OSM_OUTPUT_FILE_NAME)
        osm_file = osm_data_preprocessor.extract_areas(
            config[MapConfigKeys.MAP_AREA.value], CRS_OSM)
    except:
        warnings.warn("Error while extracting area from osm file.")
        # set status to error and return
        return

    # ------------Working in display CRS------------

    map_theme, base_config = STYLES.get(
        config[MapConfigKeys.MAP_THEME.value], DEFAULT_STYLE)

    # ------------osm file loading------------
    osm_file_parser = OsmDataParser(
        config[MapConfigKeys.WANTED_CATEGORIES.value]['nodes'],
        config[MapConfigKeys.WANTED_CATEGORIES.value]['nodes_from_area'],
        config[MapConfigKeys.WANTED_CATEGORIES.value]['ways'],
        config[MapConfigKeys.WANTED_CATEGORIES.value]['areas'],
        config[MapConfigKeys.UNWANTED_CATEGORIES.value]['nodes'],
        config[MapConfigKeys.UNWANTED_CATEGORIES.value]['ways'],
        config[MapConfigKeys.UNWANTED_CATEGORIES.value]['areas'],
        nodes_additional_columns=base_config['nodes'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        ways_additional_columns=base_config['ways'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        areas_additional_columns=base_config['areas'][BaseConfigKeys.ADDITIONAL_COLUMNS]
    )

    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        osm_file, CRS_OSM, CRS_DISPLAY)

    if (remove_osm_after_load):
        try:
            os.remove(osm_file)
        except:
            warnings.warn("Error while removing osm file.")

    # ------------gpxs------------
    # from FE

    gpxs_gdf = config[MapConfigKeys.GPXS.value]
    # sixth function - filter loaded data
    if (config[MapConfigKeys.MAP_OUTER_AREA.value] is not None):
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, config[MapConfigKeys.MAP_OUTER_AREA.value])
    else:
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, config[MapConfigKeys.MAP_AREA.value])
    gdfs_convert_loaded_columns(
        gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf, base_config)
    for var_name, var_value in map_theme['variables'].items():
        map_theme['variables'][var_name] = StyleManager.convert_variables_from_dynamic(
            var_value, config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['general'])

    # ------------prefiltering nodes by importance------------
    if (config[MapConfigKeys.PEAKS_FILTER_RADIUS.value] is not None
            and config[MapConfigKeys.PEAKS_FILTER_RADIUS.value] > 0):
        # radius is 1cm on paper * sensitivity
        nodes_gdf = GdfUtils.filter_peaks(
            nodes_gdf,
            config[MapConfigKeys.PEAKS_FILTER_RADIUS.value])
    if (config[MapConfigKeys.MIN_PLACE_POPULATION.value] is not None
            and config[MapConfigKeys.MIN_PLACE_POPULATION.value] > 0):
        nodes_gdf = GdfUtils.filter_place_by_population(
            nodes_gdf, PLACES_TO_FILTER_BY_POPULATION, config[MapConfigKeys.MIN_PLACE_POPULATION.value])

    # seven function - get bg gdf
    # get coastline and determine where is land and where water
    coast_gdf, ways_gdf = GdfUtils.filter_rows(
        ways_gdf, {'natural': 'coastline'}, compl=True)
    bg_gdf = GdfUtils.create_background_gdf(
        map_area_gdf, coast_gdf, map_theme['variables'][MapThemeVariable.WATER_COLOR],
        map_theme['variables'][MapThemeVariable.LAND_COLOR])

    # prepare styles
    process_bridges_and_tunnels(ways_gdf, config[MapConfigKeys.PLOT_BRIDGES.value],
                                config[MapConfigKeys.PLOT_TUNNELS.value])

    ways_gdf = GdfUtils.merge_lines_gdf(ways_gdf, [])
    gpxs_gdf = GdfUtils.merge_lines_gdf(gpxs_gdf, [])
    # assing zoom specific styles
    # eight function - style
    gpxs_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['gpxs'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['general'])
    nodes_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['nodes'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['nodes'])
    ways_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['ways'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['ways'])
    areas_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['areas'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['areas'])
    # combine styles
    gpxs_styles = [*config[MapConfigKeys.GPXS_STYLES.value], *gpxs_styles]
    nodes_styles = [*nodes_styles, 
                    *config[MapConfigKeys.STYLES_SIZE_CHANGES.value]['nodes']]
    ways_styles = [*ways_styles, 
                   *config[MapConfigKeys.STYLES_SIZE_CHANGES.value]['ways']]
    areas_styles = [*areas_styles, 
                    *config[MapConfigKeys.STYLES_SIZE_CHANGES.value]['areas']]

    map_scaling_factor = config[MapConfigKeys.MAP_SCALING_FACTOR.value]
    StyleManager.scale_styles(
        gpxs_styles, map_theme['variables'][MapThemeVariable.GPXS_STYLES_SCALE], map_scaling_factor)
    StyleManager.scale_styles(
        nodes_styles, map_theme['variables'][MapThemeVariable.NODES_STYLES_SCALE], map_scaling_factor)
    StyleManager.scale_styles(
        ways_styles, map_theme['variables'][MapThemeVariable.WAYS_STYLES_SCALE], map_scaling_factor)
    StyleManager.scale_styles(
        areas_styles, map_theme['variables'][MapThemeVariable.AREAS_STYLES_SCALE], map_scaling_factor)

    StyleManager.assign_styles(gpxs_gdf, gpxs_styles)
    StyleManager.assign_styles(
        nodes_gdf, nodes_styles, base_config['nodes'][BaseConfigKeys.DONT_CATEGORIZE])
    StyleManager.assign_styles(
        ways_gdf, ways_styles, base_config['ways'][BaseConfigKeys.DONT_CATEGORIZE])
    StyleManager.assign_styles(
        areas_gdf, areas_styles, base_config['areas'][BaseConfigKeys.DONT_CATEGORIZE])

    # ------------scaling and column calc------------ - to function
    # ninth - prepare/edit styled columns
    gdfs_prepare_styled_columns(gpxs_gdf, nodes_gdf, ways_gdf,
                                areas_gdf, map_scaling_factor, base_config)

    # ------------filter nodes by min req------------
    nodes_gdf = GdfUtils.check_filter_nodes_min_req(nodes_gdf)

    # 10 function - sort
    areas_gdf['area_size'] = areas_gdf.geometry.area
    bg_gdf['area_size'] = bg_gdf.area
    # -----sort-----
    GdfUtils.sort_gdf_by_columns(
        bg_gdf, ['area_size'], ascending=False, na_position='last')

    # sort by population and ele - main sort is by zindex in plotter
    GdfUtils.sort_gdf_by_columns(
        nodes_gdf, ['population', 'prominence', 'ele'], ascending=False, na_position='last')

    # first by area (from biggest to smallest) and then by zindex smallest to biggest
    GdfUtils.sort_gdf_by_columns(
        areas_gdf, ['area_size'], ascending=False, na_position='last')
    GdfUtils.sort_gdf_by_columns(
        areas_gdf, [Style.ZINDEX.value], ascending=True, na_position='first', stable=True)

    # 11 function - plot
    # ------------plot------------
    area_over_ways_filter = map_theme['variables'][MapThemeVariable.AREAS_OVER_WAYS_FILTER]
    areas_over_normal_ways, areas_gdf = GdfUtils.filter_rows(
        areas_gdf,  area_over_ways_filter[0], compl=True)
    areas_as_ways = GdfUtils.filter_rows(
        areas_over_normal_ways, area_over_ways_filter[1])
    if (not areas_as_ways.empty and not ways_gdf.empty):
        ways_gdf = GdfUtils.combine_gdfs([ways_gdf, areas_as_ways])

    plotter = Plotter(map_area_gdf, config[MapConfigKeys.PAPER_DIMENSION_MM.value],
                      map_scaling_factor, TEXT_BOUNDS_OVERFLOW_THRESHOLD, TEXT_WRAP_NAMES_LEN,
                      config[MapConfigKeys.MAP_OUTER_AREA.value],
                      map_theme['variables'][MapThemeVariable.TEXT_BB_EXPAND_PERCENT],
                      map_theme['variables'][MapThemeVariable.MARKER_BB_EXPAND_PERCENT])
    plotter.init(
        map_theme['variables'][MapThemeVariable.LAND_COLOR], bg_gdf)
    plotter.areas(areas_gdf)
    del areas_gdf

    plotter.area_boundary(config[MapConfigKeys.MAP_AREA_BOUNDARY.value],
                          color="black")

    plotter.ways(ways_gdf)
    del ways_gdf
    # must be before nodes
    plotter.gpxs(gpxs_gdf)
    plotter.clip()
    del gpxs_gdf
    plotter.nodes(nodes_gdf, TEXT_WRAP_NAMES_LEN)
    del nodes_gdf

    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()


def get_map_area_gdf(wanted_areas_to_display, boundary=False):
    map_area_gdf = GdfUtils.get_whole_area_gdf(
        wanted_areas_to_display, 'area', CRS_OSM, CRS_DISPLAY)

    if (boundary):
        # ------------store bounds to plot and combine area rows in gdf to 1 row------------
        boundary_map_area_gdf = GdfUtils.get_areas_borders_gdf(
            GdfUtils.filter_rows(map_area_gdf, {'plot': True, 'width': ''}), 'category')
        boundary_map_area_gdf = GdfUtils.map_gdf_column_names(
            boundary_map_area_gdf, REQ_AREAS_MAPPING_DICT)
        GdfUtils.remove_columns(boundary_map_area_gdf, [
                                boundary_map_area_gdf.geometry.name, *REQ_AREAS_MAPPING_DICT.values()], True)
    GdfUtils.remove_columns(map_area_gdf, [
                            map_area_gdf.geometry.name, *REQ_AREAS_MAPPING_DICT.values()], True)
    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)
    if (boundary):
        return map_area_gdf, boundary_map_area_gdf
    return map_area_gdf







@server_app.post("/generate_map", response_model=GeneratorResponseStatusModel)
def normal_map_endpoint(  gpxs: Optional[List[UploadFile]] = File(None),
    config: str = Form(...)):
    try:
        config: MapGeneratorConfigModel = MapGeneratorConfigModel(**json.loads(config))
    except Exception as e:
        return {"message": "Invalid configuration data"}
    # in processing/validation change to wanted and sizes multipiers with filters
    # wanted_categories, size_multipliers = ...
    
    map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
        config.map_area, True)

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = config.paper_dimension_mm
    # from structure
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
        MapConfigKeys.OSM_FILES.value: config.osm_files,
        MapConfigKeys.PEAKS_FILTER_RADIUS.value: peaks_filter_radius,

        # from FE - checked
        MapConfigKeys.MIN_PLACE_POPULATION.value: config.min_place_population,
        MapConfigKeys.MAP_THEME.value: config.map_theme,
        MapConfigKeys.PLOT_BRIDGES.value: True,
        MapConfigKeys.PLOT_TUNNELS.value: True,
        MapConfigKeys.WANTED_CATEGORIES.value: config.wanted_categories.dict(),
        MapConfigKeys.UNWANTED_CATEGORIES.value: config.unwanted_categories.dict(),
        MapConfigKeys.STYLES_ZOOM_LEVELS.value: config.styles_zoom_levels.dict(),
        MapConfigKeys.STYLES_SIZE_CHANGES.value: {'nodes': [], 'ways': [], 'areas': []},
        MapConfigKeys.GPXS_STYLES.value: config.gpxs_styles,
    }
    generate_map(map_generator_config)
    # and run function to generate map


def preview_map_endpoint():
    # todo check for exceptions, change paper dimensions from list to tuple
    # area - big area with all settings
    # preview_area - area to display
    # todo from wanted categories get also size multiplier with filters and edit that categories
    map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
        AREA, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")

    map_area_gdf, boundary_map_area_gdf = get_map_area_gdf(
        map_area, True)
    preview_input_files = OSM_INPUT_FILE_NAMES
    if (PREVIEW_AREA is None):
        preview_map_area_gdf = map_area_gdf.copy()
    else:
        preview_map_area = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
            PREVIEW_AREA, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")
        preview_map_area_gdf = get_map_area_gdf(
            preview_map_area, False)
    paper_dim = PREVIEW_PAPER_DIMENSIONS
    preview_dim = PAPER_DIMENSIONS
    
    fit_paper_size = True

    (map_scaling_factor, preview_map_area_gdf, map_area_gdf,
     map_scale) = calc_preview(map_area_gdf, paper_dim, fit_paper_size, preview_map_area_gdf, preview_dim)

    preview_map_area_gdf = GdfUtils.change_crs(
        preview_map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)

    peaks_filter_radius = map_scale * 10 * PEAKS_FILTER_SENSITIVITY
    gpx_manager = GpxManager(GPX_FOLDER, CRS_DISPLAY)
    gpxs_gdf = gpx_manager.get_gpxs_gdf()

    # config for map generator
    map_generator_config = {
        MapConfigKeys.MAP_AREA.value: preview_map_area_gdf,
        MapConfigKeys.MAP_AREA_BOUNDARY.value: boundary_map_area_gdf,
        MapConfigKeys.MAP_OUTER_AREA.value: map_area_gdf,
        MapConfigKeys.MAP_SCALING_FACTOR.value: map_scaling_factor,
        MapConfigKeys.PAPER_DIMENSION_MM.value: preview_dim,
        MapConfigKeys.OSM_FILES.value: preview_input_files,
        MapConfigKeys.PEAKS_FILTER_RADIUS.value: peaks_filter_radius,
        MapConfigKeys.MIN_PLACE_POPULATION.value: MIN_POPULATION,
        MapConfigKeys.MAP_THEME.value: MAP_STYLE_THEME,
        MapConfigKeys.PLOT_BRIDGES.value: True,
        MapConfigKeys.PLOT_TUNNELS.value: True,
        MapConfigKeys.WANTED_CATEGORIES.value: {'nodes': wanted_nodes, 'nodes_from_area': wanted_nodes_from_area, 'ways': wanted_ways, 'areas': wanted_areas},
        MapConfigKeys.UNWANTED_CATEGORIES.value: {'nodes': unwanted_nodes_tags, 'ways': unwanted_ways_tags, 'areas': unwanted_areas_tags},
        MapConfigKeys.STYLES_ZOOM_LEVELS.value: {'nodes': 5, 'ways': 5, 'areas': 5, 'general': 5},
        MapConfigKeys.STYLES_SIZE_CHANGES.value: {'nodes': [], 'ways': [], 'areas': []},
        MapConfigKeys.GPXS.value: gpxs_gdf,
        MapConfigKeys.GPXS_STYLES.value: [],
    }
    generate_map(map_generator_config)


@time_measurement("main")
def main() -> None:
    # normal_map_endpoint()
    # ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
    #     AREA, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")
    allowed_structure = {
        'nodes': {
            'place': ['peak', 'tower'],
            'location': ['city', 'town']
        },
        'areas_as_nodes': {
            'place': ['peak', 'tower']
        },
        'ways': {},
        'areas': {
            'buildings': True,  # True means any tag is allowed
            'leisure': {'farmland':"asd"}
        },
    }
    valid_data = {
        "nodes": {
            "place": {
                "tower": {"width_scale": 0.2},
                "peak": {"width_scale": 1, 'width_scale': 3}
            }
        },
        "areas": {
            "leisure": {'farmland': {'text_font_size_scale': 3}},
            "buildings": {"width_scale": 2, 'text_font_size_scale': 3},

        },
        "ways": {},
    }
    # preview_map_endpoint()
  
    print(ReceivedStructureProcessor.validate_wanted_elements_and_styles(valid_data, allowed_structure, FE_EDIT_STYLES_VALIDATION))
    one, twe = ReceivedStructureProcessor.transform_to_backend_structures(valid_data, FE_EDIT_STYLES_VALIDATION.keys(),
                                                                          ['nodes', 'ways', 'areas'], FE_EDIT_STYLES_MAPPING)
    print(one)
    print(twe)

if __name__ == "__main__":
    main()
