from common.map_enums import Style
from common.custom_types import RowsConditions, RowsConditionsAND
from typing import Dict, List, Union, Any, Optional, Callable

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
    def check_dict_values_and_types(values_dict: dict, allowed_keys_and_types: dict[str, tuple[type, bool, Callable]]):
        allowed_keys = set(allowed_keys_and_types.keys())
        required_keys = {
            k for k, (_, required, _) in allowed_keys_and_types.items() if required}

        # Extra keys not allowed.
        if set(values_dict.keys()) - allowed_keys:
            return False

        # All required keys are present.
        if not required_keys.issubset(values_dict.keys()):
            return False

        # Check types.
        for key, (expected_type, _, validation_func) in allowed_keys_and_types.items():
            if key in values_dict and expected_type is not None:
                if not isinstance(values_dict[key], expected_type):
                    return False
                if validation_func and not validation_func(values_dict[key]):
                    return False
        return True

    @staticmethod
    def validate_and_convert_areas_strucutre(areas_structures: list[dict], allowed_keys_and_types: dict[str, tuple[type, bool, Callable]], key_with_area):
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

    @staticmethod
    def validate_wanted_elements_and_styles(data: Dict[str, Any], allowed_structure: dict, styles_validation: dict[str, tuple[type, bool, Callable]]) -> bool:
        """
        Validate the map data structure sent from frontend.

        Args:
            data: The map data structure to validate

        Returns:
            bool: True if validation passes

        Raises:
            ValueError: If validation fails
        """

        # Validate top-level keys - must have all
        if not all(key in data for key in allowed_structure):
            raise ValueError(
                f"Invalid keys: {set(data.keys()) - set(allowed_structure.keys())}")

        for element_category in data.keys():
            if element_category not in allowed_structure:
                raise ValueError(
                    f"Invalid element_category: {element_category}")

            # Skip empty elements categories
            if not data[element_category]:
                continue

            # Validate element features
            for element, element_features in data[element_category].items():
                if element not in allowed_structure[element_category]:
                    raise ValueError(
                        f"Invalid element: {element} in {element_category}")

                allowed_element = allowed_structure[element_category][element]

                # Skip empty subcategories
                if (not element_features and allowed_element == True):
                    continue
                # Handle different validation rules based on allowed structure
                # Case 1: element allowed all is false, must have at least one tag or be missing
                if (not element_features):
                    raise ValueError(
                        f"Empty element (will have all attributes but must have at least one tag or be missing): {element} in {element_category}")

                elif (any(key in styles_validation for key in element_features.keys()) and allowed_element != True):
                    raise ValueError(
                        f"Empty element (will have all attributes but must have at least one tag or be missing): {element} in {element_category}")

                elif isinstance(allowed_element, list):
                    for tag in element_features:
                        if tag not in allowed_element:
                            raise ValueError(
                                f"Invalid tag: {tag} in {element_category}.{element}")

                        # Validate attributes
                        tag_data = element_features[tag]
                        if tag_data and isinstance(tag_data, dict):
                            if (not ReceivedStructureProcessor.check_dict_values_and_types(tag_data, styles_validation)):
                                raise ValueError(
                                    f"Invalid attribute in {element_category}.{element}.{tag}")

                # Case 2: element empty or missing allowed
                elif allowed_element is True:
                    if isinstance(element_features, dict):
                        for attr in element_features:
                            if not ReceivedStructureProcessor.check_dict_values_and_types(element_features, styles_validation):
                                raise ValueError(
                                    f"Invalid attribute: {attr} in {element_category}.{element}")
        return True

    @staticmethod
    def transform_to_backend_structures(data: Dict[str, Any], allowed_styles: dict[str, tuple[type, bool, Callable]],
                                        styles_allowed_primary_elements, names_maping: dict[str, str]) -> tuple[dict, dict]:
        """
        Transform the validated frontend data into two backend structures.

        Args:
            data: The validated map data structure

        Returns:
            Dict containing the two transformed structures
        """

        def has_subsections(dict, allowed_multiply_atributes):
            return any(key not in allowed_multiply_atributes for key in dict)

        wanted_categories = {}
        styles_edits = {key: [] for key in styles_allowed_primary_elements}
        for element_category in data:
            wanted_categories[element_category] = {}
            for element in data[element_category]:
                # Extract tags without attributes
                wanted_categories[element_category][element] = set(
                    {tag for tag in data[element_category][element] if tag not in allowed_styles})

                # create pandas filters for assing attributes from FE
                if (has_subsections(data[element_category][element], allowed_styles)):
                    for tag, tag_data in data[element_category][element].items():
                        styles = {
                            k: v for k, v in tag_data.items() if k in allowed_styles}
                        if styles:
                            styles = ReceivedStructureProcessor.map_dict_keys(
                                styles, names_maping)
                            condition: RowsConditionsAND = {element: tag}
                            styles_edits[element_category].append(
                                (condition, styles))
                else:
                    styles = {
                        k: v for k, v in data[element_category][element].items() if k in allowed_styles}
                    if styles:
                        styles = ReceivedStructureProcessor.map_dict_keys(
                            styles, names_maping)
                        condition: RowsConditionsAND = {element: ''}
                        styles_edits[element_category].append(
                            (condition, styles))

        return wanted_categories, styles_edits

    def validate_gpx_styles(data: dict, normal_keys: list, general_keys: list, styles_validation: dict[str, tuple[type, bool, Callable]], styles_mapping: dict[str, str]) -> bool:
        result = []

        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        for key in normal_keys:
            if key in data and isinstance(data[key], dict):
                for name, value in data[key].items():
                    if (not ReceivedStructureProcessor.check_dict_values_and_types(value, styles_validation)):
                        raise ValueError(f"Invalid attribute in {key}.{name}")
                    result.append(({key: name}, ReceivedStructureProcessor.map_dict_keys(
                        value, styles_mapping)))
        for key in general_keys:
            if key in data and isinstance(data[key], dict):
                if (not ReceivedStructureProcessor.check_dict_values_and_types(data[key], styles_validation)):
                    raise ValueError(f"Invalid attribute in {key}")
                result.append(
                    ([], ReceivedStructureProcessor.map_dict_keys(value, data[key])))

        return result

    @staticmethod
    def validate_and_convert_osm_files(osm_files: List[str], mapping_dict: dict[str, str]) -> List[str]:
        if (any(file not in mapping_dict for file in osm_files)):
            raise ValueError("Invalid osm files")
        return [mapping_dict[file] for file in osm_files]

    @staticmethod
    def validate_and_convert_paper_dimension(paper_dimensions: list[float, float]) -> tuple[float, float]:
        if len(paper_dimensions) != 2:
            raise ValueError("Paper dimensions must have exactly 2 values")
        if not all(isinstance(num, (int, float)) and num >= 1 for num in paper_dimensions):
            raise ValueError("Paper dimensions must have only numbers")
        return tuple(paper_dimensions)

    @staticmethod
    def validate_zoom_levels(data, level_validation) -> bool:
        if (not ReceivedStructureProcessor.check_dict_values_and_types(data, level_validation)):
            raise ValueError(f"Invalid attribute in")
        return True
