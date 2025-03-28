import osmium
import geopandas as gpd
from osmium.osm.types import TagList, Node, Way, Area

from modules.gdf_utils import GdfUtils
from common.custom_types import WantedCategories
from common.common_helpers import time_measurement

class OsmDataParser():

    def __init__(self, wanted_nodes: WantedCategories, wanted_nodes_from_area: WantedCategories, wanted_ways: WantedCategories, wanted_areas: WantedCategories, 
                 nodes_additional_columns: dict[str] = {}, ways_additional_columns: dict[str] = {}, areas_additional_columns: dict[str] = {}):
        self.wanted_nodes = wanted_nodes
        self.wanted_nodes_from_area = wanted_nodes_from_area
        self.wanted_ways = wanted_ways
        self.wanted_areas = wanted_areas
        
        # merge always wanted columns (map objects) with additions wanted info columns
        self.nodes_columns = list(wanted_nodes.keys()) + \
            nodes_additional_columns
        self.way_columns = list(wanted_ways.keys()) + ways_additional_columns
        self.area_columns = list(wanted_areas.keys()) + areas_additional_columns

    @staticmethod
    def _apply_filters(wanted_features: WantedCategories, tags: TagList):
        """ Checking for wanted features by checking values in tags. Going through wanted_tags and check if map feature is some of wanted map feature.

        Map feature is represented as key (feature category) with value (concrete feature) (e.g. key=landuse and value=forest).  

        Args:
            wanted_features (dict[str, list[str]]): dict with feature category and list of allowed features for this category
            tags (_type_): tags of concrete map feature (area, way, node)

        Returns:
            bool: If find one return true else false
        """
        for features_category, wanted_features_values in wanted_features.items():
            # check if map feature is feature from this features category
            feature: str | None = tags.get(features_category)
            if feature is not None:
                # features_values is empty list => get all from features_category else check if feature is wanted
                if not wanted_features_values or feature in wanted_features_values:
                    return True
        # map feature is not in wanted features
        return False


    # @time_measurement("gdf creating")
    def create_gdf(self, file_name: str, fromCrs: str, toCrs: str | None = None) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
        
        class ElementsFilter():
            def __init__(self, outer_self):
                self.outer_self = outer_self
                
            def node(self, node: Node):
                return not (OsmDataParser._apply_filters(self.outer_self.wanted_nodes, node.tags)) #and OsmDataParser._apply_filters_not_allowed(self.outer_self.unwanted_nodes_tags, node.tags))
            
            def way(self, way: Way):
                return not (OsmDataParser._apply_filters(self.outer_self.wanted_ways, way.tags)) #and OsmDataParser._apply_filters_not_allowed(self.outer_self.unwanted_ways_tags, way.tags))
            
            def area(self, area: Area):
                return not (OsmDataParser._apply_filters(self.outer_self.wanted_areas, area.tags)) #and OsmDataParser._apply_filters_not_allowed(self.outer_self.unwanted_areas_tags, area.tags))
 
        if (self.wanted_nodes):
            fp_node: osmium.FileProcessor = osmium.FileProcessor(file_name, osmium.osm.NODE)\
                .with_filter(osmium.filter.EmptyTagFilter())\
                .with_filter(osmium.filter.KeyFilter(*self.wanted_nodes.keys()))\
                .with_filter(ElementsFilter(self))\
                .with_filter(osmium.filter.GeoInterfaceFilter(tags=self.nodes_columns))
            nodes_gdf = GdfUtils.create_gdf_from_file_processor(fp_node, fromCrs)
        else:
            nodes_gdf = GdfUtils.create_empty_gdf(fromCrs)
            
        if (self.wanted_nodes_from_area):
            fp_node_from_area: osmium.FileProcessor = osmium.FileProcessor(file_name)\
                .with_areas()\
                .with_filter(osmium.filter.EmptyTagFilter())\
                .with_filter(osmium.filter.EntityFilter(osmium.osm.AREA))\
                .with_filter(osmium.filter.KeyFilter(*self.wanted_nodes_from_area.keys()))\
                .with_filter(ElementsFilter(self))\
                .with_filter(osmium.filter.GeoInterfaceFilter(tags=self.nodes_columns))
            nodes_from_area_gdf = GdfUtils.create_gdf_from_file_processor(fp_node_from_area, fromCrs)
        else:
            nodes_from_area_gdf = GdfUtils.create_empty_gdf(fromCrs)
        nodes_gdf = GdfUtils.combine_gdfs([nodes_gdf,  GdfUtils.create_points_from_polygons_gdf(nodes_from_area_gdf)])


        if (self.wanted_ways):
            fp_way: osmium.FileProcessor = osmium.FileProcessor(file_name)\
                .with_locations()\
                .with_filter(osmium.filter.EmptyTagFilter())\
                .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
                .with_filter(osmium.filter.KeyFilter(*self.wanted_ways.keys()))\
                .with_filter(ElementsFilter(self))\
                .with_filter(osmium.filter.GeoInterfaceFilter(tags=self.way_columns))
            ways_gdf = GdfUtils.create_gdf_from_file_processor(fp_way, fromCrs)
        else:
            ways_gdf = GdfUtils.create_empty_gdf(fromCrs)

        if (self.wanted_areas):
            fp_area: osmium.FileProcessor = osmium.FileProcessor(file_name)\
                .with_areas()\
                .with_filter(osmium.filter.EmptyTagFilter())\
                .with_filter(osmium.filter.EntityFilter(osmium.osm.AREA))\
                .with_filter(osmium.filter.KeyFilter(*self.wanted_areas.keys()))\
                .with_filter(ElementsFilter(self))\
                .with_filter(osmium.filter.GeoInterfaceFilter(tags=self.area_columns))
            areas_gdf = GdfUtils.create_gdf_from_file_processor(fp_area, fromCrs)
        else:
            areas_gdf = GdfUtils.create_empty_gdf(fromCrs)
            
        
        GdfUtils.change_columns_to_categorical(
            nodes_gdf, [key for key, _ in self.wanted_nodes.items()])
        GdfUtils.change_columns_to_categorical(
            ways_gdf, [key for key, _ in self.wanted_ways.items()])
        GdfUtils.change_columns_to_categorical(
            areas_gdf, [key for key, _ in self.wanted_areas.items()])
        #print(f"nodes: {nodes_gdf.memory_usage(deep=True).sum()}, ways: {ways_gdf.memory_usage(deep=True).sum()}, areas: {areas_gdf.memory_usage(deep=True).sum()}, combined: {nodes_gdf.memory_usage(deep=True).sum() + ways_gdf.memory_usage(deep=True).sum() + areas_gdf.memory_usage(deep=True).sum()}")

        if (toCrs is None):
            return nodes_gdf, ways_gdf, areas_gdf
        else:
            return nodes_gdf.to_crs(toCrs), ways_gdf.to_crs(toCrs), areas_gdf.to_crs(toCrs)
