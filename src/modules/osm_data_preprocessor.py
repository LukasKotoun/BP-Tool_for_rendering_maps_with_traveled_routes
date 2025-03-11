import tempfile
import subprocess
import os
from datetime import datetime
import uuid

from geopandas import GeoDataFrame


class OsmDataPreprocessor:
    def __init__(self, osm_input_files: list[str] | str, osm_output_file: str = None):
        # Can be a string (place name) or a list of coordinates
        self.osm_input_files: list[str] | str = osm_input_files
        if osm_output_file is None:
            self.osm_output_file = f'../extract_output_{uuid.uuid4()}__{datetime.now().strftime("%Y%m%d%H%M%S")}.osm.pbf'
        else:
            self.osm_output_file = osm_output_file

    def __create_tmp_geojson(self, reqired_area_gdf: GeoDataFrame) -> str:
        # create tmp file with polygon representing reqired area for osmium extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson:
            reqired_area_gdf.to_file(temp_geojson.name, driver="GeoJSON")
            return temp_geojson.name

    def __merge_osm_files(self, input_tmp_files: list[str], osm_output_file):
        command = ['osmium', 'merge'] + input_tmp_files + ['--overwrite', '-o', osm_output_file]
        subprocess.run(command, check=True)

    def __extract_area(self, osm_input_file: str, osm_output_file: str, temp_geojson_path: str) -> str:
        command = [
            'osmium', 'extract',
            '--strategy', 'smart',
            '-S', 'types=any',
            '--overwrite',
            '-p', temp_geojson_path,
            osm_input_file,
            '-o', osm_output_file
        ]
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            os.remove(temp_geojson_path)
            raise Exception(
                f"Cannot extract osm file, check if osmium command line tool is installed")
        return osm_output_file

    def extract_areas(self, reqired_area_gdf: GeoDataFrame, crsTo: str):
        temp_geojson_path = self.__create_tmp_geojson(reqired_area_gdf.to_crs(crsTo))
        extracted_files_names = []
        # extract area from osm file
        if (isinstance(self.osm_input_files, str)):
            print(f"Extracting area from file: {self.osm_input_files}")
            self.__extract_area(self.osm_input_files,
                                self.osm_output_file, temp_geojson_path)

        elif (isinstance(self.osm_input_files, list) and len(self.osm_input_files) == 1):
            print(f"Extracting area from file: {self.osm_input_files[0]}")
            self.__extract_area(
                self.osm_input_files[0], self.osm_output_file, temp_geojson_path)

        elif (isinstance(self.osm_input_files, list)):
            # extract area from multiple osm files and merge them (merge after extraction for better performance)
            for index, osm_input_file in enumerate(self.osm_input_files):
                print(f"Extracting area from file {
                      index + 1}/{len(self.osm_input_files)}: {osm_input_file}")
                extracted_file_name = self.__extract_area(osm_input_file, f'tmp_osm_merge_file_{index}_{uuid.uuid4()}.osm.pbf', temp_geojson_path)
                extracted_files_names.append(extracted_file_name)

            try:
                print(f"Merging extracted files")
                self.__merge_osm_files(
                    extracted_files_names, self.osm_output_file)
            except Exception as e:
                raise Exception(f"Cannot merge osm file")
            finally:
                # remove temp files
                for tmp_file in extracted_files_names:
                    os.remove(tmp_file)
                    
        os.remove(temp_geojson_path)
        return self.osm_output_file
