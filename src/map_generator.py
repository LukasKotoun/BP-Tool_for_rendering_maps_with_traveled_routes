import warnings
import geopandas as gpd

from config import *
from styles.mapycz_style import GENERAL_DEFAULT_STYLES, STYLES, GPXS_STYLES
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.osm_data_parser import OsmDataParser
from modules.style_assigner import StyleAssigner
from modules.plotter import Plotter
from modules.gpx_manager import GpxManager
from common.common_helpers import time_measurement
import pandas as pd
from osmium.filter import GeoInterfaceFilter

import osmium


def calc_preview(map_area_gdf, paper_dimensions_mm):
    """
        NOTE: using constants from config file
    Args:
        map_area_gdf (_type_): _description_
        paper_dimensions_mm (_type_): _description_

    Returns:
        _type_: _description_
    """

    outer_area_gdf = GdfUtils.get_whole_area_gdf(
        OUTER_AREA, CRS_OSM, CRS_DISPLAY)

    outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_area_gdf)
    # map in meters for calc automatic orientation and same pdf sides proportions
    outer_paper_dimensions_mm = Utils.adjust_paper_dimensions(outer_map_area_dimensions, OUTER_PAPER_DIMENSIONS,
                                                              OUTER_GIVEN_SMALLER_PAPER_DIMENSION,
                                                              OUTER_WANTED_ORIENTATION)
    if (OUTER_FIT_PAPER_SIZE):
        outer_area_gdf = GdfUtils.expand_area_fitPaperSize(outer_area_gdf, outer_paper_dimensions_mm)
        outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_area_gdf)
    # outer_map_area_bounds = GdfUtils.get_bounds_gdf(GdfUtils.change_crs(outer_area_gdf, CRS_OSM)) # real scale cacl
    # map_scale = Utils.get_scale(outer_map_area_bounds, outer_paper_dimensions_mm)
    map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(outer_map_area_dimensions, outer_paper_dimensions_mm)
                                 * OBJECT_MULTIPLIER)
    # calc map factor for creating automatic array with wanted elements - for preview area (without area_zoom_preview)
    # todo map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(outer_map_area_dimensions, outer_paper_dimensions_mm)
    # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(outer_paper_dimensions_mm, outer_map_area_dimensions))/2
    # ?? to doc - need because it will clip by required area - and that will be some big area in not clipping (cant use only first approach)
    # ?? req area je potom velká jako pdf stránka (přes celou stránku) a ne jako puvodně chtěná oblast a tedy by k žádnému zaříznutí nedošlo
    if (not WANT_AREA_CLIPPING):
        # všechny prvky i když to bude menší než papír - např. cesty mimo required area
        area_zoom_preview = None
        # calc bounds so area_zoom_preview will be 1 and will fill whole paper
        paper_fill_bounds = Utils.calc_bounds_to_fill_paper_with_ratio(map_area_gdf.unary_union.centroid,
                                                                       paper_dimensions_mm, outer_map_area_dimensions,
                                                                       outer_paper_dimensions_mm)
        # area will be changing -> create copy for bounds plotting
        map_area_gdf = GdfUtils.create_gdf_from_bounds(
            paper_fill_bounds, CRS_DISPLAY)
    else:
        # oříznuté okraje když to bude menší než papír
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        # if want clipping than instead of bounds calculation use zoom/unzoom - with using paper_fill_bounds it cant be clipped
        area_zoom_preview = Utils.calc_zoom_for_smaller_area(
            outer_map_area_dimensions, outer_paper_dimensions_mm,
            map_area_dimensions, paper_dimensions_mm,
        )

    return area_zoom_preview, map_object_scaling_factor, map_area_gdf


