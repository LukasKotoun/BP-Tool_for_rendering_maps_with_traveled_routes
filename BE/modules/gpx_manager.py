import warnings

import geopandas as gpd
from fastapi import UploadFile

from modules.gdf_utils import GdfUtils
from common.map_enums import GpxColumns


class GpxManager:

    @staticmethod
    def get_empty_gpx_gdf() -> gpd.GeoDataFrame:
        return GdfUtils.create_empty_gdf(
            None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.GROUP.value])
        
    @staticmethod
    def find_group_name(file_name: str, groups: dict[str, list[str]])-> str | None: 
        for group_name, group_files in groups.items():
            if file_name in group_files:
                return group_name
        return None


    @staticmethod
    def load_to_gdf_from_memory(gpx_files: list[UploadFile], groups: dict[str, list[str]], toCrs: str) -> gpd.GeoDataFrame:
        gpx_list: list[gpd.GeoDataFrame] = []
        if(gpx_files is None):
            return GdfUtils.create_empty_gdf(
                None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.GROUP.value])
            
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
            
            gpx_gdf[GpxColumns.GROUP.value] = GpxManager.find_group_name(file.filename, groups)
            gpx_list.append(gpx_gdf.to_crs(toCrs))
            
        if (gpx_list):
            gpxs_gdf = GdfUtils.combine_gdfs(gpx_list)
            GdfUtils.remove_columns(gpxs_gdf, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.GROUP.value], neg=True)
            GdfUtils.change_columns_to_categorical(
                gpxs_gdf, [GpxColumns.GROUP.name])
            return gpxs_gdf
        else:
            gpxs_gdf = GdfUtils.create_empty_gdf(
                None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.GROUP.value])
            GdfUtils.change_columns_to_categorical(
                gpxs_gdf, [GpxColumns.GROUP.name])
            return gpxs_gdf
