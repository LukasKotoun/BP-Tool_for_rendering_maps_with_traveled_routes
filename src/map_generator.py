import warnings

from config import *
from styles.mapycz_style import GENERAL_DEFAULT_STYLES, STYLES, GPXS_STYLES, OCEAN_WATER
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.osm_data_parser import OsmDataParser
from modules.style_assigner import StyleAssigner
from modules.plotter import Plotter
from modules.gpx_manager import GpxManager
from modules.received_structure_processor import ReceivedStructureProcessor

from common.common_helpers import time_measurement

# todo some class or utils..
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


def gdfs_convert_loaded_columns(gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf):
    GdfUtils.change_columns_to_numeric(nodes_gdf, NODES_NUMERIC_COLUMNS)
    GdfUtils.convert_numeric_columns_int(nodes_gdf, NODES_NUMERIC_COLUMNS)

    GdfUtils.change_columns_to_numeric(ways_gdf, WAYS_NUMERIC_COLUMNS)
    GdfUtils.convert_numeric_columns_int(ways_gdf, WAYS_ROUND_COLUMNS)

    GdfUtils.change_columns_to_numeric(areas_gdf, AREA_NUMERIC_COLUMNS)
    GdfUtils.convert_numeric_columns_int(areas_gdf, AREA_ROUND_COLUMNS)

    