@time_measurement("main")
def main():
    # ------------input validation------------
    # todo check file validity - if osm files exits

    # ------------get map area and calc paper sizes, and calc preview

    if (isinstance(OSM_INPUT_FILE_NAMES, list) and len(OSM_INPUT_FILE_NAMES) > 1 and OSM_WANT_EXTRACT_AREA == False):
        print("Multiple files feature (list of osm files) is avilable only with option OSM_WANT_EXTRACT_AREA")
        return
    # if are for preview is not specified, use whole area
    if (WANT_PREVIEW and AREA == None):
        map_area_gdf = GdfUtils.get_whole_area_gdf(
            OUTER_AREA, CRS_OSM, CRS_DISPLAY)
    else:
        map_area_gdf = GdfUtils.get_whole_area_gdf(
            AREA, CRS_OSM, CRS_DISPLAY)

    # ------------store bounds to plot and combine area rows in gdf to 1 row------------
    # todo  filter not ploting bounds and merge by category
    boundary_map_area_gdf = GdfUtils.create_empty_gdf(
        map_area_gdf.crs)  # default dont plot
    if (AREA_BOUNDARY == AreaBounds.SEPARATED):
        # store separated areas (before gdf row merge)
        boundary_map_area_gdf = map_area_gdf.copy()
        map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, CRS_DISPLAY)
    else:
        map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, CRS_DISPLAY)
        if (AREA_BOUNDARY == AreaBounds.COMBINED):
            # store comined areas (after row combination)
            boundary_map_area_gdf: gpd.GeoDataFrame = map_area_gdf.copy()

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, PAPER_DIMENSIONS,
                                                        GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)

    # ------------expand area custom (before get paper dimension)------------
    if (FIT_PAPER_SIZE):
        map_area_gdf = GdfUtils.expand_area_fitPaperSize(map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

    # store bounds as rows
    if (FIT_PAPER_SIZE and EXPAND_AREA_BOUNDS_PLOT):
        if (boundary_map_area_gdf is not None):
            boundary_map_area_gdf = GdfUtils.combine_gdfs(
                [boundary_map_area_gdf, map_area_gdf.copy()])
        else:
            boundary_map_area_gdf = map_area_gdf.copy()

    if (WANT_PREVIEW):
        (area_zoom_preview, map_object_scaling_factor,
            map_area_gdf) = calc_preview(map_area_gdf, paper_dimensions_mm)
        # todo automatic creation of wanted elements and linewidths - factor or directly giving paper size and area dimensions
    else:
        area_zoom_preview = None

        # - map scale in real size
        # map_area_bounds = GdfUtils.get_bounds_gdf(GdfUtils.change_crs(map_area_gdf, CRS_OSM))
        # map_scale = Utils.get_scale(map_area_bounds, paper_dimensions_mm)

        # - scaling factor and for zoom calc in webmercato
        map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(map_area_dimensions,
                                                                          paper_dimensions_mm)
                                     * OBJECT_MULTIPLIER)

    zoom_level = Utils.get_zoom_level(
        map_object_scaling_factor, ZOOM_MAPPING, 0.1)
    map_object_scaling_factor *= Utils.calc_scaling_factor_multiplier(
        map_object_scaling_factor, 1, 500)

    # ------------get elements from osm file------------
    if (OSM_WANT_EXTRACT_AREA):
        if (OSM_OUTPUT_FILE_NAME is None):
            print("output file is none, cant extract")
            return
        # todo check if osmium is instaled
        osm_data_preprocessor = OsmDataPreprocessor(
            OSM_INPUT_FILE_NAMES, OSM_OUTPUT_FILE_NAME)
        print(map_area_gdf)
        osm_file_name = osm_data_preprocessor.extract_areas(
            map_area_gdf, CRS_OSM)
    else:
        # todo function check osm file or in validator before?
        # list have length of 1 (checked in validator)
        if (isinstance(OSM_INPUT_FILE_NAMES, list)):
            osm_file_name = OSM_INPUT_FILE_NAMES[0]
        else:
            osm_file_name = OSM_INPUT_FILE_NAMES

    # ------------Working in display CRS------------
    map_area_gdf = GdfUtils.change_crs(map_area_gdf, CRS_DISPLAY)
    boundary_map_area_gdf = GdfUtils.change_crs(
        boundary_map_area_gdf, CRS_DISPLAY)
    reqired_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)

    # ------------gpxs------------
    gpx_manager = GpxManager(GPX_FOLDER, CRS_DISPLAY)
    # root_files_gpxs_gdf, folder_gpxs_gdf = gpx_manager.get_gpxs_gdf_splited()
    gpxs_gdf = gpx_manager.get_gpxs_gdf()
    if (not GdfUtils.are_gdf_geometry_inside_geometry(gpxs_gdf, reqired_area_polygon)):
        warnings.warn("Some gpx files are not whole inside selected map area.")
    # maybe add gpx to be change by zoom - size
    StyleAssigner.assign_styles(gpxs_gdf, GPXS_STYLES)

    # ------------osm file------------
    osm_file_parser = OsmDataParser(
        wanted_nodes, wanted_ways, wanted_areas,
        unwanted_nodes_tags, unwanted_ways_tags, unwanted_areas_tags, area_additional_columns=AREA_ADDITIONAL_COLUMNS,
        node_additional_columns=NODES_ADDITIONAL_COLUMNS, way_additional_columns=WAYS_ADDITIONAL_COLUMNS)
    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        osm_file_name, CRS_OSM, CRS_DISPLAY)


    # check for development
    whole_map_gdf = GdfUtils.create_polygon_from_gdf_bounds(
        ways_gdf, areas_gdf)
    # check if area is inside osm file
    if (not GdfUtils.is_geometry_inside_geometry(reqired_area_polygon, whole_map_gdf)):
        warnings.warn(
            "Selected area map is not whole inside given osm.pbf file.")

    # get coastline and determine where is land and where water
    coast_gdf, ways_gdf = GdfUtils.filter_rows(
        ways_gdf, [('natural', 'coastline')], compl=True)
    bg_gdf = GdfUtils.create_bg_gdf(
        map_area_gdf, coast_gdf, OCEAN_WATER, GENERAL_DEFAULT_STYLES[StyleKey.COLOR])
    bg_gdf['area'] = bg_gdf.area
    bg_gdf = bg_gdf.sort_values(by='area', ascending=False)
    
    # ------------filter some elements out - before styling ------------
    nodes_gdf = GdfUtils.get_rows_inside_area(
        nodes_gdf, map_area_gdf)
    # filter place without name
    nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [
        [('place', '~')],
        [('place', ''), ('name', '')]])
    # filter peak without name and ele
    nodes_gdf = GdfUtils.filter_rows(nodes_gdf, [
        [('natural', '~peak')],
        [('natural', 'peak'), ('name', ''), ('ele', '')]])
    # round ele to int
    GdfUtils.change_columns_to_numeric(nodes_gdf, ['ele'])
    if ('ele' in nodes_gdf.columns):
        nodes_gdf['ele'] = nodes_gdf['ele'].round(0).astype('Int64')

    # setting on bridge and tunnel ploting 
    ways_gdf['layer'] = ways_gdf.get('layer', 0)
    ways_gdf.loc[GdfUtils.get_rows_filter(
        ways_gdf, [[('tunnel', '~'), ('bridge', '~')]]), 'layer'] = 0
    GdfUtils.change_bridges_and_tunnels(ways_gdf, True, True)    
    # merge lines
    ways_gdf = GdfUtils.merge_lines_gdf(ways_gdf, [])
    GdfUtils.change_columns_to_numeric(ways_gdf, ['layer'])
    ways_gdf['layer'] = ways_gdf['layer'].fillna(0)
    
    # assing zoom specific styles 
    StyleAssigner.assign_styles(
        nodes_gdf, StyleAssigner.convert_dynamic_to_normal(STYLES['nodes'], zoom_level))
    StyleAssigner.assign_styles(
        ways_gdf, StyleAssigner.convert_dynamic_to_normal(STYLES['ways'], zoom_level))
    StyleAssigner.assign_styles(
        areas_gdf, StyleAssigner.convert_dynamic_to_normal(STYLES['areas'], zoom_level))

    
    # set base width - scale by muplitpliers and object scaling factor
    GdfUtils.multiply_column_gdf(nodes_gdf, StyleKey.WIDTH, [
        # maybe to setting like scale icons, text, and ways...
        StyleKey.WIDTH_SCALE, StyleKey.FE_WIDTH_SCALE], None)
    GdfUtils.multiply_column_gdf(nodes_gdf, StyleKey.TEXT_FONT_SIZE, [
        StyleKey.TEXT_FONT_SIZE_SCALE, StyleKey.FE_TEXT_FONT_SIZE_SCALE], None)

    GdfUtils.multiply_column_gdf(ways_gdf, StyleKey.WIDTH, [
        # if i will be creationg function with continues width scaling than multiply only by FEwidthscale
        StyleKey.WIDTH_SCALE, StyleKey.FE_WIDTH_SCALE], map_object_scaling_factor)

    GdfUtils.multiply_column_gdf(areas_gdf, StyleKey.WIDTH, [
        StyleKey.WIDTH_SCALE, StyleKey.FE_WIDTH_SCALE], map_object_scaling_factor)

    # create derivated columns
    # text outline
    GdfUtils.create_derivated_columns(nodes_gdf, StyleKey.TEXT_OUTLINE_WIDTH, StyleKey.TEXT_FONT_SIZE, [
                                      StyleKey.TEXT_OUTLINE_WIDHT_RATIO])
    # edge - icons size and ways width
    GdfUtils.create_derivated_columns(nodes_gdf, StyleKey.EDGEWIDTH, StyleKey.WIDTH, [
                                      # ?? maybe remove ...
                                      StyleKey.EDGE_WIDTH_RATIO])
    GdfUtils.create_derivated_columns(
        ways_gdf, StyleKey.EDGEWIDTH, StyleKey.WIDTH, [StyleKey.EDGE_WIDTH_RATIO])
    # calc bridge size only for bridges
    GdfUtils.create_derivated_columns(ways_gdf, StyleKey.BRIDGE_WIDTH, StyleKey.WIDTH, [
                                      StyleKey.BRIDGE_WIDTH_RATIO], [('bridge', '')])
    GdfUtils.create_derivated_columns(ways_gdf, StyleKey.BRIDGE_EDGE_WIDTH, StyleKey.BRIDGE_WIDTH, [
                                      StyleKey.BRIDGE_EDGE_WIDTH_RATIO], [('bridge', '')])
    # todo remove columns used for calc ratios (array in settings?)

    # todo review
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, "layer")
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    
    # order gdf by area plot smaller at the end
    areas_gdf['area'] = areas_gdf.geometry.area
    areas_gdf = areas_gdf.sort_values(by='area', ascending=False)

    # ------------plot------------ # todo to function
    plotter = Plotter(map_area_gdf, paper_dimensions_mm,
                      map_object_scaling_factor)

    plotter.init_plot(
        GENERAL_DEFAULT_STYLES[StyleKey.COLOR], bg_gdf, area_zoom_preview)
    plotter.zoom(zoom_percent_padding=PERCENTAGE_PADDING)
    plotter.plot_areas(areas_gdf, AREAS_EDGE_WIDTH_MULTIPLIER)
    plotter.plot_ways(ways_gdf, WAYS_WIDTH_MULTIPLIER)
    plotter.plot_nodes(nodes_gdf, TEXT_WRAP_NAMES_LEN)
    plotter.plot_gpxs(gpxs_gdf, 1)
    if (boundary_map_area_gdf is not None and not boundary_map_area_gdf.empty):
        # GdfUtils.remove_common_boundary_inaccuracy(boundary_map_area_gdf) # maybe turn off/on in settings
        plotter.plot_area_boundary(area_gdf=boundary_map_area_gdf.to_crs(
            CRS_DISPLAY), linewidth=AREA_BOUNDARY_LINEWIDTH)

    plotter.adjust_texts(TEXT_BOUNDS_OVERFLOW_THRESHOLD)

    if (WANT_AREA_CLIPPING or WANT_PREVIEW):
        plotter.clip(CRS_DISPLAY, GdfUtils.create_polygon_from_gdf_bounds(
            nodes_gdf, ways_gdf, areas_gdf))

    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()


if __name__ == "__main__":
    main()
