import os
import warnings
import unicodedata
from fastapi import UploadFile

import pandas as pd
import geopandas as gpd
from modules.gdf_utils import GdfUtils
from modules.utils import Utils
from common.map_enums import GpxColumns
from pathlib import Path


class GpxManager:

    @staticmethod
    def get_empty_gpx_gdf() -> gpd.GeoDataFrame:
        return GdfUtils.create_empty_gdf(
            None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value])
        
    # @staticmethod
    # def load_to_gdf(gpx_files: list[UploadFile] | list[str], file_prefix: str, gpx_folder: str, remove_after_load = True) -> list[str]:
    #     file_paths = []
    #     for gpx_file in gpx_files:
    #         try:
    #             file_path = os.path.join(
    #                 gpx_folder, f"{file_prefix}_{gpx_file.filename}")
    #             os.makedirs(os.path.dirname(file_path), exist_ok=True)
    #             with open(file_path, 'wb') as f:
    #                 f.write(gpx_file.file.read())
    #             file_paths.append(file_path)
    #         except Exception as e:
    #             warnings.warn(f"Error saving file {file_path}: {e}")
    #             if(remove_after_load):
    #                 Utils.remove_file(gpx_file)
    #             continue

    # @staticmethod
    # def load_gdf_from_disk(gpx_files: list[str], file_prefix: str, category_mapping: dict[str, str], toCrs: str, remove_after_load = True) -> gpd.GeoDataFrame:
    #     gpx_list: list[gpd.GeoDataFrame] = []

    #     for file_path in gpx_files:
    #         file_path = Path(file_path)
    #         if not file_path.exists():
    #             warnings.warn(f"File {file_path} does not exist.")
    #             continue
    #         # if not file_path.suffix == '.gpx':
    #         #     warnings.warn(f"File is not gpx: {file_path}")
    #         #     continue
    #         try:
    #             gpx_gdf: gpd.GeoDataFrame = (
    #                 gpd.read_file(file_path, layer='tracks'))
    #         except Exception as e:
    #             warnings.warn(f"Error reading file {file_path}: {e}")
    #             continue
    #         file_name = Utils.extract_original_name(str(file_path), file_prefix)
    #         gpx_gdf[GpxColumns.FILE_NAME.value] = "Z_Brna_.gpx"
    #         gpx_gdf[GpxColumns.CATEGORY.value] = category_mapping[file_name] if file_name in category_mapping else None
    #         gpx_list.append(gpx_gdf.to_crs(toCrs))
    #         if(remove_after_load):
    #             Utils.remove_file(file_path)

    #     if (gpx_list):
    #         gpxs_gdf = GdfUtils.combine_gdfs(gpx_list)
    #         GdfUtils.remove_columns(gpxs_gdf, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value], neg=True)
    #         GdfUtils.change_columns_to_categorical(
    #             gpxs_gdf, [GpxColumns.CATEGORY.name])
            
    #         return gpxs_gdf
    #     else:
    #         gpxs_gdf = GdfUtils.create_empty_gdf(
    #             None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value])
    #         GdfUtils.change_columns_to_categorical(
    #             gpxs_gdf, [GpxColumns.CATEGORY.name])
    #         return gpxs_gdf

    @staticmethod
    def load_to_gdf_from_memory(gpx_files: list[UploadFile], category_mapping: dict[str, str], toCrs: str) -> gpd.GeoDataFrame:
        gpx_list: list[gpd.GeoDataFrame] = []
        if(gpx_files is None):
            return GdfUtils.create_empty_gdf(
                None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value])
            
        for file in gpx_files:
            try:
                buffer = file.file.read()
                gpx_gdf: gpd.GeoDataFrame = (
                    gpd.read_file(buffer, layer='tracks'))
                file.file.close()
            except Exception as e:
                warnings.warn(f"Error reading file {file.filename}: {e}")
                continue
            gpx_gdf[GpxColumns.FILE_NAME.value] = file.filename
            gpx_gdf[GpxColumns.CATEGORY.value] = category_mapping[file.filename] if file.filename in category_mapping else None
            gpx_list.append(gpx_gdf.to_crs(toCrs))
            
        if (gpx_list):
            gpxs_gdf = GdfUtils.combine_gdfs(gpx_list)
            GdfUtils.remove_columns(gpxs_gdf, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value], neg=True)
            GdfUtils.change_columns_to_categorical(
                gpxs_gdf, [GpxColumns.CATEGORY.name])
            return gpxs_gdf
        else:
            gpxs_gdf = GdfUtils.create_empty_gdf(
                None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value])
            GdfUtils.change_columns_to_categorical(
                gpxs_gdf, [GpxColumns.CATEGORY.name])
            return gpxs_gdf

    # @staticmethod
    # def save_gpx_to_disk(gpx_files: list[UploadFile] | None, file_prefix: str, gpx_folder: str) -> list[str]:
    #     file_paths = []
    #     if(not os.path.exists(gpx_folder)):
    #         os.makedirs(gpx_folder, exist_ok=True)
    #     if(gpx_files is not None):
    #         for index, gpx_file in enumerate(gpx_files):
    #             try:
    #                 file_path = os.path.join(
    #                     gpx_folder, f"{file_prefix}_{gpx_file.filename}{index}")
    #                 with open(file_path, 'wb') as f:
    #                     f.write(gpx_file.file.read())
    #                 file_paths.append(file_path)
    #             except Exception as e:
    #                 warnings.warn(f"Error saving file {file_path}: {e}")
    #                 continue
    #     return file_paths
