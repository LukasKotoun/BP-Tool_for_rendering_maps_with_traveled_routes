import math

import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union, linemerge
from pyproj import Geod

from common.map_enums import WorldSides
from common.custom_types import BoundsDict, DimensionsTuple
from common.common_helpers import time_measurement
class GeomUtils:
    
    @staticmethod
    def get_polygon_bounds(polygon: Polygon) -> BoundsDict:
        bounds: tuple[float] = polygon.bounds
        return {WorldSides.WEST.value: bounds[0],
                WorldSides.SOUTH.value: bounds[1],
                WorldSides.EAST.value: bounds[2],
                WorldSides.NORTH.value: bounds[3]}


    @staticmethod
    def create_polygon_from_bounds(area_bounds: BoundsDict) -> Polygon:
        return Polygon([
            (area_bounds[WorldSides.EAST.value], area_bounds[WorldSides.SOUTH.value]),
            (area_bounds[WorldSides.EAST.value], area_bounds[WorldSides.NORTH.value]),
            (area_bounds[WorldSides.WEST.value], area_bounds[WorldSides.NORTH.value]),
            (area_bounds[WorldSides.WEST.value], area_bounds[WorldSides.SOUTH.value]),
            # Closing the polygon
            (area_bounds[WorldSides.EAST.value], area_bounds[WorldSides.SOUTH.value])
        ])
        
    @staticmethod
    def merge_lines_safe(geoms: GeometryCollection):
        unioned = unary_union(geoms)
        if unioned.is_empty:
            return unioned
        if isinstance(unioned, LineString):
            return unioned
        if isinstance(unioned, MultiLineString):
            try:
                return linemerge(unioned)
            except Exception as e:
                print(f"linemerge failed on MultiLineString: {e}")
                return unioned
        if isinstance(unioned, GeometryCollection):
            lines = [geom for geom in unioned.geoms if
                           isinstance(geom, (LineString, MultiLineString))]
            if not lines:
                return unioned
            elif len(lines) == 1:
                return lines[0]
            else:
                # merge the extracted line geometries from geometry collection
                try:
                    return linemerge(MultiLineString(lines))
                except Exception as e:
                    print(f"linemerge failed on extracted lines: {e}")
                    return MultiLineString(lines)
        return unioned
    #! not used
    @staticmethod
    def is_geometry_inside_bounds(area_bounds: BoundsDict, polygon: GeometryCollection) -> bool:
        return GeomUtils.is_geometry_inside_geometry(GeomUtils.create_polygon_from_bounds(area_bounds), polygon)

    @staticmethod
    def is_geometry_inside_geometry(inner: GeometryCollection, outer: GeometryCollection) -> bool:
        return outer.contains(inner)
    
    @staticmethod
    def transform_geometry_to_display(ax, geometry):
        """
        Converts a Polygon or MultiPolygon to a new geometry in display (plot) coordinates
        
        Args:
            ax: Matplotlib Axes object used for transformation.
            geometry: A Shapely Polygon or MultiPolygon in data coordinates.

        Returns:
            A new Shapely Polygon or MultiPolygon transformed to display coordinates.
        """

        def transform_polygon(polygon):
            coords = np.array(polygon.exterior.coords)
            transformed_coords = ax.transData.transform(coords)
            return Polygon(transformed_coords)
        
        if isinstance(geometry, Polygon):
            return transform_polygon(geometry)

        elif isinstance(geometry, MultiPolygon):
            transformed_polygons = [transform_polygon(p) for p in geometry.geoms]
            return MultiPolygon(transformed_polygons)

        else:
            raise ValueError("Unsupported geometry type: must be Polygon or MultiPolygon")

    @staticmethod
    def is_geometry_inside_geometry_threshold(inner: GeometryCollection, outer: GeometryCollection, threshold: float = 0.95) -> bool:
        bbox_area: float = inner.area
        intersection_area: float = inner.intersection(outer).area
        if(math.isclose(bbox_area, 0)):
            return False
        percentage_inside: float = intersection_area / bbox_area
        return percentage_inside >= threshold

    @staticmethod
    def get_distance(point1: Point, point2: Point):
        geod = Geod(ellps="WGS84")
        _, _, distance_m = geod.inv(point1[1], point1[0], point2[1], point2[0])
        return distance_m
    
    @staticmethod
    def check_same_orientation(geom: Polygon | MultiPolygon, splitter: LineString | MultiLineString) -> bool:
        if(geom.is_empty or splitter.is_empty):
            return None
        # get intersetion by orientation of geom
        inter_by_geom_orientation = geom.intersection(splitter)
        if(not isinstance(inter_by_geom_orientation, LineString | MultiLineString) 
        or inter_by_geom_orientation.is_empty):
            return None
        
        # get intersetion by orientation of splitter
        inter_by_splitter_orientation = splitter.intersection(geom)
        if(not isinstance(inter_by_splitter_orientation, LineString | MultiLineString) 
        or inter_by_splitter_orientation.is_empty):
            return None
        
        inter_by_geom_orientation = GeomUtils.merge_lines_safe(
            inter_by_geom_orientation)
        inter_by_splitter_orientation = GeomUtils.merge_lines_safe(
            inter_by_splitter_orientation)
        
        # should be same as inter_by_geom_orientation
        if(not isinstance(inter_by_splitter_orientation, LineString | MultiLineString)
            or inter_by_splitter_orientation.is_empty):
            return None
    
        if (not inter_by_geom_orientation.equals(inter_by_splitter_orientation)):
            return None
        
        # if both are linestring can compare
        if (isinstance(inter_by_geom_orientation, LineString) and isinstance(inter_by_splitter_orientation, LineString)):
            return np.allclose(inter_by_geom_orientation.coords, inter_by_splitter_orientation.coords)

        # check if there is mulitlinestring or create list from linestring for for loop
        if isinstance(inter_by_geom_orientation, MultiLineString):
            geom_lines = list(inter_by_geom_orientation.geoms)
        else:
            geom_lines = [inter_by_geom_orientation]

        if isinstance(inter_by_splitter_orientation, MultiLineString):
            split_lines = list(inter_by_splitter_orientation.geoms)
        else:
            split_lines = [inter_by_splitter_orientation]

        # if some is multilinestring find components that are equal and check if it is equal by direction
        for g_line in geom_lines:
            for s_line in split_lines:
                if g_line.equals(s_line):  # Check if they are the same
                    if(not isinstance(g_line, LineString | MultiLineString)):
                        continue
                    # check if they are same by orientation
                    return np.allclose(g_line.coords, s_line.coords)

        return None

    def get_line_first_point(geometry: LineString | MultiLineString):
        if isinstance(geometry, LineString):
            first_point = Point(geometry.coords[0])
        elif isinstance(geometry, MultiLineString):
            first_point = Point(geometry.geoms[0].coords[0])
        else:
            raise ValueError("Unsupported geometry type")
        return first_point

    def get_line_last_point(geometry: LineString | MultiLineString):
        if isinstance(geometry, LineString):
            first_point = Point(geometry.coords[-1])
        elif isinstance(geometry, MultiLineString):
            first_point = Point(geometry.geoms[-1].coords[-1])
        else:
            raise ValueError("Unsupported geometry type")
        return first_point