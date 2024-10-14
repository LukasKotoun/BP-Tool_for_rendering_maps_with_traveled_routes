from typing import Tuple

from config import * 

class Utils:
    @staticmethod
    def set_orientation(tuple:Tuple[float,float], wanted_orientation: MapOrientation) -> Tuple[float,float]:
        if(wanted_orientation == MapOrientation.LANDSCAPE):
            return tuple if tuple[0] > tuple[1] else tuple[::-1]
        #portrait
        return tuple if tuple[0] < tuple[1] else tuple[::-1]
    
    @staticmethod
    def get_paper_size_mm( map_orientaion,paperSize :PaperSize = PaperSize.A4, wanted_orientation = MapOrientation.AUTOMATIC):
        paper_size = paperSize.dimensions
        if(wanted_orientation == MapOrientation.AUTOMATIC):
            return Utils.set_orientation(paper_size, map_orientaion)
        elif(wanted_orientation in [MapOrientation.LANDSCAPE, MapOrientation.PORTRAIT]):
            return Utils.set_orientation(paper_size,wanted_orientation)
        return paper_size
    
    @staticmethod
    def get_areas_ratio(bigger_area_dim, bigger_pdf_dim, smaller_area_dim, smaller_pdf_dim):
        bigger_width_ratio = bigger_area_dim[0] / bigger_pdf_dim[0]
        bigger_length_ratio = bigger_area_dim[1] / bigger_pdf_dim[1]
        smaller_width_ratio = smaller_area_dim[0] / smaller_pdf_dim[0]
        smaller_length_ratio = smaller_area_dim[1] / smaller_pdf_dim[1]
    
        width_ratio = smaller_width_ratio/bigger_width_ratio
        length_ratio = smaller_length_ratio/bigger_length_ratio
        
        return width_ratio, length_ratio 
