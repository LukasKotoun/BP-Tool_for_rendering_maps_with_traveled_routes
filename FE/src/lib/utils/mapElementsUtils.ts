/**
 * Utils for map elements selection and transformation
 * @author Lukáš Kotoun, xkotou08
 */
// Set false to all plot properties in the data
export function resetPlotSettings(
  originalData: MapElementCategory
): MapElementCategory {
  const result: MapElementCategory = JSON.parse(JSON.stringify(originalData));

  function processElement(element: MapElementCategory | MapElementAttributes) {
    if ("plot" in element) {
      (element as MapElementAttributes)["plot"] = false;
    }

    // Recursively process nested elements
    for (const key in element) {
      const child = element[key];
      if (typeof child === "object") {
        processElement(child);
      }
    }
  }
  processElement(result);
  return result;
}

export function mapValue(dict: Dictionary, value: string): string {
  if (dict == undefined) return value;
  if (dict == null) return value;

  return dict[value] ?? value; // If value is found in dict, return the mapped value, otherwise return the original value
}

// Set plot property to true for all elements that are in the updateRules
export function updateWantedElements(
  originalData: MapElementCategory,
  updateRules: MapElementUpdateRules
): MapElementCategory {
  let dataToUpdate = JSON.parse(
    JSON.stringify(originalData)
  ) as MapElementCategory;
  // main keys to update (like highway, railway...)
  for (const categoryKey in updateRules) {
    const category = updateRules[categoryKey];
    if (typeof category === "boolean" && category) {
      if (dataToUpdate[categoryKey]) {
        // If it has plot property directly (e.g. building: {plot: true})
        if (
          typeof dataToUpdate[categoryKey] === "object" &&
          dataToUpdate[categoryKey].hasOwnProperty("plot")
        ) {
          (dataToUpdate[categoryKey] as MapElementAttributes).plot = true;
        }

        // For all its subcategories if have (e.g. highway: {motorway: {plot: true}})
        for (const subKey in dataToUpdate[categoryKey]) {
          dataToUpdate[categoryKey] = dataToUpdate[
            categoryKey
          ] as MapElementCategory;
          if (
            typeof dataToUpdate[categoryKey][subKey] === "object" &&
            dataToUpdate[categoryKey][subKey].hasOwnProperty("plot")
          ) {
            dataToUpdate[categoryKey][subKey].plot = true;
          }
        }
      }
    } else if (Array.isArray(category)) {
      // Specific parent categories are listed
      for (const parentCategory of category) {
        // check if the parent category exists in dataToUpdate
        if (dataToUpdate[categoryKey]) {
          dataToUpdate[categoryKey] = dataToUpdate[
            categoryKey
          ] as MapElementCategory;
          if (
            (dataToUpdate[categoryKey] as MapElementCategory)[parentCategory] &&
            typeof dataToUpdate[categoryKey][parentCategory] === "object" &&
            dataToUpdate[categoryKey][parentCategory].hasOwnProperty("plot")
          ) {
            dataToUpdate[categoryKey][parentCategory].plot = true;
          }
        }
      }
    }
  }
  return dataToUpdate;
}

// Transform by removing plot property and keeping only element with true on that property and attributes that are different from the default values
export function transformElementsStructureForBE(
  data: MapElementCategory,
  scale_keys: Record<string, number>
): MapElementCategorySend {
  const result: MapElementCategorySend = {};
  function isMapElementAttributes(obj: any): obj is MapElementAttributes {
    return obj && typeof obj === "object" && "plot" in obj;
  }

  // Each main category (highway, building...)
  for (const categoryKey in data) {
    const category = data[categoryKey];

    // Check if the category has a "plot" property
    if (isMapElementAttributes(category)) {
      if (category.plot === true) {
        const newCategory: MapElementAttributesSend = {};

        for (const propKey in category) {
          if (propKey === "plot" || !scale_keys.hasOwnProperty(propKey)) {
            continue;
          }
          // Remove attributes with default value
          if (category[propKey] !== scale_keys[propKey]) {
            newCategory[propKey] = category[propKey];
          }
        }

        // add only if plot is true
        result[categoryKey] = newCategory;
      }
      // If plot is false, skip this subcategory
    } else {
      // Process subcategories (like motorway, primary inside main key highway)
      const newCategory: MapElementCategorySend = {};
      let hasValidSubcategories = false;

      for (const subcategoryKey in category) {
        const subcategory = category[subcategoryKey];

        // Check if subcategory has plot property
        if (subcategory.hasOwnProperty("plot")) {
          if (subcategory.plot === true) {
            // keep this subcategory but remove plot property
            const newSubcategory: MapElementAttributesSend = {};

            for (const propKey in subcategory) {
              if (propKey === "plot" || !scale_keys.hasOwnProperty(propKey)) {
                continue;
              }
              // Remove scale attributes with value same as default
              if (subcategory[propKey] !== scale_keys[propKey]) {
                newSubcategory[propKey] = subcategory[propKey];
              }
            }
            // at least one subcategory is valid
            hasValidSubcategories = true;
            newCategory[subcategoryKey] = newSubcategory;
          }
          // If plot is false, skip this subcategory
        }
      }

      // Add category if has any valid subcategories
      if (hasValidSubcategories) {
        result[categoryKey] = newCategory;
      }
    }
  }

  return result;
}
