import warnings

import geopandas as gpd
from fastapi import UploadFile

from modules.gdf_utils import GdfUtils
from common.map_enums import GpxColumns


class GpxManager:

    @staticmethod
    def get_empty_gpx_gdf() -> gpd.GeoDataFrame:
        return GdfUtils.create_empty_gdf(
            None, ['geometry', GpxColumns.FILE_NAME.value, GpxColumns.CATEGORY.value])
        
   
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
