import warnings

from config import *
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
    # ----gpx----
    # gpx - is needed in this? will be setted in FE?

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


def calc_preview(map_area_gdf, paper_dimensions_mm):
    """
        NOTE: using constants from config file
    Args:
        map_area_gdf (_type_): _description_
        paper_dimensions_mm (_type_): _description_

    Returns:
        _type_: _description_
    """
    wanted_outer_areas_to_display = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
        OUTER_AREA, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")
    outer_map_area_gdf = GdfUtils.get_whole_area_gdf(
        wanted_outer_areas_to_display, 'area', CRS_OSM, CRS_DISPLAY)
    outer_map_area_gdf = GdfUtils.combine_rows_gdf(outer_map_area_gdf)
    outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_map_area_gdf)
    # map in meters for calc automatic orientation and same pdf sides proportions
    outer_paper_dimensions_mm = Utils.adjust_paper_dimensions(outer_map_area_dimensions, OUTER_PAPER_DIMENSIONS,
                                                              OUTER_GIVEN_SMALLER_PAPER_DIMENSION,
                                                              OUTER_WANTED_ORIENTATION)
    if (OUTER_FIT_PAPER_SIZE):
        outer_map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            outer_map_area_gdf, outer_paper_dimensions_mm)
        outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(
            outer_map_area_gdf)
        # for testing - should be same as normal area after preview calc
    # outer map scale
        # outer_map_area_bounds = GdfUtils.get_bounds_gdf(GdfUtils.change_crs(outer_map_area_gdf, CRS_OSM)) # real scale cacl
        # map_scale = Utils.get_scale(outer_map_area_bounds, outer_paper_dimensions_mm)
    map_scaling_factor = Utils.calc_map_scaling_factor(
        outer_map_area_dimensions, outer_paper_dimensions_mm)
    # calc map factor for creating automatic array with wanted elements - for preview area (without area_zoom_preview)
    # ?? to doc - need because it will clip by required area - and that will be some big area in not clipping (cant use only first approach)
    # ?? req area je potom velká jako pdf stránka (přes celou stránku) a ne jako puvodně chtěná oblast a tedy by k žádnému zaříznutí nedošlo
    # map_area_gdf = needs to be in display cords
    # calc bounds so area_zoom_preview will be 1 and will fill whole paper
    paper_fill_bounds = Utils.calc_bounds_to_fill_paper_with_ratio(map_area_gdf.union_all().centroid,
                                                                   paper_dimensions_mm, outer_map_area_dimensions,
                                                                   outer_paper_dimensions_mm)
    # area will be changing -> create copy for bounds plotting
    map_area_gdf = GdfUtils.create_gdf_from_bounds(
        paper_fill_bounds, CRS_DISPLAY)

    return map_scaling_factor, map_area_gdf, outer_map_area_gdf

# will get all as normal area - only preview endpoint will be different


def zoom_level_endpoint(area: WantedArea, paper_dimensions_mm):
    map_area_gdf = GdfUtils.get_whole_area_gdf(
        area, 'area', CRS_OSM, CRS_DISPLAY)
    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, paper_dimensions_mm,
                                                        GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)

    if (FIT_PAPER_SIZE):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

    map_scaling_factor = Utils.calc_map_scaling_factor(map_area_dimensions,
                                                       paper_dimensions_mm)

    zoom_level = Utils.get_zoom_level(
        map_scaling_factor, ZOOM_MAPPING, 0.3)
    print(map_scaling_factor, zoom_level)