def gdfs_prepare_styled_columns(gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf, map_object_scaling_factor):
    # ----gpx----
    # gpx - is needed in this? will be setted in FE?
    # GdfUtils.multiply_column_gdf(gpxs_gdf, Style.WIDTH.name, [
    #                              Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name], map_object_scaling_factor)



    GdfUtils.create_derivated_columns(gpxs_gdf, Style.EDGEWIDTH.name, Style.WIDTH.name, [
                                      Style.EDGE_WIDTH_RATIO.name])
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.START_MARKER_EDGEWIDTH.name, Style.START_MARKER_WIDHT.name, [
                                      Style.START_MARKER_EDGE_RATIO.name])
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.FINISH_MARKER_EDGEWIDTH.name, Style.FINISH_MARKER_WIDHT.name, [
                                      Style.FINISH_MARKER_EDGE_RATIO.name])
    
    # ----nodes----
    # set base width - scale by muplitpliers and object scaling factor

    GdfUtils.fill_nan_values(nodes_gdf, [Style.ZINDEX.name], 0)
    
    GdfUtils.multiply_column_gdf(nodes_gdf, Style.WIDTH.name, [
        Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name], None)
    GdfUtils.multiply_column_gdf(nodes_gdf, Style.TEXT_FONT_SIZE.name, [
        Style.TEXT_FONT_SIZE_SCALE.name, Style.FE_TEXT_FONT_SIZE_SCALE.name], None)
    # text outline
    GdfUtils.create_derivated_columns(nodes_gdf, Style.TEXT_OUTLINE_WIDTH.name, Style.TEXT_FONT_SIZE.name, [
                                      Style.TEXT_OUTLINE_WIDTH_RATIO.name])

    # edge - MARKERs size and ways width
    GdfUtils.create_derivated_columns(nodes_gdf, Style.EDGEWIDTH.name, Style.WIDTH.name, [
                                      # ?? maybe remove ...
                                      Style.EDGE_WIDTH_RATIO.name])
    old_column_remove = []
    for filter, new_column, old_column, fill in DERIVATE_COLUMNS_NODES:
        GdfUtils.create_derivated_columns(
            nodes_gdf, new_column, old_column, filter=filter, fill=fill)
        # old_column_remove.append(old_column)
    # call wrap text - by styles or other struct?

    # remove columns used for calculating
    GdfUtils.remove_columns(nodes_gdf, [Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name,
                                        Style.TEXT_FONT_SIZE_SCALE.name, Style.FE_TEXT_FONT_SIZE_SCALE.name,
                                        Style.EDGE_WIDTH_RATIO.name, Style.TEXT_OUTLINE_WIDTH_RATIO.name, *old_column_remove])

    # ----ways----

    GdfUtils.fill_nan_values(ways_gdf, [Style.ZINDEX.name], -1)

    GdfUtils.multiply_column_gdf(ways_gdf, Style.WIDTH.name, [
        # if i will be creationg function with continues width scaling than multiply only by FEwidthscale
        Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name], map_object_scaling_factor)

    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGEWIDTH.name, Style.WIDTH.name, [
        Style.EDGE_WIDTH_RATIO.name])
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_WIDTH.name, Style.WIDTH.name, [     # calc bridge size only for bridges
                                      Style.BRIDGE_WIDTH_RATIO.name], {'bridge': ''})
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_EDGE_WIDTH.name, Style.BRIDGE_WIDTH.name, [
                                      Style.BRIDGE_EDGE_WIDTH_RATIO.name], {'bridge': ''})

    for filter, new_column, old_column in DERIVATE_COLUMNS_WAYS:
        GdfUtils.create_derivated_columns(
            ways_gdf, new_column, old_column, filter=filter)

    GdfUtils.remove_columns(ways_gdf, [Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name,
                                       Style.EDGE_WIDTH_RATIO.name, Style.BRIDGE_WIDTH_RATIO.name, Style.BRIDGE_EDGE_WIDTH_RATIO.name])

    # ----areas----
    GdfUtils.multiply_column_gdf(areas_gdf, Style.WIDTH.name, [
        Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name], map_object_scaling_factor)

    GdfUtils.create_derivated_columns(areas_gdf, Style.EDGEWIDTH.name, Style.WIDTH.name, [
                                      Style.EDGE_WIDTH_RATIO.name])

    for filter, new_column, old_column in DERIVATE_COLUMNS_AREAS:
        GdfUtils.create_derivated_columns(
            areas_gdf, new_column, old_column, filter=filter)
        
    GdfUtils.fill_nan_values(areas_gdf, [Style.ZINDEX.name], -1)
    GdfUtils.remove_columns(areas_gdf, [Style.WIDTH_SCALE.name, Style.FE_WIDTH_SCALE.name,
                                        Style.EDGE_WIDTH_RATIO.name])


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
        OUTER_AREA, allowed_keys_and_types=AREA_DICT_KEYS, key_with_area="area")
    outer_map_area_gdf = GdfUtils.get_whole_area_gdf(
        wanted_outer_areas_to_display, 'area', CRS_OSM, CRS_DISPLAY)
    outer_map_area_gdf = GdfUtils.combine_rows_gdf(
        outer_map_area_gdf, CRS_DISPLAY)

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
    #outer map scale
            # outer_map_area_bounds = GdfUtils.get_bounds_gdf(GdfUtils.change_crs(outer_map_area_gdf, CRS_OSM)) # real scale cacl
            # map_scale = Utils.get_scale(outer_map_area_bounds, outer_paper_dimensions_mm)
            # print(map_scale)
    map_object_scaling_factor = Utils.calc_map_object_scaling_factor(
        outer_map_area_dimensions, outer_paper_dimensions_mm)
    # calc map factor for creating automatic array with wanted elements - for preview area (without area_zoom_preview)
    # ?? to doc - need because it will clip by required area - and that will be some big area in not clipping (cant use only first approach)
    # ?? req area je potom velká jako pdf stránka (přes celou stránku) a ne jako puvodně chtěná oblast a tedy by k žádnému zaříznutí nedošlo
    # calc bounds so area_zoom_preview will be 1 and will fill whole paper
    paper_fill_bounds = Utils.calc_bounds_to_fill_paper_with_ratio(map_area_gdf.union_all().centroid,
                                                                   paper_dimensions_mm, outer_map_area_dimensions,
                                                                   outer_paper_dimensions_mm)
    # area will be changing -> create copy for bounds plotting
    map_area_gdf = GdfUtils.create_gdf_from_bounds(
        paper_fill_bounds, CRS_DISPLAY)
  
    return map_object_scaling_factor, map_area_gdf, outer_map_area_gdf


