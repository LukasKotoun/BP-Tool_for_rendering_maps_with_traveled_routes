import os

import pandas as pd
import geopandas as gpd

class GpxProcesser:
    def __init__(self, gpx_folder):
        self.gpx_folder = gpx_folder
        
        #todo add reqired att
    def get_gpxs_gdf(self, epgs_number):
        gpx_list = []
        for file in os.listdir(self.gpx_folder):
            if not file.endswith('.gpx'):
                continue
            gpx_gdf = gpd.read_file(os.path.join(self.gpx_folder,file), layer='tracks', crs=f"EPSG:{epgs_number}")
            gpx_gdf['name'] = file
            gpx_list.append(gpx_gdf)
        return gpd.GeoDataFrame(pd.concat(gpx_list, ignore_index=True), crs=f"EPSG:{epgs_number}")
