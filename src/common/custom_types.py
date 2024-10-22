from common.map_enums import WorldSides, StyleKey
BoundsDict = dict[WorldSides, float]
ItemStyles = dict[StyleKey, str | int | float]
CategoryStyle = dict[str, ItemStyles]
WantedCategories = dict[str, list[str]]
UnwantedCategories = dict[str, any]
CategoriesStyles = dict[str, tuple[CategoryStyle, ItemStyles]]
DimensionsTuple = Point = tuple[float, float]
OptDimensionsTuple = tuple[float | None, float | None]