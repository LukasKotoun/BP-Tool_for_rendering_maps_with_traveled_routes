import warnings


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
    outer_area_gdf = GdfUtils.get_area_gdf(OUTER_AREA, EPSG_DEGREE_NUMBER)
    outer_map_area_dimensions = GdfUtils.get_dimensions_gdf(outer_area_gdf)
    outer_map_area_dimensions_m = GdfUtils.get_dimensions_gdf(outer_area_gdf, EPSG_METERS_NUMBER)
    # map in meters for calc automatic orientation and same pdf sides proportions
    outer_paper_dimensions_mm = Utils.adjust_paper_dimensions(outer_map_area_dimensions_m, OUTER_PAPER_DIMENSIONS,
                                                            OUTER_GIVEN_SMALLER_PAPER_DIMENSION,
                                                            OUTER_WANTED_ORIENTATION)
    #in meteres for same proportion keeping
    map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(outer_map_area_dimensions_m,
                                                                     outer_paper_dimensions_mm)
                                * LINEWIDTH_MULTIPLIER)
    # calc map factor for creating automatic array with wanted elements - for preview area (without area_zoom_preview)
    # map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(outer_map_area_dimensions_m, outer_paper_dimensions_mm)
    # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(outer_paper_dimensions_mm, outer_map_area_dimensions_m))/2
   
    if(TURN_OFF_AREA_CLIPPING):
        area_zoom_preview = None
        #calc bounds so area_zoom_preview will be 1 - paper in mm and areas in degrees (meters are not precies)
        paper_fill_bounds = Utils.calc_bounds_to_fill_paper(map_area_gdf.unary_union.centroid,
                                                            paper_dimensions_mm, outer_map_area_dimensions,
                                                            outer_paper_dimensions_mm)
        # area will be changing -> create copy for bounds ploting
        map_area_gdf = GdfUtils.create_gdf_from_bounds(paper_fill_bounds, EPSG_DEGREE_NUMBER)
    else:
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        # calc zoom - paper in mm and areas in degrees (meters are not precies)
        # if want clipping instead of bounds calculation calculate need zoom/unzoom 
        area_zoom_preview = Utils.calc_zoom_for_smaller_area(
            outer_map_area_dimensions, outer_paper_dimensions_mm,
            map_area_dimensions, paper_dimensions_mm,
        )
    
    return area_zoom_preview, map_object_scaling_factor, map_area_gdf 


@time_measurement_decorator("main")
def main():
    #todo check some reqired constants
    #todo check file validity - if osm file exits
    #------------get map area and calc paper sizes, and calc preview
    map_area_gdf = GdfUtils.get_area_gdf(AREA, EPSG_DEGREE_NUMBER)
    boundary_map_area_gdf = map_area_gdf.copy()
    map_area_dimensions_m = GdfUtils.get_dimensions_gdf(map_area_gdf, EPSG_METERS_NUMBER)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions_m, PAPER_DIMENSIONS,
                                                  GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)
    if(WANT_PREVIEW):
        (area_zoom_preview, map_object_scaling_factor,
         map_area_gdf) = calc_preview(map_area_gdf, paper_dimensions_mm)
    else:
        area_zoom_preview = None
        # calc map factor for creating automatic array with wanted elements
        # map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(map_area_dimensions_m, paper_dimensions_mm)
        # map_pdf_ratio_auto_filter = sum(Utils.calc_ratios(paper_dimensions_mm, map_area_dimensions_m))/2
        # in meteres for same proportion keeping
        map_object_scaling_factor = (Utils.calc_map_object_scaling_factor(map_area_dimensions_m,
                                                                         paper_dimensions_mm) 
                                    * LINEWIDTH_MULTIPLIER)

    #------------get elements from osm file------------
    osm_file_name = OSM_FILE_NAME
    if(OSM_WANT_EXTRACT_AREA):
        if(OSM_OUTPUT_FILE_NAME is None): #todo function extractioin checks, output file cant exists or try catch
            print("output file is none, cant extract")
            return
        #todo check if osmium is instaled
        osm_data_preprocessor = OsmDataPreprocessor(OSM_FILE_NAME, OSM_OUTPUT_FILE_NAME)
        osm_file_name = osm_data_preprocessor.extract_area(map_area_gdf)
    osm_file_parser = OsmDataParser(wanted_ways, wanted_areas, unwanted_ways_tags, unwanted_areas_tags)
    
    @time_measurement_decorator("apply file")
    def apply_file():
        osm_file_parser.apply_file(osm_file_name)
    apply_file()
    
    ways_gdf, areas_gdf = osm_file_parser.create_gdf(EPSG_DEGREE_NUMBER)
    osm_file_parser.clear_gdf()
    
    # todo to function
    whole_map_gdf = GdfUtils.create_polygon_from_gdf_bounds(ways_gdf, areas_gdf)
    reqired_area_polygon = GdfUtils.create_polygon_from_gdf(map_area_gdf)
    #check if area is inside osm file
    if(not GdfUtils.is_polygon_inside_polygon(reqired_area_polygon, whole_map_gdf)):
        warnings.warn("Selected area map is not whole inside given osm.pbf file. Posible problems")
        
    #------------filter some elements out------------
    # only for some ways categories
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)

    #------------style elements------------
    #todo styles for ways and areas separeated - 2 geodata stylers

    ways_style_assigner = StyleAssigner(WAYS_STYLES, GENERAL_DEFAULT_STYLES)
    ways_gdf = ways_style_assigner.assign_styles_to_gdf(ways_gdf, wanted_ways,
                                                    [StyleKey.COLOR, StyleKey.ZINDEX, StyleKey.LINEWIDTH, StyleKey.BGCOLOR])
    areas_style_assigner = StyleAssigner(AREAS_STYLES, GENERAL_DEFAULT_STYLES)
    areas_gdf = areas_style_assigner.assign_styles_to_gdf(areas_gdf, wanted_areas,
                                                     [StyleKey.COLOR, StyleKey.ZINDEX])

    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    
    #todo check if gpx go somewhere outside reqired_area - add warning 
    gpx_processer =  GpxProcesser('../gpxs')
    gpxs_gdf = gpx_processer.get_gpxs_gdf(EPSG_DEGREE_NUMBER)
    
    
    plotter = Plotter(GENERAL_DEFAULT_STYLES, ways_gdf, areas_gdf, gpxs_gdf,
                             map_area_gdf, paper_dimensions_mm, map_object_scaling_factor)
    plotter.init_plot(GENERAL_DEFAULT_STYLES[StyleKey.COLOR], area_zoom_preview)
    plotter.plot_areas()
    plotter.plot_ways()
    plotter.plot_gpxs()
    if(not TURN_OFF_AREA_CLIPPING):
        plotter.clip()
        
    if(PLOT_AREA_BOUNDARY):
        plotter.plot_area_boundary(area_gdf = boundary_map_area_gdf, linewidth=AREA_BOUNDARY_LINEWIDTH)

    plotter.zoom(zoom_percent_padding=PERCENTAGE_PADDING)
    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()
    
    
if __name__ == "__main__":
    main()
    