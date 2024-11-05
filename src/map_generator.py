import warnings

import geopandas as gpd
import pandas as pd
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
    #todo map area gdfs
    outer_area_gdf = GdfUtils.get_area_gdf(OUTER_AREA, EPSG_DEGREE_NUMBER)
    outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_area_gdf)
    outer_map_area_dimensions_m = GdfUtils.get_dimensions_m_gdf(outer_area_gdf)
    # map in meters for calc automatic orientation and same pdf sides proportions
    outer_paper_dimensions_mm = Utils.adjust_paper_dimensions(outer_map_area_dimensions_m, OUTER_PAPER_DIMENSIONS,
                                                            OUTER_GIVEN_SMALLER_PAPER_DIMENSION,
                                                            OUTER_WANTED_ORIENTATION)
    #in meteres for same proportion keeping
    map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(outer_map_area_dimensions_m,
                                                                     outer_paper_dimensions_mm)
                                * OBJECT_MULTIPLIER)
    # calc map factor for creating automatic array with wanted elements - for preview area (without area_zoom_preview)
    # todo map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(outer_map_area_dimensions_m, outer_paper_dimensions_mm)
    # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(outer_paper_dimensions_mm, outer_map_area_dimensions_m))/2
    # ?? to doc - need because it will clip by requred area - and that will be some big area in not clipping
    if(not WANT_AREA_CLIPPING):
        area_zoom_preview = None
        #calc bounds so area_zoom_preview will be 1 - paper in mm and areas in degrees (meters are not precies)
        paper_fill_bounds = Utils.calc_bounds_to_fill_paper(map_area_gdf.unary_union.centroid,
                                                            paper_dimensions_mm, outer_map_area_dimensions,
                                                            outer_paper_dimensions_mm)
        # area will be changing -> create copy for bounds ploting
        map_area_gdf = GdfUtils.create_gdf_from_bounds(paper_fill_bounds, EPSG_DEGREE_NUMBER)
    else:
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        # calc zoom - paper in mm and areas in degrees (meters are not that accurate)
        # if want clipping instead of bounds calculation calculate need zoom/unzoom 
        area_zoom_preview = Utils.calc_zoom_for_smaller_area(
            outer_map_area_dimensions, outer_paper_dimensions_mm,
            map_area_dimensions, paper_dimensions_mm,
        )

    return area_zoom_preview, map_object_scaling_factor, map_area_gdf 


