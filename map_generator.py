import sys

from config import * 
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.osm_data_parser import OsmDataParser
from modules.styles_assigner import StyleAssigner
from modules.plotter import Plotter
from modules.gpx_processer import GpxProcesser
from modules.common_helpers import time_measurement_decorator


@time_measurement_decorator("main")
def main():
    # osm_dir = '/zfs-pool/home/xkotou08/BP/'
    # osm_file = 'cz'
    # place_name = 'Czech Republic'
    osm_dir = './osm_files/'
    
    osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{OSM_FILE_NAME}{OSM_FILE_EXTENSION}')
    # osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm',[(-18.14143,65.68868),(-18.08538,65.68868),(-18.08538,65.67783),(-18.14143,65.67783)]) #island
    # osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm',[(6.94872,4.84293),(6.99314,4.84293),(6.99314,4.81603),(6.94872,4.81603)]) #afrika
    # osm_data_preprocessor = OsmDataPreprocessor(f'{osm_dir}{osm_file}.osm.pbf',f'{place_name}',"new osm name")
    get_required_area_from_osm = False #from settings if true dont use reqired_area_gdf, need to send area name for osm cutting
    reqired_area_gdf = GdfUtils.get_area_gdf(AREA)
    

    osm_file_name = osm_data_preprocessor.extract_area(reqired_area_gdf)
    osm_file_parser = OsmDataParser(wanted_ways,wanted_areas,unwanted_ways_tags, unwanted_areas_tags,
                                    reqired_map_area_name=f'{AREA}', get_required_area_from_osm = get_required_area_from_osm)
    @time_measurement_decorator("apply file")
    def t():
        osm_file_parser.apply_file(osm_file_name)
    t()
    #todo try to make all in meters and than convert for ploting only
    
    reqired_area_polygon = reqired_area_gdf.unary_union
    ways_gdf, areas_gdf = osm_file_parser.create_gdf(EPSG_DEGREE_NUMBER)
    osm_file_parser.clear_gdf()
    
    total_map_bounds = GdfUtils.get_bounds_gdf(ways_gdf, areas_gdf)
    #check if area is inside osm file
    if(not GdfUtils.is_polygon_inside_bounds(total_map_bounds, reqired_area_polygon)):
        #todo error handle class
        print("Selected area map must be inside given osm.pbf file")
        sys.exit()  
    
    
    geo_data_styler = StyleAssigner(GdfUtils, CATEGORIES_STYLES, GENERAL_DEFAULT_STYLES)
    gpx_processer =  GpxProcesser('./gpxs')
    gpxs_gdf = gpx_processer.get_gpxs_gdf(EPSG_DEGREE_NUMBER)
    #todo check if gpx go somewhere outside reqired_area
   
        
    # only for some ways categories
    # ways_gdf = GdfUtils.filter_short_ways(ways_gdf, 10)
    #todo styles for ways and areas separeated
    ways_gdf = geo_data_styler.assign_styles_to_gdf(ways_gdf, wanted_ways, [StyleKey.COLOR, StyleKey.ZINDEX, StyleKey.LINEWIDTH])
    areas_gdf = geo_data_styler.assign_styles_to_gdf(areas_gdf, wanted_areas, [StyleKey.COLOR, StyleKey.ZINDEX])
    ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, StyleKey.ZINDEX)
    areas_gdf = GdfUtils.sort_gdf_by_column(areas_gdf, StyleKey.ZINDEX)
    
    map_orientation = GdfUtils.get_map_orientation(reqired_area_gdf)
    
    #todo check for custom - without paper size 
    #also paper size custom, where to calc own side - always set 
    paper_size_mm = Utils.get_paper_size_mm(map_orientation, PAPER_SIZE)
    #want preview....
    #paper or custom or custom with only one
    if(WANT_PREVIEW):
        bigger_area_gdf = GdfUtils.get_area_gdf(PREVIEW_AREA)
        bigger_map_orientation = GdfUtils.get_map_orientation(bigger_area_gdf)
        bigger_paper_size_mm = Utils.get_paper_size_mm(bigger_map_orientation, PREVIEW_PAPER_SIZE)
        reqired_area_bounds  = GdfUtils.get_bounds_gdf(reqired_area_gdf) 
        bigger_area_bounds = GdfUtils.get_bounds_gdf(bigger_area_gdf) 
        area_ratios = Utils.get_areas_ratio(
            GdfUtils.calc_dimensions(bigger_area_bounds),
            bigger_paper_size_mm, GdfUtils.calc_dimensions(reqired_area_bounds), paper_size_mm
        )
       
    else:
        area_ratios = None
        bigger_area_gdf = None
    print(area_ratios)
    plotter = Plotter(GdfUtils, geo_data_styler, ways_gdf, areas_gdf, gpxs_gdf,
                             reqired_area_gdf, paper_size_mm, area_ratios)
    plotter.init_plot(GENERAL_DEFAULT_STYLES[StyleKey.COLOR], area_ratios)
    plotter.plot_areas()
    plotter.plot_ways()
    plotter.plot_gpxs()
    plotter.clip(total_map_bounds)
    plotter.zoom(zoom_percent_padding=1)
    plotter.plot_map_boundary()

    plotter.generate_pdf(f'./pdfs/{OUTPUT_PDF_NAME}')
    # plotter.show_plot()
if __name__ == "__main__":
    main()
    