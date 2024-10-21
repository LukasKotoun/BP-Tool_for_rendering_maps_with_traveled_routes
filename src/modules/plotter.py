from matplotlib import patheffects
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely import geometry

from config import * 
from modules.gdf_utils import GdfUtils
from common.common_helpers import time_measurement_decorator
from modules.utils import Utils

class Plotter:    
    
    MM_TO_INCH = 25.4
    def __init__(self, gdf_utils, geo_data_styler, ways_gdf, areas_gdf, gpxs_gdf,
                 requred_area_gdf, paper_dimensions_mm, areas_preview_ratios, map_dimensions_m):
        self.gdf_utils = gdf_utils
        self.geo_data_styler = geo_data_styler
        self.ways_gdf = ways_gdf
        self.areas_gdf = areas_gdf
        self.gpxs_gdf = gpxs_gdf
        self.reqired_area_gdf = requred_area_gdf
        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor = Utils.calc_map_object_scaling_factor(map_dimensions_m, paper_dimensions_mm, areas_preview_ratios)

    def init_plot(self, map_bg_color, pdf_to_area_ratios = None):
        self.fig, self.ax = plt.subplots(figsize=(self.paper_dimensions_mm[0]/self.MM_TO_INCH,self.paper_dimensions_mm[1]/self.MM_TO_INCH)) #convert mm to inch
        if(pdf_to_area_ratios is None):
            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # No margins
        else:
            left_margin = (1-pdf_to_area_ratios[0])/ 2
            right_margin = 1 - left_margin
            bottom_margin = (1-pdf_to_area_ratios[1])/2
            top_margin = 1 -bottom_margin

            self.fig.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin) 
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color, linewidth=1)
        
    def __plot_highways(self,highways_gdf):
        if(highways_gdf.empty or StyleKey.COLOR not in highways_gdf and StyleKey.LINEWIDTH not in highways_gdf):
            return
        
        for line, color, linewidth in zip(highways_gdf.geometry, highways_gdf[StyleKey.COLOR], highways_gdf[StyleKey.LINEWIDTH]):
            x, y = line.xy
            self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle = 'round')
            
    def __plot_waterways(self,waterways_gdf):
        if(waterways_gdf.empty or StyleKey.COLOR not in waterways_gdf and StyleKey.LINEWIDTH not in waterways_gdf):
            return
        waterways_gdf.plot(ax = self.ax,color=waterways_gdf[StyleKey.COLOR], linewidth = waterways_gdf[StyleKey.LINEWIDTH])
        
        # for line, color, linewidth in zip(waterways_gdf.geometry, waterways_gdf[StyleKey.COLOR], waterways_gdf[StyleKey.LINEWIDTH]):
        #     x, y = line.xy
        #     self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle='round')

                    
            
    def __plot_railways(self,railways_gdf, rail_bg_width_offset, tram_second_line_spacing):
        #todo change ploting style
        if(railways_gdf.empty or StyleKey.COLOR not in railways_gdf or StyleKey.LINEWIDTH not in railways_gdf):
            return
        
        tram_gdf, rails_gdf = self.gdf_utils.filter_gdf_in(railways_gdf, 'railway', ['tram'])
        
        # tram_gdf = self.gdf_utils.aggregate_close_lines(tram_gdf,5)
        # rails_gdf = self.gdf_utils.aggregate_close_lines(rails_gdf,5)
        if(not tram_gdf.empty):
            for line, color, linewidth in zip(tram_gdf.geometry, tram_gdf[StyleKey.COLOR], tram_gdf[StyleKey.LINEWIDTH]):
                x, y = line.xy 
                self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle='round', alpha=0.6,path_effects=[
                patheffects.withTickedStroke(angle=-90, spacing=tram_second_line_spacing, length=0.05),
                patheffects.withTickedStroke(angle=90, spacing=tram_second_line_spacing, length=0.05)])
                
        if(not rails_gdf.empty):
            if(StyleKey.BGCOLOR not in rails_gdf):
                rails_gdf = self.geo_data_styler.assign_styles_to_gdf(rails_gdf, {'railway': []}, [StyleKey.BGCOLOR])
                # rails_gdf = self.geo_data_styler.assign_styles_to_gdf(rails_gdf, {'railway': ['rail']}, [StyleKey.BGCOLOR]) #todo solve double adding
            
            for line, color, bg_color,linewidth in zip(rails_gdf.geometry, rails_gdf[StyleKey.COLOR], rails_gdf[StyleKey.BGCOLOR], rails_gdf[StyleKey.LINEWIDTH]):
                x, y = line.xy
                self.ax.plot(x, y, color=bg_color, linewidth = linewidth + rail_bg_width_offset)
                self.ax.plot(x, y, color=color, linewidth =  linewidth ,linestyle=(0,(5,5)))
    
   
    @time_measurement_decorator("wayplot")            
    def plot_ways(self):
        
        if(self.ways_gdf.empty):
            return
        self.ways_gdf[StyleKey.LINEWIDTH] = self.ways_gdf[StyleKey.LINEWIDTH] * self.map_object_scaling_factor
        
        waterways_gdf, rest_gdf = self.gdf_utils.filter_gdf_in(self.ways_gdf, 'waterway')
        self.__plot_waterways(waterways_gdf)
        
        highways_gdf, rest_gdf = self.gdf_utils.filter_gdf_in(rest_gdf, 'highway')
        self.__plot_highways(highways_gdf)
        
        railways_gdf, rest_gdf = self.gdf_utils.filter_gdf_in(rest_gdf, 'railway')
        self.__plot_railways(railways_gdf, 2*self.map_object_scaling_factor,15*self.map_object_scaling_factor)


            
    def plot_areas(self):
        if(StyleKey.COLOR in self.areas_gdf):
            #todo bounds tag filter
            self.areas_gdf.plot(ax=self.ax, color = self.areas_gdf[StyleKey.COLOR] , alpha=1)
        else:
            pass
    
    def plot_gpxs(self):
        self.gpxs_gdf.plot(ax = self.ax,color="red", linewidth = 20*self.map_object_scaling_factor)

        
    def clip(self, whole_area_bounds, clipped_area_color = 'white'):
        #clip
        if(self.areas_gdf.empty):
            return
        #todo function 
        whole_area_polygon = geometry.Polygon([
            (whole_area_bounds[WorldSides.EAST], whole_area_bounds[WorldSides.SOUTH]),  
            (whole_area_bounds[WorldSides.EAST], whole_area_bounds[WorldSides.NORTH]),  
            (whole_area_bounds[WorldSides.WEST], whole_area_bounds[WorldSides.NORTH]),  
            (whole_area_bounds[WorldSides.WEST], whole_area_bounds[WorldSides.SOUTH]),  
            (whole_area_bounds[WorldSides.EAST], whole_area_bounds[WorldSides.SOUTH])   # Closing the polygon
        ])
      
        clipping_polygon = whole_area_polygon.difference(self.reqired_area_gdf.unary_union)
        # clipping_polygon = geometry.MultiPolygon([clipping_polygon])
        clipping_polygon = gpd.GeoDataFrame(geometry=[clipping_polygon], crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        
        clipping_polygon.plot(ax=self.ax, color=clipped_area_color, alpha=1, zorder=3)
        
    
    def plot_map_boundary(self, color = 'black', linewidth = 1):
        self.reqired_area_gdf.boundary.plot(ax=self.ax, color=color, linewidth=linewidth, zorder=3)
 
    #use function to get gdf sizes - same as in ways
    #todo change to names
    def zoom(self, area_for_padding = None, zoom_percent_padding = 1):
        zoom_padding = zoom_percent_padding / 100 #convert from percent
        zoom_bounds = GdfUtils.get_bounds_gdf(self.reqired_area_gdf)
        # for preview page
        if(area_for_padding is not None):
            width, height = GdfUtils.calc_dimensions(GdfUtils.get_bounds_gdf(area_for_padding))
        else:
            width, height = GdfUtils.calc_dimensions(zoom_bounds)
        
        width_buffer = width * zoom_padding  # 1% of width
        height_buffer = height * zoom_padding  # 1% of height

        self.ax.set_xlim([zoom_bounds[WorldSides.WEST] - width_buffer, zoom_bounds[WorldSides.EAST] + width_buffer])  # Expand x limits
        self.ax.set_ylim([zoom_bounds[WorldSides.SOUTH] - height_buffer, zoom_bounds[WorldSides.NORTH] + height_buffer])  # Expand y limits
        
        
    def generate_pdf(self, pdf_name):
        plt.savefig(f'{pdf_name}.pdf', format='pdf', transparent=True)
    
    def show_plot(self):
        plt.show()
