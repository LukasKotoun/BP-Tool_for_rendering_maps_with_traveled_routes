import os
import warnings
import unicodedata

import pandas as pd
import geopandas as gpd
from modules.gdf_utils import GdfUtils


class GpxManager:
    def __init__(self, gpx_folder: str, toCrs: str):
        self.gpx_folder: str = gpx_folder
        self.gpxs_gdf = GdfUtils.create_empty_gdf(None, ['geometry', 'fileName', 'folder'])
        self.parse_gpxs_gdf(toCrs)

    def parse_gpxs_gdf(self, toCrs: int) -> gpd.GeoDataFrame:
        gpx_list: list[gpd.GeoDataFrame] = []

        for root, dirs, files in os.walk(self.gpx_folder):
            for file in files:
                if not file.endswith('.gpx'):
                    continue
                # get file path with name of last folder before file
                file_path: str = os.path.join(root, file)
                relative_path: str = os.path.relpath(root, self.gpx_folder)
                last_folder: str = os.path.basename(
                    relative_path) if relative_path != "." else None

                gpx_gdf: gpd.GeoDataFrame = (
                    gpd.read_file(file_path, layer='tracks'))
                gpx_gdf['fileName'] = unicodedata.normalize('NFC',file)
                gpx_gdf['folder'] = unicodedata.normalize('NFC', last_folder) if last_folder else None
                gpx_list.append(gpx_gdf.to_crs(toCrs))

        if (gpx_list):
            # GdfUtils.combine_gdfs
            self.gpxs_gdf = GdfUtils.combine_gdfs(gpx_list)
        else:
            warnings.warn(f"No GPX files found in {self.gpx_folder}")

    def get_gpxs_gdf(self, inCrs: str = None) -> gpd.GeoDataFrame:
        # if (self.gpxs_gdf.empty):
        #     return self.gpxs_gdf

        GdfUtils.change_columns_to_categorical(
            self.gpxs_gdf, ['fileName', 'folder'])
        if (inCrs is None):
            return self.gpxs_gdf
        else:
            return GdfUtils.change_crs(self.gpxs_gdf, inCrs)

    def get_gpxs_gdf_splited(self, inCrs: str = None) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:

        GdfUtils.change_columns_to_categorical(
            self.gpxs_gdf, ['fileName', 'folder'])
        return GdfUtils.filter_rows(self.gpxs_gdf, {'folder': ''}, neg = True, compl=True)
     
