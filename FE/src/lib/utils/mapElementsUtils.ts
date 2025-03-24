

export function resetPlotSettings(originalData: MapElementCategory, bool_key_to_reset: string): MapElementCategory{
      const result: MapElementCategory = JSON.parse(JSON.stringify(originalData));
    
      function processElement(element: MapElementCategory | MapElementAttributes) {
        if (bool_key_to_reset in element) {
          (element as MapElementAttributes)[bool_key_to_reset] = false;
        }
    
        // Recursively process nested elements
        for (const key in element) {
          const child = element[key];
          if (typeof child === 'object') {
            processElement(child);
          }
        }
      }
      processElement(result);
      return result;
    }


export function mapValue(dict: Dictionary, value: string): string {    
    if(dict == undefined) return value;
    if(dict == null) return value;
   
    return dict[value] ?? value;  // If value is found in dict, return the mapped value, otherwise return the original value
  }


export function updateWantedElements(originalData: MapElementCategory, updateRules: MapElementUpdateRules, keep_key: string): MapElementCategory {
  let dataToUpdate = JSON.parse(JSON.stringify(originalData)) as MapElementCategory
  // main keys to update (like highway, railway...)
  for (const categoryKey in updateRules) {
    const category = updateRules[categoryKey]
    if (typeof category  === 'boolean' && category) {
      if (dataToUpdate[categoryKey]) {
        // If it has plot property directly (e.g. building: {plot: true})
        if (typeof dataToUpdate[categoryKey] === "object" && dataToUpdate[categoryKey].hasOwnProperty(keep_key)) {
          ;(dataToUpdate[categoryKey] as MapElementAttributes).plot = true
        }

        // For all its subcategories if have (e.g. highway: {motorway: {plot: true}})
        for (const subKey in dataToUpdate[categoryKey]) {
          dataToUpdate[categoryKey] = dataToUpdate[categoryKey] as MapElementCategory
          if (typeof dataToUpdate[categoryKey][subKey] === "object" && dataToUpdate[categoryKey][subKey].hasOwnProperty(keep_key)) {
            dataToUpdate[categoryKey][subKey].plot = true
          }
        }
      }
    } else if (Array.isArray(category)) {
      // Specific parent categories are listed
      for (const parentCategory of category) {
        // check if the parent category exists in dataToUpdate
        if (dataToUpdate[categoryKey]) {
          dataToUpdate[categoryKey] = dataToUpdate[categoryKey] as MapElementCategory
          if (
            (dataToUpdate[categoryKey] as MapElementCategory)[parentCategory] &&
            typeof dataToUpdate[categoryKey][parentCategory] === "object" &&
            dataToUpdate[categoryKey][parentCategory].hasOwnProperty(keep_key)
          ) {
            dataToUpdate[categoryKey][parentCategory].plot = true
          }
        }
      }
    }
  }
  return dataToUpdate
}


export function transformStructure(data: MapElementCategory, keep_key: string, scale_keys: Record<string, number>): MapElementCategorySend {

    const result: MapElementCategorySend = {}
    function isMapElementAttributes(obj: any): obj is MapElementAttributes {
        return obj && typeof obj === 'object' && keep_key in obj;
      }

    // Each main category (highway, building...)
    for (const categoryKey in data) {
      const category = data[categoryKey]

      // Check if the category has a keep_key property
      if (isMapElementAttributes(category)) {
        if (category.plot === true) {
            const newCategory: MapElementAttributesSend = {};
            
          for (const propKey in category) {
            if (propKey === keep_key || !scale_keys.hasOwnProperty(propKey)) {
              continue
            }
            // Remove attributes with default value
            if (category[propKey] !== scale_keys[propKey]) {
              newCategory[propKey] = category[propKey]
            }
          }

          // add only if plot is true
          result[categoryKey] = newCategory
        }
        // If plot is false, skip this subcategory
      } else {
        // Process subcategories (like motorway, primary inside main key highway)
        const newCategory: MapElementCategorySend = {}
        let hasValidSubcategories = false

        for (const subcategoryKey in category) {
          const subcategory = category[subcategoryKey]

          // Check if subcategory has plot property
          if (subcategory.hasOwnProperty(keep_key)) {
            if (subcategory.plot === true) {
              // keep this subcategory but remove plot property
              const newSubcategory: MapElementAttributesSend = {}

              for (const propKey in subcategory) {
                if (propKey === keep_key || !scale_keys.hasOwnProperty(propKey)) {
                  continue
                }
                // Remove scale attributes with value same as default
                if (subcategory[propKey] !== scale_keys[propKey]) {
                  newSubcategory[propKey] = subcategory[propKey]
                }
              }
              // at least one subcategory is valid
              hasValidSubcategories = true
              newCategory[subcategoryKey] = newSubcategory
            }
            // If plot is false, skip this subcategory
          }
        }

        // Add category if has any valid subcategories
        if (hasValidSubcategories) {
          result[categoryKey] = newCategory
        }
      }
    }

    return result
  }