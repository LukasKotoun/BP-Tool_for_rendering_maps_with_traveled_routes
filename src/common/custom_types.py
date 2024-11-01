from common.map_enums import WorldSides, StyleKey
BoundsDict = dict[WorldSides, float]
FeatureStyles = dict[StyleKey, str | int | float]
FeaturesCategoryStyle = dict[str, FeatureStyles]
WantedCategories = dict[str, set[str]]
UnwantedCategories = dict[str, any]
FeaturesCategoriesStyles = dict[str, tuple[FeaturesCategoryStyle, FeatureStyles]]
DimensionsTuple = Point = tuple[float, float]
OptDimensionsTuple = tuple[float | None, float | None]