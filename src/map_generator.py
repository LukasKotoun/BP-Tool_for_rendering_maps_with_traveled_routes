import sys

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
    
    map_area_gdf = GdfUtils.get_area_gdf(AREA)
    map_dimensions_m = GdfUtils.calc_dimensions_gdf(map_area_gdf, EPSG_METERS_NUMBER)
    #todo check for custom - without paper size
    #also paper size custom, where to calc own side - always set 
    paper_dimensions_mm = Utils.adjust_paper_dimensions(map_dimensions_m, PAPER_DIMENSIONS,
                                                  GIVEN_SMALLER_PAPER_DIMENSION, WANTED_ORIENTATION)
    #want preview....
    #paper or custom or custom with only one
    if(WANT_PREVIEW):
        bigger_area_gdf = GdfUtils.get_area_gdf(PREVIEW_AREA)
        bigger_map_dimensions_m = GdfUtils.calc_dimensions_gdf(bigger_area_gdf, EPSG_METERS_NUMBER)
        # map in meters for calc automatic orientation and same proportions
        bigger_paper_dimensions_mm = Utils.adjust_paper_dimensions(bigger_map_dimensions_m, PREVIEW_PAPER_DIMENSIONS,
                                                             PREVIEW_GIVEN_SMALLER_PAPER_DIMENSION,
                                                             PREVIEW_WANTED_ORIENTATION)
        map_area_bounds  = GdfUtils.get_bounds_gdf(map_area_gdf) 
        bigger_map_area_bounds = GdfUtils.get_bounds_gdf(bigger_area_gdf) 
        # calc ratios - paper in mm and areas in degrees (meters are not precies)
        areas_preview_ratios = Utils.get_relative_areas_ratio(
            GdfUtils.calc_dimensions(bigger_map_area_bounds),
            bigger_paper_dimensions_mm, GdfUtils.calc_dimensions(map_area_bounds),
            paper_dimensions_mm
        )
        # automatic_filters_creating_factor = Utils.calc_map_object_scaling_factor(bigger_map_dimensions_m, bigger_paper_dimensions_mm)
    else:
        areas_preview_ratios = None
        bigger_area_gdf = None
        # automatic_filters_creating_factor = Utils.calc_map_object_scaling_factor(map_dimensions_m, paper_dimensions_mm)
    
    osm_file_name = OSM_FILE_NAME
    if(OSM_WANT_EXTRACT_AREA):
        osm_data_preprocessor = OsmDataPreprocessor(OSM_FILE_NAME, OSM_OUTPUT_FILE_NAME, OSM_WANT_EXTRACT_AREA)
        osm_file_name = osm_data_preprocessor.extract_area(map_area_gdf)
    osm_file_parser = OsmDataParser(wanted_ways, wanted_areas, unwanted_ways_tags, unwanted_areas_tags,
                                    reqired_map_area_name=f'{AREA}', get_required_area_from_osm = False)
    @time_measurement_decorator("apply file")
    def t():
        osm_file_parser.apply_file(osm_file_name)
    t()
    ways_gdf, areas_gdf = osm_file_parser.create_gdf(EPSG_DEGREE_NUMBER)
    osm_file_parser.clear_gdf()
    
    total_map_bounds = GdfUtils.get_bounds_gdf(ways_gdf, areas_gdf)
    reqired_area_polygon = map_area_gdf.unary_union
    
    #check if area is inside osm file
    if(not GdfUtils.is_polygon_inside_bounds(total_map_bounds, reqired_area_polygon)):
        #print warning
        print("Selected area map is not whole inside given osm.pbf file.")
    
   
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)
    # only for some ways categories
    
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
                             map_area_gdf, paper_dimensions_mm, areas_preview_ratios, map_dimensions_m)
    plotter.init_plot(GENERAL_DEFAULT_STYLES[StyleKey.COLOR], areas_preview_ratios)
    plotter.plot_areas()
    plotter.plot_ways()
    plotter.plot_gpxs()
    plotter.clip(total_map_bounds)
    plotter.zoom(zoom_percent_padding=1)
    plotter.plot_map_boundary()

    plotter.generate_pdf(OUTPUT_PDF_NAME)
    # plotter.show_plot()
if __name__ == "__main__":
    main()
    