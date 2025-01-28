from typing import Generator

import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.backends.backend_agg import RendererAgg
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import geometry
from shapely.geometry.polygon import Polygon
from shapely.geometry.linestring import LineString
import textwrap
from adjustText import adjust_text

from config import *
from modules.utils import Utils
from modules.gdf_utils import GdfUtils
from common.common_helpers import time_measurement_decorator


class Plotter:

    MM_TO_INCH = 25.4

    def __init__(self, requred_area_gdf: gpd.GeoDataFrame, paper_dimensions_mm: DimensionsTuple, map_object_scaling_factor: float):
        self.reqired_area_gdf: gpd.GeoDataFrame = requred_area_gdf
        self.reqired_area_polygon: Polygon = GdfUtils.create_polygon_from_gdf(
            self.reqired_area_gdf)
        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor: float = map_object_scaling_factor
        self.city_names = []
        self.other_text = []
        self.icons = []

    def init_plot(self, map_bg_color: str, area_zoom_preview: None | DimensionsTuple = None):
        self.fig, self.ax = plt.subplots(figsize=(self.paper_dimensions_mm[0]/self.MM_TO_INCH,
                                                  # convert mm to inch
                                                  self.paper_dimensions_mm[1]/self.MM_TO_INCH))
        if (area_zoom_preview is None):
            self.fig.subplots_adjust(
                left=0, right=1, top=1, bottom=0)  # No margins
        else:
            left_margin = (1 - area_zoom_preview[0])/2
            right_margin = 1 - left_margin
            bottom_margin = (1 - area_zoom_preview[1])/2
            top_margin = 1 - bottom_margin
            self.fig.subplots_adjust(
                left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin)

        self.ax.axis('off')
        # self.ax.set_aspect('equal')
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color, linewidth=1)

    def __plot_city_names(self, place_names_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        if (place_names_gdf.empty):
            return
        place_names_gdf[StyleKey.OUTLINE_WIDTH] = place_names_gdf[StyleKey.OUTLINE_WIDTH] * \
            self.map_object_scaling_factor

        def get_place_data(city_names_gdf: gpd.GeoDataFrame) -> Generator[tuple[Point, str, str, str, int, float], None, None]:
            """Yields a tuple of city data for each city in the GeoDataFrame."""
            for data in zip(
                city_names_gdf.geometry,
                city_names_gdf['name'],
                city_names_gdf[StyleKey.COLOR],
                city_names_gdf[StyleKey.EDGE_COLOR],
                city_names_gdf[StyleKey.FONT_SIZE],
                city_names_gdf[StyleKey.OUTLINE_WIDTH]
            ):
                yield data

        for geom, name, color, edge_color, fontsize, outline_width in get_place_data(place_names_gdf):
            if (wrap_len is not None):
                wraped_name = textwrap.fill(name, width=wrap_len)
            else:
                wraped_name = name
            x = geom.x
            y = geom.y
            # weight='bold'
            # todo to func?
            text = self.ax.text(
                x, y, wraped_name, fontsize=fontsize, ha='center', va='center', zorder=4, color=color,
                path_effects=[patheffects.withStroke(linewidth=outline_width, foreground=edge_color)])
            self.city_names.append(text)

    def __plot_elevations(self, elevations_gdf: gpd.GeoDataFrame):
        if (elevations_gdf.empty):
            return
        #todo edit
        elevations_gdf[StyleKey.ICON_SIZE] = elevations_gdf[StyleKey.ICON_SIZE] * \
            (np.sqrt(3) / 4) * (self.map_object_scaling_factor ** 2) # icons size is in area of triangle -todo edit 
        elevations_gdf[StyleKey.ICON_EDGE] = elevations_gdf[StyleKey.ICON_EDGE] * \
             self.map_object_scaling_factor
        elevations_gdf[StyleKey.OUTLINE_WIDTH] = elevations_gdf[StyleKey.OUTLINE_WIDTH] * \
            self.map_object_scaling_factor
        for idx, row in elevations_gdf.iterrows():
            x, y = row.geometry.x, row.geometry.y

            # peak_name = self.ax.annotate(row['name'], (x, y), textcoords="offset points", xytext=(0, 300 * self.map_object_scaling_factor), ha='center', color=row[StyleKey.COLOR],
            #     path_effects=[patheffects.withStroke(linewidth=row[StyleKey.OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.FONT_SIZE])
            # peak_ele = self.ax.annotate(row['ele'], (x, y), textcoords="offset points", xytext=(0, -300 * self.map_object_scaling_factor - row[StyleKey.ICON_SIZE]), ha='center', color=row[StyleKey.COLOR],
            #     path_effects=[patheffects.withStroke(linewidth=row[StyleKey.OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.FONT_SIZE])

            # move text to top and bottom of the icon
            #todo edit with icon size
            xy_axes = self.ax.transData.transform((x, y))
            xy_name = self.ax.transData.inverted().transform((xy_axes[0], xy_axes[1] + 300 * self.map_object_scaling_factor))
            xy_ele = self.ax.transData.inverted().transform((xy_axes[0], xy_axes[1] - 350 * self.map_object_scaling_factor - row[StyleKey.ICON_SIZE]))
            
            peak_name = self.ax.text(xy_name[0], xy_name[1], row['name'], color=row[StyleKey.COLOR], ha='center',
                                     path_effects=[patheffects.withStroke(linewidth=row[StyleKey.OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.FONT_SIZE])
            peak_ele = self.ax.text(xy_ele[0], xy_ele[1], row['ele'], color=row[StyleKey.COLOR], ha='center',
                                    path_effects=[patheffects.withStroke(linewidth=row[StyleKey.OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.FONT_SIZE])
            
            self.ax.scatter(x, y, marker=row[StyleKey.ICON], color=row[StyleKey.ICON_COLOR], s=row[StyleKey.ICON_SIZE],
                            edgecolor=row[StyleKey.EDGE_COLOR], linewidth=row[StyleKey.ICON_EDGE])
         
            # self.other_text.append(peak_name)
            # self.other_text.append(peak_ele)
            # second aproach - create annotation and get cordinates and than create text from it and use that text to adjusting

    @time_measurement_decorator("nodePlot")
    def plot_nodes(self, nodes_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        all_columns_present: bool = all(col in nodes_gdf.columns for col in [
            StyleKey.FONT_SIZE, StyleKey.OUTLINE_WIDTH, StyleKey.COLOR, StyleKey.EDGE_COLOR])
        if (nodes_gdf.empty or not all_columns_present):
            return

        # todo checks for att
        nodes_gdf[StyleKey.FONT_SIZE] = nodes_gdf[StyleKey.FONT_SIZE] * \
            self.map_object_scaling_factor
        place_names_gdf, rest_gdf = GdfUtils.filter_gdf_column_values(
            nodes_gdf, 'place', compl=True)
        self.__plot_city_names(place_names_gdf, wrap_len)
        rest_gdf = GdfUtils.filter_gdf_column_values(
            rest_gdf, 'natural', ['peak'])
        self.__plot_elevations(rest_gdf)

    #? create function filter_for_line_edges....
    def __plot_line_edges(self, lines_gdf):
        if (lines_gdf.empty):
            return
        if (StyleKey.EDGE_COLOR in lines_gdf and StyleKey.LINESTYLE in lines_gdf
           and StyleKey.EDGE_WIDTH_RATIO in lines_gdf):
            # filter rows without values on linestyle and edge color
            edge_lines_gdf = GdfUtils.filter_gdf_columns_values_AND(
                lines_gdf, [StyleKey.EDGE_COLOR, StyleKey.EDGE_WIDTH_RATIO])
            # filter out all lines that have other than solid line
            edge_lines_gdf = GdfUtils.filter_gdf_column_values(
                edge_lines_gdf, StyleKey.LINESTYLE, [pd.NA, '-'])
            if (not edge_lines_gdf.empty):
                edge_lines_gdf[StyleKey.LINEWIDTH] = edge_lines_gdf[StyleKey.LINEWIDTH] + \
                    edge_lines_gdf[StyleKey.LINEWIDTH] * \
                    edge_lines_gdf[StyleKey.EDGE_WIDTH_RATIO]
                edge_lines_gdf.plot(ax=self.ax, color=edge_lines_gdf[StyleKey.EDGE_COLOR],
                                    linewidth=edge_lines_gdf[StyleKey.LINEWIDTH],
                                    alpha=edge_lines_gdf[StyleKey.ALPHA],
                                    # path_effects=[patheffects.Stroke(capstyle="butt", joinstyle='round')])
                                    path_effects=[patheffects.Stroke(capstyle="round", joinstyle='round')])

    def __plot_highways(self, highways_gdf: gpd.GeoDataFrame, plotEdges: bool = False):
        if (highways_gdf.empty):
            return
        if (plotEdges):
            self.__plot_line_edges(highways_gdf)

        highways_gdf.plot(ax=self.ax, color=highways_gdf[StyleKey.COLOR], linewidth=highways_gdf[StyleKey.LINEWIDTH],
                          linestyle=highways_gdf[StyleKey.LINESTYLE], alpha=highways_gdf[StyleKey.ALPHA],
                          path_effects=[patheffects.Stroke(capstyle="round", joinstyle='round')])

    def __plot_waterways(self, waterways_gdf: gpd.GeoDataFrame, plotEdges: bool = False):
        if (waterways_gdf.empty):
            return
        if (plotEdges):
            self.__plot_line_edges(waterways_gdf)
        waterways_gdf.plot(ax=self.ax, color=waterways_gdf[StyleKey.COLOR], linewidth=waterways_gdf[StyleKey.LINEWIDTH],
                           linestyle=waterways_gdf[StyleKey.LINESTYLE], alpha=waterways_gdf[StyleKey.ALPHA],
                           path_effects=[patheffects.Stroke(capstyle="round", joinstyle='round')])

    def __plot_railways(self, railways_gdf: gpd.GeoDataFrame, rail_bg_width_offset: float, tram_second_line_spacing: float):
        if (railways_gdf.empty):
            return

        tram_gdf, rails_gdf = GdfUtils.filter_gdf_column_values(
            railways_gdf, 'railway', ['tram'], compl=True)
        if (not tram_gdf.empty):
            tram_gdf.plot(ax=self.ax, color=tram_gdf[StyleKey.COLOR], linewidth=tram_gdf[StyleKey.LINEWIDTH],
                          alpha=tram_gdf[StyleKey.ALPHA], path_effects=[
                patheffects.Stroke(capstyle="round", joinstyle='round'),
                patheffects.withTickedStroke(
                    angle=-90, capstyle="round",  spacing=tram_second_line_spacing, length=0.2),
                patheffects.withTickedStroke(angle=90, capstyle="round", spacing=tram_second_line_spacing, length=0.2)])


        if (not rails_gdf.empty and StyleKey.EDGE_COLOR in rails_gdf):
            rails_gdf.plot(ax=self.ax, color=rails_gdf[StyleKey.EDGE_COLOR],
                           linewidth=rails_gdf[StyleKey.LINEWIDTH] +
                           rail_bg_width_offset,
                           alpha=rails_gdf[StyleKey.ALPHA], path_effects=[
                patheffects.Stroke(capstyle="projecting", joinstyle='round')])

            rails_gdf.plot(ax=self.ax, color=rails_gdf[StyleKey.COLOR], linewidth=rails_gdf[StyleKey.LINEWIDTH],
                           alpha=rails_gdf[StyleKey.ALPHA], linestyle=rails_gdf[StyleKey.LINESTYLE])

    def __plot_bridges(self, bridges_gdf: gpd.GeoDataFrame):
        if (bridges_gdf.empty):
            return

        def plot_bridges_edges(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_gdf_columns_values_AND(
                gdf, [StyleKey.BRIDGE_EDGE_COLOR, StyleKey.BRIDGE_WIDTH_RATIO])
            if (gdf.empty):
                return
            gdf[StyleKey.LINEWIDTH] = gdf[StyleKey.LINEWIDTH] + gdf[StyleKey.LINEWIDTH] * \
                (gdf[StyleKey.BRIDGE_WIDTH_RATIO] +
                 gdf[StyleKey.EDGE_WIDTH_RATIO])
            gdf.plot(ax=self.ax, color=gdf[StyleKey.BRIDGE_EDGE_COLOR],
                     linewidth=gdf[StyleKey.LINEWIDTH],
                     alpha=gdf[StyleKey.ALPHA],
                     path_effects=[patheffects.Stroke(capstyle="butt", joinstyle='round')])

        def plot_bridges_center(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_gdf_columns_values_AND(
                gdf, [StyleKey.BRIDGE_WIDTH_RATIO, StyleKey.BRIDGE_COLOR])
            if (gdf.empty):
                return
            gdf[StyleKey.LINEWIDTH] = gdf[StyleKey.LINEWIDTH] + \
                gdf[StyleKey.LINEWIDTH] * gdf[StyleKey.BRIDGE_WIDTH_RATIO]
            gdf.plot(ax=self.ax, color=gdf[StyleKey.BRIDGE_COLOR],
                     linewidth=gdf[StyleKey.LINEWIDTH],
                     alpha=gdf[StyleKey.ALPHA],
                     path_effects=[patheffects.Stroke(capstyle="butt", joinstyle='round')])

        def plot_ways_on_bridges(gdf: gpd.GeoDataFrame):
            waterways_gdf, rest_gdf = GdfUtils.filter_gdf_column_values(
                gdf, 'waterway', compl=True)
            highways_gdf, rest_gdf = GdfUtils.filter_gdf_column_values(
                rest_gdf, 'highway', compl=True)
            railways_gdf = GdfUtils.filter_gdf_column_values(
                rest_gdf, 'railway')
            self.__plot_waterways(waterways_gdf)
            # filter out all highways that have other than solid line
            # todo - filter not solid lines but use new column to filter by - whether to plot on or not 
            highways_gdf = GdfUtils.filter_gdf_column_values(
                highways_gdf, StyleKey.LINESTYLE, [pd.NA, 'none', '-'])
            self.__plot_highways(highways_gdf, False)
            self.__plot_railways(
                railways_gdf, 2 * self.map_object_scaling_factor, 15 * self.map_object_scaling_factor)

        if ('layer' in bridges_gdf.columns):
            GdfUtils.change_columns_to_numeric(bridges_gdf, ['layer'])
            bridges_gdf['layer'] = bridges_gdf['layer'].fillna(0)  # convert NaN/None to 0
            bridges_gdf = GdfUtils.sort_gdf_by_column(bridges_gdf, "layer")

        for layer, bridge_layer_gdf in bridges_gdf.groupby("layer"):
            plot_bridges_edges(bridge_layer_gdf.copy())
            plot_bridges_center(bridge_layer_gdf.copy())
            plot_ways_on_bridges(bridge_layer_gdf.copy())

    @time_measurement_decorator("wayplot")
    def plot_ways(self, ways_gdf: gpd.GeoDataFrame, ways_width_multiplier: float):
        if (ways_gdf.empty or StyleKey.LINEWIDTH not in ways_gdf
           or StyleKey.COLOR not in ways_gdf):
            return
        ways_gdf[StyleKey.LINEWIDTH] = ways_gdf[StyleKey.LINEWIDTH] * \
            self.map_object_scaling_factor * ways_width_multiplier
            
        if ('layer' in ways_gdf.columns):
            GdfUtils.change_columns_to_numeric(ways_gdf, ['layer'])
            ways_gdf['layer'] = ways_gdf['layer'].fillna(0)  # convert NaN/None to 0
            ways_gdf = GdfUtils.sort_gdf_by_column(ways_gdf, "layer")  # todo - je potřeba řadit?
        #?? filter to plot bridges where bridge is yes and column to print bridge is true - given in settings
        bridges_gdf, rests_gdf = GdfUtils.filter_gdf_column_values(
            ways_gdf, 'bridge', ['yes'], compl=True)
      
        for layer, rest_gdf in rests_gdf.groupby("layer"):
            waterways_gdf, rest_gdf = GdfUtils.filter_gdf_column_values(
                rest_gdf, 'waterway', compl=True)
            highways_gdf, rest_gdf = GdfUtils.filter_gdf_column_values(
                rest_gdf, 'highway', compl=True)
            railways_gdf = GdfUtils.filter_gdf_column_values(
                rest_gdf, 'railway')

            self.__plot_waterways(waterways_gdf)
            self.__plot_highways(highways_gdf, True)
            self.__plot_railways(
                railways_gdf, 2 * self.map_object_scaling_factor, 15 * self.map_object_scaling_factor)
        
        self.__plot_bridges(bridges_gdf)

    @time_measurement_decorator("areaPlot")
    def plot_areas(self, areas_gdf: gpd.GeoDataFrame, areas_bounds_multiplier: float):
        if (areas_gdf.empty):
            return
        # [pd.NA, 'none'] - get all that dont have nan or 'none' (if does not have that column will return true for everything - need check if have that column)
        # plot face
        if (StyleKey.COLOR in areas_gdf):
            face_areas_gdf = GdfUtils.filter_gdf_column_values(
                areas_gdf, StyleKey.COLOR, [pd.NA], True)
            if (not face_areas_gdf.empty and StyleKey.COLOR in face_areas_gdf):
                face_areas_gdf.plot(
                    ax=self.ax, color=face_areas_gdf[StyleKey.COLOR], alpha=face_areas_gdf[StyleKey.ALPHA])
        # plot bounds
        if (StyleKey.EDGE_COLOR in areas_gdf):
            edge_areas_gdf = GdfUtils.filter_gdf_column_values(
                areas_gdf, StyleKey.EDGE_COLOR, [pd.NA], True)
            if (not edge_areas_gdf.empty and StyleKey.EDGE_COLOR in edge_areas_gdf and
               StyleKey.LINEWIDTH in edge_areas_gdf):
                edge_areas_gdf[StyleKey.LINEWIDTH] = edge_areas_gdf[StyleKey.LINEWIDTH] * \
                    self.map_object_scaling_factor * areas_bounds_multiplier
                edge_areas_gdf.plot(
                    ax=self.ax, facecolor='none', edgecolor=edge_areas_gdf[StyleKey.EDGE_COLOR],
                    linewidth=edge_areas_gdf[StyleKey.LINEWIDTH], alpha=edge_areas_gdf[StyleKey.ALPHA],
                    linestyle=edge_areas_gdf[StyleKey.LINESTYLE],
                    path_effects=[patheffects.Stroke(capstyle="round", joinstyle='round')])

    @time_measurement_decorator("gpxsPlot")
    def plot_gpxs(self, gpxs_gdf: gpd.GeoDataFrame, line_width_multiplier: float):

        if (gpxs_gdf.empty):
            return
        # gpxs_gdf.plot(ax=self.ax, color="red", linewidth=20 *
        #               self.map_object_scaling_factor)
        # self.__plot_line_edges(gpxs_gdf)
        gpxs_gdf[StyleKey.LINEWIDTH] = gpxs_gdf[StyleKey.LINEWIDTH] * \
            self.map_object_scaling_factor * line_width_multiplier
        gpxs_gdf.plot(ax=self.ax, color=gpxs_gdf[StyleKey.COLOR], linewidth=gpxs_gdf[StyleKey.LINEWIDTH],
                      linestyle=gpxs_gdf[StyleKey.LINESTYLE], alpha=gpxs_gdf[StyleKey.ALPHA],
                      path_effects=[patheffects.Stroke(capstyle="round", joinstyle='round')])

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
        
        # adjust_text(
        #     self.other_text,
        #     only_move={"texts": "y"},
        #     avoid_self=False,
        # )
        if(self.other_text):
            adjust_text(self.city_names, force_text=0.2, objects=self.other_text)
        else:
            adjust_text(self.city_names, force_text=0.2)
        # text force
        # remove overflown texts after adjusting
        if (text_bounds_overflow_threshold > 0):
            r: RendererAgg = self.fig.canvas.get_renderer()
            for text in self.ax.texts:
                text_Bbox = text.get_tightbbox(renderer=r).transformed(
                    self.ax.transData.inverted())
                bbox_polygon = geometry.box(
                    text_Bbox.x0, text_Bbox.y0, text_Bbox.x1, text_Bbox.y1)
                if (not GdfUtils.is_geometry_inside_geometry_threshold(bbox_polygon, self.reqired_area_polygon, text_bounds_overflow_threshold)):
                    text.remove()

    def clip(self, epsg: int, whole_map_polygon: Polygon, reqired_area_gdf: gpd.GeoDataFrame | None = None, clipped_area_color: str = 'white'):

        if (reqired_area_gdf is not None):
            reqired_area_polygon = GdfUtils.create_polygon_from_gdf(
                reqired_area_gdf)
        else:
            reqired_area_polygon = self.reqired_area_polygon

        clipping_polygon = whole_map_polygon.difference(reqired_area_polygon)
        if (not GdfUtils.is_geometry_inside_geometry(clipping_polygon, whole_map_polygon)):
            return

        # clipping_polygon = geometry.MultiPolygon([clipping_polygon]) - epsg in constructor
        clipping_polygon = gpd.GeoDataFrame(
            geometry=[clipping_polygon], crs=f"EPSG:{epsg}")

        clipping_polygon.plot(
            ax=self.ax, color=clipped_area_color, alpha=1, zorder=3)

    def plot_area_boundary(self, area_gdf: gpd.GeoDataFrame | None = None, color: str = 'black', linewidth: float = 1):
        if (area_gdf is None):
            self.reqired_area_gdf.boundary.plot(
                ax=self.ax, color=color, linewidth=linewidth*self.map_object_scaling_factor, zorder=3)
        else:
            area_gdf.boundary.plot(
                ax=self.ax, color=color, linewidth=linewidth*self.map_object_scaling_factor, zorder=3)

    def zoom(self, zoom_percent_padding: float = 1):
        zoom_padding = zoom_percent_padding / 100  # convert from percent

        zoom_bounds = GdfUtils.get_bounds_gdf(self.reqired_area_gdf)
        width, height = Utils.get_dimensions(zoom_bounds)

        width_buffer = width * zoom_padding  # 1% of width
        height_buffer = height * zoom_padding  # 1% of height

        self.ax.set_xlim([zoom_bounds[WorldSides.WEST] - width_buffer,
                         # Expand x limits
                          zoom_bounds[WorldSides.EAST] + width_buffer])
        self.ax.set_ylim([zoom_bounds[WorldSides.SOUTH] - height_buffer,
                         # Expand y limits
                          zoom_bounds[WorldSides.NORTH] + height_buffer])

    def generate_pdf(self, pdf_name: str):
        plt.savefig(f'{pdf_name}.pdf', format='pdf',
                    transparent=True, pad_inches=0.1)

    def show_plot(self):
        plt.show()
