from typing import Generator

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
# from matplotlib import line2d
from matplotlib.lines import Line2D


from matplotlib.text import Text, Annotation
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.transforms import Bbox
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
import numpy as np


from shapely.ops import unary_union, split, linemerge


class Plotter:

    MM_TO_INCH = 25.4
    DEFAULT_CUPSTYLE = "round"
    TEXT_EXPAND_PERCENT = 10

    def __init__(self, requred_area_gdf: gpd.GeoDataFrame, paper_dimensions_mm: DimensionsTuple, map_object_scaling_factor: float, text_bounds_overflow_threshold: float):
        self.reqired_area_gdf: gpd.GeoDataFrame = requred_area_gdf
        self.reqired_area_polygon: Polygon = GdfUtils.create_polygon_from_gdf(
            self.reqired_area_gdf)

        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor: float = map_object_scaling_factor
        self.texts_and_markers_bboxs = []
        self.text_bounds_overflow_threshold = text_bounds_overflow_threshold

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
        self.reqired_area_polygon_display = Polygon(self.ax.transData.transform(
            np.array(self.reqired_area_polygon.exterior.coords)))

    # todo to gdf utils
    def expand_bbox(self, bbox: Bbox, percent_expand: int = 0) -> Bbox:
        if (percent_expand == 0):
            return bbox
        width = bbox.x1 - bbox.x0
        height = bbox.y1 - bbox.y0
        expand_x = (width * percent_expand) / 100
        expand_y = (height * percent_expand) / 100
        expanded_bbox = Bbox.from_extents(bbox.x0 - expand_x, bbox.y0 - expand_y,
                                          bbox.x1 + expand_x, bbox.y1 + expand_y)
        return expanded_bbox

    def __check_bbox_position(self, bbox_to_overlap: Bbox, bbox_to_overflow: Bbox, bbox_list: list[Bbox]) -> bool:
        # check overlap with other bbox
        for bbox2 in bbox_list:
            if (bbox2.overlaps(bbox_to_overlap)):
                return False
        if (self.text_bounds_overflow_threshold == 0):
            return True
        # check if bbox is inside required area
        bbox_to_overflow = bbox_to_overflow.transformed(
            self.ax.transData.inverted())
        bbox_polygon = geometry.box(
            bbox_to_overflow.x0, bbox_to_overflow.y0, bbox_to_overflow.x1, bbox_to_overflow.y1)
        return GdfUtils.is_geometry_inside_geometry_threshold(bbox_polygon, self.reqired_area_polygon, self.text_bounds_overflow_threshold)
        # return GdfUtils.is_geometry_inside_geometry_threshold(bbox_polygon, self.reqired_area_polygon_display, self.text_bounds_overflow_threshold)

    def __plot_text_on_point(self, row, text: str, store_bbox: bool = True, check_bbox_position: bool = True) -> Text | None:
        text_annotation: Annotation = self.ax.text(row.geometry.x, row.geometry.y, text, color=row[StyleKey.TEXT_COLOR], fontsize=row[StyleKey.TEXT_FONT_SIZE], family=row[StyleKey.TEXT_FONTFAMILY],
                                                   weight=row[StyleKey.TEXT_WEIGHT], style=row[StyleKey.TEXT_STYLE], ha='center', va='center',
                                                   path_effects=[pe.withStroke(linewidth=row[StyleKey.TEXT_OUTLINE_WIDTH],
                                                                               alpha=row[StyleKey.EDGE_ALPHA], foreground=row[StyleKey.TEXT_OUTLINE_COLOR])])

        if (check_bbox_position or store_bbox):
            bbox = text_annotation.get_tightbbox()
            bbox_expanded = self.expand_bbox(bbox, self.TEXT_EXPAND_PERCENT)
        if (check_bbox_position):
            if (not self.__check_bbox_position(bbox_expanded, bbox, self.texts_and_markers_bboxs)):
                text_annotation.remove()
                return None
        if (store_bbox):
            self.texts_and_markers_bboxs.append(bbox_expanded)
        return text_annotation

    def __plot_marker(self, row, store_bbox: bool = True, check_bbox_position: bool = True) -> Line2D | None:
        marker: Line2D = self.ax.plot(row.geometry.x, row.geometry.y, marker=row[StyleKey.ICON], mfc=row[StyleKey.COLOR], ms=row[StyleKey.WIDTH],
                                      mec=row[StyleKey.EDGE_COLOR], mew=row[StyleKey.EDGEWIDTH])
        if (isinstance(marker, list)):
            marker = marker[0]
        if (check_bbox_position or store_bbox):
            bbox = marker.get_tightbbox()
            bbox_expanded = self.expand_bbox(bbox, self.TEXT_EXPAND_PERCENT)
        if (check_bbox_position):
            if (not self.__check_bbox_position(bbox_expanded, bbox, self.texts_and_markers_bboxs)):
                marker.remove()
                return None
        if (store_bbox):
            self.texts_and_markers_bboxs.append(bbox_expanded)
        return marker

    def __plot_marker_annotation(self, row, text: str, text_positions: list[TextPositions], check_bbox_position: bool = True) -> Annotation | None:
        x, y = row.geometry.x, row.geometry.y
        marker_size = row[StyleKey.WIDTH]
        ha = 'center'
        va = 'center'
        for position in text_positions:
            x_shift = 0
            y_shift = 0
            if (position == TextPositions.TOP):
                y_shift += marker_size * 0.8
                ha = 'center'
                va = 'bottom'
            elif (position == TextPositions.BOTTOM):
                y_shift -= marker_size
                ha = 'center'
                va = 'top'
            elif (position == TextPositions.LEFT):
                x_shift -= marker_size
                ha = 'right'
                va = 'center'
            elif (position == TextPositions.RIGHT):
                x_shift += marker_size
                ha = 'left'
                va = 'center'
            text_anotation: Annotation = self.ax.annotate(text, (x, y), textcoords="offset points", xytext=(x_shift, y_shift), ha=ha, va=va,
                                                          color=row[StyleKey.TEXT_COLOR], fontsize=row[
                                                              StyleKey.TEXT_FONT_SIZE], family=row[StyleKey.TEXT_FONTFAMILY],
                                                          weight=row[StyleKey.TEXT_WEIGHT], style=row[StyleKey.TEXT_STYLE],
                                                          path_effects=[pe.withStroke(linewidth=row[StyleKey.TEXT_OUTLINE_WIDTH],
                                                                                      alpha=row[StyleKey.EDGE_ALPHA], foreground=row[StyleKey.TEXT_OUTLINE_COLOR])])
            if (check_bbox_position):
                bbox = text_anotation.get_tightbbox()
                bbox_expanded = self.expand_bbox(
                    bbox, self.TEXT_EXPAND_PERCENT)
                if (not self.__check_bbox_position(bbox_expanded, bbox, self.texts_and_markers_bboxs)):
                    text_anotation.remove()
                    text_anotation = None
                    continue
            return text_anotation
        return None

    def __plot_marker_with_annotation(self, row, text_row=StyleKey.TEXT1, store_bbox: bool = True) -> tuple[Line2D, Text]:
        if(row[StyleKey.MIN_REQ_PLOT] in {MinParts.TEXT1_TEXT2, MinParts.MARKER_TEXT1_TEXT2}):
            return (None, None)
        marker = self.__plot_marker(row, False, True)
        # if node must have marker return None
        if (marker is None and row[StyleKey.MIN_REQ_PLOT] in {MinParts.MARKER, MinParts.MARKER_TEXT1, MinParts.MARKER_TEXT2}):
            return (None, None)

        text = self.__plot_marker_annotation(
            row, row[text_row], row[StyleKey.TEXT1_POSITIONS if text_row == StyleKey.TEXT1 else StyleKey.TEXT2_POSITIONS], True)
        # node text does not return None
        if (text is None and row[StyleKey.MIN_REQ_PLOT] in [MinParts.TEXT1, MinParts.TEXT2, MinParts.MARKER_TEXT1, MinParts.MARKER_TEXT2]):
            if (marker is not None):
                marker.remove()
            return (None, None)
        
        # node have ploted minimum parts
        if (store_bbox):
            if (marker is not None):
                self.texts_and_markers_bboxs.append(
                    self.expand_bbox(marker.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
            if (text is not None):
                self.texts_and_markers_bboxs.append(
                    self.expand_bbox(text.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
        return (marker, text)

    def __plot_marker_with_two_annotations(self, row, store_bbox: bool = True) -> tuple[Line2D, Text, Text]:
        marker = self.__plot_marker(row, False, True)
        # if node must have marker return None
        if (marker is None and row[StyleKey.MIN_REQ_PLOT] in [MinParts.MARKER, MinParts.MARKER_TEXT1, MinParts.MARKER_TEXT2, MinParts.MARKER_TEXT1_TEXT2]):
            return (None, None, None)
        text1 = self.__plot_marker_annotation(
            row, row[StyleKey.TEXT1], row[StyleKey.TEXT1_POSITIONS], True)
        if (text1 is None and row[StyleKey.MIN_REQ_PLOT] in [MinParts.TEXT1, MinParts.MARKER_TEXT1, MinParts.MARKER_TEXT1_TEXT2, MinParts.TEXT1_TEXT2]):
            if (marker is not None):
                marker.remove()
            return (None, None, None)

        text2 = self.__plot_marker_annotation(
            row, row[StyleKey.TEXT2], row[StyleKey.TEXT2_POSITIONS], True)
        if (text2 is None and row[StyleKey.MIN_REQ_PLOT] in [MinParts.TEXT2, MinParts.TEXT1_TEXT2, MinParts.MARKER_TEXT2, MinParts.MARKER_TEXT1_TEXT2]):
            if (marker is not None):
                marker.remove()
            if (text1 is not None):
                text1.remove()
            return (None, None, None)
        if (row[StyleKey.TEXT2] == ""):
            print("asdasd")
        # node have ploted minimum parts
        # todo maybe merge
        if (store_bbox):
            if (marker is not None):
                self.texts_and_markers_bboxs.append(
                    self.expand_bbox(marker.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
            if (text1 is not None):
                self.texts_and_markers_bboxs.append(
                    self.expand_bbox(text1.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
            if (text2 is not None):
                self.texts_and_markers_bboxs.append(
                    self.expand_bbox(text2.get_tightbbox(), self.TEXT_EXPAND_PERCENT))

    def __plot_with_shift(self, place_names_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        if (place_names_gdf.empty):
            return
        place_names = []

        for row in place_names_gdf.iterrows():
            place_names.append(self.__plot_text_on_point(
                row[1], row[1][StyleKey.TEXT1], True, True))
            # adjust_text(place_names, force_text=0.02)
            pass
        pass

    def __plot_text_on_points(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):

        # todo filter
        for row in gdf.iterrows():
            if (pd.isna(row[1][StyleKey.TEXT1])):
                self.__plot_text_on_point(
                    row[1], row[1][StyleKey.TEXT2], store_bbox, True)
            else:
                self.__plot_text_on_point(
                    row[1], row[1][StyleKey.TEXT1], store_bbox, True)

    def __plot_markers(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        # todo filter
        for row in gdf.iterrows():
            self.__plot_marker(row[1], store_bbox, True)

    def __plot_markers_with_annotation(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        # todo filter
        for row in gdf.iterrows():
            if(pd.isna(row[1][StyleKey.TEXT1])):
                self.__plot_marker_with_annotation(row[1], StyleKey.TEXT2, store_bbox)
            else:
                self.__plot_marker_with_annotation(row[1],StyleKey.TEXT1, store_bbox)

    def __plot_markers_with_two_annotations(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        # todo filter
        for row in gdf.iterrows():
            self.__plot_marker_with_two_annotations(row[1], store_bbox)

    def __plot_nodes_normal(self, nodes_gdf):
        groups = GdfUtils.get_groups_by_columns(
            nodes_gdf, [StyleKey.ZINDEX], [], False)
        for zindex, nodes_group_gdf in sorted(groups, key=lambda x: x[0], reverse=True):
            markers_with_two_annotations, group_rest = GdfUtils.filter_rows(
                nodes_group_gdf, {StyleKey.ICON: '', StyleKey.TEXT1: '', StyleKey.TEXT2: ''}, compl=True)
            markers_with_one_annotation, group_rest = GdfUtils.filter_rows(
                group_rest, [{StyleKey.ICON: '', StyleKey.TEXT1: ''}, {StyleKey.ICON: '', StyleKey.TEXT2: ''}], compl=True)
            markers, group_rest = GdfUtils.filter_rows(
                group_rest, {StyleKey.ICON: ''}, compl=True)
            texts = GdfUtils.filter_rows(
                group_rest, [{StyleKey.TEXT1: ''}, {StyleKey.TEXT2: ''}])
            self.__plot_text_on_points(texts)
            self.__plot_markers_with_annotation(markers_with_one_annotation)
            self.__plot_markers_with_two_annotations(
                markers_with_two_annotations)
            self.__plot_markers(markers)

    @time_measurement("nodePlot")
    def plot_nodes(self, nodes_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        if (nodes_gdf.empty):
            return
        # todo prefilter nodes by min parts
        # nodes_gdf = GdfUtils.sort_gdf_by_column(nodes_gdf, StyleKey.ZINDEX, ascending=False)
        # place_names_gdf, rest_gdf = GdfUtils.filter_rows(
            # nodes_gdf, {'place': ''}, compl=True)
        self.__plot_nodes_normal(nodes_gdf)
        # self.__plot_with_shift(place_names_gdf, wrap_len)
        # rest_gdf = GdfUtils.filter_rows(nodes_gdf, {'natural': 'peak'})
        # self.__plot_elevations(rest_gdf)

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
            self.__plot_ways_normal(gdf, True, False)

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
        pass
        # text force
        # remove overflown texts after adjusting
        # if (text_bounds_overflow_threshold > 0):
        #     r: RendererAgg = self.fig.canvas.get_renderer()
        #     for text in self.ax.texts:
        #         text_Bbox = text.get_tightbbox(renderer=r).transformed(
        #             self.ax.transData.inverted())
        #         bbox_polygon = geometry.box(
        #             text_Bbox.x0, text_Bbox.y0, text_Bbox.x1, text_Bbox.y1)
        #         if (not GdfUtils.is_geometry_inside_geometry_threshold(bbox_polygon, self.reqired_area_polygon, text_bounds_overflow_threshold)):
        #             text.remove()

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
