import warnings
import geopandas as gpd

from config import *
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.osm_data_parser import OsmDataParser
from modules.styles_assigner import StyleAssigner
from modules.plotter import Plotter
from modules.gpx_processer import GpxProcesser
from common.common_helpers import time_measurement_decorator


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
        OUTER_AREA, EPSG_OSM, EPSG_CALC)
    if (OUTER_EXPAND_AREA_MODE == ExpandArea.CUSTOM_AREA):
        outer_area_gdf = GdfUtils.expand_area(None, EPSG_OSM, EPSG_CALC, None,
                                              OUTER_CUSTOM_EXPAND_AREA)

    outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_area_gdf)
    # map in meters for calc automatic orientation and same pdf sides proportions
    outer_paper_dimensions_mm = Utils.adjust_paper_dimensions(outer_map_area_dimensions, OUTER_PAPER_DIMENSIONS,
                                                              OUTER_GIVEN_SMALLER_PAPER_DIMENSION,
                                                              OUTER_WANTED_ORIENTATION)

    if (OUTER_EXPAND_AREA_MODE == ExpandArea.FIT_PAPER_SIZE):
        outer_area_gdf = GdfUtils.expand_area(outer_area_gdf, EPSG_CALC, None, outer_paper_dimensions_mm,
                                              None)
        outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_area_gdf)

    map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(outer_map_area_dimensions,
                                                                      outer_paper_dimensions_mm)
                                 * OBJECT_MULTIPLIER)
    # calc map factor for creating automatic array with wanted elements - for preview area (without area_zoom_preview)
    # todo map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(outer_map_area_dimensions, outer_paper_dimensions_mm)
    # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(outer_paper_dimensions_mm, outer_map_area_dimensions))/2
    # ?? to doc - need because it will clip by required area - and that will be some big area in not clipping (cant use only first approach)
    if (not WANT_AREA_CLIPPING):
        area_zoom_preview = None
        # calc bounds so area_zoom_preview will be 1 and will fill whole paper
        paper_fill_bounds = Utils.calc_bounds_to_fill_paper_with_ratio(map_area_gdf.unary_union.centroid,
                                                                       paper_dimensions_mm, outer_map_area_dimensions,
                                                                       outer_paper_dimensions_mm)
        # area will be changing -> create copy for bounds plotting
        map_area_gdf = GdfUtils.create_gdf_from_bounds(
            paper_fill_bounds, EPSG_CALC)
    else:
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        # if want clipping than instead of bounds calculation use zoom/unzoom - with using paper_fill_bounds it cant be clipped
        area_zoom_preview = Utils.calc_zoom_for_smaller_area(
            outer_map_area_dimensions, outer_paper_dimensions_mm,
            map_area_dimensions, paper_dimensions_mm,
        )

    return area_zoom_preview, map_object_scaling_factor, map_area_gdf


