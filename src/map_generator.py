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


@time_measurement_decorator("main")
def main():
    #------------get map area and calc paper sizes, (for preview calc ratios between plotting area and bigger area (preview)
    map_area_gdf = GdfUtils.get_area_gdf(AREA)
    map_area_dimensions_m = GdfUtils.get_dimensions_gdf(map_area_gdf, EPSG_METERS_NUMBER)
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_area_dimensions_m, PAPER_DIMENSIONS,
                                                  GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)
    
    if(WANT_PREVIEW):
        outer_area_gdf = GdfUtils.get_area_gdf(OUTER_AREA)
        outer_map_dimensions_m = GdfUtils.get_dimensions_gdf(outer_area_gdf, EPSG_METERS_NUMBER)
        # map in meters for calc automatic orientation and same pdf sides proportions
        outer_paper_dimensions_mm = Utils.adjust_paper_dimensions(outer_map_dimensions_m, OUTER_PAPER_DIMENSIONS,
                                                             OUTER_GIVEN_SMALLER_PAPER_DIMENSION,
                                                             OUTER_WANTED_ORIENTATION)
        map_area_bounds  = GdfUtils.get_bounds_gdf(map_area_gdf) 
        outer_map_area_bounds = GdfUtils.get_bounds_gdf(outer_area_gdf) 
        # calc ratios - paper in mm and areas in degrees (meters are not precies)
        areas_ratios_preview = Utils.get_relative_areas_ratio(
            GdfUtils.get_dimensions(outer_map_area_bounds),
            outer_paper_dimensions_mm, GdfUtils.get_dimensions(map_area_bounds),
            paper_dimensions_mm
        )
        # calc map factor for creating automatic array with wanted elements - for preview area (without areas_ratios_preview)
        # map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(outer_map_dimensions_m, outer_paper_dimensions_mm)
    else:
        areas_ratios_preview = None
        outer_area_gdf = None
        # calc map factor for creating automatic array with wanted elements
        # map_object_scaling_automatic_filters_creating = Utils.calc_map_object_scaling_factor(map_area_dimensions_m, paper_dimensions_mm)
    map_object_scaling_factor = Utils.calc_map_object_scaling_factor(map_area_dimensions_m, paper_dimensions_mm, areas_ratios_preview)
    
    #------------get elements from osm file------------
    osm_file_name = OSM_FILE_NAME
    if(OSM_WANT_EXTRACT_AREA):
        osm_data_preprocessor = OsmDataPreprocessor(OSM_FILE_NAME, OSM_OUTPUT_FILE_NAME, OSM_WANT_EXTRACT_AREA)
        osm_file_name = osm_data_preprocessor.extract_area(map_area_gdf)
    osm_file_parser = OsmDataParser(wanted_ways, wanted_areas, unwanted_ways_tags, unwanted_areas_tags)
    
    @time_measurement_decorator("apply file")
    def apply_file():
        osm_file_parser.apply_file(osm_file_name)
    apply_file()
    
    ways_gdf, areas_gdf = osm_file_parser.create_gdf(EPSG_DEGREE_NUMBER)
    osm_file_parser.clear_gdf()
    total_map_bounds = GdfUtils.get_bounds_gdf(ways_gdf, areas_gdf)
    reqired_area_polygon = map_area_gdf.unary_union
    #check if area is inside osm file
    if(not GdfUtils.is_polygon_inside_bounds(total_map_bounds, reqired_area_polygon)):
        warnings.warn("Selected area map is not whole inside given osm.pbf file. Posible problems")
        
    #------------filter some elements out------------
    # only for some ways categories
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)

    #------------style elements------------
    #todo styles for ways and areas separeated - 2 geodata stylers
    geo_data_styler = StyleAssigner(CATEGORIES_STYLES, GENERAL_DEFAULT_STYLES)

    ways_gdf = geo_data_styler.assign_styles_to_gdf(ways_gdf, wanted_ways, [StyleKey.COLOR, StyleKey.ZINDEX, StyleKey.LINEWIDTH])
    areas_gdf = geo_data_styler.assign_styles_to_gdf(areas_gdf, wanted_areas, [StyleKey.COLOR, StyleKey.ZINDEX])
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    
    #todo check if gpx go somewhere outside reqired_area - add warning 
    gpx_processer =  GpxProcesser('../gpxs')
    gpxs_gdf = gpx_processer.get_gpxs_gdf(EPSG_DEGREE_NUMBER)
    
    
    plotter = Plotter(GdfUtils, geo_data_styler, ways_gdf, areas_gdf, gpxs_gdf,
                             map_area_gdf, paper_dimensions_mm, map_object_scaling_factor)
    plotter.init_plot(GENERAL_DEFAULT_STYLES[StyleKey.COLOR], areas_ratios_preview)
    plotter.plot_areas()
    plotter.plot_ways()
    plotter.plot_gpxs()
    plotter.clip(total_map_bounds)
    plotter.zoom(zoom_percent_padding=PERCENTAGE_PADDING)
    plotter.plot_map_boundary()
    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()
    
    
if __name__ == "__main__":
    main()
    