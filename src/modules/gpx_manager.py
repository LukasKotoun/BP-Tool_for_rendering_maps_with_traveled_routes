import os
import warnings
import unicodedata

import pandas as pd
import geopandas as gpd


class GpxManager:
    def __init__(self, gpx_folder: str, epsg: int):
        self.gpx_folder: str = gpx_folder
        self.gpxs_gdf = gpd.GeoDataFrame()
        self.parse_gpxs_gdf(epsg)
        
    def parse_gpxs_gdf(self, toEpsg: int) -> gpd.GeoDataFrame:
        gpx_list: list[gpd.GeoDataFrame] = []
        
        for root, dirs, files in os.walk(self.gpx_folder):
            for file in files:
                if not file.endswith('.gpx'):
                    continue
                # get file path with name of last folder before file
                file_path: str = os.path.join(root, file)
                relative_path: str = os.path.relpath(root, self.gpx_folder)
                last_folder = os.path.basename(relative_path) if relative_path != "." else ""
                gpx_gdf: gpd.GeoDataFrame = (gpd.read_file(file_path, layer='tracks'))
                gpx_gdf['fileName'] = file
                gpx_gdf['folder'] = unicodedata.normalize('NFC', last_folder)
                gpx_list.append(gpx_gdf.to_crs(epsg=toEpsg))
            
        if(gpx_list):
            self.gpxs_gdf = gpd.GeoDataFrame(pd.concat(gpx_list, ignore_index=True), crs=f"EPSG:{toEpsg}")
        else:
            warnings.warn(f"No GPX files found in {self.gpx_folder}")
    

    def get_gpxs_gdf(self, toEpsg: int = None) -> gpd.GeoDataFrame:
        if (self.gpxs_gdf.empty):
            return self.gpxs_gdf
        
        for column in ['name', 'folder']:
            if (column in self.gpxs_gdf):
                self.gpxs_gdf[column] = self.gpxs_gdf[column].astype("category")
        if (toEpsg is None):
            return self.gpxs_gdf
        else:
            return self.gpxs_gdf.to_crs(epsg=toEpsg)
