from typing import Generator

import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.backends.backend_agg import RendererAgg
import pandas as pd
import geopandas as gpd
from shapely import geometry
from shapely.geometry.polygon import Polygon
from shapely.geometry.linestring import LineString
import textwrap
from adjustText import adjust_text

from config import * 
from modules.gdf_utils import GdfUtils
from common.common_helpers import time_measurement_decorator

class Plotter:    
    
    MM_TO_INCH = 25.4
    def __init__(self, requred_area_gdf: gpd.GeoDataFrame, paper_dimensions_mm: DimensionsTuple, map_object_scaling_factor: float):
        self.reqired_area_gdf = requred_area_gdf
        self.reqired_area_polygon = GdfUtils.create_polygon_from_gdf(self.reqired_area_gdf)
        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor = map_object_scaling_factor


    def init_plot(self, map_bg_color: str, area_zoom_preview: None | DimensionsTuple = None):
        self.fig, self.ax = plt.subplots(figsize=(self.paper_dimensions_mm[0]/self.MM_TO_INCH,
                                                  self.paper_dimensions_mm[1]/self.MM_TO_INCH)) #convert mm to inch
        if(area_zoom_preview is None):
            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # No margins
        else:
            left_margin = (1 - area_zoom_preview[0])/2
            right_margin = 1 - left_margin
            bottom_margin = (1 - area_zoom_preview[1])/2
            top_margin = 1 - bottom_margin
            self.fig.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin) 
            
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color, linewidth=1)
        


    def plot_city_names(self, place_names_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        if(place_names_gdf.empty):
            return
        place_names_gdf[StyleKey.OUTLINE_WIDTH] = place_names_gdf[StyleKey.OUTLINE_WIDTH] * self.map_object_scaling_factor
        
        def get_place_data(city_names_gdf: gpd.GeoDataFrame) -> Generator[tuple[Point, str, str, str, int, float], None, None]:
            """Yields a tuple of city data for each city in the GeoDataFrame."""
            for data in zip(
                city_names_gdf.geometry,
                city_names_gdf['name'],
                city_names_gdf[StyleKey.COLOR],
                city_names_gdf[StyleKey.BGCOLOR],
                city_names_gdf[StyleKey.FONT_SIZE],
                city_names_gdf[StyleKey.OUTLINE_WIDTH]
            ):
                yield data

        for geom, name, color, bgcolor, fontsize, outline_width in get_place_data(place_names_gdf):
            if(wrap_len is not None):
                wraped_name = textwrap.fill(name, width = wrap_len)
            else:
                wraped_name = name
            x = geom.x
            y = geom.y
            # weight='bold'
            self.ax.text(
            x, y, wraped_name, fontsize = fontsize, ha = 'center', va = 'center', zorder = 4, color = color, 
            path_effects = [patheffects.withStroke(linewidth = outline_width, foreground = bgcolor)]) 

            
        
    @time_measurement_decorator("nodePlot")
    def plot_nodes(self, nodes_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        all_columns_present = all(col in nodes_gdf.columns for col in [StyleKey.FONT_SIZE, StyleKey.OUTLINE_WIDTH, StyleKey.COLOR, StyleKey.BGCOLOR])
        if(nodes_gdf.empty or not all_columns_present):
            return
        #todo checks for att
        nodes_gdf[StyleKey.FONT_SIZE] = nodes_gdf[StyleKey.FONT_SIZE] * self.map_object_scaling_factor
        place_names_gdf, rest_gdf = GdfUtils.filter_gdf_in(nodes_gdf, 'place')
        place_names_gdf = GdfUtils.filter_gdf_in(place_names_gdf, 'name')[0]
        self.plot_city_names(place_names_gdf, wrap_len)
        
        #todo filter out elevation without ele - in map_generator
        #in peak plot check if have name
        
        # todo function and set in config constants the text force 
        # adjust_text(self.ax.texts, force_text = 0.25, avoid_self= False)
       

            
            
    def __plot_highways(self, highways_gdf: gpd.GeoDataFrame, edgeSize):
        if(highways_gdf.empty):
            return
        if(StyleKey.EDGE_COLOR in highways_gdf and StyleKey.LINESTYLE in highways_gdf):
            edge_highways_gdf = GdfUtils.filter_gdf_not_in(highways_gdf, StyleKey.EDGE_COLOR, [pd.NA, 'none'])[0]
            edge_highways_gdf = GdfUtils.filter_gdf_in(edge_highways_gdf, StyleKey.LINESTYLE, [pd.NA, 'none', '-'])[0]
            if(not edge_highways_gdf.empty):
                edge_highways_gdf.plot(ax=self.ax, color=edge_highways_gdf[StyleKey.EDGE_COLOR],
                                    linewidth=edge_highways_gdf[StyleKey.LINEWIDTH] + edgeSize, alpha=edge_highways_gdf[StyleKey.ALPHA],
                                    path_effects = [patheffects.Stroke(capstyle="round", joinstyle='round')])
            
        highways_gdf.plot(ax = self.ax, color = highways_gdf[StyleKey.COLOR], linewidth = highways_gdf[StyleKey.LINEWIDTH],
                           linestyle = highways_gdf[StyleKey.LINESTYLE], 
                           path_effects = [patheffects.Stroke(capstyle = "round", joinstyle = 'round')])
        
        #todo add outline width

    def __plot_waterways(self, waterways_gdf: gpd.GeoDataFrame, edgeSize):
        if(waterways_gdf.empty):
            return
        
        #todo add outline width
        if(StyleKey.EDGE_COLOR in waterways_gdf and StyleKey.LINESTYLE in waterways_gdf):
            edge_waterways_gdf = GdfUtils.filter_gdf_not_in(waterways_gdf, StyleKey.EDGE_COLOR, [pd.NA, 'none'])[0]
            edge_waterways_gdf = GdfUtils.filter_gdf_in(edge_waterways_gdf, StyleKey.LINESTYLE, [pd.NA, 'none', '-'])[0]
            if(not edge_waterways_gdf.empty):
                edge_waterways_gdf.plot(ax=self.ax, color=edge_waterways_gdf[StyleKey.EDGE_COLOR],
                                    linewidth=edge_waterways_gdf[StyleKey.LINEWIDTH] + edgeSize, alpha=edge_waterways_gdf[StyleKey.ALPHA],
                                    path_effects = [patheffects.Stroke(capstyle="round", joinstyle='round')])
            
        waterways_gdf.plot(ax = self.ax, color = waterways_gdf[StyleKey.COLOR], linewidth = waterways_gdf[StyleKey.LINEWIDTH],
                           linestyle = waterways_gdf[StyleKey.LINESTYLE],
                           path_effects=[patheffects.Stroke(capstyle = "round", joinstyle = 'round')])
   

    def __plot_railways(self, railways_gdf: gpd.GeoDataFrame, rail_bg_width_offset: float, tram_second_line_spacing: float):
        if(railways_gdf.empty):
            return
        
        tram_gdf, rails_gdf = GdfUtils.filter_gdf_in(railways_gdf, 'railway', ['tram'])
        if(not tram_gdf.empty):
            tram_gdf.plot(ax = self.ax, color = tram_gdf[StyleKey.COLOR], linewidth = tram_gdf[StyleKey.LINEWIDTH],
                          alpha=tram_gdf[StyleKey.ALPHA], path_effects = [
                    patheffects.Stroke(capstyle="round", joinstyle = 'round'),
                    patheffects.withTickedStroke(angle = -90, capstyle = "round",  spacing = tram_second_line_spacing, length=0.2),
                    patheffects.withTickedStroke(angle = 90, capstyle = "round", spacing = tram_second_line_spacing, length=0.2)])

        if(not rails_gdf.empty and StyleKey.BGCOLOR in rails_gdf):
             rails_gdf.plot(ax = self.ax, color = rails_gdf[StyleKey.BGCOLOR],
                            linewidth = rails_gdf[StyleKey.LINEWIDTH] + rail_bg_width_offset,
                            alpha = rails_gdf[StyleKey.ALPHA], path_effects = [
                    patheffects.Stroke(capstyle = "round", joinstyle = 'round')])
             
             rails_gdf.plot(ax = self.ax, color = rails_gdf[StyleKey.COLOR], linewidth = rails_gdf[StyleKey.LINEWIDTH],
                            alpha = rails_gdf[StyleKey.ALPHA], linestyle = rails_gdf[StyleKey.LINESTYLE])        
             
    # def __plot_bridges(self, bridge)       
    @time_measurement_decorator("wayplot")            
    def plot_ways(self, ways_gdf: gpd.GeoDataFrame, ways_width_multiplier: float):
        if(ways_gdf.empty or StyleKey.LINEWIDTH not in ways_gdf 
           or StyleKey.COLOR not in ways_gdf):
            return
        edgeSize = 2 * self.map_object_scaling_factor

        ways_gdf[StyleKey.LINEWIDTH] = ways_gdf[StyleKey.LINEWIDTH] * self.map_object_scaling_factor * ways_width_multiplier

        bridges_gdf, rest_gdf = GdfUtils.filter_gdf_in(ways_gdf, 'bridge', ['yes'])
        waterways_gdf, rest_gdf = GdfUtils.filter_gdf_in(rest_gdf, 'waterway')
        highways_gdf, rest_gdf = GdfUtils.filter_gdf_in(rest_gdf, 'highway')
        railways_gdf, rest_gdf = GdfUtils.filter_gdf_in(rest_gdf, 'railway')

        self.__plot_waterways(waterways_gdf, edgeSize)
        self.__plot_highways(highways_gdf, edgeSize)
        
        self.__plot_railways(railways_gdf, 2 * self.map_object_scaling_factor, 15 * self.map_object_scaling_factor)
        #TODO TO FUNC 
        def get_bridge_data(bridges_gdf: gpd.GeoDataFrame) -> Generator[tuple[LineString, str, str, str, str, str, float, float], None, None]:
            """Yields a tuple of city data for each city in the GeoDataFrame."""
            for data in zip(
                bridges_gdf.geometry,
                bridges_gdf["railway"],
                bridges_gdf[StyleKey.COLOR],
                bridges_gdf[StyleKey.BGCOLOR],
                bridges_gdf[StyleKey.BRIDGE_EDGE_COLOR],
                bridges_gdf[StyleKey.LINESTYLE],
                bridges_gdf[StyleKey.LINEWIDTH],
                bridges_gdf[StyleKey.ALPHA]
                #todo add outline width or linewidth %, 
            ):
                yield data
        #todo order by layer
        bridges_gdf = GdfUtils.filter_gdf_not_in(bridges_gdf, StyleKey.BRIDGE_EDGE_COLOR, [pd.NA, 'none'])[0]
        for geom, railway, color, bgcolor, bridge_edge_color, linestyle, linewidth, alpha in get_bridge_data(bridges_gdf):
            x_values, y_values = geom.xy
            #notna will be checked in validator
            if (railway == "rail"):
                if(not pd.notna(color) or not pd.notna(bgcolor) or not pd.notna(bridge_edge_color)):
                    continue
                self.ax.plot(x_values, y_values, color = bridge_edge_color, linewidth=2*linewidth + 3 * edgeSize,
                            alpha = alpha, solid_capstyle="butt")
                self.ax.plot(x_values, y_values, color = color, linewidth=2*linewidth,
                            alpha = alpha, solid_capstyle="butt")
                self.ax.plot(x_values, y_values, color = bgcolor, linewidth=linewidth+edgeSize,
                            alpha = alpha)
                self.ax.plot(x_values, y_values, color = color, linewidth=linewidth,
                            alpha = alpha, linestyle = linestyle)
            else:        
                if(not pd.notna(color) or not pd.notna(bridge_edge_color)):
                    continue
                self.ax.plot(x_values, y_values, color=bridge_edge_color, linewidth=linewidth + edgeSize, linestyle=linestyle,
                            alpha=alpha, solid_capstyle="butt", solid_joinstyle = 'round')
                self.ax.plot(x_values, y_values, color=color, linewidth=linewidth, linestyle=linestyle,
                            alpha=alpha, solid_capstyle="round", solid_joinstyle = 'round')
        

    @time_measurement_decorator("areaPlot")            
    def plot_areas(self, areas_gdf: gpd.GeoDataFrame, areas_bounds_multiplier: float):
        if(areas_gdf.empty):
            return
        # [pd.NA, 'none'] - get all that dont have nan or 'none' (if does not have that column will return true for everything - need check if have that column)
        # plot face
        if(StyleKey.COLOR in areas_gdf):
            face_areas_gdf = GdfUtils.filter_gdf_not_in(areas_gdf, StyleKey.COLOR, [pd.NA, 'none'])[0]
            if(not face_areas_gdf.empty and StyleKey.COLOR in face_areas_gdf):
                face_areas_gdf.plot(ax=self.ax, color = face_areas_gdf[StyleKey.COLOR], alpha = face_areas_gdf[StyleKey.ALPHA])
        # plot bounds
        if(StyleKey.EDGE_COLOR in areas_gdf):
            edge_areas_gdf = GdfUtils.filter_gdf_not_in(areas_gdf, StyleKey.EDGE_COLOR, [pd.NA, 'none'])[0]
            if(not edge_areas_gdf.empty and StyleKey.EDGE_COLOR in edge_areas_gdf and 
            StyleKey.LINEWIDTH in edge_areas_gdf):
                edge_areas_gdf[StyleKey.LINEWIDTH] = edge_areas_gdf[StyleKey.LINEWIDTH] * self.map_object_scaling_factor * areas_bounds_multiplier
                edge_areas_gdf.plot(
                    ax=self.ax, facecolor = 'none', edgecolor = edge_areas_gdf[StyleKey.EDGE_COLOR],
                    linewidth = edge_areas_gdf[StyleKey.LINEWIDTH], alpha = edge_areas_gdf[StyleKey.ALPHA],
                    linestyle = edge_areas_gdf[StyleKey.LINESTYLE], 
                    path_effects = [patheffects.Stroke(capstyle = "round", joinstyle = 'round')])

    
    @time_measurement_decorator("gpxsPlot")            
    def plot_gpxs(self, gpxs_gdf: gpd.GeoDataFrame):
        gpxs_gdf.plot(ax = self.ax, color="red", linewidth = 20 * self.map_object_scaling_factor)
        
    @time_measurement_decorator("adjusting")
    def adjust_texts(self, text_bounds_overflow_threshold: float):
        # #remove overflown texts before adjusting, smaller threshold - can be adjusted
        # if(not allow_text_bounds_overflow):
        #     r = self.fig.canvas.get_renderer()
        #     for text in self.ax.texts:
        #         text_Bbox = text.get_tightbbox(renderer=r).transformed(self.ax.transData.inverted())
        #         bbox_polygon = geometry.box(text_Bbox.x0, text_Bbox.y0, text_Bbox.x1, text_Bbox.y1)
        #         if(not GdfUtils.is_polygon_inside_polygon_threshold(bbox_polygon, self.reqired_area_polygon, text_bounds_overflow_threshold * 0.8)):
        #             text.remove()
        adjust_text(self.ax.texts, force_text = 0.2)
        
        #remove overflown texts after adjusting
        if(text_bounds_overflow_threshold > 0):
            r: RendererAgg = self.fig.canvas.get_renderer()
            for text in self.ax.texts:
                text_Bbox = text.get_tightbbox(renderer=r).transformed(self.ax.transData.inverted())
                bbox_polygon = geometry.box(text_Bbox.x0, text_Bbox.y0, text_Bbox.x1, text_Bbox.y1)
                if(not GdfUtils.is_polygon_inside_polygon_threshold(bbox_polygon, self.reqired_area_polygon, text_bounds_overflow_threshold)):
                    text.remove()
        
    def clip(self, whole_map_polygon: Polygon, reqired_area_gdf: gpd.GeoDataFrame | None = None, clipped_area_color: str = 'white'):
        
        if(reqired_area_gdf is not None):
            reqired_area_polygon = GdfUtils.create_polygon_from_gdf(reqired_area_gdf)
        else:
            reqired_area_polygon = self.reqired_area_polygon
            
        clipping_polygon = whole_map_polygon.difference(reqired_area_polygon)
        if(not GdfUtils.is_polygon_inside_polygon(clipping_polygon, whole_map_polygon)):
            return
        
        # clipping_polygon = geometry.MultiPolygon([clipping_polygon]) - epsg in constructor
        clipping_polygon = gpd.GeoDataFrame(geometry=[clipping_polygon], crs=f"EPSG:{EPSG_DEGREE_NUMBER}")
        
        clipping_polygon.plot(ax=self.ax, color=clipped_area_color, alpha=1, zorder=3)
        
    def plot_area_boundary(self, area_gdf: gpd.GeoDataFrame | None = None, color: str = 'black', linewidth: float = 1):
        if(area_gdf is None):
            self.reqired_area_gdf.boundary.plot(ax=self.ax, color=color, linewidth=linewidth*self.map_object_scaling_factor, zorder=3)
        else:
            area_gdf.boundary.plot(ax=self.ax, color=color, linewidth=linewidth*self.map_object_scaling_factor, zorder=3)
            
    #use function to get gdf sizes - same as in ways
    #todo change to names
    def zoom(self, zoom_percent_padding: float = 1):
        zoom_padding = zoom_percent_padding / 100 #convert from percent
        
        zoom_bounds = GdfUtils.get_bounds_gdf(self.reqired_area_gdf)
        width, height = GdfUtils.get_dimensions(zoom_bounds)

        width_buffer = width * zoom_padding  # 1% of width
        height_buffer = height * zoom_padding  # 1% of height
     
        self.ax.set_xlim([zoom_bounds[WorldSides.WEST] - width_buffer, zoom_bounds[WorldSides.EAST] + width_buffer])  # Expand x limits
        self.ax.set_ylim([zoom_bounds[WorldSides.SOUTH] - height_buffer, zoom_bounds[WorldSides.NORTH] + height_buffer])  # Expand y limits
         
        
    def generate_pdf(self, pdf_name: str):
        plt.savefig(f'{pdf_name}.pdf', format='pdf', transparent=True, pad_inches=0.1)
    
    def show_plot(self):
        plt.show()
