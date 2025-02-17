from common.map_enums import WorldSides, StyleKey, StyleType
BoundsDict = dict[WorldSides, float]
DimensionsTuple = tuple[float, float]
Point = tuple[float, float]
WantedArea = str | list[Point] | list[str | list[Point]]
OptDimensionsTuple = tuple[float | None, float | None]
WantedCategories = dict[str, set[str]]
UnwantedTags = dict[str, any]
FeatureStyles = dict[StyleKey, str | int | float]
FeaturesCategoryStyle = dict[str, FeatureStyles]
FeaturesCategoriesStyles = dict[str,
                                tuple[FeaturesCategoryStyle, FeatureStyles]]

FeatureStyleZooms = dict[str, FeatureStyles]
FeatureStyleDynamics = dict[StyleType, FeatureStyles | FeatureStyleZooms]
CategoryFilters = list[tuple[str, str]]
FeatureCategoriesStyles = tuple[CategoryFilters, FeatureStyles]
FeatureCategoriesStylesDynamic = tuple[CategoryFilters, FeatureStyleDynamics]


Styles = dict[StyleKey, str | int | float]
StyleZooms = dict[str, Styles]
RowsConditionsAND = dict[str, str | list[str]]
RowsConditions = list[RowsConditionsAND]
ElementStyles = tuple[RowsConditions | RowsConditionsAND, Styles]
ElementStylesDynamic = tuple[RowsConditions | RowsConditionsAND, Styles, StyleZooms | None]

