from common.map_enums import WorldSides, StyleKey
type BoundsDict = dict[WorldSides, float]
type ItemStyles = dict[StyleKey, str | int | float]
type CategoryStyle = dict[str, ItemStyles]
type WantedCategories = dict[str, list[str]]
type UnwantedCategories = dict[str, any]
type CategoriesStyles = dict[str, tuple[CategoryStyle, ItemStyles]]