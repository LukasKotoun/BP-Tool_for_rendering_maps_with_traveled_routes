
import uuid
from typing import Any

from config import *
from common.map_enums import ProcessingStatus
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_parser import OsmDataParser
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.style_assigner import StyleManager
from modules.plotter import Plotter
from modules.gpx_manager import GpxManager
from modules.received_structure_processor import ReceivedStructureProcessor
import os
from datetime import datetime


def get_map_area_gdf(wanted_areas_to_display, boundary=False):
    map_area_gdf = GdfUtils.get_whole_area_gdf(
        wanted_areas_to_display, 'area', CRS_OSM, CRS_DISPLAY)

    if (boundary):
        # ------------store bounds to plot and combine area rows in gdf to 1 row------------
        boundary_map_area_gdf = GdfUtils.get_areas_borders_gdf(
            GdfUtils.filter_rows(map_area_gdf, {'plot': True, 'width': ''}), 'category')
        boundary_map_area_gdf = GdfUtils.map_gdf_column_names(
            boundary_map_area_gdf, REQ_AREAS_KEYS_MAPPING_DICT)
        GdfUtils.remove_columns(boundary_map_area_gdf, [
                                boundary_map_area_gdf.geometry.name, *REQ_AREAS_KEYS_MAPPING_DICT.values()], True)
    GdfUtils.remove_columns(map_area_gdf, [
                            map_area_gdf.geometry.name, *REQ_AREAS_KEYS_MAPPING_DICT.values()], True)
    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)
    if (boundary):
        return map_area_gdf, boundary_map_area_gdf
    return map_area_gdf


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


def gdfs_prepare_styled_columns(gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf, config):

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
        Style.FE_WIDTH_SCALE.value])

    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
        Style.EDGE_WIDTH_RATIO.value])
    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGE_WIDTH_DASHED_CONNECT.value, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value, [
        Style.WIDTH.value])
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_WIDTH.value, Style.WIDTH.value, [# calc bridge size only for bridges
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


def generate_map(config: dict[MapConfigKeys, any], task_id: str, shared_dict: dict[Any, Any], lock) -> None:
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.EXTRACTING.value
        }
        
    remove_osm_after_load = False if OSM_OUTPUT_FOLDER_FILE_NAME is not None else True
    map_area_gdf = config[MapConfigKeys.MAP_AREA.value]
    try:
        osm_data_preprocessor = OsmDataPreprocessor(
            config[MapConfigKeys.OSM_FILES.value], OSM_TMP_FILE_FOLDER, task_id, OSM_OUTPUT_FOLDER_FILE_NAME)
        with lock:
            shared_dict[task_id] = {
                **shared_dict[task_id],  # Keep the existing keys and values
                'files': [*shared_dict[task_id]['files'], osm_data_preprocessor.osm_output_file],
            }
        osm_file = osm_data_preprocessor.extract_areas(
            config[MapConfigKeys.MAP_AREA.value], CRS_OSM)
    except:
        warnings.warn("Error while extracting area from osm file.")
        # set status to error and return
        return

    # ------------Working in display CRS------------
    wanted_categories, styles_size_edits = ReceivedStructureProcessor.transform_to_backend_structures(
        config[MapConfigKeys.WANTED_CATEGORIES_AND_STYLES_CHANGES.value], FE_EDIT_STYLES_VALIDATION.keys(),
        FE_STYLES_ALLOWED_ELEMENTS, FE_EDIT_STYLES_MAPPING)
    
    map_theme, base_config = STYLES.get(
        config[MapConfigKeys.MAP_THEME.value], DEFAULT_STYLE)
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.LOADING.value
        }
    # get categories that are in wanted and also should be loaded from areas
    wanted_nodes_from_area = {
        key: [value for value in wanted_categories['nodes'][key] if value in NODES_ALSO_FROM_AREA[key]]
        for key in wanted_categories['nodes'] if key in NODES_ALSO_FROM_AREA
    }
    # ------------osm file loading------------
    osm_file_parser = OsmDataParser(
        wanted_categories['nodes'],
        wanted_nodes_from_area,
        {**wanted_categories['ways'], **MANDATORY_WAYS},
        wanted_categories['areas'],
        nodes_additional_columns=base_config['nodes'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        ways_additional_columns=base_config['ways'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        areas_additional_columns=base_config['areas'][BaseConfigKeys.ADDITIONAL_COLUMNS]
    )

    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        osm_file, CRS_OSM, CRS_DISPLAY)
    print(shared_dict[task_id])
    if (remove_osm_after_load):
        Utils.remove_file(osm_file)
        shared_dict[task_id] = {
                **shared_dict[task_id],
                'files': [file for file in shared_dict[task_id]['files'] if file != osm_file],
            }
    print(shared_dict[task_id])

    # ------------gpxs------------
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.FILTERING.value
        }

    gpxs_gdf = config[MapConfigKeys.GPXS.value]
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

    # get coastline and determine where is land and where water
    coast_gdf, ways_gdf = GdfUtils.filter_rows(
        ways_gdf, {'natural': 'coastline'}, compl=True)
    bg_gdf = GdfUtils.create_background_gdf(
        map_area_gdf, coast_gdf, map_theme['variables'][MapThemeVariable.WATER_COLOR],
        map_theme['variables'][MapThemeVariable.LAND_COLOR])

    # prepare styles
    process_bridges_and_tunnels(ways_gdf, config[MapConfigKeys.PLOT_BRIDGES.value],
                                config[MapConfigKeys.PLOT_TUNNELS.value])
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.STYLING.value
        }
    ways_gdf = GdfUtils.merge_lines_gdf(ways_gdf, [])

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
    nodes_styles = [*nodes_styles, *styles_size_edits['nodes']]
    ways_styles = [*ways_styles, *styles_size_edits['ways']]
    areas_styles = [*areas_styles, *styles_size_edits['areas']]

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
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.PREPARING_FOR_PLOTTING.value
        }
    # ninth - prepare/edit styled columns
    gdfs_prepare_styled_columns(gpxs_gdf, nodes_gdf, ways_gdf,
                                areas_gdf, base_config)

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
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.AREAS_PLOTTING.value
        }
    plotter.areas(areas_gdf)
    del areas_gdf

    plotter.area_boundary(config[MapConfigKeys.MAP_AREA_BOUNDARY.value],
                          color="black")
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.WAYS_PLOTTING.value
        }
    plotter.ways(ways_gdf)
    del ways_gdf
    # must be before nodes
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.GPXS_PLOTTING.value
        }
    plotter.gpxs(gpxs_gdf)
    plotter.clip()
    del gpxs_gdf

    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],  # Keep the existing keys and values
            'status': ProcessingStatus.NODES_PLOTTING.value
        }

    plotter.nodes(nodes_gdf, TEXT_WRAP_NAMES_LEN)
    del nodes_gdf

    if (OUTPUT_PDF_FOLDER_FILE_NAME is None):
        if not os.path.exists(OUTPUT_PDF_FOLDER):
            os.makedirs(OUTPUT_PDF_FOLDER)
        folder = OUTPUT_PDF_FOLDER
        if (OUTPUT_PDF_FOLDER[-1] != '/'):
            folder += OUTPUT_PDF_FOLDER + '/'
        pdf_name = f'{folder}map_{task_id}.pdf'
    else:
        pdf_name = OUTPUT_PDF_FOLDER_FILE_NAME

    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            'files': [*shared_dict[task_id]['files'], pdf_name],
            'status':  ProcessingStatus.FILE_SAVING.value
        }
    plotter.generate_pdf(pdf_name)

