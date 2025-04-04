import rtree
from modules.geom_utils import GeomUtils
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from common.map_enums import Style, MinPlot, TextPositions, WorldSides, MarkerPosition
from common.custom_types import DimensionsTuple, MarkerRow, MarkerOneAnotationRow, MarkerTwoAnotationRow, TextRow
from shapely.geometry import MultiLineString, Polygon
from shapely import MultiPolygon
from geopandas import GeoDataFrame
import pandas as pd
from matplotlib.transforms import Bbox
from matplotlib.text import Text, Annotation
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import warnings

import matplotlib
# use non-interactive backend - for processing in not main process
matplotlib.use("Agg")


class Plotter:

    MM_TO_INCH = 25.4
    DEFAULT_CAPSTYLE = "round"

    MARKER_UNDER_TEXT_ZORDER = 2
    MARKER_ABOVE_NORMAL_ZORDER = 4
    MARKER_ABOVE_ALL_ZORDER = 5

    GPX_UNDER_TEXT_ZORDER = 2
    GPX_ABOVE_TEXT_ZORDER = 4

    def __init__(self, requred_area_gdf: GeoDataFrame, paper_dimensions_mm: DimensionsTuple,
                 point_bounds_overflow_threshold: float, text_wrap_len: int, outer_reqired_area_gdf: GeoDataFrame | None = None,
                 text_expand_percent: int = 5, marker_expand_percent: int = 5):
        self.reqired_area_gdf: GeoDataFrame = requred_area_gdf
        self.reqired_area_polygon: Polygon = GdfUtils.create_polygon_from_gdf(
            self.reqired_area_gdf)
        self.text_expand_percent = text_expand_percent
        self.marker_expand_percent = marker_expand_percent

        self.outer_reqired_area_gdf = outer_reqired_area_gdf
        self.paper_dimensions_mm = paper_dimensions_mm
        self.text_wrap_len = text_wrap_len
        self.point_bounds_overflow_threshold = point_bounds_overflow_threshold
        self.markers_above_id = 0
        self.markers_and_texts_id = 0
        self.markers_above_bbox_idx = rtree.index.Index()
        self.markers_and_texts_bbox_idx = rtree.index.Index()

    def init(self, map_bg_color: str, bg_gdf: GeoDataFrame | None, area_zoom_preview: None | DimensionsTuple = None, convert_polygons=True):
        self.fig, self.ax = plt.subplots(figsize=(self.paper_dimensions_mm[0]/self.MM_TO_INCH,
                                                  # convert mm to inch
                                                  self.paper_dimensions_mm[1]/self.MM_TO_INCH), dpi=50)
        self.fig.subplots_adjust(
            left=0, right=1, top=1, bottom=0)
        self.ax.axis('off')
        self.zoom()
        self.reqired_area_gdf.plot(ax=self.ax, color=map_bg_color)
        if (bg_gdf is not None):
            if (not bg_gdf.empty):
                bg_gdf.plot(ax=self.ax, color=bg_gdf[Style.COLOR.value])

        if (convert_polygons):
            polygon_text_inside = GdfUtils.create_polygon_from_gdf(
                self.reqired_area_gdf) if self.outer_reqired_area_gdf is None else GdfUtils.create_polygon_from_gdf(self.outer_reqired_area_gdf)
            self.polygon_text_inside_display: Polygon | MultiPolygon = GeomUtils.transform_geometry_to_display_coords(
                self.ax, polygon_text_inside)
        else:
            self.polygon_text_inside_display = None

    def __filter_invalid_texts(self, gdf):
        return GdfUtils.filter_rows(gdf, {Style.TEXT_FONT_SIZE.value: '', Style.TEXT_OUTLINE_WIDTH.value: '', Style.TEXT_COLOR.value: '',
                                          Style.TEXT_OUTLINE_COLOR.value: '', Style.TEXT_FONTFAMILY.value: '', Style.TEXT_WEIGHT.value: '',
                                          Style.TEXT_STYLE.value: '', Style.ALPHA.value: '', Style.EDGE_ALPHA.value: ''})

    def __filter_invalid_markers(self, gdf):
        return GdfUtils.filter_rows(gdf, {Style.MARKER.value: '', Style.COLOR.value: '', Style.WIDTH.value: '',
                                          Style.EDGE_WIDTH.value: '', Style.EDGE_COLOR.value: '', Style.ALPHA.value: ''})

    def __marker(self, row: MarkerRow, store_bbox: bool = True, position: MarkerPosition = MarkerPosition.NORMAL.value, zorder: int = 2) -> Line2D | None:
        if (position == MarkerPosition.ABOVE_ALL.value):
            zorder = self.MARKER_ABOVE_ALL_ZORDER
        elif (position == MarkerPosition.ABOVE_NORMAL.value):
            zorder = self.MARKER_ABOVE_NORMAL_ZORDER
        elif (position == MarkerPosition.UNDER_TEXT_OVERLAP.value):
            zorder = self.MARKER_UNDER_TEXT_ZORDER

        font_properties = Utils.get_name_tuple_value(
            row, Style.MARKER_FONT_PROPERTIES.value, None)
        try:
            if (pd.notna(font_properties)):
                # icon using font properties
                va = Utils.get_name_tuple_value(
                    row, Style.MARKER_VERTICAL_ALIGN.value, "center")
                ha = Utils.get_name_tuple_value(
                    row, Style.MARKER_HORIZONTAL_ALIGN.value, "center")
                marker: Text = self.ax.text(row.geometry.x, row.geometry.y, row.MARKER, color=row.COLOR, fontsize=row.WIDTH,
                                            font_properties=font_properties, alpha=row.ALPHA,
                                            path_effects=[pe.withStroke(linewidth=row.EDGE_WIDTH,
                                                                        alpha=row.ALPHA, foreground=row.EDGE_COLOR)],
                                            zorder=zorder, va=va, ha=ha)
            else:
                marker: Line2D = self.ax.plot(row.geometry.x, row.geometry.y, marker=row.MARKER, mfc=row.COLOR, ms=row.WIDTH,
                                              mec=row.EDGE_COLOR, mew=row.EDGE_WIDTH, alpha=row.ALPHA,
                                              zorder=zorder)
        except ValueError as e:
            warnings.warn(f"Marker {row.MARKER} is not valid")
            return None

        if (isinstance(marker, list)):
            marker = marker[0]
        bbox = marker.get_tightbbox()
        if (not Utils.is_bbox_valid(bbox)):
            # marker is plotted outside of the figure
            marker.remove()
            return None

        bboxs_index = None
        if (position == MarkerPosition.ABOVE_NORMAL.value):
            bboxs_index = self.markers_above_bbox_idx
        elif (position == MarkerPosition.NORMAL.value):
            bboxs_index = self.markers_and_texts_bbox_idx

        bbox_expanded = Utils.expand_bbox(bbox, self.marker_expand_percent)
        if (not Utils.check_bbox_position(bbox_expanded, bbox, bboxs_index,
                                          self.point_bounds_overflow_threshold, self.polygon_text_inside_display)):
            marker.remove()
            return None

        if (store_bbox):
            if (position == MarkerPosition.ABOVE_NORMAL.value):
                self.markers_above_bbox_idx.insert(
                    self.markers_above_id, bbox_expanded.extents)
                self.markers_above_id += 1
            elif (position == MarkerPosition.NORMAL.value):
                self.markers_and_texts_bbox_idx.insert(
                    self.markers_and_texts_id, bbox_expanded.extents)
                self.markers_and_texts_id += 1
        return marker

    def __marker_annotation(self, row: TextRow, text: str, marker_size: float, text_positions: list[TextPositions], text_wrap_len: int = 0, check_bbox_position: bool = True,
                            zorder: int = 3) -> Annotation | None:
        text = Utils.wrap_text(text, text_wrap_len, replace_whitespace=False)
        x, y = row.geometry.x, row.geometry.y
        if (not isinstance(text_positions, list)):
            warnings.warn("Text positions must be list")
            return None
        for position in text_positions:
            x_shift = 0
            y_shift = 0
            if (position == TextPositions.TOP.value):
                y_shift += marker_size * 0.8
                ha = 'center'
                va = 'bottom'
            elif (position == TextPositions.BOTTOM.value):
                y_shift -= marker_size
                ha = 'center'
                va = 'top'
            elif (position == TextPositions.LEFT.value):
                x_shift -= marker_size
                ha = 'right'
                va = 'center'
            elif (position == TextPositions.RIGHT.value):
                x_shift += marker_size
                ha = 'left'
                va = 'center'
            elif (position == TextPositions.TOP_LEFT.value):
                x_shift -= marker_size
                y_shift += marker_size * 0.8
                ha = 'right'
                va = 'bottom'
            elif (position == TextPositions.TOP_RIGHT.value):
                x_shift += marker_size
                y_shift += marker_size * 0.8
                ha = 'left'
                va = 'bottom'
            elif (position == TextPositions.BOTTOM_LEFT.value):
                x_shift -= marker_size
                y_shift -= marker_size
                ha = 'right'
                va = 'top'
            elif (position == TextPositions.BOTTOM_RIGHT.value):
                x_shift += marker_size
                y_shift -= marker_size
                ha = 'left'
                va = 'top'
            else:
                warnings.warn(f"Unknown text position {position}")
                continue

            font_properties = Utils.get_name_tuple_value(
                row, Style.TEXT_FONT_PROPERTIES.value, None)
            text_anotation: Annotation = self.ax.annotate(text, (x, y), textcoords="offset points", xytext=(x_shift, y_shift), ha=ha, va=va,
                                                          color=row.TEXT_COLOR, fontsize=row.TEXT_FONT_SIZE, font_properties=font_properties,
                                                          family=row.TEXT_FONTFAMILY, alpha=row.ALPHA,
                                                          weight=row.TEXT_WEIGHT, style=row.TEXT_STYLE,
                                                          path_effects=[pe.withStroke(linewidth=row.TEXT_OUTLINE_WIDTH,
                                                                                      alpha=row.EDGE_ALPHA, foreground=row.TEXT_OUTLINE_COLOR)], zorder=zorder)
            bbox = text_anotation.get_tightbbox()
            if (not Utils.is_bbox_valid(bbox)):
                # text is plotted outside of the figure
                text_anotation.remove()
                text_anotation = None
                continue

            if (check_bbox_position):
                bbox_expanded = Utils.expand_bbox(
                    bbox, self.text_expand_percent)
                if (not Utils.check_bbox_position(bbox_expanded, bbox, self.markers_and_texts_bbox_idx,
                                                  self.point_bounds_overflow_threshold, self.polygon_text_inside_display)):
                    text_anotation.remove()
                    text_anotation = None
                    continue
            return text_anotation
        return None

    def __text_on_point(self, row: TextRow, text: str, text_wrap_len=0, store_bbox: bool = True, check_bbox_position: bool = True,
                        zorder: int = 3) -> Text | None:
        """Plot text on point with given text properties."""
        text = Utils.wrap_text(text, text_wrap_len, replace_whitespace=False)
        font_properties = Utils.get_name_tuple_value(
            row, Style.TEXT_FONT_PROPERTIES.value, None)
        text_plot: Text = self.ax.text(row.geometry.x, row.geometry.y, text, color=row.TEXT_COLOR, fontsize=row.TEXT_FONT_SIZE, family=row.TEXT_FONTFAMILY,
                                       weight=row.TEXT_WEIGHT, style=row.TEXT_STYLE, ha='center', va='center', alpha=row.ALPHA, font_properties=font_properties,
                                       path_effects=[pe.withStroke(linewidth=row.TEXT_OUTLINE_WIDTH,
                                                                   alpha=row.EDGE_ALPHA, foreground=row.TEXT_OUTLINE_COLOR)], zorder=zorder)
        bbox = text_plot.get_tightbbox()
        if (not Utils.is_bbox_valid(bbox)):
            # text is plotted outside of the figure
            text_plot.remove()
            return None

        if (check_bbox_position or store_bbox):
            bbox_expanded = Utils.expand_bbox(bbox, self.text_expand_percent)
        if (check_bbox_position):
            if (not Utils.check_bbox_position(bbox_expanded, bbox, self.markers_and_texts_bbox_idx,
                                              self.point_bounds_overflow_threshold, self.polygon_text_inside_display)):
                text_plot.remove()
                return None
        if (store_bbox):
            self.markers_and_texts_bbox_idx.insert(
                self.markers_and_texts_id, bbox_expanded.extents)
            self.markers_and_texts_id += 1

        return text_plot

    def __marker_with_one_annotation(self, row: MarkerOneAnotationRow, text_row=Style.TEXT1.value, store_bbox: bool = True, text_zorder: int = 3, marker_zorder: int = 2) -> tuple[Line2D, Text]:
        if (row.MIN_PLOT_REQ in {MinPlot.TEXT1_TEXT2.value, MinPlot.MARKER_TEXT1_TEXT2.value}):
            return (None, None)

        marker_position = Utils.get_name_tuple_value(
            row, Style.MARKER_LAYER_POSITION.value, MarkerPosition.NORMAL.value)
        marker = self.__marker(
            row, store_bbox=False, position=marker_position, zorder=marker_zorder)
        # if node must have marker return None
        if (marker is None and row.MIN_PLOT_REQ in {MinPlot.MARKER.value, MinPlot.MARKER_TEXT1.value, MinPlot.MARKER_TEXT2.value,
                                                    MinPlot.MARKER_TEXT1_OR_TEXT2.value}):
            return (None, None)
        # can have text in text1 or text2
        text_wrap_len = Utils.get_name_tuple_value(
            row, Style.TEXT_WRAP_LEN.value, self.text_wrap_len)
        if (text_row == Style.TEXT1.value):
            text = row.TEXT1
            text_positions = row.TEXT1_POSITIONS
        else:
            text = row.TEXT2
            text_positions = row.TEXT2_POSITIONS
        text_annotation = self.__marker_annotation(
            row, text, row.WIDTH, text_positions, text_wrap_len, True, zorder=text_zorder)

        # node text was not ploted - return None
        if (text_annotation is None and row.MIN_PLOT_REQ in [MinPlot.TEXT1.value, MinPlot.TEXT2.value, MinPlot.MARKER_TEXT1.value,
                                                             MinPlot.MARKER_TEXT2.value, MinPlot.MARKER_TEXT1_OR_TEXT2.value]):
            if (marker is not None):
                marker.remove()
            return (None, None)

        # node have ploted minimum parts
        if (store_bbox):
            if (marker is not None):
                if (marker_position == MarkerPosition.ABOVE_NORMAL.value):
                    self.markers_above_bbox_idx.insert(self.markers_above_id,
                                                       Utils.expand_bbox(marker.get_tightbbox(), self.marker_expand_percent).extents)
                    self.markers_above_id += 1
                elif (marker_position == MarkerPosition.NORMAL.value):
                    self.markers_and_texts_bbox_idx.insert(self.markers_and_texts_id,
                                                           Utils.expand_bbox(marker.get_tightbbox(), self.marker_expand_percent).extents)
                    self.markers_and_texts_id += 1
            if (text_annotation is not None):
                self.markers_and_texts_bbox_idx.insert(self.markers_and_texts_id,
                                                       Utils.expand_bbox(text_annotation.get_tightbbox(), self.text_expand_percent).extents)
                self.markers_and_texts_id += 1
        return (marker, text_annotation)

    def __marker_with_two_annotations(self, row: MarkerTwoAnotationRow, store_bbox: bool = True, text_zorder: int = 3, marker_zorder: int = 2) -> tuple[Line2D, Text, Text]:
        marker_position = Utils.get_name_tuple_value(
            row, Style.MARKER_LAYER_POSITION.value, MarkerPosition.NORMAL.value)
        marker = self.__marker(row, store_bbox=False, position=marker_position,
                               zorder=marker_zorder)
        # if node must have marker return None
        if (marker is None and row.MIN_PLOT_REQ in [MinPlot.MARKER.value, MinPlot.MARKER_TEXT1.value,
                                                    MinPlot.MARKER_TEXT2.value, MinPlot.MARKER_TEXT1_TEXT2.value,
                                                    MinPlot.MARKER_TEXT1_OR_TEXT2.value]):
            return (None, None, None)

        # must have text in text1 and text2
        text_wrap_len = Utils.get_name_tuple_value(
            row, Style.TEXT_WRAP_LEN.value, self.text_wrap_len)
        # check if text1 and text2 have same positions - merge and plot as one text
        if (row.TEXT1_POSITIONS == row.TEXT2_POSITIONS):
            text = str(row.TEXT1) + '\n' + str(row.TEXT2)
            text1 = self.__marker_annotation(
                row, text, row.WIDTH, row.TEXT1_POSITIONS, text_wrap_len, True, zorder=text_zorder)
            if (text1 is None and row.MIN_PLOT_REQ in [MinPlot.TEXT1.value, MinPlot.TEXT2.value, MinPlot.TEXT1_TEXT2.value, MinPlot.MARKER_TEXT1.value,
                                                       MinPlot.MARKER_TEXT2.value, MinPlot.MARKER_TEXT1_TEXT2.value]):
                if (marker is not None):
                    marker.remove()
                return (None, None, None)
            text2 = None
        else:
            text1 = self.__marker_annotation(
                row, row.TEXT1, row.WIDTH, row.TEXT1_POSITIONS, text_wrap_len, True, zorder=text_zorder)
            if (text1 is None and row.MIN_PLOT_REQ in [MinPlot.TEXT1.value, MinPlot.TEXT1_TEXT2.value, MinPlot.MARKER_TEXT1.value, MinPlot.MARKER_TEXT1_TEXT2.value]):
                if (marker is not None):
                    marker.remove()
                return (None, None, None)

            text2 = self.__marker_annotation(
                row, row.TEXT2, row.WIDTH, row.TEXT2_POSITIONS, text_wrap_len, True, zorder=text_zorder)
            if (text2 is None and row.MIN_PLOT_REQ in [MinPlot.TEXT2.value, MinPlot.TEXT1_TEXT2.value, MinPlot.MARKER_TEXT2.value, MinPlot.MARKER_TEXT1_TEXT2.value]):
                if (marker is not None):
                    marker.remove()
                if (text1 is not None):
                    text1.remove()
                return (None, None, None)

            # must have at least one text
            if (text1 is None and text2 is None and row.MIN_PLOT_REQ in [MinPlot.MARKER_TEXT1_OR_TEXT2.value]):
                if (marker is not None):
                    marker.remove()
                return (None, None, None)

        # node have ploted minimum parts
        if (store_bbox):
            if (marker is not None):
                if (marker_position == MarkerPosition.ABOVE_NORMAL.value):
                    self.markers_above_bbox_idx.insert(self.markers_above_id,
                                                       Utils.expand_bbox(marker.get_tightbbox(), self.marker_expand_percent).extents)
                    self.markers_above_id += 1
                elif (marker_position == MarkerPosition.NORMAL.value):
                    self.markers_and_texts_bbox_idx.insert(self.markers_and_texts_id,
                                                           Utils.expand_bbox(marker.get_tightbbox(), self.marker_expand_percent).extents)
                    self.markers_and_texts_id += 1
            if (text1 is not None):
                self.markers_and_texts_bbox_idx.insert(self.markers_and_texts_id,
                                                       Utils.expand_bbox(text1.get_tightbbox(), self.text_expand_percent).extents)
                self.markers_and_texts_id += 1
            if (text2 is not None):
                self.markers_and_texts_bbox_idx.insert(self.markers_and_texts_id,
                                                       Utils.expand_bbox(text2.get_tightbbox(), self.text_expand_percent).extents)
                self.markers_and_texts_id += 1

    def __text_gdf_on_points(self, gdf: GeoDataFrame, store_bbox: bool = True, zorder: int = 3):
        """Plot all rows in gdf with text in TEXT1 or TEXT2 to point"""
        gdf = self.__filter_invalid_texts(gdf)

        for row in gdf.itertuples(index=False):
            text1 = Utils.get_name_tuple_value(row, Style.TEXT1.value, None)
            text2 = Utils.get_name_tuple_value(row, Style.TEXT2.value, None)
            if (text1 is not None and text2 is not None):
                text = str(text1) + '\n' + str(text2)
            elif (text1 is not None):
                text = text1
            else:
                text = text2

            self.__text_on_point(
                row, text, Utils.get_name_tuple_value(row, Style.TEXT_WRAP_LEN.value, self.text_wrap_len), store_bbox, True, zorder=zorder)

    def __markers_gdf(self, gdf: GeoDataFrame, store_bbox: bool = True, zorder: int = 2):
        """Plot all markers in gdf to point"""
        gdf = self.__filter_invalid_markers(gdf)
        for row in gdf.itertuples(index=False):
            self.__marker(row, store_bbox=store_bbox,
                          position=Utils.get_name_tuple_value(
                              row, Style.MARKER_LAYER_POSITION.value, MarkerPosition.NORMAL.value), zorder=zorder)

    def __markers_gdf_with_one_annotation(self, gdf: GeoDataFrame, store_bbox: bool = True, text_zorder: int = 3, marker_zorder: int = 2):
        """Plot all markers in gdf to point with annotation in TEXT1 or TEXT2"""
        gdf = self.__filter_invalid_markers(gdf)
        gdf = self.__filter_invalid_texts(gdf)

        for row in gdf.itertuples(index=False):
            text1 = Utils.get_name_tuple_value(row, Style.TEXT1.value, None)
            if (text1 is not None):
                self.__marker_with_one_annotation(
                    row, Style.TEXT1.value, store_bbox, text_zorder=text_zorder, marker_zorder=marker_zorder)
            else:
                self.__marker_with_one_annotation(
                    row, Style.TEXT2.value, store_bbox, text_zorder=text_zorder, marker_zorder=marker_zorder)

    def __markers_gdf_with_two_annotations(self, gdf: GeoDataFrame, store_bbox: bool = True, text_zorder: int = 3, marker_zorder: int = 2):
        """PLot all markers in gdf to point with annotations in TEXT1 and TEXT2"""
        gdf = self.__filter_invalid_markers(gdf)
        gdf = self.__filter_invalid_texts(gdf)

        for row in gdf.itertuples(index=False):
            self.__marker_with_two_annotations(
                row, store_bbox, text_zorder=text_zorder, marker_zorder=marker_zorder)

    def nodes(self, nodes_gdf: GeoDataFrame):
        if (nodes_gdf.empty):
            return
        # groups sorted from biggest to smallest zindex
        groups = GdfUtils.get_groups_by_columns(
            nodes_gdf, [Style.ZINDEX.value], [])
        for zindex, nodes_group_gdf in sorted(groups, key=lambda x: x[0], reverse=True):
            markers_with_two_annotations, group_rest = GdfUtils.filter_rows(
                nodes_group_gdf, {Style.MARKER.value: '', Style.TEXT1.value: '', Style.TEXT2.value: '',
                                  Style.TEXT1_POSITIONS.value: '', Style.TEXT2_POSITIONS.value: ''}, compl=True)

            markers_with_one_annotation, group_rest = GdfUtils.filter_rows(
                group_rest, [{Style.MARKER.value: '', Style.TEXT1.value: '', Style.TEXT1_POSITIONS.value: ''}, {Style.MARKER.value: '', Style.TEXT2.value: '', Style.TEXT2_POSITIONS.value: ''}], compl=True)

            markers, group_rest = GdfUtils.filter_rows(
                group_rest, {Style.MARKER.value: ''}, compl=True)

            texts = GdfUtils.filter_rows(
                group_rest, [{Style.TEXT1.value: ''}, {Style.TEXT2.value: ''}])

            self.__text_gdf_on_points(texts)
            self.__markers_gdf_with_one_annotation(
                markers_with_one_annotation)
            self.__markers_gdf_with_two_annotations(
                markers_with_two_annotations)
            self.__markers_gdf(markers)

    def __line_edges(self, lines_gdf, capstyle: str = None, zorder: int = 2):
        edge_lines_gdf = GdfUtils.filter_rows(lines_gdf, {
            Style.EDGE_COLOR.value: '', Style.EDGE_LINESTYLE.value: '', Style.EDGE_WIDTH.value: '', Style.EDGE_ALPHA.value: ''})
        if (edge_lines_gdf.empty):
            return

        if (capstyle is not None):
            edge_lines_gdf[Style.EDGE_CAPSTYLE.value] = capstyle

        groups = GdfUtils.get_groups_by_columns(
            edge_lines_gdf, [Style.EDGE_CAPSTYLE.value], [self.DEFAULT_CAPSTYLE], False)
        for capstyle, edge_lines_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CAPSTYLE
            edge_lines_group_gdf.plot(ax=self.ax, color=edge_lines_group_gdf[Style.EDGE_COLOR.value],
                                      linewidth=edge_lines_group_gdf[Style.EDGE_WIDTH.value],
                                      linestyle=edge_lines_group_gdf[Style.EDGE_LINESTYLE.value],
                                      alpha=edge_lines_group_gdf[Style.EDGE_ALPHA.value],
                                      path_effects=[pe.Stroke(capstyle=capstyle)], zorder=zorder)

    def __line(self, lines_gdf, capstyle: str = None, zorder: int = 2):
        """
        Plot normal lines (not dashed).
        Lines in lines_gdf should have same zindex for correct order of plotting.

        Args:
            lines_gdf (_type_): _description_
            capstyle (str, optional): _description_. Defaults to None.
            zorder (int, optional): _description_. Defaults to 2.
        """
        lines_gdf = GdfUtils.filter_rows(lines_gdf, {
            Style.COLOR.value: '', Style.LINESTYLE.value: '', Style.WIDTH.value: '', Style.ALPHA.value: ''})
        if (lines_gdf.empty):
            return

        if (capstyle is not None):
            lines_gdf[Style.LINE_CAPSTYLE.value] = capstyle

        groups = GdfUtils.get_groups_by_columns(
            lines_gdf, [Style.LINE_CAPSTYLE.value], [self.DEFAULT_CAPSTYLE], False)
        for capstyle, lines_group_gdf in groups:
            if (pd.isna(capstyle)):
                capstyle = self.DEFAULT_CAPSTYLE

            lines_group_gdf.plot(ax=self.ax, color=lines_group_gdf[Style.COLOR.value],
                                 linewidth=lines_group_gdf[Style.WIDTH.value],
                                 linestyle=lines_group_gdf[Style.LINESTYLE.value],
                                 alpha=lines_group_gdf[Style.ALPHA.value],
                                 path_effects=[pe.Stroke(capstyle=capstyle)], zorder=zorder)

    def __dashed_with_edge_dashed(self, lines_gdf: GeoDataFrame, line_capstyle: str = None, edge_capstyle: str = None, zorder: int = 2):
        """
        Lines in lines_gdf should have same zindex for correct order of plotting.
        Args:
            lines_gdf (GeoDataFrame): lines to plot.
            line_capstyle (str, optional): _description_. Defaults to DEFAULT_CAPSTYLE.
            edge_capstyle (str, optional): _description_. Defaults to DEFAULT_CAPSTYLE.
            zorder (int, optional): _description_. Defaults to 2.
        """
        def plot(lines_gdf: GeoDataFrame, connect_edge: bool, line_capstyle: str = None, edge_capstyle: str = None, zorder: int = 2):
            """
            Ploting with or without connected edges in dashed lines
            """
            if (line_capstyle is not None):
                lines_gdf[Style.LINE_CAPSTYLE.value] = line_capstyle
            if (edge_capstyle is not None):
                lines_gdf[Style.EDGE_CAPSTYLE.value] = edge_capstyle
            groups = GdfUtils.get_groups_by_columns(
                lines_gdf, [Style.LINE_CAPSTYLE.value, Style.EDGE_CAPSTYLE.value, Style.EDGE_WIDTH.value,
                            Style.EDGE_COLOR.value, Style.EDGE_ALPHA.value], [], False)

            for (line_capstyle, edge_capstyle, edge_width, edge_color, edge_alpha), gdf_group in groups:
                if (pd.isna(line_capstyle)):
                    line_capstyle = self.DEFAULT_CAPSTYLE
                if (pd.isna(edge_capstyle)):
                    edge_capstyle = self.DEFAULT_CAPSTYLE

                if (connect_edge):
                    gdf_group.plot(ax=self.ax, color=gdf_group[Style.EDGE_COLOR.value], linestyle='-',
                                   linewidth=gdf_group[Style.EDGE_WIDTH_DASHED_CONNECT.value], alpha=gdf_group[Style.EDGE_ALPHA.value], path_effects=[
                        pe.Stroke(capstyle=edge_capstyle)], zorder=zorder)

                gdf_group.plot(ax=self.ax, color=gdf_group[Style.COLOR.value], linestyle=gdf_group[Style.LINESTYLE.value],
                               linewidth=gdf_group[Style.WIDTH.value], alpha=gdf_group[Style.ALPHA.value], path_effects=[
                    pe.Stroke(
                        linewidth=edge_width, foreground=edge_color, alpha=edge_alpha,
                        capstyle=edge_capstyle), pe.Normal(), pe.Stroke(capstyle=line_capstyle)], zorder=zorder)

        lines_gdf = GdfUtils.filter_rows(lines_gdf, {Style.COLOR.value: '', Style.EDGE_COLOR.value: '',
                                         Style.LINESTYLE.value: '', Style.WIDTH.value: '', Style.EDGE_WIDTH.value: '',
                                         Style.ALPHA.value: '', Style.EDGE_ALPHA.value: ''})

        connect_edge, not_connect_edge = GdfUtils.filter_rows(
            lines_gdf, [{Style.EDGE_WIDTH_DASHED_CONNECT.value: ''}], compl=True)

        if (not connect_edge.empty):
            plot(connect_edge, True, line_capstyle, edge_capstyle, zorder)
        if (not not_connect_edge.empty):
            plot(not_connect_edge, False, line_capstyle, edge_capstyle, zorder)

    def __dashed_with_edge_solid(self, lines_gdf: GeoDataFrame, line_capstyle: str = None, edge_capstyle: str = None, zorder: int = 2):
        """
        Lines in lines_gdf should have same zindex for correct order of plotting.

        Args:
            lines_gdf (GeoDataFrame): lines to plot.
            line_capstyle (str, optional): Defaults to DEFAULT_CAPSTYLE.
            edge_capstyle (str, optional): Defaults to DEFAULT_CAPSTYLE.
            zorder (int, optional): Defaults to 2.
        """
        if (lines_gdf.empty):
            return
        lines_gdf = GdfUtils.filter_rows(lines_gdf, {Style.EDGE_COLOR.value: '', Style.COLOR.value: '',
                                         Style.EDGE_WIDTH.value: '', Style.WIDTH.value: '',
                                         Style.ALPHA.value: '', Style.EDGE_ALPHA.value: '',
                                         Style.LINESTYLE.value: '', })
        if (lines_gdf.empty):
            return
        if (line_capstyle is not None):
            lines_gdf[Style.LINE_CAPSTYLE.value] = line_capstyle
        if (edge_capstyle is not None):
            lines_gdf[Style.EDGE_CAPSTYLE.value] = edge_capstyle

        for row in lines_gdf.itertuples(index=False):
            geom = row.geometry
            line_capstyle = Utils.get_name_tuple_value(
                row, Style.LINE_CAPSTYLE.value, self.DEFAULT_CAPSTYLE)
            edge_capstyle = Utils.get_name_tuple_value(
                row, Style.EDGE_CAPSTYLE.value, self.DEFAULT_CAPSTYLE)
            if isinstance(geom, MultiLineString):
                for line in geom.geoms:  # Extract each LineString
                    x, y = line.xy
                    self.ax.plot(x, y, color=row.EDGE_COLOR,
                                 linewidth=row.EDGE_WIDTH,
                                 alpha=row.EDGE_ALPHA, path_effects=[
                                     pe.Stroke(capstyle=edge_capstyle)], zorder=zorder)

                    self.ax.plot(x, y, color=row.COLOR, linewidth=row.WIDTH,
                                 alpha=row.ALPHA, linestyle=row.LINESTYLE, path_effects=[
                                     pe.Stroke(capstyle=line_capstyle)], zorder=zorder)
            else:
                x, y = geom.xy
                self.ax.plot(x, y, color=row.EDGE_COLOR,
                             linewidth=row.EDGE_WIDTH,
                             alpha=row.EDGE_ALPHA, path_effects=[
                                 pe.Stroke(capstyle=edge_capstyle)], zorder=zorder)

                self.ax.plot(x, y, color=row.COLOR, linewidth=row.WIDTH,
                             alpha=row.ALPHA, linestyle=row.LINESTYLE, path_effects=[
                                 pe.Stroke(capstyle=line_capstyle)], zorder=zorder)

    def __ways_normal(self, gdf: GeoDataFrame, plotEdges: bool = False, line_capstyle: str = None, edge_capstyle: str = None,
                      zorder: int = 2):
        """Plot ways based on z-index and capstyles. 
        """
        if (gdf.empty):
            return

        if (plotEdges):
            if (edge_capstyle is None):
                # filter out edges with butt capstyle and plot without crossing - will be ploted in loop
                edges_gdf = GdfUtils.filter_rows(
                    gdf, {Style.EDGE_CAPSTYLE.value: ['butt'], Style.PLOT_WITHOUT_CROSSING.value: True}, neg=True)
            else:
                edges_gdf = gdf.copy()
            groups = GdfUtils.get_groups_by_columns(
                edges_gdf, [Style.ZINDEX.value], [], False)
            # plot edge where line is solid or only edge is ploted
            for zindex, ways_group_gdf in groups:
                # first filter by crossroads
                areas, ways_group_gdf = GdfUtils.filter_areas(
                    ways_group_gdf, compl=True)
                if (not areas.empty):
                    self.areas(areas, zorder_fill=zorder,
                               zorder_edge=zorder, plot_fill=False, plot_edge=True)
                self.__line_edges(GdfUtils.filter_rows(
                    ways_group_gdf, [{Style.LINESTYLE.value: ['-', 'solid']}, {Style.COLOR.value: '~'}]), edge_capstyle, zorder)

        groups = GdfUtils.get_groups_by_columns(
            gdf, [Style.ZINDEX.value], [], False)

        # groups sorted from smalles to biggest zindex
        for zindex, ways_group_gdf in groups:
            areas, ways_group_gdf = GdfUtils.filter_areas(
                ways_group_gdf, compl=True)
            ways_without_crossroads = GdfUtils.filter_rows(
                ways_group_gdf, {Style.PLOT_WITHOUT_CROSSING.value: True})
            # crossroads only on ways with same zindex
            if (not ways_without_crossroads.empty):
                self.__line_edges(GdfUtils.filter_rows(
                    ways_without_crossroads, [{Style.LINESTYLE.value: ['-', 'solid']}, {Style.COLOR.value: '~'}]), 'butt', zorder)
            areas_without_crossroads, areas_with_crossroads = GdfUtils.filter_rows(
                areas, {Style.PLOT_WITHOUT_CROSSING.value: True}, compl=True)
            # areas without crossroads plot with edge
            if (not areas_without_crossroads.empty):
                self.areas(areas_without_crossroads, zorder_fill=zorder,
                           zorder_edge=zorder, plot_fill=True, plot_edge=True)

            if (not areas_with_crossroads.empty):
                self.areas(areas_with_crossroads, zorder_fill=zorder,
                           zorder_edge=zorder, plot_fill=True, plot_edge=False)

            # lines - line is solid or edge does not exists, dashed_with_edge_lines - line is dashed and edge exists
            rest_lines, dashed_with_edge_lines = GdfUtils.filter_rows(
                ways_group_gdf, [{Style.LINESTYLE.value: ['-', 'solid']}, {Style.EDGE_COLOR.value: '~'}], compl=True)
            # there will be filter for ways with specific edge style (edgeEffect)
            ways_dashed_edge_solid, ways_dashed_edge_dashed = GdfUtils.filter_rows(
                dashed_with_edge_lines, {Style.EDGE_LINESTYLE.value: ['-', 'solid']}, compl=True)

            self.__dashed_with_edge_dashed(
                ways_dashed_edge_dashed, line_capstyle, edge_capstyle, zorder)
            self.__dashed_with_edge_solid(
                ways_dashed_edge_solid, line_capstyle, edge_capstyle, zorder)
            self.__line(rest_lines, line_capstyle, zorder)

    def __bridges(self, bridges_gdf: GeoDataFrame, zorder: int = 2):
        """
        Plot ways that have tag bridge."""
        if (bridges_gdf.empty):
            return

        def bridges_edges(gdf: GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {Style.BRIDGE_EDGE_COLOR.value: '', Style.BRIDGE_EDGE_WIDTH.value: '',
                      Style.BRIDGE_EDGE_LINESTYLE.value: '', Style.EDGE_ALPHA.value: ''})

            if (gdf.empty):
                return

            gdf.plot(ax=self.ax, color=gdf[Style.BRIDGE_EDGE_COLOR.value],
                     linewidth=gdf[Style.BRIDGE_EDGE_WIDTH.value],
                     linestyle=gdf[Style.BRIDGE_EDGE_LINESTYLE.value],
                     alpha=gdf[Style.EDGE_ALPHA.value],
                     path_effects=[pe.Stroke(capstyle="butt")], zorder=zorder)

        def bridges_center(gdf: GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {Style.BRIDGE_WIDTH.value: '', Style.BRIDGE_COLOR.value: '',
                      Style.BRIDGE_LINESTYLE.value: '', Style.ALPHA.value: ''})
            if (gdf.empty):
                return

            gdf.plot(ax=self.ax, color=gdf[Style.BRIDGE_COLOR.value],
                     linewidth=gdf[Style.BRIDGE_WIDTH.value],
                     linestyle=gdf[Style.BRIDGE_LINESTYLE.value],
                     alpha=gdf[Style.ALPHA.value],
                     path_effects=[pe.Stroke(capstyle="butt")], zorder=zorder)

        def ways_on_bridges(gdf: GeoDataFrame):
            gdf = GdfUtils.filter_rows(
                gdf, {Style.PLOT_ON_BRIDGE.value: True})
            if (gdf.empty):
                return

            self.__ways_normal(
                gdf, True, edge_capstyle="butt", zorder=zorder)

        groups = GdfUtils.get_groups_by_columns(
            bridges_gdf, ['layer', Style.ZINDEX.value], [], False)
        for (layer, zindex), bridge_layer_gdf in groups:
            bridges_edges(bridge_layer_gdf.copy())
            bridges_center(bridge_layer_gdf.copy())
            ways_on_bridges(bridge_layer_gdf.copy())

    def __tunnels(self, tunnels_gdf, zorder: int = 2):
        """
        Plot ways that have tag tunnel"""
        if (tunnels_gdf.empty):
            return
        groups = GdfUtils.get_groups_by_columns(
            tunnels_gdf, ['layer', Style.ZINDEX.value], [], False)
        for (layer, zindex), tunnel_layer_gdf in groups:
            self.__ways_normal(tunnel_layer_gdf, True, zorder=zorder)

    def ways(self, ways_gdf: GeoDataFrame):
        if (ways_gdf.empty):
            return
        # water ways and tunnels
        waterways_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'waterway': ''}, compl=True)
        waterways_tunnel_gdf, waterways_gdf = GdfUtils.filter_rows(
            waterways_gdf, {'tunnel': ''}, compl=True)

        self.__tunnels(waterways_tunnel_gdf)
        self.__ways_normal(waterways_gdf, True)

        # normal tunnels
        ways_tunnel_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'tunnel': ''}, compl=True)
        self.__tunnels(ways_tunnel_gdf)

        # normal ways
        ways_bridge_gdf, ways_gdf = GdfUtils.filter_rows(
            ways_gdf, {'bridge': ''}, compl=True)
        self.__ways_normal(ways_gdf, True)

        # bridges
        self.__bridges(ways_bridge_gdf)

    def areas(self, areas_gdf: GeoDataFrame, zorder_fill: int = 1, zorder_edge: int = 2, plot_fill: bool = True, plot_edge: bool = True):

        if (areas_gdf.empty):
            return
        # plot face
        if (plot_fill):
            face_areas_gdf = GdfUtils.filter_rows(
                areas_gdf, {Style.COLOR.value: '', Style.ALPHA.value: ''})
            if (not face_areas_gdf.empty):
                face_areas_gdf.plot(
                    ax=self.ax, color=face_areas_gdf[Style.COLOR.value], alpha=face_areas_gdf[
                        Style.ALPHA.value], zorder=zorder_fill)
        # plot bounds
        if (plot_edge):
            edge_areas_gdf = GdfUtils.filter_rows(areas_gdf,
                                                  {Style.EDGE_COLOR.value: '', Style.WIDTH.value: '', Style.EDGE_LINESTYLE.value: '', Style.EDGE_ALPHA.value: ''})
            if (edge_areas_gdf.empty):
                return
            groups = GdfUtils.get_groups_by_columns(
                edge_areas_gdf, [Style.EDGE_CAPSTYLE.value], [self.DEFAULT_CAPSTYLE], False)
            for capstyle, edge_areas_group_gdf in groups:
                if (pd.isna(capstyle)):
                    capstyle = self.DEFAULT_CAPSTYLE
                edge_areas_group_gdf.boundary.plot(ax=self.ax, color=edge_areas_group_gdf[Style.EDGE_COLOR.value],
                                                   linewidth=edge_areas_group_gdf[
                    Style.WIDTH.value], alpha=edge_areas_group_gdf[Style.EDGE_ALPHA.value],
                    linestyle=edge_areas_group_gdf[Style.EDGE_LINESTYLE.value],
                    path_effects=[pe.Stroke(capstyle=capstyle)], zorder=zorder_edge)

    def __gpx_markers(self, gpxs_gdf: GeoDataFrame):
        "Plot markers of start and finish of gpx track"
        if (gpxs_gdf.empty):
            return
        gpx_start_markers = GdfUtils.filter_rows(gpxs_gdf, {Style.START_MARKER.value: '', Style.START_MARKER_WIDTH.value: '',
                                                            Style.START_MARKER_COLOR.value: '', Style.START_MARKER_EDGE_COLOR.value: '',
                                                            Style.START_MARKER_EDGE_WIDTH.value: '', Style.START_MARKER_ALPHA.value: ''})
        for row in gpx_start_markers.itertuples():
            mapped_row: MarkerRow = MarkerRow(
                geometry=GeomUtils.get_line_first_point(row.geometry),
                MARKER=row.START_MARKER,
                COLOR=row.START_MARKER_COLOR,
                WIDTH=row.START_MARKER_WIDTH,
                ALPHA=row.START_MARKER_ALPHA,
                EDGE_WIDTH=row.START_MARKER_EDGE_WIDTH,
                EDGE_COLOR=row.START_MARKER_EDGE_COLOR,
                MARKER_FONT_PROPERTIES=Utils.get_name_tuple_value(
                    row, Style.START_MARKER_FONT_PROPERTIES.value, None),
                MARKER_HORIZONTAL_ALIGN=Utils.get_name_tuple_value(
                    row, Style.START_MARKER_HORIZONTAL_ALIGN.value, "center"),
                MARKER_VERTICAL_ALIGN=Utils.get_name_tuple_value(
                    row, Style.START_MARKER_VERTICAL_ALIGN.value, "center"),
            )
            marker_default_position = MarkerPosition.ABOVE_ALL.value if Utils.get_name_tuple_value(
                row, Style.GPX_ABOVE_TEXT.value, False) else MarkerPosition.UNDER_TEXT_OVERLAP.value
            start_marker_position = Utils.get_name_tuple_value(
                row, Style.MARKER_LAYER_POSITION.value, marker_default_position)
            self.__marker(mapped_row, position=start_marker_position)

        gpx_finish_markers = GdfUtils.filter_rows(gpxs_gdf, {Style.FINISH_MARKER.value: '', Style.FINISH_MARKER_WIDTH.value: '',
                                                             Style.FINISH_MARKER_COLOR.value: '', Style.FINISH_MARKER_EDGE_COLOR.value: '',
                                                             Style.FINISH_MARKER_EDGE_WIDTH.value: '', Style.FINISH_MARKER_ALPHA.value: ''})

        for row in gpx_finish_markers.itertuples():
            mapped_row: MarkerRow = MarkerRow(
                geometry=GeomUtils.get_line_last_point(row.geometry),
                MARKER=row.FINISH_MARKER,
                COLOR=row.FINISH_MARKER_COLOR,
                WIDTH=row.FINISH_MARKER_WIDTH,
                ALPHA=row.FINISH_MARKER_ALPHA,
                EDGE_WIDTH=row.FINISH_MARKER_EDGE_WIDTH,
                EDGE_COLOR=row.FINISH_MARKER_EDGE_COLOR,
                MARKER_FONT_PROPERTIES=Utils.get_name_tuple_value(
                    row, Style.FINISH_MARKER_FONT_PROPERTIES.value, None),
                MARKER_HORIZONTAL_ALIGN=Utils.get_name_tuple_value(
                    row, Style.FINISH_MARKER_HORIZONTAL_ALIGN.value, "center"),
                MARKER_VERTICAL_ALIGN=Utils.get_name_tuple_value(
                    row, Style.FINISH_MARKER_VERTICAL_ALIGN.value, "center"),
            )
            marker_default_position = MarkerPosition.ABOVE_ALL.value if Utils.get_name_tuple_value(
                row, Style.GPX_ABOVE_TEXT.value, False) else MarkerPosition.UNDER_TEXT_OVERLAP.value
            finish_marker_position = Utils.get_name_tuple_value(
                row, Style.MARKER_LAYER_POSITION.value, marker_default_position)
            self.__marker(mapped_row, position=finish_marker_position)

    def gpxs(self, gpxs_gdf: GeoDataFrame):
        if (gpxs_gdf.empty):
            return
        gpx_above_text, gpx_under_text = GdfUtils.filter_rows(
            gpxs_gdf, {Style.GPX_ABOVE_TEXT.value: True}, compl=True)
        self.__ways_normal(gpx_under_text, True,
                           zorder=self.GPX_UNDER_TEXT_ZORDER)

        self.__ways_normal(gpx_above_text, True,
                           zorder=self.GPX_ABOVE_TEXT_ZORDER)

        self.__gpx_markers(gpxs_gdf)

    def clip(self, clipped_area_color: str = 'white'):
        """ Clip objects outside wanted area by covering it using white polygon with bigger z-index.
        """
        whole_area_bounds = Utils.adjust_bounds_to_fill_paper(
            GdfUtils.get_bounds_gdf(self.reqired_area_gdf), self.paper_dimensions_mm)
        whole_area_bounds = Utils.expand_bounds_dict(
            whole_area_bounds, 2)
        whole_area_polygon = GeomUtils.create_polygon_from_bounds(
            whole_area_bounds)

        clipping_polygon = whole_area_polygon.difference(
            self.reqired_area_polygon)
        if (not GeomUtils.is_geometry_inside_geometry(clipping_polygon, whole_area_polygon)):
            return
        clipping_polygon = GeoDataFrame(
            geometry=[clipping_polygon], crs=self.reqired_area_gdf.crs)
        clipping_polygon.plot(
            ax=self.ax, color=clipped_area_color, alpha=1, zorder=6)

    def area_boundary(self, boundary_map_area_gdf: GeoDataFrame, color: str = 'black', linewidth: float = 1):
        """PLot area boundary lines, but plot borders on edges of area with bigger z-index to prevent from ways and other things going over it on edges."""
        if (boundary_map_area_gdf.empty):
            return
        groups = GdfUtils.get_groups_by_columns(boundary_map_area_gdf, [
                                                Style.WIDTH.value], [], False)
        for width, group in groups:
            if (pd.isna(width)):
                width = linewidth
            # get common border in border and requred area to plot border on edge with bigger z-index
            common = GdfUtils.get_common_borders(
                self.reqired_area_gdf, group)
            # plot border in edge of area
            if (not common.empty):
                common.plot(ax=self.ax, color=color, linewidth=width, zorder=10,
                            path_effects=[pe.Stroke(capstyle="round")])
            # plot border inside area
            if (not group.empty):
                group.boundary.plot(
                    ax=self.ax, color=color, linewidth=width,
                    path_effects=[pe.Stroke(capstyle="round")])

    def zoom(self):
        """
        Zoom plot to wanted area."""
        zoom_bounds = Utils.adjust_bounds_to_fill_paper(
            GdfUtils.get_bounds_gdf(self.reqired_area_gdf), self.paper_dimensions_mm)
        self.ax.set_xlim([zoom_bounds[WorldSides.WEST.value],
                         # Expand x limits
                          zoom_bounds[WorldSides.EAST.value]])
        self.ax.set_ylim([zoom_bounds[WorldSides.SOUTH.value],
                         # Expand y limits
                          zoom_bounds[WorldSides.NORTH.value]])

    def generate_pdf(self, pdf_name: str):
        plt.savefig(pdf_name, format='pdf',
                    transparent=True, pad_inches=0.1)

    def show_plot(self):
        plt.show()
