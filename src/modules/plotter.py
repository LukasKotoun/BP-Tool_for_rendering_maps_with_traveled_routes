from typing import Generator

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_agg import RendererAgg
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import geometry
from shapely.geometry.polygon import Polygon
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import LinearRing, Point
import textwrap
from adjustText import adjust_text
from shapely.ops import linemerge, unary_union

from config import *
from modules.utils import Utils
from modules.gdf_utils import GdfUtils
from common.common_helpers import time_measurement


from shapely.ops import unary_union, split, linemerge


class Plotter:

    MM_TO_INCH = 25.4
    DEFAULT_CUPSTYLE = "round"

    def __init__(self, requred_area_gdf: gpd.GeoDataFrame, paper_dimensions_mm: DimensionsTuple, map_object_scaling_factor: float):
        self.reqired_area_gdf: gpd.GeoDataFrame = requred_area_gdf
        self.reqired_area_polygon: Polygon = GdfUtils.create_polygon_from_gdf(
            self.reqired_area_gdf)
        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor: float = map_object_scaling_factor
        self.city_names = []
        self.other_text = []
        self.icons = []

    def init_plot(self, map_bg_color: str, bg_gdf: gpd.GeoDataFrame, area_zoom_preview: None | DimensionsTuple = None):
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
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color)
        if (not bg_gdf.empty):
            bg_gdf.plot(ax=self.ax, color=bg_gdf[StyleKey.COLOR])

    def __plot_city_names(self, place_names_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        if (place_names_gdf.empty):
            return

        def get_place_data(city_names_gdf: gpd.GeoDataFrame) -> Generator[tuple[Point, str, str, str, int, float], None, None]:
            """Yields a tuple of city data for each city in the GeoDataFrame."""
            for data in zip(
                city_names_gdf.geometry,
                city_names_gdf['name'],
                city_names_gdf[StyleKey.COLOR],
                city_names_gdf[StyleKey.EDGE_COLOR],
                city_names_gdf[StyleKey.TEXT_FONT_SIZE],
                city_names_gdf[StyleKey.TEXT_OUTLINE_WIDTH]
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
            # todo to function

            text = self.ax.text(
                x, y, wraped_name, fontsize=fontsize, ha='center', va='center', zorder=4, color=color,
                path_effects=[pe.withStroke(linewidth=outline_width, foreground=edge_color)])
            self.city_names.append(text)

    def __plot_elevations(self, elevations_gdf: gpd.GeoDataFrame):
        if (elevations_gdf.empty):
            return

        for idx, row in elevations_gdf.iterrows():
            x, y = row.geometry.x, row.geometry.y

            # annotation aproach - does not work with adjust text lib
            # second aproach - create annotation and get cordinates and than create text from it
            # and use that text to adjusting but it will be invisible
            # peak_name = self.ax.annotate(row['name'], (x, y), textcoords="offset points", xytext=(0, 300 * self.map_object_scaling_factor), ha='center', color=row[StyleKey.COLOR],
            #     path_effects=[pe.withStroke(linewidth=row[StyleKey.TEXT_OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.TEXT_FONT_SIZE])
            # peak_ele = self.ax.annotate(row['ele'], (x, y), textcoords="offset points", xytext=(0, -300 * self.map_object_scaling_factor - row[StyleKey.WIDTH]), ha='center', color=row[StyleKey.COLOR],
            #     path_effects=[pe.withStroke(linewidth=row[StyleKey.TEXT_OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.TEXT_FONT_SIZE])

            # move text to top and bottom of the icon
            # xy_axes = self.ax.transData.transform((x, y))
            # xy_name = self.ax.transData.inverted().transform((xy_axes[0], xy_axes[1] + 300 * self.map_object_scaling_factor))
            # xy_ele = self.ax.transData.inverted().transform((xy_axes[0], xy_axes[1] - 350 * self.map_object_scaling_factor - row[StyleKey.WIDTH]))
            # #todo check if name or ele exists
            # peak_name = self.ax.text(xy_name[0], xy_name[1], row['name'], color=row[StyleKey.COLOR], ha='center',
            #                          path_effects=[pe.withStroke(linewidth=row[StyleKey.TEXT_OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.TEXT_FONT_SIZE])
            # peak_ele = self.ax.text(xy_ele[0], xy_ele[1], row['ele'], color=row[StyleKey.COLOR], ha='center',
            #                         path_effects=[pe.withStroke(linewidth=row[StyleKey.TEXT_OUTLINE_WIDTH], foreground=row[StyleKey.EDGE_COLOR])], fontsize=row[StyleKey.TEXT_FONT_SIZE])

            # self.ax.scatter(x, y, marker=row[StyleKey.ICON], color=row[StyleKey.COLOR], s=row[StyleKey.WIDTH],
            #                 edgecolor=row[StyleKey.EDGE_COLOR], linewidth=row[StyleKey.EDGEWIDTH])
            plt.plot(x, y, marker=row[StyleKey.ICON], mfc=row[StyleKey.COLOR], ms=row[StyleKey.WIDTH],
                     mec=row[StyleKey.EDGE_COLOR], mew=row[StyleKey.EDGEWIDTH])
            # self.other_text.append(peak_name)
            # self.other_text.append(peak_ele)

    @time_measurement("nodePlot")
    def plot_nodes(self, nodes_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        all_columns_present: bool = all(col in nodes_gdf.columns for col in [
            StyleKey.TEXT_FONT_SIZE, StyleKey.TEXT_OUTLINE_WIDTH, StyleKey.COLOR, StyleKey.EDGE_COLOR])
        if (nodes_gdf.empty or not all_columns_present):
            return

        place_names_gdf, rest_gdf = GdfUtils.filter_rows(
            nodes_gdf, {'place': ''}, compl=True)

        self.__plot_city_names(place_names_gdf, wrap_len)
        rest_gdf = GdfUtils.filter_rows(nodes_gdf, {'natural': 'peak'})
        self.__plot_elevations(rest_gdf)

    def __plot_line_edges(self, lines_gdf, cupstyle: str = None):
        edge_lines_gdf = GdfUtils.filter_rows(lines_gdf, {
            StyleKey.EDGE_COLOR: '', StyleKey.EDGE_LINESTYLE: '', StyleKey.EDGEWIDTH: '', StyleKey.EDGE_ALPHA: ''})

        if (edge_lines_gdf.empty):
            return
        if (cupstyle is not None):
            edge_lines_gdf[StyleKey.EDGE_CUP] = cupstyle

        groups = GdfUtils.get_groups_by_columns(
            edge_lines_gdf, [StyleKey.EDGE_CUP], [self.DEFAULT_CUPSTYLE], False)
        for capstyle, edge_lines_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CUPSTYLE

            edge_lines_group_gdf.plot(ax=self.ax, color=edge_lines_group_gdf[StyleKey.EDGE_COLOR],
                                      linewidth=edge_lines_group_gdf[StyleKey.EDGEWIDTH],
                                      linestyle=edge_lines_group_gdf[StyleKey.EDGE_LINESTYLE],
                                      alpha=edge_lines_group_gdf[StyleKey.EDGE_ALPHA],
                                      path_effects=[pe.Stroke(capstyle=capstyle)])

    def __plot_line(self, lines_gdf, cupstyle: str = None):
        lines_gdf = GdfUtils.filter_rows(lines_gdf, {
            StyleKey.COLOR: '', StyleKey.LINESTYLE: '', StyleKey.WIDTH: '', StyleKey.ALPHA: ''})
        if (lines_gdf.empty):
            return
        if (cupstyle is not None):
            lines_gdf[StyleKey.LINE_CUP] = cupstyle

        groups = GdfUtils.get_groups_by_columns(
            lines_gdf, [StyleKey.LINE_CUP], [self.DEFAULT_CUPSTYLE], False)

        for capstyle, lines_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CUPSTYLE

            lines_group_gdf.plot(ax=self.ax, color=lines_group_gdf[StyleKey.COLOR],
                                 linewidth=lines_group_gdf[StyleKey.WIDTH],
                                 linestyle=lines_group_gdf[StyleKey.LINESTYLE],
                                 alpha=lines_group_gdf[StyleKey.ALPHA],
                                 path_effects=[pe.Stroke(capstyle=capstyle)])

    def __plot_dashed_with_edge_dashed(self, gdf: gpd.GeoDataFrame, line_cupstyle: str = None, edge_cupstyle: str = None):
        if (gdf.empty):
            return
        gdf = GdfUtils.filter_rows(gdf, {StyleKey.COLOR: '', StyleKey.EDGE_COLOR: '',
                                         StyleKey.LINESTYLE: '', StyleKey.WIDTH: '', StyleKey.EDGEWIDTH: '',
                                         StyleKey.ALPHA: '', StyleKey.EDGE_ALPHA: ''})
        if (gdf.empty):
            return
        if (line_cupstyle is not None):
            gdf[StyleKey.LINE_CUP] = line_cupstyle
        if (edge_cupstyle is not None):
            gdf[StyleKey.EDGE_CUP] = edge_cupstyle

        groups = GdfUtils.get_groups_by_columns(
            gdf, [StyleKey.LINE_CUP, StyleKey.EDGE_CUP, StyleKey.EDGEWIDTH,
                  StyleKey.EDGE_COLOR, StyleKey.EDGE_ALPHA], [], False)

        for (line_cup, edge_cup, edge_width, edge_color, edge_alpha), gdf_group in groups:
            if (pd.isna(line_cup)):
                line_cup = self.DEFAULT_CUPSTYLE
            if (pd.isna(edge_cup)):
                edge_cup = self.DEFAULT_CUPSTYLE

            gdf_group.plot(ax=self.ax, color=gdf_group[StyleKey.COLOR], linestyle=gdf_group[StyleKey.LINESTYLE],
                           linewidth=gdf_group[StyleKey.WIDTH], alpha=gdf_group[StyleKey.ALPHA], path_effects=[
                pe.Stroke(
                    linewidth=edge_width, foreground=edge_color, alpha=edge_alpha,
                    capstyle=edge_cup), pe.Normal(), pe.Stroke(capstyle=line_cup)])

    def __plot_dashed_with_edge_solid(self, gdf: gpd.GeoDataFrame, line_cupstyle: str = None, edge_cupstyle: str = None):
        if (gdf.empty):
            return
        gdf = GdfUtils.filter_rows(gdf, {StyleKey.EDGE_COLOR: '', StyleKey.COLOR: '',
                                         StyleKey.EDGEWIDTH: '', StyleKey.WIDTH: '',
                                         StyleKey.ALPHA: '', StyleKey.EDGE_ALPHA: '',
                                         StyleKey.LINESTYLE: '', })
        if (gdf.empty):
            return
        if (line_cupstyle is not None):
            gdf[StyleKey.LINE_CUP] = line_cupstyle
        if (edge_cupstyle is not None):
            gdf[StyleKey.EDGE_CUP] = edge_cupstyle

        groups = GdfUtils.get_groups_by_columns(
            gdf, [StyleKey.LINE_CUP, StyleKey.EDGE_CUP], [], False)
        # todo make quciker
        for (line_cup, edge_cup), gdf_group in groups:
            if (pd.isna(line_cup)):
                line_cup = "projecting"
            if (pd.isna(edge_cup)):
                edge_cup = "projecting"
            color = gdf_group[StyleKey.COLOR]
            edge_color = gdf_group[StyleKey.EDGE_COLOR]
            linewidth = gdf_group[StyleKey.WIDTH]
            edge_linewidth = gdf_group[StyleKey.EDGEWIDTH]
            alpha = gdf_group[StyleKey.ALPHA]
            edge_alpha = gdf_group[StyleKey.EDGE_ALPHA]
            linestyle = gdf_group[StyleKey.LINESTYLE]
            edge_linestyle = "-"

            for geom in gdf_group.geometry:
                if isinstance(geom, MultiLineString):
                    for line in geom.geoms:  # Extract each LineString
                        gpd.GeoSeries(line).plot(ax=self.ax, color=edge_color,
                                                 linewidth=edge_linewidth,
                                                 alpha=edge_alpha, path_effects=[
                                                     pe.Stroke(capstyle=edge_cup)])

                        gpd.GeoSeries(line).plot(ax=self.ax, color=color, linewidth=linewidth,
                                                 alpha=alpha, linestyle=linestyle, path_effects=[
                                                     pe.Stroke(capstyle=line_cup)])
                else:
                    gpd.GeoSeries(geom).plot(ax=self.ax, color=edge_color,
                                             linewidth=edge_linewidth,
                                             alpha=edge_alpha, path_effects=[
                                                 pe.Stroke(capstyle=edge_cup)])

                    gpd.GeoSeries(geom).plot(ax=self.ax, color=color, linewidth=linewidth,
                                             alpha=alpha, linestyle=linestyle, path_effects=[
                                                 pe.Stroke(capstyle=line_cup)])

    def __plot_ways_normal(self, gdf: gpd.GeoDataFrame, plotEdges: bool = False, cross_roads_by_zindex=False, line_cupstyle: str = None, edge_cupstyle: str = None):
        """Plot ways based on z-index and capstyles. 

        Args:
            gdf (gpd.GeoDataFrame): _description_
            plotEdges (bool, optional): _description_. Defaults to False.
        """
        if (gdf.empty):
            return

        if (plotEdges and not cross_roads_by_zindex):
            # plot edge where line is solid or only edge is ploted
            self.__plot_line_edges(GdfUtils.filter_rows(
                gdf, [{StyleKey.LINESTYLE: ['-', 'solid']}, {StyleKey.COLOR: '~'}]), edge_cupstyle)

        groups = GdfUtils.get_groups_by_columns(
            gdf, [StyleKey.ZINDEX], [], False)
        for zindex, ways_group_gdf in groups:
            # crossroads only on ways with same zindex
            if (plotEdges and cross_roads_by_zindex):
                self.__plot_line_edges(GdfUtils.filter_rows(
                    gdf, [{StyleKey.LINESTYLE: ['-', 'solid']}, {StyleKey.COLOR: '~'}]), edge_cupstyle)
            # lines - line is solid or edge does not exists, dashed_with_edge_lines - line is dashed and edge exists
            rest_lines, dashed_with_edge_lines = GdfUtils.filter_rows(
                ways_group_gdf, [{StyleKey.LINESTYLE: ['-', 'solid']}, {StyleKey.EDGE_COLOR: '~'}], compl=True)
            # there will be filter for ways with specific edge style (edgeEffect)
            ways_dashed_edge_solid, ways_dashed_edge_dashed = GdfUtils.filter_rows(
                dashed_with_edge_lines, {StyleKey.EDGE_LINESTYLE: ['-', 'solid']}, compl=True)

            self.__plot_dashed_with_edge_dashed(
                ways_dashed_edge_dashed, line_cupstyle, edge_cupstyle)
            self.__plot_dashed_with_edge_solid(
                ways_dashed_edge_solid, line_cupstyle, edge_cupstyle)
            self.__plot_line(rest_lines, line_cupstyle)

    def __plot_bridges(self, bridges_gdf: gpd.GeoDataFrame):
        if (bridges_gdf.empty):
            return
        # can be merged edges and center -- using pe

        def plot_bridges_edges(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {StyleKey.BRIDGE_EDGE_COLOR: '', StyleKey.BRIDGE_EDGE_WIDTH: '',
                      StyleKey.EDGE_LINESTYLE: '', StyleKey.EDGE_ALPHA: ''})

            if (gdf.empty):
                return

            gdf.plot(ax=self.ax, color=gdf[StyleKey.BRIDGE_EDGE_COLOR],
                     linewidth=gdf[StyleKey.BRIDGE_EDGE_WIDTH],
                     linestyle=gdf[StyleKey.EDGE_LINESTYLE],
                     alpha=gdf[StyleKey.EDGE_ALPHA],
                     path_effects=[pe.Stroke(capstyle="butt")])

        def plot_bridges_center(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {StyleKey.BRIDGE_WIDTH: '', StyleKey.BRIDGE_COLOR: '',
                      StyleKey.LINESTYLE: '', StyleKey.ALPHA: ''})
            if (gdf.empty):
                return

            gdf.plot(ax=self.ax, color=gdf[StyleKey.BRIDGE_COLOR],
                     linewidth=gdf[StyleKey.BRIDGE_WIDTH],
                     linestyle=gdf[StyleKey.LINESTYLE],
                     alpha=gdf[StyleKey.ALPHA],
                     path_effects=[pe.Stroke(capstyle="butt")])

        def plot_ways_on_bridges(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {StyleKey.PLOT_ON_BRIDGE: ""})
            if (gdf.empty):
                return
            self.__plot_ways_normal(gdf, True), False

        groups = GdfUtils.get_groups_by_columns(
            bridges_gdf, ['layer'], [], False)
        for layer, bridge_layer_gdf in groups:
            plot_bridges_edges(bridge_layer_gdf.copy())
            plot_bridges_center(bridge_layer_gdf.copy())
            plot_ways_on_bridges(bridge_layer_gdf.copy())

    def __plot_tunnels(self, tunnels_gdf):
        if (tunnels_gdf.empty):
            return
        for layer, tunnel_layer_gdf in tunnels_gdf.groupby("layer"):
            self.__plot_ways_normal(tunnel_layer_gdf, True, False)

    @time_measurement("wayplot")
    def plot_ways(self, ways_gdf: gpd.GeoDataFrame, areas_ways_gdf: gpd.GeoDataFrame, plot_over_filter=None):
        if (ways_gdf.empty):
            return

        # water ways and tunnels
        waterways_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'waterway': ''}, compl=True)
        waterways_tunnel_gdf, waterways_gdf = GdfUtils.filter_rows(
            waterways_gdf, {'tunnel': ''}, compl=True)

        self.__plot_tunnels(waterways_tunnel_gdf)
        self.__plot_ways_normal(waterways_gdf, True, False)

        # normal tunnels
        ways_tunnel_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'tunnel': ''}, compl=True)

        self.__plot_tunnels(ways_tunnel_gdf)

        # normal ways
        ways_bridge_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'bridge': ''}, compl=True)

        self.__plot_ways_normal(ways_gdf, True, False)

        # bridges
        self.__plot_bridges(ways_bridge_gdf)

        # ways to prevent crossroads
        if (plot_over_filter is not None):
            self.__plot_ways_normal(GdfUtils.filter_rows(
                ways_gdf, plot_over_filter), True, True, 'butt', 'butt')

    @time_measurement("areaPlot")
    def plot_areas(self, areas_gdf: gpd.GeoDataFrame):
        if (areas_gdf.empty):
            return
        # plot face
        face_areas_gdf = GdfUtils.filter_rows(
            areas_gdf, {StyleKey.COLOR: ''})
        if (not face_areas_gdf.empty):
            face_areas_gdf.plot(
                ax=self.ax, color=face_areas_gdf[StyleKey.COLOR], alpha=face_areas_gdf[StyleKey.ALPHA])
        # plot bounds
        edge_areas_gdf = GdfUtils.filter_rows(areas_gdf,
                                              {StyleKey.EDGE_COLOR: '', StyleKey.WIDTH: '', StyleKey.EDGE_LINESTYLE: ''})
        if (edge_areas_gdf.empty):
            return
        groups = GdfUtils.get_groups_by_columns(
            edge_areas_gdf, [StyleKey.EDGE_CUP], [self.DEFAULT_CUPSTYLE], False)
        for capstyle, edge_areas_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CUPSTYLE
            edge_areas_group_gdf.plot(
                ax=self.ax, facecolor='none', edgecolor=edge_areas_group_gdf[StyleKey.EDGE_COLOR],
                linewidth=edge_areas_group_gdf[StyleKey.WIDTH], alpha=edge_areas_group_gdf[StyleKey.EDGE_ALPHA],
                linestyle=edge_areas_group_gdf[StyleKey.EDGE_LINESTYLE],
                path_effects=[pe.Stroke(capstyle=capstyle)])

    @time_measurement("gpxsPlot")
    def plot_gpxs(self, gpxs_gdf: gpd.GeoDataFrame, line_width_multiplier: float):

        if (gpxs_gdf.empty):
            return
        self.__plot_ways_normal(gpxs_gdf, True, False)

        # gpxs_edge_gdf = GdfUtils.filter_rows(
        #     gpxs_gdf, {StyleKey.EDGE_COLOR: '', StyleKey.EDGE_LINESTYLE: '', StyleKey.WIDTH: ''})
        # self.__plot_line_edges(gpxs_gdf)
        # if (not gpxs_edge_gdf.empty):
        #     gpxs_edge_gdf.plot(ax=self.ax, color=gpxs_gdf[StyleKey.EDGE_COLOR], linewidth=gpxs_gdf[StyleKey.WIDTH],
        #                        linestyle=gpxs_gdf[StyleKey.EDGE_LINESTYLE], alpha=gpxs_gdf[StyleKey.ALPHA],
        #                        path_effects=[pe.Stroke(capstyle="round")])

        # gpxs_gdf[StyleKey.WIDTH] = gpxs_gdf[StyleKey.WIDTH] * \
        #     self.map_object_scaling_factor * line_width_multiplier
        # gpxs_gdf.plot(ax=self.ax, color=gpxs_gdf[StyleKey.COLOR], linewidth=gpxs_gdf[StyleKey.WIDTH],
        #               linestyle=gpxs_gdf[StyleKey.LINESTYLE], alpha=gpxs_gdf[StyleKey.ALPHA],
        #               path_effects=[pe.Stroke(capstyle="round")])

    @time_measurement("adjusting")
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
        # remove text that is over other text
        # todo remove text that is over other text
        if (self.other_text):
            adjust_text(self.city_names, force_text=0.2,
                        objects=self.other_text)
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

    def clip(self, crs: str, whole_map_polygon: Polygon, reqired_area_gdf: gpd.GeoDataFrame | None = None, clipped_area_color: str = 'white'):

        if (reqired_area_gdf is not None):
            reqired_area_polygon = GdfUtils.create_polygon_from_gdf(
                reqired_area_gdf)
        else:
            reqired_area_polygon = self.reqired_area_polygon

        clipping_polygon = whole_map_polygon.difference(reqired_area_polygon)
        if (not GdfUtils.is_geometry_inside_geometry(clipping_polygon, whole_map_polygon)):
            return

        clipping_polygon = gpd.GeoDataFrame(
            geometry=[clipping_polygon], crs=crs)

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
