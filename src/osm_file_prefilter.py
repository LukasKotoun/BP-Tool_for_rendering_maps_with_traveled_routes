import osmium
from shapely import wkt
from typing import Callable
from osmium.osm.types import TagList, Node, Way, Area
from shapely.geometry import Point, LineString, Polygon
import subprocess

import sys
import os


class ValidGeometryFilter(osmium.SimpleHandler):

    def __init__(self, wanted_ways: dict | None = {}, wanted_areas: dict | None = {}):
        super().__init__()
        # init for storing loaded elements
        self.invalid_ways_ids = []
        self.invalid_relation_ids = []
        self.wanted_ways = wanted_ways
        self.wanted_areas = wanted_areas
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

    def _apply_filters(self, wanted_features, tags: TagList):
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

    def way(self, way: Way):
        try:
            if self.wanted_ways is not None and not self._apply_filters(self.wanted_ways, way.tags):
                self.invalid_ways_ids.append(way.id)
                return
                
        
            shapely_geometry: LineString = self.wkt_loads_func(
                self.geom_factory_linestring(way))
            if (not shapely_geometry.is_valid):
                self.invalid_ways_ids.append(way.id)
                return
        except:
            self.invalid_ways_ids.append(way.id)
            return

    def area(self, area: Area):
        try:
            if self.wanted_areas is not None and not self._apply_filters(self.wanted_areas, area.tags):
                self.invalid_relation_ids.append(area.orig_id())
                return
       
            shapely_geometry: Polygon = self.wkt_loads_func(
                self.geom_factory_multipolygon(area))
            if (not shapely_geometry.is_valid):
                self.invalid_relation_ids.append(area.orig_id())
                return
        except:
            self.invalid_relation_ids.append(area.orig_id())
            return


def remove_ids(input_file_path: str, output_file_path: str, ways_ids: list[int], relations_ids: list[int]):
    if (not ways_ids and not relations_ids):
        return

    command = [
        'osmium', 'removeid',
        input_file_path,
        '--overwrite',
        '-o', output_file_path]
    if ways_ids:
        for id in ways_ids:
            command.append(f"w{id}")
    if relations_ids:
        for id in relations_ids:
            command.append(f"r{id}")
    try:
        subprocess.run(command, check=True)
    except Exception as e:
        raise Exception(
            f"Cannot remove osm file id (error: {e}), check if osmium command line tool is installed")


def filter_valid_geometries(input_file, output_file, wanted_ways=None, wanted_areas=None):
    handler = ValidGeometryFilter(wanted_ways, wanted_areas)
    handler.apply_file(input_file)
    print(f"Found {len(handler.invalid_ways_ids)} invalid ways ")
    print(f"Found {len(handler.invalid_relation_ids)} invalid relations")
    remove_ids(input_file, output_file, handler.invalid_ways_ids, handler.invalid_relation_ids)
    
    print(f"Completed filtering invalid geoms from {input_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <file_to_prefilter.pbf>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if(input_file == output_file):
        print(f"Error: Input and output file cannot be the same")
        sys.exit(1)

    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
        
    wanted_ways = None
    wanted_areas = None


    filter_valid_geometries(input_file, output_file, wanted_ways, wanted_areas)
