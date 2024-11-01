import math
from shapely.geometry import Point

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
    def calc_zoom_for_smaller_area(bigger_area_dim: DimensionsTuple, bigger_area_pdf_dim: DimensionsTuple,
                        smaller_area_dim: DimensionsTuple,
                        smaller_area_pdf_dim: DimensionsTuple) -> DimensionsTuple:
        """Calculate ares ratio relative to pdf size coresponding to areas.
            
            Calculate the ratio of width and length between the smaller and larger area
            based on their ratio to the corresponding dimensions of the PDF to which they are to be rendered.
            Useful for calculcating how should be smaller area in preview zoomed 

        Args:
            bigger_area_dim (DimensionsTuple): (width, height)
            bigger_area_pdf_dim (DimensionsTuple): (width, height)
            smaller_area_dim (DimensionsTuple): (width, height)
            smaller_area_pdf_dim (DimensionsTuple): (width, height)

        Returns:
            DimensionsTuple: relative ratio area dimension (width, height) 
            if is <1 bigger area will have smaller detail - need unzoom in smaler area
            if is >1 bigger area will have bigger detail - need zoom in smaler area
        """

        # calc level of detail - bigger number => can have more details
        bigger_area_detail_level = Utils.calc_ratios(bigger_area_pdf_dim, bigger_area_dim)
        # calc level of detail - bigger number => can have more details
        smaller_area_detail_level = Utils.calc_ratios(smaller_area_pdf_dim, smaller_area_dim)
        
        # if bigger area have bigger detail level than smaller area => need zoom (to increase detail for preview)  on smaller area
        # if smaller area have bigger detail level than bigger area => need unzoom (to decrease detail for preview) on smaller area
        width_zoom = bigger_area_detail_level[0] / smaller_area_detail_level[0]
        height_zoom = bigger_area_detail_level[1] / smaller_area_detail_level[1] 
        
        return width_zoom, height_zoom 
    @staticmethod
    def calc_ratios(area1: DimensionsTuple, area2: DimensionsTuple) -> DimensionsTuple:
        #calculate the ratio area1 to area2 
        width_ratio = area1[0] / area2[0]
        height_ratio = area1[1] / area2[1]
        return width_ratio, height_ratio
       
    #funkce která na zakladě střed, a pomeru velikosti vetší oblasti a papíru zjistí potřebnou velikost oblasti a vrátí ji jako polygon 

    @staticmethod
    def calc_bounds_to_fill_paper(center_point: Point, pdf_dim: DimensionsTuple,
                                  bigger_area_dim: DimensionsTuple, bigger_pdf_dim: DimensionsTuple) -> BoundsDict:
        area_to_pdf_ratio = Utils.calc_ratios(bigger_pdf_dim, bigger_area_dim)
         
        # expressed coefficient from the equation pdf_dim / (center_point * (1+coefficient) - center_point * (1-coefficient)) = bigger_pdf_dim / bigger_area_dim
        # where bigger_pdf_dim / bigger_area_dim is area_to_pdf_ratio, (center_point * (1+coefficient) - center_point * (1-coefficient)) is area_dim (length of height or width)
        width_coefficient = pdf_dim[0] / (2 * center_point.x * area_to_pdf_ratio[0])
        height_coefficient = pdf_dim[1] / (2 * center_point.y * area_to_pdf_ratio[1])

        return{
            WorldSides.WEST: center_point.x * (1 - width_coefficient),
            WorldSides.SOUTH: center_point.y * (1 - height_coefficient),
            WorldSides.EAST:  center_point.x * (1 + width_coefficient),
            WorldSides.NORTH: center_point.y * (1 + height_coefficient)
        }
     
    @staticmethod
    def calc_map_object_scaling_factor(map_dimensions_m, paper_dimensions_mm):
        """_summary_

        Args:
            map_dimensions_m (_type_): _description_
            paper_dimensions_mm (_type_): _description_

        Returns:
            _type_: _description_
        """

        map_scaling_factor = (map_dimensions_m[0] + map_dimensions_m[1]) 
        paper_scaling_factor = (paper_dimensions_mm[0] + paper_dimensions_mm[1])

        return paper_scaling_factor / map_scaling_factor
        