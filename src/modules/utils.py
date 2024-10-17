import math

from config import * 
from common.custom_types import DimensionsTuple, OptDimensionsTuple
class Utils:
    @staticmethod
    def set_orientation(tuple: DimensionsTuple, wanted_orientation: MapOrientation) -> DimensionsTuple:
        if(wanted_orientation == MapOrientation.LANDSCAPE):
            return tuple if tuple[0] > tuple[1] else tuple[::-1]
        #portrait
        return tuple if tuple[0] < tuple[1] else tuple[::-1]
    
    @staticmethod
    def resolve_paper_dimensions(map_dimensions: DimensionsTuple, map_orientaion: MapOrientation,
                           paper_dimensions: OptDimensionsTuple, given_paper_smaller_side = True):
        if(given_paper_smaller_side):
            #given paper size is smaller get map smaller side (coresponding size)
            #if map orientation is landscape smaller size is height
            coresponding_map_side: float = map_dimensions[1] if map_orientaion == MapOrientation.LANDSCAPE else map_dimensions[0] 
        else:
            #given paper size is bigger get map bigger side (coresponding size)
            #if map orientation is landscape bigger size is width
            coresponding_map_side: float = map_dimensions[0] if map_orientaion == MapOrientation.LANDSCAPE else map_dimensions[1] 
            
        other_map_side: float = map_dimensions[1] if math.isclose(coresponding_map_side, map_dimensions[0]) else map_dimensions[0] 
            
        if(paper_dimensions[0] is not None):
            given_paper_side: float = paper_dimensions[0]
        else:
            given_paper_side: float = paper_dimensions[1]
        side_ratio: float = coresponding_map_side/given_paper_side
        resolved_pdf_side: float = other_map_side/side_ratio   
        return (given_paper_side, resolved_pdf_side)
    
        
        
    @staticmethod
    def adjust_paper_dimensions(map_dimensions: DimensionsTuple,
                          paper_dimensions: OptDimensionsTuple = PaperSize.A4.dimensions,
                          given_smaller_paper_side: bool = True,
                          wanted_orientation = MapOrientation.AUTOMATIC) -> DimensionsTuple:
        if map_dimensions[0] >= map_dimensions[1]:
            map_orientaion: MapOrientation = MapOrientation.LANDSCAPE
        else:
            map_orientaion: MapOrientation = MapOrientation.PORTRAIT
        
        if(paper_dimensions.count(None) == 1):
            paper_dimensions = Utils.resolve_paper_dimensions(map_dimensions, map_orientaion, paper_dimensions, given_smaller_paper_side)
        elif(paper_dimensions.count(None) > 1):
            raise ValueError("Only one paper dimension can be None")
        
        if(wanted_orientation in [MapOrientation.LANDSCAPE, MapOrientation.PORTRAIT]):
            paper_dimensions = Utils.set_orientation(paper_dimensions, wanted_orientation)
        else:
            paper_dimensions = Utils.set_orientation(paper_dimensions, map_orientaion)
        return paper_dimensions
    
    @staticmethod
    def get_areas_ratio(bigger_area_dim: DimensionsTuple, bigger_pdf_dim: DimensionsTuple,
                        smaller_area_dim: DimensionsTuple,
                        smaller_pdf_dim: DimensionsTuple) -> DimensionsTuple:
        bigger_width_ratio = bigger_area_dim[0] / bigger_pdf_dim[0]
        bigger_length_ratio = bigger_area_dim[1] / bigger_pdf_dim[1]
        smaller_width_ratio = smaller_area_dim[0] / smaller_pdf_dim[0]
        smaller_length_ratio = smaller_area_dim[1] / smaller_pdf_dim[1]
    
        width_ratio = smaller_width_ratio/bigger_width_ratio
        length_ratio = smaller_length_ratio/bigger_length_ratio
        
        return width_ratio, length_ratio 
