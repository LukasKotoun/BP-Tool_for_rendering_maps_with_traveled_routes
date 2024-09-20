import osmium
import pandas as pd
from shapely import wkt
import geopandas as gpd
import matplotlib.pyplot as plt
import time
import numpy as np

#------------cons--------------
WAYS_RATIO_TO_MAP_SIZE = 0.05
DEFAULT_MAP_BG_COLOR = '#EDEDE0'
#todo default values ... z index...

#------------settings--------------

way_filters = {
    'waterway':True,
    'highway':True
}

area_filters = {
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'leisure': ['park', 'pitch', 'garden', 'golf_course', 'nature_reserve', 'playground', 'stadium','swimming_pool', 'sports_centre'],
    'water': True,
}

attribute_map_landuse = {
    'forest': {'color': '#9FC98D', 'zindex': None},
    'farmland': {'color': '#EDEDE0', 'zindex': None},
    'residential': {'color': '#E2D4AF', 'zindex': None},
    'industrial': {'color': '#DFDBD1', 'zindex': None},
    'basin': {'color': '#8FB8DB', 'zindex': 1},
    'salt_pond': {'color': '#8FB8DB', 'zindex': 1},
    'swimming_pool': {'color': '#8FB8DB', 'zindex': 1}   
}

attribute_map_leisure = {
    'swimming_pool': {'color': '#8FB8DB', 'zindex': 1},  
    'golf_curse': {'color': '#DCE9B9', 'zindex': 1},    
    'playground': {'color': '#DCE9B9', 'zindex': 1},  
    'pitch': {'color': '#DCE9B9', 'zindex': 2},  
    'sports_centre': {'color': '#E2D4AF', 'zindex': 1},  
}
	
attribute_map_highway = {
    'highway': {'color': '#FDC364', 'zindex': 7},
    'trunk': {'color': '#FDC364', 'zindex': 6},
    'primary': {'color': '#FDC364', 'zindex': 5},
    'secondary': {'color': '#F7ED60', 'zindex': 4},
    'tertiary': {'color': '#FFFFFF', 'zindex': 3},
    'unclassified': {'color': '#FFFFFF', 'zindex': None},
    'road': {'color': '#DAD6D2', 'zindex': None},
    'footway': {'color': 'brown', 'zindex': None},
    'steps': {'color': 'purple', 'zindex': None},
    'path': {'color': 'red', 'zindex': None},
    'residential': {'color': 'blue', 'zindex': None}
}

attribute_map_building = {
    'house': {'color': 'grey', 'zindex': 1},
}


# Define attribute mapping with default values
attribute_mapping = {
    'building': (attribute_map_building, {'color': '#B7DEA6', 'zindex': 1}),
    'water': ({}, {'color': '#8FB8DB', 'zindex': 1}),
    'waterway': ({}, {'color': '#8FB8DB', 'zindex': 2}),
    'leisure': (attribute_map_leisure, {'color': '#EDEDE0', 'zindex': 0}),
    'natural': (attribute_map_landuse, {'color': '#B7DEA6', 'zindex': 0}),
    'landuse': (attribute_map_landuse, {'color': '#EDEDE0', 'zindex': 0}),
    'highway': (attribute_map_highway, {'color': '#FFFFFF', 'zindex': 2})
}

road_width_mapping = {
    'primary': 1.5,    # Primary roads
    'secondary': 1.3,  # Secondary roads
    'tertiary': 0.7,   # Tertiary roads
    'residential': 0.5, # Residential roads
    'service': 0.3     # Smallest for service roads
}

#------------settings end--------------

class Handler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.polygons = []
        self.geom_factory = osmium.geom.WKTFactory()  # Create WKT Factory for geometry conversion
        self.geom_factory_linestring = self.geom_factory.create_linestring
        self.geom_factory_polygon = self.geom_factory.create_multipolygon
        self.wkt_loads_func = wkt.loads
        
        
    def apply_filters(self,allowed_tags,  tags):
        for key, value in allowed_tags.items():
            if key in tags:
                if value is True:
                    return True
                elif isinstance(value, list):
                    return tags[key] in value
        return False
    
    
    def way(self, way):
        # todo filter - bud rozdelit na area a way a nebo pro vsechny
        if self.apply_filters(way_filters, way.tags):
            wkt_geom = self.geom_factory_linestring(way) 
            shapely_geom = self.wkt_loads_func (wkt_geom)  
            self.polygons.append(shapely_geom)
            self.tags.append(dict(way.tags))  # make copy of tags 
        pass
    
    
    def area(self, area):
            if self.apply_filters(area_filters, area.tags):
                wkt_geom = self.geom_factory_polygon(area) 
                shapely_geom = self.wkt_loads_func (wkt_geom) 

                self.polygons.append(shapely_geom)
                self.tags.append(dict(area.tags)) # make copy of tags  
            pass
    
    
    def get_gdf(self):
        return gpd.GeoDataFrame(pd.DataFrame(self.tags).assign(geometry=self.polygons), crs="EPSG:4326")


def assign_attributes(row):
    if isinstance(row, pd.Series):
        result = {}
        for attr_key, (attribute_map, default_values) in attribute_mapping.items():
            if attr_key in row and pd.notna(row[attr_key]):
                item = attribute_map.get(row[attr_key], default_values) #retrieve record for a specific key (e.g. landues) and value (e.g. forest) combination in the map or retrieve the default value for that key.
                for key, default_value in default_values.items(): # select individual values from the record or default values if there are none in the record
                    value = item.get(key)
                    result[key] = value if value is not None else default_value
                return result
    return '#EDEDE0', 0 # todo 

start_time = time.time()  # Record start time

osm_file_parser = Handler()
osm_file_parser.apply_file('output_trebic.osm.pbf')
gdf = osm_file_parser.get_gdf()

#add attributes to gdf
#todo asing attribut func
attributes = gdf.apply(assign_attributes, axis=1).tolist()
gdf = gdf.join(pd.DataFrame(attributes, index=gdf.index))

#todo print funct 
gdf = gdf.sort_values(by='zindex')

gdf_bounds = dict(zip(['west', 'north', 'east', 'south'], gdf.total_bounds))
latitude = gdf_bounds['east'] - gdf_bounds['west']
longitude = gdf_bounds['north'] - gdf_bounds['south']
map_size = max(latitude, longitude)

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor(DEFAULT_MAP_BG_COLOR)
gdf.plot(ax=ax, color=gdf['color'],linewidth = WAYS_RATIO_TO_MAP_SIZE/map_size, alpha=1)
# gdf.plot(ax=ax, color=gdf['color'], alpha=1)

end_time = time.time()  # Record end time
elapsed_time = end_time - start_time  # Calculate elapsed time

print(gdf)
pdf_filename = 'trebic_map.pdf'
plt.savefig(pdf_filename, format='pdf', bbox_inches='tight')


print(f"Elapsed time: {elapsed_time:.2f} seconds")
# plt.show()