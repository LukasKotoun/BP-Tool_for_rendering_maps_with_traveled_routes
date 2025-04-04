from typing import Dict, List, Union, Any, Callable

from common.map_enums import Style
from common.custom_types import RowsConditionsAND
from common.api_base_models import PaperDimensionsModel, FitPaperSizeModel


class ReceivedStructureProcessor:

    @staticmethod
    def map_dict(input_dict: dict[str, any], mapping_dict: dict[str, tuple[str, Callable, bool]]):
        """Replace dictionary keys with new values in mapping_dict and map its values using transform function in mapping_dict
        If missing from mapping dict keep them unchanged."""
        output = {}
        for key, value in input_dict.items():
            if key in mapping_dict:
                new_key, transform_func, *unpack = mapping_dict[key]

                new_key = new_key if new_key is not None else key
                new_value = transform_func(value) if callable(
                    transform_func) else value
                if unpack and unpack[0]:
                    if isinstance(new_value, dict):
                        output.update(new_value)
                    else:
                        raise ValueError(
                            f"Expected {new_key} to return a dictionary, got {type(new_value)}")
                else:
                    output[new_key] = new_value
            else:
                output[key] = value
        return output

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
        """Check if values in dict have allowed keys and types.
        Alowed keys and types is: str: (type, required, validation_func)
            str: name of key
            type: type of value
            required: if value is required
            validation_func: function to validate value"""
        allowed_keys = set(allowed_keys_and_types.keys())
        required_keys = {
            k for k, (_, required, *_) in allowed_keys_and_types.items() if required}

        # Extra keys not allowed.
        if set(values_dict.keys()) - allowed_keys:
            return False

        # All required keys are present.
        if not required_keys.issubset(values_dict.keys()):
            return False

        # Check types.
        for key, (expected_type, required, *validation_func) in allowed_keys_and_types.items():
            validation_func = validation_func[0] if validation_func else None
            if key in values_dict and expected_type is not None:
                if (required and values_dict[key] is None):
                    return False
                if (not required and values_dict[key] is None):
                    continue
                if (not required):
                    expected_type = Union[expected_type, type(None)]
                if not isinstance(values_dict[key], expected_type):
                    return False
                if validation_func and not validation_func(values_dict[key]):
                    return False
        return True

    @staticmethod
    def validate_and_convert_areas_strucutre(areas_structures: list[dict], allowed_keys_and_types: dict[str, tuple[type, bool, Callable]],
                                             areas_mapping: dict[str, tuple[str, Callable, bool]], key_with_area) -> list[dict]:
        if not isinstance(areas_structures, list):
            raise ValueError("Input must be a list.")

        edited_data = []
        for item in areas_structures:
            if not isinstance(item, dict):
                raise ValueError(f"Items in area list must be dictionary")

            if (not ReceivedStructureProcessor.check_dict_values_and_types(item, allowed_keys_and_types)):
                raise ValueError(
                    "some keys are not allowed or have wrong types")
            item = ReceivedStructureProcessor.map_dict(
                item, areas_mapping)
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
                f"Invalid keys in wanted elements and styles: {set(data.keys()) - set(allowed_structure.keys())}")

        for element_category in data.keys():
            if element_category not in allowed_structure:
                raise ValueError(
                    f"Invalid element_category in wanted elements and styles: {element_category}")

            # Skip empty elements categories
            if not data[element_category]:
                continue

            # Validate element features
            for element, element_features in data[element_category].items():
                if element not in allowed_structure[element_category]:
                    raise ValueError(
                        f"Invalid element: {element} in {element_category} (wanted elements and styles")

                allowed_element = allowed_structure[element_category][element]

                # Skip empty subcategories
                if (not element_features and allowed_element == True):
                    continue
                # Handle different validation rules based on allowed structure
                # Case 1: element allowed all is false, must have at least one tag or be missing
                if (not element_features):
                    raise ValueError(
                        f"Empty element (will have all attributes but must have at least one tag or be missing): {element} in {element_category} (wanted elements and styles)")

                elif (any(key in styles_validation for key in element_features.keys()) and allowed_element != True):
                    raise ValueError(
                        f"Empty element (will have all attributes but must have at least one tag or be missing): {element} in {element_category} (wanted elements and styles)")

                elif isinstance(allowed_element, list):
                    for tag in element_features:
                        if tag not in allowed_element:
                            raise ValueError(
                                f"Invalid tag: {tag} in {element_category}.{element} (wanted elements and styles)")

                        # Validate attributes
                        tag_data = element_features[tag]
                        if tag_data and isinstance(tag_data, dict):
                            if (not ReceivedStructureProcessor.check_dict_values_and_types(tag_data, styles_validation)):
                                raise ValueError(
                                    f"Invalid attribute in {element_category}.{element}.{tag} (wanted elements and styles)")

                # Case 2: element empty or missing allowed
                elif allowed_element is True:
                    if isinstance(element_features, dict):
                        for attr in element_features:
                            if not ReceivedStructureProcessor.check_dict_values_and_types(element_features, styles_validation):
                                raise ValueError(
                                    f"Invalid attribute: {attr} in {element_category}.{element} (wanted elements and styles)")
        return True

    @staticmethod
    def transform_wanted_elements_to_backend_structures(data: Dict[str, Any], allowed_styles: list, styles_allowed_primary_elements: list,
                                                        styles_mapping: dict[str,
                                                                             tuple[str, Callable, bool]] = {}) -> tuple[dict, dict]:
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
                            styles = ReceivedStructureProcessor.map_dict(
                                styles, styles_mapping)
                            condition: RowsConditionsAND = {element: tag}
                            styles_edits[element_category].append(
                                (condition, styles))
                else:
                    styles = {
                        k: v for k, v in data[element_category][element].items() if k in allowed_styles}
                    if styles:
                        styles = ReceivedStructureProcessor.map_dict(
                            styles, styles_mapping)
                        condition: RowsConditionsAND = {element: ''}
                        styles_edits[element_category].append(
                            (condition, styles))

        return wanted_categories, styles_edits

    def validate_and_convert_gpx_styles(data: dict, normal_keys: list, general_keys: list,
                                        styles_validation: dict[str,
                                                                tuple[type, bool, Callable]] = {},
                                        styles_mapping: dict[str, tuple[str, Callable, bool]] = {}) -> bool:
        result = []
        # check it there is key that is not in normal_keys or general_keys
        if (any(key not in normal_keys + general_keys for key in data)):
            raise ValueError(
                f"Invalid gpx style categories (valid area: {normal_keys + general_keys})")
        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary in gpx styles")
        for key in normal_keys:
            if key in data and isinstance(data[key], dict):
                for name, value in data[key].items():
                    if (not ReceivedStructureProcessor.check_dict_values_and_types(value, styles_validation)):
                        raise ValueError(
                            f"Invalid attribute in gpx styles {key}.{name} ({value})")
                    styles = ReceivedStructureProcessor.map_dict(
                        value, styles_mapping)
                    result.append(({key: name}, styles))
        for key in general_keys:
            if key in data and isinstance(data[key], dict):
                if (not ReceivedStructureProcessor.check_dict_values_and_types(data[key], styles_validation)):
                    raise ValueError(
                        f"Invalid attribute in gpx styles {key} ({data[key]})")
                styles = ReceivedStructureProcessor.map_dict(
                    data[key], styles_mapping)
                result.append(
                    ([], styles))

        return result

    @staticmethod
    def validate_and_convert_osm_files(osm_files: List[str], mapping_dict: dict[str, str]) -> List[str]:
        if (any(file not in mapping_dict for file in osm_files)):
            raise ValueError("Invalid osm files")
        # Remove duplicates
        osm_files = list(set(osm_files))
        return [mapping_dict[file] for file in osm_files]

    @staticmethod
    def convert_paper_dimension(paper_dimensions: PaperDimensionsModel, allow_one_dimension_only=False) -> tuple[float, float]:
        """Validate and convert the paper dimensions - must be previously validated to int or float or None"""
        if (allow_one_dimension_only):
            if (paper_dimensions.width is None and paper_dimensions.height is None):
                raise ValueError("Both paper dimensions cannot be None")
        else:
            if (paper_dimensions.width is None or paper_dimensions.height is None):
                raise ValueError("Both paper dimensions must be provided")

        return (paper_dimensions.width, paper_dimensions.height)

    @staticmethod
    def validate_wanted_orientation(orientation: str, valid_orientations: str) -> str:
        if orientation not in valid_orientations:
            raise ValueError("Invalid wanted orientation")
        return orientation

    @staticmethod
    def validate_and_convert_zoom_levels(data: dict[str, int], level_validation: dict[str, tuple[type, bool, Callable]],
                                         level_mapping: dict[str, tuple[str, Callable, bool]]) -> dict[str, int]:
        if (not ReceivedStructureProcessor.check_dict_values_and_types(data, level_validation)):
            raise ValueError(f"Invalid zoom level (must be between 1 and 10)")
        zooms = ReceivedStructureProcessor.map_dict(
            data, level_mapping)
        return zooms

    @staticmethod
    def validate_fit_paper(data: FitPaperSizeModel, fit_paper_validation: dict[str, tuple[type, bool, Callable]]) -> bool:
        if (not ReceivedStructureProcessor.check_dict_values_and_types(data.model_dump(), fit_paper_validation)):
            raise ValueError(f"Invalid fit paper size struct ")
        if (data.plot and data.width is None):
            raise ValueError(
                "Width must be provided if plot is True in fit paper size")
        return True
