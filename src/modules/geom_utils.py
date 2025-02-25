
import numpy as np
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
        return {WorldSides.WEST.name: bounds[0],
                WorldSides.SOUTH.name: bounds[1],
                WorldSides.EAST.name: bounds[2],
                WorldSides.NORTH.name: bounds[3]}


    @staticmethod
    def create_polygon_from_bounds(area_bounds: BoundsDict) -> Polygon:
        return Polygon([
            (area_bounds[WorldSides.EAST.name], area_bounds[WorldSides.SOUTH.name]),
            (area_bounds[WorldSides.EAST.name], area_bounds[WorldSides.NORTH.name]),
            (area_bounds[WorldSides.WEST.name], area_bounds[WorldSides.NORTH.name]),
            (area_bounds[WorldSides.WEST.name], area_bounds[WorldSides.SOUTH.name]),
            # Closing the polygon
            (area_bounds[WorldSides.EAST.name], area_bounds[WorldSides.SOUTH.name])
        ])
        
    @staticmethod
    def merge_lines_safe(geoms):
        unioned = unary_union(geoms)
        if unioned.is_empty:
            return unioned
        if unioned.geom_type == "LineString":
            return unioned
        if unioned.geom_type == "MultiLineString":
            try:
                return linemerge(unioned)
            except Exception as e:
                print(f"linemerge failed on MultiLineString: {e}")
                return unioned
        if unioned.geom_type == "GeometryCollection":
            lines = [geom for geom in unioned if geom.geom_type in [
                "LineString", "MultiLineString"]]
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
        if(bbox_area == 0):
            return False
        percentage_inside: float = intersection_area / bbox_area
        return percentage_inside >= threshold

    @staticmethod
    def get_distance(point1: Point, point2: Point):
        geod = Geod(ellps="WGS84")
        _, _, distance_m = geod.inv(point1[1], point1[0], point2[1], point2[0])
        return distance_m