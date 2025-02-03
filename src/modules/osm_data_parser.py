import warnings

import osmium
from shapely import wkt
import pandas as pd
import geopandas as gpd
from typing import Callable
from osmium.osm.types import TagList, Node, Way, Area
from shapely.geometry import Point, LineString, Polygon
from modules.gdf_utils import GdfUtils

from common.common_helpers import time_measurement
from common.custom_types import WantedCategories, UnwantedTags


class OsmDataParser(osmium.SimpleHandler):

    def __init__(self, wanted_nodes: WantedCategories, wanted_ways: WantedCategories, wanted_areas: WantedCategories,
                 unwanted_nodes_tags: UnwantedTags, unwanted_ways_tags: UnwantedTags, unwanted_areas_tags: UnwantedTags,
                 node_additional_columns: dict[str] = {}, way_additional_columns: dict[str] = {}, area_additional_columns: dict[str] = {}):
        super().__init__()
        # init for storing loaded elements
        self.nodes_tags: list[dict] = []
        self.nodes_geometry: list[Point] = []
        self.ways_tags: list[dict] = []
        self.ways_geometry: list[LineString] = []
        self.areas_tags: list[dict] = []
        self.areas_geometry: list[Polygon] = []

        self.wanted_nodes = wanted_nodes
        self.wanted_ways = wanted_ways
        self.wanted_areas = wanted_areas
        self.unwanted_nodes_tags = unwanted_nodes_tags
        self.unwanted_ways_tags = unwanted_ways_tags
        self.unwanted_areas_tags = unwanted_areas_tags

        # merge always wanted columns (map objects) with additions wanted info columns
        self.nodes_columns = set(wanted_nodes.keys() | node_additional_columns)
        self.way_columns = set(wanted_ways.keys() | way_additional_columns)
        self.area_columns = set(wanted_areas.keys() | area_additional_columns)
        # Create WKT Factory for geometry conversion
        # extract function from libraries - quicker than extracting every time
        self.geom_factory_point: Callable[[
            Node], str] = osmium.geom.WKTFactory().create_point
        self.geom_factory_linestring: Callable[[
            Way], str] = osmium.geom.WKTFactory().create_linestring
        self.geom_factory_multipolygon: Callable[[
            Area], str] = osmium.geom.WKTFactory().create_multipolygon
        self.wkt_loads_func: Callable[[str],
                                      Point | LineString | Polygon] = wkt.loads

    @staticmethod
    def _apply_filters_not_allowed(not_allowed_tags: UnwantedTags, tags: TagList, curr_tag_key_inside: str | None = None):
        """Checking for unwanted tag values in tags. Recursively going through 
    nested dictionaries and checks if the map feature that has these tags meets the defined condition (e.g. it is a tram track). 
    It then checks that the map feature does not contain any illegal values (e.g. tram track must not lead inside a building)

    The not_allowed_tags structure that will ensure that tram tracks doesn't have tunnel column with building_passage as value will look like this:
        {
        'railway': { # will ensure that map feature is railway category
            'tram': { # will ensure that map feature is tram track
                'tunnel': ['building_passage'] # and will set that tunnel column of map feature will not have building_passage value
                }
            }   
        }
        Args:
            not_allowed_tags (dict[str, dict[any]]|dict[str, list[str]]): Nested dictionary
            tags (_type_): Tags of concrete map feature (area, way, node)
            curr_tag_key_inside (str, optional): The key to this dict is that the function is nested within (e.g., railway)
            but cannot be a value that is inside a column in a osm data (e.g. tram, forrest...) only name of column in osm data

        Returns:
            bool: True if doesn't contain any not allowed tags otherwise false 
        """
        if (not not_allowed_tags):
            return True
        for dict_tag_key, unwanted_values in not_allowed_tags.items():
            # not directly inside any tag and curr tag is not in tags => skip
            if (curr_tag_key_inside is None and dict_tag_key not in tags):
                continue

            # Checking if map feature meets the defined conditions
            if (isinstance(unwanted_values, dict)):
                # The unwanted values are more nested => need to go down further
                next_tag_key_inside: str | None = None
                if (dict_tag_key in tags):  # dict_tag_key is tag_key (column name) in tags
                    next_tag_key_inside = dict_tag_key

                else:  # tag_key_value after tag_key
                    # check if the value inside the current key matches the dict tag key - map feature meet this condition
                    curr_tag_key_value = tags.get(curr_tag_key_inside)
                    if (curr_tag_key_value != dict_tag_key):
                        continue  # map feature does not meet this conditon for going to this next recursion level => skip

                # map feature meet this condition go to next recursion level
                return_value = OsmDataParser._apply_filters_not_allowed(
                    unwanted_values, tags, next_tag_key_inside)
                if (return_value):
                    # unwanted value not found in this branch try to find in some other tag (can't have a single one)
                    continue
                return False  # one unwanted was found, tags are not valid

            # map feature meets the defined conditions
            # Check map feature for illegal values in dict_tag_key columns
            dict_key_value = tags.get(dict_tag_key)
            if (dict_key_value is not None):
                # list of unwanted values is empty ban all values, else check for specific value in list
                if not unwanted_values or dict_key_value in unwanted_values:
                    return False
        # does not conntain unwanted tags
        return True

    @staticmethod
    def _apply_filters(wanted_features: WantedCategories, tags: TagList):
        """ Checking for wanted features by checking values in tags. Going through wanted_tags and check if map feature is some of wanted map feature.

        Map feature is represented as key (feature category) with value (concrete feature) (e.g. key=landuse and value=forest).  

        Args:
            wanted_features (dict[str, list[str]]): dict with feature category and list of allowed features for this category
            tags (_type_): tags of concrete map feature (area, way, node)

        Returns:
            bool: If find one return true else false
        """
        for features_category, wanted_features_values in wanted_features.items():
            # check if map feature is feature from this features category
            feature: str | None = tags.get(features_category)
            if feature is not None:
                # features_values is empty list => get all from features_category else check if feature is wanted
                if not wanted_features_values or feature in wanted_features_values:
                    return True
        # map feature is not in wanted features
        return False

    def node(self, node: Node):
        if OsmDataParser._apply_filters(self.wanted_nodes, node.tags):
            try:
                # convert osmium node to wkt str format and than to shapely point geometry
                shapely_geometry: Point = self.wkt_loads_func(
                    self.geom_factory_point(node))
                filtered_tags = {tag_key: tag_value for tag_key,
                                 tag_value in node.tags if tag_key in self.nodes_columns}
                self.nodes_geometry.append(shapely_geometry)
                self.nodes_tags.append(filtered_tags)
            except RuntimeError as e:
                warnings.warn(f"Invalid node geometry: {e}")
                return
            except Exception as e:
                warnings.warn(
                    f"Error in node function - osm file processing: {e}")
                return

    def way(self, way: Way):
        if OsmDataParser._apply_filters(self.wanted_ways, way.tags) and OsmDataParser._apply_filters_not_allowed(self.unwanted_ways_tags, way.tags):
            try:
                # convert osmium way to wkt str format and than to shapely linestring geometry
                shapely_geometry: LineString = self.wkt_loads_func(
                    self.geom_factory_linestring(way))
                filtered_tags = {tag_key: tag_value for tag_key,
                                 tag_value in way.tags if tag_key in self.way_columns}
                self.ways_geometry.append(shapely_geometry)
                self.ways_tags.append(filtered_tags)
            except RuntimeError as e:
                warnings.warn(f"Invalid way geometry: {e}")
                return
            except Exception as e:
                warnings.warn(
                    f"Error in way function - osm file processing: {e}")
                return

    def area(self, area: Area):
        if OsmDataParser._apply_filters(self.wanted_areas, area.tags) and OsmDataParser._apply_filters_not_allowed(self.unwanted_areas_tags, area.tags):
            try:
                # convert osmium area to wkt str format and than to shapely polygon/multipolygon geometry
                shapely_geometry: Polygon = self.wkt_loads_func(
                    self.geom_factory_multipolygon(area))
                filtered_tags = {tag_key: tag_value for tag_key,
                                 tag_value in area.tags if tag_key in self.area_columns}
                self.areas_geometry.append(shapely_geometry)
                self.areas_tags.append(filtered_tags)
            except RuntimeError as e:
                warnings.warn(f"Invalid area geometry: {e}")
                return
            except Exception as e:
                warnings.warn(
                    f"Error in area function - osm file processing: {e}")
                return

    @time_measurement("gdf creating")
    def create_gdf(self, fromEpsg: int, toEpsg: int | None = None) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:

        nodes_gdf = GdfUtils.create_gdf_from_geometry_and_attributes(
            self.nodes_geometry, self.nodes_tags, fromEpsg)
        ways_gdf = GdfUtils.create_gdf_from_geometry_and_attributes(
            self.ways_geometry, self.ways_tags, fromEpsg)
        areas_gdf = GdfUtils.create_gdf_from_geometry_and_attributes(
            self.areas_geometry, self.areas_tags, fromEpsg)

        GdfUtils.change_columns_to_categorical(
            nodes_gdf, [key for key, _ in self.wanted_nodes.items()])
        GdfUtils.change_columns_to_categorical(
            ways_gdf, [key for key, _ in self.wanted_ways.items()])
        GdfUtils.change_columns_to_categorical(
            areas_gdf, [key for key, _ in self.wanted_areas.items()])

        # print(nodes_gdf.memory_usage(deep=True))
        # print(ways_gdf.memory_usage(deep=True))
        # print(areas_gdf.memory_usage(deep=True))
        print(f"nodes: {nodes_gdf.memory_usage(deep=True).sum()}, ways: {ways_gdf.memory_usage(deep=True).sum()}, areas: {areas_gdf.memory_usage(deep=True).sum(
        )}, combined: {nodes_gdf.memory_usage(deep=True).sum() + ways_gdf.memory_usage(deep=True).sum() + areas_gdf.memory_usage(deep=True).sum()}")
        if (toEpsg is None):
            return nodes_gdf, ways_gdf, areas_gdf
        else:
            return nodes_gdf.to_crs(epsg=toEpsg), ways_gdf.to_crs(epsg=toEpsg), areas_gdf.to_crs(epsg=toEpsg)

    def clear_gdf(self):
        self.nodes_geometry.clear()
        self.nodes_tags.clear()
        self.ways_geometry.clear()
        self.ways_tags.clear()
        self.areas_geometry.clear()
        self.areas_tags.clear()
