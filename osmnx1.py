import osmnx as ox
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

place_name = "Třebíč, Czech Republic"

gdf = ox.geocode_to_gdf(place_name)
bbox = gdf.unary_union.envelope.bounds

tags = {
    'landuse': ['forest', 'residential', 'commercial', 'retail', 'industrial', 'farmland', 'meadow', 'grass'],
    'natural': ['bay','beach','water'],
    'leisure': ['park', 'garden', 'golf_course', 'nature_reserve', 'pitch', 'playground','stadium','swimming_pool','sports_centre'],
    'water': True,
    'waterway': True,
    'highway': True
}




detailed_gdf = ox.features_from_bbox(north=bbox[3], south=bbox[1], east=bbox[2], west=bbox[0], tags=tags)
# ways ={ 'highway':['primary','secondary','tertiary','unclassified','road','footway','steps','path','residential',"road"]
# }
# ways ={'highway':True}
# highways_gdf = ox.features_from_bbox(north=bbox[3], south=bbox[1], east=bbox[2], west=bbox[0], tags=ways)


#remove
detailed_gdf = detailed_gdf[detailed_gdf.geometry.geom_type.isin(['LineString', 'MultiLineString', 'Polygon', 'MultiPolygon'])]

roads = detailed_gdf[detailed_gdf.geometry.type.isin(['LineString','MultiLineString'])] # Filter for lines (roads/highways)
landuse = detailed_gdf[detailed_gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])]  # Filter for polygons (landuse areas)

color_map_landuse = {
    'forest': '#9FC98D',
    'farmland': '#EDEDE0',
    'residential': '#E2D4AF',
    'industrial': '#DFDBD1',
    'meadow': '#B7DEA6',
    'grass': '#B7DEA6',
    'basin': '#8FB8DB',
    'salt_pond': '#8FB8DB',
    'swimming_pool':'#8FB8DB'
}
color_map_highway = {
    'primary': '#FDC364',
    'secondary': '#F7ED60',
    'tertiary': '#FFFFFF',
    'unclassified': '#FFFFFF',
    'road': '#DAD6D2',
    'footway': 'brown',
    'steps': 'purple',
    'path': 'red',
    'residential': "blue"
}
color_map_building = {
    'house': 'grey',
}
road_width_mapping = {
    'primary': 1.5,    # Primary roads
    'secondary': 1.3,  # Secondary roads
    'tertiary': 0.7,   # Tertiary roads
    'residential': 0.5, # Residential roads
    'service': 0.3     # Smallest for service roads
}
attribute_mapping = {
            'building': (color_map_building, '#EDEDE0'),
            'water': ({}, '#8FB8DB'),
            'waterway': ({}, '#8FB8DB'),
            'leisure': (color_map_landuse, '#B7DEA6'),
            'natural': (color_map_landuse, '#B7DEA6'),
            'landuse': (color_map_landuse, '#EDEDE0'),
            'highway': (color_map_highway, '#FFFFFF')
        }


# gdf[columns] = pd.DataFrame(gdf.apply(assign_attributes, axis=1).tolist())

def assign_color(row):
    if isinstance(row, pd.Series):
        for attr_key, (color_key_map, default_color) in attribute_mapping.items():
            if attr_key in row and pd.notna(row[attr_key]):
                return color_key_map.get(row[attr_key], default_color) 
    return '#EDEDE0'

def assign_way_width(row):
    if isinstance(row, pd.Series):
        if 'highway' in row and pd.notna(row['highway']):
            return road_width_mapping.get(row['highway'], 0.5)
    return 0.5
gdf['color'] = gdf.apply(assign_color, axis=1)
landuse['linewidth'] = landuse.apply(assign_way_width, axis=1)

roads['color'] = roads.apply(assign_color, axis=1)
roads['linewidth'] = roads.apply(assign_way_width, axis=1)
# highways_gdf['color'] = highways_gdf.apply(assign_color, axis=1)

minx, miny, maxx, maxy = detailed_gdf.total_bounds

fig, ax = plt.subplots(figsize=(10, 10))
fig_width, fig_height = fig.get_size_inches()

#default bg color
ax.set_facecolor('#EDEDE0')
# paths = highways_gdf[highways_gdf['highway'].isin(s)]
# ot = highways_gdf[~highways_gdf['highway'].isin(s)]
extent_width = bbox[2] - bbox[0]
extent_width2 = bbox[3] - bbox[1]
extent_width = max(extent_width,extent_width2)
print(extent_width)
landuse.plot(ax=ax, alpha=1,linestyle='', linewidth = landuse['linewidth'], color=landuse['color'])
roads.plot(ax=ax, alpha=1, linestyle='-' , linewidth = 0.05/(extent_width), color=roads['color'])



#paths.plot(ax=ax, linestyle='--', color=highways_gdf['color'])
#ot.plot(ax=ax, color=highways_gdf['color'])
#normal

#detailed_gdf.plot(ax=ax, edgecolor='black', alpha=0.5, color=detailed_gdf['color'])


# mask specific area
mask = gdf.unary_union
maskgdf = gpd.GeoDataFrame(geometry=[mask], crs=gdf.crs)

#defailt bg color
#maskgdf.plot(ax=ax, color='#EDEDE0', edgecolor='none')

#filtered_gdf = detailed_gdf.clip(mask)
#filtered_gdf.plot(ax=ax, alpha=1, color=filtered_gdf['color'])


#border around area
maskgdf.boundary.plot(ax=ax, color='red', linewidth=2)

# Optionally, set title and labels
ax.set_title('Detailed Data for Horní Vilemovice')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
pdf_filename = 'map_export2.pdf'
plt.savefig(pdf_filename, format='pdf', bbox_inches='tight')

# Show the plot
plt.show()

#! pristup 2 - 0.93

# def assign_color(row):
#     if isinstance(row, pd.Series):
#         for attr_key, (color_key_map, default_color) in attribute_mapping.items():
#             if attr_key in row and pd.notna(row[attr_key]):
#                 return color_key_map.get(row[attr_key], default_color)
#     return '#EDEDE0'
    
    

# def assign_color2(row):
#     if isinstance(row, pd.Series):
#         for attr_key, (color_key_map, default_color) in attribute_mapping.items():
#             if attr_key in row and pd.notna(row[attr_key]):
#                 return color_key_map.get(row[attr_key], default_color)
#     return '#EDEDE0'
    
# gdf['color']= gdf.apply(assign_color, axis = 1)

# gdf['color2']= gdf.apply(assign_color2, axis = 1)

#!pristup 3 - 1.04
# def assign_color(row):
#     if isinstance(row, pd.Series):
#         for attr_key, (color_key_map, default_color) in attribute_mapping.items():
#             if attr_key in row and pd.notna(row[attr_key]):
#                 return color_key_map.get(row[attr_key], default_color),5
#     return '#EDEDE0',7
    

# gdf[['color', 'test']] = gdf.apply(lambda row: pd.Series(assign_color(row)), axis=1)
