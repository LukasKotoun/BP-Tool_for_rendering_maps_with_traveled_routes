from typing import Tuple
import math
from config import * 

class Utils:
    @staticmethod
    def set_orientation(tuple: Tuple[float,float], wanted_orientation: MapOrientation) -> Tuple[float,float]:
        if(wanted_orientation == MapOrientation.LANDSCAPE):
            return tuple if tuple[0] > tuple[1] else tuple[::-1]
        #portrait
        return tuple if tuple[0] < tuple[1] else tuple[::-1]
    
    @staticmethod
    def resolve_paper_dimensions(map_dimensions: Tuple[float,float], map_orientaion: MapOrientation,
                           paper_dimensions: Tuple[float,float], given_paper_smaller_side = True):
        if(given_paper_smaller_side):
            #given paper size is smaller get map smaller side (coresponding size)
            #if map orientation is landscape smaller size is height
            coresponding_map_side = map_dimensions[1] if map_orientaion == MapOrientation.LANDSCAPE else map_dimensions[0] 
        else:
            #given paper size is bigger get map bigger side (coresponding size)
            #if map orientation is landscape bigger size is width
            coresponding_map_side = map_dimensions[0] if map_orientaion == MapOrientation.LANDSCAPE else map_dimensions[1] 
            
        other_map_side = map_dimensions[1] if math.isclose(coresponding_map_side, map_dimensions[0]) else map_dimensions[0] 
            
        if(paper_dimensions[0] is not None):
            given_paper_side = paper_dimensions[0]
        else:
            given_paper_side = paper_dimensions[1]
        side_ratio = coresponding_map_side/given_paper_side
        resolved_pdf_side = other_map_side/side_ratio   
        return (given_paper_side, resolved_pdf_side)
    
        
        
    @staticmethod
    def adjust_paper_dimensions(map_dimensions: Tuple[float,float],
                          paper_dimensions: Tuple[float,float] = PaperSize.A4.dimensions,
                          given_smaller_paper_side: bool = True,
                          wanted_orientation = MapOrientation.AUTOMATIC) -> Tuple[float,float]:
        if map_dimensions[0] >= map_dimensions[1]:
            map_orientaion: MapOrientation = MapOrientation.LANDSCAPE
        else:
            map_orientaion: MapOrientation = MapOrientation.PORTRAIT
        
        if(paper_dimensions.count(None) == 1):
            paper_dimensions = Utils.resolve_paper_dimensions(map_dimensions, map_orientaion, paper_dimensions, given_smaller_paper_side)
        elif(paper_dimensions.count(None) > 1):
            raise ValueError("Only one paper dimension can be None")
        
        
        if(wanted_orientation == MapOrientation.AUTOMATIC):
            paper_dimensions = Utils.set_orientation(paper_dimensions, map_orientaion)
        elif(wanted_orientation in [MapOrientation.LANDSCAPE, MapOrientation.PORTRAIT]):
            paper_dimensions = Utils.set_orientation(paper_dimensions, wanted_orientation)
        return paper_dimensions
    
    @staticmethod
    def get_areas_ratio(bigger_area_dim, bigger_pdf_dim, smaller_area_dim, smaller_pdf_dim):
        bigger_width_ratio = bigger_area_dim[0] / bigger_pdf_dim[0]
        bigger_length_ratio = bigger_area_dim[1] / bigger_pdf_dim[1]
        smaller_width_ratio = smaller_area_dim[0] / smaller_pdf_dim[0]
        smaller_length_ratio = smaller_area_dim[1] / smaller_pdf_dim[1]
    
        width_ratio = smaller_width_ratio/bigger_width_ratio
        length_ratio = smaller_length_ratio/bigger_length_ratio
        
        return width_ratio, length_ratio 
