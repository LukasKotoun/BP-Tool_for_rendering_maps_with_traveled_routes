from matplotlib import patheffects
import warnings
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from shapely import geometry


from config import * 
from modules.gdf_utils import GdfUtils
from common.common_helpers import time_measurement_decorator
from modules.utils import Utils

class Plotter:    
    
    MM_TO_INCH = 25.4
    def __init__(self, general_styles: FeatureStyles, ways_element_gdf, areas_element_gdf, gpxs_gdf,
                 requred_area_gdf, paper_dimensions_mm, map_object_scaling_factor):
        self.general_styles = general_styles
        self.ways_element_gdf = ways_element_gdf
        self.areas_element_gdf = areas_element_gdf
        self.gpxs_gdf = gpxs_gdf
        self.reqired_area_gdf = requred_area_gdf
        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor = map_object_scaling_factor

    def init_plot(self, map_bg_color, areas_ratios_preview = None):
        self.fig, self.ax = plt.subplots(figsize=(self.paper_dimensions_mm[0]/self.MM_TO_INCH,self.paper_dimensions_mm[1]/self.MM_TO_INCH)) #convert mm to inch
        if(areas_ratios_preview is None):
            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # No margins
        else:
            left_margin = (1-areas_ratios_preview[0])/2
            right_margin = 1 - left_margin
            bottom_margin = (1-areas_ratios_preview[1])/2
            top_margin = 1 -bottom_margin
            self.fig.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin) 
            
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color, linewidth=1)
        
    def __plot_highways(self,highways_gdf):
        if(highways_gdf.empty):
            return
        
        for line, color, linewidth in zip(highways_gdf.geometry, highways_gdf[StyleKey.COLOR], highways_gdf[StyleKey.LINEWIDTH]):

            x, y = line.xy
            self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle = 'round')
            
    def __plot_waterways(self, waterways_gdf):
        if(waterways_gdf.empty):
            return
        waterways_gdf.plot(ax = self.ax,color=waterways_gdf[StyleKey.COLOR], linewidth = waterways_gdf[StyleKey.LINEWIDTH])
   
        # for line, color, linewidth in zip(waterways_gdf.geometry, waterways_gdf[StyleKey.COLOR], waterways_gdf[StyleKey.LINEWIDTH]):
        #     x, y = line.xy
        #     self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle='round')

                    
            
    def __plot_railways(self,railways_gdf, rail_bg_width_offset, tram_second_line_spacing):
        #todo change ploting style
        if(railways_gdf.empty):
            return
        
        tram_gdf, rails_gdf = GdfUtils.filter_gdf_in(railways_gdf, 'railway', ['tram'])
        if(not tram_gdf.empty):
            for line, color, linewidth in zip(tram_gdf.geometry, tram_gdf[StyleKey.COLOR], tram_gdf[StyleKey.LINEWIDTH]):
                x, y = line.xy 
                self.ax.plot(x, y, color=color, linewidth = linewidth, solid_capstyle='round', alpha=0.6,path_effects=[
                patheffects.withTickedStroke(angle=-90, spacing=tram_second_line_spacing, length=0.05),
                patheffects.withTickedStroke(angle=90, spacing=tram_second_line_spacing, length=0.05)])
                
        if(not rails_gdf.empty and StyleKey.BGCOLOR in rails_gdf):

            for line, color, bg_color, linewidth in zip(
            rails_gdf.geometry, rails_gdf[StyleKey.COLOR],
            rails_gdf[StyleKey.BGCOLOR], rails_gdf[StyleKey.LINEWIDTH]
            ):
                x, y = line.xy
                self.ax.plot(x, y, color = bg_color, linewidth = linewidth + rail_bg_width_offset)
                self.ax.plot(x, y, color = color, linewidth = linewidth, linestyle=(0, (5, 5)))
    
   
    @time_measurement_decorator("wayplot")            
    def plot_ways(self):
        if(self.ways_element_gdf.empty or StyleKey.LINEWIDTH not in self.ways_element_gdf 
           or StyleKey.COLOR not in self.ways_element_gdf):
            return
      
        self.ways_element_gdf[StyleKey.LINEWIDTH] = self.ways_element_gdf[StyleKey.LINEWIDTH] * self.map_object_scaling_factor
        waterways_gdf, rest_gdf = GdfUtils.filter_gdf_in(self.ways_element_gdf, 'waterway')
        self.__plot_waterways(waterways_gdf)
        
        highways_gdf, rest_gdf = GdfUtils.filter_gdf_in(rest_gdf, 'highway')
        self.__plot_highways(highways_gdf)
        
        railways_gdf, rest_gdf = GdfUtils.filter_gdf_in(rest_gdf, 'railway')
        self.__plot_railways(railways_gdf, 2*self.map_object_scaling_factor,15*self.map_object_scaling_factor)


    @time_measurement_decorator("areaPlot")            
    def plot_areas(self):
        # [pd.NA, 'none'] - get all that dont have nan or 'none' (if does not have that column will return true for everything - need check if have that column)
        # plot face
        if(StyleKey.COLOR in self.areas_element_gdf):
            face_areas_gdf = GdfUtils.filter_gdf_not_in(self.areas_element_gdf, StyleKey.COLOR, [pd.NA, 'none'])[0]
            if(not face_areas_gdf.empty and StyleKey.COLOR in face_areas_gdf):
                face_areas_gdf.plot(ax=self.ax, color = face_areas_gdf[StyleKey.COLOR], alpha=face_areas_gdf[StyleKey.ALPHA])
        # plot bounds
        if(StyleKey.EDGE_COLOR in self.areas_element_gdf):
            edge_areas_gdf = GdfUtils.filter_gdf_not_in(self.areas_element_gdf, StyleKey.EDGE_COLOR, [pd.NA, 'none'])[0]
            if(not edge_areas_gdf.empty and StyleKey.EDGE_COLOR in edge_areas_gdf and 
            StyleKey.LINEWIDTH in edge_areas_gdf):
                #todo to for with round cupstyles
                edge_areas_gdf[StyleKey.LINEWIDTH] = edge_areas_gdf[StyleKey.LINEWIDTH] * self.map_object_scaling_factor
                edge_areas_gdf.plot(ax=self.ax, facecolor = 'none', edgecolor = edge_areas_gdf[StyleKey.EDGE_COLOR],
                                            linewidth = edge_areas_gdf[StyleKey.LINEWIDTH], alpha=edge_areas_gdf[StyleKey.ALPHA])

    
    @time_measurement_decorator("gpxsPlot")            
    def plot_gpxs(self):
        self.gpxs_gdf.plot(ax = self.ax, color="red", linewidth = 20 * self.map_object_scaling_factor)

        
    def clip(self, whole_map_gdf = None, reqired_area_gdf = None, clipped_area_color = 'white'):
        if(self.areas_element_gdf.empty and self.ways_element_gdf.empty):
            return
        if(whole_map_gdf is not None):
            whole_area_polygon = GdfUtils.create_polygon_from_gdf(whole_map_gdf)
        else:
            whole_area_polygon = GdfUtils.create_polygon_from_gdf_bounds(self.ways_element_gdf, self.areas_element_gdf)
            
        if(reqired_area_gdf is not None):
            reqired_area_polygon = GdfUtils.create_polygon_from_gdf(reqired_area_gdf)
        else:
            reqired_area_polygon = GdfUtils.create_polygon_from_gdf(self.reqired_area_gdf)
            
        clipping_polygon = whole_area_polygon.difference(reqired_area_polygon)
        if(not GdfUtils.is_polygon_inside_polygon(clipping_polygon, whole_area_polygon)):
            return
        
        # clipping_polygon = geometry.MultiPolygon([clipping_polygon]) - epsg in constructor
        clipping_polygon = gpd.GeoDataFrame(geometry=[clipping_polygon], crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        
        clipping_polygon.plot(ax=self.ax, color=clipped_area_color, alpha=1, zorder=3)
        
    
    def plot_area_boundary(self, area_gdf = None, color = 'black', linewidth = 1):
        if(area_gdf is None):
            self.reqired_area_gdf.boundary.plot(ax=self.ax, color=color, linewidth=linewidth*self.map_object_scaling_factor, zorder=3)
        else:
            area_gdf.boundary.plot(ax=self.ax, color=color, linewidth=linewidth*self.map_object_scaling_factor, zorder=3)
            
    #use function to get gdf sizes - same as in ways
    #todo change to names
    def zoom(self, zoom_percent_padding = 1):
        zoom_padding = zoom_percent_padding / 100 #convert from percent
        
        zoom_bounds = GdfUtils.get_bounds_gdf(self.reqired_area_gdf)
        width, height = GdfUtils.get_dimensions(zoom_bounds)

        width_buffer = width * zoom_padding  # 1% of width
        height_buffer = height * zoom_padding  # 1% of height
     
        self.ax.set_xlim([zoom_bounds[WorldSides.WEST] - width_buffer, zoom_bounds[WorldSides.EAST] + width_buffer])  # Expand x limits
        self.ax.set_ylim([zoom_bounds[WorldSides.SOUTH] - height_buffer, zoom_bounds[WorldSides.NORTH] + height_buffer])  # Expand y limits
        
        
    def generate_pdf(self, pdf_name):
        plt.savefig(f'{pdf_name}.pdf', format='pdf', transparent=True)
    
    def show_plot(self):
        plt.show()
