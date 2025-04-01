import os
import glob
import sys
import osmium
import subprocess
import tempfile
from uuid_extensions import uuid7str
 
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
    """Usage: {osm_filter_invalid_geoms.py} <file_or_folder_to_check.osm.pbf> <file_or_folder_to_check.osm.pbf>.."""
    osm_files = []

    folder_or_file = sys.argv[1:]
    for path in folder_or_file:
        if os.path.isdir(path):
            osm_pattern = os.path.join(path, "*.osm")
            osm_pbf_pattern = os.path.join(path, "*.osm.pbf")
            osm_files_from_path = glob.glob(osm_pattern) + glob.glob(osm_pbf_pattern)
            osm_files.extend(osm_files_from_path)
        elif(os.path.isfile(path) and (path.endswith(".osm.pbf") or path.endswith(".osm"))):
            osm_files.append(path)
            
    # remove duplicates from osm_files
    osm_files = list(set(osm_files))
    if not osm_files:
        print(f"No osm files found in {folder_or_file}")
        exit(0)
    else:
        print(f"Files that will be filtered: {osm_files}")

    for input_file in osm_files:
        print(f"Checking file: {input_file}")
        # Check if the file exists
        if not os.path.isfile(input_file):
            print(f"Error: File {input_file} does not exist")
            continue
        
        # Generate a unique output file name
        file_path, file_name = os.path.split(input_file)
        output_file = f"{file_path}/{uuid7str()}_{file_name}"
        while os.path.exists(output_file):
            output_file = f"{file_path}/{uuid7str()}_{file_name}"

        # find invalid geometries
        handler = ValidGeometryFilter()
        handler.apply_file(input_file)
        print(f"Found {len(handler.invalid_ways_ids)} invalid ways")
        print(handler.invalid_ways_ids)
        print(f"Found {len(handler.invalid_relation_ids)} invalid relations")
        print(handler.invalid_relation_ids)

        # filter out invalid geometries to output file
        remove_ids(input_file, output_file, handler.invalid_ways_ids,
                handler.invalid_relation_ids)
            # replace the input file with the output file if exits
        if os.path.exists(output_file):
            os.replace(output_file, input_file)
        print(
            f"Completed filtering invalid geoms for {input_file}")
        
    print("Completed filtering invalid geoms for all files")
