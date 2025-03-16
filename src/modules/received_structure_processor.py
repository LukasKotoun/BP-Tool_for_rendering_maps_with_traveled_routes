from common.map_enums import Style
from typing import Dict, List, Union, Any, Optional

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
    def check_dict_values_and_types(values_dict: dict, allowed_keys_and_types: dict[str, type], must_have_none: bool = False):
        allowed_keys = set(allowed_keys_and_types.keys())
        if must_have_none:
            required_keys = set(allowed_keys_and_types.keys())
        else:
            required_keys = {
                k for k, (_, required) in allowed_keys_and_types.items() if required}

        # Extra keys not allowed.
        if set(values_dict.keys()) - allowed_keys:
            return False

        # All required keys are present.
        if not required_keys.issubset(values_dict.keys()):
            return False

        # Check types.
        for key, (expected_type, _) in allowed_keys_and_types.items():
            if key in values_dict and expected_type is not None:
                if not isinstance(values_dict[key], expected_type):
                    return False
        return True

    @staticmethod
    def validate_and_convert_areas_strucutre(areas_structures: list[dict], allowed_keys_and_types: dict[str, type], key_with_area):
        if not isinstance(areas_structures, list):
            raise ValueError("Input must be a list.")

        edited_data = []
        for item in areas_structures:
            if not isinstance(item, dict):
                raise ValueError(f"Items in area list must be dictionary")

            if (not ReceivedStructureProcessor.check_dict_values_and_types(item, allowed_keys_and_types)):
                raise ValueError(
                    "some keys are not allowed or have wrong types")

            new_item = item.copy()

            # Validate and convert the area.
            area_val = new_item[key_with_area]
            if isinstance(area_val, str):
                pass
            elif isinstance(area_val, list):
                new_item[key_with_area] = ReceivedStructureProcessor.validate_and_convert_area_cordinates(
                    area_val)
            else:
                raise ValueError(
                    f"{key_with_area} must be a string or a list of lists/tuples"
                )

            edited_data.append(new_item)

        return edited_data
    # valid_data = {
    #         "nodes": {
    #             "place": {
    #                 "tower": {"width_fe": 1, },
    #                 "peak": {"width_fe": 1, 'text_width_fe': 3}
    #             }
    #         },
    #         "areas": {
    #             "leisure": {'farmland': {"width_fe": 2, 'text_width_fe': 3}},
    #             "buildings": {"width_fe": 2, 'text_width_fe': 3},

    #         },
    #         "ways": {},

    #     }
    # validate_wanted_elements_and_styles(valid_data, {
    #         'nodes': {
    #             'place': ['peak', 'tower'],
    #             'location': ['city', 'town']
    #         },
    #         'areas_as_nodes': {
    #             'place': ['peak', 'tower']
    #         },
    #         'ways': {},
    #         'areas': {
    #             'buildings': True,  # True means any tag is allowed
    #             'leisure': ['farmland']
    #         }, ['width_fe', 'text_width_fe']):
    @staticmethod
    def validate_wanted_elements_and_styles(data: Dict[str, Any], allowed_structure: dict, frontend_styles: list) -> bool:
        """
        Validate the map data structure sent from frontend.

        Args:
            data: The map data structure to validate

        Returns:
            bool: True if validation passes

        Raises:
            ValueError: If validation fails
        """

        # Validate top-level keys
        for category in data.keys():
            if category not in allowed_structure:
                raise ValueError(f"Invalid category: {category}")

            # Skip empty categories
            if not data[category]:
                continue

            # Validate subcategories
            for subcategory, subcategory_data in data[category].items():
                if subcategory not in allowed_structure[category]:
                    raise ValueError(
                        f"Invalid subcategory: {subcategory} in {category}")

                allowed_subcategory = allowed_structure[category][subcategory]

                # Skip empty subcategories
                if (not subcategory_data and allowed_subcategory == True):
                    continue
                # Handle different validation rules based on allowed structure
                # Case 1: Subcategory has all tags allowed but must have at least one tag or be missing
                if (not subcategory_data):
                    raise ValueError(
                        f"Empty element (will have all attributes but must have at least one tag or be missing): {subcategory} in {category}")
                elif (all(key in frontend_styles for key in subcategory_data.keys()) and allowed_subcategory != True):
                    raise ValueError(
                        f"Empty element (will have all attributes but must have at least one tag or be missing): {subcategory} in {category}")
                    
                elif isinstance(allowed_subcategory, list):
                    for tag in subcategory_data:
                        if tag not in allowed_subcategory:
                            raise ValueError(
                                f"Invalid tag: {tag} in {category}.{subcategory}")

                        # Validate attributes
                        tag_data = subcategory_data[tag]
                        if tag_data and isinstance(tag_data, dict):
                            for attr in tag_data:
                                if attr not in frontend_styles:
                                    raise ValueError(
                                        f"Invalid attribute: {attr} in {category}.{subcategory}.{tag}")

                # Case 2: Subcategory empty or missing allowed
                elif allowed_subcategory is True:
                    if isinstance(subcategory_data, dict):
                        for attr in subcategory_data:
                            if attr not in frontend_styles or isinstance(subcategory_data[attr], dict):
                                raise ValueError(
                                    f"Invalid attribute: {attr} in {category}.{subcategory}")
        return True

    @staticmethod
    def transform_to_backend_structures(data: Dict[str, Any], allowed_styles=['width_fe', 'text_width_fe'],
                                        styles_allowed_primary_elements=['nodes', 'ways', 'areas']) -> Dict[str, Any]:
        """
        Transform the validated frontend data into two backend structures.

        Args:
            data: The validated map data structure

        Returns:
            Dict containing the two transformed structures
        """

        def has_subsections(dict, allowed_multiply_atributes):
            return any(key not in allowed_multiply_atributes for key in dict)

        # Structure 1: Without attributes
        wanted_categories = {}
        multiply_filters = {key: [] for key in styles_allowed_primary_elements}
        for category in data:
            wanted_categories[category] = {}
            for subcategory in data[category]:
                # Extract tags without attributes
                wanted_categories[category][subcategory] = set(
                    {tag for tag in data[category][subcategory] if tag not in allowed_styles})
                # create pandas filters for assing attributes from FE
                if (has_subsections(data[category][subcategory], allowed_styles)):
                    for tag, tag_data in data[category][subcategory].items():
                        attributes = {
                            k: v for k, v in tag_data.items() if k in allowed_styles}
                        if attributes:
                            path_key = {subcategory: tag}
                            multiply_filters[category].append(
                                (path_key, attributes))
                else:
                    attributes = {
                        k: v for k, v in data[category][subcategory].items() if k in allowed_styles}
                    if attributes:
                        path_key = {subcategory: ''}
                        multiply_filters[category].append(
                            (path_key, attributes))

        return wanted_categories, multiply_filters
