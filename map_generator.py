import osmium
import pandas as pd
import osmium.geom
from shapely import wkt
import geopandas as gpd
import matplotlib.pyplot as plt
import time
import numpy as np


tags_filters = {
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'leisure': ['park', 'garden', 'golf_course', 'nature_reserve', 'pitch', 'playground','stadium','swimming_pool','sports_centre'],
    'water':True,
    'waterway':True,
    'highway':True
}

color_map_landuse = {
    'forest': {'color': '#9FC98D', 'zindex': 1},
    'farmland': {'color': '#EDEDE0', 'zindex': 2},
    'residential': {'color': '#E2D4AF', 'zindex': 3},
    'industrial': {'color': '#DFDBD1', 'zindex': 4},
    'meadow': {'color': '#B7DEA6', 'zindex': 5},
    'grass': {'color': '#B7DEA6', 'zindex': 6},
    'basin': {'color': '#8FB8DB', 'zindex': 7},
    'salt_pond': {'color': '#8FB8DB', 'zindex': 8},
    'swimming_pool': {'color': '#8FB8DB', 'zindex': 110}
}

color_map_highway = {
    'primary': {'color': '#FDC364', 'zindex': 1},
    'secondary': {'color': '#F7ED60', 'zindex': 2},
    'tertiary': {'color': '#FFFFFF', 'zindex': 3},
    'unclassified': {'color': '#FFFFFF', 'zindex': 4},
    'road': {'color': '#DAD6D2', 'zindex': 5},
    'footway': {'color': 'brown', 'zindex': 6},
    'steps': {'color': 'purple', 'zindex': 7},
    'path': {'color': 'red', 'zindex': 8},
    'residential': {'color': 'blue', 'zindex': 9}
}

color_map_building = {
    'house': {'color': 'grey', 'zindex': 1},
}

# Define attribute mapping with default values
attribute_mapping = {
    'building': (color_map_building, {'color': '#B7DEA6', 'zindex': 0}),
    'water': ({}, {'color': '#8FB8DB', 'zindex': 1}),
    'waterway': ({}, {'color': '#8FB8DB', 'zindex': 2}),
    'leisure': (color_map_landuse, {'color': '#B7DEA6', 'zindex': 10}),
    'natural': (color_map_landuse, {'color': '#B7DEA6', 'zindex': 11}),
    'landuse': (color_map_landuse, {'color': '#EDEDE0', 'zindex': 12}),
    'highway': (color_map_highway, {'color': '#FFFFFF', 'zindex': 13})
}


class Handler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.polygons = []
        self.geom_factory = osmium.geom.WKTFactory()  # Create WKT Factory for geometry conversion
        self.geom_factory_linestring = self.geom_factory.create_linestring
        self.geom_factory_polygon = self.geom_factory.create_multipolygon
        self.wkt_loads_func = wkt.loads
        self.tags = []
    def apply_filters(self,allowed_tags,  tags):
        for key, value in allowed_tags.items():
            if key in tags:
                if value is True:
                    return True
                elif isinstance(value, list):
                    return tags[key] in value
        return False
    def way(self, way):
        # todo filter - bud rozdelit na area nebo pro vsechny
        # if 'highway' in way.tags and (way.tags['highway'] in ['secondary','primary']):
        if self.apply_filters(tags_filters, way.tags):
            wkt_geom = self.geom_factory_linestring(way) 
            shapely_geom = self.wkt_loads_func (wkt_geom)  
            self.polygons.append(shapely_geom)
            self.tags.append(dict(way.tags))  # make copy of tags 
        pass
    def area(self, area):
        if self.apply_filters(tags_filters, area.tags):
            wkt_geom = self.geom_factory_polygon(area) 
            shapely_geom = self.wkt_loads_func (wkt_geom) 
    
            self.polygons.append(shapely_geom)
            self.tags.append(dict(area.tags)) # make copy of tags  
        pass
    def get_gdf(self):
        return gpd.GeoDataFrame(pd.DataFrame(self.tags).assign(geometry=self.polygons), crs="EPSG:4326")
def assign_color(row):
    if isinstance(row, pd.Series):
        for attr_key, (color_key_map, default_color) in attribute_mapping.items():
            if attr_key in row and pd.notna(row[attr_key]):
                item = row[attr_key]
                return color_key_map.get(item,default_color)['color'], color_key_map.get(item,default_color)['zindex']
    return '#EDEDE0', 1
def assign_z(row):
    if isinstance(row, pd.Series):
        return "red"
    return 0
def assign_zs(row):
    if isinstance(row, pd.Series):
        return 2
    return 0


start_time = time.time()  # Record start time

osm_file_parser = Handler()
osm_file_parser.apply_file('output_trebic.osm.pbf')
gdf = osm_file_parser.get_gdf()



gdf[['color', 'zindex']] = pd.DataFrame(gdf.apply(assign_color, axis=1).tolist())

gdf = gdf.sort_values(by='zindex')
print(gdf)

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor('#EDEDE0')
gdf.plot(ax=ax, color=gdf['color'], alpha=1)


end_time = time.time()  # Record end time
elapsed_time = end_time - start_time  # Calculate elapsed time

print(f"Elapsed time: {elapsed_time:.2f} seconds")
plt.show()