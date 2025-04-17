import subprocess
from multiprocessing.synchronize import Lock
from typing import Any

from geopandas import GeoDataFrame

from common.map_enums import SharedDictKeys
from modules.utils import Utils


class OsmDataPreprocessor:
    def __init__(self, osm_input_files: list[str] | str, osm_tmp_folder: str, task_id: str, shared_dict: dict[str, Any], lock: Lock, osm_output_file: str = None):
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
        name: str = f'{self.osm_tmp_folder}_geojson_polygon_{self.task_id}.geojson'
        reqired_area_gdf.to_file(name, driver="GeoJSON")
        return name
    
    def __sort_osm_file(self, osm_input_file: str, osm_output_file: str):
        """Sort osm file for merging"""
        command = [
            'osmium', 'sort',
            '--strategy', 'multipass',
            '--overwrite',
            '--no-progress',
            osm_input_file,
            '-o', osm_output_file
        ]
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            raise Exception(
                f"Cannot sort osm file: {e}")
    
    def __merge_osm_files(self, input_tmp_files: list[str], osm_output_file):
        """Merge multiple osm files into one file."""
        command = ['osmium', 'merge'] + input_tmp_files + \
            ['--overwrite',
             '--no-progress',
             '-o', osm_output_file]

        try:
            subprocess.run(command, check=True)
        except Exception as e:
            raise Exception(
                f"Cannot merge osm files: {e}")

    def __extract_area(self, osm_input_file: str, osm_output_file: str, temp_geojson_path: str):
        """Extract wanted area from osm file using osmium tool. It will create a new osm file with the wanted area. That will be used to load data or in merging process."""
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
            subprocess.run(command, check=True)
        except Exception as e:
            raise Exception(
                f"Cannot extract osm file: {e}")

    def extract_areas(self, reqired_area_gdf: GeoDataFrame, crsTo: str):
        """Extract wanted area from osm files to new files and merge them if needed. That return name of that new osm file for data loading."""
        temp_geojson_path = self.__create_tmp_geojson(
            reqired_area_gdf.to_crs(crsTo))
        with self.lock:
            self.shared_dict[self.task_id] = {
                **self.shared_dict[self.task_id],
                SharedDictKeys.FILES.value: [*self.shared_dict[self.task_id][SharedDictKeys.FILES.value], temp_geojson_path],
            }

        sorted_extracted_files_names = []
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
                sorted_extract_file_name = f'{self.osm_tmp_folder}sorted_osm_merge_file_{index}_{self.task_id}.osm.pbf'
                with self.lock:
                    self.shared_dict[self.task_id] = {
                        **self.shared_dict[self.task_id],
                        SharedDictKeys.FILES.value: [*self.shared_dict[self.task_id][SharedDictKeys.FILES.value], sorted_extract_file_name, extract_file_name],
                    }
                self.__extract_area(
                    osm_input_file, extract_file_name, temp_geojson_path)
                
                self.__sort_osm_file(
                    extract_file_name, sorted_extract_file_name)
                
                Utils.remove_file(extract_file_name)
                with self.lock:
                    self.shared_dict[self.task_id] = {
                        **self.shared_dict[self.task_id],
                    SharedDictKeys.FILES.value: [file for file in self.shared_dict[self.task_id][SharedDictKeys.FILES.value] if file != extract_file_name],
                    }
                sorted_extracted_files_names.append(sorted_extract_file_name)

            try:
                self.__merge_osm_files(
                    sorted_extracted_files_names, self.osm_output_file)
            except Exception as e:
                raise Exception(f"Cannot merge osm file")
            finally:
                # remove temp files
                for tmp_file in sorted_extracted_files_names:
                    Utils.remove_file(tmp_file)
                with self.lock:
                    self.shared_dict[self.task_id] = {
                        **self.shared_dict[self.task_id],
                        SharedDictKeys.FILES.value: [file for file in self.shared_dict[self.task_id][SharedDictKeys.FILES.value] if file not in sorted_extracted_files_names],
                    }

        Utils.remove_file(temp_geojson_path)
        with self.lock:
            self.shared_dict[self.task_id] = {
                **self.shared_dict[self.task_id],
                SharedDictKeys.FILES.value: [file for file in self.shared_dict[self.task_id][SharedDictKeys.FILES.value] if file != temp_geojson_path],
            }
        return self.osm_output_file