@time_measurement_decorator("main")
def main():
    # ------------input validation------------
    # validation all inputs and combinations on start to prevent exception after long time of processing and rendering
    # some class input data checker
    # and run function to make checks
    # todo check some reqired constants
    # todo check file validity - if osm files exits
    # todo check missing styles (create array of reqired styles for every category), and by wanted categories (landues, water) check if have all required styles (check only for default category styles) (in instance of style assigner)
    # ------------get map area and calc paper sizes, and calc preview
    # todo get_area_gdfs and take list of string and lists. and resulted gdf concatenate to one and that return
    # todo to func checkOsmFilesAndNormalize - if files is list but with len 1 convert to string

    if (isinstance(OSM_INPUT_FILE_NAMES, list) and len(OSM_INPUT_FILE_NAMES) > 1 and OSM_WANT_EXTRACT_AREA == False):
        print("Multiple files feature (list of osm files) is avilable only with option OSM_WANT_EXTRACT_AREA")
        return

    map_area_gdf = GdfUtils.get_whole_area_gdf(AREA, EPSG_OSM, EPSG_CALC)

    # ------------store bounds to plot and combine area rows in gdf to 1 row------------
    boundary_map_area_gdf = None  # default dont plot
    if (AREA_BOUNDARY == AreaBounds.SEPARATED):
        # store separated areas (before gdf row merge)
        boundary_map_area_gdf = map_area_gdf.copy()
        map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, EPSG_CALC)
    else:
        map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, EPSG_CALC)
        if (AREA_BOUNDARY == AreaBounds.COMBINED):
            # store comined areas (after row combination)
            boundary_map_area_gdf: gpd.GeoDataFrame = map_area_gdf.copy()

    # # Rozdělení custom a non custom expand - před get paper dimension, fit paper expand po výpočtu paper dimensions podle základní oblasti - a poté při expandu počítat s
    # #------------expand area custom (before get paper dimension)------------
    if (EXPAND_AREA_MODE == ExpandArea.CUSTOM_AREA):
        map_area_gdf = GdfUtils.expand_area(None, EPSG_OSM, EPSG_CALC, PAPER_DIMENSIONS,
                                            CUSTOM_EXPAND_AREA)

    # ------------get paper dimension (size and orientation)------------
    map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions, PAPER_DIMENSIONS,
                                                        GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)

    # ------------expand area custom (before get paper dimension)------------
    if (EXPAND_AREA_MODE == ExpandArea.FIT_PAPER_SIZE):
        map_area_gdf = GdfUtils.expand_area(map_area_gdf, EPSG_CALC, None, paper_dimensions_mm,
                                            None)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)

    # store bounds as rows
    if (EXPAND_AREA_MODE != ExpandArea.NONE and EXPAND_AREA_BOUNDS_PLOT):
        if (boundary_map_area_gdf is not None):
            boundary_map_area_gdf = GdfUtils.combine_gdfs(
                [boundary_map_area_gdf, map_area_gdf.copy()])
        else:
            boundary_map_area_gdf = map_area_gdf.copy()

    if (WANT_PREVIEW):
        (area_zoom_preview, map_object_scaling_factor,
         map_area_gdf) = calc_preview(map_area_gdf, paper_dimensions_mm)
        # todo automatic creationg of wanted elements and linewidths - factor or directly giving paper size and area dimensions
    else:
        # todo automatic creationg of wanted elements and linewidths - factor or directly giving paper size and area dimensions
        area_zoom_preview = None
        # calc map factor for creating automatic array with wanted elements
        # todo map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(map_area_dimensions, paper_dimensions_mm)
        # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(paper_dimensions_mm, map_area_dimensions))/2
        # in meteres for same proportion keeping
        map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(map_area_dimensions,
                                                                          paper_dimensions_mm)
                                     * OBJECT_MULTIPLIER)

    # ------------get elements from osm file------------
    if (OSM_WANT_EXTRACT_AREA):
        if (OSM_OUTPUT_FILE_NAME is None):
            print("output file is none, cant extract")
            return
        # todo check if osmium is instaled
        osm_data_preprocessor = OsmDataPreprocessor(
            OSM_INPUT_FILE_NAMES, OSM_OUTPUT_FILE_NAME)
        osm_file_name = osm_data_preprocessor.extract_areas(map_area_gdf)
    else:
        # todo function check osm file or in validator before?
        # list have length of 1 (checked in validator)
        if (isinstance(OSM_INPUT_FILE_NAMES, list)):
            osm_file_name = OSM_INPUT_FILE_NAMES[0]
        else:
            osm_file_name = OSM_INPUT_FILE_NAMES

    # can use also outer paper size and area
    osm_file_parser = OsmDataParser(
        wanted_nodes, wanted_ways, wanted_areas,
        unwanted_nodes_tags, unwanted_ways_tags, unwanted_areas_tags,
        node_additional_columns=NODES_ADDITIONAL_COLUMNS, way_additional_columns=WAYS_ADDITIONAL_COLUMNS)

    @time_measurement_decorator("apply file")
    def apply_file():
        osm_file_parser.apply_file(osm_file_name)
    apply_file()
    # ------------Working in display EPSG------------

    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        EPSG_OSM, EPSG_DISPLAY)
    osm_file_parser.clear_gdf()

    map_area_gdf = map_area_gdf.to_crs(f"epsg:{EPSG_DISPLAY}")
    boundary_map_area_gdf = boundary_map_area_gdf.to_crs(
        f"epsg:{EPSG_DISPLAY}")

    # todo check if area is inside osm to function
    whole_map_gdf = GdfUtils.create_polygon_from_gdf_bounds(
        ways_gdf, areas_gdf)
    reqired_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
    # check if area is inside osm file
    if (not GdfUtils.is_polygon_inside_polygon(reqired_area_polygon, whole_map_gdf)):
        warnings.warn(
            "Selected area map is not whole inside given osm.pbf file.")
    # ------------filter some elements out - before styles adding------------
    # only for some ways categories
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)

    nodes_gdf = GdfUtils.filter_gdf_rows_inside_gdf_area(
        nodes_gdf, map_area_gdf)
    # get only places with name
    nodes_gdf = GdfUtils.filter_gdf_related_columns_values(
        nodes_gdf, 'place', [], ['name'], [])
    # todo  use to filter peeks withou ele and name?
    # function(algorithm) to get only usefull peeks + again back to nodes gdf
    # ------------style elements------------
    nodes_style_assigner = StyleAssigner(
        NODES_STYLES, GENERAL_DEFAULT_STYLES, NODES_MANDATORY_STYLES)
    nodes_gdf = nodes_style_assigner.assign_styles_to_gdf(nodes_gdf, wanted_nodes,
                                                          [StyleKey.COLOR, StyleKey.FONT_SIZE, StyleKey.OUTLINE_WIDTH,
                                                           StyleKey.EDGE_COLOR, StyleKey.ICON_COLOR, StyleKey.ICON_SIZE,
                                                           StyleKey.ICON, StyleKey.ICON_EDGE])

    ways_style_assigner = StyleAssigner(
        WAYS_STYLES, GENERAL_DEFAULT_STYLES, WAY_MANDATORY_STYLES)
    ways_gdf = ways_style_assigner.assign_styles_to_gdf(ways_gdf, wanted_ways,
                                                        [StyleKey.COLOR, StyleKey.ZINDEX, StyleKey.LINEWIDTH,
                                                         StyleKey.LINESTYLE, StyleKey.ALPHA, StyleKey.EDGE_COLOR,
                                                         StyleKey.BRIDGE_COLOR, StyleKey.BRIDGE_EDGE_COLOR,
                                                         StyleKey.EDGE_WIDTH_RATIO, StyleKey.BRIDGE_WIDTH_RATIO])
    areas_style_assigner = StyleAssigner(
        AREAS_STYLES, GENERAL_DEFAULT_STYLES, AREA_MANDATORY_STYLES)
    areas_gdf = areas_style_assigner.assign_styles_to_gdf(areas_gdf, wanted_areas,
                                                          [StyleKey.COLOR, StyleKey.EDGE_COLOR, StyleKey.ZINDEX,
                                                           StyleKey.LINEWIDTH, StyleKey.ALPHA, StyleKey.LINESTYLE])

    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, "layer")
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    # todo check if gpx go somewhere outside reqired_area - add warning
    gpx_processer = GpxProcesser('../gpxs')
    gpxs_gdf = gpx_processer.get_gpxs_gdf(EPSG_DISPLAY)

    plotter = Plotter(map_area_gdf, paper_dimensions_mm,
                      map_object_scaling_factor)
    plotter.init_plot(
        GENERAL_DEFAULT_STYLES[StyleKey.COLOR], area_zoom_preview)
    plotter.zoom(zoom_percent_padding=PERCENTAGE_PADDING)
    plotter.plot_areas(areas_gdf, AREAS_EDGE_WIDTH_MULTIPLIER)
    plotter.plot_ways(ways_gdf, WAYS_WIDTH_MULTIPLIER)
    plotter.plot_nodes(nodes_gdf, TEXT_WRAP_NAMES_LEN)
    plotter.plot_gpxs(gpxs_gdf)

    plotter.adjust_texts(TEXT_BOUNDS_OVERFLOW_THRESHOLD)

    # if want is false and preview is true area will be on whole paper (required area is calculated) - clip overflown ways
    if (WANT_AREA_CLIPPING or WANT_PREVIEW):
        plotter.clip(EPSG_DISPLAY, GdfUtils.create_polygon_from_gdf_bounds(
            nodes_gdf, ways_gdf, areas_gdf))

    if (boundary_map_area_gdf is not None):
        plotter.plot_area_boundary(area_gdf=boundary_map_area_gdf.to_crs(
            epsg=EPSG_DISPLAY), linewidth=AREA_BOUNDARY_LINEWIDTH)

    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()


if __name__ == "__main__":
    main()
