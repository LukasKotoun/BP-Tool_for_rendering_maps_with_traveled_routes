import tempfile
import subprocess
from multiprocessing.managers import DictProxy
from multiprocessing.synchronize import Lock
from typing import Any

from geopandas import GeoDataFrame

from common.map_enums import SharedDictKeys
from modules.utils import Utils


class OsmDataPreprocessor:
    def __init__(self, osm_input_files: list[str] | str, osm_tmp_folder: str, task_id: str, shared_dict: DictProxy[str, Any], lock: Lock, osm_output_file: str = None):
        # Can be a string (place name) or a list of coordinates
        self.osm_input_files: list[str] | str = osm_input_files
        self.task_id = task_id
        self.shared_dict = shared_dict
        self.lock = lock

        self.osm_tmp_folder = Utils.ensure_dir_exists(osm_tmp_folder)

        if osm_output_file is None:
            self.osm_output_file = f'{self.osm_tmp_folder}extracted_output_{self.task_id}.osm.pbf'
        else:
            self.osm_output_file = osm_output_file

    def __create_tmp_geojson(self, reqired_area_gdf: GeoDataFrame) -> str:
        # create tmp file with polygon representing reqired area for osmium extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson", dir=self.osm_tmp_folder) as temp_geojson:
            reqired_area_gdf.to_file(temp_geojson.name, driver="GeoJSON")
            return temp_geojson.name

    def __merge_osm_files(self, input_tmp_files: list[str], osm_output_file):
        command = ['osmium', 'merge'] + input_tmp_files + \
            ['--overwrite', 
             '--no-progress',
             '-o', osm_output_file]
        subprocess.run(command, check=True)

    def __extract_area(self, osm_input_file: str, osm_output_file: str, temp_geojson_path: str) -> str:
        command = [
            'osmium', 'extract',
            '--strategy', 'smart',
            '-S', 'types=any',
            '--overwrite',
            '--no-progress',
            '-p', temp_geojson_path,
            osm_input_file,
            '-o', osm_output_file
        ]
        try:
            pd = subprocess.run(command, check=True)
        except Exception as e:
            Utils.remove_file(temp_geojson_path)
            with self.lock:
                self.shared_dict[self.task_id] = {
                    **self.shared_dict[self.task_id],
                    SharedDictKeys.FILES.value: [file for file in self.shared_dict[self.task_id][SharedDictKeys.FILES.value] if file != temp_geojson_path],
                }
            raise Exception(
                f"Cannot extract osm file, check if osmium command line tool is installed")
        return osm_output_file

    def extract_areas(self, reqired_area_gdf: GeoDataFrame, crsTo: str):
        temp_geojson_path = self.__create_tmp_geojson(
            reqired_area_gdf.to_crs(crsTo))
        with self.lock:
            self.shared_dict[self.task_id] = {
                **self.shared_dict[self.task_id],
                SharedDictKeys.FILES.value: [*self.shared_dict[self.task_id][SharedDictKeys.FILES.value], temp_geojson_path],
            }

        extracted_files_names = []
        # extract area from osm file
        if (isinstance(self.osm_input_files, str)):
            self.__extract_area(self.osm_input_files,
                                self.osm_output_file, temp_geojson_path)

        elif (isinstance(self.osm_input_files, list) and len(self.osm_input_files) == 1):
            self.__extract_area(
                self.osm_input_files[0], self.osm_output_file, temp_geojson_path)

        elif (isinstance(self.osm_input_files, list)):
            # extract area from multiple osm files and merge them (merge after extraction for better performance)
            for index, osm_input_file in enumerate(self.osm_input_files):
                # print(
                #     f"Extracting area from file {index + 1}/{len(self.osm_input_files)}: {osm_input_file}")
                extract_file_name = f'{self.osm_tmp_folder}osm_merge_file_{index}_{self.task_id}.osm.pbf'
                with self.lock:
                    self.shared_dict[self.task_id] = {
                        **self.shared_dict[self.task_id],
                        SharedDictKeys.FILES.value: [*self.shared_dict[self.task_id][SharedDictKeys.FILES.value], extract_file_name],
                    }
                extracted_file_name = self.__extract_area(
                    osm_input_file, extract_file_name, temp_geojson_path)
                extracted_files_names.append(extracted_file_name)

            try:
                self.__merge_osm_files(
                    extracted_files_names, self.osm_output_file)
            except Exception as e:
                raise Exception(f"Cannot merge osm file")
            finally:
                # remove temp files
                for tmp_file in extracted_files_names:
                    Utils.remove_file(tmp_file)
                with self.lock:
                    self.shared_dict[self.task_id] = {
                        **self.shared_dict[self.task_id],
                        SharedDictKeys.FILES.value: [file for file in self.shared_dict[self.task_id][SharedDictKeys.FILES.value] if file not in extracted_files_names],
                    }

        Utils.remove_file(temp_geojson_path)
        with self.lock:
            self.shared_dict[self.task_id] = {
                **self.shared_dict[self.task_id],
                SharedDictKeys.FILES.value: [file for file in self.shared_dict[self.task_id][SharedDictKeys.FILES.value] if file != temp_geojson_path],
            }
        return self.osm_output_file
