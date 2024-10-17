import os

import pandas as pd
import geopandas as gpd

class GpxProcesser:
    def __init__(self, gpx_folder: str):
        self.gpx_folder: str = gpx_folder
        
        #todo add reqired att
    def get_gpxs_gdf(self, epgs: int) -> gpd.GeoDataFrame:
        gpx_list: list[gpd.GeoDataFrame] = []
        for file in os.listdir(self.gpx_folder):
            if not file.endswith('.gpx'):
                continue
            gpx_gdf: gpd.GeoDataFrame = gpd.read_file(os.path.join(self.gpx_folder,file), layer='tracks', crs=f"EPSG:{epgs}")
            gpx_gdf['name'] = file
            gpx_list.append(gpx_gdf)
        return gpd.GeoDataFrame(pd.concat(gpx_list, ignore_index=True), crs=f"EPSG:{epgs}")
