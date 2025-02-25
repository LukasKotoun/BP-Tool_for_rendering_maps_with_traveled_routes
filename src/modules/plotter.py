from typing import Generator
import warnings

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

from matplotlib.text import Text, Annotation
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
import shapely
# from adjustText import adjust_text
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
    TEXT_EXPAND_PERCENT = 4

    def __init__(self, requred_area_gdf: gpd.GeoDataFrame, paper_dimensions_mm: DimensionsTuple, map_object_scaling_factor: float,
                 text_bounds_overflow_threshold: float, text_wrap_len: int, outer_reqired_area_gdf: gpd.GeoDataFrame | None = None):
        self.reqired_area_gdf: gpd.GeoDataFrame = requred_area_gdf
        self.reqired_area_polygon: Polygon = GdfUtils.create_polygon_from_gdf(
            self.reqired_area_gdf)

        self.outer_reqired_area_gdf = outer_reqired_area_gdf
        self.paper_dimensions_mm = paper_dimensions_mm
        self.map_object_scaling_factor: float = map_object_scaling_factor
        self.texts_and_markers_bboxs = []
        self.text_bounds_overflow_threshold = text_bounds_overflow_threshold
        self.text_wrap_len = text_wrap_len

    def init(self, map_bg_color: str, bg_gdf: gpd.GeoDataFrame, area_zoom_preview: None | DimensionsTuple = None,
             zoom_percent_padding=0):
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
        self.zoom(zoom_percent_padding)

        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color)
        if (not bg_gdf.empty):
            bg_gdf.plot(ax=self.ax, color=bg_gdf[Style.COLOR.name])
        polygon_text_inside = GdfUtils.create_polygon_from_gdf(
            self.reqired_area_gdf) if self.outer_reqired_area_gdf is None else GdfUtils.create_polygon_from_gdf(self.outer_reqired_area_gdf)

        self.polygon_text_inside_display = GdfUtils.transform_geometry_to_display(
            self.ax, polygon_text_inside)

    def __text_on_point(self, row, text: str, text_wrap_len=0, store_bbox: bool = True, check_bbox_position: bool = True, zorder=3) -> Text | None:
        text = Utils.wrap_text(text, text_wrap_len)
        text_plot: Text = self.ax.text(row['geometry'].x, row['geometry'].y, text, color=row[Style.TEXT_COLOR.name], fontsize=row[Style.TEXT_FONT_SIZE.name], family=row[Style.TEXT_FONTFAMILY.name],
                                       weight=row[Style.TEXT_WEIGHT.name], style=row[Style.TEXT_STYLE.name], ha='center', va='center', alpha=row[Style.ALPHA.name],
                                       path_effects=[pe.withStroke(linewidth=row[Style.TEXT_OUTLINE_WIDTH.name],
                                                                   alpha=row[Style.EDGE_ALPHA.name], foreground=row[Style.TEXT_OUTLINE_COLOR.name])], zorder=zorder)
        bbox = text_plot.get_tightbbox()
        if (bbox is None):
            # text is plotted outside of the figure
            text_plot.remove()
            return None

        if (check_bbox_position or store_bbox):
            bbox_expanded = Utils.expand_bbox(bbox, self.TEXT_EXPAND_PERCENT)
        if (check_bbox_position):
            if (not Utils.check_bbox_position(bbox_expanded, bbox, self.texts_and_markers_bboxs, self.ax,
                                              self.text_bounds_overflow_threshold, self.polygon_text_inside_display)):
                text_plot.remove()
                return None
        if (store_bbox):
            self.texts_and_markers_bboxs.append(bbox_expanded)
        return text_plot

    def __marker(self, row, store_bbox: bool = True, check_bbox_position: bool = True, zorder=2) -> Line2D | None:
        font_properties = row.get(Style.MARKER_FONT_PROPERTIES.name, None)
        if (pd.notna(font_properties)):
            # va = row.get(Style.MARKER_VERTICAL_ALIGN.name, "center")
            # ha = row.get(Style.MARKER_HORIZONTAL_ALIGN.name, "center")
            marker: Text = self.ax.text(row['geometry'].x, row['geometry'].y, row[Style.MARKER.name], color=row[Style.COLOR.name], fontsize=row[Style.WIDTH.name],
                                  font_properties=font_properties, alpha=row[Style.ALPHA.name],
                                  path_effects=[pe.withStroke(linewidth=row[Style.EDGEWIDTH.name],
                                                              alpha=row[Style.ALPHA.name], foreground=row[Style.EDGE_COLOR.name])],
                                  zorder=zorder)
        else:
            marker: Line2D = self.ax.plot(row['geometry'].x, row['geometry'].y, marker=row[Style.MARKER.name], mfc=row[Style.COLOR.name], ms=row[Style.WIDTH.name],
                                          mec=row[Style.EDGE_COLOR.name], mew=row[Style.EDGEWIDTH.name], alpha=row[Style.ALPHA.name],
                                          zorder=zorder)
        if (isinstance(marker, list)):
            marker = marker[0]
        bbox = marker.get_tightbbox()
        if (bbox is None):
            # marker is plotted outside of the figure
            marker.remove()
            return None

        if (check_bbox_position or store_bbox):
            bbox_expanded = Utils.expand_bbox(bbox, self.TEXT_EXPAND_PERCENT)
        if (check_bbox_position):
            if (not Utils.check_bbox_position(bbox_expanded, bbox, self.texts_and_markers_bboxs, self.ax,
                                              self.text_bounds_overflow_threshold, self.polygon_text_inside_display)):
                marker.remove()
                return None
        if (store_bbox):
            self.texts_and_markers_bboxs.append(bbox_expanded)
        return marker

    def __marker_annotation(self, row, text: str, text_positions: list[TextPositions], text_wrap_len: int = 0, check_bbox_position: bool = True, zorder=3) -> Annotation | None:
        text = Utils.wrap_text(text, text_wrap_len)
        x, y = row['geometry'].x, row['geometry'].y
        marker_size = row[Style.WIDTH.name]
        ha = 'center'
        va = 'center'

        if (not isinstance(text_positions, list)):
            warnings.warn("Text positions must be list")
            return None
        for position in text_positions:
            x_shift = 0
            y_shift = 0
            if (position == TextPositions.TOP.name):
                y_shift += marker_size * 0.8
                ha = 'center'
                va = 'bottom'
            elif (position == TextPositions.BOTTOM.name):
                y_shift -= marker_size
                ha = 'center'
                va = 'top'
            elif (position == TextPositions.LEFT.name):
                x_shift -= marker_size
                ha = 'right'
                va = 'center'
            elif (position == TextPositions.RIGHT.name):
                x_shift += marker_size
                ha = 'left'
                va = 'center'
                # todo add other positions like top-left, top-right, bottom-left, bottom-right
            else:
                warnings.warn(f"Unknown text position {position}")
                continue
            text_anotation: Annotation = self.ax.annotate(text, (x, y), textcoords="offset points", xytext=(x_shift, y_shift), ha=ha, va=va,
                                                          color=row[Style.TEXT_COLOR.name], fontsize=row[Style.TEXT_FONT_SIZE.name],
                                                          family=row[Style.TEXT_FONTFAMILY.name], alpha=row[Style.ALPHA.name],
                                                          weight=row[Style.TEXT_WEIGHT.name], style=row[Style.TEXT_STYLE.name],
                                                          path_effects=[pe.withStroke(linewidth=row[Style.TEXT_OUTLINE_WIDTH.name],
                                                                                      alpha=row[Style.EDGE_ALPHA.name], foreground=row[Style.TEXT_OUTLINE_COLOR.name])], zorder=zorder)
            bbox = text_anotation.get_tightbbox()
            if (bbox is None):
                # text is plotted outside of the figure
                text_anotation.remove()
                text_anotation = None
                continue

            if (check_bbox_position):
                bbox_expanded = Utils.expand_bbox(
                    bbox, self.TEXT_EXPAND_PERCENT)
                if (not Utils.check_bbox_position(bbox_expanded, bbox, self.texts_and_markers_bboxs, self.ax,
                                                  self.text_bounds_overflow_threshold, self.polygon_text_inside_display)):
                    text_anotation.remove()
                    text_anotation = None
                    continue
            return text_anotation
        return None

    def __marker_with_one_annotation(self, row, text_row=Style.TEXT1.name, store_bbox: bool = True, zorder=3) -> tuple[Line2D, Text]:
        if (row[Style.MIN_REQ_POINT.name] in {MinParts.TEXT1_TEXT2.name, MinParts.MARKER_TEXT1_TEXT2.name}):
            return (None, None)
        marker = self.__marker(row, store_bbox=False, check_bbox_position=row.get(
            Style.MARKER_CHECK_OVERLAP.name, True), zorder=zorder)
        # if node must have marker return None
        if (marker is None and row[Style.MIN_REQ_POINT.name] in {MinParts.MARKER.name, MinParts.MARKER_TEXT1.name, MinParts.MARKER_TEXT2.name}):
            return (None, None)

        text_wrap_len = row.get(Style.TEXT_WRAP_LEN.name, self.text_wrap_len)
        
        text_positions = row[Style.TEXT1_POSITIONS.name if text_row ==
                             Style.TEXT1.name else Style.TEXT2_POSITIONS.name]
        text_annotation = self.__marker_annotation(
            row, row[text_row], text_positions, text_wrap_len, True, zorder)
        # node text does not return None
        if (text_annotation is None and row[Style.MIN_REQ_POINT.name] in [MinParts.TEXT1.name, MinParts.TEXT2.name, MinParts.MARKER_TEXT1.name, MinParts.MARKER_TEXT2.name]):
            if (marker is not None):
                marker.remove()
            return (None, None)

        # node have ploted minimum parts
        if (store_bbox):
            if (marker is not None):
                self.texts_and_markers_bboxs.append(
                    Utils.expand_bbox(marker.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
            if (text_annotation is not None):
                self.texts_and_markers_bboxs.append(
                    Utils.expand_bbox(text_annotation.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
        return (marker, text_annotation)

    def __marker_with_two_annotations(self, row, store_bbox: bool = True, zorder=3) -> tuple[Line2D, Text, Text]:
        marker = self.__marker(row, store_bbox=False, check_bbox_position=row.get(
            Style.MARKER_CHECK_OVERLAP.name, True), zorder=zorder)
        # if node must have marker return None
        if (marker is None and row[Style.MIN_REQ_POINT.name] in [MinParts.MARKER.name, MinParts.MARKER_TEXT1.name, MinParts.MARKER_TEXT2.name, MinParts.MARKER_TEXT1_TEXT2.name]):
            return (None, None, None)

        text_wrap_len = row.get(Style.TEXT_WRAP_LEN.name, self.text_wrap_len)
        text1 = self.__marker_annotation(
            row, row[Style.TEXT1.name], row[Style.TEXT1_POSITIONS.name], text_wrap_len, True, zorder)
        if (text1 is None and row[Style.MIN_REQ_POINT.name] in [MinParts.TEXT1.name, MinParts.MARKER_TEXT1.name, MinParts.MARKER_TEXT1_TEXT2.name, MinParts.TEXT1_TEXT2.name]):
            if (marker is not None):
                marker.remove()
            return (None, None, None)

        text2 = self.__marker_annotation(
            row, row[Style.TEXT2.name], row[Style.TEXT2_POSITIONS.name], text_wrap_len, True, zorder)
        if (text2 is None and row[Style.MIN_REQ_POINT.name] in [MinParts.TEXT2.name, MinParts.TEXT1_TEXT2.name, MinParts.MARKER_TEXT2.name, MinParts.MARKER_TEXT1_TEXT2.name]):
            if (marker is not None):
                marker.remove()
            if (text1 is not None):
                text1.remove()
            return (None, None, None)

        # node have ploted minimum parts
        if (store_bbox):
            if (marker is not None):
                self.texts_and_markers_bboxs.append(
                    Utils.expand_bbox(marker.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
            if (text1 is not None):
                self.texts_and_markers_bboxs.append(
                    Utils.expand_bbox(text1.get_tightbbox(), self.TEXT_EXPAND_PERCENT))
            if (text2 is not None):
                self.texts_and_markers_bboxs.append(
                    Utils.expand_bbox(text2.get_tightbbox(), self.TEXT_EXPAND_PERCENT))

    def __text_gdf_on_points(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        gdf = GdfUtils.filter_invalid_texts(gdf)
        texts1 = GdfUtils.filter_rows(
            gdf, [{Style.TEXT1.name: ''}])
        texts2 = GdfUtils.filter_rows(
            gdf, [{Style.TEXT2.name: ''}])

        for row in texts1.iterrows():
            self.__text_on_point(
                row[1], row[1][Style.TEXT1.name], row[1].get(Style.TEXT_WRAP_LEN.name, self.text_wrap_len), store_bbox, True)

        for row in texts2.iterrows():
            self.__text_on_point(
                row[1], row[1][Style.TEXT2.name], row[1].get(Style.TEXT_WRAP_LEN.name, self.text_wrap_len), store_bbox, True)

    def __markers_gdf(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        gdf = GdfUtils.filter_invalid_markers(gdf)
        for row in gdf.iterrows():
            self.__marker(row[1], store_bbox=store_bbox,
                          check_bbox_position=row[1].get(Style.MARKER_CHECK_OVERLAP.name, True))

    def __markers_gdf_with_one_annotation(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        gdf = GdfUtils.filter_invalid_markers(gdf)
        gdf = GdfUtils.filter_invalid_texts(gdf)
        texts1 = GdfUtils.filter_rows(
            gdf, [{Style.TEXT1.name: '', Style.TEXT1_POSITIONS.name: ''}])
        texts2 = GdfUtils.filter_rows(
            gdf, [{Style.TEXT2.name: '', Style.TEXT2_POSITIONS.name: ''}])

        for row in texts1.iterrows():
            self.__marker_with_one_annotation(
                row[1], Style.TEXT1.name, store_bbox)
        for row in texts2.iterrows():
            self.__marker_with_one_annotation(
                row[1], Style.TEXT2.name, store_bbox)

    def __markers_gdf_with_two_annotations(self, gdf: gpd.GeoDataFrame, store_bbox: bool = True):
        gdf = GdfUtils.filter_invalid_markers(gdf)
        gdf = GdfUtils.filter_invalid_texts(gdf)
        texts1 = GdfUtils.filter_rows(
            gdf, [{Style.TEXT1.name: '', Style.TEXT1_POSITIONS.name: '', Style.TEXT2.name: '', Style.TEXT2_POSITIONS.name: ''}])
        for row in gdf.iterrows():
            self.__marker_with_two_annotations(row[1], store_bbox)

    @time_measurement("nodePlot")
    def nodes(self, nodes_gdf: gpd.GeoDataFrame, wrap_len: int | None):
        if (nodes_gdf.empty):
            return
        groups = GdfUtils.get_groups_by_columns(
            nodes_gdf, [Style.ZINDEX.name], [], False)
        for zindex, nodes_group_gdf in sorted(groups, key=lambda x: x[0], reverse=True):
            markers_with_two_annotations, group_rest = GdfUtils.filter_rows(
                nodes_group_gdf, {Style.MARKER.name: '', Style.TEXT1.name: '', Style.TEXT2.name: ''}, compl=True)

            markers_with_one_annotation, group_rest = GdfUtils.filter_rows(
                group_rest, [{Style.MARKER.name: '', Style.TEXT1.name: ''}, {Style.MARKER.name: '', Style.TEXT2.name: ''}], compl=True)

            markers, group_rest = GdfUtils.filter_rows(
                group_rest, {Style.MARKER.name: ''}, compl=True)

            texts = GdfUtils.filter_rows(
                group_rest, [{Style.TEXT1.name: ''}, {Style.TEXT2.name: ''}])

            self.__text_gdf_on_points(texts)
            self.__markers_gdf_with_one_annotation(
                markers_with_one_annotation)
            self.__markers_gdf_with_two_annotations(
                markers_with_two_annotations)
            self.__markers_gdf(markers)

    def __line_edges(self, lines_gdf, cupstyle: str = None, zorder=2):
        edge_lines_gdf = GdfUtils.filter_rows(lines_gdf, {
            Style.EDGE_COLOR.name: '', Style.EDGE_LINESTYLE.name: '', Style.EDGEWIDTH.name: '', Style.EDGE_ALPHA.name: ''})

        if (edge_lines_gdf.empty):
            return
        if (cupstyle is not None):
            edge_lines_gdf[Style.EDGE_CUP.name] = cupstyle

        groups = GdfUtils.get_groups_by_columns(
            edge_lines_gdf, [Style.EDGE_CUP.name], [self.DEFAULT_CUPSTYLE], False)
        for capstyle, edge_lines_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CUPSTYLE

            edge_lines_group_gdf.plot(ax=self.ax, color=edge_lines_group_gdf[Style.EDGE_COLOR.name],
                                      linewidth=edge_lines_group_gdf[Style.EDGEWIDTH.name],
                                      linestyle=edge_lines_group_gdf[Style.EDGE_LINESTYLE.name],
                                      alpha=edge_lines_group_gdf[Style.EDGE_ALPHA.name],
                                      path_effects=[pe.Stroke(capstyle=capstyle)], zorder=zorder)

    def __line(self, lines_gdf, cupstyle: str = None, zorder=2):
        lines_gdf = GdfUtils.filter_rows(lines_gdf, {
            Style.COLOR.name: '', Style.LINESTYLE.name: '', Style.WIDTH.name: '', Style.ALPHA.name: ''})
        if (lines_gdf.empty):
            return
        if (cupstyle is not None):
            lines_gdf[Style.LINE_CUP.name] = cupstyle

        groups = GdfUtils.get_groups_by_columns(
            lines_gdf, [Style.LINE_CUP.name], [self.DEFAULT_CUPSTYLE], False)
        for capstyle, lines_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CUPSTYLE

            lines_group_gdf.plot(ax=self.ax, color=lines_group_gdf[Style.COLOR.name],
                                 linewidth=lines_group_gdf[Style.WIDTH.name],
                                 linestyle=lines_group_gdf[Style.LINESTYLE.name],
                                 alpha=lines_group_gdf[Style.ALPHA.name],
                                 path_effects=[pe.Stroke(capstyle=capstyle)], zorder=zorder)

    def __dashed_with_edge_dashed(self, gdf: gpd.GeoDataFrame, line_cupstyle: str = None, edge_cupstyle: str = None, zorder=2):
        if (gdf.empty):
            return
        gdf = GdfUtils.filter_rows(gdf, {Style.COLOR.name: '', Style.EDGE_COLOR.name: '',
                                         Style.LINESTYLE.name: '', Style.WIDTH.name: '', Style.EDGEWIDTH.name: '',
                                         Style.ALPHA.name: '', Style.EDGE_ALPHA.name: ''})
        if (gdf.empty):
            return
        if (line_cupstyle is not None):
            gdf[Style.LINE_CUP.name] = line_cupstyle
        if (edge_cupstyle is not None):
            gdf[Style.EDGE_CUP.name] = edge_cupstyle

        groups = GdfUtils.get_groups_by_columns(
            gdf, [Style.LINE_CUP.name, Style.EDGE_CUP.name, Style.EDGEWIDTH.name,
                  Style.EDGE_COLOR.name, Style.EDGE_ALPHA.name], [], False)

        for (line_cup, edge_cup, edge_width, edge_color, edge_alpha), gdf_group in groups:
            if (pd.isna(line_cup)):
                line_cup = self.DEFAULT_CUPSTYLE
            if (pd.isna(edge_cup)):
                edge_cup = self.DEFAULT_CUPSTYLE

            gdf_group.plot(ax=self.ax, color=gdf_group[Style.COLOR.name], linestyle=gdf_group[Style.LINESTYLE.name],
                           linewidth=gdf_group[Style.WIDTH.name], alpha=gdf_group[Style.ALPHA.name], path_effects=[
                pe.Stroke(
                    linewidth=edge_width, foreground=edge_color, alpha=edge_alpha,
                    capstyle=edge_cup), pe.Normal(), pe.Stroke(capstyle=line_cup)], zorder=zorder)

    def __dashed_with_edge_solid(self, gdf: gpd.GeoDataFrame, line_cupstyle: str = None, edge_cupstyle: str = None, zorder=2):
        if (gdf.empty):
            return
        gdf = GdfUtils.filter_rows(gdf, {Style.EDGE_COLOR.name: '', Style.COLOR.name: '',
                                         Style.EDGEWIDTH.name: '', Style.WIDTH.name: '',
                                         Style.ALPHA.name: '', Style.EDGE_ALPHA.name: '',
                                         Style.LINESTYLE.name: '', })
        if (gdf.empty):
            return
        if (line_cupstyle is not None):
            gdf[Style.LINE_CUP.name] = line_cupstyle
        if (edge_cupstyle is not None):
            gdf[Style.EDGE_CUP.name] = edge_cupstyle

        groups = GdfUtils.get_groups_by_columns(
            gdf, [Style.LINE_CUP.name, Style.EDGE_CUP.name], [], False)

        # todo make quciker

        for (line_cup, edge_cup), gdf_group in groups:
            if (pd.isna(line_cup)):
                line_cup = "projecting"
            if (pd.isna(edge_cup)):
                edge_cup = "projecting"
            color = gdf_group[Style.COLOR.name]
            edge_color = gdf_group[Style.EDGE_COLOR.name]
            linewidth = gdf_group[Style.WIDTH.name]
            edge_linewidth = gdf_group[Style.EDGEWIDTH.name]
            alpha = gdf_group[Style.ALPHA.name]
            edge_alpha = gdf_group[Style.EDGE_ALPHA.name]
            linestyle = gdf_group[Style.LINESTYLE.name]
            edge_linestyle = "-"

            for geom in gdf_group.geometry:
                if isinstance(geom, MultiLineString):
                    for line in geom.geoms:  # Extract each LineString
                        gpd.GeoSeries(line).plot(ax=self.ax, color=edge_color,
                                                 linewidth=edge_linewidth,
                                                 alpha=edge_alpha, path_effects=[
                                                     pe.Stroke(capstyle=edge_cup)], zorder=zorder)

                        gpd.GeoSeries(line).plot(ax=self.ax, color=color, linewidth=linewidth,
                                                 alpha=alpha, linestyle=linestyle, path_effects=[
                                                     pe.Stroke(capstyle=line_cup)], zorder=zorder)
                else:
                    gpd.GeoSeries(geom).plot(ax=self.ax, color=edge_color,
                                             linewidth=edge_linewidth,
                                             alpha=edge_alpha, path_effects=[
                                                 pe.Stroke(capstyle=edge_cup)], zorder=zorder)

                    gpd.GeoSeries(geom).plot(ax=self.ax, color=color, linewidth=linewidth,
                                             alpha=alpha, linestyle=linestyle, path_effects=[
                                                 pe.Stroke(capstyle=line_cup)], zorder=zorder)

    def __ways_normal(self, gdf: gpd.GeoDataFrame, plotEdges: bool = False, cross_roads_by_zindex=False, line_cupstyle: str = None, edge_cupstyle: str = None, zorder=2):
        """Plot ways based on z-index and capstyles. 

        Args:
            gdf (gpd.GeoDataFrame): _description_
            plotEdges (bool, optional): _description_. Defaults to False.
        """
        if (gdf.empty):
            return

        if (plotEdges and not cross_roads_by_zindex):
            # plot edge where line is solid or only edge is ploted
            self.__line_edges(GdfUtils.filter_rows(
                gdf, [{Style.LINESTYLE.name: ['-', 'solid']}, {Style.COLOR.name: '~'}]), edge_cupstyle, zorder)

        groups = GdfUtils.get_groups_by_columns(
            gdf, [Style.ZINDEX.name], [], False)
        for zindex, ways_group_gdf in groups:
            # crossroads only on ways with same zindex
            if (plotEdges and cross_roads_by_zindex):
                self.__line_edges(GdfUtils.filter_rows(
                    gdf, [{Style.LINESTYLE.name: ['-', 'solid']}, {Style.COLOR.name: '~'}]), edge_cupstyle, zorder)
            # lines - line is solid or edge does not exists, dashed_with_edge_lines - line is dashed and edge exists
            rest_lines, dashed_with_edge_lines = GdfUtils.filter_rows(
                ways_group_gdf, [{Style.LINESTYLE.name: ['-', 'solid']}, {Style.EDGE_COLOR.name: '~'}], compl=True)
            # there will be filter for ways with specific edge style (edgeEffect)
            ways_dashed_edge_solid, ways_dashed_edge_dashed = GdfUtils.filter_rows(
                dashed_with_edge_lines, {Style.EDGE_LINESTYLE.name: ['-', 'solid']}, compl=True)

            self.__dashed_with_edge_dashed(
                ways_dashed_edge_dashed, line_cupstyle, edge_cupstyle, zorder)
            self.__dashed_with_edge_solid(
                ways_dashed_edge_solid, line_cupstyle, edge_cupstyle, zorder)
            self.__line(rest_lines, line_cupstyle, zorder)

    def __bridges(self, bridges_gdf: gpd.GeoDataFrame, zorder=2):
        if (bridges_gdf.empty):
            return
        # can be merged edges and center -- using pe

        def bridges_edges(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {Style.BRIDGE_EDGE_COLOR.name: '', Style.BRIDGE_EDGE_WIDTH.name: '',
                      Style.EDGE_LINESTYLE.name: '', Style.EDGE_ALPHA.name: ''})

            if (gdf.empty):
                return

            gdf.plot(ax=self.ax, color=gdf[Style.BRIDGE_EDGE_COLOR.name],
                     linewidth=gdf[Style.BRIDGE_EDGE_WIDTH.name],
                     linestyle=gdf[Style.EDGE_LINESTYLE.name],
                     alpha=gdf[Style.EDGE_ALPHA.name],
                     path_effects=[pe.Stroke(capstyle="butt")], zorder=zorder)

        def bridges_center(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {Style.BRIDGE_WIDTH.name: '', Style.BRIDGE_COLOR.name: '',
                      Style.LINESTYLE.name: '', Style.ALPHA.name: ''})
            if (gdf.empty):
                return

            gdf.plot(ax=self.ax, color=gdf[Style.BRIDGE_COLOR.name],
                     linewidth=gdf[Style.BRIDGE_WIDTH.name],
                     linestyle=gdf[Style.LINESTYLE.name],
                     alpha=gdf[Style.ALPHA.name],
                     path_effects=[pe.Stroke(capstyle="butt")], zorder=zorder)

        def ways_on_bridges(gdf: gpd.GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {Style.PLOT_ON_BRIDGE.name: ""})
            if (gdf.empty):
                return
            self.__ways_normal(gdf, True, False, zorder=zorder)

        groups = GdfUtils.get_groups_by_columns(
            bridges_gdf, ['layer'], [], False)
        for layer, bridge_layer_gdf in groups:
            bridges_edges(bridge_layer_gdf.copy())
            bridges_center(bridge_layer_gdf.copy())
            ways_on_bridges(bridge_layer_gdf.copy())

    def __tunnels(self, tunnels_gdf, zorder=2):
        if (tunnels_gdf.empty):
            return
        for layer, tunnel_layer_gdf in tunnels_gdf.groupby("layer"):
            self.__ways_normal(tunnel_layer_gdf, True, False, zorder=zorder)

    @time_measurement("wayplot")
    def ways(self, ways_gdf: gpd.GeoDataFrame, areas_ways_gdf: gpd.GeoDataFrame, over_filter=None):
        if (ways_gdf.empty):
            return

        # water ways and tunnels
        waterways_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'waterway': ''}, compl=True)
        waterways_tunnel_gdf, waterways_gdf = GdfUtils.filter_rows(
            waterways_gdf, {'tunnel': ''}, compl=True)

        self.__tunnels(waterways_tunnel_gdf)
        self.__ways_normal(waterways_gdf, True, False)

        # normal tunnels
        ways_tunnel_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'tunnel': ''}, compl=True)

        self.__tunnels(ways_tunnel_gdf)

        # normal ways
        ways_bridge_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'bridge': ''}, compl=True)

        self.__ways_normal(ways_gdf, True, False)

        # bridges
        self.__bridges(ways_bridge_gdf)

        # ways to prevent crossroads
        if (over_filter is not None):
            self.__ways_normal(GdfUtils.filter_rows(
                ways_gdf, over_filter), True, True, 'butt', 'butt')

    @time_measurement("areaPlot")
    def areas(self, areas_gdf: gpd.GeoDataFrame):
        if (areas_gdf.empty):
            return
        # plot face
        face_areas_gdf = GdfUtils.filter_rows(
            areas_gdf, {Style.COLOR.name: ''})
        if (not face_areas_gdf.empty):
            face_areas_gdf.plot(
                ax=self.ax, color=face_areas_gdf[Style.COLOR.name], alpha=face_areas_gdf[Style.ALPHA.name])
        # plot bounds
        edge_areas_gdf = GdfUtils.filter_rows(areas_gdf,
                                              {Style.EDGE_COLOR.name: '', Style.WIDTH.name: '', Style.EDGE_LINESTYLE.name: ''})
        if (edge_areas_gdf.empty):
            return
        groups = GdfUtils.get_groups_by_columns(
            edge_areas_gdf, [Style.EDGE_CUP.name], [self.DEFAULT_CUPSTYLE], False)
        for capstyle, edge_areas_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CUPSTYLE
            edge_areas_group_gdf.plot(
                ax=self.ax, facecolor='none', edgecolor=edge_areas_group_gdf[Style.EDGE_COLOR.name],
                linewidth=edge_areas_group_gdf[Style.WIDTH.name], alpha=edge_areas_group_gdf[Style.EDGE_ALPHA.name],
                linestyle=edge_areas_group_gdf[Style.EDGE_LINESTYLE.name],
                path_effects=[pe.Stroke(capstyle=capstyle)])

    @time_measurement("gpxsPlot")
    def gpxs(self, gpxs_gdf: gpd.GeoDataFrame):
        if (gpxs_gdf.empty):
            return
        self.__ways_normal(gpxs_gdf, True, False, zorder=5)

        def get_first_point(geometry):
            if isinstance(geometry, LineString):
                # Directly access first and last points for LineString
                first_point = shapely.Point(geometry.coords[0])
            elif isinstance(geometry, MultiLineString):
                # For MultiLineString, get first and last points from each LineString
                # First point of the first LineString
                first_point = shapely.Point(geometry.geoms[0].coords[0])
            else:
                raise ValueError("Unsupported geometry type")

            return first_point

        def get_last_point(geometry):
            if isinstance(geometry, LineString):
                # Directly access first and last points for LineString
                first_point = shapely.Point(geometry.coords[-1])
            elif isinstance(geometry, MultiLineString):
                # For MultiLineString, get first and last points from each LineString
                # First point of the first LineString
                first_point = shapely.Point(geometry.geoms[-1].coords[-1])
            else:
                raise ValueError("Unsupported geometry type")

            return first_point

        gpx_start_MARKERs = GdfUtils.filter_rows(gpxs_gdf, {Style.START_MARKER.name: '', Style.START_MARKER_WIDHT.name: '',
                                                          Style.START_MARKER_COLOR.name: '', Style.START_MARKER_EDGE_COLOR.name: '',
                                                          Style.START_MARKER_EDGEWIDTH.name: '', Style.START_MARKER_ALPHA.name: ''})
        gpx_finish_MARKERs = GdfUtils.filter_rows(gpxs_gdf, {Style.FINISH_MARKER.name: '', Style.FINISH_MARKER_WIDHT.name: '',
                                                           Style.FINISH_MARKER_COLOR.name: '', Style.FINISH_MARKER_EDGE_COLOR.name: '',
                                                           Style.FINISH_MARKER_EDGEWIDTH.name: '', Style.FINISH_MARKER_ALPHA.name: ''})

        # todo in tuple only remove previfx from all keys
        for row in gpx_finish_MARKERs.itertuples():
            print(row)
        for row in gpx_finish_MARKERs.iterrows():
            style_rename_mapping = {
                Style.FINISH_MARKER.name: Style.MARKER.name,
                Style.FINISH_MARKER_COLOR.name: Style.COLOR.name,
                Style.FINISH_MARKER_EDGE_COLOR.name: Style.EDGE_COLOR.name,
                Style.FINISH_MARKER_WIDHT.name: Style.WIDTH.name,
                Style.FINISH_MARKER_EDGEWIDTH.name: Style.EDGEWIDTH.name,
                Style.FINISH_MARKER_ALPHA.name: Style.ALPHA.name,
                Style.FINISH_MARKER_FONT_PROPERTIES.name: Style.MARKER_FONT_PROPERTIES.name,
                "geometry": "geometry"
            }
            # Filter and rename the style keys
            style_data = {new_key: row[1][old_key]
                          for old_key, new_key in style_rename_mapping.items()}
            style_data['geometry'] = get_last_point(row[1].geometry)
            # Convert it to a tuple (can include the index or any other data if needed)
            self.__marker(style_data, True, True, 10)

        for row in gpx_start_MARKERs.iterrows():
            style_rename_mapping = {
                Style.START_MARKER.name: Style.MARKER.name,
                Style.START_MARKER_COLOR.name: Style.COLOR.name,
                Style.START_MARKER_EDGE_COLOR.name: Style.EDGE_COLOR.name,
                Style.START_MARKER_WIDHT.name: Style.WIDTH.name,
                Style.START_MARKER_EDGEWIDTH.name: Style.EDGEWIDTH.name,
                Style.START_MARKER_ALPHA.name: Style.ALPHA.name,
                Style.START_MARKER_FONT_PROPERTIES.name: Style.MARKER_FONT_PROPERTIES.name,
                "geometry": "geometry"
            }
        
            # Filter and rename the style keys
            style_data = {new_key: row[1].get(old_key, None)
                          for old_key, new_key in style_rename_mapping.items()}
            style_data['geometry'] = get_first_point(row[1].geometry)
            # Convert it to a tuple (can include the index or any other data if needed)
            self.__marker(style_data,  True, True, 10)

        # for marker ploting remap MARKERs to row with different tags and use marker plot function

        # gpxs_edge_gdf = GdfUtils.filter_rows(
        #     gpxs_gdf, {Style.EDGE_COLOR.name: '', Style.EDGE_LINESTYLE.name: '', Style.WIDTH.name: ''})
        # self.__line_edges(gpxs_gdf)
        # if (not gpxs_edge_gdf.empty):
        #     gpxs_edge_gdf.plot(ax=self.ax, color=gpxs_gdf[Style.EDGE_COLOR.name], linewidth=gpxs_gdf[Style.WIDTH.name],
        #                        linestyle=gpxs_gdf[Style.EDGE_LINESTYLE.name], alpha=gpxs_gdf[Style.ALPHA.name],
        #                        path_effects=[pe.Stroke(capstyle="round")])

        # gpxs_gdf[Style.WIDTH.name] = gpxs_gdf[Style.WIDTH.name] * \
        #     self.map_object_scaling_factor * line_width_multiplier
        # gpxs_gdf.plot(ax=self.ax, color=gpxs_gdf[Style.COLOR.name], linewidth=gpxs_gdf[Style.WIDTH.name],
        #               linestyle=gpxs_gdf[Style.LINESTYLE.name], alpha=gpxs_gdf[Style.ALPHA.name],
        #               path_effects=[pe.Stroke(capstyle="round")])

    def clip(self, crs: str, zoom_percentage_padding=0, clipped_area_color: str = 'white'):
        whole_area_bounds = Utils.adjust_bounds_to_fill_paper(
            GdfUtils.get_bounds_gdf(self.reqired_area_gdf), self.paper_dimensions_mm)
        whole_area_bounds = Utils.expand_bounds_dict(
            whole_area_bounds, 2 + zoom_percentage_padding)
        whole_area_polygon = GdfUtils.create_polygon_from_bounds(
            whole_area_bounds)

        clipping_polygon = whole_area_polygon.difference(
            self.reqired_area_polygon)
        if (not GdfUtils.is_geometry_inside_geometry(clipping_polygon, whole_area_polygon)):
            return
        clipping_polygon = gpd.GeoDataFrame(
            geometry=[clipping_polygon], crs=crs)
        clipping_polygon.plot(
            ax=self.ax, color=clipped_area_color, alpha=1, zorder=5)
        # by this z order clip (5) or non clip overflowed text (3)

    def area_boundary(self, boundary_map_area_gdf: gpd.GeoDataFrame, color: str = 'black', linewidth: float = 1):

        boundary_map_area_gdf_with, boundary_map_area_gdf_without = GdfUtils.filter_rows(
            boundary_map_area_gdf, {Style.WIDTH.name: '', Style.COLOR.name: ''}, compl=True)
        if (not boundary_map_area_gdf_with.empty):
            boundary_map_area_gdf_with.boundary.plot(
                ax=self.ax, color=boundary_map_area_gdf_with[Style.COLOR.name], linewidth=boundary_map_area_gdf[Style.WIDTH.name], zorder=5)
        if (not boundary_map_area_gdf_without.empty):
            boundary_map_area_gdf_without.boundary.plot(
                ax=self.ax, color=color, linewidth=linewidth, zorder=5)
        # by this z order clip (5) or non clip overflowed text (4)

    def zoom(self, zoom_percent_padding: float = 0):
        zoom_padding = zoom_percent_padding / 100  # convert from percent
        # set x and y limits by area that fit paper size for text overflow checking and area clipping
        zoom_bounds = Utils.adjust_bounds_to_fill_paper(
            GdfUtils.get_bounds_gdf(self.reqired_area_gdf), self.paper_dimensions_mm)
        # zoom_bounds = GdfUtils.get_bounds_gdf(self.reqired_area_gdf)
        width, height = Utils.get_dimensions(zoom_bounds)
        width_buffer = width * zoom_padding  # % of width
        height_buffer = height * zoom_padding  # % of height

        self.ax.set_xlim([zoom_bounds[WorldSides.WEST.name] - width_buffer,
                         # Expand x limits
                          zoom_bounds[WorldSides.EAST.name] + width_buffer])
        self.ax.set_ylim([zoom_bounds[WorldSides.SOUTH.name] - height_buffer,
                         # Expand y limits
                          zoom_bounds[WorldSides.NORTH.name] + height_buffer])

    def generate_pdf(self, pdf_name: str):
        plt.savefig(f'{pdf_name}.pdf', format='pdf',
                    transparent=True, pad_inches=0.1)

    def show_plot(self):
        plt.show()