@time_measurement("main")
def main() -> None:
    # one function
    remove_extracted_output_file = (
        OUTPUT_PDF_NAME == None and OSM_WANT_EXTRACT_AREA)
    # convert and validate formats from FE - and handle exceptions
    wanted_areas_to_display = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
        AREA, allowed_keys_and_types=REQ_AREA_DICT_KEYS, key_with_area="area")
    map_theme, base_config = STYLES.get(MAP_STYLE_THEME, DEFAULT_STYLE)

    # second function
    # if are for preview is not specified, use whole area
    if (WANT_PREVIEW and AREA == None):
        # will not happen in preview
        map_area_gdf = GdfUtils.get_whole_area_gdf(
            OUTER_AREA, 'area', CRS_OSM, CRS_DISPLAY)
    else:
        map_area_gdf = GdfUtils.get_whole_area_gdf(
            wanted_areas_to_display, 'area', CRS_OSM, CRS_DISPLAY)

    # ------------store bounds to plot and combine area rows in gdf to 1 row------------
    # store only areas for ploting with category and width
    boundary_map_area_gdf = GdfUtils.get_areas_borders_gdf(
        GdfUtils.filter_rows(map_area_gdf, {'plot': True, 'width': ''}), 'category')
    boundary_map_area_gdf = GdfUtils.map_gdf_column_names(
        boundary_map_area_gdf, REQ_AREAS_MAPPING_DICT)
    GdfUtils.remove_columns(boundary_map_area_gdf, [
                            boundary_map_area_gdf.geometry.name, *REQ_AREAS_MAPPING_DICT.values()], True)

    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)

    # third function - scalingfactor, maparea, ooutermaparea, scale, zoomlevel
    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, PAPER_DIMENSIONS,
                                                        GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)

    if (WANT_PREVIEW):
        # one endpoint
        (map_scaling_factor,
            map_area_gdf, outer_map_area_gdf) = calc_preview(map_area_gdf, paper_dimensions_mm)
    else:
        # another endpoint
        if (FIT_PAPER_SIZE):
            map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
                map_area_gdf, paper_dimensions_mm)
            map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

            if (FIT_PAPER_SIZE_BOUNDS_PLOT):
                boundary_map_area_gdf = GdfUtils.combine_gdfs(
                    [boundary_map_area_gdf, map_area_gdf.copy()])
        outer_map_area_gdf = None

        map_scaling_factor = Utils.calc_map_scaling_factor(map_area_dimensions,
                                                           paper_dimensions_mm)
    map_scale = Utils.get_scale(GdfUtils.get_bounds_gdf(
        GdfUtils.change_crs(map_area_gdf, CRS_OSM)), paper_dimensions_mm)
    # zoom level to endpoint specific - always from that biger area
    zoom_level = Utils.get_zoom_level(
        map_scaling_factor, ZOOM_MAPPING, 0.3)
    print(map_scaling_factor, zoom_level)
    # zoom_level_endpoint(OUTER_AREA if WANT_PREVIEW == True else wanted_areas_to_display,
    #                     OUTER_PAPER_DIMENSIONS if WANT_PREVIEW == True else PAPER_DIMENSIONS)

    # fifth function - parse osm file and get gdfs and than remove osm file
    # ------------get elements from osm file------------
    remove_osm_after_load = False
    try:
        if (OSM_WANT_EXTRACT_AREA):
            if not shutil.which('osmium'):
                warnings.warn("osmium is NOT installed")
                return
            remove_osm_after_load = True if OSM_OUTPUT_FILE_NAME is None else False
            
            osm_data_preprocessor = OsmDataPreprocessor(
                OSM_INPUT_FILE_NAMES, OSM_TMP_FOLDER, OSM_OUTPUT_FILE_NAME)
            osm_file_name = osm_data_preprocessor.extract_areas(
                map_area_gdf, CRS_OSM)
        else:
            osm_file_name = OSM_INPUT_FILE_NAMES[0]
    except:
        warnings.warn("Error while extracting area from osm file.")
        # pass err to fe
        return
    # ------------Working in display CRS------------
    map_area_gdf = GdfUtils.change_crs(map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)
    # prepare style dict

    # ------------osm file loading------------
    osm_file_parser = OsmDataParser(
        wanted_nodes, wanted_nodes_from_area, wanted_ways, wanted_areas,
        unwanted_nodes_tags, unwanted_ways_tags, unwanted_areas_tags,
        nodes_additional_columns=base_config['nodes'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        ways_additional_columns=base_config['ways'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        areas_additional_columns=base_config['areas'][BaseConfigKeys.ADDITIONAL_COLUMNS]
    )

    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        osm_file_name, CRS_OSM, CRS_DISPLAY)

    if (remove_osm_after_load):
        try:
            os.remove(osm_file_name)
        except:
            warnings.warn("Error while removing osm file.")

    # ------------gpxs------------
    # from FE
    gpx_manager = GpxManager(GPX_FOLDER, CRS_DISPLAY)
    gpxs_gdf = gpx_manager.get_gpxs_gdf()

    # sixth function - filter loaded data
    if (outer_map_area_gdf is not None):
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, outer_map_area_gdf)
    else:
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, map_area_gdf)
    gdfs_convert_loaded_columns(
        gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf, base_config)
    for var_name, var_value in map_theme['variables'].items():
        map_theme['variables'][var_name] = StyleManager.convert_variables_from_dynamic(
            var_value, zoom_level)

    # ------------prefiltering nodes by importance------------
    if (PEAKS_FILTER_SENSITIVITY is not None):
        # make distance 10* more than scale and prominence 10* less than scale
        nodes_gdf = GdfUtils.filter_peaks_by_prominence(
            nodes_gdf, map_scale*10*PEAKS_FILTER_SENSITIVITY, map_scale /
            10*(PEAKS_FILTER_SENSITIVITY/2),
            ELE_PROMINENCE_MAX_DIFF_RATIO)
    if (MIN_POPULATION is not None):
        nodes_gdf = GdfUtils.filter_place_by_population(
            nodes_gdf, PLACES_TO_FILTER_BY_POPULATION, MIN_POPULATION)

    # seven function - get bg gdf
    # get coastline and determine where is land and where water
    coast_gdf, ways_gdf = GdfUtils.filter_rows(
        ways_gdf, {'natural': 'coastline'}, compl=True)
    bg_gdf = GdfUtils.create_background_gdf(
        map_area_gdf, coast_gdf, map_theme['variables'][MapThemeVariable.WATER_COLOR],
        map_theme['variables'][MapThemeVariable.LAND_COLOR])

    # prepare styles
    process_bridges_and_tunnels(ways_gdf, PLOT_BRIDGES, PLOT_TUNNELS)

    ways_gdf = GdfUtils.merge_lines_gdf(ways_gdf, [])
    gpxs_gdf = GdfUtils.merge_lines_gdf(gpxs_gdf, [])
    # assing zoom specific styles
    # eight function - style
    gpxs_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['gpxs'], WAYS_STYLE_ZOOM_LEVEL)
    nodes_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['nodes'], NODES_STYLE_ZOOM_LEVEL)
    ways_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['ways'], WAYS_STYLE_ZOOM_LEVEL)
    areas_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['areas'], AREAS_STYLE_ZOOM_LEVEL)

    if (map_theme['variables'][MapThemeVariable.GPXS_STYLES_SCALE]):
        StyleManager.scale_styles(
            gpxs_styles, map_theme['variables'][MapThemeVariable.GPXS_STYLES_SCALE], map_scaling_factor)
    if (map_theme['variables'][MapThemeVariable.NODES_STYLES_SCALE]):
        StyleManager.scale_styles(
            nodes_styles, map_theme['variables'][MapThemeVariable.NODES_STYLES_SCALE], map_scaling_factor)
    if (map_theme['variables'][MapThemeVariable.WAYS_STYLES_SCALE]):
        StyleManager.scale_styles(
            ways_styles, map_theme['variables'][MapThemeVariable.WAYS_STYLES_SCALE], map_scaling_factor)
    if (map_theme['variables'][MapThemeVariable.AREAS_STYLES_SCALE]):
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
    # todo add checks for errors in plotting
    area_over_ways_filter = map_theme['variables'][MapThemeVariable.AREAS_OVER_WAYS_FILTER]
    areas_over_normal_ways, areas_gdf = GdfUtils.filter_rows(
        areas_gdf,  area_over_ways_filter[0], compl=True)
    areas_as_ways = GdfUtils.filter_rows(
        areas_over_normal_ways, area_over_ways_filter[1])
    if (not areas_as_ways.empty and not ways_gdf.empty):
        ways_gdf = GdfUtils.combine_gdfs([ways_gdf, areas_as_ways])

    plotter_settings = {"map_area_gdf": map_area_gdf, "paper_dimensions_mm": paper_dimensions_mm,
                        "map_scaling_factor": map_scaling_factor, "text_bounds_overflow_threshold": TEXT_BOUNDS_OVERFLOW_THRESHOLD,
                        "text_wrap_names_len": TEXT_WRAP_NAMES_LEN, "outer_map_area_gdf": outer_map_area_gdf,
                        "map_bg_color": map_theme['variables'][MapThemeVariable.LAND_COLOR]}

    plotter = Plotter(map_area_gdf, paper_dimensions_mm,
                      map_scaling_factor, TEXT_BOUNDS_OVERFLOW_THRESHOLD, TEXT_WRAP_NAMES_LEN, outer_map_area_gdf,
                      map_theme['variables'][MapThemeVariable.TEXT_BB_EXPAND_PERCENT],
                      map_theme['variables'][MapThemeVariable.MARKER_BB_EXPAND_PERCENT])
    plotter.init(
        map_theme['variables'][MapThemeVariable.LAND_COLOR], bg_gdf)
    plotter.areas(areas_gdf)
    del areas_gdf
    if (not boundary_map_area_gdf.empty):
        plotter.area_boundary(boundary_map_area_gdf,
                              color="black")

    del boundary_map_area_gdf

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


if __name__ == "__main__":
    main()