@time_measurement_decorator("main")
def main():
    #validation all inputs and combinations on start to prevent exception after long time of processing and rendering 
    #some class input data checker
    #and run function to make checks
    #todo check some reqired constants
    #todo check file validity - if osm files exits  
    #todo check missing styles (create array of reqired styles for every category), and by wanted categories (landues, water) check if have all required styles (check only for default category styles) (in instance of style assigner)
    #------------get map area and calc paper sizes, and calc preview
    #todo get_area_gdfs and take list of string and lists. and resulted gdf concatenate to one and that return
    #todo to func checkOsmFilesAndNormalize - if files is list but with len 1 convert to string
    if(isinstance(OSM_INPUT_FILE_NAMES, list) and len(OSM_INPUT_FILE_NAMES) > 1 and OSM_WANT_EXTRACT_AREA == False):
        print("Multiple files feature (list of osm files) is avilable only with option OSM_WANT_EXTRACT_AREA")
        return


    map_area_gdf = GdfUtils.get_area_gdf(AREA, EPSG_DEGREE_NUMBER)
    # #todo func - return one map_area_gdf
    # map_area_gdf2 = GdfUtils.get_area_gdf("Třebíč, Czech Republic", EPSG_DEGREE_NUMBER)
    # map_area_gdf3 = GdfUtils.get_area_gdf("Slovakia Republic", EPSG_DEGREE_NUMBER)
    # map_area_gdf4 = GdfUtils.get_area_gdf("Germany", EPSG_DEGREE_NUMBER)
    # map_area_gdf5 = GdfUtils.get_area_gdf("Italy", EPSG_DEGREE_NUMBER)
    # map_area_gdf6 = GdfUtils.get_area_gdf("Slovakia Republic", EPSG_DEGREE_NUMBER)
    # map_area_gdf = gpd.GeoDataFrame(pd.concat([map_area_gdf, map_area_gdf2,map_area_gdf3,map_area_gdf4,map_area_gdf5,map_area_gdf6], ignore_index=True))
    #todo as function gdfUtils.concat_gdfs()
    # map_area_gdf = pd.concat([map_area_gdf,map_area_gdf2], ignore_index=True)

    # if(not PLOT_AREA_BOUNDARY_SEPARATED or OSM_WANT_EXTRACT_AREA): #or EXPAND_AREA
    #     map_area_gdf_joined = GdfUtils.combine_rows_gdf(map_area_gdf, EPSG_DEGREE_NUMBER)   

    if(AREA_BOUNDARY == AreaBounds.SEPARATED):
        boundary_map_area_gdf = map_area_gdf.copy()
    else:
        map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, EPSG_DEGREE_NUMBER)   
        boundary_map_area_gdf = map_area_gdf
        
    #todo also to preview
    # if(EXPAND_AREA_MODE):
    # todo to func expand area - map_area_gdf =  func(map_area_gdf, expandMode, EXPAND_AREA)
    #concat here or concat after this
    #     #EXPAND AREA
    #     if(EXPAND_AREA_BOUNDS):
    #         expanded_boundary_map_area_gdf = 
    #     else:
    #         expanded_boundary_map_area_gdf = None
    # else:
    # map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf, EPSG_DEGREE_NUMBER) Dont need in preview

    map_area_dimensions_m = GdfUtils.get_dimensions_m_gdf(map_area_gdf)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions_m, PAPER_DIMENSIONS,
                                                  GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)
    if(WANT_PREVIEW):
        (area_zoom_preview, map_object_scaling_factor,
         map_area_gdf) = calc_preview(map_area_gdf, paper_dimensions_mm)
    else:
        area_zoom_preview = None
        # calc map factor for creating automatic array with wanted elements
        # todo map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(map_area_dimensions_m, paper_dimensions_mm)
        # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(paper_dimensions_mm, map_area_dimensions_m))/2
        # in meteres for same proportion keeping
        map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(map_area_dimensions_m,
                                                                         paper_dimensions_mm) 
                                    * OBJECT_MULTIPLIER)

    #------------get elements from osm file------------
    
    if(OSM_WANT_EXTRACT_AREA):
        if(OSM_OUTPUT_FILE_NAME is None):
            print("output file is none, cant extract")
            return
        #todo check if osmium is instaled
        osm_data_preprocessor = OsmDataPreprocessor(OSM_INPUT_FILE_NAMES, OSM_OUTPUT_FILE_NAME)
        osm_file_name = osm_data_preprocessor.extract_areas(map_area_gdf)
    else:
        # todo function check osm file or in validator before? 
        # list have length of 1 (checked in validator)
        if(isinstance(OSM_INPUT_FILE_NAMES, list)):
            osm_file_name = OSM_INPUT_FILE_NAMES[0]      
        else:
            osm_file_name = OSM_INPUT_FILE_NAMES
        
    osm_file_parser = OsmDataParser(
        wanted_nodes, wanted_ways, wanted_areas,
        unwanted_nodes_tags, unwanted_ways_tags, unwanted_areas_tags,
        node_additional_columns=NODES_ADDITIONAL_COLUMNS)
    
    @time_measurement_decorator("apply file")
    def apply_file():
        osm_file_parser.apply_file(osm_file_name)
    apply_file()
    
    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(EPSG_DEGREE_NUMBER)
    osm_file_parser.clear_gdf()
    
    # todo to function

    whole_map_gdf = GdfUtils.create_polygon_from_gdf_bounds(ways_gdf, areas_gdf)
    reqired_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
    #check if area is inside osm file
    if(not GdfUtils.is_polygon_inside_polygon(reqired_area_polygon, whole_map_gdf)):
        warnings.warn("Selected area map is not whole inside given osm.pbf file.")
    #------------filter some elements out - before styles adding------------
    # only for some ways categories
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)
    
    nodes_gdf = GdfUtils.filter_gdf_rows_inside_gdf_area(nodes_gdf, map_area_gdf)
    #todo function to filter fun(gdf, tag, value (or none for not nan), not nan in this columns) - use to filter city without names
    #todo  use to filter peeks withou ele
    #function(algorithm) to get only usefull peeks + again back to nodes gdf
    #------------style elements------------
    #todo styles for ways and areas separeated - 2 geodata stylers
    nodes_style_assigner = StyleAssigner(NODES_STYLES, GENERAL_DEFAULT_STYLES, NODES_MANDATORY_STYLES)
    nodes_gdf = nodes_style_assigner.assign_styles_to_gdf(nodes_gdf, wanted_nodes,
                                                    [StyleKey.COLOR, StyleKey.FONT_SIZE, StyleKey.OUTLINE_WIDTH,
                                                     StyleKey.BGCOLOR])

    ways_style_assigner = StyleAssigner(WAYS_STYLES, GENERAL_DEFAULT_STYLES, WAY_MANDATORY_STYLES)
    ways_gdf = ways_style_assigner.assign_styles_to_gdf(ways_gdf, wanted_ways,
                                                    [StyleKey.COLOR, StyleKey.ZINDEX, StyleKey.LINEWIDTH,
                                                     StyleKey.BGCOLOR, StyleKey.LINESTYLE, StyleKey.ALPHA])
    areas_style_assigner = StyleAssigner(AREAS_STYLES, GENERAL_DEFAULT_STYLES, AREA_MANDATORY_STYLES)
    areas_gdf = areas_style_assigner.assign_styles_to_gdf(areas_gdf, wanted_areas,
                                                     [StyleKey.COLOR, StyleKey.EDGE_COLOR, StyleKey.ZINDEX,
                                                      StyleKey.LINEWIDTH, StyleKey.ALPHA, StyleKey.LINESTYLE])

    # print(nodes_gdf)
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    #todo check if gpx go somewhere outside reqired_area - add warning 
    gpx_processer =  GpxProcesser('../gpxs')
    gpxs_gdf = gpx_processer.get_gpxs_gdf(EPSG_DEGREE_NUMBER)
    
    
    plotter = Plotter(map_area_gdf, paper_dimensions_mm, map_object_scaling_factor)
    plotter.init_plot(GENERAL_DEFAULT_STYLES[StyleKey.COLOR], area_zoom_preview)
    plotter.zoom(zoom_percent_padding=PERCENTAGE_PADDING)

    plotter.plot_areas(areas_gdf, AREAS_EDGE_WIDTH_MULTIPLIER)
    plotter.plot_ways(ways_gdf, WAYS_WIDTH_MULTIPLIER)
    plotter.plot_nodes(nodes_gdf, TEXT_WRAP_NAMES_LEN)
    plotter.plot_gpxs(gpxs_gdf)
    
    plotter.adjust_texts(TEXT_BOUNDS_OVERFLOW_THRESHOLD)
    
    #if want is false and preview is true area will be on whole paper (required area is calculated) - clip overflown ways
    if(WANT_AREA_CLIPPING or WANT_PREVIEW):
        plotter.clip(GdfUtils.create_polygon_from_gdf_bounds(nodes_gdf, ways_gdf, areas_gdf))
        
    if(AREA_BOUNDARY != AreaBounds.NONE):
        plotter.plot_area_boundary(area_gdf = boundary_map_area_gdf, linewidth=AREA_BOUNDARY_LINEWIDTH)
        
    # if(expanded_boundary_map_area_gdf not None and PLOT_EXPANDED_AREA_BOUNDARY and EXPAND_AREA):
    #     plotter.plot_area_boundary(area_gdf = expanded_boundary_map_area_gdf, linewidth=EXPANDED_AREA_BOUNDARY_LINEWIDTH)

    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()
    
    
if __name__ == "__main__":
    main()
    