@time_measurement("main")
def main() -> None:
    remove_extracted_output_file = (OUTPUT_PDF_NAME == None and OSM_WANT_EXTRACT_AREA)
    # convert and validate formats from FE - and handle exceptions
    wanted_areas_to_display = ReceivedStructureProcessor.validate_and_convert_areas_strucutre(
        AREA, allowed_keys_and_types=AREA_DICT_KEYS, key_with_area="area")

    # if are for preview is not specified, use whole area
    if (WANT_PREVIEW and AREA == None):
        # will not happen in preview
        map_area_gdf = GdfUtils.get_whole_area_gdf(
            OUTER_AREA, 'area', CRS_OSM, CRS_DISPLAY)
    else:
        map_area_gdf = GdfUtils.get_whole_area_gdf(
            wanted_areas_to_display, 'area', CRS_OSM, CRS_DISPLAY)

    # ------------store bounds to plot and combine area rows in gdf to 1 row------------
    boundary_map_area_gdf = GdfUtils.get_areas_borders_gdf(
        GdfUtils.filter_rows(map_area_gdf, {'plot': True}), 'category')
    boundary_map_area_gdf = GdfUtils.map_gdf_column_names(
        boundary_map_area_gdf, AREAS_MAPPING_DICT)
    GdfUtils.remove_columns(boundary_map_area_gdf, [
                            boundary_map_area_gdf.geometry.name, *AREAS_MAPPING_DICT.values()], True)

    # todo edit or remove ...
    # boundary_map_area_gdf = GdfUtils.remove_common_boundary_inaccuracy(
    #     boundary_map_area_gdf)

    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, CRS_DISPLAY)
    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, PAPER_DIMENSIONS,
                                                        GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)


    if (WANT_PREVIEW):
        # one endpoint
        (map_object_scaling_factor,
            map_area_gdf, outer_map_area_gdf) = calc_preview(map_area_gdf, paper_dimensions_mm)
    else:
        # another endpoint
        if (FIT_PAPER_SIZE):
            map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
                map_area_gdf, paper_dimensions_mm)
            map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
 
            if(FIT_PAPER_SIZE_BOUNDS_PLOT):
                boundary_map_area_gdf = GdfUtils.combine_gdfs(
                    [boundary_map_area_gdf, map_area_gdf.copy()])
        outer_map_area_gdf = None
        # - map scale in real size
        # - scaling factor and for zoom calc in webmercato
        map_object_scaling_factor = Utils.calc_map_object_scaling_factor(map_area_dimensions,
                                                                        paper_dimensions_mm)
    map_area_bounds = GdfUtils.get_bounds_gdf(GdfUtils.change_crs(map_area_gdf, CRS_OSM))
    map_scale = Utils.get_scale(map_area_bounds, paper_dimensions_mm)
    print(map_scale)
    zoom_level = Utils.get_zoom_level(
        map_object_scaling_factor, ZOOM_MAPPING, 0.1)
    print(f"Zoom level: {zoom_level}")

    # ------------get elements from osm file------------
    try:
        if (OSM_WANT_EXTRACT_AREA):
            # todo check if osmium is instaled else return?
            osm_data_preprocessor = OsmDataPreprocessor(
                OSM_INPUT_FILE_NAMES, OSM_OUTPUT_FILE_NAME)
            osm_file_name = osm_data_preprocessor.extract_areas(
                map_area_gdf, CRS_OSM)
        else:
            osm_file_name = OSM_INPUT_FILE_NAMES[0]
    except:
        warnings.warn("Error while extracting area from osm file.")
        return
    # ------------Working in display CRS------------
    map_area_gdf = GdfUtils.change_crs(map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)
    # reqired_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
    # if (not GdfUtils.are_gdf_geometry_inside_geometry(gpxs_gdf, reqired_area_polygon)):
    #     warnings.warn("Some gpx files are not whole inside selected map area.")

    # ------------osm file loading------------
    osm_file_parser = OsmDataParser(
        wanted_nodes, wanted_ways, wanted_areas,
        unwanted_nodes_tags, unwanted_ways_tags, unwanted_areas_tags, area_additional_columns=AREA_ADDITIONAL_COLUMNS,
        node_additional_columns=NODES_ADDITIONAL_COLUMNS, way_additional_columns=WAYS_ADDITIONAL_COLUMNS)
    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        osm_file_name, CRS_OSM, CRS_DISPLAY)

    # ------------gpxs------------
    # from FE
    gpx_manager = GpxManager(GPX_FOLDER, CRS_DISPLAY)
    gpxs_gdf = gpx_manager.get_gpxs_gdf()
     
    if (outer_map_area_gdf is not None):
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, outer_map_area_gdf)
    else:
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, map_area_gdf)
    gdfs_convert_loaded_columns(gpxs_gdf, nodes_gdf, ways_gdf, areas_gdf)

    # todo - by zoom also without eval - in some zoom turn off and set min req to only point? add to fe settings
    nodes_gdf = GdfUtils.filter_peaks_by_prominence(
        nodes_gdf, map_scale*10*2, map_scale/10)
    # todo filter out peak with very small elevation - to its prominence  - if ele is 4x smaller than prominence
    # get coastline and determine where is land and where water
    coast_gdf, ways_gdf = GdfUtils.filter_rows(
        ways_gdf, {'natural': 'coastline'}, compl=True)
    bg_gdf = GdfUtils.create_background_gdf(
        map_area_gdf, coast_gdf, OCEAN_WATER, GENERAL_DEFAULT_STYLES[Style.COLOR.name])
    
    # prepare ways function
    process_bridges_and_tunnels(ways_gdf, PLOT_BRIDGES, PLOT_TUNNELS)
    ways_gdf = GdfUtils.merge_lines_gdf(ways_gdf, [])
    # gpxs_gdf = GdfUtils.merge_lines_gdf(gpxs_gdf, [])

    # assing zoom specific styles
    StyleAssigner.assign_styles(gpxs_gdf, GPXS_STYLES)
    StyleAssigner.assign_styles(
        nodes_gdf, StyleAssigner.convert_dynamic_to_normal(STYLES['nodes'], zoom_level), NODES_DONT_CATEGORIZE)
    StyleAssigner.assign_styles(
        ways_gdf, StyleAssigner.convert_dynamic_to_normal(STYLES['ways'], zoom_level), WAYS_DONT_CATEGORIZE)
    StyleAssigner.assign_styles(
        areas_gdf, StyleAssigner.convert_dynamic_to_normal(STYLES['areas'], zoom_level), AREAS_DONT_CATEGORIZE)

    # ------------scaling and column calc------------ - to function
    gdfs_prepare_styled_columns(gpxs_gdf, nodes_gdf, ways_gdf,
                         areas_gdf, map_object_scaling_factor)
    # ------------filter some elements out------------
    nodes_gdf = GdfUtils.check_filter_nodes_min_req(nodes_gdf)

    # GdfUtils.wrap_text_gdf(nodes_gdf, [(Style.TEXT1.name, Style.TEXT1_WRAP_LEN.name), (Style.TEXT2.name, Style.TEXT2_WRAP_LEN.name)])
    # todo algorithm for peaks - for leaving only the highest peak in the area

    
    # nodes_gdf = GdfUtils.combine_gdfs([rest, peaksProm])
    bg_gdf['area'] = bg_gdf.area
    areas_gdf['area'] = areas_gdf.geometry.area
    # -----sort-----
    # sort by population and ele - main sort is by zindex in plotter
    GdfUtils.sort_gdf_by_columns(nodes_gdf, ['population', 'prominence', 'ele'], ascending=False, na_position='last')

    # first by zindex (from smallest to biggest) and then by area
    GdfUtils.sort_gdf_by_columns(areas_gdf, ['area'], ascending=False, na_position='last')
    GdfUtils.sort_gdf_by_columns(bg_gdf, ['area'], ascending=False, na_position='last')

    # ------------plot------------
    # todo add checks for errors in plotting cals if dict from fe is not correct
    plotter_settings = {"map_area_gdf": map_area_gdf, "paper_dimensions_mm": paper_dimensions_mm,
                        "map_object_scaling_factor": map_object_scaling_factor, "text_bounds_overflow_threshold": TEXT_BOUNDS_OVERFLOW_THRESHOLD,
                        "text_wrap_names_len": TEXT_WRAP_NAMES_LEN, "outer_map_area_gdf": outer_map_area_gdf, "map_bg_color": GENERAL_DEFAULT_STYLES[Style.COLOR.name],
                        'ways_over_filter': None}

    plotter = Plotter(map_area_gdf, paper_dimensions_mm,
                      map_object_scaling_factor, TEXT_BOUNDS_OVERFLOW_THRESHOLD, TEXT_WRAP_NAMES_LEN, outer_map_area_gdf)
    plotter.init(
        GENERAL_DEFAULT_STYLES[Style.COLOR.name], bg_gdf)
    plotter.areas(areas_gdf)
    # plotter.ways(ways_gdf, areas_gdf, [{'highway': 'motorway'}])
    # plotter.ways(ways_gdf, areas_gdf, [{'highway': 'primary'}])
    plotter.ways(ways_gdf, areas_gdf, None)
  
    # if want clip text
    plotter.gpxs(gpxs_gdf)
    plotter.clip()
    if (not boundary_map_area_gdf.empty):
        # GdfUtils.remove_common_boundary_inaccuracy(boundary_map_area_gdf) # maybe turn off/on in settings
        plotter.area_boundary(boundary_map_area_gdf,
                              color="black")
    plotter.nodes(nodes_gdf, TEXT_WRAP_NAMES_LEN)
    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()   

if __name__ == "__main__":
    main()
