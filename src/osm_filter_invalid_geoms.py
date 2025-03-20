import os
import sys
import osmium
import subprocess
import tempfile
from shapely import wkt
from typing import Callable
from osmium.osm.types import  Way, Area
from shapely.geometry import Point, LineString, Polygon


class ValidGeometryFilter(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        # init for storing loaded elements
        self.invalid_ways_ids = []
        self.invalid_relation_ids = []
        # Create WKT Factory for geometry conversion
        # extract function from libraries - quicker than extracting every time
        self.geom_factory_linestring: Callable[[
            Way], str] = osmium.geom.WKTFactory().create_linestring
        self.geom_factory_multipolygon: Callable[[
            Area], str] = osmium.geom.WKTFactory().create_multipolygon
        self.wkt_loads_func: Callable[[str],
                                      Point | LineString | Polygon] = wkt.loads

    def way(self, way: Way):
        try:
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
        print("No ids to remove, file is valid. Input file will be same as output, no output file created.")
        return

    ids = []
    if ways_ids:
        for id in ways_ids:
            ids.append(f"w{id}")

    if relations_ids:
        for id in relations_ids:
            ids.append(f"r{id}")

    ids_str = "\n".join(ids)
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write(ids_str)
        tmp_filename = tmp.name
    command = [
        'osmium', 'removeid',
        input_file_path,
        '-o', output_file_path,
        '--overwrite',
        '--id-file', tmp_filename]
    try:
        subprocess.run(command, check=True)
    except Exception as e:
        raise Exception(
            f"Cannot remove osm file id (error: {e}), check if osmium command line tool is installed")
    finally:
        if(os.path.exists(tmp_filename)):
            os.remove(tmp_filename)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Error: Invalid number of arguments")
        print("Output file will be created only if input file have invalid geometries")
        print(
            f"Usage: {sys.argv[0]} <file_to_check.osm.pbf> <output_file_with_valid_geometries.osm.pbf>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if (input_file == output_file):
        print(f"Error: Input and output file cannot be the same")
        sys.exit(1)

    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    print(f"Checking file: {input_file}")
    handler = ValidGeometryFilter()
    handler.apply_file(input_file)
    print(f"Found {len(handler.invalid_ways_ids)} invalid ways")
    print(handler.invalid_ways_ids)
    print(f"Found {len(handler.invalid_relation_ids)} invalid relations")
    print(handler.invalid_relation_ids)
    remove_ids(input_file, output_file, handler.invalid_ways_ids,
               handler.invalid_relation_ids)
    print(
        f"Completed filtering invalid geoms from {input_file} to {output_file if (handler.invalid_ways_ids or handler.invalid_relation_ids) else input_file}")
