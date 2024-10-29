import tempfile
import subprocess
from geopandas import GeoDataFrame

class OsmDataPreprocessor:
    #, area: Union[str, List[Tuple[float, float]]]
    def __init__(self, osm_input_file: str, osm_output_file : str = None):
        self.osm_input_file: str = osm_input_file # Can be a string (place name) or a list of coordinates
        self.osm_output_file = osm_output_file

    def extract_area(self, reqired_area_gdf: GeoDataFrame) -> str:
        #todo check if osm output file does exist

            temp_geojson_path = self.create_tmp_geojson(reqired_area_gdf)
            command = [
                'osmium', 'extract',
                '--strategy', 'smart',
                '-p', temp_geojson_path,
                self.osm_input_file,
                '-o', self.osm_output_file
            ]
            subprocess.run(command, check=True)
            return self.osm_output_file

        
    def create_tmp_geojson(self, reqired_area_gdf: GeoDataFrame) -> str:
        #create tmp file for osmium extraction
        with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as temp_geojson:
            reqired_area_gdf.to_file(temp_geojson.name, driver="GeoJSON")
            return temp_geojson.name