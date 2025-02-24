from common.map_enums import StyleKey

# todo add functions to check for color and linestyle validity


class ReceivedStructureProcessor:

    # def validate_and_convert_paper_dimensions
    @staticmethod
    def map_dict_keys(input_dict, mapping_dict):
        """Replace dictionary keys with values in mapping_dict if in mapping_dict, otherwise keep them unchanged."""
        return {mapping_dict.get(key, key): value for key, value in input_dict.items()}
    
    @staticmethod
    def validate_and_convert_area_cordinates(polygon_points: list[list[int | float]]):
        """Validate and convert the area cordinates.
        Validate if polygon_points are in format [[x,y], [x,y], [x,y]] or [(x,y), (x,y), (x,y)]
        and convert to [(x,y), (x,y), (x,y)]

        Args:
            cordinates (list[list[int | float]]): list of points in format [[x,y], [x,y], [x,y]] or [(x,y), (x,y), (x,y)]

        Raises:
            ValueError: If polygon have less than 3 points
            ValueError: If point is not a list or tuple
            ValueError: If point is not have exactly 2 cordinates
            ValueError: If cordinates are non-number elements

        Returns:
            list[tuple[int|float]]: [(x,y), (x,y), (x,y)]
        """
        result = []
        if (len(polygon_points) <= 2):
            raise ValueError(f"Area cordinates must have at least 3 points")
        for point in polygon_points:
            if not isinstance(point, (list, tuple)):
                raise ValueError(f"Some point is not a list or tuple")
            if len(point) != 2:
                raise ValueError(f"Some point not have exactly 2 cordinates")
            if not all(isinstance(num, (int, float)) for num in point):
                raise ValueError(f"Some cordinates area non-number elements")
            result.append(tuple(point))
        return result

    @staticmethod
    def check_dict_values_and_types(dict: dict, allowed_keys_and_types):
        if dict.keys() - allowed_keys_and_types.keys() or allowed_keys_and_types.keys() - dict.keys():
                return False
        for key, type_ in allowed_keys_and_types.items():
                if not isinstance(dict[key], type_):
                    return False
        return True
    
    @staticmethod
    def validate_and_convert_areas_strucutre(areas_structures: list[dict], allowed_keys_and_types: dict[str, type], key_with_area = "area"):
        if not isinstance(areas_structures, list):
            raise ValueError("Input must be a list.")

        edited_data = []
        for  item in areas_structures:
            if not isinstance(item, dict):
                raise ValueError(f"Items in area list must be dictionary")
            
            if(not ReceivedStructureProcessor.check_dict_values_and_types(item, allowed_keys_and_types)):
                raise ValueError("some keys are not allowed or have wrong types")

            new_item = item.copy()
            
            # Validate and convert the area.
            area_val = new_item[key_with_area]
            if isinstance(area_val, str):
                pass
            elif isinstance(area_val, list):
                new_item[key_with_area] = ReceivedStructureProcessor.validate_and_convert_area_cordinates(area_val)
            else:
                raise ValueError(
                    f"{key_with_area} must be a string or a list of lists/tuples"
                )
            
            edited_data.append(new_item)

        return edited_data

    # in this function create maping of style names to style keys
    # also add mapping of specific values of keys to specific values
    @staticmethod
    def validate_and_convert_styles(styles: list, style_names_mapping, style_values_mapping):
        pass